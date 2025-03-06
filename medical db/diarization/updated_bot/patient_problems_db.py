# import uuid
# import json
# from datetime import datetime
# from fastapi import FastAPI, HTTPException, Depends
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, String, Text, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session

# # Database connection
# DATABASE_URL = "postgresql://postgres:heheboii420@localhost/patients_db"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # Define PatientProblem model
# class PatientProblem(Base):
#     __tablename__ = "patient_problems"
#     id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
#     session_id = Column(String, nullable=False)
#     patient_id = Column(String, nullable=False)
#     problem_description = Column(Text, nullable=False)
#     conversation = Column(Text, nullable=False)
#     summary = Column(Text, nullable=True)
#     date = Column(DateTime, default=datetime.utcnow)

# # Create tables
# Base.metadata.create_all(bind=engine)

# # FastAPI instance
# app = FastAPI()

# # Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Pydantic schema for input validation
# class PatientProblemCreate(BaseModel):
#     session_id: str
#     patient_id: str
#     problem_description: str
#     conversation: dict  # Expecting a JSON object
#     summary: str

# # Endpoint to store patient problem
# @app.post("/patient_problem/")
# def create_patient_problem(problem: PatientProblemCreate, db: Session = Depends(get_db)):
#     try:
#         new_problem = PatientProblem(
#             session_id=problem.session_id,
#             patient_id=problem.patient_id,
#             problem_description=problem.problem_description,
#             conversation=json.dumps(problem.conversation),  # Store as JSON string
#             summary=problem.summary,
#         )
#         db.add(new_problem)
#         db.commit()
#         db.refresh(new_problem)
#         return {"message": "Patient problem recorded successfully", "id": new_problem.id}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
import json

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
    summary = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class Message(BaseModel):
    type: str
    content: str

class ConversationInput(BaseModel):
    session_id: str
    patient_id: str
    conversation: List[Message]

class ConversationOutput(ConversationInput):
    uuid: str
    date: datetime
    summary: Optional[str] = None

class SummaryInput(BaseModel):
    uuid: str
    summary: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/conversation", response_model=ConversationOutput)
def create_conversation(data: ConversationInput, db: Session = Depends(get_db)):
    conversation_entry = Conversation(
        uuid=str(uuid4()),
        date=datetime.utcnow(),
        session_id=data.session_id,
        patient_id=data.patient_id,
        conversation=json.dumps([msg.dict() for msg in data.conversation]),
        summary=None
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

@app.put("/summary")
def update_summary(data: SummaryInput, db: Session = Depends(get_db)):
    conversation_entry = db.query(Conversation).filter(Conversation.uuid == data.uuid).first()
    if not conversation_entry:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation_entry.summary = data.summary
    db.commit()
    db.refresh(conversation_entry)
    return {"uuid": data.uuid, "summary": conversation_entry.summary}
