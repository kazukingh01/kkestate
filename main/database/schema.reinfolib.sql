-- REINFOLIBの不動産取引価格情報を格納するテーブル
-- 国土交通省の不動産取引価格情報ダウンロードデータ

-- reinfolib_estateテーブル作成
CREATE TABLE reinfolib_estate (
    -- 主キー
    id                      bigserial PRIMARY KEY,         -- 自動採番ID
    
    -- 追加カラム
    year                    smallint NOT NULL,              -- 取引年（例: 2024）
    period                  smallint NOT NULL,              -- 四半期（1-4）
    prefecture_code         char(2) NOT NULL,               -- 都道府県コード（01-47）
    
    -- CSVカラム（日本語 -> 英語変換）
    property_type           text,                           -- 種類
    price_info_category     text,                           -- 価格情報区分
    region                  text,                           -- 地域
    municipality_code       char(5),                        -- 市区町村コード
    prefecture_name         text,                           -- 都道府県名
    municipality_name       text,                           -- 市区町村名
    district_name           text,                           -- 地区名
    nearest_station_name    text,                           -- 最寄駅：名称
    nearest_station_distance integer,                       -- 最寄駅：距離（分）
    transaction_price       bigint,                         -- 取引価格（総額）
    price_per_tsubo         integer,                        -- 坪単価
    floor_plan              text,                           -- 間取り
    area_sqm                numeric(10,2),                  -- 面積（㎡）
    price_per_sqm           integer,                        -- 取引価格（㎡単価）
    land_shape              text,                           -- 土地の形状
    frontage                numeric(10,2),                  -- 間口
    floor_area_sqm          numeric(10,2),                  -- 延床面積（㎡）
    building_year           smallint,                       -- 建築年
    building_structure      text,                           -- 建物の構造
    use                     text,                           -- 用途
    future_use              text,                           -- 今後の利用目的
    front_road_direction    text,                           -- 前面道路：方位
    front_road_type         text,                           -- 前面道路：種類
    front_road_width        numeric(10,2),                  -- 前面道路：幅員（ｍ）
    city_planning           text,                           -- 都市計画
    coverage_ratio          smallint,                       -- 建ぺい率（％）
    floor_area_ratio        smallint,                       -- 容積率（％）
    transaction_period      text,                           -- 取引時期
    renovation              text,                           -- 改装
    transaction_notes       text,                           -- 取引の事情等
    
    -- システムカラム
    sys_created             timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sys_updated             timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX idx_reinfolib_estate_year_period_pref ON reinfolib_estate (year, period, prefecture_code);
CREATE INDEX idx_reinfolib_estate_year_period ON reinfolib_estate (year, period);
CREATE INDEX idx_reinfolib_estate_prefecture ON reinfolib_estate (prefecture_code);
CREATE INDEX idx_reinfolib_estate_transaction_price ON reinfolib_estate (transaction_price);
CREATE INDEX idx_reinfolib_estate_property_type ON reinfolib_estate (property_type);
CREATE INDEX idx_reinfolib_estate_area ON reinfolib_estate (area_sqm);
CREATE INDEX idx_reinfolib_estate_transaction_period ON reinfolib_estate (transaction_period);

-- コメント追加
COMMENT ON TABLE reinfolib_estate IS '国土交通省 不動産取引価格情報';
COMMENT ON COLUMN reinfolib_estate.year IS '取引年';
COMMENT ON COLUMN reinfolib_estate.period IS '四半期（1-4）';
COMMENT ON COLUMN reinfolib_estate.prefecture_code IS '都道府県コード（01-47）';
COMMENT ON COLUMN reinfolib_estate.property_type IS '種類（土地、土地と建物、中古マンション等、農地、林地）';
COMMENT ON COLUMN reinfolib_estate.price_info_category IS '価格情報区分';
COMMENT ON COLUMN reinfolib_estate.transaction_price IS '取引価格（総額）円';
COMMENT ON COLUMN reinfolib_estate.area_sqm IS '面積（平方メートル）';
COMMENT ON COLUMN reinfolib_estate.price_per_sqm IS '取引価格（平方メートル単価）円';
COMMENT ON COLUMN reinfolib_estate.price_per_tsubo IS '坪単価（円）';
COMMENT ON COLUMN reinfolib_estate.building_year IS '建築年（数値、例: 1984）';
COMMENT ON COLUMN reinfolib_estate.coverage_ratio IS '建ぺい率（パーセント）';
COMMENT ON COLUMN reinfolib_estate.floor_area_ratio IS '容積率（パーセント）';
COMMENT ON COLUMN reinfolib_estate.transaction_period IS '取引時期（例: 2006年第1四半期）';


-- ========================================
-- REINFOLIBの地価公示・地価調査データを格納するテーブル
-- 国土交通省の地価公示・地価調査データ
-- ========================================

-- reinfolib_landテーブル作成
CREATE TABLE reinfolib_land (
    -- 主キー
    id                      bigserial PRIMARY KEY,         -- 自動採番ID
    
    -- 追加カラム（ファイル情報）
    year                    smallint NOT NULL,              -- 調査年（例: 2024）
    prefecture_code         char(2) NOT NULL,               -- 都道府県コード（01-47）
    
    -- 基本情報
    category                text NOT NULL,                  -- 区分（地価公示、地価調査）
    reference_number        text NOT NULL,                  -- 標準地番号または基準地番号
    survey_date             date,                           -- 調査基準日
    location                text NOT NULL,                  -- 所在及び地番
    residential_address     text,                           -- 住居表示
    
    -- 価格情報（クレンジング済み）
    price_per_sqm           integer,                        -- 価格(円/㎡) - カンマと単位を除去
    
    -- 交通アクセス（クレンジング済み）
    station_name            text,                           -- 最寄駅名称
    station_distance        integer,                        -- 最寄駅距離(m) - 数値化、近接=0、接面=-1
    
    -- 土地情報（クレンジング済み）
    land_area               integer,                        -- 地積(㎡) - 数値化
    land_shape              text,                           -- 形状(間口：奥行) - 原文のまま保持
    land_use_category       text,                           -- 利用区分
    
    -- 建物情報
    building_structure      text,                           -- 建物構造
    building_floors         text,                           -- 階層
    current_use             text,                           -- 利用現況
    
    -- インフラ情報
    utilities               text,                           -- 給排水等状況
    
    -- 周辺環境
    surrounding_use         text,                           -- 周辺の土地の利用概況
    
    -- 前面道路情報
    front_road_direction    text,                           -- 前面道路：方位
    front_road_width        numeric(5,1),                   -- 前面道路：幅員(m) - 数値化
    front_road_type         text,                           -- 前面道路：種類
    front_road_pavement     text,                           -- 前面道路：舗装
    
    -- その他接面道路
    other_road_direction    text,                           -- その他接面道路：方位
    other_road_category     text,                           -- その他接面道路：区分
    
    -- 都市計画情報（クレンジング済み）
    use_district            text,                           -- 用途地域等
    height_district         text,                           -- 高度地区
    fire_prevention_area    text,                           -- 防火・準防火地域
    coverage_ratio          smallint,                       -- 建蔽率(%) - 数値化
    floor_area_ratio        smallint,                       -- 容積率(%) - 数値化
    
    -- 都市計画区域
    city_planning_area      text,                           -- 都市計画区域区分
    
    -- 法規制等
    forest_park_law         text,                           -- 森林法、公園法、自然環境等
    
    -- 鑑定評価書
    appraisal_report        text,                           -- 鑑定評価書有無
    appraisal_report_url    text,                           -- 鑑定評価書URL
    
    -- システムカラム
    sys_created             timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sys_updated             timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX idx_reinfolib_land_year_pref ON reinfolib_land (year, prefecture_code);
CREATE INDEX idx_reinfolib_land_year ON reinfolib_land (year);
CREATE INDEX idx_reinfolib_land_prefecture ON reinfolib_land (prefecture_code);
CREATE INDEX idx_reinfolib_land_price ON reinfolib_land (price_per_sqm);
CREATE INDEX idx_reinfolib_land_category ON reinfolib_land (category);
CREATE INDEX idx_reinfolib_land_use_district ON reinfolib_land (use_district);
CREATE INDEX idx_reinfolib_land_station ON reinfolib_land (station_name, station_distance);
CREATE INDEX idx_reinfolib_land_location ON reinfolib_land (location);

-- 複合ユニーク制約（同じ年、都道府県、基準地番号の組み合わせは一意）
CREATE UNIQUE INDEX idx_reinfolib_land_unique ON reinfolib_land (year, prefecture_code, reference_number);

-- コメント追加
COMMENT ON TABLE reinfolib_land IS '国土交通省 地価公示・地価調査データ';
COMMENT ON COLUMN reinfolib_land.year IS '調査年';
COMMENT ON COLUMN reinfolib_land.prefecture_code IS '都道府県コード（01-47）';
COMMENT ON COLUMN reinfolib_land.category IS '区分（地価公示、地価調査）';
COMMENT ON COLUMN reinfolib_land.reference_number IS '標準地番号または基準地番号（例: 鶴見-1）';
COMMENT ON COLUMN reinfolib_land.survey_date IS '調査基準日';
COMMENT ON COLUMN reinfolib_land.location IS '所在及び地番';
COMMENT ON COLUMN reinfolib_land.residential_address IS '住居表示';
COMMENT ON COLUMN reinfolib_land.price_per_sqm IS '価格（円/平方メートル）※林地は10a当たり';
COMMENT ON COLUMN reinfolib_land.station_name IS '最寄駅名称';
COMMENT ON COLUMN reinfolib_land.station_distance IS '最寄駅距離（メートル）※近接=0、接面=-1、駅前広場接面=-2';
COMMENT ON COLUMN reinfolib_land.land_area IS '地積（平方メートル）';
COMMENT ON COLUMN reinfolib_land.land_shape IS '形状（例: (1.0:2.0)、台形(1.0:1.5)）';
COMMENT ON COLUMN reinfolib_land.land_use_category IS '利用区分（建物などの敷地、田、畑、山林、林地等）';
COMMENT ON COLUMN reinfolib_land.building_structure IS '建物構造（SRC、RC、S、W、B、LS等）';
COMMENT ON COLUMN reinfolib_land.building_floors IS '階層（例: 2F）';
COMMENT ON COLUMN reinfolib_land.utilities IS '給排水等状況（ガス・水道・下水）';
COMMENT ON COLUMN reinfolib_land.front_road_width IS '前面道路幅員（メートル）';
COMMENT ON COLUMN reinfolib_land.front_road_pavement IS '前面道路舗装（舗装、未舗装）';
COMMENT ON COLUMN reinfolib_land.coverage_ratio IS '建蔽率（パーセント）';
COMMENT ON COLUMN reinfolib_land.floor_area_ratio IS '容積率（パーセント）';
COMMENT ON COLUMN reinfolib_land.appraisal_report IS '鑑定評価書有無';
COMMENT ON COLUMN reinfolib_land.appraisal_report_url IS '鑑定評価書URL';