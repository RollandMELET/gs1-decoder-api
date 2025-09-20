#!/bin/bash
# Script de monitoring complet tous formats + endpoints

set -e

API_URL="https://gs1-decoder-api.rorworld.eu"
LOG_FILE="monitor-all-formats.log"
JSON_LOG="monitor-metrics.json"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
TIMESTAMP=$(date +%s)

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$DATE]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$DATE] WARN:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$DATE] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$DATE] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# Initialiser JSON metrics
echo "{\"timestamp\": $TIMESTAMP, \"tests\": {}" > "$JSON_LOG"

# Fonction pour ajouter métrique JSON
add_metric() {
    local format="$1"
    local status="$2"
    local size="$3"
    local response_time="$4"

    jq --arg fmt "$format" --arg st "$status" --argjson sz "$size" --argjson rt "$response_time" \
       '.tests[$fmt] = {"status": $st, "file_size": $sz, "response_time_ms": $rt}' \
       "$JSON_LOG" > "${JSON_LOG}.tmp" && mv "${JSON_LOG}.tmp" "$JSON_LOG"
}

log "🏥 === MONITORING COMPLET TOUS FORMATS ==="

# Test health
log "🏥 Test health endpoint..."
health_start=$(date +%s%N)
health_response=$(curl -s -w "%{http_code}" "$API_URL/health" -o health.json || echo "000")
health_end=$(date +%s%N)
health_time=$(( (health_end - health_start) / 1000000 ))

if [ "$health_response" = "200" ]; then
    log "✅ API accessible (${health_time}ms)"

    # Vérifier capacités critiques
    bwipjs_status=$(jq -r '.capabilities.generators.bwipjs' health.json 2>/dev/null || echo "false")
    nodejs_status=$(jq -r '.capabilities.generators.nodejs' health.json 2>/dev/null || echo "false")

    if [ "$bwipjs_status" = "true" ] && [ "$nodejs_status" = "true" ]; then
        log "✅ Capacités critiques GS1 DataMatrix disponibles"
    else
        error "❌ Capacités critiques manquantes: bwip-js=$bwipjs_status, nodejs=$nodejs_status"
    fi
else
    error "❌ API non accessible (code: $health_response)"
    exit 1
fi

log "🧪 === TESTS FORMATS PAR PRIORITÉ ==="

# PRIORITÉ 1: GS1 DataMatrix (CRITIQUE)
log "🔴 CRITIQUE: Test GS1 DataMatrix..."
gs1_start=$(date +%s%N)
gs1_simple_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)03760423190005", "barcode_format": "gs1_datamatrix"}' \
  -o gs1_simple.png || echo "000")
gs1_end=$(date +%s%N)
gs1_time=$(( (gs1_end - gs1_start) / 1000000 ))

if [ "$gs1_simple_response" = "200" ]; then
    gs1_size=$(stat -c%s gs1_simple.png 2>/dev/null || stat -f%z gs1_simple.png 2>/dev/null)
    log "✅ GS1 DataMatrix simple: ${gs1_size} bytes (${gs1_time}ms)"

    if [ "$gs1_size" -ge 500 ] && [ "$gs1_size" -le 800 ]; then
        log "✅ CRITIQUE: Optimisation GS1 DataMatrix CONFORME"
        add_metric "gs1_datamatrix" "success" "$gs1_size" "$gs1_time"
    else
        error "🚨 CRITIQUE: Optimisation GS1 DataMatrix DÉGRADÉE: ${gs1_size} bytes"
        add_metric "gs1_datamatrix" "optimization_failed" "$gs1_size" "$gs1_time"
    fi
    rm -f gs1_simple.png
else
    error "🚨 CRITIQUE: GS1 DataMatrix ÉCHOUÉ (code: $gs1_simple_response)"
    add_metric "gs1_datamatrix" "failed" 0 0
fi

# PRIORITÉ 2: Autres formats GS1
log "🟡 Test autres formats GS1..."

# GS1-128
gs1_128_start=$(date +%s%N)
gs1_128_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)03760423190005", "barcode_format": "gs1_128"}' \
  -o gs1_128.png || echo "000")
gs1_128_end=$(date +%s%N)
gs1_128_time=$(( (gs1_128_end - gs1_128_start) / 1000000 ))

if [ "$gs1_128_response" = "200" ]; then
    gs1_128_size=$(stat -c%s gs1_128.png 2>/dev/null || stat -f%z gs1_128.png 2>/dev/null)
    log "✅ GS1-128: ${gs1_128_size} bytes (${gs1_128_time}ms)"
    add_metric "gs1_128" "success" "$gs1_128_size" "$gs1_128_time"
    rm -f gs1_128.png
else
    warn "⚠️ GS1-128 échoué (code: $gs1_128_response)"
    add_metric "gs1_128" "failed" 0 0
fi

# GS1 QR Code
gs1_qr_start=$(date +%s%N)
gs1_qr_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)03760423190005", "barcode_format": "gs1_qr_code"}' \
  -o gs1_qr.png || echo "000")
gs1_qr_end=$(date +%s%N)
gs1_qr_time=$(( (gs1_qr_end - gs1_qr_start) / 1000000 ))

if [ "$gs1_qr_response" = "200" ]; then
    gs1_qr_size=$(stat -c%s gs1_qr.png 2>/dev/null || stat -f%z gs1_qr.png 2>/dev/null)
    log "✅ GS1 QR Code: ${gs1_qr_size} bytes (${gs1_qr_time}ms)"
    add_metric "gs1_qr_code" "success" "$gs1_qr_size" "$gs1_qr_time"
    rm -f gs1_qr.png
else
    warn "⚠️ GS1 QR Code échoué (code: $gs1_qr_response)"
    add_metric "gs1_qr_code" "failed" 0 0
fi

# PRIORITÉ 3: Formats standard
log "🔵 Test formats standard..."

# QR Code standard
qr_start=$(date +%s%N)
qr_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "Standard QR Test Data", "barcode_format": "qr_code"}' \
  -o qr_standard.png || echo "000")
qr_end=$(date +%s%N)
qr_time=$(( (qr_end - qr_start) / 1000000 ))

if [ "$qr_response" = "200" ]; then
    qr_size=$(stat -c%s qr_standard.png 2>/dev/null || stat -f%z qr_standard.png 2>/dev/null)
    log "✅ QR Code standard: ${qr_size} bytes (${qr_time}ms)"
    add_metric "qr_code" "success" "$qr_size" "$qr_time"
    rm -f qr_standard.png
else
    warn "⚠️ QR Code standard échoué (code: $qr_response)"
    add_metric "qr_code" "failed" 0 0
fi

# DataMatrix standard
dm_start=$(date +%s%N)
dm_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "Standard DataMatrix Content", "barcode_format": "datamatrix"}' \
  -o dm_standard.png || echo "000")
dm_end=$(date +%s%N)
dm_time=$(( (dm_end - dm_start) / 1000000 ))

if [ "$dm_response" = "200" ]; then
    dm_size=$(stat -c%s dm_standard.png 2>/dev/null || stat -f%z dm_standard.png 2>/dev/null)
    log "✅ DataMatrix standard: ${dm_size} bytes (${dm_time}ms)"
    add_metric "datamatrix" "success" "$dm_size" "$dm_time"
    rm -f dm_standard.png
else
    warn "⚠️ DataMatrix standard échoué (code: $dm_response)"
    add_metric "datamatrix" "failed" 0 0
fi

# Code 128 standard
c128_start=$(date +%s%N)
c128_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "STANDARD128TEST", "barcode_format": "code_128"}' \
  -o c128_standard.png || echo "000")
c128_end=$(date +%s%N)
c128_time=$(( (c128_end - c128_start) / 1000000 ))

if [ "$c128_response" = "200" ]; then
    c128_size=$(stat -c%s c128_standard.png 2>/dev/null || stat -f%z c128_standard.png 2>/dev/null)
    log "✅ Code 128 standard: ${c128_size} bytes (${c128_time}ms)"
    add_metric "code_128" "success" "$c128_size" "$c128_time"
    rm -f c128_standard.png
else
    warn "⚠️ Code 128 standard échoué (code: $c128_response)"
    add_metric "code_128" "failed" 0 0
fi

# ANALYSE PERFORMANCE
log "📊 === ANALYSE PERFORMANCE ==="

# Analyser métriques JSON
total_tests=$(jq '.tests | length' "$JSON_LOG")
success_tests=$(jq '[.tests[] | select(.status == "success")] | length' "$JSON_LOG")
failed_tests=$(jq '[.tests[] | select(.status == "failed" or .status == "optimization_failed")] | length' "$JSON_LOG")

log "📈 Résultats: $success_tests/$total_tests réussis"

# Vérifier seuils critiques
gs1_status=$(jq -r '.tests.gs1_datamatrix.status' "$JSON_LOG" 2>/dev/null || echo "missing")
if [ "$gs1_status" != "success" ]; then
    error "🚨 ALERT CRITIQUE: GS1 DataMatrix défaillant"
    exit 1
fi

# Seuils performance par format
log "⏱️ Validation seuils performance:"

performance_check() {
    local format="$1"
    local max_time="$2"
    local description="$3"

    local actual_time=$(jq -r ".tests.$format.response_time_ms" "$JSON_LOG" 2>/dev/null || echo "0")

    if [ "$actual_time" != "null" ] && [ "$actual_time" != "0" ]; then
        if [ "$actual_time" -le "$max_time" ]; then
            log "  ✅ $description: ${actual_time}ms (< ${max_time}ms)"
        else
            warn "  ⚠️ $description: ${actual_time}ms (> ${max_time}ms)"
        fi
    else
        warn "  ❓ $description: Pas de données temps"
    fi
}

performance_check "gs1_datamatrix" 2000 "GS1 DataMatrix"
performance_check "qr_code" 5000 "QR Code"
performance_check "datamatrix" 5000 "DataMatrix"
performance_check "code_128" 3000 "Code 128"
performance_check "gs1_128" 3000 "GS1-128"
performance_check "gs1_qr_code" 5000 "GS1 QR Code"

# Finaliser JSON
jq --arg date "$DATE" --argjson ts "$TIMESTAMP" \
   '.completed_at = $date | .duration_total_ms = ($ts - .timestamp) * 1000' \
   "$JSON_LOG" > "${JSON_LOG}.tmp" && mv "${JSON_LOG}.tmp" "$JSON_LOG"

# Nettoyage
rm -f health.json *.png

log "📊 Monitoring complet terminé"
log "📁 Logs: $LOG_FILE"
log "📊 Métriques: $JSON_LOG"

# Alerting si échecs multiples
if [ "$failed_tests" -gt 2 ]; then
    error "🚨 ALERTE: Trop d'échecs ($failed_tests)"
    exit 1
fi

log "✅ Monitoring OK - Service stable"