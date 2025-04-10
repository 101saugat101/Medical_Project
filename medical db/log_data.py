from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy import Column, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import uuid
import requests

# Initialize FastAPI
app = FastAPI()

# Database Configuration
DATABASE_URL = "postgresql://postgres:heheboii420@localhost/logs"  # Replace with actual credentials
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Conversation History Table Definition
class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    meeting_id = Column(String, primary_key=True, index=True)  # Unique numeric UUID
    session_id = Column(String, unique=True, index=True)  # Unique session ID
    patient_id = Column(String, nullable=False, index=True)  # UUID for the patient
    doctor_id = Column(String, nullable=False, index=True)  # UUID for the doctor
    conversation = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    feedback = Column(String, nullable=True)
    date_time = Column(DateTime, default=datetime.utcnow)

# Create Database Tables
Base.metadata.create_all(bind=engine)

# Pydantic Model for Request Validation
class ConversationCreate(BaseModel):
    patient_uuid: str  # Patient's unique identifier
    doctor_uuid: str  # Doctor's unique identifier
    summary: str | None = None  # Optional summary field

# Dependency to Get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Generate a Numeric UUID (12 digits)
def generate_numeric_uuid():
    return str(uuid.uuid4().int)[:12]

# Transcribe Audio Helper Function
def transcribe_audio(audio_file: UploadFile):
    try:
        audio_bytes = audio_file.file.read()
        files = {"audio": (audio_file.filename, audio_bytes, audio_file.content_type)}
        response = requests.post("http://fs.wiseyak.com:8048/transcribe_english", files=files)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Transcription failed")

        return response.json()  # Assumes transcription result is in JSON format
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")

@app.post("/conversations/")
def add_conversation(
    session_id: str,
    patient_uuid: str,
    doctor_uuid: str,
    audio_conversation: UploadFile = File(...),
    audio_feedback: UploadFile = File(...),
    summary: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        # Generate meeting_id as unique numeric UUID
        meeting_id = generate_numeric_uuid()

        # Transcribe conversation audio
        conversation_transcription = transcribe_audio(audio_conversation)
        # Transcribe feedback audio
        feedback_transcription = transcribe_audio(audio_feedback)

        # Create a new conversation entry
        new_conversation = ConversationHistory(
            meeting_id=meeting_id,
            session_id=session_id,
            patient_id=patient_uuid,
            doctor_id=doctor_uuid,
            conversation=conversation_transcription,
            summary=summary,
            feedback=feedback_transcription,
            date_time=datetime.utcnow(),
        )
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)

        return {
            "message": "Conversation added successfully",
            "conversation": {
                "meeting_id": new_conversation.meeting_id,
                "session_id": new_conversation.session_id,
                "conversation": new_conversation.conversation,
                "feedback": new_conversation.feedback,
                "summary": new_conversation.summary,
                "date_time": new_conversation.date_time,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding conversation: {str(e)}")
