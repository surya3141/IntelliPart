"""
IntelliPart - Professional Mahindra-Inspired UI with Gemini 2.0 Pro
==================================================================

This version features a professional UI inspired by Mahindra's design language:
- Corporate red and blue color scheme
- Professional typography and layout
- Modern card-based design
- Responsive mobile-first approach
- Clean, automotive-focused interface

No external template dependencies - everything embedded!
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
app.secret_key = 'intellipart_mahindra_ui_2024'

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

class MahindraSearchEngine:
    """Professional search engine with Gemini AI"""
    
    def __init__(self, parts):
        self.parts = parts
    
    def search(self, query: str, top_k: int = 6) -> List[Dict]:
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
print("🚀 Initializing IntelliPart Professional Version...")
gemini_model = initialize_gemini()
parts_data = load_parts_data()
search_engine = MahindraSearchEngine(parts_data)
print("✅ All systems ready!")

@app.route('/')
def home():
    """Serve the professional Mahindra-inspired interface"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IntelliPart - Mahindra Parts Intelligence</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        /* Mahindra-Inspired Professional Design */
        :root {
            --mahindra-red: #C41E3A;
            --mahindra-blue: #1E3A8A;
            --mahindra-orange: #F97316;
            --mahindra-gray: #6B7280;
            --mahindra-light-gray: #F3F4F6;
            --mahindra-dark: #1F2937;
            --primary-gradient: linear-gradient(135deg, var(--mahindra-red) 0%, var(--mahindra-blue) 100%);
            --secondary-gradient: linear-gradient(135deg, var(--mahindra-blue) 0%, var(--mahindra-red) 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--mahindra-light-gray);
            color: var(--mahindra-dark);
            line-height: 1.6;
        }

        /* Header Navigation */
        .navbar {
            background: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 3px solid var(--mahindra-red);
        }

        .nav-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 80px;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.8em;
            font-weight: 700;
            color: var(--mahindra-red);
        }

        .logo i {
            font-size: 2em;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .nav-info {
            display: flex;
            align-items: center;
            gap: 30px;
        }

        .nav-badge {
            background: var(--primary-gradient);
            color: white;
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Main Container */
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 24px;
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 40px;
        }

        /* Search Section */
        .search-section {
            background: white;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            overflow: hidden;
        }

        .search-header {
            background: var(--primary-gradient);
            color: white;
            padding: 32px;
            text-align: center;
        }

        .search-header h1 {
            font-size: 2.5em;
            margin-bottom: 12px;
            font-weight: 700;
        }

        .search-header p {
            font-size: 1.1em;
            opacity: 0.95;
            margin-bottom: 20px;
        }

        .features-list {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }

        .feature-item {
            background: rgba(255,255,255,0.15);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Chat Area */
        .chat-area {
            height: 500px;
            overflow-y: auto;
            padding: 32px;
            background: #FAFAFA;
        }

        .message {
            margin-bottom: 24px;
            display: flex;
            gap: 16px;
            align-items: flex-start;
        }

        .message.user {
            flex-direction: row-reverse;
        }

        .avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 1.1em;
            flex-shrink: 0;
        }

        .user .avatar {
            background: var(--mahindra-blue);
        }

        .assistant .avatar {
            background: var(--mahindra-red);
        }

        .message-content {
            max-width: 75%;
            padding: 20px 24px;
            border-radius: 20px;
            font-size: 1em;
            line-height: 1.6;
        }

        .user .message-content {
            background: var(--mahindra-blue);
            color: white;
            border-bottom-right-radius: 8px;
        }

        .assistant .message-content {
            background: white;
            border: 1px solid #E5E7EB;
            border-bottom-left-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }

        /* Input Area */
        .input-section {
            padding: 32px;
            background: white;
            border-top: 1px solid #E5E7EB;
        }

        .input-container {
            display: flex;
            gap: 16px;
            align-items: center;
        }

        .search-input {
            flex: 1;
            padding: 18px 24px;
            border: 2px solid #E5E7EB;
            border-radius: 30px;
            font-size: 16px;
            outline: none;
            transition: all 0.3s ease;
        }

        .search-input:focus {
            border-color: var(--mahindra-red);
            box-shadow: 0 0 0 3px rgba(196, 30, 58, 0.1);
        }

        .send-button {
            padding: 18px 32px;
            background: var(--primary-gradient);
            color: white;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(196, 30, 58, 0.3);
        }

        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        /* Sidebar */
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        .sidebar-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            overflow: hidden;
        }

        .card-header {
            background: var(--secondary-gradient);
            color: white;
            padding: 20px;
            font-weight: 600;
            font-size: 1.1em;
        }

        .card-content {
            padding: 24px;
        }

        /* Quick Actions */
        .quick-action {
            background: var(--mahindra-light-gray);
            border: 2px solid transparent;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .quick-action:hover {
            border-color: var(--mahindra-red);
            background: white;
            box-shadow: 0 4px 12px rgba(196, 30, 58, 0.1);
        }

        .quick-action i {
            color: var(--mahindra-red);
            font-size: 1.2em;
        }

        /* Parts Results */
        .part-card {
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            padding: 24px;
            margin: 16px 0;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }

        .part-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            border-color: var(--mahindra-red);
        }

        .part-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }

        .part-name {
            font-size: 1.3em;
            font-weight: 700;
            color: var(--mahindra-dark);
            margin-bottom: 4px;
        }

        .part-number {
            color: var(--mahindra-gray);
            font-size: 0.9em;
            font-weight: 600;
        }

        .part-price {
            color: var(--mahindra-red);
            font-size: 1.4em;
            font-weight: 700;
        }

        .part-description {
            color: var(--mahindra-gray);
            margin-bottom: 16px;
            line-height: 1.6;
        }

        .part-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
        }

        .detail-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9em;
        }

        .detail-item i {
            color: var(--mahindra-red);
            width: 16px;
        }

        /* Welcome Screen */
        .welcome-screen {
            text-align: center;
            padding: 60px 40px;
            color: var(--mahindra-gray);
        }

        .welcome-screen h3 {
            color: var(--mahindra-dark);
            font-size: 1.6em;
            margin-bottom: 16px;
        }

        .welcome-screen p {
            font-size: 1.1em;
            margin-bottom: 12px;
        }

        /* Status Bar */
        .status-bar {
            background: linear-gradient(135deg, #F8FAFC, #E2E8F0);
            border-top: 1px solid #E5E7EB;
            padding: 16px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9em;
            color: var(--mahindra-gray);
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .status-item i {
            color: var(--mahindra-red);
        }

        /* Responsive Design */
        @media (max-width: 1024px) {
            .main-container {
                grid-template-columns: 1fr;
                gap: 24px;
            }
            
            .nav-container {
                padding: 0 16px;
            }
            
            .main-container {
                padding: 24px 16px;
            }
        }

        @media (max-width: 768px) {
            .nav-info {
                display: none;
            }
            
            .logo {
                font-size: 1.5em;
            }
            
            .search-header h1 {
                font-size: 2em;
            }
            
            .features-list {
                gap: 12px;
            }
            
            .feature-item {
                padding: 6px 12px;
                font-size: 0.8em;
            }
            
            .input-container {
                flex-direction: column;
                gap: 12px;
            }
            
            .search-input,
            .send-button {
                width: 100%;
            }
        }

        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message {
            animation: fadeInUp 0.3s ease;
        }

        .part-card {
            animation: fadeInUp 0.3s ease;
        }
    </style>
</head>
<body>
    <!-- Navigation Header -->
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">
                <i class="fas fa-cogs"></i>
                <span>IntelliPart</span>
            </div>
            <div class="nav-info">
                <div class="nav-badge">
                    <i class="fas fa-brain"></i>
                    Powered by Gemini 2.0 Pro
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Container -->
    <div class="main-container">
        <!-- Search Section -->
        <div class="search-section">
            <div class="search-header">
                <h1>Parts Intelligence</h1>
                <p>Your AI-powered assistant for Mahindra automotive parts</p>
                <div class="features-list">
                    <div class="feature-item">
                        <i class="fas fa-search"></i>
                        Smart Search
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-car"></i>
                        Vehicle Specific
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-bolt"></i>
                        Real-time AI
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-shield-alt"></i>
                        Genuine Parts
                    </div>
                </div>
            </div>

            <div class="chat-area" id="chatArea">
                <div class="welcome-screen">
                    <h3><i class="fas fa-robot"></i> Welcome to IntelliPart</h3>
                    <p>I'm your intelligent assistant for Mahindra automotive parts.</p>
                    <p>Ask me about any part, and I'll help you find exactly what you need.</p>
                </div>
            </div>

            <div class="input-section">
                <div class="input-container">
                    <input type="text" id="searchInput" class="search-input" 
                           placeholder="Ask about Mahindra parts - e.g., 'brake pads for Thar'..." autocomplete="off">
                    <button id="sendBtn" class="send-button">
                        <i class="fas fa-paper-plane"></i>
                        Send
                    </button>
                </div>
            </div>

            <div class="status-bar">
                <div class="status-item">
                    <i class="fas fa-database"></i>
                    ''' + str(len(parts_data)) + ''' parts available
                </div>
                <div class="status-item">
                    <i class="fas fa-clock"></i>
                    Last search: <span id="lastTime">-</span>
                </div>
            </div>
        </div>

        <!-- Sidebar -->
        <div class="sidebar">
            <!-- Quick Actions -->
            <div class="sidebar-card">
                <div class="card-header">
                    <i class="fas fa-bolt"></i> Quick Actions
                </div>
                <div class="card-content">
                    <div class="quick-action" onclick="quickSearch('brake parts Thar')">
                        <i class="fas fa-stop-circle"></i>
                        <span>Brake Parts - Thar</span>
                    </div>
                    <div class="quick-action" onclick="quickSearch('engine parts Marazzo')">
                        <i class="fas fa-cog"></i>
                        <span>Engine Parts - Marazzo</span>
                    </div>
                    <div class="quick-action" onclick="quickSearch('suspension TUV300')">
                        <i class="fas fa-road"></i>
                        <span>Suspension - TUV300</span>
                    </div>
                    <div class="quick-action" onclick="quickSearch('electrical Scorpio')">
                        <i class="fas fa-bolt"></i>
                        <span>Electrical - Scorpio</span>
                    </div>
                </div>
            </div>

            <!-- Vehicle Models -->
            <div class="sidebar-card">
                <div class="card-header">
                    <i class="fas fa-car"></i> Vehicle Models
                </div>
                <div class="card-content">
                    <div class="quick-action" onclick="quickSearch('parts for Thar')">
                        <i class="fas fa-mountain"></i>
                        <span>Thar</span>
                    </div>
                    <div class="quick-action" onclick="quickSearch('parts for Marazzo')">
                        <i class="fas fa-car-side"></i>
                        <span>Marazzo</span>
                    </div>
                    <div class="quick-action" onclick="quickSearch('parts for TUV300')">
                        <i class="fas fa-truck"></i>
                        <span>TUV300</span>
                    </div>
                    <div class="quick-action" onclick="quickSearch('parts for Scorpio')">
                        <i class="fas fa-car"></i>
                        <span>Scorpio</span>
                    </div>
                </div>
            </div>

            <!-- AI Status -->
            <div class="sidebar-card">
                <div class="card-header">
                    <i class="fas fa-brain"></i> AI Status
                </div>
                <div class="card-content">
                    <div class="status-item">
                        <i class="fas fa-check-circle" style="color: #10B981;"></i>
                        <span>Gemini 2.0 Pro Active</span>
                    </div>
                    <div class="status-item" style="margin-top: 12px;">
                        <i class="fas fa-shield-alt" style="color: #10B981;"></i>
                        <span>Enterprise Ready</span>
                    </div>
                    <div class="status-item" style="margin-top: 12px;">
                        <i class="fas fa-sync" style="color: #3B82F6;"></i>
                        <span>Real-time Processing</span>
                    </div>
                </div>
            </div>
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
                <div class="message-content">${content}</div>
            `;
            
            // Remove welcome screen if present
            const welcome = chatArea.querySelector('.welcome-screen');
            if (welcome) welcome.remove();
            
            chatArea.appendChild(msgDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        function addTyping() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message assistant';
            typingDiv.innerHTML = `
                <div class="avatar">AI</div>
                <div class="message-content"><i class="fas fa-brain"></i> Analyzing your request...</div>
            `;
            chatArea.appendChild(typingDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
            return typingDiv;
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
                                <div class="part-card">
                                    <div class="part-header">
                                        <div>
                                            <div class="part-name">${part.part_name || 'Unknown Part'}</div>
                                            <div class="part-number">#${part.part_number || 'N/A'}</div>
                                        </div>
                                        <div class="part-price">₹${part.cost || 'N/A'}</div>
                                    </div>
                                    <div class="part-description">
                                        ${part.part_description || 'No description available'}
                                    </div>
                                    <div class="part-details">
                                        <div class="detail-item">
                                            <i class="fas fa-car"></i>
                                            <span>${part.vehicle_compatibility || 'N/A'}</span>
                                        </div>
                                        <div class="detail-item">
                                            <i class="fas fa-cogs"></i>
                                            <span>${part.system_name || 'N/A'}</span>
                                        </div>
                                        <div class="detail-item">
                                            <i class="fas fa-warehouse"></i>
                                            <span>Stock: ${part.stock || 0}</span>
                                        </div>
                                        <div class="detail-item">
                                            <i class="fas fa-shield-alt"></i>
                                            <span>${part.condition || 'N/A'}</span>
                                        </div>
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

        function quickSearch(query) {
            sendMessage(query);
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
    """Professional search API with Gemini intelligence"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query required'}), 400

        start_time = time.time()
        
        # Perform search
        results = search_engine.search(query, top_k=6)
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
    """Generate professional response using Gemini 2.0 Pro"""
    try:
        if not gemini_model:
            if results:
                return f"Found {len(results)} professional-grade parts for '{query}'. Here are our top recommendations:"
            else:
                return f"No parts found for '{query}'. Please try different search terms or contact our parts specialist."
        
        # Prepare context for Gemini
        context = ""
        if results:
            context = "\\n".join([
                f"- {part.get('part_name', 'Unknown')} (₹{part.get('cost', 'N/A')}) for {part.get('vehicle_compatibility', 'Unknown vehicle')}"
                for part in results[:3]
            ])
        
        prompt = f"""
You are a professional Mahindra automotive parts specialist with deep expertise.

Customer Query: "{query}"
Available Parts: {len(results)} parts found
Top Recommendations:
{context or "No matching parts found"}

Generate a professional, helpful response (max 120 words) that:
1. Greets the customer professionally
2. Summarizes the findings clearly
3. Highlights the best recommendation
4. Demonstrates automotive expertise
5. Maintains professional Mahindra service standards

Response:"""
        
        response = call_gemini(prompt, max_tokens=250, temperature=0.6)
        
        # Clean up response
        if response and not response.startswith('['):
            return response.strip()
        else:
            # Professional fallback response
            if results:
                return f"I've found {len(results)} high-quality Mahindra parts matching your requirements for '{query}'. Our top recommendation is the {results[0].get('part_name', 'premium part')} at ₹{results[0].get('cost', 'N/A')} - perfect for your {results[0].get('vehicle_compatibility', 'vehicle')}. All parts come with Mahindra's quality assurance."
            else:
                return f"I couldn't locate parts matching '{query}' in our current inventory. Please try alternative search terms like specific vehicle models (Thar, Marazzo, TUV300, Scorpio) or part categories (engine, brake, electrical). Our parts specialist is available for personalized assistance."
        
    except Exception as e:
        print(f"AI response error: {e}")
        if results:
            return f"Found {len(results)} quality Mahindra parts for '{query}' ✓"
        else:
            return f"No matching parts found for '{query}'. Please refine your search terms."

if __name__ == "__main__":
    print("\\n🚀 IntelliPart Professional Edition Starting...")
    print("🌐 Access your professional interface at: http://127.0.0.1:5005")
    print("🎨 Features: Mahindra-Inspired UI + Gemini 2.0 Pro AI + Professional Design")
    print("🔴 Color Scheme: Mahindra Red (#C41E3A) + Corporate Blue (#1E3A8A)")
    print("-" * 80)
    app.run(debug=True, host='0.0.0.0', port=5005)
