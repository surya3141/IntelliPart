from flask import Flask, render_template, request, jsonify
import json
import re
from typing import List, Dict, Any
import time
from collections import defaultdict

class WebPartsSearch:
    def __init__(self, jsonl_path: str):
        """Initialize search engine for web interface."""
        self.parts = []
        self.field_values = defaultdict(set)
        self.load_data(jsonl_path)
        print(f"Loaded {len(self.parts)} parts for web search.")
    
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
    
    def search_with_filters(self, 
                          query: str = "", 
                          system: str = "", 
                          manufacturer: str = "",
                          min_cost: float = 0,
                          max_cost: float = float('inf'),
                          min_stock: int = 0,
                          limit: int = 20) -> Dict[str, Any]:
        """Search with filters and return results with metadata."""
        start_time = time.time()
        query_lower = query.lower()
        results = []
        
        for part in self.parts:
            # Apply filters
            if system and part.get('system', '').lower() != system.lower():
                continue
            if manufacturer and part.get('manufacturer', '').lower() != manufacturer.lower():
                continue
            
            # Cost filter
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
                match_score = 1
                        
            if match_score > 0:
                part_copy = part.copy()
                part_copy['_match_score'] = match_score
                results.append(part_copy)
        
        results.sort(key=lambda x: x['_match_score'], reverse=True)
        search_time = time.time() - start_time
        
        return {
            'results': results[:limit],
            'total_found': len(results),
            'search_time': round(search_time, 3),
            'query': query,
            'filters': {
                'system': system,
                'manufacturer': manufacturer,
                'min_cost': min_cost if min_cost > 0 else None,
                'max_cost': max_cost if max_cost < float('inf') else None,
                'min_stock': min_stock if min_stock > 0 else None
            }
        }
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get available filter options."""
        return {
            'systems': sorted(list(self.field_values['system'])),
            'manufacturers': sorted(list(self.field_values['manufacturer'])),
            'part_types': sorted(list(self.field_values['part_type']))
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
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
            'cost_range': {
                'min': min(costs) if costs else 0,
                'max': max(costs) if costs else 0,
                'avg': round(sum(costs)/len(costs), 2) if costs else 0
            }
        }

# Initialize Flask app and search engine
app = Flask(__name__)
search_engine = WebPartsSearch("data/training Dataset.jsonl")

@app.route('/')
def index():
    """Main search page."""
    stats = search_engine.get_stats()
    filter_options = search_engine.get_filter_options()
    return render_template('index.html', stats=stats, filter_options=filter_options)

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests."""
    data = request.get_json()
    
    query = data.get('query', '')
    system = data.get('system', '')
    manufacturer = data.get('manufacturer', '')
    min_cost = float(data.get('min_cost', 0)) if data.get('min_cost') else 0
    max_cost = float(data.get('max_cost', float('inf'))) if data.get('max_cost') else float('inf')
    min_stock = int(data.get('min_stock', 0)) if data.get('min_stock') else 0
    
    results = search_engine.search_with_filters(
        query=query,
        system=system,
        manufacturer=manufacturer,
        min_cost=min_cost,
        max_cost=max_cost,
        min_stock=min_stock
    )
    
    return jsonify(results)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics."""
    return jsonify(search_engine.get_stats())

@app.route('/api/filters')
def api_filters():
    """API endpoint for filter options."""
    return jsonify(search_engine.get_filter_options())

if __name__ == '__main__':
    print("Starting IntelliPart Web Search...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
