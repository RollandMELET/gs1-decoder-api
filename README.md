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
|:--------|:-------------|:------------------------------|
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

**Scan verbose**
```bash
curl -X POST https://gs1-decoder-api.rorworld.eu/decode/ \
  -F "file=@/Users/rollandmelet/Développement/Projets/gs1-decoder-api/imagetest.jpg" \
  -F "verbose=true"
```

**Healthcheck**
```bash
curl https://gs1-decoder-api.rorworld.eu/health
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

---

## 🛠 Idées d'améliorations futures

- Ajouter support complet pour TOUS les AI GS1 existants.
- Détection automatique du format du code (QR Code, Datamatrix, etc.).
- Génération possible de codes-barres en retour.
- UI Web minimaliste pour uploader une image facilement.

---
