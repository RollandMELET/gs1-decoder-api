# Makefile pour GS1 DataMatrix API
.PHONY: help install test test-critical test-fast test-all test-coverage clean lint format setup-hooks monitor

# Configuration
PYTHON := python3
PIP := pip
PYTEST := pytest
NPM := npm

help: ## Afficher l'aide
	@echo "🔍 Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installer toutes les dépendances
	@echo "📦 Installation des dépendances..."
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-test.txt
	$(NPM) install
	@echo "✅ Installation terminée"

setup-hooks: ## Configurer les pre-commit hooks
	@echo "🪝 Configuration des pre-commit hooks..."
	$(PIP) install pre-commit
	pre-commit install
	@echo "✅ Pre-commit hooks configurés"

test-critical: ## 🔴 Exécuter uniquement les tests critiques GS1
	@echo "🔴 Tests critiques GS1 DataMatrix..."
	./scripts/run-critical-tests.sh

test-fast: ## ⚡ Tests rapides (unitaires + critiques)
	@echo "⚡ Tests rapides..."
	$(PYTEST) tests/unit/ tests/conformity/test_gs1_standards.py::TestGS1Standards::test_gs1_aim_identifier_validation -v --tb=short

test-integration: ## 🔗 Tests d'intégration
	@echo "🔗 Tests d'intégration..."
	$(PYTEST) tests/integration/ -v --tb=short

test-performance: ## ⚡ Tests de performance
	@echo "⚡ Tests de performance..."
	$(PYTEST) tests/performance/ -v --tb=short

test-regression: ## 🛡️ Tests de non-régression
	@echo "🛡️ Tests de non-régression..."
	$(PYTEST) tests/integration/test_regression.py -v --tb=short

test-all: ## 🧪 Tous les tests
	@echo "🧪 Exécution de tous les tests..."
	$(PYTEST) tests/ -v --tb=short

test-coverage: ## 📊 Tests avec couverture
	@echo "📊 Tests avec analyse de couverture..."
	$(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=85

test-nodejs: ## 🟢 Test du script Node.js
	@echo "🟢 Test script Node.js..."
	node generate_gs1_bwip.js "(01)03760423190005" "test_makefile.png"
	@ls -la test_makefile.png
	@file test_makefile.png
	@rm -f test_makefile.png
	@echo "✅ Script Node.js fonctionne"

monitor: ## 🏥 Monitoring API production (formats critiques)
	@echo "🏥 Monitoring API production..."
	./scripts/monitor-production.sh

monitor-all: ## 🎯 Monitoring tous formats + endpoints
	@echo "🎯 Monitoring complet..."
	./scripts/monitor-all-formats.sh

monitor-endpoints: ## 🔗 Monitoring endpoints spécifique
	@echo "🔗 Monitoring endpoints..."
	./scripts/monitor-endpoints.sh

monitor-performance: ## 📈 Benchmark performance
	@echo "📈 Benchmark performance..."
	./scripts/performance-benchmark.sh

monitor-performance-concurrent: ## 🚀 Benchmark concurrent
	@echo "🚀 Benchmark concurrent..."
	./scripts/performance-benchmark.sh --concurrent

monitor-alert: ## 🚨 Monitoring avec alertes
	@echo "🚨 Monitoring avec alertes..."
	./scripts/monitor-production.sh --alert

lint: ## 🔍 Vérification syntaxe et style
	@echo "🔍 Vérification du code..."
	flake8 app/ tests/ --max-line-length=100 --ignore=E203,W503
	@echo "✅ Code vérifié"

format: ## 🎨 Formatage automatique du code
	@echo "🎨 Formatage du code..."
	black app/ tests/
	@echo "✅ Code formaté"

clean: ## 🧹 Nettoyage des fichiers temporaires
	@echo "🧹 Nettoyage..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.png
	rm -rf node_modules/.cache/
	@echo "✅ Nettoyage terminé"

setup: install setup-hooks ## 🚀 Configuration complète (install + hooks)
	@echo "🚀 Configuration complète terminée"

validate: test-critical lint ## ✅ Validation rapide (critique + lint)
	@echo "✅ Validation terminée avec succès"

ci: test-all lint ## 🤖 Pipeline CI complète
	@echo "🤖 Pipeline CI terminée"

dev: ## 🔧 Mode développement
	@echo "🔧 Démarrage en mode développement..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-test: ## 🔧 Mode test continu
	@echo "🔧 Tests en mode continu..."
	$(PYTEST) tests/ --watch

benchmark: ## 📈 Tests de performance avec benchmark
	@echo "📈 Benchmark de performance..."
	$(PYTEST) tests/performance/ --benchmark-only --benchmark-sort=mean

# Targets spéciaux pour debug
debug-nodejs: ## 🐛 Debug script Node.js
	@echo "🐛 Debug script Node.js..."
	node --version
	npm --version
	node -e "console.log('bwip-js:', require('bwip-js/package.json').version)"
	ls -la generate_gs1_bwip.js

debug-python: ## 🐛 Debug environnement Python
	@echo "🐛 Debug environnement Python..."
	$(PYTHON) --version
	$(PIP) list | grep -E "(pytest|pillow|jpype|fastapi)"

# Cibles de sécurité
security-check: ## 🔒 Vérification sécurité
	@echo "🔒 Vérification sécurité..."
	$(PIP) install safety
	safety check
	@echo "✅ Vérification sécurité terminée"

# Restoration d'urgence
restore-stable: ## 🔄 Restaurer version stable
	@echo "🔄 Restauration version stable..."
	git checkout v1.3.0-gs1-stable
	@echo "✅ Version stable restaurée"

# Informations
info: ## ℹ️ Informations système
	@echo "ℹ️ Informations système:"
	@echo "  Python: $(shell $(PYTHON) --version)"
	@echo "  Node.js: $(shell node --version 2>/dev/null || echo 'Non installé')"
	@echo "  npm: $(shell npm --version 2>/dev/null || echo 'Non installé')"
	@echo "  Git branch: $(shell git branch --show-current)"
	@echo "  Last commit: $(shell git log -1 --oneline)"
	@echo "  Working dir: $(shell pwd)"

# Aide par catégorie
help-tests: ## 📋 Aide pour les tests
	@echo "📋 Tests disponibles:"
	@echo "  make test-critical    🔴 Tests critiques GS1 (obligatoires)"
	@echo "  make test-fast        ⚡ Tests rapides"
	@echo "  make test-integration 🔗 Tests d'intégration"
	@echo "  make test-performance ⚡ Tests de performance"
	@echo "  make test-regression  🛡️ Tests de non-régression"
	@echo "  make test-all         🧪 Tous les tests"
	@echo "  make test-coverage    📊 Tests avec couverture"