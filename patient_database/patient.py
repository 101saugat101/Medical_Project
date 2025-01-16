
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, Date, UniqueConstraint, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date
import hashlib


# Database configuration
DATABASE_URL = "postgresql://postgres:heheboii420@localhost/patient"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI instance
app = FastAPI()

# Database Models
class History(Base):
    __tablename__ = "history"
    id = Column(Integer, nullable=False)  # Patient ID
    visit_number = Column(Integer, nullable=False)  # Incremental visit number for each patient
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    problem_description = Column(Text, nullable=False)
    problem_summary = Column(Text, nullable=False)
    doctor_conversation = Column(Text, nullable=False)
    conversation_summary = Column(Text, nullable=False)
    doctor_feedback = Column(Text, nullable=False)
    date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint('id', 'visit_number', name='unique_id_visit_number'),  # Ensure unique ID and visit combination
    )

    # Composite primary key
    __mapper_args__ = {
        "primary_key": (id, visit_number),
    }

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class Patient(BaseModel):
    name: str
    age: int
    gender: str
    problem_description: str
    problem_summary: str
    doctor_conversation: str
    conversation_summary: str
    doctor_feedback: str

    class Config:
        orm_mode = True

# Helper function to generate a unique ID
def generate_unique_id(name: str, age: int, gender: str) -> int:
    unique_string = f"{name}{age}{gender}"
    return int(hashlib.sha256(unique_string.encode()).hexdigest(), 16) % (10 ** 8)

# FastAPI Routes
@app.post("/add_patient/")
def add_patient(patient: Patient):
    session = SessionLocal()
    try:
        # Generate a unique ID for the patient
        patient_id = generate_unique_id(patient.name, patient.age, patient.gender)

        # Calculate the next visit number
        last_visit = (
            session.query(History)
            .filter(History.id == patient_id)
            .order_by(History.visit_number.desc())
            .first()
        )
        next_visit_number = last_visit.visit_number + 1 if last_visit else 1

        # Add to history table
        new_patient = History(
            id=patient_id,
            visit_number=next_visit_number,
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            problem_description=patient.problem_description,
            problem_summary=patient.problem_summary,
            doctor_conversation=patient.doctor_conversation,
            conversation_summary=patient.conversation_summary,
            doctor_feedback=patient.doctor_feedback,
            date=date.today(),
        )
        session.add(new_patient)
        session.commit()
        return {"message": f"Patient added successfully. Your ID is {patient_id}, Visit number: {next_visit_number}"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

# @app.get("/get_history_by_id/{patient_id}")
# def get_history_by_id(patient_id: int):
#     session = SessionLocal()
#     try:
#         history_records = (
#             session.query(History)
#             .filter(History.id == patient_id)
#             .order_by(History.visit_number)
#             .all()
#         )
#         if not history_records:
#             raise HTTPException(status_code=404, detail="No history records found for the given ID")
#         return history_records
#     finally:
#         session.close()

# @app.get("/get_all_patients/")
# def get_all_patients():
#     session = SessionLocal()
#     try:
#         patients = session.query(History).all()
#         return patients
#     finally:
#         session.close()
