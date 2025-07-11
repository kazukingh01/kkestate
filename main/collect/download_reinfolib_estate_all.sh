#!/bin/bash

# REINFOLIBから指定期間のデータをダウンロードするスクリプト
# 使用方法: ./download_reinfolib_estate_all.sh [year_from] [year_to]
# 例: ./download_reinfolib_estate_all.sh 2020 2024
# 引数を省略した場合: 2006年から2024年まで

# 引数処理
YEAR_FROM=${1:-2006}
YEAR_TO=${2:-2024}

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/reinfolib.py"
DOWNLOAD_DIR="./downloads/"
MAX_RETRY=3
RETRY_WAIT=10

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# ダウンロード実行関数
download_with_retry() {
    local year=$1
    local period=$2
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRY ]; do
        log "Downloading: ${year}年第${period}四半期 (attempt $((retry_count + 1)))"
        
        # Pythonスクリプト実行
        python "$PYTHON_SCRIPT" estate --year "$year" --period "$period" --download-dir "$DOWNLOAD_DIR" --headless
        
        # 終了コードチェック
        if [ $? -eq 0 ]; then
            log "Success: ${year}年第${period}四半期"
            return 0
        else
            log "Failed: ${year}年第${period}四半期 - waiting ${RETRY_WAIT} seconds before retry"
            sleep $RETRY_WAIT
            retry_count=$((retry_count + 1))
        fi
    done
    
    log "ERROR: Failed to download ${year}年第${period}四半期 after ${MAX_RETRY} attempts"
    return 1
}

# メイン処理
main() {
    # 引数のバリデーション
    if ! [[ "$YEAR_FROM" =~ ^[0-9]{4}$ ]] || ! [[ "$YEAR_TO" =~ ^[0-9]{4}$ ]]; then
        log "ERROR: 年度は4桁の数字で指定してください"
        exit 1
    fi
    
    if [ "$YEAR_FROM" -gt "$YEAR_TO" ]; then
        log "ERROR: year_from は year_to 以下である必要があります"
        exit 1
    fi
    
    if [ "$YEAR_FROM" -lt 2006 ]; then
        log "WARNING: 2006年より前のデータは存在しません. 2006年から開始します"
        YEAR_FROM=2006
    fi
    
    # YEAR_FROM修正後の再チェック
    if [ "$YEAR_FROM" -gt "$YEAR_TO" ]; then
        log "ERROR: 修正後のyear_from(${YEAR_FROM})がyear_to(${YEAR_TO})より大きくなりました"
        exit 1
    fi
    
    log "=== REINFOLIB Download Start ==="
    log "期間: ${YEAR_FROM}年 から ${YEAR_TO}年"
    
    # ダウンロードディレクトリ作成
    mkdir -p "$DOWNLOAD_DIR"
    
    # 成功・失敗カウンタ
    success_count=0
    failed_count=0
    
    # 指定された年度範囲で処理
    for year in $(seq $YEAR_FROM $YEAR_TO); do
        for period in 1 2 3 4; do
            
            # 既にダウンロード済みファイルが存在する場合はスキップ
            if [ -f "${DOWNLOAD_DIR}/reinfolib_estate_${year}_${period}.zip" ]; then
                log "Skip: ${year}年第${period}四半期 (already exists)"
                continue
            fi
            
            # ダウンロード実行
            if download_with_retry $year $period; then
                success_count=$((success_count + 1))
            else
                failed_count=$((failed_count + 1))
            fi
            
            # 連続アクセスを避けるため少し待機
            sleep 2
        done
    done
    
    log "=== Download Complete ==="
    log "Success: $success_count files"
    log "Failed: $failed_count files"
    
    # 失敗があった場合は終了コード1
    if [ $failed_count -gt 0 ]; then
        exit 1
    fi
}

# 使用方法表示
usage() {
    echo "Usage: $0 [year_from] [year_to]"
    echo "  指定された期間の不動産取引価格データを一括取得"
    echo ""
    echo "Arguments:"
    echo "  year_from  開始年度 (デフォルト: 2006)"
    echo "  year_to    終了年度 (デフォルト: 2024)"
    echo ""
    echo "Example:"
    echo "  $0                # 2006-2024年のデータを取得"
    echo "  $0 2020           # 2020-2024年のデータを取得"
    echo "  $0 2020 2023      # 2020-2023年のデータを取得"
}

# 引数チェック
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

# 実行
main