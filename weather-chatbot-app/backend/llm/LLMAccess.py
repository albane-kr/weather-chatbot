import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from dotenv import load_dotenv
from huggingface_hub import login

load_dotenv()
login(token=os.environ.get("HUGGINGFACE_API_KEY"))
model_name = "google/gemma-3-1b-it"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)


def generate_response(prompt: str, language: str, weather_type: str, weather_type_intensity: str, temperature: str, geolocation: str, expression: str, emotion: str) -> str:
    """
    @param prompt: str -> This parameter is the textual user input
    @param language: str -> This parameter is the language in which the user is speaking
    @param weather_type: str -> This parameter is the type of weather predicted by the weather prediction model developed by Henrik Klasen
    @param weather_type_intensity: str -> This parameter is the intensity of the weather predicted by the weather prediction model developed by Henrik Klasen
    @param temperature: str -> This parameter is the temperature predicted by the weather prediction model developed by Henrik Klasen
    @param geolocation: str -> This parameter is the geolocation chosen by the user, which is used to get the weather information
    @param expression: str -> This parameter is the expression describing the predicted weather
    @param emotion: str -> This parameter is the emotion detected in text

    @return: str -> The return value of this function is the textual response of the LLM for 
    the user.

    Description: This function takes the user input, adds some part between the | and then returns the textual response. 
    The length of this is limited to 10-30 words, to not significantly impact performance by too long responses.
    """
    full_prompt = (
        prompt + f"| request: keep the answer between 10 and 50 words and answer in {language}! Take into account that the answer should include the weather type {weather_type}, weather intensity {weather_type_intensity}, temperature {temperature}, geolocation {geolocation}, this expression: {expression}, and with this emotion: {emotion}. Do not fetch the real weather, assume the prediction in this prompt is correct."
    )
    inputs = tokenizer(full_prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=60)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response[len(full_prompt):].strip()
    print(response)
    return response

#generate_response("Hello, what is the weather like today in Berlin?", "French", "rainy", "high", "20", "Berlin", "il pleut comme vache qui pisse", "sad")