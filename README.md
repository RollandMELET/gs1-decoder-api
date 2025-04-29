<<<<<<< HEAD
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
curl -X POST http://votre-domaine/decode/ -F "file=@/chemin/image.png" -F "verbose=false"
=======
# GS1 Decoder API

Microservice pour décoder des codes-barres GS1 (1D/2D) à partir d'une image, avec parsing complet et mode verbose.

## Fonctionnalités
- Scan image → décodage code-barres.
- Supporte plusieurs codes dans la même image.
- Parsing GS1 (AI à longueur fixe et variable).
- Mode `verbose` true/false.
- Healthcheck `/health`.
- Documentation Swagger `/docs` et Redoc `/redoc`.

## Déploiement avec Coolify
1. Créer un nouveau projet Docker dans Coolify.
2. Uploader ce ZIP.
3. Build & Deploy (port 8000).

## Utilisation API
- `POST /decode/`
  - `file`: fichier image
  - `verbose`: (bool) optionnel
- `GET /health/`

## Exemple cURL

**Simple scan**
```bash
curl -X POST http://votre-domaine/decode/ \
 -F "file=@/chemin/image.png" \
 -F "verbose=false"
>>>>>>> f6eba4f (Initial commit - upload project files)
```

**Scan verbose**
```bash
<<<<<<< HEAD
curl -X POST http://votre-domaine/decode/ -F "file=@/chemin/image.png" -F "verbose=true"
=======
curl -X POST http://votre-domaine/decode/ \
 -F "file=@/chemin/image.png" \
 -F "verbose=true"
>>>>>>> f6eba4f (Initial commit - upload project files)
```

**Healthcheck**
```bash
curl http://votre-domaine/health
```
<<<<<<< HEAD

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
=======
>>>>>>> f6eba4f (Initial commit - upload project files)
