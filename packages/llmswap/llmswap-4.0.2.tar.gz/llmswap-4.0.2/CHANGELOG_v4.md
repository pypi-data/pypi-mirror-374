# Changelog

## [4.0.2] - 2025-09-05

### 🚀 **NEW PROVIDER: Groq Integration**

#### **Ultra-Fast Inference**
- **Groq Provider**: Complete integration with Groq's high-performance LPU inference
- **Models Supported**: llama-3.1-8b-instant, llama-3.3-70b-versatile, gpt-oss-20b
- **Speed**: Up to 840+ tokens/second (5-15x faster than other providers)
- **Cost-Effective**: Starting at $0.05/$0.08 per million tokens

#### **Enhanced Features**
- **Provider Priority**: Groq added to auto-detection and fallback chain
- **Cost Analytics**: Groq pricing integrated into cost comparison tools
- **CLI Support**: Full compatibility with all existing CLI commands
- **SDK Integration**: Seamless switching with `LLMClient(provider="groq")`

### 🔧 **Improvements**
- **SEO Optimization**: Enhanced discoverability with strategic keywords
- **Documentation**: Updated setup instructions and provider examples
- **Dependency Management**: Added groq>=0.4.0 for reliable API access

---

## [4.0.0] - 2025-09-04

### 🎉 Major Release: Analytics & Cost Optimization Suite

### ✨ **NEW FEATURES**

#### **Cost Analytics & Optimization**
- **Provider Cost Comparison**: Compare real-time costs across OpenAI, Claude, Gemini, watsonx, and Ollama
- **Usage Tracking**: Detailed analytics on queries, tokens, costs, and response times
- **Cost Optimization**: AI-powered recommendations to reduce API spending by 50-90%
- **Monthly Cost Estimation**: Budget planning with realistic usage patterns

#### **Enhanced CLI Tools**
- `llmswap compare --input-tokens X --output-tokens Y` - Compare provider costs
- `llmswap usage --days N` - View usage statistics and trends
- `llmswap costs` - Get personalized cost optimization insights

#### **Python SDK Analytics**
- `client.get_usage_stats()` - Comprehensive usage analytics
- `client.get_cost_breakdown()` - Detailed cost analysis with optimization suggestions
- `client.get_provider_comparison()` - Real-time provider cost comparison
- `client.chat()` - Conversation memory for contextual interactions

#### **New Provider Support**
- **Enhanced watsonx Integration**: Full IBM watsonx.ai support with Granite models
- **Expanded Ollama Support**: 100+ local models including Llama, Mistral, Phi, Qwen
- **Groq Integration**: High-performance inference ✅ COMPLETED in v4.0.2

### 🔧 **IMPROVEMENTS**

#### **Performance & Reliability**
- **Advanced Token Tracking**: Accurate token counting across all providers
- **Database Optimization**: SQLite-based analytics with privacy-first design
- **Error Handling**: Improved error messages and debugging information

#### **Developer Experience**
- **Conversation Context**: Automatic conversation memory in chat mode
- **Better Examples**: Practical use cases for enterprise, education, and startups
- **Enhanced Documentation**: Token usage guidelines and cost optimization tips

#### **Security & Privacy**
- **Privacy-First Analytics**: Query content never stored, only metadata
- **Multi-User Context**: Secure caching with user isolation
- **Local Model Support**: Complete privacy with Ollama integration

### 📊 **ANALYTICS FEATURES**

#### **Cost Tracking**
- Real-time cost calculation from API responses
- Historical cost trends and analysis
- Provider cost comparison with savings recommendations
- ROI analysis for caching and provider switching

#### **Usage Insights**
- Query patterns and frequency analysis
- Token usage optimization suggestions
- Response time monitoring across providers
- Cache hit rate and cost savings metrics

#### **Optimization Recommendations**
- Automatic provider switching suggestions
- Caching strategy recommendations
- Token usage optimization tips
- Budget planning and cost forecasting

### 🏢 **USE CASE EXAMPLES**

#### **Enterprise**
- Netflix-scale content generation with 96% cost savings
- Multi-provider strategies for high availability
- Compliance-ready solutions with local models

#### **Developers**
- GitHub Copilot alternative with team cost tracking
- CI/CD integration with usage analytics
- Development workflow optimization

#### **Education**
- Khan Academy-style AI tutoring with free Ollama
- Scalable learning platforms with cost control
- Student project support with budget management

### 🔄 **MIGRATION FROM v3.x**

Fully backward compatible! No breaking changes.

#### **New Optional Features**
```python
# Enable analytics (optional)
client = LLMClient(analytics_enabled=True)

# Use conversation memory (optional)
response = client.chat("Hello")  # New method alongside query()

# Access new analytics methods
stats = client.get_usage_stats()
analysis = client.get_cost_breakdown()
```

#### **New CLI Commands**
```bash
# All existing commands work unchanged
llmswap ask "Hello"  # Still works
llmswap chat         # Still works

# New analytics commands
llmswap compare --input-tokens 1000 --output-tokens 500
llmswap usage --days 30
llmswap costs
```

### 📦 **Package Updates**
- **Keywords**: Optimized PyPI keywords for better discoverability
- **Description**: Enhanced positioning vs LangChain and LiteLLM
- **Documentation**: Comprehensive use cases and examples

### 🐛 **BUG FIXES**
- Fixed token tracking across all providers
- Resolved database corruption issues in analytics
- Improved error handling for API failures
- Fixed import errors in metrics modules

---

## [3.2.1] - Previous Release
- Response caching features
- Multi-provider support
- CLI tool suite
- Async/streaming support

**Full Changelog**: [View on GitHub](https://github.com/sreenathmmenon/llmswap/compare/v3.2.1...v4.0.0)