from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, relationship, sessionmaker, declarative_base
from sqlalchemy import create_engine, Column, Integer, String

patients_db_url = "postgresql://postgres:heheboii420@localhost/patients_db"
patients_engine = create_engine(patients_db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=patients_engine)
Base = declarative_base()

class PatientDetails(Base):
    __tablename__ = "patient_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    phone_number = Column(String)

Base.metadata.create_all(bind=patients_engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(PatientDetails).filter(PatientDetails.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {
        "id": patient.id,
        "patient_id": patient.patient_id,
        "email": patient.email,
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "phone_number": patient.phone_number
    }