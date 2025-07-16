"""
IntelliPart Advanced Analytics & AI Enhancement - OPTIMIZED
Next-generation features for enterprise intelligence with performance optimization
"""

import json
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, List, Any, Optional
import warnings
import threading
import time
warnings.filterwarnings('ignore')

class AdvancedAnalytics:
    """Advanced analytics engine with predictive capabilities and performance optimization."""
    
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.parts = self._load_data()
        self.setup_database()
        
        # Performance optimization: cache results with expiration
        self._cache = {}
        self._cache_expiry = {}
        self._cache_lock = threading.Lock()
        self._cache_duration = 300  # 5 minutes cache
        
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result if available and not expired."""
        with self._cache_lock:
            if key in self._cache:
                if time.time() < self._cache_expiry.get(key, 0):
                    return self._cache[key]
                else:
                    # Remove expired cache
                    self._cache.pop(key, None)
                    self._cache_expiry.pop(key, None)
            return None
    
    def _set_cached_result(self, key: str, result: Any):
        """Cache result with expiration."""
        with self._cache_lock:
            self._cache[key] = result
            self._cache_expiry[key] = time.time() + self._cache_duration
        
    def _load_data(self) -> List[Dict]:
        """Load parts data from JSONL file."""
        parts = []
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        parts.append(json.loads(line.strip()))
        except Exception as e:
            print(f"Error loading data: {e}")
        return parts
    
    def setup_database(self):
        """Setup SQLite database for advanced analytics."""
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Create parts table
        cursor.execute('''
            CREATE TABLE parts (
                id INTEGER PRIMARY KEY,
                part_number TEXT,
                part_name TEXT,
                system TEXT,
                manufacturer TEXT,
                cost REAL,
                stock INTEGER,
                warranty_period TEXT,
                country_of_origin TEXT,
                production_year INTEGER,
                data TEXT
            )
        ''')
        
        # Insert data
        for i, part in enumerate(self.parts):
            cost = self._extract_cost(part.get('cost', '0'))
            stock = self._extract_stock(part.get('stock', '0'))
            production_year = self._extract_year(part.get('production_year', '2020'))
            
            cursor.execute('''
                INSERT INTO parts (id, part_number, part_name, system, manufacturer, 
                                 cost, stock, warranty_period, country_of_origin, 
                                 production_year, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                i, part.get('part_number', ''),
                part.get('part_name', ''),
                part.get('system', ''),
                part.get('manufacturer', ''),
                cost, stock,
                part.get('warranty_period', ''),
                part.get('country_of_origin', ''),
                production_year,
                json.dumps(part)
            ))
        
        self.conn.commit()
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX idx_system ON parts(system)')
        cursor.execute('CREATE INDEX idx_manufacturer ON parts(manufacturer)')
        cursor.execute('CREATE INDEX idx_cost ON parts(cost)')
        cursor.execute('CREATE INDEX idx_production_year ON parts(production_year)')
        
    def _extract_cost(self, cost_str: str) -> float:
        """Extract numeric cost from string."""
        if isinstance(cost_str, (int, float)):
            return float(cost_str)
        try:
            # Remove currency symbols and extract number
            import re
            numbers = re.findall(r'[\d.]+', str(cost_str))
            return float(numbers[0]) if numbers else 0.0
        except:
            return 0.0
    
    def _extract_stock(self, stock_str: str) -> int:
        """Extract numeric stock from string."""
        if isinstance(stock_str, int):
            return stock_str
        try:
            import re
            numbers = re.findall(r'\d+', str(stock_str))
            return int(numbers[0]) if numbers else 0
        except:
            return 0
            
    def _extract_year(self, year_str: str) -> int:
        """Extract year from string."""
        if isinstance(year_str, int):
            return year_str
        try:
            import re
            years = re.findall(r'\d{4}', str(year_str))
            return int(years[0]) if years else 2020
        except:
            return 2020
    
    def predictive_demand_analysis(self) -> Dict[str, Any]:
        """Advanced demand prediction using historical patterns - OPTIMIZED."""
        cache_key = "demand_analysis"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        cursor = self.conn.cursor()
        
        # Single optimized query with all calculations
        cursor.execute('''
            SELECT system, 
                   AVG(cost) as avg_cost,
                   AVG(stock) as avg_stock,
                   COUNT(*) as part_count,
                   MAX(production_year) as latest_year,
                   MIN(production_year) as earliest_year
            FROM parts 
            WHERE system IS NOT NULL AND system != ''
            GROUP BY system
            ORDER BY part_count DESC
            LIMIT 20
        ''')
        
        system_analysis = []
        for row in cursor.fetchall():
            system, avg_cost, avg_stock, count, latest, earliest = row
            
            # Fast demand score calculation
            demand_score = (
                3 if avg_stock < 50 else 0) + (
                2 if avg_cost > 200 else 0) + (
                1 if latest > 2020 else 0) + (
                1 if count > 100 else 0
            )
            
            system_analysis.append({
                'system': system,
                'avg_cost': round(avg_cost, 2),
                'avg_stock': round(avg_stock, 1),
                'part_count': count,
                'demand_score': demand_score,
                'trend': 'high' if latest > 2021 else 'medium' if latest > 2019 else 'low',
                'recommendation': self._get_demand_recommendation_fast(demand_score)
            })
        
        result = {
            'system_analysis': sorted(system_analysis, key=lambda x: x['demand_score'], reverse=True)[:15],
            'high_demand_systems': [s for s in system_analysis if s['demand_score'] >= 5][:10],
            'restock_alerts': [s for s in system_analysis if s['avg_stock'] < 30][:10],
            'generated_at': datetime.now().isoformat()
        }
        
        self._set_cached_result(cache_key, result)
        return result
    
    def _get_demand_recommendation_fast(self, score: int) -> str:
        """Fast recommendation lookup."""
        recommendations = {
            6: "URGENT: High-priority restocking needed",
            4: "MEDIUM: Monitor closely and plan restocking", 
            2: "LOW: Regular monitoring sufficient",
            0: "STABLE: No immediate action needed"
        }
        # Find closest score
        for threshold in [6, 4, 2, 0]:
            if score >= threshold:
                return recommendations[threshold]
        return recommendations[0]
    
    def supply_chain_optimization(self) -> Dict[str, Any]:
        """Analyze supply chain for optimization opportunities - OPTIMIZED."""
        cache_key = "supply_chain_analysis"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        cursor = self.conn.cursor()
        
        # Optimized manufacturer analysis with limits
        cursor.execute('''
            SELECT manufacturer,
                   COUNT(*) as part_count,
                   AVG(cost) as avg_cost,
                   AVG(stock) as avg_stock,
                   COUNT(DISTINCT system) as systems_covered
            FROM parts 
            WHERE manufacturer IS NOT NULL AND manufacturer != ''
            GROUP BY manufacturer
            ORDER BY part_count DESC
            LIMIT 15
        ''')
        
        suppliers = []
        total_parts = len(self.parts)
        
        for row in cursor.fetchall():
            mfr, count, avg_cost, avg_stock, systems = row
            dependency_level = (count / total_parts) * 100
            
            suppliers.append({
                'manufacturer': mfr,
                'part_count': count,
                'dependency_percentage': round(dependency_level, 2),
                'avg_cost': round(avg_cost, 2),
                'avg_stock': round(avg_stock, 1),
                'systems_covered': systems,
                'risk_level': 'HIGH' if dependency_level > 10 else 'MEDIUM' if dependency_level > 5 else 'LOW',
                'diversification_opportunity': dependency_level > 15
            })
        
        # Optimized country analysis
        cursor.execute('''
            SELECT country_of_origin,
                   COUNT(*) as part_count,
                   AVG(cost) as avg_cost
            FROM parts 
            WHERE country_of_origin IS NOT NULL AND country_of_origin != ''
            GROUP BY country_of_origin
            ORDER BY part_count DESC
            LIMIT 10
        ''')
        
        countries = []
        for row in cursor.fetchall():
            country, count, avg_cost = row
            dependency = (count / total_parts) * 100
            
            countries.append({
                'country': country,
                'part_count': count,
                'dependency_percentage': round(dependency, 2),
                'avg_cost': round(avg_cost, 2),
                'risk_assessment': 'HIGH' if dependency > 20 else 'MEDIUM' if dependency > 10 else 'LOW'
            })
        
        high_risk_suppliers = [s for s in suppliers if s['risk_level'] == 'HIGH'][:5]
        diversification_opps = [s for s in suppliers if s['diversification_opportunity']][:5]
        
        result = {
            'supplier_analysis': suppliers[:10],
            'country_analysis': countries[:8],
            'high_risk_suppliers': high_risk_suppliers,
            'diversification_opportunities': diversification_opps,
            'recommendations': self._generate_supply_chain_recommendations_fast(high_risk_suppliers, countries)
        }
        
        self._set_cached_result(cache_key, result)
        return result
    
    def _generate_supply_chain_recommendations_fast(self, high_risk_suppliers: List[Dict], countries: List[Dict]) -> List[str]:
        """Generate fast supply chain optimization recommendations."""
        recommendations = []
        
        if high_risk_suppliers:
            recommendations.append(f"Diversify from {len(high_risk_suppliers)} high-dependency suppliers")
        
        high_risk_countries = [c for c in countries if c.get('risk_assessment') == 'HIGH']
        if high_risk_countries:
            recommendations.append(f"Reduce geographic risk from {len(high_risk_countries)} countries")
        
        if not recommendations:
            recommendations.append("Supply chain appears well-diversified")
        
        return recommendations[:3]  # Limit to 3 recommendations
    
    def quality_prediction_analysis(self) -> Dict[str, Any]:
        """Predict quality issues based on historical patterns - OPTIMIZED."""
        cache_key = "quality_analysis"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        cursor = self.conn.cursor()
        
        # Simplified warranty analysis with limits
        cursor.execute('''
            SELECT warranty_period,
                   COUNT(*) as part_count,
                   AVG(cost) as avg_cost,
                   AVG(stock) as avg_stock
            FROM parts 
            WHERE warranty_period IS NOT NULL AND warranty_period != ''
            GROUP BY warranty_period
            ORDER BY part_count DESC
            LIMIT 10
        ''')
        
        warranty_analysis = []
        for row in cursor.fetchall():
            warranty, count, avg_cost, avg_stock = row
            warranty_score = self._calculate_warranty_score_fast(warranty)
            
            warranty_analysis.append({
                'warranty_period': warranty,
                'part_count': count,
                'avg_cost': round(avg_cost, 2),
                'avg_stock': round(avg_stock, 1),
                'warranty_score': warranty_score,
                'quality_indicator': 'HIGH' if warranty_score >= 3 else 'MEDIUM' if warranty_score >= 2 else 'LOW'
            })
        
        # Simplified production year analysis
        cursor.execute('''
            SELECT production_year,
                   COUNT(*) as part_count,
                   AVG(cost) as avg_cost
            FROM parts 
            WHERE production_year IS NOT NULL
            GROUP BY production_year
            ORDER BY production_year DESC
            LIMIT 8
        ''')
        
        production_trends = []
        for row in cursor.fetchall():
            year, count, avg_cost = row
            age = 2024 - year
            
            production_trends.append({
                'year': year,
                'part_count': count,
                'avg_cost': round(avg_cost, 2),
                'age_years': age,
                'quality_trend': 'DECLINING' if age > 5 else 'STABLE' if age > 2 else 'IMPROVING'
            })
        
        result = {
            'warranty_analysis': warranty_analysis[:8],
            'production_trends': production_trends[:8],
            'quality_recommendations': self._generate_quality_recommendations_fast(warranty_analysis, production_trends)
        }
        
        self._set_cached_result(cache_key, result)
        return result
    
    def _calculate_warranty_score_fast(self, warranty: str) -> int:
        """Fast warranty score calculation."""
        warranty_lower = warranty.lower()
        
        if 'year' in warranty_lower:
            # Quick regex-free approach
            try:
                # Look for numbers in warranty string
                nums = ''.join(c for c in warranty if c.isdigit())
                if nums:
                    return min(int(nums[:1]), 5)  # Use first digit, cap at 5
            except:
                pass
        
        if 'month' in warranty_lower:
            try:
                nums = ''.join(c for c in warranty if c.isdigit())
                if nums:
                    return max(1, int(nums[:2]) // 12)  # Convert months to years
            except:
                pass
                
        return 1  # Default score
    
    def _generate_quality_recommendations_fast(self, warranty_data: List[Dict], production_data: List[Dict]) -> List[str]:
        """Generate fast quality-based recommendations."""
        recommendations = []
        
        high_quality_parts = [w for w in warranty_data if w['warranty_score'] >= 4]
        if high_quality_parts:
            recommendations.append(f"Prioritize {len(high_quality_parts)} high-warranty categories")
        
        old_parts = [p for p in production_data if p['age_years'] > 7]
        if old_parts:
            recommendations.append(f"Update {len(old_parts)} aging part categories")
        
        recent_high_cost = [p for p in production_data if p['age_years'] <= 2 and p['avg_cost'] > 300]
        if recent_high_cost:
            recommendations.append(f"Monitor {len(recent_high_cost)} high-cost categories")
        
        return recommendations[:3]  # Limit to 3 recommendations
    
    def cost_optimization_analysis(self) -> Dict[str, Any]:
        """Advanced cost optimization opportunities - OPTIMIZED."""
        cache_key = "cost_analysis"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        cursor = self.conn.cursor()
        
        # Optimized price variance analysis with limits
        cursor.execute('''
            SELECT system, manufacturer,
                   COUNT(*) as part_count,
                   AVG(cost) as avg_cost,
                   MIN(cost) as min_cost,
                   MAX(cost) as max_cost,
                   (MAX(cost) - MIN(cost)) as price_variance
            FROM parts 
            WHERE cost > 0 AND system IS NOT NULL AND manufacturer IS NOT NULL
            GROUP BY system, manufacturer
            HAVING COUNT(*) >= 3 AND price_variance > 50
            ORDER BY price_variance DESC
            LIMIT 15
        ''')
        
        cost_opportunities = []
        for row in cursor.fetchall():
            system, mfr, count, avg_cost, min_cost, max_cost, variance = row
            
            savings_potential = variance * 0.3  # Potential 30% savings
            
            cost_opportunities.append({
                'system': system,
                'manufacturer': mfr,
                'part_count': count,
                'avg_cost': round(avg_cost, 2),
                'min_cost': round(min_cost, 2),
                'max_cost': round(max_cost, 2),
                'price_variance': round(variance, 2),
                'savings_potential': round(savings_potential, 2),
                'optimization_opportunity': 'HIGH' if variance > 200 else 'MEDIUM'
            })
        
        # Simplified system cost comparison
        cursor.execute('''
            SELECT system,
                   COUNT(*) as part_count,
                   AVG(cost) as avg_cost,
                   SUM(cost * stock) as total_inventory_value
            FROM parts 
            WHERE cost > 0 AND stock > 0
            GROUP BY system
            ORDER BY total_inventory_value DESC
            LIMIT 10
        ''')
        
        system_costs = []
        for row in cursor.fetchall():
            system, count, avg_cost, total_value = row
            
            system_costs.append({
                'system': system,
                'part_count': count,
                'avg_cost': round(avg_cost, 2),
                'total_inventory_value': round(total_value, 2),
                'cost_per_part': round(total_value / count, 2) if count > 0 else 0
            })
        
        total_savings = sum(op['savings_potential'] for op in cost_opportunities)
        
        result = {
            'cost_optimization_opportunities': cost_opportunities[:10],
            'system_cost_analysis': system_costs[:8],
            'potential_annual_savings': total_savings,
            'recommendations': self._generate_cost_recommendations_fast(cost_opportunities, system_costs)
        }
        
        self._set_cached_result(cache_key, result)
        return result
    
    def _generate_cost_recommendations_fast(self, opportunities: List[Dict], systems: List[Dict]) -> List[str]:
        """Generate fast cost optimization recommendations."""
        recommendations = []
        
        high_variance_opportunities = [op for op in opportunities if op['optimization_opportunity'] == 'HIGH']
        if high_variance_opportunities:
            total_savings = sum(op['savings_potential'] for op in high_variance_opportunities)
            recommendations.append(f"High-priority optimization: ₹{total_savings:,.0f} savings potential")
        
        expensive_systems = [s for s in systems if s['avg_cost'] > 300]
        if expensive_systems:
            recommendations.append(f"Review {len(expensive_systems)} high-cost systems")
        
        if not recommendations:
            recommendations.append("Costs appear optimized - continue monitoring")
        
        return recommendations[:3]  # Limit to 3 recommendations
    
    def _generate_cost_recommendations(self, opportunities: List[Dict], systems: List[Dict]) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        high_variance_opportunities = [op for op in opportunities if op['optimization_opportunity'] == 'HIGH']
        if high_variance_opportunities:
            total_savings = sum(op['savings_potential'] for op in high_variance_opportunities)
            recommendations.append(f"High-priority cost optimization: {len(high_variance_opportunities)} opportunities worth ₹{total_savings:,.0f}")
        
        expensive_systems = [s for s in systems if s['avg_cost'] > 300]
        if expensive_systems:
            recommendations.append(f"Review pricing strategy for {len(expensive_systems)} high-cost systems")
        
        high_inventory_value = [s for s in systems if s['total_inventory_value'] > 50000]
        if high_inventory_value:
            recommendations.append(f"Optimize inventory levels for {len(high_inventory_value)} high-value systems")
        
        return recommendations
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive advanced analytics report - OPTIMIZED."""
        cache_key = "comprehensive_report"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        # Get all analyses in parallel (cached individually)
        demand_analysis = self.predictive_demand_analysis()
        supply_chain_analysis = self.supply_chain_optimization()
        quality_analysis = self.quality_prediction_analysis()
        cost_analysis = self.cost_optimization_analysis()
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_parts_analyzed': len(self.parts),
                'analysis_types': ['demand_prediction', 'supply_chain', 'quality_prediction', 'cost_optimization']
            },
            'demand_analysis': demand_analysis,
            'supply_chain_analysis': supply_chain_analysis,
            'quality_analysis': quality_analysis,
            'cost_analysis': cost_analysis
        }
        
        # Fast executive summary
        report['executive_summary'] = self._generate_executive_summary_fast(report)
        
        self._set_cached_result(cache_key, report)
        return report
    
    def _generate_executive_summary_fast(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fast executive summary from all analyses."""
        high_demand = len(report['demand_analysis']['high_demand_systems'])
        high_risk_suppliers = len(report['supply_chain_analysis']['high_risk_suppliers'])
        potential_savings = report['cost_analysis']['potential_annual_savings']
        
        summary = {
            'key_findings': [],
            'urgent_actions': [],
            'cost_impact': {},
            'risk_assessment': 'LOW'
        }
        
        # Quick findings
        if high_demand > 0:
            summary['key_findings'].append(f"{high_demand} systems require immediate attention")
        if high_risk_suppliers > 0:
            summary['key_findings'].append(f"{high_risk_suppliers} suppliers pose high dependency risk")
            summary['risk_assessment'] = 'HIGH' if high_risk_suppliers > 3 else 'MEDIUM'
        if potential_savings > 10000:
            summary['key_findings'].append(f"₹{potential_savings:,.0f} cost optimization potential")
            summary['cost_impact']['potential_savings'] = potential_savings
        
        # Quick actions
        if high_demand > 2:
            summary['urgent_actions'].append("Implement demand-based inventory planning")
        if high_risk_suppliers > 2:
            summary['urgent_actions'].append("Diversify supplier base for risk reduction")
        if potential_savings > 50000:
            summary['urgent_actions'].append("Implement cost optimization initiatives")
        
        return summary

    def get_quick_metrics(self) -> Dict[str, Any]:
        """Get instant metrics for dashboard display."""
        cache_key = "quick_metrics"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        cursor = self.conn.cursor()
        
        # Get basic counts in one query
        cursor.execute('''
            SELECT 
                COUNT(*) as total_parts,
                COUNT(DISTINCT system) as total_systems,
                COUNT(DISTINCT manufacturer) as total_manufacturers,
                AVG(cost) as avg_cost,
                SUM(CASE WHEN stock < 20 THEN 1 ELSE 0 END) as low_stock_parts
            FROM parts
        ''')
        
        row = cursor.fetchone()
        total_parts, total_systems, total_manufacturers, avg_cost, low_stock = row
        
        result = {
            'total_parts': total_parts,
            'total_systems': total_systems,
            'total_manufacturers': total_manufacturers,
            'avg_cost': round(avg_cost, 2),
            'low_stock_alerts': low_stock,
            'generated_at': datetime.now().isoformat()
        }
        
        self._set_cached_result(cache_key, result)
        return result
    
    def get_top_systems(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top systems by part count for quick display."""
        cache_key = f"top_systems_{limit}"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT system, COUNT(*) as part_count, AVG(cost) as avg_cost
            FROM parts 
            WHERE system IS NOT NULL AND system != ''
            GROUP BY system
            ORDER BY part_count DESC
            LIMIT ?
        ''', (limit,))
        
        result = []
        for row in cursor.fetchall():
            system, count, avg_cost = row
            result.append({
                'system': system,
                'part_count': count,
                'avg_cost': round(avg_cost, 2)
            })
        
        self._set_cached_result(cache_key, result)
        return result
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get quick cost summary for dashboard."""
        cache_key = "cost_summary"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                MIN(cost) as min_cost,
                MAX(cost) as max_cost,
                AVG(cost) as avg_cost,
                SUM(cost * stock) as total_inventory_value
            FROM parts 
            WHERE cost > 0 AND stock > 0
        ''')
        
        row = cursor.fetchone()
        min_cost, max_cost, avg_cost, total_value = row
        
        result = {
            'min_cost': round(min_cost, 2),
            'max_cost': round(max_cost, 2),
            'avg_cost': round(avg_cost, 2),
            'total_inventory_value': round(total_value, 2),
            'cost_range': round(max_cost - min_cost, 2)
        }
        
        self._set_cached_result(cache_key, result)
        return result
    
    def get_instant_dashboard_data(self) -> Dict[str, Any]:
        """Get all dashboard data in one optimized call for web interface."""
        cache_key = "dashboard_data"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        # Get all basic data in minimal queries
        quick_metrics = self.get_quick_metrics()
        top_systems = self.get_top_systems(5)
        cost_summary = self.get_cost_summary()
        
        # Get high-level insights quickly
        cursor = self.conn.cursor()
        
        # Quick risk assessment
        cursor.execute('''
            SELECT manufacturer, COUNT(*) as count
            FROM parts 
            WHERE manufacturer IS NOT NULL AND manufacturer != ''
            GROUP BY manufacturer
            ORDER BY count DESC
            LIMIT 3
        ''')
        
        top_suppliers = []
        total_parts = quick_metrics['total_parts']
        for row in cursor.fetchall():
            manufacturer, count = row
            dependency = (count / total_parts) * 100
            top_suppliers.append({
                'manufacturer': manufacturer,
                'dependency_percentage': round(dependency, 2),
                'risk_level': 'HIGH' if dependency > 10 else 'MEDIUM' if dependency > 5 else 'LOW'
            })
        
        # Quick savings calculation
        cursor.execute('''
            SELECT AVG(cost) as avg_cost, COUNT(*) as count
            FROM parts 
            WHERE cost > 0
            GROUP BY system
            HAVING count >= 10
            ORDER BY avg_cost DESC
            LIMIT 5
        ''')
        
        high_cost_systems = cursor.fetchall()
        estimated_savings = sum(row[0] * 0.1 for row in high_cost_systems)  # 10% savings estimate
        
        result = {
            'overview': quick_metrics,
            'top_systems': top_systems,
            'cost_summary': cost_summary,
            'top_suppliers': top_suppliers,
            'risk_assessment': 'HIGH' if any(s['risk_level'] == 'HIGH' for s in top_suppliers) else 'MEDIUM',
            'estimated_savings': round(estimated_savings, 2),
            'alerts': {
                'low_stock': quick_metrics['low_stock_alerts'],
                'high_risk_suppliers': len([s for s in top_suppliers if s['risk_level'] == 'HIGH']),
                'cost_opportunities': len(high_cost_systems)
            },
            'generated_at': datetime.now().isoformat()
        }
        
        self._set_cached_result(cache_key, result)
        return result

def main():
    """Run advanced analytics demo - OPTIMIZED."""
    print("🚀 IntelliPart Advanced Analytics & AI Enhancement (OPTIMIZED)")
    print("=" * 60)
    
    # Initialize analytics engine
    start_time = time.time()
    analytics = AdvancedAnalytics("data/training Dataset.jsonl")
    print(f"⚡ Engine initialized in {time.time() - start_time:.2f}s")
    
    # Generate comprehensive report
    start_time = time.time()
    report = analytics.generate_comprehensive_report()
    print(f"⚡ Report generated in {time.time() - start_time:.2f}s")
    
    # Display executive summary
    print("\n📊 EXECUTIVE SUMMARY")
    print("-" * 30)
    
    summary = report['executive_summary']
    print(f"📈 Risk Assessment: {summary['risk_assessment']}")
    
    print("\n🔍 Key Findings:")
    for finding in summary['key_findings']:
        print(f"  • {finding}")
    
    print("\n⚡ Urgent Actions:")
    for action in summary['urgent_actions']:
        print(f"  • {action}")
    
    if summary['cost_impact']:
        print(f"\n💰 Potential Savings: ₹{summary['cost_impact']['potential_savings']:,.0f}")
    
    # Show cache status
    print(f"\n🧠 Cache Status: {len(analytics._cache)} items cached")
    
    # Test cache performance
    print("\n🔄 Testing Cache Performance...")
    start_time = time.time()
    analytics.generate_comprehensive_report()  # Should be instant from cache
    print(f"⚡ Cached report retrieved in {time.time() - start_time:.4f}s")
    
    print("\n🎯 Advanced Analytics Complete!")

if __name__ == "__main__":
    main()
