# GitHub Issue Analyzer 🔍

AI-powered GitHub issue analysis tool that provides deep insights into repository issues using Google Gemini AI.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)

## ✨ Features

- **🤖 AI-Powered Analysis** - Uses Google Gemini AI to analyze GitHub issues
- **📊 Smart Insights** - Generates summary, priority score, and impact assessment
- **🏷️ Label Suggestions** - Recommends appropriate labels for better organization
- **📈 Progress Tracking** - Visual 3-step progress indicator (Fetching → Analyzing → Complete)
- **🌙 Dark/Light Mode** - Theme toggle with localStorage persistence
- **💾 Export Options** - Download analysis as Markdown or PDF
- **🖥️ Code Editor UI** - Professional editor-style JSON viewer with macOS chrome
- **⚡ Real-time Updates** - Live analysis with smooth animations

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for package management)
- Google Gemini API key

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
# Create .env file
echo LLM_API_KEY=your_gemini_api_key_here > .env
```

5. **Run the application**
```bash
uvicorn main:app --reload --port 3000
```

6. **Open in browser**
```
http://localhost:3000
```

## 📁 Project Structure

```
project/
├── main.py                 # FastAPI application entry point
├── services/
│   ├── github_service.py   # GitHub API integration
│   ├── llm_service.py      # Google Gemini AI integration
│   └── __init__.py
├── public/
│   ├── index.html          # Main HTML file
│   ├── styles.css          # Application styles
│   └── app.js              # Frontend JavaScript
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
LLM_API_KEY=your_google_gemini_api_key
```

### API Rate Limits

- Free tier: 20 requests/day for `gemini-flash-lite-latest`
- User-friendly error message when rate limit is reached
- Automatic retry suggestion

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- Google Gemini AI - AI analysis
- PyGithub - GitHub API integration

**Frontend:**
- Vanilla JavaScript - No frameworks
- CSS3 - Modern styling with glassmorphism
- HTML5 - Semantic markup

**Features:**
- Responsive design
- Progressive enhancement
- No external UI libraries

## 📝 API Endpoints

### `POST /api/analyze`

Analyzes a GitHub issue and returns AI-generated insights.

**Request Body:**
```json
{
  "repoUrl": "https://github.com/owner/repo",
  "issueNumber": "123"
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
4. View AI-generated insights
5. Download as Markdown or PDF if needed

## 🐛 Known Issues

- Google Generative AI package is deprecated (migration to `google.genai` recommended)
- Rate limits apply to free tier API keys

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.



## 🙏 Acknowledgments

- Google Gemini AI for powerful analysis capabilities
- GitHub API for issue data
- FastAPI for excellent Python web framework

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using Google Gemini AI**
