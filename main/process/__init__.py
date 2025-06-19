"""
不動産データ処理モジュール

このモジュールは以下の機能を提供します:
- estate_detailテーブルからの生データ取得
- kkestate.utilのクレンジング機能を使用したデータ処理
- estate_cleanedテーブルへの保存

主なスクリプト:
- process_estate.py: データ処理のメインスクリプト

注記:
データクレンジング機能は kkestate.util.json_cleaner に配置されています.
キーマッピング機能は kkestate.util.key_mapper に配置されています.
"""

__all__ = []