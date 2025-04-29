#!/bin/bash

# Configuration
URL="https://gs1-decoder-api.rorworld.eu"
IMAGE_PATH="/Users/rollandmelet/Développement/Projets/gs1-decoder-api/imagetest.jpg"

# 1. Healthcheck
echo "🔎 Test de santé..."
curl --fail --silent --show-error "${URL}/health" || { echo "❌ Healthcheck échoué."; exit 1; }
echo "✅ Healthcheck réussi."

# 2. Scan simple
echo "📷 Scan simple..."
curl --fail --silent --show-error -X POST "${URL}/decode/" \
    -F "file=@${IMAGE_PATH}" \
    -F "verbose=false" \
    || { echo "❌ Scan simple échoué."; exit 1; }
echo "✅ Scan simple réussi."

# 3. Scan verbose
echo "📷 Scan verbose..."
curl --fail --silent --show-error -X POST "${URL}/decode/" \
    -F "file=@${IMAGE_PATH}" \
    -F "verbose=true" \
    || { echo "❌ Scan verbose échoué."; exit 1; }
echo "✅ Scan verbose réussi."

echo "🎉 Tous les tests sont OK."
