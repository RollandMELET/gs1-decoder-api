FROM python:3.12-slim

RUN apt-get update && apt-get install -y default-jre wget

RUN mkdir /zxing
WORKDIR /zxing
RUN wget https://repo1.maven.org/maven2/com/google/zxing/javase/3.5.1/javase-3.5.1.jar

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
