#!/usr/bin/env python3
try:
    import conversational_search
    print("✅ conversational_search import successful")
except Exception as e:
    print(f"❌ conversational_search import failed: {e}")

try:
    from conversational_search import ConversationalEngine, ConversationalPartsSearch
    print("✅ Specific imports successful")
except Exception as e:
    print(f"❌ Specific imports failed: {e}")

try:
    import conversational_web_app
    print("✅ conversational_web_app import successful")
except Exception as e:
    print(f"❌ conversational_web_app import failed: {e}")
