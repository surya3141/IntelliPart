"""
IntelliPart Enhanced Demo
Demonstrates all the enhanced features and capabilities
"""

import time
import json
from analytics_dashboard import PartsAnalytics
from lightweight_ai_search import LightweightAISearch

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"🔧 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section."""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_analytics():
    """Demonstrate analytics capabilities."""
    print_header("INTELLIPART ENHANCED ANALYTICS DEMO")
    
    print("Initializing analytics engine...")
    analytics = PartsAnalytics("data/training Dataset.jsonl")
    
    print_section("Quick Statistics")
    report = analytics.generate_comprehensive_report()
    
    overview = report['overview']
    print(f"📊 Total Parts: {overview['total_parts']:,}")
    print(f"🏭 Manufacturers: {overview['unique_manufacturers']}")
    print(f"⚙️  Systems: {overview['unique_systems']}")
    print(f"💰 Average Cost: ${overview['avg_cost']:,.2f}")
    print(f"💵 Total Value: ${overview['total_inventory_value']:,.2f}")
    
    print_section("Cost Analysis")
    cost_analysis = report['cost_analysis']
    if 'cost_stats' in cost_analysis:
        stats = cost_analysis['cost_stats']
        print(f"💸 Price Range: ${stats['min']:,.2f} - ${stats['max']:,.2f}")
        print(f"📊 Median Price: ${stats['median']:,.2f}")
        print(f"📈 Standard Deviation: ${stats['std']:,.2f}")
        
        ranges = cost_analysis['cost_ranges']
        print(f"🟢 Budget Parts (≤$100): {ranges['budget']} parts")
        print(f"🟡 Mid-range ($100-$500): {ranges['mid_range']} parts")
        print(f"🔴 Premium (>$500): {ranges['premium']} parts")
    
    print_section("Top Insights")
    insights = report['insights']
    for i, insight in enumerate(insights[:5], 1):
        print(f"{i}. {insight}")
    
    print_section("Top Manufacturers")
    manufacturers = report['manufacturer_analysis']['top_manufacturers']
    for i, (mfg, count) in enumerate(list(manufacturers.items())[:5], 1):
        print(f"{i}. {mfg}: {count} parts")
    
    return analytics

def demo_search():
    """Demonstrate search capabilities."""
    print_header("INTELLIPART ENHANCED SEARCH DEMO")
    
    print("Initializing AI search engine...")
    search_engine = LightweightAISearch("data/training Dataset.jsonl")
    
    # Demo different search types
    search_queries = [
        ("LED headlight", "ai"),
        ("brake pad", "smart"),
        ("wiper blade", "keyword"),
        ("oil filter", "ai")
    ]
    
    for query, search_type in search_queries:
        print_section(f"{search_type.upper()} Search: '{query}'")
        
        start_time = time.time()
        if search_type == "ai":
            results = search_engine.ai_search(query, top_k=3)
        elif search_type == "smart":
            results = search_engine.smart_search(query, top_k=3)
        else:
            results = search_engine.keyword_search(query, top_k=3)
        
        search_time = time.time() - start_time
        
        print(f"⏱️  Search Time: {search_time:.3f}s")
        print(f"📋 Results Found: {len(results)}")
        
        for i, part in enumerate(results[:3], 1):
            score = part.get('_ai_score', part.get('_smart_score', part.get('_match_score', 'N/A')))
            print(f"\n{i}. {part.get('part_name', 'Unknown')} ({part.get('part_number', 'N/A')})")
            print(f"   Score: {score:.3f}" if isinstance(score, (int, float)) else f"   Score: {score}")
            print(f"   System: {part.get('system', 'N/A')}")
            print(f"   Manufacturer: {part.get('manufacturer', 'N/A')}")
            print(f"   Cost: {part.get('cost', 'N/A')}")
    
    print_section("Auto-Suggestions Demo")
    suggestion_tests = ["head", "bra", "wip", "oil"]
    
    for partial in suggestion_tests:
        suggestions = search_engine.auto_suggest(partial, max_suggestions=3)
        print(f"'{partial}' → {', '.join(suggestions) if suggestions else 'No suggestions'}")
    
    print_section("Similar Parts Demo")
    # Find a part to use as example
    sample_results = search_engine.keyword_search("brake", top_k=1)
    if sample_results:
        sample_part = sample_results[0]
        part_number = sample_part.get('part_number')
        if part_number:
            print(f"Finding parts similar to: {sample_part.get('part_name', 'Unknown')} ({part_number})")
            similar_parts = search_engine.find_similar_parts(part_number, top_k=3)
            
            for i, part in enumerate(similar_parts, 1):
                print(f"{i}. {part.get('part_name', 'Unknown')} - Similarity: {part.get('_ai_score', 0):.3f}")
    
    return search_engine

def demo_performance():
    """Demonstrate performance features."""
    print_header("INTELLIPART PERFORMANCE DEMO")
    
    print_section("Search Performance Comparison")
    search_engine = LightweightAISearch("data/training Dataset.jsonl")
    
    test_queries = ["brake", "LED", "filter", "wiper", "engine"]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        
        # Test different search methods
        methods = [
            ("Keyword", lambda q: search_engine.keyword_search(q, top_k=10)),
            ("AI Search", lambda q: search_engine.ai_search(q, top_k=10)),
            ("Smart Search", lambda q: search_engine.smart_search(q, top_k=10))
        ]
        
        for method_name, method_func in methods:
            start_time = time.time()
            results = method_func(query)
            end_time = time.time()
            
            print(f"  {method_name}: {end_time - start_time:.3f}s ({len(results)} results)")
    
    print_section("Memory Usage Estimation")
    # Simple memory usage estimation
    import sys
    
    parts_size = sys.getsizeof(search_engine.parts)
    print(f"Parts data: ~{parts_size / 1024 / 1024:.1f} MB")
    
    if hasattr(search_engine, 'tfidf_matrix') and search_engine.tfidf_matrix is not None:
        matrix_size = search_engine.tfidf_matrix.data.nbytes + search_engine.tfidf_matrix.indices.nbytes + search_engine.tfidf_matrix.indptr.nbytes
        print(f"TF-IDF matrix: ~{matrix_size / 1024 / 1024:.1f} MB")
    
    print(f"Total estimated: ~{(parts_size + (matrix_size if 'matrix_size' in locals() else 0)) / 1024 / 1024:.1f} MB")

def demo_web_features():
    """Demonstrate web interface features."""
    print_header("INTELLIPART WEB INTERFACE DEMO")
    
    print_section("Available Web Applications")
    
    web_apps = [
        {
            "name": "Enhanced IntelliPart",
            "file": "enhanced_intellipart_app.py",
            "port": 5002,
            "features": [
                "4 search types (Smart, AI, Fuzzy, Keyword)",
                "Real-time analytics dashboard",
                "Advanced filtering and suggestions",
                "Modern responsive UI with glassmorphism"
            ]
        },
        {
            "name": "Ultimate Search",
            "file": "ultimate_search_app.py", 
            "port": 5001,
            "features": [
                "Combined search methods",
                "Similar parts discovery",
                "Fast filtering",
                "Clean minimalist interface"
            ]
        },
        {
            "name": "Basic Web UI",
            "file": "web_app.py",
            "port": 5000,
            "features": [
                "Simple search interface",
                "Basic filtering",
                "Fast and lightweight",
                "Mobile-friendly design"
            ]
        }
    ]
    
    for app in web_apps:
        print(f"\n🌐 {app['name']}")
        print(f"   File: {app['file']}")
        print(f"   URL: http://localhost:{app['port']}")
        print("   Features:")
        for feature in app['features']:
            print(f"   • {feature}")
    
    print_section("Web Interface Features")
    features = [
        "🔍 Real-time search with auto-suggestions",
        "📊 Interactive analytics dashboard",
        "🎨 Modern UI with smooth animations",
        "📱 Responsive design for all devices",
        "⚡ Fast AJAX-based updates",
        "🔧 Advanced filtering options",
        "📈 Live statistics and insights",
        "🎯 Similar parts discovery",
        "💾 Export capabilities",
        "🌟 Glassmorphism design effects"
    ]
    
    for feature in features:
        print(feature)

def interactive_demo():
    """Run an interactive demo."""
    print_header("INTELLIPART ENHANCED - INTERACTIVE DEMO")
    
    print("Welcome to the IntelliPart Enhanced demonstration!")
    print("This demo showcases the advanced features and capabilities.")
    
    while True:
        print("\n" + "="*50)
        print("📋 DEMO MENU")
        print("="*50)
        print("1. 📊 Analytics Dashboard Demo")
        print("2. 🔍 Search Engine Demo")
        print("3. ⚡ Performance Demo")
        print("4. 🌐 Web Interface Overview")
        print("5. 🎯 Full Feature Demo")
        print("6. 📖 Help & Documentation")
        print("0. 🚪 Exit")
        
        choice = input("\nSelect demo option (0-6): ").strip()
        
        if choice == "0":
            print("\n👋 Thank you for exploring IntelliPart Enhanced!")
            print("🚀 Ready to revolutionize your auto parts management!")
            break
        elif choice == "1":
            demo_analytics()
        elif choice == "2":
            demo_search()
        elif choice == "3":
            demo_performance()
        elif choice == "4":
            demo_web_features()
        elif choice == "5":
            print_header("FULL FEATURE DEMONSTRATION")
            demo_analytics()
            demo_search()
            demo_performance()
            demo_web_features()
        elif choice == "6":
            print_header("HELP & DOCUMENTATION")
            print("📚 Available Documentation:")
            print("• README_Enhanced.md - Comprehensive feature guide")
            print("• Code comments - Detailed technical documentation")
            print("• Function docstrings - API documentation")
            print("\n🔧 Quick Start:")
            print("1. Run 'python enhanced_intellipart_app.py' for web interface")
            print("2. Run 'python analytics_dashboard.py' for CLI analytics")
            print("3. Run 'python lightweight_ai_search.py' for CLI search")
            print("\n💡 Tips:")
            print("• Use Smart Search for best results")
            print("• Check analytics for inventory insights")
            print("• Enable caching for better performance")
        else:
            print("❌ Invalid choice. Please select 0-6.")
        
        if choice != "0":
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    interactive_demo()
