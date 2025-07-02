# Web Interface for KK Estate

不動産データの分析・可視化を行うWebアプリケーション

## Remix

### Install

Follow: https://remix.run/docs/en/main/start/quickstart

### Build & Server

```bash
npx remix vite:build
npx remix-serve build/server/index.js
```

## Overview

このWebアプリケーションは、SUUMOからスクレイピングした不動産データを分析・可視化するためのインターフェースを提供する. ユーザーは地図ベースの検索、物件一覧の確認、詳細情報と価格履歴の分析を行うことができる.

### Key Features

- 日本地図ベースの物件検索（都道府県・市区町村選択）
- テキスト検索と価格帯フィルタリング
- 物件一覧表示（アクティブ状態表示付き）
- 物件詳細情報と価格時系列分析

### Target Users

現在は個人利用のみ. 将来的にサービス展開の可能性あり.

## Technology Stack

### Frontend & Backend
- **Remix** (React Router v7): サーバーサイドレンダリング、ルーティング
- **React 18**: UIライブラリ
- **TypeScript**: 型安全な開発
- **Tailwind CSS**: スタイリング

### Data Visualization
- **Leaflet.js + react-leaflet**: 日本地図表示、インタラクティブ地図
- **Recharts**: 価格時系列チャート
- **日本地図GeoJSON**: 都道府県・市区町村境界データ

### Database Integration
- **PostgreSQL**: 既存データベース（8テーブル）
- **kkpsgre**: 既存カスタムDBライブラリ
- **kklogger**: ログ管理

### 外部ライブラリ
- **zod**: バリデーション
- **clsx**: 条件付きCSS
- **date-fns**: 日付処理

## Architecture

### Request Flow
```
Browser Request → Remix Server → Database → Server Response → Browser
```

### Key Principles
- **外部API不要**: 全ての処理をサーバーサイドで完結
- **セキュリティ**: 外部APIエンドポイント公開なし
- **パフォーマンス**: サーバーサイドレンダリングでSEO対応
- **Progressive Enhancement**: JavaScript無効でも基本機能動作

## Screen Design

### 1. トップページ (`/`)

#### 機能要件
- **日本地図表示**: Leaflet.jsによるインタラクティブ地図
- **地域選択**: 都道府県クリック → 市区町村表示 → 境界線付きエリア選択
- **色分け表示**: 物件密度・平均価格等による地図の色分け
- **検索機能**:
  - テキスト検索（物件名のオートコンプリート）
  - 価格帯フィルタ（スライダー形式）
  - 物件種別フィルタ（新築/中古、マンション/戸建て等）

#### 技術実装
```typescript
// app/routes/_index.tsx
export async function loader() {
  // 地図表示用の統計データ取得
  const mapStats = await getMapStatistics()
  const prefectures = await getPrefectures()
  return json({ mapStats, prefectures })
}
```

### 2. 一覧ページ (`/properties`)

#### 機能要件
- **検索結果表示**: トップページから遷移した検索条件の物件一覧
- **アクティブ状態**: 直近20日以内のrun_id更新による「現在販売中」表示
- **ソート機能**: 価格、更新日、面積等による並び替え
- **ページネーション**: 大量データ対応
- **物件カード**: 画像、基本情報、価格、アクティブ状態をカード形式で表示

#### データ要件
```sql
-- アクティブ状態判定
SELECT DISTINCT id_main 
FROM estate_run 
WHERE timestamp >= CURRENT_DATE - INTERVAL '20 days'
  AND is_success = true
```

#### 技術実装
```typescript
// app/routes/properties.tsx
export async function loader({ request }: LoaderFunctionArgs) {
  const url = new URL(request.url)
  const searchParams = {
    region: url.searchParams.get('region'),
    priceMin: url.searchParams.get('priceMin'),
    priceMax: url.searchParams.get('priceMax'),
    page: parseInt(url.searchParams.get('page') || '1')
  }
  
  const properties = await searchProperties(searchParams)
  const activeProperties = await getActiveProperties()
  
  return json({ properties, activeProperties, searchParams })
}
```

### 3. 詳細ページ (`/properties/$propertyId`)

#### 機能要件
- **物件詳細情報**: estate_cleanedから取得したクレンジング済み全データ
- **価格履歴チャート**: Rechartsによる時系列グラフ
- **データ履歴**: 過去の更新履歴と変更内容
- **類似物件**: 同エリア・同価格帯の推奨物件

#### データ要件
```sql
-- 価格履歴取得（estate_detail_refを活用）
WITH property_history AS (
  SELECT r.timestamp, ec.value_cleaned
  FROM estate_run r
  JOIN estate_detail_ref dr ON r.id = dr.id_run_ref
  JOIN estate_cleaned ec ON dr.id_run_ref = ec.id_run
  WHERE r.id_main = ? AND ec.id_cleaned = ? -- 価格のid_cleaned
  ORDER BY r.timestamp
)
```

#### 技術実装
```typescript
// app/routes/properties.$propertyId.tsx
export async function loader({ params }: LoaderFunctionArgs) {
  const propertyId = params.propertyId!
  
  const property = await getPropertyDetails(propertyId)
  const priceHistory = await getPriceHistory(propertyId)
  const similarProperties = await getSimilarProperties(property)
  
  return json({ property, priceHistory, similarProperties })
}
```

## Database Integration

### 既存テーブル活用方針

#### 検索機能
- **estate_main**: 物件基本情報（URL、名前）
- **estate_run**: 実行履歴（アクティブ状態判定）
- **estate_cleaned**: クレンジング済みデータ（検索・表示用）

#### 地図表示
- 住所情報から緯度経度を抽出（estate_cleanedの住所項目）
- 都道府県・市区町村での集計クエリ

#### パフォーマンス対策
- 複雑なJOINは避け、複数の単純クエリで実装
- 各クエリにLIMIT制限
- インデックス活用（既存インデックス構成を維持）

## Development Setup

### Prerequisites
- Node.js 18以上
- Python 3.12以上（既存kkestate環境）
- PostgreSQL（既存Docker環境）

### Project Structure
```
main/web/
├── app/
│   ├── routes/           # Remixルート
│   ├── components/       # Reactコンポーネント
│   ├── lib/             # ユーティリティ関数
│   ├── services/        # データベース接続
│   └── styles/          # Tailwind CSS
├── public/              # 静的ファイル
├── remix.config.js      # Remix設定
├── package.json         # Node.js依存関係
└── tsconfig.json        # TypeScript設定
```

### Installation Steps
```bash
# Webアプリケーション用ディレクトリ作成
cd /home/kkazuki/10.git/kkestate/main/web

# Remixプロジェクト初期化
npx create-remix@latest . --template remix-run/remix/templates/remix

# 必要なライブラリインストール
npm install leaflet react-leaflet recharts zod clsx date-fns
npm install -D @types/leaflet

# TypeScript設定
# データベース接続設定
```

### Database Connection
```typescript
// app/services/db.ts
import { DBConnector } from 'kkpsgre/connector'
import { HOST, PORT, USER, PASS, DBNAME, DBTYPE } from 'kkestate/config/psgre'

const db = new DBConnector(
  HOST, 
  { port: PORT, dbname: DBNAME, user: USER, password: PASS, dbtype: DBTYPE }
)

export { db }
```

## Deployment Strategy

### Local Development
- `npm run dev`: 開発サーバー起動
- ホットリロード対応

### Production
- 既存VPS環境での動作
- Remix server（Node.js）として動作
- プロセス管理: PM2またはsystemd

### Security
- IP制限（VPS、自宅IP）
- HTTPS設定
- 環境変数による設定管理

## Important Notes

### Database Guidelines
- SELECT文には必ずLIMIT設定
- 複雑なJOINクエリは避ける
- シンプルなSQLを組み合わせてPython側でJOIN

### Performance
- サーバーサイドレンダリングでSEO対応
- 画像最適化
- チャートのレンダリング最適化

### Future Enhancements
- 物件お気に入り機能
- ユーザー認証（サービス展開時）
- レポート出力機能
- モバイル対応強化