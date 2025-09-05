import json
import os
from llmswap import LLMClient
from llmswap.metrics import CostEstimator

def format_provider_comparison(comparison):
    """Format provider comparison in table format"""
    print(f"💰 Provider Cost Comparison ({comparison['input_tokens']} input + {comparison['output_tokens']} output tokens)")
    print("=" * 80)
    print(f"{'Provider':<12} {'Model':<20} {'Total Cost':<12} {'Savings':<12} {'Confidence'}")
    print("-" * 80)
    
    # Sort by cost for better comparison
    providers = [(k, v) for k, v in comparison['comparison'].items()]
    providers.sort(key=lambda x: x[1]['total_cost'])
    
    max_cost = comparison['most_expensive_cost']
    for provider, data in providers:
        savings = ((max_cost - data['total_cost']) / max_cost * 100) if max_cost > 0 else 0
        savings_str = f"{savings:.1f}%" if savings > 0 else "-"
        cost_str = f"${data['total_cost']:.6f}"
        
        print(f"{provider:<12} {data.get('model','')[:19]:<20} {cost_str:<12} {savings_str:<12} {data.get('confidence','')}")
    
    print("-" * 80)
    print(f"🏆 Cheapest: {comparison['cheapest']} (${comparison['cheapest_cost']:.6f})")
    print(f"💸 Most Expensive: {comparison['most_expensive']} (${comparison['most_expensive_cost']:.6f})")
    print(f"💡 Max Savings: {comparison['max_savings_percentage']:.1f}%")

def format_usage_stats(stats):
    """Format usage statistics in table format"""
    print("📊 Usage Statistics")
    print("=" * 60)
    print(f"Period: {stats['period']['days']} days ({stats['period']['start_date']} to {stats['period']['end_date']})")
    print()
    
    # Totals
    totals = stats['totals']
    print("📈 Summary:")
    print(f"  Total Queries: {totals['queries']}")
    print(f"  Total Tokens:  {totals['tokens']:,}")
    print(f"  Total Cost:    ${totals['cost']:.4f}")
    print(f"  Avg per Query: ${totals['avg_cost_per_query']:.4f}")
    print()
    
    # Provider breakdown
    if stats['provider_breakdown']:
        print("🏢 By Provider:")
        print(f"{'Provider':<12} {'Queries':<8} {'Tokens':<10} {'Cost':<10} {'Avg Response'}")
        print("-" * 55)
        for provider in stats['provider_breakdown']:
            tokens_str = f"{provider['tokens']:,}" if provider['tokens'] else "0"
            cost_str = f"${provider['cost']:.4f}"
            response_str = f"{provider['avg_response_time_ms']:.0f}ms"
            print(f"{provider['provider']:<12} {provider['queries']:<8} {tokens_str:<10} {cost_str:<10} {response_str}")

def format_cost_analysis(analysis):
    """Format cost analysis in table format"""
    print("💡 Cost Analysis & Optimization")
    print("=" * 50)
    
    # Current spend
    spend = analysis.get('current_spend', {})
    print(f"📊 Current Spend: ${spend.get('monthly_total', 0):.2f}/month")
    print(f"🏆 Cheapest Provider: {spend.get('cheapest_provider', 'N/A')}")
    print(f"💸 Most Expensive: {spend.get('most_expensive_provider', 'N/A')}")
    print()
    
    # Optimization opportunities
    opt = analysis.get('optimization_opportunities', {})
    print("💰 Optimization Opportunities:")
    print(f"  Provider Savings:    ${opt.get('potential_provider_savings', 0):.2f}")
    print(f"  Cache Savings Est:   ${opt.get('cache_savings_estimate', 0):.2f}")
    print(f"  Cache Hit Rate:      {opt.get('overall_cache_hit_rate', 0)*100:.1f}%")
    print()
    
    # Recommendations
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        print("🎯 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

print("=== V4.0.0 Features Testing ===\n")

# Check if API key exists
api_key_available = bool(os.getenv('ANTHROPIC_API_KEY'))
print(f"API Key Available: {api_key_available}")

if not api_key_available:
    print("⚠️  No ANTHROPIC_API_KEY found. Set it with: export ANTHROPIC_API_KEY=your_key")
    print("Some tests will show 'None' without real queries.\n")

##P1 - Real-time Provider Cost Comparison
print("1. 📊 Real-time Provider Cost Comparison")
try:
    client = LLMClient(provider="anthropic", analytics_enabled=True)
    comparison = client.get_provider_comparison(input_tokens=500, output_tokens=300)
    format_provider_comparison(comparison)
except Exception as e:
    print(f"Error: {e}")
print("\n" + "="*50 + "\n")

##P2 - Post-query Actual Cost Tracking
print("2. 💰 Post-query Actual Cost Tracking")
if api_key_available:
    try:
        client = LLMClient(provider="anthropic", analytics_enabled=True)
        response = client.query("Explain IBM PowerVC in 500 words")
        print(f"Response: {response.content[:600]}...")
        cost_data = client.get_cost_breakdown()
        if cost_data:
            format_cost_analysis(cost_data)
        else:
            print("Cost data: None (database might be empty)")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("⚠️  Skipped - requires API key for real query")
print("\n" + "="*50 + "\n")

## P3 - Usage Statistics Tracking  
print("3. 📈 Usage Statistics Tracking")
if api_key_available:
    try:
        client = LLMClient(provider="anthropic", analytics_enabled=True)
        # Make multiple queries to populate analytics
        client.query("What is AI?")
        client.query("Explain ML?") 
        client.query("Define deep learning?")
        stats = client.get_usage_stats()
        if stats:
            format_usage_stats(stats)
        else:
            print("Usage stats: None (database might be empty)")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("⚠️  Skipped - requires API key for real queries")
print("\n" + "="*50 + "\n")

##P4 - Monthly Cost Estimation
print("4. 📅 Monthly Cost Estimation")
try:
    estimator = CostEstimator()
    monthly = estimator.estimate_monthly_cost(
        daily_queries=10,
        avg_input_tokens=300,
        avg_output_tokens=200,
        provider="anthropic",
        model="claude-3-5-sonnet"
    )
    print("📅 Monthly Cost Estimation")
    print("=" * 40)
    print(f"📊 Usage Pattern:")
    print(f"  Daily Queries:     {monthly['daily_queries']}")
    print(f"  Avg Tokens/Query:  {monthly['avg_tokens_per_query']}")
    print()
    print(f"💰 Cost Breakdown:")
    print(f"  Cost per Query:    ${monthly['cost_per_query']:.6f}")
    print(f"  Daily Cost:        ${monthly['daily_cost']:.2f}")
    print(f"  Monthly Cost:      ${monthly['monthly_cost']:.2f}")
    print()
    print(f"🏢 Provider: {monthly['provider']} ({monthly['breakdown']['model']})")
    print(f"📈 Confidence: {monthly['breakdown']['confidence']}")
except Exception as e:
    print(f"Error: {e}")
print("\n" + "="*50 + "\n")

##P5 - Pricing Confidence Indicators
print("5. ✅ Pricing Confidence Indicators")
try:
    estimator = CostEstimator()
    confidence = estimator.get_pricing_confidence()
    print("=" * 35)
    print(f"📊 Overall Confidence: {confidence['confidence'].upper()}")
    print(f"📅 Last Updated: {confidence.get('last_updated', 'Unknown')[:10]}")
    print(f"⏰ Data Age: {confidence.get('age_days', 'Unknown')} days")
    print(f"💬 Status: {confidence.get('message', 'No message')}")
    
    if confidence['confidence'] == 'high':
        print("✅ Pricing data is current and reliable")
    elif confidence['confidence'] == 'medium':
        print("⚠️  Pricing data may need updating soon") 
    else:
        print("❌ Pricing data is outdated - results may be inaccurate")
except Exception as e:
    print(f"Error: {e}")
print("\n" + "="*50 + "\n")

###P6 - Historical Price Change Tracking
print("6. 📉 Historical Price Change Tracking")
try:
    estimator = CostEstimator()
    old_price = {"input": 0.003, "output": 0.015}
    new_price = {"input": 0.003, "output": 0.012}
    change = estimator.track_price_change("anthropic", "claude-3-5-sonnet", old_price, new_price)
    print("📉 Historical Price Change Tracking")
    print("=" * 40)
    print(f"🏢 Provider: {change['provider']}")
    print(f"🤖 Model: {change['model']}")
    print(f"📅 Change Date: {change['change_date'][:10]}")
    print()
    print("💰 Price Changes:")
    print(f"  Input Price:  ${change['old_price']['input']:.6f} → ${change['new_price']['input']:.6f} ({change['change_percentage']['input']:+.1f}%)")
    print(f"  Output Price: ${change['old_price']['output']:.6f} → ${change['new_price']['output']:.6f} ({change['change_percentage']['output']:+.1f}%)")
    
    output_change = change['change_percentage']['output']
    if output_change < 0:
        print(f"📉 Price decreased by {abs(output_change):.1f}% - Cost savings available!")
    elif output_change > 0:
        print(f"📈 Price increased by {output_change:.1f}% - Budget impact expected")
    else:
        print("➡️  No price change detected")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Testing Complete ===")
print("Note: Features 2 & 3 need real API queries to populate analytics database.")





