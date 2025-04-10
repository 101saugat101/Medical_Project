import os
import json
from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Configure Gemini API and the model
google_api_key = "AIzaSyBGry6LwqLN_j1fPHh0ZfoOkf7oaGGgdbo"
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=google_api_key,
    temperature=0.1,
    max_tokens=8000,
    timeout=None,
    max_retries=2
)

# Define the state for the EHR extraction workflow
class State(TypedDict):
    messages: Annotated[list, add_messages]
    conversation: Optional[Dict[str, Any]]
    ehr_details: Optional[Dict[str, Any]]
    possible_diagnosis: Optional[Dict[str, Any]]
    icd_codes: Optional[Dict[str, Any]]
    combined_data: Optional[Dict[str, Any]]

class EHRDataExtractor:
    def __init__(self):
        # Prompt template for structured medical data extraction
        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a specialized medical data extraction AI assistant. 
            Your task is to meticulously extract structured medical information from a given conversation.

            Extraction Guidelines:
            1. Extract information precisely and accurately
            2. If no information is available for a category, set its value to null
            3. Focus on verified medical observations and professional assessments
            4. Be comprehensive but concise

            Required Extraction Categories:
            - Patient Demographics
            - Bone Health History
            - Diagnostic Imaging
            - Lab Results
            - Clinical Notes
            - Skeletal Assessments
            - Treatment Plans
            - Medications
            - Family History
            - Osteological Procedures
            - Doctor Diagnosis

            Provide a structured JSON output with these exact keys."""),
            ("human", "Extract medical information from this conversation: {conversation}")
        ])
        
        # Prompt template for diagnostic analysis
        self.diagnosis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a specialized medical diagnostic AI assistant.
            Your task is to analyze the provided medical conversation and suggest possible diagnoses.
            
            Guidelines:
            1. Consider all relevant symptoms, test results, and patient history
            2. For each potential diagnosis, provide:
               - Name of the condition
               - Confidence level (Low, Medium, High)
               - Supporting evidence from the conversation
               - Recommended follow-up tests or consultations
            3. Be thorough but avoid speculation beyond available evidence
            4. Include differential diagnoses when appropriate
            
            Structure your response as a JSON object with an array of possible diagnoses."""),
            ("human", "Analyze this medical conversation and suggest possible diagnoses: {conversation}")
        ])
        
        # Prompt template for ICD-10-CM code analysis
        self.icd_code_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a specialized medical coding AI assistant with expertise in ICD-10-CM coding.
            Your task is to analyze medical diagnoses and provide accurate ICD-10-CM codes.
            
            Guidelines:
            1. For each diagnosis (both confirmed and possible), provide:
               - The most specific ICD-10-CM code
               - The full code description
               - Coding notes or special considerations
               - Alternative codes if applicable
            2. Be precise and follow ICD-10-CM coding guidelines
            3. Include both the primary diagnosis code and any relevant secondary codes
            4. Distinguish between confirmed diagnoses and possible/differential diagnoses
            
            Structure your response as a JSON object with two main sections:
            1. confirmed_diagnosis_codes - For the doctor's final diagnosis
            2. possible_diagnosis_codes - For AI-generated possible diagnoses
            
            Each section should contain an array of code objects with the properties listed above."""),
            ("human", """Provide ICD-10-CM codes for the following:
            
            CONFIRMED DIAGNOSIS: {doctor_diagnosis}
            
            POSSIBLE DIAGNOSES: {possible_diagnoses}""")
        ])
        
        # JSON output parser
        self.output_parser = JsonOutputParser()
        
        # Create extraction chain
        self.extraction_chain = self.extraction_prompt | model | self.output_parser
        
        # Create diagnosis chain
        self.diagnosis_chain = self.diagnosis_prompt | model | self.output_parser
        
        # Create ICD code chain
        self.icd_code_chain = self.icd_code_prompt | model | self.output_parser

    def extract_medical_data(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured medical data from conversation
        
        :param conversation: Conversation data to extract medical information from
        :return: Structured medical information dictionary
        """
        try:
            # Convert conversation to string for processing
            conversation_str = json.dumps(conversation)
            
            # Invoke extraction chain
            extracted_data = self.extraction_chain.invoke({
                "conversation": conversation_str
            })
            
            return extracted_data
        
        except Exception as e:
            print(f"Error during medical data extraction: {e}")
            return {
                "Patient Demographics": None,
                "Bone Health History": None,
                "Diagnostic Imaging": None,
                "Lab Results": None,
                "Clinical Notes": None,
                "Skeletal Assessments": None,
                "Treatment Plans": None,
                "Medications": None,
                "Family History": None,
                "Osteological Procedures": None,
                "Doctor Diagnosis": None,
            }
    
    def analyze_conversation_for_diagnoses(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate couple possible alternate diagnoses based on the conversation
        
        :param conversation: Conversation data to analyze
        :return: Dictionary of possible diagnoses
        """
        try:
            # Convert conversation to string for processing
            conversation_str = json.dumps(conversation)
            
            # Invoke diagnosis chain
            diagnoses = self.diagnosis_chain.invoke({
                "conversation": conversation_str
            })
            
            return diagnoses
        
        except Exception as e:
            print(f"Error during diagnosis generation: {e}")
            return {
                "possible_diagnoses": []
            }
    
    def generate_icd_codes(self, doctor_diagnosis: str, possible_diagnoses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate ICD-10-CM codes for confirmed and possible diagnoses
        
        :param doctor_diagnosis: Doctor's confirmed diagnosis
        :param possible_diagnoses: Dictionary of possible diagnoses
        :return: Dictionary of ICD-10-CM codes for confirmed and possible diagnoses
        """
        try:
            # Format possible diagnoses for the prompt
            possible_diagnoses_str = json.dumps(possible_diagnoses)
            
            # Invoke ICD code chain
            icd_codes = self.icd_code_chain.invoke({
                "doctor_diagnosis": doctor_diagnosis if doctor_diagnosis else "No confirmed diagnosis provided",
                "possible_diagnoses": possible_diagnoses_str
            })
            
            return icd_codes
        
        except Exception as e:
            print(f"Error during ICD code generation: {e}")
            return {
                "confirmed_diagnosis_codes": [],
                "possible_diagnosis_codes": []
            }

def save_combined_data(combined_data: Dict[str, Any], output_path: str):
    """
    Save combined medical data to a JSON file
    
    :param combined_data: Combined medical information, diagnoses, and ICD codes
    :param output_path: Path to save the output JSON file
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(combined_data, f, indent=2)
        print(f"Combined data saved to {output_path}")
    except Exception as e:
        print(f"Error saving combined data: {e}")

def process_medical_data_workflow(state: State) -> State:
    """
    Node function to extract medical information and generate diagnoses
    
    :param state: Current state of the workflow
    :return: Updated state with extracted medical data and diagnoses
    """
    extractor = EHRDataExtractor()
    
    # Extract medical data from the conversation
    ehr_details = extractor.extract_medical_data(state['conversation'])
    
    # Generate possible diagnoses
    possible_diagnosis = extractor.analyze_conversation_for_diagnoses(state['conversation'])
    
    # Extract the doctor's diagnosis from the structured data
    doctor_diagnosis = ehr_details.get("Doctor Diagnosis")
    
    # Generate ICD-10-CM codes for both confirmed and possible diagnoses
    icd_codes = extractor.generate_icd_codes(doctor_diagnosis, possible_diagnosis)
    
    # Combine the data
    combined_data = {
        "ehr_details": ehr_details,
        "possible_diagnosis": possible_diagnosis,
        "icd_codes": icd_codes
    }
    
    # Save combined data to a JSON file
    save_combined_data(combined_data, 'medical_analysis_data.json')
    
    return {
        **state,
        "ehr_details": ehr_details,
        "possible_diagnosis": possible_diagnosis,
        "icd_codes": icd_codes,
        "combined_data": combined_data
    }

def main():
    # Initialize the graph builder
    graph_builder = StateGraph(State)

    # Add nodes and edges
    graph_builder.add_node("process_medical_data_workflow", process_medical_data_workflow)
    graph_builder.add_edge(START, "process_medical_data_workflow")
    graph_builder.add_edge("process_medical_data_workflow", END)

    # Compile the graph with a memory checkpointer
    graph = graph_builder.compile(checkpointer=MemorySaver())

    # Open and load the JSON file
    with open('yconversation.json', 'r') as file:
        conversation_data = json.load(file)

    # Configuration for the graph invocation
    config = {'configurable': {'thread_id': 'medical_extraction_1'}}

    # Invoke the graph with the sample conversation
    result = graph.invoke(
        {
            "messages": ["Extract medical information, diagnose, and generate ICD-10-CM codes"],
            "conversation": conversation_data
        }, 
        config=config
    )

    # Print the combined medical data including ICD codes
    print("Combined Medical Analysis Data with ICD-10-CM Codes:")
    print(json.dumps(result['combined_data'], indent=2))

if __name__ == "__main__":
    main()