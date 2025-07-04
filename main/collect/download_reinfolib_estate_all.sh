#!/bin/bash

# REINFOLIBから全期間のデータをダウンロードするスクリプト
# 2006年第1四半期から2024年第4四半期まで

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
    log "=== REINFOLIB Download Start ==="
    
    # ダウンロードディレクトリ作成
    mkdir -p "$DOWNLOAD_DIR"
    
    # 成功・失敗カウンタ
    success_count=0
    failed_count=0
    
    # 2006年から2024年まで処理
    for year in $(seq 2006 2024); do
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

# 実行
main