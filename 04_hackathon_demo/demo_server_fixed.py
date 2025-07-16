#!/usr/bin/env python3
"""
IntelliPart Enhanced Demo Server
Advanced AI-powered automotive parts management platform demo
Supports the enhanced_demo.html interface with live data endpoints
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
import socket

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

def find_available_port():
    """Find an available port starting from 5000"""
    ports_to_try = [5000, 5001, 5002, 5003, 8000, 8080]
    
    for port in ports_to_try:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result != 0:  # Port is free
                return port
        except Exception:
            continue
    
    return 5000  # Default fallback

def update_live_metrics():
    """Update metrics in real-time"""
    while True:
        demo_state['searches_per_hour'] = random.randint(2500, 3200)
        demo_state['active_users'] = random.randint(120, 180)
        demo_state['response_time'] = random.randint(70, 120)
        demo_state['annual_savings'] = round(random.uniform(4.2, 5.1), 1)
        demo_state['system_uptime'] = round(random.uniform(99.5, 99.9), 1)
        demo_state['parts_analyzed'] = random.randint(47000, 48000)
        demo_state['last_update'] = time.time()
        time.sleep(3)  # Update every 3 seconds

# Start background metrics updater
threading.Thread(target=update_live_metrics, daemon=True).start()

@app.route('/')
def index():
    """Serve the main demo page"""
    try:
        with open('enhanced_demo.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({
            'error': 'Demo file not found',
            'message': 'Please ensure enhanced_demo.html is in the same directory',
            'endpoints': {
                'live_metrics': '/api/demo/live-metrics',
                'predictive_analytics': '/api/demo/predictive-analytics', 
                'supply_chain': '/api/demo/supply-chain',
                'cost_optimization': '/api/demo/cost-optimization',
                'executive_summary': '/api/demo/executive-summary',
                'system_health': '/api/demo/system-health'
            }
        }), 404

@app.route('/api/demo/live-metrics')
def live_metrics():
    """Real-time system metrics"""
    return jsonify({
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'metrics': demo_state
    })

@app.route('/api/demo/predictive-analytics')
def predictive_analytics():
    """AI Predictive Analytics data"""
    return jsonify({
        'status': 'success',
        'analysis': {
            'prediction_accuracy': '94.7%',
            'critical_parts': 12,
            'stockout_predictions': 8,
            'cost_impact': '₹1.2M',
            'high_priority_systems': [
                'Brake Systems - 5 days remaining',
                'Air Filters - 7 days remaining', 
                'Oil Filters - 12 days remaining'
            ],
            'seasonal_trends': {
                'brake_components': '+23%',
                'engine_parts': '+15%',
                'electrical_components': '+8%'
            },
            'recommendations': [
                'Implement automated reorder for 15 high-velocity parts',
                'Increase safety stock for seasonal components by 25%',
                'Schedule supplier performance review'
            ]
        }
    })

@app.route('/api/demo/supply-chain')
def supply_chain():
    """Supply Chain Intelligence data"""
    return jsonify({
        'status': 'success',
        'supply_chain': {
            'risk_level': 'HIGH',
            'high_risk_suppliers': 7,
            'dependency_concentration': '60%',
            'geographic_risk': '85%',
            'financial_risk_suppliers': 3,
            'supplier_breakdown': [
                {'name': 'Mahindra Auto Parts Ltd', 'dependency': '28%', 'risk': 'HIGH'},
                {'name': 'Bosch India', 'dependency': '22%', 'risk': 'MEDIUM'},
                {'name': 'Tata AutoComp', 'dependency': '18%', 'risk': 'MEDIUM'}
            ],
            'mitigation_value': '₹8.2M',
            'recommendations': [
                'Identify 15 alternative suppliers for critical components',
                'Implement multi-sourcing strategy to reduce dependency by 40%',
                'Create supplier diversification plan across 3 regions'
            ]
        }
    })

@app.route('/api/demo/cost-optimization')
def cost_optimization():
    """Cost Optimization data"""
    return jsonify({
        'status': 'success',
        'optimization': {
            'total_savings': '₹4.7M',
            'roi': '420%',
            'payback_period': '2.1 months',
            'savings_breakdown': {
                'bulk_purchase': {'amount': '₹1.8M', 'percentage': '38%'},
                'supplier_negotiation': {'amount': '₹1.2M', 'percentage': '26%'},
                'alternative_parts': {'amount': '₹0.9M', 'percentage': '19%'},
                'inventory_optimization': {'amount': '₹0.8M', 'percentage': '17%'}
            },
            'immediate_opportunities': [
                'Negotiate volume discounts with top 5 suppliers - ₹1.2M',
                'Consolidate brake component orders - ₹450K',
                'Switch to alternative oil filter brands - ₹280K'
            ],
            'strategic_actions': [
                'Implement dynamic pricing monitoring',
                'Establish strategic partnerships for high-volume components',
                'Deploy automated procurement for standardized parts'
            ]
        }
    })

@app.route('/api/demo/executive-summary')
def executive_summary():
    """Executive Dashboard data"""
    return jsonify({
        'status': 'success',
        'executive_summary': {
            'roi_achievement': '420%',
            'annual_savings': '₹4.7M',
            'payback_months': '2.1',
            'strategic_achievements': [
                'Reduced procurement costs by 23% through AI optimization',
                'Eliminated 89% of stockout incidents with predictive analytics',
                'Improved supplier performance by 34% through intelligent monitoring',
                'Decreased search time by 76% with multi-algorithm approach'
            ],
            'kpis': {
                'inventory_turnover': {'from': '6.2x', 'to': '8.9x', 'improvement': '+44%'},
                'supplier_reliability': '96.8%',
                'cost_variance': {'from': '15%', 'to': '4%', 'improvement': '+73%'},
                'system_uptime': '99.8%'
            },
            'strategic_recommendations': [
                'Scale IntelliPart deployment to all business units (ROI: 500%+)',
                'Integrate with existing ERP systems for unified operations',
                'Establish AI-driven procurement center of excellence',
                'Implement predictive maintenance using parts analytics'
            ]
        }
    })

@app.route('/api/demo/system-health')
def system_health():
    """System Health data"""
    return jsonify({
        'status': 'success',
        'system_health': {
            'overall_status': 'HEALTHY',
            'uptime': '99.97%',
            'components': {
                'ai_search_engine': {'status': 'HEALTHY', 'response_time': '89ms'},
                'predictive_analytics': {'status': 'HEALTHY', 'processing': 'real-time'},
                'cost_optimization': {'status': 'HEALTHY', 'monitoring': 'continuous'},
                'supply_chain_monitor': {'status': 'HEALTHY', 'uptime': '99.8%'}
            },
            'performance_metrics': {
                'memory_usage': '68%',
                'cpu_utilization': '42%', 
                'database_performance': '156 queries/second',
                'network_latency': '23ms'
            },
            'demo_readiness': {
                'algorithms_loaded': True,
                'data_feeds_active': True,
                'scenarios_preloaded': True,
                'backup_systems_ready': True,
                'performance_monitoring': True,
                'security_protocols': True
            }
        }
    })

if __name__ == '__main__':
    server_port = find_available_port()
    
    print("🚀 IntelliPart Enhanced Demo Server Starting...")
    print("=" * 60)
    print(f"🌐 Demo URL: http://localhost:{server_port}")
    print("📊 API Endpoints:")
    print(f"   • Live Metrics: http://localhost:{server_port}/api/demo/live-metrics")
    print(f"   • Predictive Analytics: http://localhost:{server_port}/api/demo/predictive-analytics")
    print(f"   • Supply Chain: http://localhost:{server_port}/api/demo/supply-chain")
    print(f"   • Cost Optimization: http://localhost:{server_port}/api/demo/cost-optimization")
    print(f"   • Executive Summary: http://localhost:{server_port}/api/demo/executive-summary")
    print(f"   • System Health: http://localhost:{server_port}/api/demo/system-health")
    print("=" * 60)
    print("🎯 Ready for live demonstration!")
    print(f"🚀 Server starting on port {server_port}...")
    
    try:
        app.run(host='0.0.0.0', port=server_port, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try running: python demo_server.py directly")
        print("💡 Or check if another application is using the port")
