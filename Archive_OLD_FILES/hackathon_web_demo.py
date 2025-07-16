"""
IntelliPart Hackathon Live Web Demo
Interactive web presentation for judges and stakeholders
"""

from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
from advanced_analytics import AdvancedAnalytics

app = Flask(__name__)

# Initialize analytics engine
analytics_engine = AdvancedAnalytics("data/training Dataset.jsonl")

@app.route('/')
def hackathon_demo():
    """Main hackathon demo page."""
    return render_template('hackathon_demo.html')

@app.route('/api/demo/overview')
def demo_overview():
    """Get demo overview data - OPTIMIZED."""
    return jsonify({
        'team_name': 'IntelliPart Team',
        'challenge': 'AI-Powered Auto Parts Analytics',
        'total_parts': len(analytics_engine.parts),
        'technologies': ['AI/ML', 'Predictive Analytics', 'Flask', 'SQLite', 'Advanced Search'],
        'key_features': [
            '4 Advanced Search Algorithms',
            'Predictive Demand Analytics',
            'Supply Chain Risk Assessment',
            'Cost Optimization Engine',
            'Quality Prediction System',
            'Real-time Business Intelligence'
        ]
    })

@app.route('/api/demo/quick-dashboard')
def demo_quick_dashboard():
    """Get instant dashboard data for immediate display."""
    dashboard_data = analytics_engine.get_instant_dashboard_data()
    return jsonify(dashboard_data)

@app.route('/api/demo/demand-prediction')
def demo_demand_prediction():
    """Get demand prediction analytics - OPTIMIZED."""
    demand_data = analytics_engine.predictive_demand_analysis()
    
    return jsonify({
        'high_demand_systems': len(demand_data['high_demand_systems']),
        'restock_alerts': len(demand_data['restock_alerts']),
        'top_systems': demand_data['system_analysis'][:5],
        'generated_at': demand_data['generated_at']
    })

@app.route('/api/demo/supply-chain')
def demo_supply_chain():
    """Get supply chain risk analysis."""
    supply_data = analytics_engine.supply_chain_optimization()
    
    return jsonify({
        'high_risk_suppliers': len(supply_data['high_risk_suppliers']),
        'total_suppliers': len(supply_data['supplier_analysis']),
        'risk_suppliers': supply_data['high_risk_suppliers'][:5],
        'recommendations': supply_data['recommendations']
    })

@app.route('/api/demo/cost-optimization')
def demo_cost_optimization():
    """Get cost optimization data."""
    cost_data = analytics_engine.cost_optimization_analysis()
    
    return jsonify({
        'potential_savings': cost_data['potential_annual_savings'],
        'optimization_opportunities': len(cost_data['cost_optimization_opportunities']),
        'top_opportunities': cost_data['cost_optimization_opportunities'][:5],
        'system_costs': cost_data['system_cost_analysis'][:5]
    })

@app.route('/api/demo/quality-analysis')
def demo_quality_analysis():
    """Get quality prediction data."""
    quality_data = analytics_engine.quality_prediction_analysis()
    
    return jsonify({
        'warranty_categories': len(quality_data['warranty_analysis']),
        'production_years': len(quality_data['production_trends']),
        'warranty_analysis': quality_data['warranty_analysis'][:5],
        'production_trends': quality_data['production_trends'][:5],
        'recommendations': quality_data['quality_recommendations']
    })

@app.route('/api/demo/executive-summary')
def demo_executive_summary():
    """Get executive summary."""
    report = analytics_engine.generate_comprehensive_report()
    summary = report['executive_summary']
    
    return jsonify({
        'risk_assessment': summary['risk_assessment'],
        'key_findings': summary['key_findings'],
        'urgent_actions': summary['urgent_actions'],
        'cost_impact': summary['cost_impact'],
        'total_parts': len(analytics_engine.parts),
        'business_value': {
            'annual_savings': summary['cost_impact'].get('potential_savings', 0),
            'roi_percentage': ((summary['cost_impact'].get('potential_savings', 0) - 50000) / 50000) * 100 if summary['cost_impact'].get('potential_savings', 0) > 0 else 0,
            'payback_months': (50000 / summary['cost_impact'].get('potential_savings', 1)) * 12 if summary['cost_impact'].get('potential_savings', 0) > 0 else 0
        }
    })

@app.route('/api/demo/live-metrics')
def demo_live_metrics():
    """Get live metrics for real-time display."""
    import random
    
    # Simulate live metrics
    return jsonify({
        'searches_per_minute': random.randint(45, 65),
        'active_users': random.randint(12, 28),
        'cost_savings_today': random.randint(1500, 3200),
        'alerts_generated': random.randint(3, 8),
        'system_uptime': '99.97%',
        'response_time': f"{random.randint(120, 180)}ms"
    })

if __name__ == '__main__':
    print("🚀 Starting IntelliPart Hackathon Live Demo")
    print("🌐 Access the demo at: http://localhost:5003")
    print("🎯 Perfect for presenting to judges and stakeholders!")
    app.run(debug=True, port=5003, host='0.0.0.0')
