#!/bin/bash
# Script de monitoring de l'API production pour surveiller les métriques GS1

set -e

API_URL="https://gs1-decoder-api.rorworld.eu"
LOG_FILE="production-monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

# Test de santé
log "🏥 Test de santé API..."
health_response=$(curl -s -w "%{http_code}" "$API_URL/health" -o health.json || echo "000")

if [ "$health_response" = "200" ]; then
    log "✅ API accessible"

    # Vérifier capacités bwip-js
    bwipjs_status=$(jq -r '.capabilities.generators.bwipjs' health.json 2>/dev/null || echo "null")
    if [ "$bwipjs_status" = "true" ]; then
        log "✅ bwip-js disponible"
    else
        warn "⚠️ bwip-js non disponible"
    fi

    # Vérifier support GS1 DataMatrix
    gs1_support=$(jq -r '.capabilities.supported_codes[] | select(. == "GS1 DataMatrix")' health.json 2>/dev/null || echo "")
    if [ -n "$gs1_support" ]; then
        log "✅ GS1 DataMatrix supporté"
    else
        error "❌ GS1 DataMatrix non supporté"
    fi
else
    error "❌ API non accessible (code: $health_response)"
    exit 1
fi

# Test de génération GS1 simple
log "🧪 Test génération GS1 simple..."
simple_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)12345678901234", "barcode_format": "gs1_datamatrix"}' \
  -o simple_test.png || echo "000")

if [ "$simple_response" = "200" ]; then
    simple_size=$(stat -c%s simple_test.png 2>/dev/null || stat -f%z simple_test.png 2>/dev/null)
    log "✅ Génération simple réussie (taille: ${simple_size} bytes)"

    # Vérifier taille optimisée
    if [ "$simple_size" -ge 500 ] && [ "$simple_size" -le 700 ]; then
        log "✅ Taille optimisée conforme (500-700 bytes)"
    else
        warn "⚠️ Taille non optimisée: ${simple_size} bytes (attendu: 500-700)"
    fi

    rm -f simple_test.png
else
    error "❌ Génération simple échouée (code: $simple_response)"
fi

# Test de génération GS1 expert
log "🧪 Test génération GS1 expert..."
expert_data='(01)03760423190005(11)250910(3100)012000(21)0000019C(90)7391023(93)DHA(94)UP(95)ENVELOPPE_NUE_4UF'
expert_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d "{\"data\": \"$expert_data\", \"barcode_format\": \"gs1_datamatrix\"}" \
  -o expert_test.png || echo "000")

if [ "$expert_response" = "200" ]; then
    expert_size=$(stat -c%s expert_test.png 2>/dev/null || stat -f%z expert_test.png 2>/dev/null)
    log "✅ Génération expert réussie (taille: ${expert_size} bytes)"

    # Vérifier taille optimisée
    if [ "$expert_size" -ge 650 ] && [ "$expert_size" -le 800 ]; then
        log "✅ Taille expert optimisée conforme (650-800 bytes)"
    else
        warn "⚠️ Taille expert non optimisée: ${expert_size} bytes (attendu: 650-800)"
    fi

    rm -f expert_test.png
else
    error "❌ Génération expert échouée (code: $expert_response)"
fi

# Test temps de réponse
log "⏱️ Test temps de réponse..."
start_time=$(date +%s%N)
response_time_test=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)12345678901234", "barcode_format": "gs1_datamatrix"}' \
  -o /dev/null || echo "000")
end_time=$(date +%s%N)

if [ "$response_time_test" = "200" ]; then
    response_time_ms=$(( (end_time - start_time) / 1000000 ))
    log "✅ Temps de réponse: ${response_time_ms}ms"

    if [ "$response_time_ms" -lt 2000 ]; then
        log "✅ Performance conforme (< 2s)"
    else
        warn "⚠️ Performance dégradée: ${response_time_ms}ms (attendu: < 2000ms)"
    fi
else
    error "❌ Test temps de réponse échoué"
fi

# Vérification non-régression autres formats
log "🛡️ Test non-régression autres formats..."

# Test QR Code
qr_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "Test QR Code", "barcode_format": "qr_code"}' \
  -o /dev/null || echo "000")

if [ "$qr_response" = "200" ]; then
    log "✅ QR Code fonctionne"
else
    warn "⚠️ QR Code défaillant (code: $qr_response)"
fi

# Test DataMatrix standard
dm_response=$(curl -s -w "%{http_code}" -X POST \
  "$API_URL/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "Standard DataMatrix", "barcode_format": "datamatrix"}' \
  -o /dev/null || echo "000")

if [ "$dm_response" = "200" ]; then
    log "✅ DataMatrix standard fonctionne"
else
    warn "⚠️ DataMatrix standard défaillant (code: $dm_response)"
fi

# Nettoyage
rm -f health.json

# Résumé
echo ""
log "📊 Monitoring terminé - voir $LOG_FILE pour l'historique"

# Si script appelé avec --alert, vérifier si alerte nécessaire
if [ "$1" = "--alert" ]; then
    # Vérifier les erreurs récentes
    recent_errors=$(grep -c "ERROR" "$LOG_FILE" | tail -n 10 || echo "0")
    if [ "$recent_errors" -gt 3 ]; then
        error "🚨 ALERTE: Trop d'erreurs récentes ($recent_errors)"
        # Ici on pourrait envoyer une notification
        # curl -X POST $WEBHOOK_URL -d '{"text":"🚨 API GS1 en difficulté"}'
        exit 1
    fi
fi