# 📦 GS1 Decoder API

Microservice pour décoder et générer des codes-barres GS1 (1D/2D), avec parsing complet et support verbose.

> **🧠 Pour agents LLM :** Consultez [`/llms.txt`](/llms.txt) pour une référence complète optimisée (60% moins de tokens). Documentation alternative : [`README_LLM_OPTIMIZED.md`](/README_LLM_OPTIMIZED.md)

---

## ✨ Fonctionnalités

- 🔎 Scan d'images vers codes-barres GS1 et standard.
- 🧩 Parsing de chaînes de caractères brutes GS1.
- 📊 Formatage intelligent des valeurs (dates, décimaux).
- 🔄 Détection automatique du format du code (QR Code, DataMatrix, etc.).
- 🖼️ **Génération 6 formats** : GS1 DataMatrix (optimisé 96.8%), GS1 QR Code, GS1-128, QR Code, DataMatrix, Code 128.
- 📜 Mode `verbose` pour analyse détaillée.
- 🛡️ **Suite TDD exhaustive** : Protection anti-régression tous formats.
- 📊 **Monitoring granulaire** : Surveillance temps réel 6 formats + 4 endpoints.
- 📦 Docker-ready, production-ready avec CI/CD GitHub Actions.
- 🔥 Déploiement automatisé avec validation multi-niveau.
- 🩺 Endpoints monitoring : `/health` + scripts spécialisés.
- 📚 Documentation interactive via Swagger UI (`/docs`) et Redoc (`/redoc`).

---

## 🔥 API Endpoints

| Méthode | URL          | Description                                                    |
| :------ | :----------- | :------------------------------------------------------------- |
| GET     | `/health`    | Vérifie l'état de santé et les capacités du service.           |
| POST    | `/decode/`   | Décode les codes-barres depuis une image et parse les données. |
| POST    | `/parse/`    | Parse une chaîne de caractères GS1 brute (déjà décodée).       |
| POST    | `/generate/` | Génère une image de code-barres à partir de données GS1.       |

---

## 📚 Documentation Interactive (Aide)

L'API fournit une documentation complète et interactive, générée automatiquement. Pour explorer tous les points d'entrée, leurs paramètres et tester l'API directement depuis votre navigateur, utilisez les liens suivants :

- **Swagger UI (recommandé pour tester) :** [https://gs1-decoder-api.rorworld.eu/docs](https://gs1-decoder-api.rorworld.eu/docs)
- **ReDoc (recommandé pour lire la documentation) :** [https://gs1-decoder-api.rorworld.eu/redoc](https://gs1-decoder-api.rorworld.eu/redoc)

---

## 🛠️ Exemples d'Utilisation (cURL)

Voici un exemple pour chaque endpoint principal.

### 1. Vérifier l'état du service (`/health`)

Cette commande vérifie que l'API est en ligne et retourne ses capacités actuelles.

```bash
curl https://gs1-decoder-api.rorworld.eu/health
```

**Résultat attendu :**
```json
{
  "status": "OK",
  "capabilities": {
    "decoders": { "zxing_jpype": true, "pylibdmtx": true },
    "supported_codes": ["DataMatrix", "QR Code", "Code 128", "GS1-128", "GS1 DataMatrix", "GS1 QR Code"],
    "api_version": "1.3.0",
    "features": { "decode": true, "generate": true, "parse": true }
  }
}
```

### 2. Décoder un code-barres depuis une image (`/decode`)

Envoyez un fichier image pour en extraire les données de code-barres.

**Paramètres (form-data)** :
- `file` : fichier image (obligatoire)
- `verbose`: `true` ou `false` (optionnel)

```bash
curl -X POST "https://gs1-decoder-api.rorworld.eu/decode/" \
  -F "file=@/chemin/vers/votre/image.jpg" \
  -F "verbose=false"
```

**Résultat attendu :**
```json
{
  "success": true,
  "barcodes": [
    {
      "raw": "010376042319000517250423...",
      "parsed": {
        "GTIN": "03760423190005",
        "EXPIRY": "2025-04-23"
      },
      "decoder_info": {
        "decoder": "ZXing (JPype)",
        "format": "GS1 DataMatrix"
      }
    }
  ]
}
```

### 3. Parser une chaîne de caractères brute (`/parse`)

Envoyez une chaîne de caractères déjà décodée pour obtenir une analyse GS1 détaillée.

**Paramètres (JSON Body)** :
- `raw_data` : chaîne de caractères (obligatoire)
- `barcode_format`: nom du format (optionnel)

```bash
curl -X 'POST' \
  'https://gs1-decoder-api.rorworld.eu/parse/' \
  -H 'Content-Type: application/json' \
  -d '{
    "raw_data": "01037604231900051725042310AB-123\u001d21S12345",
    "barcode_format": "GS1 DataMatrix"
  }'
```

**Résultat attendu (toujours en mode verbose) :**
```json
{
  "success": true,
  "barcodes": [
    {
      "raw": "01037604231900051725042310AB-123\u001d21S12345",
      "parsed": [
        {"ai": "01", "name": "GTIN", "value": "03760423190005", "valid": true},
        {"ai": "17", "name": "EXPIRY", "value": "2025-04-23", "valid": true},
        {"ai": "10", "name": "BATCH", "value": "AB-123", "valid": true},
        {"ai": "21", "name": "SERIAL", "value": "S12345", "valid": true}
      ],
      "decoder_info": {
        "decoder": "Text Input",
        "format": "GS1 DataMatrix",
        "is_gs1": true,
        "confidence": 1.0
      }
    }
  ]
}
```

### 4. Générer un code-barres (`/generate`)

Créez une image de code-barres à partir de données GS1.

**Paramètres (JSON Body)** :
- `data`: données GS1 à encoder
- `format`: `gs1-datamatrix`, `gs1-qrcode`, `gs1-128`, etc.
- `image_format`: `png`, `jpeg`

```bash
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "01034531200000111719112510ABCD1234",
    "format": "gs1-datamatrix",
    "image_format": "png"
  }' \
  --output barcode.png
```

#### 🎯 **Contrôle Avancé Quiet Zone (GS1 DataMatrix)**

**Nouveau :** Contrôle précis des quiet zones selon standards GS1.

```bash
# Standard GS1 conforme (1.0 module)
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "(01)03453120000011(17)271031(10)BATCH123",
    "format": "gs1-datamatrix",
    "quiet_zone_modules": 1.0,
    "no_quiet_zone": false,
    "client_mode": "optimized"
  }' \
  --output gs1_standard.png

# Sans quiet zone (client gère design)
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "(01)03453120000011(17)271031(10)BATCH123",
    "format": "gs1-datamatrix",
    "quiet_zone_modules": 0.0,
    "no_quiet_zone": true,
    "client_mode": "optimized"
  }' \
  --output gs1_minimal.png

# Quiet zone élargie (meilleure lisibilité)
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "(01)03453120000011(17)271031(10)BATCH123",
    "format": "gs1-datamatrix",
    "quiet_zone_modules": 2.0,
    "client_mode": "optimized"
  }' \
  --output gs1_extended.png
```

**Paramètres Quiet Zone :**
- `quiet_zone_modules`: 0.0 à 10.0 (défaut: 1.0 = standard GS1)
- `no_quiet_zone`: true/false (défaut: false)
- `client_mode`: "optimized" (taille native) | "compatible" (redimensionné)

**Résultats attendus :**
- Sans quiet zone: ~491 bytes, 80×80 pixels
- Standard (1.0 module): ~526 bytes, 98×98 pixels
- Élargie (2.0 modules): ~536 bytes, 116×116 pixels

**Résultat attendu :**
Le fichier `barcode.png` sera sauvegardé dans votre répertoire courant.

---

## 🧪 Développement et Tests

Ce projet utilise une **suite TDD complète** pour sécuriser la fonctionnalité critique de génération GS1 DataMatrix.

### 🚀 Setup Développement
```bash
# Installation complète (dépendances + hooks TDD)
make setup

# Vérifier que tout fonctionne
make test-critical
```

### 🔴 Tests Critiques (Obligatoires)
```bash
# Tests critiques avant chaque commit
make test-critical

# Tests rapides pour développement
make test-fast

# 🎯 NOUVEAUX: Tests formats étendus
make test-formats         # Tous formats (QR, Code128, DataMatrix, GS1)
make test-endpoints       # Endpoints (/generate/, /decode/, /parse/, /health)

# Suite complète
make test-all
```

### 🏥 Monitoring Production
```bash
# Surveillance API production
make monitor

# Surveillance avec alertes
make monitor-alert
```

### 🛠️ Commandes Utiles
```bash
make help                    # Liste toutes les commandes
make dev                     # Mode développement avec reload
make lint                    # Vérification code
make clean                   # Nettoyage
make info                    # Informations système

# Monitoring étendu
make monitor-all             # 🎯 Monitoring tous formats
make monitor-endpoints       # 🔗 Monitoring endpoints
make monitor-performance     # 📈 Benchmark performance
make monitor-performance-concurrent  # 🚀 Tests concurrent
```

### 🔄 Point de Restauration
En cas de problème critique :
```bash
make restore-stable    # Retour version stable v1.3.0-gs1-stable
```

### 🎯 Workflow TDD Recommandé
```bash
# 1. Avant modification
make test-critical

# 2. Développement
make dev                # Terminal 1: serveur dev
make dev-test           # Terminal 2: tests continus

# 3. Avant commit
make validate          # Tests + lint automatique
git commit -m "..."    # Pre-commit hooks activés

# 4. Avant merge PR
make test-all          # Validation complète
```

---

## 📦 Construire et lancer manuellement en Docker

```bash
docker build -t gs1-decoder-api .
docker run -d -p 8000:8000 gs1-decoder-api
```

---

## 📚 Documentation Technique

### 🧠 **Documentation LLM-Optimisée (NOUVEAU)**
- **📄 Référence principale LLM :** [`/llms.txt`](/llms.txt) - Format standard 2025 (60% moins de tokens)
- **📋 Guide Claude Code :** [`CLAUDE_LLM_OPTIMIZED.md`](/CLAUDE_LLM_OPTIMIZED.md) - Commands structurés
- **📖 Guide utilisateur :** [`README_LLM_OPTIMIZED.md`](/README_LLM_OPTIMIZED.md) - Setup + usage condensés
- **🔗 Knowledge Graph :** [`PROJECT_KNOWLEDGE_GRAPH.md`](/PROJECT_KNOWLEDGE_GRAPH.md) - Relations composants
- **📊 Index navigation :** [`DOCUMENTATION_INDEX.md`](/DOCUMENTATION_INDEX.md) - Guide navigation LLM

### 📚 **Documentation Technique Complète**
- **TDD et Tests :** `docs/testing/README.md`
- **Architecture GS1 :** `docs/features/gs1-datamatrix-generation.md`
- **🎯 Service Complet :** `docs/features/service-complet-tdd.md`
- **🔧 Formats Supportés :** `docs/formats/README.md`
- **🛠️ Troubleshooting :** `docs/troubleshooting/README.md`
- **Point de Restauration :** `RESTORE_POINT.md`, `STABLE_POINT_TDD.md`
- **Configuration Claude Code :** `CLAUDE.md`
- **Rapport Final :** `FINAL_VALIDATION_REPORT.md`

---

## 🔒 Sécurité et Qualité

- ✅ **Suite TDD exhaustive** : 30 fichiers tests (4 critiques bloquants + formats + endpoints)
- ✅ **CI/CD GitHub Actions étendu** : 7 jobs validation progressive (critique → standard → performance)
- ✅ **Pre-commit hooks** avec tests automatiques tous formats
- ✅ **Monitoring granulaire** : 6 scripts surveillance (formats + endpoints + performance)
- ✅ **Optimisation 96.8%** tailles fichiers GS1 DataMatrix (500-700 bytes vs 16k-23k)
- ✅ **Conformité GS1** complète avec identifier ]d2 + architecture hybride
- ✅ **Protection anti-régression** : Tests bloquent commits dangereux automatiquement
- ✅ **Points restauration** : Tags multiples (v1.9.0-tdd-complete-service, v1.4.0-tdd-complete)

---

## 📄 Licence

Open Source sous licence MIT.
Fais-en ce que tu veux, améliore-le, utilise-le, transforme-le 🚀.
