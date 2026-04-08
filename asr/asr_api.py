from fastapi import FastAPI, HTTPException, UploadFile, File
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import librosa
import uvicorn
import io

app = FastAPI()

# (2b) Test API endpoint 
@app.get("/ping")
async def ping():
    return {"message": "pong"}

# (2c) Load model and processor once when starting the API
MODEL_ID = "facebook/wav2vec2-large-960h"
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

@app.post("/asr")
async def transcribe(file: UploadFile = File(...)):
    """
    Endpoint to receive an audio file, transcribe it using the Wav2Vec2 model, and return the transcription and duration.
    Args:
        file (UploadFile): The uploaded audio file.
    Returns:
        dict: A dictionary containing the transcription and duration.
    """
    
    try:
        # 1. Read the uploaded file into memory
        audio_content = await file.read()
        
        # 2. Use io.BytesIO so librosa can read from memory
        speech, sr = librosa.load(io.BytesIO(audio_content), sr=16000)
        
        # 3. Calculate duration
        duration_seconds = len(speech) / sr
        
        # 4. Preprocess the audio for the model - this will handle padding and sampling rate
        input_values = processor(speech, return_tensors="pt", sampling_rate=sr).input_values
        # 5. Inference with no_grad for efficiency 
        with torch.no_grad():
            # 6. Get logits and decode to predicted token IDs
            logits = model(input_values).logits
        
        # 7. Decode the predicted token IDs to text 
        predicted_ids = torch.argmax(logits, dim=-1)
        # 8. Decode to transcription
        transcription = processor.batch_decode(predicted_ids)[0]
        
        return {
                    "transcription": transcription,
                    "duration": f"{duration_seconds:.1f}"
                }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 



# Test the API with curl (adjust file path to your local audio file)
# curl -F "file=@C:\Users\xtanl\OneDrive\Desktop\technical_assessment\asr\common_voice\cv-valid-dev\cv-valid-dev\sample-000000.mp3" http://localhost:8001/asr