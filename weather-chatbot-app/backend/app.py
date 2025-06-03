from flask import Flask, request, jsonify, session
import requests
from flask_cors import CORS
from llm.LLMAccess import generate_response
import csv
import random
from llm.load_text_model import predict_emotion
import torch
import os
from datetime import datetime
import uuid
from aiohttp import web

app = Flask(__name__)
app.secret_key = '06032025'
CORS(app)

device = "cuda:0" if torch.cuda.is_available() else "cpu" 

def get_temperature(csv_path):
    """
    Retrieves the 12th value of temp from lstm_predictions.csv. Corresponds to the temperature at 12:00 PM on the day of the query.
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
                return int(round(temp))
            except Exception as e:
                print(f"Invalid temperature value: {temp_str} ({e})")
                return None
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
    return None

def get_weather_id_from_coco(csv_path):
    """
    Retrieves the 12th value of coco from lstm_predictions.csv,
    rounds it to the nearest integer, and maps it to a weather_id using coco_to_weather_id.csv file mapping.
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

def get_weather_expression(language, weather_id):
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
            return random.choice(expressions)
        else:
            return "I am speechless!"
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return ""

def get_weather_forecast(city_name, forecast_hours=72, session_id=None):
    """
    Calls the external weather API and returns the response JSON.
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
        return csv_path
    except Exception as e:
        print(f"Error calling weather API: {e}")
        return None

@app.route('/generate-response', methods=['POST'])
def generate_response_api():
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        print(f"Generated new session ID: {session['session_id']}")
    else:
        print(f"Using existing session ID: {session_id}")

    data = request.json
    prompt = data.get('prompt')
    language = data.get('language')
    geolocation = data.get('geolocation')
    print(f"Received prompt: {prompt}, language: {language}, geolocation: {geolocation}")

    weather_data = get_weather_forecast(geolocation, session_id=session_id)
    if not weather_data:
        return jsonify({'error': 'Failed to retrieve weather data'}), 500
    
    temperature = get_temperature(weather_data)
    print(f"Temperature: {temperature}")
    if temperature is None:
        return jsonify({'error': 'Failed to retrieve temperature data'}), 500
    
    weather_id = get_weather_id_from_coco(weather_data)
    print(f"Weather ID: {weather_id}")
    if weather_id is None:
        return jsonify({'error': 'Failed to retrieve weather ID'}), 500
    
    expression = get_weather_expression(language, weather_id)
    print(f"Weather Expression: {expression}")
    if not expression:
        return jsonify({'error': 'Failed to retrieve weather expression'}), 500
    
    emotion = predict_emotion(prompt, device)
    print(f"Detected Emotion: {emotion}")
    if not emotion:
        return jsonify({'error': 'Failed to detect emotion'}), 500

    # Call the generate_response function
    response = generate_response(prompt, language, temperature, geolocation, expression, emotion)
    return jsonify({'response': response, 'session_id': session_id})

if __name__ == '__main__':
    app.run(debug=True)