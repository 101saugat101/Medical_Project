

import json
import torch
import numpy as np
import gc
import requests
from pyannote.audio import Pipeline
from sklearn.metrics.pairwise import cosine_similarity
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pydub import AudioSegment

def main():
    # 🔹 Paths
    AUDIO_FILE = "D:\\diarization\\test.wav"
    REFERENCE_SPEAKER_1 = "D:\\diarization\\student.wav"
    REFERENCE_SPEAKER_2 = "D:\\diarization\\teacher.wav"
    OUTPUT_JSON = "D:\\diarization\\output.json"

    # 🔹 Load models
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    diarization_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.0",
        use_auth_token="your api for hugging face"
    ).to(device)
    
    embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=device)

    # 🔹 Function: Load & Preprocess Audio (In-Memory)
    def load_audio(audio_path):
        audio = AudioSegment.from_file(audio_path).set_frame_rate(16000).set_channels(1)
        return np.array(audio.get_array_of_samples(), dtype=np.float32) / (2**15)  # Normalize

    # 🔹 Function: Extract Speaker Embedding
    def extract_embedding(audio_array):
        tensor_waveform = torch.tensor(audio_array, dtype=torch.float32).unsqueeze(0).unsqueeze(0)  # (1, 1, num_samples)
        return embedding_model(tensor_waveform)

    # 🔹 Load Main & Reference Audio
    audio_samples = load_audio(AUDIO_FILE)
    embedding_ref_1 = extract_embedding(load_audio(REFERENCE_SPEAKER_1))
    embedding_ref_2 = extract_embedding(load_audio(REFERENCE_SPEAKER_2))

    # 🔹 Perform Diarization
    diarization_result = diarization_pipeline({"waveform": torch.tensor(audio_samples).unsqueeze(0), "sample_rate": 16000}, num_speakers=2)
    del diarization_pipeline  # Free memory

    # 🔹 Merge Speaker Segments (For Readability)
    merged_segments = []
    previous = None
    for segment in diarization_result.itertracks(yield_label=True):
        start, end, speaker = segment[0].start, segment[0].end, segment[1]
        if previous and previous[2] == speaker and start - previous[1] < 1.0:
            previous = (previous[0], end, speaker)  # Merge with previous
        else:
            if previous:
                merged_segments.append(previous)
            previous = (start, end, speaker)
    if previous:
        merged_segments.append(previous)

    # 🔹 Process Each Speaker Segment
    transcriptions = []
    for start, end, speaker in merged_segments:
        segment_audio = audio_samples[int(start * 16000):int(end * 16000)]  # Extract segment
        segment_audio_bytes = AudioSegment(
            segment_audio.astype(np.int16).tobytes(),
            frame_rate=16000,
            sample_width=2,
            channels=1
        ).export(format="wav").read()

        # Send to transcription service
        files = {"audio": ("segment.wav", segment_audio_bytes, "audio/wav")}
        transcription_response = requests.post(
            "http://fs.wiseyak.com:8048/transcribe_english/",
            files=files,
            headers={"accept": "application/json", "Content-Type": "multipart/form-data"}
        )

        transcription_text = transcription_response.text.strip().strip('"')  # Remove surrounding quotes

        # Speaker Identification
        segment_embedding = extract_embedding(segment_audio)
        similarity_1 = cosine_similarity(embedding_ref_1.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
        similarity_2 = cosine_similarity(embedding_ref_2.reshape(1, -1), segment_embedding.reshape(1, -1))[0][0]
        assigned_speaker = "student" if similarity_1 > similarity_2 else "teacher"

        # Store Result
        transcriptions.append({
            "start_time": f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{start%60:06.3f}",
            "end_time": f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{end%60:06.3f}",
            "speaker": assigned_speaker,
            "text": transcription_text
        })
        gc.collect()  # Free memory

    # 🔹 Save Output
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(transcriptions, f, indent=4, ensure_ascii=False)

    print(f"✅ Transcriptions saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
