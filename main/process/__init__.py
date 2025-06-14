"""
不動産データ処理モジュール

このモジュールは以下の機能を提供します:
- estate_detailテーブルからの生データ取得
- kkestate.utilのクレンジング機能を使用したデータ処理
- estate_cleanedテーブルへの保存

主なクラス:
- EstateProcessor: データ処理のメインクラス

注記:
データクレンジング機能は kkestate.util.cleansing に配置されています.
キーマッピング機能は kkestate.util.key_mapping に配置されています.
"""

from .processor import EstateProcessor

__all__ = [
    'EstateProcessor'
]