from flask import Flask, request, jsonify
from flask_cors import CORS
from llm.LLMAccess import generate_response

app = Flask(__name__)
CORS(app)
@app.route('/generate-response', methods=['POST'])
def generate_response_api():
    data = request.json
    prompt = data.get('prompt')
    language = data.get('language')
    weather_type = data.get('weather_type')
    weather_type_intensity = data.get('weather_type_intensity')
    temperature = data.get('temperature')
    geolocation = data.get('geolocation')
    expression = data.get('expression')
    emotion = data.get('emotion')

    # Call the generate_response function
    response = generate_response(prompt, language, weather_type, weather_type_intensity, temperature, geolocation, expression, emotion)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)