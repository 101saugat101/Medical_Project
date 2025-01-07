from transformers import pipeline

# Load the summarization pipeline
summarizer = pipeline("summarization")

# Load the transcription text from the file
input_file = "/content/transcription_output.txt"  # Path to the input transcription file
with open(input_file, "r", encoding="utf-8") as file:
    text = file.read()

# Summarize the text
summary = summarizer(text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']

# Save the summary to a new file
output_file = "/content/summarized.txt"  # Path to the output summary file
with open(output_file, "w", encoding="utf-8") as file:
    file.write(summary)

print(f"Summary saved to {output_file}")
