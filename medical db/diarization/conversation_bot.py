

import requests
import tempfile
import subprocess
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from docAppoint import graph  # Import the chatbot graph from docAppont.py
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for the frontend at localhost:8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    message: str

# Helper function to safely extract message content.
def get_message_content(message):
    try:
        return message.content
    except AttributeError:
        if isinstance(message, dict):
            return message.get("content", str(message))
        return str(message)

# Define chat function to process user messages using the chatbot graph.
def chat(user_input: UserInput):
    """Processes patient input and returns the chatbot's medical response."""
    try:
        config = {'configurable': {'thread_id': '1'}}
        response = graph.invoke({"messages": [user_input.message]}, config=config)
        last_message = response["messages"][-1]
        content = get_message_content(last_message)
        return {"response": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/")
def chat_endpoint(user_input: UserInput):
    """Endpoint that receives patient text and returns the medical chatbot response."""
    return chat(user_input)

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    """Endpoint that receives an audio file, converts it if necessary, transcribes it, and sends it to the medical chatbot."""
    try:
        # Create a temporary file to save the uploaded audio.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_input:
            temp_input.write(await file.read())
            temp_input_path = temp_input.name

        # Convert M4A to WAV using FFmpeg.
        temp_wav_path = temp_input_path.replace(".m4a", ".wav")
        subprocess.run(["ffmpeg", "-i", temp_input_path, temp_wav_path, "-y"], check=True)

        # Send the WAV file to the transcription API.
        with open(temp_wav_path, "rb") as audio_file:
            files = {"audio": (file.filename.replace(".m4a", ".wav"), audio_file, "audio/wav")}
            transcription_response = requests.post(
                "http://fs.wiseyak.com:8048/transcribe_english",
                files=files
            )

        if transcription_response.status_code != 200:
            raise HTTPException(
                status_code=transcription_response.status_code,
                detail=f"Transcription API failed: {transcription_response.text}"
            )

        transcribed_text = transcription_response.text.strip()
        print("Transcription Response:", transcribed_text)

        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Empty transcription received")

        chatbot_response = chat(UserInput(message=transcribed_text))
        return {
            "transcription": transcribed_text,
            "chatbot_response": chatbot_response["response"]
        }

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error converting audio file. Ensure FFmpeg is installed.")
    except Exception as e:
        print("Error in /transcribe/:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
