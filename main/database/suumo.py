import bs4, re, argparse, requests, datetime, time, copy
import pandas as pd
from kkpsgre.psgre import Psgre
from kkestate.config.psgre import HOST, PORT, USER, PASS, DBNAME
from kkestate.util.logger import set_logger


LOGGER    = set_logger(__name__)
BASE_URL  = "https://suumo.jp"
LIST_TYPE = ["ms/shinchiku", "ms/chuko", "ikkodate", "chukoikkodate"]
LIST_MST_URLS = [
    f"{BASE_URL}/{y}/{x}/city/" for x in [
        "hokkaido_", "aomori", "iwate", "akita", "miyagi", "yamagata", "fukushima",
        "niigata", "ishikawa", "toyama", "nagano", "yamanashi", "fukui",
        "tochigi", "gumma", "saitama", "ibaraki", "chiba", "tokyo", "kanagawa",
        "gifu", "shizuoka", "aichi", "mie",
        "shiga", "kyoto", "osaka", "nara", "wakayama", "hyogo",
        "tottori", "shimane", "okayama", "hiroshima", "yamaguchi",
        "kagawa", "tokushima", "kochi", "ehime",
        "fukuoka", "oita", "saga", "nagasaki", "kumamoto", "miyazaki", "kagoshima", "okinawa",
    ] for y in LIST_TYPE
]


def get_url_ichiran(url):
    assert isinstance(url, str)
    LOGGER.info(f"get from: {url}")
    html = requests.get(url)
    soup = bs4.BeautifulSoup(html.content, 'html.parser')
    list_sc  = [x.attrs["value"] for x in soup.find_all("input", attrs={'name': 'sc', "type": "checkbox"})]
    list_key = re.findall(r'<input[^>]+name="([^"]*)"[^>]+type="hidden"[^>]+>', str(soup.find("form", id="js-areaSelectForm")).strip())
    list_val = re.findall(r'<input[^>]+type="hidden"[^>]+value="([^"]*)">', str(soup.find("form", id="js-areaSelectForm")).strip())
    if len(list_key) != len(list_val):
        LOGGER.raise_error(f"""
            URL: {url},
            list_key: {list_key},
            list_val: {list_val}
        """)
    url_list  = f"{BASE_URL}/jj/bukken/ichiran/JJ010FJ001/?"
    url_list += "&".join([x + "=" + y for x, y in zip(list_key, list_val)])
    url_list += "&" + "&".join([f"sc={x}" for x in list_sc])
    url_list += "&" + "kb=1&kt=9999999&km=1&mb=0&mt=9999999&ekTjCd=&ekTjNm=&tj=0"
    LOGGER.info(f"create: {url_list}")
    return url_list


def get_estate_list(url: str):
    assert isinstance(url, str)
    LOGGER.info(url)
    cnt = 0
    while True:
        html = requests.get(url)
        soup = bs4.BeautifulSoup(html.content, 'html.parser')
        if len(soup.find_all("div", class_="error_pop")) > 0:
            # There is not list of estates.
            return {}
        soup = soup.find("div", id="js-bukkenList")
        if soup is None:
            LOGGER.warning("soup is None.")
            cnt += 1
            if cnt >= 3: break
            time.sleep(5)
            continue
        else:
            break
    if soup is None:
        LOGGER.raise_error(f"""
            URL: {url},
            html: {html.text},
            soup: {soup},
        """)
    if soup.find("li", class_="cassette_list-item") is not None:
        list_title = [x.find("div", class_="cassette_header").find("h2").text.strip() for x in soup.find_all("li", class_="cassette_list-item")]
        list_urls  = [x.find("div", class_="cassette_header").find("h2").find("a").attrs["href"].strip() for x in soup.find_all("li", class_="cassette_list-item")]
    else:
        list_title = [x.find("h2", class_="property_unit-title").text.strip() for x in soup.find_all("div", class_="property_unit")]
        list_urls  = [x.find("h2", class_="property_unit-title").find("a").attrs["href"].strip() for x in soup.find_all("div", class_="property_unit")]
    if len(list_title) != len(list_urls):
        LOGGER.raise_error(f"""
            URL: {url},
            list_title: {list_title},
            list_urls: {list_urls}
        """)
    df = pd.DataFrame(list_title, columns=["name"])
    df["url"] = list_urls
    return df.to_dict()


def get_estate_detail(url):
    assert isinstance(url, str)
    url  = f"{url}property/" if url[-1] == "/" else f"{url}/property/"
    LOGGER.info(url)
    html = requests.get(url)
    if html.status_code in [503]:
        LOGGER.warning(f"STATUS CODE: {html.status_code}")
        return -1
    soup = bs4.BeautifulSoup(html.content, 'html.parser')
    dict_ret = {}
    if len(soup.find_all("div", class_="error-content")) > 0:
        LOGGER.warning("web page is nothing.")
        return -1
    if soup.text.find("お探しの情報は、当サイトへの掲載が終了しているか、一時的にご覧いただけません。") >= 0:
        LOGGER.warning("web page is invalid for over the date when we can check or temporarily closed.")
        return -1
    if (len(soup.find_all("div", id="js-normal_tabs")) > 0) or (len(soup.find_all("div", class_="l-contents")) > 0):
        # suumo's real estate.
        ## section_h2-header
        tbl = soup.find("div", class_="section_h2-header").find_next("div", class_="section_h2-body").find("table", class_="detailtable")
        if tbl is not None:
            _key     = [x.text.strip() for x in tbl.find_all("th", class_="detailtable-title")]
            _val     = [x.text.strip() for x in tbl.find_all("td", class_="detailtable-body")]
            dict_ret = dict_ret | {x:y for x, y in zip(_key, _val)}
        ## ui-section_h2-header, ui-section_h3-header
        list_tbls = [] # to avoid same table
        for label_class in ["ui-section_h3", "ui-section_h2"]:
            list_soups = soup.find_all("div", class_=f"{label_class}-header")
            for soupwk in list_soups:
                title = soupwk.find(label_class[-2:]).text.strip()
                title = re.findall(r"第[0-9]+期", title)
                title = "_" + title[0] if len(title) > 0 else ""
                tbl   = soupwk.find_next("div", class_=f"{label_class}-body").find("table", class_="detailtable")
                if tbl is not None:
                    if tbl in list_tbls: continue # to avoid same table
                    list_tbls.append(copy.deepcopy(tbl))
                    _key     = [x.text.strip() for x in tbl.find_all("th", class_="detailtable-title")]
                    _val     = [x.text.strip() for x in tbl.find_all("td", class_="detailtable-body")]
                    dict_ret = dict_ret | {x + title:y for x, y in zip(_key, _val)}
        if (len(soup.find_all("div", id="js-normal_tabs")) > 0):
            ## kaishainfo
            url = url.replace("property/", "kaishainfo/")
            LOGGER.info(url)
            html = requests.get(url)
            soup = bs4.BeautifulSoup(html.content, 'html.parser')
            tbl  = soup.find("div", class_="section_h2-header").find_next("div", class_="section_h2-body").find("table", class_="detailtable")
            _key     = [x.text.strip() for x in tbl.find_all("th", class_="detailtable-title")]
            _val     = [x.text.strip() for x in tbl.find_all("td", class_="detailtable-body")]
            dict_ret = dict_ret | {x:y for x, y in zip(_key, _val)}
    else:
        list_titles_class = ["secTitleOuterK", "secTitleOuterR", "secTitleInnerK", "secTitleInnerR"]
        list_soups, target_name = [], None
        for x in list_titles_class:
            list_soups = soup.find_all("div", class_=x)
            if len(list_soups) > 0:
                target_name = x
                break
        if len(list_soups) == 0:
            LOGGER.warning(f"list_titles_class: {list_titles_class} is nothing.")
        for soupwk in [x.find_parent("div", class_="mt20") for x in list_soups]:
            if soupwk is None: continue
            title = soupwk.find("div", class_=target_name).text.strip()
            LOGGER.info(title)
            if len(soupwk.find_all("table")) > 0:
                tbl    = soupwk.find("table", summary="表")
                if tbl is None: continue
                _key   = [y.text.strip().replace("\nヒント", "") for y in tbl.find_all("th")]
                _val   = [re.sub(r"[\t\n\r\f]+", r"\t", y.find_next("td").text.strip().replace("\nヒント", "")) for y in tbl.find_all("th")]
                dict_ret = dict_ret | {x:y for x, y in zip(_key, _val)}
            else:
                dict_ret[title] = re.sub(r"[\t\n\r\f]+", r"\t", soupwk.find_next("div", class_="mt10").text.strip()) 
    dict_ret = {x: re.sub(r"[\t\n\r\f]+", r"\t", y).replace("\xa0", "").replace("'", "") for x, y in dict_ret.items()} # again
    return dict_ret


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--updateurls",  action='store_true', default=False)
    parser.add_argument("--update",      action='store_true', default=False)
    parser.add_argument("--runmain",     action='store_true', default=False)
    parser.add_argument("--rundetail",   action='store_true', default=False)
    parser.add_argument("--skipsuccess", action='store_true', default=False)
    parser.add_argument("--datefrom",    type=str, help="--datefrom 20230101", required=False)
    args = parser.parse_args()

    # connection
    DB = Psgre(f"host={HOST} port={PORT} dbname={DBNAME} user={USER} password={PASS}", max_disp_len=200)

    # get url list
    if args.updateurls:
        list_urls = []
        for x in LIST_MST_URLS:
            url = get_url_ichiran(x)
            html = requests.get(url)
            soup = bs4.BeautifulSoup(html.content, 'html.parser')
            if len(soup.find_all("div", class_="error_pop")) > 0: continue
            if soup.find("ol", class_="pagination-parts") is not None:
                list_page = int([x.text for x in soup.find("ol", class_="pagination-parts").find_all("li")][-1])
            else:
                list_page = int([x.text for x in soup.find("ol", class_="sortbox_pagination-parts").find_all("li", class_="sortbox_pagination-list")][-1])
            list_page = list(range(1, list_page + 1))
            for i_page in list_page: list_urls.append(f"{url}&page={i_page}" if url.find("?") > 0 else f"{url}?page={i_page}")
        if args.update:
            DB.set_sql("delete from estate_tmp;")
            DB.insert_from_df(pd.DataFrame(list_urls, columns=["url"]), "estate_tmp", is_select=False)
            DB.execute_sql()
    else:
        list_urls = DB.select_sql("select url from estate_tmp where is_checked = false;")["url"].tolist()
    
    # main
    if args.runmain:
        for i_url, url in enumerate(list_urls):
            dictwk = get_estate_list(url)
            df     = pd.DataFrame(dictwk)
            if args.update:
                DB.execute_sql(f"update estate_tmp set is_checked = true where url = '{url}';")
            if df.shape[0] > 0 and args.update:
                df_main = DB.select_sql("select id, url from estate_main where url in ('" + "','".join(df["url"].tolist())+ "');")
                df      = pd.merge(df, df_main, how="left", on="url")
                if df["id"].isna().sum() > 0:
                    DB.insert_from_df(df.loc[df["id"].isna(), ["name", "url"]], "estate_main", is_select=False)
                    DB.execute_sql()
                df_main = DB.select_sql("select id as id_new, url from estate_main where url in ('" + "','".join(df["url"].tolist())+ "');")
                df      = pd.merge(df, df_main, how="left", on="url")
                if args.update:
                    DB.execute_sql("update estate_main set sys_updated = CURRENT_TIMESTAMP where id in (" + ",".join(df["id_new"].astype(str).tolist()) +");")

    # detail
    if args.rundetail:
        if args.datefrom is None:
            date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            date = datetime.datetime.fromisoformat(args.datefrom).strftime('%Y-%m-%d %H:%M:%S')
        date_check_from = (datetime.datetime.now() - datetime.timedelta(days=180)).strftime('%Y-%m-%d %H:%M:%S')
        if args.skipsuccess:
            df = DB.select_sql(
                f"select main.id, main.url, sub.id as id_run, main.sys_updated from estate_main as main " + 
                f"left join estate_run as sub on main.id = sub.id_main and sub.is_success = true and sub.timestamp >= '{date}' " + 
                f"where main.sys_updated >= '{date}';"
            )
            df = df.sort_values(["id", "id_run"]).groupby("id").last().reset_index()
            df = df.loc[df["id_run"].isna()].groupby("id").first().reset_index()
        else:
            df = DB.select_sql(f"select id, url from estate_main where sys_updated >= '{date}';")
        list_df = []
        for url, id_new in df[["url", "id"]].values:
            if args.update:
                id_run = DB.execute_sql(f"INSERT into estate_run (id_main, timestamp) VALUES ({id_new}, CURRENT_TIMESTAMP);SELECT lastval();")[0][0]
            else:
                id_run = None
            try:
                dict_ret = get_estate_detail(BASE_URL + url)
            except (ConnectionResetError, requests.exceptions.ChunkedEncodingError) as e:
                LOGGER.warning(f"{str(e)} happend.")
                time.sleep(60)
                continue
            if isinstance(dict_ret, int):
                if args.update:
                    DB.execute_sql(f"update estate_run set is_success = true where id = {id_run};")
                continue
            df_detail = pd.Series(dict_ret, dtype=object).reset_index()
            df_detail.columns = ["key", "value"]
            # register mst key
            if df_detail.shape[0] > 0 and args.update:
                df_key    = DB.select_sql("select id, name as key from estate_mst_key where name in ('" + "','".join(df_detail["key"].unique().tolist())+ "');")
                df_detail = pd.merge(df_detail, df_key, how="left", on="key")
                if df_detail["id"].isna().sum() > 0:
                    df_insert = pd.DataFrame(df_detail.loc[df_detail["id"].isna(), "key"].unique(), columns=["name"])
                    DB.insert_from_df(df_insert, "estate_mst_key", is_select=False)
                    DB.execute_sql()
                df_key    = DB.select_sql("select id as id_key, name as key from estate_mst_key where name in ('" + "','".join(df_detail["key"].unique().tolist())+ "');")
                df_detail = pd.merge(df_detail, df_key, how="left", on="key")
            # insert
            df_detail["id_run"]  = id_run
            if df_detail.shape[0] > 0 and args.update:
                df_prev_run = DB.select_sql(f"select id from estate_run where id_main = {id_new} and timestamp >= '{date_check_from}' and is_success = true;")
                df_prev     = DB.select_sql(f"select id_run, id_key, value as value_prev from estate_detail where id_run in (" + ",".join(df_prev_run["id"].astype(str).tolist()) +");")
                df_prev     = df_prev.sort_values(["id_key", "id_run"]).groupby(["id_key", "id_run"]).last()
                df_detail   = pd.merge(df_detail, df_prev, how="left", on=["id_run", "id_key"])
                df_detail   = df_detail.loc[df_detail["value_prev"].isna() | (df_detail["value_prev"] != df_detail["value"])]
                DB.insert_from_df(df_detail[["id_run", "id_key", "value"]], "estate_detail", is_select=False)
                DB.set_sql(f"update estate_run set is_success = true where id = {id_run};")
                DB.execute_sql()
