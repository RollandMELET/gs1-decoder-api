# 📦 GS1 Decoder API

Microservice pour décoder et générer des codes-barres GS1 (1D/2D), avec parsing complet et support verbose.

---

## ✨ Fonctionnalités

- 🔎 Scan d'images vers codes-barres GS1
- 🧩 Parsing Application Identifiers (AI) longueur fixe et variable
- 📊 Formatage intelligent des valeurs (dates, décimaux)
- 🔄 Détection automatique du format du code (QR Code, DataMatrix, etc.)
- 🖼️ Génération de codes-barres (DataMatrix, QR Code, Code 128)
- 📜 Mode `verbose` pour analyse détaillée
- 📦 Docker-ready, Coolify-ready
- 🔥 Déploiement en un clic
- 🩺 Endpoint `/health` pour monitoring
- 📚 Documentation interactive via Swagger UI (`/docs`) et Redoc (`/redoc`)

---

## ⚙️ Déploiement rapide avec Coolify

1. Créer un projet "Docker build" dans Coolify
2. Uploader ce projet
3. Build + Exposer le port 8000
4. 🎉 API opérationnelle

---

## 🔥 API Endpoints

| Méthode | URL          | Description                  |
|:--------|:-------------|:-----------------------------|
| GET     | `/health`    | Vérifie que le service tourne |
| POST    | `/decode/`   | Envoie une image, décode et parse |
| POST    | `/generate/` | Génère un code-barres GS1 |

**POST `/decode/` paramètres** :
- `file` : fichier image (obligatoire)
- `verbose` : booléen optionnel (`true` ou `false`)

**POST `/generate/` paramètres** :
- `data` : données GS1 à encoder (ex: "01034531200000111719112510ABCD1234")
- `format` : format du code-barres (datamatrix, qrcode, code128, gs1-datamatrix, gs1-qrcode, gs1-128)
- `image_format` : format de l'image (png, jpeg, svg)
- `width` : largeur de l'image (50-1000 pixels)
- `height` : hauteur de l'image (50-1000 pixels)

---

## 📚 Exemples cURL

### Décodage de code-barres

**Scan simple**
```bash
curl -X POST https://gs1-decoder-api.rorworld.eu/decode/ \
  -F "file=@/Users/rollandmelet/Développement/Projets/gs1-decoder-api/imagetest.jpg" \
  -F "verbose=false"
```

**Résultat attendu**
```json
{
  "success": true,
  "barcodes": [
    {
      "raw": "0103760423190005112504233100012000210000003090739102393DHA.4UP.5ENVELOPPE_NUE_4UF",
      "parsed": {
        "GTIN": "03760423190005",
        "PROD_DATE": "2025-04-23",
        "NET_WEIGHT_KG": "12.000",
        "SERIAL": "00000030",
        "INTERNAL": "7391023"
      },
      "decoder_info": {
        "decoder": "pylibdmtx",
        "format": "GS1 DataMatrix"
      }
    }
  ]
}
```

**Scan verbose**
```bash
curl -X POST https://gs1-decoder-api.rorworld.eu/decode/ \
  -F "file=@/Users/rollandmelet/Développement/Projets/gs1-decoder-api/imagetest.jpg" \
  -F "verbose=true"
```

**Résultat attendu**
```json
{
  "success": true,
  "barcodes": [
    {
      "raw": "0103760423190005112504233100012000210000003090739102393DHA.4UP.5ENVELOPPE_NUE_4UF",
      "parsed": [
        {
          "ai": "01",
          "name": "GTIN",
          "value": "03760423190005",
          "valid": true
        },
        {
          "ai": "11",
          "name": "PROD_DATE",
          "value": "2025-04-23",
          "valid": true
        },
        {
          "ai": "3100",
          "name": "NET_WEIGHT_KG",
          "value": "12.000",
          "valid": true
        },
        {
          "ai": "21",
          "name": "SERIAL",
          "value": "00000030",
          "valid": true
        },
        {
          "ai": "90",
          "name": "INTERNAL",
          "value": "7391023",
          "valid": true
        },
        {
          "ai": "93",
          "name": "INTERNAL3",
          "value": "DHA",
          "valid": true
        },
        {
          "ai": "94",
          "name": "INTERNAL4",
          "value": "UP",
          "valid": true
        },
        {
          "ai": "95",
          "name": "INTERNAL5",
          "value": "ENVELOPPE_NUE_4UF",
          "valid": true
        }
      ],
      "decoder_info": {
        "decoder": "pylibdmtx",
        "format": "GS1 DataMatrix",
        "is_gs1": true,
        "confidence": 0.9,
        "characteristics": {
          "length": 81,
          "content_type": "alphanumeric",
          "contains_special_chars": true,
          "potential_ais": ["01", "11", "31", "00", "21", "90", "93", "94", "95"]
        }
      }
    }
  ]
}
```

### Génération de code-barres

**Générer un DataMatrix GS1**
```bash
curl -X POST https://gs1-decoder-api.rorworld.eu/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "data": "01034531200000111719112510ABCD1234",
    "format": "gs1-datamatrix",
    "image_format": "png",
    "width": 300,
    "height": 300
  }' \
  --output barcode.png
```

**Générer un QR Code GS1**
```bash
curl -X POST https://gs1-decoder-api.rorworld.eu/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "data": "01034531200000111719112510ABCD1234",
    "format": "gs1-qrcode",
    "image_format": "png",
    "width": 300,
    "height": 300
  }' \
  --output qrcode.png
```

**Générer un Code 128 GS1**
```bash
curl -X POST https://gs1-decoder-api.rorworld.eu/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "data": "01034531200000111719112510ABCD1234",
    "format": "gs1-128",
    "image_format": "png",
    "width": 400,
    "height": 200
  }' \
  --output code128.png
```

**Healthcheck**
```bash
curl https://gs1-decoder-api.rorworld.eu/health
```

**Résultat attendu**
```json
{
  "status": "OK",
  "capabilities": {
    "decoders": {
      "zxing": true,
      "pylibdmtx": true
    },
    "supported_codes": ["DataMatrix", "QR Code", "GS1-128", "GS1 DataMatrix", "GS1 QR Code"],
    "api_version": "1.1.0",
    "features": {
      "decode": true,
      "generate": true
    }
  }
}
```

---

## 📦 Construire et lancer manuellement en Docker

```bash
docker build -t gs1-decoder-api .
docker run -d -p 8000:8000 gs1-decoder-api
```

---

## 📊 Tests

L'API inclut plusieurs scripts de test pour valider son fonctionnement :

### Test du module de parsing GS1
```bash
python test_gs1_parser.py
```

### Test de l'endpoint de décodage
```bash
python test_api.py
```

### Test de l'endpoint de génération
```bash
python test_generate.py
```

---

## 📚 Ressources

Le dossier `resources/` contient toutes les informations nécessaires concernant les Application Identifiers (AI) de GS1, incluant :
- La liste complète des AI disponibles dans `gs1_application_identifiers.json`
- Documentation des formats GS1 supportés
- Spécifications de longueur fixe et variable
- Règles de formatage et d'interprétation (dates, décimaux)

Ces ressources sont utilisées pour assurer un support complet des AI GS1.

---

## 📄 Licence

Open Source sous licence MIT.
Fais-en ce que tu veux, améliore-le, utilise-le, transforme-le 🚀.

---

## 🛠 Idées d'améliorations futures

- ✅ Support complet pour TOUS les AI GS1 existants
- ✅ Détection automatique du format du code (QR Code, DataMatrix, etc.)
- ✅ Génération de codes-barres
- UI Web minimaliste pour uploader une image facilement et générer des codes
- Tests unitaires automatisés avec CI/CD
- Support amélioré pour le SVG dans la génération

---