#!/usr/bin/env python3
"""
Better cost estimation for llmswap that scales with query complexity.
"""

from llmswap import LLMClient

class BetterEstimator:
    """Improved cost estimation based on query patterns."""
    
    @staticmethod
    def estimate_output_tokens(query: str, input_tokens: int) -> int:
        """Estimate output tokens based on query type and complexity."""
        
        query_lower = query.lower()
        
        # Greetings and simple acknowledgments
        if any(word in query_lower for word in ['hi', 'hello', 'thanks', 'bye']):
            return 20
        
        # Simple questions
        elif query_lower.startswith('what is') and len(query) < 30:
            return 200
        
        # Explanations
        elif 'explain' in query_lower:
            if 'simple' in query_lower or 'brief' in query_lower:
                return 300
            else:
                return 800
        
        # Lists and enumerations
        elif any(word in query_lower for word in ['list', 'enumerate', 'name all']):
            return 300
        
        # Code generation
        elif any(word in query_lower for word in ['code', 'write', 'create', 'implement']):
            if 'example' in query_lower or 'simple' in query_lower:
                return 500
            elif 'full' in query_lower or 'complete' in query_lower:
                return 5000
            else:
                return 1500
        
        # Documentation and architecture
        elif any(word in query_lower for word in ['architecture', 'documentation', 'design']):
            if 'full' in query_lower or 'complete' in query_lower:
                return 10000  # These can be HUGE
            else:
                return 2000
        
        # Complex analysis
        elif any(word in query_lower for word in ['analyze', 'compare', 'evaluate']):
            return 1000
        
        # Default: scale with input length
        else:
            # Longer questions usually get longer answers
            if input_tokens < 5:
                return 100
            elif input_tokens < 20:
                return input_tokens * 30
            elif input_tokens < 50:
                return input_tokens * 50
            else:
                return input_tokens * 100

def test_better_estimation():
    """Test the improved estimation."""
    
    client = LLMClient(provider="anthropic", analytics_enabled=True)
    estimator = BetterEstimator()
    
    questions = [
        "Hi",
        "What is IBM Power?",
        "Explain machine learning",
        "Create a On premise cloud in go similar to OpenStack",
        "Generate full architectural diagram and code flow and design doc of Openstack nova code base"
    ]
    
    print("BETTER COST ESTIMATION")
    print("="*60)
    
    for q in questions:
        # Get current (bad) estimate
        current_estimate = client.estimate_query_cost(q)
        current_cost = current_estimate.get('total_cost', 0)
        
        # Calculate better estimate
        input_tokens = current_estimate.get('input_tokens', 0)
        better_output_tokens = estimator.estimate_output_tokens(q, input_tokens)
        
        # Calculate costs (using Anthropic Claude pricing)
        input_cost = input_tokens * 0.003 / 1000
        output_cost = better_output_tokens * 0.015 / 1000
        better_total = input_cost + output_cost
        
        print(f"\nQuestion: '{q[:40]}...'")
        print(f"  Current estimate: ${current_cost:.6f} (WRONG - always ~100 tokens)")
        print(f"  Better estimate:  ${better_total:.6f} ({better_output_tokens} output tokens)")
        print(f"  Difference:       {(better_total/current_cost - 1)*100:+.0f}%")

if __name__ == "__main__":
    test_better_estimation()