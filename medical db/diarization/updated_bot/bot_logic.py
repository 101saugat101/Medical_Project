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





















































import os
import json
from typing import Annotated, Literal, List
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime

# Configure Gemini API and the model
google_api_key = "AIzaSyCHh4vaVl5efQ1Xza9PgovJYDApoHlJ4B8"
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=google_api_key,
    temperature=0.1,
    max_tokens=5000,
    timeout=None,
    max_retries=2
)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    symptoms: List[str]
    speciality: str
    doctor: str
    date: str
    time: str

graph_builder = StateGraph(State)

@tool
def get_schedule(text:str) -> str:
    """
        You are a medical reservation assistant tasked to book appointments.
        Keep the conversation professional, polite.
        Only one question/ prompt at a time. Do not create a list of questions.
        You have to be sympathetic and say/ask reassuring questions/statements. Don't be too robotic ask generally about the patient's health and well-being.
        Process the user input recursively and extract information from model's output.
   
        Osteology:
            Dr. Bruce Smith
                Sunday and Friday, 10:00 AM - 12:00 PM
            Dr. Emily Green
                Tuesday, Wednesday, and Friday, 08:00 AM - 11:00 AM
        
        Dermatology:
            Dr. Sarah Parker
                Monday and Thursday, 09:00 AM - 12:00 PM
            Dr. Laura Mitchell
                Tuesday and Friday, 02:00 PM - 05:00 PM
        
        Cardiology:
            Dr. William Brown:
                Monday and Wednesday, 08:30 AM - 12:30 PM
            Dr. Nancy Davis:
                Tuesday and Friday, 09:00 AM - 01:00 PM
            Dr. Joseph White:
                Monday and Thursday, 02:00 PM - 05:00 PM

        Based on the user input and then on above listings.
        Ask for at least 4 symptoms, area of concern and duration, one by one, to determine the medical speciality. Should contain symptoms, area of concern, duration based on importance.
        Based on the medical speciality select a doctor. This can be selected by the user or the model can recommend one. Only recommend one doctor at a time.
        Ask the user for date and time of appointment. This can be selected by the user or the model can recommend one.
        Then feed the information to the model.

        If booked appointment, return the confirmation message.
        If not booked appointment, return the extracted reservation information.
    
    Args:
        text (str): The text output from the model containing reservation
        
    Returns:
        str: String containing all extracted reservation information.    
    """



@tool
def info_in_json(symptoms: List[str], specialty: str, doctor: str, date: str, time: str, summary: str) -> str:
    """
        Generte a summary of all the conversation so fer realting to the issue and reservation.
        Only run this if booking is confirmed.
        This function takes in the details of a medical reservation 
        and returns them as a JSON object.
    
    Args:
        symptoms List[str]: [symptom1, symptom2, area of concern, duration].
        doctor (str): The name of the selected doctor.
        specialty (str): The medical specialty (e.g., cardiology, dermatology).
        date (str): The date of the appointment.
        time (str): The time of the appointment.
        summary (str): The summary of the reservation based on all imformation collected.
    
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
    filename = f"appointment_{date.replace('/', '_')}_{time.replace(':', '_')}.json"
    with open(filename, 'w') as file:
        file.write(json_string)
    
    return json_string



tools = [get_schedule, info_in_json]
model_with_tools = model.bind_tools(tools)

tool_node = ToolNode(tools)
graph_builder.add_node("tool_node", tool_node)

def chatbot(state: State):
    current_timestamp = datetime.now().isoformat()
    state["timestamp"] = current_timestamp
    return {"messages": [model_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

def conditional_edge(state: State) -> Literal["tool_node", "__end__"]:
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