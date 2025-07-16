# 03_conversational_chat: Unified Conversational AI

## Purpose
Production-grade conversational AI for automotive parts, with Gemini LLM, OpenAI, and Vertex integration. Provides a modern web UI and API for natural language search, recommendations, and analytics.

## Project Structure
```
03_conversational_chat/
├── conversational_web_app.py    # Main Flask application (production-ready)
├── conversational_search.py     # Core search engine and AI logic
├── main.py                      # Module entry point
├── templates/                   # Web UI templates
│   └── conversational_search.html
├── data/                        # Local datasets
├── docs/                        # Module documentation
├── archive_legacy/              # Legacy files and old versions
├── README.md                    # This file
└── requirements.txt             # Module dependencies
```

## Features
- **Advanced AI Search**: Gemini LLM-powered conversational engine with classic/LLM toggle
- **Unified Dataset Integration**: Loads data from `../01_dataset_expansion/production_dataset/datasets/`
- **Modern Flask Web UI**: Responsive interface with intelligent search suggestions
- **Robust Error Handling**: Corporate network support and fallback mechanisms
- **Multiple AI Backends**: Supports Gemini, OpenAI, Vertex AI, and Ollama
- **Session Management**: Maintains conversation context and history

## Quick Start
```bash
cd 03_conversational_chat
pip install -r requirements.txt
python conversational_web_app.py
```
- Access at [http://localhost:5004](http://localhost:5004)

## API Endpoints
- `/api/search` - Main conversational search
- `/api/intelligent-search` - AI-enhanced search with reusability scoring
- `/api/rag-answer` - Retrieval-Augmented Generation responses
- `/api/assistant-intro` - Dynamic assistant introduction
- `/api/quick-insights` - Dataset analytics and insights

## Integration
- **Standalone Operation**: Can run independently with local datasets
- **Full Stack Integration**: Works with all IntelliPart modules
- **Corporate Network Support**: Handles SSL and proxy configurations
- **Fallback Mechanisms**: Gracefully degrades when AI services unavailable

## Development
- **Main Application**: `conversational_web_app.py` - Flask backend with all API endpoints
- **Search Engine**: `conversational_search.py` - Core AI and search logic
- **Frontend**: `templates/conversational_search.html` - Modern responsive UI
- **Configuration**: Environment variables for API keys and service endpoints

## Legacy Files
All legacy files, backup versions, and deprecated code moved to `archive_legacy/` folder for reference.

---
*Updated: July 16, 2025 - Cleaned and restructured for production use*
