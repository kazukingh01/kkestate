from kkestate.util.json_cleaner import (
    clean_address_to_json, clean_access_to_json, clean_units_to_json,
    clean_zoning_to_json, clean_force_null_to_json, clean_date_to_json,
    clean_delivery_date_to_json, clean_price_to_json, clean_management_fee_to_json,
    clean_other_expenses_to_json, clean_layout_to_json, clean_area_to_json,
    clean_multiple_area_to_json, clean_restrictions_to_json, clean_text_to_json,
    clean_expiry_date_to_json, clean_number_to_json,
    clean_feature_pickup_to_json, clean_reform_to_json, clean_building_structure_to_json,
    clean_parking_to_json, clean_utility_cost_to_json, clean_price_band_to_json,
    clean_land_use_to_json, clean_surrounding_facilities_to_json, clean_building_coverage_to_json,
    clean_floor_plan_to_json
)

EXPECTED_KEY_PROCESSING = [
    {
        "key_name": "所在地",
        "expected_cleaned_name": "住所",
        "expected_function": clean_address_to_json,
        "expected_base_type": "structured_address"
    },
    {
        "key_name": "交通",
        "expected_cleaned_name": "交通",
        "expected_function": clean_access_to_json,
        "expected_base_type": "access_routes"
    },
    {
        "key_name": "総戸数",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "用途地域",
        "expected_cleaned_name": "用途地域",
        "expected_function": clean_zoning_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "敷地の権利形態",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "販売スケジュール",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "価格",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "会社情報",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "施工",
        "expected_cleaned_name": "施工会社",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "管理",
        "expected_cleaned_name": "管理会社",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "予定価格",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "不動産会社ガイド",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "販売スケジュール_第5期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第5期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第5期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第5期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格帯_第5期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第5期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第5期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第5期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第5期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第5期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第5期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第5期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第5期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第5期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項_第5期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第5期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第5期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "販売スケジュール_第4期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第4期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第4期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第4期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "価格_第4期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第4期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第4期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第4期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第4期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第4期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第4期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第4期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第4期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第4期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "所在階_第4期",
        "expected_cleaned_name": "所在階",
        "expected_function": clean_number_to_json,
        "expected_base_type": "number_with_unit"
    },
    {
        "key_name": "向き_第4期",
        "expected_cleaned_name": "向き",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "制限事項_第4期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第4期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第4期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "所在階",
        "expected_cleaned_name": "所在階",
        "expected_function": clean_number_to_json,
        "expected_base_type": "number_with_unit"
    },
    {
        "key_name": "向き",
        "expected_cleaned_name": "向き",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "販売スケジュール_第2期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第2期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第2期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第2期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格_第2期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第2期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第2期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第2期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第2期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第2期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第2期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第2期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第2期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第2期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項_第2期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第2期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第2期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格帯",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "販売スケジュール_第1期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第1期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第1期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第1期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "価格_第1期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第1期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第1期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第1期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第1期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第1期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第1期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第1期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第1期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第1期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項_第1期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第1期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第1期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "所在階_第1期",
        "expected_cleaned_name": "所在階",
        "expected_function": clean_number_to_json,
        "expected_base_type": "number_with_unit"
    },
    {
        "key_name": "向き_第1期",
        "expected_cleaned_name": "向き",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "価格_第2期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第2期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "特徴ピックアップ",
        "expected_cleaned_name": "特徴",
        "expected_function": clean_feature_pickup_to_json,
        "expected_base_type": "structured_features"
    },
    {
        "key_name": "物件名",
        "expected_cleaned_name": "物件名",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "販売戸数",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "所在階/構造・階建",
        "expected_cleaned_name": "構造階建",
        "expected_function": clean_building_structure_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "完成時期（築年月）",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "住所",
        "expected_cleaned_name": "住所",
        "expected_function": clean_address_to_json,
        "expected_base_type": "structured_address"
    },
    {
        "key_name": "関連リンク",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "お問い合せ先",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "周辺施設",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "イベント情報",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "諸費用",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "完成時期(築年月)",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "リフォーム",
        "expected_cleaned_name": "リフォーム",
        "expected_function": clean_reform_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "その他制限事項",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他概要・特記事項",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "構造・階建て",
        "expected_cleaned_name": "構造階建",
        "expected_function": clean_building_structure_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "敷地面積",
        "expected_cleaned_name": "土地面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "駐車場",
        "expected_cleaned_name": "駐車場",
        "expected_function": clean_parking_to_json,
        "expected_base_type": "parking_info"
    },
    {
        "key_name": "会社概要",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "問い合わせ先",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "施工\n",
        "expected_cleaned_name": "施工会社",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "情報提供日",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "次回更新日",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "担当者より",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "周辺環境",
        "expected_cleaned_name": "周辺施設",
        "expected_function": clean_surrounding_facilities_to_json,
        "expected_base_type": "structured_features"
    },
    {
        "key_name": "プレゼント情報",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "販売スケジュール_第3期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第3期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第3期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第3期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格帯_第3期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第3期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第3期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第3期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第3期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第3期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第3期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第3期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第3期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第3期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項_第3期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第3期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第3期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格_第1期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第1期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "見学可能な日程",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "物件の特徴",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "土地面積",
        "expected_cleaned_name": "土地面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "建物面積",
        "expected_cleaned_name": "建物面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "私道負担・道路",
        "expected_cleaned_name": None, # データの意味が正しく理解できていないので保留
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "建ぺい率・容積率",
        "expected_cleaned_name": "建ぺい率容積率",
        "expected_function": clean_building_coverage_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "土地の権利形態",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "構造・工法",
        "expected_cleaned_name": "構造階建",
        "expected_function": clean_building_structure_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "地目",
        "expected_cleaned_name": "地目",
        "expected_function": clean_land_use_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "カーナビご利用の方",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "間取り図",
        "expected_cleaned_name": "間取り図",
        "expected_function": clean_floor_plan_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "建ぺい率･容積率",
        "expected_cleaned_name": "建ぺい率容積率",
        "expected_function": clean_building_coverage_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "販売区画数",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "総区画数",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "土地状況",
        "expected_cleaned_name": "土地状況",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "造成完了時期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "建築条件",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "引き渡し時期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格帯_第1期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定価格_第3期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定価格帯_第4期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第4期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "価格_第3期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第3期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定価格_第5期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定価格帯_第2期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "所在階_第2期",
        "expected_cleaned_name": "所在階",
        "expected_function": clean_number_to_json,
        "expected_base_type": "number_with_unit"
    },
    {
        "key_name": "向き_第2期",
        "expected_cleaned_name": "向き",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "販売スケジュール_第7期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第7期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第7期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第7期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格帯_第7期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第7期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第7期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第7期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第7期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第7期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第7期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第7期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第7期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第7期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項_第7期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第7期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第7期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格_第4期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "価格_第5期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第5期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "販売スケジュール_第6期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第6期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第6期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第6期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "価格_第6期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第6期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第6期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第6期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第6期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第6期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第6期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第6期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第6期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第6期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項_第6期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第6期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第6期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "所在階_第3期",
        "expected_cleaned_name": "所在階",
        "expected_function": clean_number_to_json,
        "expected_base_type": "number_with_unit"
    },
    {
        "key_name": "向き_第3期",
        "expected_cleaned_name": "向き",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "所在階_第5期",
        "expected_cleaned_name": "所在階",
        "expected_function": clean_number_to_json,
        "expected_base_type": "number_with_unit"
    },
    {
        "key_name": "向き_第5期",
        "expected_cleaned_name": "向き",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "価格_第7期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第7期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "所在階_第7期",
        "expected_cleaned_name": "所在階",
        "expected_function": clean_number_to_json,
        "expected_base_type": "number_with_unit"
    },
    {
        "key_name": "向き_第7期",
        "expected_cleaned_name": "向き",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "所在階_第6期",
        "expected_cleaned_name": "所在階",
        "expected_function": clean_number_to_json,
        "expected_base_type": "number_with_unit"
    },
    {
        "key_name": "向き_第6期",
        "expected_cleaned_name": "向き",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "予定価格_第6期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第6期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "お知らせ／その他",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "販売スケジュール_第8期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第8期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第8期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第8期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格帯_第8期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第8期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第8期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第8期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第8期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第8期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第8期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第8期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第8期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第8期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項_第8期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第8期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第8期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格帯_第6期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定価格_第7期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "価格_第8期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第8期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "所在階_第8期",
        "expected_cleaned_name": "所在階",
        "expected_function": clean_number_to_json,
        "expected_base_type": "number_with_unit"
    },
    {
        "key_name": "向き_第8期",
        "expected_cleaned_name": "向き",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    },
    {
        "key_name": "販売スケジュール_第9期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第9期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第9期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第9期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "価格_第9期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第9期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第9期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第9期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第9期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第9期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第9期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第9期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第9期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第9期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項_第9期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第9期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第9期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格帯_第9期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第9期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "価格 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "間取り ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "販売戸数 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "総戸数 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "土地面積 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "建物面積 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "私道負担・道路 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期（築年月） ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "最多価格帯 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "諸費用 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "建ぺい率・容積率 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期(築年月) ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "引渡可能時期 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "土地の権利形態 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "構造・工法 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "施工 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "リフォーム ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "用途地域 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "地目 ヒント",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "販売スケジュール_第10期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第10期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第10期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第10期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格帯_第10期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第10期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第10期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第10期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第10期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第10期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第10期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第10期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第10期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第10期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項_第10期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第10期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第10期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格_第8期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "エネルギー消費性能",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "断熱性能",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "目安光熱費",
        "expected_cleaned_name": "目安光熱費",
        "expected_function": clean_utility_cost_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定価格_第9期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定価格_第10期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "価格_第10期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第10期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "販売スケジュール_第11期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "完成時期_第11期",
        "expected_cleaned_name": "築年月",
        "expected_function": clean_date_to_json,
        "expected_base_type": "date_or_period"
    },
    {
        "key_name": "引渡可能時期_第11期",
        "expected_cleaned_name": "引渡時期",
        "expected_function": clean_delivery_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "今回販売戸数_第11期",
        "expected_cleaned_name": "戸数",
        "expected_function": clean_units_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "予定価格_第11期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "予定最多価格帯_第11期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理費_第11期",
        "expected_cleaned_name": "管理費",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "管理準備金_第11期",
        "expected_cleaned_name": "管理準備金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立金_第11期",
        "expected_cleaned_name": "修繕積立金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "修繕積立基金_第11期",
        "expected_cleaned_name": "修繕積立基金",
        "expected_function": clean_management_fee_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他諸経費_第11期",
        "expected_cleaned_name": "他経費",
        "expected_function": clean_other_expenses_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "間取り_第11期",
        "expected_cleaned_name": "間取り",
        "expected_function": clean_layout_to_json,
        "expected_base_type": "structured_layout"
    },
    {
        "key_name": "専有面積_第11期",
        "expected_cleaned_name": "専有面積",
        "expected_function": clean_area_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "その他面積_第11期",
        "expected_cleaned_name": "その他面積",
        "expected_function": clean_multiple_area_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "制限事項_第11期",
        "expected_cleaned_name": "制限事項",
        "expected_function": clean_restrictions_to_json,
        "expected_base_type": "array"
    },
    {
        "key_name": "その他_第11期",
        "expected_cleaned_name": None,
        "expected_function": clean_force_null_to_json,
        "expected_base_type": "null"
    },
    {
        "key_name": "取引条件有効期限_第11期",
        "expected_cleaned_name": "取引条件有効期限",
        "expected_function": clean_expiry_date_to_json,
        "expected_base_type": "single"
    },
    {
        "key_name": "価格_第11期",
        "expected_cleaned_name": "価格",
        "expected_function": clean_price_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "最多価格帯_第11期",
        "expected_cleaned_name": "価格帯",
        "expected_function": clean_price_band_to_json,
        "expected_base_type": "range_or_single"
    },
    {
        "key_name": "所在階_第9期",
        "expected_cleaned_name": "所在階",
        "expected_function": clean_number_to_json,
        "expected_base_type": "number_with_unit"
    },
    {
        "key_name": "向き_第9期",
        "expected_cleaned_name": "向き",
        "expected_function": clean_text_to_json,
        "expected_base_type": "structured_text"
    }
]

TEST_CASES_ADDRESS = [
    {"input": "東京都中央区晴海５", "expected": {"raw": "東京都中央区晴海５", "prefecture": "東京都", "secondary_division": "中央区", "secondary_type": "特別区", "tertiary_division": None, "tertiary_type": None, "remaining": "晴海５", "hierarchy": "東京都 -> 中央区", "division_types": "特別区"}},
    {"input": "神奈川県横浜市保土ケ谷区上菅田町", "expected": {"raw": "神奈川県横浜市保土ケ谷区上菅田町", "prefecture": "神奈川県", "secondary_division": "横浜市", "secondary_type": "市", "tertiary_division": None, "tertiary_type": None, "remaining": "保土ケ谷区上菅田町", "hierarchy": "神奈川県 -> 横浜市", "division_types": "市"}},
    {"input": "神奈川県愛甲郡愛川町中津", "expected": {"raw": "神奈川県愛甲郡愛川町中津", "prefecture": "神奈川県", "secondary_division": "愛甲郡", "secondary_type": "郡", "tertiary_division": "愛川町", "tertiary_type": "町", "remaining": "中津", "hierarchy": "神奈川県 -> 愛甲郡 -> 愛川町", "division_types": "郡 -> 町"}},
    {"input": "大阪府大阪市淀川区西宮原３", "expected": {"raw": "大阪府大阪市淀川区西宮原３", "prefecture": "大阪府", "secondary_division": "大阪市", "secondary_type": "市", "tertiary_division": None, "tertiary_type": None, "remaining": "淀川区西宮原３", "hierarchy": "大阪府 -> 大阪市", "division_types": "市"}},
    {"input": "京都府京都市南区吉祥院石原長田町", "expected": {"raw": "京都府京都市南区吉祥院石原長田町", "prefecture": "京都府", "secondary_division": "京都市", "secondary_type": "市", "tertiary_division": None, "tertiary_type": None, "remaining": "南区吉祥院石原長田町", "hierarchy": "京都府 -> 京都市", "division_types": "市"}},
    {"input": "愛知県愛知郡東郷町和合ケ丘２", "expected": {"raw": "愛知県愛知郡東郷町和合ケ丘２", "prefecture": "愛知県", "secondary_division": "愛知郡", "secondary_type": "郡", "tertiary_division": "東郷町", "tertiary_type": "町", "remaining": "和合ケ丘２", "hierarchy": "愛知県 -> 愛知郡 -> 東郷町", "division_types": "郡 -> 町"}},
    {"input": "静岡県浜松市中央区早出町", "expected": {"raw": "静岡県浜松市中央区早出町", "prefecture": "静岡県", "secondary_division": "浜松市", "secondary_type": "市", "tertiary_division": None, "tertiary_type": None, "remaining": "中央区早出町", "hierarchy": "静岡県 -> 浜松市", "division_types": "市"}},
    {"input": "東京都あきる野市二宮", "expected": {"raw": "東京都あきる野市二宮", "prefecture": "東京都", "secondary_division": "あきる野市", "secondary_type": "市", "tertiary_division": None, "tertiary_type": None, "remaining": "二宮", "hierarchy": "東京都 -> あきる野市", "division_types": "市"}},
    {"input": "千葉県佐倉市井野", "expected": {"raw": "千葉県佐倉市井野", "prefecture": "千葉県", "secondary_division": "佐倉市", "secondary_type": "市", "tertiary_division": None, "tertiary_type": None, "remaining": "井野", "hierarchy": "千葉県 -> 佐倉市", "division_types": "市"}},
    {"input": "岐阜県可児市土田", "expected": {"raw": "岐阜県可児市土田", "prefecture": "岐阜県", "secondary_division": "可児市", "secondary_type": "市", "tertiary_division": None, "tertiary_type": None, "remaining": "土田", "hierarchy": "岐阜県 -> 可児市", "division_types": "市"}}
]

TEST_CASES_ACCESS = [
    {"input": "ＪＲ阪和線「新家」歩5分\t[乗り換え案内]", "expected": {"routes": [{"line": "ＪＲ阪和線", "station": "新家", "method": "歩", "time": 5}]}},
    {"input": "ＪＲ東海道本線「灘」歩6分\t[乗り換え案内]\t阪急神戸線「王子公園」歩10分\t[乗り換え案内]\t阪神本線「岩屋」歩10分\t[乗り換え案内]", "expected": {"routes": [{"line": "ＪＲ東海道本線", "station": "灘", "method": "歩", "time": 6}, {"line": "阪急神戸線", "station": "王子公園", "method": "歩", "time": 10}, {"line": "阪神本線", "station": "岩屋", "method": "歩", "time": 10}]}},
    {"input": "ＪＲ福知山線「中山寺」バス7分鴻池歩8分\t[乗り換え案内]\tＪＲ福知山線「中山寺」歩36分\t[乗り換え案内]\t阪急宝塚線「中山観音」歩46分\t[乗り換え案内]", "expected": {"routes": [{"line": "ＪＲ福知山線", "station": "中山寺", "method": "バス", "time": 7}, {"line": "ＪＲ福知山線", "station": "中山寺", "method": "歩", "time": 36}, {"line": "阪急宝塚線", "station": "中山観音", "method": "歩", "time": 46}]}},
    {"input": "小田急江ノ島線「湘南台」バス17分五反田歩5分\t[乗り換え案内]\tブルーライン「湘南台」バス17分五反田歩5分\t[乗り換え案内]\t相鉄いずみ野線「湘南台」バス17分五反田歩5分\t[乗り換え案内]", "expected": {"routes": [{"line": "小田急江ノ島線", "station": "湘南台", "method": "バス", "time": 17}, {"line": "ブルーライン", "station": "湘南台", "method": "バス", "time": 17}, {"line": "相鉄いずみ野線", "station": "湘南台", "method": "バス", "time": 17}]}},
    {"input": "ＪＲ山手線「目黒」歩7分\t[乗り換え案内]\t東京メトロ南北線「白金台」歩7分\t[乗り換え案内]\t都営浅草線「高輪台」歩12分\t[乗り換え案内]", "expected": {"routes": [{"line": "ＪＲ山手線", "station": "目黒", "method": "歩", "time": 7}, {"line": "東京メトロ南北線", "station": "白金台", "method": "歩", "time": 7}, {"line": "都営浅草線", "station": "高輪台", "method": "歩", "time": 12}]}},
    {"input": "東急田園都市線「梶が谷」歩6分\t[乗り換え案内]\t東急田園都市線「溝の口」歩12分\t[乗り換え案内]\tＪＲ南武線「武蔵溝ノ口」歩14分\t[乗り換え案内]", "expected": {"routes": [{"line": "東急田園都市線", "station": "梶が谷", "method": "歩", "time": 6}, {"line": "東急田園都市線", "station": "溝の口", "method": "歩", "time": 12}, {"line": "ＪＲ南武線", "station": "武蔵溝ノ口", "method": "歩", "time": 14}]}},
    {"input": "都営三田線「本蓮沼」歩8分\t[乗り換え案内]\t都営三田線「志村坂上」歩10分\t[乗り換え案内]\t東武東上線「ときわ台」歩20分\t[乗り換え案内]", "expected": {"routes": [{"line": "都営三田線", "station": "本蓮沼", "method": "歩", "time": 8}, {"line": "都営三田線", "station": "志村坂上", "method": "歩", "time": 10}, {"line": "東武東上線", "station": "ときわ台", "method": "歩", "time": 20}]}},
    {"input": "西武新宿線「都立家政」歩7分\t[乗り換え案内]\t西武新宿線「野方」歩8分\t[乗り換え案内]", "expected": {"routes": [{"line": "西武新宿線", "station": "都立家政", "method": "歩", "time": 7}, {"line": "西武新宿線", "station": "野方", "method": "歩", "time": 8}]}},
    {"input": "ＪＲ日豊本線「鶴崎」車3.2km\t[乗り換え案内]", "expected": {"value": "ＪＲ日豊本線「鶴崎」車3.2km\t[乗り換え案内]"}},
    {"input": "-", "expected": {"value": None}}
]

TEST_CASES_UNITS1 = [
    {"input": "-", "expected": {"value": None}},
    {"input": "1戸", "expected": {"value": 1, "unit": "戸", "is_total": True}},
    {"input": "88戸", "expected": {"value": 88, "unit": "戸", "is_total": True}},
    {"input": "1342戸", "expected": {"value": 1342, "unit": "戸", "is_total": True}},
    {"input": "67戸（管理事務室・防災倉庫を除く）", "expected": {"value": 67, "unit": "戸", "note": "管理事務室・防災倉庫を除く", "is_total": True}},
    {"input": "40戸（うち非分譲住戸36戸）", "expected": {"value": 40, "unit": "戸", "note": "うち非分譲住戸36戸", "is_total": True}},
    {"input": "88戸（ほか地権者用住戸18戸、店舗8区画）", "expected": {"value": 88, "unit": "戸", "note": "ほか地権者用住戸18戸、店舗8区画", "is_total": True}},
    {"input": "115戸（1階約9区画）", "expected": {"value": 115, "unit": "戸", "note": "1階約9区画", "is_total": True}},
    {"input": "134戸（1階店舗1区画）", "expected": {"value": 134, "unit": "戸", "note": "1階店舗1区画", "is_total": True}},
    {"input": "2戸", "expected": {"value": 2, "unit": "戸", "is_total": True}},
]

TEST_CASES_UNITS2 = [
    {"input": "未定", "expected": {"value": None}},
    {"input": "3戸", "expected": {"value": 3, "unit": "戸", "is_current_sale": True}},
    {"input": "2戸（先着順）", "expected": {"value": 2, "unit": "戸", "note": "先着順", "is_current_sale": True}},
    {"input": "5戸（うちモデルルーム住戸1戸）", "expected": {"value": 5, "unit": "戸", "note": "うちモデルルーム住戸1戸", "is_current_sale": True}},
    {"input": "1戸（モデルルーム販売のみ）", "expected": {"value": 1, "unit": "戸", "note": "モデルルーム販売のみ", "is_current_sale": True}},
    {"input": "2戸（最終期）", "expected": {"value": 2, "unit": "戸", "note": "最終期", "is_current_sale": True}},
    {"input": "1戸（キャンセル住戸）", "expected": {"value": 1, "unit": "戸", "note": "キャンセル住戸", "is_current_sale": True}},
    {"input": "10戸（C1棟:3戸/D棟:7戸）", "expected": {"value": 10, "unit": "戸", "note": "C1棟:3戸/D棟:7戸", "is_current_sale": True}},
    {"input": "21戸（イーストタワー棟：17戸・サウスレジデンス棟：4戸）", "expected": {"value": 21, "unit": "戸", "note": "イーストタワー棟：17戸・サウスレジデンス棟：4戸", "is_current_sale": True}},
    {"input": "5戸（うちモデルルーム家具付き分譲住戸2戸・商談室使用住戸1戸・事務所使用住戸1戸）", "expected": {"value": 5, "unit": "戸", "note": "うちモデルルーム家具付き分譲住戸2戸・商談室使用住戸1戸・事務所使用住戸1戸", "is_current_sale": True}}
]

TEST_CASES_ZONING = [
    {"input": "-", "expected": {"values": []}},
    {"input": "１種低層", "expected": {"values": ["１種低層"]}},
    {"input": "１種低層、１種中高", "expected": {"values": ["１種低層", "１種中高"]}},
    {"input": "商業、１種住居", "expected": {"values": ["商業", "１種住居"]}},
    {"input": "市街化調整区域、無指定", "expected": {"values": ["市街化調整区域", "無指定"]}},
    {"input": "第一種中高層住居専用地域", "expected": {"values": ["第一種中高層住居専用地域"]}},
    {"input": "商業地域、準工業地域", "expected": {"values": ["商業地域", "準工業地域"]}},
    {"input": "準工業地域、第一種中高層住居専用地域", "expected": {"values": ["準工業地域", "第一種中高層住居専用地域"]}},
    {"input": "第一種中高層住居専用地域、第一種低層住居専用地域", "expected": {"values": ["第一種中高層住居専用地域", "第一種低層住居専用地域"]}},
    {"input": "都市計画区域外", "expected": {"values": ["都市計画区域外"]}}
]

TEST_CASES_DATE1 = [
    {"input": "2026年2月下旬予定", "expected": {"year": 2026, "month": 2, "period_text": "下旬", "estimated_date": "2026-02-25", "tentative": True, }},
    {"input": "2024年2月竣工済",     "expected": {"year": 2024, "month": 2, "estimated_date": "2024-02-01", "completed": True,  }},
    {"input": "2024年2月",         "expected": {"year": 2024, "month": 2, "estimated_date": "2024-02-01",               }},
    {"input": "2023年11月竣工済み","expected": {"year": 2023, "month": 11, "estimated_date": "2023-11-01", "completed": True,  }},
    {"input": "2024年3月完成済",   "expected": {"year": 2024, "month": 3, "estimated_date": "2024-03-01", "completed": True,  }},
    {"input": "2027年2月下旬予定", "expected": {"year": 2027, "month": 2, "period_text": "下旬", "estimated_date": "2027-02-25", "tentative": True, }},
    {"input": "即日",              "expected": {"immediate": True,             }},
    {"input": "未定",              "expected": {"is_undefined": True,          }},
    {"input": "2024年2月中旬",     "expected": {"year": 2024, "month": 2, "period_text": "中旬", "estimated_date": "2024-02-15",               }},
    {"input": "2025年3月28日予定","expected": {"year": 2025, "month": 3, "day": 28, "estimated_date": "2025-03-28", "tentative": True, }},
]

TEST_CASES_DATE2 = [
    {"input": "即引渡可", "expected": {"type": "immediate"}},
    {"input": "相談", "expected": {"type": "negotiable"}},
    {"input": "2025年3月予定", "expected": {"year": 2025, "month": 3, "is_planned": True, "estimated_date": "2025-03-01"}},
    {"input": "2025年1月", "expected": {"year": 2025, "month": 1, "estimated_date": "2025-01-01"}},
    {"input": "契約後1ヶ月", "expected": {"type": "after_contract", "months": 1.0}},
    {"input": "2025年2月下旬予定", "expected": {"year": 2025, "month": 2, "is_planned": True, "period_text": "下旬", "estimated_date": "2025-02-25"}},
    {"input": "2025年2月末予定", "expected": {"year": 2025, "month": 2, "is_planned": True, "period_text": "末", "estimated_date": "2025-02-28"}},
    {"input": "契約後6ヶ月", "expected": {"type": "after_contract", "months": 6.0}},
    {"input": "2025年9月12日予定", "expected": {"year": 2025, "month": 9, "day": 12, "estimated_date": "2025-09-12"}},
    {"input": "2028年4月下旬予定", "expected": {"year": 2028, "month": 4, "is_planned": True, "period_text": "下旬", "estimated_date": "2028-04-25"}}
]

TEST_CASES_PRICE = [
    {"input": "2980万円   [ □支払シミュレーション ]", "expected": {"unit": "万円", "value": 2980.0, }},
    {"input": "未定", "expected": {"value": None, "is_undefined": True, }},
    {"input": "1680万円   (土地のみの価格です)    [ □支払シミュレーション ]", "expected": {"unit": "万円", "value": 1680.0, "note": "土地のみの価格です", }},
    {"input": "3980万円〜5980万円 [ □支払シミュレーション ]", "expected": {"unit": "万円", "min": 3980.0, "max": 5980.0, "value": 4980.0}},
    {"input": "価格要相談 [ □支払シミュレーション ]", "expected": {"type": "negotiable", }},
    {"input": "2980万円（参考価格）       [ □支払シミュレーション ]", "expected": {'unit': '万円', 'value': 2980.0, 'note': '参考価格', 'tentative': True}},
    {"input": "4350万円(モデルルーム住戸につき家具家電付き)       [ □支払シミュレーション ]", "expected": {"unit": "万円", "value": 4350.0, "note": "モデルルーム住戸につき家具家電付き", }},
    {"input": "即入居可 2980万円  [ □支払シミュレーション ]", "expected": {"unit": "万円", "value": 2980.0, }},
    {"input": "2700万円(建物価格: 1800万円 、土地価格: 900万円)   [ □支払シミュレーション ]", "expected": {"unit": "万円", "value": 2700.0, "note": "建物価格: 1800万円 、土地価格: 900万円", }},
    {"input": "8980万円〜2億880万円       [ □支払シミュレーション ]", "expected": {"unit": "万円", "min": 8980.0, "max": 20880.0, "value": 14930.0}},
]

TEST_CASES_PRICE_BAND = [
    {"input": "-", "expected": {"value": None, }},
    {"input": "2400万円台（2戸）", "expected": {"unit": "万円", "values": [{"price": 2400.0, "count": 2}], "value": 2400.0, }},
    {"input": "2900万円台・3100万円台（各1戸）", "expected": {"unit": "万円", "values": [{"price": 2900.0, "count": 1}, {"price": 3100.0, "count": 1}], "value": 3000.0, }},
    {"input": "2600万円台・2900万円台（各2戸）", "expected": {"unit": "万円", "values": [{"price": 2600.0, "count": 2}, {"price": 2900.0, "count": 2}], "value": 2750.0, }},
    {"input": "3800万円台・3900万円台（各3戸）", "expected": {"unit": "万円", "values": [{"price": 3800.0, "count": 3}, {"price": 3900.0, "count": 3}], "value": 3850.0, }},
    {"input": "4600万円台・4700万円台（各2戸）", "expected": {"unit": "万円", "values": [{"price": 4600.0, "count": 2}, {"price": 4700.0, "count": 2}], "value": 4650.0, }},
    {"input": "3700万円台・3800万円台・3900万円台（各1戸）", "expected": {"unit": "万円", "values": [{"price": 3700.0, "count": 1}, {"price": 3800.0, "count": 1}, {"price": 3900.0, "count": 1}], "value": 3800.0, }},
    {"input": "1億円台（4戸）", "expected": {"unit": "万円", "values": [{"price": 10000.0, "count": 4}], "value": 10000.0, }},
    {"input": "2600万円台・2700万円台・2800万円台・2900万円台（各1戸）", "expected": {"unit": "万円", "values": [{"price": 2600.0, "count": 1}, {"price": 2700.0, "count": 1}, {"price": 2800.0, "count": 1}, {"price": 2900.0, "count": 1}], "value": 2750.0, }},
    {"input": "7300万円台（2戸）", "expected": {"unit": "万円", "values": [{"price": 7300.0, "count": 2}], "value": 7300.0, }}
]

TEST_CASES_MANAGEMENT_FEE = [
    {"input": "金額未定", "expected": {"is_undefined": True, "value": None}},
    {"input": "1万円／月（委託(通勤)）", "expected": {"management_type": "委託", "work_style": "通勤", "value": 10000, "unit": "円", "frequency": "月"}},
    {"input": "1万円／月（委託(巡回)）", "expected": {"management_type": "委託", "work_style": "巡回", "value": 10000, "unit": "円", "frequency": "月"}},
    {"input": "2万2500円／月（委託(通勤)）", "expected": {"management_type": "委託", "work_style": "通勤", "value": 22500, "unit": "円", "frequency": "月"}},
    {"input": "1万7744円／月（一部委託(管理員なし)）", "expected": {"management_type": "一部委託", "work_style": "管理員なし", "value": 17744, "unit": "円", "frequency": "月"}},
    {"input": "9300円～1万3800円／月", "expected": {"min": 9300, "max": 13800, "value": 11550.0, "unit": "円", "frequency": "月"}},
    {"input": "3020円／月（委託(巡回)）", "expected": {"management_type": "委託", "work_style": "巡回", "value": 3020, "unit": "円", "frequency": "月"}},
    {"input": "1万5000円／月（自主管理）", "expected": {"management_type": "自主", "value": 15000, "unit": "円", "frequency": "月"}},
    {"input": "8000円／月（委託(常駐)）", "expected": {"management_type": "委託", "work_style": "常駐", "value": 8000, "unit": "円", "frequency": "月"}},
    {"input": "1万2000円／月（委託(勤務形態未定)）", "expected": {"management_type": "委託", "work_style": "未定", "value": 12000, "unit": "円", "frequency": "月"}}
]

TEST_CASES_MANAGEMENT_PREP_FEE = [
    {"input": "-", "expected": {"value": None}},
    {"input": "金額未定", "expected": {"is_undefined": True, "value": None}},
    {"input": "2万5000円（一括払い）", "expected": {"value": 25000, "unit": "円", "frequency": "一括"}},
    {"input": "8000円～1万円（一括払い）", "expected": {"min": 8000, "max": 10000, "value": 9000.0, "unit": "円", "frequency": "一括"}},
    {"input": "3万2000円～4万3000円（一括払い）", "expected": {"min": 32000, "max": 43000, "value": 37500.0, "unit": "円", "frequency": "一括"}},
    {"input": "2万8240円～8万5140円（一括払い）", "expected": {"min": 28240, "max": 85140, "value": 56690.0, "unit": "円", "frequency": "一括"}},
    {"input": "5万9420円・7万5680円（一括払い）", "expected": {"min": 59420, "max": 75680, "value": 67550.0, "unit": "円", "frequency": "一括"}},
    {"input": "2770円～5620円（一括払い）（住宅一部管理準備金）、4380円～8880円（一括払い）（全体管理準備金）", "expected": {"note": "住宅一部管理準備金・全体管理準備金", "min": 2770, "max": 8880, "value": 5825.0, "unit": "円", "frequency": "一括"}},
    {"input": "3万円（一括払い）管理基金", "expected": {"value": 30000, "unit": "円", "frequency": "一括"}},
    {"input": "2万9300円～4万4600円（一括払い）（初年度のみ）", "expected": {"note": "初年度のみ", "min": 29300, "max": 44600, "value": 36950.0, "unit": "円", "frequency": "一括"}}
]

TEST_CASES_REPAIR_FUND = [
    {"input": "無", "expected": {"value": 0}},
    {"input": "金額未定", "expected": {"is_undefined": True, "value": None}},
    {"input": "1万円／月", "expected": {"value": 10000, "unit": "円", "frequency": "月"}},
    {"input": "8000円～1万2000円／月", "expected": {"min": 8000, "max": 12000, "value": 10000.0, "unit": "円", "frequency": "月"}},
    {"input": "5000円／月（契約時）、6カ月目より530円／月・㎡", "expected": {"note": "（契約時）、6カ月目より530円／月・㎡", "value": 5000, "unit": "円", "frequency": "月"}},
    {"input": "6100円～9150円／月（間取りにより異なる）", "expected": {"note": "間取りにより異なる", "min": 6100, "max": 9150, "value": 7625.0, "unit": "円", "frequency": "月"}},
    {"input": "9090円／月　※初回のみ4万5450円", "expected": {"note": "初回のみ4万5450円", "value": 9090, "unit": "円", "frequency": "月"}},
    {"input": "7200円／月（5年目より8640円／月）", "expected": {"note": "5年目より8640円／月", "value": 7200, "unit": "円", "frequency": "月"}},
    {"input": "当初月額1万1670円／月、段階増額方式", "expected": {"note": "段階増額方式", "value": 11670, "unit": "円", "frequency": "月"}},
    {"input": "1万5610円／月（1年目のみ6810円／月）", "expected": {"note": "1年目のみ6810円／月", "value": 15610, "unit": "円", "frequency": "月"}}
]

TEST_CASES_REPAIR_FUND_BASIC = [
    {"input": "-", "expected": {"value": None}},
    {"input": "金額未定", "expected": {"is_undefined": True, "value": None}},
    {"input": "38万7000円～60万1000円（一括払い）", "expected": {"min": 387000, "max": 601000, "value": 494000.0, "unit": "円", "frequency": "一括"}},
    {"input": "79万8000円～178万3000円（一括払い）", "expected": {"min": 798000, "max": 1783000, "value": 1290500.0, "unit": "円", "frequency": "一括"}},
    {"input": "41万8000円・44万4000円（一括払い）", "expected": {"min": 418000, "max": 444000, "value": 431000.0, "unit": "円", "frequency": "一括"}},
    {"input": "83万1950円（一括払い）", "expected": {"value": 831950, "unit": "円", "frequency": "一括"}},
    {"input": "64万7250円～68万7750円（一括払い）【内訳】〈全体共用〉33万6750円～35万7750円（引渡時一括払）　〈住宅一部供用〉31万500円～33万円（引渡時一括払）", "expected": {"breakdown": "〈全体共用〉33万6750円～35万7750円（引渡時一括払）　〈住宅一部供用〉31万500円～33万円（引渡時一括払）", "min": 647250, "max": 687750, "value": 667500.0, "unit": "円", "frequency": "一括"}},
    {"input": "36万円～98万円（一括払い）", "expected": {"min": 360000, "max": 980000, "value": 670000.0, "unit": "円", "frequency": "一括"}},
    {"input": "17万1180円～35万9640円（一括払い）", "expected": {"min": 171180, "max": 359640, "value": 265410.0, "unit": "円", "frequency": "一括"}},
    {"input": "91万円～105万円（一括払い）", "expected": {"min": 910000, "max": 1050000, "value": 980000.0, "unit": "円", "frequency": "一括"}}
]

TEST_CASES_OTHER_EXPENSES = [
    {"input": "-", "expected": {"value": None}},
    {"input": "災害積立金：300円／月、災害積立基金：1万円／一括", "expected": {"expenses": [{"name": "災害積立金", "category": "災害積立", "value": 300, "unit": "円", "frequency": "月"}, {"name": "災害積立基金", "category": "災害積立", "value": 10000, "unit": "円", "frequency": "一括"}]}},
    {"input": "インターネット使用料：990円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 990, "unit": "円", "frequency": "月"}]}},
    {"input": "インターネット使用料：金額未定", "expected": {"value": None}},
    {"input": "町会費：200円／月、ハイセクト（セキュリティ）使用料：1430円／月", "expected": {"expenses": [{"name": "町会費", "category": "自治会費", "value": 200, "unit": "円", "frequency": "月"}, {"name": "ハイセクト（セキュリティ）使用料", "category": "利用料", "value": 1430, "unit": "円", "frequency": "月"}]}},
    {"input": "インターネット定額料金：1760円／月、GMアソシエライフアップサービス料金：275円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 1760, "unit": "円", "frequency": "月"}, {"name": "GMアソシエライフアップサービス料金", "category": "サービス", "value": 275, "unit": "円", "frequency": "月"}]}},
    {"input": "前払地代：263万円～398万円／一括※販売価格に含む、敷金：12万8640円～19万4880円／一括、管理一時金：1万8370円～2万7820円／一括、専用利用料：2860円／月、当初地代：5360円～8120円／月", "expected": {"expenses": [{"name": "前払地代", "category": "地代", "min": 2630000, "max": 3980000, "value": 3305000.0, "unit": "円", "frequency": "一括"}, {"name": "敷金", "category": "敷金", "min": 128640, "max": 194880, "value": 161760.0, "unit": "円", "frequency": "一括"}, {"name": "管理一時金", "category": "管理費", "min": 18370, "max": 27820, "value": 23095.0, "unit": "円", "frequency": "一括"}, {"name": "専用利用料", "category": "利用料", "value": 2860, "unit": "円", "frequency": "月"}, {"name": "当初地代", "category": "地代", "min": 5360, "max": 8120, "value": 6740.0, "unit": "円", "frequency": "月"}]}},
    {"input": "インターネット使用料：660円／月、エンクレストガーデンクラブ会費：300円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 660, "unit": "円", "frequency": "月"}, {"name": "エンクレストガーデンクラブ会費", "category": "コミュニティ", "value": 300, "unit": "円", "frequency": "月"}]}},
    {"input": "インターネット定額料金：1650円／月、ＣＡＴＶ定額料金：330円／月、GMアソシエライフアップサービス料金：275円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 1650, "unit": "円", "frequency": "月"}, {"name": "CATV", "category": "通信費", "value": 330, "unit": "円", "frequency": "月"}, {"name": "GMアソシエライフアップサービス料金", "category": "サービス", "value": 275, "unit": "円", "frequency": "月"}]}},
    {"input": "保証金：19万9200円～30万4800円、月払賃料：8300円～1万2700円／月、解体準備金：5610円～8580円／月、解体準備基金：6万7320円～10万2960円／一括、インターネット使用料：880円／月、防犯センサー使用料(4・12階のみ)：500円／月", "expected": {"expenses": [{"name": "保証金", "category": "保証金", "min": 199200, "max": 304800, "value": 252000.0, "unit": "円", "frequency": "月"}, {"name": "解体準備金", "category": "解体", "min": 5610, "max": 8580, "value": 7095.0, "unit": "円", "frequency": "月"}, {"name": "解体準備基金", "category": "解体", "min": 67320, "max": 102960, "value": 85140.0, "unit": "円", "frequency": "一括"}, {"name": "インターネット", "category": "通信費", "value": 880, "unit": "円", "frequency": "月"}, {"name": "防犯センサー使用料(4・12階のみ)", "category": "利用料", "value": 500, "unit": "円", "frequency": "月"}]}},
    {"input": "自治会費：500円／月、インターネット利用料：950円／月、各戸宅配利用料：275円／月", "expected": {"expenses": [{"name": "自治会費", "category": "自治会費", "value": 500, "unit": "円", "frequency": "月"}, {"name": "インターネット", "category": "通信費", "value": 950, "unit": "円", "frequency": "月"}, {"name": "各戸宅配利用料", "category": "利用料", "value": 275, "unit": "円", "frequency": "月"}]}},
    {"input": "NET使用料(TVサービス利用料含む)：660円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 660, "unit": "円", "frequency": "月"}]}},
    {"input": "インターネット定額料金：1250円／月、環境整備一時金：1万2600円～1万6900円／一括、ゴミ収集費：1540円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 1250, "unit": "円", "frequency": "月"}]}},
    {"input": "地代：6110円～1万4590円／月、解体準備積立金：2910円～6960円／月、インターネット利用料：1386円／月", "expected": {"expenses": [{"name": "地代", "category": "地代", "min": 6110, "max": 14590, "value": 10350.0, "unit": "円", "frequency": "月"}, {"name": "解体準備積立金", "category": "解体", "min": 2910, "max": 6960, "value": 4935.0, "unit": "円", "frequency": "月"}, {"name": "インターネット", "category": "通信費", "value": 1386, "unit": "円", "frequency": "月"}]}},
    {"input": "CATV利用料：385円／月、インターネット利用料：1353円／月、給湯器リース料：2970円／月", "expected": {"expenses": [{"name": "CATV", "category": "通信費", "value": 385, "unit": "円", "frequency": "月"}, {"name": "インターネット", "category": "通信費", "value": 1353, "unit": "円", "frequency": "月"}]}},
    {"input": "インターネット使用料：825円／月　※利用開始時一時金1万9360円（一括払い）、NiSUMU利用料：990円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 825, "unit": "円", "frequency": "月"}, {"name": "NiSUMU利用料", "category": "利用料", "value": 990, "unit": "円", "frequency": "月"}]}},
    {"input": "テレビ共視聴設備利用料：550円／月、フレッツ光利用料（インターネット）：2090円／月※プロバイダー利用料込", "expected": {"expenses": [{"name": "テレビ", "category": "通信費", "value": 550, "unit": "円", "frequency": "月"}, {"name": "インターネット", "category": "通信費", "value": 2090, "unit": "円", "frequency": "月"}]}},
    {"input": "専用駐車場：1万円／月、インターネット使用料：550円／月", "expected": {"expenses": [{"name": "専用駐車場", "category": "駐車場", "value": 10000, "unit": "円", "frequency": "月"}, {"name": "インターネット", "category": "通信費", "value": 550, "unit": "円", "frequency": "月"}]}},
    {"input": "町会費：2000円／年※町会の入会は任意となります。", "expected": {"expenses": [{"name": "町会費", "category": "自治会費", "value": 2000, "unit": "円", "frequency": "年"}]}},
    {"input": "インターネット定額料金：1243円／月、ＣＡＴＶ定額料金：1100円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 1243, "unit": "円", "frequency": "月"}, {"name": "CATV", "category": "通信費", "value": 1100, "unit": "円", "frequency": "月"}]}},
    {"input": "前払地代：263万円～398万円／一括※販売価格に含む、敷金：12万8640円～19万4880円／一括、管理一時金：1万8370円～2万7820円／一括、専用利用料：2860円／月、当初地代：5360円～8120円／月", "expected": {"expenses": [{"name": "前払地代", "category": "地代", "min": 2630000, "max": 3980000, "value": 3305000.0, "unit": "円", "frequency": "一括"}, {"name": "敷金", "category": "敷金", "min": 128640, "max": 194880, "value": 161760.0, "unit": "円", "frequency": "一括"}, {"name": "管理一時金", "category": "管理費", "min": 18370, "max": 27820, "value": 23095.0, "unit": "円", "frequency": "一括"}, {"name": "専用利用料", "category": "利用料", "value": 2860, "unit": "円", "frequency": "月"}, {"name": "当初地代", "category": "地代", "min": 5360, "max": 8120, "value": 6740.0, "unit": "円", "frequency": "月"}]}},
    {"input": "インターネット使用料：825円／月　※利用開始時一時金1万9360円（一括払い）、NiSUMU利用料：990円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 825, "unit": "円", "frequency": "月"}, {"name": "NiSUMU利用料", "category": "利用料", "value": 990, "unit": "円", "frequency": "月"}]}}
]

TEST_CASES_LAYOUT = [
    {"input": "3LDK", "expected": {"values": ["3LDK"]}},
    {"input": "ワンルーム", "expected": {"value": "1R"}},
    {"input": "3LDK・4LDK", "expected": {"values": ["3LDK", "4LDK"]}},
    {"input": "2LDK+S（納戸）", "expected": {"values": ["2LDK+S"]}},
    {"input": "3LDK～4LDK", "expected": {"values": ["3LDK", "4LDK"]}},
    {"input": "3LDK～5LDK", "expected": {"values": ["3LDK", "4LDK", "5LDK"]}},
    {"input": "2LDK+2S（納戸）～3LDK+S（納戸）", "expected": {"values": ["2LDK+2S", "3LDK+S"]}},
    {"input": "3LDK：＋ロフト", "expected": {"values": ["3LDK"]}},
    {"input": "4LDK選べる3タイプの間取り3LDK～4LDK", "expected": {"values": ["4LDK"]}},
    {"input": "4LDK：全棟／＋パントリー　3・5号棟／＋SIC　4号棟／＋WIC、ワークスペース", "expected": {"values": ["4LDK"]}},
]

TEST_CASES_AREAS = [
    {"input": "-", "expected": {"areas": []}},
    {"input": "バルコニー面積：9.45m2", "expected": {"areas": [{"type": "バルコニー面積", "value": 9.45, "unit": "m^2", "tsubo": 2.86}]}},
    {"input": "バルコニー面積：1m2", "expected": {"areas": [{"type": "バルコニー面積", "value": 1.0, "unit": "m^2", "tsubo": 0.3}]}},
    {"input": "バルコニー面積：28.07m2", "expected": {"areas": [{"type": "バルコニー面積", "value": 28.07, "unit": "m^2", "tsubo": 8.49}]}},
    {"input": "テラス面積：15.4m2", "expected": {"areas": [{"type": "テラス面積", "value": 15.4, "unit": "m^2", "tsubo": 4.66}]}},
    {"input": "ルーフバルコニー面積：25.83m2", "expected": {"areas": [{"type": "ルーフバルコニー面積", "value": 25.83, "unit": "m^2", "tsubo": 7.81}]}},
    {"input": "専用庭面積：45.6m2", "expected": {"areas": [{"type": "専用庭面積", "value": 45.6, "unit": "m^2", "tsubo": 13.79}]}},
    {"input": "サービスバルコニー面積：3.8m2", "expected": {"areas": [{"type": "サービスバルコニー面積", "value": 3.8, "unit": "m^2", "tsubo": 1.15}]}},
    {"input": "バルコニー面積：6.75m2　テラス面積：12.5m2", "expected": {"areas": [{"type": "バルコニー面積", "value": 6.75, "unit": "m^2", "tsubo": 2.04}, {"type": "テラス面積", "value": 12.5, "unit": "m^2", "tsubo": 3.78}]}},
    {"input": "サービスバルコニー面積：3.8m2　バルコニー面積：8.4m2", "expected": {"areas": [{"type": "サービスバルコニー面積", "value": 3.8, "unit": "m^2", "tsubo": 1.15}, {"type": "バルコニー面積", "value": 8.4, "unit": "m^2", "tsubo": 2.54}]}},
    {"input": "専用使用料対象面積：18.7m2（2000円／月）", "expected": {"areas": [{"type": "専用使用料対象面積", "value": 18.7, "unit": "m^2", "tsubo": 5.66, "monthly_fee": 2000}]}},
    {"input": "トランクルーム面積：2.4m2（利用料：月額1500円）", "expected": {"areas": [{"type": "トランクルーム面積", "value": 2.4, "unit": "m^2", "tsubo": 0.73, "monthly_fee": 1500}]}},
    {"input": "アルコーブ面積：4.2m2", "expected": {"areas": [{"type": "アルコーブ面積", "value": 4.2, "unit": "m^2", "tsubo": 1.27}]}},
    {"input": "ウォークインクローゼット面積：6.8m2", "expected": {"areas": [{"type": "ウォークインクローゼット面積", "value": 6.8, "unit": "m^2", "tsubo": 2.06}]}},
    {"input": "共用庭利用権面積：35.2m2（共用）", "expected": {"areas": [{"type": "共用庭利用権面積", "value": 35.2, "unit": "m^2", "tsubo": 10.65, "measurement_type": "共用"}]}},
    {"input": "バルコニー面積：7.2m2　サービスバルコニー面積：2.8m2　テラス面積：9.6m2", "expected": {"areas": [{"type": "バルコニー面積", "value": 7.2, "unit": "m^2", "tsubo": 2.18}, {"type": "サービスバルコニー面積", "value": 2.8, "unit": "m^2", "tsubo": 0.85}, {"type": "テラス面積", "value": 9.6, "unit": "m^2", "tsubo": 2.9}]}},
    {"input": "ルーフテラス面積：42.3m2（使用料：月額3000円）", "expected": {"areas": [{"type": "ルーフテラス面積", "value": 42.3, "unit": "m^2", "tsubo": 12.8, "monthly_fee": 3000}]}},
    {"input": "専用ポーチ面積：8.9m2", "expected": {"areas": [{"type": "専用ポーチ面積", "value": 8.9, "unit": "m^2", "tsubo": 2.69}]}},
    {"input": "納戸面積：5.6m2　ウォークインクローゼット面積：4.3m2", "expected": {"areas": [{"type": "納戸面積", "value": 5.6, "unit": "m^2", "tsubo": 1.69}, {"type": "ウォークインクローゼット面積", "value": 4.3, "unit": "m^2", "tsubo": 1.3}]}},
    {"input": "スタディコーナー面積：3.1m2", "expected": {"areas": [{"type": "スタディコーナー面積", "value": 3.1, "unit": "m^2", "tsubo": 0.94}]}},
    {"input": "バルコニー面積：6.1m2～6.6m2、テラス：6.3m2～6.6m2（使用料未定）、ガーデンテラス面積：5.6m2～6.6m2（使用料未定）", "expected": {"areas":[{"type":"バルコニー面積","value":6.1,"unit":"m^2","tsubo":1.85},{"type":"テラス","value":6.3,"unit":"m^2","tsubo":1.91},{"type":"ガーデンテラス面積","value":5.6,"unit":"m^2","tsubo":1.69,}]}}
]

TEST_CASES_RESTRICTIONS = [
    {"input": "-", "expected": {"restrictions": []}},
    {"input": "準防火地域", "expected": {"restrictions": ["準防火地域"]}},
    {"input": "準防火地域、第3種高度地区", "expected": {"restrictions": ["準防火地域", "第3種高度地区"]}},
    {"input": "防火地域、準防火地域", "expected": {"restrictions": ["防火地域", "準防火地域"]}},
    {"input": "準防火地域、都市計画区域内、市街化区域、第2種高度地区", "expected": {"restrictions": ["準防火地域", "都市計画区域内", "市街化区域", "第2種高度地区"]}},
    {"input": "防火地域、小川駅西口地区地区計画（駅前商業地区）、高度利用地区（小川駅西口地区）、小川駅西口地区市街地再開発事業", "expected": {"restrictions": ["防火地域", "小川駅西口地区地区計画（駅前商業地区）", "高度利用地区（小川駅西口地区）", "小川駅西口地区市街地再開発事業"]}},
    {"input": "東側道路境界線から11m以内：防火地域、東側道路境界線から11mを超える部分：準防火地域", "expected": {"restrictions": ["東側道路境界線から11m以内：防火地域", "東側道路境界線から11mを超える部分：準防火地域"]}},
    {"input": "準防火地域、日影規制4h-2.5h/4.0m、20m高度地区", "expected": {"restrictions": ["準防火地域", "日影規制4h-2.5h/4.0m", "20m高度地区"]}},
    {"input": "都市計画区域内・市街化区域・宅地造成工事規制区域・地区計画（武岡ピュアタウン地区）・法22条地域・土砂災害警戒区域・土砂災害特別警戒区域", "expected": {"restrictions": ["都市計画区域内", "市街化区域", "宅地造成工事規制区域", "地区計画（武岡ピュアタウン地区）", "法22条地域", "土砂災害警戒区域", "土砂災害特別警戒区域"]}},
    {"input": "準防火地域、絶対高45m高度地区、緑化地域、都市機能誘導区域内、駐車場整備地区、居住誘導区域内", "expected": {"restrictions": ["準防火地域", "絶対高45m高度地区", "緑化地域", "都市機能誘導区域内", "駐車場整備地区", "居住誘導区域内"]}}
]

TEST_CASES_DATE_EXACT = [
    {"input": "-", "expected": {"date": None}},
    {"input": "2025年12月31日", "expected": {"date": "2025-12-31"}},
    {"input": "2025年2月28日", "expected": {"date": "2025-02-28"}},
    {"input": "2025年3月31日", "expected": {"date": "2025-03-31"}},
    {"input": "2025年4月30日", "expected": {"date": "2025-04-30"}},
    {"input": "2026年12月31日", "expected": {"date": "2026-12-31"}},
    {"input": "2033年8月31日", "expected": {"date": "2033-08-31"}},
    {"input": "2025/02/28", "expected": {"date": "2025-02-28"}},
    {"input": "2026年1月1日", "expected": {"date": "2026-01-01"}},
    {"input": "2029年3月1日", "expected": {"date": "2029-03-01"}}
]

TEST_CASES_PRICE_MISC = [
    {"input": "未定", "expected": {"value": None, 'is_undefined': True}},
    {"input": "未定※権利金含む", "expected": {"value": None, 'is_undefined': True}},
    {"input": "未定（※一括前払地代含む）", "expected": {"value": None, 'is_undefined': True}},
    {"input": "3989万5000円～4978万7000円", "expected": {'unit': '万円', 'min': 3989.5, 'max': 4978.7, 'value': 4484.1}},
    {"input": "6540万円・6990万円", "expected": {'unit': '万円', 'min': 6540.0, 'max': 6990.0, 'value': 6765.0}},
    {"input": "4430万円～1億1340万円", "expected": {'unit': '万円', 'min': 4430.0, 'max': 11340.0, 'value': 7885.0}},
    {"input": "2580万円～9800万円", "expected": {'unit': '万円', 'min': 2580.0, 'max': 9800.0, 'value': 6190.0}},
    {"input": "未定（※前払い地代含む）", "expected": {"value": None, 'is_undefined': True}},
    {"input": "未定（うちモデルルーム販売あり：使用期間2025年4月4日～引き渡しまで）", "expected": {"value": None, 'is_undefined': True}},
    {"input": "3998万円～8998万円", "expected": {'unit': '万円', 'min': 3998.0, 'max': 8998.0, 'value': 6498.0}}
]

TEST_CASES_PRICE_BAND_EXTRA = [
    {"input": "未定", "expected": {"value": None}},
    {"input": "-", "expected": {"value": None}},
    {"input": "3900万円台", "expected": {'unit': '万円', 'values': [{'price': 3900.0, 'count': 1}], 'value': 3900.0}},
    {"input": "4300万円台（5戸）", "expected": {'unit': '万円', 'values': [{'price': 4300.0, 'count': 5}], 'value': 4300.0}},
    {"input": "6400万円台・6700万円台・6900万円台（各1戸）", "expected": {'unit': '万円', 'values': [{'price': 6400.0, 'count': 1}, {'price': 6700.0, 'count': 1}, {'price': 6900.0, 'count': 1}], 'value': 6666.666666666667}},
    {"input": "4200万円台・4400万円台・4900万円台（各8戸）", "expected": {'unit': '万円', 'values': [{'price': 4200.0, 'count': 8}, {'price': 4400.0, 'count': 8}, {'price': 4900.0, 'count': 8}], 'value': 4500.0}},
    {"input": "3800万円台・4000万円台・4100万円台・4600万円台・4800万円台・6400万円台（各4戸）", "expected": {'unit': '万円', 'values': [{'price': 3800.0, 'count': 4}, {'price': 4000.0, 'count': 4}, {'price': 4100.0, 'count': 4}, {'price': 4600.0, 'count': 4}, {'price': 4800.0, 'count': 4}, {'price': 6400.0, 'count': 4}], 'value': 4616.666666666667}},
    {"input": "1億1000万円台※1000万円単位", "expected": {"unit": "万円", "values": [{"price": 11000.0, "count": 1}], "value": 11000.0}},
    {"input": "5000万円台（9戸）※1000万円単位", "expected": {"unit": "万円", "values": [{"price": 5000.0, "count": 9}], "value": 5000.0}},
    {"input": "4600万円台・4900万円台", "expected": {'unit': '万円', 'values': [{'price': 4600.0, 'count': None}, {'price': 4900.0, 'count': None}], 'value': 4750.0}}
]

TEST_CASES_PRICE_BAND2 = [
    {"input": "2700万円台～4400万円台", "expected": {"unit": "万円", "values": [{"price": 2700.0, "count": None}, {"price": 4400.0, "count": None}], "value": 3550.0, }},
    {"input": "3700万円台～8400万円台", "expected": {"unit": "万円", "values": [{"price": 3700.0, "count": None}, {"price": 8400.0, "count": None}], "value": 6050.0, }},
    {"input": "2900万円台・3200万円台", "expected": {"unit": "万円", "values": [{"price": 2900.0, "count": None}, {"price": 3200.0, "count": None}], "value": 3050.0, }},
    {"input": "3900万円台", "expected": {"unit": "万円", "values": [{"price": 3900.0, "count": 1}], "value": 3900.0, }},
    {"input": "8300万円台・9500万円台", "expected": {"unit": "万円", "values": [{"price": 8300.0, "count": None}, {"price": 9500.0, "count": None}], "value": 8900.0, }},
    {"input": "5800万円台～9900万円台", "expected": {"unit": "万円", "values": [{"price": 5800.0, "count": None}, {"price": 9900.0, "count": None}], "value": 7850.0, }},
    {"input": "2400万円台～6300万円台", "expected": {"unit": "万円", "values": [{"price": 2400.0, "count": None}, {"price": 6300.0, "count": None}], "value": 4350.0, }},
    {"input": "2900万円台～4500万円台（うちモデルルーム価格4476万円、予定）", "expected": {"unit": "万円", "values": [{"price": 2900.0, "count": None}, {"price": 4500.0, "count": None}], "value": 3700.0, }},
    {"input": "3900万円台～8300万円台（※100万円単位）", "expected": {"unit": "万円", "values": [{"price": 3900.0, "count": None}, {"price": 8300.0, "count": None}], "value": 6100.0, }},
    {"input": "8900万円台～1億2900万円台", "expected": {"unit": "万円", "values": [{"price": 8900.0, "count": None}, {"price": 12900.0, "count": None}], "value": 10900, }},
]

TEST_CASES_REPAIR_FUND_BASIC2 = [
    {"input": "金額未定", "expected": {"is_undefined": True, "value": None, }},
    {"input": "106万5000円～132万3000円（一括払い）", "expected": {"min": 1065000, "max": 1323000, "value": 1194000.0, "unit": "円", "frequency": "一括", }},
    {"input": "23万100円～33万6600円（一括払い）、修繕積立基金(住宅)：16万4400円～24万400円（一括払い）", "expected": {"min": 230100, "max": 336600, "value": 283350.0, "unit": "円", "frequency": "一括", "note": "修繕積立基金(住宅)：16万4400円～24万400円（一括払い）"}},
    {"input": "57万5400円・60万3000円（一括払い）", "expected": {"min": 575400, "max": 603000, "value": 589200.0, "unit": "円", "frequency": "一括", }},
    {"input": "75万5000円（一括払い）、全体修繕積立基金：80万6000円（一括払い）", "expected": {"value": 755000, "unit": "円", "frequency": "一括", "note": "全体修繕積立基金：80万6000円（一括払い）"}},
    {"input": "36万600円～207万7800円（一括払い）", "expected": {"min": 360600, "max": 2077800, "value": 1219200.0, "unit": "円", "frequency": "一括", }},
    {"input": "78万9840円・81万690円（一括払い）", "expected": {"min": 789840, "max": 810690, "value": 800265.0, "unit": "円", "frequency": "一括", }},
    {"input": "24万6000円～113万8500円（一括払い）", "expected": {"min": 246000, "max": 1138500, "value": 692250.0, "unit": "円", "frequency": "一括", }},
    {"input": "金額未定、金額未定 （団地修繕積立一時金）", "expected": {"is_undefined": True, "value": None, "note": "金額未定 （団地修繕積立一時金）"}},
    {"input": "75万5000円・87万6000円（一括払い）、全体修繕積立基金：80万6000円・93万5000円（一括払い）", "expected": {"min": 755000, "max": 876000, "value": 815500.0, "unit": "円", "frequency": "一括", "note": "全体修繕積立基金：80万6000円・93万5000円（一括払い）"}},
]

TEST_CASES_OTHER_EXPENSES2 = [
    {"input": "-", "expected": {"value": None, }},
    {"input": "災害積立金：300円／月、災害積立基金：1万円／一括", "expected": {"expenses": [{"name": "災害積立金", "category": "災害積立", "value": 300, "unit": "円", "frequency": "月"}, {"name": "災害積立基金", "category": "災害積立", "value": 10000, "unit": "円", "frequency": "一括"}], }},
    {"input": "インターネット接続サービス利用料：1375円／月、ロイヤルサロン使用料：650円～2110円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 1375, "unit": "円", "frequency": "月"}, {"name": "ロイヤルサロン使用料", "category": "利用料", "min": 650, "max": 2110, "value": 1380.0, "unit": "円", "frequency": "月"}], }},
    {"input": "インターネット定額料金：990円／月、給湯器リース料：2200円／月、CATV利用料金：385円／月", "expected": {"expenses": [{"name": "インターネット", "category": "通信費", "value": 990, "unit": "円", "frequency": "月"}, {"name": "CATV", "category": "通信費", "value": 385, "unit": "円", "frequency": "月"}], }},
    {"input": "管理一時金：1万6700円・2万2360円／一括、専用利用料：3080円／月(ホームセキュリティ費用、インターネットサービス利用料、プロバイダサービス料、マンションポータルサイト利用料含む)、コミュニティクラブ費：300円／月", "expected": {"expenses": [{"name": "管理一時金", "category": "管理費", "value": 16700, "unit": "円", "frequency": "月"}, {"name": "専用利用料", "category": "利用料", "value": 3080, "unit": "円", "frequency": "月"}, {"name": "コミュニティクラブ費", "category": "コミュニティ", "value": 300, "unit": "円", "frequency": "月"}], }},
    {"input": "地代：6083円／月、地代準備金：14万5992円（一括払い）、町内会費：200円／月、インターネット定額料金：1925円／月", "expected": {"expenses": [{"name": "地代", "category": "地代", "value": 6083, "unit": "円", "frequency": "月"}, {"name": "町内会費", "category": "自治会費", "value": 200, "unit": "円", "frequency": "月"}, {"name": "インターネット", "category": "通信費", "value": 1925, "unit": "円", "frequency": "月"}], }},
    {"input": "地代：6083円～7536円／月、地代準備金：14万5992円～18万864円（一括払い）", "expected": {"expenses": [{"name": "地代", "category": "地代", "min": 6083, "max": 7536, "value": 6809.5, "unit": "円", "frequency": "月"}], }},
    {"input": "保証金：21万8400円～32万6400円、月払賃料：9100円～1万3600円／月、借地返還対応準備金：6090円～9130円／月、インターネット使用料：770円／月", "expected": {"expenses": [{"name": "保証金", "category": "保証金", "min": 218400, "max": 326400, "value": 272400.0, "unit": "円", "frequency": "月"}, {"name": "インターネット", "category": "通信費", "value": 770, "unit": "円", "frequency": "月"}], }},
    {"input": "解体準備金：3300円／月、支払地代：1万614円／月、解体準備一時金：11万8800円／一括、地代保証金：25万4736円／一括、インターネット使用料：2189円／月", "expected": {"expenses": [{"name": "解体準備金", "category": "解体", "value": 3300, "unit": "円", "frequency": "月"}, {"name": "支払地代", "category": "地代", "value": 10614, "unit": "円", "frequency": "月"}, {"name": "解体準備一時金", "category": "解体", "value": 118800, "unit": "円", "frequency": "一括"}, {"name": "地代保証金", "category": "保証金", "value": 254736, "unit": "円", "frequency": "一括"}, {"name": "インターネット", "category": "通信費", "value": 2189, "unit": "円", "frequency": "月"}], }},
    {"input": "インターネット使用料：金額未定", "expected": {"value": None, }},
]

TEST_CASES_LAYOUT2 = [
    {"input": "3LDK", "expected": {"values": ["3LDK"], }},
    {"input": "2LDK・3LDK", "expected": {"values": ["2LDK", "3LDK"], }},
    {"input": "1LDK～3LDK", "expected": {"values": ["1LDK", "2LDK", "3LDK"], }},
    {"input": "2LDK+S（納戸）・3LDK", "expected": {"values": ["2LDK+S", "3LDK"], }},
    {"input": "1R～3LDK", "expected": {"values": ["1R", "1LDK", "2LDK", "3LDK"], }},
    {"input": "2LDK+S（納戸）～3LDK(2LDK+1S(サービスルーム(N))～3LDK)", "expected": {"values": ['2LDK+S', '2LDK+1S', '3LDK'], }},
    {"input": "2LDK・3LDK(2LDK+S(シューズインクローク)・3LDK+F(ファミリークロゼット))", "expected": {"values": ["2LDK", "3LDK", "3LDK+F"], }},
    {"input": "1LDK～4LDK(1LDK・2LDK・2LDK+S(納戸)・3LDK・3LDK+S(納戸)・4LDK)", "expected": {"values": ['1LDK', '2LDK', '2LDK+S', '3LDK', '3LDK+S', '4LDK'], }},
    {"input": "1LDK～3LDK+S（納戸）(1LDK・2LDK・3LDK・3LDK+S(納戸))", "expected": {"values": ["1LDK", "2LDK", "3LDK", "3LDK+S"], }},
    {"input": "2LDK～3LDK (2LDK～3LDK+WIC+SIC)", "expected": {"values": ["2LDK", "3LDK"], }},
]

TEST_CASES_AREA = [
    {"input": "56.64m2～79.2m2", "expected": {"unit": "m^2", "min": 56.64, "max": 79.2, "value": 67.92, "tsubo": 20.55, "min_tsubo": 17.13, "max_tsubo": 23.96, }},
    {"input": "56.7m2・59.43m2", "expected": {"unit": "m^2", "value": 56.7, "tsubo": 17.15, }},
    {"input": "63.83m2～104.42m2、 (全戸にトランクルーム面積0.22m2～0.42m2を含む)", "expected": {"unit": "m^2", "min": 0.42, "max": 104.42, "value": 52.42, "tsubo": 15.86, "min_tsubo": 0.13, "max_tsubo": 31.59, }},
    {"input": "64.06m2～80.32m2、（トランクルーム面積0.26m2含む）", "expected": {"unit": "m^2", "min": 64.06, "max": 80.32, "value": 72.19, "tsubo": 21.84, "min_tsubo": 19.38, "max_tsubo": 24.3, }},
    {"input": "73.99m2、(専用トランクルーム面積含む)", "expected": {"unit": "m^2", "value": 73.99, "tsubo": 22.38, }},
    {"input": "58.75m2～77.04m2、（防災備蓄倉庫面積 0.81m2・1.80m2含む）", "expected": {"unit": "m^2", "min": 58.75, "max": 77.04, "value": 67.895, "tsubo": 20.54, "min_tsubo": 17.77, "max_tsubo": 23.3, }},
    {"input": "69.79m2・73.99m2、(専用トランクルーム面積0.27m2・0.45m2含む)", "expected": {"unit": "m^2", "value": 69.79, "tsubo": 21.11, }},
    {"input": "31.84m2～141.66m2、(トランクルーム面積0.97m2～2.11m2含む)", "expected": {"unit": "m^2", "min": 2.11, "max": 141.66, "value": 71.885, "tsubo": 21.75, "min_tsubo": 0.64, "max_tsubo": 42.85, }},
    {"input": "42.88m2～208.17m2", "expected": {"unit": "m^2", "min": 42.88, "max": 208.17, "value": 125.525, "tsubo": 37.97, "min_tsubo": 12.97, "max_tsubo": 62.97, }},
    {"input": "75m2～78.57m2、(トランクルーム面積含む)", "expected": {"unit": "m^2", "min": 75.0, "max": 78.57, "value": 76.785, "tsubo": 23.23, "min_tsubo": 22.69, "max_tsubo": 23.77, }},
]

TEST_CASES_DATE_EXACT2 = [
    {"input": "-", "expected": {"date": None, }},
    {"input": "2024/03/31", "expected": {"date": "2024-03-31", }},
    {"input": "2024/06/30", "expected": {"date": "2024-06-30", }},
    {"input": "2024/02/29", "expected": {"date": "2024-02-29", }},
    {"input": "2025/02/28", "expected": {"date": "2025-02-28", }},
    {"input": "2024/12/15", "expected": {"date": "2024-12-15", }},
    {"input": "2024/03/01", "expected": {"date": "2024-03-01", }},
    {"input": "2024/12/31", "expected": {"date": "2024-12-31", }},
    {"input": "2025/09/27", "expected": {"date": "2025-09-27", }},
    {"input": "2025/04/29", "expected": {"date": "2025-04-29", }},
]

TEST_CASES_DELIVERY_DATE = [
    {"input": "即引渡可", "expected": {"type": "immediate", }},
    {"input": "即引渡可※諸手続き完了後", "expected": {"type": "immediate", "note": "諸手続き完了後", }},
    {"input": "2025年3月下旬予定", "expected": {"year": 2025, "month": 3, "is_planned": True, "period_text": "下旬", "estimated_date": "2025-03-25", }},
    {"input": "2025年6月中旬予定", "expected": {"year": 2025, "month": 6, "is_planned": True, "period_text": "中旬", "estimated_date": "2025-06-15", }},
    {"input": "2025年8月上旬予定", "expected": {"year": 2025, "month": 8, "is_planned": True, "period_text": "上旬", "estimated_date": "2025-08-05", }},
    {"input": "2025年4月予定", "expected": {"year": 2025, "month": 4, "is_planned": True, "estimated_date": "2025-04-01", }},
    {"input": "2025年9月末予定", "expected": {"year": 2025, "month": 9, "is_planned": True, "period_text": "末", "estimated_date": "2025-09-30", }},
    {"input": "即引渡可※諸手続後（第1街区）、2025年3月下旬予定（第2街区）", "expected": {"type": "immediate", "note": "諸手続き完了後", }},
    {"input": "2025年4月29日予定※完売時期によっては変更となる場合がございます。", "expected": {"year": 2025, "month": 4, "day": 29, "estimated_date": "2025-04-29", }},
    {"input": "2026年4月中旬予定 ※2025年1月以降にご契約の方の引渡は、2026年3月上旬(予定)から変更となります。", "expected": {"year": 2026, "month": 4, "is_planned": True, "period_text": "上旬", "estimated_date": "2026-04-05", }},
]

TEST_CASES_FLOOR = [
    {"input": "-", "expected": {"value": None, }},
    {"input": "1階", "expected": {"value": 1, "unit": "階", }},
    {"input": "2階", "expected": {"value": 2, "unit": "階", }},
    {"input": "3階", "expected": {"value": 3, "unit": "階", }},
    {"input": "5階", "expected": {"value": 5, "unit": "階", }},
    {"input": "6階", "expected": {"value": 6, "unit": "階", }},
    {"input": "7階", "expected": {"value": 7, "unit": "階", }},
    {"input": "8階", "expected": {"value": 8, "unit": "階", }},
    {"input": "10階", "expected": {"value": 10, "unit": "階", }},
    {"input": "13階", "expected": {"value": 13, "unit": "階", }},
]

TEST_CASES_DIRECTION = [
    {"input": "-", "expected": {"value": None, }},
    {"input": "南", "expected": {"value": "南", }},
    {"input": "東", "expected": {"value": "東", }},
    {"input": "西", "expected": {"value": "西", }},
    {"input": "北", "expected": {"value": "北", }},
    {"input": "南東", "expected": {"value": "南東", }},
    {"input": "南西", "expected": {"value": "南西", }},
    {"input": "北東", "expected": {"value": "北東", }},
    {"input": "北西", "expected": {"value": "北西", }},
    {"input": "南北", "expected": {"value": "南北", }},
]


TEST_CASES_FEATURE_PICKUP = [
    {"input": "エレベーター", "expected": {"feature_tags": ["elevator"], "structured_features": {"equipment": {"utilities": ["elevator"]}}, "raw_features": ["エレベーター"], "feature_count": 1}},
    {"input": "土地50坪以上", "expected": {"feature_tags": ["land_50tsubo_plus"], "structured_features": {"equipment": {}, "land_features": {"area_tsubo": {"min": 50}}}, "raw_features": ["土地50坪以上"], "feature_count": 1}},
    {"input": "スーパー 徒歩10分以内      /       小学校 徒歩10分以内     /       エレベーター", "expected": {"feature_tags": ["supermarket_walk_10min", "school_walk_10min", "elevator"], "structured_features": {"equipment": {"utilities": ["elevator"]}, "location_access": {"supermarket_walk_min": {"max": 10}, "elementary_school_walk_min": {"max": 10}}}, "raw_features": ["スーパー 徒歩10分以内", "小学校 徒歩10分以内", "エレベーター"], "feature_count": 3}},
    {"input": "角住戸     /       エレベーター", "expected": {"feature_tags": ["corner_unit", "elevator"], "structured_features": {"equipment": {"utilities": ["elevator"]}, "room_features": {"corner_unit": True}}, "raw_features": ["角住戸", "エレベーター"], "feature_count": 2}},
    {"input": "セキュリティ充実   /       エレベーター", "expected": {"feature_tags": ["security_enhanced", "elevator"], "structured_features": {"equipment": {"utilities": ["elevator"], "security": ["enhanced"]}}, "raw_features": ["セキュリティ充実", "エレベーター"], "feature_count": 2}},
    {"input": "土地50坪以上       /       スーパー 徒歩10分以内   /       システムキッチン        /       全居室収納      /       ＬＤＫ１５畳以上        /  整形地  /       対面式キッチン  /       ２階建", "expected": {"feature_tags": ["land_50tsubo_plus", "supermarket_walk_10min", "system_kitchen", "all_rooms_storage", "ldk_15tatami_plus", "regular_shape", "counter_kitchen", "2_story"], "structured_features": {"building_specs": {"ldk_size_tatami": {"min": 15}, "stories": 2}, "equipment": {"kitchen": ["system", "counter_facing"]}, "location_access": {"supermarket_walk_min": {"max": 10}}, "land_features": {"area_tsubo": {"min": 50}, "regular_shape": True}, "room_features": {"all_rooms_storage": True}}, "raw_features": ["土地50坪以上", "スーパー 徒歩10分以内", "システムキッチン", "全居室収納", "ＬＤＫ１５畳以上", "整形地", "対面式キッチン", "２階建"], "feature_count": 8}},
    {"input": "長期優良住宅認定通知書       /       建設住宅性能評価書（新築時）    /       フラット３５・S適合証明書       /       省エネルギー対策        /       駐車２台可  /       ＬＤＫ２０畳以上        /       省エネ給湯器    /       スーパー 徒歩10分以内  /       システムキッチン        /       浴室乾燥機      /       陽当り良好      /       全居室収納      /       閑静な住宅地    /       前道６ｍ以上        /       和室    /       シャワー付洗面化粧台    /       対面式キッチン  /       トイレ２ヶ所    /       浴室１坪以上        /       ２階建  /       東南向き        /       複層ガラス      /       オートバス      /       温水洗浄便座    /       床下収納        /       浴室に窓        /       吹抜け  /       ＴＶモニタ付インターホン        /       通風良好        /       ウォークインクローゼット        /       シューズインクローク        /       平坦地  /       食器洗乾燥機    /       整備された歩道  /       浄水器", "expected": {"feature_tags": ["long_term_excellent", "construction_performance_cert", "flat35_s", "energy_saving", "parking_2cars", "ldk_20tatami_plus", "energy_saving_heater", "supermarket_walk_10min", "system_kitchen", "bathroom_dryer", "good_sunlight", "all_rooms_storage", "quiet_area", "road_6m_plus", "japanese_room", "シャワー付洗面化粧台", "counter_kitchen", "2_toilets", "bathroom_1tsubo_plus", "2_story", "south_facing", "double_glazing", "auto_bath", "温水洗浄便座", "床下収納", "bathroom_window", "吹抜け", "tv_intercom", "通風良好", "walk_in_closet", "シューズインクローク", "flat_land", "dishwasher", "整備された歩道", "water_purifier"], "structured_features": {"certifications": {"long_term_excellent_housing": True, "construction_performance_evaluation": True, "flat35_s": True}, "building_specs": {"ldk_size_tatami": {"min": 20}, "good_sunlight": True, "bathroom_size_tsubo": {"min": 1}, "stories": 2, "orientation": "south"}, "equipment": {"kitchen": ["system", "counter_facing", "dishwasher", "water_purifier"], "bathroom": ["dryer", "auto_bath", "window"], "heating_cooling": ["energy_saving", "energy_saving_water_heater"], "utilities": ["double_glazing"], "security": ["tv_intercom"]}, "location_access": {"supermarket_walk_min": {"max": 10}, "quiet_residential": True}, "land_features": {"road_width_m": {"min": 6}, "flat_land": True}, "parking_transport": {"parking_capacity": 2}, "room_features": {"all_rooms_storage": True, "japanese_room": True, "toilets_count": 2, "walk_in_closet": True}}, "raw_features": ["長期優良住宅認定通知書", "建設住宅性能評価書（新築時）", "フラット３５・S適合証明書", "省エネルギー対策", "駐車２台可", "ＬＤＫ２０畳以上", "省エネ給湯器", "スーパー 徒歩10分以内", "システムキッチン", "浴室乾燥機", "陽当り良好", "全居室収納", "閑静な住宅地", "前道６ｍ以上", "和室", "シャワー付洗面化粧台", "対面式キッチン", "トイレ２ヶ所", "浴室１坪以上", "２階建", "東南向き", "複層ガラス", "オートバス", "温水洗浄便座", "床下収納", "浴室に窓", "吹抜け", "ＴＶモニタ付インターホン", "通風良好", "ウォークインクローゼット", "シューズインクローク", "平坦地", "食器洗乾燥機", "整備された歩道", "浄水器"], "feature_count": 35}},
    {"input": "ペット相談 /       エレベーター", "expected": {"feature_tags": ["pet_ok", "elevator"], "structured_features": {"equipment": {"utilities": ["elevator"]}, "room_features": {"pet_negotiable": True}}, "raw_features": ["ペット相談", "エレベーター"], "feature_count": 2}},
    {"input": "駐車３台以上可     /       省エネ給湯器    /       南向き  /       システムキッチン        /       浴室乾燥機      /       陽当り良好      /  全居室収納      /       閑静な住宅地    /       ＬＤＫ１５畳以上        /       角地    /       対面式キッチン  /       トイレ２ヶ所    /       浴室１坪以上    /       ２階建  /       複層ガラス      /       全室南向き      /       温水洗浄便座    /       床下収納        /  浴室に窓        /       ＴＶモニタ付インターホン        /       通風良好        /       ウォークインクローゼット        /       ＩＨクッキングヒーター      /       全居室複層ガラスか複層サッシ    /       都市ガス        /       シューズインクローク    /       食器洗乾燥機    /       浄水器      /       スマートキー", "expected": {"feature_tags": ["parking_3cars_plus", "energy_saving_heater", "south_facing", "system_kitchen", "bathroom_dryer", "good_sunlight", "all_rooms_storage", "quiet_area", "ldk_15tatami_plus", "corner_lot", "counter_kitchen", "2_toilets", "bathroom_1tsubo_plus", "2_story", "double_glazing", "south_facing", "温水洗浄便座", "床下収納", "bathroom_window", "tv_intercom", "通風良好", "walk_in_closet", "ih_cooktop", "double_glazing", "city_gas", "シューズインクローク", "dishwasher", "water_purifier", "smart_key"], "structured_features": {"building_specs": {"orientation": "south", "good_sunlight": True, "ldk_size_tatami": {"min": 15}, "bathroom_size_tsubo": {"min": 1}, "stories": 2}, "equipment": {"kitchen": ["system", "counter_facing", "ih_cooktop", "dishwasher", "water_purifier"], "bathroom": ["dryer", "window"], "heating_cooling": ["energy_saving_water_heater"], "utilities": ["double_glazing", "double_glazing", "city_gas"], "security": ["tv_intercom", "smart_key"]}, "location_access": {"quiet_residential": True}, "land_features": {"corner_lot": True}, "parking_transport": {"parking_capacity": 3}, "room_features": {"all_rooms_storage": True, "toilets_count": 2, "walk_in_closet": True}}, "raw_features": ["駐車３台以上可", "省エネ給湯器", "南向き", "システムキッチン", "浴室乾燥機", "陽当り良好", "全居室収納", "閑静な住宅地", "ＬＤＫ１５畳以上", "角地", "対面式キッチン", "トイレ２ヶ所", "浴室１坪以上", "２階建", "複層ガラス", "全室南向き", "温水洗浄便座", "床下収納", "浴室に窓", "ＴＶモニタ付インターホン", "通風良好", "ウォークインクローゼット", "ＩＨクッキングヒーター", "全居室複層ガラスか複層サッシ", "都市ガス", "シューズインクローク", "食器洗乾燥機", "浄水器", "スマートキー"], "feature_count": 29}},
    {"input": "瑕疵保証付（不動産会社独自）", "expected": {"feature_tags": ["defect_warranty"], "structured_features": {"certifications": {"defect_warranty": True}, "equipment": {}}, "raw_features": ["瑕疵保証付（不動産会社独自）"], "feature_count": 1}},
    {"input": "最上階角住戸", "expected": {"feature_tags": ["top_floor_corner"], "structured_features": {"equipment": {}, "room_features": {"corner_unit": True, "top_floor": True}}, "raw_features": ["最上階角住戸"], "feature_count": 1}},
    {"input": "分譲時の価格帯", "expected": {"feature_tags": ["original_sale_price"], "structured_features": {"equipment": {}}, "raw_features": ["分譲時の価格帯"], "feature_count": 1}},
    {"input": "管理人常駐", "expected": {"feature_tags": ["resident_manager"], "structured_features": {"equipment": {"security": ["resident_manager"]}}, "raw_features": ["管理人常駐"], "feature_count": 1}},
    {"input": "都心アクセス", "expected": {"feature_tags": ["city_center_access"], "structured_features": {"equipment": {}, "location_access": {"city_center_access": True}}, "raw_features": ["都心アクセス"], "feature_count": 1}},
    {"input": "古民家", "expected": {"feature_tags": ["old_house"], "structured_features": {"building_specs": {"house_style": "old_traditional"}, "equipment": {}}, "raw_features": ["古民家"], "feature_count": 1}},
    {"input": "宅配ボックス       /       エレベーター", "expected": {"feature_tags": ["delivery_box", "elevator"], "structured_features": {"equipment": {"utilities": ["elevator", "delivery_box"]}}, "raw_features": ["宅配ボックス", "エレベーター"], "feature_count": 2}},
    {"input": "駅 徒歩5分以内", "expected": {"feature_tags": ["station_walk_5min"], "structured_features": {"equipment": {}, "location_access": {"station_walk_min": {"max": 5}}}, "raw_features": ["駅 徒歩5分以内"], "feature_count": 1}},
    {"input": "建築中", "expected": {"feature_tags": ["under_construction"], "structured_features": {"building_specs": {"construction_status": "under_construction"}, "equipment": {}}, "raw_features": ["建築中"], "feature_count": 1}},
    {"input": "国道沿い", "expected": {"feature_tags": ["national_road"], "structured_features": {"equipment": {}, "location_access": {"national_road": True}}, "raw_features": ["国道沿い"], "feature_count": 1}},
    {"input": "食器洗い機 /       ＩＨクッキングヒーター", "expected": {"feature_tags": ["dishwasher", "ih_cooktop"], "structured_features": {"equipment": {"kitchen": ["dishwasher", "ih_cooktop"]}}, "raw_features": ["食器洗い機", "ＩＨクッキングヒーター"], "feature_count": 2}},
    {"input": "床暖房", "expected": {"feature_tags": ["floor_heating"], "structured_features": {"equipment": {"heating_cooling": ["floor_heating"]}}, "raw_features": ["床暖房"], "feature_count": 1}},
    {"input": "複数路線利用可", "expected": {"feature_tags": ["multiple_lines"], "structured_features": {"equipment": {}, "location_access": {"multiple_train_lines": True}}, "raw_features": ["複数路線利用可"], "feature_count": 1}},
    {"input": "リフォーム済み", "expected": {"feature_tags": ["renovated"], "structured_features": {"equipment": {}, "maintenance": {"renovated": True}}, "raw_features": ["リフォーム済み"], "feature_count": 1}},
    {"input": "即入居可", "expected": {"feature_tags": ["immediate_occupancy"], "structured_features": {"equipment": {}}, "raw_features": ["即入居可"], "feature_count": 1}},
    {"input": "公園隣接", "expected": {"feature_tags": ["park_adjacent"], "structured_features": {"equipment": {}, "location_access": {"park_adjacent": True}}, "raw_features": ["公園隣接"], "feature_count": 1}},
    {"input": "高層階", "expected": {"feature_tags": ["high_floor"], "structured_features": {"equipment": {}, "room_features": {"high_floor": True}}, "raw_features": ["高層階"], "feature_count": 1}},
    {"input": "駐車場敷地内", "expected": {"feature_tags": ["parking_on_site"], "structured_features": {"equipment": {}, "parking_transport": {"parking_on_site": True}}, "raw_features": ["駐車場敷地内"], "feature_count": 1}},
    {"input": "眺望良好", "expected": {"feature_tags": ["good_view"], "structured_features": {"building_specs": {"good_view": True}, "equipment": {}}, "raw_features": ["眺望良好"], "feature_count": 1}},
    {"input": "収納豊富", "expected": {"feature_tags": ["abundant_storage"], "structured_features": {"equipment": {}, "room_features": {"abundant_storage": True}}, "raw_features": ["収納豊富"], "feature_count": 1}},
    {"input": "バリアフリー", "expected": {"feature_tags": ["barrier_free"], "structured_features": {"building_specs": {"barrier_free": True}, "equipment": {}}, "raw_features": ["バリアフリー"], "feature_count": 1}},
]

TEST_CASES_BUILDING_STRUCTURE2 = [
    {"input": "4階/RC5階建", "expected": {"floor": 4, "structure": "RC", "total_floors": 5, "basement_floors": 0}},
    {"input": "11階/SRC11階建", "expected": {"floor": 11, "structure": "SRC", "total_floors": 11, "basement_floors": 0}},
    {"input": "12階/SRC14階建", "expected": {"floor": 12, "structure": "SRC", "total_floors": 14, "basement_floors": 0}},
    {"input": "1階/RC5階地下1階建", "expected": {"floor": 1, "structure": "RC", "total_floors": 5, "basement_floors": 1}},
    {"input": "9階/RC11階地下1階建", "expected": {"floor": 9, "structure": "RC", "total_floors": 11, "basement_floors": 1}},
    {"input": "11階/SRC15階地下1階建", "expected": {"floor": 11, "structure": "SRC", "total_floors": 15, "basement_floors": 1}},
    {"input": "3階/RC3階建", "expected": {"floor": 3, "structure": "RC", "total_floors": 3, "basement_floors": 0}},
    {"input": "15階/RC15階建", "expected": {"floor": 15, "structure": "RC", "total_floors": 15, "basement_floors": 0}},
    {"input": "2階/RC15階地下1階建", "expected": {"floor": 2, "structure": "RC", "total_floors": 15, "basement_floors": 1}},
    {"input": "8階/SRC10階建一部RC", "expected": {"floor": 8, "structure": "SRC", "total_floors": 10, "basement_floors": 0, 'partial_structure': 'RC'}},
]

TEST_CASES_REFORM = [
    {"input": "-", "expected": {"value": None}},
    {"input": "2025年1月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-01", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": []}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年3月完了予定　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-03", "is_scheduled": True, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": []}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年2月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室　その他：ハウスクリーニング…※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-02", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": ["ハウスクリーニング…"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2024年9月内装リフォーム完了", "expected": {"completion_date": None, "is_scheduled": False, "reform_areas": {"water_facilities": [], "interior": ["内装一般"], "other": []}, "has_reform": True}},
    {"input": "2025年1月完了　内装リフォーム：壁", "expected": {"completion_date": "2025-01", "is_scheduled": False, "reform_areas": {"water_facilities": [], "interior": ["壁"], "other": []}, "has_reform": True}},
    {"input": "2025年1月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室　その他：洗面化粧台、建具など※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-01", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": ["洗面化粧台、建具など"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年3月完了予定　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：床　その他：全室クロス/建具/洗…※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-03", "is_scheduled": True, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["床"], "other": ["全室クロス", "建具", "洗…"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年3月完了予定　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室　その他：フルリノベーション※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-03", "is_scheduled": True, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": ["フルリノベーション"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2024年12月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室　その他：給水給湯管新規交換※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2024-12", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": ["給水給湯管新規交換"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年2月完了　水回り設備交換：キッチン　内装リフォーム：壁・床　その他：ハウスクリーニング…※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-02", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン"], "interior": ["壁", "床"], "other": ["ハウスクリーニング…"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年2月完了予定　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床　その他：洗面台・給湯器交換※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-02", "is_scheduled": True, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床"], "other": ["洗面台", "給湯器交換"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2022年7月完了　水回り設備交換：キッチン・浴室・トイレ※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2022-07", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ※年月は一番古いリフォーム箇所を表します"], "interior": [], "other": []}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年1月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室　その他：建具交換　等※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-01", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": ["建具交換　等"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2024年10月内装リフォーム完了2024年10月外装リフォーム完了", "expected": {"completion_date": None, "is_scheduled": False, "reform_areas": {"water_facilities": [], "interior": ["内装一般"], "other": []}, "has_reform": True}},
    {"input": "2025年5月完了予定　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室2025年5月完了予定　その他リフォーム：外壁・屋根※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-05", "is_scheduled": True, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室2025年5月完了予定"], "other": []}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年1月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床　その他：洗面所 建具※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-01", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床"], "other": ["洗面所 建具"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年4月完了予定　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室　その他：ハウスクリーニング他※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-04", "is_scheduled": True, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": ["ハウスクリーニング他"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2024年11月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室　その他：洗面化粧台/洗面所/…※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2024-11", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": ["洗面化粧台", "洗面所", "…"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年2月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室　その他：洗面所/給湯器※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-02", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": ["洗面所", "給湯器"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年1月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：床※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-01", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["床"], "other": []}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年1月完了　水回り設備交換：キッチン・浴室　内装リフォーム：壁・床・全室　その他：ハウスクリーニング※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-01", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室"], "interior": ["壁", "床", "全室"], "other": ["ハウスクリーニング"]}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2023年7月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2023-07", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室"], "other": []}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年1月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室2025年1月完了　その他リフォーム：外壁※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-01", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室2025年1月完了"], "other": []}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年1月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁2025年1月完了　その他リフォーム：外壁※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-01", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁2025年1月完了"], "other": []}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2025年1月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床2025年1月完了　その他リフォーム：外壁※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2025-01", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床2025年1月完了"], "other": []}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
    {"input": "2024年10月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室2024年10月完了　その他リフォーム：外壁※年月は一番古いリフォーム箇所を表します", "expected": {"completion_date": "2024-10", "is_scheduled": False, "reform_areas": {"water_facilities": ["キッチン", "浴室", "トイレ"], "interior": ["壁", "床", "全室2024年10月完了"], "other": []}, "has_reform": True, "note": "年月は一番古いリフォーム箇所を表します"}},
]

TEST_CASES_SURROUNDING_FACILITIES = [
    {"input": "小学校\t糸満市立糸満小学校：徒歩14分（1120ｍ）\t中学校\t糸満市立糸満中学校：徒歩17分（1327ｍ）\tスーパー\tサンエー しおざきシティ：徒歩12分（884ｍ）\tスーパー\tタウンプラザかねひで いちゅまん市場：徒歩21分（1677ｍ）\tコンビニ\tセブンイレブン 糸満兼城サンプラザ糸満店：徒歩22分（1721ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "糸満市立糸満小学校", "walking_time": 14, "distance": 1120, "unit": "m"}, {"category": "中学校", "name": "糸満市立糸満中学校", "walking_time": 17, "distance": 1327, "unit": "m"}, {"category": "スーパー", "name": "サンエー しおざきシティ", "walking_time": 12, "distance": 884, "unit": "m"}, {"category": "スーパー", "name": "タウンプラザかねひで いちゅまん市場", "walking_time": 21, "distance": 1677, "unit": "m"}, {"category": "コンビニ", "name": "セブンイレブン 糸満兼城サンプラザ糸満店", "walking_time": 22, "distance": 1721, "unit": "m"}]}},
    {"input": "小学校\t熊谷市立熊谷東小学校：徒歩14分（1100ｍ）\t中学校\t熊谷市立富士見中学校：徒歩25分（2000ｍ）\t駅\tJR高崎線　熊谷駅：徒歩20分（1600ｍ）\t幼稚園・保育園\tくるみ保育園：徒歩4分（300ｍ）\t役所\t熊谷市役所：徒歩24分（1900ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "熊谷市立熊谷東小学校", "walking_time": 14, "distance": 1100, "unit": "m"}, {"category": "中学校", "name": "熊谷市立富士見中学校", "walking_time": 25, "distance": 2000, "unit": "m"}, {"category": "駅", "name": "JR高崎線　熊谷駅", "walking_time": 20, "distance": 1600, "unit": "m"}, {"category": "幼稚園・保育園", "name": "くるみ保育園", "walking_time": 4, "distance": 300, "unit": "m"}, {"category": "役所", "name": "熊谷市役所", "walking_time": 24, "distance": 1900, "unit": "m"}]}},
    {"input": "ショッピングセンター\tイオンタウン羽倉崎：徒歩12分（941ｍ）\tショッピングセンター\tりんくうプレミアム・アウトレット店：徒歩19分（1500ｍ）\tスーパー\tMaxvalu羽倉崎店：徒歩12分（893ｍ）\tコンビニ\tファミリーマート泉佐野羽倉崎店：徒歩6分（404ｍ）\tドラッグストア\tウエルシア泉佐野羽倉崎店：徒歩11分（829ｍ）", "expected": {"facilities": [{"category": "ショッピングセンター", "name": "イオンタウン羽倉崎", "walking_time": 12, "distance": 941, "unit": "m"}, {"category": "ショッピングセンター", "name": "りんくうプレミアム・アウトレット店", "walking_time": 19, "distance": 1500, "unit": "m"}, {"category": "スーパー", "name": "Maxvalu羽倉崎店", "walking_time": 12, "distance": 893, "unit": "m"}, {"category": "コンビニ", "name": "ファミリーマート泉佐野羽倉崎店", "walking_time": 6, "distance": 404, "unit": "m"}, {"category": "ドラッグストア", "name": "ウエルシア泉佐野羽倉崎店", "walking_time": 11, "distance": 829, "unit": "m"}]}},
    {"input": "駅\t阪神なんば線　千鳥橋駅：徒歩11分（880ｍ）\t駅\t阪神なんば線　伝法駅：徒歩15分（1200ｍ）\tスーパー\tラ・ムー　此花店：徒歩12分（960ｍ）\tその他環境\t春日出商店街：徒歩2分（160ｍ）\t公園\t此花公園：徒歩2分（160ｍ）", "expected": {"facilities": [{"category": "駅", "name": "阪神なんば線　千鳥橋駅", "walking_time": 11, "distance": 880, "unit": "m"}, {"category": "駅", "name": "阪神なんば線　伝法駅", "walking_time": 15, "distance": 1200, "unit": "m"}, {"category": "スーパー", "name": "ラ・ムー　此花店", "walking_time": 12, "distance": 960, "unit": "m"}, {"category": "その他", "name": "春日出商店街", "walking_time": 2, "distance": 160, "unit": "m"}, {"category": "公園", "name": "此花公園", "walking_time": 2, "distance": 160, "unit": "m"}]}},
    {"input": "小学校\t深谷市立上柴東小学校：徒歩11分（867ｍ）\t中学校\t深谷市立上柴中学校：徒歩16分（1251ｍ）\t幼稚園・保育園\t第２のぞみ保育園キッズガーデン：徒歩2分（96ｍ）\tスーパー\tフーコット深谷店：徒歩6分（420ｍ）\tショッピングセンター\tArio(アリオ)深谷：徒歩13分（967ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "深谷市立上柴東小学校", "walking_time": 11, "distance": 867, "unit": "m"}, {"category": "中学校", "name": "深谷市立上柴中学校", "walking_time": 16, "distance": 1251, "unit": "m"}, {"category": "幼稚園・保育園", "name": "第２のぞみ保育園キッズガーデン", "walking_time": 2, "distance": 96, "unit": "m"}, {"category": "スーパー", "name": "フーコット深谷店", "walking_time": 6, "distance": 420, "unit": "m"}, {"category": "ショッピングセンター", "name": "Ario(アリオ)深谷", "walking_time": 13, "distance": 967, "unit": "m"}]}},
    {"input": "幼稚園・保育園\t郡山市立富久山保育所：徒歩26分（2027ｍ）\t小学校\t郡山市立行健小学校：徒歩22分（1758ｍ）\t中学校\t郡山市立行健中学校：徒歩34分（2712ｍ）\tスーパー\tブイチェーン富久山店：徒歩19分（1491ｍ）\tドラッグストア\t薬王堂 郡山富久山店：徒歩5分（341ｍ）", "expected": {"facilities": [{"category": "幼稚園・保育園", "name": "郡山市立富久山保育所", "walking_time": 26, "distance": 2027, "unit": "m"}, {"category": "小学校", "name": "郡山市立行健小学校", "walking_time": 22, "distance": 1758, "unit": "m"}, {"category": "中学校", "name": "郡山市立行健中学校", "walking_time": 34, "distance": 2712, "unit": "m"}, {"category": "スーパー", "name": "ブイチェーン富久山店", "walking_time": 19, "distance": 1491, "unit": "m"}, {"category": "ドラッグストア", "name": "薬王堂 郡山富久山店", "walking_time": 5, "distance": 341, "unit": "m"}]}},
    {"input": "スーパー\t西友熱田三番町店：徒歩6分（480ｍ）\tショッピングセンター\tイオンタウン熱田千年：徒歩12分（922ｍ）\tドラッグストア\tスギ薬局南一番店：徒歩4分（314ｍ）\tホームセンター\tコーナンPRO熱田四番町店：徒歩9分（654ｍ）\t病院\tみなと医療生活協同組合協立総合病院：徒歩7分（517ｍ）", "expected": {"facilities": [{"category": "スーパー", "name": "西友熱田三番町店", "walking_time": 6, "distance": 480, "unit": "m"}, {"category": "ショッピングセンター", "name": "イオンタウン熱田千年", "walking_time": 12, "distance": 922, "unit": "m"}, {"category": "ドラッグストア", "name": "スギ薬局南一番店", "walking_time": 4, "distance": 314, "unit": "m"}, {"category": "ホームセンター", "name": "コーナンPRO熱田四番町店", "walking_time": 9, "distance": 654, "unit": "m"}, {"category": "病院", "name": "みなと医療生活協同組合協立総合病院", "walking_time": 7, "distance": 517, "unit": "m"}]}},
    {"input": "小学校\t朝霞市立朝霞第五小学校：徒歩13分（990ｍ）\t駅\t志木駅南口：徒歩9分（720ｍ）\t駅\t朝霞台駅南口：徒歩11分（840ｍ）\t駅\t北朝霞駅(JR東日本 武蔵野線)：徒歩12分（930ｍ）\tスーパー\tサミットストア朝霞台店：徒歩9分（700ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "朝霞市立朝霞第五小学校", "walking_time": 13, "distance": 990, "unit": "m"}, {"category": "駅", "name": "志木駅南口", "walking_time": 9, "distance": 720, "unit": "m"}, {"category": "駅", "name": "朝霞台駅南口", "walking_time": 11, "distance": 840, "unit": "m"}, {"category": "駅", "name": "北朝霞駅(JR東日本 武蔵野線)", "walking_time": 12, "distance": 930, "unit": "m"}, {"category": "スーパー", "name": "サミットストア朝霞台店", "walking_time": 9, "distance": 700, "unit": "m"}]}},
    {"input": "小学校\t扶桑町立柏森小学校：徒歩20分（1600ｍ）\tその他環境\t扶桑町図書館：徒歩3分（180ｍ）\t役所\t扶桑町役場：徒歩7分（500ｍ）\t駅\t名鉄犬山線『扶桑』駅：徒歩10分（800ｍ）\tショッピングセンター\tイオンモール扶桑：徒歩14分（1100ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "扶桑町立柏森小学校", "walking_time": 20, "distance": 1600, "unit": "m"}, {"category": "その他", "name": "扶桑町図書館", "walking_time": 3, "distance": 180, "unit": "m"}, {"category": "役所", "name": "扶桑町役場", "walking_time": 7, "distance": 500, "unit": "m"}, {"category": "駅", "name": "名鉄犬山線『扶桑』駅", "walking_time": 10, "distance": 800, "unit": "m"}, {"category": "ショッピングセンター", "name": "イオンモール扶桑", "walking_time": 14, "distance": 1100, "unit": "m"}]}},
    {"input": "ショッピングセンター\tヨークタウン市名坂：徒歩14分（1071ｍ）\tコンビニ\tセブンイレブン仙台泉本田町店：徒歩5分（376ｍ）\t病院\t医療法人徳洲会仙台徳洲会病院：徒歩20分（1557ｍ）\t郵便局\t泉松陵郵便局：徒歩31分（2406ｍ）\t公園\t松陵公園：徒歩30分（2345ｍ）", "expected": {"facilities": [{"category": "ショッピングセンター", "name": "ヨークタウン市名坂", "walking_time": 14, "distance": 1071, "unit": "m"}, {"category": "コンビニ", "name": "セブンイレブン仙台泉本田町店", "walking_time": 5, "distance": 376, "unit": "m"}, {"category": "病院", "name": "医療法人徳洲会仙台徳洲会病院", "walking_time": 20, "distance": 1557, "unit": "m"}, {"category": "郵便局", "name": "泉松陵郵便局", "walking_time": 31, "distance": 2406, "unit": "m"}, {"category": "公園", "name": "松陵公園", "walking_time": 30, "distance": 2345, "unit": "m"}]}},
    {"input": "駅\t江南駅：徒歩14分（1100ｍ）\t小学校\t江南市立古知野東小学校：徒歩13分（1000ｍ）\t中学校\t江南市立古知野中学校：徒歩14分（1050ｍ）\t病院\t平成クリニック：徒歩9分（700ｍ）\t公園\t中央公園：徒歩7分（550ｍ）", "expected": {"facilities": [{"category": "駅", "name": "江南駅", "walking_time": 14, "distance": 1100, "unit": "m"}, {"category": "小学校", "name": "江南市立古知野東小学校", "walking_time": 13, "distance": 1000, "unit": "m"}, {"category": "中学校", "name": "江南市立古知野中学校", "walking_time": 14, "distance": 1050, "unit": "m"}, {"category": "病院", "name": "平成クリニック", "walking_time": 9, "distance": 700, "unit": "m"}, {"category": "公園", "name": "中央公園", "walking_time": 7, "distance": 550, "unit": "m"}]}},
    {"input": "小学校\t安城市立桜井小学校：徒歩20分（1600ｍ）\t中学校\t安城市立桜井中学校：徒歩15分（1200ｍ）\tスーパー\tアピタ安城南店：徒歩28分（2200ｍ）\t駅\t桜井駅：徒歩27分（2100ｍ）\t公園\t大福公園：徒歩3分（190ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "安城市立桜井小学校", "walking_time": 20, "distance": 1600, "unit": "m"}, {"category": "中学校", "name": "安城市立桜井中学校", "walking_time": 15, "distance": 1200, "unit": "m"}, {"category": "スーパー", "name": "アピタ安城南店", "walking_time": 28, "distance": 2200, "unit": "m"}, {"category": "駅", "name": "桜井駅", "walking_time": 27, "distance": 2100, "unit": "m"}, {"category": "公園", "name": "大福公園", "walking_time": 3, "distance": 190, "unit": "m"}]}},
    {"input": "小学校\t宇土市立宇土小学校：徒歩11分（870ｍ）\t中学校\t宇土市立　鶴城中学校：徒歩17分（1310ｍ）\t幼稚園・保育園\t宇土エンゼル保育園：徒歩5分（330ｍ）\t病院\t村上歯科医院：徒歩7分（560ｍ）\tショッピングセンター\t宇土シティモール：徒歩29分（2280ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "宇土市立宇土小学校", "walking_time": 11, "distance": 870, "unit": "m"}, {"category": "中学校", "name": "宇土市立　鶴城中学校", "walking_time": 17, "distance": 1310, "unit": "m"}, {"category": "幼稚園・保育園", "name": "宇土エンゼル保育園", "walking_time": 5, "distance": 330, "unit": "m"}, {"category": "病院", "name": "村上歯科医院", "walking_time": 7, "distance": 560, "unit": "m"}, {"category": "ショッピングセンター", "name": "宇土シティモール", "walking_time": 29, "distance": 2280, "unit": "m"}]}},
    {"input": "ショッピングセンター\tイオンモール常滑：徒歩17分（1309ｍ）\tスーパー\tにぎわい市場マルス常滑駅前店：徒歩8分（598ｍ）\tコンビニ\tローソン常滑駅西店：徒歩6分（438ｍ）\tコンビニ\tファミリーマート常滑栄町店：徒歩11分（856ｍ）\t幼稚園・保育園\t常滑市立常滑幼稚園：徒歩16分（1256ｍ）", "expected": {"facilities": [{"category": "ショッピングセンター", "name": "イオンモール常滑", "walking_time": 17, "distance": 1309, "unit": "m"}, {"category": "スーパー", "name": "にぎわい市場マルス常滑駅前店", "walking_time": 8, "distance": 598, "unit": "m"}, {"category": "コンビニ", "name": "ローソン常滑駅西店", "walking_time": 6, "distance": 438, "unit": "m"}, {"category": "コンビニ", "name": "ファミリーマート常滑栄町店", "walking_time": 11, "distance": 856, "unit": "m"}, {"category": "幼稚園・保育園", "name": "常滑市立常滑幼稚園", "walking_time": 16, "distance": 1256, "unit": "m"}]}},
    {"input": "小学校\t豊田市立前山小学校：徒歩16分（1280ｍ）\t中学校\t豊田市立豊南中学校：徒歩19分（1460ｍ）\tコンビニ\tファミリーマート豊田渡刈町店：徒歩7分（500ｍ）\t駅\t末野原駅：徒歩21分（1630ｍ）\t公園\t明和町第1ちびっこ広場：徒歩2分（150ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "豊田市立前山小学校", "walking_time": 16, "distance": 1280, "unit": "m"}, {"category": "中学校", "name": "豊田市立豊南中学校", "walking_time": 19, "distance": 1460, "unit": "m"}, {"category": "コンビニ", "name": "ファミリーマート豊田渡刈町店", "walking_time": 7, "distance": 500, "unit": "m"}, {"category": "駅", "name": "末野原駅", "walking_time": 21, "distance": 1630, "unit": "m"}, {"category": "公園", "name": "明和町第1ちびっこ広場", "walking_time": 2, "distance": 150, "unit": "m"}]}},
    {"input": "ショッピングセンター\tMEGAドン・キホーテ函館店：徒歩22分（1689ｍ）\tスーパー\t生鮮げんき市場赤川店：徒歩14分（1100ｍ）\tコンビニ\tファミリーマート函館神山町店：徒歩5分（334ｍ）\t小学校\t函館市立神山小学校：徒歩5分（366ｍ）", "expected": {"facilities": [{"category": "ショッピングセンター", "name": "MEGAドン・キホーテ函館店", "walking_time": 22, "distance": 1689, "unit": "m"}, {"category": "スーパー", "name": "生鮮げんき市場赤川店", "walking_time": 14, "distance": 1100, "unit": "m"}, {"category": "コンビニ", "name": "ファミリーマート函館神山町店", "walking_time": 5, "distance": 334, "unit": "m"}, {"category": "小学校", "name": "函館市立神山小学校", "walking_time": 5, "distance": 366, "unit": "m"}]}},
    {"input": "小学校\t名護市立屋部小学校：徒歩6分（415ｍ）\t中学校\t名護市立屋部中学校：徒歩13分（1013ｍ）\tスーパー\tコープなご宮里：徒歩26分（2052ｍ）\tコンビニ\t沖縄ファミリーマート 名護宇茂佐店：徒歩7分（531ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "名護市立屋部小学校", "walking_time": 6, "distance": 415, "unit": "m"}, {"category": "中学校", "name": "名護市立屋部中学校", "walking_time": 13, "distance": 1013, "unit": "m"}, {"category": "スーパー", "name": "コープなご宮里", "walking_time": 26, "distance": 2052, "unit": "m"}, {"category": "コンビニ", "name": "沖縄ファミリーマート 名護宇茂佐店", "walking_time": 7, "distance": 531, "unit": "m"}]}},
    {"input": "小学校\t沖縄市立美里小学校：徒歩16分（1251ｍ）\tスーパー\tFRESH PLAZA Union(フレッシュプラザユニオン) 松本店：徒歩5分（354ｍ）\tスーパー\tタウンプラザかねひで 越来店：徒歩19分（1518ｍ）\tコンビニ\t沖縄ファミリーマート 松本五丁目店：徒歩6分（439ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "沖縄市立美里小学校", "walking_time": 16, "distance": 1251, "unit": "m"}, {"category": "スーパー", "name": "FRESH PLAZA Union(フレッシュプラザユニオン) 松本店", "walking_time": 5, "distance": 354, "unit": "m"}, {"category": "スーパー", "name": "タウンプラザかねひで 越来店", "walking_time": 19, "distance": 1518, "unit": "m"}, {"category": "コンビニ", "name": "沖縄ファミリーマート 松本五丁目店", "walking_time": 6, "distance": 439, "unit": "m"}]}},
    {"input": "マーブル保育園まで550m", "expected": {"facilities": [{"category": None, "name": "マーブル保育園", "walking_time": None, "distance": 550, "unit": "m"}]}},
    {"input": "スーパー\tアピタ安城南店：徒歩7分（560ｍ）\tドラッグストア\tスギ薬局桜井店：徒歩3分（240ｍ）", "expected": {"facilities": [{"category": "スーパー", "name": "アピタ安城南店", "walking_time": 7, "distance": 560, "unit": "m"}, {"category": "ドラッグストア", "name": "スギ薬局桜井店", "walking_time": 3, "distance": 240, "unit": "m"}]}},
    {"input": "小学校\t恩方第一小学校：徒歩12分（885ｍ）\tスーパー\tスーパーアルプス恩方店：徒歩4分（314ｍ）\t病院\tかわさきクリニック：徒歩7分（482ｍ）\tドラッグストア\tWelpark(ウェルパーク) 八王子下恩方店：徒歩3分（161ｍ）\t郵便局\t恩方郵便局：徒歩5分（375ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "恩方第一小学校", "walking_time": 12, "distance": 885, "unit": "m"}, {"category": "スーパー", "name": "スーパーアルプス恩方店", "walking_time": 4, "distance": 314, "unit": "m"}, {"category": "病院", "name": "かわさきクリニック", "walking_time": 7, "distance": 482, "unit": "m"}, {"category": "ドラッグストア", "name": "Welpark(ウェルパーク) 八王子下恩方店", "walking_time": 3, "distance": 161, "unit": "m"}, {"category": "郵便局", "name": "恩方郵便局", "walking_time": 5, "distance": 375, "unit": "m"}]}},
    {"input": "小学校\t名古屋市立千年小学校：徒歩6分（460ｍ）\tスーパー\t西友熱田三番町店：徒歩5分（365ｍ）\tコンビニ\tセブンイレブン 名古屋港区七番町店：徒歩8分（585ｍ）\t銀行\t百五銀行 港支店：徒歩9分（660ｍ）\t公園\t三北どんぐりひろば：徒歩4分（291ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "名古屋市立千年小学校", "walking_time": 6, "distance": 460, "unit": "m"}, {"category": "スーパー", "name": "西友熱田三番町店", "walking_time": 5, "distance": 365, "unit": "m"}, {"category": "コンビニ", "name": "セブンイレブン 名古屋港区七番町店", "walking_time": 8, "distance": 585, "unit": "m"}, {"category": "銀行", "name": "百五銀行 港支店", "walking_time": 9, "distance": 660, "unit": "m"}, {"category": "公園", "name": "三北どんぐりひろば", "walking_time": 4, "distance": 291, "unit": "m"}]}},
    {"input": "小学校\t常滑市立常滑西小学校：徒歩17分（1360ｍ）\tスーパー\tショッピングマルス 常滑駅前店：徒歩7分（550ｍ）\tコンビニ\tローソン 常滑駅西店：徒歩6分（405ｍ）\t郵便局\t常滑郵便局：徒歩9分（678ｍ）\t銀行\t三菱UFJ銀行常滑支店：徒歩7分（560ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "常滑市立常滑西小学校", "walking_time": 17, "distance": 1360, "unit": "m"}, {"category": "スーパー", "name": "ショッピングマルス 常滑駅前店", "walking_time": 7, "distance": 550, "unit": "m"}, {"category": "コンビニ", "name": "ローソン 常滑駅西店", "walking_time": 6, "distance": 405, "unit": "m"}, {"category": "郵便局", "name": "常滑郵便局", "walking_time": 9, "distance": 678, "unit": "m"}, {"category": "銀行", "name": "三菱UFJ銀行常滑支店", "walking_time": 7, "distance": 560, "unit": "m"}]}},
    {"input": "ショッピングセンター\tベビー・子供用品バースデイ鹿屋店：徒歩9分（700ｍ）\tショッピングセンター\tファッションセンターしまむら鹿屋店：徒歩8分（639ｍ）\tコンビニ\tセブンイレブン鹿屋新川町店：徒歩10分（798ｍ）\tコンビニ\tファミリーマート鹿屋寿七丁目店：徒歩10分（793ｍ）", "expected": {"facilities": [{"category": "ショッピングセンター", "name": "ベビー・子供用品バースデイ鹿屋店", "walking_time": 9, "distance": 700, "unit": "m"}, {"category": "ショッピングセンター", "name": "ファッションセンターしまむら鹿屋店", "walking_time": 8, "distance": 639, "unit": "m"}, {"category": "コンビニ", "name": "セブンイレブン鹿屋新川町店", "walking_time": 10, "distance": 798, "unit": "m"}, {"category": "コンビニ", "name": "ファミリーマート鹿屋寿七丁目店", "walking_time": 10, "distance": 793, "unit": "m"}]}},
    {"input": "幼稚園・保育園\t守山市立守山幼稚園：徒歩5分（340ｍ）\tスーパー\t西友守山店：徒歩5分（350ｍ）\tドラッグストア\tキリン堂守山梅田店：徒歩7分（490ｍ）\t病院\t社会福祉法人恩賜財団済生会守山市民病院：徒歩13分（990ｍ）\t駅\t東海道本線　守山駅：徒歩4分（320ｍ）", "expected": {"facilities": [{"category": "幼稚園・保育園", "name": "守山市立守山幼稚園", "walking_time": 5, "distance": 340, "unit": "m"}, {"category": "スーパー", "name": "西友守山店", "walking_time": 5, "distance": 350, "unit": "m"}, {"category": "ドラッグストア", "name": "キリン堂守山梅田店", "walking_time": 7, "distance": 490, "unit": "m"}, {"category": "病院", "name": "社会福祉法人恩賜財団済生会守山市民病院", "walking_time": 13, "distance": 990, "unit": "m"}, {"category": "駅", "name": "東海道本線　守山駅", "walking_time": 4, "distance": 320, "unit": "m"}]}},
    {"input": "駅\tOsakaMetro中央線　朝潮橋駅：徒歩4分（320ｍ）\tスーパー\tライフ　朝潮橋駅前店：徒歩5分（400ｍ）\tその他環境\tAsueプール：徒歩5分（400ｍ）\tその他環境\tAsueアリーナ大阪：徒歩9分（720ｍ）\t小学校\t田中小学校：徒歩1分（80ｍ）", "expected": {"facilities": [{"category": "駅", "name": "OsakaMetro中央線　朝潮橋駅", "walking_time": 4, "distance": 320, "unit": "m"}, {"category": "スーパー", "name": "ライフ　朝潮橋駅前店", "walking_time": 5, "distance": 400, "unit": "m"}, {"category": "その他", "name": "Asueプール", "walking_time": 5, "distance": 400, "unit": "m"}, {"category": "その他", "name": "Asueアリーナ大阪", "walking_time": 9, "distance": 720, "unit": "m"}, {"category": "小学校", "name": "田中小学校", "walking_time": 1, "distance": 80, "unit": "m"}]}},
    {"input": "小学校\t名護市立大宮小学校：徒歩9分（687ｍ）\t中学校\t名護市立大宮中学校：徒歩21分（1666ｍ）\tスーパー\tコープなご宮里：徒歩6分（401ｍ）\tコンビニ\t沖縄ファミリーマート 名護宮里店：徒歩3分（164ｍ）", "expected": {"facilities": [{"category": "小学校", "name": "名護市立大宮小学校", "walking_time": 9, "distance": 687, "unit": "m"}, {"category": "中学校", "name": "名護市立大宮中学校", "walking_time": 21, "distance": 1666, "unit": "m"}, {"category": "スーパー", "name": "コープなご宮里", "walking_time": 6, "distance": 401, "unit": "m"}, {"category": "コンビニ", "name": "沖縄ファミリーマート 名護宮里店", "walking_time": 3, "distance": 164, "unit": "m"}]}}
]

TEST_CASES_PARKING = [
    {"input": "空無", "expected": {"availability": False, "value": None}},
    {"input": "-", "expected": {"availability": False, "value": None}},
    {"input": "専用使用権付駐車場（無料）", "expected": {"availability": True, "location": "専用使用権付", "value": 0, "min": None, "max": None, "unit": "円", "frequency": None, "note": None}},
    {"input": "敷地内（8000円～1万2000円／月）", "expected": {"availability": True, "location": "敷地内", "value": 10000, "min": 8000, "max": 12000, "unit": "円", "frequency": "月", "note": None}},
    {"input": "敷地内（1万6761円～2万951円／月）", "expected": {"availability": True, "location": "敷地内", "value": 18856, "min": 16761, "max": 20951, "unit": "円", "frequency": "月", "note": None}},
    {"input": "敷地内（7000円～2万2000円／月）", "expected": {"availability": True, "location": "敷地内", "value": 14500, "min": 7000, "max": 22000, "unit": "円", "frequency": "月", "note": None}},
    {"input": "敷地内（5000円～2万3000円／月）", "expected": {"availability": True, "location": "敷地内", "value": 14000, "min": 5000, "max": 23000, "unit": "円", "frequency": "月", "note": None}},
    {"input": "敷地外（0円／月）", "expected": {"availability": True, "location": "敷地外", "value": 0, "min": None, "max": None, "unit": "円", "frequency": "月", "note": None}},
    {"input": "敷地内（2万5000円／月）", "expected": {"availability": True, "location": "敷地内", "value": 25000, "min": None, "max": None, "unit": "円", "frequency": "月", "note": None}},
    {"input": "敷地内（料金無）", "expected": {"availability": True, "location": "敷地内", "value": 0, "min": None, "max": None, "unit": "円", "frequency": None, "note": None}},
]

TEST_CASES_BUILDING_STRUCTURE = [
    {"input": "木造3階建（軸組工法）一部RC", "expected": {"structure": "W", "total_floors": 3, "basement_floors": 0, "partial_structure": "RC", "note": "軸組工法"}},
    {"input": "木造2階地下4階建", "expected": {"structure": "W", "total_floors": 2, "basement_floors": 4}},
    {"input": "木造（在来軸組工法）、ガルバリウム鋼板葺、省令準耐火構造、ZEH水準省エネ住宅", "expected": {"structure": "W"}},
    {"input": "構造：鉄骨造 工法：ユニット工法 地上階：1階", "expected": {"structure": "S", "total_floors": 1, "basement_floors": 0}},
    {"input": "木造在来軸組工法2階建（910モジュール）", "expected": {"structure": "W", "total_floors": 2, "basement_floors": 0, "note": "910モジュール"}},
    {"input": "RC2階地下1階建一部木造", "expected": {"structure": "RC", "total_floors": 2, "basement_floors": 1, "partial_structure": "W"}},
    {"input": "木造2階建（軸組工法）一部外壁サイディング", "expected": {"structure": "W", "total_floors": 2, "basement_floors": 0, "partial_structure": "外壁サイディング", "note": "軸組工法"}},
    {"input": "木・鉄筋コンクリート3階建", "expected": {"structure": "木・鉄筋コンクリート", "total_floors": 3, "basement_floors": 0}},
    {"input": "木造アスファルトシングル葺　平屋建て・２階建て", "expected": {"structure": "木造アスファルトシングル葺　平屋建て・", "total_floors": 2, "basement_floors": 0, "note": "アスファルトシングル葺"}},
    {"input": "アスファルトシングル葺き", "expected": {"raw_value": "アスファルトシングル葺き"}},
]

TEST_CASES_LAND_USE = [
    {"input": "-", "expected": {"value": None}},
    {"input": "宅地", "expected": {"values": ["宅地"]}},
    {"input": "宅地・雑種地", "expected": {"values": ["宅地", "雑種地"]}},
    {"input": "畑（宅地渡し）", "expected": {"values": ["畑"], "note": "宅地渡し"}},
    {"input": "田、宅地", "expected": {"values": ["田", "宅地"]}},
    {"input": "宅地、公衆用道路、雑種地", "expected": {"values": ["宅地", "公衆用道路", "雑種地"]}},
    {"input": "畑（農地転用後、宅地に変更）", "expected": {"values": ["畑"], "note": "農地転用後、宅地に変更"}},
    {"input": "雑種地　引渡し後、宅地に地目変更予定", "expected": {"values": ["雑種地", "宅地"]}},
    {"input": "山林（造成完了後「宅地」へ変更）", "expected": {"values": ["山林"], "note": "造成完了後「宅地」へ変更"}},
    {"input": "宅地・ゴミステーション部分のみ雑種地", "expected": {"values": ["宅地", "雑種地"]}},
]

TEST_CASES_FLOOR_PLAN = [
    {"input": "1号棟      価格    ：      2590万円        間取り  ：      4LDK    土地面積        ：      160.01m2        建物面積        ：      108.54m2", "expected": {"building_number": "1号棟", "price": {"value": 2590.0, "unit": "万円"}, "layout": "4LDK", "land_area": {"value": 160.01, "unit": "m2"}, "building_area": {"value": 108.54, "unit": "m2"}}},
    {"input": "A号棟      価格    ：      3790万円        間取り  ：      4LDK    土地面積        ：      104.8m2 建物面積        ：      98.95m2", "expected": {"building_number": "A号棟", "price": {"value": 3790.0, "unit": "万円"}, "layout": "4LDK", "land_area": {"value": 104.8, "unit": "m2"}, "building_area": {"value": 98.95, "unit": "m2"}}},
    {"input": "価格       ：      5180万円        間取り  ：      3LDK+S  土地面積        ：      91.18m2 建物面積        ：      90.15m2", "expected": {"price": {"value": 5180.0, "unit": "万円"}, "layout": "3LDK+S", "land_area": {"value": 91.18, "unit": "m2"}, "building_area": {"value": 90.15, "unit": "m2"}}},
    {"input": "2号棟      価格    ：      4480万円        間取り  ：      1LDK+2S 土地面積        ：      80.22m2 建物面積        ：      63.76m2", "expected": {"building_number": "2号棟", "price": {"value": 4480.0, "unit": "万円"}, "layout": "1LDK+2S", "land_area": {"value": 80.22, "unit": "m2"}, "building_area": {"value": 63.76, "unit": "m2"}}},
    {"input": "F号棟      価格    ：      5490万円        間取り  ：      4LDK    土地面積        ：      111.25m2        建物面積        ：      98.54m2", "expected": {"building_number": "F号棟", "price": {"value": 5490.0, "unit": "万円"}, "layout": "4LDK", "land_area": {"value": 111.25, "unit": "m2"}, "building_area": {"value": 98.54, "unit": "m2"}}},
    {"input": "1号棟      価格    ：      2630万円        間取り  ：      5LDK    土地面積        ：      216.91m2        建物面積        ：      107.32m2", "expected": {"building_number": "1号棟", "price": {"value": 2630.0, "unit": "万円"}, "layout": "5LDK", "land_area": {"value": 216.91, "unit": "m2"}, "building_area": {"value": 107.32, "unit": "m2"}}},
    {"input": "B棟        価格    ：      8680万円        間取り  ：      2LDK+S  土地面積        ：      55.66m2 建物面積        ：      101.98m2", "expected": {"building_number": "B棟", "price": {"value": 8680.0, "unit": "万円"}, "layout": "2LDK+S", "land_area": {"value": 55.66, "unit": "m2"}, "building_area": {"value": 101.98, "unit": "m2"}}},
    {"input": "1号棟      価格    ：      5280万円        間取り  ：      4LDK    土地面積        ：      56.01m2 建物面積        ：      110.94m2", "expected": {"building_number": "1号棟", "price": {"value": 5280.0, "unit": "万円"}, "layout": "4LDK", "land_area": {"value": 56.01, "unit": "m2"}, "building_area": {"value": 110.94, "unit": "m2"}}},
    {"input": "2号棟      価格    ：      2490万円        間取り  ：      4LDK    土地面積        ：      323.86m2        建物面積        ：      105.99m2", "expected": {"building_number": "2号棟", "price": {"value": 2490.0, "unit": "万円"}, "layout": "4LDK", "land_area": {"value": 323.86, "unit": "m2"}, "building_area": {"value": 105.99, "unit": "m2"}}},
    {"input": "-", "expected": {"value": None}},
]

TEST_CASES_BUILDING_COVERAGE = [
    {"input": "60％・200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ペい率：60％、容積率：200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ぺい率：60％/容積率：200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ぺい率：60/容積率：200", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ぺい率・容積率：60％・200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ぺい率60％、容積率200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ぺい率：60％　容積率：200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "60％/200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ぺい率：60%、容積率：200%", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ペい率：60％・70％、容積率：200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ペい率：50％・60％、容積率：100％・200％", "expected": {"building_coverage": 50.0, "floor_area_ratio": 100.0, "unit": "%"}},
    {"input": "建ペい率：60％(70％)、容積率：200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ぺい率：６０％、容積率：２００％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "60％　200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建蔽率60％　容積率200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ペい率：60％（富士見公園通り道路より20m以内）・50％（富士見公園通り道路より20m超）、容積率：200％（富士見公園通り道路より20m以内）・100％（富士見公園通り道路より20m超）", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "建ぺい率：60％（1号地は70％）/容積率：200％", "expected": {"building_coverage": 60.0, "floor_area_ratio": 200.0, "unit": "%"}},
    {"input": "80％・500％", "expected": {"building_coverage": 80.0, "floor_area_ratio": 500.0, "unit": "%"}},
    {"input": "30％・50％", "expected": {"building_coverage": 30.0, "floor_area_ratio": 50.0, "unit": "%"}},
    {"input": "-", "expected": {"value": None}},
]
