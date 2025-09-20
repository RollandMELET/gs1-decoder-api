#!/bin/bash
# Script de monitoring complet tous endpoints

set -e

API_URL="https://gs1-decoder-api.rorworld.eu"
LOG_FILE="monitor-endpoints.log"
JSON_LOG="endpoints-metrics.json"
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

# Initialiser JSON endpoints
echo "{\"timestamp\": $TIMESTAMP, \"endpoints\": {}}" > "$JSON_LOG"

add_endpoint_metric() {
    local endpoint="$1"
    local status="$2"
    local response_time="$3"
    local details="$4"

    jq --arg ep "$endpoint" --arg st "$status" --argjson rt "$response_time" --arg det "$details" \
       '.endpoints[$ep] = {"status": $st, "response_time_ms": $rt, "details": $det}' \
       "$JSON_LOG" > "${JSON_LOG}.tmp" && mv "${JSON_LOG}.tmp" "$JSON_LOG"
}

log "🔗 === MONITORING TOUS ENDPOINTS ==="

# 1. ENDPOINT /health
log "🏥 Test endpoint /health..."
health_start=$(date +%s%N)
health_response=$(curl -s -w "%{http_code}" "$API_URL/health" -o health_response.json || echo "000")
health_end=$(date +%s%N)
health_time=$(( (health_end - health_start) / 1000000 ))

if [ "$health_response" = "200" ]; then
    api_version=$(jq -r '.capabilities.api_version' health_response.json 2>/dev/null || echo "unknown")
    supported_codes_count=$(jq '.capabilities.supported_codes | length' health_response.json 2>/dev/null || echo "0")

    log "✅ /health: ${health_time}ms (version: $api_version, codes: $supported_codes_count)"
    add_endpoint_metric "health" "success" "$health_time" "version=$api_version,codes=$supported_codes_count"
else
    error "❌ /health échoué (code: $health_response)"
    add_endpoint_metric "health" "failed" 0 "error_code=$health_response"
fi

# 2. ENDPOINT /generate/ (déjà testé partiellement)
log "🎨 Test endpoint /generate/ (échantillon)..."
generate_start=$(date +%s%N)
generate_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)03760423190005", "barcode_format": "gs1_datamatrix"}' \
  -o generate_test.png || echo "000")
generate_end=$(date +%s%N)
generate_time=$(( (generate_end - generate_start) / 1000000 ))

if [ "$generate_response" = "200" ]; then
    generate_size=$(stat -c%s generate_test.png 2>/dev/null || stat -f%z generate_test.png 2>/dev/null)
    log "✅ /generate/: ${generate_time}ms (taille: ${generate_size} bytes)"
    add_endpoint_metric "generate" "success" "$generate_time" "test_file_size=$generate_size"
    rm -f generate_test.png
else
    error "❌ /generate/ échoué (code: $generate_response)"
    add_endpoint_metric "generate" "failed" 0 "error_code=$generate_response"
fi

# 3. ENDPOINT /parse/
log "📊 Test endpoint /parse/..."
parse_start=$(date +%s%N)
parse_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/parse/" \
  -H "Content-Type: application/json" \
  -d '{"raw_data": "(01)03760423190005(17)250910", "verbose": false}' \
  -o parse_response.json || echo "000")
parse_end=$(date +%s%N)
parse_time=$(( (parse_end - parse_start) / 1000000 ))

if [ "$parse_response" = "200" ]; then
    parse_success=$(jq -r '.success' parse_response.json 2>/dev/null || echo "false")
    barcodes_count=$(jq '.barcodes | length' parse_response.json 2>/dev/null || echo "0")

    if [ "$parse_success" = "true" ] && [ "$barcodes_count" -gt "0" ]; then
        log "✅ /parse/: ${parse_time}ms (barcodes: $barcodes_count)"
        add_endpoint_metric "parse" "success" "$parse_time" "barcodes_parsed=$barcodes_count"
    else
        warn "⚠️ /parse/ réponse invalide"
        add_endpoint_metric "parse" "invalid_response" "$parse_time" "success=$parse_success"
    fi
else
    error "❌ /parse/ échoué (code: $parse_response)"
    add_endpoint_metric "parse" "failed" 0 "error_code=$parse_response"
fi

# 4. ENDPOINT /decode/ (test avec image fake)
log "🔍 Test endpoint /decode/..."

# Créer une image fake pour test
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==" | base64 -d > fake_test.png

decode_start=$(date +%s%N)
decode_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/decode/" \
  -F "file=@fake_test.png" \
  -F "verbose=false" \
  -o decode_response.json || echo "000")
decode_end=$(date +%s%N)
decode_time=$(( (decode_end - decode_start) / 1000000 ))

if [ "$decode_response" = "200" ]; then
    decode_success=$(jq -r '.success' decode_response.json 2>/dev/null || echo "false")
    log "✅ /decode/: ${decode_time}ms (success: $decode_success)"
    add_endpoint_metric "decode" "success" "$decode_time" "response_valid=$decode_success"
else
    error "❌ /decode/ échoué (code: $decode_response)"
    add_endpoint_metric "decode" "failed" 0 "error_code=$decode_response"
fi

# SYNTHÈSE ENDPOINTS
log "📋 === SYNTHÈSE ENDPOINTS ==="

endpoints_tested=$(jq '.endpoints | length' "$JSON_LOG")
endpoints_success=$(jq '[.endpoints[] | select(.status == "success")] | length' "$JSON_LOG")

log "📊 Endpoints: $endpoints_success/$endpoints_tested fonctionnels"

# Validation seuils performance endpoints
log "⏱️ Seuils performance endpoints:"

endpoint_thresholds() {
    local endpoint="$1"
    local max_time="$2"

    local actual_time=$(jq -r ".endpoints.$endpoint.response_time_ms" "$JSON_LOG" 2>/dev/null || echo "0")

    if [ "$actual_time" != "null" ] && [ "$actual_time" != "0" ]; then
        if [ "$actual_time" -le "$max_time" ]; then
            log "  ✅ /$endpoint: ${actual_time}ms (< ${max_time}ms)"
        else
            warn "  ⚠️ /$endpoint: ${actual_time}ms (> ${max_time}ms)"
        fi
    fi
}

endpoint_thresholds "health" 1000
endpoint_thresholds "generate" 5000
endpoint_thresholds "parse" 1000
endpoint_thresholds "decode" 10000

# Finaliser JSON
jq --arg date "$DATE" --argjson ts "$TIMESTAMP" \
   '.completed_at = $date | .duration_total_ms = ($ts - .timestamp) * 1000' \
   "$JSON_LOG" > "${JSON_LOG}.tmp" && mv "${JSON_LOG}.tmp" "$JSON_LOG"

# Nettoyage
rm -f health_response.json parse_response.json decode_response.json fake_test.png

log "✅ Monitoring endpoints terminé"
log "📁 Logs: $LOG_FILE"
log "📊 Métriques: $JSON_LOG"

# Exit code basé sur succès critiques
critical_ok=$(jq -r '.endpoints.health.status == "success" and .endpoints.generate.status == "success"' "$JSON_LOG")

if [ "$critical_ok" = "true" ]; then
    log "✅ Endpoints critiques OK"
    exit 0
else
    error "❌ Endpoints critiques défaillants"
    exit 1
fi