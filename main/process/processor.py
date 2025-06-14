"""
データ処理のメインクラス
estate_detailからデータを取得し、クレンジングしてestate_cleanedに保存
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from kklogger import set_logger
from kkpsgre.connector import DBConnector
from kkestate.config.psgre import HOST, PORT, USER, PASS, DBNAME, DBTYPE
from kkestate.util.data_analyzer import analyze_key_and_data, get_sample_data
from kkestate.util.json_cleaner import (
    extract_period_from_key, clean_price_to_json, clean_area_to_json, 
    clean_layout_to_json, clean_date_to_json, clean_management_fee_to_json,
    clean_number_to_json, clean_boolean_to_json, clean_text_to_json,
    clean_access_to_json, clean_zoning_to_json, clean_force_null_to_json,
    clean_units_to_json, clean_price_band_to_json, clean_other_expenses_to_json,
    clean_multiple_area_to_json, clean_restrictions_to_json, clean_expiry_date_to_json,
    clean_company_info_to_json, clean_delivery_date_to_json, clean_address_to_json,
    generate_address_type_schema, generate_price_type_schema, generate_area_type_schema,
    generate_layout_type_schema, generate_date_type_schema, generate_access_type_schema,
    generate_boolean_type_schema, generate_number_type_schema, generate_text_type_schema
)
from kkestate.util.cleansing import (
    clean_price, clean_layout, clean_area, clean_access, 
    clean_date, clean_address, clean_number, clean_management_fee, clean_boolean
)

LOGGER = set_logger(__name__)

class EstateProcessor:
    """不動産データ処理クラス"""
    
    def __init__(self):
        self.db = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE)
        
        # JSON クレンジング関数のマッピング
        self.json_cleansing_functions = {
            '価格': clean_price_to_json,
            '予定価格': clean_price_to_json,
            '最多価格帯': clean_price_to_json,
            '予定最多価格帯': clean_price_to_json,
            '予定価格帯': clean_price_to_json,
            '間取り': clean_layout_to_json,
            '専有面積': clean_area_to_json,
            'その他面積': clean_multiple_area_to_json,
            'バルコニー面積': clean_multiple_area_to_json,
            '土地面積': clean_area_to_json,
            '建物面積': clean_area_to_json,
            '完成時期': clean_date_to_json,
            '引渡時期': clean_delivery_date_to_json,
            '築年月': clean_date_to_json,
            '建築年月': clean_date_to_json,
            '戸数': clean_units_to_json,
            '建物階数': clean_number_to_json,
            '所在階': clean_number_to_json,
            '管理費': clean_management_fee_to_json,
            '管理準備金': clean_management_fee_to_json,
            '修繕積立金': clean_management_fee_to_json,
            '修繕積立基金': clean_management_fee_to_json,
            'その他諸経費': clean_other_expenses_to_json,
            '駐車場': clean_boolean_to_json,
            '交通アクセス': clean_access_to_json,
            '用途地域': clean_zoning_to_json,
            '制限事項': clean_restrictions_to_json,
            '取引条件有効期限': clean_expiry_date_to_json,
            '会社情報': clean_company_info_to_json,
            '敷地権利形態': clean_force_null_to_json,
            '販売スケジュール': clean_force_null_to_json,
            '所在地': clean_address_to_json,
            '住所': clean_address_to_json,
            '物件所在地': clean_address_to_json,
            '現地案内所': clean_address_to_json,
            'モデルルーム': clean_address_to_json,
        }
    
    def update_key_mapping(self, update_db: bool = False, limit_all: bool = False, specific_key_id: Optional[int] = None):
        """
        estate_mst_cleanedとestate_mst_keyのid_cleanedを分析・更新
        id_cleanedがnullのものを対象に実データを分析して処理
        
        Args:
            update_db: Trueの場合はDBを更新、Falseの場合は分析のみ
            limit_all: Trueの場合は全てのキーを処理（LIMITなし）
            specific_key_id: 指定された場合は特定のestate_mst_key.idのみを処理
        """
        action = "更新" if update_db else "分析"
        
        # クエリ条件を構築
        if specific_key_id:
            sql = f"SELECT id, name FROM estate_mst_key WHERE id = {specific_key_id}"
            LOGGER.info(f"特定キー(id={specific_key_id})のクレンジング済みキーマッピングの{action}を開始")
        else:
            sql = "SELECT id, name FROM estate_mst_key WHERE id_cleaned IS NULL"
            # --allフラグは特定キーが指定されていない場合は無視
            if limit_all:
                LOGGER.info("--allフラグは--keyidオプションと組み合わせて使用してください")
            LOGGER.info(f"クレンジング済みキーマッピングの{action}を開始")
        
        # キーデータを取得
        keys_df = self.db.select_sql(sql)
        
        if keys_df.empty:
            if specific_key_id:
                LOGGER.info(f"指定されたキー(id={specific_key_id})が見つかりません")
            else:
                LOGGER.info("処理対象のキーがありません（すべてのキーが既にマッピング済み）")
            return
        
        # 処理対象の説明
        if specific_key_id:
            if limit_all:
                LOGGER.info(f"特定キー(id={specific_key_id})を処理します（サンプルデータLIMIT 10000）")
            else:
                LOGGER.info(f"特定キー(id={specific_key_id})を処理します（サンプルデータLIMIT 100）")
        else:
            LOGGER.info(f"{len(keys_df)}件のキーを処理します")
        
        update_count = 0
        analysis_results = []
        
        for _, row in keys_df.iterrows():
            key_id = row['id']
            raw_name = row['name']
            
            LOGGER.info(f"処理中: id={key_id}, name='{raw_name}'")
            
            # このキーのサンプルデータを取得
            if specific_key_id and limit_all:
                # 特定キー指定時の--allフラグ: LIMITなし
                sample_values = get_sample_data(self.db, key_id, limit=None)
            else:
                # デフォルト: LIMIT 100
                sample_values = get_sample_data(self.db, key_id, limit=100)
            
            # データ分析してクレンジング済み項目名と型スキーマを決定
            cleaned_name, type_schema = analyze_key_and_data(raw_name, sample_values)
            
            LOGGER.info(f"  分析結果: cleaned_name='{cleaned_name}', type_schema='{type_schema}', samples={len(sample_values)}件")
            
            # データ変換例をログ出力
            LOGGER.info(f"\n=== データ変換例: {raw_name} → {cleaned_name} (keyid={key_id}) ===", color=["BOLD", "CYAN"])
            LOGGER.info(f"型スキーマ: {json.dumps(type_schema, ensure_ascii=False)}", color=["CYAN"])
            
            # サンプルデータで実際の変換を実行して表示
            transformation_examples = []
            
            if specific_key_id and limit_all:
                # --allフラグ使用時は重複を除いて件数付きで表示
                import pandas as pd
                
                # サンプルデータをDataFrameに変換
                sample_df = pd.DataFrame({'raw_value': sample_values})
                sample_df = sample_df[sample_df['raw_value'].notna() & (sample_df['raw_value'].str.strip() != '')]
                
                # 重複を除いて件数をカウント
                value_counts = sample_df['raw_value'].value_counts()
                
                LOGGER.info(f"  重複を除いた変換例（{len(value_counts)}パターン、総{value_counts.sum()}件）:", color=["CYAN"])
                
                for i, (raw_value, count) in enumerate(value_counts.items(), 1):  # 全パターン表示
                    try:
                        json_result = self.clean_single_value_to_json(raw_name, cleaned_name, raw_value)
                        transformation_examples.append({
                            'raw': raw_value,
                            'json': json_result,
                            'count': count
                        })
                        LOGGER.info(f"  {i:3d}. '{raw_value}' ({count}件) → {json.dumps(json_result, ensure_ascii=False)}")
                    except Exception as e:
                        LOGGER.error(f"  {i:3d}. '{raw_value}' ({count}件) → エラー: {e}")
            else:
                # 通常時は最初の5件を表示
                for i, sample_value in enumerate(sample_values[:5]):
                    if sample_value and sample_value.strip():
                        try:
                            json_result = self.clean_single_value_to_json(raw_name, cleaned_name, sample_value)
                            transformation_examples.append({
                                'raw': sample_value,
                                'json': json_result
                            })
                            LOGGER.info(f"  {i+1}. '{sample_value}' → {json.dumps(json_result, ensure_ascii=False)}")
                        except Exception as e:
                            LOGGER.error(f"  {i+1}. '{sample_value}' → エラー: {e}")
            
            # 分析結果を保存
            analysis_results.append({
                'key_id': key_id,
                'raw_name': raw_name,
                'cleaned_name': cleaned_name,
                'type_schema': type_schema,
                'sample_count': len(sample_values),
                'transformation_examples': transformation_examples
            })
            
            if update_db:
                # estate_mst_cleanedに存在するかチェック
                existing_df = self.db.select_sql(f"SELECT id FROM estate_mst_cleaned WHERE name = '{cleaned_name}'")
                
                if existing_df.empty:
                    # 新規登録
                    type_schema_json = json.dumps(type_schema, ensure_ascii=False)
                    # シングルクォートをエスケープ
                    cleaned_name_escaped = cleaned_name.replace("'", "''")
                    type_schema_escaped = type_schema_json.replace("'", "''")
                    result = self.db.execute_sql(f"INSERT INTO estate_mst_cleaned (name, type) VALUES ('{cleaned_name_escaped}', '{type_schema_escaped}') RETURNING id;")
                    cleaned_id = result[0][0]
                    LOGGER.info(f"  新規登録: estate_mst_cleaned.id={cleaned_id}")
                else:
                    # 既存のIDを取得
                    cleaned_id = existing_df.iloc[0]['id']
                    LOGGER.info(f"  既存使用: estate_mst_cleaned.id={cleaned_id}")
                
                # estate_mst_keyのid_cleanedを更新
                self.db.execute_sql(f"UPDATE estate_mst_key SET id_cleaned = {cleaned_id} WHERE id = {key_id}")
                update_count += 1
        
        # 分析結果をサマリ表示
        LOGGER.info(f"\n=== キーマッピング分析結果 ===", color=["BOLD", "GREEN"])
        LOGGER.info(f"処理対象: {len(analysis_results)}件")
        
        # 型別の統計
        type_count = {}
        for result in analysis_results:
            base_type = result['type_schema'].get('base_type', 'unknown')
            type_count[base_type] = type_count.get(base_type, 0) + 1
        
        LOGGER.info(f"\n型別統計:", color=["CYAN"])
        for vtype, count in sorted(type_count.items()):
            LOGGER.info(f"  {vtype}: {count}件")
        
        # サンプル表示（最初の10件）
        LOGGER.info(f"\n分析結果サンプル（最初の10件）:", color=["CYAN"])
        for i, result in enumerate(analysis_results[:10]):
            base_type = result['type_schema'].get('base_type', 'unknown')
            data_type = result['type_schema'].get('data_type', 'unknown')
            LOGGER.info(f"  {i+1:2d}. {result['raw_name']} → {result['cleaned_name']} ({base_type}/{data_type}) [{result['sample_count']}件]")
        
        if len(analysis_results) > 10:
            LOGGER.info(f"  ... 他{len(analysis_results)-10}件")
        
        if update_db:
            LOGGER.info(f"クレンジング済みキーマッピングを{update_count}件更新しました")
        else:
            LOGGER.info(f"クレンジング済みキーマッピングの分析が完了しました（更新なし）")
    
    def get_unprocessed_runs(self, limit: int = 1000) -> List[int]:
        """
        未処理のestate_runのIDリストを取得
        estate_cleanedにまだ登録されていないもの
        """
        sql = f"""
        SELECT DISTINCT er.id
        FROM estate_run er
        WHERE er.is_success = true
          AND NOT EXISTS (
              SELECT 1 FROM estate_cleaned ec 
              WHERE ec.id_run = er.id
          )
        ORDER BY er.id
        LIMIT {limit}
        """
        
        result_df = self.db.select_sql(sql)
        return result_df['id'].tolist()
    
    def get_run_details(self, run_id: int) -> List[Dict[str, Any]]:
        """
        指定されたrun_idの詳細データを取得
        estate_detailと同じ構造でリストを返す
        """
        sql = f"""
        SELECT 
            er.id as run_id,
            er.id_main,
            em.name as property_name,
            em.url as property_url,
            ed.id_key,
            emk.name as key_name,
            emk.id_cleaned,
            ed.value
        FROM estate_run er
        JOIN estate_main em ON er.id_main = em.id
        JOIN estate_detail ed ON er.id = ed.id_run
        JOIN estate_mst_key emk ON ed.id_key = emk.id
        WHERE er.id = {run_id}
        """
        
        details_df = self.db.select_sql(sql)
        
        if details_df.empty:
            return []
        
        # estate_detailと同じ構造のリストを作成
        result = []
        for _, row in details_df.iterrows():
            if row['value']:  # 値がある場合のみ処理
                result.append({
                    'run_id': row['run_id'],
                    'id_main': row['id_main'],
                    'property_name': row['property_name'],
                    'property_url': row['property_url'],
                    'id_key': row['id_key'],
                    'key_name': row['key_name'],
                    'id_cleaned': row['id_cleaned'],
                    'value': row['value'].strip()
                })
        
        return result
    
    def clean_single_value_to_json(self, raw_key_name: str, cleaned_key_name: str, raw_value: str) -> Dict[str, Any]:
        """
        単一の値をクレンジングしてJSON形式で返す
        """
        if not raw_value:
            return {"value": None}
        
        # 期別情報を抽出
        base_key, period = extract_period_from_key(raw_key_name)
        
        # 対応するクレンジング関数があるかチェック
        base_cleaned_key = cleaned_key_name.replace(f"_第{period}期", "") if period else cleaned_key_name
        
        # 特別なマッピング処理
        # 面積系で「バルコニー面積」が含まれるデータは複数面積として処理
        if "面積" in base_cleaned_key and "：" in raw_value and "バルコニー" in raw_value:
            cleaning_func = clean_multiple_area_to_json
            try:
                cleaned_value = cleaning_func(raw_value, period)
                return cleaned_value
            except Exception as e:
                LOGGER.error(f"複数面積クレンジング失敗: {base_cleaned_key}={raw_value}, エラー: {e}")
                return clean_text_to_json(raw_value, period)
        
        if base_cleaned_key in self.json_cleansing_functions:
            cleaning_func = self.json_cleansing_functions[base_cleaned_key]
            try:
                # 戸数の場合は raw_key_name も渡す
                if base_cleaned_key == '戸数' and cleaning_func.__name__ == 'clean_units_to_json':
                    cleaned_value = cleaning_func(raw_value, raw_key_name, period)
                # 最多価格帯の場合は専用関数を使用
                elif "最多価格帯" in raw_key_name:
                    cleaned_value = clean_price_band_to_json(raw_value, raw_key_name, period)
                # 管理費系の場合は raw_key_name も渡す
                elif cleaning_func.__name__ == 'clean_management_fee_to_json':
                    cleaned_value = cleaning_func(raw_value, raw_key_name, period)
                else:
                    cleaned_value = cleaning_func(raw_value, period)
                return cleaned_value
            except Exception as e:
                LOGGER.error(f"クレンジング失敗: {base_cleaned_key}={raw_value}, エラー: {e}")
                # クレンジングに失敗した場合は生データを返す
                return clean_text_to_json(raw_value, period)
        else:
            # クレンジング関数がない場合は生データをテキストとして返す
            return clean_text_to_json(raw_value, period)
    
    def save_cleaned_data(self, detail_items: List[Dict[str, Any]]):
        """
        クレンジング済みデータをestate_cleanedに保存
        JSON形式でestate_cleanedに保存
        """
        
        for item in detail_items:
            if not item['id_cleaned']:
                LOGGER.warning(f"id_cleanedが設定されていません: key_name={item['key_name']}")
                continue
            
            # 値をJSON形式でクレンジング
            cleaned_value_dict = self.clean_single_value_to_json(
                item['key_name'], 
                item.get('cleaned_key_name', item['key_name']), 
                item['value']
            )
            
            # JSON文字列に変換
            cleaned_value_json = json.dumps(cleaned_value_dict, ensure_ascii=False)
            
            # estate_cleanedに挿入/更新
            sql = f"""
            INSERT INTO estate_cleaned (id_run, id_key, id_cleaned, value_cleaned)
            VALUES ({item['run_id']}, {item['id_key']}, {item['id_cleaned']}, '{cleaned_value_json.replace("'", "''")}')
            ON CONFLICT (id_run, id_key) 
            DO UPDATE SET 
                id_cleaned = EXCLUDED.id_cleaned,
                value_cleaned = EXCLUDED.value_cleaned
            """
            
            self.db.execute_sql(sql)
    
    def process_single_run(self, run_id: int) -> bool:
        """
        単一のrun_idを処理
        """
        try:
            # データ取得
            detail_items = self.get_run_details(run_id)
            if not detail_items:
                LOGGER.warning(f"run_id {run_id} のデータが見つかりません")
                return False
            
            # データクレンジングと保存
            self.save_cleaned_data(detail_items)
            
            LOGGER.info(f"run_id {run_id} の処理が完了しました ({len(detail_items)}件)")
            return True
            
        except Exception as e:
            LOGGER.error(f"run_id {run_id} の処理中にエラーが発生: {e}")
            return False
    
    def process_batch(self, batch_size: int = 100) -> Dict[str, int]:
        """
        バッチ処理で複数のrun_idを処理
        """
        LOGGER.info(f"バッチ処理を開始 (バッチサイズ: {batch_size})")
        
        # 未処理のrun_idを取得
        unprocessed_runs = self.get_unprocessed_runs(batch_size)
        
        if not unprocessed_runs:
            LOGGER.info("処理対象のデータがありません")
            return {"total": 0, "success": 0, "failed": 0}
        
        LOGGER.info(f"{len(unprocessed_runs)}件の処理を開始")
        
        success_count = 0
        failed_count = 0
        
        for run_id in unprocessed_runs:
            if self.process_single_run(run_id):
                success_count += 1
            else:
                failed_count += 1
        
        result = {
            "total": len(unprocessed_runs),
            "success": success_count,
            "failed": failed_count
        }
        
        LOGGER.info(f"バッチ処理完了: {result}")
        return result
    
    def get_processing_stats(self) -> Dict[str, int]:
        """
        処理統計を取得
        """
        stats = {}
        
        # 総run数
        total_runs_df = self.db.select_sql("SELECT COUNT(*) as count FROM estate_run WHERE is_success = true")
        stats['total_successful_runs'] = total_runs_df.iloc[0]['count']
        
        # 処理済み数（重複を除くrun数）
        processed_df = self.db.select_sql("SELECT COUNT(DISTINCT id_run) as count FROM estate_cleaned")
        stats['processed_runs'] = processed_df.iloc[0]['count']
        
        # 未処理数
        stats['unprocessed_runs'] = stats['total_successful_runs'] - stats['processed_runs']
        
        return stats