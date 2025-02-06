import json
import torch
import numpy as np
import gc
import requests
from fastapi import FastAPI, File, UploadFile
from pyannote.audio import Pipeline
from sklearn.metrics.pairwise import cosine_similarity
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pydub import AudioSegment
from io import BytesIO

app = FastAPI()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Using device: {device}")

diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.0",
    use_auth_token="your api for hugging face"
).to(device)

embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=device)

def load_audio(audio_bytes):
    audio = AudioSegment.from_file(BytesIO(audio_bytes)).set_frame_rate(16000).set_channels(1)
    return np.array(audio.get_array_of_samples(), dtype=np.float32) / (2**15)

def extract_embedding(audio_array):
    tensor_waveform = torch.tensor(audio_array, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    return embedding_model(tensor_waveform)

@app.post("/diarize/")
async def diarize(
    audio_file: UploadFile = File(...),
    reference_speaker_1: UploadFile = File(...),
    reference_speaker_2: UploadFile = File(...)
):
    audio_samples = load_audio(await audio_file.read())
    embedding_ref_1 = extract_embedding(load_audio(await reference_speaker_1.read()))
    embedding_ref_2 = extract_embedding(load_audio(await reference_speaker_2.read()))

    diarization_result = diarization_pipeline({"waveform": torch.tensor(audio_samples).unsqueeze(0), "sample_rate": 16000}, num_speakers=2)
    
    merged_segments = []
    previous = None
    for segment in diarization_result.itertracks(yield_label=True):
        start, end, speaker = segment[0].start, segment[0].end, segment[1]
        if previous and previous[2] == speaker and start - previous[1] < 1.0:
            previous = (previous[0], end, speaker)
        else:
            if previous:
                merged_segments.append(previous)
            previous = (start, end, speaker)
    if previous:
        merged_segments.append(previous)
    
    transcriptions = []
    for start, end, speaker in merged_segments:
        segment_audio = audio_samples[int(start * 16000):int(end * 16000)]
        segment_audio_bytes = AudioSegment(
            segment_audio.astype(np.int16).tobytes(),
            frame_rate=16000,
            sample_width=2,
            channels=1
        ).export(format="wav").read()
        
        files = {"audio": ("segment.wav", segment_audio_bytes, "audio/wav")}
        transcription_response = requests.post(
            "http://fs.wiseyak.com:8048/transcribe_english/",
            files=files,
            headers={"accept": "application/json", "Content-Type": "multipart/form-data"}
        )
        transcription_text = transcription_response.text.strip().strip('"')
        
        segment_embedding = extract_embedding(segment_audio)
        similarity_1 = cosine_similarity(embedding_ref_1.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
        similarity_2 = cosine_similarity(embedding_ref_2.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
        assigned_speaker = "student" if similarity_1 > similarity_2 else "teacher"
        
        transcriptions.append({
            "start_time": f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{start%60:06.3f}",
            "end_time": f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{end%60:06.3f}",
            "speaker": assigned_speaker,
            "text": transcription_text
        })
        gc.collect()
    
    return json.dumps(transcriptions, indent=4, ensure_ascii=False)