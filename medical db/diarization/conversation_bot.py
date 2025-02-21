# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from docAppoint import graph

# app = FastAPI()

# # Request model for user input
# class UserInput(BaseModel):
#     message: str

# @app.post("/chat/")
# def chat(user_input: UserInput):
#     try:
#         config = {'configurable': {'thread_id': '1'}}
#         response = graph.invoke({"messages": [user_input.message]}, config=config)
#         return {"response": response["messages"][-1].content}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # @app.get("/")
# # def read_root():
# #     return {"message": "Welcome to the DocAppoint Chatbot API!"}
import requests
import tempfile
import subprocess
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from docAppoint import graph  # ✅ Import chatbot from docAppoint, not conversation_bot itself

app = FastAPI()

class UserInput(BaseModel):
    message: str

# ✅ Define chat function instead of importing it to avoid circular import
def chat(user_input: UserInput):
    """Processes user message and returns chatbot response."""
    try:
        config = {'configurable': {'thread_id': '1'}}
        response = graph.invoke({"messages": [user_input.message]}, config=config)
        return {"response": response["messages"][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/")
def chat_endpoint(user_input: UserInput):
    """Receives text and returns chatbot response."""
    return chat(user_input)

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    """Receives an audio file, converts to WAV (if needed), transcribes it, and sends to chatbot."""
    try:
        # Create a temporary file to save the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_input:
            temp_input.write(await file.read())
            temp_input_path = temp_input.name

        # Convert M4A to WAV using FFmpeg (if needed)
        temp_wav_path = temp_input_path.replace(".m4a", ".wav")
        subprocess.run(["ffmpeg", "-i", temp_input_path, temp_wav_path, "-y"], check=True)

        # Send WAV file to transcription API
        with open(temp_wav_path, "rb") as audio_file:
            files = {"audio": (file.filename.replace(".m4a", ".wav"), audio_file, "audio/wav")}
            transcription_response = requests.post(
                "http://fs.wiseyak.com:8048/transcribe_english",
                files=files
            )

        # Check for errors in transcription
        if transcription_response.status_code != 200:
            raise HTTPException(
                status_code=transcription_response.status_code,
                detail=f"Transcription API failed: {transcription_response.text}"
            )

        # Read response as plain text
        transcribed_text = transcription_response.text.strip()
        print("Transcription Response:", transcribed_text)  # Debugging log

        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Empty transcription received")

        # ✅ Call the chatbot function locally instead of importing it
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

@app.get("/")
def read_root():
    return {"message": "Welcome to the DocAppoint Chatbot API!"}
