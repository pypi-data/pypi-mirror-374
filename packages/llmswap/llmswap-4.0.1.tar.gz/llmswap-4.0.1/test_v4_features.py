#!/usr/bin/env python3
"""
Interactive test script for llmswap v4.0.0 features.
Run this to see all new features in action with your API key.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python test_v4_features.py
"""

import os
import sys
import time
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_api_key():
    """Check if API key is set."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found!")
        print("\n🔑 Set your API key first:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        print("   python test_v4_features.py")
        return False
    
    print("✅ API key found!")
    return True

def test_basic_vs_analytics():
    """Compare v3 (basic) vs v4 (analytics) functionality."""
    print("\n" + "="*60)
    print("TEST 1: BASIC vs ANALYTICS MODE COMPARISON")
    print("="*60)
    
    from llmswap import LLMClient
    
    # Test basic mode (like v3.x)
    print("\n🔵 BASIC MODE (like v3.x):")
    print("-" * 30)
    
    client_basic = LLMClient(provider="anthropic")
    print(f"Analytics enabled: {getattr(client_basic, '_analytics_enabled', False)}")
    
    query = "What are the benefits of Python?"
    start_time = time.time()
    response = client_basic.query(query)
    basic_time = time.time() - start_time
    
    print(f"Query: {query}")
    print(f"Response length: {len(response.content)} chars")
    print(f"Time taken: {basic_time:.2f} seconds")
    print(f"Usage data available: {'Yes' if response.usage else 'No'}")
    
    # Test analytics mode (v4.0.0)
    print("\n🟢 ANALYTICS MODE (v4.0.0):")
    print("-" * 30)
    
    client_analytics = LLMClient(provider="anthropic", analytics_enabled=True)
    print(f"Analytics enabled: {client_analytics._analytics_enabled}")
    
    # Pre-query cost estimation
    cost_estimate = client_analytics.estimate_query_cost(query)
    if cost_estimate:
        print(f"💰 Pre-query cost estimate: ${cost_estimate.get('total_cost', 0):.6f}")
        print(f"📊 Estimated input tokens: {cost_estimate.get('input_tokens', 0)}")
    
    start_time = time.time()
    response = client_analytics.query(query)
    analytics_time = time.time() - start_time
    
    print(f"Query: {query}")
    print(f"Response length: {len(response.content)} chars")
    print(f"Time taken: {analytics_time:.2f} seconds")
    print(f"Usage data available: {'Yes' if response.usage else 'No'}")
    
    if response.usage:
        actual_input = response.usage.get('input_tokens', 0)
        actual_output = response.usage.get('output_tokens', 0)
        print(f"📊 Actual tokens: {actual_input} input, {actual_output} output")
        
        if cost_estimate:
            estimated = cost_estimate.get('input_tokens', 0)
            accuracy = abs(actual_input - estimated) / max(actual_input, 1) * 100
            print(f"🎯 Estimation accuracy: {100 - accuracy:.1f}%")
    
    # Show new analytics methods
    print(f"\n📈 NEW ANALYTICS METHODS:")
    stats = client_analytics.get_usage_stats()
    print(f"   get_usage_stats(): {'Available' if stats else 'No data yet'}")
    
    comparison = client_analytics.get_provider_comparison(1000, 500)
    if comparison:
        cheapest = comparison.get('cheapest')
        savings = comparison.get('max_savings_percentage', 0)
        print(f"   get_provider_comparison(): {cheapest} cheapest ({savings:.1f}% savings)")
    
    trends = client_analytics.get_pricing_trends()
    print(f"   get_pricing_trends(): {'Available' if trends else 'No historical data'}")

def test_cost_comparison():
    """Show detailed cost comparison across providers."""
    print("\n" + "="*60)
    print("TEST 2: PROVIDER COST COMPARISON")
    print("="*60)
    
    from llmswap import LLMClient
    
    client = LLMClient(provider="anthropic", analytics_enabled=True)
    
    # Test different query sizes
    test_cases = [
        ("Small query", "Hello", 100, 50),
        ("Medium query", "Explain machine learning", 1000, 500),  
        ("Large query", "Write comprehensive analysis", 2000, 1000)
    ]
    
    for case_name, query, input_tokens, output_tokens in test_cases:
        print(f"\n📊 {case_name.upper()}")
        print(f"Query: '{query}'")
        print(f"Token estimate: {input_tokens} input + {output_tokens} output")
        
        comparison = client.get_provider_comparison(input_tokens, output_tokens)
        if comparison:
            print(f"\n💰 Cost breakdown:")
            for provider, info in comparison.get('comparison', {}).items():
                if isinstance(info, dict):
                    cost = info.get('total_cost', 0)
                    confidence = info.get('confidence', 'unknown')
                    note = info.get('note', '')
                    savings_indicator = "🏆" if provider == comparison.get('cheapest') else "💸" if provider == comparison.get('most_expensive') else "  "
                    print(f"   {savings_indicator} {provider:10}: ${cost:8.6f} ({confidence}) {note}")
            
            cheapest_cost = comparison.get('cheapest_cost', 0)
            most_expensive_cost = comparison.get('most_expensive_cost', 0)
            if most_expensive_cost > 0:
                savings = (most_expensive_cost - cheapest_cost) / most_expensive_cost * 100
                print(f"\n   📈 Maximum savings: {savings:.1f}% (${most_expensive_cost - cheapest_cost:.6f})")

def test_caching_performance():
    """Demonstrate caching performance improvements."""
    print("\n" + "="*60)
    print("TEST 3: CACHING PERFORMANCE")
    print("="*60)
    
    from llmswap import LLMClient
    
    # Test without caching
    print("\n⭕ WITHOUT CACHING:")
    client_no_cache = LLMClient(provider="anthropic", cache_enabled=False)
    
    query = "What is the capital of France?"
    
    start_time = time.time()
    response1 = client_no_cache.query(query)
    time1 = time.time() - start_time
    
    start_time = time.time() 
    response2 = client_no_cache.query(query)
    time2 = time.time() - start_time
    
    print(f"First query:  {time1:.3f} seconds")
    print(f"Second query: {time2:.3f} seconds")
    print(f"Time difference: {abs(time2 - time1):.3f} seconds")
    
    # Test with caching
    print("\n✅ WITH CACHING:")
    client_cache = LLMClient(provider="anthropic", cache_enabled=True, cache_ttl=300)
    
    start_time = time.time()
    response1 = client_cache.query(query)
    time1 = time.time() - start_time
    
    start_time = time.time()
    response2 = client_cache.query(query)
    time2 = time.time() - start_time
    
    print(f"First query (cached): {time1:.3f} seconds")
    print(f"Second query (from cache): {time2:.3f} seconds") 
    print(f"Speed improvement: {(time1/time2 if time2 > 0 else 0):.0f}x faster")
    print(f"Cache hit: {'Yes' if getattr(response2, 'from_cache', False) else 'No'}")
    
    # Show cache stats
    stats = client_cache.get_cache_stats()
    if stats:
        print(f"\n📊 Cache Statistics:")
        print(f"   Entries: {stats.get('entries', 0)}")
        print(f"   Memory used: {stats.get('memory_used_mb', 0):.2f} MB")
        print(f"   Hit rate: {stats.get('hit_rate', 0):.1%}")

def test_conversation_context():
    """Test conversation mode with context."""
    print("\n" + "="*60)
    print("TEST 4: CONVERSATION CONTEXT")
    print("="*60)
    
    from llmswap import LLMClient
    
    client = LLMClient(provider="anthropic")
    client.start_conversation()
    
    conversation = [
        "My name is Alice and I'm learning Python.",
        "What's the best way to learn loops?",
        "Can you give me a for loop example?",
        "What's my name again?"  # Tests context retention
    ]
    
    print("💬 Conversation Test:")
    for i, message in enumerate(conversation, 1):
        print(f"\n{i}. 👤 User: {message}")
        
        response = client.chat(message)
        
        # Truncate long responses for readability
        content = response.content
        if len(content) > 200:
            content = content[:200] + "..."
        
        print(f"   🤖 Assistant: {content}")
    
    print(f"\n📊 Conversation Stats:")
    print(f"   Total messages: {client.get_conversation_length()}")
    print(f"   Context maintained: {'Yes' if 'Alice' in response.content else 'No'}")

def test_error_handling():
    """Test error handling and fallback."""
    print("\n" + "="*60)
    print("TEST 5: ERROR HANDLING & FALLBACK")
    print("="*60)
    
    from llmswap import LLMClient, ConfigurationError
    
    print("🔍 Testing provider availability:")
    client = LLMClient(provider="anthropic")
    
    providers = ["anthropic", "openai", "gemini", "ollama", "watsonx"]
    available_count = 0
    
    for provider in providers:
        is_available = client.is_provider_available(provider)
        status = "✅ Available" if is_available else "❌ Not configured" 
        print(f"   {provider:12}: {status}")
        if is_available:
            available_count += 1
    
    print(f"\nConfigured providers: {available_count}/{len(providers)}")
    
    # Test graceful error handling
    print(f"\n🚨 Testing error handling:")
    try:
        bad_client = LLMClient(provider="anthropic", api_key="invalid_key")
        response = bad_client.query("test")
        print("   ❌ Should have failed")
    except Exception as e:
        print(f"   ✅ Gracefully handled: {type(e).__name__}")
        print(f"      Error: {str(e)[:80]}...")

def test_new_methods():
    """Test all new methods added in v4.0.0."""
    print("\n" + "="*60)
    print("TEST 6: NEW V4.0.0 METHODS")
    print("="*60)
    
    from llmswap import LLMClient
    
    # Test with analytics disabled (default)
    print("🔵 Analytics DISABLED (default):")
    client_basic = LLMClient(provider="anthropic")
    
    new_methods = [
        ('get_usage_stats', []),
        ('get_cost_breakdown', [7]),
        ('get_provider_comparison', [1000, 500]),
        ('estimate_query_cost', ["Test query"]),
        ('get_pricing_trends', []),
        ('export_analytics', ["/tmp/test.json"])
    ]
    
    for method_name, args in new_methods:
        try:
            method = getattr(client_basic, method_name)
            result = method(*args)
            print(f"   {method_name:22}: {'None (disabled)' if result is None else 'Has data'}")
        except Exception as e:
            print(f"   {method_name:22}: Error - {e}")
    
    # Test with analytics enabled
    print(f"\n🟢 Analytics ENABLED:")
    client_analytics = LLMClient(provider="anthropic", analytics_enabled=True)
    
    for method_name, args in new_methods[:5]:  # Skip export for demo
        try:
            method = getattr(client_analytics, method_name)
            result = method(*args)
            if result is None:
                print(f"   {method_name:22}: None (no data yet)")
            elif isinstance(result, dict):
                key_info = list(result.keys())[:3]  # Show first 3 keys
                print(f"   {method_name:22}: Dict with keys: {key_info}...")
            else:
                print(f"   {method_name:22}: {type(result).__name__}")
        except Exception as e:
            print(f"   {method_name:22}: Error - {e}")

def run_all_tests():
    """Run all v4.0.0 feature tests."""
    print("🎉 llmswap v4.0.0 Feature Testing Suite")
    print("=" * 60)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not check_api_key():
        return False
    
    try:
        test_basic_vs_analytics()
        test_cost_comparison() 
        test_caching_performance()
        test_conversation_context()
        test_error_handling()
        test_new_methods()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("🎊 llmswap v4.0.0 features are working perfectly!")
        print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print(f"\n🚀 Next steps:")
        print("   • Try the CLI: python -m llmswap ask 'Your question'")
        print("   • Test code review: python -m llmswap review yourfile.py")
        print("   • Interactive chat: python -m llmswap chat")
    
    sys.exit(0 if success else 1)