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
















































#1111111111111111111111111111111111

# from fastapi import FastAPI, Depends, HTTPException, Form
# from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from datetime import datetime
# import random

# # Initialize FastAPI
# app = FastAPI()

# # Doctor Database Configuration
# DOCTOR_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"
# doctor_engine = create_engine(DOCTOR_DATABASE_URL)
# DoctorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=doctor_engine)
# DoctorBase = declarative_base()

# # Log Database Configuration
# LOG_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/logs"
# log_engine = create_engine(LOG_DATABASE_URL)
# LogSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=log_engine)
# LogBase = declarative_base()

# # Doctor Table Definition
# class Doctor(DoctorBase):
#     __tablename__ = "doctor_details"

#     doctor_id = Column(String, primary_key=True, index=True)
#     email = Column(String, nullable=False, unique=True, index=True)
#     password = Column(String, nullable=False)
#     name = Column(String, index=True)
#     age = Column(Integer)
#     gender = Column(String)
#     specialised_field = Column(String)
#     phone_number = Column(String, nullable=True)

# DoctorBase.metadata.create_all(bind=doctor_engine)

# # LogsHistory Table Definition
# class LogsHistory(LogBase):
#     __tablename__ = "logs_history"

#     session_id = Column(Integer, primary_key=True, index=True)  # Numeric session ID
#     email = Column(String, nullable=False, index=True)          # Doctor's email
#     logged_in_date = Column(DateTime, nullable=False)           # Login date and time
#     logged_out_date = Column(DateTime, nullable=True)           # Logout date and time

# LogBase.metadata.create_all(bind=log_engine)

# # Dependency to Get DB Sessions
# def get_doctor_db():
#     db = DoctorSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def get_log_db():
#     db = LogSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Helper function to generate numeric session IDs
# def generate_session_id():
#     return random.randint(100000, 999999)

# # In-memory store for authenticated doctors
# authenticated_doctors = {}

# # POST: Doctor Login and Create Log
# @app.post("/doctor/login/")
# def login_doctor(
#     email: str = Form(...),  # Input email as form data
#     password: str = Form(...),  # Input password as form data
#     db: Session = Depends(get_doctor_db),
#     logs_db: Session = Depends(get_log_db),
# ):
#     # Authenticate doctor
#     doctor = db.query(Doctor).filter(Doctor.email == email.strip()).first()
#     if not doctor or doctor.password != password:
#         raise HTTPException(status_code=404, detail="Incorrect email or password")

#     # Generate a unique numeric session ID
#     session_id = generate_session_id()
#     authenticated_doctors[session_id] = email

#     # Save login in logs_history table
#     log_entry = LogsHistory(
#         session_id=session_id,
#         email=email,
#         logged_in_date=datetime.utcnow(),
#         logged_out_date=None
#     )
#     logs_db.add(log_entry)
#     logs_db.commit()
#     logs_db.refresh(log_entry)

#     return {
#         "message": "Login successful",
#         "session_id": session_id,
#         "email": email
#     }

# # POST: Doctor Logout and Update Log
# @app.post("/doctor/logout/")
# def logout_doctor(logs_db: Session = Depends(get_log_db)):
#     # Ensure there is at least one authenticated doctor
#     if not authenticated_doctors:
#         raise HTTPException(status_code=401, detail="No doctor is currently logged in")

#     # Get the latest session ID and email
#     session_id, email = list(authenticated_doctors.items())[-1]

#     # Update the logout time in logs_history table
#     log_entry = logs_db.query(LogsHistory).filter(
#         LogsHistory.session_id == session_id
#     ).first()
#     if not log_entry:
#         raise HTTPException(status_code=404, detail="Log entry not found")

#     log_entry.logged_out_date = datetime.utcnow()
#     logs_db.commit()

#     # Remove the session from authenticated doctors
#     authenticated_doctors.pop(session_id, None)

#     return {
#         "message": "Logout successful",
#         "session_id": session_id,
#         "email": email
#     }









#3333333333333333333333333333

# from fastapi import FastAPI, Depends, HTTPException, Form
# from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from datetime import datetime
# import random
# from doctor_dashboard import get_doctor_details

# # Initialize FastAPI
# app = FastAPI()

# # Doctor Database Configuration
# DOCTOR_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"
# doctor_engine = create_engine(DOCTOR_DATABASE_URL)
# DoctorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=doctor_engine)
# DoctorBase = declarative_base()

# # Log Database Configuration
# LOG_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/logs"
# log_engine = create_engine(LOG_DATABASE_URL)
# LogSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=log_engine)
# LogBase = declarative_base()

# # Doctor Table Definition
# class Doctor(DoctorBase):
#     __tablename__ = "doctor_details"

#     doctor_id = Column(String, primary_key=True, index=True)
#     email = Column(String, nullable=False, unique=True, index=True)
#     password = Column(String, nullable=False)
#     name = Column(String, index=True)
#     age = Column(Integer)
#     gender = Column(String)
#     specialised_field = Column(String)
#     phone_number = Column(String, nullable=True)

# DoctorBase.metadata.create_all(bind=doctor_engine)

# # LogsHistory Table Definition
# class LogsHistory(LogBase):
#     __tablename__ = "logs_history"

#     session_id = Column(Integer, primary_key=True, index=True)  # Numeric session ID
#     email = Column(String, nullable=False, index=True)          # Doctor's email
#     logged_in_date = Column(DateTime, nullable=False)           # Login date and time
#     logged_out_date = Column(DateTime, nullable=True)           # Logout date and time

# LogBase.metadata.create_all(bind=log_engine)

# # Dependency to Get DB Sessions
# def get_doctor_db():
#     db = DoctorSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def get_log_db():
#     db = LogSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Helper function to generate numeric session IDs
# def generate_session_id():
#     return random.randint(100000, 999999)

# # In-memory store for authenticated doctors
# authenticated_doctors = {}

# # POST: Doctor Login and Create Log
# @app.post("/doctor/login/")
# def login_doctor(
#     email: str = Form(...),  # Input email as form data
#     password: str = Form(...),  # Input password as form data
#     db: Session = Depends(get_doctor_db),
#     logs_db: Session = Depends(get_log_db),
# ):
#     # Authenticate doctor
#     doctor = db.query(Doctor).filter(Doctor.email == email.strip()).first()
#     if not doctor or doctor.password != password:
#         raise HTTPException(status_code=404, detail="Incorrect email or password")

#     # Generate a unique numeric session ID
#     session_id = generate_session_id()
#     authenticated_doctors[session_id] = email

#     # Save login in logs_history table
#     log_entry = LogsHistory(
#         session_id=session_id,
#         email=email,
#         logged_in_date=datetime.utcnow(),
#         logged_out_date=None
#     )
#     logs_db.add(log_entry)
#     logs_db.commit()
#     logs_db.refresh(log_entry)

#     # Fetch doctor details
#     doctor_details = get_doctor_details(email=email, db=db)

#     return {
#         "message": "Login successful",
#         "session_id": session_id,
#         "doctor_details": doctor_details
#     }

# # POST: Doctor Logout and Update Log
# @app.post("/doctor/logout/")
# def logout_doctor(logs_db: Session = Depends(get_log_db)):
#     # Ensure there is at least one authenticated doctor
#     if not authenticated_doctors:
#         raise HTTPException(status_code=401, detail="No doctor is currently logged in")

#     # Get the latest session ID and email
#     session_id, email = list(authenticated_doctors.items())[-1]

#     # Update the logout time in logs_history table
#     log_entry = logs_db.query(LogsHistory).filter(
#         LogsHistory.session_id == session_id
#     ).first()
#     if not log_entry:
#         raise HTTPException(status_code=404, detail="Log entry not found")

#     log_entry.logged_out_date = datetime.utcnow()
#     logs_db.commit()

#     # Remove the session from authenticated doctors
#     authenticated_doctors.pop(session_id, None)

#     return {
#         "message": "Logout successful",
#         "session_id": session_id,
#         "email": email
#     }





from fastapi import FastAPI, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import datetime
import random
from doctor_dashboard import get_doctor_details, get_assigned_patients, get_doctor_db, get_receptionist_db, get_patient_db, Doctor
from fastapi.middleware.cors import CORSMiddleware

#this is for views.py import
from fastapi import FastAPI, Depends
import asyncpg
from pydantic import BaseModel
from typing import List, Optional
from views import get_db_connection, DoctorDashboard 
#############


# Initialize FastAPI
app = FastAPI()







origins = [
    "http://localhost:8000",  # Local React development server
    
]

# Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specified origins
    allow_credentials=True,  # Allow cookies and credentials
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)











# Helper function to generate numeric session IDs
def generate_session_id():
    return random.randint(100000, 999999)

# In-memory store for authenticated doctors
authenticated_doctors = {}

# POST: Doctor Login
@app.post("/doctor/login/")
def login_doctor(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_doctor_db),
):
    # Fetch doctor details
    doctor = db.query(Doctor).filter(Doctor.email == email.strip()).first()
    if not doctor or doctor.password != password:
        raise HTTPException(status_code=404, detail="Incorrect email or password")
    
    # Generate session ID
    session_id = generate_session_id()
    authenticated_doctors[session_id] = email
    
    return {
        "message": f"Login successful and {doctor.doctor_id}",
        "session_id": session_id,
        "doctor_id": doctor.doctor_id
    }

# GET: Fetch Doctor Details and Assigned Patients
# GET: Fetch Doctor Details and Assigned Patients
@app.get("/doctor/details/")
def get_doctor_info(
    doctor_id: str,
    db: Session = Depends(get_doctor_db),
    receptionist_db: Session = Depends(get_receptionist_db),
    patient_db: Session = Depends(get_patient_db),
):
    
    
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    email = doctor.email
    doctor = db.query(Doctor).filter(Doctor.email == email).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    doctor_details = get_doctor_details(email, db)
    assigned_patients = get_assigned_patients(doctor.doctor_id, receptionist_db, patient_db)
    
    return {
        "doctor_details": doctor_details,
        "assigned_patients": assigned_patients
    }



#Endpoint to fetch doctor details based on doctor_id
@app.get("/doctor_dashboard/{doctor_id}", response_model=List[DoctorDashboard])
async def get_doctor_by_id(doctor_id: str):
    conn = await get_db_connection()
    query = """
    SELECT * FROM doctor_dashboard WHERE doctor_id = $1
    """
    result = await conn.fetch(query, doctor_id)
    await conn.close()
    
    if not result:
        return []  # Return empty list if no doctor found
    
    return [DoctorDashboard(**row) for row in result]



# POST: Doctor Logout
@app.post("/doctor/logout/")
def logout_doctor():
    if not authenticated_doctors:
        raise HTTPException(status_code=401, detail="No doctor is currently logged in")
    
    session_id, email = list(authenticated_doctors.items())[-1]
    authenticated_doctors.pop(session_id, None)
    
    return {
        "message": "Logout successful",
        "session_id": session_id,
        "email": email
    }

























#@22222222222222222222222222222222222


# from fastapi import FastAPI, Depends, HTTPException, Form
# from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from datetime import datetime
# from typing import Optional
# from pydantic import BaseModel
# import random

# # Initialize FastAPI
# app = FastAPI()

# # Doctor Database Configuration
# DOCTOR_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"
# doctor_engine = create_engine(DOCTOR_DATABASE_URL)
# DoctorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=doctor_engine)
# DoctorBase = declarative_base()

# # Log Database Configuration
# LOG_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/logs"
# log_engine = create_engine(LOG_DATABASE_URL)
# LogSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=log_engine)
# LogBase = declarative_base()

# # Doctor Table Definition
# class Doctor(DoctorBase):
#     __tablename__ = "doctor_details"

#     doctor_id = Column(String, primary_key=True, index=True)
#     email = Column(String, nullable=False, unique=True, index=True)
#     password = Column(String, nullable=False)
#     name = Column(String, index=True)
#     age = Column(Integer)
#     gender = Column(String)
#     specialised_field = Column(String)
#     phone_number = Column(String, nullable=True)

# DoctorBase.metadata.create_all(bind=doctor_engine)

# # LogsHistory Table Definition
# class LogsHistory(LogBase):
#     __tablename__ = "logs_history"

#     session_id = Column(Integer, primary_key=True, index=True)  # Numeric session ID
#     email = Column(String, nullable=False, index=True)          # Doctor's email
#     logged_in_date = Column(DateTime, nullable=False)           # Login date and time
#     logged_out_date = Column(DateTime, nullable=True)           # Logout date and time

# LogBase.metadata.create_all(bind=log_engine)

# # Pydantic Models for Request/Response
# class DoctorDetails(BaseModel):
#     doctor_id: str
#     email: str
#     name: str
#     age: int
#     gender: str
#     specialised_field: str
#     phone_number: Optional[str] = None

#     class Config:
#         from_attributes = True

# # Dependency to Get DB Sessions
# def get_doctor_db():
#     db = DoctorSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def get_log_db():
#     db = LogSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Helper function to generate numeric session IDs
# def generate_session_id():
#     return random.randint(100000, 999999)

# # In-memory store for authenticated doctors
# authenticated_doctors = {}

# # POST: Doctor Login and Create Log
# @app.post("/doctor/login/")
# def login_doctor(
#     email: str = Form(...),  # Input email as form data
#     password: str = Form(...),  # Input password as form data
#     db: Session = Depends(get_doctor_db),
#     logs_db: Session = Depends(get_log_db),
# ):
#     # Authenticate doctor
#     doctor = db.query(Doctor).filter(Doctor.email == email.strip()).first()
#     if not doctor or doctor.password != password:
#         raise HTTPException(status_code=404, detail="Incorrect email or password")

#     # Generate a unique numeric session ID
#     session_id = generate_session_id()
#     authenticated_doctors[session_id] = email

#     # Save login in logs_history table
#     log_entry = LogsHistory(
#         session_id=session_id,
#         email=email,
#         logged_in_date=datetime.utcnow(),
#         logged_out_date=None
#     )
#     logs_db.add(log_entry)
#     logs_db.commit()
#     logs_db.refresh(log_entry)

#     return {
#         "message": "Login successful",
#         "session_id": session_id,
#         "email": email
#     }

# # POST: Doctor Logout and Update Log
# @app.post("/doctor/logout/")
# def logout_doctor(logs_db: Session = Depends(get_log_db)):
#     # Ensure there is at least one authenticated doctor
#     if not authenticated_doctors:
#         raise HTTPException(status_code=401, detail="No doctor is currently logged in")

#     # Get the latest session ID and email
#     session_id, email = list(authenticated_doctors.items())[-1]

#     # Update the logout time in logs_history table
#     log_entry = logs_db.query(LogsHistory).filter(
#         LogsHistory.session_id == session_id
#     ).first()
#     if not log_entry:
#         raise HTTPException(status_code=404, detail="Log entry not found")

#     log_entry.logged_out_date = datetime.utcnow()
#     logs_db.commit()

#     # Remove the session from authenticated doctors
#     authenticated_doctors.pop(session_id, None)

#     return {
#         "message": "Logout successful",
#         "session_id": session_id,
#         "email": email
#     }

# # GET: Doctor Details
# @app.get("/doctor/details/{session_id}", response_model=DoctorDetails)
# def get_doctor_details(
#     session_id: int,
#     db: Session = Depends(get_doctor_db)
# ):
#     # Check if the session exists in authenticated_doctors
#     if session_id not in authenticated_doctors:
#         raise HTTPException(
#             status_code=401,
#             detail="Not authenticated. Please login first."
#         )
    
#     # Get the email from authenticated_doctors
#     doctor_email = authenticated_doctors[session_id]
    
#     # Query the doctor's details from the database
#     doctor = db.query(Doctor).filter(Doctor.email == doctor_email).first()
    
#     if not doctor:
#         raise HTTPException(
#             status_code=404,
#             detail="Doctor not found"
#         )
    
#     return doctor

# # For development purposes only
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)