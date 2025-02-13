import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
import json
import re

class MedicalInformation(BaseModel):
    condition_overview: str
    symptoms: list
    diagnosis: list
    treatment: list
    prevention: list

def clean_json_string(text):
    """Extract and clean JSON from the model's response."""
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        json_str = re.sub(r'```json|```', '', json_str)
        return json_str.strip()
    return None

def create_medical_prompt(user_input):
    return [
        {
            "role": "system",
            "content": "You are an expert medical assistant. Provide responses in valid JSON format only. Provide 3 points for each keypoint in the json make it short and to the point."
        },
        {
            "role": "user",
            "content": f"""Based on these symptoms/concerns: '{user_input}', 
            provide medical information in this exact JSON format:

            {{
                "disease_overview": "Brief summary of the likely condition",
                "symptoms": ["symptom 1", "symptom 2", "symptom 3"],
                "diagnosis": ["possible disease 1", "possible disease 2", "possible disease 3"],
                "treatment": ["treatment 1", "treatment 2", "treatment 3"],
                "prevention": ["prevention measure 1", "prevention measure 2", "prevention measure 3"]
            }}

            Return ONLY the JSON with no additional text or formatting."""
        }
    ]

# def get_medical_information(user_input):
#     """Calls Google's Gemini API to analyze medical symptoms."""
#     try:
#         model = ChatGoogleGenerativeAI(
#             model="gemini-2.0-flash",
#             temperature=0,
#             # google_api_key=os.getenv("AIzaSyCHh4vaVl5efQ1Xza9PgovJYDApoHlJ4B8")  # Replace with your actual API key
#             google_api_key="AIzaSyCHh4vaVl5efQ1Xza9PgovJYDApoHlJ4B8"

#         )

#         prompt = create_medical_prompt(user_input)
#         response = model.invoke(prompt)

#         json_str = clean_json_string(response.content)
#         if not json_str:
#             return {"error": "Could not extract JSON from response"}

#         try:
#             medical_info = json.loads(json_str)
#             validated_info = MedicalInformation(**medical_info)
#             return validated_info.model_dump()
#         except json.JSONDecodeError as je:
#             return {"error": f"Failed to parse JSON response: {str(je)}", "raw_response": response.content}
#         except Exception as ve:
#             return {"error": f"Failed to validate response structure: {str(ve)}", "raw_response": response.content}
#     except Exception as e:
#         return {"error": f"An error occurred: {str(e)}"}


def get_medical_information(user_input):
    """Calls Google's Gemini API to analyze medical symptoms."""
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key="AIzaSyCHh4vaVl5efQ1Xza9PgovJYDApoHlJ4B8" # Load API key from environment
        )

        prompt = create_medical_prompt(user_input)
        response = model.invoke(prompt)

        json_str = clean_json_string(response.content)
        if not json_str:
            return {"error": "Could not extract JSON from response"}

        try:
            medical_info = json.loads(json_str)

            # ✅ FIX: Rename "disease_overview" to "condition_overview" if present
            if "disease_overview" in medical_info:
                medical_info["condition_overview"] = medical_info.pop("disease_overview")

            # Validate the response using Pydantic model
            validated_info = MedicalInformation(**medical_info)
            return validated_info.model_dump()

        except json.JSONDecodeError as je:
            return {
                "error": f"Failed to parse JSON response: {str(je)}",
                "raw_response": response.content
            }
        except Exception as ve:
            return {
                "error": f"Failed to validate response structure: {str(ve)}",
                "raw_response": response.content
            }
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
