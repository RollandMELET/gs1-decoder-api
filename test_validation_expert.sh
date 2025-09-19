#!/bin/bash

# Script de validation finale pour expert GS1
# Génère un fichier test propre et vérifie qu'il utilise bwip-js

API_URL="https://gs1-decoder-api.rorworld.eu"
GS1_DATA="(01)03760423190005(11)250326(3100)015500(21)0000000D(90)7391023(93)DHA(94)UP(95)ENVELOPPE_NUE_4UF"
TEST_FILE="GS1_DATAMATRIX_VALIDATION_EXPERT.png"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  VALIDATION FINALE EXPERT GS1${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Nettoyage
rm -f "$TEST_FILE"

# Vérification infrastructure
echo -e "${BLUE}📋 Vérification infrastructure...${NC}"
HEALTH_RESPONSE=$(curl -s "${API_URL}/health")

BWIPJS_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.capabilities.generators.bwipjs' 2>/dev/null)
TREEPOEM_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.capabilities.generators.treepoem' 2>/dev/null)
NODEJS_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.capabilities.generators.nodejs' 2>/dev/null)

echo "   🔧 bwip-js: $BWIPJS_STATUS"
echo "   🌳 treepoem: $TREEPOEM_STATUS"
echo "   📦 Node.js: $NODEJS_STATUS"

if [ "$BWIPJS_STATUS" != "true" ]; then
    echo -e "${YELLOW}   ⚠️  bwip-js non disponible - utilisation treepoem/pylibdmtx${NC}"
else
    echo -e "${GREEN}   ✅ bwip-js disponible - priorité 1 dans architecture hybride${NC}"
fi

echo ""

# Génération du fichier test
echo -e "${BLUE}🎯 Génération GS1 DataMatrix pour validation expert...${NC}"
echo "   Données: $GS1_DATA"
echo "   Format: gs1-datamatrix (avec FNC1)"
echo "   Sortie: $TEST_FILE"
echo ""

HTTP_CODE=$(curl -X POST "${API_URL}/generate/" \
    -H "Content-Type: application/json" \
    -d "{
        \"data\": \"$GS1_DATA\",
        \"format\": \"gs1-datamatrix\",
        \"image_format\": \"png\"
    }" \
    --output "$TEST_FILE" \
    --write-out "%{http_code}" \
    --silent)

if [ "$HTTP_CODE" != "200" ]; then
    echo -e "${RED}❌ Erreur génération (HTTP $HTTP_CODE)${NC}"
    if [ -f "$TEST_FILE" ]; then
        echo "Contenu erreur:"
        cat "$TEST_FILE"
    fi
    exit 1
fi

if [ ! -f "$TEST_FILE" ] || [ ! -s "$TEST_FILE" ]; then
    echo -e "${RED}❌ Fichier non généré ou vide${NC}"
    exit 1
fi

FILE_SIZE=$(stat -f%z "$TEST_FILE" 2>/dev/null || stat -c%s "$TEST_FILE" 2>/dev/null)
echo -e "${GREEN}✅ Fichier généré: $TEST_FILE (${FILE_SIZE} bytes)${NC}"
echo ""

# Analyse de la taille pour déterminer le générateur utilisé
echo -e "${BLUE}🔍 Analyse du générateur utilisé...${NC}"

if [ "$FILE_SIZE" -eq 32089 ]; then
    echo -e "${GREEN}   🎉 Taille 32,089 bytes = bwip-js (OPTIMAL pour GS1)${NC}"
    GENERATOR_USED="bwip-js"
elif [ "$FILE_SIZE" -eq 50283 ]; then
    echo -e "${YELLOW}   ⚠️  Taille 50,283 bytes = pylibdmtx (fallback - pas de FNC1)${NC}"
    GENERATOR_USED="pylibdmtx"
else
    echo -e "${BLUE}   📊 Taille ${FILE_SIZE} bytes = générateur non identifié${NC}"
    GENERATOR_USED="inconnu"
fi

echo ""

# Test de décodage pour information
echo -e "${BLUE}🧪 Test décodage informatif...${NC}"

DECODE_RESPONSE=$(curl -X POST "${API_URL}/decode/" \
    -F "file=@$TEST_FILE" \
    -F "verbose=true" \
    --silent)

SUCCESS=$(echo "$DECODE_RESPONSE" | jq -r '.success' 2>/dev/null)

if [ "$SUCCESS" = "true" ]; then
    FORMAT_DETECTED=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.format' 2>/dev/null)
    IS_GS1=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.is_gs1' 2>/dev/null)
    CONTAINS_FNC1=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.characteristics.contains_fnc1' 2>/dev/null)

    echo "   📊 Résultat décodage ZXing:"
    echo "      Format détecté: $FORMAT_DETECTED"
    echo "      Est GS1: $IS_GS1"
    echo "      Contient FNC1: $CONTAINS_FNC1"

    if [ "$IS_GS1" = "true" ] && [ "$FORMAT_DETECTED" = "GS1 DataMatrix" ]; then
        echo -e "${GREEN}   ✅ ZXing reconnaît comme GS1 DataMatrix${NC}"
        ZXING_RESULT="CONFORME"
    else
        echo -e "${YELLOW}   ⚠️  ZXing ne reconnaît pas comme GS1 DataMatrix${NC}"
        ZXING_RESULT="NON_CONFORME"
    fi
else
    echo -e "${RED}   ❌ Décodage ZXing échoué${NC}"
    ZXING_RESULT="ECHEC"
fi

echo ""

# Résumé final pour l'expert
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  RÉSUMÉ POUR VALIDATION EXPERT GS1${NC}"
echo -e "${BLUE}============================================${NC}"

echo -e "${BLUE}📁 Fichier à valider:${NC} $TEST_FILE"
echo -e "${BLUE}📊 Générateur utilisé:${NC} $GENERATOR_USED"
echo -e "${BLUE}📏 Taille fichier:${NC} ${FILE_SIZE} bytes"
echo -e "${BLUE}🔍 Décodage ZXing:${NC} $ZXING_RESULT"

echo ""

echo -e "${BLUE}🎯 Instructions pour l'expert:${NC}"
echo "   1. Scannez $TEST_FILE avec scanner GS1 professionnel"
echo "   2. Vérifiez identifiant AIM dans la réponse:"
echo "      • ]d2 = GS1 DataMatrix CONFORME (avec FNC1) ✅"
echo "      • ]d1 = DataMatrix standard (sans FNC1) ❌"
echo "   3. Confirmez que l'application affiche 'GS1 DataMatrix'"

echo ""

echo -e "${BLUE}📋 Spécifications techniques du fichier:${NC}"
echo "   • Format: gs1-datamatrix avec parsefnc=true"
if [ "$GENERATOR_USED" = "bwip-js" ]; then
    echo "   • Générateur: bwip-js (backend BWIPP natif)"
    echo "   • Conformité: OPTIMALE selon note technique expert"
elif [ "$GENERATOR_USED" = "pylibdmtx" ]; then
    echo "   • Générateur: pylibdmtx (fallback - limitations FNC1)"
    echo "   • Conformité: LIMITÉE (pas de FNC1 automatique)"
fi
echo "   • Données: Format parenthèses avec 8 Application Identifiers"
echo "   • Structure: AI fixes + AI variables avec séparateurs GS"

echo ""

if [ "$GENERATOR_USED" = "bwip-js" ]; then
    echo -e "${GREEN}🏆 CONFIANCE ÉLEVÉE: Ce fichier devrait être reconnu${NC}"
    echo -e "${GREEN}    comme un vrai GS1 DataMatrix par l'expert !${NC}"
else
    echo -e "${YELLOW}⚠️  CONFIANCE MODÉRÉE: Fichier généré par fallback${NC}"
    echo -e "${YELLOW}    Peut ne pas avoir le FNC1 requis pour conformité GS1${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Fichier prêt pour validation !${NC}"