# receptionist.py
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship



from fastapi.middleware.cors import CORSMiddleware



# Database URLs
PATIENT_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/patients_db"
DOCTOR_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/doctors_db"

# Create engines
patient_engine = create_engine(PATIENT_DATABASE_URL)
doctor_engine = create_engine(DOCTOR_DATABASE_URL)

# Create bases
PatientBase = declarative_base()
DoctorBase = declarative_base()

# Models
class PatientDetails(PatientBase):
    __tablename__ = "patient_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    phone_number = Column(String)
    problems = relationship("PatientProblem", back_populates="patient")

class PatientProblem(PatientBase):
    __tablename__ = "patient_problem"
    
    uuid = Column(Integer, primary_key=True, autoincrement=True)  # Changed from 'id'
    patient_id = Column(String, ForeignKey('patient_details.patient_id'))
    problem_description = Column(String)
    patient = relationship("PatientDetails", back_populates="problems")

class DoctorDetails(DoctorBase):
    __tablename__ = "doctor_details"
    
    doctor_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    specialised_field = Column(String)
    phone_number = Column(String)

# Create sessions
PatientSessionLocal = sessionmaker(bind=patient_engine)
DoctorSessionLocal = sessionmaker(bind=doctor_engine)

# FastAPI app
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










# Database dependency
def get_patient_db():
    db = PatientSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_doctor_db():
    db = DoctorSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/")
def read_root():
    return {"message": "Medical Reception System"}

@app.get("/patients/")
def get_all_patients(db: Session = Depends(get_patient_db)):
    patients = db.query(PatientDetails).all()
    return [
        {
            "patient_id": patient.patient_id,
            "name": patient.name,
            "email": patient.email,
            "age": patient.age,
            "gender": patient.gender,
            "phone": patient.phone_number,
            "problems": [
                {
                    "problem_id": problem.uuid,  # Changed from 'id'
                    "description": problem.problem_description
                }
                for problem in patient.problems
            ]
        }
        for patient in patients
    ]

@app.get("/patients/{patient_id}/problems")
def get_patient_problems(patient_id: str, db: Session = Depends(get_patient_db)):
    patient = db.query(PatientDetails).filter(PatientDetails.patient_id == patient_id).first()
    if not patient:
        return {"error": "Patient not found"}
    
    return {
        "patient_name": patient.name,
        "problems": [
            {
                "problem_id": problem.uuid,  # Changed from 'id'
                "description": problem.problem_description
            }
            for problem in patient.problems
        ]
    }

@app.get("/doctors/")
def get_all_doctors(db: Session = Depends(get_doctor_db)):
    doctors = db.query(DoctorDetails).all()
    return [
        {
            "doctor_id": doctor.doctor_id,
            "name": doctor.name,
            "email": doctor.email,
            "specialised_field": doctor.specialised_field,
            "phone": doctor.phone_number
        }
        for doctor in doctors
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8086)
