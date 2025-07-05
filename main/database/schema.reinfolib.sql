-- REINFOLIBの不動産取引価格情報を格納するテーブル
-- 国土交通省の不動産取引価格情報ダウンロードデータ

-- テーブル削除（再作成時用）
DROP TABLE IF EXISTS reinfolib_estate CASCADE;

-- reinfolib_estateテーブル作成
CREATE TABLE reinfolib_estate (
    -- 追加カラム（主キー用）
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
    building_year           text,                           -- 建築年
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
    sys_updated             timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 主キー制約
    CONSTRAINT pk_reinfolib_estate PRIMARY KEY (year, period, prefecture_code)
);

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
COMMENT ON COLUMN reinfolib_estate.building_year IS '建築年（例: 1984年）';
COMMENT ON COLUMN reinfolib_estate.coverage_ratio IS '建ぺい率（パーセント）';
COMMENT ON COLUMN reinfolib_estate.floor_area_ratio IS '容積率（パーセント）';
COMMENT ON COLUMN reinfolib_estate.transaction_period IS '取引時期（例: 2006年第1四半期）';