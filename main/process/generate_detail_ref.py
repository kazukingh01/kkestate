"""
データ参照関係生成処理 (generate_detail_ref.py)

目的:
- estate_detail_refテーブルにデータ参照関係を生成
- 特定のrun_idに対して、半年以内の同一物件の最新データを参照
- データ節約のため省略されたレコードを補完するための参照情報を作成

処理概要:
1. 指定されたrun_idに対して、その日時以前かつ過去半年以内の同一物件データを取得
2. 各id_keyに対して最新のデータを特定（sort_values + groupby + first）
3. estate_detail_refテーブルに参照関係を保存
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

def get_run_info(db: DBConnector, run_id: int) -> dict:
    """
    指定されたrun_idの情報を取得
    
    Args:
        db: データベース接続
        run_id: 対象のrun_id
        
    Returns:
        dict: run情報（id_main, timestamp等）
    """
    sql = f"""
    SELECT id, id_main, timestamp 
    FROM estate_run 
    WHERE id = {run_id}
    """
    df = db.select_sql(sql)
    
    if df.empty:
        raise ValueError(f"run_id {run_id} が見つかりません")
    
    return df.iloc[0].to_dict()

def get_historical_data(db: DBConnector, run_info: dict, months_back: int = 6) -> pd.DataFrame:
    """
    指定されたrun_idの日時以前かつ過去指定月以内の同一物件データを取得
    
    Args:
        db: データベース接続
        run_info: 対象run情報
        months_back: 過去何ヶ月分取得するか
        
    Returns:
        pd.DataFrame: 履歴データ
    """
    # 日時範囲を計算
    target_date = run_info['timestamp']
    start_date = target_date - timedelta(days=months_back * 30)  # 概算
    
    sql = f"""
    SELECT 
        r.id as id_run,
        r.id_main,
        r.timestamp,
        d.id_key,
        d.value
    FROM estate_run r
    JOIN estate_detail d ON r.id = d.id_run
    WHERE r.id_main = {run_info['id_main']}
      AND r.timestamp >= '{start_date}'
      AND r.timestamp <= '{target_date}'
      AND r.is_success = true
    ORDER BY r.id, d.id_key
    """
    
    df = db.select_sql(sql)
    
    LOGGER.info(f"取得した履歴データ: {len(df)}件", color=["BOLD", "GREEN"])
    return df

def generate_reference_data(historical_df: pd.DataFrame, target_run_id: int) -> pd.DataFrame:
    """
    データ参照関係を生成
    
    Args:
        historical_df: 履歴データ
        target_run_id: 対象のrun_id
        
    Returns:
        pd.DataFrame: 参照関係データ
    """
    if historical_df.empty:
        LOGGER.warning("履歴データが空です")
        return pd.DataFrame(columns=['id_run', 'id_key', 'id_run_ref'])
    
    # 各id_keyに対して最新のデータを取得
    # sort_values("id_run", ascending=False).groupby("id_key").first()
    latest_data = (historical_df
                   .sort_values("id_run", ascending=False)
                   .groupby("id_key")
                   .first()
                   .reset_index())
    
    # 参照関係データを作成
    ref_data = pd.DataFrame({
        'id_run': target_run_id,
        'id_key': latest_data['id_key'],
        'id_run_ref': latest_data['id_run']
    })
    
    LOGGER.info(f"生成した参照関係データ: {len(ref_data)}件", color=["BOLD", "GREEN"])
    return ref_data

def save_reference_data(db: DBConnector, ref_data: pd.DataFrame, update: bool = False) -> None:
    """
    参照関係データをestate_detail_refテーブルに保存
    
    Args:
        db: データベース接続
        ref_data: 参照関係データ
        update: 更新フラグ
    """
    if ref_data.empty:
        LOGGER.warning("保存するデータがありません")
        return
    
    if not update:
        LOGGER.info("--update フラグが指定されていないため、データベースには保存しません")
        LOGGER.info(f"保存予定データ: {len(ref_data)}件")
        return
    
    # 既存データの削除（同一run_idの場合）
    if len(ref_data) > 0:
        target_run_id = ref_data['id_run'].iloc[0]
        delete_sql = f"DELETE FROM estate_detail_ref WHERE id_run = {target_run_id}"
        db.set_sql(delete_sql)
        db.insert_from_df(ref_data, "estate_detail_ref", is_select=True, set_sql=True)
        db.execute_sql()
        # 新規データの保存
        LOGGER.info(f"estate_detail_refテーブルに保存完了: run_id={target_run_id}, {len(ref_data)}件", color=["BOLD", "GREEN"])

def process_run_id(db: DBConnector, run_id: int, months_back: int = 6, update: bool = False) -> None:
    """
    指定されたrun_idに対してデータ参照関係を生成・保存
    
    Args:
        db: データベース接続
        run_id: 対象のrun_id
        months_back: 過去何ヶ月分取得するか
        update: 更新フラグ
    """
    LOGGER.info(f"データ参照関係生成開始: run_id={run_id}, months_back={months_back}")
    
    # run情報取得
    run_info = get_run_info(db, run_id)
    LOGGER.info(f"対象run情報: id_main={run_info['id_main']}, timestamp={run_info['timestamp']}")
    
    # 履歴データ取得
    historical_df = get_historical_data(db, run_info, months_back)
    
    # 参照関係データ生成
    ref_data = generate_reference_data(historical_df, run_id)
    
    # データ保存
    save_reference_data(db, ref_data, update)
    
    LOGGER.info(f"データ参照関係生成完了: run_id={run_id}")

def get_target_runs_info(db: DBConnector, run_ids: list = None, recent_months: int = None, limit: int = 100) -> pd.DataFrame:
    """
    対象となるrun_idとtimestampを一括取得
    
    Args:
        db: データベース接続
        run_ids: 処理対象のrun_idリスト（指定時は範囲指定処理）
        recent_months: 過去Xヶ月以内のrun_idを処理対象とする
        limit: 処理するrun数の上限（未処理分自動処理時）
        
    Returns:
        pd.DataFrame: 対象run情報（id_run, id_main, timestamp）
    """
    if run_ids:
        # 範囲指定処理
        run_ids_str = ",".join(map(str, run_ids))
        sql = f"""
        SELECT id as id_run, id_main, timestamp
        FROM estate_run
        WHERE id IN ({run_ids_str})
          AND is_success = true
        ORDER BY id DESC
        """
    elif recent_months:
        # 直近X ヶ月以内の処理対象を取得（既存データは除く）
        recent_start_date = datetime.now() - timedelta(days=recent_months * 30)
        sql = f"""
        SELECT r.id as id_run, r.id_main, r.timestamp
        FROM estate_run r
        LEFT JOIN estate_detail_ref ref ON r.id = ref.id_run
        WHERE r.is_success = true
          AND r.timestamp >= '{recent_start_date}'
          AND ref.id_run IS NULL
        ORDER BY r.id DESC
        """
    else:
        # 未処理分自動処理
        sql = f"""
        SELECT r.id as id_run, r.id_main, r.timestamp
        FROM estate_run r
        LEFT JOIN estate_detail_ref ref ON r.id = ref.id_run
        WHERE r.is_success = true
          AND ref.id_run IS NULL
        ORDER BY r.id DESC
        LIMIT {limit}
        """
    
    target_runs_df = db.select_sql(sql)
    LOGGER.info(f"対象run情報取得: {len(target_runs_df)}件", color=["BOLD", "GREEN"])
    return target_runs_df

def process_multiple_runs(db: DBConnector, run_ids: list = None, recent_months: int = None, limit: int = 100, months_back: int = 6, update: bool = False) -> None:
    """
    複数のrun_idに対してデータ参照関係を生成（ループ処理版）
    
    Args:
        db: データベース接続
        run_ids: 処理対象のrun_idリスト（指定時は範囲指定処理）
        recent_months: 過去Xヶ月以内のrun_idを処理対象とする
        limit: 処理するrun数の上限（未処理分自動処理時）
        months_back: 過去何ヶ月分取得するか
        update: 更新フラグ
    """
    # Step 1: 対象run_idとtimestampを一括取得
    target_runs_df = get_target_runs_info(db, run_ids, recent_months, limit)
    
    if target_runs_df.empty:
        LOGGER.info("処理対象のrun_idがありません")
        return
    
    # 範囲指定時の既存データ削除
    if run_ids and update:
        run_ids_str = ",".join(map(str, run_ids))
        delete_sql = f"DELETE FROM estate_detail_ref WHERE id_run IN ({run_ids_str})"
        db.execute_sql(delete_sql)
        LOGGER.info(f"既存データを一括削除: {len(run_ids)}件")
    
    LOGGER.info(f"処理対象のrun_id: {len(target_runs_df)}件")
    
    # Step 2: 各run_idをループ処理
    for _, run_row in target_runs_df.iterrows():
        try:
            run_id = int(run_row['id_run'])
            id_main = int(run_row['id_main'])
            timestamp = run_row['timestamp']
            
            # 該当物件の半年以内の履歴データを取得
            start_date = timestamp - timedelta(days=months_back * 30)
            
            sql = f"""
            SELECT 
                r.id as id_run,
                r.id_main,
                r.timestamp,
                d.id_key,
                d.value
            FROM estate_run r
            JOIN estate_detail d ON r.id = d.id_run
            WHERE r.id_main = {id_main}
              AND r.timestamp >= '{start_date}'
              AND r.timestamp <= '{timestamp}'
              AND r.is_success = true
            ORDER BY r.id, d.id_key
            """
            
            historical_df = db.select_sql(sql)
            
            if historical_df.empty:
                LOGGER.info(f"run_id={run_id}: 履歴データなし")
                continue
            
            # 各id_keyに対して最新のデータを取得
            latest_data = (historical_df
                           .sort_values("id_run", ascending=False)
                           .groupby("id_key")
                           .first()
                           .reset_index())
            
            # 参照関係データを作成
            ref_data = pd.DataFrame({
                'id_run': run_id,
                'id_key': latest_data['id_key'],
                'id_run_ref': latest_data['id_run']
            })
            
            # 単一run_idの既存データ削除・保存
            if update:
                if not ref_data.empty:
                    delete_sql = f"DELETE FROM estate_detail_ref WHERE id_run = {run_id}"
                    db.set_sql(delete_sql)
                    db.insert_from_df(ref_data, "estate_detail_ref", is_select=True, set_sql=True)
                    db.execute_sql()
                    LOGGER.info(f"run_id={run_id}: {len(ref_data)}件の参照関係を保存", color=["BOLD", "GREEN"])
                else:
                    LOGGER.info(f"run_id={run_id}: 保存するデータなし")
            else:
                LOGGER.info(f"run_id={run_id}: {len(ref_data)}件の参照関係を生成（--update未指定のため保存なし）")
                
        except Exception as e:
            LOGGER.error(f"run_id={run_row['id_run']} の処理でエラー: {e}", color=["BOLD", "RED"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="データ参照関係生成処理")
    parser.add_argument("--runid", type=str, help="処理対象のrun_id（単一: 123、範囲: 1,1000）（指定しない場合は未処理分を自動処理）")
    parser.add_argument("--recent", type=int, help="過去X ヶ月以内のrun_idを処理対象とする（例: 3で過去3ヶ月）")
    parser.add_argument("--limit", type=int, default=100, help="一度に処理するrun数の上限（デフォルト: 100）")
    parser.add_argument("--months", type=int, default=6, help="過去何ヶ月分のデータを取得するか（デフォルト: 6）")
    parser.add_argument("--update", action='store_true', default=False, help="データベースに実際に保存する")
    parser.add_argument("--stats", action='store_true', default=False, help="統計情報を表示")
    
    args = parser.parse_args()
    LOGGER.info(f"実行引数: {args}")
    
    # データベース接続
    DB = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE, max_disp_len=200)
    
    try:
        if args.stats:
            # 統計情報表示
            stats_sql = """
            SELECT 
                COUNT(*) as total_runs,
                COUNT(CASE WHEN ref.id_run IS NOT NULL THEN 1 END) as processed_runs,
                COUNT(CASE WHEN ref.id_run IS NULL THEN 1 END) as pending_runs
            FROM estate_run r
            LEFT JOIN estate_detail_ref ref ON r.id = ref.id_run
            WHERE r.is_success = true
            """
            stats_df = DB.select_sql(stats_sql)
            LOGGER.info("=== 統計情報 ===", color=["BOLD", "BLUE"])
            LOGGER.info(f"総run数: {stats_df.iloc[0]['total_runs']}")
            LOGGER.info(f"処理済み: {stats_df.iloc[0]['processed_runs']}")
            LOGGER.info(f"未処理: {stats_df.iloc[0]['pending_runs']}")
            
        elif args.runid:
            # run_id範囲指定処理
            run_ids = parse_runid_range(args.runid)
            if len(run_ids) == 1:
                # 単一のrun_id処理
                process_run_id(DB, run_ids[0], args.months, args.update)
            else:
                # 複数のrun_id処理（範囲指定・上書きモード）
                process_multiple_runs(DB, run_ids, None, args.limit, args.months, args.update)
        elif args.recent:
            # 直近X ヶ月以内の処理
            process_multiple_runs(DB, None, args.recent, args.limit, args.months, args.update)
        else:
            # 未処理分を自動処理
            process_multiple_runs(DB, None, None, args.limit, args.months, args.update)
            
    except Exception as e:
        LOGGER.error(f"処理中にエラーが発生しました: {e}", color=["BOLD", "RED"])
        raise