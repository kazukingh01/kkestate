-- estate_cleaned: クレンジング済みデータを保管するテーブル
-- データはJSONB型で柔軟に保管し、将来的な項目追加にも対応可能
CREATE TABLE IF NOT EXISTS estate_cleaned (
    id_run BIGINT NOT NULL,                         -- estate_runのID（PK）
    id_main BIGINT NOT NULL,                        -- estate_mainテーブルのID（FK）
    data JSONB NOT NULL,                            -- クレンジング済みデータ（JSON形式）
    sys_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- レコード作成日時
    sys_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- レコード更新日時
    PRIMARY KEY (id_run),
    FOREIGN KEY (id_main) REFERENCES estate_main(id),
    FOREIGN KEY (id_run) REFERENCES estate_run(id)
);

-- 物件IDでの検索用インデックス
CREATE INDEX idx_estate_cleaned_main ON estate_cleaned(id_main);

-- 更新日時の自動更新用インデックス
CREATE INDEX idx_estate_cleaned_updated ON estate_cleaned(sys_updated);

-- JSON内の特定フィールドに対する検索用インデックス（例）
-- 価格での検索が多い場合
CREATE INDEX idx_estate_cleaned_price ON estate_cleaned((data->>'price'));
-- 住所での検索が多い場合
CREATE INDEX idx_estate_cleaned_address ON estate_cleaned((data->>'address'));
-- 間取りでの検索が多い場合
CREATE INDEX idx_estate_cleaned_layout ON estate_cleaned((data->>'layout'));

-- JSONBのGINインデックス（JSON内の任意のキーでの検索を高速化）
CREATE INDEX idx_estate_cleaned_data_gin ON estate_cleaned USING GIN (data);

-- データ例：
-- {
--   "price": 28990000,
--   "price_raw": "2899万円",
--   "price_range": {"min": null, "max": null},
--   "address": "広島県広島市安佐南区長束西１",
--   "address_parsed": {
--     "prefecture": "広島県",
--     "city": "広島市",
--     "ward": "安佐南区",
--     "detail": "長束西１"
--   },
--   "transport": [
--     {"line": "ＪＲ可部線", "station": "安芸長束", "walk_minutes": 9},
--     {"line": "ＪＲ可部線", "station": "三滝", "walk_minutes": 17}
--   ],
--   "layout": "3LDK",
--   "layout_parsed": {"rooms": 3, "type": "LDK"},
--   "area": 75.5,
--   "area_raw": "75.5㎡",
--   "completion_date": "2024-03-31",
--   "total_units": 120,
--   "management_fee": 12000,
--   "repair_fund": 8000,
--   "sales_period": "第1期",
--   "original_keys": {
--     "価格": "価格_第1期", 
--     "間取り": "間取り_第1期"
--   }
-- }