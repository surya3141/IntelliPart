import json
import re
from typing import List, Dict, Any, Optional, Set
import time
from collections import defaultdict

class EnhancedPartsSearch:
    def __init__(self, jsonl_path: str):
        """Initialize enhanced search with JSONL data file."""
        self.parts = []
        self.field_values = defaultdict(set)  # For autocomplete
        self.load_data(jsonl_path)
        print(f"Loaded {len(self.parts)} parts for enhanced search.")
    
    def load_data(self, jsonl_path: str):
        """Load data from JSONL file and build indexes."""
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    part = json.loads(line)
                    self.parts.append(part)
                    
                    # Build field value indexes for autocomplete
                    for key, value in part.items():
                        if isinstance(value, str):
                            self.field_values[key].add(value)
    
    def search_with_filters(self, 
                          query: str = "", 
                          system: str = "", 
                          manufacturer: str = "",
                          min_cost: float = 0,
                          max_cost: float = float('inf'),
                          min_stock: int = 0,
                          limit: int = 10) -> List[Dict[str, Any]]:
        """Advanced search with multiple filters."""
        start_time = time.time()
        query_lower = query.lower()
        results = []
        
        for part in self.parts:
            # Apply filters
            if system and part.get('system', '').lower() != system.lower():
                continue
            if manufacturer and part.get('manufacturer', '').lower() != manufacturer.lower():
                continue
            
            # Cost filter (extract numeric value)
            try:
                cost_str = part.get('cost', '0')
                cost_num = float(re.sub(r'[^\d.]', '', str(cost_str)))
                if not (min_cost <= cost_num <= max_cost):
                    continue
            except:
                pass
            
            # Stock filter
            try:
                stock = int(part.get('stock', 0))
                if stock < min_stock:
                    continue
            except:
                pass
            
            # Text search
            match_score = 0
            if query:
                for key, value in part.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        match_score += 1
            else:
                match_score = 1  # All results if no query
                        
            if match_score > 0:
                part_copy = part.copy()
                part_copy['_match_score'] = match_score
                results.append(part_copy)
        
        # Sort by match score (highest first)
        results.sort(key=lambda x: x['_match_score'], reverse=True)
        
        search_time = time.time() - start_time
        print(f"Enhanced search completed in {search_time:.3f}s - Found {len(results)} results")
        
        return results[:limit]
    
    def get_suggestions(self, field: str, partial: str = "") -> List[str]:
        """Get autocomplete suggestions for a field."""
        partial_lower = partial.lower()
        suggestions = []
        
        for value in self.field_values.get(field, set()):
            if not partial or partial_lower in value.lower():
                suggestions.append(value)
        
        return sorted(suggestions)[:10]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        stats = {
            'total_parts': len(self.parts),
            'systems': list(self.field_values['system']),
            'manufacturers': list(self.field_values['manufacturer']),
            'part_types': list(self.field_values['part_type']),
        }
        
        # Cost statistics
        costs = []
        for part in self.parts:
            try:
                cost_str = part.get('cost', '0')
                cost_num = float(re.sub(r'[^\d.]', '', str(cost_str)))
                costs.append(cost_num)
            except:
                pass
        
        if costs:
            stats['cost_range'] = {'min': min(costs), 'max': max(costs), 'avg': sum(costs)/len(costs)}
        
        return stats

def enhanced_interactive_search():
    """Enhanced interactive search interface."""
    search_engine = EnhancedPartsSearch("data/training Dataset.jsonl")
    
    print("\n=== IntelliPart Enhanced Search MVP ===")
    print("Commands:")
    print("  search <query>                    - General search")
    print("  filter system=<sys> mfr=<mfr>     - Search with filters")
    print("  cost <min>-<max>                  - Filter by cost range")
    print("  suggest <field> <partial>         - Get autocomplete suggestions")
    print("  stats                             - Show dataset statistics")
    print("  exit                              - Quit")
    print("\nExamples:")
    print("  search LED")
    print("  filter system=LIGHTING mfr=Bosch")
    print("  cost 1000-5000") 
    print("  suggest manufacturer B")
    print("-" * 60)
    
    # Show initial stats
    stats = search_engine.get_stats()
    print(f"\nDataset: {stats['total_parts']} parts")
    print(f"Systems: {len(stats['systems'])} ({', '.join(stats['systems'][:3])}...)")
    print(f"Manufacturers: {len(stats['manufacturers'])} ({', '.join(stats['manufacturers'][:3])}...)")
    
    while True:
        user_input = input("\n> ").strip()
        
        if user_input.lower() == "exit":
            break
            
        if user_input.startswith("search "):
            query = user_input[7:]
            results = search_engine.search_with_filters(query=query)
            display_enhanced_results(results)
            
        elif user_input.startswith("filter "):
            # Parse filter command: filter system=LIGHTING mfr=Bosch
            filter_str = user_input[7:]
            filters = {}
            for part in filter_str.split():
                if "=" in part:
                    key, value = part.split("=", 1)
                    if key == "system":
                        filters['system'] = value
                    elif key in ["mfr", "manufacturer"]:
                        filters['manufacturer'] = value
            
            results = search_engine.search_with_filters(**filters)
            display_enhanced_results(results)
            
        elif user_input.startswith("cost "):
            # Parse cost range: cost 1000-5000
            cost_range = user_input[5:]
            if "-" in cost_range:
                try:
                    min_cost, max_cost = map(float, cost_range.split("-"))
                    results = search_engine.search_with_filters(min_cost=min_cost, max_cost=max_cost)
                    display_enhanced_results(results)
                except:
                    print("Format: cost <min>-<max> (e.g., cost 1000-5000)")
            else:
                print("Format: cost <min>-<max> (e.g., cost 1000-5000)")
                
        elif user_input.startswith("suggest "):
            # Parse suggest command: suggest manufacturer B
            suggest_parts = user_input[8:].split()
            if len(suggest_parts) >= 1:
                field = suggest_parts[0]
                partial = suggest_parts[1] if len(suggest_parts) > 1 else ""
                suggestions = search_engine.get_suggestions(field, partial)
                print(f"Suggestions for '{field}' with '{partial}':")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")
            else:
                print("Format: suggest <field> <partial>")
                
        elif user_input == "stats":
            stats = search_engine.get_stats()
            print("\n=== Dataset Statistics ===")
            print(f"Total Parts: {stats['total_parts']}")
            print(f"Systems: {', '.join(stats['systems'])}")
            print(f"Manufacturers: {', '.join(stats['manufacturers'])}")
            if 'cost_range' in stats:
                cost = stats['cost_range']
                print(f"Cost Range: {cost['min']:.0f} - {cost['max']:.0f} INR (Avg: {cost['avg']:.0f})")
            
        else:
            print("Unknown command. Type 'exit' to quit.")

def display_enhanced_results(results: List[Dict[str, Any]]):
    """Display enhanced search results."""
    if not results:
        print("No results found.")
        return
        
    print(f"\nShowing top {min(5, len(results))} results:")
    for i, part in enumerate(results[:5], 1):
        print(f"\n{i}. {part.get('part_name', 'Unknown')} ({part.get('part_number', 'N/A')})")
        print(f"   System: {part.get('system', 'N/A')} | Type: {part.get('part_type', 'N/A')}")
        print(f"   Manufacturer: {part.get('manufacturer', 'N/A')} | Origin: {part.get('country_of_origin', 'N/A')}")
        print(f"   Cost: {part.get('cost', 'N/A')} | Stock: {part.get('stock', 'N/A')} | Warranty: {part.get('warranty_period', 'N/A')}")
        if '_match_score' in part:
            print(f"   Match Score: {part['_match_score']}")

if __name__ == "__main__":
    enhanced_interactive_search()
