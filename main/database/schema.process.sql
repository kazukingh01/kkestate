-- estate_mst_cleanedテーブル: クレンジング済み項目名マスタ
CREATE TABLE IF NOT EXISTS estate_mst_cleaned (
    id SMALLINT NOT NULL,
    name TEXT NOT NULL,
    type JSON,
    PRIMARY KEY (id)
);

-- estate_mst_cleaned用のシーケンス
CREATE SEQUENCE IF NOT EXISTS estate_mst_cleaned_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- シーケンスの所有権設定
ALTER SEQUENCE estate_mst_cleaned_id_seq OWNED BY estate_mst_cleaned.id;

-- idカラムのデフォルト値設定
ALTER TABLE estate_mst_cleaned ALTER COLUMN id SET DEFAULT nextval('estate_mst_cleaned_id_seq'::regclass);

-- 項目名の一意性制約
CREATE UNIQUE INDEX IF NOT EXISTS idx_estate_mst_cleaned_name ON estate_mst_cleaned(name);

-- estate_cleanedテーブル: クレンジング済みデータ
-- estate_detailと同じCSV構造でクレンジング済みデータを管理
CREATE TABLE IF NOT EXISTS estate_cleaned (
    id_run BIGINT NOT NULL,
    id_key SMALLINT NOT NULL,
    id_cleaned SMALLINT NOT NULL,
    value_cleaned JSON,
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
CREATE INDEX IF NOT EXISTS idx_estate_cleaned_spec1_run ON estate_cleaned(id_run) WHERE id_key = 1;


-- estate_detail_refテーブル: データ参照関係管理
-- 各run_idの各keyに対して、実際のデータがどのrun_idを参照しているかを管理
CREATE TABLE IF NOT EXISTS estate_detail_ref (
    id_run BIGINT NOT NULL,
    id_key SMALLINT NOT NULL,
    id_run_ref BIGINT NOT NULL,
    PRIMARY KEY (id_run, id_key),
    FOREIGN KEY (id_run) REFERENCES estate_run(id),
    FOREIGN KEY (id_key) REFERENCES estate_mst_key(id),
    FOREIGN KEY (id_run_ref) REFERENCES estate_run(id)
);

-- 検索用インデックス
CREATE INDEX IF NOT EXISTS idx_estate_detail_ref_run ON estate_detail_ref(id_run);
CREATE INDEX IF NOT EXISTS idx_estate_detail_ref_key ON estate_detail_ref(id_key);
CREATE INDEX IF NOT EXISTS idx_estate_detail_ref_run_ref ON estate_detail_ref(id_run_ref);
CREATE INDEX IF NOT EXISTS idx_estate_detail_ref_run_key ON estate_detail_ref(id_run, id_key);
CREATE INDEX IF NOT EXISTS idx_estate_detail_ref_spec1_run     ON estate_detail_ref(id_run)     WHERE id_key = 1;
CREATE INDEX IF NOT EXISTS idx_estate_detail_ref_spec1_run_ref ON estate_detail_ref(id_run_ref) WHERE id_key = 1;
