import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import time
from typing import List, Dict, Any, Optional

class SemanticPartsSearch:
    def __init__(self, jsonl_path: str, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize semantic search with sentence transformers."""
        self.parts = []
        self.embeddings = None
        self.model = None
        self.model_name = model_name
        self.embeddings_file = 'parts_embeddings.pkl'
        
        print("Loading data...")
        self.load_data(jsonl_path)
        
        print(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Load or generate embeddings
        if os.path.exists(self.embeddings_file):
            print("Loading pre-computed embeddings...")
            self.load_embeddings()
        else:
            print("Generating embeddings for the first time...")
            self.generate_embeddings()
            
        print(f"Semantic search ready with {len(self.parts)} parts!")
    
    def load_data(self, jsonl_path: str):
        """Load parts data from JSONL file."""
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.parts.append(json.loads(line))
    
    def create_part_text(self, part: Dict[str, Any]) -> str:
        """Create searchable text from part data."""
        important_fields = [
            'part_name', 'part_type', 'system', 'sub_system', 
            'manufacturer', 'type', 'material', 'feature'
        ]
        
        text_parts = []
        for field in important_fields:
            if field in part and part[field]:
                text_parts.append(str(part[field]))
        
        return ' '.join(text_parts)
    
    def generate_embeddings(self):
        """Generate embeddings for all parts."""
        print("Creating searchable text for parts...")
        part_texts = [self.create_part_text(part) for part in self.parts]
        
        print("Generating embeddings... This may take a few minutes.")
        start_time = time.time()
        self.embeddings = self.model.encode(part_texts, show_progress_bar=True)
        end_time = time.time()
        
        print(f"Embeddings generated in {end_time - start_time:.2f} seconds")
        
        # Save embeddings for future use
        self.save_embeddings()
    
    def save_embeddings(self):
        """Save embeddings to disk."""
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
        print(f"Embeddings saved to {self.embeddings_file}")
    
    def load_embeddings(self):
        """Load embeddings from disk."""
        with open(self.embeddings_file, 'rb') as f:
            self.embeddings = pickle.load(f)
        print("Embeddings loaded from cache")
    
    def semantic_search(self, query: str, top_k: int = 10, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Perform semantic search using cosine similarity."""
        start_time = time.time()
        
        # Generate embedding for query
        query_embedding = self.model.encode([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top results above threshold
        results = []
        for i, similarity in enumerate(similarities):
            if similarity > threshold:
                part = self.parts[i].copy()
                part['_similarity_score'] = float(similarity)
                results.append(part)
        
        # Sort by similarity
        results.sort(key=lambda x: x['_similarity_score'], reverse=True)
        
        search_time = time.time() - start_time
        print(f"Semantic search completed in {search_time:.3f}s - Found {len(results)} results")
        
        return results[:top_k]
    
    def hybrid_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Combine keyword and semantic search."""
        # Semantic search
        semantic_results = self.semantic_search(query, top_k * 2)
        
        # Keyword search
        keyword_results = self.keyword_search(query, top_k * 2)
        
        # Combine and deduplicate
        combined = {}
        
        # Add semantic results with boost
        for result in semantic_results:
            part_id = result.get('part_number', str(id(result)))
            combined[part_id] = result
            combined[part_id]['_hybrid_score'] = result['_similarity_score'] * 0.7
        
        # Add keyword results
        for result in keyword_results:
            part_id = result.get('part_number', str(id(result)))
            if part_id in combined:
                # Boost if found in both
                combined[part_id]['_hybrid_score'] += result.get('_match_score', 0) * 0.3
            else:
                result['_hybrid_score'] = result.get('_match_score', 0) * 0.3
                combined[part_id] = result
        
        # Sort by hybrid score
        final_results = list(combined.values())
        final_results.sort(key=lambda x: x.get('_hybrid_score', 0), reverse=True)
        
        return final_results[:top_k]
    
    def keyword_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Simple keyword search for hybrid approach."""
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
        """Find parts similar to a given part."""
        # Find the part
        target_part = None
        target_index = None
        
        for i, part in enumerate(self.parts):
            if part.get('part_number') == part_number:
                target_part = part
                target_index = i
                break
        
        if target_part is None:
            print(f"Part {part_number} not found")
            return []
        
        # Get similarities with all other parts
        target_embedding = self.embeddings[target_index].reshape(1, -1)
        similarities = cosine_similarity(target_embedding, self.embeddings)[0]
        
        # Get top similar parts (excluding the part itself)
        results = []
        for i, similarity in enumerate(similarities):
            if i != target_index and similarity > 0.3:  # Exclude self and low similarity
                part = self.parts[i].copy()
                part['_similarity_score'] = float(similarity)
                results.append(part)
        
        results.sort(key=lambda x: x['_similarity_score'], reverse=True)
        return results[:top_k]

def interactive_semantic_search():
    """Interactive semantic search interface."""
    print("Initializing semantic search engine...")
    search_engine = SemanticPartsSearch("synthetic_car_parts_500.jsonl")
    
    print("\n=== IntelliPart Semantic Search MVP ===")
    print("Commands:")
    print("  search <query>           - Semantic search")
    print("  hybrid <query>           - Hybrid search (semantic + keyword)")
    print("  similar <part_number>    - Find similar parts")
    print("  keyword <query>          - Traditional keyword search")
    print("  exit                     - Quit")
    print("\nExamples:")
    print("  search bright LED headlight for car")
    print("  hybrid efficient wiper system")
    print("  similar 17FL1054")
    print("  keyword Bosch")
    print("-" * 60)
    
    while True:
        user_input = input("\n> ").strip()
        
        if user_input.lower() == "exit":
            break
            
        if user_input.startswith("search "):
            query = user_input[7:]
            results = search_engine.semantic_search(query)
            display_semantic_results(results, "Semantic Search")
            
        elif user_input.startswith("hybrid "):
            query = user_input[7:]
            results = search_engine.hybrid_search(query)
            display_semantic_results(results, "Hybrid Search")
            
        elif user_input.startswith("similar "):
            part_number = user_input[8:]
            results = search_engine.find_similar_parts(part_number)
            display_semantic_results(results, f"Similar to {part_number}")
            
        elif user_input.startswith("keyword "):
            query = user_input[8:]
            results = search_engine.keyword_search(query)
            display_semantic_results(results, "Keyword Search")
            
        else:
            print("Unknown command. Type 'exit' to quit.")

def display_semantic_results(results: List[Dict[str, Any]], search_type: str):
    """Display semantic search results."""
    if not results:
        print("No results found.")
        return
        
    print(f"\n=== {search_type} Results ===")
    for i, part in enumerate(results[:5], 1):
        print(f"\n{i}. {part.get('part_name', 'Unknown')} ({part.get('part_number', 'N/A')})")
        print(f"   System: {part.get('system', 'N/A')} | Type: {part.get('part_type', 'N/A')}")
        print(f"   Manufacturer: {part.get('manufacturer', 'N/A')}")
        print(f"   Cost: {part.get('cost', 'N/A')} | Stock: {part.get('stock', 'N/A')}")
        
        if '_similarity_score' in part:
            print(f"   Similarity: {part['_similarity_score']:.3f}")
        if '_hybrid_score' in part:
            print(f"   Hybrid Score: {part['_hybrid_score']:.3f}")
        if '_match_score' in part:
            print(f"   Match Score: {part['_match_score']}")

if __name__ == "__main__":
    interactive_semantic_search()
