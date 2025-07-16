# IntelliPart File Organization Plan
# Based on Core Requirements: AI-powered chat-based engineering conversation for part reusability

## 🎯 CORE ESSENTIAL FILES (Keep Active)

### 1. AI Chat & Conversational Interface
- conversational_search.py         # Main AI conversational engine
- conversational_web_app.py        # Web interface for engineers
- lightweight_ai_search.py         # AI similarity search
- semantic_search.py               # Advanced semantic understanding

### 2. Core Data & Models
- data/                           # Part database
- tfidf_embeddings.pkl            # AI models
- enhanced_tfidf_embeddings.pkl   # Enhanced AI models
- requirements.txt                # Dependencies

### 3. Templates & UI
- templates/                      # Web interface templates

### 4. Documentation (Core)
- README.md                       # Main documentation
- AI_INTEGRATION_OVERVIEW.md      # AI architecture guide

## 🗂️ ARCHIVE CANDIDATES (Move to archived/)

### Demo & Test Files
- demo_ai_integration.py
- demo_enhanced.py
- demo_instant_dashboard.py
- hackathon_demo.py
- hackathon_web_demo.py
- test_fast_analytics.py

### Alternative/Redundant Search Engines
- enhanced_intellipart_app.py     # Redundant - use conversational_search.py
- simple_search.py               # Basic search - not needed
- enhanced_search.py             # Redundant functionality
- ultimate_search_app.py         # Demo app
- web_app.py                     # Basic web app - use conversational_web_app.py

### Analytics & Forecasting (Not Core to Chat Interface)
- advanced_analytics.py
- analytics_dashboard.py
- ai_demand_forecasting.py
- advanced_analytics_report.json

### Integration & Deployment
- enterprise_integration.py
- enterprise_integration_hub.py
- mobile_api.py                   # Keep if mobile needed
- elasticsearch_ingest.py
- performance_optimizer.py

### Data Generation & Utilities
- generate_car_parts_dataset.py
- main.py                        # Generic main - use conversational_web_app.py

### Documentation (Non-Essential)
- COMPLETE_SEARCH_ARCHITECTURE.md
- FAST_OPTIMIZATION_COMPLETE.md
- FINAL_STATUS_REPORT.md
- HACKATHON_PRESENTATION_SCRIPT.md
- OPTIMIZATION_SUMMARY.py
- deployment_guide.md
- strategic_roadmap.md
- alignment.md
- README_Enhanced.md

### Deployment Files
- deploy.sh
- quick_deploy.py
- docker-compose.yml
- Dockerfile
- gunicorn.conf.py
- .env.production

## 🎯 FINAL STRUCTURE (Post-Archive)

Active Directory:
├── conversational_search.py      # Core AI chat engine
├── conversational_web_app.py     # Engineer interface
├── lightweight_ai_search.py      # AI search backend
├── semantic_search.py            # Semantic understanding
├── data/                         # Part database
├── templates/                    # UI templates
├── requirements.txt              # Dependencies
├── tfidf_embeddings.pkl          # AI models
├── enhanced_tfidf_embeddings.pkl
├── README.md                     # Core documentation
├── AI_INTEGRATION_OVERVIEW.md    # AI guide
└── archived/                     # All other files

This focuses the project on the core requirement:
"AI-powered chat-based understanding for engineer conversation about part reusability"
