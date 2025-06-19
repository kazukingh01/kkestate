"""
処理関数と清浄化名から確定的にestate_mst_cleaned.typeを生成
"""

from typing import Dict, Any, Callable
from .json_cleaner import (
    clean_price_to_json, clean_area_to_json, clean_layout_to_json, 
    clean_date_to_json, clean_management_fee_to_json, clean_number_to_json, 
    clean_boolean_to_json, clean_text_to_json, clean_access_to_json, 
    clean_zoning_to_json, clean_force_null_to_json, clean_units_to_json, 
    clean_price_band_to_json, clean_other_expenses_to_json, 
    clean_multiple_area_to_json, clean_restrictions_to_json, 
    clean_expiry_date_to_json, clean_company_info_to_json, 
    clean_delivery_date_to_json, clean_address_to_json, 
    clean_utility_cost_to_json, clean_feature_pickup_to_json, 
    clean_reform_to_json, clean_building_structure_to_json, 
    clean_parking_to_json, clean_surrounding_facilities_to_json,
    generate_address_type_schema, generate_price_type_schema, 
    generate_area_type_schema, generate_layout_type_schema, 
    generate_date_type_schema, generate_access_type_schema,
    generate_boolean_type_schema, generate_number_type_schema, 
    generate_text_type_schema, generate_utility_cost_type_schema, 
    generate_feature_pickup_type_schema
)

def generate_type_schema_from_function(processing_function: Callable, cleaned_name: str, has_period: bool = False) -> Dict[str, Any]:
    """
    処理関数と清浄化名から確定的に型スキーマを生成
    
    Args:
        processing_function: JSON処理関数
        cleaned_name: estate_mst_cleaned.name
        has_period: 期別情報を含むかどうか
        
    Returns:
        Dict[str, Any]: 型スキーマ
    """
    
    # 関数ベースのスキーママッピング（確定的）
    function_schema_mapping = {
        clean_address_to_json: generate_address_type_schema,
        clean_price_to_json: generate_price_type_schema,
        clean_area_to_json: generate_area_type_schema,
        clean_multiple_area_to_json: lambda: {
            "base_type": "array",
            "data_type": "multiple_area",
            "fields": ["areas"],
            "area_fields": ["type", "value", "unit", "tsubo", "monthly_fee", "measurement_type"],
            "period_aware": has_period
        },
        clean_layout_to_json: generate_layout_type_schema,
        clean_date_to_json: generate_date_type_schema,
        clean_delivery_date_to_json: lambda: {
            "base_type": "single",
            "data_type": "delivery_date",
            "fields": ["type", "year", "month", "day", "estimated_date", "period_text", "months", "note", "is_planned", "value"],
            "period_aware": has_period
        },
        clean_units_to_json: lambda: {
            "base_type": "single",
            "data_type": "units",
            "fields": ["value", "unit", "total", "current"],
            "period_aware": has_period
        },
        clean_number_to_json: generate_number_type_schema,
        clean_management_fee_to_json: lambda: {
            "base_type": "range_or_single",
            "data_type": "management_fee",
            "fields": ["min", "max", "value", "unit", "note", "is_undefined", "fee_type", "management_type", "work_style", "frequency"],
            "period_aware": has_period
        },
        clean_other_expenses_to_json: lambda: {
            "base_type": "array",
            "data_type": "other_expenses",
            "fields": ["expenses"],
            "expense_fields": ["type", "amount", "unit", "frequency", "note"],
            "period_aware": has_period
        },
        clean_access_to_json: generate_access_type_schema,
        clean_zoning_to_json: lambda: {
            "base_type": "array",
            "data_type": "zoning",
            "fields": ["zones"],
            "period_aware": has_period
        },
        clean_restrictions_to_json: lambda: {
            "base_type": "array",
            "data_type": "restrictions",
            "fields": ["restrictions"],
            "period_aware": has_period
        },
        clean_expiry_date_to_json: lambda: {
            "base_type": "single",
            "data_type": "expiry_date",
            "fields": ["date"],
            "period_aware": has_period
        },
        clean_company_info_to_json: lambda: {
            "base_type": "array",
            "data_type": "company_info",
            "fields": ["companies"],
            "company_fields": ["role", "name", "licenses", "construction_permits", "memberships", "postal_code", "address"],
            "period_aware": has_period
        },
        clean_utility_cost_to_json: generate_utility_cost_type_schema,
        clean_feature_pickup_to_json: generate_feature_pickup_type_schema,
        clean_reform_to_json: lambda: {
            "base_type": "single",
            "data_type": "reform_info",
            "fields": ["completion_date", "reform_areas", "note"],
            "period_aware": has_period
        },
        clean_building_structure_to_json: lambda: {
            "base_type": "single",
            "data_type": "building_structure_info",
            "fields": ["structure", "total_floors", "basement_floors", "note"],
            "period_aware": has_period
        },
        clean_parking_to_json: lambda: {
            "base_type": "parking_info",
            "data_type": "object",
            "required_fields": ["period"],
            "optional_fields": ["availability", "location", "value", "min", "max", "unit", "frequency", "note"],
            "period_aware": has_period
        },
        clean_force_null_to_json: lambda: {
            "base_type": "null",
            "data_type": "force_null",
            "fields": ["value"],
            "period_aware": has_period
        },
        clean_boolean_to_json: generate_boolean_type_schema,
        clean_text_to_json: generate_text_type_schema,
        clean_price_band_to_json: lambda: {
            "base_type": "range_or_single",
            "data_type": "price_band",
            "fields": ["values", "unit"],
            "value_fields": ["price", "count"],
            "period_aware": has_period
        },
        clean_surrounding_facilities_to_json: lambda: {
            "base_type": "array",
            "data_type": "surrounding_facilities",
            "fields": ["facilities"],
            "facility_fields": ["category", "name", "walking_time", "distance", "unit"],
            "period_aware": has_period
        },
    }
    
    # 最優先: 清浄化名ベースの特殊処理 (cleaned_nameがNoneの場合をスキップ)
    if cleaned_name and "所在階構造階建" in cleaned_name:
        return {
            "base_type": "structure_info", 
            "data_type": "object",
            "fields": ["floor", "structure", "total_floors", "basement_floors", "partial_structure", "note"],
            "period_aware": has_period
        }
    
    # 通常の関数ベース処理
    if processing_function in function_schema_mapping:
        schema_func = function_schema_mapping[processing_function]
        if callable(schema_func):
            return schema_func()
        else:
            return schema_func
    
    # デフォルトはテキスト型
    return generate_text_type_schema()