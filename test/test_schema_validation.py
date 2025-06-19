"""
test_schema_validation.py - estate_mst_cleaned/type のスキーマ検証テスト
"""

import argparse
from kklogger import set_logger
from .MST import TEST_MAPPING, EXPECTED_KEY_PROCESSING, EXPECTED_SCHEMAS
from kkestate.util.key_mapper import get_processing_info_for_key

LOGGER = set_logger(__name__)

def get_cleaned_name_for_function(function_name: str, raw_key: str = "") -> str:
    """
    関数名とraw_keyからcleaned_nameを取得
    """
    for entry in EXPECTED_KEY_PROCESSING:
        if (entry["expected_function"].__name__ == function_name and
            (not raw_key or entry["key_name"] == raw_key)):
            return entry["expected_cleaned_name"]
    return None

def validate_json_output_schema(output_json: dict, cleaned_name: str) -> tuple[bool, str]:
    """
    JSON出力が期待されるスキーマに合致するかを検証
    
    Args:
        output_json (dict): 関数の出力JSON
        cleaned_name (str): クレンジング済み項目名
        
    Returns:
        tuple[bool, str]: (検証結果, エラーメッセージ)
    """
    if cleaned_name is None or cleaned_name not in EXPECTED_SCHEMAS:
        return True, ""  # スキーマが定義されていない場合は検証しない
    
    schema = EXPECTED_SCHEMAS[cleaned_name]
    expected_fields = set(schema.get("required_fields", []) + schema.get("optional_fields", []))
    actual_fields = set(output_json.keys())
    
    # 実際の出力にあるがスキーマに定義されていないフィールドをチェック
    undefined_fields = actual_fields - expected_fields
    if undefined_fields:
        LOGGER.warning(f"WARNING: {cleaned_name} - スキーマに未定義のフィールド: {sorted(undefined_fields)}")
        LOGGER.warning(f"  実際の出力: {output_json}")
    
    # 必須フィールドの確認
    for field in schema["required_fields"]:
        if field not in output_json:
            return False, f"必須フィールド '{field}' が見つかりません"
    
    # フィールドの型確認
    for field, value in output_json.items():
        if field in schema["field_types"]:
            expected_types = schema["field_types"][field]
            if not isinstance(expected_types, list):
                expected_types = [expected_types]
            
            if not any(isinstance(value, t) for t in expected_types):
                return False, f"フィールド '{field}' の型が不正です。期待: {expected_types}, 実際: {type(value)}"
    
    return True, ""

def test_type_schema_consistency():
    """
    get_processing_info_for_keyが返すtype_schemaがEXPECTED_SCHEMASと一致するかテスト
    """
    total_tests = 0
    failed_tests = 0
    
    LOGGER.info("Testing type_schema consistency with EXPECTED_SCHEMAS")
    
    # EXPECTED_KEY_PROCESSINGの各項目についてテスト
    for entry in EXPECTED_KEY_PROCESSING:
        key_name = entry["key_name"]
        expected_cleaned_name = entry["expected_cleaned_name"]
        
        # 強制null項目はスキップ
        if expected_cleaned_name is None:
            continue
            
        total_tests += 1
        
        try:
            # get_processing_info_for_keyから実際のスキーマを取得
            actual_cleaned_name, processing_function, actual_type_schema = get_processing_info_for_key(key_name)
            
            # cleaned_nameが一致するかチェック
            if actual_cleaned_name != expected_cleaned_name:
                failed_tests += 1
                LOGGER.info(f"  FAIL: {key_name} - cleaned_name不一致", color=["BOLD", "RED"])
                LOGGER.info(f"    Expected: {expected_cleaned_name}")
                LOGGER.info(f"    Actual: {actual_cleaned_name}")
                continue
            
            # EXPECTED_SCHEMASに定義があるかチェック
            if expected_cleaned_name not in EXPECTED_SCHEMAS:
                LOGGER.info(f"  SKIP: {key_name} -> {expected_cleaned_name} (EXPECTED_SCHEMASに未定義)")
                total_tests -= 1
                continue
                
            expected_schema = EXPECTED_SCHEMAS[expected_cleaned_name]
            
            # type_schemaの比較
            schema_matches = True
            error_details = []
            
            # required_fieldsの比較
            expected_required = set(expected_schema.get("required_fields", []))
            actual_required = set(actual_type_schema.get("required_fields", []))
            if expected_required != actual_required:
                schema_matches = False
                error_details.append(f"required_fields不一致: expected={sorted(expected_required)}, actual={sorted(actual_required)}")
            
            # optional_fieldsの比較
            expected_optional = set(expected_schema.get("optional_fields", []))
            actual_optional = set(actual_type_schema.get("optional_fields", []))
            if expected_optional != actual_optional:
                schema_matches = False
                error_details.append(f"optional_fields不一致: expected={sorted(expected_optional)}, actual={sorted(actual_optional)}")
            
            if not schema_matches:
                failed_tests += 1
                LOGGER.info(f"  FAIL: {key_name} -> {expected_cleaned_name} - type_schema不一致", color=["BOLD", "RED"])
                for detail in error_details:
                    LOGGER.info(f"    {detail}")
                LOGGER.info(f"    Expected schema: {expected_schema}")
                LOGGER.info(f"    Actual schema: {actual_type_schema}")
            
        except Exception as e:
            failed_tests += 1
            LOGGER.info(f"  ERROR: {key_name}: {e}", color=["BOLD", "RED"])
    
    # 結果サマリー
    passed_tests = total_tests - failed_tests
    LOGGER.info(f"Type Schema Consistency Summary: {passed_tests}/{total_tests} passed, {failed_tests} failed", 
                color=["BOLD", "GREEN"] if failed_tests == 0 else ["BOLD", "RED"])
    
    return failed_tests == 0

def run_schema_validation_tests():
    """
    実際のテストデータを使用してJSON出力のスキーマ検証を実行
    """
    total_tests = 0
    failed_tests = 0
    
    for test_mapping_item in TEST_MAPPING:
        if len(test_mapping_item) == 4:
            test_name, test_cases, clean_function, raw_key = test_mapping_item
        else:
            test_name, test_cases, clean_function = test_mapping_item
            raw_key = None
        
        # 関数名からcleaned_nameを取得
        cleaned_name = get_cleaned_name_for_function(clean_function.__name__, raw_key or "")
        
        if cleaned_name is None:
            continue  # スキーマ検証対象外
        
        LOGGER.info(f"Testing schema for {test_name} -> {cleaned_name}")
        
        for i, test_case in enumerate(test_cases):
            total_tests += 1
            input_value = test_case["input"]
            
            try:
                # クレンジング関数を実行
                if clean_function.__name__ in ['clean_units_to_json']:
                    actual_result = clean_function(input_value, raw_key=raw_key or "総戸数")
                elif clean_function.__name__ in ['clean_utility_cost_to_json']:
                    actual_result = clean_function(input_value, raw_key="目安光熱費")
                elif clean_function.__name__ in ['clean_price_band_to_json']:
                    actual_result = clean_function(input_value, raw_key="最多価格帯")
                else:
                    actual_result = clean_function(input_value)
                
                # スキーマ検証
                is_valid, error_msg = validate_json_output_schema(actual_result, cleaned_name)
                
                if not is_valid:
                    failed_tests += 1
                    LOGGER.info(f"  FAIL: {test_name}[{i}] '{input_value}'", color=["BOLD", "RED"])
                    LOGGER.info(f"    Schema Error: {error_msg}")
                    LOGGER.info(f"    Output: {actual_result}")
                    
            except Exception as e:
                failed_tests += 1
                LOGGER.info(f"  ERROR: {test_name}[{i}] '{input_value}': {e}", color=["BOLD", "RED"])
    
    # 結果サマリー
    passed_tests = total_tests - failed_tests
    LOGGER.info(f"Schema Validation Summary: {passed_tests}/{total_tests} passed, {failed_tests} failed", 
                color=["BOLD", "GREEN"] if failed_tests == 0 else ["BOLD", "RED"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    LOGGER.info(f"{args}")
    
    # type_schemaの一致性テストを実行
    type_schema_success = test_type_schema_consistency()
    
    # スキーマ検証テストを実行
    run_schema_validation_tests()
    
    # type_schemaテストが失敗した場合は終了コードで知らせる
    if not type_schema_success:
        import sys
        sys.exit(1)