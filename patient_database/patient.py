from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date

# Database setup
DATABASE_URL = "postgresql://postgres:heheboii420@localhost/medical_feild"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    summary = Column(Text)  # New column for summary
    histories = relationship("PatientHistory", back_populates="patient")
    current_problem = relationship("CurrentProblem", uselist=False, back_populates="patient")


class PatientHistory(Base):
    __tablename__ = "patient_history"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_date = Column(Date, nullable=False)
    problem = Column(Text)
    solution = Column(Text)
    summary = Column(Text)  # New column for summary
    patient = relationship("Patient", back_populates="histories")


class CurrentProblem(Base):
    __tablename__ = "current_problem"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    problem = Column(Text, nullable=False)
    patient = relationship("Patient", back_populates="current_problem")

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI setup
app = FastAPI()

# Pydantic schemas
class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str

class CurrentProblemCreate(BaseModel):
    patient_id: int
    problem: str

# Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.post("/patients/")
async def create_patient(patient: PatientCreate, db: SessionLocal = Depends(get_db)):
    new_patient = Patient(name=patient.name, age=patient.age, gender=patient.gender)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@app.post("/patients/current-problem/")
async def add_current_problem(problem: CurrentProblemCreate, db: SessionLocal = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == problem.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Save existing current problem to history if it exists
    if patient.current_problem:
        new_history = PatientHistory(
            patient_id=patient.id,
            visit_date=date.today(),  # Automatically use today's date for history
            problem=patient.current_problem.problem,
            solution="Pending"
        )
        db.add(new_history)
        db.delete(patient.current_problem)  # Remove the current problem

    # Add new current problem
    new_problem = CurrentProblem(patient_id=problem.patient_id, problem=problem.problem)
    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)
    return new_problem

@app.get("/patients/{patient_id}/details/")
async def get_patient_details(patient_id: int, db: SessionLocal = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {
        "personal_info": {
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
        },
        "current_problem": patient.current_problem.problem if patient.current_problem else None,
        "history": [
            {
                "visit_date": history.visit_date,
                "problem": history.problem,
                "solution": history.solution,
            }
            for history in patient.histories
        ],
    }

# Disable editing patient history
@app.post("/patients/history/", include_in_schema=False)
async def add_patient_history():
    raise HTTPException(status_code=403, detail="Editing patient history is not allowed.")
