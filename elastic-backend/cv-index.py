import os
import pandas as pd
from pathlib import Path
from elasticsearch import Elasticsearch, helpers


# CONFIGURATION (Change here if needed)
CONFIG = {
    "data_root": "./asr",
    "csv_filename": "cv-valid-dev.csv",
    "es_host": os.getenv("ES_HOST", "http://localhost:9200"),
    "es_index": "cv-transcriptions"
}

ROOT = Path(CONFIG["data_root"]).resolve()
CSV_PATH = ROOT / CONFIG["csv_filename"]
connection_pool = CONFIG["es_host"].split(",")
# Connect to the container
es = Elasticsearch(connection_pool, request_timeout=30)

# (4e) Index files in Elasticsearch
def index_csv(file_path):
    if not file_path.exists():
        print(f"Error: CSV not found at {file_path}")
        return
    
    df = pd.read_csv(file_path)
    df = df.fillna("")
    actions = [
        {
            "_index": CONFIG["es_index"],
            "_source": record
        }
        for record in df.to_dict(orient="records")
    ]
    
    # Use bulk API to index all records at once
    helpers.bulk(es, actions)
    print(f"Indexed {len(actions)} records successfully")

if __name__ == "__main__":
    index_csv(CSV_PATH)