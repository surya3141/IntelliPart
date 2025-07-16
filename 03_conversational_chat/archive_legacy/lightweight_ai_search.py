import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import time
from typing import List, Dict, Any
import re

class LightweightAISearch:
    def __init__(self, parts: list):
        """Initialize lightweight AI search using TF-IDF."""
        self.parts = parts
        self.vectorizer = None
        self.tfidf_matrix = None
        self.embeddings_file = 'tfidf_embeddings.pkl'
        print(f"Loading {len(self.parts)} parts...")
        # Load or generate TF-IDF embeddings
        if os.path.exists(self.embeddings_file):
            print("Loading pre-computed TF-IDF embeddings...")
            self.load_embeddings()
        else:
            print("Generating TF-IDF embeddings...")
            self.generate_embeddings()
        print(f"Lightweight AI search ready with {len(self.parts)} parts!")

    def create_part_text(self, part: Dict[str, Any]) -> str:
        """Create searchable text from part data."""
        text_parts = []
        
        # Important fields for search
        important_fields = [
            'part_name', 'part_type', 'system', 'sub_system', 
            'manufacturer', 'type', 'material', 'feature',
            'part_number', 'oem_part_number'
        ]
        
        for field in important_fields:
            if field in part and part[field]:
                # Clean and add text
                text = str(part[field]).lower()
                text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)  # Remove special chars
                text_parts.append(text)
        
        # Add specifications as searchable text
        specs = []
        for key, value in part.items():
            if key not in important_fields and isinstance(value, str):
                clean_value = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(value).lower())
                specs.append(clean_value)
        
        if specs:
            text_parts.extend(specs)
        
        return ' '.join(text_parts)
    
    def generate_embeddings(self):
        """Generate TF-IDF embeddings for all parts."""
        print("Creating searchable text for parts...")
        part_texts = [self.create_part_text(part) for part in self.parts]
        
        print("Generating TF-IDF vectors...")
        start_time = time.time()
        
        # TF-IDF with optimized parameters
        self.vectorizer = TfidfVectorizer(
            max_features=5000,      # Limit vocabulary size
            min_df=2,              # Ignore rare terms
            max_df=0.95,           # Ignore very common terms
            stop_words='english',   # Remove stop words
            ngram_range=(1, 2),    # Use unigrams and bigrams
            lowercase=True,
            strip_accents='ascii'
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(part_texts)
        
        end_time = time.time()
        print(f"TF-IDF embeddings generated in {end_time - start_time:.2f} seconds")
        
        # Save embeddings
        self.save_embeddings()
    
    def save_embeddings(self):
        """Save TF-IDF model and matrix to disk."""
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'tfidf_matrix': self.tfidf_matrix
            }, f)
        print(f"TF-IDF embeddings saved to {self.embeddings_file}")
    
    def load_embeddings(self):
        """Load TF-IDF model and matrix from disk."""
        with open(self.embeddings_file, 'rb') as f:
            data = pickle.load(f)
            self.vectorizer = data['vectorizer']
            self.tfidf_matrix = data['tfidf_matrix']
        print("TF-IDF embeddings loaded from cache")
    
    def ai_search(self, query: str, top_k: int = 10, threshold: float = 0.05) -> List[Dict[str, Any]]:
        """Perform AI search using TF-IDF cosine similarity."""
        start_time = time.time()
        
        # Clean and vectorize query
        clean_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query.lower())
        query_vector = self.vectorizer.transform([clean_query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # Get top results above threshold
        results = []
        for i, similarity in enumerate(similarities):
            if similarity > threshold:
                part = self.parts[i].copy()
                part['_ai_score'] = float(similarity)
                results.append(part)
        
        # Sort by similarity
        results.sort(key=lambda x: x['_ai_score'], reverse=True)
        
        search_time = time.time() - start_time
        print(f"AI search completed in {search_time:.3f}s - Found {len(results)} results")
        
        return results[:top_k]
    
    def smart_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Smart search combining multiple approaches."""
        # AI search
        ai_results = self.ai_search(query, top_k * 2)
        
        # Keyword search for exact matches
        keyword_results = self.keyword_search(query, top_k)
        
        # Combine results
        combined = {}
        
        # Add AI results
        for result in ai_results:
            part_id = result.get('part_number', str(id(result)))
            combined[part_id] = result
            combined[part_id]['_smart_score'] = result['_ai_score'] * 0.8
        
        # Boost exact keyword matches
        for result in keyword_results:
            part_id = result.get('part_number', str(id(result)))
            if part_id in combined:
                combined[part_id]['_smart_score'] += result.get('_match_score', 0) * 0.2
            else:
                result['_smart_score'] = result.get('_match_score', 0) * 0.2
                combined[part_id] = result
        
        # Sort by smart score
        final_results = list(combined.values())
        final_results.sort(key=lambda x: x.get('_smart_score', 0), reverse=True)
        
        return final_results[:top_k]
    
    def keyword_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Simple keyword search."""
        query_lower = query.lower()
        results = []
        
        for part in self.parts:
            match_score = 0
            for key, value in part.items():
                if isinstance(value, str) and query_lower in value.lower():
                    match_score += 1
            
            if match_score > 0:
                part_copy = part.copy()
                part_copy['_match_score'] = match_score
                results.append(part_copy)
        
        results.sort(key=lambda x: x['_match_score'], reverse=True)
        return results[:top_k]
    
    def find_similar_parts(self, part_number: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find parts similar to a given part using AI."""
        # Find the target part
        target_index = None
        for i, part in enumerate(self.parts):
            if part.get('part_number') == part_number:
                target_index = i
                break
        
        if target_index is None:
            print(f"Part {part_number} not found")
            return []
        
        # Get similarities
        target_vector = self.tfidf_matrix[target_index]
        similarities = cosine_similarity(target_vector, self.tfidf_matrix)[0]
        
        # Get similar parts (excluding the part itself)
        results = []
        for i, similarity in enumerate(similarities):
            if i != target_index and similarity > 0.1:
                part = self.parts[i].copy()
                part['_ai_score'] = float(similarity)
                results.append(part)
        
        results.sort(key=lambda x: x['_ai_score'], reverse=True)
        return results[:top_k]
    
    def auto_suggest(self, partial_query: str, max_suggestions: int = 5) -> List[str]:
        """Generate auto-suggestions based on vocabulary."""
        if len(partial_query) < 2:
            return []
        
        suggestions = []
        vocabulary = self.vectorizer.get_feature_names_out()
        
        partial_lower = partial_query.lower()
        for term in vocabulary:
            if term.startswith(partial_lower) and len(term) > len(partial_query):
                suggestions.append(term)
                if len(suggestions) >= max_suggestions:
                    break
        
        return suggestions

def interactive_ai_search():
    """Interactive AI search interface."""
    print("Initializing lightweight AI search engine...")
    search_engine = LightweightAISearch("synthetic_car_parts_500.jsonl")
    
    print("\n=== IntelliPart Lightweight AI Search MVP ===")
    print("Commands:")
    print("  search <query>           - AI-powered search")
    print("  smart <query>            - Smart search (AI + keyword)")
    print("  similar <part_number>    - Find similar parts")
    print("  suggest <partial>        - Auto-suggestions")
    print("  keyword <query>          - Traditional keyword search")
    print("  exit                     - Quit")
    print("\nExamples:")
    print("  search bright LED headlight")
    print("  smart efficient wiper")
    print("  similar 17FL1054")
    print("  suggest head")
    print("-" * 60)
    
    while True:
        user_input = input("\n> ").strip()
        
        if user_input.lower() == "exit":
            break
            
        if user_input.startswith("search "):
            query = user_input[7:]
            results = search_engine.ai_search(query)
            display_ai_results(results, "AI Search")
            
        elif user_input.startswith("smart "):
            query = user_input[6:]
            results = search_engine.smart_search(query)
            display_ai_results(results, "Smart Search")
            
        elif user_input.startswith("similar "):
            part_number = user_input[8:]
            results = search_engine.find_similar_parts(part_number)
            display_ai_results(results, f"Similar to {part_number}")
            
        elif user_input.startswith("suggest "):
            partial = user_input[8:]
            suggestions = search_engine.auto_suggest(partial)
            print(f"Suggestions for '{partial}':")
            for suggestion in suggestions:
                print(f"  - {suggestion}")
            
        elif user_input.startswith("keyword "):
            query = user_input[8:]
            results = search_engine.keyword_search(query)
            display_ai_results(results, "Keyword Search")
            
        else:
            print("Unknown command. Type 'exit' to quit.")

def display_ai_results(results: List[Dict[str, Any]], search_type: str):
    """Display AI search results."""
    if not results:
        print("No results found.")
        return
        
    print(f"\n=== {search_type} Results ===")
    for i, part in enumerate(results[:5], 1):
        print(f"\n{i}. {part.get('part_name', 'Unknown')} ({part.get('part_number', 'N/A')})")
        print(f"   System: {part.get('system', 'N/A')} | Type: {part.get('part_type', 'N/A')}")
        print(f"   Manufacturer: {part.get('manufacturer', 'N/A')}")
        print(f"   Cost: {part.get('cost', 'N/A')} | Stock: {part.get('stock', 'N/A')}")
        
        if '_ai_score' in part:
            print(f"   AI Score: {part['_ai_score']:.3f}")
        if '_smart_score' in part:
            print(f"   Smart Score: {part['_smart_score']:.3f}")
        if '_match_score' in part:
            print(f"   Match Score: {part['_match_score']}")

if __name__ == "__main__":
    interactive_ai_search()
