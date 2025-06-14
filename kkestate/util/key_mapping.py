"""
estate_mst_key の name から name_cleaned へのマッピング定義
共通ユーティリティ関数
"""

KEY_MAPPING = {
    # 基本情報
    "所在地": "address",
    "交通": "access",
    "総戸数": "total_units",
    "用途地域": "zoning",
    "敷地の権利形態": "land_rights",
    
    # 販売情報
    "販売スケジュール": "sales_schedule",
    "完成時期": "completion_date",
    "引渡可能時期": "delivery_date",
    "今回販売戸数": "units_for_sale",
    
    # 価格情報
    "価格": "price",
    "予定価格": "planned_price",
    "最多価格帯": "most_common_price_range",
    "予定最多価格帯": "planned_price",
    "予定価格帯": "planned_price",
    
    # 管理費関連
    "管理費": "management_fee",
    "管理準備金": "management_reserve",
    "修繕積立金": "repair_fund",
    "修繕積立基金": "repair_reserve",
    "その他諸経費": "other_expenses",
    
    # 物件詳細
    "間取り": "layout",
    "専有面積": "exclusive_area",
    "その他面積": "other_area",
    "バルコニー面積": "balcony_area",
    
    # 建物情報
    "構造・階建": "structure",
    "建物階": "building_floors",
    "階": "floor",
    "向き": "direction",
    "築年月": "built_date",
    "建築年月": "construction_date",
    
    # 土地情報
    "土地面積": "land_area",
    "建物面積": "building_area",
    "建ぺい率・容積率": "coverage_ratio",
    "私道負担・道路": "road_burden",
    "接道状況": "road_access",
    "地目": "land_category",
    "権利": "rights",
    "現況": "current_status",
    
    # 設備・条件
    "駐車場": "parking",
    "設備・サービス": "facilities",
    "条件": "conditions",
    "備考": "remarks",
    "制限事項": "restrictions",
    
    # 管理・施工情報
    "管理": "management_company",
    "施工": "construction_company",
    "会社情報": "company_info",
    "不動産会社ガイド": "real_estate_guide",
    
    # その他
    "その他": "other",
    "取引条件有効期限": "transaction_validity",
    "物件番号": "property_number",
    "取引態様": "transaction_type",
    "情報公開日": "publication_date",
    "次回更新予定日": "next_update_date",
}

def map_phase_key(key: str) -> str:
    """
    第n期のような期別情報を含むキーを処理する
    例: "価格_第5期" -> "price_phase5"
    """
    import re
    
    # 期別情報を抽出
    phase_match = re.search(r'_第(\d+)期$', key)
    if phase_match:
        base_key = key.replace(phase_match.group(0), '')
        phase_num = phase_match.group(1)
        
        # 基本キーのマッピングを取得
        if base_key in KEY_MAPPING:
            return f"{KEY_MAPPING[base_key]}_phase{phase_num}"
        else:
            # マッピングがない場合は、キーを正規化して返す
            normalized = base_key.lower().replace(' ', '_')
            return f"{normalized}_phase{phase_num}"
    
    # 期別情報がない場合は通常のマッピング
    return KEY_MAPPING.get(key, key.lower().replace(' ', '_'))

def get_cleaned_name(raw_name: str) -> str:
    """
    生のキー名からクレンジング済みのキー名を取得する
    """
    # まず期別情報を含むキーの処理を試みる
    cleaned = map_phase_key(raw_name)
    
    # 日本語文字が残っている場合は、アンダースコアで置換
    import re
    if re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', cleaned):
        # 未マッピングのキーは小文字化してスペースをアンダースコアに
        cleaned = raw_name.lower()
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        cleaned = re.sub(r'\s+', '_', cleaned)
    
    return cleaned