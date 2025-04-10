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
