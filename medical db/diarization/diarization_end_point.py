
import json
import torch
import numpy as np
import requests
from fastapi import FastAPI, File, UploadFile, Query, Depends, HTTPException
from pyannote.audio import Pipeline
from sklearn.metrics.pairwise import cosine_similarity
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pydub import AudioSegment
from io import BytesIO
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from summary import get_medical_information
import uuid

# Patient Database Configuration
patients_db_url = "postgresql://postgres:heheboii420@localhost/patients_db"
patients_engine = create_engine(patients_db_url)
PatientsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=patients_engine)
PatientsBase = declarative_base()

# Logs Database Configuration
logs_db_url = "postgresql://postgres:heheboii420@localhost/logs"
logs_engine = create_engine(logs_db_url)
LogsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=logs_engine)
LogsBase = declarative_base()

# Define PatientProblem Table in patients_db
class PatientProblem(PatientsBase):
    __tablename__ = "patient_problem"
    uuid = Column(String, primary_key=True)
    session_id = Column(Integer)
    patient_id = Column(String, ForeignKey('patient_details.patient_id'))
    problem_description = Column(String)
    audio_file = Column(String, nullable=True)
    summary = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

# Define ConversationHistory Table in logs_db
class ConversationHistory(LogsBase):
    __tablename__ = "conversation_history"
    meeting_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, unique=True, index=True)
    patient_id = Column(String, nullable=False, index=True)
    doctor_id = Column(String, nullable=False, index=True)
    conversation = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    feedback = Column(String, nullable=True)
    date_time = Column(DateTime, default=datetime.utcnow)

# Create tables if they don't exist
PatientsBase.metadata.create_all(bind=patients_engine)
LogsBase.metadata.create_all(bind=logs_engine)

def get_patients_db():
    db = PatientsSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_logs_db():
    db = LogsSessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_audio(audio_source):
    """Loads and normalizes audio data from file or bytes."""
    try:
        if isinstance(audio_source, bytes):
            audio = AudioSegment.from_file(BytesIO(audio_source))
        elif isinstance(audio_source, str):
            audio = AudioSegment.from_file(audio_source)
        else:
            raise ValueError("Invalid audio source. Must be bytes or file path.")

        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        temp_wav = BytesIO()
        audio.export(temp_wav, format="wav")
        temp_wav.seek(0)
        audio_array = np.array(AudioSegment.from_file(temp_wav).get_array_of_samples(), dtype=np.float32) / (2**15)

        return np.nan_to_num(audio_array)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error loading audio: {str(e)}")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = torch.device("cpu")
print(f"\U0001F680 Using device: {device}")

diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.0",
    use_auth_token="your-huggingface-api-token"
).to(device)

embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=device)

global_reference_speaker_path = None

@app.post("/set_reference_speaker/")
async def set_reference_speaker(
    audio_file: UploadFile = File(...),
    doctor_id: str = Query(..., description="Doctor ID")
):
    """Stores reference speaker audio for speaker verification."""
    global global_reference_speaker_path
    try:
        file_path = f"./uploaded_reference_{audio_file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await audio_file.read())
        
        global_reference_speaker_path = file_path
        return {"message": "Reference speaker audio stored successfully", "path": file_path, "doctor_id": doctor_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving reference speaker file: {str(e)}")

@app.post("/diarize/")
async def diarize(
    audio_file: UploadFile = File(...),
    session_id: str = Query(..., description="Session ID"),
    patient_id: str = Query(..., description="Patient ID"),
    doctor_id: str = Query(..., description="Doctor ID"),
    logs_db: Session = Depends(get_logs_db)
):
    """Performs diarization, transcription, and stores data in logs_db."""
    audio_samples = load_audio(await audio_file.read())
    diarization_result = diarization_pipeline(
        {"waveform": torch.tensor(audio_samples).unsqueeze(0), "sample_rate": 16000},
        num_speakers=2
    )
    
    transcriptions = []
    for segment in diarization_result.itertracks(yield_label=True):
        start, end, speaker = segment[0].start, segment[0].end, segment[1]
        segment_audio_bytes = BytesIO(audio_samples.tobytes())
        files = {"audio": ("segment.wav", segment_audio_bytes, "audio/wav")}
        transcription_response = requests.post("http://fs.wiseyak.com:8048/transcribe_english/", files=files)
        
        try:
            response_text = transcription_response.text.strip()
            transcription_json = json.loads(response_text) if response_text.startswith("{") else {"text": response_text}
            transcription_text = transcription_json.get("text", "")
        except json.JSONDecodeError:
            transcription_text = response_text
        
        transcriptions.append({"start": start, "end": end, "speaker": speaker, "text": transcription_text})
    
    patient_transcripts = " ".join([t["text"] for t in transcriptions if t["speaker"] == "patient"])
    medical_summary = json.dumps(get_medical_information(patient_transcripts))
    
    new_entry = ConversationHistory(
        meeting_id=str(uuid.uuid4()),
        session_id=session_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        conversation=json.dumps(transcriptions),
        summary=medical_summary,
        feedback=None
    )
    logs_db.add(new_entry)
    logs_db.commit()
    return {"session_id": session_id, "transcription_result": transcriptions, "medical_summary": json.loads(medical_summary)}
