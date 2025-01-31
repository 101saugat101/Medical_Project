from fastapi import FastAPI
import asyncpg
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Database configuration (logs database where the view resides)
DATABASE_URL = "postgresql://postgres:heheboii420@localhost/logs"

# Define a Pydantic model for the data returned from the view\
class DoctorDashboard(BaseModel):
    doctor_id: str
    doctor_name: str
    specialised_field: str
    patient_id: str
    patient_name: str
    age: int
    gender: str
    phone_number: str
    problem_description: str
    problem_summary: Optional[str]  # Allow None values
    conversation: Optional[str]  # Allow None values
    conversation_summary: Optional[str]  # Allow None values
    feedback: Optional[str]  # Allow None values
    conversation_date: Optional[str]  # Allow None values

# Connect to the database
async def get_db_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn







from pydantic import BaseModel, validator
from typing import Optional







# Endpoint to fetch data from the doctor_dashboard view
@app.get("/doctor_dashboard", response_model=List[DoctorDashboard])
async def get_doctor_dashboard():
    conn = await get_db_connection()
    # Query data from the doctor_dashboard view
    result = await conn.fetch('SELECT * FROM doctor_dashboard')
    await conn.close()
    return [DoctorDashboard(**row) for row in result]


