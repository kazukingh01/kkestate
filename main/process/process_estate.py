#!/usr/bin/env python3
"""
不動産データ処理のメインスクリプト
コマンドライン引数でオプションを指定して実行
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from kklogger import set_logger
from kkpsgre.connector import DBConnector
from kkestate.config.psgre import HOST, PORT, USER, PASS, DBNAME, DBTYPE
# get_sample_data function moved here from util/data_analyzer.py
from kkestate.util.key_mapper import get_processing_info_for_key
from kkestate.util.json_cleaner import extract_period_from_key

LOGGER = set_logger(__name__)

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

def update_key_mapping(db: DBConnector, update_db: bool = False, limit_all: bool = False, specific_key_id: Optional[Union[int, List[int]]] = None):
    """
    estate_mst_keyとestate_mst_cleanedのマッピングを分析・更新する
    
    Args:
        db: データベースコネクター
        update_db: Trueの場合はDBを更新、Falseの場合は分析のみ
        limit_all: Trueの場合は全てのキーを処理（LIMITなし）
        specific_key_id: 指定された場合は特定のestate_mst_key.idのみを処理
    """
    action = "更新" if update_db else "分析"
    
    # クエリ条件を構築
    if specific_key_id:
        if isinstance(specific_key_id, list):
            # 複数ID指定
            id_list_str = ','.join(map(str, specific_key_id))
            sql = f"SELECT id, name FROM estate_mst_key WHERE id IN ({id_list_str})"
            LOGGER.info(f"特定キー(id={specific_key_id})のクレンジング済みキーマッピングの{action}を開始")
        else:
            # 単一ID指定
            sql = f"SELECT id, name FROM estate_mst_key WHERE id = {specific_key_id}"
            LOGGER.info(f"特定キー(id={specific_key_id})のクレンジング済みキーマッピングの{action}を開始")
    else:
        # keyidが指定されていない場合は全キー処理
        sql = "SELECT id, name FROM estate_mst_key ORDER BY id"
        LOGGER.info(f"全キーのクレンジング済みキーマッピングの{action}を開始")
    
    # キーデータを取得
    keys_df = db.select_sql(sql)
    
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
        if limit_all:
            LOGGER.info(f"全{len(keys_df)}件のキーを処理します（サンプルデータLIMIT 10000）")
        else:
            LOGGER.info(f"全{len(keys_df)}件のキーを処理します（サンプルデータLIMIT 100）")
    
    update_count = 0
    skip_count = 0
    analysis_results = []
    
    for _, row in keys_df.iterrows():
        key_id = row['id']
        raw_name = row['name']
        
        LOGGER.info(f"処理中: id={key_id}, name='{raw_name}'")
        
        # このキーのサンプルデータを取得
        if specific_key_id and limit_all:
            # 特定キー指定時の--allフラグ: LIMITなし
            sample_values = get_sample_data(db, key_id, limit=None)
        else:
            # デフォルト: LIMIT 100
            sample_values = get_sample_data(db, key_id, limit=100)
        
        # key_processing_mapperを使用してクレンジング済み項目名と型スキーマを決定
        cleaned_name, processing_function, type_schema = get_processing_info_for_key(raw_name)
        
        # cleaned_nameがNoneの場合（強制null項目）の処理
        if cleaned_name is None:
            LOGGER.info(f"  分析結果: '{raw_name}' は強制null項目, samples={len(sample_values)}件")
            
            # データ変換例をログ出力（強制null項目でも表示）
            LOGGER.info(f"\n=== データ変換例: {raw_name} → 強制null (keyid={key_id}) (func: {processing_function.__name__}) ===", color=["BOLD", "CYAN"])
            LOGGER.info(f"型スキーマ: {json.dumps({'base_type': 'null', 'data_type': 'null', 'fields': ['value'], 'period_aware': False}, ensure_ascii=False)}", color=["CYAN"])
            
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
                        # 一部の関数は特別にraw_key引数が必要
                        if hasattr(processing_function, '__name__') and processing_function.__name__ in ['clean_units_to_json', 'clean_price_band_to_json', 'clean_management_fee_to_json']:
                            json_result = processing_function(str(raw_value), raw_key=raw_name, period=None)
                        else:
                            json_result = processing_function(str(raw_value), period=None)
                        transformation_examples.append({
                            'raw': raw_value,
                            'json': json_result,
                            'count': count
                        })
                        LOGGER.info(f"  {i}. '{raw_value}' → {json_result} [{count}件]")
                    except Exception as e:
                        LOGGER.info(f"  {i}. '{raw_value}' → エラー: {e} [{count}件]", color=["RED"])
            else:
                # 通常表示（最初の5件のみ）
                for i, raw_value in enumerate(sample_values[:5], 1):
                    if raw_value is None or str(raw_value).strip() == '':
                        continue
                    try:
                        # 一部の関数は特別にraw_key引数が必要
                        if hasattr(processing_function, '__name__') and processing_function.__name__ in ['clean_units_to_json', 'clean_price_band_to_json', 'clean_management_fee_to_json']:
                            json_result = processing_function(str(raw_value), raw_key=raw_name, period=None)
                        else:
                            json_result = processing_function(str(raw_value), period=None)
                        transformation_examples.append({
                            'raw': raw_value,
                            'json': json_result
                        })
                        LOGGER.info(f"  {i}. '{raw_value}' → {json_result}")
                    except Exception as e:
                        LOGGER.info(f"  {i}. '{raw_value}' → エラー: {e}", color=["RED"])
            
            analysis_results.append({
                'key_id': key_id,
                'raw_name': raw_name,
                'cleaned_name': None,
                'type_schema': {'base_type': 'null', 'data_type': 'null', 'fields': ['value'], 'period_aware': False},
                'sample_count': len(sample_values),
                'transformation_examples': transformation_examples,
                'is_force_null': True
            })
            
            skip_count += 1
            continue
        
        LOGGER.info(f"  分析結果: cleaned_name='{cleaned_name}', type_schema='{type_schema}', samples={len(sample_values)}件")
        
        # データ変換例をログ出力
        LOGGER.info(f"\n=== データ変換例: {raw_name} → {cleaned_name} (keyid={key_id}) (func: {processing_function.__name__}) ===", color=["BOLD", "CYAN"])
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
                    json_result = clean_single_value_to_json(raw_name, cleaned_name, raw_value, processing_function, type_schema)
                    transformation_examples.append({
                        'raw': raw_value,
                        'json': json_result,
                        'count': count
                    })
                    LOGGER.info(f"  {i}. '{raw_value}' → {json_result} [{count}件]")
                except Exception as e:
                    LOGGER.info(f"  {i}. '{raw_value}' → エラー: {e} [{count}件]", color=["RED"])
        else:
            # 通常表示（最初の5件のみ）
            for i, raw_value in enumerate(sample_values[:5], 1):
                if raw_value is None or str(raw_value).strip() == '':
                    continue
                try:
                    json_result = clean_single_value_to_json(raw_name, cleaned_name, raw_value, processing_function, type_schema)
                    transformation_examples.append({
                        'raw': raw_value,
                        'json': json_result
                    })
                    LOGGER.info(f"  {i}. '{raw_value}' → {json_result}")
                except Exception as e:
                    LOGGER.info(f"  {i}. '{raw_value}' → エラー: {e}", color=["RED"])
        
        analysis_results.append({
            'key_id': key_id,
            'raw_name': raw_name,
            'cleaned_name': cleaned_name,
            'type_schema': type_schema,
            'sample_count': len(sample_values),
            'transformation_examples': transformation_examples
        })
        
        # データベース更新
        if update_db:
            try:
                # estate_mst_cleanedに項目を挿入または取得
                # SQLインジェクション対策のため、文字列をエスケープ
                escaped_name = cleaned_name.replace("'", "''")
                escaped_type = json.dumps(type_schema, ensure_ascii=False).replace("'", "''")
                
                insert_cleaned_sql = f"""
                INSERT INTO estate_mst_cleaned (name, type) 
                VALUES ('{escaped_name}', '{escaped_type}')
                ON CONFLICT (name) DO UPDATE SET type = EXCLUDED.type
                RETURNING id;
                """
                
                result = db.execute_sql(insert_cleaned_sql)
                
                if result and len(result) > 0:
                    cleaned_id = result[0][0]
                else:
                    # ON CONFLICTで既存レコードがアップデートされた場合、idを取得
                    select_cleaned_id_sql = "SELECT id FROM estate_mst_cleaned WHERE name = %s"
                    cleaned_result = db.select_sql_with_params(select_cleaned_id_sql, (cleaned_name,))
                    if not cleaned_result.empty:
                        cleaned_id = cleaned_result.iloc[0]['id']
                    else:
                        LOGGER.error(f"  estate_mst_cleanedの登録に失敗: {cleaned_name}")
                        continue
                
                # estate_mst_keyのid_cleanedを更新
                update_key_sql = f"UPDATE estate_mst_key SET id_cleaned = {cleaned_id} WHERE id = {key_id}"
                db.execute_sql(update_key_sql)
                
                update_count += 1
                LOGGER.info(f"  更新完了: estate_mst_cleaned.id={cleaned_id}, estate_mst_key.id_cleaned={cleaned_id}")
                
            except Exception as e:
                LOGGER.error(f"  データベース更新エラー: {e}")
    
    # 結果サマリー
    LOGGER.info("\n=== キーマッピング分析結果 ===", color=["BOLD", "GREEN"])
    LOGGER.info(f"処理対象: {len(keys_df)}件")
    if skip_count > 0:
        LOGGER.info(f"スキップ: {skip_count}件（強制null項目）")
    
    if update_db:
        LOGGER.info(f"更新: {update_count}件")
        LOGGER.info(f"クレンジング済みキーマッピングの更新が完了しました")
    else:
        # 型別統計
        type_stats = {}
        for result in analysis_results:
            if result.get('is_force_null', False):
                base_type = 'force_null'
            else:
                base_type = result['type_schema'].get('base_type', 'unknown') if result['type_schema'] else 'unknown'
            type_stats[base_type] = type_stats.get(base_type, 0) + 1
        
        LOGGER.info("型別統計:", color=["CYAN"])
        for type_name, count in type_stats.items():
            LOGGER.info(f"  {type_name}: {count}件")
        
        LOGGER.info(f"分析結果（全{len(analysis_results)}件）:", color=["CYAN"])
        for result in analysis_results:
            key_id = result['key_id']
            if result.get('is_force_null', False):
                # 強制null項目の場合
                sample_count = result['sample_count']
                LOGGER.info(f"   [{key_id}] {result['raw_name']} → 強制null (force_null/null) [{sample_count}件]")
            else:
                # 通常項目の場合
                type_schema = result['type_schema']
                base_type = type_schema.get('base_type', 'unknown')
                data_type = type_schema.get('data_type', 'unknown')
                sample_count = result['sample_count']
                LOGGER.info(f"   [{key_id}] {result['raw_name']} → {result['cleaned_name']} ({base_type}/{data_type}) [{sample_count}件]")
        
        LOGGER.info(f"クレンジング済みキーマッピングの分析が完了しました（更新なし）")

def clean_single_value_to_json(raw_name: str, cleaned_name: str, raw_value: Any, processing_function, type_schema: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    単一の値をJSONクレンジングする
    
    Args:
        raw_name: 元のキー名
        cleaned_name: クリーニング済みキー名
        raw_value: 生の値
        processing_function: 処理関数
        type_schema: 型スキーマ（period_aware判定用）
        
    Returns:
        クリーニング済みのJSON辞書
    """
    if raw_value is None or str(raw_value).strip() == '':
        return {"value": None}
    
    try:
        # 期別情報を抽出
        period_info = extract_period_from_key(raw_name)
        # period_infoはTuple[str, Optional[int]]なので、期別番号のみを取得
        period = period_info[1] if isinstance(period_info, tuple) else None
        
        # period_awareがFalseの場合はperiodをNoneにする
        if type_schema and not type_schema.get('period_aware', True):
            period = None
        
        # 処理関数を実行
        # 一部の関数は特別にraw_key引数が必要
        if processing_function.__name__ in ['clean_units_to_json', 'clean_price_band_to_json', 'clean_management_fee_to_json']:
            result = processing_function(str(raw_value), raw_key=raw_name, period=period)
        else:
            result = processing_function(str(raw_value), period=period)
        
        return result
        
    except Exception as e:
        LOGGER.warning(f"クレンジングエラー ({raw_name}): {e}")
        return {"value": str(raw_value), "error": str(e)}

def get_unprocessed_runs(db: DBConnector, limit: int = 1000) -> List[int]:
    """
    未処理のrun_idリストを取得する
    
    Args:
        db: データベースコネクター
        limit: 取得する最大件数
        
    Returns:
        未処理のrun_idのリスト
    """
    sql = """
    SELECT r.id 
    FROM estate_run r 
    WHERE r.is_success = true 
    AND NOT EXISTS (
        SELECT 1 FROM estate_cleaned c WHERE c.id_run = r.id
    )
    ORDER BY r.id
    LIMIT %s
    """
    
    result_df = db.select_sql_with_params(sql, (limit,))
    return result_df['id'].tolist() if not result_df.empty else []

def get_run_details(db: DBConnector, run_id: int) -> List[Dict[str, Any]]:
    """
    指定されたrun_idの詳細データを取得する
    
    Args:
        db: データベースコネクター
        run_id: 取得するrun_id
        
    Returns:
        データ詳細のリスト
    """
    sql = """
    SELECT ed.id_run, ed.id_key, ed.value, mk.name as key_name
    FROM estate_detail ed
    JOIN estate_mst_key mk ON ed.id_key = mk.id
    WHERE ed.id_run = %s
    """
    
    result_df = db.select_sql_with_params(sql, (run_id,))
    return result_df.to_dict('records') if not result_df.empty else []

def save_cleaned_data(db: DBConnector, run_id: int, details: List[Dict[str, Any]]) -> bool:
    """
    クレンジング済みデータをestate_cleanedに保存する
    
    Args:
        db: データベースコネクター
        run_id: run_id
        details: 詳細データリスト
        
    Returns:
        保存成功フラグ
    """
    try:
        for detail in details:
            key_id = detail['id_key']
            key_name = detail['key_name']
            raw_value = detail['value']
            
            # get_processing_info_for_keyでクレンジング情報を取得
            cleaned_name, processing_function, type_schema = get_processing_info_for_key(key_name)
            
            # 強制null項目はスキップ
            if cleaned_name is None:
                continue
            
            # クリーニング処理実行
            cleaned_value = clean_single_value_to_json(key_name, cleaned_name, raw_value, processing_function, type_schema)
            
            # estate_mst_cleanedのidを取得
            select_cleaned_sql = "SELECT id FROM estate_mst_cleaned WHERE name = %s"
            cleaned_result = db.select_sql_with_params(select_cleaned_sql, (cleaned_name,))
            
            if cleaned_result.empty:
                LOGGER.warning(f"estate_mst_cleanedに'{cleaned_name}'が見つかりません")
                continue
            
            cleaned_id = cleaned_result.iloc[0]['id']
            
            # estate_cleanedに保存
            # SQLインジェクション対策のため、文字列をエスケープ
            escaped_value = json.dumps(cleaned_value, ensure_ascii=False).replace("'", "''")
            
            insert_sql = f"""
            INSERT INTO estate_cleaned (id_run, id_key, id_cleaned, value_cleaned)
            VALUES ({run_id}, {key_id}, {cleaned_id}, '{escaped_value}')
            ON CONFLICT (id_run, id_key) DO UPDATE SET
                id_cleaned = EXCLUDED.id_cleaned,
                value_cleaned = EXCLUDED.value_cleaned
            """
            
            db.execute_sql(insert_sql)
        
        return True
        
    except Exception as e:
        LOGGER.error(f"データ保存エラー (run_id={run_id}): {e}")
        return False

def process_single_run(db: DBConnector, run_id: int) -> bool:
    """
    単一のrun_idを処理する
    
    Args:
        db: データベースコネクター
        run_id: 処理するrun_id
        
    Returns:
        処理成功フラグ
    """
    try:
        # run詳細データを取得
        details = get_run_details(db, run_id)
        
        if not details:
            LOGGER.warning(f"run_id {run_id} のデータが見つかりません")
            return False
        
        # クレンジング・保存実行
        success = save_cleaned_data(db, run_id, details)
        
        if success:
            LOGGER.info(f"run_id {run_id} の処理が完了しました ({len(details)}件)")
        else:
            LOGGER.error(f"run_id {run_id} の処理が失敗しました")
        
        return success
        
    except Exception as e:
        LOGGER.error(f"run_id {run_id} の処理中にエラーが発生しました: {e}")
        return False

def process_batch(db: DBConnector, batch_size: int = 100) -> Dict[str, int]:
    """
    バッチ処理でデータクレンジングを実行する
    
    Args:
        db: データベースコネクター
        batch_size: バッチサイズ
        
    Returns:
        処理結果統計
    """
    try:
        # 未処理のrun_idリストを取得
        unprocessed_runs = get_unprocessed_runs(db, batch_size)
        
        if not unprocessed_runs:
            return {'total': 0, 'success': 0, 'failed': 0}
        
        success_count = 0
        failed_count = 0
        
        LOGGER.info(f"バッチ処理開始: {len(unprocessed_runs)}件のrun_idを処理します")
        
        for i, run_id in enumerate(unprocessed_runs, 1):
            LOGGER.info(f"処理中 ({i}/{len(unprocessed_runs)}): run_id {run_id}")
            
            if process_single_run(db, run_id):
                success_count += 1
            else:
                failed_count += 1
        
        result = {
            'total': len(unprocessed_runs),
            'success': success_count,
            'failed': failed_count
        }
        
        LOGGER.info(f"バッチ処理完了: 成功={success_count}, 失敗={failed_count}")
        return result
        
    except Exception as e:
        LOGGER.error(f"バッチ処理中にエラーが発生しました: {e}")
        return {'total': 0, 'success': 0, 'failed': 0}

def get_processing_stats(db: DBConnector) -> Dict[str, int]:
    """
    処理統計を取得する
    
    Args:
        db: データベースコネクター
        
    Returns:
        統計情報辞書
    """
    try:
        # 成功したRUN総数
        total_sql = "SELECT COUNT(*) as count FROM estate_run WHERE is_success = true"
        total_result = db.select_sql(total_sql)
        total_runs = total_result.iloc[0]['count'] if not total_result.empty else 0
        
        # 処理済みRUN数
        processed_sql = "SELECT COUNT(DISTINCT id_run) as count FROM estate_cleaned"
        processed_result = db.select_sql(processed_sql)
        processed_runs = processed_result.iloc[0]['count'] if not processed_result.empty else 0
        
        # 未処理RUN数
        unprocessed_runs = total_runs - processed_runs
        
        # 処理進捗率
        progress = (processed_runs / total_runs * 100) if total_runs > 0 else 0
        
        return {
            'total_runs': total_runs,
            'processed_runs': processed_runs,
            'unprocessed_runs': unprocessed_runs,
            'progress_percent': progress
        }
        
    except Exception as e:
        LOGGER.error(f"統計取得エラー: {e}")
        return {'total_runs': 0, 'processed_runs': 0, 'unprocessed_runs': 0, 'progress_percent': 0}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='不動産データ処理ツール')
    parser.add_argument("--update", action='store_true', default=False, help='データベース更新処理を実行')
    parser.add_argument("--mapping", action='store_true', default=False, help='キーマッピング処理を実行')
    parser.add_argument("--process", action='store_true', default=False, help='データクレンジング処理を実行')
    parser.add_argument("--batchsize", type=int, default=100, help='バッチ処理のサイズ（デフォルト: 100）')
    parser.add_argument("--stats", action='store_true', default=False, help='処理統計を表示')
    parser.add_argument("--runid", type=int, help='特定のrun_idのみを処理')
    parser.add_argument("--verbose", action='store_true', default=False, help='詳細ログを出力')
    parser.add_argument("--all", action='store_true', default=False, help='全てのキーを処理（LIMITなし）')
    parser.add_argument("--keyid", type=lambda x: [int(y) for y in x.split(",")], help='特定のestate_mst_key.idのみを処理（複数指定時はカンマ区切り: 121,122,123）')
    
    args = parser.parse_args()
    
    if args.keyid:
        LOGGER.info(f"対象keyid: {args.keyid}")
    
    LOGGER.info(f"{args}")
    
    try:
        # データベース接続
        db = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE)
        
        # キーマッピング処理
        if args.mapping:
            if args.update:
                LOGGER.info("キーマッピング分析・更新を開始", color=["BOLD", "GREEN"])
                update_key_mapping(db, update_db=True, limit_all=args.all, specific_key_id=args.keyid)
                LOGGER.info("キーマッピング分析・更新が完了しました", color=["BOLD", "GREEN"])
            else:
                LOGGER.info("キーマッピング分析を開始（更新なし）", color=["BOLD", "GREEN"])
                update_key_mapping(db, update_db=False, limit_all=args.all, specific_key_id=args.keyid)
                LOGGER.info("キーマッピング分析が完了しました", color=["BOLD", "GREEN"])
        
        # 統計表示
        if args.stats:
            stats = get_processing_stats(db)
            LOGGER.info("=== 処理統計 ===")
            LOGGER.info(f"成功したRUN総数: {stats['total_runs']:,}")
            LOGGER.info(f"処理済みRUN数: {stats['processed_runs']:,}")
            LOGGER.info(f"未処理RUN数: {stats['unprocessed_runs']:,}")
            LOGGER.info(f"処理進捗: {stats['progress_percent']:.1f}%")
        
        # データクレンジング処理
        if args.process:
            if args.runid:
                # 単一run_idの処理
                LOGGER.info(f"run_id {args.runid} の処理を開始", color=["BOLD", "CYAN"])
                if args.update:
                    success = process_single_run(db, args.runid)
                    if success:
                        LOGGER.info(f"run_id {args.runid} の処理が成功しました", color=["BOLD", "CYAN"])
                    else:
                        LOGGER.error(f"run_id {args.runid} の処理が失敗しました")
                        sys.exit(1)
                else:
                    LOGGER.info(f"run_id {args.runid} の分析のみ実行（未実装）", color=["BOLD", "YELLOW"])
                    LOGGER.warning("分析のみの処理は未実装です")
            else:
                # バッチ処理
                if args.update:
                    LOGGER.info("データクレンジング処理を開始", color=["BOLD", "GREEN"])
                    result = process_batch(db, args.batchsize)
                    
                    if result['total'] == 0:
                        LOGGER.warning("処理対象のデータがありません")
                    else:
                        success_rate = (result['success'] / result['total']) * 100
                        LOGGER.info(f"処理完了: {result['success']}/{result['total']} ({success_rate:.1f}%)", color=["BOLD", "GREEN"])
                        
                        if result['failed'] > 0:
                            LOGGER.warning(f"失敗した処理: {result['failed']}件")
                else:
                    LOGGER.info("バッチ分析のみ実行（未実装）", color=["BOLD", "YELLOW"])
                    LOGGER.warning("分析のみの処理は未実装です")
        
        # 処理が何も指定されていない場合のメッセージは表示しない
        # （デフォルトで分析が実行されるため）
            
    except KeyboardInterrupt:
        LOGGER.warning("処理が中断されました")
        sys.exit(1)
    except Exception as e:
        LOGGER.error(f"予期しないエラーが発生しました: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)