# Dockerfile (RESTE IDENTIQUE au précédent)
FROM python:3.10-slim

ARG ZXING_VERSION=3.4.1
ARG JCOMMANDER_VERSION=1.78

# 1) Prérequis système (inchangé)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      default-jre-headless \
      libdmtx-dev \
      wget \
      ghostscript \
      libmagickwand-dev && \
    rm -rf /var/lib/apt/lists/*

# 2) Récupération des JARs (inchangé - garder les 3 JARs)
RUN mkdir -p /zxing && \
    wget -q https://repo1.maven.org/maven2/com/google/zxing/core/${ZXING_VERSION}/core-${ZXING_VERSION}.jar -O /zxing/core.jar && \
    wget -q https://repo1.maven.org/maven2/com/google/zxing/javase/${ZXING_VERSION}/javase-${ZXING_VERSION}.jar -O /zxing/javase.jar && \
    wget -q https://repo1.maven.org/maven2/com/beust/jcommander/${JCOMMANDER_VERSION}/jcommander-${JCOMMANDER_VERSION}.jar -O /zxing/jcommander.jar && \
    ls -l /zxing

WORKDIR /app

# 3) Dépendances Python (MODIFIÉ via requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt # Installera pyzxing maintenant

# 4) Code source (inchangé)
COPY . /app

# 5) Port (inchangé)
EXPOSE 8000

# 6) Commande de lancement (inchangé)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]