from flask import Flask, request, jsonify
from flask_cors import CORS
from llm.LLMAccess import generate_response
import csv
import random

app = Flask(__name__)
CORS(app)

def get_weather_id(weather_type, weather_type_intensity):
    #TODO
    pass

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
    weather_type = data.get('weather_type')
    weather_type_intensity = data.get('weather_type_intensity')
    temperature = data.get('temperature')
    geolocation = data.get('geolocation')
    weather_id = get_weather_id(weather_type, weather_type_intensity)
    expression = get_weather_expression(language, weather_id)
    emotion = data.get('emotion')

    # Call the generate_response function
    response = generate_response(prompt, language, weather_type, weather_type_intensity, temperature, geolocation, expression, emotion)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)