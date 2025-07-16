"""
Test script to demonstrate the fast analytics performance
"""

import time
from advanced_analytics import AdvancedAnalytics

def test_performance():
    print("🚀 Testing IntelliPart Fast Analytics Performance")
    print("=" * 55)
    
    # Initialize analytics
    start_time = time.time()
    analytics = AdvancedAnalytics("data/training Dataset.jsonl")
    init_time = time.time() - start_time
    print(f"⚡ Initialization: {init_time:.3f}s")
    
    # Test quick metrics
    start_time = time.time()
    metrics = analytics.get_quick_metrics()
    metrics_time = time.time() - start_time
    print(f"⚡ Quick Metrics: {metrics_time:.4f}s")
    print(f"   📊 {metrics['total_parts']} parts, {metrics['total_systems']} systems")
    
    # Test top systems
    start_time = time.time()
    top_systems = analytics.get_top_systems(5)
    systems_time = time.time() - start_time
    print(f"⚡ Top Systems: {systems_time:.4f}s")
    print(f"   📊 Top system: {top_systems[0]['system']} ({top_systems[0]['part_count']} parts)")
    
    # Test cost summary
    start_time = time.time()
    cost_summary = analytics.get_cost_summary()
    cost_time = time.time() - start_time
    print(f"⚡ Cost Summary: {cost_time:.4f}s")
    print(f"   💰 Avg cost: ₹{cost_summary['avg_cost']}, Range: ₹{cost_summary['cost_range']}")
    
    # Test full analytics (first time)
    start_time = time.time()
    demand = analytics.predictive_demand_analysis()
    demand_time = time.time() - start_time
    print(f"⚡ Demand Analysis: {demand_time:.4f}s")
    
    # Test full analytics (cached)
    start_time = time.time()
    demand_cached = analytics.predictive_demand_analysis()
    demand_cached_time = time.time() - start_time
    print(f"⚡ Demand Analysis (cached): {demand_cached_time:.6f}s")
    
    # Test comprehensive report
    start_time = time.time()
    report = analytics.generate_comprehensive_report()
    report_time = time.time() - start_time
    print(f"⚡ Comprehensive Report: {report_time:.4f}s")
    
    print(f"\n🧠 Cache Status: {len(analytics._cache)} items cached")
    print("\n🎯 Performance Test Complete!")
    print("\n📈 Summary:")
    print(f"   • Quick Metrics: {metrics_time*1000:.1f}ms")
    print(f"   • Analytics (first): {demand_time*1000:.1f}ms")
    print(f"   • Analytics (cached): {demand_cached_time*1000:.3f}ms")
    print(f"   • Full Report: {report_time*1000:.1f}ms")

if __name__ == "__main__":
    test_performance()
