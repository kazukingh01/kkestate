"""
test_json_cleansing.py - JSON クレンジング機能のテスト
"""

import argparse
from kklogger import set_logger
from .MST import TEST_MAPPING

LOGGER = set_logger(__name__)

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