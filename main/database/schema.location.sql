-- 住所と緯度経度のマスターテーブル
-- 国土地理院APIで取得した位置情報を格納

-- estate_mst_locationテーブル作成
CREATE TABLE estate_mst_location (
    -- 主キー
    location                text PRIMARY KEY,               -- 住所（所在地）
    
    -- 位置情報
    longitude               double precision,               -- 経度
    latitude                double precision,               -- 緯度
    
    -- システムカラム
    sys_created             timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sys_updated             timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX idx_estate_mst_location_coords ON estate_mst_location (longitude, latitude);

-- コメント追加
COMMENT ON TABLE estate_mst_location IS '住所緯度経度マスターテーブル';
COMMENT ON COLUMN estate_mst_location.location IS '住所（所在地）';
COMMENT ON COLUMN estate_mst_location.longitude IS '経度';
COMMENT ON COLUMN estate_mst_location.latitude IS '緯度';
COMMENT ON COLUMN estate_mst_location.sys_created IS '作成日時';
COMMENT ON COLUMN estate_mst_location.sys_updated IS '更新日時';