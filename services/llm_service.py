import os
import json
import re
from google import genai
from google.genai import types

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
    """
    # Remove markdown code blocks
    clean = re.sub(r'```json', '', text)
    clean = re.sub(r'```', '', clean).strip()
    
    # Extract JSON object between first { and last }
    first_brace = clean.find('{')
    last_brace = clean.rfind('}')
    
    if first_brace != -1 and last_brace != -1:
        clean = clean[first_brace : last_brace + 1]
    
    return clean

async def analyze_issue_with_llm(issue_data: dict) -> dict:
    """
    Analyzes issue data using the Google Gemini SDK (new google.genai package).
    """
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY is missing in .env")

    # Initialize the client with API key
    client = genai.Client(api_key=api_key)

    prompt = f"""
{SYSTEM_PROMPT}

Analyze the following GitHub Issue:

Title: {issue_data['title']}
Body: {issue_data['body']}
Comments Summary:
{issue_data['comments']}

Provide the JSON output strictly adhering to the schema.
"""

    try:
        # Use the new API with generate_content
        response = await client.aio.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                safety_settings=[
                    types.SafetySetting(
                        category='HARM_CATEGORY_HATE_SPEECH',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_HARASSMENT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_DANGEROUS_CONTENT',
                        threshold='BLOCK_NONE'
                    ),
                ]
            )
        )
        
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
        print(f"Gemini SDK Error: {error_msg}")
        
        # Check if it's a rate limit error (429)
        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            raise ValueError("AI rate limit reached. Please wait a few seconds and try again.")
        
        raise ValueError(f"Gemini Error: {error_msg}")
