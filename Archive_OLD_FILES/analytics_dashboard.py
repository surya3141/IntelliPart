"""
IntelliPart Analytics Dashboard
Provides advanced analytics and insights for the parts database
"""

import json
from collections import defaultdict, Counter
from typing import Dict, List, Any
import re
import os
from datetime import datetime

# Optional imports - will work without pandas/matplotlib
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class PartsAnalytics:
    def __init__(self, jsonl_path: str):
        """Initialize analytics engine."""
        self.parts = []
        self.df = None
        self.load_data(jsonl_path)
        self.prepare_data()
        print(f"Analytics ready for {len(self.parts)} parts")
    
    def load_data(self, jsonl_path: str):
        """Load parts data."""
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.parts.append(json.loads(line))
    
    def prepare_data(self):
        """Prepare data for analysis."""
        # Use pandas if available, otherwise work with raw data
        if HAS_PANDAS:
            self.df = pd.DataFrame(self.parts)
            
            # Clean cost data
            if 'cost' in self.df.columns:
                self.df['cost_numeric'] = self.df['cost'].apply(self._extract_numeric_cost)
            
            # Clean stock data
            if 'stock' in self.df.columns:
                self.df['stock_numeric'] = pd.to_numeric(self.df['stock'], errors='coerce').fillna(0)
            
            # Clean weight data
            if 'weight' in self.df.columns:
                self.df['weight_numeric'] = self.df['weight'].apply(self._extract_numeric_weight)
        else:
            # Prepare data without pandas
            for part in self.parts:
                part['cost_numeric'] = self._extract_numeric_cost(part.get('cost', '0'))
                part['stock_numeric'] = self._extract_numeric_stock(part.get('stock', '0'))
                part['weight_numeric'] = self._extract_numeric_weight(part.get('weight', '0'))
    
    def _extract_numeric_cost(self, cost_str):
        """Extract numeric cost from string."""
        try:
            if pd.isna(cost_str):
                return 0
            # Remove currency symbols and extract number
            numeric = re.sub(r'[^\d.]', '', str(cost_str))
            return float(numeric) if numeric else 0
        except:
            return 0
    
    def _extract_numeric_stock(self, stock_str):
        """Extract numeric stock from string."""
        try:
            if stock_str in [None, '', 'N/A']:
                return 0
            return int(float(str(stock_str)))
        except:
            return 0
    
    def _extract_numeric_weight(self, weight_str):
        """Extract numeric weight from string."""
        try:
            if weight_str in [None, '', 'N/A']:
                return 0
            # Extract number from weight string
            numeric = re.findall(r'\d+\.?\d*', str(weight_str))
            return float(numeric[0]) if numeric else 0
        except:
            return 0
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report."""
        report = {
            'overview': self._overview_stats(),
            'cost_analysis': self._cost_analysis(),
            'inventory_analysis': self._inventory_analysis(),
            'manufacturer_analysis': self._manufacturer_analysis(),
            'system_analysis': self._system_analysis(),
            'quality_analysis': self._data_quality_analysis(),
            'insights': self._generate_insights()
        }
        return report
    
    def _overview_stats(self) -> Dict[str, Any]:
        """Basic overview statistics."""
        if HAS_PANDAS and self.df is not None:
            return {
                'total_parts': len(self.parts),
                'unique_manufacturers': self.df['manufacturer'].nunique() if 'manufacturer' in self.df.columns else 0,
                'unique_systems': self.df['system'].nunique() if 'system' in self.df.columns else 0,
                'unique_part_types': self.df['part_type'].nunique() if 'part_type' in self.df.columns else 0,
                'avg_cost': round(self.df['cost_numeric'].mean(), 2) if 'cost_numeric' in self.df.columns else 0,
                'total_inventory_value': round(self.df['cost_numeric'].sum(), 2) if 'cost_numeric' in self.df.columns else 0,
                'total_stock_units': int(self.df['stock_numeric'].sum()) if 'stock_numeric' in self.df.columns else 0
            }
        else:
            # Manual calculation without pandas
            manufacturers = set()
            systems = set()
            part_types = set()
            costs = []
            stocks = []
            
            for part in self.parts:
                if part.get('manufacturer'):
                    manufacturers.add(part['manufacturer'])
                if part.get('system'):
                    systems.add(part['system'])
                if part.get('part_type'):
                    part_types.add(part['part_type'])
                
                costs.append(part.get('cost_numeric', 0))
                stocks.append(part.get('stock_numeric', 0))
            
            return {
                'total_parts': len(self.parts),
                'unique_manufacturers': len(manufacturers),
                'unique_systems': len(systems),
                'unique_part_types': len(part_types),
                'avg_cost': round(sum(costs) / len(costs), 2) if costs else 0,
                'total_inventory_value': round(sum(costs), 2),
                'total_stock_units': int(sum(stocks))
            }
    
    def _cost_analysis(self) -> Dict[str, Any]:
        """Analyze cost distribution and patterns."""
        if HAS_PANDAS and self.df is not None and 'cost_numeric' in self.df.columns:
            cost_data = self.df['cost_numeric']
            cost_data = cost_data[cost_data > 0]  # Remove zero costs
            
            return {
                'cost_stats': {
                    'min': round(cost_data.min(), 2),
                    'max': round(cost_data.max(), 2),
                    'mean': round(cost_data.mean(), 2),
                    'median': round(cost_data.median(), 2),
                    'std': round(cost_data.std(), 2)
                },
                'cost_ranges': {
                    'budget': len(cost_data[cost_data <= 100]),
                    'mid_range': len(cost_data[(cost_data > 100) & (cost_data <= 500)]),
                    'premium': len(cost_data[cost_data > 500])
                },
                'most_expensive_parts': self._get_top_parts_by_cost(5),
                'cheapest_parts': self._get_bottom_parts_by_cost(5)
            }
        else:
            # Manual calculation without pandas
            costs = [part.get('cost_numeric', 0) for part in self.parts if part.get('cost_numeric', 0) > 0]
            
            if not costs:
                return {'error': 'Cost data not available'}
            
            costs.sort()
            n = len(costs)
            
            return {
                'cost_stats': {
                    'min': round(min(costs), 2),
                    'max': round(max(costs), 2),
                    'mean': round(sum(costs) / n, 2),
                    'median': round(costs[n // 2], 2),
                    'std': round(self._calculate_std(costs), 2)
                },
                'cost_ranges': {
                    'budget': len([c for c in costs if c <= 100]),
                    'mid_range': len([c for c in costs if 100 < c <= 500]),
                    'premium': len([c for c in costs if c > 500])
                },
                'most_expensive_parts': self._get_top_parts_by_cost(5),
                'cheapest_parts': self._get_bottom_parts_by_cost(5)
            }
    
    def _inventory_analysis(self) -> Dict[str, Any]:
        """Analyze inventory levels and stock patterns."""
        if HAS_PANDAS and self.df is not None and 'stock_numeric' in self.df.columns:
            stock_data = self.df['stock_numeric']
            
            return {
                'stock_stats': {
                    'total_units': int(stock_data.sum()),
                    'avg_stock': round(stock_data.mean(), 2),
                    'median_stock': round(stock_data.median(), 2),
                    'parts_out_of_stock': len(stock_data[stock_data == 0]),
                    'parts_low_stock': len(stock_data[(stock_data > 0) & (stock_data < 10)]),
                    'parts_high_stock': len(stock_data[stock_data >= 100])
                },
                'low_stock_alerts': self._get_low_stock_parts(),
                'overstocked_parts': self._get_overstocked_parts()
            }
        else:
            # Manual calculation without pandas
            stocks = [part.get('stock_numeric', 0) for part in self.parts]
            
            return {
                'stock_stats': {
                    'total_units': int(sum(stocks)),
                    'avg_stock': round(sum(stocks) / len(stocks), 2) if stocks else 0,
                    'median_stock': round(sorted(stocks)[len(stocks) // 2], 2) if stocks else 0,
                    'parts_out_of_stock': len([s for s in stocks if s == 0]),
                    'parts_low_stock': len([s for s in stocks if 0 < s < 10]),
                    'parts_high_stock': len([s for s in stocks if s >= 100])
                },
                'low_stock_alerts': self._get_low_stock_parts(),
                'overstocked_parts': self._get_overstocked_parts()
            }
    
    def _manufacturer_analysis(self) -> Dict[str, Any]:
        """Analyze manufacturer distribution and performance."""
        if HAS_PANDAS and self.df is not None and 'manufacturer' in self.df.columns:
            mfg_counts = self.df['manufacturer'].value_counts()
            
            # Calculate average cost per manufacturer
            mfg_cost_avg = self.df.groupby('manufacturer')['cost_numeric'].mean().round(2) if 'cost_numeric' in self.df.columns else {}
            
            return {
                'top_manufacturers': mfg_counts.head(10).to_dict(),
                'manufacturer_diversity': len(mfg_counts),
                'avg_cost_by_manufacturer': mfg_cost_avg.head(10).to_dict() if isinstance(mfg_cost_avg, pd.Series) else {},
                'single_part_manufacturers': len(mfg_counts[mfg_counts == 1])
            }
        else:
            # Manual calculation without pandas
            from collections import Counter
            manufacturers = [part.get('manufacturer', '') for part in self.parts if part.get('manufacturer')]
            mfg_counts = Counter(manufacturers)
            
            # Calculate average cost per manufacturer
            mfg_costs = defaultdict(list)
            for part in self.parts:
                mfg = part.get('manufacturer')
                cost = part.get('cost_numeric', 0)
                if mfg and cost > 0:
                    mfg_costs[mfg].append(cost)
            
            mfg_cost_avg = {mfg: round(sum(costs) / len(costs), 2) 
                           for mfg, costs in mfg_costs.items()}
            
            return {
                'top_manufacturers': dict(mfg_counts.most_common(10)),
                'manufacturer_diversity': len(mfg_counts),
                'avg_cost_by_manufacturer': dict(list(mfg_cost_avg.items())[:10]),
                'single_part_manufacturers': len([mfg for mfg, count in mfg_counts.items() if count == 1])
            }
    
    def _system_analysis(self) -> Dict[str, Any]:
        """Analyze parts by automotive systems."""
        if HAS_PANDAS and self.df is not None and 'system' in self.df.columns:
            system_counts = self.df['system'].value_counts()
            system_cost_avg = self.df.groupby('system')['cost_numeric'].mean().round(2) if 'cost_numeric' in self.df.columns else {}
            
            return {
                'parts_by_system': system_counts.to_dict(),
                'avg_cost_by_system': system_cost_avg.to_dict() if isinstance(system_cost_avg, pd.Series) else {},
                'most_expensive_system': system_cost_avg.idxmax() if isinstance(system_cost_avg, pd.Series) and not system_cost_avg.empty else None,
                'most_parts_system': system_counts.idxmax() if not system_counts.empty else None
            }
        else:
            # Manual calculation without pandas
            from collections import Counter
            systems = [part.get('system', '') for part in self.parts if part.get('system')]
            system_counts = Counter(systems)
            
            # Calculate average cost per system
            system_costs = defaultdict(list)
            for part in self.parts:
                system = part.get('system')
                cost = part.get('cost_numeric', 0)
                if system and cost > 0:
                    system_costs[system].append(cost)
            
            system_cost_avg = {system: round(sum(costs) / len(costs), 2) 
                              for system, costs in system_costs.items()}
            
            most_expensive_system = max(system_cost_avg.items(), key=lambda x: x[1])[0] if system_cost_avg else None
            most_parts_system = system_counts.most_common(1)[0][0] if system_counts else None
            
            return {
                'parts_by_system': dict(system_counts),
                'avg_cost_by_system': system_cost_avg,
                'most_expensive_system': most_expensive_system,
                'most_parts_system': most_parts_system
            }
    
    def _data_quality_analysis(self) -> Dict[str, Any]:
        """Analyze data quality and completeness."""
        quality_report = {}
        
        if HAS_PANDAS and self.df is not None:
            for column in self.df.columns:
                null_count = self.df[column].isnull().sum()
                empty_count = (self.df[column] == '').sum() if self.df[column].dtype == 'object' else 0
                completeness = round((len(self.df) - null_count - empty_count) / len(self.df) * 100, 2)
                
                quality_report[column] = {
                    'completeness_percentage': completeness,
                    'null_count': int(null_count),
                    'empty_count': int(empty_count)
                }
        else:
            # Manual calculation without pandas
            if not self.parts:
                return quality_report
            
            # Get all possible fields
            all_fields = set()
            for part in self.parts:
                all_fields.update(part.keys())
            
            for field in all_fields:
                null_count = 0
                empty_count = 0
                
                for part in self.parts:
                    value = part.get(field)
                    if value is None:
                        null_count += 1
                    elif value == '':
                        empty_count += 1
                
                completeness = round((len(self.parts) - null_count - empty_count) / len(self.parts) * 100, 2)
                
                quality_report[field] = {
                    'completeness_percentage': completeness,
                    'null_count': null_count,
                    'empty_count': empty_count
                }
        
        return quality_report
    
    def _generate_insights(self) -> List[str]:
        """Generate actionable insights from the data."""
        insights = []
        
        # Cost insights
        if HAS_PANDAS and self.df is not None and 'cost_numeric' in self.df.columns:
            avg_cost = self.df['cost_numeric'].mean()
            if avg_cost > 200:
                insights.append("Average part cost is high ($200+). Consider exploring budget alternatives.")
            
            expensive_count = len(self.df[self.df['cost_numeric'] > 500])
            if expensive_count > len(self.df) * 0.1:
                insights.append(f"{expensive_count} parts are premium-priced (>$500). Review pricing strategy.")
        else:
            # Manual calculation without pandas
            costs = [part.get('cost_numeric', 0) for part in self.parts if part.get('cost_numeric', 0) > 0]
            if costs:
                avg_cost = sum(costs) / len(costs)
                if avg_cost > 200:
                    insights.append("Average part cost is high ($200+). Consider exploring budget alternatives.")
                
                expensive_count = len([c for c in costs if c > 500])
                if expensive_count > len(costs) * 0.1:
                    insights.append(f"{expensive_count} parts are premium-priced (>$500). Review pricing strategy.")
        
        # Stock insights
        if HAS_PANDAS and self.df is not None and 'stock_numeric' in self.df.columns:
            out_of_stock = len(self.df[self.df['stock_numeric'] == 0])
            if out_of_stock > len(self.df) * 0.05:
                insights.append(f"{out_of_stock} parts are out of stock. Urgent restocking needed.")
            
            low_stock = len(self.df[(self.df['stock_numeric'] > 0) & (self.df['stock_numeric'] < 10)])
            if low_stock > len(self.df) * 0.1:
                insights.append(f"{low_stock} parts have low stock (<10 units). Monitor inventory levels.")
        else:
            # Manual calculation without pandas
            stocks = [part.get('stock_numeric', 0) for part in self.parts]
            out_of_stock = len([s for s in stocks if s == 0])
            if out_of_stock > len(stocks) * 0.05:
                insights.append(f"{out_of_stock} parts are out of stock. Urgent restocking needed.")
            
            low_stock = len([s for s in stocks if 0 < s < 10])
            if low_stock > len(stocks) * 0.1:
                insights.append(f"{low_stock} parts have low stock (<10 units). Monitor inventory levels.")
        
        # Manufacturer insights
        if HAS_PANDAS and self.df is not None and 'manufacturer' in self.df.columns:
            mfg_counts = self.df['manufacturer'].value_counts()
            if len(mfg_counts) > 50:
                insights.append("High manufacturer diversity. Consider vendor consolidation opportunities.")
            
            single_mfg = len(mfg_counts[mfg_counts == 1])
            if single_mfg > len(mfg_counts) * 0.3:
                insights.append(f"{single_mfg} manufacturers supply only one part. Evaluate supplier relationships.")
        else:
            # Manual calculation without pandas
            from collections import Counter
            manufacturers = [part.get('manufacturer', '') for part in self.parts if part.get('manufacturer')]
            mfg_counts = Counter(manufacturers)
            if len(mfg_counts) > 50:
                insights.append("High manufacturer diversity. Consider vendor consolidation opportunities.")
            
            single_mfg = len([mfg for mfg, count in mfg_counts.items() if count == 1])
            if single_mfg > len(mfg_counts) * 0.3:
                insights.append(f"{single_mfg} manufacturers supply only one part. Evaluate supplier relationships.")
        
        # System insights
        if HAS_PANDAS and self.df is not None and 'system' in self.df.columns:
            system_counts = self.df['system'].value_counts()
            top_system = system_counts.idxmax()
            top_count = system_counts.max()
            if top_count > len(self.df) * 0.3:
                insights.append(f"'{top_system}' dominates inventory ({top_count} parts). Ensure balanced coverage.")
        else:
            # Manual calculation without pandas
            from collections import Counter
            systems = [part.get('system', '') for part in self.parts if part.get('system')]
            system_counts = Counter(systems)
            if system_counts:
                top_system, top_count = system_counts.most_common(1)[0]
                if top_count > len(self.parts) * 0.3:
                    insights.append(f"'{top_system}' dominates inventory ({top_count} parts). Ensure balanced coverage.")
        
        return insights
    
    def _get_top_parts_by_cost(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get most expensive parts."""
        if HAS_PANDAS and self.df is not None and 'cost_numeric' in self.df.columns:
            top_parts = self.df.nlargest(n, 'cost_numeric')
            return [
                {
                    'part_name': row.get('part_name', 'Unknown'),
                    'part_number': row.get('part_number', 'N/A'),
                    'cost': row.get('cost_numeric', 0),
                    'manufacturer': row.get('manufacturer', 'Unknown')
                }
                for _, row in top_parts.iterrows()
            ]
        else:
            # Manual calculation without pandas
            parts_with_cost = [(part, part.get('cost_numeric', 0)) for part in self.parts 
                              if part.get('cost_numeric', 0) > 0]
            parts_with_cost.sort(key=lambda x: x[1], reverse=True)
            
            return [
                {
                    'part_name': part.get('part_name', 'Unknown'),
                    'part_number': part.get('part_number', 'N/A'),
                    'cost': cost,
                    'manufacturer': part.get('manufacturer', 'Unknown')
                }
                for part, cost in parts_with_cost[:n]
            ]
    
    def _get_bottom_parts_by_cost(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get cheapest parts."""
        if HAS_PANDAS and self.df is not None and 'cost_numeric' in self.df.columns:
            # Only consider parts with cost > 0
            filtered_df = self.df[self.df['cost_numeric'] > 0]
            bottom_parts = filtered_df.nsmallest(n, 'cost_numeric')
            
            return [
                {
                    'part_name': row.get('part_name', 'Unknown'),
                    'part_number': row.get('part_number', 'N/A'),
                    'cost': row.get('cost_numeric', 0),
                    'manufacturer': row.get('manufacturer', 'Unknown')
                }
                for _, row in bottom_parts.iterrows()
            ]
        else:
            # Manual calculation without pandas
            parts_with_cost = [(part, part.get('cost_numeric', 0)) for part in self.parts 
                              if part.get('cost_numeric', 0) > 0]
            parts_with_cost.sort(key=lambda x: x[1])
            
            return [
                {
                    'part_name': part.get('part_name', 'Unknown'),
                    'part_number': part.get('part_number', 'N/A'),
                    'cost': cost,
                    'manufacturer': part.get('manufacturer', 'Unknown')
                }
                for part, cost in parts_with_cost[:n]
            ]
    
    def _get_low_stock_parts(self, threshold: int = 5) -> List[Dict[str, Any]]:
        """Get parts with low stock."""
        if HAS_PANDAS and self.df is not None and 'stock_numeric' in self.df.columns:
            low_stock = self.df[(self.df['stock_numeric'] > 0) & (self.df['stock_numeric'] <= threshold)]
            
            return [
                {
                    'part_name': row.get('part_name', 'Unknown'),
                    'part_number': row.get('part_number', 'N/A'),
                    'stock': int(row.get('stock_numeric', 0)),
                    'cost': row.get('cost_numeric', 0)
                }
                for _, row in low_stock.iterrows()
            ][:10]  # Limit to top 10
        else:
            # Manual calculation without pandas
            low_stock_parts = []
            for part in self.parts:
                stock = part.get('stock_numeric', 0)
                if 0 < stock <= threshold:
                    low_stock_parts.append({
                        'part_name': part.get('part_name', 'Unknown'),
                        'part_number': part.get('part_number', 'N/A'),
                        'stock': int(stock),
                        'cost': part.get('cost_numeric', 0)
                    })
            
            return low_stock_parts[:10]
    
    def _get_overstocked_parts(self, threshold: int = 100) -> List[Dict[str, Any]]:
        """Get potentially overstocked parts."""
        if HAS_PANDAS and self.df is not None and 'stock_numeric' in self.df.columns:
            overstocked = self.df[self.df['stock_numeric'] >= threshold]
            
            return [
                {
                    'part_name': row.get('part_name', 'Unknown'),
                    'part_number': row.get('part_number', 'N/A'),
                    'stock': int(row.get('stock_numeric', 0)),
                    'cost': row.get('cost_numeric', 0)
                }
                for _, row in overstocked.iterrows()
            ][:10]  # Limit to top 10
        else:
            # Manual calculation without pandas
            overstocked_parts = []
            for part in self.parts:
                stock = part.get('stock_numeric', 0)
                if stock >= threshold:
                    overstocked_parts.append({
                        'part_name': part.get('part_name', 'Unknown'),
                        'part_number': part.get('part_number', 'N/A'),
                        'stock': int(stock),
                        'cost': part.get('cost_numeric', 0)
                    })
            
            return overstocked_parts[:10]
    
    def export_report(self, filename: str = None) -> str:
        """Export analytics report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"parts_analytics_report_{timestamp}.json"
        
        report = self.generate_comprehensive_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Analytics report exported to: {filename}")
        return filename
    
    def print_summary_report(self):
        """Print a summary analytics report to console."""
        report = self.generate_comprehensive_report()
        
        print("\n" + "="*60)
        print("🔍 INTELLIPART ANALYTICS DASHBOARD")
        print("="*60)
        
        # Overview
        overview = report['overview']
        print(f"\n📊 OVERVIEW:")
        print(f"   Total Parts: {overview['total_parts']:,}")
        print(f"   Manufacturers: {overview['unique_manufacturers']}")
        print(f"   Systems: {overview['unique_systems']}")
        print(f"   Part Types: {overview['unique_part_types']}")
        print(f"   Average Cost: ${overview['avg_cost']:,.2f}")
        print(f"   Total Inventory Value: ${overview['total_inventory_value']:,.2f}")
        
        # Cost Analysis
        if 'cost_stats' in report['cost_analysis']:
            cost_stats = report['cost_analysis']['cost_stats']
            print(f"\n💰 COST ANALYSIS:")
            print(f"   Range: ${cost_stats['min']:,.2f} - ${cost_stats['max']:,.2f}")
            print(f"   Median: ${cost_stats['median']:,.2f}")
            print(f"   Standard Deviation: ${cost_stats['std']:,.2f}")
        
        # Inventory Analysis
        if 'stock_stats' in report['inventory_analysis']:
            stock_stats = report['inventory_analysis']['stock_stats']
            print(f"\n📦 INVENTORY ANALYSIS:")
            print(f"   Total Units: {stock_stats['total_units']:,}")
            print(f"   Out of Stock: {stock_stats['parts_out_of_stock']}")
            print(f"   Low Stock: {stock_stats['parts_low_stock']}")
            print(f"   High Stock: {stock_stats['parts_high_stock']}")
        
        # Top Manufacturers
        if 'top_manufacturers' in report['manufacturer_analysis']:
            top_mfg = report['manufacturer_analysis']['top_manufacturers']
            print(f"\n🏭 TOP MANUFACTURERS:")
            for mfg, count in list(top_mfg.items())[:5]:
                print(f"   {mfg}: {count} parts")
        
        # Systems
        if 'parts_by_system' in report['system_analysis']:
            systems = report['system_analysis']['parts_by_system']
            print(f"\n⚙️  PARTS BY SYSTEM:")
            for system, count in list(systems.items())[:5]:
                print(f"   {system}: {count} parts")
        
        # Insights
        insights = report['insights']
        if insights:
            print(f"\n💡 KEY INSIGHTS:")
            for i, insight in enumerate(insights, 1):
                print(f"   {i}. {insight}")
        
        print("\n" + "="*60)


    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation manually."""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

def interactive_analytics():
    """Interactive analytics interface."""
    print("Initializing IntelliPart Analytics Dashboard...")
    analytics = PartsAnalytics("data/training Dataset.jsonl")
    
    print("\n=== IntelliPart Analytics Dashboard ===")
    print("Commands:")
    print("  summary              - Show summary report")
    print("  report               - Show detailed report")
    print("  export [filename]    - Export report to file")
    print("  overview             - Basic statistics")
    print("  costs                - Cost analysis")
    print("  inventory            - Inventory analysis")
    print("  manufacturers        - Manufacturer analysis")
    print("  systems              - System analysis")
    print("  quality              - Data quality analysis")
    print("  insights             - Key insights")
    print("  exit                 - Quit")
    print("-" * 50)
    
    while True:
        user_input = input("\nanalytics> ").strip().lower()
        
        if user_input == "exit":
            break
        elif user_input == "summary":
            analytics.print_summary_report()
        elif user_input == "report":
            report = analytics.generate_comprehensive_report()
            print(json.dumps(report, indent=2))
        elif user_input.startswith("export"):
            parts = user_input.split()
            filename = parts[1] if len(parts) > 1 else None
            analytics.export_report(filename)
        elif user_input == "overview":
            report = analytics.generate_comprehensive_report()
            print(json.dumps(report['overview'], indent=2))
        elif user_input == "costs":
            report = analytics.generate_comprehensive_report()
            print(json.dumps(report['cost_analysis'], indent=2))
        elif user_input == "inventory":
            report = analytics.generate_comprehensive_report()
            print(json.dumps(report['inventory_analysis'], indent=2))
        elif user_input == "manufacturers":
            report = analytics.generate_comprehensive_report()
            print(json.dumps(report['manufacturer_analysis'], indent=2))
        elif user_input == "systems":
            report = analytics.generate_comprehensive_report()
            print(json.dumps(report['system_analysis'], indent=2))
        elif user_input == "quality":
            report = analytics.generate_comprehensive_report()
            print(json.dumps(report['quality_analysis'], indent=2))
        elif user_input == "insights":
            report = analytics.generate_comprehensive_report()
            for i, insight in enumerate(report['insights'], 1):
                print(f"{i}. {insight}")
        else:
            print("Unknown command. Type 'exit' to quit.")


if __name__ == "__main__":
    interactive_analytics()
