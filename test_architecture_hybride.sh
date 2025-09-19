#!/bin/bash

# Test complet de l'architecture hybride GS1 DataMatrix
# Vérifie que nous n'avons pas de régressions et que GS1 fonctionne

API_URL="https://gs1-decoder-api.rorworld.eu"
GS1_DATA="(01)03760423190005(11)250326(3100)015500(21)0000000D(90)7391023(93)DHA(94)UP(95)ENVELOPPE_NUE_4UF"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Test Architecture Hybride GS1 DataMatrix${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Nettoyage initial
rm -f test_*.png

# Fonction de test générique
test_format() {
    local data="$1"
    local format="$2"
    local description="$3"
    local filename="$4"

    echo -e "${BLUE}🧪 Test: $description${NC}"
    echo "   Données: $data"
    echo "   Format: $format"

    # Génération
    HTTP_CODE=$(curl -X POST "${API_URL}/generate/" \
        -H "Content-Type: application/json" \
        -d "{
            \"data\": \"$data\",
            \"format\": \"$format\",
            \"image_format\": \"png\"
        }" \
        --output "$filename" \
        --write-out "%{http_code}" \
        --silent)

    if [ "$HTTP_CODE" != "200" ]; then
        echo -e "${RED}   ❌ Génération échouée (HTTP $HTTP_CODE)${NC}"
        return 1
    fi

    if [ ! -f "$filename" ] || [ ! -s "$filename" ]; then
        echo -e "${RED}   ❌ Fichier non généré${NC}"
        return 1
    fi

    FILE_SIZE=$(stat -f%z "$filename" 2>/dev/null || stat -c%s "$filename" 2>/dev/null)
    echo -e "${GREEN}   ✅ Généré avec succès (${FILE_SIZE} bytes)${NC}"

    # Test de décodage
    DECODE_RESPONSE=$(curl -X POST "${API_URL}/decode/" \
        -F "file=@$filename" \
        -F "verbose=true" \
        --silent)

    SUCCESS=$(echo "$DECODE_RESPONSE" | jq -r '.success' 2>/dev/null)
    if [ "$SUCCESS" = "true" ]; then
        FORMAT_DETECTED=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.format' 2>/dev/null)
        IS_GS1=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.is_gs1' 2>/dev/null)
        CONTAINS_FNC1=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.characteristics.contains_fnc1' 2>/dev/null)

        echo -e "${GREEN}   ✅ Décodé avec succès${NC}"
        echo "      Format détecté: $FORMAT_DETECTED"
        echo "      Est GS1: $IS_GS1"
        echo "      Contient FNC1: $CONTAINS_FNC1"

        # Validation spéciale pour GS1
        if [ "$format" = "gs1-datamatrix" ]; then
            if [ "$IS_GS1" = "true" ] && [ "$CONTAINS_FNC1" = "true" ]; then
                echo -e "${GREEN}   🎉 GS1 DataMatrix CONFORME!${NC}"
                return 0
            else
                echo -e "${YELLOW}   ⚠️  GS1 DataMatrix non-conforme${NC}"
                return 2
            fi
        fi
        return 0
    else
        echo -e "${RED}   ❌ Décodage échoué${NC}"
        echo "      Erreur: $(echo "$DECODE_RESPONSE" | jq -r '.detail' 2>/dev/null)"
        return 1
    fi
}

# Attendre déploiement
echo -e "${YELLOW}⏳ Attente déploiement (15 secondes)...${NC}"
sleep 15

echo -e "${BLUE}📋 PLAN DE TESTS${NC}"
echo "1. DataMatrix standard (vérification non-régression)"
echo "2. QR Code standard (vérification non-régression)"
echo "3. Code 128 standard (vérification non-régression)"
echo "4. GS1 DataMatrix (nouvelle architecture)"
echo ""

# Tests de non-régression
echo -e "${BLUE}=== TESTS DE NON-RÉGRESSION ===${NC}"

# Test 1: DataMatrix standard
test_format "Hello World Standard" "datamatrix" "DataMatrix Standard" "test_datamatrix_std.png"
RESULT_STD=$?

# Test 2: QR Code
test_format "Hello QR Code" "qrcode" "QR Code Standard" "test_qrcode_std.png"
RESULT_QR=$?

# Test 3: Code 128
test_format "HELLO128" "code128" "Code 128 Standard" "test_code128_std.png"
RESULT_128=$?

echo ""

# Test principal: GS1 DataMatrix avec nouvelle architecture
echo -e "${BLUE}=== TEST PRINCIPALE: GS1 DATAMATRIX ===${NC}"

test_format "$GS1_DATA" "gs1-datamatrix" "GS1 DataMatrix (Architecture Hybride)" "test_gs1_hybrid.png"
RESULT_GS1=$?

echo ""

# Résumé des résultats
echo -e "${BLUE}=== RÉSUMÉ DES TESTS ===${NC}"

echo -e "DataMatrix Standard:    $([ $RESULT_STD -eq 0 ] && echo -e "${GREEN}✅ OK${NC}" || echo -e "${RED}❌ ÉCHEC${NC}")"
echo -e "QR Code Standard:       $([ $RESULT_QR -eq 0 ] && echo -e "${GREEN}✅ OK${NC}" || echo -e "${RED}❌ ÉCHEC${NC}")"
echo -e "Code 128 Standard:      $([ $RESULT_128 -eq 0 ] && echo -e "${GREEN}✅ OK${NC}" || echo -e "${RED}❌ ÉCHEC${NC}")"

if [ $RESULT_GS1 -eq 0 ]; then
    echo -e "GS1 DataMatrix:         ${GREEN}🎉 CONFORME GS1${NC}"
elif [ $RESULT_GS1 -eq 2 ]; then
    echo -e "GS1 DataMatrix:         ${YELLOW}⚠️  FONCTIONNEL mais non-conforme GS1${NC}"
else
    echo -e "GS1 DataMatrix:         ${RED}❌ ÉCHEC${NC}"
fi

echo ""

# Conclusions
if [ $RESULT_STD -eq 0 ] && [ $RESULT_QR -eq 0 ] && [ $RESULT_128 -eq 0 ]; then
    echo -e "${GREEN}✅ AUCUNE RÉGRESSION détectée sur les formats existants${NC}"
else
    echo -e "${RED}❌ RÉGRESSIONS détectées - architecture instable${NC}"
    exit 1
fi

if [ $RESULT_GS1 -eq 0 ]; then
    echo -e "${GREEN}🎉 SUCCÈS COMPLET: GS1 DataMatrix conforme + zéro régression${NC}"
    echo -e "${GREEN}   Prêt pour validation expert GS1${NC}"
elif [ $RESULT_GS1 -eq 2 ]; then
    echo -e "${YELLOW}⚠️  SUCCÈS PARTIEL: Architecture stable mais FNC1 à corriger${NC}"
else
    echo -e "${RED}❌ GS1 DataMatrix non-fonctionnel${NC}"
fi

echo ""
echo -e "${BLUE}📁 Fichiers générés:${NC}"
echo "   test_datamatrix_std.png (DataMatrix standard)"
echo "   test_qrcode_std.png (QR Code standard)"
echo "   test_code128_std.png (Code 128 standard)"
echo "   test_gs1_hybrid.png (GS1 DataMatrix hybride)"
echo ""

echo -e "${BLUE}🧪 Prochaine étape:${NC}"
echo "   Envoyer test_gs1_hybrid.png à l'expert GS1 pour validation"