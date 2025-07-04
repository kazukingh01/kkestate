#!/bin/bash

# REINFOLIBから地価公示・地価調査データをスクレイピングするスクリプト
# 全都道府県（01-47）の1970-2024年データを一括取得

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/reinfolib.py"
DOWNLOAD_DIR="./downloads/"
MAX_RETRY=3
RETRY_WAIT=10
START_YEAR=1970
END_YEAR=2024

# 都道府県コードと名前のマッピング
declare -A PREFECTURE_NAMES=(
    ["01"]="北海道" ["02"]="青森県" ["03"]="岩手県" ["04"]="宮城県" ["05"]="秋田県"
    ["06"]="山形県" ["07"]="福島県" ["08"]="茨城県" ["09"]="栃木県" ["10"]="群馬県"
    ["11"]="埼玉県" ["12"]="千葉県" ["13"]="東京都" ["14"]="神奈川県" ["15"]="新潟県"
    ["16"]="富山県" ["17"]="石川県" ["18"]="福井県" ["19"]="山梨県" ["20"]="長野県"
    ["21"]="岐阜県" ["22"]="静岡県" ["23"]="愛知県" ["24"]="三重県" ["25"]="滋賀県"
    ["26"]="京都府" ["27"]="大阪府" ["28"]="兵庫県" ["29"]="奈良県" ["30"]="和歌山県"
    ["31"]="鳥取県" ["32"]="島根県" ["33"]="岡山県" ["34"]="広島県" ["35"]="山口県"
    ["36"]="徳島県" ["37"]="香川県" ["38"]="愛媛県" ["39"]="高知県" ["40"]="福岡県"
    ["41"]="佐賀県" ["42"]="長崎県" ["43"]="熊本県" ["44"]="大分県" ["45"]="宮崎県"
    ["46"]="鹿児島県" ["47"]="沖縄県"
)

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# ダウンロード実行関数
download_with_retry() {
    local year=$1
    local prefecture_code=$2
    local prefecture_name=${PREFECTURE_NAMES[$prefecture_code]}
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRY ]; do
        log "Downloading: ${year}年 ${prefecture_name}(${prefecture_code}) (attempt $((retry_count + 1)))"
        
        # Pythonスクリプト実行
        python "$PYTHON_SCRIPT" land --year "$year" --prefecture-code "$prefecture_code" --download-dir "$DOWNLOAD_DIR" --headless
        
        # 終了コードチェック
        if [ $? -eq 0 ]; then
            log "Success: ${year}年 ${prefecture_name}(${prefecture_code})"
            return 0
        else
            log "Failed: ${year}年 ${prefecture_name}(${prefecture_code}) - waiting ${RETRY_WAIT} seconds before retry"
            sleep $RETRY_WAIT
            retry_count=$((retry_count + 1))
        fi
    done
    
    log "ERROR: Failed to download ${year}年 ${prefecture_name}(${prefecture_code}) after ${MAX_RETRY} attempts"
    return 1
}

# メイン処理
main() {
    log "=== REINFOLIB Land Prices Download Start ==="
    log "Target Years: ${START_YEAR}-${END_YEAR}"
    log "Target Prefectures: 01-47 (全都道府県)"
    
    # ダウンロードディレクトリ作成
    mkdir -p "$DOWNLOAD_DIR"
    
    # 成功・失敗カウンタ
    total_success=0
    total_failed=0
    
    # 1970年から2024年まで全年をループ
    for year in $(seq $START_YEAR $END_YEAR); do
        log "Processing Year: ${year}"
        year_success=0
        year_failed=0
        
        # 全都道府県（01-47）を処理
        for prefecture_code in $(seq -w 01 47); do
            prefecture_name=${PREFECTURE_NAMES[$prefecture_code]}
            
            # 既にダウンロード済みファイルが存在する場合はスキップ
            if [ -f "${DOWNLOAD_DIR}/reinfolib_land_${year}_${prefecture_code}.csv" ]; then
                log "Skip: ${year}年 ${prefecture_name}(${prefecture_code}) (already exists)"
                continue
            fi
            
            # ダウンロード実行
            if download_with_retry $year $prefecture_code; then
                year_success=$((year_success + 1))
                total_success=$((total_success + 1))
            else
                year_failed=$((year_failed + 1))
                total_failed=$((total_failed + 1))
            fi
            
            # 連続アクセスを避けるため少し待機
            sleep 3
        done
        
        log "Year ${year} Complete: Success=${year_success}, Failed=${year_failed}"
    done
    
    log "=== All Years Download Complete ==="
    log "Total Success: $total_success files"
    log "Total Failed: $total_failed files"
    
    # 失敗があった場合は終了コード1
    if [ $total_failed -gt 0 ]; then
        exit 1
    fi
}

# 使用方法表示
usage() {
    echo "Usage: $0"
    echo "  全都道府県の${START_YEAR}年-${END_YEAR}年の地価公示・地価調査データを一括取得"
    echo ""
    echo "Example:"
    echo "  $0        # ${START_YEAR}-${END_YEAR}年の全都道府県データを取得"
}

# 引数チェック
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

# 実行
main