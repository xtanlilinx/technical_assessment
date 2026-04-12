FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY asr/cv-valid-dev.csv ./asr/cv-valid-dev.csv
COPY elastic-backend/ ./elastic-backend/

CMD ["python", "elastic-backend/cv-index.py"]