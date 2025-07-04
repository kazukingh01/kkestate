"""
データ参照関係生成処理 (generate_detail_ref.py)

目的:
- estate_detail_refテーブルにデータ参照関係を生成
- 特定のrun_idに対して、過去指定期間内の同一物件の最新データを参照
- データ節約のため省略されたレコードを補完するための参照情報を作成
- estate_run.is_refフラグによる処理済み管理

処理概要:
1. 対象run_idの範囲に追加で指定期間さかのぼった拡張データを一括取得
2. 各run_idに対して同一物件の過去データからestate_detailを取得
3. 各id_keyの最新データを特定しestate_detail_refに保存
4. 処理完了時にestate_run.is_ref=trueを設定
"""

import argparse
import pandas as pd
from datetime import datetime, timedelta
from kklogger import set_logger
from kkpsgre.connector import DBConnector
from kkestate.config.psgre import HOST, PORT, USER, PASS, DBNAME, DBTYPE

LOGGER = set_logger(__name__)

def parse_runid_range(x: str):
    """
    runid範囲指定を解析する
    
    Args:
        x: 入力文字列（例: "123" または "1,1000"）
        
    Returns:
        List[int]: run_idのリスト
    """
    parts = x.split(",")
    
    if len(parts) == 1:
        # 単一指定
        return [int(parts[0])]
    elif len(parts) == 2:
        # 範囲指定
        start = int(parts[0])
        end = int(parts[1])
        if start > end:
            raise ValueError(f"範囲指定が無効です: {start} > {end}")
        return list(range(start, end + 1))
    else:
        # 3つ以上はエラー
        raise ValueError(f"runid指定は単一（123）または範囲（1,1000）のみ対応しています。入力: {x}")

def get_extended_runs_data(db: DBConnector, run_ids: list[int] | None = None, recent_months: int | None = None, months_back: int = 6) -> pd.DataFrame:
    """
    対象run_idに対して、追加で指定期間さかのぼった拡張run情報を取得
    
    Args:
        db: データベース接続
        run_ids: 処理対象のrun_idリスト（指定時は範囲指定処理）
        recent_months: 過去Xヶ月以内のrun_idを処理対象とする
        months_back: 追加でさかのぼる月数（デフォルト: 6ヶ月）
        
    Returns:
        tuple: (拡張run情報DataFrame, 対象run_id最小値, 対象run_id最大値)
    """
    if recent_months is None:
        assert run_ids is not None
        dfwk = db.select_sql(
            f"""
            SELECT MIN(timestamp) as t_min, MAX(timestamp) as t_max FROM estate_run
            WHERE is_success = true and 
                id >= {min(run_ids)} and id <= {max(run_ids)}
            """
        )
        min_timestamp = dfwk["t_min"].iloc[0]
        max_timestamp = dfwk["t_max"].iloc[0]
    else:
        assert run_ids is None
        min_timestamp = datetime.now() - timedelta(days=recent_months * 31)
        max_timestamp = datetime.now()
    extended_min_date = min_timestamp - timedelta(days=months_back * 31)
    sql = f"""
    SELECT id as id_run, id_main, timestamp
    FROM estate_run
    WHERE is_success = true
      AND timestamp >= '{extended_min_date}'
      AND timestamp <= '{max_timestamp}'
    ORDER BY id
    """
    df = db.select_sql(sql)
    dfwk = df.loc[(df["timestamp"] >= min_timestamp) & (df["timestamp"] <= max_timestamp)]
    if dfwk.shape[0] == 0:
        return pd.DataFrame(), None, None
    run_id_min, run_id_max = dfwk["id_run"].min(), dfwk["id_run"].max()
    LOGGER.info(f"日付範囲: {extended_min_date} ～ {max_timestamp}, run_id範囲: {run_id_min} ～ {run_id_max}")
    return df, run_id_min, run_id_max

def get_keys_by_target_id_runs(db: DBConnector, run_ids: list[int]) -> pd.DataFrame:
    """
    指定されたrun_idリストからestate_detailのid_key情報を取得
    
    Args:
        db: データベース接続
        run_ids: 対象のrun_idリスト
        
    Returns:
        pd.DataFrame: id_run, id_keyのペア
    """
    assert run_ids is not None
    assert len(run_ids) > 0
    sql = f"""
    SELECT 
        id_run,
        id_key
    FROM estate_detail
    WHERE id_run IN ({','.join(map(str, run_ids))})
    """
    df = db.select_sql(sql)
    return df

def get_unprocessed_runs(db: DBConnector, limit: int = 100) -> pd.DataFrame:
    """
    未処理のrun_idを取得（is_ref=falseのもの）
    
    Args:
        db: データベース接続
        limit: 取得する最大件数
        
    Returns:
        pd.DataFrame: 未処理のrun情報（id_run, id_main, timestamp）
    """
    sql = f"""
    SELECT id as id_run, id_main, timestamp
    FROM estate_run
    WHERE is_success = true
        AND is_ref = false
    ORDER BY id ASC
    LIMIT {limit}
    """
    df = db.select_sql(sql)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="データ参照関係生成処理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
実行例:
  # 統計情報表示
  python generate_detail_ref.py stats
  
  # データ参照関係処理
  python generate_detail_ref.py process --runid 123456 --update
  python generate_detail_ref.py process --runid 123,456 --update      # 範囲指定
  python generate_detail_ref.py process --update                       # 未処理分100件まで
  python generate_detail_ref.py process --update --limit 500          # 未処理分500件まで
  python generate_detail_ref.py process --recent 3 --update           # 過去3ヶ月分
  python generate_detail_ref.py process --recent 1 --limit 200 --update  # 過去1ヶ月、200件まで
  python generate_detail_ref.py process --runid 123456 --months 12 --update  # 過去12ヶ月分を参照
  
  # 分析のみ（更新なし）
  python generate_detail_ref.py process --runid 123456                # 分析のみ
  python generate_detail_ref.py process --recent 1                    # 過去1ヶ月分を分析のみ
'''
    )
    
    # サブコマンドを追加
    subparsers = parser.add_subparsers(dest='command', help='実行する処理')
    
    # processサブコマンド
    process_parser = subparsers.add_parser('process', help='データ参照関係生成処理')
    process_parser.add_argument("--runid", type=str, help="処理対象のrun_id（単一: 123、範囲: 1,1000）（指定しない場合は未処理分を自動処理）")
    process_parser.add_argument("--recent", type=int, help="過去X ヶ月以内のrun_idを処理対象とする（例: 3で過去3ヶ月）")
    process_parser.add_argument("--limit", type=int, default=100, help="一度に処理するrun数の上限（デフォルト: 100）")
    process_parser.add_argument("--months", type=int, default=6, help="過去何ヶ月分のデータを取得するか（デフォルト: 6）")
    process_parser.add_argument("--update", action='store_true', default=False, help="データベースに実際に保存する")
    
    # statsサブコマンド
    stats_parser = subparsers.add_parser('stats', help='統計情報を表示')
    
    args = parser.parse_args()
    
    # コマンドが指定されていない場合はエラー
    if args.command is None:
        parser.print_help()
        LOGGER.error("実行する処理を指定してください（process, stats）")
        exit(1)
    
    LOGGER.info(f"実行引数: {args}")
    
    # データベース接続
    DB = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE, max_disp_len=200)
    
    try:
        if args.command == 'stats':
            # 統計情報表示（is_refフラグベース）
            # 成功したRUN総数を取得
            total_sql = "SELECT COUNT(*) as total_runs FROM estate_run WHERE is_success = true"
            total_df = DB.select_sql(total_sql)
            total_runs = total_df.iloc[0]['total_runs'] if not total_df.empty else 0
            
            # 参照関係処理済みrun数を取得（is_ref=true）
            processed_sql = "SELECT COUNT(*) as processed_runs FROM estate_run WHERE is_success = true AND is_ref = true"
            processed_df = DB.select_sql(processed_sql)
            processed_runs = processed_df.iloc[0]['processed_runs'] if not processed_df.empty else 0
            
            # 参照関係未処理run数を取得（is_ref=false）
            pending_sql = "SELECT COUNT(*) as pending_runs FROM estate_run WHERE is_success = true AND is_ref = false"
            pending_df = DB.select_sql(pending_sql)
            pending_runs = pending_df.iloc[0]['pending_runs'] if not pending_df.empty else 0
            
            # 処理進捗率を計算
            progress_percent = (processed_runs / total_runs * 100) if total_runs > 0 else 0
            
            LOGGER.info("=== 処理統計 ===")
            LOGGER.info(f"成功したRUN総数: {total_runs:,}")
            LOGGER.info(f"処理済みRUN数: {processed_runs:,}")
            LOGGER.info(f"未処理RUN数: {pending_runs:,}")
            LOGGER.info(f"処理進捗: {progress_percent:.1f}%")
            
        elif args.command == 'process':
            # データ参照関係生成処理（最適化版）
            if args.runid or args.recent:
                run_ids = parse_runid_range(args.runid) if args.runid else None
            else:
                # 未処理分を自動処理（is_ref=falseのrun_idを対象）
                run_ids = get_unprocessed_runs(DB, args.limit)["id_run"].tolist()
            df, run_id_min, run_id_max = get_extended_runs_data(DB, run_ids=run_ids, recent_months=args.recent, months_back=args.months)
            for id_run, id_main, timestamp in df.loc[(df["id_run"] >= run_id_min) & (df["id_run"] <= run_id_max), ["id_run", "id_main", "timestamp"]].to_numpy():
                target_id_runs = df.loc[(df["id_main"] == id_main) & (df["timestamp"] >= (timestamp - timedelta(days=args.months * 31))) & (df["id_run"] <= id_run), "id_run"].tolist()
                dfwk = get_keys_by_target_id_runs(DB, target_id_runs)
                dfwk = pd.merge(dfwk, df[["id_run", "timestamp"]], how="left", on="id_run")
                dfwk = dfwk.sort_values(["id_key", "timestamp"], ascending=False).reset_index(drop=True).groupby("id_key")["id_run"].first().reset_index()
                dfwk.columns = dfwk.columns.str.replace("id_run", "id_run_ref")
                dfwk["id_run"] = id_run
                if args.update:
                    DB.set_sql(f"DELETE FROM estate_detail_ref WHERE id_run = {id_run};")
                    DB.insert_from_df(dfwk, "estate_detail_ref", is_select=True, set_sql=True)
                    DB.set_sql(f"UPDATE estate_run SET is_ref = true WHERE id = {id_run};")
                    DB.execute_sql()
                    LOGGER.info(f"run_id={id_run}: {len(dfwk)}件の参照関係を保存", color=["BOLD", "GREEN"])
                else:
                    LOGGER.info(f"run_id={id_run}: {len(dfwk)}件の参照関係を生成（--update未指定のため保存なし）")
    except Exception as e:
        LOGGER.error(f"処理中にエラーが発生しました: {e}", color=["BOLD", "RED"])
        raise