from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# FastAPI app
app = FastAPI()

# Database configuration
LOGS_DATABASE_URL = "postgresql://postgres:heheboii420@localhost/logs"  # Replace with your credentials
engine = create_engine(LOGS_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# LogsHistory Table Definition
class LogsHistory(Base):
    __tablename__ = "logs_history"

    session_id = Column(Integer, primary_key=True, index=True)  # Unique session ID
    email = Column(String, nullable=False, index=True)        # User email
    logged_in_date = Column(DateTime, nullable=False)         # Login date and time
    logged_out_date = Column(DateTime, nullable=True)         # Logout date and time

# Create the table
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to create a new log entry
@app.post("/logs/")
def create_log_entry(
    session_id: str, 
    email: str, 
    logged_in_date: datetime, 
    logged_out_date: datetime = None, 
    db: SessionLocal = Depends(get_db)
):
    # Create a new log entry
    new_log = LogsHistory(
        session_id=session_id,
        email=email,
        logged_in_date=logged_in_date,
        logged_out_date=logged_out_date,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return {"message": "Log entry created successfully", "log": new_log}

