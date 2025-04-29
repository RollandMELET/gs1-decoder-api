# Dockerfile
FROM python:3.10-slim

# 1) Prérequis système : Java + libdmtx
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      default-jre-headless \
      libdmtx-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pillow pylibdmtx

# 3) Copie ZXing (assure-toi que ./zxing est dans le contexte build)
COPY zxing /zxing

# 4) Copie du code source
COPY . /app

# 5) Expose et lancement
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
