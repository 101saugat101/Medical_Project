from transformers import pipeline

model = pipeline("automatic-speech-recognition")

input = model("/content/speech_transciption.mp3")
transcription_text = input['text']

# Save the transcription to a .txt file
output_file = "/content/transcription_output.txt"  # Specify the output file path
with open(output_file, "w", encoding="utf-8") as file:
    file.write(transcription_text)

print(f"Transcription saved to {output_file}")
