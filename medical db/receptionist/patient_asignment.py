from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from receptionist import get_doctor_db, get_patient_db, DoctorDetails, PatientDetails  # Import existing DB connections

# Database URL for Receptionist DB
RECEPTIONIST_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/receptionist_db"

# Create engine and base
receptionist_engine = create_engine(RECEPTIONIST_DATABASE_URL)
Base = declarative_base()

# Model
class PatientAssignment(Base):
    __tablename__ = "patient_assignment"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    assigned_doctor_id = Column(String, nullable=False)  # Removed ForeignKey
    assigned_patient_id = Column(String, nullable=False)  # Removed ForeignKey
    date_assigned = Column(DateTime, default=datetime.utcnow)  # New column to store assignment date and time

# Create session
ReceptionistSessionLocal = sessionmaker(bind=receptionist_engine)

# FastAPI app
app = FastAPI()

# Database dependency for Receptionist DB
def get_receptionist_db():
    db = ReceptionistSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create table if not exists
Base.metadata.create_all(bind=receptionist_engine)

# Endpoint to assign a patient to a doctor
@app.post("/assign")
def assign_patient(doctor_id: str, patient_id: str, db: Session = Depends(get_receptionist_db), doctor_db: Session = Depends(get_doctor_db), patient_db: Session = Depends(get_patient_db)):
    # Validate doctor_id exists
    doctor = doctor_db.query(DoctorDetails).filter(DoctorDetails.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Validate patient_id exists
    patient = patient_db.query(PatientDetails).filter(PatientDetails.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Assign patient to doctor
    assignment = PatientAssignment(assigned_doctor_id=doctor_id, assigned_patient_id=patient_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {"message": "Patient assigned successfully", "assignment_id": assignment.id, "date_assigned": assignment.date_assigned}
