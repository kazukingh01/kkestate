"""
test_json_cleansing.py - JSON クレンジング機能のテスト
"""

import argparse
from kklogger import set_logger

# JSON クレンジング関数をインポート
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

# MST.py からすべてのテストケースをインポート
from .MST import (
    TEST_CASES_ADDRESS,
    TEST_CASES_ACCESS,
    TEST_CASES_UNITS1,
    TEST_CASES_UNITS2,
    TEST_CASES_ZONING,
    TEST_CASES_DATE1,
    TEST_CASES_DATE2,
    TEST_CASES_PRICE,
    TEST_CASES_PRICE_BAND,
    TEST_CASES_MANAGEMENT_FEE,
    TEST_CASES_MANAGEMENT_PREP_FEE,
    TEST_CASES_REPAIR_FUND,
    TEST_CASES_REPAIR_FUND_BASIC,
    TEST_CASES_OTHER_EXPENSES,
    TEST_CASES_LAYOUT,
    TEST_CASES_AREAS,
    TEST_CASES_RESTRICTIONS,
    TEST_CASES_DATE_EXACT,
    TEST_CASES_PRICE_MISC,
    TEST_CASES_PRICE_BAND_EXTRA,
    TEST_CASES_PRICE_BAND2,
    TEST_CASES_REPAIR_FUND_BASIC2,
    TEST_CASES_OTHER_EXPENSES2,
    TEST_CASES_LAYOUT2,
    TEST_CASES_AREA,
    TEST_CASES_DATE_EXACT2,
    TEST_CASES_DELIVERY_DATE,
    TEST_CASES_FLOOR,
    TEST_CASES_DIRECTION,
    TEST_CASES_FEATURE_PICKUP,
    TEST_CASES_BUILDING_STRUCTURE2,
    TEST_CASES_REFORM,
    TEST_CASES_SURROUNDING_FACILITIES,
    TEST_CASES_PARKING,
    TEST_CASES_BUILDING_STRUCTURE,
    TEST_CASES_LAND_USE,
    TEST_CASES_FLOOR_PLAN,
    TEST_CASES_BUILDING_COVERAGE
)

LOGGER = set_logger(__name__)

# テストケースと関数のマッピング
TEST_MAPPING = [
    # 住所関連
    ("TEST_CASES_ADDRESS", TEST_CASES_ADDRESS, clean_address_to_json),
    
    # 交通関連
    ("TEST_CASES_ACCESS", TEST_CASES_ACCESS, clean_access_to_json),
    
    # 戸数関連
    ("TEST_CASES_UNITS1", TEST_CASES_UNITS1, clean_units_to_json, "総戸数"),
    ("TEST_CASES_UNITS2", TEST_CASES_UNITS2, clean_units_to_json, "今回販売戸数"),
    
    # 用途地域関連
    ("TEST_CASES_ZONING", TEST_CASES_ZONING, clean_zoning_to_json),
    
    # 日付関連
    ("TEST_CASES_DATE1", TEST_CASES_DATE1, clean_date_to_json),
    ("TEST_CASES_DATE2", TEST_CASES_DATE2, clean_delivery_date_to_json),
    ("TEST_CASES_DATE_EXACT", TEST_CASES_DATE_EXACT, clean_expiry_date_to_json),
    ("TEST_CASES_DATE_EXACT2", TEST_CASES_DATE_EXACT2, clean_expiry_date_to_json),
    ("TEST_CASES_DELIVERY_DATE", TEST_CASES_DELIVERY_DATE, clean_delivery_date_to_json),
    
    # 価格関連
    ("TEST_CASES_PRICE", TEST_CASES_PRICE, clean_price_to_json),
    ("TEST_CASES_PRICE_MISC", TEST_CASES_PRICE_MISC, clean_price_to_json),
    ("TEST_CASES_PRICE_BAND", TEST_CASES_PRICE_BAND, clean_price_band_to_json),
    ("TEST_CASES_PRICE_BAND_EXTRA", TEST_CASES_PRICE_BAND_EXTRA, clean_price_band_to_json),
    ("TEST_CASES_PRICE_BAND2", TEST_CASES_PRICE_BAND2, clean_price_band_to_json),
    
    # 管理費関連
    ("TEST_CASES_MANAGEMENT_FEE", TEST_CASES_MANAGEMENT_FEE, clean_management_fee_to_json),
    ("TEST_CASES_MANAGEMENT_PREP_FEE", TEST_CASES_MANAGEMENT_PREP_FEE, clean_management_fee_to_json),
    ("TEST_CASES_REPAIR_FUND", TEST_CASES_REPAIR_FUND, clean_management_fee_to_json),
    ("TEST_CASES_REPAIR_FUND_BASIC", TEST_CASES_REPAIR_FUND_BASIC, clean_management_fee_to_json),
    ("TEST_CASES_REPAIR_FUND_BASIC2", TEST_CASES_REPAIR_FUND_BASIC2, clean_management_fee_to_json),
    
    # その他経費関連
    ("TEST_CASES_OTHER_EXPENSES", TEST_CASES_OTHER_EXPENSES, clean_other_expenses_to_json),
    ("TEST_CASES_OTHER_EXPENSES2", TEST_CASES_OTHER_EXPENSES2, clean_other_expenses_to_json),
    
    # 間取り関連
    ("TEST_CASES_LAYOUT", TEST_CASES_LAYOUT, clean_layout_to_json),
    ("TEST_CASES_LAYOUT2", TEST_CASES_LAYOUT2, clean_layout_to_json),
    
    # 面積関連
    ("TEST_CASES_AREAS", TEST_CASES_AREAS, clean_multiple_area_to_json),
    ("TEST_CASES_AREA", TEST_CASES_AREA, clean_area_to_json),
    
    # 制限事項関連
    ("TEST_CASES_RESTRICTIONS", TEST_CASES_RESTRICTIONS, clean_restrictions_to_json),
    
    # 階数・方向関連
    ("TEST_CASES_FLOOR", TEST_CASES_FLOOR, clean_number_to_json),
    ("TEST_CASES_DIRECTION", TEST_CASES_DIRECTION, clean_text_to_json),
    
    # 特徴ピックアップ関連  
    ("TEST_CASES_FEATURE_PICKUP", TEST_CASES_FEATURE_PICKUP, clean_feature_pickup_to_json),
    
    # 建物構造関連
    ("TEST_CASES_BUILDING_STRUCTURE", TEST_CASES_BUILDING_STRUCTURE, clean_building_structure_to_json),
    ("TEST_CASES_BUILDING_STRUCTURE2", TEST_CASES_BUILDING_STRUCTURE2, clean_building_structure_to_json),
    
    # リフォーム関連
    ("TEST_CASES_REFORM", TEST_CASES_REFORM, clean_reform_to_json),
    
    # 周辺施設関連
    ("TEST_CASES_SURROUNDING_FACILITIES", TEST_CASES_SURROUNDING_FACILITIES, clean_surrounding_facilities_to_json),
    
    # 駐車場関連
    ("TEST_CASES_PARKING", TEST_CASES_PARKING, clean_parking_to_json),
    
    # 地目関連
    ("TEST_CASES_LAND_USE", TEST_CASES_LAND_USE, clean_land_use_to_json),
    
    # 間取り図関連
    ("TEST_CASES_FLOOR_PLAN", TEST_CASES_FLOOR_PLAN, clean_floor_plan_to_json),
    
    # 建ぺい率・容積率関連
    ("TEST_CASES_BUILDING_COVERAGE", TEST_CASES_BUILDING_COVERAGE, clean_building_coverage_to_json),
]

def run_json_cleansing_tests():
    """
    全てのJSONクレンジング機能のテストを実行
    """
    total_tests = 0
    failed_tests = 0
    
    for test_mapping_item in TEST_MAPPING:
        if len(test_mapping_item) == 4:
            test_name, test_cases, clean_function, raw_key = test_mapping_item
        else:
            test_name, test_cases, clean_function = test_mapping_item
            raw_key = None
        LOGGER.info(f"Testing {test_name} with {clean_function.__name__}")
        
        for i, test_case in enumerate(test_cases):
            total_tests += 1
            input_value = test_case["input"]
            expected_result = test_case["expected"]
            
            try:
                # クレンジング関数を実行
                # 関数によって引数が異なる場合の対応
                if clean_function.__name__ in ['clean_units_to_json']:
                    # raw_keyが必要な関数の場合（テストマッピングからraw_keyを取得）
                    actual_result = clean_function(input_value, raw_key=raw_key or "総戸数")
                elif clean_function.__name__ in ['clean_utility_cost_to_json']:
                    # raw_keyがオプションの関数の場合
                    actual_result = clean_function(input_value, raw_key="目安光熱費")
                elif clean_function.__name__ in ['clean_price_band_to_json']:
                    # price_bandにraw_keyが必要な関数の場合
                    actual_result = clean_function(input_value, raw_key="最多価格帯")
                else:
                    # 通常の関数
                    actual_result = clean_function(input_value)
                
                # 結果を比較
                if actual_result != expected_result:
                    failed_tests += 1
                    LOGGER.info(f"  FAIL: {test_name}[{i}] '{input_value}'", color=["BOLD", "RED"])
                    LOGGER.info(f"    Expected: {expected_result}")
                    LOGGER.info(f"    Actual:   {actual_result}")
                # PASSした場合は何も出力しない
                    
            except Exception as e:
                failed_tests += 1
                LOGGER.info(f"  ERROR: {test_name}[{i}] '{input_value}': {e}", color=["BOLD", "RED"])
    
    # 結果サマリー
    passed_tests = total_tests - failed_tests
    LOGGER.info(f"Test Summary: {passed_tests}/{total_tests} passed, {failed_tests} failed", 
                color=["BOLD", "GREEN"] if failed_tests == 0 else ["BOLD", "RED"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    LOGGER.info(f"{args}")
    
    # JSONクレンジングテストを実行
    run_json_cleansing_tests()