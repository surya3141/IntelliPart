#!/usr/bin/env python3
"""
Production Conversational AI - Main Entry Point
Advanced AI assistant with Gemini, OpenAI, and Invertex AI integration
"""

import sys
import os
from pathlib import Path
from dataset_loader import load_all_parts


# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    """Main function for production conversational AI"""
    print("🚀 IntelliPart Production Conversational AI")
    print("=" * 60)
    print("🤖 AI-Powered Assistant • 🔍 Smart Search • 🎯 Production Ready")
    print()
    
    # Available AI platforms
    ai_platforms = [
        {
            "name": "Production AI Assistant",
            "module": "production_ai_assistant",
            "description": "Multi-platform AI (Gemini, OpenAI, Invertex)",
            "features": ["Production Error Handling", "Context Management", "Visual Recognition"],
            "recommended": True
        },
        {
            "name": "Conversational Web App",
            "module": "conversational_web_app",
            "description": "Web-based conversational interface",
            "features": ["Web UI", "Real-time Chat", "Search Integration"],
            "recommended": False
        },
        {
            "name": "Lightweight AI Search",
            "module": "lightweight_ai_search",
            "description": "Fast TF-IDF based search",
            "features": ["Offline Search", "Fast Response", "No API Required"],
            "recommended": False
        }
    ]
    
    print("Available AI Platforms:")
    for i, platform in enumerate(ai_platforms, 1):
        status = "🌟 RECOMMENDED" if platform["recommended"] else "🔧 Available"
        features = " • ".join(platform["features"][:2])
        print(f"{i}. {platform['name']}")
        print(f"   {platform['description']} {status}")
        print(f"   Features: {features}")
        print()
    
    choice = input("Select AI platform (1-3) or press Enter for recommended: ").strip()
    
    if not choice:
        choice = "1"  # Default to production AI assistant
    
    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(ai_platforms):
            selected = ai_platforms[choice_idx]
        else:
            selected = ai_platforms[0]  # Default to first option
    except ValueError:
        selected = ai_platforms[0]  # Default to first option
    
    print(f"\n🔧 Launching {selected['name']}...")
    
    try:
        if selected["module"] == "production_ai_assistant":
            print("🤖 Starting Production AI Assistant...")
            run_production_ai_assistant()
        elif selected["module"] == "conversational_web_app":
            print("🌐 Starting Conversational Web App...")
            from conversational_web_app import app
            print("🌐 Access the app at http://127.0.0.1:5000")
            app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
        elif selected["module"] == "lightweight_ai_search":
            print("⚡ Starting Lightweight AI Search...")
            from lightweight_ai_search import interactive_ai_search as run_lightweight_search
            run_lightweight_search()
        else:
            print("🔄 Falling back to web app...")
            from conversational_web_app import app
            print("🌐 Access the app at http://127.0.0.1:5000")
            app.run(debug=True, use_reloader=False)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔄 Attempting fallback to web app...")
        try:
            from conversational_web_app import app
            print("🌐 Starting fallback web app at http://127.0.0.1:5000")
            app.run(debug=True, use_reloader=False)
        except Exception as fallback_error:
            print(f"❌ Fallback failed: {fallback_error}")
            print("📝 Manual setup required - check requirements.txt")
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        print("🔄 Trying alternative launch method...")
        try:
            from conversational_web_app import app
            print("🌐 Starting alternative web app at http://127.0.0.1:5000")
            app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
        except Exception as alt_error:
            print(f"❌ All launch methods failed: {alt_error}")

def run_production_ai_assistant():
    """Run the production AI assistant with interactive CLI"""
    try:
        from production_ai_assistant import ProductionAIOrchestrator, QueryContext
        
        print("\n🤖 Production AI Assistant Ready!")
        print("=" * 50)
        print("Supported Platforms:")
        print("  • 🔮 Gemini Pro (Google)")
        print("  • 🧠 OpenAI GPT-4")
        print("  • 🎯 Invertex AI (Vertex)")
        print()
        print("Commands:")
        print("  • Type your question about automotive parts")
        print("  • 'exit' or 'quit' to stop")
        print("  • 'help' for more options")
        print()
        
        # Initialize AI orchestrator
        orchestrator = ProductionAIOrchestrator()
        
        # Load all parts from the base dataset directory
        all_parts = load_all_parts()
        
        # Interactive conversation loop
        session_id = "cli_session_001"
        user_id = "production_user"
        
        while True:
            try:
                user_input = input("🔍 Ask about parts: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'stop']:
                    print("👋 Goodbye! Thanks for using IntelliPart AI!")
                    break
                
                if user_input.lower() == 'help':
                    print("\n📋 Help:")
                    print("  • Search: 'Find brake pads for XUV700'")
                    print("  • Technical: 'What are the specs for part MP-001?'")
                    print("  • Compare: 'Compare engine parts from different suppliers'")
                    print("  • Analytics: 'Show me inventory insights'")
                    print()
                    continue
                
                if not user_input:
                    continue
                
                # Create query context
                context = QueryContext(
                    user_id=user_id,
                    session_id=session_id,
                    query_type="part_search",
                    priority="normal",
                    department="technical",
                    previous_queries=[]
                )
                
                # Process query
                print("🤖 Processing...")
                response = orchestrator.process_query(user_input, context)
                
                # Display response
                print(f"\n💡 {response.content}")
                
                if response.suggestions:
                    print(f"\n📝 Suggestions:")
                    for suggestion in response.suggestions[:3]:
                        print(f"  • {suggestion}")
                
                print(f"\n⚡ Response time: {response.processing_time:.2f}s")
                print(f"🎯 Confidence: {response.confidence:.0%}")
                print(f"🔧 Source: {response.source}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("🔄 Try rephrasing your question or type 'help'\n")
    
    except ImportError:
        print("❌ Production AI Assistant not available")
        print("📋 Install requirements: pip install -r requirements.txt")
        print("🔧 Or use: python -m pip install google-generativeai openai")
    except Exception as e:
        print(f"❌ AI Assistant startup failed: {e}")

if __name__ == "__main__":
    main()
