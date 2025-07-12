"""
JSON形式でのクレンジング処理
estate_detailの生データをJSONオブジェクトに変換
"""

import re
import csv
import os
from typing import Dict, Any, Optional, List, Tuple
from .parser import (
    parse_address_structure,
    clean_surrounding_facilities_to_json,
    parse_land_use_to_json,
    parse_floor_structure_to_json,
    parse_reform_to_json,
    parse_building_structure_to_json,
    parse_parking_to_json,
    parse_floor_plan_to_json,
    parse_building_coverage_to_json,
    get_building_structure_analysis_schema,
    get_parking_analysis_schema,
    get_structure_analysis_schema,
    get_reform_analysis_schema
)

# citycode.csvからマッピング辞書を作成（グローバル変数）
_CITYCODE_MAP = None

def _load_citycode_map():
    """citycode.csvを読み込んでマッピング辞書を作成"""
    global _CITYCODE_MAP
    if _CITYCODE_MAP is not None:
        return _CITYCODE_MAP
    
    _CITYCODE_MAP = {}
    citycode_path = os.path.join(os.path.dirname(__file__), "../master/citycode.csv")
    
    if os.path.exists(citycode_path):
        try:
            with open(citycode_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 6:
                        citycode = row[0].strip('"')
                        city_name = row[1].strip('"')
                        pref_name = row[5].strip('"')
                        
                        # 都道府県名+市区町村名をキーにしてcitycodeをマッピング
                        full_name = pref_name + city_name
                        _CITYCODE_MAP[full_name] = citycode
        except Exception:
            pass
    
    return _CITYCODE_MAP

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
    if not value or value.strip() == "":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # 価格未定などのケース  
    if "未定" in value:
        result["is_undefined"] = True
        result["value"] = None
        if period is not None:
            result["period"] = period
        return result
    
    # その他の無効な値のチェック
    if _should_nullify_text(value):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    # 価格要相談のケース
    if "要相談" in value or "価格要相談" in value:
        result["type"] = "negotiable"
        if period is not None:
            result["period"] = period
        return result
    
    # 括弧内の価格は注記として扱い、主価格は括弧外から抽出
    main_text = re.sub(r'[（(][^）)]*[）)]', '', value)  # 括弧を除去
    
    # 億円を含む価格の処理
    if "億" in main_text:
        # 億円の数値をすべて万円に変換
        prices_in_man = []
        
        # 億と万を含む価格を処理（例：1億2300万円）
        for match in re.finditer(r'(\d+(?:\.\d+)?)億(?:(\d+(?:\.\d+)?)万)?', main_text):
            oku = float(match.group(1))
            man = float(match.group(2)) if match.group(2) else 0
            total_man = oku * 10000 + man  # 億を万に変換して合計
            prices_in_man.append(total_man)
        
        # 万円のみの価格も抽出（億と組み合わさっていないもの）
        for match in re.finditer(r'(?<![億\d])(\d+(?:,\d{3})*(?:\.\d+)?)万', main_text):
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
        # 万円を含む複雑な価格パターンの処理（括弧外のテキストから）
        prices_in_unit = []
        
        # 万円パターンの処理（例：3989万5000円）
        if "万" in main_text:
            # パターン1: 「3989万5000円」のような形式
            man_yen_pattern = re.findall(r'(\d+(?:,\d{3})*)万(\d+(?:,\d{3})*)円', main_text)
            for man_part, yen_part in man_yen_pattern:
                man_val = float(man_part.replace(',', ''))
                yen_val = float(yen_part.replace(',', ''))
                # 万円単位に変換：3989万5000円 → 3989.5万円
                total_man = man_val + (yen_val / 10000)
                prices_in_unit.append(total_man)
            
            # パターン2: 「万円」のみ（例：3989万円）
            man_only_pattern = re.findall(r'(\d+(?:,\d{3})*)万円', main_text)
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
        
        # 範囲表現（〜）がある場合（括弧外のテキストをチェック）
        if "～" in main_text or "〜" in main_text:
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
    
    # 括弧内の注記を抽出
    note_match = re.search(r'[（(]([^）)]*)[）)]', value)
    if note_match:
        note_text = note_match.group(1).strip()
        # 支払いシミュレーションなどの不要な情報は除外
        if not any(exclude in note_text for exclude in ["支払シミュレーション", "□"]):
            result["note"] = note_text
    
    # 参考価格の場合
    if "参考価格" in value:
        result["tentative"] = True
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_price_band_to_json(value: str, raw_key: str, period: Optional[int] = None) -> Dict[str, Any]:
    """
    最多価格帯情報をJSON形式でクレンジング
    例: "3500万円台（7戸）" -> {"values": [{"price": 3500, "count": 7}], "value": 3500, "unit": "万円"}
    例: "1200万円台（4区画）" -> {"values": [{"price": 1200, "count": 4}], "value": 1200, "unit": "万円"}
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
    
    # パターン1: "5500万円台（2戸）"、"1200万円台（4区画）"、"5000万円台（9戸）※1000万円単位" - 単一価格帯で括弧内に戸数/区画数
    single_pattern_match = re.match(r'^(\d+(?:,\d{3})*(?:\.\d+)?)万円台(?:（予定）)?（(\d+)(?:戸|区画)）(?:※.*)?$', value.strip())
    
    # 億円台パターン: "1億円台（4戸）" -> 1億円を10000万円に変換
    oku_pattern_match = re.match(r'^(\d+(?:\.\d+)?)億円台（(\d+)(?:戸|区画)）$', value.strip())
    
    # パターン1-2: "8000万円台 2区画 ※1000万円単位" - 括弧なしで戸数/区画数（※注記は無視）
    single_no_paren_match = re.match(r'^(\d+(?:,\d{3})*(?:\.\d+)?)万円台\s+(\d+)(?:戸|区画)(?:\s+※.*)?$', value.strip())
    
    # パターン2: "5700万円台・5900万円台（各1戸）" または "5700万円台・5900万円台（各1区画）" - 複数価格帯で「各X戸/区画」
    multi_pattern_match = re.match(r'^(.+?)（各(\d+)(?:戸|区画)）$', value.strip())
    
    # パターン3: 範囲指定価格帯（括弧内注記は無視）
    # 「8900万円台～1億2900万円台」のような億万円混合範囲パターン
    oku_man_range_match = re.match(r'^(\d+(?:,\d{3})*(?:\.\d+)?)万円台～(\d+(?:\.\d+)?)億(\d+(?:,\d{3})*)万円台$', value.strip())
    
    # 「2700万円台～4400万円台（うちモデルルーム価格4476万円、予定）」のような万円のみ範囲パターン
    range_pattern_match = re.match(r'^(\d+(?:,\d{3})*(?:\.\d+)?)万円台～(\d+(?:,\d{3})*(?:\.\d+)?)万円台(?:[（(].*?[）)])?(?:※.*)?$', value.strip())
    
    if oku_man_range_match:
        # 億万円混合範囲パターン: 8900万円台～1億2900万円台
        min_man_str = oku_man_range_match.group(1)
        max_oku_str = oku_man_range_match.group(2)
        max_man_str = oku_man_range_match.group(3)
        
        min_price = float(min_man_str.replace(',', ''))  # 8900万円
        max_oku = float(max_oku_str)  # 1億
        max_man = float(max_man_str.replace(',', ''))  # 2900万円
        max_price = max_oku * 10000 + max_man  # 10000 + 2900 = 12900万円
        
        avg_price = (min_price + max_price) / 2
        result["values"].append({"price": min_price, "count": None})
        result["values"].append({"price": max_price, "count": None})
        result["value"] = avg_price
        
        if period is not None:
            result["period"] = period
        return result
        
    elif oku_pattern_match:
        # 億円台パターン
        oku_str = oku_pattern_match.group(1)
        count_str = oku_pattern_match.group(2)
        oku = float(oku_str)
        count = int(count_str)
        price_in_man = oku * 10000  # 億を万に変換
        result["values"].append({"price": price_in_man, "count": count})
        
    elif single_pattern_match:
        # パターン1: 単一価格帯（括弧あり）
        price_str = single_pattern_match.group(1)
        count_str = single_pattern_match.group(2)
        price = float(price_str.replace(',', ''))
        count = int(count_str)
        result["values"].append({"price": price, "count": count})
        
    elif single_no_paren_match:
        # パターン1-2: 単一価格帯（括弧なし）
        price_str = single_no_paren_match.group(1)
        count_str = single_no_paren_match.group(2)
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
    elif '・' in value.strip():
        # パターン3-2: 複数価格帯（戸数情報なし）例: "4600万円台・4900万円台"
        price_items = value.strip().split('・')
        valid_prices = []
        for item in price_items:
            price_match = re.match(r'^(\d+(?:,\d{3})*(?:\.\d+)?)万円台$', item.strip())
            if price_match:
                price = float(price_match.group(1).replace(',', ''))
                valid_prices.append(price)
        
        if len(valid_prices) == len(price_items):  # 全ての価格が正しく抽出できた場合のみ
            for price in valid_prices:
                result["values"].append({"price": price, "count": None})
        else:
            # 一部でも抽出できない場合は対応不可
            result["value"] = -1
            if period is not None:
                result["period"] = period
            return result
    elif range_pattern_match:
        # パターン4: 範囲指定価格帯
        min_price_str = range_pattern_match.group(1)
        max_price_str = range_pattern_match.group(2)
        min_price = float(min_price_str.replace(',', ''))
        max_price = float(max_price_str.replace(',', ''))
        
        # 範囲の平均値を計算
        avg_price = (min_price + max_price) / 2
        result["values"].append({"price": min_price, "count": None})
        result["values"].append({"price": max_price, "count": None})
        result["value"] = avg_price
        
        if period is not None:
            result["period"] = period
        return result
    else:
        # パターン5: 単一価格帯（戸数情報なし）
        
        # 億万円台パターン（例：「1億1000万円台※1000万円単位」）
        oku_man_band_match = re.match(r'^(\d+(?:\.\d+)?)億(\d+(?:,\d{3})*)万円台(?:※.*)?$', value.strip())
        if oku_man_band_match:
            oku_str = oku_man_band_match.group(1)
            man_str = oku_man_band_match.group(2)
            oku = float(oku_str)
            man = float(man_str.replace(',', ''))
            price_in_man = oku * 10000 + man  # 億を万に変換して合計
            result["values"].append({"price": price_in_man, "count": 1})
        else:
            # 万円台パターン（例：「3900万円台」）
            single_band_match = re.match(r'^(\d+(?:,\d{3})*(?:\.\d+)?)万円台(?:※.*)?$', value.strip())
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
            result["value"] = round((result["min"] + result["max"]) / 2, 3)
        else:
            # フォールバック：すべての数値から最初の2つを使用
            result["min"] = clean_numbers[0]
            result["max"] = clean_numbers[1] if len(clean_numbers) > 1 else clean_numbers[0]
            result["value"] = round((result["min"] + result["max"]) / 2, 3)
    else:
        # 単一値または複数値があっても範囲でない場合
        # 最初の数値を面積として扱い、2番目があれば坪数として扱う
        result["value"] = clean_numbers[0]
        
        # tsuboの値は削除（ユーザーのリクエストにより不要）
    
    # 測定タイプ（壁芯・登記）を抽出
    if "壁芯" in value:
        result["measurement_type"] = "壁芯"
    elif "登記" in value:
        result["measurement_type"] = "登記"
    
    # tsuboの計算は削除（ユーザーのリクエストにより不要）
    
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
    
    # 「、」や全角スペースで分割して各面積項目を処理
    parts = re.split(r'[,、，　\s]+', value)
    
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
        
        # tsuboの計算は削除（ユーザーのリクエストにより不要）
        
        # 使用料を抽出
        # パターン1: 使用料1500円
        usage_fee_match = re.search(r'使用料[：:]?(\d+)円', area_value)
        # パターン2: （2000円／月）
        monthly_fee_match = re.search(r'[（(](\d+)円[／/]月[）)]', area_value)
        # パターン3: （利用料：月額1500円）または（使用料：月額3000円）
        monthly_fee_match2 = re.search(r'[（(][利使]用料[：:]?月額(\d+)円[）)]', area_value)
        
        if usage_fee_match:
            area_info["monthly_fee"] = int(usage_fee_match.group(1))
        elif monthly_fee_match:
            area_info["monthly_fee"] = int(monthly_fee_match.group(1))
        elif monthly_fee_match2:
            area_info["monthly_fee"] = int(monthly_fee_match2.group(1))
        elif "使用料無" in area_value:
            area_info["monthly_fee"] = 0
        
        # 測定タイプ（壁芯・登記・共用）を抽出
        if "壁芯" in area_value:
            area_info["measurement_type"] = "壁芯"
        elif "登記" in area_value:
            area_info["measurement_type"] = "登記"
        elif "共用" in area_value:
            area_info["measurement_type"] = "共用"
        
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
    
    # 間取りの正規化処理
    normalized_oneroom = False
    if value == "ワンルーム":
        value = "1R"
        normalized_oneroom = True
    
    # 間取りパターンを保持しながら括弧内の説明を簡略化
    # +S（納戸） → +S のように、間取り情報は保持する
    
    # 正規化前の値を保存（括弧内の間取り抽出用）
    original_value = value
    
    # 括弧内の説明を除去（+S（納戸）→+S）
    value = re.sub(r'([+＋][A-Z]+)[（(][^）)]*[）)]', r'\1', value)
    
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
                layout_match = re.search(r'(\d+(?:[LDKSRF]+)(?:[+＋]\d*[LDKSRF]*)*)', part.upper())
                if layout_match:
                    matched_layout = layout_match.group(1)
                    # 間取りパターンとして有効な場合のみ追加（+で終わるパターンを除外）
                    if len(matched_layout) <= 10 and re.match(r'^\d+[LDKSRF]+(?:[+＋]\d*[LDKSRF]+)*$', matched_layout) and not matched_layout.endswith(('+', '＋')):
                        layout_items.append(matched_layout)
            
            # 簡単な展開が可能な場合のみ展開（例：1LDK～3LDK）
            if len(layout_items) == 2:
                first_layout = layout_items[0]
                second_layout = layout_items[1]
                
                # 単純なパターン（数字+同じ文字列）の場合のみ展開
                first_match = re.match(r'^(\d+)([LDKSRF]+)$', first_layout)
                second_match = re.match(r'^(\d+)([LDKSRF]+)$', second_layout)
                
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
                    # 特殊パターン: 1R～XLDKの場合も展開
                    elif first_layout == "1R" and end_type == "LDK" and start_num == 1 and end_num >= 1:
                        layout_items = []
                        layout_items.append("1R")
                        for i in range(1, end_num + 1):
                            layout_items.append(f"{i}LDK")
        else:
            # 複雑な範囲パターンは通常の処理に任せる
            all_layouts = re.findall(r'(\d+(?:[LDKSRF]+)(?:[+＋]\d*[LDKSRF]*)*)', value.upper())
            for layout in all_layouts:
                if len(layout) <= 10 and re.match(r'^\d+[LDKSRF]+(?:[+＋]\d*[LDKSRF]+)*$', layout) and not layout.endswith(('+', '＋')):
                    layout_items.append(layout)
        
        # 範囲処理後に括弧内の詳細情報からも間取りを抽出
        bracket_content = re.findall(r'[（(]([^）)]*)[）)]', value)
        for bracket in bracket_content:
            # 括弧内を・で分割してさらに間取りを抽出
            bracket_parts = re.split(r'[・]', bracket)
            for bracket_part in bracket_parts:
                bracket_part = bracket_part.strip()
                # サービスルーム等の説明文を除去
                bracket_part = re.sub(r'[（(][^）)]*(?:サービスルーム|ファミリークロゼット|シューズインクローク|納戸)[^）)]*[）)]', '', bracket_part)
                bracket_layout_match = re.search(r'(\d+(?:[LDKSRF]+)(?:[+＋]\d*[LDKSRF]*)*)', bracket_part.upper())
                if bracket_layout_match:
                    bracket_matched_layout = bracket_layout_match.group(1)
                    if len(bracket_matched_layout) <= 10 and re.match(r'^\d+[LDKSRF]+(?:[+＋]\d*[LDKSRF]+)*$', bracket_matched_layout) and not bracket_matched_layout.endswith(('+', '＋')):
                        # 重複チェック
                        if bracket_matched_layout not in layout_items:
                            layout_items.append(bracket_matched_layout)
    else:
        # ・（中点）で分割
        parts = re.split(r'[・]', value)
        
        for part in parts:
            part = part.strip()
            if part:
                # 括弧がある場合は括弧内の詳細情報も処理
                if '(' in part or '（' in part:
                    # 括弧外の間取りを抽出
                    main_part = re.sub(r'[（(][^）)]*[）)]', '', part)
                    # 余分な括弧を除去
                    main_part = re.sub(r'[）)]', '', main_part)
                    layout_match = re.search(r'(\d+(?:[LDKSR]+)(?:[+＋]\d*[LDKSRF]*)*)', main_part.upper())
                    if layout_match:
                        matched_layout = layout_match.group(1)
                        # +で終わるパターンや不完全なパターンを除外
                        if len(matched_layout) <= 10 and re.match(r'^\d+[LDKSR]+(?:[+＋]\d*[LDKSRF]+)*$', matched_layout) and not matched_layout.endswith(('+', '＋')):
                            layout_items.append(matched_layout)
                    
                    # 括弧内の間取りも抽出（・で分割されている可能性）
                    bracket_content = re.findall(r'[（(]([^）)]*)[）)]', part)
                    for bracket in bracket_content:
                        # 括弧内を・で分割してさらに間取りを抽出
                        bracket_parts = re.split(r'[・]', bracket)
                        for bracket_part in bracket_parts:
                            bracket_part = bracket_part.strip()
                            # サービスルーム等の説明文を除去
                            bracket_part = re.sub(r'[（(][^）)]*(?:サービスルーム|ファミリークロゼット|シューズインクローク|納戸)[^）)]*[）)]', '', bracket_part)
                            bracket_layout_match = re.search(r'(\d+(?:[LDKSRF]+)(?:[+＋]\d*[LDKSRF]*)*)', bracket_part.upper())
                            if bracket_layout_match:
                                bracket_matched_layout = bracket_layout_match.group(1)
                                if len(bracket_matched_layout) <= 10 and re.match(r'^\d+[LDKSRF]+(?:[+＋]\d*[LDKSRF]+)*$', bracket_matched_layout) and not bracket_matched_layout.endswith(('+', '＋')):
                                    layout_items.append(bracket_matched_layout)
                else:
                    # 各部分から間取りパターンを抽出
                    # より厳密な間取りパターン: 数字 + L/D/K/S/R/F の組み合わせ
                    layout_match = re.search(r'(\d+(?:[LDKSRF]+)(?:[+＋]\d*[LDKSRF]*)*)', part.upper())
                    if layout_match:
                        # マッチした部分が間取りとして妥当かチェック
                        matched_layout = layout_match.group(1)
                        # 間取りパターンとして有効な場合のみ追加（LDKSRFのみを含み、長すぎない、+で終わらない）
                        if len(matched_layout) <= 10 and re.match(r'^\d+[LDKSRF]+(?:[+＋]\d*[LDKSRF]+)*$', matched_layout) and not matched_layout.endswith(('+', '＋')):
                            layout_items.append(matched_layout)
    
    # ワンルームの正規化の場合は特別処理
    if normalized_oneroom:
        result["value"] = "1R"
    elif layout_items:
        # 重複を除去してソート
        unique_layouts = list(set(layout_items))
        
        # 間取りの適切な順序でソート（2LDK → 2LDK+S → 2LDK+1S → 3LDK → ...）
        def layout_sort_key(layout):
            # 数字を抽出
            num_match = re.match(r'^(\d+)', layout)
            if num_match:
                num = int(num_match.group(1))
                # Rの場合は特別に小さい値を設定
                if 'R' in layout and 'LDK' not in layout:
                    return (num, 0, 0, layout)  # 1R → (1, 0, 0, "1R")
                elif 'LDK' in layout:
                    # +が付いていない基本LDKを先にソート
                    if '+' in layout or '＋' in layout:
                        # +の後の内容でさらにソート（S が 1S より先）
                        plus_part = layout.split('+')[1] if '+' in layout else layout.split('＋')[1]
                        # 数字のないもの（S）を数字があるもの（1S）より先にソート
                        has_number_after_plus = re.search(r'\d', plus_part)
                        if has_number_after_plus:
                            return (num, 1, 2, layout)  # 2LDK+1S → (2, 1, 2, "2LDK+1S")
                        else:
                            return (num, 1, 1, layout)  # 2LDK+S → (2, 1, 1, "2LDK+S")
                    else:
                        return (num, 1, 0, layout)  # 3LDK → (3, 1, 0, "3LDK")
                else:
                    return (num, 2, 0, layout)  # その他 → (num, 2, 0, layout)
            return (999, 999, 999, layout)  # 数字が見つからない場合
        
        unique_layouts.sort(key=layout_sort_key)
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
    if not value or value.strip() == "":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # 未定の場合（_should_nullify_textより先に処理）
    if value == "未定":
        result = {"is_undefined": True}
        if period is not None:
            result["period"] = period
        return result
    
    # その他のnullifyケース
    if _should_nullify_text(value):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
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
        # 即日の場合は他のフィールドをクリアしてimmediateのみ返す
        if value == "即日":
            result = {"immediate": True}
    
    
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
    
    # 「無」の場合は0として処理
    if value == "無":
        result["value"] = 0
        if period is not None:
            result["period"] = period
        return result
    
    # 複数項目がある場合は先に分離処理を行う
    # その後で各項目内容の処理（未定、金額等）を行う
    
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
    
    # 特殊パターン1：※記号で注記がある場合
    if '※' in value:
        note_idx = value.index('※')
        main_part = value[:note_idx].strip()
        note_part = value[note_idx+1:].strip()
        
        # メイン部分から金額を抽出
        amount_match = re.search(r'(\d+(?:万\d+)?(?:,\d{3})*)円', main_part)
        if amount_match:
            amount_str = amount_match.group(1)
            # 金額をパース
            if '万' in amount_str:
                man_match = re.match(r'(\d+)万(\d+)', amount_str)
                if man_match:
                    amount = int(man_match.group(1)) * 10000 + int(man_match.group(2))
                else:
                    amount = int(amount_str.replace(',', '').replace('万', '')) * 10000
            else:
                amount = int(amount_str.replace(',', ''))
            
            result["value"] = amount
            result["unit"] = "円"
            result["frequency"] = "月" if "月" in main_part else "一括"
            result["note"] = note_part
            
            if period is not None:
                result["period"] = period
            return result
    
    # 特殊パターン1.5：「当初月額X円／月、段階増額方式」のようなパターン
    stage_pattern = re.match(r'^当初月額(\d+(?:万\d+)?(?:,\d{3})*)円／月、(.+)$', value)
    if stage_pattern:
        amount_str = stage_pattern.group(1)
        note_text = stage_pattern.group(2)
        
        # 金額をパース
        if '万' in amount_str:
            man_match = re.match(r'(\d+)万(\d+)', amount_str)
            if man_match:
                amount = int(man_match.group(1)) * 10000 + int(man_match.group(2))
            else:
                amount = int(amount_str.replace(',', '').replace('万', '')) * 10000
        else:
            amount = int(amount_str.replace(',', ''))
        
        result["value"] = amount
        result["unit"] = "円"
        result["frequency"] = "月"
        result["note"] = note_text
        
        if period is not None:
            result["period"] = period
        return result
    
    # 特殊パターン2：「X円／月（Y年目のみZ円／月）」のような期間限定特別料金パターン
    period_special_pattern = re.match(r'^(\d+(?:万\d+)?(?:,\d{3})*)円／月（([^）]+のみ\d+(?:万\d+)?(?:,\d{3})*円／月)）$', value)
    if period_special_pattern:
        # メインの金額を値として取る（期間限定は注記扱い）
        main_amount_str = period_special_pattern.group(1)
        note_text = period_special_pattern.group(2)
        
        # 金額をパース
        if '万' in main_amount_str:
            man_match = re.match(r'(\d+)万(\d+)', main_amount_str)
            if man_match:
                main_amount = int(man_match.group(1)) * 10000 + int(man_match.group(2))
            else:
                main_amount = int(main_amount_str.replace(',', '').replace('万', '')) * 10000
        else:
            main_amount = int(main_amount_str.replace(',', ''))
        
        result["value"] = main_amount
        result["unit"] = "円"
        result["frequency"] = "月"
        result["note"] = note_text
        
        if period is not None:
            result["period"] = period
        return result
    
    # 特殊パターン2.5：「X円／月（契約時）、Y」のような形式の処理
    special_pattern = re.match(r'^(\d+(?:万\d+)?(?:,\d{3})*)円／月（([^）]+)）(.*)$', value)
    if special_pattern and '、' in value:
        # 最初の金額を値として取る
        first_amount_str = special_pattern.group(1)
        note_start = special_pattern.group(2)  # 括弧内の内容
        remaining = special_pattern.group(3)   # 括弧後の内容
        
        # 金額をパース
        if '万' in first_amount_str:
            man_match = re.match(r'(\d+)万(\d+)', first_amount_str)
            if man_match:
                first_amount = int(man_match.group(1)) * 10000 + int(man_match.group(2))
            else:
                first_amount = int(first_amount_str.replace(',', '').replace('万', '')) * 10000
        else:
            first_amount = int(first_amount_str.replace(',', ''))
        
        result["value"] = first_amount
        result["unit"] = "円"
        result["frequency"] = "月"
        result["note"] = f"（{note_start}）{remaining}"
        
        if period is not None:
            result["period"] = period
        return result
    
    # 特殊パターン3：括弧内に期間変更情報がある場合（年目より、年後より、など）
    paren_match = re.search(r'(\d+(?:万\d+)?(?:,\d{3})*)円／月[（(]([^）)]*(?:年目|年後|カ月目|カ月後)より[^）)]*)[）)]', value)
    if paren_match:
        amount_str = paren_match.group(1)
        note_text = paren_match.group(2)
        
        # 金額をパース
        if '万' in amount_str:
            man_match = re.match(r'(\d+)万(\d+)', amount_str)
            if man_match:
                amount = int(man_match.group(1)) * 10000 + int(man_match.group(2))
            else:
                amount = int(amount_str.replace(',', '').replace('万', '')) * 10000
        else:
            amount = int(amount_str.replace(',', ''))
        
        result["value"] = amount
        result["unit"] = "円"
        result["frequency"] = "月"
        result["note"] = note_text
        
        if period is not None:
            result["period"] = period
        return result
    
    # 複数パターンがある場合の処理
    # 「、」で区切られた複数の管理費項目の場合
    if '、' in value:
        parts = value.split('、')
        
        # 完全に異なる項目種別（修繕積立基金等）が含まれる場合は最初の項目のみ処理
        # ただし、管理準備金の「住宅一部」と「全体」の組み合わせは統合処理する
        has_different_items = False
        for part in parts[1:]:  # 2番目以降をチェック
            if any(keyword in part for keyword in ["修繕積立基金", "全体修繕", "団地"]):
                has_different_items = True
                break
            # 管理準備金の場合は「住宅一部」と「全体」の組み合わせをチェック
            if "管理準備金" in part:
                # 最初の項目も管理準備金で、住宅一部+全体の組み合わせかチェック
                first_part = parts[0]
                if ("住宅一部" in first_part and "全体" in part) or ("一部" in first_part and "全体" in part):
                    # この場合は統合処理（has_different_items = False のまま）
                    pass
                else:
                    has_different_items = True
                    break
        
        if has_different_items:
            # 最初の項目のみを処理対象とする
            main_part = parts[0].strip()
            # 後続の項目を注記として保存
            if len(parts) > 1:
                note_parts = []
                for part in parts[1:]:
                    note_parts.append(part.strip())
                result["note"] = "、".join(note_parts)
            use_all_amounts = False
        else:
            # 同一項目の複数範囲の場合は従来通り全額処理
            # 各項目の注記を収集
            notes = []
            for part in parts:
                part = part.strip()
                # 複数の括弧がある場合は最後の括弧を取得
                paren_matches = re.findall(r'[（(]([^）)]*)[）)]', part)
                if paren_matches:
                    # 最後の括弧内容を注記として使用
                    note_text = paren_matches[-1]
                    if any(keyword in note_text for keyword in ["修繕", "積立", "基金", "準備金", "住宅", "団地", "街区"]):
                        notes.append(note_text)
            
            # 複数の注記がある場合は「・」で結合
            if notes:
                result["note"] = "・".join(notes)
            
            # 複数の項目がある場合、全ての金額を収集して最小・最大を取る
            all_amounts = []
            for part in parts:
                part = part.strip()
                # 各パートから金額を抽出
                # パターン1: 「1万7744円」のような形式
                man_pattern = re.findall(r'(\d+)万(\d+)円', part)
                for man_part, remaining_part in man_pattern:
                    total_amount = int(man_part) * 10000 + int(remaining_part)
                    all_amounts.append(total_amount)
                
                # パターン2: 「万円」単位（「10万円」など）
                man_only_pattern = re.findall(r'(\d+(?:,\d{3})*)万円', part)
                for man_str in man_only_pattern:
                    # 既にパターン1で処理されていないかチェック
                    already_processed = False
                    for m, r in man_pattern:
                        if man_str == m:
                            already_processed = True
                            break
                    if not already_processed:
                        all_amounts.append(int(man_str.replace(',', '')) * 10000)
                
                # パターン3: 通常の円表記
                yen_pattern = re.findall(r'(\d+(?:,\d{3})*)円', part)
                for yen_str in yen_pattern:
                    # 万円パターンに含まれていない場合のみ追加
                    already_processed = False
                    for m, r in man_pattern:
                        if yen_str == r:
                            already_processed = True
                            break
                    if not already_processed:
                        all_amounts.append(int(yen_str.replace(',', '')))
            
            # 全額を処理
            main_part = value  # 後続の処理のために全体を保持
            # 既に収集した金額を使用するフラグ
            use_all_amounts = True
    else:
        # 単一項目の場合は注記処理を実行
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
        use_all_amounts = False
    
    # 「未定」「金額未定」などのケース（勤務形態未定は除く）
    # 複数項目の場合でも未定があれば処理
    undefined_keywords = ["金額未定", "価格未定", "未確定", "未決定", "要相談", "応相談"]
    if any(word in value for word in undefined_keywords) or \
       (value.strip() == "未定"):  # 「未定」単体の場合のみ
        result["is_undefined"] = True
        result["value"] = None
        if period is not None:
            result["period"] = period
        return result
    
    # メイン部分から金額を抽出（「万」を含む場合を正しく処理）
    if 'use_all_amounts' in locals() and use_all_amounts and all_amounts:
        # 既に収集した金額を使用
        amounts = all_amounts
    else:
        # 通常の金額抽出処理
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
        "駐車場": r'(.*駐車場[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "地代": r'(.*地代)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "敷金": r'(敷金)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "保証金": r'(.*保証金[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "解体": r'(.*解体[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "災害積立": r'(災害積立[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "メンテナンス": r'(.*メンテナンス[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "通信費": r'(.*(?:インターネット|ネット|ＣＡＴＶ|CATV|TV|テレビ|フレッツ)[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "管理費": r'(管理一時金[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "利用料": r'(.*(?:利用料|使用料|専用利用料)[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "自治会費": r'(.*(?:町会費|町内会費|自治会費)[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "セキュリティ": r'(.*(?:セキュリティ|防犯|警備)[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "コミュニティ": r'(.*(?:コミュニティ|会費)[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?',
        "サービス": r'(.*(?:サービス)[^：]*)[:：]\s*([0-9万,～〜円未定]+)(?:[／/](.+))?'
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
                # 通信費の場合は名前を統一
                if category == "通信費":
                    if any(word in item_name for word in ["インターネット", "ネット", "NET"]):
                        normalized_name = "インターネット"
                    elif "ＣＡＴＶ" in item_name or "CATV" in item_name:
                        normalized_name = "CATV"
                    elif "TV" in item_name or "テレビ" in item_name:
                        normalized_name = "テレビ"
                    elif "フレッツ" in item_name:
                        normalized_name = "フレッツ光"
                    else:
                        normalized_name = item_name
                    expense_item = {"name": normalized_name, "category": category}
                else:
                    expense_item = {"name": item_name, "category": category}
                
                # 未定の場合
                if "未定" in amount_str or "金額未定" in amount_str:
                    expense_item["is_undefined"] = True
                    expense_item["value"] = None
                    expense_item["unit"] = "円"
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
                        expense_item["frequency"] = "月"
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
                    
                    # 頻度の判定（金額直後の周期のみを優先、それ以外は無視）
                    if frequency_str:
                        # 最初の単語のみを見る（括弧や注記は無視）
                        first_word = frequency_str.split()[0] if frequency_str.split() else frequency_str
                        first_word = re.sub(r'[（(].*', '', first_word)  # 括弧以降を削除
                        
                        if "一括" in first_word:
                            expense_item["frequency"] = "一括"
                        elif "月" in first_word:
                            expense_item["frequency"] = "月"
                        elif "年" in first_word:
                            expense_item["frequency"] = "年"
                        else:
                            expense_item["frequency"] = "月"  # デフォルト
                    else:
                        expense_item["frequency"] = "月"  # デフォルト
                    
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
        # スラッシュ形式をパース（例: "2024/03/31"）
        slash_date_match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', value)
        if slash_date_match:
            year = slash_date_match.group(1)
            month = slash_date_match.group(2).zfill(2)  # 0埋め
            day = slash_date_match.group(3).zfill(2)    # 0埋め
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
    
    # 住所関連の特殊処理
    address_keywords = ["住所", "所在地", "物件所在地", "現地案内所", "モデルルーム", "アドレス"]
    if any(keyword in base_key for keyword in address_keywords):
        return generate_address_type_schema()
    
    # 価格関連の特殊処理
    price_keywords = ["価格", "料金", "費用", "金額", "万円", "円"]
    if any(keyword in base_key for keyword in price_keywords):
        return generate_price_type_schema()
    
    # 面積関連の特殊処理
    area_keywords = ["面積", "平米", "m²", "㎡", "坪"]
    if any(keyword in base_key for keyword in area_keywords):
        return generate_area_type_schema()
    
    # 間取り関連の特殊処理
    layout_keywords = ["間取り", "LDK", "DK", "1R", "ワンルーム"]
    if any(keyword in base_key for keyword in layout_keywords):
        return generate_layout_type_schema()
    
    # 日付関連の特殊処理
    date_keywords = ["時期", "年月", "完成", "竣工", "引渡", "築年", "建築年"]
    if any(keyword in base_key for keyword in date_keywords):
        return generate_date_type_schema()
    
    # 交通アクセスの特殊処理
    if "交通" in base_key or "アクセス" in base_key:
        return generate_access_type_schema()
    
    # 建物構造の特殊処理（「構造・階建て」など）
    if "構造" in base_key and "階建" in base_key and "所在階" not in base_key:
        # get_building_structure_analysis_schema already imported from .parser
        return get_building_structure_analysis_schema()
    
    # 駐車場の特殊処理
    if "駐車場" in base_key:
        # get_parking_analysis_schema already imported from .parser
        return get_parking_analysis_schema()
    
    # 構造階建の特殊処理（「所在階/構造・階建」など）
    structure_keywords = ["所在階", "構造", "階建"]
    if any(keyword in base_key for keyword in structure_keywords):
        # get_structure_analysis_schema already imported from .parser
        return get_structure_analysis_schema()
    
    # リフォームの特殊処理
    if "リフォーム" in base_key:
        # get_reform_analysis_schema already imported from .parser
        return get_reform_analysis_schema()
    
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
    
    # 特徴ピックアップの特殊処理
    if "特徴ピックアップ" in base_key or "物件の特徴" in base_key:
        return generate_feature_pickup_type_schema()
    
    # 光熱費の特殊処理
    if "目安光熱費" in base_key:
        return generate_utility_cost_type_schema()
    
    # 強制null処理の特殊処理
    force_null_keys = [
        "物件名", "情報提供日", "次回更新日", "関連リンク", "お問い合せ先", 
        "周辺施設", "イベント情報", "その他概要・特記事項", "敷地権利形態", "販売スケジュール"
    ]
    if any(key in base_key for key in force_null_keys):
        return {
            "base_type": "null",
            "data_type": "force_null",
            "fields": ["value"],
            "period_aware": has_period
        }
    
    # 会社情報の特殊処理
    if "会社情報" in base_key or "会社概要" in base_key:
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
    
    # サンプルデータによる自動判定でも詳細なtype生成関数を使用
    if has_boolean_words and not has_numeric:
        return generate_boolean_type_schema()
    elif has_date:
        return generate_date_type_schema()
    elif has_range and has_numeric:
        if "価格" in base_key or "費" in base_key:
            return generate_price_type_schema()
        elif "面積" in base_key:
            return generate_area_type_schema()
        else:
            return generate_number_type_schema()
    elif has_numeric and not has_range:
        if "価格" in base_key or "費" in base_key:
            return generate_price_type_schema()
        elif "面積" in base_key:
            return generate_area_type_schema()
        else:
            return generate_number_type_schema()
    else:
        return generate_text_type_schema()

def clean_address_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    住所情報をJSON形式でクレンジング
    都道府県とその次の区分に分けて構造化
    
    Args:
        value (str): 住所の生データ
        raw_key (str): 元のキー名
        period (Optional[int]): 期別情報
        
    Returns:
        Dict[str, Any]: 構造化された住所情報
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # 住所を構造化
    parsed = parse_address_structure(value)
    
    if parsed:
        result.update({
            "raw": parsed["raw"],
            "prefecture": parsed["prefecture"],
            "secondary_division": parsed["secondary_division"],
            "secondary_type": parsed["secondary_type"],
            "tertiary_division": parsed["tertiary_division"],
            "tertiary_type": parsed["tertiary_type"],
            "remaining": parsed["remaining"]
        })
        
        # 住所階層の文字列表現を追加
        hierarchy = []
        if parsed["prefecture"]:
            hierarchy.append(parsed["prefecture"])
        if parsed["secondary_division"]:
            hierarchy.append(parsed["secondary_division"])
        if parsed["tertiary_division"]:
            hierarchy.append(parsed["tertiary_division"])
        
        result["hierarchy"] = " -> ".join(hierarchy)
        
        # 区分タイプの組み合わせ
        division_types = []
        if parsed["secondary_type"]:
            division_types.append(parsed["secondary_type"])
        if parsed["tertiary_type"]:
            division_types.append(parsed["tertiary_type"])
        
        if division_types:
            result["division_types"] = " -> ".join(division_types)
    else:
        # パースに失敗した場合は生データを保存
        result["raw"] = value
        result["parse_failed"] = True
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_address_simple_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    住所情報をシンプルなJSON形式でクレンジング
    location（クリーニング済み住所）とcitycode（先頭一致）の2項目のみ
    
    Args:
        value (str): 住所の生データ
        raw_key (str): 元のキー名
        period (Optional[int]): 期別情報
        
    Returns:
        Dict[str, Any]: {"location": クリーニング済み住所, "citycode": コード}
    """
    if not value or value.strip() == "" or _should_nullify_text(value.strip()):
        result = {"location": None, "citycode": None}
        if period is not None:
            result["period"] = period
        return result
    
    # 住所をクリーニング
    cleaned_address = _clean_address_string(value.strip())
    
    result = {
        "location": cleaned_address,
        "citycode": _get_citycode_from_address(cleaned_address)
    }
    
    if period is not None:
        result["period"] = period
    
    return result

def _clean_address_string(address: str) -> str:
    """
    住所文字列をクリーニング
    
    処理内容:
    1. 複数住所がある場合は地番を優先、なければ最初の住所を取得
    2. 住所番号の「・」区切りがある場合は最初の番号のみ取得
    3. 括弧内の付加情報を除去（地番）、【角部屋】など
    4. 不要な記号や空白の整理
    
    Args:
        address (str): 住所の生データ
        
    Returns:
        str: クリーニング済み住所
    """
    if not address:
        return address
    
    import re
    
    # 1. 複数住所の分離（「、」で区切り）
    address_parts = [part.strip() for part in address.split('、')]
    
    # 地番優先ロジック: 「（地番）」を含む住所で完全な住所があれば優先
    selected_address = address_parts[0]  # デフォルトは最初の住所
    for part in address_parts:
        if '（地番）' in part or '地番' in part:
            # 地番表記があり、かつ都道府県名を含む完全な住所の場合のみ優先
            if any(pref in part for pref in ['北海道', '県', '府', '都']):
                selected_address = part
                break
    
    # 2. 「／」で区切られた情報がある場合は最初の部分を取得
    selected_address = selected_address.split('／')[0].strip()
    
    # 3. 住所番号の「・」分割処理（番地部分のみ）
    # 例: 「平岸三条１４-68・72・73」→「平岸三条１４-68」
    if '・' in selected_address:
        # 「・」で分割されている番号の最初の部分のみ取得
        selected_address = re.sub(r'・[\d・]+', '', selected_address)
    
    # 4. 括弧内情報の除去
    # 丸括弧の除去: （地番）、（エアリー・地番）など
    selected_address = re.sub(r'（[^）]*）', '', selected_address)
    
    # 角括弧の除去: 【角部屋】など
    selected_address = re.sub(r'【[^】]*】', '', selected_address)
    
    # かぎ括弧の除去: 「物件価格+諸費用+おまとめ」など
    selected_address = re.sub(r'「[^」]*」', '', selected_address)
    
    # 5. 住所の後の不要な文字列を除去
    # 番地の後に続く住所と関係ない文字列を除去
    # スペースありなし両方の月日表記や不要文字列を除去
    selected_address = re.sub(
        r'(-?\d+(?:-\d+)?(?:号室)?)'  # 番地部分
        r'(\s*\d+月\d+日.*|\s*価格更新.*|\s*頭金.*|\s*物件.*|\s*諸費用.*|\s*おまとめ.*)',  # 日付表記以降や不要文字列（スペースあり・なし両方）
        r'\1', 
        selected_address
    )
    
    # 6. 不要な空白や記号の整理
    selected_address = re.sub(r'\s+', '', selected_address)  # 連続する空白を削除
    selected_address = selected_address.strip()
    
    return selected_address

def _get_citycode_from_address(address: str) -> Optional[str]:
    """
    住所文字列からcitycodeを取得
    都道府県名+市区町村名で先頭一致検索
    
    Args:
        address (str): 住所文字列
        
    Returns:
        Optional[str]: 見つかったcitycode、見つからない場合はNone
    """
    citycode_map = _load_citycode_map()
    
    # 最長一致でcitycodeを検索
    best_match = ""
    best_citycode = None
    
    for full_name, citycode in citycode_map.items():
        if address.startswith(full_name) and len(full_name) > len(best_match):
            best_match = full_name
            best_citycode = citycode
    
    return best_citycode

def generate_address_simple_type_schema() -> Dict[str, Any]:
    """
    シンプルな住所データ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: シンプルな住所データ用のtype情報
    """
    return {
        "base_type": "simple_address",
        "data_type": "object",
        "required_fields": ["location", "citycode"],
        "optional_fields": ["period"],
        "field_definitions": {
            "location": {
                "type": "string", 
                "description": "住所の生データ（location値）"
            },
            "citycode": {
                "type": "string", 
                "description": "市区町村コード（5桁）"
            },
            "period": {
                "type": "integer", 
                "description": "期別情報（第X期）"
            }
        }
    }

def generate_address_type_schema() -> Dict[str, Any]:
    """
    住所データ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: 住所データ用のtype情報
    """
    return {
        "base_type": "structured_address",
        "data_type": "object",
        "required_fields": ["raw"],
        "optional_fields": [
            "prefecture", "secondary_division", "secondary_type", 
            "tertiary_division", "tertiary_type", "remaining", 
            "hierarchy", "division_types", "parse_failed", "period"
        ],
        "field_definitions": {
            "raw": {
                "type": "string", 
                "description": "元の住所文字列（スクレイピング生データ）"
            },
            "prefecture": {
                "type": "string", 
                "description": "都道府県（東京都、北海道、○○府、○○県）"
            },
            "secondary_division": {
                "type": "string", 
                "description": "都道府県直下の区分（市区町村・郡・支庁等）"
            },
            "secondary_type": {
                "type": "string", 
                "enum": ["市", "区", "町", "村", "郡", "特別区", "支庁・振興局"],
                "description": "第二レベル区分のタイプ"
            },
            "tertiary_division": {
                "type": "string", 
                "description": "第三レベル区分（郡配下の町村）"
            },
            "tertiary_type": {
                "type": "string", 
                "enum": ["町", "村"],
                "description": "第三レベル区分のタイプ"
            },
            "remaining": {
                "type": "string", 
                "description": "残りの住所詳細（番地・建物名等）"
            },
            "hierarchy": {
                "type": "string", 
                "description": "行政区分の階層構造（例: 千葉県 -> 印旛郡 -> 酒々井町）"
            },
            "division_types": {
                "type": "string", 
                "description": "区分タイプの組み合わせ（例: 郡 -> 町）"
            },
            "parse_failed": {
                "type": "boolean", 
                "description": "住所解析に失敗した場合true"
            },
            "period": {
                "type": "integer", 
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "東京都特別区",
                "value": "東京都 -> 渋谷区"
            },
            {
                "description": "郡制地域", 
                "value": "千葉県 -> 印旛郡 -> 酒々井町"
            },
            {
                "description": "政令指定都市",
                "value": "神奈川県 -> 横浜市"
            },
            {
                "description": "北海道",
                "value": "北海道 -> 札幌市"
            }
        ],
        "analysis_keys": {
            "prefecture_grouping": {
                "field": "prefecture",
                "description": "都道府県別の集計・分析"
            },
            "administrative_type": {
                "field": ["secondary_type", "tertiary_type"],
                "description": "行政区分タイプ別の分析"
            },
            "hierarchy_analysis": {
                "field": "hierarchy",
                "description": "階層構造での分析"
            },
            "urban_rural_classification": {
                "field": "division_types",
                "description": "都市部・地方部の分類分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "都道府県別物件数",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.prefecture') as pref, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [address_id] GROUP BY pref"
            },
            {
                "purpose": "行政区分タイプ別分析",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.secondary_type') as type, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [address_id] GROUP BY type"
            },
            {
                "purpose": "階層構造での検索",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [address_id] AND JSON_EXTRACT(value_cleaned, '$.hierarchy') LIKE '%東京都%'"
            }
        ],
        "period_aware": True
    }

def generate_price_type_schema() -> Dict[str, Any]:
    """
    価格データ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: 価格データ用のtype情報
    """
    return {
        "base_type": "range_or_single",
        "data_type": "number",
        "required_fields": ["period"],
        "optional_fields": [
            "min", "max", "value", "unit", "is_undefined", 
            "tentative", "immediate_available", "note"
        ],
        "field_definitions": {
            "min": {
                "type": "number",
                "description": "価格帯の最小値（万円単位）"
            },
            "max": {
                "type": "number", 
                "description": "価格帯の最大値（万円単位）"
            },
            "value": {
                "type": "number",
                "description": "単一価格（万円単位）"
            },
            "unit": {
                "type": "string",
                "enum": ["万円", "円", "千円", "億円"],
                "description": "価格の単位"
            },
            "is_undefined": {
                "type": "boolean",
                "description": "価格未定の場合true"
            },
            "tentative": {
                "type": "boolean",
                "description": "予定価格の場合true"
            },
            "immediate_available": {
                "type": "boolean",
                "description": "即入居可の場合true"
            },
            "note": {
                "type": "string",
                "description": "追加情報・特記事項"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "価格帯", 
                "value": {"min": 2685, "max": 3955, "unit": "万円", "period": 4}
            },
            {
                "description": "単一価格",
                "value": {"value": 3200, "unit": "万円", "period": 4}
            },
            {
                "description": "価格未定",
                "value": {"is_undefined": True, "period": 4}
            },
            {
                "description": "予定価格",
                "value": {"min": 3000, "max": 4000, "unit": "万円", "tentative": True, "period": 4}
            }
        ],
        "analysis_keys": {
            "price_range_analysis": {
                "field": ["min", "max", "value"],
                "description": "価格帯・単価の分析"
            },
            "unit_standardization": {
                "field": "unit",
                "description": "単位別の価格正規化"
            },
            "market_status": {
                "field": ["is_undefined", "tentative"],
                "description": "市場状況・販売ステータス分析"
            },
            "period_comparison": {
                "field": "period",
                "description": "期別価格動向分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "価格帯分析",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.min') as min_price, JSON_EXTRACT(value_cleaned, '$.max') as max_price FROM estate_cleaned WHERE id_cleaned = [price_id] AND JSON_EXTRACT(value_cleaned, '$.min') IS NOT NULL"
            },
            {
                "purpose": "平均価格計算",
                "sql": "SELECT AVG(CASE WHEN JSON_EXTRACT(value_cleaned, '$.value') IS NOT NULL THEN JSON_EXTRACT(value_cleaned, '$.value') ELSE (JSON_EXTRACT(value_cleaned, '$.min') + JSON_EXTRACT(value_cleaned, '$.max'))/2 END) as avg_price FROM estate_cleaned WHERE id_cleaned = [price_id]"
            },
            {
                "purpose": "期別価格推移",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.period') as period, AVG(JSON_EXTRACT(value_cleaned, '$.value')) as avg_price FROM estate_cleaned WHERE id_cleaned = [price_id] GROUP BY period ORDER BY period"
            }
        ],
        "period_aware": True
    }

def generate_area_type_schema() -> Dict[str, Any]:
    """
    面積データ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: 面積データ用のtype情報
    """
    return {
        "base_type": "range_or_single",
        "data_type": "number",
        "required_fields": ["period"],
        "optional_fields": [
            "min", "max", "value", "unit", "is_undefined",
            "multiple_areas", "note"
        ],
        "field_definitions": {
            "min": {
                "type": "number",
                "description": "面積の最小値"
            },
            "max": {
                "type": "number",
                "description": "面積の最大値"
            },
            "value": {
                "type": "number",
                "description": "単一面積値"
            },
            "unit": {
                "type": "string",
                "enum": ["m²", "㎡", "坪", "畳"],
                "description": "面積の単位"
            },
            "is_undefined": {
                "type": "boolean",
                "description": "面積未定の場合true"
            },
            "multiple_areas": {
                "type": "array",
                "description": "複数面積の配列（その他面積等）",
                "items": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "number"},
                        "unit": {"type": "string"},
                        "description": {"type": "string"}
                    }
                }
            },
            "note": {
                "type": "string",
                "description": "面積に関する特記事項"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "面積帯",
                "value": {"min": 70.5, "max": 85.2, "unit": "m²", "period": 4}
            },
            {
                "description": "単一面積",
                "value": {"value": 75.8, "unit": "m²", "period": 4}
            },
            {
                "description": "複数面積",
                "value": {"multiple_areas": [{"value": 12.5, "unit": "m²", "description": "バルコニー"}, {"value": 8.3, "unit": "m²", "description": "テラス"}], "period": 4}
            }
        ],
        "analysis_keys": {
            "area_distribution": {
                "field": ["min", "max", "value"],
                "description": "面積分布・平均面積分析"
            },
            "unit_conversion": {
                "field": "unit",
                "description": "単位換算・標準化"
            },
            "additional_space": {
                "field": "multiple_areas",
                "description": "付加価値面積の分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "平均面積計算",
                "sql": "SELECT AVG(CASE WHEN JSON_EXTRACT(value_cleaned, '$.value') IS NOT NULL THEN JSON_EXTRACT(value_cleaned, '$.value') ELSE (JSON_EXTRACT(value_cleaned, '$.min') + JSON_EXTRACT(value_cleaned, '$.max'))/2 END) as avg_area FROM estate_cleaned WHERE id_cleaned = [area_id]"
            },
            {
                "purpose": "面積帯別物件数",
                "sql": "SELECT CASE WHEN JSON_EXTRACT(value_cleaned, '$.value') < 50 THEN '50m²未満' WHEN JSON_EXTRACT(value_cleaned, '$.value') < 80 THEN '50-80m²' ELSE '80m²以上' END as area_range, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [area_id] GROUP BY area_range"
            }
        ],
        "period_aware": True
    }

def generate_layout_type_schema() -> Dict[str, Any]:
    """
    間取りデータ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: 間取りデータ用のtype情報
    """
    return {
        "base_type": "structured_layout",
        "data_type": "object",
        "required_fields": ["raw", "period"],
        "optional_fields": [
            "rooms", "layout_type", "variations", "is_multiple",
            "parsed_layouts", "standardized"
        ],
        "field_definitions": {
            "raw": {
                "type": "string",
                "description": "元の間取り文字列"
            },
            "rooms": {
                "type": "string",
                "description": "主要間取り（例: 3LDK, 2DK）"
            },
            "layout_type": {
                "type": "string",
                "enum": ["LDK", "DK", "K", "R", "1R", "S", "SLDK"],
                "description": "間取りタイプ"
            },
            "variations": {
                "type": "array",
                "description": "間取りバリエーション",
                "items": {"type": "string"}
            },
            "is_multiple": {
                "type": "boolean",
                "description": "複数間取りの場合true"
            },
            "parsed_layouts": {
                "type": "array",
                "description": "解析済み間取り詳細",
                "items": {
                    "type": "object",
                    "properties": {
                        "bedrooms": {"type": "integer"},
                        "living": {"type": "boolean"},
                        "dining": {"type": "boolean"}, 
                        "kitchen": {"type": "boolean"},
                        "service": {"type": "boolean"}
                    }
                }
            },
            "standardized": {
                "type": "string",
                "description": "標準化された間取り表記"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "単一間取り",
                "value": {"raw": "3LDK", "rooms": "3LDK", "layout_type": "LDK", "period": 4}
            },
            {
                "description": "複数間取り",
                "value": {"raw": "2LDK・3LDK", "is_multiple": True, "variations": ["2LDK", "3LDK"], "period": 4}
            },
            {
                "description": "解析済み",
                "value": {"raw": "3LDK", "parsed_layouts": [{"bedrooms": 3, "living": True, "dining": True, "kitchen": True}], "period": 4}
            }
        ],
        "analysis_keys": {
            "room_count_analysis": {
                "field": ["rooms", "parsed_layouts"],
                "description": "部屋数・間取りタイプ別分析"
            },
            "layout_popularity": {
                "field": "layout_type",
                "description": "間取りタイプ別人気度分析"
            },
            "variation_analysis": {
                "field": ["is_multiple", "variations"],
                "description": "間取りバリエーション分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "間取り別物件数",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.layout_type') as layout, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [layout_id] GROUP BY layout"
            },
            {
                "purpose": "部屋数分布",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.parsed_layouts[0].bedrooms') as bedrooms, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [layout_id] GROUP BY bedrooms"
            }
        ],
        "period_aware": True
    }

def generate_date_type_schema() -> Dict[str, Any]:
    """
    日付データ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: 日付データ用のtype情報
    """
    return {
        "base_type": "date_or_period",
        "data_type": "date",
        "required_fields": ["period"],
        "optional_fields": [
            "year", "month", "day", "period_text", "estimated_date",
            "completed", "tentative", "immediate", "is_undefined"
        ],
        "field_definitions": {
            "year": {
                "type": "integer",
                "description": "年（西暦）"
            },
            "month": {
                "type": "integer",
                "description": "月"
            },
            "day": {
                "type": "integer",
                "description": "日"
            },
            "period_text": {
                "type": "string",
                "enum": ["上旬", "中旬", "下旬"],
                "description": "期間テキスト"
            },
            "estimated_date": {
                "type": "string",
                "description": "推定日付（YYYY-MM-DD形式）"
            },
            "completed": {
                "type": "boolean",
                "description": "完成済み・竣工済みの場合true"
            },
            "tentative": {
                "type": "boolean",
                "description": "予定の場合true"
            },
            "immediate": {
                "type": "boolean",
                "description": "即時の場合true"
            },
            "is_undefined": {
                "type": "boolean",
                "description": "日付未定の場合true"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "具体的日付",
                "value": {"year": 2024, "month": 3, "estimated_date": "2024-03-01", "period": 4}
            },
            {
                "description": "期間指定",
                "value": {"year": 2024, "month": 3, "period_text": "下旬", "estimated_date": "2024-03-25", "period": 4}
            },
            {
                "description": "完成済み",
                "value": {"completed": True, "period": 4}
            },
            {
                "description": "日付未定",
                "value": {"is_undefined": True, "period": 4}
            }
        ],
        "analysis_keys": {
            "timeline_analysis": {
                "field": ["year", "month", "estimated_date"],
                "description": "時系列・スケジュール分析"
            },
            "completion_status": {
                "field": ["completed", "tentative", "immediate"],
                "description": "完成状況・スケジュール状態分析"
            },
            "seasonal_trends": {
                "field": ["month", "period_text"],
                "description": "季節別・月別トレンド分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "年別完成予定",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.year') as year, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [date_id] AND JSON_EXTRACT(value_cleaned, '$.year') IS NOT NULL GROUP BY year"
            },
            {
                "purpose": "完成状況別",
                "sql": "SELECT CASE WHEN JSON_EXTRACT(value_cleaned, '$.completed') = true THEN '完成済み' WHEN JSON_EXTRACT(value_cleaned, '$.tentative') = true THEN '予定' ELSE 'その他' END as status, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [date_id] GROUP BY status"
            }
        ],
        "period_aware": True
    }

def generate_access_type_schema() -> Dict[str, Any]:
    """
    交通アクセスデータ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: 交通アクセスデータ用のtype情報
    """
    return {
        "base_type": "access_routes",
        "data_type": "array",
        "required_fields": ["routes", "period"],
        "optional_fields": ["note"],
        "field_definitions": {
            "routes": {
                "type": "array",
                "description": "交通ルート配列",
                "items": {
                    "type": "object",
                    "properties": {
                        "line": {"type": "string", "description": "路線名"},
                        "station": {"type": "string", "description": "駅名"},
                        "method": {"type": "string", "description": "交通手段"},
                        "time": {"type": "integer", "description": "所要時間（分）"},
                        "distance": {"type": "number", "description": "距離（km）"}
                    }
                }
            },
            "note": {
                "type": "string",
                "description": "交通アクセスに関する特記事項"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "複数路線アクセス",
                "value": {
                    "routes": [
                        {"line": "JR山手線", "station": "新宿駅", "method": "徒歩", "time": 5},
                        {"line": "東京メトロ丸の内線", "station": "新宿三丁目駅", "method": "徒歩", "time": 3}
                    ],
                    "period": 4
                }
            }
        ],
        "analysis_keys": {
            "accessibility_score": {
                "field": ["routes"],
                "description": "アクセス利便性スコア算出"
            },
            "transportation_method": {
                "field": "routes[].method",
                "description": "交通手段別分析"
            },
            "commute_time": {
                "field": "routes[].time",
                "description": "通勤時間帯別分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "平均アクセス時間",
                "sql": "SELECT AVG(JSON_EXTRACT(route.value, '$.time')) as avg_time FROM estate_cleaned, JSON_EACH(JSON_EXTRACT(value_cleaned, '$.routes')) as route WHERE id_cleaned = [access_id]"
            },
            {
                "purpose": "路線別物件数",
                "sql": "SELECT JSON_EXTRACT(route.value, '$.line') as line, COUNT(DISTINCT id_run) FROM estate_cleaned, JSON_EACH(JSON_EXTRACT(value_cleaned, '$.routes')) as route WHERE id_cleaned = [access_id] GROUP BY line"
            }
        ],
        "period_aware": True
    }

def generate_boolean_type_schema() -> Dict[str, Any]:
    """
    Boolean（有無）データ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: Booleanデータ用のtype情報  
    """
    return {
        "base_type": "boolean_with_details",
        "data_type": "boolean",
        "required_fields": ["value", "period"],
        "optional_fields": ["details", "note", "availability_type"],
        "field_definitions": {
            "value": {
                "type": "boolean",
                "description": "有無の真偽値"
            },
            "details": {
                "type": "string",
                "description": "詳細情報（料金、条件等）"
            },
            "note": {
                "type": "string",
                "description": "特記事項"
            },
            "availability_type": {
                "type": "string",
                "enum": ["有", "無", "可", "不可", "要確認", "条件付き"],
                "description": "可用性タイプ"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "単純な有無",
                "value": {"value": True, "availability_type": "有", "period": 4}
            },
            {
                "description": "詳細情報付き",
                "value": {"value": True, "details": "月額1万円", "availability_type": "有", "period": 4}
            },
            {
                "description": "条件付き",
                "value": {"value": True, "details": "抽選", "availability_type": "条件付き", "period": 4}
            }
        ],
        "analysis_keys": {
            "availability_rate": {
                "field": "value",
                "description": "設備・サービス提供率"
            },
            "condition_analysis": {
                "field": ["availability_type", "details"],
                "description": "提供条件・詳細分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "設備提供率",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.value') as available, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [boolean_id] GROUP BY available"
            },
            {
                "purpose": "提供条件別",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.availability_type') as type, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [boolean_id] GROUP BY type"
            }
        ],
        "period_aware": True
    }

def generate_number_type_schema() -> Dict[str, Any]:
    """
    数値データ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: 数値データ用のtype情報
    """
    return {
        "base_type": "number_with_unit",
        "data_type": "number",
        "required_fields": ["period"],
        "optional_fields": ["value", "unit", "is_undefined", "note"],
        "field_definitions": {
            "value": {
                "type": "number",
                "description": "数値"
            },
            "unit": {
                "type": "string",
                "description": "単位（階、戸、台等）"
            },
            "is_undefined": {
                "type": "boolean",
                "description": "未定の場合true"
            },
            "note": {
                "type": "string",
                "description": "補足情報"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "階数",
                "value": {"value": 15, "unit": "階", "period": 4}
            },
            {
                "description": "戸数",
                "value": {"value": 180, "unit": "戸", "period": 4}
            }
        ],
        "analysis_keys": {
            "value_distribution": {
                "field": "value",
                "description": "数値分布分析"
            },
            "unit_categorization": {
                "field": "unit",
                "description": "単位別カテゴリ分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "平均値計算",
                "sql": "SELECT AVG(JSON_EXTRACT(value_cleaned, '$.value')) as avg_value FROM estate_cleaned WHERE id_cleaned = [number_id] AND JSON_EXTRACT(value_cleaned, '$.value') IS NOT NULL"
            }
        ],
        "period_aware": True
    }

def generate_text_type_schema() -> Dict[str, Any]:
    """
    テキストデータ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: テキストデータ用のtype情報
    """
    return {
        "base_type": "structured_text",
        "data_type": "text",
        "required_fields": ["value", "period"],
        "optional_fields": ["category", "keywords", "is_null"],
        "field_definitions": {
            "value": {
                "type": "string",
                "description": "テキスト内容"
            },
            "category": {
                "type": "string",
                "description": "テキストカテゴリ"
            },
            "keywords": {
                "type": "array",
                "description": "抽出キーワード",
                "items": {"type": "string"}
            },
            "is_null": {
                "type": "boolean",
                "description": "分析対象外の場合true"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "通常テキスト",
                "value": {"value": "南向きバルコニー", "keywords": ["南向き", "バルコニー"], "period": 4}
            }
        ],
        "analysis_keys": {
            "keyword_frequency": {
                "field": "keywords",
                "description": "キーワード頻度分析"
            },
            "category_distribution": {
                "field": "category",
                "description": "カテゴリ別分布"
            }
        },
        "sql_examples": [
            {
                "purpose": "キーワード検索",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [text_id] AND JSON_EXTRACT(value_cleaned, '$.value') LIKE '%keyword%'"
            }
        ],
        "period_aware": True
    }

def clean_utility_cost_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    目安光熱費をJSON形式でクレンジング
    例: "約18.8万円～19万円/年" -> {"min": 18.8, "max": 19, "unit": "万円", "frequency": "年", "period": 4}
    例: "約18.6万円/年" -> {"value": 18.6, "unit": "万円", "frequency": "年", "period": 4}
    """
    if not value or value.strip() == "":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # 「未定」「要相談」などのケース（_should_nullify_textより先にチェック）
    if "未定" in value or "要相談" in value or value.strip() == "未定":
        result["value"] = None
        result["is_undefined"] = True
        if period is not None:
            result["period"] = period
        return result
    
    # 汎用的な無効データチェック（ただし「未定」は除外済み）
    if _should_nullify_text(value):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    # 「約」の表記を検出
    if "約" in value:
        result["approximate"] = True
    
    # 頻度を抽出（年、月など）
    if "/年" in value or "年" in value:
        result["frequency"] = "年"
    elif "/月" in value or "月" in value:
        result["frequency"] = "月"
    
    # 価格範囲の抽出
    # パターン1: 「約18.8万円～19万円/年」
    range_pattern = r'約?(\d+(?:\.\d+)?)万円～(\d+(?:\.\d+)?)万円'
    range_match = re.search(range_pattern, value)
    
    if range_match:
        min_val = float(range_match.group(1))
        max_val = float(range_match.group(2))
        result["min"] = min_val
        result["max"] = max_val
        result["unit"] = "万円"
    else:
        # パターン2: 「約18.6万円/年」
        single_pattern = r'約?(\d+(?:\.\d+)?)万円'
        single_match = re.search(single_pattern, value)
        
        if single_match:
            val = float(single_match.group(1))
            result["value"] = val
            result["unit"] = "万円"
        else:
            # パターンにマッチしない場合は元の値を保存
            result["value"] = value
            result["parse_failed"] = True
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_feature_pickup_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    特徴ピックアップをJSON形式で構造化
    例: "土地50坪以上/角地/都市ガス" -> 構造化されたJSON
    """
    if not value or value.strip() == "":
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    
    # 特徴ピックアップは長いリストになることがあるため、長さ制限をスキップ
    # その他の無効データパターンのみチェック
    if value.strip() in ["-", "－", "ー", "未定", "未設定", "なし", "無し", "N/A", ""]:
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    # 分析に重要でないパターンのチェック
    unimportant_patterns = [
        "■支払い例", "■ローンのご案内", "提携ローン", "※ローンは一定要件該当者が対象",
        "※金利は", "融資限度額", "事務手数料", "保証料", "適用される金利は融資実行時",
        "お申込みの際には、お認印", "収入証明書", "本人確認書類", "運転免許証",
        "健康保険証", "パスポート", "先着順販売のため販売済の場合",
        "販売開始まで契約または予約の申し込み", "申し込み順位の確保につながる行為は一切できません",
        "確定情報は新規分譲広告において明示", "物件データは第", "期以降の全販売対象住戸",
        "のものを表記", "受付時間／", "定休日／", "受付場所／", "マンションギャラリー"
    ]
    
    for pattern in unimportant_patterns:
        if pattern in value:
            result = {"value": None}
            if period is not None:
                result["period"] = period
            return result
    
    # スラッシュ区切りで特徴を分割（前後の空白も含めて）
    features = [f.strip() for f in re.split(r'\s*/\s*', value) if f.strip()]
    if not features:
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    # 構造化データの初期化
    structured_features = {
        "certifications": {},
        "building_specs": {},
        "equipment": {
            "kitchen": [],
            "bathroom": [],
            "heating_cooling": [],
            "utilities": [],
            "security": [],
            "other": []
        },
        "location_access": {},
        "land_features": {},
        "parking_transport": {},
        "room_features": {},
        "maintenance": {}
    }
    
    feature_tags = []
    
    for feature in features:
        feature_lower = feature.lower()
        
        # 認証・評価書系
        if "設計住宅性能評価書" in feature:
            structured_features["certifications"]["design_performance_evaluation"] = True
            feature_tags.append("design_performance_cert")
        elif "建設住宅性能評価書" in feature:
            structured_features["certifications"]["construction_performance_evaluation"] = True
            feature_tags.append("construction_performance_cert")
        elif "長期優良住宅認定通知書" in feature:
            structured_features["certifications"]["long_term_excellent_housing"] = True
            feature_tags.append("long_term_excellent")
        elif "フラット３５" in feature or "フラット35" in feature:
            structured_features["certifications"]["flat35_s"] = True
            feature_tags.append("flat35_s")
        elif "bels" in feature_lower or "省エネ基準適合認定書" in feature:
            structured_features["certifications"]["bels"] = True
            feature_tags.append("bels")
        elif "瑕疵保証" in feature:
            structured_features["certifications"]["defect_warranty"] = True
            feature_tags.append("defect_warranty")
        
        # 建物仕様系
        elif "２階建" in feature or "2階建" in feature:
            structured_features["building_specs"]["stories"] = 2
            feature_tags.append("2_story")
        elif "３階建以上" in feature or "3階建以上" in feature:
            structured_features["building_specs"]["stories"] = 3
            feature_tags.append("3_story_plus")
        elif "南向き" in feature:
            structured_features["building_specs"]["orientation"] = "south"
            feature_tags.append("south_facing")
        elif "東南向き" in feature:
            structured_features["building_specs"]["orientation"] = "southeast"
            feature_tags.append("southeast_facing")
        elif "全室南向き" in feature:
            structured_features["building_specs"]["all_rooms_south"] = True
            feature_tags.append("all_rooms_south")
        elif "陽当り良好" in feature:
            structured_features["building_specs"]["good_sunlight"] = True
            feature_tags.append("good_sunlight")
        
        # LDK面積
        elif "ＬＤＫ１５畳以上" in feature or "LDK15畳以上" in feature:
            structured_features["building_specs"]["ldk_size_tatami"] = {"min": 15}
            feature_tags.append("ldk_15tatami_plus")
        elif "ＬＤＫ１８畳以上" in feature or "LDK18畳以上" in feature:
            structured_features["building_specs"]["ldk_size_tatami"] = {"min": 18}
            feature_tags.append("ldk_18tatami_plus")
        elif "ＬＤＫ２０畳以上" in feature or "LDK20畳以上" in feature:
            structured_features["building_specs"]["ldk_size_tatami"] = {"min": 20}
            feature_tags.append("ldk_20tatami_plus")
        
        # 設備系 - キッチン
        elif "システムキッチン" in feature:
            structured_features["equipment"]["kitchen"].append("system")
            feature_tags.append("system_kitchen")
        elif "対面式キッチン" in feature:
            structured_features["equipment"]["kitchen"].append("counter_facing")
            feature_tags.append("counter_kitchen")
        elif "ＩＨクッキングヒーター" in feature or "IHクッキングヒーター" in feature:
            structured_features["equipment"]["kitchen"].append("ih_cooktop")
            feature_tags.append("ih_cooktop")
        elif "食器洗乾燥機" in feature:
            structured_features["equipment"]["kitchen"].append("dishwasher")
            feature_tags.append("dishwasher")
        elif "浄水器" in feature:
            structured_features["equipment"]["kitchen"].append("water_purifier")
            feature_tags.append("water_purifier")
        
        # 設備系 - 浴室
        elif "浴室乾燥機" in feature:
            structured_features["equipment"]["bathroom"].append("dryer")
            feature_tags.append("bathroom_dryer")
        elif "浴室１坪以上" in feature or "浴室1坪以上" in feature:
            structured_features["building_specs"]["bathroom_size_tsubo"] = {"min": 1}
            feature_tags.append("bathroom_1tsubo_plus")
        elif "浴室に窓" in feature:
            structured_features["equipment"]["bathroom"].append("window")
            feature_tags.append("bathroom_window")
        elif "オートバス" in feature:
            structured_features["equipment"]["bathroom"].append("auto_bath")
            feature_tags.append("auto_bath")
        
        # 設備系 - 暖房・冷房
        elif "床暖房" in feature:
            structured_features["equipment"]["heating_cooling"].append("floor_heating")
            feature_tags.append("floor_heating")
        elif "省エネルギー対策" in feature:
            structured_features["equipment"]["heating_cooling"].append("energy_saving")
            feature_tags.append("energy_saving")
        elif "省エネ給湯器" in feature:
            structured_features["equipment"]["heating_cooling"].append("energy_saving_water_heater")
            feature_tags.append("energy_saving_heater")
        
        # 設備系 - ユーティリティ
        elif "オール電化" in feature:
            structured_features["equipment"]["utilities"].append("all_electric")
            feature_tags.append("all_electric")
        elif "都市ガス" in feature:
            structured_features["equipment"]["utilities"].append("city_gas")
            feature_tags.append("city_gas")
        elif "エレベーター" in feature:
            structured_features["equipment"]["utilities"].append("elevator")
            feature_tags.append("elevator")
        elif "複層ガラス" in feature:
            structured_features["equipment"]["utilities"].append("double_glazing")
            feature_tags.append("double_glazing")
        
        # 設備系 - セキュリティ
        elif "セキュリティ充実" in feature:
            structured_features["equipment"]["security"].append("enhanced")
            feature_tags.append("security_enhanced")
        elif "ＴＶモニタ付インターホン" in feature or "TVモニタ付インターホン" in feature:
            structured_features["equipment"]["security"].append("tv_intercom")
            feature_tags.append("tv_intercom")
        elif "スマートキー" in feature:
            structured_features["equipment"]["security"].append("smart_key")
            feature_tags.append("smart_key")
        
        # 立地・アクセス系
        elif "スーパー 徒歩10分以内" in feature or "スーパー徒歩10分以内" in feature:
            structured_features["location_access"]["supermarket_walk_min"] = {"max": 10}
            feature_tags.append("supermarket_walk_10min")
        elif "小学校 徒歩10分以内" in feature or "小学校徒歩10分以内" in feature:
            structured_features["location_access"]["elementary_school_walk_min"] = {"max": 10}
            feature_tags.append("school_walk_10min")
        elif "駅まで平坦" in feature:
            structured_features["location_access"]["station_flat_access"] = True
            feature_tags.append("station_flat")
        elif "閑静な住宅地" in feature:
            structured_features["location_access"]["quiet_residential"] = True
            feature_tags.append("quiet_area")
        elif "緑豊かな住宅地" in feature:
            structured_features["location_access"]["green_residential"] = True
            feature_tags.append("green_area")
        elif "２沿線以上利用可" in feature or "2沿線以上利用可" in feature:
            structured_features["parking_transport"]["multiple_rail_lines"] = True
            feature_tags.append("multiple_lines")
        
        # 土地特徴系
        elif "土地50坪以上" in feature or "土地５０坪以上" in feature:
            structured_features["land_features"]["area_tsubo"] = {"min": 50}
            feature_tags.append("land_50tsubo_plus")
        elif "角地" in feature:
            structured_features["land_features"]["corner_lot"] = True
            feature_tags.append("corner_lot")
        elif "南側道路面す" in feature:
            structured_features["land_features"]["south_facing_road"] = True
            feature_tags.append("south_road")
        elif "前道６ｍ以上" in feature or "前道6m以上" in feature:
            structured_features["land_features"]["road_width_m"] = {"min": 6}
            feature_tags.append("road_6m_plus")
        elif "整形地" in feature:
            structured_features["land_features"]["regular_shape"] = True
            feature_tags.append("regular_shape")
        elif "平坦地" in feature:
            structured_features["land_features"]["flat_land"] = True
            feature_tags.append("flat_land")
        
        # 駐車場・交通系
        elif "駐車２台可" in feature or "駐車2台可" in feature:
            structured_features["parking_transport"]["parking_capacity"] = 2
            feature_tags.append("parking_2cars")
        elif "駐車３台以上可" in feature or "駐車3台以上可" in feature:
            structured_features["parking_transport"]["parking_capacity"] = 3
            feature_tags.append("parking_3cars_plus")
        
        # 室内特徴系（複合パターンを先に処理）
        elif "最上階角住戸" in feature:
            structured_features["room_features"]["corner_unit"] = True
            structured_features["room_features"]["top_floor"] = True
            feature_tags.append("top_floor_corner")
        elif "角住戸" in feature:
            structured_features["room_features"]["corner_unit"] = True
            feature_tags.append("corner_unit")
        elif "最上階" in feature:
            structured_features["room_features"]["top_floor"] = True
            feature_tags.append("top_floor")
        elif "全居室収納" in feature:
            structured_features["room_features"]["all_rooms_storage"] = True
            feature_tags.append("all_rooms_storage")
        elif "ウォークインクローゼット" in feature:
            structured_features["room_features"]["walk_in_closet"] = True
            feature_tags.append("walk_in_closet")
        elif "トイレ２ヶ所" in feature or "トイレ2ヶ所" in feature:
            structured_features["room_features"]["toilets_count"] = 2
            feature_tags.append("2_toilets")
        elif "和室" in feature:
            structured_features["room_features"]["japanese_room"] = True
            feature_tags.append("japanese_room")
        elif "ペット相談" in feature:
            structured_features["room_features"]["pet_negotiable"] = True
            feature_tags.append("pet_ok")
        
        # メンテナンス・リフォーム系
        elif "内装リフォーム" in feature:
            structured_features["maintenance"]["interior_reform"] = True
            feature_tags.append("interior_reform")
        elif "外装リフォーム" in feature:
            structured_features["maintenance"]["exterior_reform"] = True
            feature_tags.append("exterior_reform")
        elif "内外装リフォーム" in feature:
            structured_features["maintenance"]["full_reform"] = True
            feature_tags.append("full_reform")
        
        # 価格・販売関連情報
        elif "分譲時の価格帯" in feature:
            feature_tags.append("original_sale_price")
        
        # その他の特徴をタグとして保存
        else:
            # 特殊文字を除去してタグ化
            tag = re.sub(r'[^\w\d]', '_', feature).lower()
            if tag and tag not in feature_tags:
                feature_tags.append(tag)
    
    # 空の辞書を削除
    structured_features = {k: v for k, v in structured_features.items() if v}
    for category in ["equipment"]:
        if category in structured_features:
            structured_features[category] = {k: v for k, v in structured_features[category].items() if v}
    
    # 期待される形式に合わせて、feature_tagsを日本語のままにする
    result = {
        "feature_tags": features,  # 元の日本語テキストをそのまま使用
        "feature_count": len(features)
    }
    
    if period is not None:
        result["period"] = period
    
    return result

def clean_rating_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    評価データをJSON形式でクレンジング
    例: "5段階/7段階中" -> {"current_level": 5, "max_level": 7, "percentage": 71.4}
    """
    if not value or value.strip() == "" or value.strip() in ["-", "－"] or _should_nullify_text(value.strip()):
        result = {"value": None}
        if period is not None:
            result["period"] = period
        return result
    
    value = value.strip()
    result = {}
    
    # 「X段階/Y段階中」のパターンをマッチ
    rating_pattern = r'(\d+)段階/(\d+)段階中'
    match = re.match(rating_pattern, value)
    
    if match:
        current = int(match.group(1))
        max_val = int(match.group(2))
        
        result["current_level"] = current
        result["max_level"] = max_val
        result["rating_text"] = value
        
        # パーセンテージ計算
        if max_val > 0:
            percentage = (current / max_val) * 100
            result["percentage"] = round(percentage, 1)
    else:
        # パターンにマッチしない場合は元の値を保存
        result["rating_text"] = value
        result["parse_failed"] = True
    
    if period is not None:
        result["period"] = period
    
    return result

def generate_utility_cost_type_schema() -> Dict[str, Any]:
    """
    目安光熱費用のtype定義を生成
    
    Returns:
        Dict[str, Any]: 光熱費用のtype情報
    """
    return {
        "base_type": "range_or_single",
        "data_type": "utility_cost",
        "required_fields": ["period"],
        "optional_fields": [
            "min", "max", "value", "unit", "frequency", "approximate",
            "is_undefined", "note", "parse_failed"
        ],
        "field_definitions": {
            "min": {
                "type": "number",
                "description": "最小費用（万円単位）"
            },
            "max": {
                "type": "number", 
                "description": "最大費用（万円単位）"
            },
            "value": {
                "type": "number",
                "description": "単一費用値（万円単位）"
            },
            "unit": {
                "type": "string",
                "description": "単位（万円、円など）"
            },
            "frequency": {
                "type": "string",
                "description": "頻度（年、月など）"
            },
            "approximate": {
                "type": "boolean",
                "description": "概算値の場合true"
            },
            "is_undefined": {
                "type": "boolean",
                "description": "費用未定の場合true"
            },
            "parse_failed": {
                "type": "boolean",
                "description": "パース失敗の場合true"
            },
            "note": {
                "type": "string",
                "description": "費用に関する補足情報"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "年間費用範囲",
                "value": {"min": 18.8, "max": 19, "unit": "万円", "frequency": "年", "approximate": True, "period": 4}
            },
            {
                "description": "年間費用単一値",
                "value": {"value": 18.6, "unit": "万円", "frequency": "年", "approximate": True, "period": 4}
            },
            {
                "description": "費用未定",
                "value": {"value": None, "is_undefined": True, "period": 4}
            }
        ],
        "analysis_keys": {
            "cost_range_analysis": {
                "field": ["min", "max", "value"],
                "description": "光熱費範囲分析"
            },
            "annual_cost_average": {
                "field": "value",
                "description": "年間平均光熱費"
            },
            "frequency_distribution": {
                "field": "frequency",
                "description": "光熱費算出頻度分布"
            }
        },
        "sql_examples": [
            {
                "purpose": "年間光熱費平均",
                "sql": "SELECT AVG(CASE WHEN JSON_EXTRACT(value_cleaned, '$.min') IS NOT NULL THEN (JSON_EXTRACT(value_cleaned, '$.min') + JSON_EXTRACT(value_cleaned, '$.max'))/2 ELSE JSON_EXTRACT(value_cleaned, '$.value') END) as avg_cost FROM estate_cleaned WHERE id_cleaned = [utility_cost_id] AND JSON_EXTRACT(value_cleaned, '$.frequency') = '年'"
            },
            {
                "purpose": "光熱費範囲検索",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [utility_cost_id] AND ((JSON_EXTRACT(value_cleaned, '$.min') IS NOT NULL AND JSON_EXTRACT(value_cleaned, '$.max') <= 20) OR (JSON_EXTRACT(value_cleaned, '$.value') IS NOT NULL AND JSON_EXTRACT(value_cleaned, '$.value') <= 20))"
            },
            {
                "purpose": "概算費用物件抽出",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [utility_cost_id] AND JSON_EXTRACT(value_cleaned, '$.approximate') = true"
            }
        ],
        "period_aware": True
    }

def generate_feature_pickup_type_schema() -> Dict[str, Any]:
    """
    特徴ピックアップ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: 特徴ピックアップのtype情報
    """
    return {
        "base_type": "structured_features",
        "data_type": "features",
        "required_fields": ["period"],
        "optional_fields": [
            "feature_tags", "structured_features", "raw_features", "feature_count"
        ],
        "field_definitions": {
            "feature_tags": {
                "type": "array",
                "description": "特徴タグの配列",
                "items": {"type": "string"}
            },
            "structured_features": {
                "type": "object",
                "description": "構造化された特徴情報",
                "properties": {
                    "certifications": {
                        "type": "object",
                        "description": "認証・評価書関連"
                    },
                    "building_specs": {
                        "type": "object", 
                        "description": "建物仕様関連"
                    },
                    "equipment": {
                        "type": "object",
                        "description": "設備関連",
                        "properties": {
                            "kitchen": {"type": "array"},
                            "bathroom": {"type": "array"},
                            "heating_cooling": {"type": "array"},
                            "utilities": {"type": "array"},
                            "security": {"type": "array"}
                        }
                    },
                    "location_access": {
                        "type": "object",
                        "description": "立地・アクセス関連"
                    },
                    "land_features": {
                        "type": "object",
                        "description": "土地特徴関連"
                    },
                    "parking_transport": {
                        "type": "object",
                        "description": "駐車場・交通関連"
                    },
                    "room_features": {
                        "type": "object",
                        "description": "室内特徴関連"
                    },
                    "maintenance": {
                        "type": "object",
                        "description": "メンテナンス・リフォーム関連"
                    }
                }
            },
            "raw_features": {
                "type": "array",
                "description": "元の特徴文字列の配列",
                "items": {"type": "string"}
            },
            "feature_count": {
                "type": "integer",
                "description": "特徴の総数"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "戸建住宅の特徴",
                "value": {
                    "feature_tags": ["land_50tsubo_plus", "corner_lot", "system_kitchen", "parking_2cars"],
                    "structured_features": {
                        "land_features": {"area_tsubo": {"min": 50}, "corner_lot": True},
                        "equipment": {"kitchen": ["system"]},
                        "parking_transport": {"parking_capacity": 2}
                    },
                    "raw_features": ["土地50坪以上", "角地", "システムキッチン", "駐車2台可"],
                    "feature_count": 4,
                    "period": 4
                }
            },
            {
                "description": "マンションの特徴",
                "value": {
                    "feature_tags": ["elevator", "corner_unit", "security_enhanced"],
                    "structured_features": {
                        "equipment": {"utilities": ["elevator"], "security": ["enhanced"]},
                        "room_features": {"corner_unit": True}
                    },
                    "raw_features": ["エレベーター", "角住戸", "セキュリティ充実"],
                    "feature_count": 3,
                    "period": 4
                }
            }
        ],
        "analysis_keys": {
            "feature_frequency": {
                "field": "feature_tags",
                "description": "特徴頻度分析"
            },
            "equipment_analysis": {
                "field": ["structured_features", "equipment"],
                "description": "設備分析"
            },
            "certification_analysis": {
                "field": ["structured_features", "certifications"],
                "description": "認証・評価分析"
            },
            "location_analysis": {
                "field": ["structured_features", "location_access"],
                "description": "立地・アクセス分析"
            },
            "land_analysis": {
                "field": ["structured_features", "land_features"],
                "description": "土地特徴分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "特定の特徴を持つ物件検索",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [feature_id] AND JSON_EXTRACT(value_cleaned, '$.feature_tags') LIKE '%elevator%'"
            },
            {
                "purpose": "駐車場台数別集計",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.structured_features.parking_transport.parking_capacity') as parking_capacity, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [feature_id] GROUP BY parking_capacity"
            },
            {
                "purpose": "認証取得物件抽出",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [feature_id] AND JSON_EXTRACT(value_cleaned, '$.structured_features.certifications') IS NOT NULL"
            },
            {
                "purpose": "特徴数による分析",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.feature_count') as feature_count, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [feature_id] GROUP BY feature_count ORDER BY feature_count"
            },
            {
                "purpose": "LDK面積別集計",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.structured_features.building_specs.ldk_size_tatami.min') as ldk_size, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [feature_id] AND JSON_EXTRACT(value_cleaned, '$.structured_features.building_specs.ldk_size_tatami') IS NOT NULL GROUP BY ldk_size"
            }
        ],
        "period_aware": True
    }

def generate_rating_type_schema() -> Dict[str, Any]:
    """
    評価・格付けデータ用のtype定義を生成
    
    Returns:
        Dict[str, Any]: 評価データ用のtype情報
    """
    return {
        "base_type": "rating_scale",
        "data_type": "rating",
        "required_fields": ["period"],
        "optional_fields": [
            "current_level", "max_level", "rating_text", "percentage",
            "is_undefined", "note", "parse_failed", "value"
        ],
        "field_definitions": {
            "current_level": {
                "type": "number",
                "description": "現在の評価レベル（例: 5段階中の5）"
            },
            "max_level": {
                "type": "number",
                "description": "最大評価レベル（例: 7段階中の7）"
            },
            "rating_text": {
                "type": "string",
                "description": "評価の文字列表現（例: 5段階/7段階中）"
            },
            "percentage": {
                "type": "number",
                "description": "パーセンテージ換算値（0-100）"
            },
            "value": {
                "type": "null",
                "description": "評価なしの場合null"
            },
            "is_undefined": {
                "type": "boolean",
                "description": "評価未定の場合true"
            },
            "parse_failed": {
                "type": "boolean",
                "description": "パース失敗の場合true"
            },
            "note": {
                "type": "string",
                "description": "評価に関する補足情報"
            },
            "period": {
                "type": "integer",
                "description": "期別情報"
            }
        },
        "examples": [
            {
                "description": "断熱性能評価",
                "value": {"current_level": 5, "max_level": 7, "rating_text": "5段階/7段階中", "percentage": 71.4, "period": 4}
            },
            {
                "description": "最高評価",
                "value": {"current_level": 7, "max_level": 7, "rating_text": "7段階/7段階中", "percentage": 100, "period": 4}
            },
            {
                "description": "評価なし",
                "value": {"value": None, "period": 4}
            }
        ],
        "analysis_keys": {
            "rating_distribution": {
                "field": ["current_level", "max_level"],
                "description": "評価レベル分布分析"
            },
            "performance_score": {
                "field": "percentage",
                "description": "性能スコア分析"
            },
            "rating_scale_analysis": {
                "field": "max_level",
                "description": "評価スケール別分析"
            }
        },
        "sql_examples": [
            {
                "purpose": "平均評価レベル",
                "sql": "SELECT AVG(JSON_EXTRACT(value_cleaned, '$.current_level')) as avg_level, AVG(JSON_EXTRACT(value_cleaned, '$.max_level')) as avg_max FROM estate_cleaned WHERE id_cleaned = [rating_id] AND JSON_EXTRACT(value_cleaned, '$.current_level') IS NOT NULL"
            },
            {
                "purpose": "評価分布",
                "sql": "SELECT JSON_EXTRACT(value_cleaned, '$.current_level') as level, COUNT(*) FROM estate_cleaned WHERE id_cleaned = [rating_id] GROUP BY level ORDER BY level"
            },
            {
                "purpose": "高評価物件抽出",
                "sql": "SELECT * FROM estate_cleaned WHERE id_cleaned = [rating_id] AND (JSON_EXTRACT(value_cleaned, '$.current_level') / JSON_EXTRACT(value_cleaned, '$.max_level')) >= 0.8"
            }
        ],
        "period_aware": True
    }

def clean_structure_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    構造・階建情報をJSON形式でクレンジング
    「所在階/構造・階建」データを構造化JSONに変換
    """
    # parse_floor_structure_to_json already imported from .parser
    return parse_floor_structure_to_json(value, period)

def clean_reform_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    リフォーム情報をJSON形式でクレンジング
    完了日付、リフォーム箇所等を構造化
    """
    # parse_reform_to_json already imported from .parser
    return parse_reform_to_json(value, period)

def clean_building_structure_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    建物構造・階建て情報をJSON形式でクレンジング
    「構造・階建て」データを構造化
    """
    # parse_building_structure_to_json already imported from .parser
    return parse_building_structure_to_json(value, period)

def clean_parking_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    駐車場情報をJSON形式でクレンジング
    空き状況、料金、台数等を構造化
    """
    # parse_parking_to_json already imported from .parser
    return parse_parking_to_json(value, period)

def clean_land_use_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    地目情報をJSON形式でクレンジング
    複数地目をリスト形式で処理
    """
    return parse_land_use_to_json(value, period)

def clean_floor_plan_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    間取り図情報をJSON形式でクレンジング
    物件詳細情報を構造化して処理
    """
    # parse_floor_plan_to_json already imported from .parser
    return parse_floor_plan_to_json(value, period)

def clean_building_coverage_to_json(value: str, raw_key: str = "", period: Optional[int] = None) -> Dict[str, Any]:
    """
    建ぺい率・容積率情報をJSON形式でクレンジング
    建ぺい率と容積率を数値化して処理
    """
    # parse_building_coverage_to_json already imported from .parser
    return parse_building_coverage_to_json(value, period)