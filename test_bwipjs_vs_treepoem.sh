#!/bin/bash

# Test comparatif bwip-js vs treepoem pour GS1 DataMatrix
# Génère avec les deux solutions et compare les résultats

API_URL="https://gs1-decoder-api.rorworld.eu"
GS1_DATA_SIMPLE="(01)03760423190005(11)250326"
GS1_DATA_COMPLEX="(01)03760423190005(11)250326(3100)015500(21)0000000D(90)7391023(93)DHA(94)UP(95)ENVELOPPE_NUE_4UF"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Test Comparatif: bwip-js vs treepoem${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Nettoyage
rm -f bwipjs_*.png treepoem_*.png

# Fonction de test générique
test_gs1_generation() {
    local data="$1"
    local description="$2"
    local filename_prefix="$3"

    echo -e "${BLUE}🧪 Test: $description${NC}"
    echo "   Données: ${data}"
    echo ""

    # Test génération
    HTTP_CODE=$(curl -X POST "${API_URL}/generate/" \
        -H "Content-Type: application/json" \
        -d "{
            \"data\": \"$data\",
            \"format\": \"gs1-datamatrix\",
            \"image_format\": \"png\"
        }" \
        --output "${filename_prefix}_generated.png" \
        --write-out "%{http_code}" \
        --silent)

    if [ "$HTTP_CODE" != "200" ]; then
        echo -e "${RED}   ❌ Génération échouée (HTTP $HTTP_CODE)${NC}"
        return 1
    fi

    FILE_SIZE=$(stat -f%z "${filename_prefix}_generated.png" 2>/dev/null || stat -c%s "${filename_prefix}_generated.png" 2>/dev/null)
    echo -e "${GREEN}   ✅ Généré: ${filename_prefix}_generated.png (${FILE_SIZE} bytes)${NC}"

    # Test de décodage pour validation
    DECODE_RESPONSE=$(curl -X POST "${API_URL}/decode/" \
        -F "file=@${filename_prefix}_generated.png" \
        -F "verbose=true" \
        --silent)

    SUCCESS=$(echo "$DECODE_RESPONSE" | jq -r '.success' 2>/dev/null)
    if [ "$SUCCESS" = "true" ]; then
        FORMAT_DETECTED=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.format' 2>/dev/null)
        IS_GS1=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.is_gs1' 2>/dev/null)
        CONTAINS_FNC1=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.characteristics.contains_fnc1' 2>/dev/null)

        echo "   📊 Résultat décodage:"
        echo "      Format: $FORMAT_DETECTED"
        echo "      Est GS1: $IS_GS1"
        echo "      Contient FNC1: $CONTAINS_FNC1"

        if [ "$IS_GS1" = "true" ] && [ "$CONTAINS_FNC1" = "true" ] && [ "$FORMAT_DETECTED" = "GS1 DataMatrix" ]; then
            echo -e "${GREEN}   🎉 GS1 DataMatrix CONFORME (]d2 attendu)${NC}"
            return 0
        else
            echo -e "${YELLOW}   ⚠️  DataMatrix standard détecté (]d1) - pas de FNC1${NC}"
            return 2
        fi
    else
        echo -e "${RED}   ❌ Décodage échoué${NC}"
        echo "      Erreur: $(echo "$DECODE_RESPONSE" | jq -r '.detail' 2>/dev/null)"
        return 1
    fi
}

# Vérifier disponibilité API
echo -e "${BLUE}📋 Vérification disponibilité générateurs...${NC}"
HEALTH_RESPONSE=$(curl -s "${API_URL}/health")

TREEPOEM_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.capabilities.generators.treepoem' 2>/dev/null)
BWIPJS_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.capabilities.generators.bwipjs' 2>/dev/null)

echo "   treepoem: $TREEPOEM_STATUS"
echo "   bwip-js: $BWIPJS_STATUS (à vérifier après déploiement)"
echo ""

# Attendre déploiement si nécessaire
echo -e "${YELLOW}⏳ Attente déploiement bwip-js (30 secondes)...${NC}"
sleep 30

echo -e "${BLUE}=== TESTS GS1 DATAMATRIX COMPARATIFS ===${NC}"

# Test 1: Données simples
echo -e "${BLUE}Test 1: Données GS1 simples${NC}"
test_gs1_generation "$GS1_DATA_SIMPLE" "GS1 DataMatrix Simple" "simple"
RESULT_SIMPLE=$?

echo ""

# Test 2: Données complexes
echo -e "${BLUE}Test 2: Données GS1 complexes${NC}"
test_gs1_generation "$GS1_DATA_COMPLEX" "GS1 DataMatrix Complexe" "complex"
RESULT_COMPLEX=$?

echo ""

# Résumé des résultats
echo -e "${BLUE}=== RÉSUMÉ COMPARATIF ===${NC}"

echo -e "Données simples:    $([ $RESULT_SIMPLE -eq 0 ] && echo -e "${GREEN}🎉 GS1 CONFORME${NC}" || ([ $RESULT_SIMPLE -eq 2 ] && echo -e "${YELLOW}⚠️ DataMatrix standard${NC}" || echo -e "${RED}❌ ÉCHEC${NC}"))"
echo -e "Données complexes:  $([ $RESULT_COMPLEX -eq 0 ] && echo -e "${GREEN}🎉 GS1 CONFORME${NC}" || ([ $RESULT_COMPLEX -eq 2 ] && echo -e "${YELLOW}⚠️ DataMatrix standard${NC}" || echo -e "${RED}❌ ÉCHEC${NC}"))"

echo ""

# Recommendations finales
if [ $RESULT_SIMPLE -eq 0 ] || [ $RESULT_COMPLEX -eq 0 ]; then
    echo -e "${GREEN}🎯 SUCCÈS: Au moins un générateur produit des GS1 DataMatrix conformes !${NC}"
    echo -e "${GREEN}   → Envoyez les fichiers à l'expert GS1 pour validation finale${NC}"

    if [ $RESULT_SIMPLE -eq 0 ] && [ $RESULT_COMPLEX -ne 0 ]; then
        echo -e "${YELLOW}   → Problème formatage données complexes à résoudre${NC}"
    fi

elif [ $RESULT_SIMPLE -eq 2 ] || [ $RESULT_COMPLEX -eq 2 ]; then
    echo -e "${YELLOW}⚠️  PARTIEL: Génération réussie mais pas de FNC1 détecté${NC}"
    echo -e "${YELLOW}   → Vérifiez configuration bwip-js et treepoem${NC}"
else
    echo -e "${RED}❌ ÉCHEC: Aucun générateur ne fonctionne${NC}"
    echo -e "${RED}   → Vérifiez logs serveur et installations${NC}"
fi

echo ""
echo -e "${BLUE}📁 Fichiers générés pour test expert:${NC}"
echo "   simple_generated.png"
echo "   complex_generated.png"
echo ""

echo -e "${BLUE}🔍 Vérification manuelle recommandée:${NC}"
echo "   1. Scannez avec application GS1 professionnelle"
echo "   2. Vérifiez identifiant AIM: ]d2 = GS1, ]d1 = standard"
echo "   3. Confirmez reconnaissance comme 'GS1 DataMatrix'"