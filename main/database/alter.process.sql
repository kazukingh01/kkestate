-- estate_mst_key テーブルにクレンジング後の英語キー名を追加
ALTER TABLE estate_mst_key 
ADD COLUMN IF NOT EXISTS name_cleaned TEXT;

-- クレンジング後のキー名に対するインデックス
CREATE INDEX IF NOT EXISTS idx_estate_mst_key_cleaned 
ON estate_mst_key(name_cleaned);

-- コメント追加
COMMENT ON COLUMN estate_mst_key.name_cleaned IS 'クレンジング後の英語キー名（例：価格_第1期 → price）';

-- 初期データの例（実際の更新は後ほどプログラムで行う）
-- UPDATE estate_mst_key SET name_cleaned = 'price' WHERE name IN ('価格', '価格_第1期', '価格_第2期', '価格_第3期', '価格_第4期', '価格_第5期', '予定価格', '予定価格_第1期', '予定価格_第2期', '予定価格帯', '予定価格帯_第5期');
-- UPDATE estate_mst_key SET name_cleaned = 'layout' WHERE name IN ('間取り', '間取り_第1期', '間取り_第2期', '間取り_第3期', '間取り_第4期', '間取り_第5期');
-- UPDATE estate_mst_key SET name_cleaned = 'area' WHERE name IN ('専有面積', '専有面積_第1期', '専有面積_第2期', '専有面積_第3期', '専有面積_第4期', '専有面積_第5期');
-- UPDATE estate_mst_key SET name_cleaned = 'management_fee' WHERE name IN ('管理費', '管理費_第1期', '管理費_第2期', '管理費_第3期', '管理費_第4期', '管理費_第5期');
-- UPDATE estate_mst_key SET name_cleaned = 'repair_fund' WHERE name IN ('修繕積立金', '修繕積立金_第1期', '修繕積立金_第2期', '修繕積立金_第3期', '修繕積立金_第4期', '修繕積立金_第5期');
-- UPDATE estate_mst_key SET name_cleaned = 'address' WHERE name = '所在地';
-- UPDATE estate_mst_key SET name_cleaned = 'transport' WHERE name = '交通';
-- UPDATE estate_mst_key SET name_cleaned = 'total_units' WHERE name = '総戸数';
-- UPDATE estate_mst_key SET name_cleaned = 'completion_date' WHERE name IN ('完成時期', '完成時期_第1期', '完成時期_第2期', '完成時期_第3期', '完成時期_第4期', '完成時期_第5期');