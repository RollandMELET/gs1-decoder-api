#!/bin/bash

# Test du GS1 DataMatrix avec FNC1 correctement ajouté
# Ce script va tester la correction apportée suite au feedback de l'expert GS1

# Configuration
API_URL="https://gs1-decoder-api.rorworld.eu"
GS1_DATA="(01)03760423190005(11)250326(3100)015500(21)0000000D(90)7391023(93)DHA(94)UP(95)ENVELOPPE_NUE_4UF"
OUTPUT_FILE="gs1_datamatrix_avec_fnc1.png"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Test GS1 DataMatrix avec FNC1 corrigé${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Nettoyage
rm -f "$OUTPUT_FILE"

echo -e "${BLUE}📋 Données à encoder:${NC}"
echo "   $GS1_DATA"
echo ""

# Attendre que le déploiement soit effectif
echo -e "${YELLOW}⏳ Attente du déploiement (10 secondes)...${NC}"
sleep 10

# Génération du GS1 DataMatrix
echo -e "${BLUE}🔨 Génération du GS1 DataMatrix avec FNC1...${NC}"

HTTP_CODE=$(curl -X POST "${API_URL}/generate/" \
    -H "Content-Type: application/json" \
    -d "{
        \"data\": \"$GS1_DATA\",
        \"format\": \"gs1-datamatrix\",
        \"image_format\": \"png\"
    }" \
    --output "$OUTPUT_FILE" \
    --write-out "%{http_code}" \
    --silent)

if [ "$HTTP_CODE" != "200" ]; then
    echo -e "${RED}❌ Erreur génération (HTTP $HTTP_CODE)${NC}"
    if [ -f "$OUTPUT_FILE" ]; then
        echo "Réponse du serveur:"
        cat "$OUTPUT_FILE"
    fi
    exit 1
fi

if [ ! -f "$OUTPUT_FILE" ] || [ ! -s "$OUTPUT_FILE" ]; then
    echo -e "${RED}❌ Fichier PNG non généré${NC}"
    exit 1
fi

FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
echo -e "${GREEN}✅ GS1 DataMatrix généré (${FILE_SIZE} bytes)${NC}"
echo ""

# Test de décodage pour validation
echo -e "${BLUE}🔍 Validation par décodage...${NC}"

DECODE_RESPONSE=$(curl -X POST "${API_URL}/decode/" \
    -F "file=@$OUTPUT_FILE" \
    -F "verbose=true" \
    --silent)

# Analyser la réponse
SUCCESS=$(echo "$DECODE_RESPONSE" | jq -r '.success' 2>/dev/null)
IS_GS1=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.is_gs1' 2>/dev/null)
FORMAT=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.format' 2>/dev/null)
CONTAINS_FNC1=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.characteristics.contains_fnc1' 2>/dev/null)

echo "📊 Résultats du décodage:"
echo "   Décodage réussi: $SUCCESS"
echo "   Format détecté: $FORMAT"
echo "   Est GS1: $IS_GS1"
echo "   Contient FNC1: $CONTAINS_FNC1"
echo ""

# Validation finale
echo -e "${BLUE}🎯 Validation finale:${NC}"

if [ "$SUCCESS" = "true" ] && [ "$IS_GS1" = "true" ] && [ "$FORMAT" = "GS1 DataMatrix" ] && [ "$CONTAINS_FNC1" = "true" ]; then
    echo -e "${GREEN}🎉 SUCCÈS COMPLET!${NC}"
    echo -e "${GREEN}   ✅ Génération réussie${NC}"
    echo -e "${GREEN}   ✅ Format GS1 DataMatrix confirmé${NC}"
    echo -e "${GREEN}   ✅ FNC1 détecté${NC}"
    echo -e "${GREEN}   ✅ Décodage correct${NC}"
    echo ""
    echo -e "${GREEN}🏆 Le DataMatrix devrait maintenant être reconnu${NC}"
    echo -e "${GREEN}    comme un vrai GS1 DataMatrix par les scanners professionnels!${NC}"
else
    echo -e "${YELLOW}⚠️  Résultats partiels:${NC}"
    [ "$SUCCESS" != "true" ] && echo -e "${RED}   ❌ Décodage échoué${NC}"
    [ "$IS_GS1" != "true" ] && echo -e "${RED}   ❌ Pas reconnu comme GS1${NC}"
    [ "$FORMAT" != "GS1 DataMatrix" ] && echo -e "${RED}   ❌ Format incorrect: $FORMAT${NC}"
    [ "$CONTAINS_FNC1" != "true" ] && echo -e "${RED}   ❌ FNC1 non détecté${NC}"
fi

echo ""
echo -e "${BLUE}📁 Fichier généré: $OUTPUT_FILE${NC}"
echo ""

echo -e "${BLUE}🧪 Test avec l'expert GS1:${NC}"
echo "   Envoyez le fichier $OUTPUT_FILE à l'expert pour validation"
echo ""

echo -e "${BLUE}📋 Résumé des corrections apportées:${NC}"
echo "   • Ajout explicite du caractère FNC1 (chr(232)) au début"
echo "   • Encodage latin-1 pour supporter le caractère spécial"
echo "   • Distinction claire entre DataMatrix et GS1 DataMatrix"
echo "   • Gestion du FNC1 dans les deux moteurs (pylibdmtx et treepoem)"