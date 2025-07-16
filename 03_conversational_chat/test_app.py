#!/usr/bin/env python3
"""
Minimal test version of IntelliPart Web App
This version focuses on basic functionality without advanced AI features
"""

from flask import Flask, render_template, request, jsonify
import json
import time
from pathlib import Path
from typing import List, Dict, Any

app = Flask(__name__)
app.secret_key = 'intellipart_test_key_2024'

# Simple global storage
all_parts = []

def load_test_data():
    """Load test data from the local dataset"""
    global all_parts
    
    # Try loading from local data directory
    local_dataset = Path(__file__).parent / "data" / "training Dataset.jsonl"
    if local_dataset.is_file():
        try:
            print(f"[DEBUG] Loading local dataset: {local_dataset}")
            with open(local_dataset, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        all_parts.append(json.loads(line.strip()))
            print(f"[DEBUG] Loaded {len(all_parts)} parts from local dataset")
            return True
        except Exception as e:
            print(f"Error loading local dataset: {e}")
    
    # Fallback to sample data
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
        },
        {
            "part_number": "BAT003",
            "part_name": "Battery 12V",
            "system_name": "Electrical System",
            "manufacturer": "Mahindra",
            "cost": 4500,
            "stock": 12,
            "condition": "Good", 
            "material": "Lead Acid",
            "vehicle_model": "TUV300"
        }
    ]
    print(f"[DEBUG] Created {len(all_parts)} sample parts for testing")
    return True

def simple_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Simple keyword-based search"""
    if not query.strip():
        return []
    
    query_terms = query.lower().split()
    results = []
    
    for part in all_parts:
        score = 0
        part_text = " ".join(str(v) for v in part.values()).lower()
        
        for term in query_terms:
            if term in part_text:
                # Boost score for matches in important fields
                if term in part.get('part_name', '').lower():
                    score += 3
                elif term in part.get('system_name', '').lower():
                    score += 2
                elif term in part.get('manufacturer', '').lower():
                    score += 2
                else:
                    score += 1
        
        if score > 0:
            part_copy = part.copy()
            part_copy['similarity'] = min(score / len(query_terms), 1.0)
            results.append(part_copy)
    
    # Sort by score and return top results
    results = sorted(results, key=lambda x: x['similarity'], reverse=True)
    return results[:limit]

@app.route('/')
def home():
    """Main interface"""
    return render_template('conversational_search.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """Handle search requests"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        start_time = time.time()
        
        # Perform search
        results = simple_search(query, limit=10)
        
        search_time_ms = round((time.time() - start_time) * 1000, 2)
        
        # Generate response
        if results:
            response_text = f"Found {len(results)} results for '{query}'. Top match: {results[0].get('part_name', 'Unknown')}"
        else:
            response_text = f"No results found for '{query}'. Try different keywords."
        
        # Clean results for frontend
        clean_results = []
        for result in results:
            clean_result = result.copy()
            clean_result.pop('similarity', None)
            clean_results.append(clean_result)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': clean_results,
            'result_count': len(clean_results),
            'search_time_ms': search_time_ms,
            'intelligent_response': response_text,
            'suggestions': []
        })
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/api/assistant-intro')
def assistant_intro():
    """Return assistant introduction"""
    intro_data = {
        "greeting": "Welcome to IntelliPart!",
        "intro": f"I am your Mahindra automotive parts assistant. I have access to {len(all_parts)} parts in the database.",
        "capabilities": [
            "Search parts by name, number, or description",
            "Filter by vehicle model and system", 
            "Quick keyword matching",
            "Real-time inventory status"
        ],
        "suggestion": "Try searching for brake pads, radiator, or battery."
    }
    return jsonify({"success": True, "assistant_intro": intro_data})

@app.route('/api/example-queries')
def example_queries():
    """Return example search queries"""
    queries = [
        "brake pads for Thar",
        "radiator for Marazzo", 
        "battery 12V",
        "Mahindra brake system",
        "cooling system parts",
        "electrical components"
    ]
    return jsonify({"success": True, "example_queries": queries})

def extract_numeric_cost(cost_value):
    """Extract numeric value from cost field that might contain 'INR' or other text"""
    if not cost_value:
        return 0.0
    
    # Convert to string and clean it
    cost_str = str(cost_value).replace(',', '').replace('INR', '').replace('₹', '').strip()
    
    # Try to extract number
    try:
        return float(cost_str)
    except (ValueError, TypeError):
        # Try to extract first number from string
        import re
        numbers = re.findall(r'\d+\.?\d*', cost_str)
        if numbers:
            return float(numbers[0])
        return 0.0

@app.route('/api/quick-insights')
def quick_insights():
    """Return dataset insights"""
    if not all_parts:
        return jsonify({'error': 'No data loaded'}), 500
        
    total_parts = len(all_parts)
    
    # Handle cost conversion safely
    costs = []
    for part in all_parts:
        cost = extract_numeric_cost(part.get('cost', 0))
        if cost > 0:
            costs.append(cost)
    
    avg_cost = sum(costs) / len(costs) if costs else 0
    total_stock = sum(int(str(p.get('stock', 0)).replace(',', '').split()[0]) if str(p.get('stock', 0)).replace(',', '').split() else 0 for p in all_parts)
    
    metrics = {
        "total_parts": total_parts,
        "average_cost": round(avg_cost, 2),
        "total_stock": total_stock,
        "unique_manufacturers": len(set(p.get('manufacturer', '') for p in all_parts))
    }
    
    summary = f"Database contains {total_parts} parts with average cost ₹{avg_cost:.2f} and total stock of {total_stock} units."
    
    return jsonify({
        'success': True, 
        'insights': metrics, 
        'summary': summary
    })

if __name__ == "__main__":
    print("🚀 Starting IntelliPart Test Web App...")
    
    # Load data
    if load_test_data():
        print(f"✅ Loaded {len(all_parts)} parts successfully")
    else:
        print("❌ Failed to load data")
        
    print("🌐 Starting Flask server on http://127.0.0.1:5000...")
    app.run(debug=True, host='127.0.0.1', port=5000)
