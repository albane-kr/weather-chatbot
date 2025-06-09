import json
import requests
import csv
import random
import os
from datetime import datetime
from io import StringIO
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Weather processing functions from your Flask app
def get_temperature(csv_path: str) -> Optional[int]:
    """
    Retrieves the temperature value closest to the current time from lstm_predictions.csv.
    """
    try:
        with open(csv_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            now = datetime.now()
            closest_row = min(
                reader,
                key=lambda row: abs(datetime.fromisoformat(row["time"]) - now)
            )
            temp_str = closest_row["temp"]
            try:
                temp = float(temp_str)
                print(f"Raw temperature value (closest time row): {temp}")
                return int(round(temp))
            except Exception as e:
                print(f"Invalid temperature value: {temp_str} ({e})")
                return None
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
    return None

def get_weather_id_from_coco(csv_path: str) -> Optional[str]:
    """
    Retrieves the coco value from the row with the timestamp closest to now,
    rounds it to the nearest integer, and maps it to a weather_id using coco_to_weather_id.csv file mapping.
    If multiple weather_id are mapped to the same coco_code, one is chosen randomly.
    """
    try:
        with open(csv_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            now = datetime.now()
            closest_row = min(
                reader,
                key=lambda row: abs(datetime.fromisoformat(row["time"]) - now)
            )
            coco_value = float(closest_row["coco"])
            print(f"Raw COCO value (closest time row): {coco_value}")
            coco_rounded = int(round(coco_value))
            print(f"Rounded COCO value: {coco_rounded}")
            weather_ids = []
            with open("llm/coco_to_weather_id.csv", encoding="utf-8") as mapfile:
                mapreader = csv.DictReader(mapfile)
                for row in mapreader:
                    coco_code = row["coco_code"].strip().rstrip(',')
                    if coco_code and int(coco_code) == coco_rounded:
                        weather_ids.append(row["weather_id"].strip())
            if weather_ids:
                return random.choice(weather_ids)
    except Exception as e:
        print(f"Error processing coco to weather_id: {e}")
    return None

def get_weather_expression(language: str, weather_id: str) -> str:
    """
    Selects a random expression from the correct CSV file based on language and weather_id.
    """
    if language.lower() == "french":
        filename = "llm/weather_expressions_FR.csv"
    else:
        filename = "llm/weather_expressions_DE.csv"
    expressions = []
    try:
        with open(filename, encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            for row in reader:
                if len(row) >= 2 and row[0].strip() == str(weather_id):
                    expressions.append(row[1].strip())
        if expressions:
            expression = random.choice(expressions)
            print(f"Selected expression: {expression}")
            return expression
        else:
            return "I am speechless!"
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return ""

def get_weather_forecast(city_name: str, forecast_hours: int = 72, session_id: str = None):
    """
    Calls the external weather API and returns the path to the CSV file.
    """
    url = "http://127.0.0.1:5001/weather/predict_lstm"
    payload = {
        "city_name": city_name,
        "forecast_hours": forecast_hours,
        "session_id": session_id
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../weather_forecast_api/lstm_predictions_{session_id}.csv"))
        print(f"Weather forecast CSV saved to: {csv_path}")
        return csv_path
    except Exception as e:
        print(f"Error calling weather API: {e}")
        return None

# LangChain tool for weather information
@tool
def get_weather(city: str, language: str = "french") -> dict:
    """
    Get comprehensive weather information for a specific city using the local weather prediction API.
    
    Args:
        city (str): The name of the city to get weather for
        language (str): Language for weather expressions (english, french, german)
        
    Returns:
        str: Comprehensive weather information including temperature, weather description, and expression
    """
    try:
        # Generate a session ID for this request
        import uuid
        session_id = str(uuid.uuid4())
        
        print(f"Getting weather forecast for {city} (session: {session_id})")
        
        # Get weather forecast CSV file
        csv_path = get_weather_forecast(city, session_id=session_id)
        print(f"CSV path: {csv_path}")
        if not csv_path:
            return f"Failed to retrieve weather data for {city}. Please check if the weather API is running."
        
        # Check if the CSV file exists
        if not os.path.exists(csv_path):
            return f"Weather data file not found for {city}. The API may not have generated the forecast yet."
        
        # Get temperature
        temperature = get_temperature(csv_path)
        if temperature is None:
            return f"Failed to retrieve temperature data for {city}."
        
        # Get weather ID from coco value
        weather_id = get_weather_id_from_coco(csv_path)
        if weather_id is None:
            return f"Failed to determine weather conditions for {city}."
        
        # Get weather expression
        expression = get_weather_expression(language, weather_id)
        if not expression:
            expression = "Clear conditions"
        
        # Format the response
        response = f"Weather in {city}:\n"
        response += f"🌡️ Temperature: {temperature}°C\n"
        response += f"🌤️ Conditions: {expression}\n"
        response += f"📊 Weather ID: {weather_id}\n"
        response += f"🕐 Forecast based on current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Clean up the CSV file
        try:
            os.remove(csv_path)
            print(f"Cleaned up CSV file: {csv_path}")
        except Exception as e:
            print(f"Could not clean up CSV file: {e}")
        
        return {"output: ",response}
        
    except Exception as e:
        return f"Error getting weather information for {city}: {str(e)}"

# Enhanced tool that can detect language from the question
@tool 
def get_weather_smart(city: str, user_question: str = "") -> dict:
    """
    Get weather information with automatic language detection from user question.
    
    Args:
        city (str): The name of the city to get weather for
        user_question (str): The original user question to detect language
        
    Returns:
        str: Weather information in appropriate language
    """
    # Simple language detection based on keywords
    language = "english"  # default
    question_lower = user_question.lower()
    
    if any(word in question_lower for word in ["météo", "temps", "température", "french", "français"]):
        language = "french"
    elif any(word in question_lower for word in ["wetter", "temperatur", "german", "deutsch"]):
        language = "german"
    
    print(f"Detected language: {language}")
    return get_weather.invoke({"city": city, "language": language})

def main():
    # Initialize the Llama 3.1 model with Ollama
    llm = ChatOllama(
        model="llama3.1",
        temperature=0,
    )
    
    # Create the tools list - using the smart weather tool
    tools = [get_weather_smart]
    
    # Create a prompt template for the agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful weather assistant with access to advanced weather prediction capabilities. 

        When users ask about weather in specific cities, use the get_weather_smart function to provide detailed weather information including:
        - Current temperature
        - Weather conditions and expressions
        - Weather classification ID
        - Forecast timestamp

        The weather system supports multiple languages and will automatically detect the appropriate language from the user's question.
        
        Extract the city name from the user's question and call the function with both the city name and the original user question for language detection.
        
        If the user's question is not about weather, respond normally without using any tools."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Example usage
    print("Advanced Weather Assistant with Llama 3.1 Function Calling")
    print("=" * 60)
    print("Features:")
    print("- LSTM-based weather predictions")
    print("- Multi-language support (English, French, German)")
    print("- Automatic language detection")
    print("- Weather condition classification")
    print("=" * 60)
    
    # Test questions in different languages
    test_questions = [
        "What's the weather like in Luxembourg?",
        "Quel temps fait-il à Luxembourg?",  # French
        "Wie ist das Wetter in Berlin?",  # German
        "Can you tell me the current weather in Tokyo?",
        "What's the temperature in New York City today?",
        "Météo à Marseille s'il vous plaît",  # French
        "Hello, how are you?"  # Non-weather question
    ]
    
    for question in test_questions:
        print(f"\n🤔 User: {question}")
        try:
            response = agent_executor.invoke({"input": question})
            print(f"🤖 Assistant: {response['output']}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        print("-" * 40)

def interactive_mode():
    """Interactive mode for testing with user input"""
    llm = ChatOllama(
        model="llama3.1",
        temperature=0,
    )
    
    tools = [get_weather_smart]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful weather assistant with access to advanced weather prediction capabilities. 

        When users ask about weather in specific cities, use the get_weather_smart function to provide detailed weather information.
        The system supports multiple languages and will automatically detect the appropriate language.
        
        Extract the city name from the user's question and call the function with both the city name and the original user question.
        
        If the user's question is not about weather, respond normally without using any tools."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    print("Interactive Advanced Weather Assistant")
    print("Supports: English, French (français), German (Deutsch)")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        user_input = input("\n🤔 You: ")
        if user_input.lower() == 'quit':
            break
            
        try:
            response = agent_executor.invoke({"input": user_input})
            print(f"🤖 Assistant: {response['output']}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Run the example
    main()
    
    # Uncomment the line below to run in interactive mode
    #interactive_mode()