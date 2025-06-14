"""
住所解析ユーティリティ
住所から都道府県とその次の区分を分離して構造化
"""

import re
from typing import Dict, Any, Optional

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