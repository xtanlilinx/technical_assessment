# Automatic Speech Recognition (ASR)
![Technical Assessment](https://img.shields.io/badge/Technical%20Assessment-purple?style=for-the-badge)
![AWS](https://img.shields.io/badge/AWS-orange?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-blue?style=for-the-badge)
![ElasticSearch](https://img.shields.io/badge/ElasticSearch-lightblue?style=for-the-badge)

A containerised ASR search platform featuring an Elasticsearch cluster and React Search-UI hosted on AWS EC2, using Python for automated bulk indexing of audio transcriptions.

### Deployment URL

| URL |   Status   | History |
| --- | ---------- | ------- |
| <img alt="" src="https://duckduckgo.com" height="13"> [EC2 - Search UI](http://ec2-13-250-112-203.ap-southeast-1.compute.amazonaws.com:3000) | ![Status](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fxtanlilinx%2Fstatus-page%2Frefs%2Fheads%2Fmaster%2Fhistory%2Fec-2-ta.yml&query=%24.status&label=Status&color&style=for-the-badge) | [Last Checked](https://github.com/xtanlilinx/status-page/commits/HEAD/history/ec-2-ta.yml) |

## Getting started
#### 1. Local Environment Setup  
Clone the repository and install dependencies for local development:
```bash
conda create -n env_name python=3.11
conda activate env_name
pip install -r requirements.txt
```

#### 2. ASR API
To explore and test the API interactively, visit http://localhost:8001/docs.

```bash
# Compose and build
docker build -t asr-api -f asr/Dockerfile .
docker run -p 8001:8001 asr-api 

# Single file load
curl -X POST http://localhost:8001/asr -F "file=@C:<path-to-audio-files>\common_voice\cv-valid-dev\cv-valid-dev\sample-000000.mp3"

# Multiple file load
curl -X POST http://localhost:8001/asr
  -F "file=@C:<path-to-audio-files>\common_voice\cv-valid-dev\cv-valid-dev\sample-000000.mp3"
  -F "file=@C:<path-to-audio-files>\common_voice\cv-valid-dev\cv-valid-dev\sample-000001.mp3"
  -F "file=@C:<path-to-audio-files>\common_voice\cv-valid-dev\cv-valid-dev\sample-000002.mp3"
```

#### 3. CV Decode
To run the bulk transcription in batches
```bash
cd asr
python -m cv-decode
```

## Project structure
```
./
├── asr/
│   ├── asr_api.py
│   ├── cv-decode.py
│   ├── cv-valid-dev.csv
│   └── Dockerfile
│
├── deployment-design/
│   └── design.pdf
│
├── elastic-backend/
│   ├── cv-index.py
│   └── Dockerfile
│
├── search-ui/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js
│   │   └── index.js
│   ├── Dockerfile
│   ├── package.json
│   └── package-lock.json
│
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── essay.pdf
├── README.md
└── requirements.txt
```
