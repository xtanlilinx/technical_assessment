import requests
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor


def get_asr_api(audio_file_path):
    """
    Transcribe an audio file in asr_api.py and return the transcription and duration.
    Args:
        audio_file_path (str): The file path to the audio file to be transcribed.
    Returns:
        dict: A dictionary containing the audio_path, transcription and duration.
    """
        
    url = "http://localhost:8001/asr"
    
    if not os.path.exists(audio_file_path):
        return {"transcription": "File not found", "duration": "0", "audio_path": audio_file_path}

    try:
        with open(audio_file_path, "rb") as f:
            # Use the actual filename from the path
            fname = os.path.basename(audio_file_path)
            audio_file = {"file": (fname, f, "audio/mpeg")}
            response = requests.post(url, files=audio_file)

        if response.status_code == 200:
            output = response.json()
            # Clean up the audio_path to match your CSV 'filename' column
            output["audio_path"] = f"cv-valid-dev/{fname}"

            # print(f"Status Code: {response.status_code}")
            # print(f"Response: {response.json()}")
            return output
        else:
            return {"transcription": f"Error {response.status_code}", "duration": "0", "audio_path": f"cv-valid-dev/{fname}"}
    
    except Exception as e:
        return {"transcription": f"Exception: {str(e)}", "duration": "0", "audio_path": f"cv-valid-dev/{fname}"}



if __name__ == "__main__":

    # (2d) Process all audio files in the directory and update the CSV
    audio_dir = "common_voice/cv-valid-dev/cv-valid-dev"
    if not os.path.exists(audio_dir):
        print(f"Directory {audio_dir} not found.")
    else:
        audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(".mp3")]
        print(f"Processing {len(audio_files)} files...")
        
        # This sends 5 files to the server simultaneously
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(get_asr_api, audio_files))
        results_df = pd.DataFrame(results)

        if not results_df.empty:
            results_df = results_df[['audio_path', 'transcription']].rename(columns={'transcription': 'generated_text'})
            
            fp = "common_voice/cv-valid-dev.csv"
            original_df = pd.read_csv(fp)
            
            merged_df = pd.merge(original_df, results_df, left_on="filename", right_on="audio_path", how="inner").drop(columns=["audio_path"])
            merged_df.to_csv(fp, index=False)
            print(f"Successfully updated {fp}")
        else:
            print("No results to write.")