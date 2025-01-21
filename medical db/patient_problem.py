from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import requests

database_url = "postgresql://postgres:heheboii420@localhost/patients_db"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class PatientDetails(Base):
    __tablename__ = "patient_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, unique=True, index=True) 
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
    patient_id = Column(Integer, ForeignKey('patient_details.id'))
    problem_description = Column(String)
    summary = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to PatientDetails
    patient = relationship("PatientDetails", back_populates="problems")

# Don't create tables - they already exist
# Base.metadata.create_all(bind=engine)

# FastAPI application
app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/patient/problem", response_model=dict)
async def record_patient_problem(
    email: str = Form(...),
    password: str = Form(...),
    summary: str = Form(...),
    audio_file: UploadFile = File(...),
    db: SessionLocal = Depends(get_db)
):
    try:
        # Debug log
        print(f"Received email: {email}, password: {password}")

        # Authenticate patient
        patient = db.query(PatientDetails).filter(
            PatientDetails.email == email.strip(),
            PatientDetails.password == password
        ).first()
        
        print(f"Patient found: {patient}")  # Debug log

        if not patient:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        
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
        
        # Create new problem record
        new_problem = PatientProblem(
            patient_id=patient.id,
            problem_description=transcription_result,
            summary=summary
        )
        
        db.add(new_problem)
        db.commit()
        db.refresh(new_problem)
        
        return {
            "uuid": patient.uuid,  
            "problem_id": new_problem.id,
            "problem_description": new_problem.problem_description,
            "summary": new_problem.summary,
            "date": new_problem.date
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
