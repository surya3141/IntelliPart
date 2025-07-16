"""
IntelliPart Conversational Web Interface
Flask web app for natural language parts search
"""

from flask import Flask, render_template, request, jsonify, session
import json
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'intellipart_conversation_key_2024'

# Initialize the conversational search engine
try:
    # search_engine = ConversationalPartsSearch("data/training Dataset.jsonl")
    print("✅ Conversational search engine initialized successfully")
except Exception as e:
    print(f"❌ Error initializing search engine: {e}")
    search_engine = None

@app.route('/')
def conversational_interface():
    """Main conversational search interface."""
    return render_template('conversational_search.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for conversational search."""
    if not search_engine:
        return jsonify({'error': 'Search engine not available'}), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Perform search
        start_time = time.time()
        result = search_engine.search(query, limit=limit)
        search_time = time.time() - start_time
        
        # Store conversation in session
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        session['conversation_history'].append({
            'query': query,
            'result_count': result['result_count'],
            'intent': result['understanding']['intent'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 conversations in session
        session['conversation_history'] = session['conversation_history'][-10:]
        
        return jsonify({
            'success': True,
            'query': query,
            'results': result['results'],
            'result_count': result['result_count'],
            'search_time_ms': round(search_time * 1000, 2),
            'understanding': result['understanding'],
            'suggestions': result['suggestions'],
            'conversation_id': len(session['conversation_history'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/followup', methods=['POST'])
def api_followup():
    """API endpoint for follow-up questions."""
    if not search_engine:
        return jsonify({'error': 'Search engine not available'}), 500
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Handle follow-up question
        result = search_engine.ask_followup(question)
        
        return jsonify({
            'success': True,
            'question': question,
            'response': result.get('response', ''),
            'type': result.get('type', ''),
            'alternatives': result.get('alternatives', []),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/summary')
def api_conversation_summary():
    """Get conversation summary."""
    if not search_engine:
        return jsonify({'error': 'Search engine not available'}), 500
    
    try:
        summary = search_engine.get_conversation_summary()
        session_history = session.get('conversation_history', [])
        
        return jsonify({
            'success': True,
            'engine_summary': summary,
            'session_history': session_history,
            'total_session_queries': len(session_history)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/similar/<part_number>')
def api_find_similar(part_number):
    """Find parts similar to a specific part number."""
    if not search_engine:
        return jsonify({'error': 'Search engine not available'}), 500
    
    try:
        query = f"Find parts similar to {part_number}"
        result = search_engine.search(query, limit=8)
        
        return jsonify({
            'success': True,
            'similar_parts': result['results'],
            'count': result['result_count'],
            'reference_part': part_number
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exact/<part_number>')
def api_exact_match(part_number):
    """Find exact matches for a part number."""
    if not search_engine:
        return jsonify({'error': 'Search engine not available'}), 500
    
    try:
        query = f"exact part number {part_number}"
        result = search_engine.search(query, limit=5)
        
        return jsonify({
            'success': True,
            'exact_matches': result['results'],
            'count': result['result_count'],
            'part_number': part_number
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick-insights')
def api_quick_insights():
    """Get quick insights about the parts database."""
    if not search_engine:
        return jsonify({'error': 'Search engine not available'}), 500
    
    try:
        # Get quick metrics from analytics
        metrics = search_engine.analytics.get_quick_metrics()
        top_systems = search_engine.analytics.get_top_systems(5)
        
        return jsonify({
            'success': True,
            'total_parts': metrics['total_parts'],
            'total_systems': metrics['total_systems'],
            'total_manufacturers': metrics['total_manufacturers'],
            'avg_cost': metrics['avg_cost'],
            'low_stock_alerts': metrics['low_stock_alerts'],
            'top_systems': top_systems,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# This file is archived and should not be used. Use conversational_web_app.py instead.

if __name__ == '__main__':
    print("🚀 Starting IntelliPart Conversational Web Interface")
    print("🌐 Access the interface at: http://localhost:5004")
    print("🤖 Natural language search ready!")
    
    app.run(
        host='0.0.0.0',
        port=5004,
        debug=True,
        threaded=True
    )
