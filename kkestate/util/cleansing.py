"""
データクレンジング用の関数群
各種データ型に対応したクレンジング処理を提供
共通ユーティリティ関数
"""

import re
from typing import Optional, Union, Dict, List, Any
from datetime import datetime

def clean_price(value: str) -> Optional[Dict[str, Any]]:
    """
    価格情報をクレンジング
    例: "2685万円～3955万円" -> {"min": 26850000, "max": 39550000, "unit": "円"}
    """
    if not value or value.strip() == "":
        return None
    
    value = value.strip()
    result = {"raw": value}
    
    # 価格未定などのケース
    if "未定" in value or "要相談" in value:
        result["status"] = "undecided"
        return result
    
    # 最初の価格範囲部分のみを抽出（XX万円～YY万円 または XX万円）
    price_range_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?万\d*円)(?:～(\d+(?:,\d{3})*(?:\.\d+)?万\d*円))?', value)
    if price_range_match:
        # 抽出した価格範囲部分のみを処理対象とする
        price_text = price_range_match.group(0)
        numbers = re.findall(r'(\d+(?:,\d{3})*(?:\.\d+)?)', price_text)
    else:
        # 従来通り全体から数値を抽出（後方互換性のため）
        numbers = re.findall(r'(\d+(?:,\d{3})*(?:\.\d+)?)', value)
    
    if not numbers:
        return result
    
    # 単位を判定
    unit_multiplier = 1
    if "万円" in value:
        unit_multiplier = 10000
        result["unit"] = "円"
    elif "千円" in value:
        unit_multiplier = 1000
        result["unit"] = "円"
    elif "億円" in value:
        unit_multiplier = 100000000
        result["unit"] = "円"
    else:
        result["unit"] = "円"
    
    # カンマを除去して数値に変換
    clean_numbers = []
    for num in numbers:
        clean_num = float(num.replace(',', '')) * unit_multiplier
        clean_numbers.append(int(clean_num))
    
    if len(clean_numbers) == 1:
        result["price"] = clean_numbers[0]
    elif len(clean_numbers) >= 2:
        result["min"] = min(clean_numbers)
        result["max"] = max(clean_numbers)
    
    return result

def clean_layout(value: str) -> Optional[Dict[str, Any]]:
    """
    間取り情報をクレンジング
    例: "1LDK～3LDK" -> {"min": "1LDK", "max": "3LDK", "types": ["1LDK", "2LDK", "3LDK"]}
    """
    if not value or value.strip() == "":
        return None
    
    value = value.strip()
    result = {"raw": value}
    
    # 間取りパターンを抽出
    layout_pattern = r'(\d+[A-Z]+(?:\+[A-Z]+)?)'
    layouts = re.findall(layout_pattern, value.upper())
    
    if layouts:
        result["types"] = list(set(layouts))  # 重複を除去
        result["types"].sort()
        
        if len(result["types"]) == 1:
            result["layout"] = result["types"][0]
        else:
            result["min"] = result["types"][0]
            result["max"] = result["types"][-1]
    
    return result

def clean_area(value: str) -> Optional[Dict[str, Any]]:
    """
    面積情報をクレンジング
    例: "55.02㎡～75.89㎡" -> {"min": 55.02, "max": 75.89, "unit": "㎡"}
    """
    if not value or value.strip() == "":
        return None
    
    value = value.strip()
    result = {"raw": value}
    
    # 数値を抽出
    numbers = re.findall(r'(\d+(?:\.\d+)?)', value)
    if not numbers:
        return result
    
    # 単位を判定
    if "㎡" in value or "m²" in value:
        result["unit"] = "㎡"
    elif "坪" in value:
        result["unit"] = "坪"
    else:
        result["unit"] = "㎡"  # デフォルト
    
    # 数値に変換
    clean_numbers = [float(num) for num in numbers]
    
    if len(clean_numbers) == 1:
        result["area"] = clean_numbers[0]
    elif len(clean_numbers) >= 2:
        result["min"] = min(clean_numbers)
        result["max"] = max(clean_numbers)
    
    # 坪数も計算（㎡の場合）
    if result["unit"] == "㎡":
        if "area" in result:
            result["tsubo"] = round(result["area"] / 3.30579, 2)
        if "min" in result:
            result["min_tsubo"] = round(result["min"] / 3.30579, 2)
        if "max" in result:
            result["max_tsubo"] = round(result["max"] / 3.30579, 2)
    
    return result

def clean_access(value: str) -> Optional[List[Dict[str, Any]]]:
    """
    交通アクセス情報をクレンジング
    複数路線に対応
    """
    if not value or value.strip() == "":
        return None
    
    value = value.strip()
    access_list = []
    
    # 複数の交通手段を分割（改行や句読点で）
    lines = re.split(r'[\n。、]', value)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        access_info = {"raw": line}
        
        # 駅名と徒歩分数を抽出
        station_match = re.search(r'「([^」]+)」', line)
        if station_match:
            access_info["station"] = station_match.group(1)
        
        # 路線名を抽出
        line_match = re.search(r'([^\s「」]+線)', line)
        if line_match:
            access_info["line"] = line_match.group(1)
        
        # 徒歩分数を抽出
        walk_match = re.search(r'徒歩(\d+)分', line)
        if walk_match:
            access_info["walk_minutes"] = int(walk_match.group(1))
        
        # バス利用を抽出
        bus_match = re.search(r'バス(\d+)分', line)
        if bus_match:
            access_info["bus_minutes"] = int(bus_match.group(1))
        
        if len(access_info) > 1:  # rawだけでない場合
            access_list.append(access_info)
    
    return access_list if access_list else None

def clean_date(value: str) -> Optional[Dict[str, Any]]:
    """
    日付情報をクレンジング
    例: "2023年12月", "2024年3月下旬"
    """
    if not value or value.strip() == "":
        return None
    
    value = value.strip()
    result = {"raw": value}
    
    # 年月を抽出
    year_month_match = re.search(r'(\d{4})年(\d{1,2})月', value)
    if year_month_match:
        year = int(year_month_match.group(1))
        month = int(year_month_match.group(2))
        result["year"] = year
        result["month"] = month
        
        # 上旬・中旬・下旬を判定
        if "上旬" in value:
            result["period"] = "early"
            result["estimated_date"] = f"{year}-{month:02d}-05"
        elif "中旬" in value:
            result["period"] = "middle"
            result["estimated_date"] = f"{year}-{month:02d}-15"
        elif "下旬" in value:
            result["period"] = "late"
            result["estimated_date"] = f"{year}-{month:02d}-25"
        else:
            result["estimated_date"] = f"{year}-{month:02d}-01"
    
    # 即入居可などの特殊ケース
    if "即入居" in value:
        result["immediate"] = True
    
    return result

def clean_address(value: str) -> Optional[Dict[str, Any]]:
    """
    住所情報をクレンジング
    都道府県、市区町村、番地などを分離
    """
    if not value or value.strip() == "":
        return None
    
    value = value.strip()
    result = {"raw": value}
    
    # 都道府県を抽出
    pref_pattern = r'(東京都|北海道|(?:京都|大阪)府|.{2,3}県)'
    pref_match = re.match(pref_pattern, value)
    if pref_match:
        result["prefecture"] = pref_match.group(1)
        remaining = value[len(result["prefecture"]):]
        
        # 市区町村を抽出
        city_pattern = r'^(.+?[市区町村])'
        city_match = re.match(city_pattern, remaining)
        if city_match:
            result["city"] = city_match.group(1)
            remaining = remaining[len(result["city"]):]
            
            # 残りを町名・番地として保存
            if remaining:
                result["detail"] = remaining.strip()
    
    return result

def clean_number(value: str) -> Optional[Union[int, float]]:
    """
    数値をクレンジング（総戸数、階数など）
    """
    if not value or value.strip() == "":
        return None
    
    # 数値を抽出
    number_match = re.search(r'(\d+(?:\.\d+)?)', value.replace(',', ''))
    if number_match:
        num_str = number_match.group(1)
        if '.' in num_str:
            return float(num_str)
        else:
            return int(num_str)
    
    return None

def clean_management_fee(value: str) -> Optional[Dict[str, Any]]:
    """
    管理費・修繕積立金などの月額費用をクレンジング
    """
    if not value or value.strip() == "":
        return None
    
    value = value.strip()
    result = {"raw": value}
    
    # 「未定」などのケース
    if "未定" in value:
        result["status"] = "undecided"
        return result
    
    # 金額を抽出
    amount_match = re.search(r'(\d+(?:,\d{3})*)', value)
    if amount_match:
        amount = int(amount_match.group(1).replace(',', ''))
        result["amount"] = amount
        
        # 単位を判定
        if "月" in value:
            result["period"] = "monthly"
        else:
            result["period"] = "monthly"  # デフォルト
    
    return result

def clean_boolean(value: str) -> Optional[bool]:
    """
    有無や可否をブール値に変換
    """
    if not value or value.strip() == "":
        return None
    
    value = value.strip()
    
    # True判定
    if any(word in value for word in ["有", "あり", "可", "可能", "○"]):
        return True
    
    # False判定
    if any(word in value for word in ["無", "なし", "不可", "×", "-"]):
        return False
    
    return None