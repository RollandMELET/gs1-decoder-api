# 📦 GS1 Decoder API

Microservice pour décoder et générer des codes-barres GS1 (1D/2D), avec parsing complet et support verbose.

---

## ✨ Fonctionnalités

- 🔎 Scan d'images vers codes-barres GS1.
- 🧩 Parsing de chaînes de caractères brutes GS1.
- 📊 Formatage intelligent des valeurs (dates, décimaux).
- 🔄 Détection automatique du format du code (QR Code, DataMatrix, etc.).
- 🖼️ Génération de codes-barres (DataMatrix, QR Code, Code 128).
- 📜 Mode `verbose` pour analyse détaillée.
- 📦 Docker-ready, Coolify-ready.
- 🔥 Déploiement en un clic.
- 🩺 Endpoint `/health` pour monitoring.
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
**Résultat attendu :**
Le fichier `barcode.png` sera sauvegardé dans votre répertoire courant.

---

## 📦 Construire et lancer manuellement en Docker

```bash
docker build -t gs1-decoder-api .
docker run -d -p 8000:8000 gs1-decoder-api
```

---

## 📄 Licence

Open Source sous licence MIT.
Fais-en ce que tu veux, améliore-le, utilise-le, transforme-le 🚀.
