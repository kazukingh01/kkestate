"""
住所から緯度経度を取得してDBに格納するスクリプト

対応テーブル:
- land: reinfolib_land 地価公示データの住所（2020-2024年）
- ext: estate_main_extended 物件基本情報の住所（全件）
- clean: estate_cleaned クレンジング済み住所データ

使用例:
python make_location_mst.py --table land --update --skip
python make_location_mst.py --table ext --update
python make_location_mst.py --table clean --limit 5000 --update --skip
"""

import argparse
import requests
import pandas as pd
from kkpsgre.connector import DBConnector
from kklogger import set_logger
from kkestate.config.psgre import HOST, PORT, USER, PASS, DBNAME, DBTYPE
LOGGER    = set_logger(__name__)


if __name__ == "__main__":
    # 引数処理
    parser = argparse.ArgumentParser(description="住所から緯度経度を取得してDBに格納")
    parser.add_argument("--update", action="store_true", default=False, help="データベース更新を実行")
    parser.add_argument("--skip", action="store_true", default=False, help="既存データがある場合はスキップ")
    parser.add_argument("--table", type=str, choices=["land", "ext", "clean"], 
                        default="land", help="対象テーブル選択 (land: reinfolib_land, ext: estate_main_extended, clean: estate_cleaned)")
    parser.add_argument("--limit", type=int, default=None, help="処理件数の上限")
    args = parser.parse_args()
    LOGGER.info(f"実行引数: {args}")
    
    # connection
    DB  = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE, max_disp_len=200)
    
    # テーブル別のSQL構築
    if args.table == "land":
        sql = "SELECT location FROM reinfolib_land WHERE year BETWEEN 2020 AND 2024"
        if args.limit:
            sql += f" LIMIT {args.limit}"
        LOGGER.info(f"対象テーブル: reinfolib_land (2020-2024年)")
    elif args.table == "ext":
        sql = "SELECT location FROM estate_main_extended WHERE location IS NOT NULL"
        # extテーブルは全件処理（limitは適用しない）
        LOGGER.info(f"対象テーブル: estate_main_extended (全件)")
    elif args.table == "clean":
        # estate_mst_cleanedで"住所"となっているid_cleanedを取得
        sql = """
        SELECT (value_cleaned->>'location') as location
        FROM estate_cleaned
        WHERE id_cleaned in (SELECT id FROM estate_mst_cleaned WHERE name = '住所')
        """
        if args.limit:
            sql += f" LIMIT {args.limit}"
        LOGGER.info(f"対象テーブル: estate_cleaned (住所クレンジング済み)")
    
    df = DB.select_sql(sql)
    
    if df.empty:
        LOGGER.warning(f"{args.table}から住所データを取得できませんでした")
        exit(1)
    
    LOGGER.info(f"取得した住所データ: {len(df)}件")
    
    # 重複除去後の住所数を確認
    locations = df.groupby("location")["location"].first().sort_values().tolist()
    total = len(locations)
    LOGGER.info(f"重複除去後の住所数: {total}件")
    
    url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
    for i, x in enumerate(locations, 1):
        # skipフラグがある場合、既存データをチェック
        if args.skip:
            check_result = DB.select_sql(f"SELECT 1 FROM estate_mst_location WHERE location = '{x.replace('\'', '\'\'')}'")
            if len(check_result) > 0:
                LOGGER.info(f"[{i:5d}/{total:5d}] {x} - スキップ（既存データあり）")
                continue
        
        LOGGER.info(f"[{i:5d}/{total:5d}] {x}")
        tmp = f"{url}{x}"
        res = requests.get(tmp)
        assert res.status_code == 200, f"status code is not 200: {x}"
        res = res.json()
        if len(res) != 1:
            LOGGER.warning(f"no result: {x}")
            if args.update:
                DB.execute_sql(f"""
                    INSERT INTO estate_mst_location (location, longitude, latitude)
                    VALUES ('{x.replace("'", "''")}', NULL, NULL)
                    ON CONFLICT (location) DO UPDATE SET
                        sys_updated = CURRENT_TIMESTAMP
                """)
            else:
                LOGGER.info("  [ドライラン] INSERT をスキップ")
            continue
        longitude, latitude = res[0]["geometry"]["coordinates"]
        if args.update:
            DB.execute_sql(f"""
                INSERT INTO estate_mst_location (location, longitude, latitude)
                VALUES ('{x.replace("'", "''")}', {longitude:.15f}, {latitude:.15f})
                ON CONFLICT (location) DO UPDATE SET
                    longitude = EXCLUDED.longitude,
                    latitude = EXCLUDED.latitude,
                    sys_updated = CURRENT_TIMESTAMP
            """)
        else:
            LOGGER.info(f"  [ドライラン] 緯度: {latitude:.15f}, 経度: {longitude:.15f}")

