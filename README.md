# ASR
This is a technical assessment repository.


## Getting started

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

Run the main application:

```bash
python src/main.py
```

## Project structure
```
./
├── .git/
├── .gitignore
├── README.md
├── requirements.txt
├── asr/
│   ├── asr_api.py
│   └── cv-decode.py
├── deployment-design/
├── elastic-backend/
└── search-ui/
```

## Access

| Component | URL |
|-----------|-----|
| ASR API | http://localhost:8001/asr |
| Elastic Backend | http://localhost:8000 |
| Elasticsearch | http://localhost:9200 |
| Search UI | http://localhost:3000 |