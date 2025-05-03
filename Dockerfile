# Dockerfile
FROM python:3.10-slim

# --- AJOUT: Définir les versions pour une gestion plus facile ---
ARG ZXING_VERSION=3.4.1
ARG JCOMMANDER_VERSION=1.78 # Version compatible et stable

# 1) Prérequis système : Java, libdmtx, wget et autres dépendances que vous aviez
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      # Paquets nécessaires :
      default-jre-headless \  # Java Runtime Environment
      libdmtx-dev \           # Dépendance C pour pylibdmtx
      wget \                  # Outil pour télécharger les JARs
      ghostscript \           # Conservé car présent initialement
      libmagickwand-dev && \  # Conservé car présent initialement
    # Nettoyage pour réduire la taille de l'image
    rm -rf /var/lib/apt/lists/*

# 2) Récupération des JARs ZXing JavaSE et JCommander nécessaires
#    Création du répertoire et téléchargement des deux JARs dans une seule couche RUN
RUN mkdir -p /zxing && \
    # Téléchargement du JAR principal de ZXing
    wget -q \
      https://repo1.maven.org/maven2/com/google/zxing/javase/${ZXING_VERSION}/javase-${ZXING_VERSION}.jar \
      -O /zxing/javase.jar && \
    # Téléchargement du JAR JCommander
    wget -q \
      https://repo1.maven.org/maven2/com/beust/jcommander/${JCOMMANDER_VERSION}/jcommander-${JCOMMANDER_VERSION}.jar \
      -O /zxing/jcommander.jar && \
    # Vérification optionnelle que les fichiers sont bien présents
    ls -l /zxing

WORKDIR /app

# 3) Dépendances Python
COPY requirements.txt .
# Utilisation de --no-cache-dir pour potentiellement réduire la taille
RUN pip install --no-cache-dir -r requirements.txt

# 4) Code source de l'application
COPY . /app

# Port exposé par l'application FastAPI/Uvicorn
EXPOSE 8000

# 5) Commande de lancement de l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]