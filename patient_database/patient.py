from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, Date, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date
import hashlib
from sqlalchemy import UniqueConstraint


# Database configuration
DATABASE_URL = "postgresql://postgres:heheboii420@localhost/medical_info"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI instance
app = FastAPI()

# Database Models
class Present(Base):
    __tablename__ = "present"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    problem_description = Column(Text, nullable=False)
    problem_summary = Column(Text, nullable=False)
    doctor_conversation = Column(Text, nullable=False)
    conversation_summary = Column(Text, nullable=False)
    doctor_feedback = Column(Text, nullable=False)


from sqlalchemy import Column, Integer, String, Text, Date, create_engine, UniqueConstraint

# class History(Base):
#     __tablename__ = "history"
#     history_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key for internal tracking
#     id = Column(Integer, nullable=False)  # Patient ID
#     visit_number = Column(Integer, nullable=False)  # Visit number for each patient
#     name = Column(String, nullable=False)
#     age = Column(Integer, nullable=False)
#     gender = Column(String, nullable=False)
#     problem_description = Column(Text, nullable=False)
#     problem_summary = Column(Text, nullable=False)
#     doctor_conversation = Column(Text, nullable=False)
#     conversation_summary = Column(Text, nullable=False)
#     doctor_feedback = Column(Text, nullable=False)
#     date = Column(Date, nullable=False)

#     __table_args__ = (
#         UniqueConstraint('id', 'visit_number', name='unique_id_visit_number'),  # Ensure unique ID and visit combination
#     )
class History(Base):
    __tablename__ = "history"
    id = Column(Integer, nullable=False)  # Patient ID
    visit_number = Column(Integer, nullable=False)  # Visit number for each patient
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

        # Check if patient already exists in the present table
        existing_patient = session.query(Present).filter(Present.id == patient_id).first()
        if existing_patient:
            return {"message": f"Patient already exists. Your ID is {patient_id}"}

        # Add to present table
        new_patient = Present(
            id=patient_id,
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            problem_description=patient.problem_description,
            problem_summary=patient.problem_summary,
            doctor_conversation=patient.doctor_conversation,
            conversation_summary=patient.conversation_summary,
            doctor_feedback=patient.doctor_feedback,
        )
        session.add(new_patient)
        session.commit()
        return {"message": f"Patient added successfully. Your ID is {patient_id}"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

# @app.post("/move_to_history/{patient_id}")
# def move_to_history(patient_id: int):
#     session = SessionLocal()
#     try:
#         # Get patient from the present table
#         patient = session.query(Present).filter(Present.id == patient_id).first()
#         if not patient:
#             raise HTTPException(status_code=404, detail="Patient not found")

#         # Calculate the next visit number
#         last_visit = (
#             session.query(History)
#             .filter(History.id == patient_id)
#             .order_by(History.visit_number.desc())
#             .first()
#         )
#         next_visit_number = last_visit.visit_number + 1 if last_visit else 1

#         # Add a new entry to the history table
#         history_entry = History(
#             id=patient.id,
#             visit_number=next_visit_number,
#             name=patient.name,
#             age=patient.age,
#             gender=patient.gender,
#             problem_description=patient.problem_description,
#             problem_summary=patient.problem_summary,
#             doctor_conversation=patient.doctor_conversation,
#             conversation_summary=patient.conversation_summary,
#             doctor_feedback=patient.doctor_feedback,
#             date=date.today(),
#         )
#         session.add(history_entry)

#         # Remove the patient from the present table
#         session.delete(patient)
#         session.commit()
#         return {"message": f"Patient moved to history successfully. Visit number: {next_visit_number}"}
#     except Exception as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         session.close()
@app.post("/move_to_history/{patient_id}")
def move_to_history(patient_id: int):
    session = SessionLocal()
    try:
        # Get patient from the present table
        patient = session.query(Present).filter(Present.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Calculate the next visit number
        last_visit = (
            session.query(History)
            .filter(History.id == patient_id)
            .order_by(History.visit_number.desc())
            .first()
        )
        next_visit_number = last_visit.visit_number + 1 if last_visit else 1

        # Add a new entry to the history table
        history_entry = History(
            id=patient.id,
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
        session.add(history_entry)

        # Remove the patient from the present table
        session.delete(patient)
        session.commit()
        return {"message": f"Patient moved to history successfully. Visit number: {next_visit_number}"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@app.get("/get_present_patients/")
def get_present_patients():
    session = SessionLocal()
    try:
        patients = session.query(Present).all()
        return patients
    finally:
        session.close()

@app.get("/get_history_patients/")
def get_history_patients():
    session = SessionLocal()
    try:
        patients = session.query(History).all()
        return patients
    finally:
        session.close()

# @app.get("/get_history_by_id/{patient_id}")
# def get_history_by_id(patient_id: int):
#     session = SessionLocal()
#     try:
#         history_records = session.query(History).filter(History.id == patient_id).order_by(History.date).all()
#         if not history_records:
#             raise HTTPException(status_code=404, detail="No history records found for the given ID")
#         return history_records
#     finally:
#         session.close()

@app.get("/get_history_by_id/{patient_id}")
def get_history_by_id(patient_id: int):
    session = SessionLocal()
    try:
        history_records = (
            session.query(History)
            .filter(History.id == patient_id)
            .order_by(History.visit_number)
            .all()
        )
        if not history_records:
            raise HTTPException(status_code=404, detail="No history records found for the given ID")
        return history_records
    finally:
        session.close()
