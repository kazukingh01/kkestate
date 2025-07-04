import argparse
import os
import time
import re
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright, expect
from kklogger import set_logger
import pandas as pd

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="国土交通省の不動産取引価格情報をダウンロード",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
実行例:
  # 不動産取引価格情報（2024年第4四半期）をダウンロード
  python reinfolib.py estate --year 2024 --period 4
  
  # 地価公示・地価調査データ（2024年・東京都）をスクレイピング
  python reinfolib.py land --year 2024 --prefecture-code 13
  
  # ダウンロード先を指定
  python reinfolib.py estate --year 2024 --period 3 --download-dir /home/share/reinfolib
  
  # ヘッドレスモードで実行
  python reinfolib.py land --year 2023 --prefecture-code 27 --headless
'''
    )
    
    parser.add_argument("type", choices=["estate", "land"], help="データタイプ（estate: 不動産取引価格, land: 地価公示・地価調査）")
    parser.add_argument("--year", type=int, required=True, help="対象年（例: 2024）")
    parser.add_argument("--period", type=int, choices=[1, 2, 3, 4], help="四半期（1-4）（estateタイプのみ必須）")
    parser.add_argument("--prefecture-code", type=str, help="都道府県コード（01-47の2桁）（landタイプのみ必須）")
    parser.add_argument("--download-dir", type=str, default="./downloads", help="ダウンロード保存先ディレクトリ")
    parser.add_argument("--headless", action="store_true", default=False, help="ヘッドレスモードで実行")
    
    args = parser.parse_args()
    LOGGER.info(f"実行引数: {args}")
    
    if args.headless:
        LOGGER.info("ヘッドレスモードで実行します")
    else:
        LOGGER.info("ブラウザを表示して実行します")
    
    # データタイプによる引数検証
    if args.type == "estate" and args.period is None:
        parser.error("estateタイプの場合、--periodは必須です")
    if args.type == "land" and args.prefecture_code is None:
        parser.error("landタイプの場合、--prefecture-codeは必須です")
    
    # 都道府県コードの検証（landタイプの場合）
    if args.type == "land":
        if not args.prefecture_code.isdigit() or len(args.prefecture_code) != 2 or not (1 <= int(args.prefecture_code) <= 47):
            parser.error("--prefecture-codeは01-47の2桁で指定してください")
    
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
