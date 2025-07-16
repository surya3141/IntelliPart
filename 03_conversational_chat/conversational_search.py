"""
IntelliPart Conversational AI Search Interface
Advanced natural language search for automotive parts with similarity detection
"""

import json
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import sqlite3
# from lightweight_ai_search import LightweightAISearch  # Moved to archive
import os
from google import genai
from google.genai import types

# --- Gemini/LLM Integration Module ---
class GeminiLLM:
    """Abstraction for Gemini/LLM integration using Vertex AI."""
    def __init__(self, model_name: str = "gemini-2.0-flash-001", project: str = None, location: str = None, json_key_path: str = None):
        self.model_name = model_name
        self.project = project or "mdp-ad-parts-dev-338172"
        self.location = location or "global"
        self.json_key_path = json_key_path or "D://OneDrive - Mahindra & Mahindra Ltd//Desktop//POC//Gemini//gemini_v1//scripts//mdp-ad-parts-dev-api-json-key.json"
        self.client = self._connect_to_google_genai()

    def _authenticate_json(self):
        if not os.path.exists(self.json_key_path):
            raise FileNotFoundError(f"Service account key file '{self.json_key_path}' not found.")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.json_key_path

    def _connect_to_google_genai(self):
        self._authenticate_json()
        return genai.Client(
            vertexai=True,
            project=self.project,
            location=self.location
        )

    def generate_response(self, prompt: str, context: list = None) -> str:
        # Compose context if provided
        context_str = ""
        if context:
            for turn in context[-3:]:
                context_str += f"User: {turn.get('query', '')}\nAI: {turn.get('llm_response', '')}\n"
        full_prompt = f"{context_str}\n{prompt}" if context_str else prompt
        response = ""
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=full_prompt)]
            )
        ]
        for chunk in self.client.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.2,
                top_p=0.8,
                max_output_tokens=2000,
            )
        ):
            response += chunk.text
        return response.strip()

# --- Modular Conversational Engine ---
class ConversationalEngine:
    """Modular conversational engine orchestrating LLM and search backend."""
    def __init__(self, parts: list, llm: GeminiLLM = None):
        self.parts_search = ConversationalPartsSearch(parts)
        self.llm = llm or GeminiLLM()
        self.conversation_history = []

    def process_query(self, query: str, limit: int = 10, user_language: str = "en") -> dict:
        # Use the search backend for understanding and retrieval
        search_result = self.parts_search.search(query, limit=limit)
        # Compose LLM prompt with search context and user language
        llm_prompt = self._build_llm_prompt(query, search_result, user_language)
        llm_response = self.llm.generate_response(llm_prompt, context=self.conversation_history)
        # Update conversation history
        self.conversation_history.append({
            'query': query,
            'search_result': search_result,
            'llm_response': llm_response
        })
        # Return combined result
        return {
            'llm_response': llm_response,
            'search_result': search_result
        }

    def _build_llm_prompt(self, query: str, search_result: dict, user_language: str = "en") -> str:
        """
        Build a prompt for the LLM grounded in the search results, user query, and recent context.
        This is modular and ready for future extension (analytics, user profile, etc).
        """
        # --- Gather context ---
        top_results = search_result.get('results', [])[:3]
        context_lines = []
        for r in top_results:
            fields = []
            if r.get('part_name') and r.get('part_name') != 'N/A':
                fields.append(f"Part: {r.get('part_name')}")
            if r.get('part_number') and r.get('part_number') != 'N/A':
                fields.append(f"Number: {r.get('part_number')}")
            if r.get('system') and r.get('system') != 'N/A':
                fields.append(f"System: {r.get('system')}")
            if r.get('manufacturer') and r.get('manufacturer') != 'N/A':
                fields.append(f"Manufacturer: {r.get('manufacturer')}")
            if r.get('cost') and r.get('cost') != 'N/A':
                fields.append(f"Cost: ₹{r.get('cost')}")
            if r.get('stock') and r.get('stock') != 'N/A':
                fields.append(f"Stock: {r.get('stock')}")
            if fields:
                context_lines.append(", ".join(fields))
        context_str = "\n".join(context_lines) if context_lines else "No relevant parts found."

        # --- Add recent conversation context (future extensible) ---
        # For now, just include the last user query if available
        # In future, can add analytics, user profile, etc.
        # recent_history = self.conversation_history[-3:] if hasattr(self, 'conversation_history') else []

        # --- Compose prompt with extensible instructions ---
        prompt = (
            f"You are an expert automotive parts assistant for Mahindra.\n"
            f"User Query: {query}\n"
            f"Relevant Parts (Top 3):\n{context_str}\n"
            f"Instructions: If the results are missing, ambiguous, or not relevant, proactively explain this to the user, suggest next steps, and offer to clarify or refine their query.\n"
            f"If the user asks a question outside the parts database, answer as best as possible or politely explain the limitation.\n"
            f"Always answer in a natural, conversational, and context-aware way in the user's language ({user_language}).\n"
            f"If you can provide analytics, insights, or recommendations, do so.\n"
            f"If the user asks for help, suggest example queries or features.\n"
        )
        return prompt

# --- ConversationalPartsSearch (Search Implementation) ---
class ConversationalPartsSearch:
    """Intelligent conversational interface for finding similar and exact automotive parts."""
    def __init__(self, parts: list):
        # ...existing code...
        self.parts = parts
        # self.ai_search = LightweightAISearch(parts)  # Moved to archive - using alternative search
        self.ai_search = None  # Placeholder for now
        
        # Setup conversational context
        self.conversation_history = []
        self.last_search_results = []
        self.user_preferences = {}
        
        # Setup database for fast exact matching
        self._setup_search_database()
        
        print(f"🤖 ConversationalPartsSearch ready with {len(self.parts)} parts!")
    
    def _setup_search_database(self):
        """Setup SQLite database for fast searching."""
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Create optimized search table
        cursor.execute('''
            CREATE TABLE parts_search (
                id INTEGER PRIMARY KEY,
                part_number TEXT,
                part_name TEXT,
                system TEXT,
                sub_system TEXT,
                manufacturer TEXT,
                material TEXT,
                part_type TEXT,
                feature TEXT,
                cost REAL,
                stock INTEGER,
                search_text TEXT,
                data TEXT
            )
        ''')
        
        # Insert data with searchable text
        for i, part in enumerate(self.parts):
            search_text = self._create_search_text(part)
            
            cursor.execute('''
                INSERT INTO parts_search VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                i,
                part.get('part_number', ''),
                part.get('part_name', ''),
                part.get('system', ''),
                part.get('sub_system', ''),
                part.get('manufacturer', ''),
                part.get('material', ''),
                part.get('part_type', ''),
                part.get('feature', ''),
                self._extract_cost(part.get('cost', '0')),
                self._extract_stock(part.get('stock', '0')),
                search_text,
                json.dumps(part)
            ))
        
        # Create search indexes
        cursor.execute('CREATE INDEX idx_part_number ON parts_search(part_number)')
        cursor.execute('CREATE INDEX idx_part_name ON parts_search(part_name)')
        cursor.execute('CREATE INDEX idx_system ON parts_search(system)')
        cursor.execute('CREATE INDEX idx_manufacturer ON parts_search(manufacturer)')
        cursor.execute('CREATE INDEX idx_search_text ON parts_search(search_text)')
        
        self.conn.commit()
    
    def _create_search_text(self, part: Dict) -> str:
        """Create comprehensive search text for a part."""
        fields = [
            'part_name', 'part_type', 'system', 'sub_system',
            'manufacturer', 'material', 'feature', 'part_number',
            'oem_part_number', 'description', 'application'
        ]
        
        text_parts = []
        for field in fields:
            value = part.get(field, '')
            if value and str(value).strip():
                text_parts.append(str(value).strip())
        
        return ' '.join(text_parts).lower()
    
    def _extract_cost(self, cost_str: str) -> float:
        """Extract numeric cost."""
        if isinstance(cost_str, (int, float)):
            return float(cost_str)
        try:
            numbers = re.findall(r'[\d.]+', str(cost_str))
            return float(numbers[0]) if numbers else 0.0
        except:
            return 0.0
    
    def _extract_stock(self, stock_str: str) -> int:
        """Extract numeric stock."""
        if isinstance(stock_str, int):
            return stock_str
        try:
            numbers = re.findall(r'\d+', str(stock_str))
            return int(numbers[0]) if numbers else 0
        except:
            return 0
    
    def understand_query(self, query: str) -> Dict[str, Any]:
        """Parse and understand natural language query."""
        query_lower = query.lower()
        
        # Intent classification
        intent = self._classify_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Extract filters
        filters = self._extract_filters(query_lower)
        
        # Determine search strategy
        search_strategy = self._determine_search_strategy(intent, entities, filters)
        
        return {
            'original_query': query,
            'intent': intent,
            'entities': entities,
            'filters': filters,
            'search_strategy': search_strategy,
            'processed_at': datetime.now().isoformat()
        }
    
    def _classify_intent(self, query: str) -> str:
        """Classify user intent from query."""
        # Exact search patterns
        if any(word in query for word in ['exact', 'exactly', 'precise', 'specific part number']):
            return 'exact_search'
        
        # Similar/alternative search patterns  
        if any(word in query for word in ['similar', 'like', 'alternative', 'substitute', 'replacement', 'equivalent']):
            return 'similarity_search'
        
        # Comparison patterns
        if any(word in query for word in ['compare', 'vs', 'versus', 'difference', 'better']):
            return 'comparison'
        
        # Recommendation patterns
        if any(word in query for word in ['recommend', 'suggest', 'best', 'optimal', 'should i']):
            return 'recommendation'
        
        # Price/cost patterns
        if any(word in query for word in ['cheap', 'affordable', 'cost', 'price', 'budget']):
            return 'cost_search'
        
        # Availability patterns
        if any(word in query for word in ['available', 'stock', 'inventory', 'in stock']):
            return 'availability_search'
        
        # Default to general search
        return 'general_search'
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities like part names, systems, manufacturers."""
        entities = {
            'part_numbers': [],
            'part_names': [],
            'systems': [],
            'manufacturers': [],
            'materials': [],
            'features': []
        }
        
        # Extract part numbers (alphanumeric patterns)
        part_number_patterns = re.findall(r'\b[A-Z0-9]{3,}[-_]?[A-Z0-9]*\b', query.upper())
        entities['part_numbers'] = part_number_patterns
        
        # Extract known systems from database
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT system FROM parts_search WHERE system IS NOT NULL')
        known_systems = [row[0].lower() for row in cursor.fetchall() if row[0]]
        
        for system in known_systems:
            if system in query:
                entities['systems'].append(system)
        
        # Extract known manufacturers
        cursor.execute('SELECT DISTINCT manufacturer FROM parts_search WHERE manufacturer IS NOT NULL')
        known_manufacturers = [row[0].lower() for row in cursor.fetchall() if row[0]]
        
        for manufacturer in known_manufacturers:
            if manufacturer in query:
                entities['manufacturers'].append(manufacturer)
        
        # Extract materials
        materials = ['steel', 'aluminum', 'plastic', 'rubber', 'metal', 'carbon', 'fiber']
        for material in materials:
            if material in query:
                entities['materials'].append(material)
        
        return entities
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filter criteria from query."""
        filters = {}
        
        # Price filters - fixed regex patterns
        price_matches = re.findall(r'under \$?([\d,]+)', query)
        if price_matches:
            filters['max_cost'] = float(price_matches[0].replace(',', ''))
        
        price_matches = re.findall(r'over \$?([\d,]+)', query)
        if price_matches:
            filters['min_cost'] = float(price_matches[0].replace(',', ''))
        
        # Stock filters
        if 'in stock' in query or 'available' in query:
            filters['min_stock'] = 1
        
        # Quality filters
        if any(word in query for word in ['high quality', 'premium', 'best']):
            filters['quality_level'] = 'high'
        
        return filters
    
    def _determine_search_strategy(self, intent: str, entities: Dict, filters: Dict) -> str:
        """Determine the best search strategy based on intent and entities."""
        # If we have specific part numbers, prioritize exact matching
        if entities['part_numbers']:
            return 'exact_match'
        
        # If intent is similarity, use AI similarity search
        if intent == 'similarity_search':
            return 'ai_similarity'
        
        # If we have specific systems/manufacturers, use filtered search
        if entities['systems'] or entities['manufacturers']:
            return 'filtered_search'
        
        # If we have cost constraints, use cost-optimized search
        if intent == 'cost_search' or filters.get('max_cost') or filters.get('min_cost'):
            return 'cost_optimized'
        
        # Default to hybrid search
        return 'hybrid_search'
    
    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Main search function with conversational understanding."""
        start_time = time.time()
        
        # Understand the query
        understanding = self.understand_query(query)
        
        # Store in conversation history
        self.conversation_history.append({
            'query': query,
            'understanding': understanding,
            'timestamp': datetime.now().isoformat()
        })
        
        # Execute search based on strategy
        results = self._execute_search(understanding, limit)
        
        # Enhance results with similarity scores and explanations
        enhanced_results = self._enhance_results(results, understanding)
        
        # Store results for follow-up questions
        self.last_search_results = enhanced_results
        
        search_time = time.time() - start_time
        
        return {
            'query': query,
            'understanding': understanding,
            'results': enhanced_results,
            'result_count': len(enhanced_results),
            'search_time_ms': round(search_time * 1000, 2),
            'suggestions': self._generate_suggestions(understanding, enhanced_results)
        }
    
    def _execute_search(self, understanding: Dict, limit: int) -> List[Dict]:
        """Execute search based on determined strategy."""
        strategy = understanding['search_strategy']
        entities = understanding['entities']
        filters = understanding['filters']
        
        if strategy == 'exact_match':
            return self._exact_match_search(entities, filters, limit)
        elif strategy == 'ai_similarity':
            return self._ai_similarity_search(understanding['original_query'], filters, limit)
        elif strategy == 'filtered_search':
            return self._filtered_search(entities, filters, limit)
        elif strategy == 'cost_optimized':
            return self._cost_optimized_search(understanding['original_query'], filters, limit)
        else:  # hybrid_search
            return self._hybrid_search(understanding['original_query'], entities, filters, limit)
    
    def _exact_match_search(self, entities: Dict, filters: Dict, limit: int) -> List[Dict]:
        """Search for exact part number matches."""
        results = []
        cursor = self.conn.cursor()
        
        for part_number in entities['part_numbers']:
            query = '''
                SELECT * FROM parts_search 
                WHERE part_number LIKE ? OR search_text LIKE ?
                ORDER BY part_number = ? DESC
                LIMIT ?
            '''
            cursor.execute(query, (f'%{part_number}%', f'%{part_number}%', part_number, limit))
            
            for row in cursor.fetchall():
                part_data = json.loads(row[12])  # data column
                part_data['match_type'] = 'exact'
                part_data['match_score'] = 1.0
                results.append(part_data)
        
        return results[:limit]
    
    def _ai_similarity_search(self, query: str, filters: Dict, limit: int) -> List[Dict]:
        """Use AI to find similar parts."""
        # Use the existing lightweight AI search
        ai_results = self.ai_search.search(query, limit=limit*2)  # Get more for filtering
        
        results = []
        for result in ai_results['results']:
            # Apply filters
            if self._passes_filters(result, filters):
                result['match_type'] = 'similarity'
                result['match_score'] = result.get('similarity_score', 0.5)
                results.append(result)
        
        return results[:limit]
    
    def _filtered_search(self, entities: Dict, filters: Dict, limit: int) -> List[Dict]:
        """Search with specific system/manufacturer filters."""
        cursor = self.conn.cursor()
        
        where_conditions = []
        params = []
        
        if entities['systems']:
            system_conditions = ' OR '.join(['system LIKE ?' for _ in entities['systems']])
            where_conditions.append(f'({system_conditions})')
            params.extend([f'%{s}%' for s in entities['systems']])
        
        if entities['manufacturers']:
            mfr_conditions = ' OR '.join(['manufacturer LIKE ?' for _ in entities['manufacturers']])
            where_conditions.append(f'({mfr_conditions})')
            params.extend([f'%{m}%' for m in entities['manufacturers']])
        
        # Add filter conditions
        if filters.get('min_cost'):
            where_conditions.append('cost >= ?')
            params.append(filters['min_cost'])
        
        if filters.get('max_cost'):
            where_conditions.append('cost <= ?')
            params.append(filters['max_cost'])
        
        if filters.get('min_stock'):
            where_conditions.append('stock >= ?')
            params.append(filters['min_stock'])
        
        where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
        
        query = f'''
            SELECT * FROM parts_search 
            WHERE {where_clause}
            ORDER BY cost ASC
            LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            part_data = json.loads(row[12])
            part_data['match_type'] = 'filtered'
            part_data['match_score'] = 0.8
            results.append(part_data)
        
        return results
    
    def _cost_optimized_search(self, query: str, filters: Dict, limit: int) -> List[Dict]:
        """Search optimized for cost considerations."""
        cursor = self.conn.cursor()
        
        # First get parts matching the query
        cursor.execute('''
            SELECT * FROM parts_search 
            WHERE search_text LIKE ?
            ORDER BY cost ASC
            LIMIT ?
        ''', (f'%{query.lower()}%', limit*3))
        
        results = []
        for row in cursor.fetchall():
            part_data = json.loads(row[12])
            if self._passes_filters(part_data, filters):
                part_data['match_type'] = 'cost_optimized'
                part_data['match_score'] = 0.7
                results.append(part_data)
        
        return results[:limit]
    
    def _hybrid_search(self, query: str, entities: Dict, filters: Dict, limit: int) -> List[Dict]:
        """Hybrid search combining multiple strategies."""
        results = []
        
        # 1. Try exact matches first (30% of results)
        exact_limit = max(1, limit // 3)
        if entities['part_numbers']:
            exact_results = self._exact_match_search(entities, filters, exact_limit)
            results.extend(exact_results)
        
        # 2. Try AI similarity (40% of results) 
        remaining = limit - len(results)
        if remaining > 0:
            ai_limit = max(1, min(remaining, limit * 2 // 5))
            ai_results = self._ai_similarity_search(query, filters, ai_limit)
            results.extend(ai_results)
        
        # 3. Fill remaining with filtered search
        remaining = limit - len(results)
        if remaining > 0:
            filtered_results = self._filtered_search(entities, filters, remaining)
            results.extend(filtered_results)
        
        # Remove duplicates and sort by match score
        seen_parts = set()
        unique_results = []
        for result in results:
            part_id = result.get('part_number', '') + result.get('part_name', '')
            if part_id not in seen_parts:
                seen_parts.add(part_id)
                unique_results.append(result)
        
        # Sort by match score
        unique_results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return unique_results[:limit]
    
    def _passes_filters(self, part: Dict, filters: Dict) -> bool:
        """Check if part passes the specified filters."""
        # Cost filters
        cost = self._extract_cost(part.get('cost', '0'))
        if filters.get('min_cost') and cost < filters['min_cost']:
            return False
        if filters.get('max_cost') and cost > filters['max_cost']:
            return False
        
        # Stock filters
        stock = self._extract_stock(part.get('stock', '0'))
        if filters.get('min_stock') and stock < filters['min_stock']:
            return False
        
        return True
    
    def _enhance_results(self, results: List[Dict], understanding: Dict) -> List[Dict]:
        """Enhance results with additional information and explanations. Always include expected fields for frontend."""
        enhanced = []
        for result in results:
            # Add explanation for why this part was matched
            explanation = self._generate_match_explanation(result, understanding)
            # Add similarity to previous searches
            similarity_context = self._get_similarity_context(result)
            # Add cost insights
            cost_insights = self._get_cost_insights(result)
            # Add availability insights
            availability_insights = self._get_availability_insights(result)
            # Ensure all expected fields are present for frontend rendering
            enhanced_result = {
                **result,
                'part_name': result.get('part_name') or result.get('name') or 'N/A',
                'part_number': result.get('part_number') or result.get('oem_part_number') or 'N/A',
                'system': result.get('system') or result.get('category') or 'N/A',
                'manufacturer': result.get('manufacturer') or 'N/A',
                'cost': result.get('cost') or result.get('cost_price') or result.get('retail_price') or 'N/A',
                'stock': result.get('stock') or (result.get('supply_chain', {}).get('current_stock') if isinstance(result.get('supply_chain'), dict) else None) or 'N/A',
                'match_explanation': explanation,
                'similarity_context': similarity_context,
                'cost_insights': cost_insights,
                'availability_insights': availability_insights,
                'enhanced_at': datetime.now().isoformat()
            }
            enhanced.append(enhanced_result)
        return enhanced
    
    def _generate_match_explanation(self, result: Dict, understanding: Dict) -> str:
        """Generate explanation for why this part matched."""
        match_type = result.get('match_type', 'general')
        
        explanations = {
            'exact': f"Exact match for part number {result.get('part_number', 'N/A')}",
            'similarity': f"Similar to your search with {result.get('match_score', 0.5)*100:.0f}% relevance",
            'filtered': f"Matches your criteria for {understanding['entities']['systems'] or understanding['entities']['manufacturers']}",
            'cost_optimized': f"Cost-effective option at ₹{self._extract_cost(result.get('cost', '0')):.2f}",
            'general': "General match based on your search terms"
        }
        
        return explanations.get(match_type, explanations['general'])
    
    def _get_similarity_context(self, result: Dict) -> Dict[str, Any]:
        """Get context about similar parts."""
        cursor = self.conn.cursor()
        
        # Find parts in same system
        system = result.get('system', '')
        if system:
            cursor.execute('''
                SELECT COUNT(*) FROM parts_search 
                WHERE system = ? AND part_number != ?
            ''', (system, result.get('part_number', '')))
            
            similar_count = cursor.fetchone()[0]
            
            return {
                'similar_parts_in_system': similar_count,
                'system': system
            }
        
        return {}
    
    def _get_cost_insights(self, result: Dict) -> Dict[str, Any]:
        """Get cost insights for the part."""
        cost = self._extract_cost(result.get('cost', '0'))
        cursor = self.conn.cursor()
        
        # Get average cost for similar parts
        system = result.get('system', '')
        if system:
            cursor.execute('''
                SELECT AVG(cost), MIN(cost), MAX(cost) 
                FROM parts_search 
                WHERE system = ? AND cost > 0
            ''', (system,))
            
            avg_cost, min_cost, max_cost = cursor.fetchone()
            
            if avg_cost:
                cost_position = 'below average' if cost < avg_cost else 'above average' if cost > avg_cost else 'average'
                
                return {
                    'cost_position': cost_position,
                    'system_avg_cost': round(avg_cost, 2),
                    'system_cost_range': f"₹{min_cost:.2f} - ₹{max_cost:.2f}",
                    'savings_potential': max(0, round(avg_cost - cost, 2))
                }
        
        return {'cost_position': 'unknown'}
    
    def _get_availability_insights(self, result: Dict) -> Dict[str, Any]:
        """Get availability insights."""
        stock = self._extract_stock(result.get('stock', '0'))
        
        if stock > 50:
            status = 'high_stock'
            message = 'Well stocked'
        elif stock > 10:
            status = 'medium_stock' 
            message = 'Moderate stock'
        elif stock > 0:
            status = 'low_stock'
            message = 'Limited stock'
        else:
            status = 'out_of_stock'
            message = 'Out of stock'
        
        return {
            'status': status,
            'message': message,
            'stock_level': stock
        }
    
    def _generate_suggestions(self, understanding: Dict, results: List[Dict]) -> List[str]:
        """Generate helpful suggestions for the user."""
        suggestions = []
        
        intent = understanding['intent']
        
        if intent == 'similarity_search' and len(results) < 5:
            suggestions.append("Try broadening your search terms for more similar parts")
        
        if intent == 'cost_search':
            suggestions.append("Consider checking alternative manufacturers for better pricing")
        
        if not results:
            suggestions.append("Try using more general terms or check the part system category")
            suggestions.append("Consider searching by manufacturer or part type instead")
        
        # Suggest related searches based on results
        if results:
            systems = list(set([r.get('system', '') for r in results[:3] if r.get('system')]))
            if systems:
                suggestions.append(f"Explore more parts in: {', '.join(systems)}")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def ask_followup(self, question: str) -> Dict[str, Any]:
        """Handle follow-up questions about previous search results."""
        question_lower = question.lower()
        
        if not self.last_search_results:
            return {
                'response': "I don't have any previous search results to reference. Please start with a new search.",
                'type': 'no_context'
            }
        
        # Analyze follow-up question type
        if any(word in question_lower for word in ['cheaper', 'less expensive', 'lower cost']):
            return self._find_cheaper_alternatives()
        
        elif any(word in question_lower for word in ['more like', 'similar to', 'alternatives']):
            return self._find_more_similar_parts(question)
        
        elif any(word in question_lower for word in ['in stock', 'available', 'stock level']):
            return self._check_availability_info()
        
        elif any(word in question_lower for word in ['compare', 'difference', 'which is better']):
            return self._compare_parts()
        
        else:
            return self._general_followup_response(question)
    
    def _find_cheaper_alternatives(self) -> Dict[str, Any]:
        """Find cheaper alternatives to previous results."""
        if not self.last_search_results:
            return {'response': 'No previous results to compare against.', 'type': 'error'}
        
        # Get average cost of previous results
        costs = [self._extract_cost(r.get('cost', '0')) for r in self.last_search_results]
        avg_cost = sum(costs) / len(costs) if costs else 0
        
        # Find cheaper alternatives with same functionality
        alternatives = []
        for result in self.last_search_results:
            system = result.get('system', '')
            current_cost = self._extract_cost(result.get('cost', '0'))
            
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM parts_search 
                WHERE system = ? AND cost < ? AND cost > 0
                ORDER BY cost ASC
                LIMIT 5
            ''', (system, current_cost))
            
            for row in cursor.fetchall():
                part_data = json.loads(row[12])
                part_data['savings'] = round(current_cost - self._extract_cost(part_data.get('cost', '0')), 2)
                alternatives.append(part_data)
        
        return {
            'response': f'Found {len(alternatives)} cheaper alternatives',
            'alternatives': alternatives[:10],
            'type': 'cheaper_alternatives'
        }
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation."""
        return {
            'total_queries': len(self.conversation_history),
            'recent_queries': self.conversation_history[-5:] if self.conversation_history else [],
            'last_result_count': len(self.last_search_results),
            'user_preferences': self.user_preferences
        }
    
    def get_quick_metrics(self):
        """Return quick insights for dashboard: total parts, systems, manufacturers, avg cost, low stock alerts."""
        cursor = self.conn.cursor()
        # Total parts
        cursor.execute('SELECT COUNT(*) FROM parts_search')
        total_parts = cursor.fetchone()[0]
        # Total unique systems
        cursor.execute('SELECT COUNT(DISTINCT system) FROM parts_search WHERE system IS NOT NULL AND system != ""')
        total_systems = cursor.fetchone()[0]
        # Total unique manufacturers
        cursor.execute('SELECT COUNT(DISTINCT manufacturer) FROM parts_search WHERE manufacturer IS NOT NULL AND manufacturer != ""')
        total_manufacturers = cursor.fetchone()[0]
        # Average cost
        cursor.execute('SELECT AVG(cost) FROM parts_search WHERE cost > 0')
        avg_cost = cursor.fetchone()[0] or 0.0
        # Low stock alerts (stock <= 5)
        cursor.execute('SELECT COUNT(*) FROM parts_search WHERE stock <= 5 AND stock > 0')
        low_stock_alerts = cursor.fetchone()[0]
        return {
            'total_parts': total_parts,
            'total_systems': total_systems,
            'total_manufacturers': total_manufacturers,
            'avg_cost': avg_cost,
            'low_stock_alerts': low_stock_alerts
        }

# --- Main Demo Entrypoint ---
def main():
    """Demo the modular conversational engine with LLM integration."""
    print("🚀 IntelliPart Modular Conversational Engine Demo")
    print("=" * 50)
    # Use the shared dataset loader if available
    try:
        # Try to import from parent directory (moved to archive)
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from Archive_OLD_FILES.dataset_loader import load_all_parts
        all_parts = load_all_parts()
    except (ImportError, ModuleNotFoundError):
        # Fallback to local loading
        script_dir = os.path.dirname(os.path.abspath(__file__))
        datasets_dir = os.path.join(script_dir, '..', '01_dataset_expansion', 'production_dataset', 'datasets')
        all_parts = []
        if os.path.isdir(datasets_dir):
            for fname in os.listdir(datasets_dir):
                if fname.endswith('.jsonl'):
                    fpath = os.path.join(datasets_dir, fname)
                    with open(fpath, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    all_parts.append(json.loads(line))
                                except Exception as e:
                                    print(f"Error parsing line in {fname}: {e}")
        else:
            print(f"Datasets directory not found: {datasets_dir}")
    print(f"Loaded {len(all_parts)} parts from unified dataset.")

    # Initialize the modular conversational engine
    engine = ConversationalEngine(all_parts)
    demo_queries = [
        "Find me engine parts similar to brake pads",
        "I need exact part number ENG-123-ABC",
        "Show me cheap brake components under ₹500",
        "What aluminum parts are available in stock?",
        "Find alternatives to transmission parts",
        "Compare engine mounts from different manufacturers"
    ]
    print("\n🎯 Running Demo Queries:")
    print("-" * 30)
    for query in demo_queries:
        print(f"\n🔍 Query: '{query}'")
        start_time = time.time()
        result = engine.process_query(query, limit=5)
        search_time = time.time() - start_time
        print(f"⚡ Found {result['search_result']['result_count']} results in {search_time*1000:.1f}ms")
        print(f"🧠 Intent: {result['search_result']['understanding']['intent']}")
        print(f"📋 Strategy: {result['search_result']['understanding']['search_strategy']}")
        print(f"🤖 LLM: {result['llm_response']}")
        if result['search_result']['results']:
            top_result = result['search_result']['results'][0]
            print(f"🏆 Top Result: {top_result.get('part_name', 'N/A')} ({top_result.get('match_type', 'N/A')})")
            print(f"💡 Explanation: {top_result.get('match_explanation', 'N/A')}")
        if result['search_result']['suggestions']:
            print(f"💡 Suggestions: {', '.join(result['search_result']['suggestions'][:2])}")
        print("-" * 30)
    print("\n🎊 Modular Conversational Engine Demo Complete!")

def main():
    print("ConversationalPartsSearch module loaded. Run as part of the web app.")

if __name__ == "__main__":
    main()
