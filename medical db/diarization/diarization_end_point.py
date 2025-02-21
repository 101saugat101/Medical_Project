# import json
# import torch
# import numpy as np
# import gc
# import requests
# from fastapi import FastAPI, File, UploadFile
# from pyannote.audio import Pipeline
# from sklearn.metrics.pairwise import cosine_similarity
# from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
# from pydub import AudioSegment
# from io import BytesIO

# app = FastAPI()

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"🚀 Using device: {device}")

# diarization_pipeline = Pipeline.from_pretrained(
#     "pyannote/speaker-diarization-3.0",
#     use_auth_token="your api for hugging face"
# ).to(device)

# embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=device)

# def load_audio(audio_bytes):
#     audio = AudioSegment.from_file(BytesIO(audio_bytes)).set_frame_rate(16000).set_channels(1)
#     return np.array(audio.get_array_of_samples(), dtype=np.float32) / (2**15)

# def extract_embedding(audio_array):
#     tensor_waveform = torch.tensor(audio_array, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
#     return embedding_model(tensor_waveform)

# @app.post("/diarize/")
# async def diarize(
#     audio_file: UploadFile = File(...),
#     reference_speaker_1_patient: UploadFile = File(...),
#     reference_speaker_2_doctor: UploadFile = File(...)
# ):
#     audio_samples = load_audio(await audio_file.read())
#     embedding_ref_1 = extract_embedding(load_audio(await reference_speaker_1_patient.read()))
#     embedding_ref_2 = extract_embedding(load_audio(await reference_speaker_2_doctor.read()))

#     diarization_result = diarization_pipeline({"waveform": torch.tensor(audio_samples).unsqueeze(0), "sample_rate": 16000}, num_speakers=2)
    
#     merged_segments = []
#     previous = None
#     for segment in diarization_result.itertracks(yield_label=True):
#         start, end, speaker = segment[0].start, segment[0].end, segment[1]
#         if previous and previous[2] == speaker and start - previous[1] < 1.0:
#             previous = (previous[0], end, speaker)
#         else:
#             if previous:
#                 merged_segments.append(previous)
#             previous = (start, end, speaker)
#     if previous:
#         merged_segments.append(previous)
    
#     transcriptions = []
#     for start, end, speaker in merged_segments:
#         segment_audio = audio_samples[int(start * 16000):int(end * 16000)]
#         segment_audio_bytes = AudioSegment(
#             segment_audio.astype(np.int16).tobytes(),
#             frame_rate=16000,
#             sample_width=2,
#             channels=1
#         ).export(format="wav").read()
        
#         files = {"audio": ("segment.wav", segment_audio_bytes, "audio/wav")}
#         transcription_response = requests.post(
#             "http://fs.wiseyak.com:8048/transcribe_english/",
#             files=files,
#             headers={"accept": "application/json", "Content-Type": "multipart/form-data"}
#         )
#         transcription_text = transcription_response.text.strip().strip('"')
        
#         segment_embedding = extract_embedding(segment_audio)
#         similarity_1 = cosine_similarity(embedding_ref_1.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
#         similarity_2 = cosine_similarity(embedding_ref_2.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
#         assigned_speaker = "student" if similarity_1 > similarity_2 else "teacher"
        
#         transcriptions.append({
#             "start_time": f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{start%60:06.3f}",
#             "end_time": f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{end%60:06.3f}",
#             "speaker": assigned_speaker,
#             "text": transcription_text
#         })
#         gc.collect()
    
#     return json.dumps(transcriptions, indent=4, ensure_ascii=False)





















# import json
# import torch
# import numpy as np
# import gc
# import requests
# from fastapi import FastAPI, File, UploadFile, Query, Depends
# from pyannote.audio import Pipeline
# from sklearn.metrics.pairwise import cosine_similarity
# from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
# from pydub import AudioSegment
# from io import BytesIO
# from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
# from sqlalchemy.orm import sessionmaker, relationship
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime


# from fastapi.middleware.cors import CORSMiddleware

# # Database setup
# DATABASE_URL = "postgresql://postgres:heheboii420@localhost/patients_db"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()


# class PatientProblem(Base):
#     __tablename__ = "patient_problem"

#     uuid = Column(String, primary_key=True)
#     session_id = Column(Integer)
#     patient_id = Column(String, ForeignKey('patient_details.patient_id'))
#     problem_description = Column(String)
#     audio_file = Column(String, nullable=True)
#     summary = Column(String)
#     date = Column(DateTime, default=datetime.utcnow)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# app = FastAPI()





# origins = [
#     "http://localhost:8000",  # Local React development server
    
# ]

# # Add CORS middleware to the FastAPI app
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # Allow specified origins
#     allow_credentials=True,  # Allow cookies and credentials
#     allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allow all headers
# )









# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"🚀 Using device: {device}")

# diarization_pipeline = Pipeline.from_pretrained(
#     "pyannote/speaker-diarization-3.0",
#     use_auth_token="your api for hugging face"
# ).to(device)

# embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=device)

# def load_audio(audio_source):
#     if isinstance(audio_source, bytes):  # If input is raw bytes
#         audio = AudioSegment.from_file(BytesIO(audio_source))
#     elif isinstance(audio_source, str):  # If input is a file path
#         audio = AudioSegment.from_file(audio_source)
#     else:
#         raise ValueError("Invalid audio source. Must be bytes or file path.")

#     audio = audio.set_frame_rate(16000).set_channels(1)
#     return np.array(audio.get_array_of_samples(), dtype=np.float32) / (2**15)


# def extract_embedding(audio_array):
#     tensor_waveform = torch.tensor(audio_array, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
#     return embedding_model(tensor_waveform)

# @app.post("/diarize/")
# async def diarize(
#     audio_file: UploadFile = File(...),
#     patient_id: str = Query(..., description="Patient ID to retrieve reference audio"),
#     reference_speaker_2_doctor: UploadFile = File(...),
#     #  reference_speaker_2_doctor: str ="C:/Users/sauga/Downloads/teacher.wav",
#     db: SessionLocal = Depends(get_db)
# ):
#     # Fetch latest audio file path for the given patient_id
#     # latest_audio = db.query(PatientProblem.audio_file).filter_by(patient_id=patient_id).order_by(PatientProblem.date.desc()).first()
#     latest_audio = db.query(PatientProblem.audio_file)\
#     .filter(PatientProblem.patient_id == patient_id, PatientProblem.audio_file.isnot(None))\
#     .order_by(PatientProblem.date.desc())\
#     .first()

#     if not latest_audio or not latest_audio.audio_file:
#         return {"error": "No audio found for the given patient ID"}
    
#     audio_samples = load_audio(await audio_file.read())
#     embedding_ref_1 = extract_embedding(load_audio(latest_audio.audio_file))
#     embedding_ref_2 = extract_embedding(load_audio(await reference_speaker_2_doctor.read()))
#     # embedding_ref_2 = extract_embedding(load_audio(reference_speaker_2_doctor))

#     diarization_result = diarization_pipeline({"waveform": torch.tensor(audio_samples).unsqueeze(0), "sample_rate": 16000}, num_speakers=2)
    
#     merged_segments = []
#     previous = None
#     for segment in diarization_result.itertracks(yield_label=True):
#         start, end, speaker = segment[0].start, segment[0].end, segment[1]
#         if previous and previous[2] == speaker and start - previous[1] < 1.0:
#             previous = (previous[0], end, speaker)
#         else:
#             if previous:
#                 merged_segments.append(previous)
#             previous = (start, end, speaker)
#     if previous:
#         merged_segments.append(previous)
    
#     transcriptions = []
#     for start, end, speaker in merged_segments:
#         segment_audio = audio_samples[int(start * 16000):int(end * 16000)]
#         segment_audio_bytes = AudioSegment(
#             segment_audio.astype(np.int16).tobytes(),
#             frame_rate=16000,
#             sample_width=2,
#             channels=1
#         ).export(format="wav").read()
        
#         files = {"audio": ("segment.wav", segment_audio_bytes, "audio/wav")}
#         transcription_response = requests.post(
#             "http://fs.wiseyak.com:8048/transcribe_english/",
#             files=files,
#             headers={"accept": "application/json", "Content-Type": "multipart/form-data"}
#         )
#         transcription_text = transcription_response.text.strip().strip('"')
        
#         segment_embedding = extract_embedding(segment_audio)
#         similarity_1 = cosine_similarity(embedding_ref_1.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
#         similarity_2 = cosine_similarity(embedding_ref_2.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
#         assigned_speaker = "patient" if similarity_1 > similarity_2 else "doctor"
        
#         transcriptions.append({
#             "start_time": f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{start%60:06.3f}",
#             "end_time": f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{end%60:06.3f}",
#             "speaker": assigned_speaker,
#             "text": transcription_text
#         })
#         gc.collect()
    
#     return json.dumps(transcriptions, indent=4, ensure_ascii=False)







# import json
# import torch
# import numpy as np
# import gc
# import requests
# from fastapi import FastAPI, File, UploadFile, Query, Depends, HTTPException
# from pyannote.audio import Pipeline
# from sklearn.metrics.pairwise import cosine_similarity
# from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
# from pydub import AudioSegment
# from io import BytesIO
# from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
# from sqlalchemy.orm import sessionmaker, relationship, Session
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime
# from fastapi.middleware.cors import CORSMiddleware

# # Database setup
# DATABASE_URL = "postgresql://postgres:heheboii420@localhost/patients_db"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# class PatientProblem(Base):
#     __tablename__ = "patient_problem"
#     uuid = Column(String, primary_key=True)
#     session_id = Column(Integer)
#     patient_id = Column(String, ForeignKey('patient_details.patient_id'))
#     problem_description = Column(String)
#     audio_file = Column(String, nullable=True)
#     summary = Column(String)
#     date = Column(DateTime, default=datetime.utcnow)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8000"],  # Adjust based on frontend needs
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load Models
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"🚀 Using device: {device}")

# diarization_pipeline = Pipeline.from_pretrained(
#     "pyannote/speaker-diarization-3.0",
#     use_auth_token="your-huggingface-api-token"
# ).to(device)

# embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=device)

# def load_audio(audio_source):
#     """Loads audio from bytes or file path and returns a normalized numpy array."""
#     try:
#         if isinstance(audio_source, bytes):
#             audio = AudioSegment.from_file(BytesIO(audio_source))
#         elif isinstance(audio_source, str):
#             audio = AudioSegment.from_file(audio_source)
#         else:
#             raise ValueError("Invalid audio source. Must be bytes or file path.")
#         return np.array(audio.set_frame_rate(16000).set_channels(1).get_array_of_samples(), dtype=np.float32) / (2**15)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error loading audio: {str(e)}")

# def extract_embedding(audio_array):
#     """Extracts speaker embedding from audio."""
#     tensor_waveform = torch.tensor(audio_array, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
#     return embedding_model(tensor_waveform)

# @app.post("/diarize/")
# async def diarize(
#     audio_file: UploadFile = File(...),
#     patient_id: str = Query(..., description="Patient ID to retrieve reference audio"),
#     # reference_speaker_2_doctor: str ="C:/Users/sauga/Downloads/teacher.wav",
#     reference_speaker_2_doctor: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     """Processes uploaded audio, diarizes speakers, and returns structured transcription."""
    
#     # Get latest patient audio
#     latest_audio = db.query(PatientProblem.audio_file)\
#         .filter(PatientProblem.patient_id == patient_id, PatientProblem.audio_file.isnot(None))\
#         .order_by(PatientProblem.date.desc())\
#         .first()

#     if not latest_audio or not latest_audio.audio_file:
#         raise HTTPException(status_code=404, detail="No patient audio found for the given ID.")

#     # Load Audio Files
#     try:
#         audio_samples = load_audio(await audio_file.read())
#         embedding_ref_1 = extract_embedding(load_audio(latest_audio.audio_file))
#         embedding_ref_2 = extract_embedding(load_audio(await reference_speaker_2_doctor.read()))
#         # embedding_ref_2 = extract_embedding(load_audio(reference_speaker_2_doctor))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error processing audio files: {str(e)}")

#     # Perform Diarization
#     diarization_result = diarization_pipeline({"waveform": torch.tensor(audio_samples).unsqueeze(0), "sample_rate": 16000}, num_speakers=2)

#     # Merge Speaker Segments (For Readability)
#     merged_segments = []
#     previous = None
#     for segment in diarization_result.itertracks(yield_label=True):
#         start, end, speaker = segment[0].start, segment[0].end, segment[1]
#         if previous and previous[2] == speaker and start - previous[1] < 1.0:
#             previous = (previous[0], end, speaker)
#         else:
#             if previous:
#                 merged_segments.append(previous)
#             previous = (start, end, speaker)
#     if previous:
#         merged_segments.append(previous)

#     # Process Each Speaker Segment
#     transcriptions = []
#     for start, end, speaker in merged_segments:
#         # Extract segment
#         segment_audio = (audio_samples[int(start * 16000):int(end * 16000)] * 32767).astype(np.int16)

#         # Convert to bytes for API request
#         segment_audio_bytes = AudioSegment(
#             segment_audio.tobytes(),
#             frame_rate=16000,
#             sample_width=2,
#             channels=1
#         ).export(format="wav").read()

#         # Send to transcription service
#         files = {"audio": ("segment.wav", segment_audio_bytes, "audio/wav")}
#         transcription_response = requests.post(
#             "http://fs.wiseyak.com:8048/transcribe_english/",
#             files=files
          
#         )

#         # Validate API response
#         try:
#             transcription_text = transcription_response.json()
#             if isinstance(transcription_text, dict) and "text" in transcription_text:
#                 transcription_text = transcription_text["text"]
#             else:
#                 transcription_text = str(transcription_text)
#         except json.JSONDecodeError:
#             transcription_text = transcription_response.text.strip().strip('"')

#         # Speaker Identification
#         segment_embedding = extract_embedding(segment_audio / 32767.0)
#         similarity_1 = cosine_similarity(embedding_ref_1.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
#         similarity_2 = cosine_similarity(embedding_ref_2.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
#         assigned_speaker = "patient" if similarity_1 > similarity_2 else "doctor"

#         # Store Transcription
#         transcriptions.append({
#             "start_time": f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{start%60:06.3f}",
#             "end_time": f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{end%60:06.3f}",
#             "speaker": assigned_speaker,
#             "text": transcription_text
#         })
#         gc.collect()

#     return {"transcriptions": transcriptions}



























# import json
# import torch
# import numpy as np
# import gc
# import requests
# from fastapi import FastAPI, File, UploadFile, Query, Depends, HTTPException
# from pyannote.audio import Pipeline
# from sklearn.metrics.pairwise import cosine_similarity
# from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
# from pydub import AudioSegment
# from io import BytesIO
# from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
# from sqlalchemy.orm import sessionmaker, relationship, Session
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime
# from fastapi.middleware.cors import CORSMiddleware

# # Database setup
# DATABASE_URL = "postgresql://postgres:heheboii420@localhost/patients_db"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# class PatientProblem(Base):
#     __tablename__ = "patient_problem"
#     uuid = Column(String, primary_key=True)
#     session_id = Column(Integer)
#     patient_id = Column(String, ForeignKey('patient_details.patient_id'))
#     problem_description = Column(String)
#     audio_file = Column(String, nullable=True)
#     summary = Column(String)
#     date = Column(DateTime, default=datetime.utcnow)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load Models
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"\U0001F680 Using device: {device}")

# diarization_pipeline = Pipeline.from_pretrained(
#     "pyannote/speaker-diarization-3.0",
#     use_auth_token="your-huggingface-api-token"
# ).to(device)

# embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=device)

# # Store Reference Speaker Path
# global_reference_speaker_path = None

# def load_audio(audio_source):
#     try:
#         if isinstance(audio_source, bytes):
#             audio = AudioSegment.from_file(BytesIO(audio_source))
#         elif isinstance(audio_source, str):
#             audio = AudioSegment.from_file(audio_source)
#         else:
#             raise ValueError("Invalid audio source. Must be bytes or file path.")
#         return np.array(audio.set_frame_rate(16000).set_channels(1).get_array_of_samples(), dtype=np.float32) / (2**15)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error loading audio: {str(e)}")

# def extract_embedding(audio_array):
#     tensor_waveform = torch.tensor(audio_array, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
#     return embedding_model(tensor_waveform)

# @app.post("/set_reference_speaker/")
# async def set_reference_speaker(audio_file: UploadFile = File(...)):
#     global global_reference_speaker_path
#     try:
#         file_path = f"./uploaded_reference_{audio_file.filename}"
#         with open(file_path, "wb") as buffer:
#             buffer.write(await audio_file.read())
#         global_reference_speaker_path = file_path
#         return {"message": "Reference speaker audio stored successfully", "path": file_path}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error saving reference speaker file: {str(e)}")

# @app.post("/diarize/")
# async def diarize(
#     audio_file: UploadFile = File(...),
#     patient_id: str = Query(..., description="Patient ID to retrieve reference audio"),
#     db: Session = Depends(get_db)
# ):
#     global global_reference_speaker_path
    
#     if not global_reference_speaker_path:
#         raise HTTPException(status_code=400, detail="Reference speaker audio not set. Please upload first.")
    
#     latest_audio = db.query(PatientProblem.audio_file)\
#         .filter(PatientProblem.patient_id == patient_id, PatientProblem.audio_file.isnot(None))\
#         .order_by(PatientProblem.date.desc())\
#         .first()

#     if not latest_audio or not latest_audio.audio_file:
#         raise HTTPException(status_code=404, detail="No patient audio found for the given ID.")
    
#     try:
#         audio_samples = load_audio(await audio_file.read())
#         embedding_ref_1 = extract_embedding(load_audio(latest_audio.audio_file))
#         embedding_ref_2 = extract_embedding(load_audio(global_reference_speaker_path))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error processing audio files: {str(e)}")

#     diarization_result = diarization_pipeline({"waveform": torch.tensor(audio_samples).unsqueeze(0), "sample_rate": 16000}, num_speakers=2)

#     merged_segments = []
#     previous = None
#     for segment in diarization_result.itertracks(yield_label=True):
#         start, end, speaker = segment[0].start, segment[0].end, segment[1]
#         if previous and previous[2] == speaker and start - previous[1] < 1.0:
#             previous = (previous[0], end, speaker)
#         else:
#             if previous:
#                 merged_segments.append(previous)
#             previous = (start, end, speaker)
#     if previous:
#         merged_segments.append(previous)

#     transcriptions = []
#     for start, end, speaker in merged_segments:
#         segment_audio = (audio_samples[int(start * 16000):int(end * 16000)] * 32767).astype(np.int16)
#         segment_audio_bytes = AudioSegment(
#             segment_audio.tobytes(),
#             frame_rate=16000,
#             sample_width=2,
#             channels=1
#         ).export(format="wav").read()

#         files = {"audio": ("segment.wav", segment_audio_bytes, "audio/wav")}
#         transcription_response = requests.post(
#             "http://fs.wiseyak.com:8048/transcribe_english/",
#             files=files
#         )
        
#         try:
#             transcription_text = transcription_response.json()
#             if isinstance(transcription_text, dict) and "text" in transcription_text:
#                 transcription_text = transcription_text["text"]
#             else:
#                 transcription_text = str(transcription_text)
#         except json.JSONDecodeError:
#             transcription_text = transcription_response.text.strip().strip('"')  # Fallback to raw response

#         segment_embedding = extract_embedding(segment_audio / 32767.0)
#         similarity_1 = cosine_similarity(embedding_ref_1.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
#         similarity_2 = cosine_similarity(embedding_ref_2.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
#         assigned_speaker = "patient" if similarity_1 > similarity_2 else "doctor"

#         transcriptions.append({"start_time": start, "end_time": end, "speaker": assigned_speaker, "text": transcription_text})
#         gc.collect()

#     return {"transcriptions": transcriptions}





# import json
# import torch
# import numpy as np
# import gc
# import requests
# from fastapi import FastAPI, File, UploadFile, Query, Depends, HTTPException
# from pyannote.audio import Pipeline
# from sklearn.metrics.pairwise import cosine_similarity
# from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
# from pydub import AudioSegment
# from io import BytesIO
# from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
# from sqlalchemy.orm import sessionmaker, relationship, Session
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime
# from fastapi.middleware.cors import CORSMiddleware
# from summary import get_medical_information

# # Database setup
# DATABASE_URL = "postgresql://postgres:heheboii420@localhost/patients_db"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# class PatientProblem(Base):
#     __tablename__ = "patient_problem"
#     uuid = Column(String, primary_key=True)
#     session_id = Column(Integer)
#     patient_id = Column(String, ForeignKey('patient_details.patient_id'))
#     problem_description = Column(String)
#     audio_file = Column(String, nullable=True)
#     summary = Column(String)
#     date = Column(DateTime, default=datetime.utcnow)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load Models (CPU only)
# device = torch.device("cpu")  # Force CPU mode
# print(f"🚀 Using device: {device}")

# diarization_pipeline = Pipeline.from_pretrained(
#     "pyannote/speaker-diarization-3.0",
#     use_auth_token="your-huggingface-api-token"
# ).to(device)

# embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=device)

# # Store Reference Speaker Path
# global_reference_speaker_path = None

# def load_audio(audio_source):
#     """Loads and normalizes audio data from file or bytes."""
#     try:
#         if isinstance(audio_source, bytes):
#             audio = AudioSegment.from_file(BytesIO(audio_source))
#         elif isinstance(audio_source, str):
#             audio = AudioSegment.from_file(audio_source)
#         else:
#             raise ValueError("Invalid audio source. Must be bytes or file path.")

#         # Convert to 16kHz, mono, WAV format
#         audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

#         # Export to a temporary WAV file and reload as numpy array
#         temp_wav = BytesIO()
#         audio.export(temp_wav, format="wav")
#         temp_wav.seek(0)

#         audio_array = np.array(AudioSegment.from_file(temp_wav).get_array_of_samples(), dtype=np.float32) / (2**15)

#         # 🚨 Debugging
#         if len(audio_array) == 0:
#             raise ValueError("Error: Audio file is empty or corrupted.")

#         if np.isnan(audio_array).any():
#             raise ValueError("Error: Audio array contains NaN values.")

#         return np.nan_to_num(audio_array)  # Replace NaNs with zeroes

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error loading audio: {str(e)}")

# def extract_embedding(audio_array):
#     """Extracts a speaker embedding from an audio array."""
#     try:
#         if len(audio_array) == 0:
#             raise ValueError("Error: Received empty audio array for embedding extraction.")

#         tensor_waveform = torch.tensor(audio_array, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

#         with torch.no_grad():
#             embedding = embedding_model(tensor_waveform)  # No need to call `.numpy()`

#         if np.isnan(embedding).any():
#             raise ValueError("Error: Embedding contains NaN values.")

#         return np.nan_to_num(embedding)  # Ensure no NaNs

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error extracting embedding: {str(e)}")


# # @app.post("/set_reference_speaker/")
# # async def set_reference_speaker(audio_file: UploadFile = File(...)):
# #     """Stores reference speaker audio for comparison."""
# #     global global_reference_speaker_path
# #     try:
# #         file_path = f"./uploaded_reference_{audio_file.filename}"
# #         with open(file_path, "wb") as buffer:
# #             buffer.write(await audio_file.read())
# #         global_reference_speaker_path = file_path
# #         return {"message": "Reference speaker audio stored successfully", "path": file_path}
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Error saving reference speaker file: {str(e)}")


# @app.post("/set_reference_speaker/")
# async def set_reference_speaker(
#     audio_file: UploadFile = File(...),
#     session_id: int = Query(..., description="Session ID"),
#     doctor_id: str = Query(..., description="Doctor ID")
# ):
#     """Stores reference speaker audio for comparison, including session and doctor metadata."""
#     global global_reference_speaker_path
#     try:
#         file_path = f"./uploaded_reference_{audio_file.filename}"
#         with open(file_path, "wb") as buffer:
#             buffer.write(await audio_file.read())
        
#         global_reference_speaker_path = file_path
        
#         return {
#             "message": "Reference speaker audio stored successfully",
#             "path": file_path,
#             "session_id": session_id,
#             "doctor_id": doctor_id
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error saving reference speaker file: {str(e)}")



# @app.post("/diarize/")
# async def diarize(
#     audio_file: UploadFile = File(...),
#     patient_id: str = Query(..., description="Patient ID to retrieve reference audio"),
#     db: Session = Depends(get_db)
# ):
#     """Performs speaker diarization, extracts patient's speech, and runs medical analysis."""
#     global global_reference_speaker_path
    
#     if not global_reference_speaker_path:
#         raise HTTPException(status_code=400, detail="Reference speaker audio not set. Please upload first.")
    
#     latest_audio = db.query(PatientProblem.audio_file)\
#         .filter(PatientProblem.patient_id == patient_id, PatientProblem.audio_file.isnot(None))\
#         .order_by(PatientProblem.date.desc())\
#         .first()

#     if not latest_audio or not latest_audio.audio_file:
#         raise HTTPException(status_code=404, detail="No patient audio found for the given ID.")
    
#     try:
#         audio_samples = load_audio(await audio_file.read())
#         embedding_ref_1 = extract_embedding(load_audio(latest_audio.audio_file))
#         embedding_ref_2 = extract_embedding(load_audio(global_reference_speaker_path))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error processing audio files: {str(e)}")

#     diarization_result = diarization_pipeline(
#         {"waveform": torch.tensor(audio_samples).unsqueeze(0), "sample_rate": 16000}, 
#         num_speakers=1
#     )

#     transcriptions = []
#     patient_texts = []
    
#     for segment in diarization_result.itertracks(yield_label=True):
#         start, end, speaker = segment[0].start, segment[0].end, segment[1]
#         segment_audio = (audio_samples[int(start * 16000):int(end * 16000)] * 32767).astype(np.int16)
        
#         # Convert segment to WAV format
#         segment_audio_bytes = AudioSegment(
#             segment_audio.tobytes(),
#             frame_rate=16000,
#             sample_width=2,
#             channels=1
#         ).export(format="wav").read()

#         files = {"audio": ("segment.wav", segment_audio_bytes, "audio/wav")}
#         transcription_response = requests.post("http://fs.wiseyak.com:8048/transcribe_english/", files=files)

#         try:
#             transcription_text = transcription_response.json()  # Try parsing as JSON
#             if isinstance(transcription_text, dict) and "text" in transcription_text:
#                 transcription_text = transcription_text["text"]
#             else:
#                 transcription_text = str(transcription_text)  # Convert to string if not a dict
#         except json.JSONDecodeError:
#             transcription_text = transcription_response.text.strip()  # Use raw response



#         segment_embedding = extract_embedding(segment_audio / 32767.0)
#         similarity_1 = cosine_similarity(np.nan_to_num(embedding_ref_1).reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
#         similarity_2 = cosine_similarity(np.nan_to_num(embedding_ref_2).reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
#         assigned_speaker = "patient" if similarity_1 > similarity_2 else "doctor"

#         transcriptions.append({"start_time": start, "end_time": end, "speaker": assigned_speaker, "text": transcription_text})

#         if assigned_speaker == "patient":
#             patient_texts.append(transcription_text)
    
#     # Combine patient's text for medical processing
#     patient_input_text = " ".join(patient_texts)

#     # Get medical analysis
#     medical_analysis = get_medical_information(patient_input_text)

#     # Return both transcription and medical information
#     return {
#         "transcription_result": transcriptions,
#         "medical_analysis": medical_analysis
#     }




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
