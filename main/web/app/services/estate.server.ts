import { executeQuery } from "~/lib/db.server";

// データ型定義
export interface PrefectureStats {
  [prefectureCode: string]: {
    count: number;
  };
}

export interface PropertyDetails {
  property: {
    id: number;
    name: string | null;
    url: string;
    prefecture: string | null;
    city: string | null;
    property_type: string | null;
    sys_updated: string;
  };
  priceHistory: PriceHistoryItem[];
  latestDetails: DetailItem[];
}

export interface DetailItem {
  key: string;
  value: string;
}

export interface PriceHistoryItem {
  timestamp: string;
  price: number | null;
  min_price: number | null;
  max_price: number | null;
  unit: string | null;
  run_id: number;
  period: number | null;
}

// モックデータ
const MOCK_PREFECTURE_STATS: PrefectureStats = {
  "01": { count: 150 },
  "13": { count: 8500 },
  "14": { count: 3200 },
  "23": { count: 1800 },
  "27": { count: 4500 },
  "40": { count: 2100 },
};

// 都道府県統計データ取得（正しいエラーハンドリング）
export async function getPrefectureStats(): Promise<PrefectureStats> {
  // 環境変数でMOCKモードが明示的に設定されている場合
  if (process.env.USE_MOCK_DATA === 'true') {
    console.log("[getPrefectureStats] Using mock data (USE_MOCK_DATA=true)");
    return MOCK_PREFECTURE_STATS;
  }

  // 実際のデータベースからデータ取得を試行
  try {
    console.log("[getPrefectureStats] Fetching data from database");
    
    const sql = `
      SELECT 
        eme.prefecture,
        COUNT(*) as count
      FROM estate_main_extended eme
      WHERE eme.sys_updated >= CURRENT_DATE - INTERVAL '30 days'
      GROUP BY eme.prefecture
      HAVING COUNT(*) > 0
      ORDER BY COUNT(*) DESC
      LIMIT 50;
    `;
    
    const rows = await executeQuery<{
      prefecture: string;
      count: string;
    }>(sql);
    
    const stats: PrefectureStats = {};
    for (const row of rows) {
      if (row.prefecture) {
        stats[row.prefecture] = {
          count: parseInt(row.count) || 0
        };
      }
    }
    
    console.log(`[getPrefectureStats] Retrieved ${Object.keys(stats).length} prefectures from database`);
    return stats;
    
  } catch (error) {
    console.error("[getPrefectureStats] Database error:", error);
    // エラーをそのまま投げる（モックデータにフォールバックしない）
    throw new Error(`Failed to fetch prefecture stats from database: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// 物件詳細データ取得
export async function getPropertyDetails(propertyId: number): Promise<PropertyDetails | null> {
  try {
    console.log(`[getPropertyDetails] Fetching details for property ID: ${propertyId}`);

    // 1. 基本情報を取得
    const propertyBasicSql = `
      SELECT 
        id,
        name,
        url,
        prefecture,
        city,
        property_type,
        sys_updated
      FROM estate_main_extended
      WHERE id = $1;
    `;

    const propertyRows = await executeQuery<{
      id: string;
      name: string | null;
      url: string;
      prefecture: string | null;
      city: string | null;
      property_type: string | null;
      sys_updated: string;
    }>(propertyBasicSql, [propertyId]);

    if (propertyRows.length === 0) {
      console.log(`[getPropertyDetails] Property not found: ${propertyId}`);
      return null;
    }

    const property = propertyRows[0];

    // 2. 価格履歴を取得（periodの最大値優先）
    const priceHistorySql = `
      WITH price_data AS (
        SELECT 
          er.timestamp,
          er.id as run_id,
          ec.value_cleaned,
          ROW_NUMBER() OVER (
            PARTITION BY er.id 
            ORDER BY 
              CASE WHEN ec.value_cleaned->>'period' IS NULL THEN 0 ELSE (ec.value_cleaned->>'period')::int END DESC,
              ec.id_run DESC
          ) as rn
        FROM estate_run er
        JOIN estate_detail_ref edr ON er.id = edr.id_run
        JOIN estate_cleaned ec ON edr.id_run_ref = ec.id_run AND edr.id_key = ec.id_key
        JOIN estate_mst_cleaned emc ON ec.id_cleaned = emc.id
        WHERE er.id_main = $1
          AND er.is_success = true
          AND er.is_ref = true
          AND emc.name = '価格'
          AND ec.value_cleaned->>'value' IS NOT NULL
      )
      SELECT 
        timestamp,
        run_id,
        value_cleaned->>'value' as price,
        value_cleaned->>'min' as min_price,
        value_cleaned->>'max' as max_price,
        value_cleaned->>'unit' as unit,
        value_cleaned->>'period' as period
      FROM price_data
      WHERE rn = 1
      ORDER BY timestamp DESC
      LIMIT 100;
    `;

    const priceRows = await executeQuery<{
      timestamp: string;
      price: string | null;
      min_price: string | null;
      max_price: string | null;
      unit: string | null;
      run_id: string;
      period: string | null;
    }>(priceHistorySql, [propertyId]);

    const priceHistory: PriceHistoryItem[] = priceRows.map(row => ({
      timestamp: row.timestamp,
      price: row.price ? parseFloat(row.price) : null,
      min_price: row.min_price ? parseFloat(row.min_price) : null,
      max_price: row.max_price ? parseFloat(row.max_price) : null,
      unit: row.unit,
      run_id: parseInt(row.run_id),
      period: row.period ? parseInt(row.period) : null
    }));

    console.log(`[getPropertyDetails] Retrieved ${priceHistory.length} price history items`);

    // 3. 最新の詳細情報を取得
    const latestDetailSql = `
      WITH latest_run AS (
        SELECT id as run_id
        FROM estate_run
        WHERE id_main = $1 AND is_success = true AND is_ref = true
        LIMIT 1
      )
      SELECT 
        emk.name as key_name,
        ed.value as key_value,
        er.timestamp
      FROM latest_run lr
      JOIN estate_run er ON lr.run_id = er.id
      JOIN estate_detail_ref edr ON lr.run_id = edr.id_run
      JOIN estate_detail ed ON edr.id_run_ref = ed.id_run AND edr.id_key = ed.id_key
      JOIN estate_mst_key emk ON ed.id_key = emk.id
      ORDER BY er.timestamp DESC, emk.id;
    `;

    const detailRows = await executeQuery<{
      key_name: string;
      key_value: string;
      timestamp: string;
    }>(latestDetailSql, [propertyId]);

    const latestDetails = detailRows.map(row => ({
      key: row.key_name,
      value: row.key_value
    }));

    console.log(`[getPropertyDetails] Retrieved ${latestDetails.length} detail items`);

    return {
      property: {
        id: parseInt(property.id),
        name: property.name,
        url: property.url,
        prefecture: property.prefecture,
        city: property.city,
        property_type: property.property_type,
        sys_updated: property.sys_updated,
      },
      priceHistory: priceHistory.reverse(), // 古い順に並び替え
      latestDetails: latestDetails,
    };

  } catch (error) {
    console.error("[getPropertyDetails] Database error:", error);
    throw new Error(`Failed to fetch property details: ${error instanceof Error ? error.message : String(error)}`);
  }
}