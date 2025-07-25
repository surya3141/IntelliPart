"""
IntelliPart Conversational Web Interface

This script launches a Flask-based web application that provides a conversational
interface for searching car parts. It leverages the ConversationalPartsSearch engine
to understand natural language queries and provide intelligent search results.

The web app includes the following features:
- A main search interface for user queries.
- An API for handling search, follow-up questions, and other interactions.
- Session management to maintain conversation history.
- Integration with the advanced analytics module for quick insights.
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
from conversational_search import ConversationalEngine, ConversationalPartsSearch
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Sequence

# Configure SSL for corporate networks
try:
    ssl._create_default_https_context = ssl._create_unverified_context
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''
except Exception:
    pass

try:
    import openai
except ImportError:
    openai = None

try:
    import faiss
except ImportError:
    faiss = None

try:
    from rapidfuzz import process as fuzzy_process  # type: ignore
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
import re

app = Flask(__name__)
app.secret_key = 'intellipart_conversation_key_2024'

# Set Gemini API key for direct REST API usage
# os.environ["GEMINI_API_KEY"] = "AIzaSyBkiH75m5TbvW3c80LSYSt5HDFBOKU9pbE"

# Helper to load only the shrunk dataset as the primary and sole dataset

def load_all_parts_from_datasets():
    """Load parts data from all available datasets."""
    all_parts = []
    
    # Try loading from local data directory first
    local_dataset = Path(__file__).parent / "data" / "training Dataset.jsonl"
    if local_dataset.is_file():
        try:
            print(f"[DEBUG] Loading local dataset: {local_dataset}")
            with open(local_dataset, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        all_parts.append(json.loads(line.strip()))
            print(f"[DEBUG] Loaded {len(all_parts)} parts from local dataset")
            return all_parts
        except Exception as e:
            print(f"Error loading local dataset {local_dataset}: {e}")
    
    # Try loading from main dataset
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
        # Create sample data for testing
        print("[DEBUG] Creating sample data for testing")
        all_parts = [
            {
                "part_number": "BRK001",
                "part_name": "Brake Pad Set",
                "system_name": "Braking System",
                "manufacturer": "Mahindra",
                "cost": 2500,
                "stock": 15,
                "condition": "Good",
                "material": "Ceramic",
                "vehicle_model": "Thar"
            },
            {
                "part_number": "RAD002",
                "part_name": "Radiator",
                "system_name": "Cooling System", 
                "manufacturer": "Mahindra",
                "cost": 8500,
                "stock": 8,
                "condition": "Excellent",
                "material": "Aluminum",
                "vehicle_model": "Marazzo"
            }
        ]
        print(f"[DEBUG] Created {len(all_parts)} sample parts for testing")
    
    return all_parts

# --- Gemini GenAI utility using Vertex AI Python client ---
def call_gemini_vertex(prompt: str, model_name: str = "gemini-1.0-pro", max_output_tokens: int = 512) -> str:
    """
    Calls Gemini Vertex AI using the Python client and service account key.
    """
    try:
        client = connect_to_google_genai()
        from google.genai import types
        from google.generativeai.types import ContentType, GenerateContentResponse
        
        # Create content in the correct format
        content: ContentType = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
        
        response = ""
        for chunk in client.models.generate_content_stream(
            model=model_name,
            contents=[content],
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=max_output_tokens
            )
        ):
            if chunk.text is not None:  # Type check for None
                response += chunk.text
        return response.strip()
    except Exception as e:
        return f"[ERROR: Gemini Vertex call failed: {e}]"

# --- Gemini GenAI utility (auto: API key or Vertex client) ---
def call_gemini(prompt: str, api_key: Optional[str] = None, model: str = "models/gemini-1.5-pro-latest") -> str:
    """
    Calls Gemini API with the given prompt and returns the response text.
    Uses API key if set, else falls back to Vertex AI Python client.
    """
    api_key = api_key or os.environ.get("GEMINI_API_KEY", "")  # Default to empty string if not found
    if api_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 512}
        }
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=15)
            resp.raise_for_status()
            out = resp.json()
            return out['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"[ERROR: Gemini API call failed: {e}]"
    else:
        # Use Vertex AI Python client
        return call_gemini_vertex(prompt)

# --- Gemini Vertex AI authentication utility ---
def authenticate_json():
    json_key_path = "D://OneDrive - Mahindra & Mahindra Ltd//Desktop//POC//Gemini//gemini_v1//scripts//mdp-ad-parts-dev-api-json-key.json"  # JSON key file
    if not os.path.exists(json_key_path):
        raise FileNotFoundError(f"Service account key file '{json_key_path}' not found.")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_path  # Set environment variable

# --- Connect to Google Vertex AI (genai.Client) ---
def connect_to_google_genai():
    authenticate_json()
    from google import genai
    client = genai.Client(
        vertexai=True,
        project="mdp-ad-parts-dev-338172",  # Replace with your actual Project ID
        location="global"                  # Replace with your model's location
    )
    return client

# --- Semantic Search Engine ---
class SemanticSearchEngineHF:
    def __init__(self, parts: List[Dict[str, Any]], embedding_model_name: Optional[str] = None):
        self.parts = parts
        if hf_logging:
            hf_logging.set_verbosity_error()
        
        # Use a simple, reliable model that can be downloaded automatically
        if embedding_model_name is None:
            # Use a small, efficient model that works well for general text
            embedding_model_name = 'all-MiniLM-L6-v2'
        
        if not SentenceTransformer:
            raise ImportError("sentence_transformers is required but not installed")
        
        if not faiss:
            raise ImportError("faiss-cpu is required but not installed")
            
        if not np:
            raise ImportError("numpy is required but not installed")
            
        print(f"🔄 Loading SentenceTransformer model: {embedding_model_name}")
        
        # Corporate-friendly model loading with multiple fallback strategies
        model_loaded = False
        
        # Strategy 1: Try loading from local cache first
        try:
            cache_dir = Path.home() / ".cache" / "huggingface" / "transformers"
            self.embedding_model = SentenceTransformer(embedding_model_name, cache_folder=str(cache_dir))
            print(f"✅ SentenceTransformer model loaded from local cache")
            model_loaded = True
        except Exception as cache_error:
            print(f"⚠️ Local cache loading failed: {cache_error}")
        
        # Strategy 2: Try with corporate SSL settings
        if not model_loaded:
            try:
                import ssl
                import os
                # Temporarily disable SSL verification for corporate networks
                ssl._create_default_https_context = ssl._create_unverified_context
                os.environ['REQUESTS_CA_BUNDLE'] = ''
                os.environ['CURL_CA_BUNDLE'] = ''
                
                self.embedding_model = SentenceTransformer(
                    embedding_model_name, 
                    trust_remote_code=False,
                    use_auth_token=False
                )
                print(f"✅ SentenceTransformer model loaded with corporate SSL settings")
                model_loaded = True
            except Exception as ssl_error:
                print(f"⚠️ Corporate SSL method failed: {ssl_error}")
        
        # Strategy 3: Try offline mode with pre-downloaded model
        if not model_loaded:
            try:
                # Try to load from a local model directory if it exists
                local_model_path = Path(__file__).parent / "models" / embedding_model_name
                if local_model_path.exists():
                    self.embedding_model = SentenceTransformer(str(local_model_path))
                    print(f"✅ SentenceTransformer model loaded from local directory")
                    model_loaded = True
                else:
                    print(f"💡 Local model directory not found: {local_model_path}")
            except Exception as local_error:
                print(f"⚠️ Local model loading failed: {local_error}")
        
        # Strategy 4: Try with minimal model (fallback)
        if not model_loaded:
            try:
                # Use a smaller, simpler model that might be easier to download
                fallback_model = 'paraphrase-MiniLM-L3-v2'
                print(f"💡 Trying fallback model: {fallback_model}")
                self.embedding_model = SentenceTransformer(fallback_model)
                print(f"✅ Fallback SentenceTransformer model loaded successfully")
                model_loaded = True
            except Exception as fallback_error:
                print(f"⚠️ Fallback model also failed: {fallback_error}")
        
        if not model_loaded:
            print("❌ All model loading strategies failed!")
            print("🏢 CORPORATE NETWORK DETECTED:")
            print("   1. Contact your IT department to whitelist huggingface.co")
            print("   2. Or ask them to configure proxy settings for ML models")
            print("   3. Alternatively, use the simple keyword search (which works perfectly!)")
            raise Exception("Unable to load SentenceTransformer model in corporate environment")
            
        self.index = None
        self.id_to_idx: Dict[str, int] = {}
        self.idx_to_id: Dict[int, str] = {}
        self.embeddings: Optional[np.ndarray] = None
        self._build_index()

    def _get_text(self, part):
        # Serialize all attributes in a structured way for embedding
        return '; '.join(f"{k}: {v}" for k, v in part.items() if v and isinstance(v, (str, int, float)))

    def _build_index(self) -> None:
        print(f"🔄 Building search index for {len(self.parts)} parts...")
        
        descriptions = [self._get_text(p) for p in self.parts]
        self.embeddings = self.embedding_model.encode(descriptions, show_progress_bar=False, convert_to_numpy=True)
        
        if self.embeddings is not None:
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings.astype('float32'))
            
            for idx, part in enumerate(self.parts):
                part_id = str(part.get('part_number', str(idx)))
                self.id_to_idx[part_id] = idx
                self.idx_to_id[idx] = part_id
                
        print(f"✅ Search index built successfully with {len(self.parts)} parts")

    def search(self, query: str, top_k: int = 5, min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """Semantic search implementation"""
        if self.index is None or self.embeddings is None:
            return []
            
        # Hybrid: Try keyword/entity match in any attribute first
        query_lower = query.lower().strip()
        filtered = []
        for part in self.parts:
            for v in part.values():
                if isinstance(v, str) and query_lower in v.lower():
                    filtered.append(part.copy())
                    break
        if filtered:
            # Optionally, sort by semantic similarity
            query_vec = self.embedding_model.encode([query], convert_to_numpy=True)
            for part in filtered:
                part_text = self._get_text(part)
                part_vec = self.embedding_model.encode([part_text], convert_to_numpy=True)
                sim = float(np.dot(query_vec, part_vec.T) / (np.linalg.norm(query_vec) * np.linalg.norm(part_vec)))
                part['similarity'] = sim
            filtered = sorted(filtered, key=lambda x: x['similarity'], reverse=True)
            return filtered[:top_k]
            
        # Fallback: semantic search on all attributes
        query_vec = self.embedding_model.encode([query], convert_to_numpy=True)
        if self.index is not None:  # Type check
            D, I = self.index.search(query_vec, top_k * 2)
            similarities = 1 - (D[0] / 2)
            results = []
            for idx, sim in zip(I[0], similarities):
                if sim >= min_similarity:
                    part = self.parts[idx].copy()
                    part['similarity'] = float(sim)
                    results.append(part)
            results = sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_k]
            return results
        return []

    def suggest(self, query: str, limit: int = 5) -> List[str]:
        """Get query suggestions"""
        if not fuzzy_process:
            return []
            
        choices = [p.get('part_name', '') for p in self.parts] + [p.get('part_number', '') for p in self.parts]
        suggestions = fuzzy_process.extract(query, choices, limit=limit)
        return [s[0] for s in suggestions if s[1] > 60]

    def _normalize(self, text):
        if not isinstance(text, str):
            text = str(text)
        import re
        # Lowercase, remove punctuation, collapse whitespace, remove filler words
        text = text.lower()
        text = re.sub(r"[\?\.,!;:>\-_/\\]", " ", text)  # Remove/replace common punctuation and separators
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        return text

    def _clean_query(self, query):
        """
        Remove common filler words, stopwords, and trailing phrases from the query for robust direct/field matching.
        Handles cases like trailing 'can', 'please', etc. anywhere in the query.
        """
        import re
        stop_phrases = [
            r"\bplease\b", r"\bcan you\b", r"\bcould you\b", r"\bshow me\b", r"\bfind\b", r"\blist\b", r"\bgive me\b", r"\bi want\b", r"\bi need\b",
            r"\bthe\b", r"\ba\b", r"\ban\b", r"\bof\b", r"\bfor\b", r"\bwith\b", r"\bto\b", r"\bin\b", r"\bon\b", r"\bby\b", r"\babout\b", r"\bshow\b", r"\bfind\b", r"\blist\b", r"\bgive\b", r"\bme\b", r"\bcan\b"
        ]
        cleaned = query.lower()
        for phrase in stop_phrases:
            cleaned = re.sub(phrase, "", cleaned)
        cleaned = re.sub(r"[\?\.,!;:>\-_/\\]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def direct_or_semantic_search(self, query, top_k=5, min_similarity=0.7):
        key_fields = [
            "Part Number", "Part Description", "System Name", "Sub System Name",
            "Sub Sub System Name", "Serviceability", "End Items", "Source"
        ]
        import re
        normalized_query = self._normalize(query)
        cleaned_query = self._clean_query(query)
        normalized_cleaned_query = self._normalize(cleaned_query)
        # Try direct/field match for any field (not just key_fields)
        for part in self.parts:
            for v in part.values():
                if self._normalize(v) == normalized_query or self._normalize(v) == normalized_cleaned_query:
                    part_copy = part.copy()
                    part_copy['similarity'] = 1.0
                    part_copy['direct_match'] = True
                    return [part_copy]
        # Try key_fields logic (field:value extraction)
        for field in key_fields:
            if field.lower() in normalized_query or field.lower() in normalized_cleaned_query:
                match = re.search(rf"{field}.*?[=:]?\\s*([\w\-\s\(\)\/]+)", query, re.IGNORECASE)
                if not match:
                    match = re.search(rf"{field}.*?[=:]?\\s*([\w\-\s\(\)\/]+)", cleaned_query, re.IGNORECASE)
                if match:
                    value = self._normalize(match.group(1))
                    results = [p.copy() for p in self.parts if self._normalize(p.get(field, "")) == value]
                    if results:
                        for part in results:
                            part['similarity'] = 1.0
                            part['direct_match'] = True
                        return sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_k]
                    results = [p.copy() for p in self.parts if value in self._normalize(p.get(field, ""))]
                    if results:
                        for part in results:
                            part['similarity'] = 0.95
                            part['direct_match'] = True
                        return sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_k]
                return []
        # Only use semantic search if no direct/field match
        return self.search(query, top_k=top_k, min_similarity=min_similarity)

def extract_technical_specs(query):
    """Extract technical specifications from the query."""
    specs = {}
    # Example: "friction coefficient above 0.4"
    friction_match = re.search(r"friction coefficient (?:above|of|greater than) (\d\.\d+)", query, re.IGNORECASE)
    if friction_match:
        specs['friction_coefficient'] = float(friction_match.group(1))

    # Example: "with ceramic material"
    material_match = re.search(r"(?:with|made of) (\w+) material", query, re.IGNORECASE)
    if material_match:
        specs['material'] = material_match.group(1)
        
    return specs

def filter_results_by_specs(results, specs):
    """Filter search results based on extracted technical specs."""
    if not specs:
        return results
    
    filtered_results = []
    for r in results:
        match = True
        if 'friction_coefficient' in specs:
            if float(r.get('friction_coefficient', 0)) < specs['friction_coefficient']:
                match = False
        if 'material' in specs:
            if r.get('material', '').lower() != specs['material'].lower():
                match = False
        if match:
            filtered_results.append(r)
            
    return filtered_results

# --- Simple Keyword Search Engine (Fallback when AI libraries are not available) ---
class SimpleKeywordSearchEngine:
    """
    A simple keyword-based search engine that works without AI libraries.
    This serves as a fallback when advanced semantic search is not available.
    """
    
    def __init__(self, parts: List[Dict[str, Any]]):
        self.parts = parts
        print(f"✅ Simple keyword search engine initialized with {len(parts)} parts")
    
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
    
    def search(self, query: str, top_k: int = 5, min_similarity: float = 0.1) -> List[Dict[str, Any]]:
        """Perform keyword-based search"""
        if not query.strip():
            return []
        
        query_terms = query.lower().split()
        results = []
        
        for part in self.parts:
            score = self._calculate_score(part, query_terms)
            if score > 0:
                part_copy = part.copy()
                part_copy['similarity'] = min(score / len(query_terms), 1.0)
                results.append(part_copy)
        
        # Sort by score and return top results
        results = sorted(results, key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def direct_or_semantic_search(self, query: str, top_k: int = 5, min_similarity: float = 0.1) -> List[Dict[str, Any]]:
        """Perform direct keyword search"""
        return self.search(query, top_k, min_similarity)
    
    def suggest(self, query: str, limit: int = 5) -> List[str]:
        """Get query suggestions based on available data"""
        if not fuzzy_process:
            # Simple fallback suggestions
            suggestions = []
            query_lower = query.lower()
            
            # Extract common terms from parts
            all_terms = set()
            for part in self.parts[:100]:  # Limit for performance
                for field in ['part_name', 'system_name', 'manufacturer']:
                    value = part.get(field, '')
                    if isinstance(value, str) and len(value) > 2:
                        all_terms.add(value)
            
            # Find terms that start with the query
            for term in all_terms:
                if term.lower().startswith(query_lower):
                    suggestions.append(term)
                    if len(suggestions) >= limit:
                        break
            
            return suggestions
        
        # Use fuzzy matching if available
        choices = []
        for part in self.parts:
            choices.extend([
                part.get('part_name', ''),
                part.get('system_name', ''),
                part.get('manufacturer', '')
            ])
        
        choices = [c for c in choices if c and len(c) > 2]
        
        try:
            suggestions = fuzzy_process.extract(query, choices, limit=limit)
            return [s[0] for s in suggestions if s[1] > 60]
        except:
            return []

# Remove OpenAI engine and all switching logic
# Engine selection logic with fallback
print("🔄 Initializing search engine...")
print(f"📊 Available libraries:")
print(f"   - SentenceTransformer: {'✅' if SentenceTransformer else '❌'}")
print(f"   - FAISS: {'✅' if faiss else '❌'}")
print(f"   - NumPy: {'✅' if np else '❌'}")
print(f"   - RapidFuzz: {'✅' if fuzzy_process else '❌'}")

try:
    all_parts = load_all_parts_from_datasets()
    print(f"📦 Loaded {len(all_parts)} parts from dataset")
    
    if SentenceTransformer and faiss and np and len(all_parts) > 0:
        # Try to use advanced semantic search with a simple model
        print("🚀 Attempting to initialize advanced semantic search engine...")
        try:
            semantic_engine = SemanticSearchEngineHF(all_parts, embedding_model_name='all-MiniLM-L6-v2')
            print(f"✅ Advanced semantic engine (HF) initialized successfully with {len(all_parts)} parts")
        except Exception as e:
            print(f"❌ Failed to initialize advanced engine with model download: {e}")
            print("🔄 Trying with fallback to simple search...")
            semantic_engine = SimpleKeywordSearchEngine(all_parts)
            print("✅ Using simple keyword search engine as fallback")
    else:
        missing_libs = []
        if not SentenceTransformer:
            missing_libs.append("sentence_transformers")
        if not faiss:
            missing_libs.append("faiss")
        if not np:
            missing_libs.append("numpy")
        if len(all_parts) == 0:
            missing_libs.append("dataset_files")
        print(f"❌ Advanced semantic engine not available: {missing_libs}")
        semantic_engine = SimpleKeywordSearchEngine(all_parts)
        print("✅ Using simple keyword search engine")
        
except Exception as e:
    print(f"❌ Error initializing search engine: {e}")
    try:
        # Fall back to simple keyword search with sample data
        if not all_parts:
            all_parts = load_all_parts_from_datasets()
        semantic_engine = SimpleKeywordSearchEngine(all_parts)
        print("✅ Using simple keyword search engine as fallback")
    except Exception as e2:
        print(f"❌ Error initializing fallback search engine: {e2}")
        semantic_engine = None
        all_parts = []

@app.route('/')
def conversational_interface():
    """
    Renders the main conversational search interface.

    This is the entry point for the user-facing web page.
    """
    return render_template('conversational_search.html')

# --- Semantic Search First, LLM as Fallback ---
@app.route('/api/search', methods=['POST'])
def api_search():
    """
    Handles conversational search queries from the user.
    """
    if not semantic_engine:
        return jsonify({'error': 'Semantic search engine not available'}), 500
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        start_time = time.time()
        
        # 1. Perform initial semantic search
        semantic_results = semantic_engine.direct_or_semantic_search(query, top_k=20)
        
        # 2. Extract technical specs and filter results
        tech_specs = extract_technical_specs(query)
        if tech_specs:
            final_results = filter_results_by_specs(semantic_results, tech_specs)
        else:
            final_results = semantic_results
            
        suggestions = semantic_engine.suggest(query, limit=5)
        search_time_ms = round((time.time() - start_time) * 1000, 2)
        
        # 3. Generate intelligent response based on the *final* results
        intelligent_response = generate_intelligent_response(query, final_results, search_time_ms, tech_specs)
        
        if not final_results:
            return jsonify({
                'success': False,
                'query': query,
                'intelligent_response': generate_no_results_response(query),
            })

        # 4. Sanitize results for frontend
        sanitized_results = []
        for part in final_results:
            part_copy = dict(part)
            part_copy.pop('similarity', None) # Remove internal score
            part_copy.pop('direct_match', None)
            sanitized_results.append(part_copy)

        response = {
            'success': True,
            'query': query,
            'results': sanitized_results[:10], # Limit to top 10 for display
            'result_count': len(sanitized_results),
            'search_time_ms': search_time_ms,
            'suggestions': suggestions,
            'intelligent_response': intelligent_response,
        }
        return jsonify(response)

    except Exception as e:
        app.logger.error(f"API Search Error: {e}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred. Please try again later.'}), 500

# --- Dynamic Assistant Intro, Example Queries, and Quick Insights ---
@app.route('/api/assistant-intro')
def api_assistant_intro():
    """
    Returns a static assistant intro and questionnaire (no LLM, fully offline).
    """
    if not all_parts:
        return jsonify({'error': 'No dataset loaded'}), 500
    sample = all_parts[0] if all_parts else {}
    intro_json = {
        "greeting": "Welcome to IntelliPart!",
        "intro": "I am your expert assistant for Mahindra automotive parts. You can search for parts by name, number, system, or manufacturer. All search is powered by fast, offline semantic search.",
        "capabilities": [
            "Find parts by description, name, or number",
            "Get suggestions for similar parts",
            "Search by manufacturer or system",
            "View quick dataset insights (offline)"
        ],
        "suggestion": "Try searching for a part name, number, or description."
    }
    return jsonify({"success": True, "assistant_intro": intro_json})

@app.route('/api/example-queries')
def api_example_queries():
    """
    Returns dynamic example queries based on actual dataset (no LLM, fully offline).
    """
    if not all_parts:
        return jsonify({'error': 'No dataset loaded'}), 500
    
    # Generate relevant queries based on actual dataset
    queries = [
        "Show brake pads with friction coefficient above 0.4",
        "Show Mahindra Radiator with Metallic material",
        "Show me Mahindra Radiator for Thar",
        "Show me Mahindra Exhaust System for Marazzo",
        "Show all parts compatible with Marazzo",
        "Show me Mahindra Battery for TUV300",
        "Show Mahindra Radiator with Alloy material",
        "Show me Mahindra Radiator for Marazzo",
        "Find parts made of Aluminized Steel",
        "Show me Mahindra Radiator for TUV300",
        "Show clutch plates with ceramic material",
        "Find radiators with cooling capacity over 15000 BTU",
        "Show well-stocked parts",
        "Show all parts compatible with Alturas",
        "List parts with good condition rating",
        "Show me Mahindra Engine Disc/Flywheel for Marazzo",
        "Show expensive parts over ₹10000",
        "Show all parts compatible with e2o",
        "Find tyres with size 235/65R17",
        "Show me Mahindra Battery for Thar",
        "Show me Mahindra Tyre/Wheel for TUV300",
        "Show me Mahindra Engine Disc/Flywheel for TUV300",
        "Find all Radiator components",
        "Find all Tyre/Wheel components",
        "List batteries with 12V rating"
    ]
    return jsonify({"success": True, "example_queries": queries})

@app.route('/api/quick-insights')
def api_quick_insights():
    """
    Returns quick dataset insights using the actual loaded dataset (no LLM).
    """
    if not all_parts:
        return jsonify({'error': 'No dataset loaded'}), 500
    total_parts = len(all_parts)
    unique_part_numbers = len(set(p.get('part_number') for p in all_parts if p.get('part_number')))
    avg_cost = sum(float(p.get('cost', 0)) for p in all_parts if p.get('cost')) / total_parts if total_parts else 0
    total_stock = sum(int(p.get('stock', 0)) for p in all_parts if p.get('stock'))
    metrics = {
        "total_parts": total_parts,
        "unique_parts": unique_part_numbers,
        "average_cost": round(avg_cost, 2),
        "total_stock": total_stock
    }
    summary = f"Total parts: {total_parts}. Unique part numbers: {unique_part_numbers}. Average cost: ₹{round(avg_cost,2)}. Total stock: {total_stock}."
    return jsonify({'success': True, 'insights': metrics, 'summary': summary})

# --- Update LLM prompt for flexible answer formats ---
# Patch ConversationalEngine._build_llm_prompt to instruct answer formatting
from conversational_search import ConversationalEngine

def patched_build_llm_prompt(self, query: str, search_result: dict, user_language: str = "en") -> str:
    """
    Build a prompt for the LLM that instructs it to first analyze and understand the dataset (provided as JSONL), then answer the user's query as helpfully and contextually as possible.
    The LLM should:
    - Use its own reasoning to interpret the dataset structure and content.
    - Not simply echo top results, but synthesize a valuable, context-aware answer.
    - If the query is ambiguous, ask clarifying questions or suggest next steps.
    - If the query is about the dataset, provide insights or summaries as needed.
    - Always be natural, helpful, and use the user's language.
    - IMPORTANT: The answer must be concise and fit in a single line, unless the user explicitly asks for a list or detailed explanation.
    """
    # Provide a sample of the dataset (first 10 records) for LLM context
    dataset_sample = self.all_parts[:10] if hasattr(self, 'all_parts') else []
    dataset_jsonl = "\n".join(json.dumps(rec, ensure_ascii=False) for rec in dataset_sample)
    prompt = (
        f"You are Mahindra IntelliPart, an expert automotive parts assistant.\n"
        f"Below is a sample of the dataset you have access to (JSONL format, each line is a part record):\n"
        f"{dataset_jsonl}\n"
        f"User Query: {query}\n"
        f"Instructions: First, analyze and understand the dataset structure and content. Then, answer the user's query as helpfully and contextually as possible, using your own reasoning and the dataset context.\n"
        f"- If the query is ambiguous, ask clarifying questions or suggest next steps.\n"
        f"- If the query is about the dataset, provide insights or summaries as needed.\n"
        f"- Always be natural, helpful, and use the user's language ({user_language}).\n"
        f"- If you cannot answer, explain why and suggest what the user can try next.\n"
        f"- IMPORTANT: Your answer must be concise and fit in a single line, unless the user explicitly asks for a list or detailed explanation.\n"
    )
    return prompt

ConversationalEngine._build_llm_prompt = patched_build_llm_prompt

# --- Semantic Search API ---
@app.route('/api/semantic-search', methods=['POST'])
def api_semantic_search():
    if not semantic_engine:
        return jsonify({'error': 'Semantic search engine not available'}), 500
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = int(data.get('top_k', 5))
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        results = semantic_engine.search(query, top_k=top_k)
        suggestions = semantic_engine.suggest(query, limit=5)
        return jsonify({'success': True, 'results': results, 'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Ollama LLM utility ---
def call_ollama_llm(prompt, model="llama3"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        return f"[ERROR: Ollama call failed: {e}]"

@app.route('/api/rag-answer', methods=['POST'])
def api_rag_answer():
    """
    RAG endpoint: fetch top-k records with semantic search, then synthesize an answer using Ollama (local LLM) or OpenAI.
    """
    if not semantic_engine:
        return jsonify({'error': 'Semantic search engine not available'}), 500
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = int(data.get('limit', 5))
        min_similarity = float(data.get('min_similarity', 0.55))
        llm = data.get('llm', 'ollama')  # 'ollama' (default) or 'openai'
        openai_api_key = data.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
            
        # 1. Retrieve top-k records (use direct_or_semantic_search)
        top_k_records = semantic_engine.direct_or_semantic_search(query, top_k=limit, min_similarity=min_similarity)
        if not top_k_records:
            return jsonify({'success': False, 'answer': '', 'results': [], 'error': 'No relevant results found.'})
            
        # 2. Compose prompt for LLM
        context = "\n".join([json.dumps(rec, ensure_ascii=False) for rec in top_k_records])
        prompt = (
            "You are an expert automotive parts assistant. Here is the dataset context:\n"
            f"{context}\n"
            f"User Query: {query}\n"
            "Answer the query using only the dataset context above. Your answer must be concise and fit in a single line, unless the user explicitly asks for a list or detailed explanation. If you don't know, say so."
        )
        
        # 3. Call LLM (Ollama by default)
        if llm == 'openai' and openai and openai_api_key:  # Check if OpenAI is available
            openai.api_key = openai_api_key
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=256,
                    temperature=0.2
                )
                answer = response['choices'][0]['message']['content']
            except Exception as e:
                answer = f"Error calling OpenAI: {str(e)}"
        else:
            answer = call_ollama_llm(prompt, model=data.get('ollama_model', 'llama3'))
            
        # Post-process answer
        if ("list" not in query.lower() and "show" not in query.lower() and 
            "all" not in query.lower() and "details" not in query.lower()):
            answer = answer.split("\n")[0].strip()
            
        # Add dataset sample
        dataset_sample = all_parts[:10] if all_parts else []
        return jsonify({
            'success': True,
            'answer': answer,
            'results': top_k_records,
            'dataset_sample': dataset_sample
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Dataset Sample API ---
@app.route('/api/dataset-sample')
def api_dataset_sample():
    """
    Returns the first N records from the loaded dataset as JSONL (for LLM context, debugging, or UI display).
    """
    if not all_parts:
        return jsonify({'error': 'No dataset loaded'}), 500
    n = int(request.args.get('n', 10))
    sample = all_parts[:n]
    dataset_jsonl = "\n".join(json.dumps(rec, ensure_ascii=False) for rec in sample)
    return jsonify({'success': True, 'sample_jsonl': dataset_jsonl, 'sample': sample, 'count': len(sample)})

# --- AI Intelligence Enhancement Functions ---

def enhance_query_with_ai(query, llm_provider="gemini"):
    """
    Enhance user queries using AI to handle vague, incomplete, or ambiguous requests.
    This demonstrates genuine AI intelligence beyond basic search.
    """
    try:
        enhancement_prompt = f"""
        You are an automotive parts expert. The user has asked: "{query}"
        
        Analyze this query and provide:
        1. Enhanced query terms (if the original is vague or incomplete)
        2. Possible alternative interpretations
        3. Key technical terms that should be included
        4. Relevant part categories to search
        
        Return as JSON:
        {{
            "enhanced_query": "improved search terms",
            "alternatives": ["alt1", "alt2"],
            "technical_terms": ["term1", "term2"],
            "categories": ["category1", "category2"],
            "confidence": 0.85
        }}
        """
        
        if llm_provider == "gemini":
            response = call_gemini(enhancement_prompt)
        else:
            response = call_ollama_llm(enhancement_prompt)
            
        # Try to parse JSON response
        try:
            import json
            enhanced_data = json.loads(response)
            return enhanced_data
        except:
            # Fallback if JSON parsing fails
            return {
                "enhanced_query": query,
                "alternatives": [],
                "technical_terms": [],
                "categories": [],
                "confidence": 0.5
            }
    except Exception as e:
        print(f"Query enhancement error: {e}")
        return {
            "enhanced_query": query,
            "alternatives": [],
            "technical_terms": [],
            "categories": [],
            "confidence": 0.5
        }

def calculate_reusability_score(part_data):
    """
    Calculate intelligent reusability score based on multiple factors.
    This demonstrates AI-driven decision making beyond simple retrieval.
    """
    try:
        score = 0.0
        factors = {}
        
        # Factor 1: Standardization (check if part follows standard naming/coding)
        part_name = part_data.get('part_name', '').lower()
        part_number = part_data.get('part_number', '').lower()
        
        if any(std in part_name for std in ['standard', 'std', 'common', 'universal']):
            score += 0.2
            factors['standardization'] = 0.2
        
        # Factor 2: Material analysis
        material = part_data.get('material', '').lower()
        if any(mat in material for mat in ['steel', 'aluminum', 'plastic', 'rubber']):
            score += 0.15
            factors['material_compatibility'] = 0.15
            
        # Factor 3: Condition assessment
        condition = part_data.get('condition', '').lower()
        if 'good' in condition or 'excellent' in condition:
            score += 0.25
            factors['condition_score'] = 0.25
        elif 'fair' in condition or 'acceptable' in condition:
            score += 0.15
            factors['condition_score'] = 0.15
            
        # Factor 4: Availability
        stock = part_data.get('stock', 0)
        if isinstance(stock, (int, float)) and stock > 0:
            if stock >= 10:
                score += 0.2
                factors['availability'] = 0.2
            elif stock >= 5:
                score += 0.15
                factors['availability'] = 0.15
            else:
                score += 0.1
                factors['availability'] = 0.1
        
        # Factor 5: Cost efficiency
        cost = part_data.get('cost', 0)
        if isinstance(cost, (int, float)) and cost > 0:
            if cost < 100:  # Assuming low cost parts are more reusable
                score += 0.15
                factors['cost_efficiency'] = 0.15
            elif cost < 500:
                score += 0.1
                factors['cost_efficiency'] = 0.1
                
        # Factor 6: System criticality (lower criticality = higher reusability)
        system = part_data.get('system_name', '').lower()
        if any(sys in system for sys in ['interior', 'exterior', 'accessory']):
            score += 0.05
            factors['system_criticality'] = 0.05
            
        return min(score, 1.0), factors
        
    except Exception as e:
        print(f"Reusability calculation error: {e}")
        return 0.5, {}

def generate_inspection_checklist(part_data):
    """
    Generate intelligent inspection checklist based on part type and specifications.
    This demonstrates AI-driven automation and decision support.
    """
    try:
        checklist = []
        part_type = part_data.get('part_name', '').lower()
        material = part_data.get('material', '').lower()
        system = part_data.get('system_name', '').lower()
        
        # Material-specific checks
        if 'metal' in material or 'steel' in material or 'aluminum' in material:
            checklist.extend([
                "Check for corrosion or rust",
                "Inspect for cracks or stress fractures",
                "Verify dimensional accuracy with calipers",
                "Test material hardness if applicable"
            ])
        
        if 'plastic' in material or 'polymer' in material:
            checklist.extend([
                "Check for UV damage or discoloration",
                "Inspect for stress cracks",
                "Verify flexibility and elasticity",
                "Check for chemical degradation"
            ])
            
        if 'rubber' in material or 'elastomer' in material:
            checklist.extend([
                "Check for dry rot or cracking",
                "Test elasticity and compression",
                "Inspect for ozone damage",
                "Verify Shore hardness"
            ])
        
        # System-specific checks
        if 'engine' in system:
            checklist.extend([
                "Check for oil contamination",
                "Verify temperature resistance",
                "Test for pressure tolerance"
            ])
        
        if 'brake' in system:
            checklist.extend([
                "Check for wear patterns",
                "Verify friction material condition",
                "Test heat resistance"
            ])
            
        if 'electrical' in system:
            checklist.extend([
                "Test electrical continuity",
                "Check insulation resistance",
                "Verify connector condition"
            ])
        
        # Generic checks
        checklist.extend([
            "Verify part number matches requirements",
            "Check overall cleanliness",
            "Document inspection date and inspector",
            "Photograph any defects found"
        ])
        
        return list(set(checklist))  # Remove duplicates
        
    except Exception as e:
        print(f"Checklist generation error: {e}")
        return ["Perform visual inspection", "Check part number", "Document condition"]

def detect_potential_duplicates(query_part, all_parts, threshold=0.8):
    """
    Intelligent duplicate detection using multiple similarity metrics.
    This demonstrates AI-driven quality control and data management.
    """
    try:
        potential_duplicates = []
        
        if not semantic_engine:
            return potential_duplicates
            
        # Get semantic similarity
        semantic_results = semantic_engine.search(query_part, top_k=10, min_similarity=threshold)
        
        for result in semantic_results:
            similarity_score = result.get('similarity', 0)
            
            # Additional similarity checks
            name_similarity = 0
            if 'part_name' in result and query_part:
                name_similarity = fuzzy_process.extractOne(query_part, [result['part_name']])[1] / 100
            
            # Combined similarity score
            combined_score = (similarity_score * 0.7) + (name_similarity * 0.3)
            
            if combined_score >= threshold:
                potential_duplicates.append({
                    'part': result,
                    'similarity_score': combined_score,
                    'semantic_score': similarity_score,
                    'name_similarity': name_similarity,
                    'confidence': 'high' if combined_score >= 0.9 else 'medium'
                })
        
        return sorted(potential_duplicates, key=lambda x: x['similarity_score'], reverse=True)
        
    except Exception as e:
        print(f"Duplicate detection error: {e}")
        return []

# --- Enhanced AI-Powered API Endpoints ---

@app.route('/api/intelligent-search', methods=['POST'])
def api_intelligent_search():
    """
    Enhanced search with AI query understanding, reusability scoring, and intelligent recommendations.
    This demonstrates genuine AI beyond basic search.
    """
    if not semantic_engine:
        return jsonify({'error': 'Semantic search engine not available'}), 500
        
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        enable_ai_enhancement = data.get('enable_ai_enhancement', True)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
            
        start_time = time.time()
        
        # Step 1: AI Query Enhancement
        enhanced_query_data = None
        if enable_ai_enhancement:
            enhanced_query_data = enhance_query_with_ai(query)
            search_query = enhanced_query_data.get('enhanced_query', query)
        else:
            search_query = query
            
        # Step 2: Semantic Search
        semantic_results = semantic_engine.direct_or_semantic_search(
            search_query, 
            top_k=10, 
            min_similarity=0.35
        )
        
        # Step 3: AI-Enhanced Results Processing
        intelligent_results = []
        for result in semantic_results:
            # Calculate reusability score
            reusability_score, reusability_factors = calculate_reusability_score(result)
            
            # Generate inspection checklist
            inspection_checklist = generate_inspection_checklist(result)
            
            # Detect potential duplicates
            duplicates = detect_potential_duplicates(
                result.get('part_name', ''), 
                all_parts, 
                threshold=0.75
            )
            
            enhanced_result = {
                **result,
                'ai_insights': {
                    'reusability_score': round(reusability_score, 2),
                    'reusability_factors': reusability_factors,
                    'inspection_checklist': inspection_checklist,
                    'potential_duplicates': len(duplicates),
                    'recommendation': 'highly_recommended' if reusability_score > 0.8 else 'recommended' if reusability_score > 0.6 else 'consider_with_caution'
                }
            }
            
            # Remove sensitive internal data
            enhanced_result.pop('similarity', None)
            enhanced_result.pop('direct_match', None)
            
            intelligent_results.append(enhanced_result)
        
        search_time = time.time() - start_time
        
        response = {
            'success': True,
            'query': query,
            'ai_enhancement': enhanced_query_data,
            'results': intelligent_results,
            'result_count': len(intelligent_results),
            'search_time_ms': round(search_time * 1000, 2),
            'ai_insights': {
                'total_highly_recommended': sum(1 for r in intelligent_results if r['ai_insights']['recommendation'] == 'highly_recommended'),
                'average_reusability_score': round(sum(r['ai_insights']['reusability_score'] for r in intelligent_results) / len(intelligent_results), 2) if intelligent_results else 0
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/duplicate-analysis', methods=['POST'])
def api_duplicate_analysis():
    """
    Intelligent duplicate detection and analysis using AI-powered similarity matching.
    """
    if not semantic_engine:
        return jsonify({'error': 'Semantic search engine not available'}), 500
        
    try:
        data = request.get_json()
        part_description = data.get('part_description', '').strip()
        threshold = float(data.get('threshold', 0.8))
        
        if not part_description:
            return jsonify({'error': 'Part description is required'}), 400
            
        start_time = time.time()
        
        # Detect duplicates
        duplicates = detect_potential_duplicates(part_description, all_parts, threshold)
        
        analysis_time = time.time() - start_time
        
        # Generate AI insights
        ai_analysis = {
            'duplicate_risk': 'high' if len(duplicates) > 3 else 'medium' if len(duplicates) > 1 else 'low',
            'confidence_distribution': {
                'high': sum(1 for d in duplicates if d['confidence'] == 'high'),
                'medium': sum(1 for d in duplicates if d['confidence'] == 'medium')
            },
            'recommendation': 'Review existing parts before creating new' if len(duplicates) > 0 else 'No similar parts found - safe to create new'
        }
        
        return jsonify({
            'success': True,
            'input_description': part_description,
            'duplicates_found': len(duplicates),
            'duplicates': duplicates,
            'ai_analysis': ai_analysis,
            'analysis_time_ms': round(analysis_time * 1000, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reusability-assessment', methods=['POST'])
def api_reusability_assessment():
    """
    AI-powered reusability assessment with detailed scoring and recommendations.
    """
    try:
        data = request.get_json()
        part_data = data.get('part_data', {})
        
        if not part_data:
            return jsonify({'error': 'Part data is required'}), 400
            
        start_time = time.time()
        
        # Calculate reusability score
        reusability_score, factors = calculate_reusability_score(part_data)
        
        # Generate inspection checklist
        checklist = generate_inspection_checklist(part_data)
        
        # AI-powered recommendations
        recommendations = []
        if reusability_score > 0.8:
            recommendations.append("Highly recommended for reuse - excellent condition and compatibility")
        elif reusability_score > 0.6:
            recommendations.append("Good candidate for reuse - perform thorough inspection")
        elif reusability_score > 0.4:
            recommendations.append("Consider reuse with caution - additional validation required")
        else:
            recommendations.append("Not recommended for reuse - consider procurement of new part")
            
        # Add specific recommendations based on factors
        if factors.get('condition_score', 0) < 0.15:
            recommendations.append("Part condition needs improvement - consider refurbishment")
        if factors.get('availability', 0) < 0.1:
            recommendations.append("Limited availability - consider alternative parts")
        if factors.get('cost_efficiency', 0) > 0.1:
            recommendations.append("Cost-effective option - good value for reuse")
            
        assessment_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'part_data': part_data,
            'reusability_score': round(reusability_score, 2),
            'score_breakdown': factors,
            'inspection_checklist': checklist,
            'recommendations': recommendations,
            'assessment_time_ms': round(assessment_time * 1000, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/design-optimization', methods=['POST'])
def api_design_optimization():
    """
    AI-powered design optimization suggestions based on part requirements.
    """
    try:
        data = request.get_json()
        requirements = data.get('requirements', {})
        context = data.get('context', '')
        
        if not requirements and not context:
            return jsonify({'error': 'Requirements or context is required'}), 400
            
        start_time = time.time()
        
        # Generate optimization prompt
        optimization_prompt = f"""
        As an automotive design optimization expert, analyze the following requirements:
        Context: {context}
        Requirements: {json.dumps(requirements, indent=2)}
        
        Provide design optimization suggestions in JSON format:
        {{
            "optimization_suggestions": [
                {{
                    "category": "material_optimization",
                    "suggestion": "specific suggestion",
                    "impact": "cost_saving|performance_improvement|sustainability",
                    "priority": "high|medium|low"
                }}
            ],
            "alternative_approaches": ["approach1", "approach2"],
            "sustainability_improvements": ["improvement1", "improvement2"],
            "cost_optimization": ["cost_saving1", "cost_saving2"]
        }}
        """
        
        # Get AI suggestions
        ai_response = call_gemini(optimization_prompt)
        
        try:
            optimization_data = json.loads(ai_response)
        except:
            # Fallback if JSON parsing fails
            optimization_data = {
                "optimization_suggestions": [
                    {
                        "category": "general",
                        "suggestion": "Consider standardized parts to reduce inventory complexity",
                        "impact": "cost_saving",
                        "priority": "medium"
                    }
                ],
                "alternative_approaches": ["Standard part substitution", "Material optimization"],
                "sustainability_improvements": ["Increase recyclability", "Reduce material usage"],
                "cost_optimization": ["Bulk purchasing", "Supplier consolidation"]
            }
        
        optimization_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'requirements': requirements,
            'context': context,
            'optimization_data': optimization_data,
            'processing_time_ms': round(optimization_time * 1000, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Intelligent Response Generation ---
def generate_intelligent_response(query, results, search_time, tech_specs=None):
    """
    Generate intelligent, conversational response based on search results.
    """
    try:
        # Extract key information from query
        query_lower = query.lower()
        
        # Determine response type based on results
        if not results:
            return generate_no_results_response(query)
        
        # Extract specific model/part from query
        extracted_model = extract_vehicle_model(query)
        extracted_part = extract_part_type(query)
        
        # Generate personalized greeting and response
        response_parts = []
        
        # Contextual greeting based on search
        if extracted_model and extracted_part:
            if len(results) == 1:
                response_parts.append(f"Hi! I found exactly what you're looking for! 🎯")
                response_parts.append(f"Here's the perfect {extracted_part} for your {extracted_model}:")
            else:
                response_parts.append(f"Hi! Great news! I found {len(results)} excellent {extracted_part} options for your {extracted_model}! ✨")
        elif extracted_part:
            response_parts.append(f"Hi! I found {len(results)} great {extracted_part} options for you! 👍")
        elif extracted_model:
            response_parts.append(f"Hi! I found {len(results)} compatible parts for your {extracted_model}! 🚗")
        else:
            response_parts.append(f"Hi! I found {len(results)} excellent matches for your search! ✨")
        
        if tech_specs:
            spec_details = []
            if 'friction_coefficient' in tech_specs:
                spec_details.append(f"friction coefficient > {tech_specs['friction_coefficient']}")
            if 'material' in tech_specs:
                spec_details.append(f"material: {tech_specs['material']}")
            
            if spec_details:
                response_parts.append(f"🔍 **Filters Applied**: {', '.join(spec_details)}")

        # Add results summary with recommendations
        if results:
            best_result = results[0]
            price_range = get_price_range(results)
            stock_info = get_stock_summary(results)
            
            # Highlight the best option
            best_part_name = best_result.get('part_name', 'Top match')
            best_cost = best_result.get('cost', 'N/A')
            best_stock = best_result.get('stock', 0)
            
            response_parts.append(f"🏆 **Top Recommendation**: {best_part_name}")
            if best_cost != 'N/A':
                response_parts.append(f"💰 **Price**: ₹{best_cost}")
            
            # Stock availability message
            if best_stock > 20:
                response_parts.append("✅ **Excellent availability** - Ready for immediate dispatch!")
            elif best_stock > 5:
                response_parts.append("⚠️ **Good availability** - In stock, order soon!")
            elif best_stock > 0:
                response_parts.append("🚨 **Limited stock** - Only a few left, order now!")
            else:
                response_parts.append("❌ **Out of stock** - Please check alternatives below")
            
            # Add helpful insights
            if len(results) > 1:
                cheapest = min(results, key=lambda x: float(x.get('cost', 0)))
                most_expensive = max(results, key=lambda x: float(x.get('cost', 0)))
                
                if cheapest != best_result:
                    response_parts.append(f"💰 **Budget Option**: {cheapest['part_name']} at ₹{cheapest['cost']}")
                
                if float(most_expensive.get('cost', 0)) > float(cheapest.get('cost', 0)) * 1.5:
                    response_parts.append(f"📊 **Price Range**: ₹{cheapest['cost']} - ₹{most_expensive['cost']}")
        
        # Performance note
        response_parts.append(f"⚡ **Search completed in {search_time:.2f}ms** using AI semantic matching")
        
        return "\n\n".join(response_parts)
        
    except Exception as e:
        return f"Hi! I found {len(results)} results for your query. Here are the best matches:"

def generate_no_results_response(query):
    """
    Generate helpful response when no results are found.
    """
    extracted_model = extract_vehicle_model(query)
    extracted_part = extract_part_type(query)
    
    response_parts = []
    
    if extracted_model and extracted_part:
        response_parts.append(f"Hi! I'm sorry, but I couldn't find any {extracted_part} specifically for {extracted_model} in our current inventory. 🔍")
        response_parts.append("**But don't worry! Here's what I can do for you:**")
        response_parts.append(f"🔄 **Try searching for '{extracted_part}' without the specific model** - many parts are cross-compatible!")
        response_parts.append(f"🚗 **Check compatibility** - {extracted_model} parts might work with similar models")
        response_parts.append("📞 **Special orders** - Our parts team can source hard-to-find components")
        response_parts.append("💡 **Alternative suggestion** - Try searching for the part by its system (e.g., 'braking system', 'engine parts')")
    elif extracted_model:
        response_parts.append(f"Hi! I couldn't find specific matches for {extracted_model} with your search terms. 🔍")
        response_parts.append("**Let me help you find what you need:**")
        response_parts.append(f"🔍 **Try being more specific** - What part do you need for your {extracted_model}?")
        response_parts.append("📋 **Browse categories** - Check our recommended searches below")
        response_parts.append("🔄 **Alternative search** - Try 'Mahindra [part name]' format")
    elif extracted_part:
        response_parts.append(f"Hi! I couldn't find the specific {extracted_part} you're looking for. 🔍")
        response_parts.append("**Here are some suggestions:**")
        response_parts.append(f"🚗 **Add vehicle model** - Try '{extracted_part} for [your vehicle model]'")
        response_parts.append("💡 **Check spelling** - Make sure the part name is correct")
        response_parts.append("📋 **Browse similar parts** - Check our recommended queries below")
    else:
        response_parts.append("Hi! I couldn't find exact matches for your search. 🔍")
        response_parts.append("**Let me help you find what you need:**")
        response_parts.append("🔍 **Try different keywords** - Use specific part names or vehicle models")
        response_parts.append("📋 **Check our popular searches** - Browse recommended queries below")
        response_parts.append("💬 **Be more specific** - Include model, year, or system information")
    
    response_parts.append("🎯 **Quick tip**: Our AI works best with queries like 'Thar brake pads' or 'Marazzo exhaust system'")
    
    return "\n\n".join(response_parts)

def extract_vehicle_model(query):
    """Extract vehicle model from query"""
    models = ["Thar", "Marazzo", "XUV500", "Scorpio", "TUV300", "Alturas", "e2o", "Bolero", "XUV300", "Marazo", "Mahindra"]
    query_lower = query.lower()
    for model in models:
        if model.lower() in query_lower:
            # Handle common misspellings
            if model.lower() == "marazo":
                return "Marazzo"
            return model
    return None

def extract_part_type(query):
    """Extract part type from query"""
    parts = ["radiator", "brake pad", "exhaust system", "battery", "tyre", "wheel", "engine", "disc", "flywheel"]
    query_lower = query.lower()
    for part in parts:
        if part.lower() in query_lower:
            return part
    return None

def get_price_range(results):
    """Get price range summary"""
    if not results:
        return "No pricing info"
    
    prices = [float(r.get('cost', 0)) for r in results if r.get('cost')]
    if not prices:
        return "Pricing available on request"
    
    min_price = min(prices)
    max_price = max(prices)
    
    if min_price == max_price:
        return f"₹{min_price:.2f}"
    else:
        return f"₹{min_price:.2f} - ₹{max_price:.2f}"

def get_stock_summary(results):
    """Get stock availability summary"""
    if not results:
        return "No stock info"
    
    total_stock = sum(int(r.get('stock', 0)) for r in results)
    available_items = len([r for r in results if int(r.get('stock', 0)) > 0])
    
    if total_stock == 0:
        return "Out of stock"
    elif available_items == len(results):
        return f"{total_stock} units available"
    else:
        return f"{available_items}/{len(results)} items in stock"

# Main execution block
if __name__ == "__main__":
    # Initialize the search engine
    print("🚀 Starting IntelliPart Conversational Web App...")
    print(f"📊 Loaded {len(load_all_parts_from_datasets())} parts from dataset")
    print("🌐 Starting Flask server...")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
