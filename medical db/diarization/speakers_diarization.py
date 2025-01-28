import whisper
import subprocess
import torch
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pyannote.audio import Audio
from pyannote.core import Segment
import wave
import contextlib
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

# Path to audio file
path = "/content/test.wav"
reference_audio_1 = "/content/student.wav"  
reference_audio_2 = "/content/teacher.wav" 

language = 'English'
model_size = 'base'

model = whisper.load_model(model_size)

embedding_model = PretrainedSpeakerEmbedding(
    "speechbrain/spkrec-ecapa-voxceleb",
    device=torch.device("cuda")
)

def get_audio_duration(path):
    with contextlib.closing(wave.open(path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)

def extract_embedding(audio_path):
    audio_duration = get_audio_duration(audio_path)
    segment = Segment(0, audio_duration)
    waveform, sample_rate = Audio().crop(audio_path, segment)
    if waveform.shape[0] > 1:  # Convert to mono if stereo
        waveform = waveform.mean(axis=0, keepdims=True)
    return embedding_model(waveform[None])

embedding_ref_1 = extract_embedding(reference_audio_1)
embedding_ref_2 = extract_embedding(reference_audio_2)

# Process main audio
if path[-3:] != 'wav':
    subprocess.call(['ffmpeg', '-i', path, 'audio.wav', '-y'])
    path = 'audio.wav'

result = model.transcribe(path)
segments = result["segments"]
duration = get_audio_duration(path)

audio = Audio()
def segment_embedding(segment):
    start = segment["start"]
    end = min(duration, segment["end"])  # Handle end of file
    clip = Segment(start, end)
    waveform, sample_rate = audio.crop(path, clip)
    if waveform.shape[0] > 1:  # Convert to mono if stereo
        waveform = waveform.mean(axis=0, keepdims=True)
    return embedding_model(waveform[None])

segment_embeddings = np.zeros((len(segments), 192))
for i, segment in enumerate(segments):
    segment_embeddings[i] = segment_embedding(segment)


SIMILARITY_THRESHOLD = 0.7  # Adjust this value based on your needs

speakers = []
for embedding in segment_embeddings:
    similarity_1 = cosine_similarity(embedding_ref_1.reshape(1, -1), embedding.reshape(1, -1))[0][0]
    similarity_2 = cosine_similarity(embedding_ref_2.reshape(1, -1), embedding.reshape(1, -1))[0][0]

    # Assign to speaker1 or speaker2 if similarity is above the threshold
    if similarity_1 > similarity_2 and similarity_1 >= SIMILARITY_THRESHOLD:
        speakers.append("student")
    elif similarity_2 > similarity_1 and similarity_2 >= SIMILARITY_THRESHOLD:
        speakers.append("teacher")
    else:
        speakers.append(None) 

# Generate chat format transcript, ignoring segments with `None`
chat_transcript = []
for i, segment in enumerate(segments):
    speaker = speakers[i]
    if speaker:  # Include only the relevant speakers
        text = segment["text"].strip()
        chat_transcript.append(f'{speaker}: "{text}"')

with open('chat_transcript.json', 'w') as f:
    json.dump(chat_transcript, f, indent=4)

print("Diarization completed and saved to 'chat_transcript.json'.")
