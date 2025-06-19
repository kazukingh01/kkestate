"""
キー処理の統合マッピング - estate_mst_key.nameから処理関数、清浄化名、型スキーマを決定
"""

import re
from typing import Tuple, Callable, Dict, Any, Optional
from .schema_generator import generate_type_schema_from_function
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
    clean_land_use_to_json, clean_floor_plan_to_json,
    clean_building_coverage_to_json
)

def get_processing_info_for_key(key_name: str) -> Tuple[str, Callable, Dict[str, Any]]:
    """
    キー名から処理関数、清浄化名、型スキーマを取得（統合関数）
    
    Args:
        key_name: estate_mst_key.name
        
    Returns:
        Tuple[str, Callable, Dict[str, Any]]: (cleaned_name, processing_function, type_schema)
    """
    # 期別情報の判定
    has_period = "_第" in key_name
    
    # 処理関数と清浄化名を取得
    cleaned_name, processing_function = map_key_to_processing_info(key_name)
    
    # 型スキーマを取得
    type_schema = generate_type_schema_from_function(processing_function, cleaned_name, has_period)
    
    return cleaned_name, processing_function, type_schema

def map_key_to_processing_info(key_name: str) -> Tuple[str, Callable]:
    """
    estate_mst_key.name から estate_mst_cleaned.name と処理関数を決定
    
    Args:
        key_name: estate_mst_key.name (例: "特徴ピックアップ", "価格_第4期")
        
    Returns:
        Tuple[str, Callable]: (cleaned_name, processing_function)
    """
    # 期別情報を除去してベースキーを取得
    phase_match = re.search(r'_第(\d+)期$', key_name)
    base_key = key_name.replace(phase_match.group(0), '') if phase_match else key_name
    
    # 確定的なマッピング定義
    key_function_mapping = {
        # 住所関連 -> clean_address_to_json
        "所在地": ("住所", clean_address_to_json),
        "住所": ("住所", clean_address_to_json),
        "物件所在地": ("住所", clean_address_to_json),
        "現地案内所": ("住所", clean_address_to_json),
        "モデルルーム": ("住所", clean_address_to_json),
        
        # 交通関連 -> clean_access_to_json
        "交通": ("交通", clean_access_to_json),  # 期待値に合わせて "交通アクセス" -> "交通" に変更
        
        # 価格関連 -> clean_price_to_json
        "価格": ("価格", clean_price_to_json),
        "予定価格": ("価格", clean_price_to_json),
        
        # 価格帯関連 -> clean_price_band_to_json
        "最多価格帯": ("価格帯", clean_price_band_to_json),
        "予定最多価格帯": ("価格帯", clean_price_band_to_json),
        "予定価格帯": ("価格帯", clean_price_band_to_json),
        
        # 面積関連
        "専有面積": ("専有面積", clean_area_to_json),
        "その他面積": ("その他面積", clean_multiple_area_to_json),
        "バルコニー面積": ("その他面積", clean_multiple_area_to_json),
        "土地面積": ("土地面積", clean_area_to_json),
        "建物面積": ("建物面積", clean_area_to_json),
        "敷地面積": ("土地面積", clean_area_to_json),
        
        # 間取り関連 -> clean_layout_to_json
        "間取り": ("間取り", clean_layout_to_json),
        
        # 日付関連
        "完成時期": ("築年月", clean_date_to_json),
        "引渡時期": ("引渡時期", clean_delivery_date_to_json),
        "引渡可能時期": ("引渡時期", clean_delivery_date_to_json),
        "引き渡し時期": ("引渡時期", clean_delivery_date_to_json),
        "築年月": ("築年月", clean_date_to_json),
        "建築年月": ("築年月", clean_date_to_json),
        "完成時期（築年月）": ("築年月", clean_date_to_json),
        "完成時期(築年月)": ("築年月", clean_date_to_json),
        "造成完了時期": ("築年月", clean_date_to_json),
        
        # 戸数関連 -> clean_units_to_json
        "総戸数": ("戸数", clean_units_to_json),
        "今回販売戸数": ("戸数", clean_units_to_json),
        "販売戸数": ("戸数", clean_units_to_json),
        "販売区画数": ("戸数", clean_units_to_json),
        "総区画数": ("戸数", clean_units_to_json),
        
        # 階数関連 -> clean_number_to_json
        "建物階数": ("階数", clean_number_to_json),
        "所在階": ("所在階", clean_number_to_json),
        "向き": ("向き", clean_text_to_json),
        
        # 管理費関連 -> clean_management_fee_to_json
        "管理費": ("管理費", clean_management_fee_to_json),
        "修繕積立金": ("修繕積立金", clean_management_fee_to_json),
        "修繕積立基金": ("修繕積立基金", clean_management_fee_to_json),
        "管理準備金": ("管理準備金", clean_management_fee_to_json),
        
        # その他諸経費 -> clean_other_expenses_to_json
        "その他諸経費": ("他経費", clean_other_expenses_to_json),
        "他諸経費": ("他経費", clean_other_expenses_to_json),
        "他経費": ("他経費", clean_other_expenses_to_json),
        "諸費用": ("他経費", clean_other_expenses_to_json),
        
        # 交通アクセス -> clean_access_to_json (既に上で定義済み)
        "交通アクセス": ("交通アクセス", clean_access_to_json),
        
        # 用途地域 -> clean_zoning_to_json
        "用途地域": ("用途地域", clean_zoning_to_json),
        
        # 制限事項 -> clean_restrictions_to_json
        "制限事項": ("制限事項", clean_restrictions_to_json),
        "その他制限事項": ("制限事項", clean_restrictions_to_json),
        
        # 取引条件有効期限 -> clean_expiry_date_to_json
        "取引条件有効期限": ("取引条件有効期限", clean_expiry_date_to_json),
        
        # 会社情報 -> clean_company_info_to_json
        "会社情報": ("会社情報", clean_company_info_to_json),
        "会社概要": (None, clean_force_null_to_json),
        
        # 光熱費 -> clean_utility_cost_to_json
        "目安光熱費": ("目安光熱費", clean_utility_cost_to_json),
        
        # 特徴ピックアップ -> clean_feature_pickup_to_json
        "特徴ピックアップ": ("特徴", clean_feature_pickup_to_json),
        "物件の特徴": (None, clean_force_null_to_json),
        
        # リフォーム -> clean_reform_to_json
        "リフォーム": ("リフォーム", clean_reform_to_json),
        
        # 建物構造 -> clean_building_structure_to_json
        "構造・階建て": ("構造階建", clean_building_structure_to_json),
        "構造・工法": ("構造階建", clean_building_structure_to_json),
        
        # 駐車場 -> clean_parking_to_json
        "駐車場": ("駐車場", clean_parking_to_json),
        
        # 特殊構造データ（所在階/構造・階建は専用パーサー使用）
        "所在階/構造・階建": ("構造階建", clean_building_structure_to_json),
        
        # 強制null処理 -> clean_force_null_to_json (期待値でNoneとされている項目)
        "敷地権利形態": ("敷地権利形態", clean_force_null_to_json),
        "敷地の権利形態": (None, clean_force_null_to_json),
        "土地の権利形態": (None, clean_force_null_to_json),
        "販売スケジュール": (None, clean_force_null_to_json),
        "関連リンク": (None, clean_force_null_to_json),
        "お問い合せ先": (None, clean_force_null_to_json),
        "問い合わせ先": (None, clean_force_null_to_json),
        "周辺施設": (None, clean_force_null_to_json),
        "周辺環境": ("周辺施設", clean_surrounding_facilities_to_json),
        "イベント情報": (None, clean_force_null_to_json),
        "その他概要・特記事項": (None, clean_force_null_to_json),
        "情報提供日": (None, clean_force_null_to_json),
        "次回更新日": (None, clean_force_null_to_json),
        "担当者より": (None, clean_force_null_to_json),
        "プレゼント情報": (None, clean_force_null_to_json),
        "お知らせ／その他": (None, clean_force_null_to_json),
        "カーナビご利用の方": (None, clean_force_null_to_json),
        "見学可能な日程": (None, clean_force_null_to_json),
        "間取り図": ("間取り図", clean_floor_plan_to_json),
        
        # その他のテキスト項目
        "その他": ("その他", clean_text_to_json),
        "物件名": ("物件名", clean_text_to_json),
        "施工": ("施工会社", clean_text_to_json),
        "施工\n": ("施工会社", clean_text_to_json),
        "管理": ("管理会社", clean_text_to_json),
        "不動産会社ガイド": (None, clean_force_null_to_json),
        "物件番号": ("物件番号", clean_text_to_json),
        "取引態様": ("取引態様", clean_text_to_json),
        "地目": ("地目", clean_land_use_to_json),
        "私道負担・道路": (None, clean_force_null_to_json),
        "建ぺい率・容積率": ("建ぺい率容積率", clean_building_coverage_to_json),
        "建ぺい率･容積率": ("建ぺい率容積率", clean_building_coverage_to_json),
        "土地状況": ("土地状況", clean_text_to_json),
        "建築条件": (None, clean_force_null_to_json),
        "エネルギー消費性能": (None, clean_force_null_to_json),
        "断熱性能": (None, clean_force_null_to_json),
    }
    
    # ヒント系は強制null (期待値に合わせてNone)
    if " ヒント" in base_key:
        return (None, clean_force_null_to_json)
    
    # 特別な条件: 期別付きの「その他」はforce_null、基本の「その他」と「会社情報」も同様
    if base_key == "その他":
        return (None, clean_force_null_to_json)
    elif base_key == "会社情報" and phase_match is None:
        return (None, clean_force_null_to_json)
    
    # 直接マッピングがあるかチェック
    if base_key in key_function_mapping:
        return key_function_mapping[base_key]
    
    # パターンマッチング（フォールバック）
    if "価格" in base_key:
        return ("価格", clean_price_to_json)
    elif "面積" in base_key:
        if "その他" in base_key or "バルコニー" in base_key:
            return ("その他面積", clean_multiple_area_to_json)
        else:
            return ("面積", clean_area_to_json)
    elif "間取り" in base_key:
        return ("間取り", clean_layout_to_json)
    elif any(word in base_key for word in ["時期", "年月", "完成", "竣工", "築年", "建築年"]):
        if "引渡" in base_key:
            return ("引渡時期", clean_delivery_date_to_json)
        else:
            return ("完成時期", clean_date_to_json)
    elif "戸数" in base_key or "区画" in base_key:
        return ("戸数", clean_units_to_json)
    elif "準備金" in base_key:
        return ("管理費", clean_management_fee_to_json)
    elif any(word in base_key for word in ["管理費", "積立"]):
        return ("管理費", clean_management_fee_to_json)
    elif "階" in base_key and ("所在" in base_key or "建物" in base_key):
        return ("階数", clean_number_to_json)
    elif "交通" in base_key:
        return ("交通", clean_access_to_json)
    elif "制限" in base_key:
        return ("制限事項", clean_restrictions_to_json)
    elif "会社" in base_key:
        return ("会社情報", clean_company_info_to_json)
    
    # デフォルトはテキスト処理
    normalized_name = _normalize_key_name(base_key)
    return (normalized_name, clean_text_to_json)

def _normalize_key_name(key: str) -> str:
    """
    キー名を正規化（日本語をそのまま使用）
    """
    # 特殊文字を除去し、スペースをアンダースコアに
    normalized = re.sub(r'[^\w\s]', '', key)
    normalized = re.sub(r'\s+', '_', normalized)
    return normalized