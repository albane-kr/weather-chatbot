from flask import Flask, request, jsonify
from flask_cors import CORS
from llm.LLMAccess import generate_response
import csv
import random
from llm.load_text_model import predict_emotion
import torch

app = Flask(__name__)
CORS(app)

device = "cuda:0" if torch.cuda.is_available() else "cpu" 

def get_temperature():
    """
    Retrieves the 12th value of temp from lstm_predictions.csv. Corresponds to the temperature at 12:00 PM on the day of the query.
    """
    try:
        with open("weather_forecast_api/lstm_predictions.csv", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            temps = [float(row["temp"]) for row in reader]
            if len(temps) >= 12:
                return temps[12]  # 12th value (0-based index)
    except Exception as e:
        print(f"Error reading lstm_predictions.csv: {e}")
    return None

def get_weather_id_from_coco():
    """
    Retrieves the 12th value of coco from lstm_predictions.csv,
    rounds it to the nearest integer, and maps it to a weather_id using coco_to_weather_id.csv file mapping.
    """
    try:
        with open("weather_forecast_api/lstm_predictions.csv", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            cocos = [float(row["coco"]) for row in reader]
            if len(cocos) >= 12:
                coco_value = cocos[12]  # 12th value (1-based index)
                coco_rounded = int(round(coco_value))
                # Now map to weather_id using coco_to_weather_id.csv
                with open("weather_forecast_api/coco_to_weather_id.csv", encoding="utf-8") as mapfile:
                    mapreader = csv.DictReader(mapfile)
                    for row in mapreader:
                        if int(row["coco_code"]) == coco_rounded:
                            return row["weather_id"]
    except Exception as e:
        print(f"Error processing coco to weather_id: {e}")
    return None

def get_weather_expression(language, weather_id):
    """
    Selects a random expression from the correct CSV file based on language and weather_id.
    """
    if language.lower() == "french":
        filename = "weather_expressions_FR.csv"
    else:
        filename = "weather_expressions_DE.csv"
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

@app.route('/generate-response', methods=['POST'])
def generate_response_api():
    data = request.json
    prompt = data.get('prompt')
    language = data.get('language')
    temperature = get_temperature()
    geolocation = data.get('geolocation')
    weather_id = get_weather_id_from_coco()
    expression = get_weather_expression(language, weather_id)
    emotion = predict_emotion(prompt, device)

    # Call the generate_response function
    response = generate_response(prompt, language, temperature, geolocation, expression, emotion)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)