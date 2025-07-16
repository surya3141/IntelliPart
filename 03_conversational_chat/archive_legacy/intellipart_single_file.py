"""
IntelliPart - Single File Version with Gemini 2.0 Pro
=====================================

This is a complete, self-contained version of IntelliPart that includes:
- Backend Flask application
- Embedded HTML frontend 
- Gemini 2.0 Pro AI integration
- Enhanced search capabilities

Just run this single file and access http://127.0.0.1:5002

Requirements:
- pip install flask google-generativeai numpy rapidfuzz
- Valid Gemini API key or service account JSON
"""

from flask import Flask, request, jsonify
import json
import time
import os
import re
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Google AI imports for Gemini 2.0 Pro
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    print("❌ Please install: pip install google-generativeai")
    genai = None

try:
    from rapidfuzz import process as fuzzy_process
except ImportError:
    print("⚠️ rapidfuzz not available, suggestions will be limited")
    fuzzy_process = None

app = Flask(__name__)
app.secret_key = 'intellipart_single_file_2024'

# Configuration
GEMINI_JSON_PATH = "D://OneDrive - Mahindra & Mahindra Ltd//Desktop//POC//Gemini//gemini_v1//scripts//mdp-ad-parts-dev-api-json-key.json"
GEMINI_MODEL_NAME = "gemini-2.0-flash-exp"

# Global variables
gemini_model = None
all_parts = []

def initialize_gemini():
    """Initialize Gemini 2.0 Pro"""
    global gemini_model
    try:
        if not genai:
            print("❌ google-generativeai not installed")
            return None
            
        # Try API key first (easier for development)
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            print("✅ Gemini configured with API key")
        elif os.path.exists(GEMINI_JSON_PATH):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GEMINI_JSON_PATH
            print("✅ Gemini configured with service account")
        else:
            print("❌ No Gemini credentials found")
            return None
            
        # Initialize model
        gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        
        # Test the model
        test_response = gemini_model.generate_content("Hello, respond with 'Gemini ready'")
        if test_response.candidates and test_response.candidates[0].content:
            print("✅ Gemini 2.0 Pro is ready!")
            return gemini_model
        else:
            print("❌ Gemini test failed")
            return None
            
    except Exception as e:
        print(f"❌ Failed to initialize Gemini: {e}")
        return None

def call_gemini(prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
    """Call Gemini 2.0 Pro with error handling"""
    try:
        if not gemini_model:
            return "[Gemini not available]"
            
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            top_p=0.8,
            top_k=40
        )
        
        response = gemini_model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if response.candidates and response.candidates[0].content:
            return response.candidates[0].content.parts[0].text
        else:
            return "[No response generated]"
            
    except Exception as e:
        return f"[Gemini error: {str(e)[:100]}...]"

def load_sample_data():
    """Load sample automotive parts data"""
    return [
        {
            "part_number": "TH001",
            "part_name": "Mahindra Thar Brake Pad Set",
            "system_name": "Brake System",
            "manufacturer": "Mahindra",
            "cost": 2500,
            "stock": 25,
            "condition": "New",
            "vehicle_compatibility": "Thar",
            "part_description": "High-performance ceramic brake pads for Mahindra Thar"
        },
        {
            "part_number": "MZ002",
            "part_name": "Marazzo Engine Air Filter",
            "system_name": "Engine System",
            "manufacturer": "Mahindra",
            "cost": 800,
            "stock": 50,
            "condition": "New",
            "vehicle_compatibility": "Marazzo",
            "part_description": "Premium air filter for optimal engine performance"
        },
        {
            "part_number": "TV003",
            "part_name": "TUV300 Radiator Assembly",
            "system_name": "Cooling System",
            "manufacturer": "Mahindra",
            "cost": 8500,
            "stock": 15,
            "condition": "New", 
            "vehicle_compatibility": "TUV300",
            "part_description": "Complete radiator assembly with enhanced cooling capacity"
        },
        {
            "part_number": "TH004",
            "part_name": "Thar LED Headlight Assembly",
            "system_name": "Electrical System",
            "manufacturer": "Mahindra",
            "cost": 12000,
            "stock": 8,
            "condition": "New",
            "vehicle_compatibility": "Thar",
            "part_description": "Modern LED headlight with DRL for enhanced visibility"
        },
        {
            "part_number": "SC005",
            "part_name": "Scorpio Shock Absorber",
            "system_name": "Suspension System", 
            "manufacturer": "Mahindra",
            "cost": 4500,
            "stock": 20,
            "condition": "New",
            "vehicle_compatibility": "Scorpio",
            "part_description": "Heavy-duty shock absorber for smooth ride quality"
        }
    ]

def load_parts_data():
    """Try to load real data, fallback to sample data"""
    global all_parts
    
    # Try to load from existing dataset
    dataset_paths = [
        Path(__file__).parent.parent / "synthetic_car_parts_500.jsonl",
        Path(__file__).parent / "synthetic_car_parts_500.jsonl",
        Path(__file__).parent.parent / "data" / "car_parts_dataset.jsonl"
    ]
    
    for path in dataset_paths:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            all_parts.append(json.loads(line.strip()))
                print(f"✅ Loaded {len(all_parts)} parts from {path}")
                return all_parts
            except Exception as e:
                print(f"Failed to load {path}: {e}")
    
    # Fallback to sample data
    all_parts = load_sample_data()
    print(f"✅ Using sample data: {len(all_parts)} parts")
    return all_parts

class SimpleSearchEngine:
    """Simple but effective search engine"""
    
    def __init__(self, parts):
        self.parts = parts
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search parts with scoring"""
        if not query.strip():
            return []
            
        query_terms = query.lower().split()
        results = []
        
        for part in self.parts:
            score = 0
            part_text = " ".join(str(v) for v in part.values()).lower()
            
            for term in query_terms:
                if term in part_text:
                    # Higher score for matches in important fields
                    if term in part.get('part_name', '').lower():
                        score += 3
                    elif term in part.get('vehicle_compatibility', '').lower():
                        score += 2
                    elif term in part.get('system_name', '').lower():
                        score += 2
                    else:
                        score += 1
            
            if score > 0:
                part_copy = part.copy()
                part_copy['similarity'] = min(score / len(query_terms), 1.0)
                results.append(part_copy)
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_k]

# Initialize components
print("🚀 Initializing IntelliPart Single File Version...")
gemini_model = initialize_gemini()
parts_data = load_parts_data()
search_engine = SimpleSearchEngine(parts_data)
print("✅ Ready to serve!")

@app.route('/')
def home():
    """Serve embedded HTML interface"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IntelliPart - Single File Edition</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container {
            max-width: 1000px; margin: 0 auto;
            background: rgba(255,255,255,0.95); border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
            color: white; padding: 30px; text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; margin-bottom: 10px; }
        .badge {
            background: rgba(255,255,255,0.2); padding: 5px 15px;
            border-radius: 20px; display: inline-block; font-size: 0.9em;
        }
        .chat-area { height: 60vh; overflow-y: auto; padding: 20px; background: #f8f9fa; }
        .message { margin-bottom: 20px; display: flex; gap: 10px; }
        .message.user { flex-direction: row-reverse; }
        .avatar {
            width: 40px; height: 40px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: bold;
        }
        .user .avatar { background: #667eea; }
        .assistant .avatar { background: #ff6b6b; }
        .content {
            max-width: 70%; padding: 15px 20px; border-radius: 18px; line-height: 1.5;
        }
        .user .content { background: #667eea; color: white; border-bottom-right-radius: 5px; }
        .assistant .content { background: white; border: 1px solid #ddd; border-bottom-left-radius: 5px; }
        .input-area { padding: 20px; background: white; border-top: 1px solid #ddd; }
        .input-container { display: flex; gap: 10px; }
        .search-input {
            flex: 1; padding: 15px 20px; border: 2px solid #ddd;
            border-radius: 25px; font-size: 16px; outline: none;
        }
        .search-input:focus { border-color: #667eea; }
        .send-btn {
            padding: 15px 25px; background: #667eea; color: white;
            border: none; border-radius: 25px; cursor: pointer; font-weight: bold;
        }
        .send-btn:hover { background: #5a67d8; }
        .send-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .result-item {
            background: #f8f9fa; border: 1px solid #e9ecef;
            border-radius: 10px; padding: 15px; margin: 10px 0;
        }
        .result-title { font-weight: 600; color: #2c3e50; font-size: 1.1em; margin-bottom: 5px; }
        .result-details { color: #6c757d; font-size: 0.9em; }
        .result-price { color: #27ae60; font-weight: 600; float: right; }
        .welcome { text-align: center; padding: 40px 20px; color: #6c757d; }
        .welcome h3 { color: #2c3e50; margin-bottom: 15px; }
        .status { padding: 10px 20px; background: #e8f4f8; border-top: 1px solid #ddd; font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 IntelliPart</h1>
            <div class="subtitle">Single File Edition with Gemini 2.0 Pro</div>
            <div class="badge">🧠 AI-Powered Assistant</div>
        </div>
        
        <div class="chat-area" id="chatArea">
            <div class="welcome">
                <h3>Welcome to IntelliPart! 🚀</h3>
                <p>I'm your AI assistant for Mahindra automotive parts. Ask me about parts, get recommendations, or search by vehicle model.</p>
                <p><strong>Try:</strong> "Show me brake parts for Thar" or "I need a radiator for TUV300"</p>
            </div>
        </div>
        
        <div class="input-area">
            <div class="input-container">
                <input type="text" id="searchInput" class="search-input" 
                       placeholder="Ask about automotive parts..." autocomplete="off">
                <button id="sendBtn" class="send-btn">Send</button>
            </div>
        </div>
        
        <div class="status">
            <span>🤖 Gemini 2.0 Pro Ready</span> | 
            <span>📦 ''' + str(len(parts_data)) + ''' parts loaded</span> |
            <span>⚡ Last search: <span id="lastTime">-</span></span>
        </div>
    </div>

    <script>
        const chatArea = document.getElementById('chatArea');
        const searchInput = document.getElementById('searchInput');
        const sendBtn = document.getElementById('sendBtn');
        const lastTime = document.getElementById('lastTime');

        function addMessage(content, isUser = false) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            
            msgDiv.innerHTML = `
                <div class="avatar">${isUser ? 'U' : 'AI'}</div>
                <div class="content">${content}</div>
            `;
            
            // Remove welcome message if present
            const welcome = chatArea.querySelector('.welcome');
            if (welcome) welcome.remove();
            
            chatArea.appendChild(msgDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        function addTyping() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message assistant';
            typingDiv.innerHTML = `
                <div class="avatar">AI</div>
                <div class="content">🤔 Thinking...</div>
            `;
            chatArea.appendChild(typingDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
            return typingDiv;
        }

        async function sendMessage() {
            const query = searchInput.value.trim();
            if (!query) return;

            sendBtn.disabled = true;
            addMessage(query, true);
            const typing = addTyping();
            searchInput.value = '';

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });

                const data = await response.json();
                typing.remove();

                if (data.success) {
                    let content = data.ai_response || 'Found some results for you!';
                    
                    if (data.results && data.results.length > 0) {
                        content += '<div style="margin-top: 15px;">';
                        data.results.forEach(part => {
                            content += `
                                <div class="result-item">
                                    <div class="result-title">
                                        ${part.part_name || 'Unknown Part'}
                                        <span class="result-price">₹${part.cost || 'N/A'}</span>
                                    </div>
                                    <div class="result-details">
                                        <strong>Vehicle:</strong> ${part.vehicle_compatibility || 'N/A'} | 
                                        <strong>System:</strong> ${part.system_name || 'N/A'} | 
                                        <strong>Stock:</strong> ${part.stock || 0}
                                    </div>
                                </div>
                            `;
                        });
                        content += '</div>';
                    }
                    
                    addMessage(content);
                    lastTime.textContent = `${data.search_time_ms || 0}ms`;
                } else {
                    addMessage(data.error || 'Sorry, something went wrong.');
                }
            } catch (error) {
                typing.remove();
                addMessage('Sorry, I encountered a technical issue. Please try again.');
            }

            sendBtn.disabled = false;
            searchInput.focus();
        }

        sendBtn.addEventListener('click', sendMessage);
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        // Focus input on load
        searchInput.focus();
    </script>
</body>
</html>'''

@app.route('/api/search', methods=['POST'])
def api_search():
    """Enhanced search API with Gemini intelligence"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query required'}), 400

        start_time = time.time()
        
        # Perform search
        results = search_engine.search(query, top_k=5)
        search_time_ms = round((time.time() - start_time) * 1000, 2)
        
        # Generate AI response using Gemini
        ai_response = generate_ai_response(query, results)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'ai_response': ai_response,
            'search_time_ms': search_time_ms,
            'result_count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_ai_response(query: str, results: List[Dict]) -> str:
    """Generate intelligent response using Gemini 2.0 Pro"""
    try:
        if not gemini_model:
            if results:
                return f"Found {len(results)} results for '{query}'. Here are the best matches:"
            else:
                return f"No results found for '{query}'. Try different keywords or check spelling."
        
        # Prepare context for Gemini
        context = ""
        if results:
            context = "\\n".join([
                f"- {part.get('part_name', 'Unknown')} (₹{part.get('cost', 'N/A')}) for {part.get('vehicle_compatibility', 'Unknown vehicle')}"
                for part in results[:3]
            ])
        
        prompt = f"""
You are an expert automotive parts assistant for Mahindra vehicles.

User Query: "{query}"
Search Results: {len(results)} parts found
Top Results:
{context or "No results found"}

Generate a helpful, conversational response (max 100 words) that:
1. Acknowledges their query naturally
2. Summarizes what was found
3. Highlights the best option if available
4. Uses automotive expertise
5. Is friendly and professional

Response:"""
        
        response = call_gemini(prompt, max_tokens=200, temperature=0.7)
        
        # Clean up response
        if response and not response.startswith('['):
            return response.strip()
        else:
            # Fallback response
            if results:
                return f"Great! I found {len(results)} automotive parts matching '{query}'. The top result is {results[0].get('part_name', 'a suitable part')} for ₹{results[0].get('cost', 'N/A')}. 🔧"
            else:
                return f"I couldn't find exact matches for '{query}'. Try searching with different keywords like vehicle model (Thar, Marazzo) or part type (brake, engine, radiator). 🤔"
        
    except Exception as e:
        print(f"AI response error: {e}")
        if results:
            return f"Found {len(results)} results for '{query}' 🔍"
        else:
            return f"No results found for '{query}'. Try different keywords! 🤔"

if __name__ == "__main__":
    print("\\n🚀 IntelliPart Single File Edition Starting...")
    print("🌐 Access your app at: http://127.0.0.1:5002")
    print("✨ Features: Gemini 2.0 Pro AI + Smart Search + Single File Deployment")
    print("-" * 60)
    app.run(debug=True, host='0.0.0.0', port=5002)
