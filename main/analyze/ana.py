import argparse, datetime
import numpy as np
import pandas as pd
from kkpsgre.connector import DBConnector
from kklogger import set_logger
from kkestate.config.psgre import HOST, PORT, USER, PASS, DBNAME, DBTYPE
import folium


LOGGER = set_logger(__name__)
DICT_TYPE = {
    (False,   'house'): "中古戸",
    (False, 'mansion'): "中古MS",
    ( True,   'house'): "新築戸",
    ( True, 'mansion'): "新築MS",
    ( None,    'land'): "土地",
}


def make_heatmap(df: pd.DataFrame, base_d: float, save_path: str="./heatmap.html"):
    # don't use now
    assert isinstance(df, pd.DataFrame)
    assert isinstance(base_d,    float)
    assert isinstance(save_path, str)    
    # dataframe processing
    df      = df.copy()
    lat_min = int(df["latitude" ].min() / base_d) * base_d
    lat_max = int(df["latitude" ].max() / base_d) * base_d + base_d
    lng_min = int(df["longitude"].min() / base_d) * base_d
    lng_max = int(df["longitude"].max() / base_d) * base_d + base_d
    df      = df.loc[~df["latitude"].isna()]
    df["latitude" ] = ((df["latitude" ] - lat_min) / base_d).astype(int)
    df["longitude"] = ((df["longitude"] - lng_min) / base_d).astype(int)
    df["grid"     ] = df[["latitude", "longitude"]].apply(lambda x: tuple(x), axis=1)
    df_heat = df.groupby("grid")["price_per_sqm"].mean()
    df_heat.index = pd.MultiIndex.from_tuples(df_heat.index.tolist())
    ndf  = np.zeros((max(df["latitude"].max() + 1, df["longitude"].max() + 1), max(df["latitude"].max() + 1, df["longitude"].max() + 1)), dtype=int)
    for y, x, v in df_heat.loc[~df_heat.isna()].reset_index().to_numpy().astype(int):
        ndf[y, x] = v
    # make heatmap
    from branca.colormap import linear
    m    = folium.Map(location=[36.0, 138.0], zoom_start=5)
    lats = np.arange(lat_min, lat_max, base_d)
    lons = np.arange(lng_min, lng_max, base_d)
    colormap = linear.YlOrRd_09.scale(ndf.min(), ndf.max())
    colormap.caption = 'average price'
    colormap.add_to(m)
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            val   = ndf[i, j]
            if val == 0:
                continue
            color = colormap(val)
            folium.Rectangle(
                bounds=[[lat,        lon],
                        [lat+base_d, lon+base_d] ],
                stroke=False,          # 枠線なし
                fill=True,
                fill_color=color,
                fill_opacity=0.5       # 0〜1で調整
            ).add_to(m)
    m.save(save_path)


def make_map(df_land: pd.DataFrame, df_suumo: pd.DataFrame, save_path: str="./map.html"):
    from folium.features import DivIcon
    assert isinstance(df_land, pd.DataFrame)
    assert isinstance(df_suumo, pd.DataFrame)
    assert isinstance(save_path, str)
    lat_min = df_land['latitude' ].min()
    lat_max = df_land['latitude' ].max()
    lng_min = df_land['longitude'].min()
    lng_max = df_land['longitude'].max()
    m = folium.Map(
        location=[(lat_min + lat_max) / 2, (lng_min + lng_max) / 2],
        zoom_start=10,        # お好みのズームレベルに
        tiles='CartoDB positron',
        control_scale=False,  # スケール（距離目盛）も非表示
        max_bounds=True       # マップの端（bounds）外へのパンを制限
    )
    m.fit_bounds([
        [lat_min, lng_min],   # 南西コーナー
        [lat_max, lng_max],   # 北東コーナー
    ])
    from folium.plugins import MarkerCluster
    from branca.colormap import linear
    colormap = linear.YlOrRd_09.scale(df_land["price_per_sqm"].quantile(0.1), df_land["price_per_sqm"].quantile(0.9))
    colormap.caption = 'average price'
    colormap.add_to(m)
    groups = {}
    for cat in (df_land['category'].unique().tolist() + list(DICT_TYPE.values())):
        fg = folium.FeatureGroup(name=cat, show=True)
        mc = MarkerCluster(
            name=f"{cat} Cluster",
            disableClusteringAtZoom=15
        ).add_to(fg)
        m.add_child(fg)
        groups[cat] = mc
    area_min, area_max = df_land["land_area"].quantile(0.01), df_land["land_area"].quantile(0.99)
    list_points = [(x, y, "land") for x, y in df_land.iterrows()] + [(x, y, "suumo") for x, y in df_suumo.iterrows()]
    for _, row, _type in list_points:
        if _type == "land":
            lat, lon, price, area, cat = row['latitude'], row['longitude'], row['price_per_sqm'], row['land_area'], row['category']
            url = None
        else:
            lat, lon, price = row['latitude'], row['longitude'], row["price"]
            cat1, cat2, url = row["building_type"], row["is_new"], row["url"]
            area1, area2, area3 = row["area_ms"], row["area_land"], row["area_building"]
            cat = DICT_TYPE.get((cat2, cat1))
            if cat1 == "house":
                area = area3
            elif cat1 == "mansion":
                area = area1
            else:
                area = area2
            price = (price * 10000) / area
        if area is None or np.isnan(area):
            area = df_land["land_area"].median()
        if np.isnan(lat) or np.isnan(lon) or np.isnan(price):
            continue
        LOGGER.info(f"{lat}, {lon}, {price}, {area}, {cat}")
        folium.CircleMarker(
            location=[lat, lon],
            radius=25.0 * np.clip((area - area_min) / (area_max - area_min), 0.0, 1.0) + 5.0,
            color=colormap(price),
            fill=True,
            fill_color=colormap(price),
            fill_opacity=0.6,
            stroke=False,
            popup=f"{cat}: {int(price)}, {area}m^2" + (f"<br><a href='https://suumo.jp/{url}'>link</a>" if url else ""),
        ).add_to(groups[cat])
        folium.map.Marker(
            location=[lat, lon],
            icon=DivIcon(
                icon_size=(0,0),    # アイコンサイズをゼロにして「丸のみ」を表示
                icon_anchor=(0,0),
                html=f'''<div style="
                            font-size:12px;
                            font-weight:bold;
                            color:{colormap(price)};
                            text-shadow: 1px 1px 1px white;
                            transform: translate(-50%, -150%);
                        ">
                            {int(price/1000)}
                        </div>'''
            )
        ).add_to(groups[cat])
    folium.LayerControl(collapsed=False).add_to(m)
    m.save(save_path)


if __name__ == "__main__":
    # 引数処理
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--code",  type=str, required=True)
    parser.add_argument("--year",  type=int, default=2024)
    parser.add_argument("--dir",   type=str, default="./html")
    parser.add_argument(
        "--since", type=lambda x: datetime.datetime.strptime(x, "%Y%m%d"),
        default=(datetime.datetime.now() - datetime.timedelta(days=30*6)).strftime("%Y%m%d")
    )
    args = parser.parse_args()
    LOGGER.info(f"{args}")

    # connection
    DB        = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE, max_disp_len=200)
    # reinfolib
    df_land   = DB.select_sql(f"select * from reinfolib_land   where year = {args.year} and prefecture_code = '{args.code}';")
    df_estate = DB.select_sql(f"select * from reinfolib_estate where year = {args.year} and prefecture_code = '{args.code}' and period = 1;")
    df_loc    = DB.select_sql(f"select * from estate_mst_location;")
    df_land   = pd.merge(df_land, df_loc[["location", "latitude", "longitude"]], on="location", how="left")
    # suumo
    df_target = DB.select_sql(f"select * from estate_run where is_success = true and is_ref = true and timestamp >= '{args.since.strftime("%Y-%m-%d 00:00:00")}';")
    df_suumo  = DB.select_sql(
        f"select a.*, b.longitude, b.latitude from estate_main_extended as a " + 
        f"left join estate_mst_location as b on a.location = b.location " + 
        f"where a.citycode like '{args.code}%' and a.id in ({','.join(df_target["id_main"].unique().astype(str).tolist())});"
    )
    df_run_latest = DB.select_sql(
        f"select id as id_run, id_main, timestamp from estate_run where is_ref = true and " + 
        f"id_main in (select id from estate_main_extended where citycode like '{args.code}%') and " + 
        f"timestamp >= '{args.since.strftime("%Y-%m-%d 00:00:00")}'"
    ).sort_values("timestamp", ascending=False).groupby("id_main").first()
    df_detail = DB.select_sql(
        f"select a.*, b.* from estate_detail_ref as a " + 
        f"left join estate_cleaned as b on a.id_run_ref = b.id_run and a.id_key = b.id_key and " + 
        f"b.id_cleaned in (select id from estate_mst_cleaned where name like '価格%' or name like '%面積%') "
        f"where true and " +
        f"a.id_run in ({','.join(df_run_latest['id_run'].astype(str).tolist())}) and " + 
        f"id_cleaned is not null;"
    )
    df_mst   = DB.select_sql("select * from estate_mst_cleaned;")
    dict_mst = {int(a): {x: y for x, y in df_mst[["id", "name"]].to_numpy()}[a] for a in df_detail["id_cleaned"].unique()}
    ## join
    df_detail = df_detail.sort_values(["id_run", "id_run_ref"]).reset_index(drop=True).groupby(["id_run", "id_cleaned"])[["value_cleaned"]].last().reset_index()
    df_join   = df_run_latest.reset_index()[["id_main", "id_run"]].copy()
    for x, y in dict_mst.items():
        dfwk = df_detail.loc[df_detail["id_cleaned"] == x, ["id_run", "value_cleaned"]].copy()
        dfwk.columns = ["id_run", f"value_{y}"]
        df_join = pd.merge(df_join, dfwk, how="left", on="id_run")
    df_suumo = pd.merge(df_suumo, df_join, how="left", left_on="id", right_on="id_main")
    ## value_価格
    df_suumo["price"] = df_suumo["value_価格"].str["value"].copy()
    df_suumo.loc[df_suumo["value_価格"].str["is_undefined"] == True, "price"] = -1
    assert df_suumo.loc[(df_suumo["value_価格"].str["unit"] != "万円") & (df_suumo["price"] >= 0)].shape[0] == 0
    ## value_面積
    df_suumo["area_ms"] = df_suumo["value_専有面積"].str["value"].copy()
    assert df_suumo.loc[(df_suumo["value_専有面積"].str["unit"] != "m^2") & (~df_suumo["area_ms"].isna())].shape[0] == 0
    df_suumo["area_land"] = df_suumo["value_土地面積"].str["value"].copy()
    assert df_suumo.loc[(df_suumo["value_土地面積"].str["unit"] != "m^2") & (~df_suumo["area_land"].isna())].shape[0] == 0
    df_suumo["area_building"] = df_suumo["value_建物面積"].str["value"].copy()
    assert df_suumo.loc[(df_suumo["value_建物面積"].str["unit"] != "m^2") & (~df_suumo["area_building"].isna())].shape[0] == 0
    ## 0.00001 ~= 1m, 1km ~= 0.01
    # BASE_D  = 0.01
    # make_heatmap(df, BASE_D)
    make_map(df_land.copy(), df_suumo.copy(), save_path=f"{args.dir}/map_{args.code}.html")
