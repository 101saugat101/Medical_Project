from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import random

# Database URL for PostgreSQL
# Replace the below URL with your actual PostgreSQL credentials
# Format: postgresql://username:password@localhost:port/database_name
database_url = "postgresql://postgres:heheboii420@localhost/patients_db"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Patient model for the database
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Auto-incrementing primary key
    uuid = Column(String, index=True)  # Unique identifier for patients (numbers only)
    patient_name = Column(String, index=True)  # Patient's name
    age = Column(Integer)  # Patient's age
    gender = Column(String)  # Patient's gender
    problem_description = Column(String)  # Description of the patient's problem
    summary = Column(String)  # Summary of the visit or case
    visit_date = Column(DateTime, default=datetime.utcnow)  # Date and time of the visit

# Create the database table if it doesn't already exist
Base.metadata.create_all(bind=engine)

# Pydantic models for request validation and response formatting
class PatientCreate(BaseModel):
    patient_name: str
    age: int
    gender: str
    problem_description: str
    summary: str

class PatientResponse(PatientCreate):
    id: int
    uuid: str
    visit_date: datetime

    class Config:
        orm_mode = True  # Enables ORM compatibility for response models

# Service layer to manage patient-related database operations
class PatientService:
    def __init__(self, db_session):
        self.db_session = db_session

    def generate_numeric_uuid(self):
        """
        Generate a unique numeric UUID.
        """
        while True:
            new_uuid = str(random.randint(1000000000, 9999999999))  # Generate a 10-digit number
            if not self.db_session.query(Patient).filter(Patient.uuid == new_uuid).first():
                return new_uuid

    def get_or_create_patient(self, patient_data: PatientCreate) -> Patient:
        """
        Check if a patient already exists (based on name, age, and gender).
        If found, add a new visit entry with the same UUID.
        Otherwise, create a new patient with a unique numeric UUID.
        """
        existing_patient = self.db_session.query(Patient).filter(
            Patient.patient_name == patient_data.patient_name,
            Patient.age == patient_data.age,
            Patient.gender == patient_data.gender
        ).first()

        if existing_patient:
            # Add a new visit entry for the existing patient
            new_visit = Patient(
                uuid=existing_patient.uuid,
                patient_name=existing_patient.patient_name,
                age=existing_patient.age,
                gender=existing_patient.gender,
                problem_description=patient_data.problem_description,
                summary=patient_data.summary,
                visit_date=datetime.utcnow()
            )
            self.db_session.add(new_visit)
            self.db_session.commit()
            self.db_session.refresh(new_visit)
            return new_visit

        # Create a new patient record
        new_patient = Patient(
            uuid=self.generate_numeric_uuid(),  # Generate a unique numeric UUID
            **patient_data.dict()  # Unpack the patient data into the model
        )
        self.db_session.add(new_patient)
        self.db_session.commit()  # Save changes to the database
        self.db_session.refresh(new_patient)  # Refresh instance with new data
        return new_patient

    def get_all_patients(self) -> List[Patient]:
        """
        Retrieve all patients from the database.
        """
        return self.db_session.query(Patient).all()

    def get_patient_by_uuid(self, patient_uuid: str) -> List[Patient]:
        """
        Retrieve all visit records for a specific patient by their UUID.
        Raise an HTTPException if no records are found.
        """
        patient_visits = self.db_session.query(Patient).filter(Patient.uuid == patient_uuid).all()
        if not patient_visits:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient_visits

# FastAPI application setup
app = FastAPI()

@app.post("/patients", response_model=PatientResponse)
def create_or_get_patient(patient: PatientCreate):
    """
    Endpoint to create a new patient or retrieve an existing patient based on input data.
    """
    with SessionLocal() as db_session:
        patient_service = PatientService(db_session)
        patient_record = patient_service.get_or_create_patient(patient)
        return {
            "id": patient_record.id,
            "uuid": patient_record.uuid,
            "visit_date": patient_record.visit_date,
            "patient_name": patient_record.patient_name,
            "age": patient_record.age,
            "gender": patient_record.gender,
            "problem_description": patient_record.problem_description,
            "summary": patient_record.summary,
            "message": f"Your unique ID number is {patient_record.uuid}"
        }

@app.get("/patients", response_model=List[PatientResponse])
def list_patients():
    """
    Endpoint to retrieve a list of all patients in the database.
    """
    with SessionLocal() as db_session:
        patient_service = PatientService(db_session)
        return patient_service.get_all_patients()

@app.get("/patients/{patient_uuid}", response_model=List[PatientResponse])
def get_patient(patient_uuid: str):
    """
    Endpoint to retrieve all visit records for a specific patient by their UUID.
    """
    with SessionLocal() as db_session:
        patient_service = PatientService(db_session)
        patient_visits = patient_service.get_patient_by_uuid(patient_uuid)
        return patient_visits


# To run this application:
# 1. Replace the database URL with your PostgreSQL credentials.
# 2. Save this file as `main.py`.
# 3. Run the application using: `uvicorn main:app --reload`. or uvicorn table_patient:app --port 8086  --reload
# 4. Access the API documentation at `http://127.0.0.1:8000/docs`.
#database_url = "postgresql://postgres:heheboii420@localhost/patients_db"
