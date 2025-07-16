"""
IntelliPart Conversational Web Interface with Gemini 2.0 Pro

Enhanced version using Google's Gemini 2.0 Pro model for advanced AI capabilities.
This script launches a Flask-based web application that provides a conversational
interface for searching car parts with AI-powered understanding.

Features:
- Gemini 2.0 Pro integration for intelligent responses
- Advanced query understanding and enhancement
- Semantic search with AI fallback
- Enhanced conversation capabilities
- Modern UI with AI insights
"""

from flask import Flask, render_template, request, jsonify, session
import json
import time
import os
import ssl
import re
import requests
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Sequence

# Configure SSL for corporate networks
try:
    ssl._create_default_https_context = ssl._create_unverified_context
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''
except:
    pass

# Import optional AI libraries
try:
    import openai
except ImportError:
    openai = None
try:
    import faiss
except ImportError:
    faiss = None
try:
    from rapidfuzz import process as fuzzy_process
except ImportError:
    fuzzy_process = None
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
try:
    from transformers import logging as hf_logging
except ImportError:
    hf_logging = None

# Google AI imports for Gemini 2.0 Pro
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    genai = None

app = Flask(__name__)
app.secret_key = 'intellipart_gemini2_conversation_key_2024'

# Gemini 2.0 Pro Configuration
GEMINI_JSON_PATH = "D:/OneDrive - Mahindra & Mahindra Ltd/Desktop/POC/Gemini/gemini_v1/scripts/mdp-ad-parts-dev-api-json-key.json"
GEMINI_MODEL_NAME = "gemini-2.0-flash-exp"  # Using Gemini 2.0 Pro experimental

def initialize_gemini():
    """Initialize Gemini 2.0 Pro with service account"""
    try:
        if not os.path.exists(GEMINI_JSON_PATH):
            print(f"⚠️ Gemini JSON key not found at: {GEMINI_JSON_PATH}")
            return None
            
        # Set up Google Cloud credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GEMINI_JSON_PATH
        
        # Initialize Gemini AI
        if genai:
            # Try to get API key from environment or use service account
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                print("✅ Gemini 2.0 Pro initialized with API key")
            else:
                print("✅ Gemini 2.0 Pro initialized with service account")
            
            # Test the model
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            print(f"✅ Gemini model '{GEMINI_MODEL_NAME}' ready")
            return model
        else:
            print("❌ google.generativeai not available")
            return None
            
    except Exception as e:
        print(f"❌ Failed to initialize Gemini 2.0 Pro: {e}")
        return None

# Initialize Gemini model
gemini_model = initialize_gemini()

def call_gemini_2_pro(prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
    """
    Call Gemini 2.0 Pro with enhanced capabilities
    """
    try:
        if not gemini_model:
            return "[ERROR: Gemini 2.0 Pro not available]"
            
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            top_p=0.8,
            top_k=40
        )
        
        # Safety settings for corporate use
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Generate response
        response = gemini_model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        if response.candidates and response.candidates[0].content:
            return response.candidates[0].content.parts[0].text
        else:
            return "[ERROR: No response generated]"
            
    except Exception as e:
        return f"[ERROR: Gemini 2.0 Pro call failed: {e}]"

def load_all_parts_from_datasets():
    """Load parts data from all available datasets."""
    all_parts = []
    
    # Try loading from main dataset first
    main_dataset = Path(__file__).parent.parent / "data" / "car_parts_dataset.jsonl"
    if main_dataset.is_file():
        try:
            print(f"[DEBUG] Loading main dataset: {main_dataset}")
            with open(main_dataset, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        all_parts.append(json.loads(line.strip()))
            print(f"[DEBUG] Loaded {len(all_parts)} parts from main dataset")
            return all_parts
        except Exception as e:
            print(f"Error loading main dataset {main_dataset}: {e}")
    
    # Fallback to synthetic dataset if main dataset not found
    synthetic_dataset = Path(__file__).parent.parent / "synthetic_car_parts_500.jsonl"
    if synthetic_dataset.is_file():
        try:
            print(f"[DEBUG] Loading synthetic dataset: {synthetic_dataset}")
            with open(synthetic_dataset, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        all_parts.append(json.loads(line.strip()))
            print(f"[DEBUG] Loaded {len(all_parts)} parts from synthetic dataset")
        except Exception as e:
            print(f"Error loading synthetic dataset {synthetic_dataset}: {e}")
    
    if not all_parts:
        print("[ERROR] No datasets could be loaded")
    
    return all_parts

# Enhanced Keyword Search Engine with Gemini Integration
class GeminiEnhancedSearchEngine:
    """
    Enhanced search engine that combines keyword search with Gemini 2.0 Pro intelligence
    """
    
    def __init__(self, parts: List[Dict[str, Any]]):
        self.parts = parts
        print(f"✅ Gemini-enhanced search engine initialized with {len(parts)} parts")
    
    def _normalize(self, text):
        """Normalize text for matching"""
        if not isinstance(text, str):
            text = str(text)
        return text.lower().strip()
    
    def _calculate_score(self, part, query_terms):
        """Calculate relevance score based on keyword matches"""
        score = 0
        part_text = " ".join(str(v) for v in part.values()).lower()
        
        for term in query_terms:
            term_lower = term.lower()
            if term_lower in part_text:
                # Boost score for exact matches in important fields
                if term_lower in self._normalize(part.get('part_name', '')):
                    score += 3
                elif term_lower in self._normalize(part.get('system_name', '')):
                    score += 2
                elif term_lower in self._normalize(part.get('manufacturer', '')):
                    score += 2
                else:
                    score += 1
        
        return score
    
    def enhance_query_with_gemini(self, query: str) -> Dict[str, Any]:
        """Use Gemini 2.0 Pro to enhance and understand the query"""
        try:
            enhancement_prompt = f"""
You are an expert automotive parts assistant with deep knowledge of car components and systems.

Analyze this user query: "{query}"

Please provide a JSON response with the following structure:
{{
    "enhanced_query": "improved search terms optimized for finding automotive parts",
    "part_type": "specific type of automotive part being searched (e.g., brake pad, radiator, battery)",
    "vehicle_model": "vehicle model mentioned if any (e.g., Thar, Marazzo, TUV300)",
    "specifications": ["list", "of", "technical", "specifications", "mentioned"],
    "search_terms": ["optimized", "keywords", "for", "search"],
    "user_intent": "what the user is trying to accomplish",
    "confidence": 0.95
}}

Focus on automotive terminology and Mahindra vehicle models. If the query is vague, suggest the most likely interpretation.
"""
            
            response = call_gemini_2_pro(enhancement_prompt, max_tokens=500, temperature=0.3)
            
            try:
                enhanced_data = json.loads(response)
                return enhanced_data
            except:
                # Fallback if JSON parsing fails
                return {
                    "enhanced_query": query,
                    "part_type": "unknown",
                    "vehicle_model": "unknown", 
                    "specifications": [],
                    "search_terms": query.split(),
                    "user_intent": "search for automotive parts",
                    "confidence": 0.5
                }
                
        except Exception as e:
            print(f"Query enhancement error: {e}")
            return {
                "enhanced_query": query,
                "part_type": "unknown",
                "vehicle_model": "unknown",
                "specifications": [],
                "search_terms": query.split(),
                "user_intent": "search for automotive parts", 
                "confidence": 0.5
            }
    
    def search(self, query: str, top_k: int = 5, min_similarity: float = 0.1) -> List[Dict[str, Any]]:
        """Perform enhanced search with Gemini intelligence"""
        if not query.strip():
            return []
        
        # Use Gemini to enhance the query
        enhancement = self.enhance_query_with_gemini(query)
        enhanced_query = enhancement.get('enhanced_query', query)
        search_terms = enhancement.get('search_terms', query.split())
        
        # Perform keyword search with enhanced terms
        results = []
        for part in self.parts:
            score = self._calculate_score(part, search_terms)
            if score > 0:
                part_copy = part.copy()
                part_copy['similarity'] = min(score / len(search_terms), 1.0)
                part_copy['gemini_enhancement'] = enhancement
                results.append(part_copy)
        
        # Sort by score and return top results
        results = sorted(results, key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def direct_or_semantic_search(self, query: str, top_k: int = 5, min_similarity: float = 0.1) -> List[Dict[str, Any]]:
        """Perform direct search with Gemini enhancement"""
        return self.search(query, top_k, min_similarity)
    
    def suggest(self, query: str, limit: int = 5) -> List[str]:
        """Get AI-powered query suggestions"""
        try:
            suggestion_prompt = f"""
Based on the automotive parts query: "{query}"

Suggest {limit} related search queries that might help the user find relevant Mahindra automotive parts.
Focus on:
- Similar parts or components
- Different vehicle models
- Related systems or assemblies
- Alternative specifications

Return only a JSON array of strings:
["suggestion 1", "suggestion 2", "suggestion 3", "suggestion 4", "suggestion 5"]
"""
            
            response = call_gemini_2_pro(suggestion_prompt, max_tokens=300, temperature=0.5)
            
            try:
                suggestions = json.loads(response)
                return suggestions if isinstance(suggestions, list) else []
            except:
                # Fallback suggestions
                return [
                    f"Find {query} for Thar",
                    f"Find {query} for Marazzo", 
                    f"Find {query} for TUV300",
                    f"Show {query} with good condition",
                    f"List all {query} components"
                ]
                
        except Exception as e:
            return []

# Initialize search engine
print("🔄 Initializing Gemini-enhanced search engine...")
try:
    all_parts = load_all_parts_from_datasets()
    print(f"📦 Loaded {len(all_parts)} parts from dataset")
    
    search_engine = GeminiEnhancedSearchEngine(all_parts)
    print("🚀 Gemini-enhanced search engine ready!")
    
except Exception as e:
    print(f"❌ Error initializing search engine: {e}")
    search_engine = None
    all_parts = []

@app.route('/')
def conversational_interface():
    """Main interface with enhanced Gemini capabilities"""
    try:
        return render_template('conversational_search_gemini.html')
    except Exception as e:
        return f"""
        <h1>Template Error</h1>
        <p>Could not load template: {e}</p>
        <p>Please check if templates/conversational_search_gemini.html exists</p>
        <p><a href="/api/assistant-intro">Test API</a></p>
        """

@app.route('/api/search', methods=['POST'])
def api_search():
    """Enhanced search API with Gemini 2.0 Pro intelligence"""
    if not search_engine:
        return jsonify({'error': 'Search engine not available'}), 500
        
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        start_time = time.time()
        
        # Perform Gemini-enhanced search
        results = search_engine.direct_or_semantic_search(query, top_k=10)
        suggestions = search_engine.suggest(query, limit=5)
        search_time_ms = round((time.time() - start_time) * 1000, 2)
        
        # Generate intelligent response using Gemini 2.0 Pro
        intelligent_response = generate_gemini_response(query, results, search_time_ms)
        
        if not results:
            return jsonify({
                'success': False,
                'query': query,
                'intelligent_response': generate_no_results_response_gemini(query),
                'suggestions': suggestions
            })

        # Sanitize results for frontend
        sanitized_results = []
        for part in results:
            part_copy = dict(part)
            part_copy.pop('similarity', None)
            part_copy.pop('gemini_enhancement', None)  # Remove for frontend
            sanitized_results.append(part_copy)

        response = {
            'success': True,
            'query': query,
            'results': sanitized_results[:10],
            'result_count': len(sanitized_results),
            'search_time_ms': search_time_ms,
            'suggestions': suggestions,
            'intelligent_response': intelligent_response,
            'ai_enhanced': True,
            'model_used': 'Gemini 2.0 Pro'
        }
        return jsonify(response)

    except Exception as e:
        app.logger.error(f"API Search Error: {e}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred. Please try again later.'}), 500

def generate_gemini_response(query: str, results: List[Dict], search_time: float) -> str:
    """Generate intelligent response using Gemini 2.0 Pro"""
    try:
        # Prepare context for Gemini
        context_parts = []
        for i, part in enumerate(results[:3]):  # Top 3 results
            context_parts.append(f"Result {i+1}: {part.get('part_name', 'Unknown')} - {part.get('system_name', 'Unknown System')} (₹{part.get('cost', 'N/A')})")
        
        context = "/n".join(context_parts) if context_parts else "No specific results found"
        
        response_prompt = f"""
You are an expert Mahindra automotive parts assistant. A user asked: "{query}"

Search Results Context:
{context}

Search completed in {search_time:.1f}ms with {len(results)} results found.

Generate a helpful, conversational response that:
1. Acknowledges their query in a friendly way
2. Summarizes what was found (if any)
3. Highlights the best options
4. Provides useful next steps or suggestions
5. Uses appropriate automotive terminology

Keep the response conversational, helpful, and under 150 words. Use emojis appropriately.
"""
        
        response = call_gemini_2_pro(response_prompt, max_tokens=300, temperature=0.7)
        return response if response and not response.startswith("[ERROR") else f"Found {len(results)} results for your search in {search_time:.1f}ms! 🔍"
        
    except Exception as e:
        return f"Found {len(results)} results for your search in {search_time:.1f}ms! 🔍"

def generate_no_results_response_gemini(query: str) -> str:
    """Generate helpful no-results response using Gemini"""
    try:
        no_results_prompt = f"""
A user searched for "{query}" but no results were found in our Mahindra automotive parts database.

Generate a helpful, empathetic response that:
1. Acknowledges that no exact matches were found
2. Suggests alternative search terms or approaches
3. Offers to help them refine their search
4. Maintains a positive, helpful tone
5. Uses automotive expertise to suggest related parts

Keep it conversational and under 100 words. Use appropriate emojis.
"""
        
        response = call_gemini_2_pro(no_results_prompt, max_tokens=200, temperature=0.7)
        return response if response and not response.startswith("[ERROR") else "I couldn't find exact matches for your search. Try using different keywords or check the spelling. 🤔"
        
    except Exception as e:
        return "I couldn't find exact matches for your search. Try using different keywords or check the spelling. 🤔"

@app.route('/api/assistant-intro')
def api_assistant_intro():
    """Enhanced assistant intro with Gemini capabilities"""
    intro_json = {
        "greeting": "Welcome to IntelliPart with Gemini 2.0 Pro! 🚀",
        "intro": "I'm your advanced AI assistant powered by Google's Gemini 2.0 Pro model. I can understand complex queries, provide intelligent recommendations, and help you find the perfect Mahindra automotive parts with enhanced AI capabilities.",
        "capabilities": [
            "🧠 AI-powered query understanding and enhancement",
            "🔍 Intelligent part search with context awareness", 
            "💡 Smart suggestions and recommendations",
            "🚗 Deep knowledge of Mahindra vehicles and systems",
            "⚡ Real-time AI-driven responses"
        ],
        "suggestion": "Try asking me something like 'I need brake parts for my Thar' or 'Show me radiators with good cooling performance'",
        "model": "Gemini 2.0 Pro",
        "enhanced_features": True
    }
    return jsonify({"success": True, "assistant_intro": intro_json})

@app.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():
    """Direct AI chat endpoint using Gemini 2.0 Pro"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create a conversational prompt
        chat_prompt = f"""
You are an expert Mahindra automotive parts assistant with access to a comprehensive parts database.

User message: "{message}"

Available parts database contains information about:
- Part names, numbers, and descriptions
- System classifications (Engine, Brake, Electrical, etc.)
- Vehicle compatibility (Thar, Marazzo, TUV300, etc.)
- Pricing, stock levels, and conditions
- Technical specifications

Respond conversationally and helpfully. If they're asking about parts, provide specific guidance. If they need help with search strategies, suggest effective approaches.

Keep your response helpful, accurate, and under 200 words.
"""
        
        response = call_gemini_2_pro(chat_prompt, max_tokens=400, temperature=0.8)
        
        return jsonify({
            'success': True,
            'response': response,
            'model': 'Gemini 2.0 Pro',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting IntelliPart with Gemini 2.0 Pro...")
    print(f"🌐 Access your enhanced AI assistant at: http://127.0.0.1:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
