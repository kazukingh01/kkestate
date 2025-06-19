"""
統合パーサーモジュール
すべての個別パーサーの機能を一つのファイルに統合

このモジュールには以下のパーサーが含まれています:
- 住所パーサー (address_parser)
- 建物構造パーサー (structure_parser, building_structure_parser)
- リフォームパーサー (reform_parser)
- 地目パーサー (land_use_parser)
- 周辺施設パーサー (surrounding_facilities_parser)
- 駐車場パーサー (parking_parser)
- 間取り図パーサー (floor_plan_parser)
- 建ぺい率・容積率パーサー (building_coverage_parser)
"""

import re
from typing import Dict, Any, Optional, List, Tuple


# ============================================================================
# 住所パーサー (address_parser.py)
# ============================================================================

def parse_address_structure(address: str) -> Optional[Dict[str, Any]]:
    """
    住所を都道府県とその次の区分に分けて構造化
    
    都道府県の下の区分:
    - 市（○○市）
    - 郡（○○郡）-> 町（○○町）/ 村（○○村）
    - 特別区（○○区）※東京都のみ
    - 支庁・振興局（○○支庁／○○振興局）※北海道のみ
    
    Args:
        address (str): 住所文字列
        
    Returns:
        Dict[str, Any]: 構造化された住所情報
    """
    if not address or address.strip() == "":
        return None
    
    address = address.strip()
    result = {
        "raw": address,
        "prefecture": None,
        "secondary_division": None,
        "secondary_type": None,
        "tertiary_division": None,
        "tertiary_type": None,
        "remaining": None
    }
    
    # 都道府県パターン
    pref_patterns = [
        r'^(東京都)',
        r'^(北海道)', 
        r'^(京都府|大阪府)',
        r'^(.{2,3}県)'
    ]
    
    prefecture = None
    remaining = address
    
    for pattern in pref_patterns:
        match = re.match(pattern, address)
        if match:
            prefecture = match.group(1)
            remaining = address[len(prefecture):]
            break
    
    if not prefecture:
        return result
    
    result["prefecture"] = prefecture
    
    # 東京都の特別区処理
    if prefecture == "東京都":
        special_ward_match = re.match(r'^(.+?区)', remaining)
        if special_ward_match:
            result["secondary_division"] = special_ward_match.group(1)
            result["secondary_type"] = "特別区"
            result["remaining"] = remaining[len(result["secondary_division"]):]
            return result
    
    # 北海道の支庁・振興局処理
    if prefecture == "北海道":
        office_patterns = [
            r'^(.+?支庁)',
            r'^(.+?振興局)'
        ]
        for pattern in office_patterns:
            office_match = re.match(pattern, remaining)
            if office_match:
                result["secondary_division"] = office_match.group(1)
                result["secondary_type"] = "支庁・振興局"
                remaining = remaining[len(result["secondary_division"]):]
                break
    
    # 郡の処理（郡 -> 町/村）
    gun_match = re.match(r'^(.+?郡)', remaining)
    if gun_match:
        result["secondary_division"] = gun_match.group(1)
        result["secondary_type"] = "郡"
        remaining = remaining[len(result["secondary_division"]):]
        
        # 郡の下の町・村を抽出
        town_village_patterns = [
            r'^(.+?町)',
            r'^(.+?村)'
        ]
        for pattern in town_village_patterns:
            tv_match = re.match(pattern, remaining)
            if tv_match:
                result["tertiary_division"] = tv_match.group(1)
                result["tertiary_type"] = "町" if "町" in tv_match.group(1) else "村"
                remaining = remaining[len(result["tertiary_division"]):]
                break
    else:
        # 市区町村の処理（郡以外）
        city_patterns = [
            r'^(.+?市)',
            r'^(.+?区)',  # 政令指定都市の区
            r'^(.+?町)',  # 町（単独）
            r'^(.+?村)'   # 村（単独）
        ]
        
        for pattern in city_patterns:
            city_match = re.match(pattern, remaining)
            if city_match:
                division = city_match.group(1)
                result["secondary_division"] = division
                
                if division.endswith('市'):
                    result["secondary_type"] = "市"
                elif division.endswith('区'):
                    result["secondary_type"] = "区"
                elif division.endswith('町'):
                    result["secondary_type"] = "町"
                elif division.endswith('村'):
                    result["secondary_type"] = "村"
                
                remaining = remaining[len(result["secondary_division"]):]
                break
    
    result["remaining"] = remaining.strip() if remaining.strip() else None
    
    return result


def format_address_components(parsed_address: Dict[str, Any]) -> Dict[str, str]:
    """
    解析結果を表示用にフォーマット
    
    Args:
        parsed_address (Dict[str, Any]): parse_address_structure の結果
        
    Returns:
        Dict[str, str]: フォーマット済みの住所コンポーネント
    """
    if not parsed_address:
        return {}
    
    components = {}
    
    if parsed_address.get("prefecture"):
        components["prefecture"] = parsed_address["prefecture"]
    
    # 第二レベル（都道府県の直下）
    if parsed_address.get("secondary_division"):
        secondary = parsed_address["secondary_division"]
        secondary_type = parsed_address.get("secondary_type", "")
        components["secondary"] = f"{secondary} ({secondary_type})"
    
    # 第三レベル（郡の下の町村）
    if parsed_address.get("tertiary_division"):
        tertiary = parsed_address["tertiary_division"]
        tertiary_type = parsed_address.get("tertiary_type", "")
        components["tertiary"] = f"{tertiary} ({tertiary_type})"
    
    return components


def get_administrative_hierarchy(parsed_address: Dict[str, Any]) -> str:
    """
    行政区分の階層構造を文字列で表現
    
    Args:
        parsed_address (Dict[str, Any]): parse_address_structure の結果
        
    Returns:
        str: 階層構造を表す文字列
    """
    if not parsed_address:
        return ""
    
    hierarchy = []
    
    if parsed_address.get("prefecture"):
        hierarchy.append(parsed_address["prefecture"])
    
    if parsed_address.get("secondary_division"):
        hierarchy.append(parsed_address["secondary_division"])
    
    if parsed_address.get("tertiary_division"):
        hierarchy.append(parsed_address["tertiary_division"])
    
    return " -> ".join(hierarchy)


# ============================================================================
# 建物構造パーサー (structure_parser.py + building_structure_parser.py)
# ============================================================================

def normalize_structure_code(structure: str) -> str:
    """
    構造コードを標準化
    """
    structure = structure.strip()
    
    # よくある表記の標準化
    structure_mapping = {
        # 基本構造
        "RC": "RC",  # 鉄筋コンクリート造
        "SRC": "SRC",  # 鉄骨鉄筋コンクリート造
        "S": "S",  # 鉄骨造
        "鉄骨": "S",
        "鉄筋コンクリート": "RC",
        "鉄骨鉄筋コンクリート": "SRC",
        
        # 軽量系
        "LS": "LS",  # 軽量鉄骨造
        "LGS": "LGS",  # 軽量鉄骨造
        "軽量鉄骨": "LS",
        
        # 木造系
        "W": "W",  # 木造
        "木造": "W",
        "2×4": "2x4",
        "2×6": "2x6",
        "ツーバイフォー": "2x4",
        "ツーバイシックス": "2x6",
        
        # ブロック系
        "CB": "CB",  # コンクリートブロック造
        "RCB": "RCB",  # 鉄筋コンクリートブロック造
        "コンクリートブロック": "CB",
        "鉄筋コンクリートブロック": "RCB",
        
        # その他
        "PC": "PC",  # プレストレストコンクリート造
        "ALC": "ALC",  # ALC造
        "プレストレストコンクリート": "PC",
    }
    
    # 複合構造の処理（例: "鉄筋コンクリート・鉄"）
    if "・" in structure or "+" in structure:
        # 複合構造の場合はそのまま返す
        return structure
    
    # 完全一致から検索
    if structure in structure_mapping:
        return structure_mapping[structure]
    
    # 部分一致検索（長い順にソートして優先度をつける）
    sorted_keys = sorted(structure_mapping.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key in structure:
            return structure_mapping[key]
    
    # マッピングにない場合はそのまま返す
    return structure


def parse_floor_structure_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    所在階/構造・階建 データをJSON形式でクレンジング
    
    パターン例:
    - "3階/RC5階建" -> {"floor": 3, "structure": "RC", "total_floors": 5, "basement_floors": 0}
    - "2階/SRC12階地下1階建" -> {"floor": 2, "structure": "SRC", "total_floors": 12, "basement_floors": 1}
    - "1階/SRC11階建一部RC" -> {"floor": 1, "structure": "SRC", "total_floors": 11, "basement_floors": 0, "partial_structure": "RC"}
    """
    if not value or value.strip() == "":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # 基本パターン: {所在階}階/{構造}{総階数}階{地下情報}建{オプション}
    pattern = r'^(\d+)階/(.+?)(\d+)階(?:地下(\d+)階)?建(.*)$'
    match = re.match(pattern, value)
    
    if not match:
        # パースできない場合は元の値を保持
        result = {"raw_value": value}
        if period is not None:
            result["period"] = period
        return result
    
    floor = int(match.group(1))
    structure_part = match.group(2)
    total_floors = int(match.group(3))
    basement_floors = int(match.group(4)) if match.group(4) else 0
    option_part = match.group(5).strip() if match.group(5) else ""
    
    # 構造コードの標準化
    main_structure = normalize_structure_code(structure_part)
    
    result = {
        "floor": floor,
        "structure": main_structure,
        "total_floors": total_floors,
        "basement_floors": basement_floors
    }
    
    # 一部構造の処理
    if "一部" in option_part:
        partial_match = re.search(r'一部(.+?)(?:$|\s)', option_part)
        if partial_match:
            partial_structure = normalize_structure_code(partial_match.group(1))
            result["partial_structure"] = partial_structure
    
    # その他のオプション情報
    if option_part and "一部" not in option_part:
        result["note"] = option_part
    
    if period is not None:
        result["period"] = period
    
    return result


def parse_building_structure_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    構造・階建て データをJSON形式でクレンジング
    
    パターン例:
    - "RC7階建" -> {"structure": "RC", "total_floors": 7, "basement_floors": 0}
    - "SRC11階建" -> {"structure": "SRC", "total_floors": 11, "basement_floors": 0}
    - "RC11階地下1階建" -> {"structure": "RC", "total_floors": 11, "basement_floors": 1}
    - "木造2階建（軸組工法）" -> {"structure": "W", "total_floors": 2, "basement_floors": 0}
    """
    if not value or value.strip() == "" or value.strip() == "-":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # 複数のパターンを試行（具体的なパターンから先に試行）
    
    # パターン1: X階/構造Y階建 形式（物件の階数が先頭にある）- 具体的パターンのため先に評価
    pattern1 = r'^(\d+)階/(.+?)(\d+)階(?:地下(\d+)階)?建.*?$'
    match1 = re.match(pattern1, value)
    
    # パターン2: 基本パターン {構造}{数字}階{地下情報}建{追加情報}
    pattern2 = r'^(.+?)(\d+)階(?:地下(\d+)階)?建.*?$'
    match2 = re.match(pattern2, value)
    
    # パターン3: 地下から始まるパターン（地上X階　構造）
    pattern3 = r'^地上(\d+)階.*?(.+)$'
    match3 = re.match(pattern3, value)
    
    # パターン4: 構造：xxx 地上階：x階 形式
    pattern4 = r'^構造：(.+?)\s+工法：.*?\s+地上階：(\d+)階.*?$'
    match4 = re.match(pattern4, value)
    
    # パターン5: 構造/地上x階 形式
    pattern5 = r'^(.+?)/地上(\d+)階.*?$'
    match5 = re.match(pattern5, value)
    
    # パターン6: 構造　地上x階 形式（全角スペース）
    pattern6 = r'^(.+?)\u3000地上(\d+)階.*?$'
    match6 = re.match(pattern6, value)
    
    # パターン7: 構造、x階建 形式
    pattern7 = r'^(.+?)、\s*(\d+)階建.*?$'
    match7 = re.match(pattern7, value)
    
    structure_part = None
    total_floors = None
    basement_floors = 0
    property_floor = None
    
    if match1:
        property_floor = int(match1.group(1))
        structure_part = match1.group(2)
        total_floors = int(match1.group(3))
        basement_floors = int(match1.group(4)) if match1.group(4) else 0
    elif match2:
        structure_part = match2.group(1)
        total_floors = int(match2.group(2))
        basement_floors = int(match2.group(3)) if match2.group(3) else 0
    elif match3:
        total_floors = int(match3.group(1))
        structure_part = match3.group(2).strip()
    elif match4:
        structure_part = match4.group(1)
        total_floors = int(match4.group(2))
    elif match5:
        structure_part = match5.group(1)
        total_floors = int(match5.group(2))
    elif match6:
        structure_part = match6.group(1)
        total_floors = int(match6.group(2))
    elif match7:
        structure_part = match7.group(1)
        total_floors = int(match7.group(2))
    else:
        # 単一の構造のみの場合も処理
        normalized = normalize_structure_code(value)
        if normalized and normalized != value:
            result = {"structure": normalized}
            if period is not None:
                result["period"] = period
            return result
        
        # パースできない場合は元の値を保持
        result = {"raw_value": value}
        if period is not None:
            result["period"] = period
        return result
    
    # 構造コードの標準化
    main_structure = normalize_structure_code(structure_part)
    
    result = {
        "structure": main_structure,
        "total_floors": total_floors,
        "basement_floors": basement_floors
    }
    
    # 物件の階数が指定されている場合は追加
    if property_floor is not None:
        result["floor"] = property_floor
    
    # 一部構造の処理（例: "木造2階地下1階建一部RC"）
    if "一部" in value:
        partial_match = re.search(r'一部(.+?)(?:$|\s)', value)
        if partial_match:
            partial_structure = normalize_structure_code(partial_match.group(1))
            result["partial_structure"] = partial_structure
    
    # その他の詳細情報がある場合はnoteに保存
    extra_info = ""
    if "（" in value and "）" in value:
        bracket_content = re.findall(r'（(.+?)）', value)
        if bracket_content:
            extra_info = "、".join(bracket_content)
    
    # 外装材などの詳細情報
    if any(keyword in value for keyword in ["サイディング", "シングル", "タイル", "モルタル", "リシン"]):
        exterior_match = re.search(r'(サイディング貼|アスファルトシングル葺|タイル貼|モルタル塗|リシン掻落)', value)
        if exterior_match:
            if extra_info:
                extra_info += "、" + exterior_match.group(1)
            else:
                extra_info = exterior_match.group(1)
    
    if extra_info:
        result["note"] = extra_info
    
    if period is not None:
        result["period"] = period
    
    return result


def get_structure_analysis_schema() -> Dict[str, Any]:
    """
    構造分析用のスキーマ定義を生成
    """
    return {
        "base_type": "structure_info",
        "data_type": "object",
        "required_fields": ["period"],
        "optional_fields": [
            "floor", "structure", "total_floors", "basement_floors", 
            "partial_structure", "note", "raw_value"
        ],
        "field_definitions": {
            "floor": {
                "type": "integer",
                "description": "所在階数"
            },
            "structure": {
                "type": "string", 
                "description": "主要構造（RC, SRC, S, W等）"
            },
            "total_floors": {
                "type": "integer",
                "description": "建物総階数"
            },
            "basement_floors": {
                "type": "integer",
                "description": "地下階数（0の場合は地下なし）"
            },
            "partial_structure": {
                "type": "string",
                "description": "一部構造（例: 一部RC）"
            },
            "note": {
                "type": "string",
                "description": "その他の補足情報"
            },
            "raw_value": {
                "type": "string",
                "description": "パースできない場合の元データ"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "基本構造",
                "value": {
                    "floor": 3,
                    "structure": "RC", 
                    "total_floors": 5,
                    "basement_floors": 0,
                    "period": 4
                }
            },
            {
                "description": "地下あり",
                "value": {
                    "floor": 2,
                    "structure": "SRC",
                    "total_floors": 12,
                    "basement_floors": 1,
                    "period": 4
                }
            },
            {
                "description": "一部構造",
                "value": {
                    "floor": 1,
                    "structure": "SRC",
                    "total_floors": 11,
                    "basement_floors": 0,
                    "partial_structure": "RC",
                    "period": 4
                }
            }
        ],
        "analysis_keys": {
            "structure_distribution": {
                "field": "structure",
                "description": "構造別分布分析"
            },
            "floor_distribution": {
                "field": "floor", 
                "description": "所在階分布分析"
            },
            "building_height": {
                "field": "total_floors",
                "description": "建物高さ分析"
            },
            "basement_analysis": {
                "field": "basement_floors",
                "description": "地下階分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "RC構造の物件数",
                "sql": "SELECT COUNT(*) FROM estate_cleaned WHERE id_cleaned = [structure_id] AND JSON_EXTRACT(value_cleaned, '$.structure') = 'RC'"
            },
            {
                "purpose": "高層物件の抽出",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [structure_id] AND JSON_EXTRACT(value_cleaned, '$.total_floors') >= 10"
            },
            {
                "purpose": "所在階別分布",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.floor') as floor, COUNT(*) as count FROM estate_cleaned WHERE id_cleaned = [structure_id] GROUP BY floor ORDER BY floor"
            }
        ],
        "period_aware": True
    }


def get_building_structure_analysis_schema() -> Dict[str, Any]:
    """
    建物構造分析用のスキーマ定義を生成
    """
    return {
        "base_type": "building_structure_info",
        "data_type": "object",
        "required_fields": ["period"],
        "optional_fields": [
            "structure", "total_floors", "basement_floors", "raw_value"
        ],
        "field_definitions": {
            "structure": {
                "type": "string", 
                "description": "建物構造（RC, SRC, S, W等）"
            },
            "total_floors": {
                "type": "integer",
                "description": "建物総階数"
            },
            "basement_floors": {
                "type": "integer",
                "description": "地下階数（0の場合は地下なし）"
            },
            "raw_value": {
                "type": "string",
                "description": "パースできない場合の元データ"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "RC構造7階建て",
                "value": {
                    "structure": "RC", 
                    "total_floors": 7,
                    "basement_floors": 0,
                    "period": 4
                }
            },
            {
                "description": "SRC構造地下あり",
                "value": {
                    "structure": "SRC",
                    "total_floors": 11,
                    "basement_floors": 1,
                    "period": 4
                }
            }
        ],
        "analysis_keys": {
            "structure_distribution": {
                "field": "structure",
                "description": "建物構造別分布分析"
            },
            "building_height": {
                "field": "total_floors",
                "description": "建物高さ分析"
            },
            "basement_analysis": {
                "field": "basement_floors",
                "description": "地下階分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "RC構造の建物数",
                "sql": "SELECT COUNT(*) FROM estate_cleaned WHERE id_cleaned = [structure_id] AND JSON_EXTRACT(value_cleaned, '$.structure') = 'RC'"
            },
            {
                "purpose": "高層建物の抽出",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [structure_id] AND JSON_EXTRACT(value_cleaned, '$.total_floors') >= 10"
            },
            {
                "purpose": "構造別平均階数",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.structure') as structure, AVG(JSON_EXTRACT(value_cleaned, '$.total_floors')) as avg_floors FROM estate_cleaned WHERE id_cleaned = [structure_id] GROUP BY structure ORDER BY avg_floors DESC"
            }
        ],
        "period_aware": True
    }


# ============================================================================
# リフォームパーサー (reform_parser.py)
# ============================================================================

def parse_reform_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    リフォーム情報をJSON形式でクレンジング
    
    パターン例:
    - "2024年10月完了　水回り設備交換：キッチン・浴室・トイレ　内装リフォーム：壁・床・全室※年月は一番古いリフォーム箇所を表します"
    - "2024年9月内装リフォーム完了"
    """
    if not value or value.strip() == "" or value.strip() == "-":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # 完了日付の抽出
    completion_date = None
    date_match = re.search(r'(\d{4})年(\d{1,2})月(?:(?:完了)|(?:リフォーム完了))', value)
    if date_match:
        year = int(date_match.group(1))
        month = int(date_match.group(2))
        completion_date = f"{year:04d}-{month:02d}"
    
    # 予定の場合
    is_scheduled = "完了予定" in value
    
    # リフォーム箇所の抽出
    reform_areas = {
        "water_facilities": [],  # 水回り設備
        "interior": [],          # 内装
        "other": []              # その他
    }
    
    # 水回り設備交換の抽出
    water_match = re.search(r'水回り設備交換[：:]([^　]+)', value)
    if water_match:
        water_items = water_match.group(1).replace('・', ',').split(',')
        reform_areas["water_facilities"] = [item.strip() for item in water_items if item.strip()]
    
    # 内装リフォームの抽出
    interior_match = re.search(r'内装リフォーム[：:]([^　※]+)', value)
    if interior_match:
        interior_items = interior_match.group(1).replace('・', ',').split(',')
        reform_areas["interior"] = [item.strip() for item in interior_items if item.strip()]
    
    # その他の抽出
    other_match = re.search(r'その他[：:]([^※]+)', value)
    if other_match:
        other_items = other_match.group(1).replace('・', ',').replace('/', ',').split(',')
        reform_areas["other"] = [item.strip() for item in other_items if item.strip()]
    
    # 注記の抽出
    note = None
    if "※" in value:
        note_match = re.search(r'※(.+)$', value)
        if note_match:
            note = note_match.group(1).strip()
    
    # 簡単なパターン（例: "2024年9月内装リフォーム完了"）
    if not any(reform_areas.values()) and "リフォーム" in value:
        if "内装" in value:
            reform_areas["interior"] = ["内装一般"]
        elif "水回り" in value:
            reform_areas["water_facilities"] = ["水回り一般"]
        else:
            reform_areas["other"] = ["リフォーム実施"]
    
    result = {
        "completion_date": completion_date,
        "is_scheduled": is_scheduled,
        "reform_areas": reform_areas,
        "has_reform": any(reform_areas.values()) or completion_date is not None
    }
    
    if note:
        result["note"] = note
    
    # 元データも保持
    if not result["has_reform"]:
        result["raw_value"] = value
    
    if period is not None:
        result["period"] = period
    
    return result


def get_reform_analysis_schema() -> Dict[str, Any]:
    """
    リフォーム分析用のスキーマ定義を生成
    """
    return {
        "base_type": "reform_info",
        "data_type": "object",
        "required_fields": ["period"],
        "optional_fields": [
            "completion_date", "is_scheduled", "reform_areas", "has_reform", 
            "note", "raw_value"
        ],
        "field_definitions": {
            "completion_date": {
                "type": "string",
                "description": "完了日付（YYYY-MM形式）"
            },
            "is_scheduled": {
                "type": "boolean",
                "description": "完了予定かどうか"
            },
            "reform_areas": {
                "type": "object",
                "description": "リフォーム箇所の詳細",
                "properties": {
                    "water_facilities": {
                        "type": "array",
                        "description": "水回り設備（キッチン、浴室、トイレ等）"
                    },
                    "interior": {
                        "type": "array", 
                        "description": "内装（壁、床、全室等）"
                    },
                    "other": {
                        "type": "array",
                        "description": "その他（洗面所、建具等）"
                    }
                }
            },
            "has_reform": {
                "type": "boolean",
                "description": "リフォーム実施有無"
            },
            "note": {
                "type": "string",
                "description": "注記・補足情報"
            },
            "raw_value": {
                "type": "string",
                "description": "パースできない場合の元データ"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "水回り・内装リフォーム",
                "value": {
                    "completion_date": "2024-10",
                    "is_scheduled": False,
                    "reform_areas": {
                        "water_facilities": ["キッチン", "浴室", "トイレ"],
                        "interior": ["壁", "床", "全室"],
                        "other": []
                    },
                    "has_reform": True,
                    "note": "年月は一番古いリフォーム箇所を表します",
                    "period": 4
                }
            },
            {
                "description": "内装リフォームのみ",
                "value": {
                    "completion_date": "2024-09",
                    "is_scheduled": False,
                    "reform_areas": {
                        "water_facilities": [],
                        "interior": ["内装一般"],
                        "other": []
                    },
                    "has_reform": True,
                    "period": 4
                }
            },
            {
                "description": "リフォームなし",
                "value": {
                    "value": None,
                    "period": 4
                }
            }
        ],
        "analysis_keys": {
            "reform_status": {
                "field": "has_reform",
                "description": "リフォーム実施状況分析"
            },
            "completion_timeline": {
                "field": "completion_date",
                "description": "リフォーム完了時期分析"
            },
            "water_facility_reform": {
                "field": "reform_areas.water_facilities",
                "description": "水回り設備リフォーム分析"
            },
            "interior_reform": {
                "field": "reform_areas.interior", 
                "description": "内装リフォーム分析"
            },
            "reform_scope": {
                "field": "reform_areas",
                "description": "リフォーム範囲分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "リフォーム済み物件数",
                "sql": "SELECT COUNT(*) FROM estate_cleaned WHERE id_cleaned = [reform_id] AND JSON_EXTRACT(value_cleaned, '$.has_reform') = true"
            },
            {
                "purpose": "水回りリフォーム済み物件",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [reform_id] AND JSON_LENGTH(JSON_EXTRACT(value_cleaned, '$.reform_areas.water_facilities')) > 0"
            },
            {
                "purpose": "最近のリフォーム物件",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [reform_id] AND JSON_EXTRACT(value_cleaned, '$.completion_date') >= '2024-01'"
            },
            {
                "purpose": "リフォーム箇所別集計",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.reform_areas') as areas, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [reform_id] AND JSON_EXTRACT(value_cleaned, '$.has_reform') = true GROUP BY areas"
            }
        ],
        "period_aware": True
    }


# ============================================================================
# 地目パーサー (land_use_parser.py)
# ============================================================================

def parse_land_use_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    地目データをJSON形式でクレンジング
    
    パターン例:
    - "宅地" -> {"values": ["宅地"]}
    - "宅地・畑・山林" -> {"values": ["宅地", "畑", "山林"]}
    - "畑（引渡までに宅地へ変更致します）" -> {"values": ["畑"], "note": "引渡までに宅地へ変更致します"}
    """
    if not value or value.strip() == "" or value.strip() == "-":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # 地目の基本パターン定義
    basic_land_types = [
        "宅地", "田", "畑", "山林", "原野", "雑種地", "公衆用道路",
        "墓地", "境内地", "運河用地", "水道用地", "用悪水路",
        "ため池", "堤", "井溝", "保安林", "公園", "鉄道用地"
    ]
    
    # 注記情報の抽出
    note = ""
    clean_value = value
    
    # 括弧内の情報を抽出
    if "（" in value and "）" in value:
        bracket_matches = re.findall(r'（(.+?)）', value)
        if bracket_matches:
            note_parts = []
            for match in bracket_matches:
                note_parts.append(match)
                clean_value = clean_value.replace(f"（{match}）", "")
            note = "、".join(note_parts)
    
    # ※記号での注記
    if "※" in value:
        note_match = re.search(r'※(.+)$', value)
        if note_match:
            if note:
                note += "、" + note_match.group(1)
            else:
                note = note_match.group(1)
            clean_value = re.sub(r'※.+$', '', clean_value)
    
    # 「地目：」プレフィックスの除去
    clean_value = re.sub(r'^地目：', '', clean_value)
    
    clean_value = clean_value.strip()
    
    # 地目の分割パターン
    land_types = []
    
    # 複数の区切り文字で分割
    separators = ['・', '、', '，', ',', '／', '/']
    current_parts = [clean_value]
    
    for separator in separators:
        new_parts = []
        for part in current_parts:
            new_parts.extend([p.strip() for p in part.split(separator) if p.strip()])
        current_parts = new_parts
    
    # 各部分を地目として抽出
    for part in current_parts:
        part = part.strip()
        if not part:
            continue
            
        # 基本地目の完全一致
        if part in basic_land_types:
            land_types.append(part)
        else:
            # 部分一致で地目を探す
            found = False
            for land_type in basic_land_types:
                if land_type in part:
                    land_types.append(land_type)
                    found = True
                    break
            
            # 見つからない場合はそのまま追加
            if not found:
                land_types.append(part)
    
    # 重複を除去しつつ順序を保持
    unique_land_types = []
    for land_type in land_types:
        if land_type not in unique_land_types:
            unique_land_types.append(land_type)
    
    # 結果の構築
    result = {
        "values": unique_land_types if unique_land_types else [clean_value]
    }
    
    if note:
        result["note"] = note
    
    if period is not None:
        result["period"] = period
    
    return result


def get_land_use_analysis_schema() -> Dict[str, Any]:
    """
    地目分析用のスキーマ定義を生成
    """
    return {
        "base_type": "land_use_info",
        "data_type": "object",
        "required_fields": ["values", "period"],
        "optional_fields": ["note", "value"],
        "field_definitions": {
            "values": {
                "type": "array",
                "items": {"type": "string"},
                "description": "地目のリスト"
            },
            "note": {
                "type": "string",
                "description": "補足情報（地目変更予定等）"
            },
            "value": {
                "type": "null",
                "description": "null値の場合"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "単一地目",
                "value": {
                    "values": ["宅地"],
                    "period": 4
                }
            },
            {
                "description": "複数地目",
                "value": {
                    "values": ["宅地", "畑", "山林"],
                    "period": 4
                }
            },
            {
                "description": "注記付き",
                "value": {
                    "values": ["畑"],
                    "note": "引渡までに宅地へ変更致します",
                    "period": 4
                }
            }
        ],
        "analysis_keys": {
            "land_type_distribution": {
                "field": "values",
                "description": "地目別分布分析"
            },
            "conversion_planned": {
                "field": "note",
                "description": "地目変更予定物件の分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "宅地物件の抽出",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [land_use_id] AND JSON_CONTAINS(JSON_EXTRACT(value_cleaned, '$.values'), JSON_QUOTE('宅地'))"
            },
            {
                "purpose": "複数地目物件の抽出",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [land_use_id] AND JSON_LENGTH(JSON_EXTRACT(value_cleaned, '$.values')) > 1"
            },
            {
                "purpose": "地目変更予定物件",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [land_use_id] AND JSON_EXTRACT(value_cleaned, '$.note') IS NOT NULL"
            }
        ],
        "period_aware": True
    }


# ============================================================================
# 周辺施設パーサー (surrounding_facilities_parser.py)
# ============================================================================

def normalize_facility_category(category: str) -> str:
    """
    施設カテゴリを正規化
    """
    category_mapping = {
        # 商業施設
        "スーパー": "スーパー",
        "コンビニ": "コンビニ",
        "ドラッグストア": "ドラッグストア", 
        "ホームセンター": "ホームセンター",
        "ショッピングセンター": "ショッピングセンター",
        
        # 教育機関
        "小学校": "小学校",
        "中学校": "中学校", 
        "高校・高専": "高校・高専",
        "幼稚園・保育園": "幼稚園・保育園",
        
        # 医療・福祉
        "病院": "病院",
        
        # 公共施設
        "郵便局": "郵便局",
        "銀行": "銀行",
        "図書館": "図書館",
        "公園": "公園",
        "役所": "役所",
        "警察署・交番": "警察署・交番",
        
        # 交通
        "駅": "駅",
        
        # その他
        "その他環境": "その他"
    }
    
    return category_mapping.get(category, category)


def parse_surrounding_facilities_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    周辺施設情報をJSON形式でクレンジング
    
    パターン例:
    - "コンビニ セブンイレブン野洲南桜店：徒歩9分（720ｍ）" 
    - "スーパー 食品館アプロ高見の里店：徒歩5分（350ｍ）"
    - "駅 近鉄難波奈良線　瓢箪山駅：徒歩6分（414ｍ）"
    """
    if not value or value.strip() == "" or value.strip() == "-":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # 基本構造
    result = {
        "facilities": []
    }
    
    # 施設パターンの正規表現
    # パターン1: カテゴリ 施設名：徒歩X分（YYYｍ）
    pattern1 = r'([^\s]+)\s+([^：]+)：徒歩(\d+)分[（(](\d+)(?:ｍ|m)[）)]'
    
    # パターン2: カテゴリ 施設名：徒歩X分（YYYｍ）※備考
    pattern2 = r'([^\s]+)\s+([^：]+)：徒歩(\d+)分[（(](\d+)(?:ｍ|m)[）)]※?([^※]*?)(?=\s+[^\s]+\s+|$)'
    
    # パターン3: 施設名まで数値単位（カテゴリなし、徒歩時間なし）
    pattern3 = r'^([^まで]+)まで(\d+)(?:ｍ|m)$'
    
    # パターン3の単独チェック（「施設名まで数値m」）
    pattern3_match = re.match(pattern3, value)
    if pattern3_match:
        name = pattern3_match.group(1).strip()
        distance = int(pattern3_match.group(2))
        
        facility = {
            "category": None,
            "name": name,
            "walking_time": None,
            "distance": distance,
            "unit": "m"
        }
        result["facilities"].append(facility)
    else:
        # 全体を分割して処理（複数施設が連続している場合）
        # タブ文字で区切られた施設単位で分割
        segments = re.split(r'\t+', value)
        
        # ペアで処理（カテゴリ + 施設情報）
        i = 0
        while i < len(segments):
            segment = segments[i].strip()
            if not segment:
                i += 1
                continue
            
            # 施設カテゴリかどうかをチェック
            category_keywords = ["スーパー", "コンビニ", "ドラッグストア", "ホームセンター", 
                               "ショッピングセンター", "小学校", "中学校", "高校・高専", 
                               "幼稚園・保育園", "病院", "郵便局", "銀行", "図書館", "公園", 
                               "役所", "警察署・交番", "駅", "その他環境"]
            
            if segment in category_keywords and i + 1 < len(segments):
                # カテゴリと次のセグメント（施設情報）をペアで処理
                category = segment
                facility_info = segments[i + 1].strip()
                
                # パターンマッチング（施設名：徒歩X分（YYYｍ））
                facility_match = re.match(r'([^：]+)：徒歩(\d+)分[（(](\d+)(?:ｍ|m)[）)]', facility_info)
                if facility_match:
                    name = facility_match.group(1).strip()
                    walking_time = int(facility_match.group(2))
                    distance = int(facility_match.group(3))
                    
                    # 施設カテゴリの正規化
                    normalized_category = normalize_facility_category(category)
                    
                    facility = {
                        "category": normalized_category,
                        "name": name,
                        "walking_time": walking_time,
                        "distance": distance,
                        "unit": "m"
                    }
                    
                    # 重複チェック（同じ名前の施設は除外）
                    if not any(f["name"] == name for f in result["facilities"]):
                        result["facilities"].append(facility)
                
                i += 2  # カテゴリと施設情報の両方を処理したので2つ進む
            else:
                # 単独セグメントの従来パターンマッチング
                matches = re.findall(pattern1, segment)
                if not matches:
                    # より詳細なパターンで再試行
                    matches = re.findall(r'([^\s]+)\s+([^：]+)：徒歩(\d+)分[（(](\d+)(?:ｍ|m)[）)]', segment)
                
                for match in matches:
                    category = match[0].strip()
                    name = match[1].strip()
                    walking_time = int(match[2])
                    distance = int(match[3])
                    
                    # 施設カテゴリの正規化
                    normalized_category = normalize_facility_category(category)
                    
                    facility = {
                        "category": normalized_category,
                        "name": name,
                        "walking_time": walking_time,
                        "distance": distance,
                        "unit": "m"
                    }
                    
                    # 重複チェック（同じ名前の施設は除外）
                    if not any(f["name"] == name for f in result["facilities"]):
                        result["facilities"].append(facility)
                
                i += 1
    
    if period is not None:
        result["period"] = period
    
    return result


def clean_surrounding_facilities_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    周辺施設情報をJSON形式でクレンジング（メイン関数）
    """
    return parse_surrounding_facilities_to_json(value, period)


def get_surrounding_facilities_analysis_schema() -> Dict[str, Any]:
    """
    周辺施設分析用のスキーマ定義を生成
    """
    return {
        "base_type": "array",
        "data_type": "surrounding_facilities",
        "fields": ["facilities"],
        "facility_fields": ["category", "name", "walking_time", "distance", "unit"],
        "field_definitions": {
            "category": {
                "type": "string",
                "description": "施設カテゴリ（スーパー、コンビニ、学校など）"
            },
            "name": {
                "type": "string", 
                "description": "施設名"
            },
            "walking_time": {
                "type": "number",
                "description": "徒歩時間（分）"
            },
            "distance": {
                "type": "number",
                "description": "距離"
            },
            "unit": {
                "type": "string",
                "description": "距離の単位（m）"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "コンビニと学校の情報",
                "value": {
                    "facilities": [
                        {
                            "category": "コンビニ",
                            "name": "セブンイレブン野洲南桜店",
                            "walking_time": 9,
                            "distance": 720,
                            "unit": "m"
                        },
                        {
                            "category": "小学校", 
                            "name": "守山市立守山小学校",
                            "walking_time": 7,
                            "distance": 550,
                            "unit": "m"
                        }
                    ],
                    "period": 4
                }
            }
        ],
        "analysis_keys": {
            "facility_availability": {
                "field": "category",
                "description": "施設種別の充実度分析"
            },
            "accessibility_analysis": {
                "field": "walking_time", 
                "description": "徒歩アクセス性分析"
            },
            "distance_distribution": {
                "field": "distance",
                "description": "距離分布分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "コンビニが徒歩5分以内の物件",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [facilities_id] AND JSON_EXTRACT(value_cleaned, '$.facilities[*].category') LIKE '%コンビニ%' AND JSON_EXTRACT(value_cleaned, '$.facilities[*].walking_time') <= 5"
            },
            {
                "purpose": "小学校までの平均徒歩時間",
                "sql": "SELECT AVG(JSON_EXTRACT(facility.value, '$.walking_time')) as avg_time FROM estate_cleaned, JSON_TABLE(value_cleaned, '$.facilities[*]' COLUMNS (category VARCHAR(50) PATH '$.category', walking_time INT PATH '$.walking_time')) as facility WHERE id_cleaned = [facilities_id] AND facility.category = '小学校'"
            },
            {
                "purpose": "施設カテゴリ別の物件数",
                "sql": "SELECT facility.category, COUNT(*) as property_count FROM estate_cleaned, JSON_TABLE(value_cleaned, '$.facilities[*]' COLUMNS (category VARCHAR(50) PATH '$.category')) as facility WHERE id_cleaned = [facilities_id] GROUP BY facility.category"
            }
        ],
        "period_aware": True
    }


# ============================================================================
# 駐車場パーサー (parking_parser.py)
# ============================================================================

def parse_parking_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    駐車場情報をJSON形式でクレンジング
    
    パターン例:
    - "空無" -> {"availability": false}
    - "敷地内（6000円／月）" -> {"availability": true, "location": "敷地内", "value": 6000, "unit": "円", "frequency": "月"}
    - "敷地内（料金無）" -> {"availability": true, "location": "敷地内", "value": 0, "unit": "円"}
    - "敷地内（4500円～6000円／月）" -> {"availability": true, "location": "敷地内", "min": 4500, "max": 6000, "value": 5250, "unit": "円", "frequency": "月"}
    """
    if not value or value.strip() == "" or value.strip() == "-":
        result = {"availability": False, "value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # 駐車場なしのパターン
    if value in ["空無", "無"]:
        result = {
            "availability": False,
            "value": None
        }
        if period is not None:
            result["period"] = period
        return result
    
    # 基本構造
    result = {
        "availability": True,
        "location": None,
        "value": None,
        "min": None,
        "max": None,
        "unit": None,
        "frequency": None,
        "note": None
    }
    
    # 敷地内/敷地外パターンの解析
    if "敷地内" in value:
        result["location"] = "敷地内"
    elif "敷地外" in value:
        result["location"] = "敷地外"
    
    # 敷地内・敷地外の共通料金処理
    if "敷地内" in value or "敷地外" in value:
        # 料金の抽出（無料パターンを先にチェック）
        if "料金無" in value or "無料" in value:
            result["value"] = 0
            result["unit"] = "円"
        elif re.search(r'(?<!\d)0円(?!\d)', value):  # 前後に数字がない0円のみマッチ
            result["value"] = 0
            result["unit"] = "円"
        else:
            # 範囲パターンのチェック（例: 6000円～1万円）
            range_patterns = [
                (r'(\d+)万(\d+)円～(\d+)万(\d+)円', 'man_en_man_en'),           # 1万6761円～2万951円
                (r'(\d+(?:,\d{3})*(?:\.\d+)?)円～(\d+)万(\d+)円', 'en_man_en'),   # 6000円～1万2000円
                (r'(\d+(?:,\d{3})*(?:\.\d+)?)円～(\d+)万円', 'en_man'),            # 6000円～1万円
                (r'(\d+(?:,\d{3})*(?:\.\d+)?)円～(\d+(?:,\d{3})*(?:\.\d+)?)円', 'en_en'), # 4500円～6000円
            ]
            
            range_found = False
            for pattern, pattern_type in range_patterns:
                range_match = re.search(pattern, value)
                if range_match:
                    if pattern_type == 'man_en_man_en':
                        # 1万6761円～2万951円
                        min_man = int(range_match.group(1))
                        min_en = int(range_match.group(2))
                        max_man = int(range_match.group(3))
                        max_en = int(range_match.group(4))
                        min_val = min_man * 10000 + min_en
                        max_val = max_man * 10000 + max_en
                    elif pattern_type == 'en_man_en':
                        # 6000円～1万2000円
                        min_val = int(range_match.group(1).replace(',', ''))
                        man = int(range_match.group(2))
                        en = int(range_match.group(3))
                        max_val = man * 10000 + en
                    elif pattern_type == 'en_man':
                        # 6000円～1万円
                        min_val = int(range_match.group(1).replace(',', ''))
                        man = int(range_match.group(2))
                        max_val = man * 10000
                    elif pattern_type == 'en_en':
                        # 4500円～6000円
                        min_val = int(range_match.group(1).replace(',', ''))
                        max_val = int(range_match.group(2).replace(',', ''))
                    
                    result["min"] = min_val
                    result["max"] = max_val
                    result["value"] = (min_val + max_val) // 2  # 平均値
                    result["unit"] = "円"
                    range_found = True
                    break
            
            if not range_found:
                # 金額パターンの抽出（優先順位順）
                fee_patterns = [
                    (r'(\d+)万(\d+)円', 'man_en'),   # 1万2000円
                    (r'(\d+)万円', 'man'),           # 1万円  
                    (r'(\d+)円', 'en')               # 6000円
                ]
                
                for pattern, pattern_type in fee_patterns:
                    fee_match = re.search(pattern, value)
                    if fee_match:
                        if pattern_type == 'man_en':
                            # 万円+円のパターン
                            man = int(fee_match.group(1))
                            en = int(fee_match.group(2))
                            result["value"] = man * 10000 + en
                        elif pattern_type == 'man':
                            # 万円のパターン
                            man = int(fee_match.group(1))
                            result["value"] = man * 10000
                        elif pattern_type == 'en':
                            # 円のパターン
                            result["value"] = int(fee_match.group(1))
                        result["unit"] = "円"
                        break
        
        # 頻度の抽出（/月、/年など）
        if "月" in value and ("/" in value or "／" in value):
            result["frequency"] = "月"
        elif "年" in value and ("/" in value or "／" in value):
            result["frequency"] = "年"
    
    # 専用使用権付駐車場
    elif "専用使用権付駐車場" in value:
        result["location"] = "専用使用権付"
        if "無料" in value:
            result["value"] = 0
            result["unit"] = "円"
        else:
            # 料金の抽出
            fee_patterns = [
                (r'(\d+)万(\d+)円', 'man_en'),   # 1万2000円
                (r'(\d+)万円', 'man'),           # 3万円  
                (r'(\d+)円', 'en')               # 6000円
            ]
            
            for pattern, pattern_type in fee_patterns:
                fee_match = re.search(pattern, value)
                if fee_match:
                    if pattern_type == 'man_en':
                        man = int(fee_match.group(1))
                        en = int(fee_match.group(2))
                        result["value"] = man * 10000 + en
                    elif pattern_type == 'man':
                        man = int(fee_match.group(1))
                        result["value"] = man * 10000
                    elif pattern_type == 'en':
                        result["value"] = int(fee_match.group(1))
                    result["unit"] = "円"
                    break
        
        # 頻度の抽出（/月、/年など）
        if "月" in value and ("/" in value or "／" in value):
            result["frequency"] = "月"
    
    # 機械式駐車場
    elif "機械" in value:
        result["location"] = "機械式"
        
        # 料金の抽出（複数料金の場合は最初の値を使用）
        fee_patterns = [
            (r'(\d+)万(\d+)円', 'man_en'),   # 1万2000円
            (r'(\d+)万円', 'man'),           # 1万円  
            (r'(\d+)円', 'en')               # 12700円
        ]
        
        for pattern, pattern_type in fee_patterns:
            fee_match = re.search(pattern, value)
            if fee_match:
                if pattern_type == 'man_en':
                    man = int(fee_match.group(1))
                    en = int(fee_match.group(2))
                    result["value"] = man * 10000 + en
                elif pattern_type == 'man':
                    man = int(fee_match.group(1))
                    result["value"] = man * 10000
                elif pattern_type == 'en':
                    result["value"] = int(fee_match.group(1))
                result["unit"] = "円"
                break
        
        # 頻度の抽出（/月、/年など）
        if "月" in value and ("/" in value or "／" in value):
            result["frequency"] = "月"
    
    # 平置き駐車場
    elif "平置" in value:
        result["location"] = "平置き"
    
    # 分譲駐車場の処理
    if "分譲駐車場" in value:
        result["location"] = "分譲駐車場"
    
    # その他の複雑なパターンは note に保存
    elif not result["location"]:
        result["note"] = value
    
    if period is not None:
        result["period"] = period
    
    return result


def get_parking_analysis_schema() -> Dict[str, Any]:
    """
    駐車場分析用のスキーマ定義を生成
    """
    return {
        "base_type": "parking_info",
        "data_type": "object",
        "required_fields": ["period"],
        "optional_fields": [
            "availability", "has_parking", "location", "monthly_fee", 
            "spaces", "parking_type", "note"
        ],
        "field_definitions": {
            "availability": {
                "type": "boolean",
                "description": "駐車場利用可能性"
            },
            "location": {
                "type": "string",
                "description": "駐車場の場所（敷地内、専用使用権付等）"
            },
            "value": {
                "type": "number",
                "description": "月額料金（円）・範囲の場合は平均値"
            },
            "min": {
                "type": "number",
                "description": "範囲料金の最小値（円）"
            },
            "max": {
                "type": "number",
                "description": "範囲料金の最大値（円）"
            },
            "unit": {
                "type": "string",
                "description": "料金の単位"
            },
            "frequency": {
                "type": "string",
                "description": "支払い頻度（月、年など）"
            },
            "note": {
                "type": "string",
                "description": "その他詳細情報"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "駐車場なし",
                "value": {
                    "availability": False,
                    "period": 4
                }
            },
            {
                "description": "敷地内有料駐車場",
                "value": {
                    "availability": True,
                    "location": "敷地内",
                    "value": 6000,
                    "unit": "円",
                    "frequency": "月",
                    "period": 4
                }
            },
            {
                "description": "無料駐車場",
                "value": {
                    "availability": True,
                    "location": "敷地内",
                    "value": 0,
                    "unit": "円",
                    "period": 4
                }
            }
        ],
        "analysis_keys": {
            "parking_availability": {
                "field": "availability",
                "description": "駐車場有無の分析"
            },
            "fee_distribution": {
                "field": "value",
                "description": "駐車場料金分布分析"
            },
            "location_analysis": {
                "field": "location",
                "description": "駐車場立地分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "駐車場ありの物件数",
                "sql": "SELECT COUNT(*) FROM estate_cleaned WHERE id_cleaned = [parking_id] AND JSON_EXTRACT(value_cleaned, '$.availability') = true"
            },
            {
                "purpose": "平均駐車場料金",
                "sql": "SELECT AVG(JSON_EXTRACT(value_cleaned, '$.value')) as avg_fee FROM estate_cleaned WHERE id_cleaned = [parking_id] AND JSON_EXTRACT(value_cleaned, '$.value') IS NOT NULL"
            },
            {
                "purpose": "無料駐車場物件",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [parking_id] AND JSON_EXTRACT(value_cleaned, '$.value') = 0 AND JSON_EXTRACT(value_cleaned, '$.availability') = true"
            },
            {
                "purpose": "料金別駐車場分布",
                "sql": "SELECT CASE WHEN JSON_EXTRACT(value_cleaned, '$.value') = 0 THEN '無料' WHEN JSON_EXTRACT(value_cleaned, '$.value') < 5000 THEN '5000円未満' WHEN JSON_EXTRACT(value_cleaned, '$.value') < 10000 THEN '5000-10000円' ELSE '10000円以上' END as fee_range, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [parking_id] AND JSON_EXTRACT(value_cleaned, '$.availability') = true GROUP BY fee_range"
            }
        ],
        "period_aware": True
    }


# ============================================================================
# 間取り図パーサー (floor_plan_parser.py)
# ============================================================================

def _extract_price(price_text: str) -> Optional[Dict[str, Any]]:
    """
    価格テキストから価格情報を抽出
    例: "2590万円" -> {"value": 2590, "unit": "万円"}
    """
    if not price_text:
        return None
    
    # 価格パターンのマッチング
    price_match = re.search(r'(\d+(?:\.\d+)?)万円', price_text)
    if price_match:
        return {
            "value": float(price_match.group(1)),
            "unit": "万円"
        }
    
    # その他の価格パターン
    price_match = re.search(r'(\d+(?:\.\d+)?)(円|千円|億円)', price_text)
    if price_match:
        return {
            "value": float(price_match.group(1)),
            "unit": price_match.group(2)
        }
    
    return {"raw_value": price_text}


def _extract_area(area_text: str) -> Optional[Dict[str, Any]]:
    """
    面積テキストから面積情報を抽出
    例: "160.01m2" -> {"value": 160.01, "unit": "m2"}
    """
    if not area_text:
        return None
    
    # 面積パターンのマッチング (m2, ㎡, 平米, 坪)
    area_patterns = [
        r'(\d+(?:\.\d+)?)m2',
        r'(\d+(?:\.\d+)?)㎡',
        r'(\d+(?:\.\d+)?)平米',
        r'(\d+(?:\.\d+)?)坪'
    ]
    
    for pattern in area_patterns:
        area_match = re.search(pattern, area_text)
        if area_match:
            value = float(area_match.group(1))
            if '坪' in pattern:
                unit = "坪"
            else:
                unit = "m2"
            
            return {
                "value": value,
                "unit": unit
            }
    
    return {"raw_value": area_text}


def parse_floor_plan_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    間取り図データをJSON形式でクレンジング
    
    パターン例:
    - "1号棟	価格	：	2590万円	間取り	：	4LDK	土地面積	：	160.01m2	建物面積	：	108.54m2"
    - "A号棟	価格	：	3790万円	間取り	：	4LDK	土地面積	：	104.8m2	建物面積	：	98.95m2"
    - "価格	：	5180万円	間取り	：	3LDK+S	土地面積	：	91.18m2	建物面積	：	90.15m2"
    """
    if not value or value.strip() == "" or value.strip() == "-":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # タブ区切りまたはスペース区切りでデータを分割
    if '\t' in value:
        parts = value.split('\t')
    else:
        # 複数のスペースで区切られている場合は、スペースで分割して空文字を除去
        parts = [p.strip() for p in value.split() if p.strip()]
    
    result = {}
    
    # 建物番号の抽出（最初の部分）
    if parts and not parts[0].startswith('価格'):
        building_number = parts[0].strip()
        if building_number:
            result["building_number"] = building_number
    
    # 各項目を抽出
    for i in range(len(parts)):
        part = parts[i].strip()
        
        # 価格の抽出
        if part == "価格" and i + 2 < len(parts) and parts[i + 1] == "：":
            price_text = parts[i + 2]
            price_info = _extract_price(price_text)
            if price_info:
                result["price"] = price_info
        
        # 間取りの抽出
        elif part == "間取り" and i + 2 < len(parts) and parts[i + 1] == "：":
            layout_text = parts[i + 2]
            if layout_text:
                result["layout"] = layout_text
        
        # 土地面積の抽出
        elif part == "土地面積" and i + 2 < len(parts) and parts[i + 1] == "：":
            land_area_text = parts[i + 2]
            area_info = _extract_area(land_area_text)
            if area_info:
                result["land_area"] = area_info
        
        # 建物面積の抽出
        elif part == "建物面積" and i + 2 < len(parts) and parts[i + 1] == "：":
            building_area_text = parts[i + 2]
            area_info = _extract_area(building_area_text)
            if area_info:
                result["building_area"] = area_info
    
    # データが取得できない場合は元データを保持
    if not result or (len(result) == 1 and "building_number" in result):
        result = {"raw_value": value}
    
    if period is not None:
        result["period"] = period
    
    return result


def get_floor_plan_analysis_schema() -> Dict[str, Any]:
    """
    間取り図分析用のスキーマ定義を生成
    """
    return {
        "base_type": "floor_plan_info",
        "data_type": "object",
        "required_fields": ["period"],
        "optional_fields": [
            "building_number", "price", "layout", "land_area", 
            "building_area", "raw_value", "value"
        ],
        "field_definitions": {
            "building_number": {
                "type": "string",
                "description": "建物番号（1号棟、A号棟等）"
            },
            "price": {
                "type": "object",
                "description": "価格情報",
                "properties": {
                    "value": {"type": "number", "description": "価格"},
                    "unit": {"type": "string", "description": "単位（万円等）"},
                    "raw_value": {"type": "string", "description": "解析不能な場合の元データ"}
                }
            },
            "layout": {
                "type": "string",
                "description": "間取り（4LDK、3LDK+S等）"
            },
            "land_area": {
                "type": "object",
                "description": "土地面積",
                "properties": {
                    "value": {"type": "number", "description": "面積値"},
                    "unit": {"type": "string", "description": "単位（m2、坪等）"},
                    "raw_value": {"type": "string", "description": "解析不能な場合の元データ"}
                }
            },
            "building_area": {
                "type": "object",
                "description": "建物面積",
                "properties": {
                    "value": {"type": "number", "description": "面積値"},
                    "unit": {"type": "string", "description": "単位（m2、坪等）"},
                    "raw_value": {"type": "string", "description": "解析不能な場合の元データ"}
                }
            },
            "raw_value": {
                "type": "string",
                "description": "パース不能な場合の元データ"
            },
            "value": {
                "type": "null",
                "description": "null値の場合"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "完全な物件情報",
                "value": {
                    "building_number": "1号棟",
                    "price": {"value": 2590, "unit": "万円"},
                    "layout": "4LDK",
                    "land_area": {"value": 160.01, "unit": "m2"},
                    "building_area": {"value": 108.54, "unit": "m2"},
                    "period": 4
                }
            },
            {
                "description": "建物番号なし",
                "value": {
                    "price": {"value": 5180, "unit": "万円"},
                    "layout": "3LDK+S",
                    "land_area": {"value": 91.18, "unit": "m2"},
                    "building_area": {"value": 90.15, "unit": "m2"},
                    "period": 4
                }
            }
        ],
        "analysis_keys": {
            "price_distribution": {
                "field": "price.value",
                "description": "価格分布分析"
            },
            "layout_distribution": {
                "field": "layout",
                "description": "間取り別分布"
            },
            "area_analysis": {
                "field": ["land_area.value", "building_area.value"],
                "description": "面積分析"
            },
            "building_efficiency": {
                "field": ["land_area.value", "building_area.value"],
                "description": "建物効率分析（建物面積/土地面積）"
            }
        },
        "sql_examples": [
            {
                "purpose": "価格帯別物件数",
                "sql": "SELECT CASE WHEN JSON_EXTRACT(value_cleaned, '$.price.value') < 3000 THEN '3000万円未満' WHEN JSON_EXTRACT(value_cleaned, '$.price.value') < 5000 THEN '3000-5000万円' ELSE '5000万円以上' END as price_range, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [floor_plan_id] GROUP BY price_range"
            },
            {
                "purpose": "間取り別平均価格",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.layout') as layout, AVG(JSON_EXTRACT(value_cleaned, '$.price.value')) as avg_price FROM estate_cleaned WHERE id_cleaned = [floor_plan_id] AND JSON_EXTRACT(value_cleaned, '$.price.value') IS NOT NULL GROUP BY layout ORDER BY avg_price DESC"
            },
            {
                "purpose": "建物効率の高い物件",
                "sql": "SELECT *, (JSON_EXTRACT(value_cleaned, '$.building_area.value') / JSON_EXTRACT(value_cleaned, '$.land_area.value')) as efficiency FROM estate_cleaned WHERE id_cleaned = [floor_plan_id] AND JSON_EXTRACT(value_cleaned, '$.land_area.value') > 0 ORDER BY efficiency DESC"
            }
        ],
        "period_aware": True
    }


# ============================================================================
# 建ぺい率・容積率パーサー (building_coverage_parser.py)
# ============================================================================

def parse_building_coverage_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    建ぺい率・容積率データをJSON形式でクレンジング
    
    パターン例:
    - "60％・200％" -> {"building_coverage": 60, "floor_area_ratio": 200, "unit": "%"}
    - "建ペい率：60％、容積率：200％" -> {"building_coverage": 60, "floor_area_ratio": 200, "unit": "%"}
    - "建ぺい率：60％/容積率：200％" -> {"building_coverage": 60, "floor_area_ratio": 200, "unit": "%"}
    """
    if not value or value.strip() == "" or value.strip() == "-":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # パターン1: 数字％・数字％ 形式（シンプルな2値のみ）
    pattern1 = r'^(\d+(?:\.\d+)?)％・(\d+(?:\.\d+)?)％$'
    match1 = re.search(pattern1, value)
    
    if match1:
        building_coverage = float(match1.group(1))
        floor_area_ratio = float(match1.group(2))
        result = {
            "building_coverage": building_coverage,
            "floor_area_ratio": floor_area_ratio,
            "unit": "%"
        }
        if period is not None:
            result["period"] = period
        return result
    
    # パターン2: 建ペい率：XX％、容積率：YY％ 形式（建蔽率の表記とコロンなしも対応）
    pattern2 = r'建(?:ペ|ぺ|蔽)い?率[：:]?(\d+(?:\.\d+)?)[％%](?:[\(（][^）\)]*[\)）]|[・･]\d+(?:\.\d+)?[％%])*[、,，\u3000].*?容積率[：:]?(\d+(?:\.\d+)?)[％%]'
    match2 = re.search(pattern2, value)
    
    if match2:
        building_coverage = float(match2.group(1))
        floor_area_ratio = float(match2.group(2))
        result = {
            "building_coverage": building_coverage,
            "floor_area_ratio": floor_area_ratio,
            "unit": "%"
        }
        if period is not None:
            result["period"] = period
        return result
    
    # パターン3: 建ぺい率：XX％/容積率：YY％ 形式（括弧付きも対応）
    pattern3 = r'建(?:ペ|ぺ|蔽)い?率[：:](\d+(?:\.\d+)?)％(?:[\(（][^）\)]*[\)）])?[／/]容積率[：:](\d+(?:\.\d+)?)％'
    match3 = re.search(pattern3, value)
    
    if match3:
        building_coverage = float(match3.group(1))
        floor_area_ratio = float(match3.group(2))
        result = {
            "building_coverage": building_coverage,
            "floor_area_ratio": floor_area_ratio,
            "unit": "%"
        }
        if period is not None:
            result["period"] = period
        return result
    
    # パターン4: 建ぺい率：XX/容積率：YY 形式（％記号なし）
    pattern4 = r'建(?:ペ|ぺ|蔽)い?率[：:](\d+(?:\.\d+)?)[／/]容積率[：:](\d+(?:\.\d+)?)'
    match4 = re.search(pattern4, value)
    
    if match4:
        building_coverage = float(match4.group(1))
        floor_area_ratio = float(match4.group(2))
        result = {
            "building_coverage": building_coverage,
            "floor_area_ratio": floor_area_ratio,
            "unit": "%"
        }
        if period is not None:
            result["period"] = period
        return result
    
    # パターン5: 建ぺい率XX％、容積率YY％ 形式（コロンなし、建蔽率の表記も対応）
    pattern5 = r'建(?:ペ|ぺ|蔽)い?率(\d+(?:\.\d+)?)％[、,，].*?容積率(\d+(?:\.\d+)?)％'
    match5 = re.search(pattern5, value)
    
    if match5:
        building_coverage = float(match5.group(1))
        floor_area_ratio = float(match5.group(2))
        result = {
            "building_coverage": building_coverage,
            "floor_area_ratio": floor_area_ratio,
            "unit": "%"
        }
        if period is not None:
            result["period"] = period
        return result
    
    # パターン6: 建ぺい率・容積率：XX％・YY％ 形式
    pattern6 = r'建(?:ペ|ぺ|蔽)い?率[・･]容積率[：:](\d+(?:\.\d+)?)％[・･](\d+(?:\.\d+)?)％'
    match6 = re.search(pattern6, value)
    
    if match6:
        building_coverage = float(match6.group(1))
        floor_area_ratio = float(match6.group(2))
        result = {
            "building_coverage": building_coverage,
            "floor_area_ratio": floor_area_ratio,
            "unit": "%"
        }
        if period is not None:
            result["period"] = period
        return result
    
    # パターン7: 数字％　数字％ 形式（全角スペース区切り）
    pattern7 = r'^(\d+(?:\.\d+)?)％\u3000(\d+(?:\.\d+)?)％$'
    match7 = re.search(pattern7, value)
    
    if match7:
        building_coverage = float(match7.group(1))
        floor_area_ratio = float(match7.group(2))
        result = {
            "building_coverage": building_coverage,
            "floor_area_ratio": floor_area_ratio,
            "unit": "%"
        }
        if period is not None:
            result["period"] = period
        return result
    
    # パターン8: 数字％/数字％ 形式（シンプルなスラッシュ区切り）
    pattern8 = r'^(\d+(?:\.\d+)?)％[／/](\d+(?:\.\d+)?)％$'
    match8 = re.search(pattern8, value)
    
    if match8:
        building_coverage = float(match8.group(1))
        floor_area_ratio = float(match8.group(2))
        result = {
            "building_coverage": building_coverage,
            "floor_area_ratio": floor_area_ratio,
            "unit": "%"
        }
        if period is not None:
            result["period"] = period
        return result
    
    # パターン8: 単純な数字・数字 形式（％記号なし）
    pattern8 = r'^(\d+(?:\.\d+)?)[・･](\d+(?:\.\d+)?)$'
    match8 = re.search(pattern8, value)
    
    if match8:
        building_coverage = float(match8.group(1))
        floor_area_ratio = float(match8.group(2))
        result = {
            "building_coverage": building_coverage,
            "floor_area_ratio": floor_area_ratio,
            "unit": "%"
        }
        if period is not None:
            result["period"] = period
        return result
    
    # パースできない場合は元の値を保持
    result = {"raw_value": value}
    if period is not None:
        result["period"] = period
    return result


def get_building_coverage_analysis_schema() -> Dict[str, Any]:
    """
    建ぺい率・容積率分析用のスキーマ定義を生成
    """
    return {
        "base_type": "building_coverage_info",
        "data_type": "object",
        "required_fields": ["period"],
        "optional_fields": [
            "building_coverage", "floor_area_ratio", "unit", "raw_value", "value"
        ],
        "field_definitions": {
            "building_coverage": {
                "type": "number",
                "description": "建ぺい率（％）"
            },
            "floor_area_ratio": {
                "type": "number",
                "description": "容積率（％）"
            },
            "unit": {
                "type": "string",
                "description": "単位（％）"
            },
            "raw_value": {
                "type": "string",
                "description": "パース不能な場合の元データ"
            },
            "value": {
                "type": "null",
                "description": "null値の場合"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "基本パターン",
                "value": {
                    "building_coverage": 60,
                    "floor_area_ratio": 200,
                    "unit": "%",
                    "period": 4
                }
            },
            {
                "description": "住宅地域",
                "value": {
                    "building_coverage": 50,
                    "floor_area_ratio": 80,
                    "unit": "%",
                    "period": 4
                }
            },
            {
                "description": "商業地域",
                "value": {
                    "building_coverage": 80,
                    "floor_area_ratio": 400,
                    "unit": "%",
                    "period": 4
                }
            }
        ],
        "analysis_keys": {
            "building_coverage_distribution": {
                "field": "building_coverage",
                "description": "建ぺい率別分布分析"
            },
            "floor_area_ratio_distribution": {
                "field": "floor_area_ratio",
                "description": "容積率別分布分析"
            },
            "development_potential": {
                "field": ["building_coverage", "floor_area_ratio"],
                "description": "開発ポテンシャル分析"
            },
            "zoning_classification": {
                "field": ["building_coverage", "floor_area_ratio"],
                "description": "用途地域分類推定"
            }
        },
        "sql_examples": [
            {
                "purpose": "建ぺい率別物件数",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.building_coverage') as coverage, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [coverage_id] AND JSON_EXTRACT(value_cleaned, '$.building_coverage') IS NOT NULL GROUP BY coverage ORDER BY coverage"
            },
            {
                "purpose": "容積率別物件数",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.floor_area_ratio') as ratio, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [coverage_id] AND JSON_EXTRACT(value_cleaned, '$.floor_area_ratio') IS NOT NULL GROUP BY ratio ORDER BY ratio"
            },
            {
                "purpose": "高容積率物件の抽出",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [coverage_id] AND JSON_EXTRACT(value_cleaned, '$.floor_area_ratio') >= 300"
            },
            {
                "purpose": "用途地域推定（商業系）",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [coverage_id] AND JSON_EXTRACT(value_cleaned, '$.building_coverage') >= 80 AND JSON_EXTRACT(value_cleaned, '$.floor_area_ratio') >= 300"
            }
        ],
        "period_aware": True
    }