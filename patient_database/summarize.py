# from transformers import pipeline

# # Load the summarization pipeline
# summarizer = pipeline("summarization")

# # Load the transcription text from the file
# input_file = "/content/transcription_output.txt"  # Path to the input transcription file
# with open(input_file, "r", encoding="utf-8") as file:
#     text = file.read()

# # Summarize the text
# summary = summarizer(text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']

# # Save the summary to a new file
# output_file = "/content/summarized.txt"  # Path to the output summary file
# with open(output_file, "w", encoding="utf-8") as file:
#     file.write(summary)

# print(f"Summary saved to {output_file}")

from transformers import pipeline
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from patient import PatientHistory, Patient, Base  # Import models from patient.py

# Database setup
DATABASE_URL = "postgresql://postgres:heheboii420@localhost/medical_feild"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

summarizer = pipeline("summarization")

input_file = "/content/transcription_output.txt"
with open(input_file, "r", encoding="utf-8") as file:
    text = file.read()

summary = summarizer(text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']

# Save the summary to the database
db = SessionLocal()
try:
    # Assuming the patient and history IDs are known
    patient_id = 1  # Replace with the actual patient ID
    history_id = 1  # Replace with the actual patient history ID

    # Update summary in the patient table
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        patient.summary = summary 
        db.add(patient)

    # Update summary in the patient history table
    history = db.query(PatientHistory).filter(PatientHistory.id == history_id).first()
    if history:
        history.summary = summary
        db.add(history)

    db.commit()
finally:
    db.close()

print("Summary saved to the database.")

