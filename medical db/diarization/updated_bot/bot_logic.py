# import os
# from typing import Annotated, Literal
# from typing_extensions import TypedDict
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint.sqlite import SqliteSaver
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langgraph.prebuilt import ToolNode
# from langchain_core.tools import tool
# from langchain_google_genai import ChatGoogleGenerativeAI
# from datetime import datetime

# # Configure Gemini API and the model
# google_api_key = "AIzaSyCHh4vaVl5efQ1Xza9PgovJYDApoHlJ4B8"
# if not google_api_key:
#     raise ValueError("GOOGLE_API_KEY environment variable is not set")

# model = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     google_api_key=google_api_key,
#     temperature=0.7,
#     max_tokens=5000,
#     timeout=None,
#     max_retries=2
# )

# class State(TypedDict):
#     messages: Annotated[list, add_messages]

# graph_builder = StateGraph(State)

# # Helper function to safely get an attribute from a message (object or dict)
# def get_message_attr(message, attr, default=None):
#     if isinstance(message, dict):
#         return message.get(attr, default)
#     return getattr(message, attr, default)

# # Tool to determine the required medical specialty based on symptoms.
# @tool
# def check_field(symptoms: str):
#     """Determines the medical specialization based on patient symptoms."""
#     symptoms_lower = symptoms.lower()
#     if any(keyword in symptoms_lower for keyword in ["bone", "arm", "leg", "joint", "hip", "orthopedic"]):
#         return "orthopedics"
#     elif any(keyword in symptoms_lower for keyword in ["skin", "dermatology", "rash", "acne"]):
#         return "dermatology"
#     else:
#         return "unknown"

# # Tool to select a doctor based on the provided name.
# @tool
# def select_doctor(doc_name: str):
#     """Selects a doctor based on the provided name."""
#     doctors = [
#         {"name": "Jane Smith", "specialty": "orthopedics"},
#         {"name": "Alan Green", "specialty": "orthopedics"},
#         {"name": "John Doe", "specialty": "dermatology"},
#         {"name": "Mary Brown", "specialty": "dermatology"}
#     ]
#     for doctor in doctors:
#         # Match either full name or first name
#         if (doctor['name'].lower() == doc_name.lower()) or (doctor['name'].split()[0].lower() == doc_name.split()[0].lower()):
#             return doctor
#     return "Doctors relating to your problem are unavailable right now."

# # Tool to book an appointment given doctor name, date, and time.
# @tool
# def book_appointment(doctor_name: str, date: str, time: str):
#     """Books an appointment with the selected doctor at the specified date and time."""
#     doctors = [
#         {"name": "Jane Smith", "specialty": "orthopedics"},
#         {"name": "Alan Green", "specialty": "orthopedics"},
#         {"name": "John Doe", "specialty": "dermatology"},
#         {"name": "Mary Brown", "specialty": "dermatology"}
#     ]
#     for doctor in doctors:
#         if doctor['name'].lower() == doctor_name.lower():
#             return f"Appointment booked with Dr. {doctor['name']} on {date} at {time}."
#     return "Doctor not found. Unable to book appointment."

# # Update the tools list to include the required tools.
# tools = [check_field, select_doctor, book_appointment]
# model_with_tools = model.bind_tools(tools)

# tool_node = ToolNode(tools)
# graph_builder.add_node("tool_node", tool_node)

# # Helper function to ensure messages are in a standard dict format.
# def ensure_message_format(messages):
#     formatted = []
#     for msg in messages:
#         if isinstance(msg, str):
#             formatted.append({"role": "user", "content": msg})
#         elif isinstance(msg, dict):
#             formatted.append(msg)
#         else:
#             role = get_message_attr(msg, "role", "user")
#             content = get_message_attr(msg, "content", str(msg))
#             formatted.append({"role": role, "content": content})
#     return formatted

# # Helper function to safely extract message content.
# def get_message_content(message):
#     return get_message_attr(message, "content", str(message))

# # The chatbot node injects a system message that includes the list of available doctors.
# def chatbot(state: State):
#     state["messages"] = ensure_message_format(state["messages"])
#     if not state["messages"] or get_message_attr(state["messages"][0], "role") != "system":
#         system_message = (
#             "You are a medical chatbot that helps patients book appointments based on their symptoms. "
#             "The available doctors are: Jane Smith and Alan Green (Orthopedics), John Doe and Mary Brown (Dermatology). "
#             "When a patient describes their symptoms, first use the check_field tool to determine the required specialty. "
#             "If the symptoms match either orthopedics or dermatology, respond by listing the available doctors for that specialty as given above, "
#             "and then ask the patient: 'Please provide the doctor's name from the list along with your desired appointment date and time.' "
#             "Once the patient provides these details, use the book_appointment tool to confirm the booking. "
#             "If the symptoms do not match either specialty, inform the patient that appointments are available only for orthopedics and dermatology."
#         )
#         state["messages"].insert(0, {"role": "system", "content": system_message})
#     return {"messages": [model_with_tools.invoke(state["messages"])]}

# graph_builder.add_node("chatbot", chatbot)

# def conditional_edge(state: State) -> Literal["tool_node", "__end__"]:
#     last_message = state["messages"][-1]
#     return "tool_node" if hasattr(last_message, "tool_calls") and last_message.tool_calls else "__end__"

# graph_builder.add_conditional_edges("chatbot", conditional_edge)
# graph_builder.add_edge("tool_node", "chatbot")
# graph_builder.set_entry_point("chatbot")

# memory = SqliteSaver.from_conn_string(":memory:")
# graph = graph_builder.compile(checkpointer=MemorySaver())

# if __name__ == "__main__":
#     while True:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break
#         config = {'configurable': {'thread_id': '1'}}
#         response = graph.invoke({"messages": [user_input]}, config=config)
#         last_message = response["messages"][-1]
#         print("Bot:", get_message_content(last_message))
#         print('-' * 20)





# import os
# from typing import Annotated, Literal
# from typing_extensions import TypedDict
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint.sqlite import SqliteSaver
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langgraph.prebuilt import ToolNode
# from langchain_core.tools import tool
# from langchain_google_genai import ChatGoogleGenerativeAI
# from datetime import datetime

# # Configure Gemini API and the model
# google_api_key = "AIzaSyCHh4vaVl5efQ1Xza9PgovJYDApoHlJ4B8"
# if not google_api_key:
#     raise ValueError("GOOGLE_API_KEY environment variable is not set")

# model = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     google_api_key=google_api_key,
#     temperature=0.7,
#     max_tokens=5000,
#     timeout=None,
#     max_retries=2
# )

# class State(TypedDict):
#     messages: Annotated[list, add_messages]

# graph_builder = StateGraph(State)

# # Helper function to safely get an attribute from a message (object or dict)
# def get_message_attr(message, attr, default=None):
#     if isinstance(message, dict):
#         return message.get(attr, default)
#     return getattr(message, attr, default)

# # Tool to determine the required medical specialty based on symptoms.
# @tool
# def check_field(symptoms: str):
#     """Determines the medical specialization based on patient symptoms."""
#     symptoms_lower = symptoms.lower()
#     if any(keyword in symptoms_lower for keyword in ["bone", "arm", "leg", "joint", "hip", "orthopedic"]):
#         return "orthopedics"
#     elif any(keyword in symptoms_lower for keyword in ["skin", "dermatology", "rash", "acne"]):
#         return "dermatology"
#     else:
#         return "unknown"

# # Tool to select a doctor based on the provided name.
# @tool
# def select_doctor(doc_name: str):
#     """Selects a doctor based on the provided name."""
#     doctors = [
#         {"name": "Jane Smith", "specialty": "orthopedics"},
#         {"name": "John Doe", "specialty": "dermatology"},
#         {"name": "Alan Green", "specialty": "orthopedics"},
#         {"name": "Mary Brown", "specialty": "dermatology"}
#     ]
#     for doctor in doctors:
#         if (doctor['name'].lower() == doc_name.lower()) or (doctor['name'].split()[0].lower() == doc_name.split()[0].lower()):
#             return doctor
#     return "Doctors relating to your problem are unavailable right now."

# # Tool to book an appointment given doctor name, date, and time.
# @tool
# def book_appointment(doctor_name: str, date: str, time: str):
#     """Books an appointment with the selected doctor at the specified date and time."""
#     doctors = [
#         {"name": "Jane Smith", "specialty": "orthopedics"},
#         {"name": "John Doe", "specialty": "dermatology"},
#         {"name": "Alan Green", "specialty": "orthopedics"},
#         {"name": "Mary Brown", "specialty": "dermatology"}
#     ]
#     for doctor in doctors:
#         if doctor['name'].lower() == doctor_name.lower():
#             return f"Appointment booked with Dr. {doctor['name']} on {date} at {time}."
#     return "Doctor not found. Unable to book appointment."

# # Update the tools list to include the required tools.
# tools = [check_field, select_doctor, book_appointment]
# model_with_tools = model.bind_tools(tools)

# tool_node = ToolNode(tools)
# graph_builder.add_node("tool_node", tool_node)

# # Helper function to ensure messages are in a standard dict format.
# def ensure_message_format(messages):
#     formatted = []
#     for msg in messages:
#         if isinstance(msg, str):
#             formatted.append({"role": "user", "content": msg})
#         elif isinstance(msg, dict):
#             formatted.append(msg)
#         else:
#             role = get_message_attr(msg, "role", "user")
#             content = get_message_attr(msg, "content", str(msg))
#             formatted.append({"role": role, "content": content})
#     return formatted

# # Helper function to safely extract message content.
# def get_message_content(message):
#     return get_message_attr(message, "content", str(message))

# # The chatbot node injects an enhanced system message to guide a natural, detailed conversation.
# def chatbot(state: State):
#     state["messages"] = ensure_message_format(state["messages"])
#     # Only inject the system prompt if it hasn't been set yet.
#     if not state["messages"] or get_message_attr(state["messages"][0], "role") != "system":
#         system_message = (
#             "You are a friendly and empathetic medical chatbot who helps patients determine which type of doctor they need, "
#             "and assists in booking appointments. You have doctors in only two specialties: orthopedics and dermatology. \n\n"
#             "Here's how you should proceed:\n"
#             "1. Greet the patient and ask how they are feeling, then ask them to describe their symptoms in detail.\n"
#             "   For example, if a patient says 'I'm feeling pain in my leg', ask follow-up questions such as:\n"
#             "     - Where exactly is the pain? (e.g., knee, ankle, thigh)\n"
#             "     - How long have you been experiencing the pain?\n"
#             "     - Is the pain sharp, dull, or throbbing?\n"
#             "     - Did it start after an injury or gradually over time?\n"
#             "     - Does anything make it better or worse?\n\n"
#             "2. After gathering enough details, use the check_field tool to determine if the symptoms point to orthopedics or dermatology.\n"
#             "   - If the symptoms match orthopedics (e.g., leg or knee pain), inform the patient that an orthopedic specialist is recommended.\n"
#             "   - If they match dermatology (e.g., skin issues), inform the patient accordingly.\n\n"
#             "3. Once the specialty is determined, provide a static list of available doctors for that field:\n"
#             "   - Orthopedics: Jane Smith and Alan Green\n"
#             "   - Dermatology: John Doe and Mary Brown\n\n"
#             "4. Then ask the patient for their preferred doctor and their desired appointment time. For example, ask:\n"
#             "   'Would you like to book an appointment with one of these doctors? If so, which doctor do you prefer and what time would work best for you?'\n\n"
#             "Remember to maintain a conversational tone, ask clarifying questions if necessary, and ensure the patient feels heard and understood. \n\n"
#             "Now, start the conversation by greeting the patient and asking how they are feeling. Are you ready to begin?"
#         )
#         state["messages"].insert(0, {"role": "system", "content": system_message})
#     return {"messages": [model_with_tools.invoke(state["messages"])]}

# graph_builder.add_node("chatbot", chatbot)

# def conditional_edge(state: State) -> Literal["tool_node", "__end__"]:
#     last_message = state["messages"][-1]
#     return "tool_node" if hasattr(last_message, "tool_calls") and last_message.tool_calls else "__end__"

# graph_builder.add_conditional_edges("chatbot", conditional_edge)
# graph_builder.add_edge("tool_node", "chatbot")
# graph_builder.set_entry_point("chatbot")

# memory = SqliteSaver.from_conn_string(":memory:")
# graph = graph_builder.compile(checkpointer=MemorySaver())

# if __name__ == "__main__":
#     while True:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break
#         config = {'configurable': {'thread_id': '1'}}
#         response = graph.invoke({"messages": [user_input]}, config=config)
#         last_message = response["messages"][-1]
#         print("Bot:", get_message_content(last_message))
#         print('-' * 20)


# import os
# import json
# from typing import Annotated, Literal
# from typing_extensions import TypedDict
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint.sqlite import SqliteSaver
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langgraph.prebuilt import ToolNode
# from langchain_core.tools import tool
# from langchain_google_genai import ChatGoogleGenerativeAI
# from datetime import datetime

# # Configure Gemini API and the model
# google_api_key = "AIzaSyCHh4vaVl5efQ1Xza9PgovJYDApoHlJ4B8"
# if not google_api_key:
#     raise ValueError("GOOGLE_API_KEY environment variable is not set")

# model = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     google_api_key=google_api_key,
#     temperature=0.1,
#     max_tokens=5000,
#     timeout=None,
#     max_retries=2
# )



# # Load the JSON file into a Python variable
# # with open('schedule.json', 'r') as file:
# #     doctor_data = json.load(file)


# class State(TypedDict):
#     messages: Annotated[list, add_messages]
#     speciality: str
#     doctor: str
#     date: str
#     time: str

# graph_builder = StateGraph(State)

# @tool
# def get_schedule(text:str) -> str:
#     """
#         You are a medical reservation assistant tasked to book appointments.
#         Keep the conversation professional, polite, sympathetic and do not ask a long question or provide a long prompt.
#         Keeping the conversation very short is a must only ask one question / prompt at a time.
#         Process the user input recursively and extract information from model's output.
   
#         Osteology:
#             Dr. Bruce Smith
#                 Sunday and Friday, 10:00 AM - 12:00 PM
#             Dr. Emily Green
#                 Tuesday, Wednesday, and Friday, 08:00 AM - 11:00 AM
        
#         Dermatology:
#             Dr. Sarah Parker
#                 Monday and Thursday, 09:00 AM - 12:00 PM
#             Dr. Laura Mitchell
#                 Tuesday and Friday, 02:00 PM - 05:00 PM
        
#         Cardiology:
#             Dr. William Brown:
#                 Monday and Wednesday, 08:30 AM - 12:30 PM
#             Dr. Nancy Davis:
#                 Tuesday and Friday, 09:00 AM - 01:00 PM
#             Dr. Joseph White:
#                 Monday and Thursday, 02:00 PM - 05:00 PM

#         Based on the user input and then on above listings.
#         Ask for all the symptoms(symptoms, location, duration) one by one to determine the medical speciality.
#         Based on the medical speciality select a doctor. This can be selected by the user or the model can recommend one.
#         Ask the user for date and time of appointment. This can be selected by the user or the model can recommend one.
#         Then feed the information to the model.

#         If booked appointment, return the confirmation message.
#         If not booked appointment, return the extracted reservation information.
    
#     Args:
#         text (str): The text output from the model containing reservation
        
#     Returns:
#         str: String containing all extracted reservation information.    
#     """

# @tool
# def info_in_json(symptoms: str, specialty: str, doctor: str, date: str, time: str) -> str:
#     """
#         Only run this if booking is confirmed.
#         This function takes in the details of a medical reservation 
#         and returns them as a JSON object.
    
#     Args:
#         symptoms (str): The symptoms of the patient as csv.
#         doctor (str): The name of the selected doctor.
#         specialty (str): The medical specialty (e.g., cardiology, dermatology).
#         date (str): The date of the appointment.
#         time (str): The time of the appointment.
    
#     Returns:
#         str: A JSON string with the reservation details.
#     """

#     timestamp = datetime.now().isoformat()

#     reservation_info = {
#         "symptoms": symptoms,
#         "specialty": specialty,
#         "doctor": doctor,
#         "date": date,
#         "time": time,
#         "timestamp": timestamp  
#     }
    
#     # Convert the dictionary to a JSON string
#     json_string = json.dumps(reservation_info, indent=4)
    
#     # Save to a file
#     # filename = f"appointment_{date.replace('/', '_')}_{time.replace(':', '_')}.json"
#     # with open(filename, 'w') as file:
#     #     file.write(json_string)
#     # print(json_string)
#     return json_string


# tools = [get_schedule, info_in_json]
# model_with_tools = model.bind_tools(tools)

# tool_node = ToolNode(tools)
# graph_builder.add_node("tool_node", tool_node)

# def chatbot(state: State):
#     current_timestamp = datetime.now().isoformat()
#     state["timestamp"] = current_timestamp
#     return {"messages": [model_with_tools.invoke(state["messages"])]}

# graph_builder.add_node("chatbot", chatbot)

# def conditional_edge(state: State) -> Literal["tool_node", "__end__"]:
#     last_message = state["messages"][-1]
#     return "tool_node" if last_message.tool_calls else "__end__"

# graph_builder.add_conditional_edges("chatbot", conditional_edge)
# graph_builder.add_edge("tool_node", "chatbot")
# graph_builder.set_entry_point("chatbot")

# memory = SqliteSaver.from_conn_string(":memory:")
# graph = graph_builder.compile(checkpointer=MemorySaver())

# if __name__ == "__main__":
#     while True:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break
#         config = {'configurable': {'thread_id': '1'}}
#         response = graph.invoke({"messages": [user_input]}, config=config)
#         print("Bot:", response["messages"][-1].content)
#         print('-' * 20)







































from typing import Annotated, Literal, List
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime, timedelta
from langchain_core.tools import tool
# from IPython.display import display
import json
import psycopg2
import os


# Configure Gemini API and the model
google_api_key = "AIzaSyBGry6LwqLN_j1fPHh0ZfoOkf7oaGGgdbo"
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=google_api_key,
    streaming = True,
    temperature=0.1,
    max_tokens=5000,
    timeout=None,
    max_retries=2
)

# PostgreSQL database configuration - replace with your actual PostgreSQL connection details
DB_CONFIG = {
    'dbname': 'doctors_db',
    'user': 'postgres',
    'password': 'heheboii420',
    'host': 'localhost',
    'port': '5432'
}

# Helper function to establish connection to PostgreSQL
def get_db_connection():
    """Create a connection to the PostgreSQL database"""
    try:
        print("Attempting to connect to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("Database connection successful!")
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise


# Defining the state graph
class resState(TypedDict):
    messages: Annotated[list, add_messages]
    symptoms: List[str]
    speciality: str
    doctor: str
    date: str
    time: str

graph_builder = StateGraph(resState)

SPECIALTY_MAPPING = {
    # "orthopedist": "Osteology",
    "orthopedist": "Osteology",
    "cardiologist": "Cardiology",
    "dermatologist": "Dermatology"
}


# @tool
# def get_available_doctors(specialty: str) -> str:
#     """Query the database to get available doctors based on specialty."""
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # Map user-input specialty to database terms
#         specialty_mapped = SPECIALTY_MAPPING.get(specialty.lower(), specialty)

#         print(f"Fetching doctors for specialty: {specialty_mapped}")  # Debugging

#         # Query the correct table `doctor_schedule`
#         cursor.execute("""
#             SELECT DISTINCT doctor_name FROM doctor_schedule WHERE specialty = %s
#         """, (specialty_mapped,))

#         doctors = cursor.fetchall()

#         cursor.close()
#         conn.close()

#         print("Doctors found:", doctors)  # Debugging

#         if not doctors:
#             return f"No doctors found for {specialty}."

#         result = f"Available doctors for {specialty}:\n"
#         for doctor in doctors:
#             result += f"- {doctor[0]}\n"

#         return result
#     except Exception as e:
#         return f"Error querying doctors: {str(e)}"


# @tool
# def get_available_doctors(specialty: str) -> str:
#     """Query the database to get available doctors based on specialty."""
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

        

#         # Normalize input: trim spaces and convert to lowercase
#         specialty_normalized = specialty.strip().lower()

#         # Fetch all distinct specialties from database
#         cursor.execute("SELECT DISTINCT LOWER(TRIM(specialty)) FROM doctor_schedule")
#         available_specialties = [row[0] for row in cursor.fetchall()]

#         if specialty_normalized not in available_specialties:
#             return f"⚠️ Specialty '{specialty}' not found. Available options: {', '.join(available_specialties)}"

#         # Fetch doctors for this specialty
#         cursor.execute('''
#             SELECT DISTINCT doctor_name FROM doctor_schedule 
#             WHERE LOWER(specialty) = %s
#         ''', (specialty_normalized,))

#         doctors = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         if not doctors:
#             return f"❌ No doctors found for {specialty.capitalize()}."

#         result = f"🩺 Available doctors for {specialty.capitalize()}:\n"
#         for doctor in doctors:
#             result += f"- {doctor[0]}\n"

#         return result
#     except Exception as e:
#         return f"❌ Error querying doctors: {str(e)}"


@tool
def get_available_doctors(specialty: str) -> str:
    """Query the database to get available doctors based on specialty."""
    
    SPECIALTY_MAPPING = {
        "orthopedist": "osteology",
        "cardiologist": "cardiology",
        "dermatologist": "dermatology"
    }

    # Normalize specialty before searching
    specialty_normalized = specialty.strip().lower()
    mapped_specialty = SPECIALTY_MAPPING.get(specialty_normalized, specialty_normalized)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all distinct specialties from database
        cursor.execute("SELECT DISTINCT LOWER(TRIM(specialty)) FROM doctor_schedule")
        available_specialties = [row[0] for row in cursor.fetchall()]

        # Check if the mapped specialty exists in the database
        if mapped_specialty not in available_specialties:
            return f"⚠️ Specialty '{specialty}' not found. Available options: {', '.join(available_specialties)}"

        # Fetch doctors for this mapped specialty
        cursor.execute('''
            SELECT DISTINCT doctor_name FROM doctor_schedule 
            WHERE LOWER(specialty) = %s
        ''', (mapped_specialty,))

        doctors = cursor.fetchall()
        cursor.close()
        conn.close()

        if not doctors:
            return f"❌ No doctors found for {mapped_specialty.capitalize()}."

        result = f"🩺 Available doctors for {mapped_specialty.capitalize()}:\n"
        for doctor in doctors:
            result += f"- {doctor[0]}\n"

        return result
    except Exception as e:
        return f"❌ Error querying doctors: {str(e)}"




@tool
def get_doctor_availability(doctor_name: str) -> str:
    """
    Query the database to get a doctor's availability schedule.

    Args:
        doctor_name (str): The name of the doctor
        
    Returns:
        str: A formatted string with the doctor's availability
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve the doctor's schedule from the correct table
        cursor.execute('''
        SELECT day_of_week, time_slot
        FROM doctor_schedule
        WHERE doctor_name = %s
        ORDER BY 
            CASE day_of_week
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END
        ''', (doctor_name,))

        timeslots = cursor.fetchall()
        cursor.close()
        conn.close()

        # Check if any availability exists
        if not timeslots:
            return f"❌ No availability found for Dr. {doctor_name}. Please check for another doctor or date."

        # Format the response
        result = f"📅 **General availability for Dr. {doctor_name}:**\n"
        for day, time_slot in timeslots:
            result += f"- {day}: {time_slot}\n"

        return result
    except Exception as e:
        return f"❌ Error retrieving availability for Dr. {doctor_name}: {str(e)}"

@tool
def book_appointment(doctor_name: str, date_str: str, time_str: str, patient_name: str = "Patient") -> str:
    """
    Book an appointment in the database.
    
    Args:
        doctor_name (str): The name of the doctor
        date_str (str): The date in "YYYY-MM-DD" format
        time_str (str): The time of the appointment
        patient_name (str): The name of the patient
        
    Returns:
        str: Confirmation message or error message.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the appointments table exists
        cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'appointments'
        )
        """)
        table_exists = cursor.fetchone()[0]

        # if not table_exists:
        #     cursor.close()
        #     conn.close()
        #     return "❌ Booking failed: The appointments table does not exist. Please create it before booking."

        # Check if the slot is available
        cursor.execute('''
        SELECT 1 FROM appointments 
        WHERE doctor_name = %s AND date = %s AND time = %s
        ''', (doctor_name, date_str, time_str))

        if cursor.fetchone():
            cursor.close()
            conn.close()
            return f"❌ The slot at {time_str} on {date_str} is already booked. Please select another time."

        # Book the appointment
        cursor.execute('''
        INSERT INTO appointments (doctor_name, patient_name, date, time, status) 
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        ''', (doctor_name, patient_name, date_str, time_str, 'scheduled'))

        appointment_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return f"✅ Appointment #{appointment_id} confirmed with Dr. {doctor_name} on {date_str} at {time_str}."
    except Exception as e:
        return f"❌ Error booking appointment: {str(e)}"


@tool
def get_available_slots(doctor_name: str, date_str: str) -> str:
    """
    Query the database to find available time slots for a specific doctor on a specific date.
    
    Args:
        doctor_name (str): The name of the doctor
        date_str (str): The date in "YYYY-MM-DD" format
        
    Returns:
        str: A formatted string with available time slots
    """
    try:
        # Parse the date string to get the day of the week
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_of_week = date_obj.strftime("%A")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get doctor's working hours for the given day
        cursor.execute('''
        SELECT time_slot
        FROM doctor_schedule
        WHERE doctor_name = %s AND day_of_week = %s
        ''', (doctor_name, day_of_week))

        working_hours = cursor.fetchone()

        if not working_hours:
            cursor.close()
            conn.close()
            return f"Dr. {doctor_name} does not work on {day_of_week}."

        time_slot = working_hours[0]

        # Get booked appointments
        cursor.execute('''
        SELECT time 
        FROM appointments 
        WHERE doctor_name = %s AND date = %s
        ''', (doctor_name, date_str))

        booked_times = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        # Generate available slots from the stored time slot
        start_time, end_time = time_slot.split(" - ")
        start_dt = datetime.strptime(start_time, "%I:%M %p")
        end_dt = datetime.strptime(end_time, "%I:%M %p")

        available_slots = []
        current = start_dt

        while current + timedelta(minutes=30) <= end_dt:
            slot = current.strftime("%I:%M %p")
            if slot not in booked_times:
                available_slots.append(slot)
            current += timedelta(minutes=30)

        if not available_slots:
            return f"❌ No available slots for Dr. {doctor_name} on {date_str}."

        result = f"🗓 Available slots for Dr. {doctor_name} on {date_str} ({day_of_week}):\n"
        for slot in available_slots:
            result += f"- {slot}\n"

        return result
    except ValueError:
        return "❌ Invalid date format. Please use YYYY-MM-DD."
    except Exception as e:
        return f"❌ Error querying available slots: {str(e)}"

# @tool
# def get_schedule(text: str) -> str:
#     """
#     You are a medical reservation assistant tasked to book appointments.
#     Keep the conversation professional, polite and start off with a greeting.
#     Keep each prompt under 100 characters.
#     You have to be sympathetic and say/ask reassuring questions/statements. Don't be too robotic ask generally about the patient's health and well-being.
#     Process the user input recursively and extract information from model's output.
   
#     Ask for at least 4 symptoms, area of concern and duration, one by one, to determine the medical speciality. 
#     Should contain symptoms, area of concern, duration based on importance.
    
#     Based on the medical speciality, use get_available_doctors() to find appropriate doctors.
#     When a doctor is selected, use get_doctor_availability() to show their schedule.
#     When a date is selected, use get_available_slots() to show available time slots.
#     Finally, use book_appointment() to confirm the booking.
    
#     If booked appointment, return the confirmation message.
#     If not booked appointment, return the extracted reservation information.
    
#     Args:
#         text (str): The text output from the model containing reservation
        
#     Returns:
#         str: String containing all extracted reservation information.    
#     """
#     return text




@tool
def get_schedule(text: str) -> str:
    """
    You are a medical reservation assistant. Start with a warm greeting and be professional, polite, and empathetic.)
    
    Ask open-ended questions to determine how the user wants to find a doctor:
    - Are they looking for a specialist? (Use get_available_doctors)
    - Do they have a specific doctor in mind? (Use get_doctor_availability)
    - Do they need an appointment on a particular date? (Use get_available_slots)
    - Do they have location, gender, or language preferences? (Modify the query accordingly)

    Be conversational and guide the user to provide key details (symptoms, specialty, doctor name, date, or preferences).
    Adapt the queries dynamically based on the provided details.

    Once a doctor is chosen, check their availability and suggest open slots.
    When a user confirms, finalize the booking with book_appointment.

    If an appointment is booked, return the confirmation message.
    If not booked, return the extracted reservation details.

    Args:
        text (str): User’s input about their appointment request.

    Returns:
        str: Extracted details or booking confirmation.
    """
    return text



@tool
def reservation_info_json(symptoms: List[str], specialty: str, doctor: str, date: str, time: str, summary: str) -> str:
    """
    Automatically generate a summary of all the conversation so far relating to the issue and reservation.
    Only run this if booking is confirmed.
    This function takes in the details of a medical reservation
    and returns them as a JSON object.
    
    Args:
        symptoms List[str]: [symptom1, symptom2, area of concern, duration].
        doctor (str): The name of the selected doctor.
        specialty (str): The medical specialty (e.g., cardiology, dermatology).
        date (str): The date of the appointment.
        time (str): The time of the appointment.
        summary (str): The summary of the reservation based on all information collected.
    
    Returns:
        str: A JSON string with the reservation details.
    """
    timestamp = datetime.now().isoformat()

    reservation_info = {
        "summary": summary,
        "symptoms": symptoms,
        "specialty": specialty,
        "doctor": doctor,
        "date": date,
        "time": time,
        "timestamp": timestamp  
    }
    
    # Convert the dictionary to a JSON string
    json_string = json.dumps(reservation_info, indent=4)
    
    # Save to a file
    filename = f"appointment_{specialty.replace('/', '_')}_{time.replace(':', '_')}.json"
    with open(filename, 'w') as file:
        file.write(json_string)
    
    return json_string


# Update the tools list to include the database tools
tools = [
    get_schedule, 
    reservation_info_json, 
    get_available_doctors, 
    get_doctor_availability, 
    get_available_slots,
    book_appointment
]

model_with_tools = model.bind_tools(tools)

tool_node = ToolNode(tools)
graph_builder.add_node("tool_node", tool_node)

def chatbot(state: resState):
    current_timestamp = datetime.now().isoformat()
    state["timestamp"] = current_timestamp
    return {"messages": [model_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

def conditional_edge(state: resState) -> Literal["tool_node", "__end__"]:
    last_message = state["messages"][-1]
    return "tool_node" if last_message.tool_calls else "__end__"

graph_builder.add_conditional_edges("chatbot", conditional_edge)
graph_builder.add_edge("tool_node", "chatbot")
graph_builder.set_entry_point("chatbot")

memory = SqliteSaver.from_conn_string(":memory:")
graph = graph_builder.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Goodbye!")
            break
        config = {'configurable': {'thread_id': '1'}}
        response = graph.invoke({"messages": [user_input]}, config=config)
        print("Bot:", response["messages"][-1].content)
        print('-' * 20)
 