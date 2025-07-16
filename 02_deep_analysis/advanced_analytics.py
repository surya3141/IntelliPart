"""
IntelliPart Advanced Analytics & AI Enhancement - OPTIMIZED

This module provides a comprehensive suite of advanced analytics and AI-powered
features for the IntelliPart project. It is designed for high performance,
utilizing an in-memory SQLite database for complex queries and a caching
mechanism to deliver real-time insights.

Key Features:
- Predictive Demand Analysis: Forecasts demand for various car systems.
- Supply Chain Optimization: Identifies risks and opportunities in the supply chain.
- Quality Prediction: Analyzes warranty and production data to predict quality issues.
- Cost Optimization: Finds opportunities to reduce costs through variance analysis.
- Comprehensive Reporting: Generates a consolidated report with an executive summary.
"""

import json
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, List, Any, Optional
import warnings
import threading
import time
from pathlib import Path
warnings.filterwarnings('ignore')

class AdvancedAnalytics:
    """
    The main class for handling advanced analytics.

    This class loads car parts data, sets up an in-memory database for efficient
    querying, and provides methods for various types of analysis. It includes
    a caching system to optimize performance for repeated requests.
    """
    
    def __init__(self, data_file: str):
        """
        Initializes the AdvancedAnalytics engine.

        Args:
            data_file (str): The path to the JSONL file containing the car parts data.
        """
        self.data_file = data_file
        self.parts = self._load_data()
        self.setup_database()
        
        # Performance optimization: cache results with expiration
        self._cache = {}
        self._cache_expiry = {}
        self._cache_lock = threading.Lock()
        self._cache_duration = 300  # 5 minutes cache
        
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """
        Retrieves a result from the cache if it is available and not expired.

        Args:
            key (str): The key for the cached item.

        Returns:
            Optional[Any]: The cached result, or None if it's not found or expired.
        """
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
        """
        Stores a result in the cache with a set expiration time.

        Args:
            key (str): The key to store the result under.
            result (Any): The result to be cached.
        """
        with self._cache_lock:
            self._cache[key] = result
            self._cache_expiry[key] = time.time() + self._cache_duration
        
    def _load_data(self) -> List[Dict]:
        """
        Loads car parts data from the specified JSONL file.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary represents a car part.
        """
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
        """
        Sets up an in-memory SQLite database and populates it with the car parts data.

        This method creates a 'parts' table, inserts all the data, and creates
        indexes on key columns to ensure fast query performance.
        """
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
        """
        Extracts a numerical cost value from a string (e.g., "₹1,200.50").

        Args:
            cost_str (str): The string containing the cost.

        Returns:
            float: The extracted cost as a float.
        """
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
        """
        Extracts a numerical stock value from a string.

        Args:
            stock_str (str): The string containing the stock quantity.

        Returns:
            int: The extracted stock as an integer.
        """
        if isinstance(stock_str, int):
            return stock_str
        try:
            import re
            numbers = re.findall(r'\d+', str(stock_str))
            return int(numbers[0]) if numbers else 0
        except:
            return 0
            
    def _extract_year(self, year_str: str) -> int:
        """
        Extracts a 4-digit year from a string.

        Args:
            year_str (str): The string containing the year.

        Returns:
            int: The extracted year as an integer.
        """
        if isinstance(year_str, int):
            return year_str
        try:
            import re
            years = re.findall(r'\d{4}', str(year_str))
            return int(years[0]) if years else 2020
        except:
            return 2020
    
    def predictive_demand_analysis(self) -> Dict[str, Any]:
        """
        Performs a predictive demand analysis based on historical data.

        This analysis groups parts by system and calculates metrics like average cost,
        average stock, and part count to derive a demand score.

        Returns:
            Dict[str, Any]: A dictionary containing the demand analysis results,
                            including system analysis, high-demand systems, and restock alerts.
        """
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
        """
        Provides a quick recommendation based on a demand score.

        Args:
            score (int): The demand score.

        Returns:
            str: A recommendation string.
        """
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
        """
        Analyzes the supply chain to identify risks and optimization opportunities.

        This method assesses supplier dependency and geographic concentration to
        identify potential risks in the supply chain.

        Returns:
            Dict[str, Any]: A dictionary with supply chain analysis, including
                            supplier and country analysis, and recommendations.
        """
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
        """
        Generates a list of recommendations for supply chain optimization.

        Args:
            high_risk_suppliers (List[Dict]): A list of suppliers with high dependency.
            countries (List[Dict]): A list of countries with analysis data.

        Returns:
            List[str]: A list of recommendation strings.
        """
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
        """
        Analyzes warranty periods and production years to predict potential quality issues.

        Returns:
            Dict[str, Any]: A dictionary containing the quality analysis, including
                            warranty analysis, production trends, and recommendations.
        """
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
        """
        Calculates a quality score based on the warranty period string.

        Args:
            warranty (str): The warranty period (e.g., "2 years", "24 months").

        Returns:
            int: A numerical quality score.
        """
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
        """
        Generates recommendations based on quality analysis.

        Args:
            warranty_data (List[Dict]): The results of the warranty analysis.
            production_data (List[Dict]): The results of the production trend analysis.

        Returns:
            List[str]: A list of recommendation strings.
        """
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
        """
        Identifies cost optimization opportunities by analyzing price variance.

        Returns:
            Dict[str, Any]: A dictionary containing cost optimization opportunities,
                            system cost analysis, and potential savings.
        """
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
        """
        Generates recommendations for cost optimization.

        Args:
            opportunities (List[Dict]): A list of cost-saving opportunities.
            systems (List[Dict]): A list of systems with their cost analysis.

        Returns:
            List[str]: A list of recommendation strings.
        """
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
        """
        DEPRECATED: Generate detailed cost optimization recommendations.
        This method is kept for reference but `_generate_cost_recommendations_fast` is used.
        """
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
        """
        Generates a single, comprehensive report by running all analysis types.

        Returns:
            Dict[str, Any]: A dictionary containing all analysis results and an
                            executive summary.
        """
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
        """
        Creates a high-level executive summary from the comprehensive report.

        Args:
            report (Dict[str, Any]): The comprehensive report.

        Returns:
            Dict[str, Any]: A dictionary containing key findings, urgent actions,
                            and a risk assessment.
        """
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
        """
        Retrieves a set of quick, high-level metrics for a dashboard display.

        Returns:
            Dict[str, Any]: A dictionary of key metrics.
        """
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
        """
        Gets the top N systems based on the number of associated parts.

        Args:
            limit (int, optional): The number of top systems to return. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a top system.
        """
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
        """
        Provides a quick summary of cost-related metrics.

        Returns:
            Dict[str, Any]: A dictionary containing min, max, and average cost,
                            as well as total inventory value.
        """
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
        """
        Gathers all necessary data for an instant dashboard in a single, optimized call.

        Returns:
            Dict[str, Any]: A dictionary containing all data needed for the dashboard.
        """
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

    def get_dataset_profile(self) -> Dict[str, Any]:
        """
        Profiles the dataset to extract schema, unique values, value ranges, and sample records.

        Returns:
            Dict[str, Any]: A dictionary containing dataset schema, unique values, value ranges, and samples.
        """
        cache_key = "dataset_profile"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result

        profile = {}
        if not self.parts:
            return profile

        # Get schema (all keys)
        schema = set()
        for part in self.parts:
            schema.update(part.keys())
        schema = list(schema)

        # Unique values and value ranges
        unique_values = {k: set() for k in schema}
        min_max = {}
        for part in self.parts:
            for k in schema:
                v = part.get(k)
                if v is not None:
                    unique_values[k].add(v)
                    if isinstance(v, (int, float)):
                        if k not in min_max:
                            min_max[k] = {'min': v, 'max': v}
                        else:
                            min_max[k]['min'] = min(min_max[k]['min'], v)
                            min_max[k]['max'] = max(min_max[k]['max'], v)
        # Convert sets to sorted lists (limit to 20 for brevity)
        unique_values = {k: sorted(list(v))[:20] for k, v in unique_values.items()}

        # Sample records
        samples = self.parts[:5]

        profile = {
            'schema': schema,
            'unique_values': unique_values,
            'min_max': min_max,
            'sample_records': samples,
            'total_records': len(self.parts)
        }
        self._set_cached_result(cache_key, profile)
        return profile

def get_script_root():
    return Path(__file__).parent.resolve()

def main():
    """
    Main function to run a demonstration of the AdvancedAnalytics module.
    
    Initializes the analytics engine, generates a comprehensive report,
    and prints a summary of the findings to the console. It also demonstrates
    the performance benefit of the caching system.
    """
    print("🚀 IntelliPart Advanced Analytics & AI Enhancement (OPTIMIZED)")
    print("=" * 60)
    
    # Use production dataset as default
    script_root = get_script_root()
    production_dataset = script_root.parent / "01_dataset_expansion" / "production_dataset" / "datasets"
    # Find a .jsonl file in the production dataset
    jsonl_files = list(production_dataset.glob("*.jsonl"))
    if jsonl_files:
        data_file = str(jsonl_files[0])
    else:
        data_file = "synthetic_car_parts_500.jsonl"
    # Initialize analytics engine
    start_time = time.time()
    analytics = AdvancedAnalytics(data_file)
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
