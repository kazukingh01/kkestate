import argparse
from kklogger import set_logger
from kkestate.util.key_processing_mapper import get_processing_info_for_key
from .MST import EXPECTED_KEY_PROCESSING
LOGGER = set_logger(__name__)


def test_key_processing():
    """get_processing_info_for_key の結果が期待値と一致するかテスト"""
    failed_tests = []
    
    for i, expected in enumerate(EXPECTED_KEY_PROCESSING):
        key_name = expected["key_name"]
        expected_cleaned_name = expected["expected_cleaned_name"]
        expected_function = expected["expected_function"]
        
        try:
            # 実際の処理結果を取得
            actual_cleaned_name, actual_function, _ = get_processing_info_for_key(key_name)
            
            # cleaned_name のチェック
            if actual_cleaned_name != expected_cleaned_name:
                failed_tests.append({
                    "index": i,
                    "key_name": key_name,
                    "type": "cleaned_name",
                    "expected": expected_cleaned_name,
                    "actual": actual_cleaned_name
                })
            
            # function のチェック
            if actual_function != expected_function:
                failed_tests.append({
                    "index": i,
                    "key_name": key_name,
                    "type": "function",
                    "expected": expected_function.__name__ if expected_function else None,
                    "actual": actual_function.__name__ if actual_function else None
                })
        
        except Exception as e:
            failed_tests.append({
                "index": i,
                "key_name": key_name,
                "type": "error",
                "error": str(e)
            })
    
    # 結果を出力
    if failed_tests:
        LOGGER.info(f"失敗したテスト数: {len(failed_tests)}", color=["BOLD", "RED"])
        for fail in failed_tests:
            if fail["type"] == "error":
                LOGGER.info(f"  [{fail['index']}] {fail['key_name']}: エラー - {fail['error']}")
            else:
                LOGGER.info(f"  [{fail['index']}] {fail['key_name']}: {fail['type']} - 期待値: {fail['expected']}, 実際: {fail['actual']}")
    else:
        LOGGER.info(f"すべてのテスト ({len(EXPECTED_KEY_PROCESSING)}件) が成功しました. ", color=["BOLD", "GREEN"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    LOGGER.info(f"{args}")
    
    test_key_processing()