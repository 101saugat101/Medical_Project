# This code is a medical chatbot that interacts with users to determine their symptoms, suggest a medical specialty, select a doctor, and book an appointment.
# It uses the LangGraph library to create a state graph and manage the conversation flow. The chatbot is powered by the Google Gemini model and includes tools for checking medical fields, selecting doctors, and booking appointments. The code also includes a FastAPI server to handle user input and responses.
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
