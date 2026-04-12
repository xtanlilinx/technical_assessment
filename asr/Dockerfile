FROM python:3.11-slim


RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY asr/ ./asr/

EXPOSE 8001

CMD ["uvicorn", "asr.asr_api:app", "--host", "0.0.0.0", "--port", "8001"]