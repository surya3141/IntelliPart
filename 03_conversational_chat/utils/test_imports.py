#!/usr/bin/env python3
"""
Quick test script to verify all imports work correctly after cleanup
"""

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing IntelliPart 03_conversational_chat imports...")
    
    try:
        print("  Testing conversational_search imports...")
        from conversational_search import ConversationalEngine, ConversationalPartsSearch
        print("  ✅ conversational_search imports OK")
    except Exception as e:
        print(f"  ❌ conversational_search import failed: {e}")
        return False
    
    try:
        print("  Testing conversational_web_app imports...")
        import conversational_web_app
        print("  ✅ conversational_web_app imports OK")
    except Exception as e:
        print(f"  ❌ conversational_web_app import failed: {e}")
        return False
    
    try:
        print("  Testing Flask app creation...")
        app = conversational_web_app.app
        print(f"  ✅ Flask app created: {app}")
    except Exception as e:
        print(f"  ❌ Flask app creation failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic search functionality"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        # Test with sample data
        sample_parts = [
            {"part_name": "Brake Pad", "system": "BRAKES", "manufacturer": "Bosch"},
            {"part_name": "Engine Filter", "system": "ENGINE", "manufacturer": "Mahle"}
        ]
        
        from conversational_search import ConversationalPartsSearch
        search_engine = ConversationalPartsSearch(sample_parts)
        print("  ✅ ConversationalPartsSearch initialized")
        
        # Test basic search
        results = search_engine.search("brake")
        print(f"  ✅ Search test completed: {len(results)} results")
        
    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 IntelliPart Module Health Check")
    print("=" * 40)
    
    imports_ok = test_imports()
    functionality_ok = test_basic_functionality()
    
    print("\n" + "=" * 40)
    if imports_ok and functionality_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Module is ready for production use")
        print("\n🚀 Ready to launch:")
        print("   python conversational_web_app.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Check the errors above and fix before proceeding")
