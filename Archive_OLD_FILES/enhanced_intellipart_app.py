"""
Enhanced IntelliPart Web Application with Analytics Dashboard
Combines search functionality with comprehensive analytics
"""

from flask import Flask, render_template, request, jsonify
import json
import re
from typing import List, Dict, Any
import time
from collections import defaultdict
import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import our analytics dashboard
from IntelliPart.analytics_dashboard import PartsAnalytics

class EnhancedIntelliPartApp:
    def __init__(self, jsonl_path: str):
        """Enhanced app with search + analytics."""
        self.parts = []
        self.field_values = defaultdict(set)
        self.vectorizer = None
        self.tfidf_matrix = None
        self.embeddings_file = 'enhanced_tfidf_embeddings.pkl'
        
        print("Loading data...")
        self.load_data(jsonl_path)
        
        print("Initializing AI search...")
        self.init_ai_search()
        
        print("Initializing analytics...")
        self.analytics = PartsAnalytics(jsonl_path)
        
        print(f"Enhanced IntelliPart ready with {len(self.parts)} parts!")
    
    def load_data(self, jsonl_path: str):
        """Load data from JSONL file."""
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    part = json.loads(line)
                    self.parts.append(part)
                    
                    for key, value in part.items():
                        if isinstance(value, str):
                            self.field_values[key].add(value)
    
    def init_ai_search(self):
        """Initialize AI search capabilities."""
        if os.path.exists(self.embeddings_file):
            self.load_ai_embeddings()
        else:
            self.generate_ai_embeddings()
    
    def create_part_text(self, part: Dict[str, Any]) -> str:
        """Create searchable text from part data."""
        text_parts = []
        important_fields = [
            'part_name', 'part_type', 'system', 'sub_system', 
            'manufacturer', 'type', 'material', 'feature'
        ]
        
        for field in important_fields:
            if field in part and part[field]:
                text = str(part[field]).lower()
                text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
                text_parts.append(text)
        
        return ' '.join(text_parts)
    
    def generate_ai_embeddings(self):
        """Generate TF-IDF embeddings."""
        part_texts = [self.create_part_text(part) for part in self.parts]
        
        self.vectorizer = TfidfVectorizer(
            max_features=3000,
            min_df=2,
            max_df=0.95,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(part_texts)
        self.save_ai_embeddings()
    
    def save_ai_embeddings(self):
        """Save AI embeddings."""
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'tfidf_matrix': self.tfidf_matrix
            }, f)
    
    def load_ai_embeddings(self):
        """Load AI embeddings."""
        with open(self.embeddings_file, 'rb') as f:
            data = pickle.load(f)
            self.vectorizer = data['vectorizer']
            self.tfidf_matrix = data['tfidf_matrix']
    
    def enhanced_search(self, 
                       query: str = "",
                       search_type: str = "smart",
                       system: str = "",
                       manufacturer: str = "",
                       min_cost: float = 0,
                       max_cost: float = float('inf'),
                       min_stock: int = 0,
                       limit: int = 20) -> Dict[str, Any]:
        """Enhanced search with better scoring."""
        start_time = time.time()
        
        if search_type == "keyword":
            results = self._keyword_search(query, limit * 2)
        elif search_type == "ai":
            results = self._ai_search(query, limit * 2)
        elif search_type == "fuzzy":
            results = self._fuzzy_search(query, limit * 2)
        else:  # smart
            results = self._smart_search(query, limit * 2)
        
        # Apply filters
        filtered_results = []
        for part in results:
            if system and part.get('system', '').lower() != system.lower():
                continue
            if manufacturer and part.get('manufacturer', '').lower() != manufacturer.lower():
                continue
            
            try:
                cost_str = part.get('cost', '0')
                cost_num = float(re.sub(r'[^\d.]', '', str(cost_str)))
                if not (min_cost <= cost_num <= max_cost):
                    continue
            except:
                pass
            
            try:
                stock = int(part.get('stock', 0))
                if stock < min_stock:
                    continue
            except:
                pass
            
            filtered_results.append(part)
        
        search_time = time.time() - start_time
        
        return {
            'results': filtered_results[:limit],
            'total_found': len(filtered_results),
            'search_time': round(search_time, 3),
            'query': query,
            'search_type': search_type,
            'filters': {
                'system': system,
                'manufacturer': manufacturer,
                'min_cost': min_cost if min_cost > 0 else None,
                'max_cost': max_cost if max_cost < float('inf') else None,
                'min_stock': min_stock if min_stock > 0 else None
            }
        }
    
    def _keyword_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Enhanced keyword search with field weighting."""
        query_lower = query.lower()
        results = []
        
        # Field weights for scoring
        field_weights = {
            'part_name': 3.0,
            'part_number': 2.5,
            'part_type': 2.0,
            'manufacturer': 1.5,
            'system': 1.5,
            'feature': 1.0
        }
        
        for part in self.parts:
            match_score = 0
            for key, value in part.items():
                if isinstance(value, str) and query_lower in value.lower():
                    weight = field_weights.get(key, 0.5)
                    match_score += weight
            
            if match_score > 0:
                part_copy = part.copy()
                part_copy['_score'] = match_score
                part_copy['_score_type'] = 'keyword'
                results.append(part_copy)
        
        results.sort(key=lambda x: x['_score'], reverse=True)
        return results[:limit]
    
    def _ai_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """AI search with improved threshold."""
        if not self.vectorizer:
            return self._keyword_search(query, limit)
        
        clean_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query.lower())
        query_vector = self.vectorizer.transform([clean_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        results = []
        for i, similarity in enumerate(similarities):
            if similarity > 0.05:
                part = self.parts[i].copy()
                part['_score'] = float(similarity)
                part['_score_type'] = 'ai'
                results.append(part)
        
        results.sort(key=lambda x: x['_score'], reverse=True)
        return results[:limit]
    
    def _fuzzy_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fuzzy search for typo tolerance."""
        query_words = query.lower().split()
        results = []
        
        for part in self.parts:
            fuzzy_score = 0
            part_text = ' '.join([str(v).lower() for v in part.values() if isinstance(v, str)])
            
            for query_word in query_words:
                if len(query_word) < 3:
                    continue
                
                # Simple fuzzy matching - check if word is substring or similar
                for part_word in part_text.split():
                    if query_word in part_word or part_word in query_word:
                        fuzzy_score += 1
                    elif len(query_word) > 3 and self._similar_words(query_word, part_word):
                        fuzzy_score += 0.5
            
            if fuzzy_score > 0:
                part_copy = part.copy()
                part_copy['_score'] = fuzzy_score
                part_copy['_score_type'] = 'fuzzy'
                results.append(part_copy)
        
        results.sort(key=lambda x: x['_score'], reverse=True)
        return results[:limit]
    
    def _similar_words(self, word1: str, word2: str) -> bool:
        """Simple similarity check for fuzzy matching."""
        if len(word1) < 3 or len(word2) < 3:
            return False
        
        # Check if words share significant portion
        shared_chars = set(word1) & set(word2)
        return len(shared_chars) >= min(3, len(word1) // 2)
    
    def _smart_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Enhanced smart search combining multiple methods."""
        # Get results from different methods
        ai_results = self._ai_search(query, limit)
        keyword_results = self._keyword_search(query, limit)
        fuzzy_results = self._fuzzy_search(query, limit // 2)
        
        # Combine with weighted scoring
        combined = {}
        
        # AI results (higher weight)
        for result in ai_results:
            part_id = result.get('part_number', str(id(result)))
            combined[part_id] = result
            combined[part_id]['_score'] = result['_score'] * 0.5
            combined[part_id]['_score_type'] = 'smart'
        
        # Keyword results (medium weight)
        for result in keyword_results:
            part_id = result.get('part_number', str(id(result)))
            if part_id in combined:
                combined[part_id]['_score'] += result['_score'] * 0.3
            else:
                result['_score'] = result['_score'] * 0.3
                result['_score_type'] = 'smart'
                combined[part_id] = result
        
        # Fuzzy results (lower weight)
        for result in fuzzy_results:
            part_id = result.get('part_number', str(id(result)))
            if part_id in combined:
                combined[part_id]['_score'] += result['_score'] * 0.2
            else:
                result['_score'] = result['_score'] * 0.2
                result['_score_type'] = 'smart'
                combined[part_id] = result
        
        final_results = list(combined.values())
        final_results.sort(key=lambda x: x['_score'], reverse=True)
        return final_results[:limit]
    
    def get_suggestions(self, partial: str, max_suggestions: int = 5) -> List[str]:
        """Enhanced auto-suggestions."""
        if len(partial) < 2:
            return []
        
        suggestions = set()
        partial_lower = partial.lower()
        
        # Get suggestions from vocabulary
        if self.vectorizer:
            vocabulary = self.vectorizer.get_feature_names_out()
            for term in vocabulary:
                if term.startswith(partial_lower) and len(term) > len(partial):
                    suggestions.add(term)
                    if len(suggestions) >= max_suggestions:
                        break
        
        # Get suggestions from part data
        for part in self.parts:
            for key, value in part.items():
                if isinstance(value, str):
                    words = value.lower().split()
                    for word in words:
                        if word.startswith(partial_lower) and len(word) > len(partial):
                            suggestions.add(word)
                            if len(suggestions) >= max_suggestions * 2:
                                break
        
        return list(suggestions)[:max_suggestions]
    
    def find_similar(self, part_number: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar parts with better matching."""
        target_index = None
        for i, part in enumerate(self.parts):
            if part.get('part_number') == part_number:
                target_index = i
                break
        
        if target_index is None or not self.tfidf_matrix:
            return []
        
        target_vector = self.tfidf_matrix[target_index]
        similarities = cosine_similarity(target_vector, self.tfidf_matrix)[0]
        
        results = []
        for i, similarity in enumerate(similarities):
            if i != target_index and similarity > 0.1:
                part = self.parts[i].copy()
                part['_score'] = float(similarity)
                part['_score_type'] = 'similarity'
                results.append(part)
        
        results.sort(key=lambda x: x['_score'], reverse=True)
        return results[:top_k]
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get enhanced filter options."""
        return {
            'systems': sorted(list(self.field_values['system'])),
            'manufacturers': sorted(list(self.field_values['manufacturer'])),
            'part_types': sorted(list(self.field_values['part_type'])),
            'materials': sorted(list(self.field_values.get('material', set()))),
            'features': sorted(list(self.field_values.get('feature', set())))
        }
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        return self.analytics.generate_comprehensive_report()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced statistics."""
        costs = []
        for part in self.parts:
            try:
                cost_str = part.get('cost', '0')
                cost_num = float(re.sub(r'[^\d.]', '', str(cost_str)))
                costs.append(cost_num)
            except:
                pass
        
        return {
            'total_parts': len(self.parts),
            'systems_count': len(self.field_values['system']),
            'manufacturers_count': len(self.field_values['manufacturer']),
            'ai_enabled': self.vectorizer is not None,
            'cost_range': {
                'min': min(costs) if costs else 0,
                'max': max(costs) if costs else 0,
                'avg': round(sum(costs)/len(costs), 2) if costs else 0
            },
            'search_methods': ['keyword', 'ai', 'fuzzy', 'smart']
        }

# Initialize Flask app
app = Flask(__name__)
enhanced_app = EnhancedIntelliPartApp("data/training Dataset.jsonl")

@app.route('/')
def index():
    """Enhanced main page."""
    stats = enhanced_app.get_stats()
    filter_options = enhanced_app.get_filter_options()
    return render_template('enhanced.html', stats=stats, filter_options=filter_options)

@app.route('/analytics')
def analytics():
    """Analytics dashboard page."""
    analytics_data = enhanced_app.get_analytics_summary()
    return render_template('analytics.html', analytics=analytics_data)

@app.route('/search', methods=['POST'])
def search():
    """Enhanced search endpoint."""
    data = request.get_json()
    
    query = data.get('query', '')
    search_type = data.get('search_type', 'smart')
    system = data.get('system', '')
    manufacturer = data.get('manufacturer', '')
    min_cost = float(data.get('min_cost', 0)) if data.get('min_cost') else 0
    max_cost = float(data.get('max_cost', float('inf'))) if data.get('max_cost') else float('inf')
    min_stock = int(data.get('min_stock', 0)) if data.get('min_stock') else 0
    
    results = enhanced_app.enhanced_search(
        query=query,
        search_type=search_type,
        system=system,
        manufacturer=manufacturer,
        min_cost=min_cost,
        max_cost=max_cost,
        min_stock=min_stock
    )
    
    return jsonify(results)

@app.route('/suggestions', methods=['POST'])
def suggestions():
    """Enhanced auto-suggestions."""
    data = request.get_json()
    partial = data.get('partial', '')
    suggestions = enhanced_app.get_suggestions(partial)
    return jsonify({'suggestions': suggestions})

@app.route('/similar/<part_number>')
def similar(part_number):
    """Enhanced similar parts."""
    results = enhanced_app.find_similar(part_number)
    return jsonify({'similar_parts': results})

@app.route('/analytics/data')
def analytics_data():
    """Get analytics data as JSON."""
    return jsonify(enhanced_app.get_analytics_summary())

if __name__ == '__main__':
    print("🚀 Starting Enhanced IntelliPart with Analytics...")
    print("🔍 Features: Advanced Search + Analytics Dashboard")
    print("🌟 Search Types: Keyword, AI, Fuzzy, Smart")
    print("📊 Analytics: Comprehensive insights and reports")
    print("🔗 Open: http://localhost:5002")
    app.run(debug=True, host='0.0.0.0', port=5002)
