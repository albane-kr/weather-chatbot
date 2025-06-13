import requests
import csv
import random
import torch
from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

from langchain import hub
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory

from collections import defaultdict

from llm.load_text_model import predict_emotion

device = "cuda:0" if torch.cuda.is_available() else "cpu"

session_memories = defaultdict(lambda: ConversationBufferMemory(memory_key="chat_history", return_messages=True))

# Weather processing functions
def get_weather_id_from_coco(coco_code: float) -> Optional[str]:
    try:
        coco_rounded = int(round(coco_code))
        print(f"Rounded COCO value: {coco_rounded}")
        weather_ids = []
        with open("llm/coco_to_weather_id.csv", encoding="utf-8") as mapfile:
            mapreader = csv.DictReader(mapfile)
            for row in mapreader:
                coco_code = row["coco_code"].strip().rstrip(',')
                if coco_code and int(coco_code) == coco_rounded:
                    weather_ids.append(row["weather_id"].strip())
        if len(weather_ids) > 0:
            return random.choice(weather_ids)
        else:
            return '00'
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
        if weather_id != '00':
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
            return "No comment!"
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return ""

def get_weather_forecast(city_name: str, forecast_hours: int = 72):
    url = "http://127.0.0.1:5001/weather/predict"
    payload = {
        "city_name": city_name,
        "forecast_hours": forecast_hours
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Weather forecast response: {response.text}")
        return response
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
        print(f"Getting weather forecast for {city}")
        weather_api_data = get_weather_forecast(city)
        print(f"Results from API: {weather_api_data}")
        if not weather_api_data:
            return {"output": f"Failed to retrieve weather data for {city}. Please check if the weather API is running."}
        temperature_maximum = weather_api_data.json().get("tmax")
        if temperature_maximum is None:
            return {"output": f"Failed to retrieve maximum temperature data for {city}."}
        temperature_minimum = weather_api_data.json().get("tmin")
        if temperature_minimum is None:
            return {"output": f"Failed to retrieve minimum temperature data for {city}."}
        precipitation = weather_api_data.json().get("prcp")
        if temperature_maximum is None:
            return {"output": f"Failed to retrieve precipitation data for {city}."}
        coco_code = weather_api_data.json().get("coco")
        if coco_code is None:
            return {"output": f"Failed to retrieve coco data for {city}."}
        weather_id = get_weather_id_from_coco(coco_code=coco_code)
        if weather_id is None:
            return {"output": f"Failed to determine weather conditions for {city}."}
        expression = get_weather_expression(language, weather_id)
        if not expression:
            expression = "Clear conditions"
        weather_emoji = get_weather_icon_from_weather_id(weather_id)
        response = f"{weather_emoji} Weather in {city}:\n"
        response += f"🌡️ Temperatures: {temperature_minimum} - {temperature_maximum}°C\n"
        response += f"🌧️ Precipitation: {precipitation}mm\n"
        response += f"🌤️ Coco: {coco_code}\n"
        response += f"🌤️ Conditions: {expression}\n"
        response += f"📊 Weather ID: {weather_id}\n"
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
    
    # Get the weather response
    weather_result = get_weather.invoke({"city": city, "language": language})
    weather_output = weather_result.get("output", "")
    
    # Predict emotion using your model
    emotion = predict_emotion(weather_output, device)
    
    # Optionally, add the emotion to the output (as text or emoji)
    weather_output_with_emotion = f"{weather_output}\nEmotion: {emotion}"
    
    return {"output": weather_output_with_emotion}

# LangChain agent setup
llm = ChatOllama(
    model="llama3.1",  # Make sure this matches your Ollama model name
    temperature=0,
)
tools = [get_weather_smart]
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful weather assistant with access to advanced weather prediction capabilities.
        ONLY use the get_weather_smart tool if the user's question is about the weather. 
        If the question is not about the weather, answer directly and DO NOT use any tools.
        Your tasks:
        - Always answer in the same language as the user's input (English, French, or German).
        - When users ask about weather in specific cities, you MUST use the get_weather_smart function to provide detailed weather information, including:
            - Temperature range (clearly indicate the minimum temperature and maximum temperature)
            - Precipitation amount in mm
            - Weather conditions and expressions (always use the provided weather expression in your answer, use get_weather_expression(language, weather_id) to get the expression)
            - The weather icon (emoji) corresponding to the weather_id (use get_weather_icon_from_weather_id(weather_id) and always include the emoji in your answer after mentioning the weather conditions)
        - If the user's question is not about weather, respond normally without using any tools, but always in the language of the user's input.
        - You MUST answer in the tone of the emotion predicted by the model, which is based on the weather conditions and user question.
        - The weather system supports multiple languages and will automatically detect the appropriate language from the user's question.
        - Extract the city name from the user's question and call the function with both the city name and the original user question for language detection.
        - If the user's question is not about weather, respond normally without using any tools and don't mention anything about weather API, but always in the language of the user's input.
    {chat_history}"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(llm, tools, prompt)

# --- Flask app for frontend integration ---
app = Flask(__name__)
CORS(app)
@app.route('/api/weather', methods=['POST'])
def weather_api():
    data = request.json
    user_input = data.get("prompt")
    session_id = data.get("session_id", "default_session")

    memory = session_memories[session_id]
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)

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