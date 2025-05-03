# Dockerfile
FROM python:3.10-slim

# --- Définir les versions pour une gestion plus facile ---
ARG ZXING_VERSION=3.4.1
ARG JCOMMANDER_VERSION=1.78 # Version compatible et stable

# 1) Prérequis système : Java, libdmtx, wget et autres dépendances
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      # Java Runtime Environment
      default-jre-headless \
      # Dépendance C pour pylibdmtx
      libdmtx-dev \
      # Outil pour télécharger les JARs
      wget \
      # Conservé car présent initialement
      ghostscript \
      # Conservé car présent initialement
      libmagickwand-dev && \
    # Nettoyage pour réduire la taille de l'image
    rm -rf /var/lib/apt/lists/*

# 2) Récupération des JARs ZXing (Core, JavaSE) et JCommander nécessaires
RUN mkdir -p /zxing && \
    # --- AJOUT: Téléchargement du JAR ZXing Core ---
    wget -q \
      https://repo1.maven.org/maven2/com/google/zxing/core/${ZXING_VERSION}/core-${ZXING_VERSION}.jar \
      -O /zxing/core.jar && \
    # Téléchargement du JAR ZXing JavaSE
    wget -q \
      https://repo1.maven.org/maven2/com/google/zxing/javase/${ZXING_VERSION}/javase-${ZXING_VERSION}.jar \
      -O /zxing/javase.jar && \
    # Téléchargement du JAR JCommander
    wget -q \
      https://repo1.maven.org/maven2/com/beust/jcommander/${JCOMMANDER_VERSION}/jcommander-${JCOMMANDER_VERSION}.jar \
      -O /zxing/jcommander.jar && \
    # Vérification optionnelle que les TROIS fichiers sont bien présents
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