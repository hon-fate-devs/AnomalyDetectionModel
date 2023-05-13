FROM python:3.10-alpine
LABEL authors="hon-fate-devs"

WORKDIR /app

COPY requirements.txt .

RUN apk --no-cache add musl-dev linux-headers g++ && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "./producer.py"]

