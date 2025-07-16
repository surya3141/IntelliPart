#!/usr/bin/env python3
"""
Dataset-Specific Query Generator for IntelliPart

This script analyzes the actual dataset and generates relevant example queries
based on the real data structure and content.
"""

import json
from collections import Counter
import random

def analyze_dataset(jsonl_file):
    """Analyze the dataset and extract key information for query generation"""
    parts = []
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                parts.append(json.loads(line.strip()))
    
    analysis = {
        'total_parts': len(parts),
        'part_types': list(set(p['part_name'] for p in parts)),
        'models': list(set(model for p in parts for model in p['compatible_models'])),
        'materials': list(set(p.get('material', '') for p in parts if p.get('material'))),
        'manufacturers': list(set(p['manufacturer'] for p in parts)),
        'systems': list(set(p['system'] for p in parts)),
        'cost_ranges': {
            'low': [p for p in parts if p.get('cost', 0) < 2000],
            'medium': [p for p in parts if 2000 <= p.get('cost', 0) < 10000],
            'high': [p for p in parts if p.get('cost', 0) >= 10000]
        },
        'stock_levels': {
            'low': [p for p in parts if p.get('stock', 0) < 10],
            'medium': [p for p in parts if 10 <= p.get('stock', 0) < 50],
            'high': [p for p in parts if p.get('stock', 0) >= 50]
        }
    }
    
    return analysis, parts

def generate_dataset_queries(analysis):
    """Generate relevant queries based on dataset analysis"""
    queries = []
    
    # Part type + model combinations
    for part_type in analysis['part_types'][:5]:  # Top 5 part types
        for model in analysis['models'][:3]:  # Top 3 models
            queries.append(f"Show me {part_type} for {model}")
    
    # Material-based queries
    for material in analysis['materials'][:5]:
        queries.append(f"Find parts made of {material}")
        if analysis['part_types']:
            part_type = random.choice(analysis['part_types'])
            queries.append(f"Show {part_type} with {material} material")
    
    # Cost-based queries
    queries.extend([
        "Find parts under ₹2000",
        "Show expensive parts over ₹10000",
        "List budget-friendly parts under ₹5000",
        "Find cost-effective parts between ₹1000-3000"
    ])
    
    # Stock-based queries
    queries.extend([
        "Show parts with low stock (under 10 units)",
        "Find parts with high availability (50+ units)",
        "List parts that need restocking",
        "Show well-stocked parts"
    ])
    
    # System-specific queries
    for system in analysis['systems'][:4]:
        queries.append(f"Find all {system} components")
    
    # Model-specific queries
    for model in analysis['models'][:6]:
        queries.append(f"Show all parts compatible with {model}")
    
    # Technical specification queries
    queries.extend([
        "Find radiators with cooling capacity over 15000 BTU",
        "Show brake pads with friction coefficient above 0.4",
        "List batteries with 12V rating",
        "Find tyres with size 235/65R17",
        "Show clutch plates with ceramic material",
        "Find exhaust systems with BS6 compliance"
    ])
    
    # Maintenance and inspection queries
    queries.extend([
        "Parts that need inspection checklist",
        "Show reusable parts with high scores",
        "Find parts suitable for refurbishment",
        "List parts with good condition rating"
    ])
    
    # Remove duplicates and limit to reasonable number
    queries = list(set(queries))[:25]
    
    return queries

def update_webapp_queries(queries, webapp_file):
    """Update the webapp with new queries"""
    with open(webapp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Format queries as Python list
    formatted_queries = '[\n        "' + '",\n        "'.join(queries) + '"\n    ]'
    
    # Find and replace the queries section
    start_marker = 'queries = ['
    end_marker = ']'
    
    start_idx = content.find(start_marker)
    if start_idx != -1:
        # Find the end of the queries list
        bracket_count = 0
        end_idx = start_idx + len(start_marker)
        
        for i, char in enumerate(content[start_idx + len(start_marker):], start_idx + len(start_marker)):
            if char == '[':
                bracket_count += 1
            elif char == ']':
                if bracket_count == 0:
                    end_idx = i + 1
                    break
                bracket_count -= 1
        
        # Replace the queries
        new_content = content[:start_idx] + f'queries = {formatted_queries}' + content[end_idx:]
        
        with open(webapp_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Updated {webapp_file} with {len(queries)} dataset-specific queries")
    else:
        print(f"❌ Could not find queries section in {webapp_file}")

def main():
    """Main function to generate and update queries"""
    print("🔍 Analyzing dataset for query generation...")
    
    # Analyze dataset
    analysis, parts = analyze_dataset('synthetic_car_parts_500.jsonl')
    
    print(f"📊 Dataset Analysis:")
    print(f"   Total parts: {analysis['total_parts']}")
    print(f"   Part types: {len(analysis['part_types'])}")
    print(f"   Vehicle models: {len(analysis['models'])}")
    print(f"   Materials: {len(analysis['materials'])}")
    
    # Generate queries
    queries = generate_dataset_queries(analysis)
    
    print(f"\n🎯 Generated {len(queries)} dataset-specific queries:")
    for i, query in enumerate(queries[:10], 1):
        print(f"   {i}. {query}")
    if len(queries) > 10:
        print(f"   ... and {len(queries) - 10} more")
    
    # Update webapp
    webapp_file = '03_conversational_chat/conversational_web_app.py'
    try:
        update_webapp_queries(queries, webapp_file)
    except Exception as e:
        print(f"❌ Error updating webapp: {e}")
        print("Manual update required in conversational_web_app.py")
    
    # Save queries to file
    with open('dataset_queries.json', 'w', encoding='utf-8') as f:
        json.dump({
            'queries': queries,
            'analysis': {
                'total_parts': analysis['total_parts'],
                'part_types': analysis['part_types'],
                'models': analysis['models'],
                'materials': analysis['materials']
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved queries to dataset_queries.json")
    print(f"🚀 Ready to use dataset-specific example queries!")

if __name__ == "__main__":
    main()
