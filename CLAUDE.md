# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

IMPORTANT: 基本的に日本語での応答をお願いする. 「。」は嫌いなので、「. 」ピリオド＆半角スペース(文末ではなく、文中の場合)を代用する.
NEVER: 「→」は使用禁止.「->」で代用する.

下記 README.md は読み込んで.
@REAME.md
@main/collect/README.md
@main/process/README.md

## Project Overview

このリポジトリでは日本の不動産データを扱う. データはの日本のWEBサイト「SUUMO」からスクレイピングされている.
スクレイピングされたデータを整理し、分析を行い、可視化し、それらは不動産購入目的のために利活用される.

### Purpose & Goals

スクレイピングされた日本の不動産データを整理・分析し、私個人が有効に不動産を購入する事である.
このプロジェクトが完成された場合、以下の機能を有する.

- データスクレイピング
- データクレンジング及び分析可能な項目整理
- 多数の分析関数及び価格予測モデリング
- 分析行為及び分析結果を視覚的に確認可能なWebページ

### Technology Stack

このプロジェクトで用いられる技術スタックは以下. 

- Python
- React, Typescript ( Web )
- Database ( PostgreSQL )
- Cron
- Docker

この環境とは別に、Virtual Private Server ( VPS ) 上で既にデータスクレイピング処理が動いている.
VPSのホスト側でCron起動されたPythonが常時実行され、Docker container として起動している PostgreSQL に読み書きを行っている.

#### Python Dependencies

`pyproject.toml` で管理される主要な依存パッケージ：

**データベース関連**
- `kkpsgre`: PostgreSQL操作用のカスタムライブラリ
- 使用目的: データベース接続、クエリ実行

**データ処理関連**
- `kkdf`: データフレーム処理用のカスタムライブラリ
- `pandas==2.2.3`: データ分析・操作
- `numpy==2.2.1`: 数値計算
- `polars==1.18.0`: 高速データフレーム処理
- `pyarrow==19.0.1`: 列指向データ処理

**ウェブスクレイピング関連**
- `requests==2.32.3`: HTTP リクエスト
- `beautifulsoup4==4.12.3`: HTML/XML パース

**並列処理関連**
- `joblib==1.4.2`: 並列計算・キャッシュ

**ログ管理**
- `kklogger`: ログ出力用のカスタムライブラリ（実装確認済み）

### Key Features

- 時系列的に定点観測された日本全国の不動産データを用いた分析が可能である.
- 機械学習モデルのよる価格予測から比較される割高割安の判定.
- 及びそれらを可視化する機能提供

### Target Users

今のところ、私個人のみである. もしかしたらサービス展開する可能性はある.

## Project Structure

### Directory Layout

```
├── .claude
├── CLAUDE.md
├── README.md          # プロジェクト概要や、サービス構築手順など.
├── kkestate           # 共通して使われる class や function はここで管理される
│   ├── config         # データベース接続などの設定用ファイル
│   ├── master         # マスターデータ管理（JSONスキーマ定義など）
│   │   └── json_schemas.py    # JSONスキーマ定義
│   ├── test           # テスト用共通データ
│   │   └── testcases.py       # テストケース定義
│   └── util           # 共通した処理が関数化されて管理される
├── main               # サービスインストールや実行に必要なファイル群
│   ├── analyze        # データ分析
│   ├── collect        # データ収集
│   │   ├── monitor.sh # 実行バッチ（完成済）
│   │   └── suumo.py   # 情報収集モジュール（完成済）
│   ├── database       # データベースに関連するファイル. schema など
│   │   ├── schema.collect.sql
│   │   └── schema.process.sql
│   ├── log            # サービス実行時のログが格納される. 基本的に空
│   ├── others         # その他ファイル. crontab など
│   ├── process        # 収集されたデータの後処理. データクレンジングや項目整理など
│   │   ├── generate_detail_ref.py  # 物件詳細参照データ生成
│   │   └── process_estate.py       # データクレンジング処理メイン
│   └── web            # データ分析及び結果を確認するためのWeb画面
├── pyproject.toml     # Python の依存パッケージの記述
├── test               # テスト用プログラム
└── venv               # pyproject.toml を元に作成された仮想環境. `python -m venv venv & source venv/bin/activate & pip install -e .` で実行された後の状態
```

NEVER: 上述のディレクトリ構造は保ち、新規ディレクトリの作成は禁ずる.

### Proceeding

- collect: completed.
- process: completed.
- analyze: not yet ( make it later ).
- web: high proority

### File Organization

#### Core Packages

- **kkestate/**: 共通ライブラリパッケージ
  - `config/`: 設定管理モジュール
    - `psgre.py`: PostgreSQL接続設定（HOST, PORT, USER, PASS, DBNAME）
  - `master/`: マスターデータ管理
    - `json_schemas.py`: JSONスキーマ定義（クレンジング済みデータの型定義）
  - `test/`: テスト用共通データ
    - `testcases.py`: 全テストケース定義（467ケース）
  - `util/`: 汎用ユーティリティ関数
    - `parser.py`: 統合パーサーモジュール（住所、建物構造、リフォーム、地目、周辺施設、駐車場、間取り図、建ぺい率・容積率）
    - `json_cleaner.py`: JSONクレンジング処理（価格、面積、間取りなどの正規化）
    - `key_mapper.py`: キーごとの処理マッピング（estate_mst_keyとクレンジング関数の対応）

#### Application Modules

- **main/collect/**: データ収集モジュール（完成済み）
  - `suumo.py`: SUUMOサイトからのスクレイピング実行モジュール
  - `monitor.sh`: バッチ実行用シェルスクリプト（URLリスト更新、メインページ収集、詳細ページ収集）
  - `README.md`: モジュール説明書

- **main/process/**: データ処理モジュール（完成済み）
  - `process_estate.py`: データクレンジング処理メイン（mapping/process/statsサブコマンド）
  - `generate_detail_ref.py`: 物件詳細参照データ生成（process/statsサブコマンド）
  - `README.md`: モジュール説明書

- **main/analyze/**: データ分析モジュール（未実装）
  - 統計分析関数（今後実装予定）
  - 価格予測モデル（今後実装予定）

- **main/web/**: Webインターフェース（未実装・高優先度）
  - React フロントエンド（今後実装予定）
  - API エンドポイント（今後実装予定）

- **main/database/**: データベース関連ファイル
  - `schema.collect.sql`: 収集系テーブル定義（estate_tmp、estate_main、estate_run、estate_mst_key、estate_detail）
  - `schema.process.sql`: 処理系テーブル定義（estate_mst_cleaned、estate_cleaned、estate_detail_ref）

- **main/others/**: その他ユーティリティ
  - `crontab`: Cron設定ファイル
  - `process_kill.py`: プロセス強制終了ユーティリティ

#### Module Dependencies

- `main/*` モジュールは `kkestate` パッケージに依存
- 各モジュールは独立して動作可能な設計
- データフローは collect -> process -> ( analyze )  -> web の順序
- 基本的に各フローは並列に動作し、データベースで間接的にステータス管理され、データフローが構築される

### Naming Conventions

Python については、既存のモジュールを確認した上で私の好みを理解し、それに可能な限り習うようにする.
その他については一任する.

## Development Setup

IMPORTANT: 本環境は本番環境ではない.
IMPORTANT: 本番環境のデータベースはMCPで接続されているが、あなたは読み取り権限しか与えられない. そのため、新規 schema 作成などは私が行う必要がある.

### Prerequisites

- Ubuntu OS
- Python 3.12.8以上
- Docker (PostgreSQL用)

### Python Setup

```bash
# リポジトリクローンと仮想環境作成
cd /home/kkazuki/10.git/kkestate
python -m venv venv
source venv/bin/activate
pip install -e .

# 設定ファイルの編集
vi kkestate/config/psgre.py  # データベース接続情報の設定
# 以下の変数を環境に合わせて設定:
# HOST, PORT, USER, PASS, DBNAME

# ログディレクトリの作成
mkdir -p main/log
```

## Common Commands

### Build & Run

```bash
# データ収集の実行
bash ~/kkestate/main/collect/monitor.sh 1  # URLリストの更新
bash ~/kkestate/main/collect/monitor.sh 2  # メインページのスクレイピング
bash ~/kkestate/main/collect/monitor.sh 3  # 詳細ページのスクレイピング (日付指定: YYYYMMDD)

# Python モジュールの直接実行
source ~/venv/bin/activate
python ~/kkestate/main/collect/suumo.py --updateurls --update
python ~/kkestate/main/collect/suumo.py --runmain --update
python ~/kkestate/main/collect/suumo.py --rundetail --datefrom 20250101 --skipsuccess --update

# データ処理の実行
python ~/kkestate/main/process/process_estate.py --mapping --update    # キーマッピング更新
python ~/kkestate/main/process/process_estate.py --process --update    # データクレンジング処理
python ~/kkestate/main/process/process_estate.py --stats               # 統計情報表示
python ~/kkestate/main/process/process_estate.py --runid 12345 --process --update  # 特定runのみ処理
```

### Testing

```bash
# テストの実行例
source venv/bin/activate
python test/test_json_cleansing.py
python test/test_parser_integration.py
python test/test_structure_integration.py
python test/test_feature_pickup.py
python test/test_address_parser.py

# 全テストの実行
cd test && python -m pytest . -v

# 特定のテストファイルのみ実行
python -m pytest test/test_json_cleansing.py -v
```

### Deployment

`./README.md` に記述あり.

### Database Operations

```bash
# PostgreSQL 接続
sudo docker exec -it --user=postgres postgres psql -U postgres -d estate

# データベースのバックアップ
sudo docker exec --user=postgres postgres pg_dump -Fc estate > /home/share/db_$(date +%Y%m%d).dump

# よく使用するクエリ
# 最新の収集データ確認
SELECT * FROM estate_run ORDER BY id DESC LIMIT 10;

# キーマスタの確認
SELECT id, name, id_cleaned FROM estate_mst_key ORDER BY id;

# クレンジング済み項目の確認
SELECT id, name, type FROM estate_mst_cleaned ORDER BY id;

# 特定物件の詳細確認
SELECT k.name, d.value 
FROM estate_detail d 
JOIN estate_mst_key k ON d.id_key = k.id 
WHERE d.id_run = ? ORDER BY k.id;

# 未処理のURL確認
SELECT COUNT(*) FROM estate_tmp WHERE is_checked = false;
```

### Python

#### Class/Function

IMPORTANT: モジュール（テストスクリプトも含む）を横断して使われるような共通的な関数やクラスは、repository 名と同じディレクトリ配下の箇所に適切に書いて整理して.
IMPORTANT: モジュール内でしか使われない関数やクラスは、そのモジュール内で定義して使って.

#### Main

- NEVER: main() プロセスは書かない.
- IMPORTANT: 以下のように `if __name__ == "__main__":` からはじめ、argparse で引数を設定できるようにする. 
- その際、database の INSERT / UPDATE / COPY の処理が入る場合は、`update` flg を持たせる事. また、それらの処理は if args.update: で必ずロジックを分ける事.

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update",  action='store_true', default=False)
    ...
    args = parser.parse_args()
    LOGGER.info(f"{args}")
```

#### Logger

NEVER: pythonモジュール内の実行処理として、log ファイルを外部に生成し、そこに print や logger の情報を出力する、といった処理は禁ずる.
IMPORTANT: logger は下記の方法で `main/` と `test/` 内の各モジュールで実装される事. 

```python
# Import
from kklogger import set_logger
LOGGER = set_logger(__name__)
# How to use
LOGGER.info(f"test code.")
# Change the color
LOGGER.info("Hello, World!", color=["BOLD",      "GREEN"])
LOGGER.info("Hello, World!", color=["UNDERLINE", "BLUE"])
LOGGER.info("Hello, World!", color=["REVERCE",   "RED"])
LOGGER.info("Hello, World!", color=["INVISIBLE", "WHITE"])
```

#### Database

- IMPORTANT: 一連の処理のトランザクションを確保したい場合（例えばDELETE/INSERTの処理）、そのように気を付ける事.

```python
# Import
from kkpsgre.connector import DBConnector
from kkestate.config.psgre import HOST, PORT, USER, PASS, DBNAME, DBTYPE
# Connection
DB = DBConnector(HOST, port=PORT, dbname=DBNAME, user=USER, password=PASS, dbtype=DBTYPE, max_disp_len=200)
# Select
df: pd.DataFrame = DB.select_sql("select * from tabel_name limit 100;")
print(df)
# Insert (一連のトランザクションを確保)
DB.set_sql("delete from table_name where ...;")
DB.insert_from_df(df, "table_name", is_select=True, set_sql=True)
DB.execute_sql()
# 汎用実行SQL
DB.execute_sql(f"update estate_run set is_success = true where id = {id_run};")
```

## Architecture

### System Design

@README.md

### Data Flow

1. COLLECT
    1. `estate_tmp` をクリアする.
    2. `SUUMO` には大項目としての「都道府県」や「新築/中古」などの項目があり、そのページには各物件が何ページにも渡ってリスト化されている. まずはそれらページに直接アクセスできるようなURL_Aを編集作成し、`estate_tmp` に書き込む.
    3. `estate_tmp` から `is_checked = false` な URL_A を参照し、そのページにリスト化されている物件の詳細情報を取得するための URL_B を抽出する.
    4. URA_A ページにある各物件について情報を取得できた場合は、`estate_tmp` の該当レコードの `is_checked` を true にする.
    5. ある URL_B は1物件に対して一意であるとし、`estate_main` に URL_B が存在しない場合は URL_B の情報を書き込む. 存在する場合は、`sys_updated` のみが update される. この処理において、URL_B と一意に対応する `id` は自動採番される.
    6. `estate_main` の情報を取得し、各物件の詳細情報を URL_B から取得する. 
    7. 各物件の詳細情報の取得可否については `estate_run` で管理され、詳細情報取得処理が走れば `estate_run` にレコードが追加される. `estate_run` の `id` は自動採番される.
    8. 詳細情報は `key` と `value` で保持され、それらはピュアにスクレイピングされたテキスト情報であり、未クレンジングな状態である. `key` の名前は `estate_mst_key` で管理され、新規の名前の場合は登録され、`id` が自動採番される.
    9. 詳細情報は `estate_detail` に記録され、その際、`estate_mst_key` で管理される `id` に置き換えて記録される. ただし、前回記録されたデータと `key` と `value` 単位で同じデータであった場合、その項目は記録されない. 要は差異がある場合のみ記録される仕組みになっている.
    10. 正しく記録できた場合は、`estate_run` の `is_success` を true にする.
2. PROCESS（完成済み）
    **2-1. MAPPING（キーマッピング）**
    1. `estate_mst_key` に登録されている全ての生データキーを取得する.
    2. `key_mapper.py` の定義に基づいて、各キーに対応するクレンジング関数を特定する.
    3. クレンジング対象となるキーについて、`estate_mst_cleaned` に項目名とJSONスキーマを登録する.
    4. `estate_mst_key.id_cleaned` に対応する `estate_mst_cleaned.id` を紐づける.
    5. 実行: `python process_estate.py mapping --update`

    **2-2. CLEANING（データクレンジング）**
    1. `estate_run` から `is_success = true` かつ未処理のデータを取得する（estate_cleanedに存在しないrun_id）.
    2. 対象run_idの `estate_detail` から、`id_cleaned IS NOT NULL` のキーのみを取得する.
    3. 各キーの生データを、対応するクレンジング関数で処理する（parser.py、json_cleaner.py使用）.
    4. クレンジング結果をJSON形式に正規化し、`estate_cleaned` テーブルに保存する.
    5. 実行: `python process_estate.py process --update`
    6. 注: `is_success` の更新はcollect側で既に完了しているため、process側では更新しない.

    **2-3. REF（データ参照関係生成）**
    1. 指定されたrun_idに対して、過去半年以内の同一物件（同じid_main）の履歴データを取得する.
    2. 各id_keyごとに、対象日時以前の最新データを持つrun_idを特定する.
    3. `estate_detail_ref` テーブルに参照関係（id_run, id_key, id_run_ref）を保存する.
    4. この参照関係により、データ節約のため省略されたレコードを過去データから補完可能にする.
    5. 実行: `python generate_detail_ref.py process --update`

3. ANALYZE
  未実装
4. WEB
  未実装

### Key Components

### Database Schema

プロジェクトでは以下の8つのテーブルを使用している：

1. **`estate_tmp`** - 一時的なURL管理テーブル
   - `url` (text, NOT NULL): スクレイピング対象のURL
   - `is_checked` (boolean, NOT NULL, default: false): 処理済みフラグ
   - `sys_updated` (timestamp, NOT NULL, default: CURRENT_TIMESTAMP): 更新日時

2. **`estate_main`** - 物件の基本情報テーブル
   - `id` (bigint, NOT NULL, PK, auto-increment): 自動採番ID
   - `name` (text): 物件名
   - `url` (text, NOT NULL, UNIQUE): 物件詳細ページのURL（一意）
   - `sys_updated` (timestamp, NOT NULL, default: CURRENT_TIMESTAMP): 更新日時

3. **`estate_run`** - 実行履歴管理テーブル
   - `id` (bigint, NOT NULL, PK, auto-increment): 自動採番ID
   - `id_main` (bigint, NOT NULL): estate_mainのIDへの参照
   - `is_success` (boolean, NOT NULL, default: false): 実行成功フラグ
   - `timestamp` (timestamp): 実行日時

4. **`estate_mst_key`** - 項目名マスタテーブル
   - `id` (smallint, NOT NULL, PK, auto-increment): 自動採番ID
   - `name` (text, NOT NULL, UNIQUE): 項目名（スクレイピングで取得されるキー）
   - `sys_updated` (timestamp, NOT NULL, default: CURRENT_TIMESTAMP): 更新日時
   - `id_cleaned` (smallint): estate_mst_cleanedのIDへの参照

5. **`estate_mst_cleaned`** - クレンジング済み項目名マスタテーブル
   - `id` (smallint, NOT NULL, PK, auto-increment): 自動採番ID
   - `name` (text, NOT NULL, UNIQUE): クレンジング済み項目名
   - `type` (json): 値の型定義とスキーマ情報

6. **`estate_detail`** - 物件詳細情報テーブル
   - `id_run` (bigint, NOT NULL): estate_runのIDへの参照
   - `id_key` (smallint, NOT NULL): estate_mst_keyのIDへの参照
   - `value` (text): 項目の値（スクレイピングで取得される生データ）
   - 複合主キー: (id_run, id_key)

7. **`estate_cleaned`** - クレンジング済みデータテーブル
   - `id_run` (bigint, NOT NULL): estate_runのIDへの参照
   - `id_key` (smallint, NOT NULL): estate_mst_keyのIDへの参照
   - `id_cleaned` (smallint, NOT NULL): estate_mst_cleanedのIDへの参照
   - `value_cleaned` (json): クレンジング済みの値（JSON形式）
   - 複合主キー: (id_run, id_key)
   - 外部キー: id_run → estate_run(id), id_key → estate_mst_key(id), id_cleaned → estate_mst_cleaned(id)

8. **`estate_detail_ref`** - データ参照関係管理テーブル
   - `id_run` (bigint, NOT NULL): estate_runのIDへの参照
   - `id_key` (smallint, NOT NULL): estate_mst_keyのIDへの参照
   - `id_run_ref` (bigint, NOT NULL): 参照先のestate_runのID
   - 複合主キー: (id_run, id_key)
   - 外部キー: id_run → estate_run(id), id_key → estate_mst_key(id), id_run_ref → estate_run(id)

#### JSON データ構造例

**estate_mst_cleaned.type**:
```json
{
  "base_type": "range|single|boolean|list|structure",
  "data_type": "number|text|date|boolean",
  "fields": ["min", "max", "unit"] or ["value"] or ["items"],
  "required_fields": [],
  "optional_fields": ["note", "tentative", "management_type", "work_style", "has_reform", "reform_info", "total_floors", "basement_floors", "floor", "partial_structure", "raw_value"]
}
```

**estate_cleaned.value_cleaned**:
```json
// 範囲データ（価格、面積など）
{"min": 2685, "max": 3955, "unit": "万円"}

// 単一値データ
{"value": "2LDK・3LDK"}

// Boolean データ
{"value": true}

// リスト形式データ（地目、特徴など）
{"items": ["宅地", "畑"], "note": "現況地目：宅地"}

// 構造化データ（建物構造、駐車場など）
{"structure": "木造", "total_floors": 2, "floor": 1, "note": "軸組工法"}
```

#### インデックス構成

**estate_main**:
- PK: `id`
- UNIQUE: `url`

**estate_run**:
- PK: `id`
- INDEX: `is_success`
- INDEX: `timestamp`
- INDEX: `(id, is_success, timestamp)`

**estate_mst_key**:
- PK: `id`
- UNIQUE: `name`

**estate_mst_cleaned**:
- PK: `id`
- UNIQUE INDEX: `name`

**estate_detail**:
- PK: `(id_run, id_key)`
- INDEX: `id_run`
- INDEX: `id_key`

**estate_cleaned**:
- PK: `(id_run, id_key)`
- INDEX: `id_run`
- INDEX: `id_key`
- INDEX: `id_cleaned`
- INDEX: `(id_run, id_cleaned)`

**estate_detail_ref**:
- PK: `(id_run, id_key)`
- INDEX: `id_run`
- INDEX: `id_key`
- INDEX: `id_run_ref`
- INDEX: `(id_run, id_key)`

### External Services

## Coding Guidelines

特に無いが、既存のコード様式を Follow して.

## Development Workflow

### Git Workflow

1. **基本フロー**
  - 作業前に必ず最新の main ブランチを pull
  - 機能開発は feature ブランチで行う
  - コミットは小さく、頻繁に行う
  - push 前にローカルでテストを実行

2. **コミット前の確認事項**
  - 不要なデバッグコードの削除
  - 秘密情報（パスワード、APIキー）が含まれていないか確認
  - コードフォーマットの統一

### Branch Strategy

1. **ブランチ命名規則**
  - feature/機能名 - 新機能開発
  - fix/バグ名 - バグ修正
  - refactor/対象名 - リファクタリング
  - docs/文書名 - ドキュメント更新

2. **ブランチ運用**
  - main: 本番環境相当の安定版
  - develop: 開発中の最新版（使用する場合）
  - feature/*: 各機能開発用
  - 長期間のブランチは定期的に main をマージ

### PR Process

1. **PR作成前**
  - ローカルでのテスト完了
  - コンフリクトの解消
  - 不要なファイルの除外

2. **PR作成時**
  - タイトルは変更内容を簡潔に記載
  - 本文には以下を含める：
    - 変更の概要
    - 変更理由
    - テスト方法
    - 関連するIssue番号（あれば）

3. **マージ条件**
  - レビュー承認
  - CI/CDパス（設定されている場合）
  - コンフリクトなし

### Review Guidelines

1. **レビュー観点**
  - コードの可読性
  - パフォーマンスへの影響
  - セキュリティリスク
  - 既存機能への影響
  - テストの妥当性

2. **フィードバック方法**
  - 具体的な改善案を提示
  - 必須修正と推奨事項を区別
  - 良い点も積極的にコメント

3. **レビュー対応**
  - フィードバックには迅速に対応
  - 修正内容はコミットメッセージで明確化
  - 議論が必要な場合はコメントで返信

## Testing

IMPORTANT: テスト用のコードは `test/*` に書いて.

### Test Structure

プロジェクトでは以下のテスト構成を使用:

- **test/test_key_mapping.py**: キーマッピング機能のテスト
- **test/test_json_cleansing.py**: JSON形式でのデータクレンジングテスト（467テストケース、全パス）
- **test/test_schema_validation.py**: JSONスキーマ検証テスト（467テストケース、全パス）
- **test/test_parser_integration.py**: パーサー統合テスト
- **test/test_structure_integration.py**: 構造解析統合テスト
- **test/test_feature_pickup.py**: 特徴抽出テスト
- **test/test_address_parser.py**: 住所パーサーテスト
- **test/MST.py**: テスト用のマスターデータ（変更禁止）

### Running Tests

- 何かの修正後は以下を実行して問題が無い事を確認する事.

```bash
# 基本的なテスト実行
python -m test.test_key_mapping
python -m test.test_json_cleansing
python -m test.test_schema_validation

# 全テストの実行（推奨）
cd test && python -m pytest . -v

# 特定のテストファイルのみ実行
python -m pytest test/test_parser_integration.py -v
python -m pytest test/test_structure_integration.py -v

# 失敗したテストのみ再実行
python -m pytest test/ -v --lf

# 特定のテストケースのみ実行
python -m pytest test/test_json_cleansing.py::TestJsonCleansing::test_keyid_123 -v
```

### Writing Tests

## Troubleshooting

### Common Issues

### Debug Tips

## Important Notes

### IMPORTANT: Record sessions

IMPORTANT: 
- 実行した内容について、「どんな経緯で」「何を目的に」「どんな実装をしたか」「結果どうだったか」を、後日あなたが見返した時に過去に何があったかを詳細に把握できるように記載する必要がある.
- `./.claude/sessions/YYYYMMDD.md` 形式で、実装が発生した場合は都度内容を更新する. 
- 
- IMPORTANT: この内容はいちいち指示しないため、あなたのタイミングでサマライズして簡潔に記録しなければならない.
- session 開始時は `./.claude/sessions/*.md` から直近２ファイルの記録を見て、何があったかを把握しなければならない.
- 特に最新のセッションファイル（前日や当日分）は必ず確認し、継続作業や未完了のタスクがないか確認する.
- 最新セッションのファイル名は日付順でソートして特定し、その内容から前回の作業状況と次のステップを理解する.
- 作業中断や問題発生時は、問題の内容と次回の対応方針をセッションファイルに明記し、継続性を保つ.
- 大量のテストが失敗する場合は、個別対処ではなく根本原因（設定ファイル、依存関係、環境等）の分析から開始する.

**記録フォーマット例**:
```markdown
## YYYYMMDD.md

### HH:MM - 作業タイトル
**経緯**: なぜこの作業を行うことになったか
**目的**: 何を達成しようとしているか
**実装内容**: 
- 実装したファイルと主な変更点
- 使用した技術やアプローチ
**結果**: 実装の結果と次のステップ

### 例: 10:30 - データクレンジング機能の実装
**経緯**: estate_detailの生データを分析可能な形式に変換する必要がある
**目的**: 価格、面積、間取りなどを統一されたJSON形式で保存
**実装内容**: 
- key_processing_mapper.pyを作成し、各キーに対応する処理関数を定義
- json_cleaner.pyでJSON形式での出力を実装
- 価格の「万円」表記を数値に変換する処理を追加
**結果**: 主要項目のクレンジングが完了. 次は特殊なケースへの対応が必要
```

### IMPORTANT: Database

IMPORTANT: 
- データのSELECT には必ず LIMIT をつける事. LIMIT 100 でまずは様子をみつつ、その取得時間が10秒以内である場合は、LIMIT を x5 ずつして許容量を上げていく. 基本的にクエリは 10秒以内に終了される事.
- 初手の JOINS は避ける. まずは LIMIT をつけて単体のテーブルデータを確認する事.
- 複雑な JOIN クエリは避ける事。なるべくシンプルなSQLを組み合わせて python モジュールの中で joins させるなどする.

### IMPORTANT: For Test

NEVER: `./kkestate/test/*` は絶対に修正しないで.