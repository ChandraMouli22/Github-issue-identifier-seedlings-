# GitHub Issue Analyzer 🔍

AI-powered GitHub issue analysis tool that provides deep insights into repository issues using multiple LLM providers (Google Gemini and Hugging Face).

## 🚀 Live Demo

**Try it now:** [https://github-issue-analyzer.onrender.com](https://github-issue-analyzer.onrender.com)

[![Deploy Status](https://img.shields.io/badge/deployment-live-success.svg)](https://github-issue-analyzer.onrender.com)

---

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![CI/CD](https://github.com/ChandraMouli22/Github-issue-identifier-seedlings-/actions/workflows/tests.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen.svg)
![Tests](https://img.shields.io/badge/tests-51%20passed-success.svg)

## ✨ Features

- **🤖 Multi-Model AI Support** - Choose from Google Gemini or Hugging Face models (DeepSeek R1, Llama 3.1)
- **📊 Smart Insights** - Generates summary, priority score, and impact assessment
- **🏷️ Label Suggestions** - Recommends appropriate labels for better organization
- **📈 Progress Tracking** - Visual 3-step progress indicator (Fetching → Analyzing → Complete)
- **🌙 Dark/Light Mode** - Theme toggle with localStorage persistence
- **💾 Export Options** - Download analysis as Markdown or PDF
- **🖥️ Code Editor UI** - Professional editor-style JSON viewer with macOS chrome
- **⚡ Real-time Updates** - Live analysis with smooth animations

## 🎯 Bonus Features (Beyond Requirements)

This project goes beyond the core requirements with production-ready features:

### 🤖 Multi-Model LLM Support
- **Multiple AI providers** - Choose between Google Gemini and Hugging Face models
- **6 models available** - 3 Gemini models + 3 Hugging Face models (DeepSeek R1, Llama 3.1)
- **Provider abstraction** - Seamless switching between providers with unified API
- **Model-specific features** - DeepSeek R1 reasoning support with `<think>` tag parsing
- **Fallback suggestions** - Rate limit errors suggest alternative models
- **Impact**: Flexibility to choose the best model for your use case, avoid vendor lock-in

### 🗄️ Intelligent Caching System
- **Automatic result caching** - Analysis results are stored locally using MD5-hashed cache keys
- **Model-specific caching** - Each model's analysis is cached separately
- **Instant responses** - Previously analyzed issues return instantly without API calls
- **Persistent storage** - Cache survives server restarts
- **Smart invalidation** - Each unique repo/issue/model combination gets its own cache entry
- **Impact**: Dramatically reduces API usage and prevents rate limit errors

### 🔄 Retry Logic with Exponential Backoff
- **Automatic retries** - Up to 3 retry attempts on rate limit errors
- **Smart delays** - Exponential backoff (5s → 10s → 20s)
- **Graceful degradation** - User-friendly error messages after all retries exhausted
- **Impact**: Significantly improves reliability and handles API rate limits gracefully

### 🎨 Premium UI/UX
- **Responsive design** - Works seamlessly on desktop and mobile
- **Glassmorphism effects** - Modern, premium visual design
- **Smooth animations** - Polished transitions and micro-interactions
- **60/40 layout** - Optimized split between human-readable and JSON output
- **Horizontal scrolling** - JSON content never overflows boundaries
- **Impact**: Professional, production-ready user experience

### 🛡️ Robust Error Handling
- **Edge case coverage** - Handles missing comments, long bodies, invalid URLs
- **Text truncation** - Prevents API overload with smart content limits
- **HTTP status codes** - Proper 400/404/500 error responses
- **User feedback** - Clear, actionable error messages in the UI

### 🧪 Comprehensive Testing & CI/CD
- **96% code coverage** - 52 automated tests covering all services and endpoints
- **Multi-version testing** - Tests run on Python 3.10, 3.11, and 3.12
- **GitHub Actions CI/CD** - Automated testing on every push and pull request
- **Unit & integration tests** - Complete test suite with mocking for external APIs
- **Code quality checks** - Automated linting with Ruff on every commit
- **Impact**: Production-grade quality assurance with automated testing pipeline

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js (for package management)
- Google Gemini API key (required)
- Hugging Face API key (optional, for HF models)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ChandraMouli22/Github-issue-identifier-seedlings-.git
cd Github-issue-identifier-seedlings-
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file with required API keys
echo LLM_API_KEY=your_gemini_api_key_here > .env
echo HF_API_KEY=your_huggingface_api_key_here >> .env
```

5. **Run the application**
```bash
uvicorn main:app --reload --port 3000
```

6. **Open in browser**
```
http://localhost:3000
```

## 🧪 Testing

This project includes a comprehensive test suite with **96% code coverage** and **51 tests**.

### Run Tests

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=services --cov=main --cov-report=term-missing

# Run specific test categories
pytest tests/ -m unit          # Unit tests only
pytest tests/ -m integration   # Integration tests only
```

### Continuous Integration

Every push and pull request automatically runs:
- ✅ Tests across Python 3.10, 3.11, and 3.12
- ✅ Code coverage reporting
- ✅ Code quality checks with Ruff

View test results in the [Actions tab](https://github.com/ChandraMouli22/Github-issue-identifier-seedlings-/actions).

## 📁 Project Structure

```
project/
├── main.py                 # FastAPI application entry point
├── services/
│   ├── github_service.py   # GitHub API integration
│   ├── llm_service.py      # Google Gemini AI integration with retry logic
│   ├── cache_service.py    # Caching layer for analysis results
│   └── __init__.py
├── public/
│   ├── index.html          # Main HTML file
│   ├── styles.css          # Application styles
│   └── app.js              # Frontend JavaScript
├── cache/                  # Cached analysis results (auto-generated)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
└── .gitignore
```

## 🎨 UI Features

### Progress Indicator
- **Step 1**: Fetching Issue from GitHub
- **Step 2**: Analyzing with AI
- **Step 3**: Complete with results

### Theme Toggle
- Click the sun/moon icon in the navbar
- Automatically saves your preference
- Smooth transitions between themes

### Download Options
- **Markdown**: Formatted text file with analysis
- **PDF**: Print-based export via browser

### Code Editor
- macOS-style traffic lights (red, yellow, green)
- Syntax highlighting for JSON
- Custom scrollbars
- Monospace font (JetBrains Mono)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Required: Google Gemini API Key
LLM_API_KEY=your_google_gemini_api_key

# Optional: Hugging Face API Key (for DeepSeek, Llama models)
HF_API_KEY=your_huggingface_api_key

# Optional: GitHub Personal Access Token (for higher rate limits)
GITHUB_TOKEN=your_github_token_here
```

**Getting API Keys:**
- **Gemini API**: Get your free API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Hugging Face API**: Get your free API key at [Hugging Face Settings](https://huggingface.co/settings/tokens)
  - Required for DeepSeek R1 and Llama 3.1 models
  - **Note**: Llama 3.1 requires accepting the model license on Hugging Face
- **GitHub Token** (Optional): Generate at [GitHub Settings → Tokens](https://github.com/settings/tokens)
  - Increases rate limit from 60 to 5,000 requests/hour
  - Recommended for production use

### Available Models

**Google Gemini (LLM_API_KEY required):**
- `gemini-2.0-flash` - Latest generation, balanced performance
- `gemini-2.0-flash-lite` - Fastest, lightweight model
- `gemini-flash-lite-latest` - Previous stable generation

**Hugging Face (HF_API_KEY required):**
- `deepseek-ai/DeepSeek-R1` - Full 671B reasoning model (slower but powerful)
- `deepseek-ai/DeepSeek-R1-Distill-Llama-8B` - Fast reasoning model (recommended)
- `meta-llama/Meta-Llama-3.1-8B-Instruct` - Meta's latest (requires license acceptance)

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

These provide a live, interactive interface to test the API endpoints directly from your browser.

### Rate Limits & Caching

- **Gemini Free Tier**: ~15 requests/minute
- **Hugging Face Free Tier**: Varies by model, generally generous
- **Automatic Retry**: 3 attempts with exponential backoff (5s, 10s, 20s)
- **Model Switching**: Rate limit errors suggest switching to alternative models
- **Caching**: Previously analyzed issues return instantly from cache (per model)
- **GitHub API**: 60 requests/hour (unauthenticated) or 5,000/hour (with token)

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Modern Python web framework with auto-generated API docs
- Google Gemini AI - Fast, reliable AI analysis
- Hugging Face Inference API - Open-source models (DeepSeek, Llama)
- httpx - Async HTTP client for GitHub API integration
- File-based caching - MD5-hashed cache keys for instant results
- Exponential backoff retry logic - Resilient API error handling

**Frontend:**
- Vanilla JavaScript - No frameworks, lightweight and fast
- CSS3 - Modern styling with glassmorphism and animations
- HTML5 - Semantic markup with accessibility in mind

**Features:**
- Fully responsive design (mobile + desktop)
- Progressive enhancement
- Theme persistence with localStorage
- Real-time progress tracking
- Professional code editor UI

## 📝 API Endpoints

### `POST /api/analyze`

Analyzes a GitHub issue and returns AI-generated insights.

**Request Body:**
```json
{
  "repoUrl": "https://github.com/owner/repo",
  "issueNumber": "123",
  "model": "gemini-2.0-flash"  // Optional, defaults to gemini-2.0-flash
}
```

**Response:**
```json
{
  "summary": "Brief summary of the issue",
  "type": "bug",
  "priority_score": "4/5 – Blocks core functionality",
  "suggested_labels": ["bug", "high-priority", "backend"],
  "potential_impact": "Affects all users on mobile devices"
}
```

## 🎯 Usage Example

1. Enter a GitHub repository URL (e.g., `https://github.com/facebook/react`)
2. Enter an issue number (e.g., `1`)
3. Click "Generate Analysis"
4. View AI-generated insights in real-time with progress tracking
5. Download as Markdown or PDF if needed
6. **Try analyzing the same issue again** - it will return instantly from cache! ⚡

## ⚡ Performance Highlights

- **First request**: ~3-5 seconds (GitHub API + Gemini AI analysis)
- **Cached requests**: **< 100ms** (instant response from local cache)
- **Retry resilience**: Automatic recovery from temporary API failures
- **Rate limit protection**: Smart exponential backoff prevents quota exhaustion
- **Optimized payload**: Text truncation prevents API overload (2000 chars for body, 500 for comments)

## 🐛 Known Limitations

- Gemini free tier has rate limits (~15 requests/minute)
- Very large issues (100+ comments) are truncated to prevent API overload
- Cache is file-based (not distributed) - suitable for single-instance deployments

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.



## 🙏 Acknowledgments

- Google Gemini AI for powerful analysis capabilities
- Hugging Face for open-source model infrastructure
- GitHub API for issue data
- FastAPI for excellent Python web framework

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using Google Gemini AI & Hugging Face**
