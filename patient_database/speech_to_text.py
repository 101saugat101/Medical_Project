# ! pip install git+https://github.com/huggingface/transformers -q 

from transformers import pipeline

whisper = pipeline('automatic-speech-recognition', model = 'openai/whisper-medium', device = 0)

# Pass return_timestamps=True to the pipeline call
text = whisper('/content/speech_transciption.mp3', return_timestamps=True) 

print(text['text'])