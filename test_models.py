import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("LLM_API_KEY")
genai.configure(api_key=api_key)

candidates = [
    "gemini-flash-lite-latest",
    "gemini-pro",
    "gemini-pro-latest",
    "gemini-2.5-flash-lite"
]

print("Testing model generation...")
for model_name in candidates:
    print(f"\nTesting: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"SUCCESS with {model_name}")
        break 
    except Exception as e:
        print(f"FAILED {model_name}: {e}")
