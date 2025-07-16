"""
Demo of instant dashboard data for web interface
"""

import time
import json
from advanced_analytics import AdvancedAnalytics

def demo_instant_dashboard():
    print("🚀 IntelliPart Instant Dashboard Demo")
    print("=" * 45)
    
    # Initialize analytics
    analytics = AdvancedAnalytics("data/training Dataset.jsonl")
    
    # Get instant dashboard data
    start_time = time.time()
    dashboard_data = analytics.get_instant_dashboard_data()
    dashboard_time = time.time() - start_time
    
    print(f"⚡ Dashboard data retrieved in {dashboard_time*1000:.2f}ms")
    print("\n📊 INSTANT DASHBOARD DATA")
    print("-" * 30)
    
    # Overview
    overview = dashboard_data['overview']
    print(f"📈 Total Parts: {overview['total_parts']:,}")
    print(f"📈 Systems: {overview['total_systems']}")
    print(f"📈 Manufacturers: {overview['total_manufacturers']}")
    print(f"💰 Avg Cost: ₹{overview['avg_cost']:,.2f}")
    print(f"⚠️  Low Stock Alerts: {overview['low_stock_alerts']}")
    
    # Risk assessment
    print(f"\n🔴 Risk Assessment: {dashboard_data['risk_assessment']}")
    print(f"💰 Estimated Savings: ₹{dashboard_data['estimated_savings']:,.0f}")
    
    # Top systems
    print(f"\n🏆 TOP SYSTEMS:")
    for i, system in enumerate(dashboard_data['top_systems'][:3], 1):
        print(f"   {i}. {system['system']}: {system['part_count']} parts (₹{system['avg_cost']:.0f} avg)")
    
    # Alerts
    alerts = dashboard_data['alerts']
    print(f"\n⚠️  ALERTS:")
    print(f"   • Low Stock: {alerts['low_stock']} parts")
    print(f"   • High Risk Suppliers: {alerts['high_risk_suppliers']}")
    print(f"   • Cost Opportunities: {alerts['cost_opportunities']}")
    
    # Test caching performance
    print(f"\n🔄 Testing Cache Performance...")
    start_time = time.time()
    cached_data = analytics.get_instant_dashboard_data()
    cached_time = time.time() - start_time
    print(f"⚡ Cached data retrieved in {cached_time*1000:.3f}ms")
    
    # Show cache status
    print(f"\n🧠 Cache Status: {len(analytics._cache)} items cached")
    
    print("\n🎯 Dashboard Demo Complete!")
    print(f"\n📈 Performance Summary:")
    print(f"   • First call: {dashboard_time*1000:.2f}ms")
    print(f"   • Cached call: {cached_time*1000:.3f}ms")
    if cached_time > 0:
        print(f"   • Speed improvement: {dashboard_time/cached_time:.0f}x faster")
    else:
        print(f"   • Speed improvement: Instant (cache hit)")

if __name__ == "__main__":
    demo_instant_dashboard()
