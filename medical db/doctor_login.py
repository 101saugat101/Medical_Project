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


# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy import Column, Integer, String, create_engine, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from pydantic import BaseModel
# from datetime import datetime
# import uuid

# # Initialize FastAPI
# app = FastAPI()

# # Doctor Database Configuration
# DOCTOR_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"  # Replace with actual credentials
# doctor_engine = create_engine(DOCTOR_DATABASE_URL)
# DoctorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=doctor_engine)
# DoctorBase = declarative_base()

# # Log Database Configuration
# LOG_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/logs"  # Replace with actual credentials
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

# # Log Table Definition
# class Conversation(LogBase):
#     __tablename__ = "log_table"

#     session_id = Column(String, primary_key=True, index=True)  # Unique numeric UUID
#     patient_id = Column(String, nullable=False, index=True)  # UUID for the patient
#     doctor_id = Column(String, nullable=False, index=True)  # UUID for the doctor
#     conversation = Column(String, nullable=False)
#     summary = Column(String, nullable=True)
#     feedback = Column(String, nullable=True)
#     date_time = Column(DateTime, default=datetime.utcnow)

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

# # Pydantic Models
# class DoctorLogin(BaseModel):
#     email: str
#     password: str

# # Endpoint to Login a Doctor
# @app.post("/doctor/login/")
# def login_doctor(credentials: DoctorLogin, db: Session = Depends(get_doctor_db)):
#     # Check if the doctor with the provided email exists
#     doctor = db.query(Doctor).filter(Doctor.email == credentials.email).first()
#     if not doctor or doctor.password != credentials.password:
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

# # New Endpoint to Get Log Data by Doctor ID
# @app.get("/doctor/{doctor_id}/logs/")
# def get_logs_by_doctor_id(doctor_id: str, db: Session = Depends(get_log_db)):
#     # Query logs based on doctor_id
#     logs = db.query(Conversation).filter(Conversation.doctor_id == doctor_id).all()
#     if not logs:
#         raise HTTPException(status_code=404, detail="No logs found for this doctor ID")

#     # Format and return the logs
#     return {
#         "doctor_id": doctor_id,
#         "logs": [
#             {
#                 "session_id": log.session_id,
#                 "patient_id": log.patient_id,
#                 "conversation": log.conversation,
#                 "summary": log.summary,
#                 "feedback": log.feedback,
#                 "date_time": log.date_time,
#             }
#             for log in logs
#         ],
#     }



from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy import Column, Integer, String, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Initialize FastAPI
app = FastAPI()

# Secret key for JWT
SECRET_KEY = "57c505f9992c17d776a3b3036f5d096fbf483fe5ddb85d138fb0a5b4dfcac66b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Doctor Database Configuration
DOCTOR_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"  # Replace with actual credentials
doctor_engine = create_engine(DOCTOR_DATABASE_URL)
DoctorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=doctor_engine)
DoctorBase = declarative_base()

# Log Database Configuration
LOG_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/logs"  # Replace with actual credentials
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

# Log Table Definition
class Conversation(LogBase):
    __tablename__ = "log_table"

    session_id = Column(String, primary_key=True, index=True)  # Unique numeric UUID
    patient_id = Column(String, nullable=False, index=True)  # UUID for the patient
    doctor_id = Column(String, nullable=False, index=True)  # UUID for the doctor
    conversation = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    feedback = Column(String, nullable=True)
    date_time = Column(DateTime, default=datetime.utcnow)

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

# Pydantic Models
class DoctorLogin(BaseModel):
    email: str
    password: str

# Utility Function to Create JWT Token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to Extract Doctor ID from Token
def get_current_doctor(token: str = Header(...), db: Session = Depends(get_doctor_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        doctor_id: str = payload.get("sub")
        if doctor_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

# Endpoint to Login a Doctor
@app.post("/doctor/login/")
def login_doctor(credentials: DoctorLogin, db: Session = Depends(get_doctor_db)):
    doctor = db.query(Doctor).filter(Doctor.email == credentials.email).first()
    if not doctor or doctor.password != credentials.password:
        raise HTTPException(status_code=404, detail="Incorrect email or password")

    # Create access token
    access_token = create_access_token(data={"sub": doctor.doctor_id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "doctor": {
            "doctor_id": doctor.doctor_id,
            "email": doctor.email,
            "name": doctor.name,
            "specialised_field": doctor.specialised_field,
        },
    }

# GET Endpoint to Retrieve Logs by Doctor ID (Automatically Extracted)
@app.get("/doctor/logs/")
def get_logs_by_doctor_id(doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_log_db)):
    logs = db.query(Conversation).filter(Conversation.doctor_id == doctor.doctor_id).all()
    if not logs:
        raise HTTPException(status_code=404, detail="No logs found for this doctor")

    return {
        "doctor_id": doctor.doctor_id,
        "logs": [
            {
                "session_id": log.session_id,
                "patient_id": log.patient_id,
                "conversation": log.conversation,
                "summary": log.summary,
                "feedback": log.feedback,
                "date_time": log.date_time,
            }
            for log in logs
        ],
    }
