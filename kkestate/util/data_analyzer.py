"""
実データに基づくクレンジング項目名と型の決定ロジック
"""

import re
from typing import Dict, Tuple, Optional, Any
from .json_cleaner import create_type_schema

def analyze_key_and_data(key_name: str, sample_values: list) -> Tuple[str, Dict[str, Any]]:
    """
    キー名とサンプルデータから、クレンジング済み項目名と型を決定する
    
    Args:
        key_name: estate_mst_keyのname
        sample_values: そのキーに対応するestate_detailのvalueのサンプル
        
    Returns:
        (cleaned_name, type_schema): クレンジング済み項目名と型スキーマ
    """
    
    # 期別情報を処理
    phase_match = re.search(r'_第(\d+)期$', key_name)
    base_key = key_name.replace(phase_match.group(0), '') if phase_match else key_name
    phase_suffix = f"_第{phase_match.group(1)}期" if phase_match else ""
    
    # 基本キーのマッピング
    key_mappings = {
        # 所在地・住所
        "所在地": ("住所", "text"),
        
        # 交通アクセス
        "交通": ("交通アクセス", "text"),
        
        # 価格関連
        "価格": ("価格", "text"),
        "予定価格": ("予定価格", "text"),
        "最多価格帯": ("価格", "text"),
        "予定最多価格帯": ("予定最多価格帯", "text"),
        "予定価格帯": ("予定価格帯", "text"),
        
        # 管理費関連
        "管理費": ("管理費", "text"),
        "管理準備金": ("管理準備金", "text"),
        "修繕積立金": ("修繕積立金", "text"),
        "修繕積立基金": ("修繕積立基金", "text"),
        "その他諸経費": ("その他諸経費", "text"),
        
        # 物件仕様
        "間取り": ("間取り", "text"),
        "専有面積": ("専有面積", "text"),
        "その他面積": ("その他面積", "text"),
        "バルコニー面積": ("バルコニー面積", "text"),
        
        # 建物情報
        "総戸数": ("戸数", "text"),
        "今回販売戸数": ("戸数", "text"),
        "構造・階建": ("構造階建", "text"),
        "建物階": ("建物階数", "text"),
        "階": ("所在階", "text"),
        "向き": ("向き", "text"),
        "築年月": ("築年月", "text"),
        "建築年月": ("建築年月", "text"),
        
        # 日程
        "完成時期": ("完成時期", "text"),
        "引渡可能時期": ("引渡時期", "text"),
        "販売スケジュール": ("販売スケジュール", "text"),
        
        # 土地情報
        "用途地域": ("用途地域", "text"),
        "敷地の権利形態": ("敷地権利形態", "text"),
        "土地面積": ("土地面積", "text"),
        "建物面積": ("建物面積", "text"),
        "建ぺい率・容積率": ("建ぺい率容積率", "text"),
        "私道負担・道路": ("私道負担道路", "text"),
        "接道状況": ("接道状況", "text"),
        "地目": ("地目", "text"),
        "権利": ("権利", "text"),
        "現況": ("現況", "text"),
        
        # 設備・条件
        "駐車場": ("駐車場", "text"),
        "設備・サービス": ("設備サービス", "text"),
        "条件": ("条件", "text"),
        "備考": ("備考", "text"),
        "制限事項": ("制限事項", "text"),
        
        # 管理・施工情報
        "管理": ("管理会社", "text"),
        "施工": ("施工会社", "text"),
        "会社情報": ("会社情報", "text"),
        "不動産会社ガイド": ("不動産会社ガイド", "text"),
        
        # その他
        "その他": ("その他", "text"),
        "取引条件有効期限": ("取引条件有効期限", "text"),
        "物件番号": ("物件番号", "text"),
        "取引態様": ("取引態様", "text"),
        "情報公開日": ("情報公開日", "text"),
        "次回更新予定日": ("次回更新予定日", "text"),
    }
    
    # マッピングから取得（期別情報は cleaned_name に含めない）
    if base_key in key_mappings:
        cleaned_name, _ = key_mappings[base_key]  # 型は使わない
        final_cleaned_name = cleaned_name  # 期別情報は含めない
    else:
        # マッピングにない場合は、キー名を正規化
        cleaned_name = _normalize_key_name(base_key)
        final_cleaned_name = cleaned_name  # 期別情報は含めない
    
    # サンプルデータから型スキーマを生成
    type_schema = create_type_schema(key_name, sample_values)
    
    return final_cleaned_name, type_schema

def _normalize_key_name(key: str) -> str:
    """
    キー名を正規化（日本語をそのまま使用）
    """
    # 特殊文字を除去し、スペースをアンダースコアに
    normalized = re.sub(r'[^\w\s]', '', key)
    normalized = re.sub(r'\s+', '_', normalized)
    return normalized

def _guess_value_type(sample_values: list) -> str:
    """
    サンプルデータから型を推測
    """
    if not sample_values:
        return "text"
    
    # 空でない値のみを対象
    non_empty_values = [v for v in sample_values if v and v.strip()]
    if not non_empty_values:
        return "text"
    
    # 数値パターンチェック
    numeric_count = 0
    for value in non_empty_values[:10]:  # 最初の10件をチェック
        # 純粋な数値
        if re.match(r'^\d+$', value.strip()):
            numeric_count += 1
        # 小数点付き数値
        elif re.match(r'^\d+\.\d+$', value.strip()):
            numeric_count += 1
    
    # 過半数が数値なら数値型
    if numeric_count > len(non_empty_values[:10]) * 0.7:
        # 小数点があるかチェック
        has_decimal = any('.' in str(v) for v in non_empty_values[:5])
        return "float" if has_decimal else "int"
    
    # Boolean パターンチェック
    boolean_count = 0
    for value in non_empty_values[:10]:
        if any(word in value for word in ["有", "無", "あり", "なし", "可", "不可", "○", "×", "-"]):
            boolean_count += 1
    
    if boolean_count > len(non_empty_values[:10]) * 0.7:
        return "boolean"
    
    # JSON構造がありそうかチェック（複雑なデータ）
    complex_count = 0
    for value in non_empty_values[:5]:
        # 範囲表現、複数値、単位付きなど
        if any(pattern in value for pattern in ["～", "・", "円", "m2", "㎡", "分", "駅", "戸", "階"]):
            complex_count += 1
    
    if complex_count > len(non_empty_values[:5]) * 0.6:
        return "json"
    
    return "text"

def get_sample_data(db, key_id: int, limit: Optional[int] = 100) -> list:
    """
    指定されたkey_idのサンプルデータを取得
    """
    try:
        base_sql = f"""
            SELECT value 
            FROM estate_detail 
            WHERE id_key = {key_id} 
            AND value IS NOT NULL 
            AND value != ''
        """
        
        if limit is not None:
            sql = base_sql + f" LIMIT {limit}"
        else:
            sql = base_sql + " LIMIT 10000"  # --allフラグ使用時はLIMIT 10000
        
        df = db.select_sql(sql)
        return df['value'].tolist() if not df.empty else []
    except Exception:
        return []