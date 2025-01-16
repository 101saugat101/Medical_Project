
# # To run this application:
# # 1. Replace the database URL with your PostgreSQL credentials.
# # 2. Save this file as `main.py`.
# # 3. Run the application using: `uvicorn main:app --reload`. or uvicorn table_patient:app --port 8086  --reload
# # 4. Access the API documentation at `http://127.0.0.1:8000/docs`.
# #database_url = "postgresql://postgres:heheboii420@localhost/patients_db"


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import random

# Database URL for PostgreSQL
database_url = "postgresql://postgres:heheboii420@localhost/patients_db"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the PatientDetails model for the patient table
class PatientDetails(Base):
    __tablename__ = "patient_details"
    uuid = Column(String, primary_key=True, index=True)  # Unique identifier for patients
    patient_name = Column(String, index=True)  # Patient's name
    age = Column(Integer)  # Patient's age
    gender = Column(String)  # Patient's gender
    phone_number = Column(String)  # Patient's phone number
    
    # Relationship to client_db table (One-to-One relationship)
    client_info = relationship("ClientDb", back_populates="patient_details", uselist=False)

# Define the ClientDb model for the client-specific data table
class ClientDb(Base):
    __tablename__ = "client_db"
    id = Column(Integer, primary_key=True, index=True)
    problem_description = Column(String)  # Description of the patient's problem
    summary = Column(String)  # Summary of the visit or case
    uuid = Column(String, ForeignKey('patient_details.uuid'))  # Foreign key to the patient_details table
    date = Column(DateTime, default=datetime.utcnow)  # Full DateTime for the visit
    
    # Relationship back to PatientDetails
    patient_details = relationship("PatientDetails", back_populates="client_info")

# Create the database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Pydantic models for request validation and response formatting
class PatientCreate(BaseModel):
    patient_name: str
    age: int
    gender: str
    phone_number: str
    problem_description: str
    summary: str

class PatientResponse(PatientCreate):
    uuid: str
    date: datetime

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
            if not self.db_session.query(PatientDetails).filter(PatientDetails.uuid == new_uuid).first():
                return new_uuid

    def get_or_create_patient(self, patient_data: PatientCreate):
        """
        Check if a patient already exists (based on name, age, and gender).
        If found, add a new visit entry with the same UUID.
        Otherwise, create a new patient with a unique numeric UUID.
        """
        existing_patient = self.db_session.query(PatientDetails).filter(
            PatientDetails.patient_name == patient_data.patient_name,
            PatientDetails.age == patient_data.age,
            PatientDetails.gender == patient_data.gender
        ).first()

        if existing_patient:
            # Create a new entry in the client_db for the existing patient
            new_client_record = ClientDb(
                uuid=existing_patient.uuid,
                problem_description=patient_data.problem_description,
                summary=patient_data.summary
            )
            self.db_session.add(new_client_record)
            self.db_session.commit()
            self.db_session.refresh(new_client_record)
            return new_client_record

        # Create a new patient record
        new_patient_uuid = self.generate_numeric_uuid()
        new_patient = PatientDetails(
            uuid=new_patient_uuid,
            patient_name=patient_data.patient_name,
            age=patient_data.age,
            gender=patient_data.gender,
            phone_number=patient_data.phone_number
        )
        self.db_session.add(new_patient)
        self.db_session.commit()
        self.db_session.refresh(new_patient)

        # Create a new client record linked to the patient
        new_client_record = ClientDb(
            uuid=new_patient.uuid,
            problem_description=patient_data.problem_description,
            summary=patient_data.summary
        )
        self.db_session.add(new_client_record)
        self.db_session.commit()
        self.db_session.refresh(new_client_record)
        return new_client_record

    def get_all_patients(self) -> List[PatientDetails]:
        """
        Retrieve all patients from the database.
        """
        return self.db_session.query(PatientDetails).all()

    def get_patient_by_uuid(self, patient_uuid: str) -> List[ClientDb]:
        """
        Retrieve all visit records for a specific patient by their UUID.
        Raise an HTTPException if no records are found.
        """
        client_visits = self.db_session.query(ClientDb).filter(ClientDb.uuid == patient_uuid).all()
        if not client_visits:
            raise HTTPException(status_code=404, detail="Patient not found")
        return client_visits

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

        # Get the PatientDetails record associated with the ClientDb record
        patient_details = db_session.query(PatientDetails).filter(
            PatientDetails.uuid == patient_record.uuid
        ).first()

        # Construct the response using data from both PatientDetails and ClientDb
        return {
            "uuid": patient_details.uuid,
            "patient_name": patient_details.patient_name,
            "age": patient_details.age,
            "gender": patient_details.gender,
            "phone_number": patient_details.phone_number,
            "problem_description": patient_record.problem_description,
            "summary": patient_record.summary,
            "date": patient_record.date,
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
