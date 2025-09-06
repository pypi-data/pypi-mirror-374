#!/usr/bin/env python3
"""
Interactive menu-driven demo for llmswap v4.0.0 features.
Let's you explore and test features interactively.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"  
    python interactive_v4_demo.py
"""

import os
import sys
import time
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class V4Demo:
    def __init__(self):
        self.client_basic = None
        self.client_analytics = None
        self.setup_clients()
    
    def setup_clients(self):
        """Initialize clients for testing."""
        try:
            from llmswap import LLMClient
            
            # Basic client (like v3.x)
            self.client_basic = LLMClient(provider="anthropic")
            
            # Analytics-enabled client (v4.0.0)
            self.client_analytics = LLMClient(
                provider="anthropic", 
                analytics_enabled=True,
                cache_enabled=True
            )
            
            print("✅ Clients initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize clients: {e}")
            sys.exit(1)
    
    def show_menu(self):
        """Display interactive menu."""
        print("\n" + "="*60)
        print("🚀 llmswap v4.0.0 Interactive Feature Demo")
        print("="*60)
        print()
        print("📊 ANALYTICS FEATURES:")
        print("  1. Cost Estimation (Pre-query)")
        print("  2. Provider Cost Comparison")  
        print("  3. Usage Statistics")
        print("  4. Pricing Trends")
        print()
        print("⚡ PERFORMANCE FEATURES:")
        print("  5. Caching Demo (Speed Test)")
        print("  6. Basic vs Analytics Mode")
        print()
        print("💬 CONVERSATION FEATURES:")
        print("  7. Context-Aware Chat")
        print("  8. Conversation History")
        print()
        print("🛠️ UTILITY FEATURES:")
        print("  9. Error Handling Demo")
        print(" 10. Provider Availability Check")
        print(" 11. New Methods Showcase")
        print()
        print("🎯 REAL-WORLD DEMOS:")
        print(" 12. Developer Q&A Session")
        print(" 13. Code Review Simulation")
        print(" 14. Debugging Helper")
        print()
        print("📋 OTHER:")
        print(" 15. Show All Features Summary")
        print("  0. Exit")
        print()
    
    def demo_cost_estimation(self):
        """Demo pre-query cost estimation."""
        print("\n💰 COST ESTIMATION DEMO")
        print("-" * 40)
        
        queries = [
            "Hello world",
            "Explain machine learning basics", 
            "Write a comprehensive guide to Python web development with examples"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. Query: \"{query}\"")
            print(f"   Length: {len(query)} characters")
            
            estimate = self.client_analytics.estimate_query_cost(query)
            if estimate:
                cost = estimate.get('total_cost', 0)
                tokens = estimate.get('input_tokens', 0)
                confidence = estimate.get('confidence', 'unknown')
                
                print(f"   💰 Estimated cost: ${cost:.6f}")
                print(f"   📊 Estimated tokens: {tokens}")
                print(f"   🎯 Confidence: {confidence}")
                
                # Ask if user wants to run the actual query
                if input(f"   ▶️  Run this query? (y/n): ").lower().startswith('y'):
                    start_time = time.time()
                    response = self.client_analytics.query(query)
                    elapsed = time.time() - start_time
                    
                    print(f"   ⏱️  Response time: {elapsed:.2f} seconds")
                    print(f"   📝 Response length: {len(response.content)} chars")
                    
                    if response.usage:
                        actual_tokens = response.usage.get('input_tokens', 0)
                        accuracy = abs(actual_tokens - tokens) / max(actual_tokens, 1) * 100
                        print(f"   🎯 Token estimation accuracy: {100-accuracy:.1f}%")
                    
                    print(f"   📄 Response preview: {response.content[:100]}...")
        
        input("\n⏸️  Press Enter to continue...")
    
    def demo_provider_comparison(self):
        """Demo provider cost comparison."""
        print("\n💸 PROVIDER COST COMPARISON")
        print("-" * 40)
        
        test_cases = [
            ("Small task", 100, 50),
            ("Medium task", 1000, 500),
            ("Large task", 2000, 1000)
        ]
        
        for case_name, input_tokens, output_tokens in test_cases:
            print(f"\n📊 {case_name}: {input_tokens} input + {output_tokens} output tokens")
            
            comparison = self.client_analytics.get_provider_comparison(input_tokens, output_tokens)
            if comparison:
                cheapest = comparison.get('cheapest')
                most_expensive = comparison.get('most_expensive')
                savings = comparison.get('max_savings_percentage', 0)
                
                print(f"   🏆 Cheapest: {cheapest}")
                print(f"   💸 Most expensive: {most_expensive}")
                print(f"   💰 Potential savings: {savings:.1f}%")
                
                print(f"   📋 Full breakdown:")
                for provider, info in comparison.get('comparison', {}).items():
                    if isinstance(info, dict):
                        cost = info.get('total_cost', 0)
                        confidence = info.get('confidence', 'unknown')
                        icon = "🥇" if provider == cheapest else "🥉" if provider == most_expensive else "🥈"
                        print(f"      {icon} {provider:10}: ${cost:8.6f} ({confidence})")
        
        input("\n⏸️  Press Enter to continue...")
    
    def demo_caching_performance(self):
        """Demo caching performance improvement."""
        print("\n⚡ CACHING PERFORMANCE DEMO")
        print("-" * 40)
        
        query = input("Enter a query to test caching (or press Enter for default): ").strip()
        if not query:
            query = "What are the main differences between Python and JavaScript?"
        
        print(f"\nTesting query: \"{query}\"")
        
        # First query (will be cached)
        print(f"\n1️⃣ First query (will be cached)...")
        start_time = time.time()
        response1 = self.client_analytics.query(query)
        time1 = time.time() - start_time
        
        print(f"   ⏱️  Time: {time1:.3f} seconds")
        print(f"   📝 Response length: {len(response1.content)} chars")
        print(f"   🗄️  Cached: {'Yes' if getattr(response1, 'from_cache', False) else 'No'}")
        
        # Second query (from cache)
        print(f"\n2️⃣ Second identical query (from cache)...")
        start_time = time.time()
        response2 = self.client_analytics.query(query)
        time2 = time.time() - start_time
        
        print(f"   ⏱️  Time: {time2:.3f} seconds") 
        print(f"   📝 Response length: {len(response2.content)} chars")
        print(f"   🗄️  Cached: {'Yes' if getattr(response2, 'from_cache', False) else 'No'}")
        
        if time2 > 0:
            improvement = time1 / time2
            print(f"   🚀 Speed improvement: {improvement:.1f}x faster")
        
        # Show cache stats
        stats = self.client_analytics.get_cache_stats()
        if stats:
            print(f"\n📊 Cache Statistics:")
            print(f"   Entries: {stats.get('entries', 0)}")
            print(f"   Memory: {stats.get('memory_used_mb', 0):.2f} MB")
            print(f"   Hit rate: {stats.get('hit_rate', 0):.1%}")
        
        input("\n⏸️  Press Enter to continue...")
    
    def demo_conversation_mode(self):
        """Demo context-aware conversation."""
        print("\n💬 CONTEXT-AWARE CONVERSATION DEMO")
        print("-" * 40)
        
        self.client_analytics.start_conversation()
        print("Starting new conversation...")
        
        print("\n🤖 I'll simulate a context-aware conversation:")
        
        conversation = [
            ("I'm building a Python web API for user management.", "Setting context"),
            ("What's the best framework to use?", "Framework recommendation"),
            ("Why FastAPI over Flask?", "Follow-up question"),
            ("Show me a simple user model example.", "Code request"),
            ("What was I originally building again?", "Context test")
        ]
        
        for i, (message, purpose) in enumerate(conversation, 1):
            print(f"\n{i}. 👤 User ({purpose}): {message}")
            
            if input("   ▶️  Send this message? (y/n): ").lower().startswith('y'):
                response = self.client_analytics.chat(message)
                
                # Show truncated response
                content = response.content
                if len(content) > 300:
                    content = content[:300] + "..."
                
                print(f"   🤖 Assistant: {content}")
            else:
                print("   ⏭️  Skipped")
        
        print(f"\n📊 Conversation Stats:")
        print(f"   Messages: {self.client_analytics.get_conversation_length()}")
        
        input("\n⏸️  Press Enter to continue...")
    
    def demo_new_methods(self):
        """Showcase all new v4.0.0 methods."""
        print("\n🆕 NEW V4.0.0 METHODS SHOWCASE")
        print("-" * 40)
        
        methods = [
            ("get_usage_stats", "Usage statistics and analytics", []),
            ("get_cost_breakdown", "Cost analysis for recent usage", [7]),
            ("get_provider_comparison", "Compare costs across providers", [1000, 500]),
            ("estimate_query_cost", "Pre-query cost estimation", ["Sample query"]),
            ("get_pricing_trends", "Historical pricing analysis", []),
        ]
        
        print("Testing with analytics ENABLED:")
        for method_name, description, args in methods:
            print(f"\n📋 {method_name}:")
            print(f"   Purpose: {description}")
            
            try:
                method = getattr(self.client_analytics, method_name)
                result = method(*args)
                
                if result is None:
                    print(f"   Result: None (no data yet)")
                elif isinstance(result, dict):
                    # Show interesting keys
                    keys = list(result.keys())[:3]
                    print(f"   Result: Dict with keys {keys}...")
                    
                    # Show specific interesting values
                    if 'cheapest' in result:
                        print(f"           Cheapest provider: {result['cheapest']}")
                    if 'total_cost' in result:
                        print(f"           Estimated cost: ${result['total_cost']:.6f}")
                    if 'confidence' in result:
                        print(f"           Confidence: {result['confidence']}")
                else:
                    print(f"   Result: {type(result).__name__}")
                    
            except Exception as e:
                print(f"   Error: {e}")
        
        print("\n🔄 Compare with analytics DISABLED:")
        for method_name, _, args in methods[:2]:  # Just test first 2
            method = getattr(self.client_basic, method_name)
            result = method(*args)
            print(f"   {method_name}: {'None (disabled)' if result is None else 'Has data'}")
        
        input("\n⏸️  Press Enter to continue...")
    
    def demo_developer_qa(self):
        """Simulate real developer Q&A session."""
        print("\n🎯 DEVELOPER Q&A SIMULATION")
        print("-" * 40)
        
        questions = [
            "How do I handle database connections in Python?",
            "What's the difference between authentication and authorization?",
            "Best practices for API error handling?",
            "How to implement rate limiting?",
            "Custom question (enter your own)"
        ]
        
        print("Choose a question to ask:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "5":
            question = input("Enter your question: ").strip()
        elif choice in "1234":
            question = questions[int(choice) - 1]
        else:
            print("Invalid choice")
            return
        
        if question:
            print(f"\n❓ Question: {question}")
            
            # Show cost estimate first
            estimate = self.client_analytics.estimate_query_cost(question)
            if estimate:
                print(f"💰 Estimated cost: ${estimate.get('total_cost', 0):.6f}")
            
            if input("▶️  Get answer? (y/n): ").lower().startswith('y'):
                print("\n🤖 Answer:")
                print("-" * 20)
                
                response = self.client_analytics.query(question)
                print(response.content)
                
                if response.usage:
                    input_tokens = response.usage.get('input_tokens', 0)
                    output_tokens = response.usage.get('output_tokens', 0)
                    print(f"\n📊 Usage: {input_tokens} input + {output_tokens} output = {input_tokens + output_tokens} total tokens")
        
        input("\n⏸️  Press Enter to continue...")
    
    def show_feature_summary(self):
        """Show comprehensive feature summary."""
        print("\n📋 LLMSWAP V4.0.0 FEATURE SUMMARY")
        print("="*60)
        
        features = {
            "🆕 NEW ANALYTICS FEATURES": [
                "Pre-query cost estimation",
                "Real-time provider cost comparison", 
                "Usage statistics and tracking",
                "Price trend analysis",
                "Privacy-first analytics (no queries stored)"
            ],
            "⚡ PERFORMANCE IMPROVEMENTS": [
                "Intelligent response caching",
                "Cache invalidation and management",
                "Response time optimization",
                "Memory usage tracking"
            ],
            "💬 CONVERSATION ENHANCEMENTS": [
                "Context-aware conversations",
                "Conversation history management",
                "Multi-turn dialogue support"
            ],
            "🛠️ DEVELOPER TOOLS": [
                "Comprehensive CLI interface",
                "Advanced log analysis",
                "Code review capabilities",
                "Error debugging assistance"
            ],
            "🔒 ENTERPRISE READY": [
                "100% backward compatibility",
                "Privacy-first design", 
                "Multi-user safe caching",
                "Production-grade error handling"
            ]
        }
        
        for category, items in features.items():
            print(f"\n{category}:")
            for item in items:
                print(f"   ✓ {item}")
        
        print(f"\n🎯 READY FOR PRODUCTION:")
        print("   • All existing v3.x code works unchanged")
        print("   • New features are optional (analytics disabled by default)")
        print("   • Enterprise-grade privacy and security")
        print("   • Comprehensive testing and documentation")
        
        input("\n⏸️  Press Enter to continue...")
    
    def run(self):
        """Run the interactive demo."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("❌ ANTHROPIC_API_KEY not found!")
            print("\n🔑 Set your API key first:")
            print("   export ANTHROPIC_API_KEY='your-key-here'")
            return
        
        while True:
            self.show_menu()
            choice = input("Enter your choice (0-15): ").strip()
            
            try:
                if choice == "0":
                    print("\n👋 Thanks for exploring llmswap v4.0.0!")
                    break
                elif choice == "1":
                    self.demo_cost_estimation()
                elif choice == "2":
                    self.demo_provider_comparison()
                elif choice == "3":
                    print("\n📊 Usage statistics require multiple queries to generate data.")
                    print("Run other demos first to generate usage data!")
                    input("⏸️  Press Enter to continue...")
                elif choice == "4":
                    print("\n📈 Pricing trends require historical data.")
                    print("This feature tracks price changes over time.")
                    input("⏸️  Press Enter to continue...")
                elif choice == "5":
                    self.demo_caching_performance()
                elif choice == "6":
                    print("\n🔄 Basic vs Analytics comparison was shown in the main demo.")
                    print("Analytics adds cost tracking without affecting core functionality!")
                    input("⏸️  Press Enter to continue...")
                elif choice == "7":
                    self.demo_conversation_mode()
                elif choice == "8":
                    print("\n💬 Conversation history is managed automatically.")
                    print("Try the conversation demo to see it in action!")
                    input("⏸️  Press Enter to continue...")
                elif choice == "9":
                    print("\n🚨 Error handling works automatically.")
                    print("Try invalid API keys or unavailable providers to see graceful failures.")
                    input("⏸️  Press Enter to continue...")
                elif choice == "10":
                    print(f"\n🔍 Provider availability:")
                    for provider in ["anthropic", "openai", "gemini", "ollama", "watsonx"]:
                        available = self.client_basic.is_provider_available(provider)
                        status = "✅ Available" if available else "❌ Not configured"
                        print(f"   {provider:12}: {status}")
                    input("\n⏸️  Press Enter to continue...")
                elif choice == "11":
                    self.demo_new_methods()
                elif choice == "12":
                    self.demo_developer_qa()
                elif choice == "13":
                    print("\n📝 Code review is available via CLI:")
                    print("   python -m llmswap review yourfile.py --focus security")
                    input("⏸️  Press Enter to continue...")
                elif choice == "14":
                    print("\n🐛 Debugging is available via CLI:")
                    print("   python -m llmswap debug --error 'Your error message'")
                    input("⏸️  Press Enter to continue...")
                elif choice == "15":
                    self.show_feature_summary()
                else:
                    print("❌ Invalid choice. Please try again.")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("⏸️  Press Enter to continue...")

if __name__ == "__main__":
    demo = V4Demo()
    demo.run()