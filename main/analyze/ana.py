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
    args = parser.parse_args()
    LOGGER.info(f"実行引数: {args}")
    
    # connection
    DB  = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE, max_disp_len=200)
    df  = DB.select_sql("select * from reinfolib_land where year between 2020 and 2024;")
    url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
    list_ret = []
    locations = df.groupby("location")["location"].first().sort_values().tolist()
    total = len(locations)
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
        if len(res) == 0:
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
        assert len(res) == 1, f"list length is not 1: {res}"
        longitude, latitude = res[0]["geometry"]["coordinates"]
        if args.update:
            DB.execute_sql(f"""
                INSERT INTO estate_mst_location (location, longitude, latitude)
                VALUES ('{x.replace("'", "''")}', {longitude}, {latitude})
                ON CONFLICT (location) DO UPDATE SET
                    longitude = EXCLUDED.longitude,
                    latitude = EXCLUDED.latitude,
                    sys_updated = CURRENT_TIMESTAMP
            """)
        else:
            LOGGER.info(f"  [ドライラン] 緯度: {latitude}, 経度: {longitude}")

