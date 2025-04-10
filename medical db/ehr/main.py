import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any

# Import the existing EHRDataExtractor and related functions
from test import EHRDataExtractor

app = FastAPI()

@app.post("/upload/")
async def upload_json(file: UploadFile = File(...)):
    """
    Upload a JSON file containing a medical conversation, 
    process it to extract medical details, generate diagnoses, 
    and produce ICD-10-CM codes.
    """
    try:
        # Read and load the JSON file
        contents = await file.read()
        conversation_data = json.loads(contents)

        # Initialize the extractor
        extractor = EHRDataExtractor()
        
        # Extract medical data
        ehr_details = extractor.extract_medical_data(conversation_data)
        
        # Generate possible diagnoses
        possible_diagnosis = extractor.analyze_conversation_for_diagnoses(conversation_data)
        
        # Extract doctor's diagnosis
        doctor_diagnosis = ehr_details.get("Doctor Diagnosis")
        
        # Generate ICD codes
        icd_codes = extractor.generate_icd_codes(doctor_diagnosis, possible_diagnosis)
        
        # Combine extracted data
        combined_data = {
            "ehr_details": ehr_details,
            "possible_diagnosis": possible_diagnosis,
            "icd_codes": icd_codes
        }
        
        return JSONResponse(content=combined_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
