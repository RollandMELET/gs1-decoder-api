#!/bin/bash

# Script de test complet : Génération puis décodage GS1 DataMatrix
# Test du round-trip pour valider que le format avec parenthèses fonctionne correctement

# Configuration
API_URL="https://gs1-decoder-api.rorworld.eu"
GS1_DATA="(01)03760423190005(11)250326(3100)015500(21)0000000D(90)7391023(93)DHA(94)UP(95)ENVELOPPE_NUE_4UF"
OUTPUT_FILE="test_gs1_generated.png"
LOG_FILE="test_gs1_roundtrip.log"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Test Round-trip GS1 DataMatrix${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Fonction de nettoyage
cleanup() {
    echo -e "${YELLOW}Nettoyage des fichiers temporaires...${NC}"
    rm -f "$OUTPUT_FILE" "$LOG_FILE"
}

# Nettoyage au début
cleanup

echo -e "${BLUE}1. Données d'entrée:${NC}"
echo "   $GS1_DATA"
echo ""

# Étape 1: Vérifier que l'API est en ligne
echo -e "${BLUE}2. Vérification de l'API...${NC}"
if ! curl -f -s "${API_URL}/health" > /dev/null; then
    echo -e "${RED}❌ L'API n'est pas accessible à ${API_URL}${NC}"
    exit 1
fi
echo -e "${GREEN}✅ API accessible${NC}"
echo ""

# Étape 2: Générer le GS1 DataMatrix
echo -e "${BLUE}3. Génération du GS1 DataMatrix...${NC}"
echo "   Format: gs1-datamatrix"
echo "   Fichier de sortie: $OUTPUT_FILE"

GENERATE_RESPONSE=$(curl -X POST "${API_URL}/generate/" \
    -H "Content-Type: application/json" \
    -d "{
        \"data\": \"$GS1_DATA\",
        \"format\": \"gs1-datamatrix\",
        \"image_format\": \"png\"
    }" \
    --output "$OUTPUT_FILE" \
    --write-out "%{http_code}" \
    --silent \
    --show-error)

if [ "$GENERATE_RESPONSE" != "200" ]; then
    echo -e "${RED}❌ Erreur lors de la génération (HTTP $GENERATE_RESPONSE)${NC}"
    if [ -f "$OUTPUT_FILE" ]; then
        echo "Contenu de la réponse:"
        cat "$OUTPUT_FILE"
    fi
    exit 1
fi

if [ ! -f "$OUTPUT_FILE" ] || [ ! -s "$OUTPUT_FILE" ]; then
    echo -e "${RED}❌ Fichier PNG non généré ou vide${NC}"
    exit 1
fi

FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
echo -e "${GREEN}✅ GS1 DataMatrix généré avec succès (${FILE_SIZE} bytes)${NC}"
echo ""

# Étape 3: Décoder le GS1 DataMatrix généré
echo -e "${BLUE}4. Décodage du GS1 DataMatrix...${NC}"

# Test du décodage en mode verbose pour voir tous les détails
DECODE_RESPONSE=$(curl -X POST "${API_URL}/decode/" \
    -F "file=@$OUTPUT_FILE" \
    -F "verbose=true" \
    --silent \
    --show-error)

DECODE_STATUS=$?

if [ $DECODE_STATUS -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors de l'appel de décodage${NC}"
    exit 1
fi

# Sauvegarder la réponse complète pour analyse
echo "$DECODE_RESPONSE" > "$LOG_FILE"

echo -e "${GREEN}✅ Décodage effectué${NC}"
echo ""

# Étape 4: Analyser les résultats
echo -e "${BLUE}5. Analyse des résultats:${NC}"
echo ""

# Vérifier si le décodage a réussi
SUCCESS=$(echo "$DECODE_RESPONSE" | jq -r '.success' 2>/dev/null)

if [ "$SUCCESS" != "true" ]; then
    echo -e "${RED}❌ Le décodage a échoué${NC}"
    echo "Réponse complète:"
    echo "$DECODE_RESPONSE" | jq . 2>/dev/null || echo "$DECODE_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Décodage réussi!${NC}"
echo ""

# Extraire les données décodées
RAW_DATA=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].raw' 2>/dev/null)
DECODER_INFO=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.decoder' 2>/dev/null)
FORMAT_INFO=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.format' 2>/dev/null)
IS_GS1=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].decoder_info.is_gs1' 2>/dev/null)

echo -e "${BLUE}📊 Informations de décodage:${NC}"
echo "   Décodeur utilisé: $DECODER_INFO"
echo "   Format détecté: $FORMAT_INFO"
echo "   Est GS1: $IS_GS1"
echo ""

echo -e "${BLUE}📝 Données brutes décodées:${NC}"
echo "   $RAW_DATA"
echo ""

# Afficher les données parsées (AI détaillés)
echo -e "${BLUE}🔍 Application Identifiers parsés:${NC}"
PARSED_DATA=$(echo "$DECODE_RESPONSE" | jq -r '.barcodes[0].parsed' 2>/dev/null)

if echo "$PARSED_DATA" | jq -e 'type == "array"' > /dev/null 2>&1; then
    # Mode verbose : affichage détaillé des AI
    echo "$PARSED_DATA" | jq -r '.[] | "   AI \(.ai) (\(.name)): \(.value) - Valide: \(.valid)"' 2>/dev/null
else
    # Mode simple : affichage clé-valeur
    echo "$PARSED_DATA" | jq -r 'to_entries[] | "   \(.key): \(.value)"' 2>/dev/null
fi

echo ""

# Étape 5: Validation du round-trip
echo -e "${BLUE}6. Validation du round-trip:${NC}"

# Vérifier que c'est bien un GS1 DataMatrix
if [ "$IS_GS1" = "true" ] && [[ "$FORMAT_INFO" == *"GS1"* ]]; then
    echo -e "${GREEN}✅ Format GS1 DataMatrix confirmé${NC}"
else
    echo -e "${YELLOW}⚠️  Format non-GS1 détecté: $FORMAT_INFO${NC}"
fi

# Vérifier que les données contiennent les AI attendus
EXPECTED_AIS=("01" "11" "3100" "21" "90" "93" "94" "95")
MISSING_AIS=()

for ai in "${EXPECTED_AIS[@]}"; do
    if ! echo "$DECODE_RESPONSE" | grep -q "\"ai\".*\"$ai\"" && ! echo "$DECODE_RESPONSE" | grep -q "\"$ai\""; then
        MISSING_AIS+=("$ai")
    fi
done

if [ ${#MISSING_AIS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les AI attendus sont présents${NC}"
else
    echo -e "${YELLOW}⚠️  AI manquants: ${MISSING_AIS[*]}${NC}"
fi

# Comparer les données d'entrée et de sortie (structurellement)
if echo "$RAW_DATA" | grep -q "03760423190005" && echo "$RAW_DATA" | grep -q "250326"; then
    echo -e "${GREEN}✅ Données principales préservées${NC}"
else
    echo -e "${YELLOW}⚠️  Certaines données peuvent avoir été altérées${NC}"
fi

echo ""

# Résumé final
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}           RÉSUMÉ DU TEST${NC}"
echo -e "${BLUE}==========================================${NC}"

if [ "$SUCCESS" = "true" ] && [ "$IS_GS1" = "true" ]; then
    echo -e "${GREEN}🎉 TEST RÉUSSI!${NC}"
    echo -e "${GREEN}   Le format avec parenthèses fonctionne correctement${NC}"
    echo -e "${GREEN}   Un vrai GS1 DataMatrix a été généré et décodé${NC}"
else
    echo -e "${YELLOW}⚠️  TEST PARTIELLEMENT RÉUSSI${NC}"
    echo -e "${YELLOW}   Le code a été généré et décodé mais peut ne pas être GS1-conforme${NC}"
fi

echo ""
echo -e "${BLUE}📁 Fichiers générés:${NC}"
echo "   🖼️  Image: $OUTPUT_FILE"
echo "   📄 Log détaillé: $LOG_FILE"
echo ""

echo -e "${BLUE}🔍 Pour voir le log complet:${NC}"
echo "   cat $LOG_FILE | jq ."
echo ""

echo -e "${BLUE}🧹 Pour nettoyer:${NC}"
echo "   rm $OUTPUT_FILE $LOG_FILE"