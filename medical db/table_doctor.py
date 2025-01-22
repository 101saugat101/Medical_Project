from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, create_engine, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import uuid

app = FastAPI()

DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"  # Replace with actual credentials
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Doctor(Base):
    __tablename__ = "doctor_details"

    doctor_id = Column(String, primary_key=True, index=True)
    email=Column(String, nullable=False, index=True)
    password=Column(String, nullable=False)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    specialised_field = Column(String)
    phone_number = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# Pydantic Model for Request Validation
class DoctorCreate(BaseModel):
    email: str
    password: str
    name: str
    age: int
    gender: str
    specialised_field: str
    phone_number: str | None = None  # Optional phone number

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
@app.post("/doctor_details/")
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    # Check if a doctor with the same email already exists
    existing_email = db.query(Doctor).filter(Doctor.email == doctor.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="A doctor with this email already exists.")

    # Create a new doctor entry
    new_doctor = Doctor(
        doctor_id=generate_numeric_uuid(),
        email=doctor.email,
        password=doctor.password,
        name=doctor.name,
        age=doctor.age,
        gender=doctor.gender,
        specialised_field=doctor.specialised_field,
        phone_number=doctor.phone_number,
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return {"message": "Doctor added successfully", "doctor": new_doctor}

# # API Endpoint to Get All Doctors
# @app.get("/doctor_details/")
# def get_all_doctors(db: Session = Depends(get_db)):
#     doctor_details = db.query(Doctor).all()
#     return {"doctor_details": doctor_details}


