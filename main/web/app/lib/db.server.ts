import { Pool } from "pg";

// データベース設定
const DB_CONFIG = {
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "estate",
  user: process.env.DB_USER || "guest", 
  password: process.env.DB_PASSWORD || "guest",
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
};

// PostgreSQL接続プール
let pool: Pool | null = null;

function getPool(): Pool {
  if (!pool) {
    pool = new Pool(DB_CONFIG);
    
    pool.on('error', (err) => {
      console.error('PostgreSQL pool error:', err);
    });
  }
  return pool;
}

// クエリ実行関数
export async function executeQuery<T = any>(
  sql: string, 
  params: any[] = []
): Promise<T[]> {
  const client = getPool();
  
  try {
    console.log("Executing SQL:", sql.trim());
    if (params.length > 0) {
      console.log("Parameters:", params);
    }
    
    const result = await client.query(sql, params);
    return result.rows;
  } catch (error) {
    console.error("Database query error:", error);
    console.error("SQL:", sql);
    console.error("Parameters:", params);
    // エラーをそのまま投げる（モックデータにフォールバックしない）
    throw error;
  }
}

// 接続テスト
export async function testConnection(): Promise<boolean> {
  try {
    await executeQuery("SELECT 1 as test");
    return true;
  } catch (error) {
    console.error("Database connection test failed:", error);
    return false;
  }
}