# 📦 GS1 Decoder API

Microservice pour décoder des codes-barres GS1 (1D/2D) à partir d'une image, avec parsing complet et support verbose.

---

## ✨ Fonctionnalités

- 🔎 Scan d'images vers codes-barres GS1.
- 🧩 Parsing Application Identifiers (AI) longueur fixe et variable.
- 📜 Mode `verbose` pour analyse détaillée.
- 📦 Docker-ready, Coolify-ready.
- 🔥 Déploiement en un clic.
- 🩺 Endpoint `/health` pour monitoring.
- 📚 Documentation interactive via Swagger UI (`/docs`) et Redoc (`/redoc`).

---

## ⚙️ Déploiement rapide avec Coolify

1. Créer un projet "Docker build" dans Coolify.
2. Uploader ce projet.
3. Build + Exposer le port 8000.
4. 🎉 API opérationnelle.

---

## 🔥 API Endpoints

| Méthode | URL          | Description                  |
|:--------|:-------------|:-----------------------------|
| GET     | `/health`    | Vérifie que le service tourne |
| POST    | `/decode/`   | Envoie une image, decode et parse |

**POST `/decode/` paramètres** :
- `file` : fichier image (obligatoire)
- `verbose` : booléen optionnel (`true` ou `false`)

---

## 📚 Exemples cURL

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
        "PROD_DATE": "25-04-23",
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
          "value": "03760423190005"
        },
        {
          "ai": "11",
          "name": "PROD_DATE",
          "value": "25-04-23"
        },
        {
          "ai": "3100",
          "name": "NET_WEIGHT_KG",
          "value": "12.000"
        },
        {
          "ai": "21",
          "name": "SERIAL",
          "value": "00000030"
        },
        {
          "ai": "90",
          "name": "INTERNAL",
          "value": "7391023"
        },
        {
          "ai": "93",
          "name": "INTERNAL3",
          "value": "DHA"
        },
        {
          "ai": "94",
          "name": "INTERNAL4",
          "value": "UP"
        },
        {
          "ai": "95",
          "name": "INTERNAL5",
          "value": "ENVELOPPE_NUE_4UF"
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
    "supported_codes": ["DataMatrix", "QR Code", "GS1-128"],
    "api_version": "1.0.0"
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

## 📚 Ressources

Le dossier `resources/` contient toutes les informations nécessaires concernant les Application Identifiers (AI) de GS1, incluant :
- La liste complète des AI disponibles
- La documentation officielle des formats
- Les spécifications de longueur fixe et variable
- Les règles de formatage et d'interprétation

Ces ressources seront utilisées pour implémenter le support complet de tous les AI GS1 existants, l'une des améliorations futures prioritaires.

---

## 📄 Licence

Open Source sous licence MIT.
Fais-en ce que tu veux, améliore-le, utilise-le, transforme-le 🚀.

---

## 🛠 Idées d'améliorations futures

- Ajouter support complet pour TOUS les AI GS1 existants.
- Détection automatique du format du code (QR Code, Datamatrix, etc.).
- Génération possible de codes-barres en retour.
- UI Web minimaliste pour uploader une image facilement.

---