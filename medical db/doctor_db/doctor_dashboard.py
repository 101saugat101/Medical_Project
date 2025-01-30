
# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session

# # Database Configuration
# DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"  # Replace with actual credentials
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # Doctor Table Definition
# class Doctor(Base):
#     __tablename__ = "doctor_details"

#     doctor_id = Column(String, primary_key=True, index=True)
#     email = Column(String, nullable=False, unique=True, index=True)
#     password = Column(String, nullable=False)
#     name = Column(String, index=True)
#     age = Column(Integer)
#     gender = Column(String)
#     specialised_field = Column(String)
#     phone_number = Column(String, nullable=True)

# Base.metadata.create_all(bind=engine)

# # Initialize FastAPI App
# app = FastAPI()

# # Dependency to Get DB Session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # GET: Doctor Dashboard
# @app.get("/doctor/dashboard/")
# def get_doctor_details(email: str, db: Session = Depends(get_db)):
#     doctor = db.query(Doctor).filter(Doctor.email == email.strip()).first()
#     if not doctor:
#         raise HTTPException(status_code=404, detail="Doctor not found")

#     return {
#         "doctor_id": doctor.doctor_id,
#         "email": doctor.email,
#         "name": doctor.name,
#         "age": doctor.age,
#         "gender": doctor.gender,
#         "specialised_field": doctor.specialised_field,
#         "phone_number": doctor.phone_number
#     }



from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Database URLs
DOCTOR_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"
RECEPTIONIST_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/receptionist_db"
PATIENT_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/patients_db"

# Create engines
doctor_engine = create_engine(DOCTOR_DATABASE_URL)
receptionist_engine = create_engine(RECEPTIONIST_DATABASE_URL)
patient_engine = create_engine(PATIENT_DATABASE_URL)

# Create session makers
DoctorSessionLocal = sessionmaker(bind=doctor_engine)
ReceptionistSessionLocal = sessionmaker(bind=receptionist_engine)
PatientSessionLocal = sessionmaker(bind=patient_engine)

# Define bases
DoctorBase = declarative_base()
ReceptionistBase = declarative_base()
PatientBase = declarative_base()

# Doctor Model
class Doctor(DoctorBase):
    __tablename__ = "doctor_details"
    doctor_id = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    specialised_field = Column(String)
    phone_number = Column(String, nullable=True)

DoctorBase.metadata.create_all(bind=doctor_engine)

# Patient Assignment Model
class PatientAssignment(ReceptionistBase):
    __tablename__ = "patient_assignment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    assigned_doctor_id = Column(String, nullable=False)
    assigned_patient_id = Column(String, nullable=False)
    date_assigned = Column(DateTime, default=datetime.utcnow)

ReceptionistBase.metadata.create_all(bind=receptionist_engine)

# Patient Details Model
class PatientDetails(PatientBase):
    __tablename__ = "patient_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    phone_number = Column(String)

PatientBase.metadata.create_all(bind=patient_engine)

# Database dependencies
def get_doctor_db():
    db = DoctorSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_receptionist_db():
    db = ReceptionistSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_patient_db():
    db = PatientSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get doctor details
def get_doctor_details(email: str, db: Session):
    doctor = db.query(Doctor).filter(Doctor.email == email).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {
        "doctor_id": doctor.doctor_id,
        "email": doctor.email,
        "name": doctor.name,
        "age": doctor.age,
        "gender": doctor.gender,
        "specialised_field": doctor.specialised_field,
        "phone_number": doctor.phone_number
    }

# Get patients assigned to doctor
def get_assigned_patients(doctor_id: str, receptionist_db: Session, patient_db: Session):
    assignments = receptionist_db.query(PatientAssignment).filter(PatientAssignment.assigned_doctor_id == doctor_id).all()
    if not assignments:
        return []
    patient_details = []
    for assignment in assignments:
        patient = patient_db.query(PatientDetails).filter(PatientDetails.patient_id == assignment.assigned_patient_id).first()
        if patient:
            patient_details.append({
                "patient_id": patient.patient_id,
                "name": patient.name,
                "age": patient.age,
                "gender": patient.gender,
                "phone_number": patient.phone_number
            })
    return patient_details
