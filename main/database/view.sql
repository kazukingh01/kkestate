-- estate_main拡張MATERIALIZED VIEW: URL解析による物件情報の追加
-- 
-- 目的: estate_mainテーブルのURLから以下の情報を抽出
-- - 物件タイプ (ms_new, ms_used, house_new, house_used)
-- - 新築/中古 (new, used)
-- - 建物タイプ (mansion, house)
-- - 都道府県 (47都道府県名)
-- - 市町村区 (sc_の後の文字列)
--
-- URL形式: /{property_type}/{prefecture}/sc_{city}/nc_{id}/
-- 例: /ms/chuko/tokyo/sc_koto/nc_74051837/

-- 既存のMATERIALIZED VIEWを削除（存在する場合）
DROP MATERIALIZED VIEW IF EXISTS estate_main_extended CASCADE;

CREATE MATERIALIZED VIEW estate_main_extended AS
SELECT 
    em.id,
    
    -- 物件タイプ判定 (ms: マンション, ikkodate: 一戸建て, tochi: 土地, shinchiku: 新築, chuko: 中古)
    CASE 
        WHEN em.url LIKE '/ms/shinchiku/%' THEN 'ms_new'
        WHEN em.url LIKE '/ms/chuko/%' THEN 'ms_used'
        WHEN em.url LIKE '/ikkodate/%' THEN 'house_new'
        WHEN em.url LIKE '/chukoikkodate/%' THEN 'house_used'
        WHEN em.url LIKE '/tochi/%' THEN 'land'
        ELSE 'unknown'
    END AS property_type,
    
    -- 新築/中古判定 (Boolean: true=新築, false=中古, null=土地・unknown)
    CASE 
        WHEN em.url LIKE '/ms/shinchiku/%' OR em.url LIKE '/ikkodate/%' THEN true
        WHEN em.url LIKE '/ms/chuko/%' OR em.url LIKE '/chukoikkodate/%' THEN false
        ELSE null
    END AS is_new,
    
    -- 建物タイプ判定
    CASE 
        WHEN em.url LIKE '/ms/%' THEN 'mansion'
        WHEN em.url LIKE '%ikkodate/%' THEN 'house'
        WHEN em.url LIKE '/tochi/%' THEN 'land'
        ELSE 'unknown'
    END AS building_type,
    
    -- 都道府県コード抽出（LIST_MST_URLSのprefecture部分に対応）
    CASE 
        WHEN em.url LIKE '%/hokkaido_/%' THEN 'hokkaido'
        WHEN em.url LIKE '%/aomori/%' THEN 'aomori'
        WHEN em.url LIKE '%/iwate/%' THEN 'iwate'
        WHEN em.url LIKE '%/akita/%' THEN 'akita'
        WHEN em.url LIKE '%/miyagi/%' THEN 'miyagi'
        WHEN em.url LIKE '%/yamagata/%' THEN 'yamagata'
        WHEN em.url LIKE '%/fukushima/%' THEN 'fukushima'
        WHEN em.url LIKE '%/niigata/%' THEN 'niigata'
        WHEN em.url LIKE '%/ishikawa/%' THEN 'ishikawa'
        WHEN em.url LIKE '%/toyama/%' THEN 'toyama'
        WHEN em.url LIKE '%/nagano/%' THEN 'nagano'
        WHEN em.url LIKE '%/yamanashi/%' THEN 'yamanashi'
        WHEN em.url LIKE '%/fukui/%' THEN 'fukui'
        WHEN em.url LIKE '%/tochigi/%' THEN 'tochigi'
        WHEN em.url LIKE '%/gumma/%' THEN 'gumma'
        WHEN em.url LIKE '%/saitama/%' THEN 'saitama'
        WHEN em.url LIKE '%/ibaraki/%' THEN 'ibaraki'
        WHEN em.url LIKE '%/chiba/%' THEN 'chiba'
        WHEN em.url LIKE '%/tokyo/%' THEN 'tokyo'
        WHEN em.url LIKE '%/kanagawa/%' THEN 'kanagawa'
        WHEN em.url LIKE '%/gifu/%' THEN 'gifu'
        WHEN em.url LIKE '%/shizuoka/%' THEN 'shizuoka'
        WHEN em.url LIKE '%/aichi/%' THEN 'aichi'
        WHEN em.url LIKE '%/mie/%' THEN 'mie'
        WHEN em.url LIKE '%/shiga/%' THEN 'shiga'
        WHEN em.url LIKE '%/kyoto/%' THEN 'kyoto'
        WHEN em.url LIKE '%/osaka/%' THEN 'osaka'
        WHEN em.url LIKE '%/nara/%' THEN 'nara'
        WHEN em.url LIKE '%/wakayama/%' THEN 'wakayama'
        WHEN em.url LIKE '%/hyogo/%' THEN 'hyogo'
        WHEN em.url LIKE '%/tottori/%' THEN 'tottori'
        WHEN em.url LIKE '%/shimane/%' THEN 'shimane'
        WHEN em.url LIKE '%/okayama/%' THEN 'okayama'
        WHEN em.url LIKE '%/hiroshima/%' THEN 'hiroshima'
        WHEN em.url LIKE '%/yamaguchi/%' THEN 'yamaguchi'
        WHEN em.url LIKE '%/kagawa/%' THEN 'kagawa'
        WHEN em.url LIKE '%/tokushima/%' THEN 'tokushima'
        WHEN em.url LIKE '%/kochi/%' THEN 'kochi'
        WHEN em.url LIKE '%/ehime/%' THEN 'ehime'
        WHEN em.url LIKE '%/fukuoka/%' THEN 'fukuoka'
        WHEN em.url LIKE '%/oita/%' THEN 'oita'
        WHEN em.url LIKE '%/saga/%' THEN 'saga'
        WHEN em.url LIKE '%/nagasaki/%' THEN 'nagasaki'
        WHEN em.url LIKE '%/kumamoto/%' THEN 'kumamoto'
        WHEN em.url LIKE '%/miyazaki/%' THEN 'miyazaki'
        WHEN em.url LIKE '%/kagoshima/%' THEN 'kagoshima'
        WHEN em.url LIKE '%/okinawa/%' THEN 'okinawa'
        ELSE 'unknown'
    END AS prefecture,
    
    -- 市町村区コード抽出（sc_の後、/nc_の前の文字列を抽出）
    CASE 
        WHEN em.url ~ '/sc_[^/]+/' THEN 
            SUBSTRING(em.url FROM '/sc_([^/]+)/')
        ELSE 'unknown'
    END AS city,
    
    -- 物件ID抽出（nc_の後、/の前の数字を抽出）
    CASE 
        WHEN em.url ~ '/nc_[0-9]+/' THEN 
            SUBSTRING(em.url FROM '/nc_([0-9]+)/')
        ELSE 'unknown'
    END AS property_id,
    
    -- 更新日時（最後に配置）
    em.sys_updated
    
FROM estate_main em;

-- インデックス作成
-- 1. 主キー（既存のestate_mainのidに対応）
CREATE UNIQUE INDEX idx_estate_main_extended_id ON estate_main_extended (id);

-- 2. 新規フィールドに対するインデックス
CREATE INDEX idx_estate_main_extended_property_type ON estate_main_extended (property_type);
CREATE INDEX idx_estate_main_extended_is_new ON estate_main_extended (is_new);
CREATE INDEX idx_estate_main_extended_building_type ON estate_main_extended (building_type);
CREATE INDEX idx_estate_main_extended_prefecture ON estate_main_extended (prefecture);
CREATE INDEX idx_estate_main_extended_city ON estate_main_extended (city);
CREATE INDEX idx_estate_main_extended_property_id ON estate_main_extended (property_id);
CREATE INDEX idx_estate_main_extended_sys_updated ON estate_main_extended (sys_updated);

-- 3. 複合インデックス（検索パフォーマンス向上）
CREATE INDEX idx_estate_main_extended_pref_type ON estate_main_extended (prefecture, property_type);
CREATE INDEX idx_estate_main_extended_pref_city ON estate_main_extended (prefecture, city);
CREATE INDEX idx_estate_main_extended_type_isnew ON estate_main_extended (building_type, is_new);

-- 4. sys_updated も追加し、インデックス設定完了

-- MATERIALIZED VIEWの更新コマンド
-- REFRESH MATERIALIZED VIEW estate_main_extended;

-- 使用例:
-- 1. 物件タイプ別統計
-- SELECT property_type, COUNT(*) FROM estate_main_extended GROUP BY property_type;
--
-- 2. 都道府県別統計
-- SELECT prefecture, COUNT(*) FROM estate_main_extended GROUP BY prefecture ORDER BY COUNT(*) DESC;
--
-- 3. 東京都の新築マンション
-- SELECT * FROM estate_main_extended WHERE prefecture = 'tokyo' AND property_type = 'ms_new';
--
-- 4. 中古物件のみ
-- SELECT * FROM estate_main_extended WHERE is_new = false;
--
-- 5. 新築物件のみ
-- SELECT * FROM estate_main_extended WHERE is_new = true;
--
-- 6. 土地のみ
-- SELECT * FROM estate_main_extended WHERE building_type = 'land';

-- 統計情報:
-- 物件タイプ分布 (全データ):
-- - house_new: 42.58% (新築一戸建て)
-- - ms_used: 33.49% (中古マンション) 
-- - house_used: 20.90% (中古一戸建て)
-- - land: 2.73% (土地)
-- - ms_new: 0.30% (新築マンション)
--
-- 建物タイプ分布 (全データ):
-- - house: 63.48% (一戸建て)
-- - mansion: 33.79% (マンション)
-- - land: 2.73% (土地)
--
-- 都道府県分布 (10,000件サンプル):
-- - other: 23.82% (その他都道府県)
-- - hokkaido: 19.91%
-- - tokyo: 18.85%
-- - kanagawa: 17.21%
-- - fukuoka: 7.61%
-- - saitama: 6.23%
-- - osaka: 3.44%
-- - hyogo: 1.44%
-- - chiba: 1.34%
-- - aichi: 0.15%