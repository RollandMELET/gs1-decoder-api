# Dockerfile
FROM python:3.10-slim

# 1) Prérequis système : Java, libdmtx et wget
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      default-jre-headless \
      libdmtx-dev \
      wget \
      ghostscript \
      libmagickwand-dev && \
    rm -rf /var/lib/apt/lists/*

# 2) Récupération du JAR ZXing JavaSE
RUN mkdir -p /zxing && \
    wget -q \
      https://repo1.maven.org/maven2/com/google/zxing/javase/3.4.1/javase-3.4.1.jar \
      -O /zxing/javase.jar

WORKDIR /app

# 3) Dépendances Python 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Code source
COPY . /app

EXPOSE 8000

# 5) Lancement
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
