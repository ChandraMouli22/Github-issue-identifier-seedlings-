import os
import json
import re
import asyncio
import google.generativeai as genai
import httpx
from huggingface_hub import AsyncInferenceClient

SYSTEM_PROMPT = """
You are an expert technical project manager and developer.
Your task is to analyze GitHub issues and output a strictly formatted JSON summary.
You must NOT output anything other than the JSON object.
Do not include markdown formatting like ```json or ```.

Output Schema:
{
  "summary": "A one-sentence summary of the user's problem or request.",
  "type": "bug" | "feature_request" | "documentation" | "question" | "other",
  "priority_score": "A string containing the score (1-5) followed by a brief justification (e.g., '4/5 – Blocks users...').",
  "suggested_labels": ["Array of exactly 2-3 labels. Prefer standard GitHub labels like 'bug', 'enhancement', 'documentation', 'help wanted', 'ui', 'backend'. Avoid highly specific custom labels."],
  "potential_impact": "Brief impact description."
}
"""

def clean_json(text: str) -> str:
    """
    Cleans the LLM response to ensure valid JSON.
    Removes markdown code blocks and reasoning tags like <think>...</think>.
    """
    # Remove <think> blocks (DeepSeek R1 reasoning)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Remove markdown code blocks
    clean = re.sub(r'```json', '', text)
    clean = re.sub(r'```', '', clean).strip()
    
    # Extract JSON object between first { and last }
    first_brace = clean.find('{')
    last_brace = clean.rfind('}')
    
    if first_brace != -1 and last_brace != -1:
        clean = clean[first_brace : last_brace + 1]
    
    return clean

async def analyze_issue_with_llm(issue_data: dict, model_name: str = "gemini-2.0-flash", provider: str = "google") -> dict:
    """
    Dispatcher function to route analysis to the correct LLM provider.
    """
    if provider == "huggingface":
        return await analyze_with_huggingface(issue_data, model_name)
    elif provider == "google":
        return await analyze_with_gemini(issue_data, model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

async def analyze_with_huggingface(issue_data: dict, model_name: str) -> dict:
    """
    Analyzes issue using Hugging Face Inference API via AsyncInferenceClient.
    """
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_API_KEY is missing in .env")

    # Initialize Async Client
    client = AsyncInferenceClient(token=api_key)

    prompt = f"""
{SYSTEM_PROMPT}

Analyze the following GitHub Issue:

Title: {issue_data['title']}
Body: {issue_data['body']}
Comments Summary:
{issue_data['comments']}

Provide the JSON output strictly adhering to the schema.
"""
    
    messages = [
        {"role": "user", "content": prompt}
    ]

    try:
        # Use chat_completion which handles format automatically
        response = await client.chat_completion(
            messages=messages,
            model=model_name,
            max_tokens=1024,
            temperature=0.1
        )
        
        # Extract content
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from Hugging Face model")
            
        cleaned_text = clean_json(content)
        return json.loads(cleaned_text)
                 
    except json.JSONDecodeError:
        print(f"Failed JSON: {content}")
        raise ValueError("Failed to parse Hugging Face response as JSON")
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "model_not_found" in error_msg:
            raise ValueError(
                f"The model '{model_name}' is not available or access is denied (gated model). "
                "Please check if you have access to this model on Hugging Face. "
                "If not, consider switching to an open-access model such as DeepSeek or Gemini Flash Lite for best results."
            )
        raise ValueError(f"Hugging Face API Error: {error_msg}")

async def analyze_with_gemini(issue_data: dict, model_name: str) -> dict:
    """
    Analyzes issue data using the Google Gemini SDK with retry logic.
    
    Args:
        issue_data: Dictionary containing issue title, body, and comments
        model_name: Name of the Gemini model to use
    """
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY is missing in .env")

    genai.configure(api_key=api_key)
    
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    
    model = genai.GenerativeModel(
        model_name=model_name,  # Use the provided model name
        generation_config={
            "response_mime_type": "application/json"
        },
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )

    prompt = f"""
{SYSTEM_PROMPT}

Analyze the following GitHub Issue:

Title: {issue_data['title']}
Body: {issue_data['body']}
Comments Summary:
{issue_data['comments']}

Provide the JSON output strictly adhering to the schema.
"""

    # Retry logic with exponential backoff
    max_retries = 3
    base_delay = 5  # Start with 5 seconds
    
    for attempt in range(max_retries):
        try:
            response = await model.generate_content_async(prompt)
            text = response.text
            
            cleaned_content = clean_json(text)
            
            try:
                return json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
                print(f"Raw Content: {text}")
                raise ValueError("Failed to parse LLM response as JSON")

        except Exception as e:
            error_msg = str(e)
            print(f"Gemini SDK Error (Attempt {attempt + 1}/{max_retries}): {error_msg}")
            
            # Check if it's a rate limit error (429)
            is_rate_limit = "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower() or "resource_exhausted" in error_msg.lower()
            
            if is_rate_limit and attempt < max_retries - 1:
                # Exponential backoff: 5s, 10s, 20s
                delay = base_delay * (2 ** attempt)
                print(f"⏳ Rate limit hit. Waiting {delay} seconds before retry...")
                await asyncio.sleep(delay)
                continue
            
            # If it's a rate limit error on last attempt, give helpful message
            if is_rate_limit:
                raise ValueError(f"Rate limit reached for this model. Please try switching to Gemini Flash Lite or DeepSeek R1 Distill from the dropdown, or wait a minute and retry.")
            
            # For other errors, raise immediately
            raise ValueError(f"Gemini Error: {error_msg}")

