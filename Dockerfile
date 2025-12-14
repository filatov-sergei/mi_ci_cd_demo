FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

ENV MODEL_VERSION=v1.0.0

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]