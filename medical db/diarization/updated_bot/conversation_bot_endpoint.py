# import requests
# import tempfile
# import subprocess
# from fastapi import FastAPI, HTTPException, UploadFile, File
# from pydantic import BaseModel
# from bot_logic import graph  # Import the chatbot graph from docAppont.py
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class UserInput(BaseModel):
#     message: str

# # Helper function to safely extract message content.
# def get_message_content(message):
#     try:
#         return message.content
#     except AttributeError:
#         if isinstance(message, dict):
#             return message.get("content", str(message))
#         return str(message)

# def chat(user_input: UserInput):
#     """Processes patient input and returns the chatbot's medical response."""
#     try:
#         config = {'configurable': {'thread_id': '1'}}
#         response = graph.invoke({"messages": [user_input.message]}, config=config)
#         last_message = response["messages"][-1]
#         content = get_message_content(last_message)
#         return {"response": content}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/chat/")
# def chat_endpoint(user_input: UserInput):
#     """Endpoint that receives patient text and returns the medical chatbot response."""
#     return chat(user_input)

# @app.post("/transcribe/")
# async def transcribe_audio(file: UploadFile = File(...)):
#     """Endpoint that receives an audio file, converts it if necessary, transcribes it, and sends it to the medical chatbot."""
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_input:
#             temp_input.write(await file.read())
#             temp_input_path = temp_input.name

#         temp_wav_path = temp_input_path.replace(".m4a", ".wav")
#         subprocess.run(["ffmpeg", "-i", temp_input_path, temp_wav_path, "-y"], check=True)

#         with open(temp_wav_path, "rb") as audio_file:
#             files = {"audio": (file.filename.replace(".m4a", ".wav"), audio_file, "audio/wav")}
#             transcription_response = requests.post(
#                 "http://fs.wiseyak.com:8048/transcribe_english",
#                 files=files
#             )

#         if transcription_response.status_code != 200:
#             raise HTTPException(
#                 status_code=transcription_response.status_code,
#                 detail=f"Transcription API failed: {transcription_response.text}"
#             )

#         transcribed_text = transcription_response.text.strip()
#         print("Transcription Response:", transcribed_text)

#         if not transcribed_text:
#             raise HTTPException(status_code=400, detail="Empty transcription received")

#         chatbot_response = chat(UserInput(message=transcribed_text))
#         return {
#             "transcription": transcribed_text,
#             "chatbot_response": chatbot_response["response"]
#         }

#     except subprocess.CalledProcessError:
#         raise HTTPException(status_code=500, detail="Error converting audio file. Ensure FFmpeg is installed.")
#     except Exception as e:
#         print("Error in /transcribe/:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))



# import requests
# import tempfile
# import subprocess
# from fastapi import FastAPI, HTTPException, UploadFile, File
# from pydantic import BaseModel
# from bot_logic import graph  # Import the chatbot graph from docAppont.py
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class UserInput(BaseModel):
#     message: str

# # Helper function to safely extract message content.
# def get_message_content(message):
#     try:
#         return message.content
#     except AttributeError:
#         if isinstance(message, dict):
#             return message.get("content", str(message))
#         return str(message)

# def chat(user_input: UserInput):
#     """Processes patient input and returns the chatbot's medical response."""
#     try:
#         config = {'configurable': {'thread_id': '1'}}
#         response = graph.invoke({"messages": [user_input.message]}, config=config)
#         last_message = response["messages"][-1]
#         content = get_message_content(last_message)
#         return {"response": content}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/chat/")
# def chat_endpoint(user_input: UserInput):
#     """Endpoint that receives patient text and returns the medical chatbot response."""
#     return chat(user_input)

# @app.post("/transcribe/")
# async def transcribe_audio(file: UploadFile = File(...)):
#     """Endpoint that receives an audio file, converts it if necessary, transcribes it, and sends it to the medical chatbot."""
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_input:
#             temp_input.write(await file.read())
#             temp_input_path = temp_input.name

#         temp_wav_path = temp_input_path.replace(".m4a", ".wav")
#         subprocess.run(["ffmpeg", "-i", temp_input_path, temp_wav_path, "-y"], check=True)

#         with open(temp_wav_path, "rb") as audio_file:
#             files = {"audio": (file.filename.replace(".m4a", ".wav"), audio_file, "audio/wav")}
#             transcription_response = requests.post(
#                 "http://fs.wiseyak.com:8048/transcribe_english",
#                 files=files
#             )

#         if transcription_response.status_code != 200:
#             raise HTTPException(
#                 status_code=transcription_response.status_code,
#                 detail=f"Transcription API failed: {transcription_response.text}"
#             )

#         transcribed_text = transcription_response.text.strip()
#         print("Transcription Response:", transcribed_text)

#         if not transcribed_text:
#             raise HTTPException(status_code=400, detail="Empty transcription received")

#         chatbot_response = chat(UserInput(message=transcribed_text))
#         return {
#             "transcription": transcribed_text,
#             "chatbot_response": chatbot_response["response"]
#         }

#     except subprocess.CalledProcessError:
#         raise HTTPException(status_code=500, detail="Error converting audio file. Ensure FFmpeg is installed.")
#     except Exception as e:
#         print("Error in /transcribe/:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))



# this code takes the summary feild from frontend, so we modify the summary to be get from the latest json file in code bellow this code
import os
import json
import requests
import tempfile
import subprocess
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from bot_logic import graph  # Import the chatbot graph from docAppont.py
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

patients_db_url = "postgresql://postgres:heheboii420@localhost/patients_db"
engine = create_engine(patients_db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Conversation(Base):
    __tablename__ = "conversations"
    uuid = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True)
    patient_id = Column(String, index=True)
    conversation = Column(Text)
    summary = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class Message(BaseModel):
    type: str
    content: str

class ConversationInput(BaseModel):
    session_id: str
    patient_id: str
    conversation: List[Message]
    summary: str

class ConversationOutput(ConversationInput):
    uuid: str
    date: datetime

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
 
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
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_input:
            temp_input.write(await file.read())
            temp_input_path = temp_input.name

        temp_wav_path = temp_input_path.replace(".m4a", ".wav")
        subprocess.run(["ffmpeg", "-i", temp_input_path, temp_wav_path, "-y"], check=True)

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


def get_latest_appointment():
    """Fetch the most recent appointment JSON file from the directory."""
    files = [f for f in os.listdir() if f.startswith("appointment_") and f.endswith(".json")]
    if not files:
        raise HTTPException(status_code=404, detail="No appointment records found.")

    files.sort(key=lambda f: os.path.getctime(f), reverse=True)  # Sort by creation time (latest first)
    latest_file = files[0]

    with open(latest_file, "r") as file:
        appointment_data = json.load(file)

    return appointment_data

def get_latest_appointment_db():
    """Fetch the most recent appointment JSON file from the directory."""
    files = [f for f in os.listdir() if f.startswith("appointment_") and f.endswith(".json")]
    if not files:
        raise HTTPException(status_code=404, detail="No appointment records found.")
    
    files.sort(key=lambda f: os.path.getctime(f), reverse=True)  # Sort by creation time (latest first)
    latest_file = files[0]
    
    with open(latest_file, "r") as file:
        appointment_data = json.load(file)
    
    return json.dumps(appointment_data)  # Returning as string to store in DB


@app.get("/appointment/")
def get_appointment():
    """GET endpoint to retrieve the latest appointment JSON file."""
    try:
        return get_latest_appointment()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation", response_model=ConversationOutput)
def create_conversation(data: ConversationInput, db: Session = Depends(get_db)):
    try:
        summary = get_latest_appointment_db()
    except HTTPException:
        summary = "No appointment summary available."
    
    conversation_entry = Conversation(
        uuid=str(uuid4()),
        date=datetime.utcnow(),
        session_id=data.session_id,
        patient_id=data.patient_id,
        conversation=json.dumps([msg.dict() for msg in data.conversation]),
        summary=summary
    )
    db.add(conversation_entry)
    db.commit()
    db.refresh(conversation_entry)
    
    return ConversationOutput(
        uuid=conversation_entry.uuid,
        date=conversation_entry.date,
        session_id=conversation_entry.session_id,
        patient_id=conversation_entry.patient_id,
        conversation=[Message(**msg) for msg in json.loads(conversation_entry.conversation)],
        summary=conversation_entry.summary
    )


