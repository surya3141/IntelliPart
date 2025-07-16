"""
IntelliPart - Complete Self-Contained Version with Gemini 2.0 Pro
================================================================

This version includes everything in one file to avoid template issues:
- Full Flask backend with Gemini 2.0 Pro
- Embedded HTML frontend
- Complete parts search functionality
- AI-powered conversational interface

No external template dependencies!
"""

from flask import Flask, request, jsonify
import json
import time
import os
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

app = Flask(__name__)
app.secret_key = 'intellipart_complete_2024'

# Gemini 2.0 Pro Configuration
GEMINI_JSON_PATH = "D:/OneDrive - Mahindra & Mahindra Ltd/Desktop/POC/Gemini/gemini_v1/scripts/mdp-ad-parts-dev-api-json-key.json"
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
            
        # Check JSON file
        if not os.path.exists(GEMINI_JSON_PATH):
            print(f"⚠️ Gemini JSON key not found at: {GEMINI_JSON_PATH}")
            return None
            
        # Set up credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GEMINI_JSON_PATH
        
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

def load_parts_data():
    """Load parts data from available datasets"""
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
    all_parts = [
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
    print(f"✅ Using sample data: {len(all_parts)} parts")
    return all_parts

class GeminiSearchEngine:
    """Enhanced search engine with Gemini AI"""
    
    def __init__(self, parts):
        self.parts = parts
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search parts with AI enhancement"""
        if not query.strip():
            return []
            
        # Enhanced query processing with Gemini
        enhanced_query = self.enhance_query_with_gemini(query)
        search_terms = enhanced_query.get('search_terms', query.split())
        
        results = []
        for part in self.parts:
            score = 0
            part_text = " ".join(str(v) for v in part.values()).lower()
            
            for term in search_terms:
                if term.lower() in part_text:
                    # Higher score for matches in important fields
                    if term.lower() in part.get('part_name', '').lower():
                        score += 3
                    elif term.lower() in part.get('vehicle_compatibility', '').lower():
                        score += 2
                    elif term.lower() in part.get('system_name', '').lower():
                        score += 2
                    else:
                        score += 1
            
            if score > 0:
                part_copy = part.copy()
                part_copy['similarity'] = min(score / len(search_terms), 1.0)
                results.append(part_copy)
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_k]
    
    def enhance_query_with_gemini(self, query: str) -> Dict[str, Any]:
        """Use Gemini to enhance the search query"""
        try:
            enhancement_prompt = f"""
Analyze this automotive parts query: "{query}"

Return a JSON response:
{{
    "enhanced_query": "improved search terms",
    "search_terms": ["keyword1", "keyword2", "keyword3"],
    "part_type": "type of part",
    "vehicle_model": "vehicle mentioned"
}}

Focus on Mahindra vehicles (Thar, Marazzo, TUV300, Scorpio) and automotive parts.
"""
            
            response = call_gemini(enhancement_prompt, max_tokens=300, temperature=0.3)
            
            try:
                enhanced_data = json.loads(response)
                return enhanced_data
            except:
                return {
                    "enhanced_query": query,
                    "search_terms": query.split(),
                    "part_type": "unknown",
                    "vehicle_model": "unknown"
                }
                
        except Exception as e:
            return {
                "enhanced_query": query,
                "search_terms": query.split(),
                "part_type": "unknown",
                "vehicle_model": "unknown"
            }

# Initialize components
print("🚀 Initializing IntelliPart Complete Version...")
gemini_model = initialize_gemini()
parts_data = load_parts_data()
search_engine = GeminiSearchEngine(parts_data)
print("✅ All systems ready!")

@app.route('/')
def home():
    """Serve the complete embedded application"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IntelliPart - Complete AI Assistant</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px;
        }
        .container {
            background: rgba(255, 255, 255, 0.95); border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1); width: 100%; max-width: 1200px;
            height: 85vh; display: flex; flex-direction: column; overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #ff6b6b, #4ecdc4); color: white;
            padding: 25px; text-align: center; position: relative;
        }
        .header h1 { font-size: 2.8em; margin-bottom: 10px; font-weight: 700; }
        .subtitle { opacity: 0.9; font-size: 1.1em; margin-bottom: 15px; }
        .features { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }
        .feature-badge {
            background: rgba(255, 255, 255, 0.2); padding: 8px 16px;
            border-radius: 20px; font-size: 0.9em; display: flex; align-items: center; gap: 5px;
        }
        .chat-container { flex: 1; display: flex; flex-direction: column; }
        .chat-area { flex: 1; overflow-y: auto; padding: 25px; background: #f8f9fa; }
        .message { margin-bottom: 20px; display: flex; gap: 15px; animation: fadeIn 0.3s ease; }
        .message.user { flex-direction: row-reverse; }
        .avatar {
            width: 45px; height: 45px; border-radius: 50%; display: flex;
            align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 1.1em;
        }
        .user .avatar { background: linear-gradient(135deg, #667eea, #764ba2); }
        .assistant .avatar { background: linear-gradient(135deg, #ff6b6b, #4ecdc4); }
        .content {
            max-width: 75%; padding: 18px 22px; border-radius: 20px; line-height: 1.6; font-size: 1em;
        }
        .user .content { 
            background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
            border-bottom-right-radius: 8px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .assistant .content { 
            background: white; border: 1px solid #e1e5e9; border-bottom-left-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .input-area { padding: 25px; background: white; border-top: 1px solid #e1e5e9; }
        .input-container { display: flex; gap: 15px; align-items: center; }
        .search-input {
            flex: 1; padding: 18px 25px; border: 2px solid #e1e5e9; border-radius: 30px;
            font-size: 16px; outline: none; transition: all 0.3s ease;
        }
        .search-input:focus { border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
        .send-btn {
            padding: 18px 30px; background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; border: none; border-radius: 30px; cursor: pointer;
            font-weight: 600; font-size: 16px; transition: all 0.3s ease;
        }
        .send-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3); }
        .send-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .result-item {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef); border: 1px solid #dee2e6;
            border-radius: 15px; padding: 20px; margin: 15px 0; transition: all 0.3s ease;
        }
        .result-item:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
        .result-title { 
            font-weight: 700; color: #2c3e50; font-size: 1.2em; margin-bottom: 8px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .result-price { color: #27ae60; font-weight: 700; font-size: 1.1em; }
        .result-details { color: #6c757d; font-size: 0.95em; line-height: 1.5; }
        .result-meta { 
            display: flex; gap: 15px; margin-top: 10px; font-size: 0.9em;
            color: #495057; flex-wrap: wrap;
        }
        .meta-item { display: flex; align-items: center; gap: 5px; }
        .welcome { text-align: center; padding: 50px 30px; color: #6c757d; }
        .welcome h3 { color: #2c3e50; margin-bottom: 20px; font-size: 1.5em; }
        .welcome p { margin-bottom: 15px; font-size: 1.1em; line-height: 1.6; }
        .suggestions { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-top: 20px; }
        .suggestion-chip {
            background: #e3f2fd; color: #1976d2; padding: 8px 16px; border-radius: 20px;
            cursor: pointer; font-size: 0.9em; transition: all 0.3s ease;
        }
        .suggestion-chip:hover { background: #1976d2; color: white; transform: translateY(-1px); }
        .status-bar { 
            padding: 15px 25px; background: linear-gradient(135deg, #e8f4f8, #f1f8ff);
            border-top: 1px solid #dee2e6; font-size: 0.9em; color: #495057;
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
        }
        .status-left { display: flex; gap: 20px; align-items: center; }
        .status-item { display: flex; align-items: center; gap: 5px; }
        .typing { opacity: 0.7; font-style: italic; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 768px) {
            .container { height: 95vh; margin: 10px; }
            .header h1 { font-size: 2.2em; }
            .features { gap: 10px; }
            .feature-badge { padding: 6px 12px; font-size: 0.8em; }
            .content { max-width: 85%; padding: 15px 18px; }
            .input-container { flex-direction: column; gap: 12px; }
            .search-input, .send-btn { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-cog"></i> IntelliPart</h1>
            <div class="subtitle">Complete AI Assistant with Gemini 2.0 Pro</div>
            <div class="features">
                <div class="feature-badge"><i class="fas fa-brain"></i> AI-Powered</div>
                <div class="feature-badge"><i class="fas fa-search"></i> Smart Search</div>
                <div class="feature-badge"><i class="fas fa-car"></i> Mahindra Parts</div>
                <div class="feature-badge"><i class="fas fa-comments"></i> Conversational</div>
            </div>
        </div>
        
        <div class="chat-container">
            <div class="chat-area" id="chatArea">
                <div class="welcome">
                    <h3><i class="fas fa-robot"></i> Welcome to IntelliPart! 🚀</h3>
                    <p>I'm your AI-powered assistant for Mahindra automotive parts. I can help you find exactly what you need using advanced AI understanding.</p>
                    <p><strong>Try asking me:</strong></p>
                    <div class="suggestions">
                        <div class="suggestion-chip" onclick="sendSuggestion('brake parts for Thar')">🔧 Brake parts for Thar</div>
                        <div class="suggestion-chip" onclick="sendSuggestion('engine filter for Marazzo')">🏭 Engine filter for Marazzo</div>
                        <div class="suggestion-chip" onclick="sendSuggestion('cooling system TUV300')">❄️ Cooling system TUV300</div>
                        <div class="suggestion-chip" onclick="sendSuggestion('suspension parts Scorpio')">🚗 Suspension Scorpio</div>
                    </div>
                </div>
            </div>
            
            <div class="input-area">
                <div class="input-container">
                    <input type="text" id="searchInput" class="search-input" 
                           placeholder="Ask me about Mahindra automotive parts..." autocomplete="off">
                    <button id="sendBtn" class="send-btn">
                        <i class="fas fa-paper-plane"></i> Send
                    </button>
                </div>
            </div>
        </div>
        
        <div class="status-bar">
            <div class="status-left">
                <div class="status-item"><i class="fas fa-robot text-success"></i> Gemini 2.0 Pro Active</div>
                <div class="status-item"><i class="fas fa-database"></i> ''' + str(len(parts_data)) + ''' parts loaded</div>
            </div>
            <div class="status-item">⚡ Last search: <span id="lastTime">-</span></div>
        </div>
    </div>

    <script>
        const chatArea = document.getElementById('chatArea');
        const searchInput = document.getElementById('searchInput');
        const sendBtn = document.getElementById('sendBtn');
        const lastTime = document.getElementById('lastTime');

        function addMessage(content, isUser = false, isTyping = false) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${isUser ? 'user' : 'assistant'}${isTyping ? ' typing' : ''}`;
            
            msgDiv.innerHTML = `
                <div class="avatar">${isUser ? 'U' : 'AI'}</div>
                <div class="content">${content}</div>
            `;
            
            // Remove welcome message if present
            const welcome = chatArea.querySelector('.welcome');
            if (welcome) welcome.remove();
            
            chatArea.appendChild(msgDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
            return msgDiv;
        }

        function addTyping() {
            return addMessage('<i class="fas fa-brain"></i> Thinking with AI...', false, true);
        }

        async function sendMessage(query = null) {
            const message = query || searchInput.value.trim();
            if (!message) return;

            sendBtn.disabled = true;
            addMessage(message, true);
            const typing = addTyping();
            if (!query) searchInput.value = '';

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: message })
                });

                const data = await response.json();
                typing.remove();

                if (data.success) {
                    let content = data.ai_response || 'Found some results for you!';
                    
                    if (data.results && data.results.length > 0) {
                        content += '<div style="margin-top: 20px;">';
                        data.results.forEach(part => {
                            content += `
                                <div class="result-item">
                                    <div class="result-title">
                                        <span>${part.part_name || 'Unknown Part'}</span>
                                        <span class="result-price">₹${part.cost || 'N/A'}</span>
                                    </div>
                                    <div class="result-details">
                                        ${part.part_description || 'No description available'}
                                    </div>
                                    <div class="result-meta">
                                        <div class="meta-item"><i class="fas fa-car"></i> ${part.vehicle_compatibility || 'N/A'}</div>
                                        <div class="meta-item"><i class="fas fa-cogs"></i> ${part.system_name || 'N/A'}</div>
                                        <div class="meta-item"><i class="fas fa-warehouse"></i> Stock: ${part.stock || 0}</div>
                                        <div class="meta-item"><i class="fas fa-tag"></i> ${part.condition || 'N/A'}</div>
                                    </div>
                                </div>
                            `;
                        });
                        content += '</div>';
                    }
                    
                    addMessage(content);
                    lastTime.textContent = `${data.search_time_ms || 0}ms`;
                } else {
                    addMessage(data.error || data.ai_response || 'Sorry, I encountered an issue.');
                }
            } catch (error) {
                typing.remove();
                addMessage('Sorry, I encountered a technical issue. Please try again.');
            }

            sendBtn.disabled = false;
            searchInput.focus();
        }

        function sendSuggestion(text) {
            sendMessage(text);
        }

        sendBtn.addEventListener('click', () => sendMessage());
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

Generate a helpful, conversational response (max 120 words) that:
1. Acknowledges their query naturally
2. Summarizes what was found
3. Highlights the best option if available
4. Uses automotive expertise
5. Is friendly and professional

Response:"""
        
        response = call_gemini(prompt, max_tokens=250, temperature=0.7)
        
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
    print("\\n🚀 IntelliPart Complete Version Starting...")
    print("🌐 Access your complete AI assistant at: http://127.0.0.1:5004")
    print("✨ Features: Gemini 2.0 Pro AI + Smart Search + Complete UI + No Template Dependencies")
    print("-" * 80)
    app.run(debug=True, host='0.0.0.0', port=5004)
