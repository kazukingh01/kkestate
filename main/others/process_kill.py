import psutil
import time
import argparse
import os
import sys
from joblib import Parallel, delayed
from functools import partial

def is_already_running():
    """同じスクリプトが他に動作中かチェック (自身を除外)"""
    my_pid = os.getpid()
    script_name = os.path.basename(sys.argv[0])
    # 絶対パスも考慮
    script_path = os.path.abspath(sys.argv[0])
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            pid = proc.info['pid']
            if pid == my_pid:
                continue
            cmdline = proc.info['cmdline'] or []
            # インタプリタ経由 or 直接実行の両方を検出
            if len(cmdline) >= 2:
                # python script.py の場合
                if os.path.basename(cmdline[1]) == script_name or os.path.abspath(cmdline[1]) == script_path:
                    return True
            if len(cmdline) >= 1:
                # ./script.py のような直接実行
                if os.path.basename(cmdline[0]) == script_name or os.path.abspath(cmdline[0]) == script_path:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def find_pids(cmd_substring):
    """cmd_substring を含むプロセスの PID を返す。自分自身は除外。"""
    my_pid = os.getpid()
    pids = []
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            pid = proc.info['pid']
            if pid == my_pid:
                continue
            cmdline = proc.info['cmdline'] or []
            full_cmd = ' '.join(cmdline)
            if cmd_substring in full_cmd:
                pids.append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return pids

def monitor_and_kill(pid, duration, interval, cpu_thresh, flg_kill: bool=False):
    """単一 PID を一定時間監視し、条件が続いたら kill する。"""
    try:
        p = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"[PID {pid}] 存在しません。")
        return

    checks = int(duration / interval)
    p.cpu_percent(interval=None)  # 初回プライム

    hang_count = 0
    print(f"--- PID {pid} を監視 (duration={duration}s, interval={interval}s) ---")
    for i in range(1, checks + 1):
        cpu = p.cpu_percent(interval=interval)
        status = p.status()  # e.g. 'running'／'disk-sleep'
        print(f"[{i}/{checks}] CPU={cpu:.2f}% | status={status}")
        if status == psutil.STATUS_DISK_SLEEP and cpu < cpu_thresh:
            hang_count += 1
        else:
            print(f"[PID {pid}] 正常応答あり → kill 中止")
            break
        time.sleep(interval)

    if hang_count == checks:
        if flg_kill:
            print(f"[PID {pid}] ハング判定 → kill 実行")
            try:
                p.kill()
                print(f"[PID {pid}] kill 完了")
            except Exception as e:
                print(f"kill 失敗: {e}")
    else:
        print(f"[PID {pid}] 正常と判断 → 何もしません")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Monitor & kill hung processes matching a cmdline substring"
    )
    parser.add_argument("cmd", metavar="CMD_SUBSTRING", help="プロセス cmdline に含まれる文字列 (例: 'python XXXX --update')")
    parser.add_argument("-d", "--duration", type=int,   default=10, help="監視合計時間 (秒) (デフォルト: 110)")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="チェック間隔 (秒) (デフォルト: 1.0)")
    parser.add_argument("-c", "--cpu-threshold", type=float, default=0.1, help="低 CPU とみなす CPU%% の閾値 (デフォルト: 0.1)")
    parser.add_argument("-k", "--kill", action="store_true", help="kill 実行フラグ (デフォルト: False)")
    args = parser.parse_args()
    if is_already_running():
        print("Error: process_kill.py が既に実行中です。重複起動を防止します。")
        sys.exit(1)

    # 該当プロセスを検索
    pids = find_pids(args.cmd)
    if not pids:
        print(f"'{args.cmd}' を含むプロセスが見つかりませんでした。")
        sys.exit(0)

    # joblib で並列実行
    func = partial(monitor_and_kill, flg_kill=args.kill)
    Parallel(n_jobs=-1)(
        delayed(func)(pid, args.duration, args.interval, args.cpu_threshold)
        for pid in pids
    )
