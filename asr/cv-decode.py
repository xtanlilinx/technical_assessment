import os
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from mutagen.mp3 import MP3 
from pathlib import Path
import time
import subprocess 

# CONFIGURATION
CONFIG = {
    "data_root": "./common_voice",
    "subfolder": "cv-valid-dev",
    "csv_filename": "cv-valid-dev.csv",
    "asr_api_url": "http://localhost:8001/asr",
    "batch_size": 10, # Process files in batches
    "max_audio_length": 30, # Long audios might be computationally expensive > to prevent OOMs errors, skip them and log as [TOO LONG]
    "temp_log": "transcription_temp.csv" # Temporary file to store batch results before merging into master CSV
}

ROOT = Path(CONFIG["data_root"]).resolve()
AUDIO_DIR = ROOT / CONFIG["subfolder"] / CONFIG["subfolder"]
CSV_PATH = Path(CONFIG["csv_filename"])
TEMP_PATH = Path(CONFIG["temp_log"])


# def ensure_api_is_running():
#     """Checks if the Docker container is running; starts it if not."""
#     try:
#         # Check current status using docker inspect
#         status = subprocess.check_output(
#             f'docker inspect -f "{{{{.State.Running}}}}" {CONFIG["asr_container_name"]}', 
#             shell=True
#         ).decode().strip()
        
#         if status == 'false':
#             print(f"Container {CONFIG['asr_container_name']} is stopped. Restarting...")
#             subprocess.run(f"docker start {CONFIG['asr_container_name']}", shell=True)
#             print("Waiting 10s for API to warm up...")
#             time.sleep(10)
#     except Exception as e:
#         print(f"Docker check failed: {e}. Check if Docker Desktop is running.")


def get_asr_api():
    """Creates a requests session with retry logic"""

    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=3, # Exponential sleep: 3s, 9s, 27s...
        status_forcelist=[429, 500, 502, 503, 504], # Retry on these HTTP status codes
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Initialize session globally
session = get_asr_api()

def process_batch(file_batch_paths):
    files_to_send = []
    opened_files = []
    batch_results = []
    
    for path in file_batch_paths:
        fname = os.path.basename(path)
        rel_path = f"{CONFIG['subfolder']}/{fname}"
        
        # Filter out long audio files before sending to API
        try:
            audio = MP3(path)
            if audio.info.length > CONFIG["max_audio_length"]:
                batch_results.append({"filename": rel_path, "generated_text": "[TOO LONG]"})
                continue
        except Exception:
            batch_results.append({"filename": rel_path, "generated_text": "[CORRUPT]"})
            continue

        f = open(path, "rb")
        opened_files.append(f)
        files_to_send.append(("file", (fname, f, "audio/mpeg")))


    # Send batch to ASR API with retries
    if files_to_send:
        try:
            print(f"Sending batch of {len(files_to_send)} files to ASR API...")
            response = session.post(CONFIG["asr_api_url"], files=files_to_send, timeout=(5, 300)) # timeout=(connect_timeout, read_timeout)
            response.raise_for_status() # Raise exception for 4xx/5xx
            
            api_outputs = response.json()
            if isinstance(api_outputs, dict): api_outputs = [api_outputs]
            
            for i, result in enumerate(api_outputs):
                actual_fname = files_to_send[i][1][0]
                batch_results.append({
                    "filename": f"{CONFIG['subfolder']}/{actual_fname}",
                    "generated_text": result.get("transcription", "")
                })
        except Exception as e:
            print(f"Batch Request Failed: {e}")
            # Log failed files as errors
            for item in files_to_send:
                batch_results.append({"filename": f"{CONFIG['subfolder']}/{item[1][0]}", "generated_text": "[API ERROR]"})
        finally:
            for f in opened_files: f.close()
            
    return batch_results


if __name__ == "__main__":

    # Gather all audio files in AUDIO_DIR
    audio_files = [os.path.join(AUDIO_DIR, f) for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")]
    
    # Processing Loop
    print(f"Transcribing {len(audio_files)} files...")
    for i in range(0, len(audio_files), CONFIG["batch_size"]):
        batch = audio_files[i : i + CONFIG["batch_size"]]
        results = process_batch(batch)
        
        if results:
            # Intermediate logging to CSV
            batch_df = pd.DataFrame(results)
            write_header = not TEMP_PATH.exists()
            batch_df.to_csv(TEMP_PATH, mode='a', header=write_header, index=False)
        print(f"Batch {i//CONFIG['batch_size'] + 1} logged.")

    # Merge into Master CSV
    if TEMP_PATH.exists():
        print("Merging transcriptions into master CSV...")
        master_df = pd.read_csv(CSV_PATH)
        temp_df = pd.read_csv(TEMP_PATH)
        
        # Merge the new column 'generated_text' onto the original CSV based on 'filename'
        final_df = pd.merge(master_df, temp_df, on="filename", how="left")
        
        # Save file
        final_df.to_csv(CSV_PATH, index=False)
        print(f"Master file {CONFIG['csv_filename']} updated.")

        # Delete the temporary file
        os.remove(TEMP_PATH)
        print(f"Temporary file {CONFIG['temp_log']} deleted.")
    else:
        print("No transcriptions were generated.")


# Test
# python -m cv-decode