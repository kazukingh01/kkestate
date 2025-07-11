import argparse
import numpy as np
import pandas as pd
from kkpsgre.connector import DBConnector
from kklogger import set_logger
from kkestate.config.psgre import HOST, PORT, USER, PASS, DBNAME, DBTYPE
import folium


LOGGER    = set_logger(__name__)


def make_heatmap(df: pd.DataFrame, base_d: float, save_path: str="./heatmap.html"):
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


def make_map(df: pd.DataFrame, save_path: str="./map.html"):
    from folium.features import DivIcon
    assert isinstance(df, pd.DataFrame)
    assert isinstance(save_path, str)
    m = folium.Map(
        location=[36.0, 138.0],
        zoom_start=5,
        tiles='CartoDB positron',    # 'Stamen Toner Lite' も候補
        control_scale=False          # スケール（距離目盛）も非表示
    )
    from branca.colormap import linear
    colormap = linear.YlOrRd_09.scale(df["price_per_sqm"].quantile(0.1), df["price_per_sqm"].quantile(0.9))
    colormap.caption = 'average price'
    colormap.add_to(m)
    groups = {}
    for cat in df['category'].unique():
        fg = folium.FeatureGroup(name=cat, show=True)
        groups[cat] = fg
        m.add_child(fg)
    area_min, area_max = df["land_area"].quantile(0.01), df["land_area"].quantile(0.99)
    for _, row in df.iterrows():
        lat, lon, price, area, cat = row['latitude'], row['longitude'], row['price_per_sqm'], row['land_area'], row['category']
        if np.isnan(area):
            area = df["land_area"].median()
        if np.isnan(lat) or np.isnan(lon) or np.isnan(price):
            continue
        folium.CircleMarker(
            location=[lat, lon],
            radius=25.0 * np.clip((area - area_min) / (area_max - area_min), 0.0, 1.0) + 5.0,
            color=colormap(price),
            fill=True,
            fill_color=colormap(price),
            fill_opacity=0.6,
            stroke=False,
            popup=f"{cat}: {int(price)}, {area}m^2",
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
    parser.add_argument("--code", type=str, required=True)
    args = parser.parse_args()
    LOGGER.info(f"{args}")

    # connection
    DB        = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE, max_disp_len=200)
    df_land   = DB.select_sql(f"select * from reinfolib_land   where year = 2024 and prefecture_code = '{args.code}';")
    df_estate = DB.select_sql(f"select * from reinfolib_estate where year = 2024 and prefecture_code = '{args.code}' and period = 1;")
    df_loc    = DB.select_sql(f"select * from estate_mst_location;")
    df_org    = pd.merge(df_land, df_loc[["location", "latitude", "longitude"]], on="location", how="left")
    df        = df_org.copy()
    ## 0.00001 ~= 1m, 1km ~= 0.01
    BASE_D  = 0.01
    make_heatmap(df, BASE_D)
    make_map(df)
