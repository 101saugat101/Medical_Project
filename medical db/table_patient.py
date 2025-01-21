
# # To run this application:
# # 1. Replace the database URL with your PostgreSQL credentials.
# # 2. Save this file as `main.py`.
# # 3. Run the application using: `uvicorn main:app --reload`. or uvicorn table_patient:app --port 8086  --reload
# # 4. Access the API documentation at `http://127.0.0.1:8000/docs`.
# #database_url = "postgresql://postgres:heheboii420@localhost/patients_db"


# from fastapi import FastAPI, HTTPException, File, UploadFile, Form
# from pydantic import BaseModel
# from typing import List
# from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, relationship
# from datetime import datetime
# import requests
# import random
# import logging

# from typing import Optional

# # Database URL for PostgreSQL
# database_url = "postgresql://postgres:heheboii420@localhost/patients_db"

# # SQLAlchemy setup
# Base = declarative_base()
# engine = create_engine(database_url)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Define the PatientDetails model for the patient table
# class PatientDetails(Base):
#     __tablename__ = "patient_details"
#     patient_uuid = Column(String, primary_key=True, index=True)  # Unique identifier for patients
#     name = Column(String, index=True)  # Patient's name
#     age = Column(Integer)  # Patient's age
#     gender = Column(String)  # Patient's gender
#     phone_number = Column(String)  # Patient's phone number
    
#     # Relationship to client_db table (One-to-One relationship)
#     client_info = relationship("ClientDb", back_populates="patient_details", uselist=False)

# # Define the ClientDb model for the client-specific data table
# class ClientDb(Base):
#     __tablename__ = "client_db"
#     id = Column(Integer, primary_key=True, index=True)
#     problem_description = Column(String)  # Description of the patient's problem
#     summary = Column(String)  # Summary of the visit or case
#     patient_uuid = Column(String, ForeignKey('patient_details.patient_uuid'))  # Foreign key to the patient_details table
#     date = Column(DateTime, default=datetime.utcnow)  # Full DateTime for the visit
    
#     # Relationship back to PatientDetails
#     patient_details = relationship("PatientDetails", back_populates="client_info")

# # Create the database tables if they don't exist
# Base.metadata.create_all(bind=engine)

# # Service layer to manage patient-related database operations
# class PatientService:
#     def __init__(self, db_session):
#         self.db_session = db_session

#     def generate_numeric_uuid(self):
#         """
#         Generate a unique numeric UUID.
#         """
#         while True:
#             new_uuid = str(random.randint(1000000000, 9999999999))  # Generate a 10-digit number
#             if not self.db_session.query(PatientDetails).filter(PatientDetails.patient_uuid == new_uuid).first():
#                 return new_uuid

#     def get_or_create_patient(self, patient_data, problem_description: str):
#         """
#         Check if a patient already exists (based on name, age, and gender).
#         If found, add a new visit entry with the same UUID.
#         Otherwise, create a new patient with a unique numeric UUID.
#         """
#         existing_patient = self.db_session.query(PatientDetails).filter(
#             PatientDetails.name == patient_data["name"],
#             PatientDetails.age == patient_data["age"],
#             PatientDetails.gender == patient_data["gender"]
#         ).first()

#         if existing_patient:
#             # Create a new entry in the client_db for the existing patient
#             new_client_record = ClientDb(
#                 patient_uuid=existing_patient.patient_uuid,
#                 problem_description=problem_description,
#                 summary=patient_data["summary"]
#             )
#             self.db_session.add(new_client_record)
#             self.db_session.commit()
#             self.db_session.refresh(new_client_record)
#             return new_client_record

#         # Create a new patient record
#         new_patient_uuid = self.generate_numeric_uuid()
#         new_patient = PatientDetails(
#             patient_uuid=new_patient_uuid,
#             name=patient_data["name"],
#             age=patient_data["age"],
#             gender=patient_data["gender"],
#             phone_number=patient_data["phone_number"]
#         )
#         self.db_session.add(new_patient)
#         self.db_session.commit()
#         self.db_session.refresh(new_patient)

#         # Create a new client record linked to the patient
#         new_client_record = ClientDb(
#             patient_uuid=new_patient.patient_uuid,
#             problem_description=problem_description,
#             summary=patient_data["summary"]
#         )
#         self.db_session.add(new_client_record)
#         self.db_session.commit()
#         self.db_session.refresh(new_client_record)
#         return new_client_record

# # FastAPI application setup
# app = FastAPI()

# #uvicorn table_patient:app --host 0.0.0.0 --port 8086  --reload
# @app.post("/patients/audio", response_model=dict)
# async def create_patient_with_audio(
#     name: str = Form(...),
#     age: int = Form(...),
#     gender: str = Form(...),
#     phone_number: str = Form(...),
#     summary: str = Form(...),
#     audio_file: UploadFile = File(...)
# ):
# # @app.post("/patients/audio", response_model=dict)
# # async def create_patient_with_audio(
# #     name: Optional[str] = Form(None),
# #     age: Optional[int] = Form(None),
# #     gender: Optional[str] = Form(None),
# #     phone_number: Optional[str] = Form(None),
# #     summary: Optional[str] = Form(None),
# #     audio_file: UploadFile = File(...)
# # ):
#     """
#     Endpoint to create a new patient or retrieve an existing patient based on input data and audio transcription.
#     """
#     try:
#         # Read the content of the uploaded audio file
#         audio_bytes = await audio_file.read()

#         # Prepare the file payload with correct content type
#         files = {
#             "audio": (audio_file.filename, audio_bytes, audio_file.content_type)
#         }
#         transcription_response = requests.post(
#             "http://fs.wiseyak.com:8048/transcribe_english", files=files
#         )

#         # Handle transcription service response
#         if transcription_response.status_code != 200:
#             raise HTTPException(
#                 status_code=transcription_response.status_code, 
#                 detail="Transcription failed"
#             )

#         # Extract the transcribed text
#         transcription_result = transcription_response.json()
#         print(transcription_result)
#         # problem_description = transcription_result.get("text", "")
#         problem_description = transcription_result


#         if not problem_description:
#             raise HTTPException(status_code=400, detail="Transcription service returned no text")

#         # Add the patient record with the transcribed text
#         patient_data = {
#             "name": name,
#             "age": age,
#             "gender": gender,
#             "phone_number": phone_number,
#             "summary": summary,
#         }

#         with SessionLocal() as db_session:
#             patient_service = PatientService(db_session)
#             patient_record = patient_service.get_or_create_patient(patient_data, transcription_result)

#         return {
#             "patient_uuid": patient_record.patient_uuid,
#             "problem_description": problem_description,
#             "summary": patient_record.summary,
#             "date": patient_record.date,
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random

# Database URL for PostgreSQL
database_url = "postgresql://postgres:heheboii420@localhost/patients_db"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the PatientDetails model
class PatientDetails(Base):
    __tablename__ = "patient_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, unique=True, index=True)  # Numeric UUID
    email = Column(String, unique=True, index=True)  # Unique email
    password = Column(String)  # Password field
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    phone_number = Column(String)
    
    # Add unique constraint on email
    __table_args__ = (UniqueConstraint('email', name='unique_email_constraint'),)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic model for request validation
class PatientCreate(BaseModel):
    email: str
    password: str
    name: str
    age: int
    gender: str
    phone_number: str

# Service layer for patient operations
class PatientService:
    def __init__(self, db_session):
        self.db_session = db_session

    def generate_numeric_uuid(self):
        """Generate a unique numeric UUID."""
        while True:
            new_uuid = str(random.randint(1000000000, 9999999999))  # 10-digit number
            if not self.db_session.query(PatientDetails).filter(PatientDetails.uuid == new_uuid).first():
                return new_uuid

    def create_patient(self, patient_data: PatientCreate):
        """Create a new patient if email doesn't exist."""
        # Check if email already exists
        if self.db_session.query(PatientDetails).filter(PatientDetails.email == patient_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new patient with generated UUID
        new_patient = PatientDetails(
            uuid=self.generate_numeric_uuid(),
            email=patient_data.email,
            password=patient_data.password,  # Note: In production, this should be hashed
            name=patient_data.name,
            age=patient_data.age,
            gender=patient_data.gender,
            phone_number=patient_data.phone_number
        )
        
        self.db_session.add(new_patient)
        self.db_session.commit()
        self.db_session.refresh(new_patient)
        return new_patient

# FastAPI application
app = FastAPI()

@app.post("/patients/register", response_model=dict)
async def register_patient(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    phone_number: str = Form(...)
):
    """Endpoint to register a new patient."""
    try:
        patient_data = PatientCreate(
            email = email.strip(),
            password = password.strip(),

            name=name,
            age=age,
            gender=gender,
            phone_number=phone_number
        )

        with SessionLocal() as db_session:
            patient_service = PatientService(db_session)
            patient = patient_service.create_patient(patient_data)

        return {
            "uuid": patient.uuid,
            "email": patient.email,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "phone_number": patient.phone_number
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn your_file_name:app --host 0.0.0.0 --port 8086 --reload