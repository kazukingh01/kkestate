"""
実データに基づくサンプルデータ取得機能
"""

from typing import Optional

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