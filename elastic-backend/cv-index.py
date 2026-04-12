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


def create_index_with_mapping():
    
    if es.indices.exists(index=CONFIG["es_index"]):
        es.indices.delete(index=CONFIG["es_index"])
        print(f"Deleted old index: {CONFIG['es_index']}")

    # Define Mapping: Base fields are 'text' for search, '.keyword' subfields are for facets
    mapping = {
        "mappings": {
            "properties": {
                "generated_text": {"type": "text"},
                "filename": {"type": "keyword"},
                "gender": {
                    "type": "text", 
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "accent": {
                    "type": "text", 
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "age": {
                    "type": "text", 
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "duration": {
                    "type": "text", 
                    "fields": {"keyword": {"type": "keyword"}}
                }
            }
        }
    }
    
    es.indices.create(index=CONFIG["es_index"], body=mapping)
    print("Created index with multi-field mapping.")

# (4e) Index files in Elasticsearch
def index_csv(file_path):
    if not file_path.exists():
        print(f"Error: CSV not found at {file_path}")
        return
    
    # Create the correct index structure first
    create_index_with_mapping()
    
    df = pd.read_csv(file_path)
    df = df.fillna("")
    
    actions = [
        {
            "_index": CONFIG["es_index"],
            "_source": record
        }
        for record in df.to_dict(orient="records")
    ]
    
    # Use bulk API for efficient indexing
    helpers.bulk(es, actions)
    print(f"Indexed {len(actions)} records successfully.")

if __name__ == "__main__":
    index_csv(CSV_PATH)
