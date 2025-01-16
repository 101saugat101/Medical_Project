from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import uuid

# Initialize FastAPI
app = FastAPI()

# Database Configuration
DATABASE_URL = "postgresql://postgres:heheboii420@localhost/conversation_db"  # Replace with actual credentials
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Conversation Table Definition
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)  # Unique numeric UUID
    patient_uuid = Column(String, nullable=False, index=True)  # UUID for the patient
    doctor_uuid = Column(String, nullable=False, index=True)  # UUID for the doctor
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
    conversation: str
    summary: str | None = None
    feedback: str | None = None

# Dependency to Get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Generate a Numeric UUID
def generate_numeric_uuid():
    return str(uuid.uuid4().int)[:12]

# API Endpoint to Add a Conversation
@app.post("/conversations/")
def add_conversation(conversation_data: ConversationCreate, db: Session = Depends(get_db)):
    # Create a new conversation entry
    new_conversation = Conversation(
        id=generate_numeric_uuid(),
        patient_uuid=conversation_data.patient_uuid,
        doctor_uuid=conversation_data.doctor_uuid,
        conversation=conversation_data.conversation,
        summary=conversation_data.summary,
        feedback=conversation_data.feedback,
        date_time=datetime.utcnow(),
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return {"message": "Conversation added successfully", "conversation": new_conversation}

# API Endpoint to Get All Conversations
@app.get("/conversations/")
def get_all_conversations(db: Session = Depends(get_db)):
    conversations = db.query(Conversation).all()
    return {"conversations": conversations}
