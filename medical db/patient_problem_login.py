from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
import random
import requests

# Patient Database Configuration
patients_db_url = "postgresql://postgres:heheboii420@localhost/patients_db"
patients_engine = create_engine(patients_db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=patients_engine)
Base = declarative_base()

# Logs Database Configuration
logs_db_url = "postgresql://postgres:heheboii420@localhost/logs"
logs_engine = create_engine(logs_db_url)
LogsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=logs_engine)
LogsBase = declarative_base()

# Patient Table Definition
class PatientDetails(Base):
    __tablename__ = "patient_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    phone_number = Column(String)
    problems = relationship("PatientProblem", back_populates="patient")

class PatientProblem(Base):
    __tablename__ = "patient_problems"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey('patient_details.patient_id'))
    problem_description = Column(String)
    summary = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

    patient = relationship("PatientDetails", back_populates="problems")

# LogsHistory Table Definition
class LogsHistory(LogsBase):
    __tablename__ = "logs_history"

    session_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    logged_in_date = Column(DateTime, nullable=False)
    logged_out_date = Column(DateTime, nullable=True)

# Create tables if they do not exist
Base.metadata.create_all(bind=patients_engine)
LogsBase.metadata.create_all(bind=logs_engine)

# FastAPI app
app = FastAPI()

# Dependency to get database sessions
def get_patients_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_logs_db():
    db = LogsSessionLocal()
    try:
        yield db
    finally:
        db.close()

# In-memory store for authenticated users
authenticated_users = {}

# Helper function to generate numeric session IDs
def generate_session_id():
    return random.randint(100000, 999999)

# POST: Authenticate Patient and Save Session
@app.post("/patient/authenticate", response_model=dict)
async def authenticate_patient(
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_patients_db),
    logs_db: Session = Depends(get_logs_db),
):
    # Authenticate patient
    patient = db.query(PatientDetails).filter(
        PatientDetails.email == email.strip(),
        PatientDetails.password == password
    ).first()

    if not patient:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate a unique numeric session ID
    session_id = generate_session_id()
    authenticated_users[session_id] = email

    # Save session in logs_history table
    log_entry = LogsHistory(
        session_id=session_id,
        email=email,
        logged_in_date=datetime.utcnow(),
        logged_out_date=None
    )
    logs_db.add(log_entry)
    logs_db.commit()
    logs_db.refresh(log_entry)

    return {
        "message": "Authentication successful",
        "session_id": session_id,
        "email": email
    }

# POST: Record Patient Problem with Transcription
@app.post("/patient/problem", response_model=dict)
async def record_patient_problem(
    summary: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_patients_db)
):
    if not authenticated_users:
        raise HTTPException(status_code=401, detail="No authenticated user found. Please log in first.")

    # Get the last authenticated user's session ID and email
    session_id, email = list(authenticated_users.items())[-1]

    # Find patient in database
    patient = db.query(PatientDetails).filter(
        PatientDetails.email == email
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Authenticated patient not found")

    # Process audio file
    audio_bytes = await audio_file.read()
    files = {
        "audio": (audio_file.filename, audio_bytes, audio_file.content_type)
    }

    # Send to transcription service
    transcription_response = requests.post(
        "http://fs.wiseyak.com:8048/transcribe_english",
        files=files
    )

    if transcription_response.status_code != 200:
        raise HTTPException(
            status_code=transcription_response.status_code,
            detail="Transcription failed"
        )

    # Get transcription result
    transcription_result = transcription_response.json()

    # Create new problem record with session ID as ID
    new_problem = PatientProblem(
        id=session_id,
        patient_id=patient.patient_id,
        problem_description=transcription_result,
        summary=summary
    )

    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)

    return {
        "uuid": patient.patient_id,
        "problem_id": new_problem.id,
        "problem_description": new_problem.problem_description,
        "summary": new_problem.summary,
        "date": new_problem.date
    }

# POST: Logout Patient
@app.post("/patient/logout", response_model=dict)
async def logout_patient(logs_db: Session = Depends(get_logs_db)):
    if not authenticated_users:
        raise HTTPException(status_code=401, detail="No user is currently logged in")

    # Get the last authenticated user's session ID and email
    session_id, email = list(authenticated_users.items())[-1]

    # Update the logout time in logs_history table
    log_entry = logs_db.query(LogsHistory).filter(
        LogsHistory.session_id == session_id
    ).first()

    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")

    log_entry.logged_out_date = datetime.utcnow()
    logs_db.commit()

    # Remove session from authenticated users
    authenticated_users.pop(session_id, None)

    return {
        "message": "Logout successful",
        "session_id": session_id,
        "email": email
    }
