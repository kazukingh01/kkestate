#!/bin/bash

# スクリプトのディレクトリに移動
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 現在日付から10日を引いて、1日、11日、21日のいずれかに丸める関数
get_rounded_date() {
    # 現在日付から10日を引く
    target_date=$(date -d "10 days ago" +%Y%m%d)
    
    # 日付の日部分を取得
    day=$(date -d "$target_date" +%d)
    year_month=$(date -d "$target_date" +%Y%m)
    
    # 日付を1、11、21のいずれかに丸める
    if [ $day -le 10 ]; then
        rounded_day="01"
    elif [ $day -le 20 ]; then
        rounded_day="11"
    else
        rounded_day="21"
    fi
    
    echo "${year_month}${rounded_day}"
}

# デフォルト値
YEAR=2024
DRY_RUN=false
PREFECTURES=""
SINCE_DATE=""
OUTPUT_DIR=""

# 引数処理
while [[ $# -gt 0 ]]; do
    case $1 in
        --year)
            YEAR="$2"
            shift 2
            ;;
        --since)
            SINCE_DATE="$2"
            shift 2
            ;;
        --dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --prefectures)
            PREFECTURES="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --year YEAR          処理対象年 (default: 2024)"
            echo "  --since YYYYMMDD     開始日付 (default: 現在日時-10日を1/11/21に丸めた値)"
            echo "  --dir PATH           出力ディレクトリ (default: ./html)"
            echo "  --dry-run            実際には実行せず、コマンドのみ表示"
            echo "  --prefectures CODES  実行する都道府県コード（カンマ区切り）. 例: 13,14,27"
            echo "  --help               このヘルプを表示"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# 日付が指定されていない場合は計算
if [ -z "$SINCE_DATE" ]; then
    SINCE_DATE=$(get_rounded_date)
fi

echo "実行設定: year=$YEAR, since=$SINCE_DATE, dir=$OUTPUT_DIR, dry_run=$DRY_RUN"

# 実行する都道府県コードのリストを決定
if [ -n "$PREFECTURES" ]; then
    # カンマ区切りを配列に変換
    IFS=',' read -ra PREFECTURE_ARRAY <<< "$PREFECTURES"
else
    # 01-47の全都道府県コード
    PREFECTURE_ARRAY=($(seq -w 01 47))
fi

echo "処理対象都道府県数: ${#PREFECTURE_ARRAY[@]}"

# 結果カウント
SUCCESS_COUNT=0
FAILED_CODES=()

# 各都道府県に対して実行
for CODE in "${PREFECTURE_ARRAY[@]}"; do
    CMD="python ana.py --code $CODE --year $YEAR --since $SINCE_DATE"
    if [ -n "$OUTPUT_DIR" ]; then
        CMD="$CMD --dir $OUTPUT_DIR"
    fi
    
    echo "=========================================="
    echo "都道府県コード $CODE の処理を開始"
    echo "コマンド: $CMD"
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] 実行をスキップ"
        continue
    fi
    
    # コマンド実行
    if eval $CMD; then
        echo "都道府県コード $CODE の処理が完了"
        ((SUCCESS_COUNT++))
    else
        echo "エラー: 都道府県コード $CODE の処理に失敗"
        FAILED_CODES+=($CODE)
    fi
done

# 結果のサマリを表示
echo "=========================================="
echo "処理完了: 成功 $SUCCESS_COUNT/${#PREFECTURE_ARRAY[@]} 件"

if [ ${#FAILED_CODES[@]} -gt 0 ]; then
    echo "失敗した都道府県コード: ${FAILED_CODES[*]}"
    exit 1
else
    echo "全ての都道府県の処理が正常に完了しました"
    exit 0
fi