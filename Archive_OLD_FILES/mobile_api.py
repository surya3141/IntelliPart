"""
IntelliPart Mobile API & Cross-Platform Integration
RESTful API for mobile apps and external system integration
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
import sqlite3
import json
import io
import csv
from typing import Dict, List, Any
import base64
import qrcode
from PIL import Image

# Import our existing modules
try:
    from enhanced_intellipart_app import EnhancedIntelliPartApp
    from analytics_dashboard import PartsAnalytics
    from ai_demand_forecasting import DemandForecaster
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False

class MobileAPI:
    """Mobile-optimized API for IntelliPart."""
    
    def __init__(self, secret_key: str = "intellipart_mobile_secret_2025"):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = secret_key
        CORS(self.app)  # Enable CORS for mobile apps
        
        # Initialize core modules
        if MODULES_AVAILABLE:
            self.search_engine = None  # Lazy load
            self.analytics = None      # Lazy load
            self.forecaster = None     # Lazy load
        
        self.init_mobile_database()
        self.setup_routes()
        
    def init_mobile_database(self):
        """Initialize mobile-specific database tables."""
        conn = sqlite3.connect('mobile_api.db')
        cursor = conn.cursor()
        
        # API users and authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                email TEXT,
                role TEXT DEFAULT 'user',
                api_key TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Mobile sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mobile_sessions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                device_id TEXT,
                platform TEXT,
                session_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES api_users (id)
            )
        ''')
        
        # Search history for mobile users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mobile_search_history (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                query TEXT,
                search_type TEXT,
                results_count INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES api_users (id)
            )
        ''')
        
        # Favorites/Bookmarks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_favorites (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                part_number TEXT,
                part_name TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES api_users (id)
            )
        ''')
        
        # Create default admin user
        cursor.execute('''
            INSERT OR IGNORE INTO api_users (username, password_hash, email, role, api_key)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'admin',
            hashlib.sha256('admin123'.encode()).hexdigest(),
            'admin@intellipart.com',
            'admin',
            'intellipart_admin_api_key_2025'
        ))
        
        conn.commit()
        conn.close()
    
    def require_auth(self, f):
        """Decorator for API authentication."""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            api_key = request.headers.get('X-API-Key')
            
            if api_key:
                # API Key authentication
                user = self.validate_api_key(api_key)
                if not user:
                    return jsonify({'error': 'Invalid API key'}), 401
                request.current_user = user
            elif token:
                # JWT token authentication
                try:
                    if token.startswith('Bearer '):
                        token = token[7:]
                    payload = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=['HS256'])
                    request.current_user = payload
                except jwt.ExpiredSignatureError:
                    return jsonify({'error': 'Token expired'}), 401
                except jwt.InvalidTokenError:
                    return jsonify({'error': 'Invalid token'}), 401
            else:
                return jsonify({'error': 'Authentication required'}), 401
            
            return f(*args, **kwargs)
        return decorated
    
    def validate_api_key(self, api_key: str) -> Dict:
        """Validate API key and return user info."""
        conn = sqlite3.connect('mobile_api.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, role FROM api_users
            WHERE api_key = ? AND is_active = 1
        ''', (api_key,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'role': user[2]
            }
        return None
    
    def setup_routes(self):
        """Setup API routes."""
        
        @self.app.route('/api/v1/auth/login', methods=['POST'])
        def login():
            """Mobile login endpoint."""
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            device_id = data.get('device_id', 'unknown')
            platform = data.get('platform', 'unknown')
            
            if not username or not password:
                return jsonify({'error': 'Username and password required'}), 400
            
            # Validate credentials
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            conn = sqlite3.connect('mobile_api.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, role FROM api_users
                WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Create JWT token
            payload = {
                'user_id': user[0],
                'username': user[1],
                'role': user[2],
                'exp': datetime.utcnow() + timedelta(days=7)
            }
            
            token = jwt.encode(payload, self.app.config['SECRET_KEY'], algorithm='HS256')
            
            # Save session
            cursor.execute('''
                INSERT INTO mobile_sessions 
                (user_id, device_id, platform, session_token, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user[0], device_id, platform, token,
                datetime.utcnow() + timedelta(days=7)
            ))
            
            # Update last login
            cursor.execute('''
                UPDATE api_users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user[0],))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'token': token,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'role': user[2]
                },
                'expires_in': 7 * 24 * 3600  # 7 days in seconds
            })
        
        @self.app.route('/api/v1/search', methods=['POST'])
        @self.require_auth
        def mobile_search():
            """Mobile-optimized search endpoint."""
            data = request.get_json()
            query = data.get('query', '')
            search_type = data.get('search_type', 'smart')
            limit = min(data.get('limit', 20), 50)  # Max 50 results for mobile
            
            # Get search engine (lazy load)
            if not self.search_engine and MODULES_AVAILABLE:
                self.search_engine = EnhancedIntelliPartApp("data/training Dataset.jsonl")
            
            try:
                if MODULES_AVAILABLE and self.search_engine:
                    results = self.search_engine.enhanced_search(
                        query=query,
                        search_type=search_type,
                        limit=limit
                    )
                else:
                    # Fallback simple search
                    results = {
                        'results': [],
                        'total_found': 0,
                        'search_time': 0,
                        'message': 'Search modules not available'
                    }
                
                # Log search for analytics
                self.log_mobile_search(request.current_user['user_id'], query, search_type, len(results['results']))
                
                # Mobile-optimized response
                mobile_results = []
                for part in results['results']:
                    mobile_results.append({
                        'id': part.get('part_number', ''),
                        'name': part.get('part_name', 'Unknown'),
                        'number': part.get('part_number', ''),
                        'system': part.get('system', ''),
                        'manufacturer': part.get('manufacturer', ''),
                        'cost': part.get('cost', ''),
                        'stock': part.get('stock', ''),
                        'score': part.get('_score', 0),
                        'image_url': f"/api/v1/parts/{part.get('part_number', '')}/image"
                    })
                
                return jsonify({
                    'success': True,
                    'results': mobile_results,
                    'total': results['total_found'],
                    'search_time': results['search_time'],
                    'query': query,
                    'search_type': search_type
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/parts/<part_number>/qr', methods=['GET'])
        @self.require_auth
        def generate_qr_code(part_number):
            """Generate QR code for a part."""
            try:
                # Create QR code with part information
                qr_data = {
                    'part_number': part_number,
                    'type': 'intellipart_part',
                    'url': f'https://intellipart.app/parts/{part_number}'
                }
                
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(json.dumps(qr_data))
                qr.make(fit=True)
                
                # Create image
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to bytes
                img_io = io.BytesIO()
                img.save(img_io, 'PNG')
                img_io.seek(0)
                
                return send_file(img_io, mimetype='image/png')
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/favorites', methods=['GET', 'POST', 'DELETE'])
        @self.require_auth
        def manage_favorites():
            """Manage user favorites."""
            user_id = request.current_user['user_id']
            
            if request.method == 'GET':
                # Get favorites
                conn = sqlite3.connect('mobile_api.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT part_number, part_name, added_at FROM user_favorites
                    WHERE user_id = ?
                    ORDER BY added_at DESC
                ''', (user_id,))
                
                favorites = []
                for row in cursor.fetchall():
                    favorites.append({
                        'part_number': row[0],
                        'part_name': row[1],
                        'added_at': row[2]
                    })
                
                conn.close()
                return jsonify({'favorites': favorites})
            
            elif request.method == 'POST':
                # Add favorite
                data = request.get_json()
                part_number = data.get('part_number')
                part_name = data.get('part_name', '')
                
                if not part_number:
                    return jsonify({'error': 'Part number required'}), 400
                
                conn = sqlite3.connect('mobile_api.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO user_favorites 
                    (user_id, part_number, part_name)
                    VALUES (?, ?, ?)
                ''', (user_id, part_number, part_name))
                
                conn.commit()
                conn.close()
                
                return jsonify({'success': True, 'message': 'Added to favorites'})
            
            elif request.method == 'DELETE':
                # Remove favorite
                part_number = request.args.get('part_number')
                
                if not part_number:
                    return jsonify({'error': 'Part number required'}), 400
                
                conn = sqlite3.connect('mobile_api.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM user_favorites 
                    WHERE user_id = ? AND part_number = ?
                ''', (user_id, part_number))
                
                conn.commit()
                conn.close()
                
                return jsonify({'success': True, 'message': 'Removed from favorites'})
        
        @self.app.route('/api/v1/analytics/dashboard', methods=['GET'])
        @self.require_auth
        def mobile_analytics():
            """Mobile analytics dashboard."""
            try:
                if not self.analytics and MODULES_AVAILABLE:
                    self.analytics = PartsAnalytics("data/training Dataset.jsonl")
                
                if MODULES_AVAILABLE and self.analytics:
                    report = self.analytics.generate_comprehensive_report()
                    
                    # Mobile-optimized analytics
                    mobile_analytics = {
                        'overview': {
                            'total_parts': report['overview']['total_parts'],
                            'total_value': report['overview']['total_inventory_value'],
                            'avg_cost': report['overview']['avg_cost'],
                            'manufacturers': report['overview']['unique_manufacturers']
                        },
                        'alerts': [],
                        'top_insights': report['insights'][:3],  # Top 3 insights for mobile
                        'chart_data': {
                            'cost_distribution': report.get('cost_analysis', {}).get('cost_ranges', {}),
                            'top_manufacturers': list(report.get('manufacturer_analysis', {}).get('top_manufacturers', {}).items())[:5]
                        }
                    }
                    
                    # Add alerts based on insights
                    if 'stock_stats' in report.get('inventory_analysis', {}):
                        stock_stats = report['inventory_analysis']['stock_stats']
                        if stock_stats['parts_out_of_stock'] > 0:
                            mobile_analytics['alerts'].append({
                                'type': 'warning',
                                'message': f"{stock_stats['parts_out_of_stock']} parts are out of stock"
                            })
                    
                    return jsonify(mobile_analytics)
                else:
                    return jsonify({'error': 'Analytics not available'}), 503
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/export/<format>', methods=['GET'])
        @self.require_auth
        def export_data(format):
            """Export data in various formats."""
            if request.current_user['role'] != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            try:
                if format == 'csv':
                    return self.export_csv()
                elif format == 'json':
                    return self.export_json()
                else:
                    return jsonify({'error': 'Unsupported format'}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """API health check."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'modules_available': MODULES_AVAILABLE
            })
    
    def log_mobile_search(self, user_id: int, query: str, search_type: str, results_count: int):
        """Log mobile search for analytics."""
        conn = sqlite3.connect('mobile_api.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mobile_search_history 
            (user_id, query, search_type, results_count)
            VALUES (?, ?, ?, ?)
        ''', (user_id, query, search_type, results_count))
        
        conn.commit()
        conn.close()
    
    def export_csv(self):
        """Export data as CSV."""
        # Implementation for CSV export
        return jsonify({'message': 'CSV export not implemented yet'})
    
    def export_json(self):
        """Export data as JSON."""
        # Implementation for JSON export
        return jsonify({'message': 'JSON export not implemented yet'})
    
    def run(self, host='0.0.0.0', port=8080, debug=False):
        """Run the mobile API server."""
        print(f"🚀 Starting IntelliPart Mobile API on {host}:{port}")
        print(f"📱 API Documentation: http://{host}:{port}/api/v1/health")
        print(f"🔑 Admin API Key: intellipart_admin_api_key_2025")
        self.app.run(host=host, port=port, debug=debug)

def create_api_documentation():
    """Create API documentation."""
    docs = {
        "IntelliPart Mobile API v1.0": {
            "base_url": "http://localhost:8080/api/v1",
            "authentication": {
                "methods": ["JWT Token", "API Key"],
                "headers": {
                    "Authorization": "Bearer <jwt_token>",
                    "X-API-Key": "<api_key>"
                }
            },
            "endpoints": {
                "/auth/login": {
                    "method": "POST",
                    "description": "User authentication",
                    "body": {
                        "username": "string",
                        "password": "string",
                        "device_id": "string (optional)",
                        "platform": "string (optional)"
                    }
                },
                "/search": {
                    "method": "POST",
                    "description": "Search for parts",
                    "auth_required": True,
                    "body": {
                        "query": "string",
                        "search_type": "smart|ai|keyword|fuzzy",
                        "limit": "integer (max 50)"
                    }
                },
                "/parts/<part_number>/qr": {
                    "method": "GET",
                    "description": "Generate QR code for part",
                    "auth_required": True
                },
                "/favorites": {
                    "methods": ["GET", "POST", "DELETE"],
                    "description": "Manage user favorites",
                    "auth_required": True
                },
                "/analytics/dashboard": {
                    "method": "GET",
                    "description": "Mobile analytics dashboard",
                    "auth_required": True
                },
                "/export/<format>": {
                    "method": "GET",
                    "description": "Export data (admin only)",
                    "auth_required": True,
                    "formats": ["csv", "json"]
                },
                "/health": {
                    "method": "GET",
                    "description": "API health check",
                    "auth_required": False
                }
            }
        }
    }
    
    return docs

if __name__ == "__main__":
    # Create and run mobile API
    api = MobileAPI()
    
    # Print API documentation
    docs = create_api_documentation()
    print(json.dumps(docs, indent=2))
    
    # Run the API server
    api.run(debug=True)
