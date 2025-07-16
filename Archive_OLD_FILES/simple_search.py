import json
import re
from typing import List, Dict, Any
import time

class SimplePartsSearch:
    def __init__(self, jsonl_path: str):
        """Initialize search with JSONL data file."""
        self.parts = []
        self.load_data(jsonl_path)
        print(f"Loaded {len(self.parts)} parts for search.")
    
    def load_data(self, jsonl_path: str):
        """Load data from JSONL file."""
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.parts.append(json.loads(line))
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search parts by keyword across all fields."""
        start_time = time.time()
        query_lower = query.lower()
        results = []
        
        for part in self.parts:
            # Search across all string fields
            match_score = 0
            for key, value in part.items():
                if isinstance(value, str) and query_lower in value.lower():
                    match_score += 1
                    
            if match_score > 0:
                part_copy = part.copy()
                part_copy['_match_score'] = match_score
                results.append(part_copy)
        
        # Sort by match score (highest first)
        results.sort(key=lambda x: x['_match_score'], reverse=True)
        
        search_time = time.time() - start_time
        print(f"Search completed in {search_time:.3f}s - Found {len(results)} results")
        
        return results[:limit]
    
    def search_by_field(self, field: str, value: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search parts by specific field."""
        start_time = time.time()
        results = []
        
        for part in self.parts:
            if field in part and str(part[field]).lower() == value.lower():
                results.append(part)
                
        search_time = time.time() - start_time
        print(f"Field search completed in {search_time:.3f}s - Found {len(results)} results")
        
        return results[:limit]
    
    def fuzzy_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fuzzy search with partial matching."""
        start_time = time.time()
        query_words = query.lower().split()
        results = []
        
        for part in self.parts:
            match_score = 0
            for key, value in part.items():
                if isinstance(value, str):
                    value_lower = value.lower()
                    for word in query_words:
                        if word in value_lower:
                            match_score += 1
                            
            if match_score > 0:
                part_copy = part.copy()
                part_copy['_match_score'] = match_score
                results.append(part_copy)
        
        results.sort(key=lambda x: x['_match_score'], reverse=True)
        search_time = time.time() - start_time
        print(f"Fuzzy search completed in {search_time:.3f}s - Found {len(results)} results")
        
        return results[:limit]

def interactive_search():
    """Interactive search interface."""
    search_engine = SimplePartsSearch("data/training Dataset.jsonl")
    
    print("\n=== IntelliPart Search MVP ===")
    print("Commands:")
    print("  search <query>        - General search")
    print("  field <field>=<value> - Search by specific field")
    print("  fuzzy <query>         - Fuzzy search")
    print("  exit                  - Quit")
    print("\nExamples:")
    print("  search Fog Light")
    print("  field system=LIGHTING") 
    print("  fuzzy wiper motor")
    print("-" * 50)
    
    while True:
        user_input = input("\n> ").strip()
        
        if user_input.lower() == "exit":
            break
            
        if user_input.startswith("search "):
            query = user_input[7:]
            results = search_engine.search(query)
            display_results(results)
            
        elif user_input.startswith("field "):
            field_query = user_input[6:]
            if "=" in field_query:
                field, value = field_query.split("=", 1)
                results = search_engine.search_by_field(field.strip(), value.strip())
                display_results(results)
            else:
                print("Format: field <field>=<value>")
                
        elif user_input.startswith("fuzzy "):
            query = user_input[6:]
            results = search_engine.fuzzy_search(query)
            display_results(results)
            
        else:
            print("Unknown command. Type 'exit' to quit.")

def display_results(results: List[Dict[str, Any]]):
    """Display search results in a readable format."""
    if not results:
        print("No results found.")
        return
        
    for i, part in enumerate(results[:5], 1):  # Show top 5
        print(f"\n{i}. {part.get('part_name', 'Unknown')} ({part.get('part_number', 'N/A')})")
        print(f"   System: {part.get('system', 'N/A')} | Manufacturer: {part.get('manufacturer', 'N/A')}")
        print(f"   Cost: {part.get('cost', 'N/A')} | Stock: {part.get('stock', 'N/A')}")
        if '_match_score' in part:
            print(f"   Match Score: {part['_match_score']}")

if __name__ == "__main__":
    interactive_search()
