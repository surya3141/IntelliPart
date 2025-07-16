"""
IntelliPart Performance Optimization Module
Provides caching, indexing, and performance improvements
"""

import json
import pickle
import hashlib
import time
from functools import lru_cache, wraps
from typing import Dict, List, Any, Optional
import threading
import os
from collections import defaultdict
import sqlite3

class PerformanceOptimizer:
    def __init__(self, jsonl_path: str, cache_dir: str = "cache"):
        """Initialize performance optimizer."""
        self.jsonl_path = jsonl_path
        self.cache_dir = cache_dir
        self.db_path = os.path.join(cache_dir, "parts_index.db")
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize SQLite index
        self.init_sqlite_index()
        
        print("Performance optimizer initialized")
    
    def init_sqlite_index(self):
        """Initialize SQLite database for fast lookups."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create parts table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY,
                part_number TEXT UNIQUE,
                part_name TEXT,
                system TEXT,
                manufacturer TEXT,
                part_type TEXT,
                cost_numeric REAL,
                stock_numeric INTEGER,
                searchable_text TEXT,
                json_data TEXT
            )
        ''')
        
        # Create indexes for fast searching
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_part_number ON parts(part_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_system ON parts(system)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_manufacturer ON parts(manufacturer)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_part_type ON parts(part_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cost ON parts(cost_numeric)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock ON parts(stock_numeric)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_searchable ON parts(searchable_text)')
        
        conn.commit()
        conn.close()
        print("SQLite index initialized")
    
    def index_parts_data(self, parts: List[Dict[str, Any]]):
        """Index parts data in SQLite for fast retrieval."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM parts')
        
        # Insert all parts
        for i, part in enumerate(parts):
            part_number = part.get('part_number', f'part_{i}')
            part_name = part.get('part_name', '')
            system = part.get('system', '')
            manufacturer = part.get('manufacturer', '')
            part_type = part.get('part_type', '')
            
            # Extract numeric cost
            cost_numeric = self._extract_cost(part.get('cost', '0'))
            
            # Extract numeric stock
            stock_numeric = self._extract_stock(part.get('stock', '0'))
            
            # Create searchable text
            searchable_text = self._create_searchable_text(part)
            
            # Store full JSON data
            json_data = json.dumps(part)
            
            cursor.execute('''
                INSERT OR REPLACE INTO parts 
                (part_number, part_name, system, manufacturer, part_type, 
                 cost_numeric, stock_numeric, searchable_text, json_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (part_number, part_name, system, manufacturer, part_type,
                  cost_numeric, stock_numeric, searchable_text, json_data))
        
        conn.commit()
        conn.close()
        print(f"Indexed {len(parts)} parts in SQLite")
    
    def _extract_cost(self, cost_str: str) -> float:
        """Extract numeric cost."""
        try:
            import re
            numeric = re.sub(r'[^\d.]', '', str(cost_str))
            return float(numeric) if numeric else 0
        except:
            return 0
    
    def _extract_stock(self, stock_str: str) -> int:
        """Extract numeric stock."""
        try:
            return int(float(str(stock_str)))
        except:
            return 0
    
    def _create_searchable_text(self, part: Dict[str, Any]) -> str:
        """Create searchable text from part."""
        import re
        text_parts = []
        
        important_fields = [
            'part_name', 'part_type', 'system', 'sub_system',
            'manufacturer', 'type', 'material', 'feature'
        ]
        
        for field in important_fields:
            if field in part and part[field]:
                text = str(part[field]).lower()
                text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
                text_parts.append(text)
        
        return ' '.join(text_parts)
    
    def fast_search(self, 
                   query: str = "",
                   system: str = "",
                   manufacturer: str = "",
                   min_cost: float = 0,
                   max_cost: float = float('inf'),
                   min_stock: int = 0,
                   limit: int = 20) -> List[Dict[str, Any]]:
        """Fast search using SQLite index."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build SQL query
        where_conditions = []
        params = []
        
        if query:
            where_conditions.append("searchable_text LIKE ?")
            params.append(f"%{query.lower()}%")
        
        if system:
            where_conditions.append("system = ?")
            params.append(system)
        
        if manufacturer:
            where_conditions.append("manufacturer = ?")
            params.append(manufacturer)
        
        if min_cost > 0:
            where_conditions.append("cost_numeric >= ?")
            params.append(min_cost)
        
        if max_cost < float('inf'):
            where_conditions.append("cost_numeric <= ?")
            params.append(max_cost)
        
        if min_stock > 0:
            where_conditions.append("stock_numeric >= ?")
            params.append(min_stock)
        
        # Construct full query
        sql = "SELECT json_data FROM parts"
        if where_conditions:
            sql += " WHERE " + " AND ".join(where_conditions)
        sql += " LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        results = []
        
        for row in cursor.fetchall():
            part_data = json.loads(row[0])
            results.append(part_data)
        
        conn.close()
        return results
    
    def get_filter_options_fast(self) -> Dict[str, List[str]]:
        """Get filter options using SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get unique systems
        cursor.execute("SELECT DISTINCT system FROM parts WHERE system != '' ORDER BY system")
        systems = [row[0] for row in cursor.fetchall()]
        
        # Get unique manufacturers
        cursor.execute("SELECT DISTINCT manufacturer FROM parts WHERE manufacturer != '' ORDER BY manufacturer")
        manufacturers = [row[0] for row in cursor.fetchall()]
        
        # Get unique part types
        cursor.execute("SELECT DISTINCT part_type FROM parts WHERE part_type != '' ORDER BY part_type")
        part_types = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'systems': systems,
            'manufacturers': manufacturers,
            'part_types': part_types
        }
    
    def get_stats_fast(self) -> Dict[str, Any]:
        """Get statistics using SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM parts")
        total_parts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT system) FROM parts WHERE system != ''")
        unique_systems = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT manufacturer) FROM parts WHERE manufacturer != ''")
        unique_manufacturers = cursor.fetchone()[0]
        
        # Cost statistics
        cursor.execute("SELECT AVG(cost_numeric), MIN(cost_numeric), MAX(cost_numeric) FROM parts WHERE cost_numeric > 0")
        cost_stats = cursor.fetchone()
        avg_cost, min_cost, max_cost = cost_stats if cost_stats[0] else (0, 0, 0)
        
        # Stock statistics
        cursor.execute("SELECT SUM(stock_numeric), COUNT(*) FROM parts WHERE stock_numeric = 0")
        stock_stats = cursor.fetchone()
        total_stock, out_of_stock = stock_stats if stock_stats[0] else (0, 0)
        
        conn.close()
        
        return {
            'total_parts': total_parts,
            'unique_systems': unique_systems,
            'unique_manufacturers': unique_manufacturers,
            'avg_cost': round(avg_cost, 2) if avg_cost else 0,
            'cost_range': {
                'min': min_cost,
                'max': max_cost,
                'avg': round(avg_cost, 2) if avg_cost else 0
            },
            'out_of_stock_count': out_of_stock,
            'total_stock': total_stock
        }

class CacheManager:
    """Manages caching for search results and computations."""
    
    def __init__(self, cache_dir: str = "cache", max_size: int = 1000):
        self.cache_dir = cache_dir
        self.max_size = max_size
        self._cache = {}
        self._access_times = {}
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        if key in self._cache:
            self._access_times[key] = time.time()
            return self._cache[key]
        
        # Try loading from disk
        cache_file = os.path.join(self.cache_dir, f"{key}.cache")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self._cache[key] = data
                    self._access_times[key] = time.time()
                    return data
            except:
                os.remove(cache_file)
        
        return None
    
    def set(self, key: str, value: Any):
        """Set item in cache."""
        # Clean cache if too large
        if len(self._cache) >= self.max_size:
            self._cleanup_cache()
        
        self._cache[key] = value
        self._access_times[key] = time.time()
        
        # Save to disk
        cache_file = os.path.join(self.cache_dir, f"{key}.cache")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
        except:
            pass
    
    def _cleanup_cache(self):
        """Remove least recently used items."""
        # Sort by access time and remove oldest 25%
        sorted_items = sorted(self._access_times.items(), key=lambda x: x[1])
        to_remove = sorted_items[:len(sorted_items) // 4]
        
        for key, _ in to_remove:
            self._cache.pop(key, None)
            self._access_times.pop(key, None)
            
            # Remove from disk
            cache_file = os.path.join(self.cache_dir, f"{key}.cache")
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                except:
                    pass

def cache_result(cache_manager: CacheManager, expire_minutes: int = 60):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{func.__name__}_{args}_{sorted(kwargs.items())}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached = cache_manager.get(cache_key)
            if cached is not None:
                cache_time, result = cached
                if time.time() - cache_time < expire_minutes * 60:
                    return result
            
            # Compute and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, (time.time(), result))
            return result
        
        return wrapper
    return decorator

class BatchProcessor:
    """Process large datasets in batches for better performance."""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
    
    def process_in_batches(self, data: List[Any], process_func, **kwargs):
        """Process data in batches."""
        results = []
        total_batches = (len(data) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            
            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")
            
            batch_results = process_func(batch, **kwargs)
            results.extend(batch_results)
        
        return results

class MemoryOptimizer:
    """Optimize memory usage for large datasets."""
    
    @staticmethod
    def compress_part_data(part: Dict[str, Any]) -> Dict[str, Any]:
        """Compress part data by removing empty fields and optimizing types."""
        compressed = {}
        
        for key, value in part.items():
            if value is None or value == "":
                continue
            
            # Optimize numeric fields
            if key in ['cost_numeric', 'stock_numeric', 'weight_numeric']:
                try:
                    if isinstance(value, str):
                        value = float(value)
                    compressed[key] = value
                except:
                    continue
            else:
                compressed[key] = value
        
        return compressed
    
    @staticmethod
    def create_part_summary(part: Dict[str, Any]) -> Dict[str, Any]:
        """Create a lightweight summary of part for search results."""
        summary_fields = [
            'part_number', 'part_name', 'system', 'manufacturer',
            'part_type', 'cost', 'stock', 'material'
        ]
        
        summary = {}
        for field in summary_fields:
            if field in part and part[field]:
                summary[field] = part[field]
        
        return summary

# Example usage with the enhanced app
class OptimizedIntelliPartApp:
    """Enhanced IntelliPart app with performance optimizations."""
    
    def __init__(self, jsonl_path: str):
        self.jsonl_path = jsonl_path
        self.optimizer = PerformanceOptimizer(jsonl_path)
        self.cache_manager = CacheManager()
        self.batch_processor = BatchProcessor()
        
        # Load and index data
        self.parts = self._load_parts()
        self.optimizer.index_parts_data(self.parts)
        
        print(f"Optimized IntelliPart ready with {len(self.parts)} parts")
    
    def _load_parts(self) -> List[Dict[str, Any]]:
        """Load parts with memory optimization."""
        parts = []
        with open(self.jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    part = json.loads(line)
                    compressed_part = MemoryOptimizer.compress_part_data(part)
                    parts.append(compressed_part)
        return parts
    
    @cache_result(CacheManager(), expire_minutes=30)
    def optimized_search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Optimized search with caching."""
        start_time = time.time()
        
        # Use SQLite for fast filtering
        results = self.optimizer.fast_search(query=query, **kwargs)
        
        search_time = time.time() - start_time
        
        return {
            'results': results,
            'total_found': len(results),
            'search_time': round(search_time, 3),
            'cached': False
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimized statistics."""
        return self.optimizer.get_stats_fast()
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get optimized filter options."""
        return self.optimizer.get_filter_options_fast()

if __name__ == "__main__":
    # Test the optimization
    print("Testing IntelliPart Performance Optimizations...")
    
    # Initialize optimized app
    app = OptimizedIntelliPartApp("synthetic_car_parts_500.jsonl")
    
    # Test search performance
    start_time = time.time()
    results = app.optimized_search("brake", limit=10)
    end_time = time.time()
    
    print(f"Search completed in {end_time - start_time:.3f}s")
    print(f"Found {results['total_found']} results")
    
    # Test stats
    stats = app.get_stats()
    print(f"Stats: {stats}")
    
    print("Performance optimization test completed!")
