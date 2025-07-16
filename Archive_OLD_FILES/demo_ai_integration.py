"""
IntelliPart AI Integration Demonstration
Shows exactly where and how AI is used in the system
"""

from lightweight_ai_search import LightweightAISearch
# from conversational_search import ConversationalPartsSearch
import time

# This file is archived and should not be used. Use conversational_web_app.py instead.

def main():
    print("🤖 INTELLIPART AI INTEGRATION DEMONSTRATION")
    print("=" * 60)
    
    # 1. Initialize AI components
    print("\n🔄 Step 1: Loading AI Models & Embeddings")
    print("-" * 40)
    
    try:
        # Load the AI search engine with TF-IDF vectors
        ai_search = LightweightAISearch("data/training Dataset.jsonl")
        print("✅ TF-IDF AI Vectorization loaded successfully")
        
        # Load conversational AI with NLU
        # conv_search = ConversationalPartsSearch("data/training Dataset.jsonl")
        # print("✅ Conversational AI with NLU loaded successfully")
        
    except Exception as e:
        print(f"❌ Error loading AI components: {e}")
        return
    
    # 2. Demonstrate Natural Language Understanding AI
    print("\n🧠 Step 2: Natural Language Understanding AI")
    print("-" * 45)
    
    test_queries = [
        "Find brake pads similar to Brembo",
        "I need exact part number ENG-123",
        "Show me cheap aluminum parts under $300",
        "What steel components are available?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        understanding = conv_search.understand_query(query)
        print(f"   🤖 AI Intent: {understanding['intent']}")
        print(f"   🎯 AI Strategy: {understanding['search_strategy']}")
        print(f"   📝 AI Entities: {understanding['entities']}")
    
    # 3. Demonstrate AI Similarity Search
    print("\n\n🔍 Step 3: AI Similarity Search Engine")
    print("-" * 42)
    
    similarity_query = "brake pads heavy duty"
    print(f"🔍 Testing AI similarity for: '{similarity_query}'")
    
    start_time = time.time()
    ai_results = ai_search.ai_search(similarity_query, top_k=3)
    ai_time = time.time() - start_time
    
    print(f"⚡ AI search completed in {ai_time:.3f} seconds")
    print(f"📊 AI found {len(ai_results)} similar parts")
    
    print("\n🎯 AI-Ranked Results:")
    for i, result in enumerate(ai_results, 1):
        ai_score = result.get('_ai_score', 0)
        part_name = result.get('part_name', 'Unknown')
        print(f"   {i}. {part_name} (AI Score: {ai_score:.3f})")
    
    # 4. Demonstrate Conversational AI
    print("\n\n💬 Step 4: Conversational AI Integration")
    print("-" * 43)
    
    conv_query = "Find alternatives to expensive brake components"
    print(f"🔍 Conversational query: '{conv_query}'")
    
    start_time = time.time()
    conv_result = conv_search.search(conv_query, limit=3)
    conv_time = time.time() - start_time
    
    print(f"⚡ Conversational AI completed in {conv_time:.3f} seconds")
    print(f"🧠 AI Understanding:")
    print(f"   Intent: {conv_result['understanding']['intent']}")
    print(f"   Strategy: {conv_result['understanding']['search_strategy']}")
    print(f"📊 Found {conv_result['result_count']} results")
    
    # 5. Show AI Integration Summary
    print("\n\n🎯 AI INTEGRATION SUMMARY")
    print("-" * 30)
    print("✅ Natural Language Understanding (NLU)")
    print("✅ TF-IDF Vectorization & Cosine Similarity")
    print("✅ Intent Classification & Entity Extraction")
    print("✅ Semantic Part Matching")
    print("✅ Conversational Context Memory")
    print("✅ Intelligent Search Strategy Selection")
    print("✅ AI-Powered Result Ranking")
    
    print("\n🚀 IntelliPart uses AI at EVERY level!")
    print("   From understanding your question to finding the perfect part!")

if __name__ == "__main__":
    main()
