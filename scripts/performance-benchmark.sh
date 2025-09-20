#!/bin/bash
# Script de benchmark performance tous formats

set -e

API_URL="https://gs1-decoder-api.rorworld.eu"
LOG_FILE="performance-benchmark.log"
JSON_LOG="performance-metrics.json"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
TIMESTAMP=$(date +%s)

# Configuration
ITERATIONS=5
CONCURRENT_REQUESTS=3

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
echo "{\"timestamp\": $TIMESTAMP, \"config\": {\"iterations\": $ITERATIONS, \"concurrent\": $CONCURRENT_REQUESTS}, \"benchmarks\": {}}" > "$JSON_LOG"

benchmark_format() {
    local format="$1"
    local data="$2"
    local description="$3"
    local max_time="$4"

    log "📈 Benchmark $description..."

    local times=()
    local sizes=()
    local success_count=0

    for i in $(seq 1 $ITERATIONS); do
        local start_time=$(date +%s%N)

        local response=$(curl -s -w "%{http_code}" -X POST \
          "$API_URL/generate/" \
          -H "Content-Type: application/json" \
          -d "{\"data\": \"$data\", \"barcode_format\": \"$format\"}" \
          -o "benchmark_${format}_${i}.png" || echo "000")

        local end_time=$(date +%s%N)
        local response_time=$(( (end_time - start_time) / 1000000 ))

        if [ "$response" = "200" ]; then
            local file_size=$(stat -c%s "benchmark_${format}_${i}.png" 2>/dev/null || stat -f%z "benchmark_${format}_${i}.png" 2>/dev/null)
            times+=($response_time)
            sizes+=($file_size)
            success_count=$((success_count + 1))
            info "  Iteration $i: ${response_time}ms, ${file_size} bytes"
        else
            warn "  Iteration $i: FAILED (code: $response)"
            times+=(9999)  # Échec
            sizes+=(0)
        fi

        rm -f "benchmark_${format}_${i}.png"
        sleep 0.5  # Éviter surcharge
    done

    # Calculer statistiques
    if [ $success_count -gt 0 ]; then
        local min_time=$(printf '%s\n' "${times[@]}" | sort -n | head -1)
        local max_time_actual=$(printf '%s\n' "${times[@]}" | sort -n | tail -1)
        local avg_time=$(( ($(printf '%s+' "${times[@]}" | sed 's/+$//')) / ${#times[@]} ))

        local min_size=$(printf '%s\n' "${sizes[@]}" | sort -n | head -1)
        local max_size=$(printf '%s\n' "${sizes[@]}" | sort -n | tail -1)
        local avg_size=$(( ($(printf '%s+' "${sizes[@]}" | sed 's/+$//')) / ${#sizes[@]} ))

        log "📊 $description - Résultats:"
        log "  ⏱️ Temps: min=${min_time}ms, avg=${avg_time}ms, max=${max_time_actual}ms"
        log "  📏 Taille: min=${min_size}b, avg=${avg_size}b, max=${max_size}b"
        log "  ✅ Succès: $success_count/$ITERATIONS"

        # Validation seuils
        if [ "$avg_time" -le "$max_time" ]; then
            log "  ✅ Performance CONFORME (< ${max_time}ms)"
            local status="success"
        else
            warn "  ⚠️ Performance DÉGRADÉE (> ${max_time}ms)"
            local status="degraded"
        fi

        # Ajouter au JSON
        jq --arg fmt "$format" --argjson min_t "$min_time" --argjson avg_t "$avg_time" --argjson max_t "$max_time_actual" \
           --argjson min_s "$min_size" --argjson avg_s "$avg_size" --argjson max_s "$max_size" \
           --argjson succ "$success_count" --argjson total "$ITERATIONS" --arg st "$status" \
           '.benchmarks[$fmt] = {
               "time_ms": {"min": $min_t, "avg": $avg_t, "max": $max_t},
               "size_bytes": {"min": $min_s, "avg": $avg_s, "max": $max_s},
               "success_rate": ($succ / $total),
               "status": $st
           }' \
           "$JSON_LOG" > "${JSON_LOG}.tmp" && mv "${JSON_LOG}.tmp" "$JSON_LOG"
    else
        error "  ❌ Tous tests échoués"
        jq --arg fmt "$format" \
           '.benchmarks[$fmt] = {"status": "failed", "success_rate": 0}' \
           "$JSON_LOG" > "${JSON_LOG}.tmp" && mv "${JSON_LOG}.tmp" "$JSON_LOG"
    fi
}

# Benchmarks par format avec seuils différenciés
benchmark_format "gs1_datamatrix" "(01)03760423190005" "GS1 DataMatrix (CRITIQUE)" 2000
benchmark_format "qr_code" "Benchmark QR Test Data" "QR Code Standard" 5000
benchmark_format "datamatrix" "Benchmark DataMatrix Test" "DataMatrix Standard" 5000
benchmark_format "code_128" "BENCHMARK128" "Code 128 Standard" 3000

# Test concurrent (si activé)
if [ "$1" = "--concurrent" ]; then
    log "🚀 Test performance concurrent..."

    concurrent_start=$(date +%s%N)

    # Lancer requêtes concurrentes
    for i in $(seq 1 $CONCURRENT_REQUESTS); do
        {
            curl -s -X POST \
              "$API_URL/generate/" \
              -H "Content-Type: application/json" \
              -d '{"data": "(01)03760423190005", "barcode_format": "gs1_datamatrix"}' \
              -o "concurrent_${i}.png" &
        }
    done

    wait  # Attendre toutes les requêtes

    concurrent_end=$(date +%s%N)
    concurrent_time=$(( (concurrent_end - concurrent_start) / 1000000 ))

    log "🚀 Concurrent ($CONCURRENT_REQUESTS requêtes): ${concurrent_time}ms"

    # Vérifier résultats concurrent
    concurrent_success=0
    for i in $(seq 1 $CONCURRENT_REQUESTS); do
        if [ -f "concurrent_${i}.png" ] && [ -s "concurrent_${i}.png" ]; then
            concurrent_success=$((concurrent_success + 1))
        fi
        rm -f "concurrent_${i}.png"
    done

    log "✅ Concurrent success: $concurrent_success/$CONCURRENT_REQUESTS"

    # Ajouter au JSON
    jq --argjson conc_time "$concurrent_time" --argjson conc_succ "$concurrent_success" --argjson conc_total "$CONCURRENT_REQUESTS" \
       '.concurrent_test = {
           "total_time_ms": $conc_time,
           "success_count": $conc_succ,
           "total_requests": $conc_total,
           "success_rate": ($conc_succ / $conc_total)
       }' \
       "$JSON_LOG" > "${JSON_LOG}.tmp" && mv "${JSON_LOG}.tmp" "$JSON_LOG"
fi

# ANALYSE GLOBALE
log "📊 === ANALYSE PERFORMANCE GLOBALE ==="

# Statut critique GS1 DataMatrix
gs1_status=$(jq -r '.benchmarks.gs1_datamatrix.status' "$JSON_LOG" 2>/dev/null || echo "missing")
gs1_avg_time=$(jq -r '.benchmarks.gs1_datamatrix.time_ms.avg' "$JSON_LOG" 2>/dev/null || echo "0")

if [ "$gs1_status" = "success" ]; then
    log "✅ CRITIQUE: GS1 DataMatrix performance OK (avg: ${gs1_avg_time}ms)"
else
    error "🚨 CRITIQUE: GS1 DataMatrix performance DÉGRADÉE"
fi

# Synthèse formats standard
standard_formats=("qr_code" "datamatrix" "code_128")
standard_ok=0

for fmt in "${standard_formats[@]}"; do
    fmt_status=$(jq -r ".benchmarks.$fmt.status" "$JSON_LOG" 2>/dev/null || echo "missing")
    if [ "$fmt_status" = "success" ]; then
        standard_ok=$((standard_ok + 1))
    fi
done

log "📊 Formats standard: $standard_ok/${#standard_formats[@]} performants"

# Finaliser JSON avec résumé
jq --arg date "$DATE" \
   --argjson gs1_ok "$([ "$gs1_status" = "success" ] && echo true || echo false)" \
   --argjson std_ok "$standard_ok" \
   --argjson std_total "${#standard_formats[@]}" \
   '.summary = {
       "completed_at": $date,
       "gs1_datamatrix_ok": $gs1_ok,
       "standard_formats_ok": $std_ok,
       "standard_formats_total": $std_total,
       "overall_health": ($gs1_ok and ($std_ok > ($std_total / 2)))
   }' \
   "$JSON_LOG" > "${JSON_LOG}.tmp" && mv "${JSON_LOG}.tmp" "$JSON_LOG"

log "✅ Performance benchmark terminé"

# Exit code
if [ "$gs1_status" = "success" ]; then
    exit 0
else
    exit 1
fi