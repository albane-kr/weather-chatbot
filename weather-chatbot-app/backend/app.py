import json
import requests
import csv
import random
import os
from datetime import datetime
from io import StringIO
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Weather processing functions
def get_temperature(csv_path: str) -> Optional[int]:
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

def get_weather_icon_from_weather_id(weather_id):
    weather_id = str(weather_id)
    if weather_id == '1':
        return '🌦️'  # light_rain
    if weather_id == '2':
        return '🌧️'  # medium_rain
    if weather_id == '3':
        return '⛈️'  # high_rain
    if weather_id == '4':
        return '🌤️'  # light_sun
    if weather_id == '5':
        return '☀️'  # medium_sun
    if weather_id == '6':
        return '🌞'  # high_sun
    if weather_id == '7':
        return '🌥️'  # light_cloud
    if weather_id == '8':
        return '☁️'  # medium_cloud
    if weather_id == '9':
        return '🌫️'  # high_cloud
    if weather_id == '10':
        return '❄️'  # light_snow
    if weather_id == '11':
        return '🌨️'  # medium_snow
    if weather_id == '12':
        return '☃️'  # high_snow
    return ''  # default

# LangChain tool for weather information
@tool
def get_weather(city: str, language: str) -> dict:
    """
    Get comprehensive weather information for a specific city using the local weather prediction API.
    """
    try:
        import uuid
        session_id = str(uuid.uuid4())
        print(f"Getting weather forecast for {city} (session: {session_id})")
        csv_path = get_weather_forecast(city, session_id=session_id)
        print(f"CSV path: {csv_path}")
        if not csv_path:
            return {"output": f"Failed to retrieve weather data for {city}. Please check if the weather API is running."}
        if not os.path.exists(csv_path):
            return {"output": f"Weather data file not found for {city}. The API may not have generated the forecast yet."}
        temperature = get_temperature(csv_path)
        if temperature is None:
            return {"output": f"Failed to retrieve temperature data for {city}."}
        weather_id = get_weather_id_from_coco(csv_path)
        if weather_id is None:
            return {"output": f"Failed to determine weather conditions for {city}."}
        expression = get_weather_expression(language, weather_id)
        if not expression:
            expression = "Clear conditions"
        weather_emoji = get_weather_icon_from_weather_id(weather_id)
        response = f"{weather_emoji} Weather in {city}:\n"
        response += f"🌡️ Temperature: {temperature}°C\n"
        response += f"🌤️ Conditions: {expression}\n"
        response += f"📊 Weather ID: {weather_id}\n"
        response += f"🕐 Forecast based on current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        try:
            os.remove(csv_path)
            print(f"Cleaned up CSV file: {csv_path}")
        except Exception as e:
            print(f"Could not clean up CSV file: {e}")
        return {"output": response}
    except Exception as e:
        return {"output": f"Error getting weather information for {city}: {str(e)}"}

# Enhanced tool that can detect language from the question
@tool 
def get_weather_smart(city: str, user_question: str = "") -> dict:
    """
    Get weather information with automatic language detection from user question.
    """
    language = "english"  # default
    question_lower = user_question.lower()
    if any(word in question_lower for word in ["météo", "temps", "température", "french", "français"]):
        language = "french"
    elif any(word in question_lower for word in ["wetter", "temperatur", "german", "deutsch"]):
        language = "german"
    print(f"Detected language: {language}")
    return get_weather.invoke({"city": city, "language": language})

# LangChain agent setup
llm = ChatOllama(
    model="llama3.1",  # Make sure this matches your Ollama model name
    temperature=0,
)
tools = [get_weather_smart]
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful weather assistant with access to advanced weather prediction capabilities.

Your tasks:
- Always answer in the same language as the user's input (English, French, or German).
- When users ask about weather in specific cities, you MUST use the get_weather_smart function to provide detailed weather information, including:
    - Current temperature
    - Weather conditions and expressions (always use the provided weather expression in your answer)
    - Forecast timestamp
    - The weather icon (emoji) corresponding to the weather_id (always include the emoji in your answer after mentioning the weather conditions)
- If the user's question is not about weather, respond normally without using any tools, but always in the language of the user's input.
- The weather system supports multiple languages and will automatically detect the appropriate language from the user's question.
- Extract the city name from the user's question and call the function with both the city name and the original user question for language detection.
- If the user's question is not about weather, respond normally without using any tools and don't mention anything about weather API, but always in the language of the user's input.
"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Flask app for frontend integration ---
app = Flask(__name__)
CORS(app)

@app.route('/api/weather', methods=['POST'])
def weather_api():
    data = request.json
    user_input = data.get("prompt")
    try:
        response = agent_executor.invoke({"input": user_input})
        output = response["output"]
        return jsonify({
            "output": output
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # To test the agent with hardcoded questions, uncomment below:
    # test_questions = [
    #     "What's the weather like in Luxembourg?",
    #     "Quel temps fait-il à Luxembourg?",  # French
    #     "Wie ist das Wetter in Berlin?",  # German
    #     "Can you tell me the current weather in Tokyo?",
    #     "What's the temperature in New York City today?",
    #     "Météo à Marseille s'il vous plaît",  # French
    #     "Hello, how are you?"  # Non-weather question
    # ]
    # for question in test_questions:
    #     print(f"\n🤔 User: {question}")
    #     try:
    #         response = agent_executor.invoke({"input": question})
    #         print(f"🤖 Assistant: {response['output']}")
    #     except Exception as e:
    #         print(f"❌ Error: {str(e)}")
    #     print("-" * 40)
    print("Starting Flask API for Advanced Weather Assistant...")
    app.run(host="0.0.0.0", port=5000, debug=True)