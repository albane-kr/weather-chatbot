import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from dotenv import load_dotenv
from huggingface_hub import login
import re
import json

load_dotenv()
login(token=os.environ.get("HUGGINGFACE_API_KEY"))
model_name = "google/gemma-3-1b-it"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def extract_args_from_input(user_input:str) -> str:
    """
    Function call
    Extracts the language, temperature, geolocation, expression, and emotion from the user input using the LLM.
    
    @param user_input: str -> The user input containing the parameters.
    
    @return: str -> A formatted string with the extracted parameters.
    """
    extraction_prompt = f"""
Extract the following fields from the user input:
- geolocation (the city the user is asking about)
- prompt (the user's question or statement)

Respond ONLY in JSON format like:
{{
  "geolocation": "...",
  "prompt": "..."
}}

User input: {user_input}
"""
    inputs = tokenizer(extraction_prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=128)
    extraction_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    match = re.search(r'\{.*\}', extraction_response, re.DOTALL)
    if not match:
        return {"geolocation": None, "prompt": user_input}
    try:
        args = json.loads(match.group())
    except Exception:
        args = {"geolocation": None, "prompt": user_input}
    print(f"Extracted args: {args}")
    return args

def generate_response(prompt: str, language: str, temperature: str, geolocation: str, expression: str, emotion: str) -> str:
    """
    @param prompt: str -> This parameter is the textual user input
    @param language: str -> This parameter is the language in which the user is speaking
    @param temperature: str -> This parameter is the temperature predicted by the weather prediction model developed by Henrik Klasen
    @param geolocation: str -> This parameter is the geolocation chosen by the user, which is used to get the weather information
    @param expression: str -> This parameter is the expression describing the predicted weather
    @param emotion: str -> This parameter is the emotion detected in text

    @return: str -> The return value of this function is the textual response of the LLM for 
    the user.
    """

    full_prompt = (
        f"You are asked to give the temperature in {geolocation}. The temperature was already calculated beforehand so you just need to give the answer. keep the answer between 10 and 20 words and answer in {language}! The tone of the answer should be {emotion}. Take into account that the answer should include the temperature {temperature}°C, geolocation {geolocation}, and this expression: {expression}. Do not fetch the real weather, assume the prediction in this prompt is correct"
    )
    inputs = tokenizer(full_prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=100)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response[len(full_prompt):].strip()
    print(response)
    return response