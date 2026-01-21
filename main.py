import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

from services.github_service import get_issue_data
from services.llm_service import analyze_issue_with_llm
from services.cache_service import get_cached_analysis, save_to_cache

# Available models configuration
AVAILABLE_MODELS = [
    # Google Gemini Models
    {
        "id": "gemini-2.0-flash",
        "name": "Gemini 2.0 Flash",
        "description": "Newest generation",
        "speed": "fast",
        "recommended": False,
        "provider": "google"
    },
    {
        "id": "gemini-2.0-flash-lite",
        "name": "Gemini 2.0 Flash Lite",
        "description": "Lightweight & efficient",
        "speed": "fastest",
        "recommended": False,
        "provider": "google"
    },
    {
        "id": "gemini-flash-lite-latest",
        "name": "Gemini Flash Lite",
        "description": "Previous stable generation",
        "speed": "fast",
        "recommended": False,
        "provider": "google"
    },
    # Hugging Face Models
    {
        "id": "deepseek-ai/DeepSeek-R1",
        "name": "DeepSeek R1",
        "description": "Full 671B Base Model",
        "speed": "slow",
        "recommended": False,
        "provider": "huggingface"
    },
    {
        "id": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "name": "DeepSeek R1 Distill",
        "description": "Powerful reasoning model",
        "speed": "medium",
        "recommended": True,
        "provider": "huggingface"
    },
    {
        "id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "name": "Llama 3.1 8B",
        "description": "Meta's latest open model",
        "speed": "fast",
        "recommended": False,
        "provider": "huggingface"
    }
]

app = FastAPI()

# Input Schema
class AnalyzeRequest(BaseModel):
    repoUrl: str
    issueNumber: int
    model: str = "gemini-2.0-flash"  # Default model

# 1. API Routes
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/models")
async def get_models():
    """Get list of available AI models"""
    return {"models": AVAILABLE_MODELS}

@app.post("/api/analyze")
async def analyze_issue(request: AnalyzeRequest):
    try:
        print(f"Analyzing: {request.repoUrl} #{request.issueNumber} with model: {request.model}")
        
        # Determine provider based on model ID
        provider = "google" # Default
        for m in AVAILABLE_MODELS:
            if m["id"] == request.model:
                provider = m.get("provider", "google")
                break
        
        # Check cache first (cache key includes model)
        cached_result = get_cached_analysis(request.repoUrl, request.issueNumber, request.model)
        if cached_result:
            return cached_result
        
        # 1. Fetch from GitHub
        issue_data = await get_issue_data(request.repoUrl, request.issueNumber)
        
        # 2. Analyze with selected LLM and provider
        analysis = await analyze_issue_with_llm(issue_data, request.model, provider)
        
        # 3. Save to cache for future use (with model in key)
        save_to_cache(request.repoUrl, request.issueNumber, request.model, analysis)
        
        return analysis

    except ValueError as e:
        # Client errors (400/404)
        error_msg = str(e)
        status_code = 404 if "not found" in error_msg.lower() else 400
        raise HTTPException(status_code=status_code, detail=error_msg)
    except Exception as e:
        # Server errors (500)
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 2. Static Files
# Mount the public directory to serve assets (css, js)
app.mount("/static", StaticFiles(directory="public"), name="static")

# Serve index.html at root
@app.get("/")
async def read_index():
    return FileResponse("public/index.html")

# Catch-all for other static files if they are requested relative to root (like styles.css in index.html)
# Since the HTML uses <link href="styles.css">, we strictly need to serve them from root or fix HTML.
# Constraints say "Do not change frontend".
# So we must serve text/css and application/javascript files located in public/ at the root level too.

@app.get("/{filename}")
async def read_root_file(filename: str):
    file_path = os.path.join("public", filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
