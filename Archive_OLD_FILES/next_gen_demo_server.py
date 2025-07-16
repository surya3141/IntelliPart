#!/usr/bin/env python3
"""
IntelliPart Next-Generation Demo Server
Advanced AI-powered automotive parts management platform demo
Supports the next_gen_demo.html interface with live data endpoints
"""

from flask import Flask, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import json
import random
import time
import threading
from datetime import datetime, timedelta
import os
import sqlite3

app = Flask(__name__)
CORS(app)

# Global demo state
demo_state = {
    'searches_per_hour': 2847,
    'active_users': 156,
    'response_time': 89,
    'annual_savings': 4.7,
    'system_uptime': 99.8,
    'parts_analyzed': 47523,
    'last_update': time.time()
}

class IntelliPartDemo:
    def __init__(self):
        self.parts_data = self.generate_sample_data()
        self.suppliers = self.generate_supplier_data()
        
    def generate_sample_data(self):
        """Generate realistic automotive parts data"""
        systems = [
            "Engine", "Transmission", "Braking", "Suspension", "Electrical",
            "Cooling", "Exhaust", "Fuel", "Steering", "Lighting", "Air Conditioning",
            "Safety", "Interior", "Exterior", "Drivetrain"
        ]
        
        manufacturers = [
            "Bosch", "Mahindra Auto Parts", "Tata AutoComp", "Bajaj Auto",
            "TVS Motor", "Hero MotoCorp", "Ashok Leyland", "Maruti Suzuki",
            "Hyundai Motor", "Toyota Kirloskar", "Ford India", "Honda Cars"
        ]
        
        parts = []
        for i in range(500):
            part = {
                'id': f'MP{1000 + i}',
                'name': f'{random.choice(systems)} Component {i+1}',
                'system': random.choice(systems),
                'manufacturer': random.choice(manufacturers),
                'price': round(random.uniform(50, 5000), 2),
                'stock': random.randint(0, 100),
                'warranty_months': random.choice([6, 12, 18, 24, 36]),
                'demand_score': round(random.uniform(1, 7), 1),
                'quality_rating': round(random.uniform(3.5, 5.0), 1),
                'last_ordered': datetime.now() - timedelta(days=random.randint(1, 365))
            }
            parts.append(part)
        
        return parts
    
    def generate_supplier_data(self):
        """Generate supplier risk analysis data"""
        suppliers = [
            {
                'name': 'Mahindra Auto Parts Ltd',
                'parts_count': 145,
                'dependency_percentage': 28,
                'risk_level': 'HIGH',
                'credit_rating': 'B+',
                'geographic_region': 'Western India',
                'systems_covered': ['Engine', 'Transmission', 'Braking'],
                'annual_value': 2.1e6
            },
            {
                'name': 'Bosch India Limited', 
                'parts_count': 118,
                'dependency_percentage': 22,
                'risk_level': 'MEDIUM',
                'credit_rating': 'A-',
                'geographic_region': 'Southern India',
                'systems_covered': ['Electrical', 'Fuel', 'Safety'],
                'annual_value': 1.8e6
            },
            {
                'name': 'Tata AutoComp Systems',
                'parts_count': 94,
                'dependency_percentage': 18,
                'risk_level': 'MEDIUM', 
                'credit_rating': 'A',
                'geographic_region': 'Western India',
                'systems_covered': ['Interior', 'Exterior', 'Lighting'],
                'annual_value': 1.4e6
            }
        ]
        return suppliers

demo = IntelliPartDemo()

def update_live_metrics():
    """Update live metrics with realistic variations"""
    while True:
        global demo_state
        
        # Simulate realistic metric changes
        demo_state['searches_per_hour'] += random.randint(-50, 100)
        demo_state['active_users'] += random.randint(-10, 20)
        demo_state['response_time'] = max(60, demo_state['response_time'] + random.randint(-20, 30))
        demo_state['annual_savings'] += random.uniform(-0.1, 0.2)
        demo_state['system_uptime'] = min(100, max(99.0, demo_state['system_uptime'] + random.uniform(-0.1, 0.1)))
        demo_state['parts_analyzed'] += random.randint(0, 50)
        demo_state['last_update'] = time.time()
        
        # Keep values in realistic ranges
        demo_state['searches_per_hour'] = max(2000, min(4000, demo_state['searches_per_hour']))
        demo_state['active_users'] = max(100, min(300, demo_state['active_users']))
        demo_state['annual_savings'] = max(3.0, min(6.0, demo_state['annual_savings']))
        
        time.sleep(3)  # Update every 3 seconds

# Start background metrics update
threading.Thread(target=update_live_metrics, daemon=True).start()

@app.route('/')
def index():
    """Serve the main demo page"""
    try:
        with open('next_gen_demo.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({
            'error': 'Demo file not found',
            'message': 'Please ensure next_gen_demo.html is in the same directory',
            'endpoints': {
                'live_metrics': '/api/demo/live-metrics',
                'predictive_analytics': '/api/demo/predictive-analytics', 
                'supply_chain': '/api/demo/supply-chain',
                'cost_optimization': '/api/demo/cost-optimization',
                'executive_summary': '/api/demo/executive-summary'
            }
        })

@app.route('/api/demo/live-metrics')
def live_metrics():
    """Provide real-time metrics for the demo dashboard"""
    return jsonify({
        'searches_per_hour': f"{demo_state['searches_per_hour']:,}",
        'active_users': demo_state['active_users'],
        'response_time': f"{demo_state['response_time']}ms",
        'annual_savings': f"₹{demo_state['annual_savings']:.1f}M",
        'system_uptime': f"{demo_state['system_uptime']:.1f}%",
        'parts_analyzed': f"{demo_state['parts_analyzed']:,}",
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/demo/predictive-analytics')
def predictive_analytics():
    """Generate predictive analytics demo data"""
    high_demand_systems = random.randint(10, 15)
    restock_alerts = random.randint(6, 12)
    
    top_systems = []
    systems = ["Engine", "Braking", "Transmission", "Electrical", "Suspension"]
    
    for system in systems[:4]:
        parts = [p for p in demo.parts_data if p['system'] == system]
        if parts:
            avg_stock = sum(p['stock'] for p in parts) / len(parts)
            avg_cost = sum(p['price'] for p in parts) / len(parts)
            demand_score = random.uniform(2, 6)
            
            recommendation = "Monitor closely"
            if demand_score >= 5:
                recommendation = "Immediate restock required"
            elif demand_score >= 3.5:
                recommendation = "Schedule reorder within 7 days"
            
            top_systems.append({
                'system': system,
                'part_count': len(parts),
                'avg_stock': round(avg_stock, 1),
                'avg_cost': round(avg_cost, 2),
                'demand_score': round(demand_score, 1),
                'recommendation': recommendation
            })
    
    return jsonify({
        'high_demand_systems': high_demand_systems,
        'restock_alerts': restock_alerts,
        'prediction_accuracy': 94.7,
        'top_systems': top_systems,
        'insights': [
            'Brake components showing 23% seasonal demand increase',
            'Oil filter demand predicted to spike in 7 days',
            'Engine parts inventory optimization can save ₹1.2M annually'
        ]
    })

@app.route('/api/demo/supply-chain')
def supply_chain_analysis():
    """Generate supply chain risk analysis"""
    high_risk_count = len([s for s in demo.suppliers if s['risk_level'] == 'HIGH'])
    total_suppliers = len(demo.suppliers) + random.randint(5, 15)
    
    risk_suppliers = [
        {
            'manufacturer': s['name'],
            'part_count': s['parts_count'],
            'dependency_percentage': s['dependency_percentage'],
            'risk_level': s['risk_level'],
            'systems_covered': ', '.join(s['systems_covered'][:2])
        }
        for s in demo.suppliers if s['risk_level'] in ['HIGH', 'MEDIUM']
    ]
    
    recommendations = [
        'Diversify supplier base for brake components across 3 regions',
        'Establish backup suppliers for high-dependency manufacturers',
        'Implement supplier financial health monitoring system',
        'Create strategic partnerships with alternative suppliers',
        'Reduce single-source dependencies by 40% within 6 months'
    ]
    
    return jsonify({
        'high_risk_suppliers': high_risk_count,
        'total_suppliers': total_suppliers,
        'risk_suppliers': risk_suppliers[:3],
        'recommendations': random.sample(recommendations, 4),
        'geographic_concentration': 85,
        'financial_risk_suppliers': 3
    })

@app.route('/api/demo/cost-optimization')
def cost_optimization():
    """Generate cost optimization analysis"""
    potential_savings = random.uniform(4200000, 5200000)
    
    opportunities = []
    systems = ["Engine", "Braking", "Transmission", "Electrical"]
    manufacturers = ["Bosch", "Mahindra Auto Parts", "Tata AutoComp", "TVS Motor"]
    
    for i in range(4):
        system = random.choice(systems)
        manufacturer = random.choice(manufacturers)
        price_variance = random.uniform(150, 800)
        savings_potential = random.uniform(280000, 450000)
        
        opportunities.append({
            'system': system,
            'manufacturer': manufacturer,
            'price_variance': price_variance,
            'savings_potential': savings_potential,
            'optimization_opportunity': random.choice(['HIGH', 'MEDIUM', 'HIGH'])
        })
    
    return jsonify({
        'potential_savings': potential_savings,
        'optimization_opportunities': len(opportunities) + random.randint(8, 15),
        'top_opportunities': opportunities,
        'roi_percentage': 420,
        'payback_months': 2.1,
        'savings_breakdown': {
            'bulk_purchase': 1800000,
            'supplier_negotiation': 1200000,
            'alternative_parts': 900000,
            'inventory_optimization': 800000
        }
    })

@app.route('/api/demo/executive-summary')
def executive_summary():
    """Generate executive dashboard data"""
    return jsonify({
        'total_parts': 47523,
        'risk_assessment': 'Medium risk with high opportunity for optimization',
        'business_value': {
            'annual_savings': 4700000,
            'roi_percentage': 420,
            'payback_months': 2.1
        },
        'key_findings': [
            '₹4.7M in cost optimization opportunities identified',
            '7 high-risk suppliers require immediate diversification',
            '94.7% prediction accuracy achieved by AI algorithms',
            'Supply chain dependency reduced by 60% potential',
            'Inventory turnover improved from 6.2x to 8.9x annually'
        ],
        'urgent_actions': [
            'Implement automated reordering for 15 critical components',
            'Diversify brake component suppliers within 30 days',
            'Negotiate volume discounts with top 5 suppliers',
            'Deploy predictive maintenance using parts analytics'
        ],
        'performance_metrics': {
            'search_response_time': 87,
            'system_uptime': 99.8,
            'prediction_accuracy': 94.7,
            'cost_reduction': 23
        }
    })

@app.route('/api/demo/system-health')
def system_health():
    """System health monitoring"""
    return jsonify({
        'status': 'HEALTHY',
        'components': {
            'search_engine': {'status': 'HEALTHY', 'response_time': 89, 'uptime': 99.9},
            'ai_analytics': {'status': 'HEALTHY', 'processing': 'real-time', 'accuracy': 94.7},
            'database': {'status': 'HEALTHY', 'queries_per_second': 156, 'uptime': 99.8},
            'api_gateway': {'status': 'HEALTHY', 'requests_per_minute': 847, 'latency': 23}
        },
        'performance': {
            'memory_usage': 68,
            'cpu_utilization': 42,
            'disk_io': 'normal',
            'network_latency': 23
        },
        'demo_readiness': {
            'algorithms_loaded': True,
            'data_feeds_active': True,
            'scenarios_ready': True,
            'backup_systems': True
        }
    })

@app.route('/api/demo/ai-assistant')
def ai_assistant():
    """AI Assistant responses"""
    responses = {
        'capabilities': [
            'Multi-algorithm search with 96.8% relevance',
            'Predictive analytics with 94.7% accuracy', 
            'Real-time supply chain risk assessment',
            'Cost optimization discovering ₹4.7M+ savings',
            'Natural language processing for intuitive queries'
        ],
        'quick_commands': [
            'Show me cost savings opportunities',
            'Analyze supply chain risks',
            'Predict demand for brake components',
            'Find alternative suppliers',
            'Generate executive summary report'
        ],
        'status': 'Ready to assist with IntelliPart demonstration'
    }
    return jsonify(responses)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'demo_ready': True
    })

if __name__ == '__main__':
    print("🚀 IntelliPart Next-Gen Demo Server Starting...")
    print("=" * 60)
    print("📊 Demo Dashboard: http://localhost:5000")
    print("🔗 API Endpoints:")
    print("   • Live Metrics: http://localhost:5000/api/demo/live-metrics")
    print("   • Predictive Analytics: http://localhost:5000/api/demo/predictive-analytics")
    print("   • Supply Chain: http://localhost:5000/api/demo/supply-chain")
    print("   • Cost Optimization: http://localhost:5000/api/demo/cost-optimization")
    print("   • Executive Summary: http://localhost:5000/api/demo/executive-summary")
    print("   • System Health: http://localhost:5000/api/demo/system-health")
    print("=" * 60)
    print("🎯 Ready for live demonstration!")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
