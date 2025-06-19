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

| Méthode | URL          | Description                  |
|:--------|:-------------|:-----------------------------|
| GET     | `/health`    | Vérifie que le service tourne |
| POST    | `/decode/`   | Envoie une image, décode et parse |
| POST    | `/parse/`    | Envoie une chaîne brute, parse |
| POST    | `/generate/` | Génère un code-barres GS1 |

**POST `/decode/` paramètres (form-data)** :
- `file` : fichier image (obligatoire)
- `verbose` : booléen optionnel (`true` ou `false`)

**POST `/parse/` paramètres (JSON Body)** :
- `raw_data` : chaîne de caractères brute du code-barres (obligatoire)
- `barcode_format` : chaîne de caractères (ex: "GS1 DataMatrix") (optionnel)

**POST `/generate/` paramètres (JSON Body)** :
- `data` : données GS1 à encoder (ex: "01034531200000111719112510ABCD1234")
- `format` : format du code-barres (datamatrix, qrcode, code128, gs1-datamatrix, gs1-qrcode, gs1-128)
- `image_format` : format de l'image (png, jpeg, svg)
- `width` : largeur de l'image (50-1000 pixels)
- `height` : hauteur de l'image (50-1000 pixels)

---

## 📚 Exemples cURL

### Décodage de code-barres (Image)

**Scan simple**
```bash
curl -X POST https://gs1-decoder-api.rorworld.eu/decode/ \
  -F "file=@/path/to/your/imagetest.jpg" \
  -F "verbose=false"
```

### Parsing de données brutes (Texte)

**Parse simple**
```bash
curl -X 'POST' \
  'https://gs1-decoder-api.rorworld.eu/parse/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "raw_data": "01037604231900051725042310AB-123\u001d21S12345",
    "barcode_format": "GS1 DataMatrix"
  }'
```

**Résultat attendu pour `/parse/`**
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
        "confidence": 1.0,
        "characteristics": {
          "length": 42,
          "content_type": "alphanumeric",
          "contains_special_chars": true,
          "contains_fnc1": true,
          "potential_leading_ais": ["01", "17", "10", "21"]
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