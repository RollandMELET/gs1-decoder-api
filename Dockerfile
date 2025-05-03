# Dockerfile pour JPype (syntaxe commentaires corrigée)
FROM python:3.10-slim

ARG ZXING_VERSION=3.4.1
# JCOMMANDER_VERSION n'est plus nécessaire

# 1) Prérequis système (Java est essentiel pour JPype)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      # Java Runtime Environment (Important pour JPype/ZXing Java)
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