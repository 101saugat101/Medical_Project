# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy import Column, Integer, String, create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from pydantic import BaseModel
# import uuid

# app = FastAPI()

# DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"  # Replace with actual credentials
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # Database Model
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

# # Pydantic Models
# class DoctorLogin(BaseModel):
#     email: str
#     password: str

# # Dependency to Get DB Session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # # Endpoint to Login a Doctor
# # @app.post("/doctor/login/")
# # def login_doctor(credentials: DoctorLogin, db: Session = Depends(get_db)):
# #     # Check if the doctor with the provided email exists

# #     doctor = db.query(Doctor).filter(Doctor.email == credentials.email).first()
# #     if not doctor or doctor.password != credentials.password:
# #         raise HTTPException(status_code=404, detail="incorrect email or password")
    
   

# #     # doctor = db.query(Doctor).filter(Doctor.email == credentials.email).first()
# #     # if not doctor:
# #     #     raise HTTPException(status_code=404, detail="Doctor with this email does not exist.")
    
# #     # # Verify the password
# #     # if doctor.password != credentials.password:
# #     #     raise HTTPException(status_code=401, detail="Incorrect email or password.")

# #     # Return success response
# #     return {
# #         "message": "Login successful",
# #         "doctor": {
# #             "doctor_id": doctor.doctor_id,
# #             "email": doctor.email,
# #             "name": doctor.name,
# #             "specialised_field": doctor.specialised_field,
# #         }
# #     }
# @app.get("/doctor/login/")
# def login_doctor(email: str, password: str, db: Session = Depends(get_db)):
#     # Check if the doctor with the provided email exists
#     doctor = db.query(Doctor).filter(Doctor.email == email).first()
#     if not doctor or doctor.password != password:
#         raise HTTPException(status_code=404, detail="Incorrect email or password")

#     # Return success response
#     return {
#         "message": "Login successful",
#         "doctor": {
#             "doctor_id": doctor.doctor_id,
#             "email": doctor.email,
#             "name": doctor.name,
#             "specialised_field": doctor.specialised_field,
#         }
#     }
from fastapi import FastAPI, Depends, HTTPException, Form
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import random

# Initialize FastAPI
app = FastAPI()

# Doctor Database Configuration
DOCTOR_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"
doctor_engine = create_engine(DOCTOR_DATABASE_URL)
DoctorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=doctor_engine)
DoctorBase = declarative_base()

# Log Database Configuration
LOG_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/logs"
log_engine = create_engine(LOG_DATABASE_URL)
LogSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=log_engine)
LogBase = declarative_base()

# Doctor Table Definition
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

# LogsHistory Table Definition
class LogsHistory(LogBase):
    __tablename__ = "logs_history"

    session_id = Column(Integer, primary_key=True, index=True)  # Numeric session ID
    email = Column(String, nullable=False, index=True)          # Doctor's email
    logged_in_date = Column(DateTime, nullable=False)           # Login date and time
    logged_out_date = Column(DateTime, nullable=True)           # Logout date and time

LogBase.metadata.create_all(bind=log_engine)

# Dependency to Get DB Sessions
def get_doctor_db():
    db = DoctorSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_log_db():
    db = LogSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to generate numeric session IDs
def generate_session_id():
    return random.randint(100000, 999999)

# In-memory store for authenticated doctors
authenticated_doctors = {}

# POST: Doctor Login and Create Log
@app.post("/doctor/login/")
def login_doctor(
    email: str = Form(...),  # Input email as form data
    password: str = Form(...),  # Input password as form data
    db: Session = Depends(get_doctor_db),
    logs_db: Session = Depends(get_log_db),
):
    # Authenticate doctor
    doctor = db.query(Doctor).filter(Doctor.email == email.strip()).first()
    if not doctor or doctor.password != password:
        raise HTTPException(status_code=404, detail="Incorrect email or password")

    # Generate a unique numeric session ID
    session_id = generate_session_id()
    authenticated_doctors[session_id] = email

    # Save login in logs_history table
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
        "message": "Login successful",
        "session_id": session_id,
        "email": email
    }

# POST: Doctor Logout and Update Log
@app.post("/doctor/logout/")
def logout_doctor(logs_db: Session = Depends(get_log_db)):
    # Ensure there is at least one authenticated doctor
    if not authenticated_doctors:
        raise HTTPException(status_code=401, detail="No doctor is currently logged in")

    # Get the latest session ID and email
    session_id, email = list(authenticated_doctors.items())[-1]

    # Update the logout time in logs_history table
    log_entry = logs_db.query(LogsHistory).filter(
        LogsHistory.session_id == session_id
    ).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")

    log_entry.logged_out_date = datetime.utcnow()
    logs_db.commit()

    # Remove the session from authenticated doctors
    authenticated_doctors.pop(session_id, None)

    return {
        "message": "Logout successful",
        "session_id": session_id,
        "email": email
    }
