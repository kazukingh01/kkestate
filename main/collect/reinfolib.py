import argparse
import os
import time
import re
import zipfile
import tempfile
import shutil
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright, expect
from kklogger import set_logger
import pandas as pd
from kkpsgre.connector import DBConnector
from kkestate.config.psgre import HOST, PORT, USER, PASS, DBNAME, DBTYPE

LOGGER = set_logger(__name__)


def download_land_prices(playwright: Playwright, year: int, prefecture_code: str, headless: bool = False) -> pd.DataFrame:
    """
    国土交通省の地価公示・地価調査データをスクレイピングしてDataFrameに変換
    
    Args:
        playwright: Playwright instance
        year: 対象年（例: 2024）
        prefecture_code: 都道府県コード（01-47の2桁）
        headless: ヘッドレスモードで実行するか
        
    Returns:
        pd.DataFrame: スクレイピングしたデータ
    """
    LOGGER.info(f"地価公示・地価調査データのスクレイピング開始: {year}年 都道府県コード{prefecture_code} (headless={headless})")
    
    # 年号変換関数
    def convert_year_to_era(year: int) -> str:
        """西暦を和暦表示に変換"""
        if year >= 2019:
            # 令和（2019年〜）
            reiwa_year = year - 2018
            if reiwa_year == 1:
                return f"{year}"  # value は西暦のまま（selectのvalue）
            else:
                return f"{year}"
        elif year >= 1989:
            # 平成（1989年〜2018年）
            if year == 1989:
                return f"{year}"  # 昭和64年/平成元年の特殊ケース
            else:
                return f"{year}"
        else:
            # 昭和（〜1988年）
            return f"{year}"
    
    # ※ダウンロードディレクトリ作成は呼び出し側で実行
    
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()
    
    try:
        # ページアクセス
        page.goto("https://www.reinfolib.mlit.go.jp/landPrices/")
        page.wait_for_load_state("networkidle")
        LOGGER.info("ページ読み込み完了")
        
        # 1. 区分: 全てチェック（デフォルトでチェック済みだが念のため確認）
        checkboxes = [
            "#chkLandPricesPublic",      # 地価公示
            "#chkTransactionPriceSurvey" # 地価調査
        ]
        
        for checkbox_id in checkboxes:
            checkbox = page.locator(checkbox_id)
            if not checkbox.is_checked():
                checkbox.check()
                time.sleep(0.2)
        LOGGER.info("区分: 地価公示・地価調査の両方をチェック")
        
        # 2. 地域: 都道府県選択
        # 地域選択ボタンをクリック
        page.get_by_role("button", name="地域選択").click()
        time.sleep(0.5)
        
        # ポップアップが表示されるまで待機
        page.wait_for_selector("#cboPrefectures", state="visible")
        
        # 都道府県選択
        page.locator("#cboPrefectures").select_option(prefecture_code)
        time.sleep(0.5)
        LOGGER.info(f"都道府県コード {prefecture_code} を選択")
        
        # 「変更」ボタンをクリック（ポップアップ内の）
        page.locator("#btnDecisionArea").click()
        time.sleep(0.5)
        
        # 3. 用途区分: 全てチェック
        use_category_checkboxes = [
            "#chkResidential",             # 住宅地
            "#chkCommercial",              # 商業地
            "#chkIndustrial",              # 工業地
            "#chkProspectiveResidential",  # 宅地見込地
            "#chkQuasiIndustrial",         # 準工業地
            "#chkLandUrbanization",        # 市街化調整区域内の現況宅地
            "#chkForestLandUrbanization",  # 市街化調整区域内の現況林地(地価公示のみ)
            "#chkForestLand"               # 林地(都道府県地価調査のみ)
        ]
        
        for checkbox_id in use_category_checkboxes:
            checkbox = page.locator(checkbox_id)
            if not checkbox.is_checked():
                checkbox.check()
                time.sleep(0.1)
        LOGGER.info("用途区分: 全ての項目をチェック")
        
        # 4. 調査年: 上限・下限に同一年を設定
        year_value = str(year)
        page.locator("#cmbSeasonFrom").select_option(year_value)
        time.sleep(0.2)
        page.locator("#cmbSeasonTo").select_option(year_value)
        time.sleep(0.2)
        LOGGER.info(f"調査年: {year}年 を上限・下限に設定")
        
        # 一覧表示ボタンをクリック
        page.locator("#btnDislpayList").click()
        time.sleep(1)
        page.wait_for_load_state("networkidle")
        LOGGER.info("一覧表示をクリック")
        
        # 検索結果件数チェック
        result_count_text = page.locator("text=現在の条件での検索結果：").text_content()
        count_match = re.search(r"(\d+)件", result_count_text)
        if count_match:
            result_count = int(count_match.group(1))
            LOGGER.info(f"検索結果: {result_count}件")
            
            # 検索結果が0件の場合は警告して空のDataFrameを返す
            if result_count == 0:
                LOGGER.warning(f"検索結果: 0件 - データなし", color=["BOLD", "YELLOW"])
                return pd.DataFrame()
            
            if result_count > 10000:
                LOGGER.error(f"検索結果が10,000件を超えています: {result_count}件", color=["BOLD", "RED"])
                raise ValueError(f"検索結果が上限を超えています: {result_count}件 > 10,000件")
        else:
            LOGGER.warning("検索結果件数を取得できませんでした")
        
        # 一覧表示の結果が表示されるまで待機
        LOGGER.info("一覧表示の結果を確認")
        
        # DataFrameリストを初期化
        all_dataframes = []
        page_number = 1
        
        while True:
            LOGGER.info(f"ページ {page_number} の表をスクレイピング中...")
            
            try:
                # 現在のページのHTMLを取得
                html_content = page.content()
                
                # pandas.read_html()で表を取得
                tables = pd.read_html(html_content, attrs={'id': 'result'})
                
                if tables and len(tables) > 0:
                    df = tables[0]  # 最初（唯一）のテーブルを取得
                    
                    # 鑑定評価書のURLを抽出してDataFrameに追加
                    try:
                        # 鑑定評価書リンクを全て取得
                        appraisal_links = page.locator("a[id^='lnkReport_']").all()
                        appraisal_urls = []
                        
                        for link in appraisal_links:
                            href = link.get_attribute("href")
                            if href:
                                # 相対URLを絶対URLに変換
                                full_url = f"https://www.reinfolib.mlit.go.jp{href}"
                                appraisal_urls.append(full_url)
                            else:
                                appraisal_urls.append(None)
                        
                        # DataFrameに鑑定評価書URLカラムを追加
                        if len(appraisal_urls) == len(df):
                            df['鑑定評価書URL'] = appraisal_urls
                            LOGGER.info(f"鑑定評価書URL {len([url for url in appraisal_urls if url])}件を追加")
                        elif len(appraisal_urls) > 0:
                            # URLの数がDataFrameの行数と一致しない場合、Noneで埋める
                            urls_padded = appraisal_urls + [None] * (len(df) - len(appraisal_urls))
                            df['鑑定評価書URL'] = urls_padded[:len(df)]
                            LOGGER.info(f"鑑定評価書URL {len(appraisal_urls)}件を追加（行数調整済み）")
                        else:
                            df['鑑定評価書URL'] = None
                            LOGGER.info("鑑定評価書URLなし")
                            
                    except Exception as e:
                        LOGGER.warning(f"鑑定評価書URL抽出中にエラー: {e}")
                        df['鑑定評価書URL'] = None
                    
                    all_dataframes.append(df)
                    LOGGER.info(f"ページ {page_number}: {len(df)}行 x {len(df.columns)}列を取得")
                    
                    # データフレームの先頭5行を表示
                    LOGGER.info(f"ページ {page_number} のデータサンプル:")
                    LOGGER.info(f"\n{df.head(5)}")
                    
                else:
                    LOGGER.warning(f"ページ {page_number}: テーブルが見つかりませんでした")
                
            except Exception as e:
                LOGGER.error(f"ページ {page_number} のスクレイピング中にエラー: {e}")
                break
            
            # 次のページへ
            try:
                # 現在のページ番号を取得（"1/174"形式から"1"を抽出）
                page_indicator = page.locator("text=/\\d+/\\d+/").text_content()
                current_page = int(page_indicator.split('/')[0])
                total_pages = int(page_indicator.split('/')[1])
                
                LOGGER.info(f"現在のページ: {current_page}/{total_pages}")
                
                # 最終ページの場合は終了
                if current_page >= total_pages:
                    LOGGER.info("最終ページに到達しました. スクレイピング完了")
                    break
                
                # 次のページ番号
                next_page = current_page + 1
                next_button_id = f"#LandPricesPager{next_page}"
                
                # 次のページボタンを探す
                next_button = page.locator(next_button_id)
                
                # ボタンが存在するかチェック
                if next_button.is_visible():
                    LOGGER.info(f"ページ {next_page} のボタンをクリック中...")
                    next_button.click()
                    # ページ変更を待機（最大10秒）
                    page_changed = False
                    for i in range(20):  # 0.5秒 × 20 = 10秒
                        time.sleep(0.25)
                        try:
                            new_page_indicator = page.locator("text=/\\d+/\\d+/").text_content()
                            new_current_page = int(new_page_indicator.split('/')[0])
                            if new_current_page == next_page:
                                page_changed = True
                                break
                        except:
                            pass  # ページ遷移中はエラーが発生する可能性
                    
                    if not page_changed:
                        LOGGER.warning("ページ変更が確認できませんでした. 終了します")
                        break
                    
                    # ネットワークの安定を待機
                    page.wait_for_load_state("networkidle", timeout=30000)
                    time.sleep(1)  # 追加の安全待機
                    page_number = next_page
                    LOGGER.info(f"ページ {page_number} に移動完了")
                else:
                    LOGGER.info(f"ページ {next_page} のボタンが見つかりません. スクレイピング完了")
                    break
                    
            except Exception as e:
                LOGGER.info(f"ページネーション終了: {e}")
                break
        
        # 全DataFrameを連結
        if all_dataframes:
            final_df = pd.concat(all_dataframes, ignore_index=True)
            # 鑑定評価書URLがあるデータの統計
            if '鑑定評価書URL' in final_df.columns:
                url_count = final_df['鑑定評価書URL'].notna().sum()
                LOGGER.info(f"鑑定評価書URLあり: {url_count}件 / {len(final_df)}件")
            
            LOGGER.info(f"全データ取得完了: {len(final_df)}行 x {len(final_df.columns)}列")
            
            LOGGER.info(f"スクレイピング完了", color=["BOLD", "GREEN"])
            return final_df
        else:
            raise ValueError("データが取得できませんでした")
        
    except Exception as e:
        LOGGER.error(f"スクレイピング中にエラーが発生: {e}", color=["BOLD", "RED"])
        raise
    finally:
        context.close()
        browser.close()


def download_estate_prices(playwright: Playwright, year: int, period: int, download_dir: str = "./downloads", headless: bool = False) -> str:
    """
    国土交通省の不動産取引価格情報をダウンロード
    
    Args:
        playwright: Playwright instance
        year: 対象年（例: 2024）
        period: 四半期（1-4）
        download_dir: ダウンロード保存先ディレクトリ
        headless: ヘッドレスモードで実行するか
        
    Returns:
        str: ダウンロードしたファイルパス
    """
    # 時期の値を生成（例: 2024年第4四半期 -> "20244"）
    season_value = f"{year}{period}"
    
    LOGGER.info(f"REINFOLIB からデータをダウンロード開始: {year}年第{period}四半期 (headless={headless})")
    
    # ダウンロードディレクトリ作成
    os.makedirs(download_dir, exist_ok=True)
    
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    
    try:
        # ページアクセス
        page.goto("https://www.reinfolib.mlit.go.jp/realEstatePrices/")
        page.wait_for_load_state("networkidle")
        
        # 地域: 全都道府県
        page.locator("#cmbPrefectures").select_option("99")
        LOGGER.info("地域: 全都道府県を選択")
        time.sleep(0.5)
        
        # 価格情報区分: 両方チェック（デフォルトで両方チェックされているはず）
        # 必要に応じてチェック状態を確認・設定
        checkbox1 = page.locator("#chkTransactionPrice")
        checkbox2 = page.locator("#chkClosedPrice")
        if not checkbox1.is_checked():
            checkbox1.check()
            time.sleep(0.5)
        if not checkbox2.is_checked():
            checkbox2.check()
            time.sleep(0.5)
        LOGGER.info("価格情報区分: 両方チェック")
        
        # 種類: すべて
        page.locator("#cmbKind").select_option("all")
        LOGGER.info("種類: すべてを選択")
        time.sleep(0.5)
        
        # 時期: 下限と上限に同じ値を設定
        page.locator("#cmbSeasonFrom").select_option(season_value)
        time.sleep(0.5)
        page.locator("#cmbSeasonTo").select_option(season_value)
        time.sleep(0.5)
        LOGGER.info(f"時期: {season_value}（{year}年第{period}四半期）を設定")
        
        # ダウンロード実行
        try:
            with page.expect_download(timeout=5000) as download_info:
                page.get_by_role("button", name="ダウンロード", exact=True).click()
            download = download_info.value
        except Exception:
            # タイムアウトした場合、ポップアップが表示されている可能性をチェック
            try:
                # ポップアップの「閉じる」ボタンを探す
                close_button = page.locator("#btnClose")
                if close_button.is_visible():
                    LOGGER.warning("ダウンロード用ファイルの作成中です. 後で再試行してください.")
                    close_button.click()
                    time.sleep(0.5)
                    import sys
                    sys.exit(1)  # 失敗を示す終了コード
            except:
                pass
            raise
        
        # ファイル保存
        filename = f"reinfolib_estate_{year}_{period}.zip"
        filepath = os.path.join(download_dir, filename)
        download.save_as(filepath)
        
        LOGGER.info(f"ダウンロード完了: {filepath}", color=["BOLD", "GREEN"])
        return filepath
        
    except Exception as e:
        LOGGER.error(f"ダウンロード中にエラーが発生: {e}", color=["BOLD", "RED"])
        raise
    finally:
        context.close()
        browser.close()


def upload_land_to_db(download_dir: str = "./downloads", update: bool = False, skip: bool = False):
    """
    land CSVファイルをデータベースにアップロード
    
    Args:
        download_dir: CSVファイルが格納されたディレクトリ
        update: データベース更新を実行するか
        skip: 既存データがある場合はスキップするか
    """
    LOGGER.info(f"Landデータのデータベースアップロード開始: {download_dir}")
    
    # データベース接続
    DB = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE, max_disp_len=200)
    
    # reinfolib_land_*.csv ファイルを探す
    csv_files = [f for f in os.listdir(download_dir) if f.startswith('reinfolib_land_') and f.endswith('.csv')]
    
    if not csv_files:
        LOGGER.warning(f"{download_dir} にreinfolib_land_*.csvファイルが見つかりません")
        return
    
    LOGGER.info(f"{len(csv_files)}個のCSVファイルを処理します")
    
    success_count = 0
    failed_count = 0
    
    for csv_file in sorted(csv_files):
        # ファイル名からyearとprefecture_codeを抽出 (reinfolib_land_YYYY_PP.csv)
        match = re.match(r'reinfolib_land_(\d{4})_(\d{2})\.csv', csv_file)
        if not match:
            LOGGER.warning(f"ファイル名が不正です: {csv_file}")
            failed_count += 1
            continue
        
        year = int(match.group(1))
        prefecture_code = match.group(2)
        
        # skipフラグがある場合、既存データをチェック
        if skip:
            check_sql = f"SELECT COUNT(*) FROM reinfolib_land WHERE year = {year} AND prefecture_code = '{prefecture_code}'"
            result = DB.select_sql(check_sql)
            if len(result) > 0 and result.iloc[0, 0] > 0:
                LOGGER.info(f"スキップ: {csv_file} (Year: {year}, Prefecture: {prefecture_code}) - 既存データあり")
                continue
        
        LOGGER.info(f"処理中: {csv_file} (Year: {year}, Prefecture: {prefecture_code})")
        
        csv_path = os.path.join(download_dir, csv_file)
        
        # CSVを読み込み（UTF-8 with BOM）
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig', skiprows=1)
        except pd.errors.EmptyDataError:
            LOGGER.warning(f"{csv_file}: 空のCSVファイル")
            failed_count += 1
            continue
        
        # 空のDataFrameの場合はスキップ
        if df.empty:
            LOGGER.info(f"{csv_file}: データなし")
            failed_count += 1
            continue
        
        # データクレンジング関数
        def clean_price(price_str):
            """価格データをクレンジング（241,000(円/㎡) -> 241000）"""
            if pd.isna(price_str):
                return None
            price_str = str(price_str).replace(',', '').replace('(円/㎡)', '').replace('(円/10a)', '')
            try:
                return int(price_str)
            except:
                return None
        
        def clean_distance(distance_str):
            """距離データをクレンジング（1,300m -> 1300、近接 -> 0、接面 -> -1）"""
            if pd.isna(distance_str):
                return None
            distance_str = str(distance_str)
            if '近接' in distance_str:
                return 0
            elif '接面' in distance_str:
                return -1
            elif '駅前広場接面' in distance_str:
                return -2
            else:
                # 数値部分を抽出
                distance_str = distance_str.replace(',', '').replace('m', '').replace('ｍ', '')
                try:
                    return int(distance_str)
                except:
                    return None
        
        def clean_area(area_str):
            """地積データをクレンジング（101(㎡) -> 101）"""
            if pd.isna(area_str):
                return None
            area_str = str(area_str).replace('(㎡)', '').replace(',', '')
            try:
                return int(area_str)
            except:
                return None
        
        def clean_width(width_str):
            """幅員データをクレンジング（4.0m -> 4.0）"""
            if pd.isna(width_str):
                return None
            width_str = str(width_str).replace('m', '').replace('ｍ', '').replace(',', '')
            try:
                return float(width_str)
            except:
                return None
        
        def clean_ratio(ratio_str):
            """建蔽率・容積率をクレンジング（60(%) -> 60）"""
            if pd.isna(ratio_str):
                return None
            ratio_str = str(ratio_str).replace('(%)', '').replace(',', '')
            try:
                return int(ratio_str)
            except:
                return None
        
        def clean_reference_number(ref_str):
            """標準地番号の重複文字列をクリーニング（春日-1春日-1 -> 春日-1）"""
            if pd.isna(ref_str):
                return None
            ref_str = str(ref_str).strip()
            
            # 文字列長が偶数で、前半と後半が同じ場合は前半のみを返す
            if len(ref_str) % 2 == 0:
                mid = len(ref_str) // 2
                first_half = ref_str[:mid]
                second_half = ref_str[mid:]
                if first_half == second_half:
                    return first_half
            
            return ref_str
        
        def parse_survey_date(date_str):
            """調査基準日をパース（令和6年7月1日 -> 2024-07-01）"""
            if pd.isna(date_str):
                return None
            # 令和、平成、昭和の変換
            import datetime
            date_str = str(date_str)
            
            # 令和の場合
            if '令和' in date_str:
                match = re.match(r'令和(\d+)年(\d+)月(\d+)日', date_str)
                if match:
                    year = 2018 + int(match.group(1))  # 令和元年 = 2019
                    month = int(match.group(2))
                    day = int(match.group(3))
                    return datetime.date(year, month, day)
            # 平成の場合
            elif '平成' in date_str:
                match = re.match(r'平成(\d+)年(\d+)月(\d+)日', date_str)
                if match:
                    year = 1988 + int(match.group(1))  # 平成元年 = 1989
                    month = int(match.group(2))
                    day = int(match.group(3))
                    return datetime.date(year, month, day)
            # 昭和の場合
            elif '昭和' in date_str:
                match = re.match(r'昭和(\d+)年(\d+)月(\d+)日', date_str)
                if match:
                    year = 1925 + int(match.group(1))  # 昭和元年 = 1926
                    month = int(match.group(2))
                    day = int(match.group(3))
                    return datetime.date(year, month, day)
            
            return None
        
        # カラム名マッピング（日本語から英語への変換）
        def clean_column_name(col_name):
            """カラム名から余計な文字列を除去して正規化"""
            import re
            # 先頭の文字列で厳密にマッチング
            if col_name.startswith('標準地番号'):
                return 'reference_number'
            elif col_name.startswith('調査基準日'):
                return 'survey_date'
            elif col_name.startswith('所在及び地番'):
                return 'location'
            elif col_name.startswith('住居表示'):
                return 'residential_address'
            elif col_name.startswith('価格(円/㎡)'):
                return 'price_per_sqm'
            elif col_name.startswith('名称'):
                return 'station_name'
            elif col_name.startswith('距離'):
                return 'station_distance'
            elif col_name.startswith('地積(㎡)'):
                return 'land_area'
            elif col_name.startswith('形状'):
                return 'land_shape'
            elif col_name.startswith('利用区分'):
                return 'land_use_category'
            elif col_name.startswith('構造'):
                return 'building_structure'
            elif col_name.startswith('階層'):
                return 'building_floors'
            elif col_name.startswith('利用現況'):
                return 'current_use'
            elif col_name.startswith('給排水'):
                return 'utilities'
            elif col_name.startswith('周辺の土地'):
                return 'surrounding_use'
            elif col_name.startswith('方位') and col_name.endswith('.1'):
                return 'other_road_direction'
            elif col_name.startswith('方位'):
                return 'front_road_direction'
            elif col_name.startswith('幅員'):
                return 'front_road_width'
            elif col_name.startswith('種類'):
                return 'front_road_type'
            elif col_name.startswith('舗装'):
                return 'front_road_pavement'
            elif col_name.startswith('区分') and col_name != '区分':
                return 'other_road_category'
            elif col_name.startswith('用途地域'):
                return 'use_district'
            elif col_name.startswith('高度地区'):
                return 'height_district'
            elif col_name.startswith('防火'):
                return 'fire_prevention_area'
            elif col_name.startswith('建蔽率'):
                return 'coverage_ratio'
            elif col_name.startswith('容積率'):
                return 'floor_area_ratio'
            elif col_name.startswith('都市計画区域'):
                return 'city_planning_area'
            elif col_name.startswith('森林法') or col_name.startswith('公園法'):
                return 'forest_park_law'
            elif col_name.startswith('鑑定評価書') and 'URL' not in col_name:
                return 'appraisal_report'
            elif col_name == '区分':
                return 'category'
            else:
                return col_name.lower().replace(' ', '_')
        
        # カラム名を変換
        column_mapping = {col: clean_column_name(col) for col in df.columns}
        df = df.rename(columns=column_mapping)
        
        cleaned_df = pd.DataFrame({
            'year': year,
            'prefecture_code': prefecture_code,
            'category': df['category'],
            'reference_number': df['reference_number'].apply(clean_reference_number),
            'survey_date': df['survey_date'].apply(parse_survey_date),
            'location': df['location'],
            'residential_address': df['residential_address'],
            'price_per_sqm': df['price_per_sqm'].apply(clean_price),
            'station_name': df['station_name'],
            'station_distance': df['station_distance'].apply(clean_distance),
            'land_area': df['land_area'].apply(clean_area),
            'land_shape': df['land_shape'],
            'land_use_category': df['land_use_category'],
            'building_structure': df['building_structure'],
            'building_floors': df['building_floors'],
            'current_use': df['current_use'],
            'utilities': df['utilities'],
            'surrounding_use': df['surrounding_use'],
            'front_road_direction': df['front_road_direction'],
            'front_road_width': df['front_road_width'].apply(clean_width),
            'front_road_type': df['front_road_type'],
            'front_road_pavement': df['front_road_pavement'],
            'other_road_direction': df.get('other_road_direction'),
            'other_road_category': df.get('other_road_category'),
            'use_district': df.get('use_district'),
            'height_district': df.get('height_district'),
            'fire_prevention_area': df.get('fire_prevention_area'),
            'coverage_ratio': df['coverage_ratio'].apply(clean_ratio) if 'coverage_ratio' in df.columns else None,
            'floor_area_ratio': df['floor_area_ratio'].apply(clean_ratio) if 'floor_area_ratio' in df.columns else None,
            'city_planning_area': df.get('city_planning_area'),
            'forest_park_law': df.get('forest_park_law'),
            'appraisal_report': df.get('appraisal_report'),
            'appraisal_report_url': df.get('鑑定評価書URL')
        })
        
        LOGGER.info(f"  {csv_file}: {len(cleaned_df)}行をクレンジング完了")
        
        if update:
            # 既存データを削除
            delete_sql = f"DELETE FROM reinfolib_land WHERE year = {year} AND prefecture_code = '{prefecture_code}'"
            DB.set_sql(delete_sql)
            LOGGER.info(f"  既存データ削除: year={year}, prefecture_code={prefecture_code}")
            
            # 新データを挿入
            DB.insert_from_df(cleaned_df, 'reinfolib_land', is_select=False, set_sql=True)
            DB.execute_sql()
            LOGGER.info(f"  データベース挿入完了: {len(cleaned_df)}行", color=["BOLD", "GREEN"])
        else:
            LOGGER.info(f"  [ドライラン] データベース挿入をスキップ")
        success_count += 1
    
    LOGGER.info(f"\n=== アップロード完了 ===")
    LOGGER.info(f"成功: {success_count} ファイル")
    LOGGER.info(f"失敗: {failed_count} ファイル")


def upload_estate_to_db(download_dir: str = "./downloads", update: bool = False, skip: bool = False):
    """
    estate ZIPファイルを展開してデータベースにアップロード
    
    Args:
        download_dir: ZIPファイルが格納されたディレクトリ
        update: データベース更新を実行するか
        skip: 既存データがある場合はスキップするか
    """
    LOGGER.info(f"Estateデータのデータベースアップロード開始: {download_dir}")
    
    # カラムマッピング（CSVカラム名 -> DBカラム名）
    column_mapping = {
        '種類': 'property_type',
        '価格情報区分': 'price_info_category',
        '地域': 'region',
        '市区町村コード': 'municipality_code',
        '都道府県名': 'prefecture_name',
        '市区町村名': 'municipality_name',
        '地区名': 'district_name',
        '最寄駅：名称': 'nearest_station_name',
        '最寄駅：距離（分）': 'nearest_station_distance',
        '取引価格（総額）': 'transaction_price',
        '坪単価': 'price_per_tsubo',
        '間取り': 'floor_plan',
        '面積（u）': 'area_sqm',
        '取引価格（u単価）': 'price_per_sqm',
        '土地の形状': 'land_shape',
        '間口': 'frontage',
        '延床面積（u）': 'floor_area_sqm',
        '建築年': 'building_year',
        '建物の構造': 'building_structure',
        '用途': 'use',
        '今後の利用目的': 'future_use',
        '前面道路：方位': 'front_road_direction',
        '前面道路：種類': 'front_road_type',
        '前面道路：幅員（ｍ）': 'front_road_width',
        '都市計画': 'city_planning',
        '建ぺい率（％）': 'coverage_ratio',
        '容積率（％）': 'floor_area_ratio',
        '取引時期': 'transaction_period',
        '改装': 'renovation',
        '取引の事情等': 'transaction_notes'
    }
    
    # データベース接続
    DB = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE, max_disp_len=200)
    
    # reinfolib_estate_*.zip ファイルを探す
    zip_files = [f for f in os.listdir(download_dir) if f.startswith('reinfolib_estate_') and f.endswith('.zip')]
    
    if not zip_files:
        LOGGER.warning(f"{download_dir} にreinfolib_estate_*.zipファイルが見つかりません")
        return
    
    LOGGER.info(f"{len(zip_files)}個のZIPファイルを処理します")
    
    success_count = 0
    failed_count = 0
    
    for zip_file in sorted(zip_files):
        # ファイル名からyearとperiodを抽出 (reinfolib_estate_YYYY_P.zip)
        match = re.match(r'reinfolib_estate_(\d{4})_(\d)\.zip', zip_file)
        if not match:
            LOGGER.warning(f"ファイル名が不正です: {zip_file}")
            continue
        
        year = int(match.group(1))
        period = int(match.group(2))
        
        # skipフラグがある場合、既存データをチェック
        if skip:
            check_sql = f"SELECT COUNT(*) FROM reinfolib_estate WHERE year = {year} AND period = {period}"
            result = DB.select_sql(check_sql)
            if len(result) > 0 and result.iloc[0, 0] > 0:
                LOGGER.info(f"スキップ: {zip_file} (Year: {year}, Period: {period}) - 既存データあり")
                continue
        
        LOGGER.info(f"処理中: {zip_file} (Year: {year}, Period: {period})")
        
        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as temp_dir:
            # ZIPファイルを展開
            zip_path = os.path.join(download_dir, zip_file)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_dir)
                LOGGER.info(f"  ZIP展開完了: {temp_dir}")
            
            # CSVファイルを処理
            csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
            LOGGER.info(f"  {len(csv_files)}個のCSVファイルを処理")
            
            all_data = []
            
            for csv_file in csv_files:
                # ファイル名から都道府県コードを抽出
                match_csv = re.match(r'(\d{2})_', csv_file)
                if not match_csv:
                    LOGGER.warning(f"    CSVファイル名が不正です: {csv_file}")
                    continue
                
                prefecture_code = match_csv.group(1)
                csv_path = os.path.join(temp_dir, csv_file)
                
                # CSVを読み込み（Shift-JIS）
                try:
                    df = pd.read_csv(csv_path, encoding='shift_jis', encoding_errors='ignore')
                except pd.errors.EmptyDataError:
                    LOGGER.warning(f"    {csv_file}: 空のCSVファイル")
                    continue
                
                # 空のDataFrameの場合はスキップ
                if df.empty:
                    LOGGER.info(f"    {csv_file}: データなし")
                    continue
                
                # カラム名を変換
                df = df.rename(columns=column_mapping)
                
                # year, period, prefecture_codeを追加
                df['year'] = year
                df['period'] = period
                df['prefecture_code'] = prefecture_code
                
                # building_year のクレンジング（「1989年」-> 1989）
                def clean_building_year(year_str):
                    """建築年をクレンジング（1989年 -> 1989, 戦前 -> 1944）"""
                    if pd.isna(year_str):
                        return None
                    year_str = str(year_str).replace('年', '').replace('頃', '').strip()
                    # 戦前の場合は1944年とする（昭和19年、終戦前年）
                    if '戦前' in year_str:
                        return 1944
                    # 年代範囲の場合（例: 1980年代前半）
                    if '年代' in year_str:
                        match = re.search(r'(\d{4})', year_str)
                        if match:
                            return int(match.group(1))
                    # 通常の年の場合
                    match = re.search(r'(\d{4})', year_str)
                    if match:
                        return int(match.group(1))
                    return None
                
                if 'building_year' in df.columns:
                    df['building_year'] = df['building_year'].apply(clean_building_year)
                
                # 数値型の変換とクリーニング
                numeric_columns = ['nearest_station_distance', 'transaction_price', 'price_per_tsubo', 
                                 'area_sqm', 'price_per_sqm', 'frontage', 'floor_area_sqm', 
                                 'front_road_width', 'coverage_ratio', 'floor_area_ratio']
                
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                all_data.append(df)
                LOGGER.info(f"    {csv_file}: {len(df)}行読み込み")
            
            # 全データを結合
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                LOGGER.info(f"  合計: {len(combined_df)}行")
                
                if update:
                    # 既存データを削除
                    delete_sql = f"DELETE FROM reinfolib_estate WHERE year = {year} AND period = {period}"
                    DB.set_sql(delete_sql)
                    LOGGER.info(f"  既存データ削除: year={year}, period={period}")
                    
                    # 新データを挿入
                    DB.insert_from_df(combined_df, 'reinfolib_estate', is_select=False, set_sql=True)
                    DB.execute_sql()
                    LOGGER.info(f"  データベース挿入完了: {len(combined_df)}行", color=["BOLD", "GREEN"])
                else:
                    LOGGER.info(f"  [ドライラン] データベース挿入をスキップ")
                
                success_count += 1
            else:
                LOGGER.warning(f"  有効なデータがありません")
                failed_count += 1
    
    LOGGER.info(f"\n=== アップロード完了 ===")
    LOGGER.info(f"成功: {success_count} ファイル")
    LOGGER.info(f"失敗: {failed_count} ファイル")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='国土交通省 不動産取引価格情報・地価公示データ取得ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
=================================================================
実行例:

■ 不動産取引価格情報（estate）のダウンロード
  # 基本的な使用方法（2024年第4四半期）
  python reinfolib.py estate --year 2024 --period 4
  
  # 保存先を指定してダウンロード
  python reinfolib.py estate --year 2024 --period 3 --download-dir /home/share/reinfolib
  
  # ヘッドレスモード（ブラウザ非表示）で実行
  python reinfolib.py estate --year 2024 --period 2 --headless
  
  # 一括ダウンロード（別スクリプト）
  bash download_reinfolib_estate_all.sh

■ 地価公示・地価調査データ（land）のスクレイピング
  # 基本的な使用方法（2024年・東京都）
  python reinfolib.py land --year 2024 --prefecture-code 13
  
  # 全都道府県コード例
  # 北海道:01, 青森:02, 岩手:03, 宮城:04, 秋田:05, 山形:06, 福島:07
  # 茨城:08, 栃木:09, 群馬:10, 埼玉:11, 千葉:12, 東京:13, 神奈川:14
  # 新潟:15, 富山:16, 石川:17, 福井:18, 山梨:19, 長野:20, 岐阜:21
  # 静岡:22, 愛知:23, 三重:24, 滋賀:25, 京都:26, 大阪:27, 兵庫:28
  # 奈良:29, 和歌山:30, 鳥取:31, 島根:32, 岡山:33, 広島:34, 山口:35
  # 徳島:36, 香川:37, 愛媛:38, 高知:39, 福岡:40, 佐賀:41, 長崎:42
  # 熊本:43, 大分:44, 宮崎:45, 鹿児島:46, 沖縄:47
  
  # ヘッドレスモードで実行（大阪府）
  python reinfolib.py land --year 2023 --prefecture-code 27 --headless
  
  # 一括スクレイピング（別スクリプト・1970-2024年全都道府県）
  bash download_reinfolib_land_all.sh

■ ダウンロード済みデータのデータベース投入
  # Estate データ（不動産取引価格）のDB投入
  python reinfolib.py uploadestate                      # ドライラン
  python reinfolib.py uploadestate --update              # DB更新
  python reinfolib.py uploadestate --download-dir /home/share/reinfolib --update
  
  # Land データ（地価公示・地価調査）のDB投入
  python reinfolib.py uploadland                        # ドライラン
  python reinfolib.py uploadland --update                # DB更新

=================================================================
注意事項:
  - estate: ZIPファイルをダウンロード（四半期ごと、全国一括）
  - land: CSVファイルを生成（年度ごと、都道府県別）
  - uploadestate: estateデータ（ZIPファイル）のDB投入
  - uploadland: landデータ（CSVファイル）のDB投入
  - データベース更新時は --update フラグが必須（安全のため）
  - 大量データ取得時はヘッドレスモード推奨（--headless）
  - ダウンロード済みファイルは再取得しません（既存ファイルチェック）
=================================================================
'''
    )
    
    parser.add_argument("type", choices=["estate", "land", "uploadestate", "uploadland"], help="コマンドタイプ（estate: 不動産取引価格ダウンロード, land: 地価公示・地価調査スクレイピング, uploadestate: estateデータDB投入, uploadland: landデータDB投入）")
    parser.add_argument("--year", type=int, help="対象年（例: 2024）（estate/landタイプで必須）")
    parser.add_argument("--period", type=int, choices=[1, 2, 3, 4], help="四半期（1-4）（estateタイプのみ必須）")
    parser.add_argument("--prefecture-code", type=str, help="都道府県コード（01-47の2桁）（landタイプのみ必須）")
    parser.add_argument("--download-dir", type=str, default="./downloads", help="ダウンロード保存先ディレクトリ")
    parser.add_argument("--headless", action="store_true", default=False, help="ヘッドレスモードで実行")
    parser.add_argument("--update", action="store_true", default=False, help="データベース更新を実行（uploadestate/uploadlandで使用）")
    parser.add_argument("--skip", action="store_true", default=False, help="既存データがある場合はスキップ（uploadestate/uploadlandで使用）")
    
    args = parser.parse_args()
    LOGGER.info(f"実行引数: {args}")
    
    # データタイプによる引数検証
    if args.type in ["estate", "land"] and args.year is None:
        parser.error(f"{args.type}タイプの場合、--yearは必須です")
    if args.type == "estate" and args.period is None:
        parser.error("estateタイプの場合、--periodは必須です")
    if args.type == "land" and args.prefecture_code is None:
        parser.error("landタイプの場合、--prefecture-codeは必須です")
    
    # 都道府県コードの検証（landタイプの場合）
    if args.type == "land":
        if not args.prefecture_code.isdigit() or len(args.prefecture_code) != 2 or not (1 <= int(args.prefecture_code) <= 47):
            parser.error("--prefecture-codeは01-47の2桁で指定してください")
    
    if args.type == "uploadestate":
        # Estate データのアップロード処理
        upload_estate_to_db(args.download_dir, args.update, args.skip)
    elif args.type == "uploadland":
        # Land データのアップロード処理
        upload_land_to_db(args.download_dir, args.update, args.skip)
    else:
        # ダウンロード処理
        if args.headless:
            LOGGER.info("ヘッドレスモードで実行します")
        else:
            LOGGER.info("ブラウザを表示して実行します")        
        with sync_playwright() as playwright:
            if args.type == "estate":
                filepath = download_estate_prices(playwright, args.year, args.period, args.download_dir, args.headless)
                LOGGER.info(f"処理完了: {filepath}")
            elif args.type == "land":
                # DataFrameを取得
                df = download_land_prices(playwright, args.year, args.prefecture_code, args.headless)
                
                # CSV保存処理
                os.makedirs(args.download_dir, exist_ok=True)
                filename = f"reinfolib_land_{args.year}_{args.prefecture_code}.csv"
                filepath = os.path.join(args.download_dir, filename)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                
                LOGGER.info(f"CSV保存完了: {filepath}", color=["BOLD", "GREEN"])
                LOGGER.info(f"データ行数: {len(df)}行, カラム数: {len(df.columns)}列")
