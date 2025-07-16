#!/usr/bin/env python3
"""
Production Deep Analysis - Main Entry Point
Advanced analytics for 200K+ automotive parts with predictive insights
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to the Python path for shared modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from dataset_loader import load_all_parts
except ImportError:
    print("[ERROR] Could not import dataset_loader. Please ensure dataset_loader.py is in the project root.")
    def load_all_parts():
        print("[ERROR] Dummy load_all_parts called. No data loaded.")
        return []

def main():
    """Main function for production deep analysis"""
    print("🚀 IntelliPart Production Deep Analysis")
    print("=" * 60)
    print("📊 Advanced Analytics • 🔮 Predictive Insights • 📈 Business Intelligence")
    print()
    
    # Check for available analytics engines
    analytics_options = [
        {
            "name": "Production Analytics Engine",
            "module": "production_analytics_engine",
            "class": "ProductionAnalyticsEngine",
            "description": "200K+ parts with 50+ attributes analytics",
            "recommended": True
        },
        {
            "name": "Legacy Advanced Analytics",
            "module": "advanced_analytics",
            "class": "AdvancedAnalytics",
            "description": "Compatible with existing datasets",
            "recommended": False
        }
    ]
    
    print("Available Analytics Engines:")
    for i, option in enumerate(analytics_options, 1):
        status = "🌟 RECOMMENDED" if option["recommended"] else "📊 Available"
        print(f"{i}. {option['name']} - {option['description']} {status}")
    
    print()
    choice = input("Select analytics engine (1-2) or press Enter for recommended: ").strip()
    
    if not choice:
        choice = "1"  # Default to production engine
    
    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(analytics_options):
            selected = analytics_options[choice_idx]
        else:
            selected = analytics_options[0]  # Default to first option
    except ValueError:
        selected = analytics_options[0]  # Default to first option
    
    print(f"\n🔧 Initializing {selected['name']}...")
    
    try:
        # Import and run the selected analytics engine
        if selected["module"] == "production_analytics_engine":
            from production_analytics_engine import main as run_production_analytics
            run_production_analytics()
        else:
            from advanced_analytics import AdvancedAnalytics, main as run_advanced_analytics
            print("🚀 Running Legacy Advanced Analytics...")
            run_advanced_analytics()
        
        print("\n🎯 Analysis Complete! Next Steps:")
        print("  1. Review generated analytics report")
        print("  2. Test conversational AI: python ../03_conversational_chat/main.py")
        print("  3. Launch demo: python ../04_hackathon_demo/launch_demo.py")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔄 Falling back to basic analytics...")
        run_basic_analytics()
    except Exception as e:
        print(f"❌ Analytics execution failed: {e}")
        print("🔄 Attempting fallback analytics...")
        run_basic_analytics()

def run_basic_analytics():
    """Fallback basic analytics if main engines fail"""
    print("\n📊 Running Basic Analytics...")
    
    # Load all parts from the base dataset directory
    all_parts = load_all_parts()
    
    if not all_parts:
        print("❌ No data found. Please run dataset generation first.")
        return
    
    # Basic analytics
    total_parts = len(all_parts)
    categories = set()
    costs = []
    
    for part in all_parts:
        categories.add(part.get('category', part.get('system', 'Unknown')))
        
        cost = part.get('cost', part.get('cost_price', 0))
        if isinstance(cost, str):
            import re
            numbers = re.findall(r'[\d.]+', cost)
            cost = float(numbers[0]) if numbers else 0
        costs.append(float(cost))
    
    avg_cost = sum(costs) / len(costs) if costs else 0
    
    basic_report = {
        "metadata": {
            "analysis_type": "basic",
            "total_parts": total_parts,
            "data_source": "fallback"
        },
        "summary": {
            "total_parts": total_parts,
            "unique_categories": len(categories),
            "average_cost": round(avg_cost, 2),
            "categories": list(categories)
        }
    }
    
    print(f"✅ Basic Analysis Complete:")
    print(f"  📦 Total Parts: {total_parts:,}")
    print(f"  📂 Categories: {len(categories)}")
    print(f"  💰 Average Cost: ₹{avg_cost:.2f}")
    
    # Save basic report
    with open("basic_analytics_report.json", "w") as f:
        json.dump(basic_report, f, indent=2)
    
    print("📄 Basic report saved to basic_analytics_report.json")

if __name__ == "__main__":
    main()
