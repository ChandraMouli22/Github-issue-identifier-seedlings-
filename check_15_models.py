import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("LLM_API_KEY")
genai.configure(api_key=api_key)

print("Searching for Flash models...")
for m in genai.list_models():
    if 'flash' in m.name.lower():
        print(f"Make: {m.name} | Methods: {m.supported_generation_methods}")
