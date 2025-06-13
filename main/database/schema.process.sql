-- estate_mst_cleanedテーブル: クレンジング済み項目名マスタ
CREATE TABLE IF NOT EXISTS estate_mst_cleaned (
    id SMALLINT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

-- 項目名の一意性制約
CREATE UNIQUE INDEX IF NOT EXISTS idx_estate_mst_cleaned_name ON estate_mst_cleaned(name);

-- estate_cleanedテーブル: クレンジング済みデータ
-- estate_detailと同じCSV構造でクレンジング済みデータを管理
CREATE TABLE IF NOT EXISTS estate_cleaned (
    id_run BIGINT NOT NULL,
    id_key SMALLINT NOT NULL,
    id_cleaned SMALLINT NOT NULL,
    value_cleaned TEXT,
    PRIMARY KEY (id_run, id_key),
    FOREIGN KEY (id_run) REFERENCES estate_run(id),
    FOREIGN KEY (id_key) REFERENCES estate_mst_key(id),
    FOREIGN KEY (id_cleaned) REFERENCES estate_mst_cleaned(id)
);

-- 検索用インデックス
CREATE INDEX IF NOT EXISTS idx_estate_cleaned_run ON estate_cleaned(id_run);
CREATE INDEX IF NOT EXISTS idx_estate_cleaned_key ON estate_cleaned(id_key);
CREATE INDEX IF NOT EXISTS idx_estate_cleaned_cleaned ON estate_cleaned(id_cleaned);
CREATE INDEX IF NOT EXISTS idx_estate_cleaned_run_cleaned ON estate_cleaned(id_run, id_cleaned);