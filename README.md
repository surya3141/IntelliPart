# IntelliPart - Production-Ready AI Platform

## Overview
IntelliPart is a modular, enterprise-grade AI platform for automotive parts intelligence, supporting 200,000+ parts, 50+ attributes, and multi-platform AI (Gemini, OpenAI, Vertex). The architecture is organized into five main modules:

- **01_dataset_expansion**: Production dataset generation (200K+ parts, 50+ attributes, images, drawings)
- **02_deep_analysis**: Advanced analytics engine (predictive, BI, dashboards)
- **03_conversational_chat**: Unified conversational AI (Gemini LLM, OpenAI, Vertex, web UI)
- **04_hackathon_demo**: Modern demo and presentation platform
- **05_new_features**: Innovation lab for rapid prototyping

## Key Features
- Unified dataset loader for all modules
- Modular, extensible codebase
- Gemini LLM integration for deep conversational UI
- Robust error handling and session management
- Modern web UI with LLM/classic toggle

## Project Structure
```
IntelliPart/
├── 01_dataset_expansion/    # Production dataset generation (200K+ parts)
├── 02_deep_analysis/        # Advanced analytics engine
├── 03_conversational_chat/  # AI conversational interface  
├── 04_hackathon_demo/       # Demo and presentation platform
├── 05_new_features/         # Innovation lab
├── docs/                    # Documentation and presentations
├── Archive_OLD_FILES/       # Legacy files and backups
├── launch_demo.py           # Quick launch script
├── production_demo.py       # Production system demo
├── README.md               # This file
└── requirements.txt        # Core dependencies

```

## Quick Start
1. **Easy Launch**: `python launch_demo.py` (launches web interface automatically)
2. **Manual Launch**: 
   - Install: `pip install -r requirements.txt`
   - Generate dataset: `cd 01_dataset_expansion && python main.py`
   - Launch app: `cd 03_conversational_chat && python conversational_web_app.py`
   - Access: [http://localhost:5004](http://localhost:5004)

## Architecture Flow
```
01_dataset_expansion → 02_deep_analysis → 03_conversational_chat
                        ↘             ↗
                         04_hackathon_demo ← 05_new_features
```

## Documentation
- **User Guide**: `docs/USER_GUIDE.md`
- **Solution Document**: `docs/COMPREHENSIVE_SOLUTION_DOCUMENT.md`
- **Demo Guide**: `docs/HACKATHON_DEMO_GUIDE.md`
- **Presentations**: `docs/*.pdf`, `docs/*.pptx`

---
For module-specific details, see each module's README.