# Dockerfile pour JPype + Node.js/bwip-js (GS1 DataMatrix conformes)
FROM python:3.10-slim

# Variables de build pour bwip-js
ARG NODEJS_VERSION=18.x
ARG BWIPJS_VERSION=latest

ARG ZXING_VERSION=3.4.1
# JCOMMANDER_VERSION n'est plus nécessaire

# 1) Installation dépendances système + Node.js pour bwip-js (GS1 conforme)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      # Node.js setup (PRIORITÉ pour bwip-js GS1 DataMatrix)
      curl \
      gnupg \
      ca-certificates && \
    # Installation Node.js 18.x LTS (requis pour bwip-js)
    curl -fsSL https://deb.nodesource.com/setup_${NODEJS_VERSION} | bash - && \
    apt-get install -y \
      # Node.js pour bwip-js (solution GS1 recommandée)
      nodejs \
      # Java Runtime Environment (Important pour JPype/ZXing Java)
      default-jre-headless \
      # Dépendance C pour pylibdmtx
      libdmtx-dev \
      # Outil pour télécharger les JARs
      wget \
      # Ghostscript pour treepoem
      ghostscript \
      # ImageMagick pour diverses conversions
      libmagickwand-dev && \
    # Installation bwip-js globalement (backend BWIPP natif)
    npm install -g bwip-js@${BWIPJS_VERSION} && \
    # Vérification installations
    node --version && \
    npm list -g bwip-js && \
    # Nettoyage complet pour optimiser taille image
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* ~/.npm

# 2) Récupération des JARs ZXing (Core et JavaSE)
RUN mkdir -p /zxing && \
    wget -q https://repo1.maven.org/maven2/com/google/zxing/core/${ZXING_VERSION}/core-${ZXING_VERSION}.jar \
      -O /zxing/core.jar && \
    wget -q https://repo1.maven.org/maven2/com/google/zxing/javase/${ZXING_VERSION}/javase-${ZXING_VERSION}.jar \
      -O /zxing/javase.jar && \
    # jcommander.jar n'est plus téléchargé
    ls -l /zxing

WORKDIR /app

# 3) Dépendances Python (inclut JPype1 via requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Code source
COPY . /app

# 5) Port
EXPOSE 8000

# 6) Commande de lancement
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]