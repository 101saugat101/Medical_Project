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
# google_api_key ="AIzaSyCHh4vaVl5efQ1Xza9PgovJYDApoHlJ4B8"
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

# class State(TypedDict):
#     messages: Annotated[list, add_messages]

# graph_builder = StateGraph(State)

# @tool
# def check_field(specialty: str):
#     """
#     Call to get the what kind of specialization the user requires.
#     Use this anytime field of the patient's problem is needed. Only use this tool when the user's problem is not known.
#     Do not use five out any specialization except for the ones mentioned in the prompt.
#     Do not use any medical term to the patient. Be very polite and professional.
#     """

#     if any(specialty.lower() in word or specialty.lower() + "s" == word for word in ["orthopedic", "bone", "arm", "leg", "joint", "hip"]):
#         return "orthopedics"
#     elif specialty.lower() in ["skin", "dermatology", "rash", "acne"]:
#         return "dermatology"
#     elif specialty.lower() in ["heart", "cardiology", "chest"]:
#         return "cardiology"
#     else:
#         return "unknown"

# @tool
# # Function to select a doctor by name
# def select_doctor(doc_name: str):
#     """
#     Only use this tool when the specializtion is already known.
#     Call to get the doctor's name based on specialization.
#     Use this anytime doctor's name is needed or when the user requests the name of one.
#     If user doesn't provide a doctor name, recommend a doctor based on the speciality.
#     Be very polite and professional.
#     """
#     doctors = [
#         {"name": "Jane Smith", "specialty": "orthopedics"},
#         {"name": "John Doe", "specialty": "dermatology"},
#         {"name": "Alan Green", "specialty": "orthopedics"},
#         {"name": "Mary Brown", "specialty": "dermatology"}
#     ]

#     for doctor in doctors:
#         if (doctor['name'].lower() == doc_name.lower()) or (doctor['name'].split()[0].lower() == doc_name.split()[0].lower()):
#             return doctor
#     return "Doctors relating to your problem are unavailable right now"

# @tool
# def select_appointment(doctor, day: str, time: str):
#     """
#     Only use this tool when the doctor's name is already known.
#     Call this to an appointment based on the date and time based on the name of the doctor and based on day of the week and time 'HH:MM' format.
#     Use this anytime an appointment is needed.
#     Be very polite and professional.
    
#     """

#     schedule = [
#     {"name": "Jane Smith", "day": "Monday", "time_range": ("09:00", "12:00")},
#     {"name": "Jane Smith", "day": "Thursday", "time_range": ("09:00", "12:00")},
#     {"name": "John Doe", "day": "Tuesday", "time_range": ("10:00", "14:00")},
#     {"name": "Alan Green", "day": "Wednesday", "time_range": ("13:00", "16:00")},
#     {"name": "Mary Brown", "day": "Thursday", "time_range": ("08:00", "11:00")},
#     ]

#     time_format = "%H:%M"
#     requested_time = datetime.strptime(time, time_format)

#     # Check if the doctor has an appointment on the requested day and time
#     for entry in schedule:
#         if entry["name"] == doctor and entry["day"] == day:
#             booked_start_time = datetime.strptime(entry["time_range"][0], time_format)
#             booked_end_time = datetime.strptime(entry["time_range"][1], time_format)

#             # Check if the requested time falls within the booked time range
#             if booked_start_time <= requested_time < booked_end_time:
#                 return f"Sorry, Dr. {doctor} is already booked on {day} between {entry['time_range'][0]} and {entry['time_range'][1]}."
    
#     return f"Appointment successfully booked with Dr. {doctor} on {day} at {time}."


# tools = [check_field, select_doctor]
# #tools = [check_field, select_doctor, select_appointment] # List of tools to be added to the graph
# model_with_tools = model.bind_tools(tools) # Bind the tools to the model

# # Creating the tool node
# tool_node = ToolNode(tools)

# # Adding the tool node to the graph
# graph_builder.add_node("tool_node", tool_node)

# def chatbot(state:State):
#     return{"messages": [model_with_tools.invoke(state["messages"])]}


# graph_builder.add_node("chatbot", chatbot)


# # defining conditional edge
# def conditional_edge(state: State) -> Literal["tool_node", "__end__"]:
#     last_message = state["messages"][-1]
#     if last_message.tool_calls:
#         return "tool_node"
#     else:
#         return "__end__"


# # Adding the conditional edge to the graph
# graph_builder.add_conditional_edges("chatbot", conditional_edge)

# # Adding normal edge to the graph
# graph_builder.add_edge("tool_node", "chatbot")

# #setting entry point of our graph
# graph_builder.set_entry_point("chatbot")


# # Saving the graph to memory (conversation history)
# memory = SqliteSaver.from_conn_string(":memory:")
# graph = graph_builder.compile(checkpointer=MemorySaver())


# while True:
#     user_input = input("User: ")
#     if user_input.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")
#         break

#     config = {'configurable': {'thread_id': '1'}}

#     response = graph.invoke({"messages": [user_input]}, config = config)
#     print("Bot:", response["messages"][-1].content)
#     print('-'*20)












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

# @tool
# def check_field(specialty: str):
#     """Determines the medical specialization needed."""
#     if any(specialty.lower() in word or specialty.lower() + "s" == word for word in ["orthopedic", "bone", "arm", "leg", "joint", "hip"]):
#         return "orthopedics"
#     elif specialty.lower() in ["skin", "dermatology", "rash", "acne"]:
#         return "dermatology"
#     elif specialty.lower() in ["heart", "cardiology", "chest"]:
#         return "cardiology"
#     else:
#         return "unknown"

# @tool
# def select_doctor(doc_name: str):
#     """Selects a doctor based on specialization."""
#     doctors = [
#         {"name": "Jane Smith", "specialty": "orthopedics"},
#         {"name": "John Doe", "specialty": "dermatology"},
#         {"name": "Alan Green", "specialty": "orthopedics"},
#         {"name": "Mary Brown", "specialty": "dermatology"}
#     ]
#     for doctor in doctors:
#         if (doctor['name'].lower() == doc_name.lower()) or (doctor['name'].split()[0].lower() == doc_name.split()[0].lower()):
#             return doctor
#     return "Doctors relating to your problem are unavailable right now"

# tools = [check_field, select_doctor]
# model_with_tools = model.bind_tools(tools)

# tool_node = ToolNode(tools)
# graph_builder.add_node("tool_node", tool_node)

# def chatbot(state: State):
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

# # 🚀 Prevent running the chatbot in CLI mode when imported into FastAPI
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
from typing import Annotated, Literal
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
    temperature=0.7,
    max_tokens=5000,
    timeout=None,
    max_retries=2
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# Helper function to safely get an attribute from a message (object or dict)
def get_message_attr(message, attr, default=None):
    if isinstance(message, dict):
        return message.get(attr, default)
    return getattr(message, attr, default)

# Tool to determine the required medical specialty based on symptoms.
@tool
def check_field(symptoms: str):
    """Determines the medical specialization based on patient symptoms."""
    symptoms_lower = symptoms.lower()
    if any(keyword in symptoms_lower for keyword in ["bone", "arm", "leg", "joint", "hip", "orthopedic"]):
        return "orthopedics"
    elif any(keyword in symptoms_lower for keyword in ["skin", "dermatology", "rash", "acne"]):
        return "dermatology"
    else:
        return "unknown"

# Tool to check/select a doctor based on the provided name.
@tool
def select_doctor(doc_name: str):
    """Selects a doctor based on the provided name."""
    doctors = [
        {"name": "Jane Smith", "specialty": "orthopedics"},
        {"name": "John Doe", "specialty": "dermatology"},
        {"name": "Alan Green", "specialty": "orthopedics"},
        {"name": "Mary Brown", "specialty": "dermatology"}
    ]
    for doctor in doctors:
        if (doctor['name'].lower() == doc_name.lower()) or (doctor['name'].split()[0].lower() == doc_name.split()[0].lower()):
            return doctor
    return "Doctors relating to your problem are unavailable right now"

# New tool to book an appointment given doctor name, date, and time.
@tool
def book_appointment(doctor_name: str, date: str, time: str):
    """Books an appointment with the selected doctor at the specified date and time."""
    doctors = [
        {"name": "Jane Smith", "specialty": "orthopedics"},
        {"name": "John Doe", "specialty": "dermatology"},
        {"name": "Alan Green", "specialty": "orthopedics"},
        {"name": "Mary Brown", "specialty": "dermatology"}
    ]
    for doctor in doctors:
        if doctor['name'].lower() == doctor_name.lower():
            return f"Appointment booked with Dr. {doctor['name']} on {date} at {time}"
    return "Doctor not found. Unable to book appointment."

# Update the tools list to include the new appointment booking tool.
tools = [check_field, select_doctor, book_appointment]
model_with_tools = model.bind_tools(tools)

tool_node = ToolNode(tools)
graph_builder.add_node("tool_node", tool_node)

# Helper function to ensure messages are in a standard dict format.
def ensure_message_format(messages):
    formatted = []
    for msg in messages:
        if isinstance(msg, str):
            formatted.append({"role": "user", "content": msg})
        elif isinstance(msg, dict):
            formatted.append(msg)
        else:
            # If message is an object, extract its attributes.
            role = get_message_attr(msg, "role", "user")
            content = get_message_attr(msg, "content", str(msg))
            formatted.append({"role": role, "content": content})
    return formatted

# Helper function to safely extract message content.
def get_message_content(message):
    return get_message_attr(message, "content", str(message))

# The chatbot node now injects a system message to guide the conversation.
def chatbot(state: State):
    state["messages"] = ensure_message_format(state["messages"])
    # Safely check the role of the first message.
    first_role = get_message_attr(state["messages"][0], "role") if state["messages"] else None
    if first_role != "system":
        system_message = (
            "You are a medical chatbot. First, ask the patient to describe their symptoms. "
            "Determine the potential disease and required specialty—only orthopedics and dermatology are available. "
            "If the symptoms do not match these specialties, reply that the disease symptoms do not match the available specialties. "
            "If they do match, ask the patient for the preferred doctor's name along with the desired appointment date and time. "
            "Once provided, confirm that the appointment is booked."
        )
        state["messages"].insert(0, {"role": "system", "content": system_message})
    return {"messages": [model_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

# Conditional edge to check if a tool was called.
def conditional_edge(state: State) -> Literal["tool_node", "__end__"]:
    last_message = state["messages"][-1]
    return "tool_node" if hasattr(last_message, "tool_calls") and last_message.tool_calls else "__end__"

graph_builder.add_conditional_edges("chatbot", conditional_edge)
graph_builder.add_edge("tool_node", "chatbot")
graph_builder.set_entry_point("chatbot")

memory = SqliteSaver.from_conn_string(":memory:")
graph = graph_builder.compile(checkpointer=MemorySaver())

# Prevent running the chatbot in CLI mode when imported into FastAPI.
if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        config = {'configurable': {'thread_id': '1'}}
        response = graph.invoke({"messages": [user_input]}, config=config)
        last_message = response["messages"][-1]
        print("Bot:", get_message_content(last_message))
        print('-' * 20)
