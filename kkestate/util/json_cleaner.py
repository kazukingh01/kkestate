"""
JSON形式でのクレンジング処理
estate_detailの生データをJSONオブジェクトに変換
"""

import re
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

def _should_nullify_text(value: str) -> bool:
    """
    テキストを null にすべきかどうかを判定
    """
    # 文字数が異常に長い場合
    if len(value) > 500:
        return True
    
    # 無意味なデータ（"-" のみなど）
    if value.strip() in ["-", "－", "ー", "未定", "未設定", "なし", "無し", "N/A", ""]:
        return True
    
    # 分析に重要でないパターン
    unimportant_patterns = [
        "■支払い例",
        "■ローンのご案内",
        "提携ローン",
        "※ローンは一定要件該当者が対象",
        "※金利は",
        "融資限度額",
        "事務手数料",
        "保証料",
        "適用される金利は融資実行時",
        "お申込みの際には、お認印",
        "収入証明書",
        "本人確認書類",
        "運転免許証",
        "健康保険証",
        "パスポート",
        "先着順販売のため販売済の場合",
        "販売開始まで契約または予約の申し込み",
        "申し込み順位の確保につながる行為は一切できません",
        "確定情報は新規分譲広告において明示",
        "物件データは第",
        "期以降の全販売対象住戸",
        "のものを表記",
        "受付時間／",
        "定休日／",
        "受付場所／",
        "マンションギャラリー",
    ]
    
    # いずれかのパターンに一致する場合は null にする
    for pattern in unimportant_patterns:
        if pattern in value:
            return True
    
    return False

def extract_period_from_key(key_name: str) -> Tuple[str, Optional[int]]:
    """
    キー名から期別情報を抽出
    例: "価格_第4期" -> ("価格", 4)
    """
    phase_match = re.search(r'_第(\d+)期$', key_name)
    if phase_match:
        base_key = key_name.replace(phase_match.group(0), '')
        period = int(phase_match.group(1))
        return base_key, period
    return key_name, None

def clean_price_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    価格情報をJSON形式でクレンジング
    例: "2685万円～3955万円" -> {"min": 2685, "max": 3955, "unit": "万円", "period": 4}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # 価格未定などのケース（nullとして処理）
    if "未定" in value or "要相談" in value:
        result["value"] = None
        if period is not None:
            result["period"] = period
        return result
    
    # 億円を含む価格の処理
    if "億" in value:
        # 億円の数値をすべて万円に変換
        prices_in_man = []
        
        # 億と万を含む価格を処理（例：1億2300万円）
        for match in re.finditer(r'(\d+(?:\.\d+)?)億(?:(\d+(?:\.\d+)?)万)?', value):
            oku = float(match.group(1))
            man = float(match.group(2)) if match.group(2) else 0
            total_man = oku * 10000 + man  # 億を万に変換して合計
            prices_in_man.append(total_man)
        
        # 万円のみの価格も抽出（億と組み合わさっていないもの）
        for match in re.finditer(r'(?<![億\d])(\d+(?:,\d{3})*(?:\.\d+)?)万', value):
            man = float(match.group(1).replace(',', ''))
            prices_in_man.append(man)
        
        if prices_in_man:
            result["unit"] = "万円"
            if len(prices_in_man) == 1:
                result["value"] = prices_in_man[0]
            else:
                result["min"] = min(prices_in_man)
                result["max"] = max(prices_in_man)
                # 平均値も追加
                result["value"] = (result["min"] + result["max"]) / 2
    else:
        # 万円を含む複雑な価格パターンの処理
        prices_in_unit = []
        
        # 万円パターンの処理（例：3989万5000円）
        if "万" in value:
            # パターン1: 「3989万5000円」のような形式
            man_yen_pattern = re.findall(r'(\d+(?:,\d{3})*)万(\d+(?:,\d{3})*)円', value)
            for man_part, yen_part in man_yen_pattern:
                man_val = float(man_part.replace(',', ''))
                yen_val = float(yen_part.replace(',', ''))
                # 万円単位に変換：3989万5000円 → 3989.5万円
                total_man = man_val + (yen_val / 10000)
                prices_in_unit.append(total_man)
            
            # パターン2: 「万円」のみ（例：3989万円）
            man_only_pattern = re.findall(r'(\d+(?:,\d{3})*)万円', value)
            for man_str in man_only_pattern:
                # 既にパターン1で処理されていないかチェック
                already_processed = False
                for m, y in man_yen_pattern:
                    if man_str == m:
                        already_processed = True
                        break
                if not already_processed:
                    man_val = float(man_str.replace(',', ''))
                    prices_in_unit.append(man_val)
            
            result["unit"] = "万円"
        else:
            # 通常の数値抽出
            numbers = re.findall(r'(\d+(?:,\d{3})*(?:\.\d+)?)', value)
            if not numbers:
                result["value"] = value
                if period is not None:
                    result["period"] = period
                return result
            
            # 単位を判定
            unit = "円"
            if "千円" in value:
                unit = "千円"
            
            result["unit"] = unit
            
            # カンマを除去して数値に変換
            for num in numbers:
                clean_num = float(num.replace(',', ''))
                prices_in_unit.append(clean_num)
        
        # 範囲表現（〜）がある場合
        if "～" in value or "〜" in value:
            if len(prices_in_unit) >= 2:
                result["min"] = min(prices_in_unit)
                result["max"] = max(prices_in_unit)
                # 平均値も追加
                result["value"] = (result["min"] + result["max"]) / 2
            elif len(prices_in_unit) == 1:
                result["value"] = prices_in_unit[0]
        else:
            # 単一の値
            if len(prices_in_unit) == 1:
                result["value"] = prices_in_unit[0]
            elif len(prices_in_unit) >= 2:
                # 複数の数値がある場合は範囲として扱う
                result["min"] = min(prices_in_unit)
                result["max"] = max(prices_in_unit)
                # 平均値も追加
                result["value"] = (result["min"] + result["max"]) / 2
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_price_band_to_json(value: str, raw_key: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    最多価格帯情報をJSON形式でクレンジング
    例: "3500万円台（7戸）" -> {"values": [{"price": 3500, "count": 7}], "value": 3500, "unit": "万円"}
    例: "3700万円台・3800万円台（各2戸）" -> {"values": [{"price": 3700, "count": 2}, {"price": 3800, "count": 2}], "value": 3750, "unit": "万円"}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # 価格未定などのケース（nullとして処理）
    if "未定" in value or "要相談" in value:
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    result = {"unit": "万円", "values": []}
    
    # 価格帯と戸数のパターンを厳密にチェック
    
    # パターン1: "5500万円台（2戸）" - 単一価格帯で括弧内に戸数
    single_pattern_match = re.match(r'^(\d+(?:,\d{3})*(?:\.\d+)?)万円台（(\d+)戸）$', value.strip())
    
    # パターン2: "5700万円台・5900万円台（各1戸）" - 複数価格帯で「各X戸」
    multi_pattern_match = re.match(r'^(.+?)（各(\d+)戸）$', value.strip())
    
    if single_pattern_match:
        # パターン1: 単一価格帯
        price_str = single_pattern_match.group(1)
        count_str = single_pattern_match.group(2)
        price = float(price_str.replace(',', ''))
        count = int(count_str)
        result["values"].append({"price": price, "count": count})
        
    elif multi_pattern_match:
        # パターン2: 複数価格帯（各X戸）
        price_part = multi_pattern_match.group(1)
        count = int(multi_pattern_match.group(2))
        
        # 価格部分が「・」で区切られているかチェック
        if '・' in price_part:
            price_items = price_part.split('・')
            valid_prices = []
            for item in price_items:
                price_match = re.match(r'(\d+(?:,\d{3})*(?:\.\d+)?)万円台$', item.strip())
                if price_match:
                    price = float(price_match.group(1).replace(',', ''))
                    valid_prices.append(price)
            
            if len(valid_prices) == len(price_items):  # 全ての価格が正しく抽出できた場合のみ
                for price in valid_prices:
                    result["values"].append({"price": price, "count": count})
            else:
                # 一部でも抽出できない場合は対応不可
                result["value"] = -1
                if period is not None:
                    result["period"] = period
                return result
        else:
            # 「・」区切りでない複数価格帯は対応不可
            result["value"] = -1
            if period is not None:
                result["period"] = period
            return result
    else:
        # パターン3: 単一価格帯（戸数情報なし）例：「3900万円台」
        single_band_match = re.match(r'^(\d+(?:,\d{3})*(?:\.\d+)?)万円台$', value.strip())
        if single_band_match:
            price_str = single_band_match.group(1)
            price = float(price_str.replace(',', ''))
            result["values"].append({"price": price, "count": 1})
        else:
            # 既知のパターンに当てはまらない場合は対応不可
            result["value"] = -1
            if period is not None:
                result["period"] = period
            return result
    
    # 平均価格を計算
    if result["values"]:
        # countがNoneでない項目のみで計算
        weighted_items = [item for item in result["values"] if item["count"] is not None]
        if weighted_items:
            total_price = sum(item["price"] * item["count"] for item in weighted_items)
            total_count = sum(item["count"] for item in weighted_items)
            if total_count > 0:
                result["value"] = total_price / total_count
            else:
                result["value"] = None
        else:
            # 全てのcountがNoneの場合は単純平均
            total_price = sum(item["price"] for item in result["values"])
            result["value"] = total_price / len(result["values"])
    else:
        result["value"] = None
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_area_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    面積情報をJSON形式でクレンジング
    例: "55.02m²～75.89m²" -> {"min": 55.02, "max": 75.89, "value": 65.455, "unit": "m^2", "period": 4}
    例: "43.27m2（13.08坪）（壁芯）" -> {"value": 43.27, "unit": "m^2", "tsubo": 13.08, "measurement_type": "壁芯"}
    例: "56.44m2（登記）" -> {"value": 56.44, "unit": "m^2", "tsubo": 17.07, "measurement_type": "登記"}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # 数値を抽出
    numbers = re.findall(r'(\d+(?:\.\d+)?)', value)
    if not numbers:
        result["value"] = value
        if period is not None:
            result["period"] = period
        return result
    
    # 単位を判定
    if "㎡" in value or "m²" in value or "m2" in value:
        result["unit"] = "m^2"
    elif "坪" in value:
        result["unit"] = "坪"
    else:
        result["unit"] = "m^2"  # デフォルト
    
    # 数値に変換
    clean_numbers = [float(num) for num in numbers]
    
    # 範囲かどうかを判定（～がある場合）
    has_range = "～" in value or "〜" in value
    
    if has_range and len(clean_numbers) >= 2:
        # 範囲の場合：min, max, valueを設定
        # m^2の値のみを使用（坪の値は除外）
        area_numbers = []
        
        if result["unit"] == "m^2":
            # m^2の値を抽出（～の前後）
            range_parts = re.split(r'[～〜]', value)
            for part in range_parts:
                if any(unit in part for unit in ["㎡", "m²", "m2"]):
                    area_match = re.search(r'(\d+(?:\.\d+)?)', part)
                    if area_match:
                        area_numbers.append(float(area_match.group(1)))
        
        if len(area_numbers) >= 2:
            result["min"] = min(area_numbers)
            result["max"] = max(area_numbers)
            result["value"] = (result["min"] + result["max"]) / 2
        else:
            # フォールバック：すべての数値から最初の2つを使用
            result["min"] = clean_numbers[0]
            result["max"] = clean_numbers[1] if len(clean_numbers) > 1 else clean_numbers[0]
            result["value"] = (result["min"] + result["max"]) / 2
    else:
        # 単一値または複数値があっても範囲でない場合
        # 最初の数値を面積として扱い、2番目があれば坪数として扱う
        result["value"] = clean_numbers[0]
        
        # 坪数が明示的に書かれている場合（例：43.27m2（13.08坪））
        if len(clean_numbers) >= 2 and "坪" in value and result["unit"] == "m^2":
            # 坪の数値を直接使用
            tsubo_match = re.search(r'(\d+(?:\.\d+)?)坪', value)
            if tsubo_match:
                result["tsubo"] = float(tsubo_match.group(1))
    
    # 測定タイプ（壁芯・登記）を抽出
    if "壁芯" in value:
        result["measurement_type"] = "壁芯"
    elif "登記" in value:
        result["measurement_type"] = "登記"
    
    # 坪数を計算（m^2の場合で、まだ設定されていない場合）
    if result["unit"] == "m^2" and "tsubo" not in result:
        if "value" in result:
            result["tsubo"] = round(result["value"] / 3.30579, 2)
        if "min" in result:
            result["min_tsubo"] = round(result["min"] / 3.30579, 2)
        if "max" in result:
            result["max_tsubo"] = round(result["max"] / 3.30579, 2)
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_multiple_area_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    複数面積情報をJSON形式でクレンジング（バルコニー面積、その他面積等）
    例: "バルコニー面積：3.79m2、専用庭：27.7m2（使用料1000円／月）" 
        -> {"areas": [{"type": "バルコニー面積", "value": 3.79, "unit": "m^2", "tsubo": 1.15}, 
                     {"type": "専用庭", "value": 27.7, "unit": "m^2", "tsubo": 8.38, "usage_fee": 1000}]}
    例: "バルコニー面積：15.56m2" 
        -> {"areas": [{"type": "バルコニー面積", "value": 15.56, "unit": "m^2", "tsubo": 4.71}]}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"areas": []}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {"areas": []}
    
    # 「、」で分割して各面積項目を処理
    parts = re.split(r'[,、，]', value)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        area_info = {}
        
        # 面積タイプを抽出（：より前の部分）
        if "：" in part:
            type_part, value_part = part.split("：", 1)
            area_info["type"] = type_part.strip()
            area_value = value_part.strip()
        else:
            # ：がない場合は全体を値として扱う
            area_info["type"] = "その他"
            area_value = part
        
        # 数値を抽出
        numbers = re.findall(r'(\d+(?:\.\d+)?)', area_value)
        if not numbers:
            continue
            
        # 面積値を設定（最初の数値）
        area_info["value"] = float(numbers[0])
        
        # 単位を判定
        if "㎡" in area_value or "m²" in area_value or "m2" in area_value:
            area_info["unit"] = "m^2"
        elif "坪" in area_value:
            area_info["unit"] = "坪"
        else:
            area_info["unit"] = "m^2"  # デフォルト
        
        # 坪数を計算
        if area_info["unit"] == "m^2":
            area_info["tsubo"] = round(area_info["value"] / 3.30579, 2)
        
        # 使用料を抽出
        usage_fee_match = re.search(r'使用料(\d+)円', area_value)
        if usage_fee_match:
            area_info["usage_fee"] = int(usage_fee_match.group(1))
        elif "使用料無" in area_value:
            area_info["usage_fee"] = 0
        
        # 測定タイプ（壁芯・登記）を抽出
        if "壁芯" in area_value:
            area_info["measurement_type"] = "壁芯"
        elif "登記" in area_value:
            area_info["measurement_type"] = "登記"
        
        result["areas"].append(area_info)
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_layout_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    間取り情報をJSON形式でクレンジング
    例: "1LDK～3LDK" -> {"values": ["1LDK", "2LDK", "3LDK"]}
    例: "3LDK・3LDK+2S（納戸）" -> {"values": ["3LDK", "3LDK+2S（納戸）"]}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # （納戸）などの説明文を除去
    value = re.sub(r'[（(][^）)]*納戸[^）)]*[）)]', '', value)
    
    result = {}
    
    # 間取りパターンを抽出
    layout_items = []
    
    # 範囲表現（～）がある場合の処理
    if '～' in value or '〜' in value:
        # 範囲を～で分割
        range_parts = re.split(r'[～〜]', value)
        
        if len(range_parts) == 2:
            # 各部分から間取りを抽出
            for part in range_parts:
                part = part.strip()
                layout_match = re.search(r'(\d+(?:[LDKSR]+)(?:[+＋]\d*[LDKSR]*)*)', part.upper())
                if layout_match:
                    matched_layout = layout_match.group(1)
                    # 間取りパターンとして有効な場合のみ追加
                    if len(matched_layout) <= 10 and re.match(r'^\d+[LDKSR]+(?:[+＋]\d*[LDKSR]*)*$', matched_layout):
                        layout_items.append(matched_layout)
            
            # 簡単な展開が可能な場合のみ展開（例：1LDK～3LDK）
            if len(layout_items) == 2:
                first_layout = layout_items[0]
                second_layout = layout_items[1]
                
                # 単純なパターン（数字+同じ文字列）の場合のみ展開
                first_match = re.match(r'^(\d+)([LDKSR]+)$', first_layout)
                second_match = re.match(r'^(\d+)([LDKSR]+)$', second_layout)
                
                if first_match and second_match:
                    start_num = int(first_match.group(1))
                    start_type = first_match.group(2)
                    end_num = int(second_match.group(1))
                    end_type = second_match.group(2)
                    
                    # 同じタイプで数字のみ異なる場合は展開
                    if start_type == end_type and start_num < end_num:
                        layout_items = []
                        for i in range(start_num, end_num + 1):
                            layout_items.append(f"{i}{start_type}")
        else:
            # 複雑な範囲パターンは通常の処理に任せる
            all_layouts = re.findall(r'(\d+(?:[LDKSR]+)(?:[+＋]\d*[LDKSR]*)*)', value.upper())
            for layout in all_layouts:
                if len(layout) <= 10 and re.match(r'^\d+[LDKSR]+(?:[+＋]\d*[LDKSR]*)*$', layout):
                    layout_items.append(layout)
    else:
        # ・（中点）で分割
        parts = re.split(r'[・]', value)
        
        for part in parts:
            part = part.strip()
            if part:
                # 各部分から間取りパターンを抽出
                # より厳密な間取りパターン: 数字 + L/D/K/S/R の組み合わせ
                layout_match = re.search(r'(\d+(?:[LDKSR]+)(?:[+＋]\d*[LDKSR]*)*)', part.upper())
                if layout_match:
                    # マッチした部分が間取りとして妥当かチェック
                    matched_layout = layout_match.group(1)
                    # 間取りパターンとして有効な場合のみ追加（LDKSRのみを含み、長すぎない）
                    if len(matched_layout) <= 10 and re.match(r'^\d+[LDKSR]+(?:[+＋]\d*[LDKSR]*)*$', matched_layout):
                        layout_items.append(matched_layout)
    
    if layout_items:
        # 重複を除去してソート
        unique_layouts = list(set(layout_items))
        unique_layouts.sort()
        result["values"] = unique_layouts
    else:
        result["value"] = value
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_date_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    日付情報をJSON形式でクレンジング
    例: "2023年12月下旬" -> {"year": 2023, "month": 12, "period_text": "下旬", "period": 4}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # 年月日を抽出（日付がある場合）
    year_month_day_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', value)
    if year_month_day_match:
        year = int(year_month_day_match.group(1))
        month = int(year_month_day_match.group(2))
        day = int(year_month_day_match.group(3))
        result["year"] = year
        result["month"] = month
        result["day"] = day
        result["estimated_date"] = f"{year}-{month:02d}-{day:02d}"
    else:
        # 年月を抽出
        year_month_match = re.search(r'(\d{4})年(\d{1,2})月', value)
        if year_month_match:
            year = int(year_month_match.group(1))
            month = int(year_month_match.group(2))
            result["year"] = year
            result["month"] = month
            
            # 上旬・中旬・下旬を判定
            if "上旬" in value:
                result["period_text"] = "上旬"
                result["estimated_date"] = f"{year}-{month:02d}-05"
            elif "中旬" in value:
                result["period_text"] = "中旬"
                result["estimated_date"] = f"{year}-{month:02d}-15"
            elif "下旬" in value:
                result["period_text"] = "下旬"
                result["estimated_date"] = f"{year}-{month:02d}-25"
            else:
                result["estimated_date"] = f"{year}-{month:02d}-01"
        else:
            result["value"] = value
    
    # 完成済み・竣工済みなどのステータス
    if any(status in value for status in ["完成済", "竣工済", "竣工"]):
        result["completed"] = True
    
    # 予定
    if "予定" in value:
        result["tentative"] = True
    
    # 即入居可などの特殊ケース
    if "即" in value:
        result["immediate"] = True
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_management_fee_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    管理費などの月額費用をJSON形式でクレンジング
    例: "9300円～1万3800円／月" -> {"min": 9300, "max": 13800, "unit": "円", "frequency": "月", "period": 4}
    例: "1万7744円／月（一部委託(管理員なし)）" -> {"value": 17744, "unit": "円", "frequency": "月", "management_type": "一部委託", "note": "管理員なし"}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # 「未定」「金額未定」などのケース（勤務形態未定は除く）
    undefined_keywords = ["金額未定", "価格未定", "未確定", "未決定", "要相談", "応相談"]
    if any(word in value for word in undefined_keywords) or \
       (value.strip() == "未定"):  # 「未定」単体の場合のみ
        result["is_undefined"] = True
        result["value"] = None
        if period is not None:
            result["period"] = period
        return result
    
    # 管理体制情報を抽出
    if "自主管理" in value:
        result["management_type"] = "自主"
    elif "一部委託" in value:
        result["management_type"] = "一部委託"
    elif "委託" in value:
        result["management_type"] = "委託"
    
    # 勤務形態情報を抽出
    work_patterns = {
        "通勤": "通勤",
        "巡回": "巡回", 
        "常駐": "常駐",
        "管理員なし": "管理員なし",
        "勤務形態未定": "未定"
    }
    
    for pattern, work_type in work_patterns.items():
        if pattern in value:
            result["work_style"] = work_type
            break
    
    # 括弧内の追加情報を抽出（管理体制・勤務形態・一括払い以外）
    paren_matches = re.findall(r'[（(]([^）)]*)[）)]', value)
    for note_text in paren_matches:
        # 管理体制・勤務形態・一括払い情報でない場合はnoteとして保存
        is_excluded = any(keyword in note_text for keyword in 
                         ["自主管理", "委託", "通勤", "巡回", "常駐", "管理員", "勤務形態", "一括"])
        if not is_excluded and note_text.strip():
            result["note"] = note_text.strip()
    
    # 内訳がある場合は分離して処理
    breakdown_match = re.search(r'【内訳】(.+)$', value)
    if breakdown_match:
        main_part = value[:breakdown_match.start()].strip()
        breakdown_part = breakdown_match.group(1)
        result["breakdown"] = breakdown_part
    else:
        main_part = value
    
    # メイン部分から金額を抽出（「万」を含む場合を正しく処理）
    amounts = []
    
    # パターン1: 「1万7744円」のような形式
    man_pattern = re.findall(r'(\d+)万(\d+)円', main_part)
    for man_part, remaining_part in man_pattern:
        total_amount = int(man_part) * 10000 + int(remaining_part)
        amounts.append(total_amount)
    
    # パターン2: 「万円」単位（「10万円」など）
    man_only_pattern = re.findall(r'(\d+(?:,\d{3})*)万円', main_part)
    for man_str in man_only_pattern:
        # 既にパターン1で処理されていないかチェック
        already_processed = False
        for m, r in man_pattern:
            if man_str == m:
                already_processed = True
                break
        if not already_processed:
            amounts.append(int(man_str.replace(',', '')) * 10000)
    
    # パターン3: 通常の円表記
    yen_pattern = re.findall(r'(\d+(?:,\d{3})*)円', main_part)
    for yen_str in yen_pattern:
        # 万円パターンに含まれていない場合のみ追加
        already_processed = False
        for m, r in man_pattern:
            if yen_str == r:
                already_processed = True
                break
        if not already_processed:
            amounts.append(int(yen_str.replace(',', '')))
    
    if amounts:
        if len(amounts) == 1:
            result["value"] = amounts[0]
        elif len(amounts) >= 2:
            result["min"] = min(amounts)
            result["max"] = max(amounts)
            # 平均値を追加
            result["value"] = (result["min"] + result["max"]) / 2
        
        result["unit"] = "円"
        
        # 頻度を判定
        if "一括" in value:
            result["frequency"] = "一括"
        elif "月" in value:
            result["frequency"] = "月"
        elif "年" in value:
            result["frequency"] = "年"
        else:
            # キー名や値から判定
            if any(keyword in raw_key for keyword in ["準備金", "基金"]) or \
               any(keyword in value for keyword in ["準備金", "基金", "一時金", "一括払い"]):
                result["frequency"] = "一括"
            else:
                result["frequency"] = "月"  # デフォルト
    else:
        result["value"] = value
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_number_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    数値をJSON形式でクレンジング（総戸数、階数など）
    例: "128戸" -> {"value": 128, "unit": "戸", "period": 4}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # 数値を抽出
    number_match = re.search(r'(\d+(?:\.\d+)?)', value.replace(',', ''))
    if number_match:
        num_str = number_match.group(1)
        if '.' in num_str:
            result["value"] = float(num_str)
        else:
            result["value"] = int(num_str)
        
        # 単位を抽出
        unit_match = re.search(r'(\D+)', value.replace(',', '').replace(num_str, ''))
        if unit_match:
            unit = unit_match.group(1).strip()
            if unit:
                result["unit"] = unit
    else:
        result["value"] = value
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_units_to_json(value: str, raw_key: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    戸数情報をJSON形式でクレンジング（総戸数、今回販売戸数を統一）
    例: "128戸" + "総戸数" -> {"value": 128, "unit": "戸", "is_total": true}
    例: "50戸" + "今回販売戸数" -> {"value": 50, "unit": "戸", "is_current_sale": true}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # 数値を抽出
    number_match = re.search(r'(\d+(?:\.\d+)?)', value.replace(',', ''))
    if number_match:
        num_str = number_match.group(1)
        if '.' in num_str:
            result["value"] = float(num_str)
        else:
            result["value"] = int(num_str)
        
        # 単位を抽出（括弧の前まで）
        # 数値の後から括弧または文末までの間の文字を取得
        after_number = value[value.find(num_str) + len(num_str):]
        unit_match = re.match(r'^([^（(]+)', after_number)
        if unit_match:
            unit = unit_match.group(1).strip()
            if unit:
                result["unit"] = unit
        
        # 括弧内の追加情報を抽出
        paren_match = re.search(r'[（(](.+?)[）)]', value)
        if paren_match:
            result["note"] = paren_match.group(1)
    else:
        result["value"] = value
    
    # 総戸数か今回販売戸数かを判定
    if "総" in raw_key:
        result["is_total"] = True
    elif "今回" in raw_key:
        result["is_current_sale"] = True
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_boolean_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    有無や可否をJSON形式でクレンジング
    例: "有" -> {"value": true, "period": 4}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # True判定
    if any(word in value for word in ["有", "あり", "可", "可能", "○"]):
        result["value"] = True
    # False判定
    elif any(word in value for word in ["無", "なし", "不可", "×", "-"]):
        result["value"] = False
    else:
        result["value"] = value
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_text_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    テキストをJSON形式でクレンジング
    例: "テキスト" -> {"value": "テキスト", "period": 4}
    長すぎるまたは分析に重要でないテキストは value: null に設定
    """
    result = {}
    
    if not value or value.strip() == "":
        result["value"] = None
    else:
        value = value.strip()
        
        # 長すぎるテキストまたは分析に重要でないパターンをチェック
        if _should_nullify_text(value):
            result["value"] = None
        else:
            result["value"] = value
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_access_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    交通アクセス情報をJSON形式でクレンジング
    例: "ＪＲ京浜東北線「大宮」歩8分\t[乗り換え案内]\t東武野田線「北大宮」歩17分"
    -> {"routes": [
        {"line": "ＪＲ京浜東北線", "station": "大宮", "method": "歩", "time": 8},
        {"line": "東武野田線", "station": "北大宮", "method": "歩", "time": 17}
    ]}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # タブや改行で分割してルートを抽出
    routes = []
    parts = re.split(r'[\t\n]', value)
    
    for part in parts:
        part = part.strip()
        if not part or "[乗り換え案内]" in part:
            continue
        
        # パターン: 路線名「駅名」移動手段+数字分
        match = re.match(r'(.+?)「(.+?)」(.+?)(\d+)分', part)
        if match:
            line = match.group(1).strip()
            station = match.group(2).strip()
            method = match.group(3).strip()
            time = int(match.group(4))
            
            routes.append({
                "line": line,
                "station": station,
                "method": method,
                "time": time
            })
        else:
            # バス路線などの特殊ケース
            # 例: "バス10分（バス停「○○」まで歩5分）"
            bus_match = re.match(r'バス(\d+)分.*?バス停「(.+?)」.*?歩(\d+)分', part)
            if bus_match:
                routes.append({
                    "line": "バス",
                    "station": bus_match.group(2),
                    "method": "バス",
                    "time": int(bus_match.group(1)),
                    "walk_to_stop": int(bus_match.group(3))
                })
            # 車のケース
            elif "車" in part:
                car_match = re.search(r'車(\d+)分', part)
                if car_match:
                    routes.append({
                        "line": "車",
                        "station": "",
                        "method": "車",
                        "time": int(car_match.group(1))
                    })
    
    if routes:
        result["routes"] = routes
    else:
        # パースできない場合は元の値を保持
        result["value"] = value
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_zoning_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    用途地域情報をJSON形式でクレンジング
    例: "商業、１種住居" -> {"values": ["商業", "１種住居"]}
    例: "商業" -> {"values": ["商業"]}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"values": []}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # カンマや読点で分割
    zones = []
    parts = re.split(r'[,、，]', value)
    
    for part in parts:
        part = part.strip()
        if part and part != "-":
            zones.append(part)
    
    if zones:
        result["values"] = zones  # 常にリストとして保存
    else:
        result["values"] = []
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_force_null_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    強制的にnullを返すクレンジング関数
    """
    result = {"value": None}
    if period is not None:
        result["period"] = period
    return result

def clean_other_expenses_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    その他諸経費をJSON形式でクレンジング
    額が大きく頻出する項目のみを抽出し、その他は保存しない
    
    抽出対象項目:
    - 駐車場関連（専用駐車場使用料等）
    - 地代
    - 保証金系（敷金、地代保証金等）
    - 解体関連（解体準備金、解体費用積立基金等）
    - 災害積立基金
    - メンテナンスサービス料
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # "-" の場合は null
    if value == "-":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    result = {"expenses": []}
    
    # カンマで分割して各項目を処理
    items = [item.strip() for item in re.split(r'[、,]', value)]
    
    # 抽出対象のキーワードパターン
    target_patterns = {
        "駐車場": r'(.*駐車場[^：]*)[:：]\s*([0-9万,～〜円]+)(?:[／/](.+))?',
        "地代": r'(地代)[:：]\s*([0-9万,～〜円]+)(?:[／/](.+))?',
        "敷金": r'(敷金)[:：]\s*([0-9万,～〜円]+)(?:[／/](.+))?',
        "保証金": r'(.*保証金[^：]*)[:：]\s*([0-9万,～〜円]+)(?:[／/](.+))?',
        "解体": r'(.*解体[^：]*)[:：]\s*([0-9万,～〜円]+)(?:[／/](.+))?',
        "災害積立": r'(災害積立[^：]*)[:：]\s*([0-9万,～〜円]+)(?:[／/](.+))?',
        "メンテナンス": r'(.*メンテナンス[^：]*)[:：]\s*([0-9万,～〜円]+)(?:[／/](.+))?'
    }
    
    found_any = False
    
    for item in items:
        if not item.strip():
            continue
            
        for category, pattern in target_patterns.items():
            match = re.match(pattern, item.strip(), re.IGNORECASE)
            if match:
                item_name = match.group(1).strip()
                amount_str = match.group(2).strip()
                frequency_str = match.group(3).strip() if match.group(3) else ""
                
                # 金額を解析
                expense_item = {"name": item_name, "category": category}
                
                # 未定の場合
                if "未定" in amount_str or "金額未定" in amount_str:
                    expense_item["is_undefined"] = True
                    expense_item["value"] = None
                    expense_item["unit"] = "円"
                    expense_item["frequency"] = frequency_str if frequency_str else "月"
                    result["expenses"].append(expense_item)
                    found_any = True
                    break
                
                # 金額を抽出して解析（範囲対応）
                amounts = []
                
                # 範囲の場合（「1万940円～1万4080円」など）
                if '～' in amount_str or '〜' in amount_str:
                    # すべての万円パターンを抽出
                    man_patterns = re.findall(r'(\d+)万(\d+)円', amount_str)
                    for man_part, yen_part in man_patterns:
                        amounts.append(int(man_part) * 10000 + int(yen_part))
                    
                    # 万円のみパターンを抽出（万+数字円の形式でないもの）
                    # 先に万+数字円のパターンを除外したテキストで処理
                    temp_str = amount_str
                    for man_part, yen_part in man_patterns:
                        temp_str = temp_str.replace(f'{man_part}万{yen_part}円', '')
                    
                    man_only_patterns = re.findall(r'(\d+(?:,\d{3})*)万円', temp_str)
                    for man_str in man_only_patterns:
                        amount_val = int(man_str.replace(',', '')) * 10000
                        amounts.append(amount_val)
                    
                    # 通常の円表記（既に処理済みでないもの）
                    temp_str2 = temp_str
                    for man_str in man_only_patterns:
                        temp_str2 = temp_str2.replace(f'{man_str}万円', '')
                    
                    yen_patterns = re.findall(r'(\d+(?:,\d{3})*)円', temp_str2)
                    for yen_str in yen_patterns:
                        amount_val = int(yen_str.replace(',', ''))
                        if amount_val not in amounts and amount_val < 1000000:  # 100万円未満の円
                            amounts.append(amount_val)
                else:
                    # 単一金額の場合
                    amount = 0
                    
                    # パターン1: 「1万5000円」のような形式
                    man_pattern = re.search(r'(\d+)万(\d+)円', amount_str)
                    if man_pattern:
                        man_part = int(man_pattern.group(1))
                        yen_part = int(man_pattern.group(2))
                        amount = man_part * 10000 + yen_part
                    else:
                        # パターン2: 「10万円」のような形式
                        man_only = re.search(r'(\d+(?:,\d{3})*)万円', amount_str)
                        if man_only:
                            amount = int(man_only.group(1).replace(',', '')) * 10000
                        else:
                            # パターン3: 通常の円表記
                            yen_match = re.search(r'(\d+(?:,\d{3})*)円', amount_str)
                            if yen_match:
                                amount = int(yen_match.group(1).replace(',', ''))
                    
                    if amount > 0:
                        amounts = [amount]
                
                if amounts:
                    if len(amounts) == 1:
                        expense_item["value"] = amounts[0]
                    else:
                        expense_item["min"] = min(amounts)
                        expense_item["max"] = max(amounts)
                        expense_item["value"] = (expense_item["min"] + expense_item["max"]) / 2
                    
                    expense_item["unit"] = "円"
                    
                    # 頻度の判定
                    if frequency_str:
                        if "一括" in frequency_str:
                            expense_item["frequency"] = "一括"
                        elif "月" in frequency_str:
                            expense_item["frequency"] = "月"
                        elif "年" in frequency_str:
                            expense_item["frequency"] = "年"
                        else:
                            expense_item["frequency"] = frequency_str
                    else:
                        # デフォルトは月額と仮定
                        expense_item["frequency"] = "月"
                    
                    result["expenses"].append(expense_item)
                    found_any = True
                break  # パターンマッチしたら次の項目へ
    
    # 抽出できた項目がない場合はnull
    if not found_any:
        result = {"value": None}
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_restrictions_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    制限事項をJSON形式でクレンジング（複数制限項目をリスト管理）
    例: "準防火地域、60m高度地区" -> {"restrictions": ["準防火地域", "60m高度地区"]}
    例: "防火地域" -> {"restrictions": ["防火地域"]}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"restrictions": []}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # "-" の場合は空のリスト
    if value == "-":
        result = {"restrictions": []}
        if period is not None:
            result["period"] = period
        return result
    
    result = {"restrictions": []}
    
    # 「、」や「・」で分割して各制限項目を処理
    parts = re.split(r'[,、，・]', value)
    
    for part in parts:
        part = part.strip()
        if part and part != "-":
            # 複雑な条件文の場合（例: "東側道路境界線から11m以内：防火地域"）
            if "：" in part:
                # 条件全体を一つの制限として扱う
                result["restrictions"].append(part)
            else:
                # 単純な制限項目
                result["restrictions"].append(part)
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_expiry_date_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    取引条件有効期限をYYYY-MM-DD形式でクレンジング
    例: "2025年3月26日" -> {"date": "2025-03-26"}
    例: "2029年12月31日" -> {"date": "2029-12-31"}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"date": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # "-" の場合はnull
    if value == "-":
        result = {"date": None}
        if period is not None:
            result["period"] = period
        return result
    
    result = {}
    
    # 日本語日付形式をパース（例: "2025年3月26日"）
    date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', value)
    if date_match:
        year = date_match.group(1)
        month = date_match.group(2).zfill(2)  # 0埋め
        day = date_match.group(3).zfill(2)    # 0埋め
        result["date"] = f"{year}-{month}-{day}"
    else:
        # パースできない場合は元の値を保持
        result["date"] = value
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_company_info_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    会社情報をJSON形式でクレンジング（複数会社の詳細情報を分類）
    例: "＜事業主・売主＞国土交通大臣（14）第1786 号...第一交通産業株式会社..." 
        -> {"companies": [{"role": "事業主・売主", "license": "国土交通大臣（14）第1786号", "name": "第一交通産業株式会社", ...}]}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"companies": []}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # "-" の場合は空のリスト
    if value == "-":
        result = {"companies": []}
        if period is not None:
            result["period"] = period
        return result
    
    result = {"companies": []}
    
    # タブ文字で複数会社を分割
    company_blocks = value.split('\t')
    
    for block in company_blocks:
        block = block.strip()
        if not block:
            continue
        
        company_info = {}
        
        # 役割を抽出（＜＞で囲まれた部分）
        role_match = re.search(r'＜([^＞]+)＞', block)
        if role_match:
            company_info["role"] = role_match.group(1)
            # 役割部分を除去
            block = re.sub(r'＜[^＞]+＞', '', block).strip()
        
        # 免許番号を抽出
        license_patterns = [
            r'国土交通大臣\s*\（(\d+)\）\s*第(\d+)\s*号',
            r'([^知事]*?)知事\s*\（(\d+)\）\s*第(\d+)\s*号'
        ]
        
        licenses = []
        for pattern in license_patterns:
            matches = re.finditer(pattern, block)
            for match in matches:
                if "国土交通大臣" in pattern:
                    licenses.append(f"国土交通大臣（{match.group(1)}）第{match.group(2)}号")
                else:
                    licenses.append(f"{match.group(1)}知事（{match.group(2)}）第{match.group(3)}号")
        
        if licenses:
            company_info["licenses"] = licenses
        
        # 建設業許可を抽出
        construction_matches = re.findall(r'建設業許可[/／]([^　\s]+)', block)
        if construction_matches:
            company_info["construction_permits"] = construction_matches
        
        # 協会・団体会員情報を抽出
        memberships = []
        membership_patterns = [
            r'\(公社\)([^　\s会員]+)会員',
            r'\(一社\)([^　\s会員]+)会員',
            r'([^　\s（）]+)協議会加盟'
        ]
        
        for pattern in membership_patterns:
            matches = re.findall(pattern, block)
            for match in matches:
                if match not in memberships:
                    memberships.append(match)
        
        if memberships:
            company_info["memberships"] = memberships
        
        # 会社名を抽出（株式会社等を含む）
        company_name_patterns = [
            r'(株式会社[^〒\n\t　]+)',
            r'([^株式会社]*株式会社[^〒\n\t　]*)',
            r'([^〒\n\t　]+株式会社)',
            r'([^〒\n\t　]*会社[^〒\n\t　]*)'
        ]
        
        for pattern in company_name_patterns:
            match = re.search(pattern, block)
            if match:
                name = match.group(1).strip()
                # ノイズ除去
                name = re.sub(r'[（）\(\)].*?[（）\(\)]', '', name)
                name = re.sub(r'第\d+.*', '', name)
                company_info["name"] = name.strip()
                break
        
        # 住所を抽出（〒以降）
        address_match = re.search(r'〒(\d{3}-\d{4})\s*([^〒]+?)(?=株式会社|$)', block)
        if address_match:
            company_info["postal_code"] = address_match.group(1)
            company_info["address"] = address_match.group(2).strip()
        
        # 会社情報が抽出できた場合のみ追加
        if any(key in company_info for key in ["name", "role", "licenses"]):
            result["companies"].append(company_info)
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_delivery_date_to_json(value: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    引渡時期をJSON形式でクレンジング
    例: "2024年1月25日" -> {"year": 2024, "month": 1, "day": 25, "estimated_date": "2024-01-25"}
    例: "即引渡可" -> {"type": "immediate", "note": null}
    例: "相談" -> {"type": "negotiable"}
    例: "契約後3ヶ月" -> {"type": "after_contract", "months": 3}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # "-" の場合はnull
    if value == "-":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    result = {}
    
    # 即引渡可パターン
    if "即引渡可" in value or "即入居可" in value:
        result["type"] = "immediate"
        # 条件付きの場合（諸手続き完了後など）
        if "諸手続" in value or "手続" in value:
            result["note"] = "諸手続き完了後"
        elif "※" in value:
            note_match = re.search(r'※(.+)', value)
            if note_match:
                result["note"] = note_match.group(1).strip()
        if period is not None:
            result["period"] = period
        return result
    
    # 相談パターン
    if value == "相談" or value == "要相談":
        result["type"] = "negotiable"
        if period is not None:
            result["period"] = period
        return result
    
    # 契約後パターン
    contract_match = re.search(r'契約後(\d+(?:\.\d+)?)ヶ月', value)
    if contract_match:
        result["type"] = "after_contract"
        result["months"] = float(contract_match.group(1))
        if period is not None:
            result["period"] = period
        return result
    
    # 完全な日付パターン（年月日）
    full_date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', value)
    if full_date_match:
        year = int(full_date_match.group(1))
        month = int(full_date_match.group(2))
        day = int(full_date_match.group(3))
        result["year"] = year
        result["month"] = month
        result["day"] = day
        result["estimated_date"] = f"{year:04d}-{month:02d}-{day:02d}"
        if period is not None:
            result["period"] = period
        return result
    
    # 年月パターン（日なし） - 「予定」も含む
    year_month_match = re.search(r'(\d{4})年(\d{1,2})月', value)
    if year_month_match:
        year = int(year_month_match.group(1))
        month = int(year_month_match.group(2))
        result["year"] = year
        result["month"] = month
        
        # 予定かどうかを記録
        if "予定" in value:
            result["is_planned"] = True
        
        # 期間指定（上旬、中旬、下旬、初旬、末）
        if "上旬" in value or "初旬" in value:
            result["period_text"] = "上旬"
            result["estimated_date"] = f"{year:04d}-{month:02d}-05"
        elif "中旬" in value:
            result["period_text"] = "中旬"
            result["estimated_date"] = f"{year:04d}-{month:02d}-15"
        elif "下旬" in value:
            result["period_text"] = "下旬"
            result["estimated_date"] = f"{year:04d}-{month:02d}-25"
        elif "末" in value:
            result["period_text"] = "末"
            # 月末日を計算
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            result["estimated_date"] = f"{year:04d}-{month:02d}-{last_day:02d}"
        else:
            # 期間指定なしの場合は月初
            result["estimated_date"] = f"{year:04d}-{month:02d}-01"
        
        if period is not None:
            result["period"] = period
        return result
    
    # その他のパターンは元の値を保持
    result["value"] = value
    if period is not None:
        result["period"] = period
    
    return result

def create_type_schema(base_key: str, sample_values: List[str]) -> Dict[str, Any]:
    """
    サンプルデータから型スキーマを生成
    """
    # 期別情報を含むかチェック
    has_period = "_第" in base_key
    
    # 交通アクセスの特殊処理
    if "交通" in base_key or "アクセス" in base_key:
        return {
            "base_type": "array",
            "data_type": "access",
            "fields": ["routes"],
            "route_fields": ["line", "station", "method", "time"],
            "period_aware": has_period
        }
    
    # 用途地域の特殊処理
    if "用途地域" in base_key:
        return {
            "base_type": "array",
            "data_type": "zoning",
            "fields": ["values"],
            "period_aware": has_period
        }
    
    # 複数面積の特殊処理（その他面積、バルコニー面積等）
    if ("その他面積" in base_key or "バルコニー面積" in base_key or 
        any("面積" in base_key and "：" in str(v) for v in sample_values[:5] if v) or
        any("バルコニー面積" in str(v) for v in sample_values[:5] if v)):
        return {
            "base_type": "array",
            "data_type": "multiple_area",
            "fields": ["areas"],
            "area_fields": ["type", "value", "unit", "tsubo", "usage_fee", "measurement_type"],
            "period_aware": has_period
        }
    
    # 制限事項の特殊処理
    if "制限事項" in base_key:
        return {
            "base_type": "array",
            "data_type": "restrictions",
            "fields": ["restrictions"],
            "period_aware": has_period
        }
    
    # 取引条件有効期限の特殊処理
    if "取引条件有効期限" in base_key:
        return {
            "base_type": "single",
            "data_type": "expiry_date",
            "fields": ["date"],
            "period_aware": has_period
        }
    
    # 会社情報の特殊処理
    if "会社情報" in base_key:
        return {
            "base_type": "array",
            "data_type": "company_info",
            "fields": ["companies"],
            "company_fields": ["role", "name", "licenses", "construction_permits", "memberships", "postal_code", "address"],
            "period_aware": has_period
        }
    
    # 引渡時期の特殊処理
    if "引渡" in base_key and "時期" in base_key:
        return {
            "base_type": "single",
            "data_type": "delivery_date",
            "fields": ["type", "year", "month", "day", "estimated_date", "period_text", "months", "note", "is_planned", "value"],
            "period_aware": has_period
        }
    
    # 敷地権利形態の特殊処理（強制null）
    if "敷地" in base_key and "権利" in base_key:
        return {
            "base_type": "null",
            "data_type": "force_null",
            "fields": ["value"],
            "period_aware": has_period
        }
    
    # 販売スケジュールの特殊処理（強制null）
    if "販売スケジュール" in base_key:
        return {
            "base_type": "null",
            "data_type": "force_null",
            "fields": ["value"],
            "period_aware": has_period
        }
    
    
    # サンプルデータの分析
    has_range = any("～" in str(v) for v in sample_values[:10] if v)
    has_numeric = any(re.search(r'\d+', str(v)) for v in sample_values[:10] if v)
    has_boolean_words = any(any(word in str(v) for word in ["有", "無", "あり", "なし", "可", "不可", "○", "×"]) 
                           for v in sample_values[:10] if v)
    has_date = any(re.search(r'\d{4}年', str(v)) for v in sample_values[:10] if v)
    
    # 基本型を決定
    if has_boolean_words and not has_numeric:
        base_type = "boolean"
        data_type = "boolean"
        fields = ["value"]
    elif has_date:
        base_type = "date"
        data_type = "date"
        fields = ["year", "month", "period_text", "estimated_date"]
    elif has_range and has_numeric:
        base_type = "range"
        if "価格" in base_key or "費" in base_key:
            data_type = "money"
            fields = ["min", "max", "unit"]
        elif "面積" in base_key:
            data_type = "area"
            fields = ["min", "max", "unit", "tsubo", "measurement_type"]
        else:
            data_type = "number"
            fields = ["min", "max", "unit"]
    elif has_numeric and not has_range:
        base_type = "single"
        if "価格" in base_key or "費" in base_key:
            data_type = "money"
            fields = ["value", "unit"]
        elif "面積" in base_key:
            data_type = "area"
            fields = ["value", "unit", "tsubo", "measurement_type"]
        elif "戸数" in base_key or "階" in base_key:
            data_type = "number"
            fields = ["value", "unit"]
        else:
            data_type = "number"
            fields = ["value"]
    else:
        base_type = "single"
        data_type = "text"
        fields = ["value"]
    
    # 期別情報を追加
    if has_period:
        fields.append("period")
    
    return {
        "base_type": base_type,
        "data_type": data_type,
        "fields": fields,
        "period_aware": has_period
    }