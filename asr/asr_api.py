from fastapi import FastAPI, HTTPException, UploadFile, File
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from typing import List
import torch
import torchaudio
import torchaudio.transforms as T
import uvicorn
import io
import os


app = FastAPI()

# (2b) Test API endpoint 
@app.get("/ping")
async def ping():
    return {"message": "pong"}

# (2c) Load model and processor once when starting the API
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_ID = os.getenv("MODEL_ID", "facebook/wav2vec2-large-960h")
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID).to(DEVICE)


@app.post("/asr")
async def transcribe(file: List[UploadFile] = File(...)):
    """
    Bulk ASR Endpoint: Accepts multiple files under the 'file' key.
    Args:        
        file (List[UploadFile]): A list of uploaded audio files.
    Returns:        
        List[dict]: 
        A list of dictionaries, each containing the transcription and duration for the corresponding audio file.
        If only one file is sent, returns a single dictionary instead of a list.
    """
    try:
        speeches = []
        durations = []
        
        # Process all uploaded files into memory
        for uploaded_file in file:
            audio_content = await uploaded_file.read()
            # Load into a tensor and preprocess
            waveform, sample_rate = torchaudio.load(io.BytesIO(audio_content), format="mp3")

            # Resample to 16kHz if necessary
            if sample_rate != 16000:
                resampler = T.Resample(sample_rate, 16000)
                waveform = resampler(waveform)

            # Convert to mono (average across channels) to match Wav2Vec2's expected input shape
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            # Wav2Vec2 expects a 1D array
            speech = waveform.squeeze().numpy()
            
            speeches.append(speech)
            durations.append(len(speech) / 16000)

        # Batch preprocessing (padding=True handles different lengths)
        inputs = processor(speeches, return_tensors="pt", padding=True, sampling_rate=16000).to(DEVICE)
        
        # Batch Inference
        with torch.no_grad():
            logits = model(inputs.input_values).logits
        
        # Batch Decode
        predicted_ids = torch.argmax(logits, dim=-1)
        transcriptions = processor.batch_decode(predicted_ids)

        # Output
        output = []
        for i in range(len(transcriptions)):
            output.append({
                "transcription": transcriptions[i],
                "duration": f"{durations[i]:.1f}"
            })
        # If only one file was sent, return just the dict instead of a list
        return output if len(output) > 1 else output[0]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 