
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






















