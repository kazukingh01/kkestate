#!/usr/bin/env python3
"""
不動産データ処理のメインスクリプト
コマンドライン引数でオプションを指定して実行
"""

import argparse
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from kklogger import set_logger
from main.process.processor import EstateProcessor

LOGGER = set_logger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='不動産データ処理ツール')
    parser.add_argument("--update", action='store_true', default=False, help='データベース更新処理を実行')
    parser.add_argument("--process", action='store_true', default=False, help='データクレンジング処理を実行')
    parser.add_argument("--batchsize", type=int, default=100, help='バッチ処理のサイズ（デフォルト: 100）')
    parser.add_argument("--stats", action='store_true', default=False, help='処理統計を表示')
    parser.add_argument("--runid", type=int, help='特定のrun_idのみを処理')
    parser.add_argument("--verbose", action='store_true', default=False, help='詳細ログを出力')
    parser.add_argument("--all", action='store_true', default=False, help='全てのキーを処理（LIMITなし）')
    parser.add_argument("--keyid", type=int, help='特定のestate_mst_key.idのみを処理')
    
    args = parser.parse_args()
    LOGGER.info(f"{args}")
    
    try:
        processor = EstateProcessor()
        
        # キーマッピング分析・更新
        if args.update:
            LOGGER.info("キーマッピング分析・更新を開始", color=["BOLD", "GREEN"])
            processor.update_key_mapping(update_db=True, limit_all=args.all, specific_key_id=args.keyid)
            LOGGER.info("キーマッピング分析・更新が完了しました", color=["BOLD", "GREEN"])
        else:
            # デフォルトでは分析のみ実行（更新なし）
            LOGGER.info("キーマッピング分析を開始（更新なし）", color=["BOLD", "GREEN"])
            processor.update_key_mapping(update_db=False, limit_all=args.all, specific_key_id=args.keyid)
            LOGGER.info("キーマッピング分析が完了しました", color=["BOLD", "GREEN"])
        
        # 統計表示
        if args.stats:
            stats = processor.get_processing_stats()
            LOGGER.info("=== 処理統計 ===")
            LOGGER.info(f"成功したRUN総数: {stats['total_successful_runs']:,}")
            LOGGER.info(f"処理済みRUN数: {stats['processed_runs']:,}")
            LOGGER.info(f"未処理RUN数: {stats['unprocessed_runs']:,}")
            
            if stats['total_successful_runs'] > 0:
                progress = (stats['processed_runs'] / stats['total_successful_runs']) * 100
                LOGGER.info(f"処理進捗: {progress:.1f}%")
        
        # 単一run_idの処理
        if args.runid:
            LOGGER.info(f"run_id {args.runid} の処理を開始", color=["BOLD", "CYAN"])
            success = processor.process_single_run(args.runid)
            if success:
                LOGGER.info(f"run_id {args.runid} の処理が成功しました", color=["BOLD", "CYAN"])
            else:
                LOGGER.error(f"run_id {args.runid} の処理が失敗しました")
                sys.exit(1)
        
        # バッチ処理
        elif args.process:
            LOGGER.info("データクレンジング処理を開始", color=["BOLD", "GREEN"])
            result = processor.process_batch(args.batchsize)
            
            if result['total'] == 0:
                LOGGER.warning("処理対象のデータがありません")
            else:
                success_rate = (result['success'] / result['total']) * 100
                LOGGER.info(f"処理完了: {result['success']}/{result['total']} ({success_rate:.1f}%)", color=["BOLD", "GREEN"])
                
                if result['failed'] > 0:
                    LOGGER.warning(f"失敗した処理: {result['failed']}件")
        
        # 処理が何も指定されていない場合のメッセージは表示しない
        # （デフォルトで分析が実行されるため）
            
    except KeyboardInterrupt:
        LOGGER.warning("処理が中断されました")
        sys.exit(1)
    except Exception as e:
        LOGGER.error(f"予期しないエラーが発生しました: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)