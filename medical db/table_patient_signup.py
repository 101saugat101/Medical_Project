from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random

database_url = "postgresql://postgres:heheboii420@localhost/patients_db"

Base = declarative_base()
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class PatientDetails(Base):
    __tablename__ = "patient_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, unique=True, index=True)  # Numeric UUID
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
            if not self.db_session.query(PatientDetails).filter(PatientDetails.patient_id == new_uuid).first():
                return new_uuid

    def create_patient(self, patient_data: PatientCreate):
        """Create a new patient if email doesn't exist."""
        # Check if email already exists
        if self.db_session.query(PatientDetails).filter(PatientDetails.email == patient_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new patient with generated UUID
        new_patient = PatientDetails(
            patient_id=self.generate_numeric_uuid(),
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

app = FastAPI()

@app.post("/patients/register", response_model=dict)
async def register_patient(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    phone_number: str = Form(...)
    #  email: str ,
    # password: str ,
    # name: str,
    # age: int,
    # gender: str,
    # phone_number: str
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
            "patient_id": patient.patient_id,
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
