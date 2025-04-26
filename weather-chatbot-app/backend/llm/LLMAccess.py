import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
# INSERT YOUR API KEY BELOW
genai.configure(api_key=os.environ("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
def generate_response(prompt: str, language: str, weather_type: str, temperature: str, geolocation: str, expression: str, emotion: str) -> str:
    """
    @param prompt: str -> This parameter is the textual user input
    @param language: str -> This parameter is the language in which the user is speaking
    @param emotion: str -> This parameter is the emotion detected in text

    @return: str -> The return value of this function is the textual response of the LLM for 
    the user.

    Description: This function takes the user input, adds some part between the | and then returns the textual response. 
    The length of this is limited to 10-30 words, to not significantly impact performance by too long responses.
    """
    response = model.generate_content(prompt + f" | request: keep the answer between 10 and 30 words and answer in {language}! | Take into account that the answer should include the weather type {weather_type}, temperature {temperature}, geolocation {geolocation}, and this expression: {expression}, and with this emotion: {emotion}")
    print(response)
    return response.text