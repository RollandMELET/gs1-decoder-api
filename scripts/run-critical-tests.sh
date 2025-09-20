#!/bin/bash
# Script pour exécuter les tests critiques GS1 DataMatrix

set -e

echo "🔴 Exécution des tests critiques GS1 DataMatrix..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier la présence de Node.js
if ! command -v node &> /dev/null; then
    log_error "Node.js n'est pas installé"
    exit 1
fi

# Vérifier la présence de npm
if ! command -v npm &> /dev/null; then
    log_error "npm n'est pas installé"
    exit 1
fi

# Vérifier package.json et node_modules
if [ ! -f "package.json" ]; then
    log_error "package.json non trouvé"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    log_warn "node_modules manquant, installation des dépendances..."
    npm install
fi

# Vérifier bwip-js
log_info "Vérification de bwip-js..."
if ! node -e "require('bwip-js')" 2>/dev/null; then
    log_error "bwip-js n'est pas installé correctement"
    exit 1
fi

# Test du script Node.js
log_info "Test du script generate_gs1_bwip.js..."
if node generate_gs1_bwip.js "(01)12345678901234" "test_critical.png"; then
    if [ -f "test_critical.png" ]; then
        file_size=$(stat -c%s "test_critical.png" 2>/dev/null || stat -f%z "test_critical.png" 2>/dev/null)
        log_info "✅ Script Node.js fonctionne (taille: ${file_size} bytes)"
        rm -f "test_critical.png"
    else
        log_error "❌ Fichier de sortie non généré"
        exit 1
    fi
else
    log_error "❌ Script Node.js a échoué"
    exit 1
fi

# Vérifier pytest
if ! command -v pytest &> /dev/null; then
    log_error "pytest n'est pas installé"
    exit 1
fi

# Exécuter les tests critiques
log_info "Exécution des tests critiques Python..."

# Tests critiques obligatoires
CRITICAL_TESTS=(
    "tests/unit/test_gs1_datamatrix_core.py::TestGS1DataMatrixCore::test_use_treepoem_false_for_gs1_datamatrix"
    "tests/unit/test_gs1_datamatrix_core.py::TestGS1DataMatrixCore::test_bwipjs_priority_in_hybrid_architecture"
    "tests/conformity/test_gs1_standards.py::TestGS1Standards::test_gs1_aim_identifier_validation"
    "tests/performance/test_file_size_optimization.py::TestFileSizeOptimization::test_file_size_optimization_simple"
)

failed_tests=()

for test in "${CRITICAL_TESTS[@]}"; do
    echo ""
    log_info "🧪 Exécution: $test"

    if pytest "$test" -v --tb=short --no-header -q; then
        log_info "✅ RÉUSSI: $test"
    else
        log_error "❌ ÉCHEC: $test"
        failed_tests+=("$test")
    fi
done

# Résumé
echo ""
echo "================================"
echo "📊 RÉSUMÉ DES TESTS CRITIQUES"
echo "================================"

total_tests=${#CRITICAL_TESTS[@]}
failed_count=${#failed_tests[@]}
passed_count=$((total_tests - failed_count))

log_info "Total: $total_tests tests"
log_info "Réussis: $passed_count tests"

if [ $failed_count -eq 0 ]; then
    log_info "✅ TOUS LES TESTS CRITIQUES ONT RÉUSSI"
    echo ""
    log_info "🔒 La fonctionnalité GS1 DataMatrix est sécurisée"
    exit 0
else
    log_error "Échoués: $failed_count tests"
    echo ""
    log_error "❌ TESTS CRITIQUES ÉCHOUÉS:"
    for failed_test in "${failed_tests[@]}"; do
        log_error "  - $failed_test"
    done
    echo ""
    log_error "🚨 LA FONCTIONNALITÉ GS1 DATAMATRIX EST COMPROMISE"
    log_error "🔄 Utilisez: git checkout v1.3.0-gs1-stable pour restaurer"
    exit 1
fi