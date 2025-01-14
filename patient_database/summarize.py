# # from transformers import pipeline

# # # Load the summarization pipeline
# # summarizer = pipeline("summarization")

# # # Load the transcription text from the file
# # input_file = "/content/transcription_output.txt"  # Path to the input transcription file
# # with open(input_file, "r", encoding="utf-8") as file:
# #     text = file.read()

# # # Summarize the text
# # summary = summarizer(text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']

# # # Save the summary to a new file
# # output_file = "/content/summarized.txt"  # Path to the output summary file
# # with open(output_file, "w", encoding="utf-8") as file:
# #     file.write(summary)

# # print(f"Summary saved to {output_file}")

# from transformers import pipeline
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from patient import PatientHistory, Patient, Base  # Import models from patient.py

# # Database setup
# DATABASE_URL = "postgresql://postgres:heheboii420@localhost/medical_feild"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base.metadata.create_all(bind=engine)

# summarizer = pipeline("summarization")

# input_file = "/content/transcription_output.txt"
# with open(input_file, "r", encoding="utf-8") as file:
#     text = file.read()

# summary = summarizer(text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']

# # Save the summary to the database
# db = SessionLocal()
# try:
#     # Assuming the patient and history IDs are known
#     patient_id = 1  # Replace with the actual patient ID
#     history_id = 1  # Replace with the actual patient history ID

#     # Update summary in the patient table
#     patient = db.query(Patient).filter(Patient.id == patient_id).first()
#     if patient:
#         patient.summary = summary 
#         db.add(patient)

#     # Update summary in the patient history table
#     history = db.query(PatientHistory).filter(PatientHistory.id == history_id).first()
#     if history:
#         history.summary = summary
#         db.add(history)

#     db.commit()
# finally:
#     db.close()

# print("Summary saved to the database.")

import json
import openai

# Set your OpenAI API key
openai.api_key = "your_openai_api_key"

# Load the JSON file containing the conversation
with open('transcript.json', 'r') as f:
    data = json.load(f)

# Check if the data contains a single speaker (simple format) or multiple speakers (complex format)
if isinstance(data, dict):  # Single speaker format
    # Combine all text under speaker(s)
    conversation = ""
    for speaker, text in data.items():
        conversation += f"{speaker}: {text}\n"
else:  # Multiple speakers format
    # Combine the conversation into a single string
    conversation = ""
    for segment in data:
        speaker = segment["speaker"].replace("SPEAKER ", "")
        text = segment["text"].strip()
        conversation += f"{speaker}: {text}\n"

# Define a prompt to summarize the conversation
prompt = f"""
The following is a conversation. Please summarize the key points of the discussion clearly and concisely:

{conversation}
"""

# Call OpenAI API to generate the summary
response = openai.Completion.create(
    engine="text-davinci-003",  # Use "gpt-4" if available
    prompt=prompt,
    max_tokens=150,  # Adjust token limit based on the length of the conversation
    temperature=0.7
)

# Extract the summary from the API response
summary = response.choices[0].text.strip()

# Save the summary to a JSON file
output = {"summary": summary}
with open('summary.json', 'w') as f:
    json.dump(output, f, indent=4)

print("Summary generated and saved to 'summary.json'.")
