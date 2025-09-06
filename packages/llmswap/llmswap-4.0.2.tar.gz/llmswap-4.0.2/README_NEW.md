# llmswap - Complete AI CLI Suite + Python SDK

[![PyPI version](https://badge.fury.io/py/llmswap.svg)](https://badge.fury.io/py/llmswap)
[![pip install llmswap](https://img.shields.io/badge/pip%20install-llmswap-brightgreen)](https://pypi.org/project/llmswap/)
[![PyPI Downloads](https://static.pepy.tech/badge/llmswap)](https://pepy.tech/projects/llmswap)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Two Powerful Interfaces: 5 AI CLI Tools + Complete Python SDK**

## 🚀 Terminal AI Suite - No Browser Required

```bash
# Install once, get 5 AI CLI tools
pip install llmswap

# 1. One-line AI assistant
llmswap ask "How to optimize PostgreSQL queries?"

# 2. Interactive AI chat  
llmswap chat

# 3. AI code reviewer
llmswap review app.py --focus security

# 4. AI debugger
llmswap debug --error "ConnectionTimeout: Connection timed out"

# 5. AI log analyzer
llmswap logs --analyze /var/log/app.log --since "2h ago"
```

## 📦 Python SDK for Applications

```python
pip install llmswap
from llmswap import LLMClient

client = LLMClient()  # Auto-detects OpenAI, Claude, Gemini, etc.
response = client.query("Analyze this data trend")
print(response.content)
```

**Complete AI-powered development workflow in your terminal + Python library for applications**

---

## CLI vs Python SDK - Which Should You Use?

| Use Case | CLI | Python SDK |
|----------|-----|------------|
| Quick terminal questions | ✅ `llmswap ask "question"` | ❌ |
| Interactive debugging sessions | ✅ `llmswap chat` | ❌ |
| Shell scripting/automation | ✅ Bash/Shell integration | ❌ |
| Code review from terminal | ✅ `llmswap review file.py` | ❌ |
| CI/CD pipelines | ✅ Direct CLI commands | ✅ Python scripts |
| Building applications | ❌ | ✅ Import and integrate |
| Jupyter notebooks | ❌ | ✅ Import library |
| Web applications | ❌ | ✅ Flask/Django integration |
| Programmatic control | ❌ | ✅ Full API access |
| Async operations | ❌ | ✅ AsyncLLMClient |

---

## 🖥️ CLI Tools - Terminal AI for Developers

### Installation & Setup
```bash
# Install CLI suite
pip install llmswap

# Set API key (choose any one)
export ANTHROPIC_API_KEY="your-key"     # Claude
export OPENAI_API_KEY="your-key"       # GPT-4
export GEMINI_API_KEY="your-key"       # Gemini
# Or use free local models with Ollama (no API key needed)

# Verify installation
llmswap --version
```

### 1. One-Line AI Assistant - `llmswap ask`

Get answers instantly without leaving your terminal:

```bash
# Quick questions - no setup, no context switching
llmswap ask "What is the difference between GET and POST?"
llmswap ask "How to handle exceptions in Python?"
llmswap ask "Best way to optimize database queries?"
llmswap ask "How to fix Docker permission denied error?"

# Works with any development question
llmswap ask "Explain microservices architecture"
llmswap ask "What are JWT tokens and how do they work?"
llmswap ask "How to implement rate limiting in API?"

# Use specific provider
llmswap ask "Optimize this SQL query" --provider claude
llmswap ask "Debug JavaScript error" --provider openai
```

**Perfect for:**
- Quick lookups during coding
- Learning new concepts on-the-fly
- Replacing StackOverflow searches
- Getting instant explanations
- No browser context switching required

### 2. Interactive Terminal AI Chat - `llmswap chat`

When you need more than one-line answers:

```bash
# Start interactive AI session
$ llmswap chat

You: I'm getting a weird error in my React app
AI: I'd be happy to help! Can you share the error message?
You: TypeError: Cannot read property 'map' of undefined
AI: This usually happens when you're trying to map over data that hasn't loaded yet...
You: How do I fix it?
AI: Here are 3 approaches: 1) Add loading state, 2) Use optional chaining...
You: Show me the code for approach 1
AI: Here's how to implement loading state:
```

**Features:**
- Full conversation context maintained
- Follow-up questions and clarifications
- Code examples and explanations
- Problem-solving sessions
- Learning conversations
- Exit with `quit` or `Ctrl+C`

### 3. AI Code Reviewer - `llmswap review`

Professional code review from command line:

```bash
# Security scan from terminal
llmswap review app.py --focus security
# Output:
# ⚠️ Line 23: SQL injection risk - use parameterized queries
# ⚠️ Line 45: Hardcoded API key - use environment variables
# ✅ Input validation properly implemented

# Bug detection
llmswap review script.js --focus bugs
llmswap review main.go --focus performance
llmswap review *.py --focus style

# Review focus areas
--focus security    # Security vulnerabilities
--focus bugs        # Logic errors and bugs  
--focus performance # Performance issues
--focus style       # Code style and readability
--focus general     # Overall code review
```

**Features:**
- Terminal-native code analysis
- Security vulnerability detection
- Bug pattern recognition  
- Performance optimization suggestions
- Style and readability improvements
- CI/CD pipeline ready

### 4. AI Debugger - `llmswap debug`

Transform error messages into solutions instantly:

```bash
# Debug specific errors
llmswap debug --error "IndexError: list index out of range"
llmswap debug --error "ConnectionRefusedError: [Errno 111] Connection refused"
llmswap debug --error "TypeError: 'NoneType' object is not callable"

# Real production errors
llmswap debug --error "QueuePool limit of size 30 overflow 100 reached"
# Output:
# Database connection pool exhausted. Common causes:
# 1. Connection leak - not closing connections properly
# 2. Pool size too small for traffic
# 3. Long-running queries blocking connections
# Quick fix: Increase pool_size and max_overflow
# Code: create_engine(url, pool_size=50, max_overflow=150)

# Pipe errors directly
python app.py 2>&1 | llmswap debug --error
```

**Features:**
- Instant error analysis from terminal
- No context switching to browser/docs
- Copy-paste error messages for instant solutions
- Integration with shell pipelines
- Real-world error patterns recognized

### 5. AI Log Analyzer - `llmswap logs`

Make sense of logs without grep/awk complexity:

```bash
# Analyze production logs
llmswap logs --analyze /var/log/app.log --since "2h ago"
# Output:
# Critical: 47 database timeout errors (10:15-10:18 AM)
# Pattern: Errors correlate with backup job schedule  
# Recommendation: Adjust backup timing or add connection pooling

# Analyze recent entries
llmswap logs --analyze app.log --last 1000
llmswap logs --analyze error.log --since "1h ago"

# Real-time log monitoring
tail -f app.log | llmswap logs --analyze
```

**Features:**
- Pattern recognition in log files
- Error correlation analysis
- Actionable recommendations
- Time-based filtering
- Real-time log stream analysis

### Complete CLI Workflow Example

Real developer day using all CLI features:

```bash
# Morning: Quick question about new feature
llmswap ask "How to implement WebSocket authentication?"

# Code the feature, then review it
llmswap review websocket_auth.py --focus security

# Hit an error during testing
llmswap debug --error "WebSocket connection failed: 403 Forbidden"

# Check logs for patterns
llmswap logs --analyze /var/log/app.log --since "1h ago"

# Need detailed help? Start conversation
llmswap chat
You: I'm implementing WebSocket auth but getting 403 errors...
AI: Let's troubleshoot this step by step...
```

### DevOps & Automation Examples

```bash
# CI/CD Integration
for file in src/*.py; do
    llmswap review "$file" --focus security --quiet
done

# Daily log analysis
llmswap logs --analyze /var/log/nginx/error.log --since "24h ago"

# Quick production debugging
llmswap debug --error "$(tail -1 /var/log/app.log)"

# Shell aliases for productivity
alias ai="llmswap ask"
alias debug="llmswap debug --error"
alias review="llmswap review"

# Usage
ai "How to restart nginx service?"
debug "$(docker logs myapp 2>&1 | tail -1)"
review app.py --focus bugs
```

---

## 🐍 Python SDK - AI Library for Applications

### Installation & Setup
```bash
pip install llmswap
```

### Quick Start
```python
from llmswap import LLMClient

# Auto-detects available provider
client = LLMClient()
response = client.query("What is Python?")
print(response.content)
```

### API Key Configuration
```bash
# Set API keys (choose any one)
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"  
export GEMINI_API_KEY="your-gemini-key"
export WATSONX_API_KEY="your-ibm-key"
export WATSONX_PROJECT_ID="your-project-id"
# Or run Ollama locally for free models
```

### Multi-Provider Support

```python
# Auto-detection (uses first available)
client = LLMClient()

# Specify provider
client = LLMClient(provider="anthropic")
client = LLMClient(provider="openai") 
client = LLMClient(provider="gemini")
client = LLMClient(provider="watsonx")
client = LLMClient(provider="ollama")  # Local models

# Custom models
client = LLMClient(provider="openai", model="gpt-4")
client = LLMClient(provider="anthropic", model="claude-3-opus-20240229")
```

### Response Caching - Save 50-90% on API Costs

**What is Response Caching?**  
Intelligent caching stores LLM responses temporarily to avoid repeated expensive API calls for identical queries.

**Default State:** DISABLED (for security in multi-user environments)

**Key Benefits:**
- **Massive cost savings:** 50-90% reduction in API costs
- **Lightning speed:** 100,000x+ faster responses (0.001s vs 1-3s)
- **Rate limit protection:** Avoid hitting API limits
- **Reliability:** Serve cached responses even if API is down

#### Basic Caching Usage

```python
from llmswap import LLMClient

# Enable caching (disabled by default)
client = LLMClient(cache_enabled=True)

# First call: hits API and costs money
response = client.query("What is machine learning?")
print(f"From cache: {response.from_cache}")  # False

# Identical call: returns from cache (FREE!)
response = client.query("What is machine learning?")  
print(f"From cache: {response.from_cache}")  # True
```

#### Advanced Caching Configuration

```python
# Customize cache behavior
client = LLMClient(
    cache_enabled=True,
    cache_ttl=3600,        # 1 hour expiry
    cache_max_size_mb=50   # Memory limit
)

# Multi-user security: separate cache per user
response = client.query(
    "Show my account balance",
    cache_context={"user_id": "user123"}
)

# Per-query settings
response = client.query(
    "Current weather",
    cache_ttl=300,         # 5 minutes for weather
    cache_bypass=True      # Force fresh API call
)

# Monitor performance
stats = client.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']}%")
print(f"Cost savings: ~{stats['hit_rate']}%")
```

#### When to Use Caching

**✅ Good Use Cases:**
- Single-user applications
- Public/educational content queries  
- FAQ bots and documentation assistants
- Development and testing (save API costs)
- Repeated queries during development

**❌ Avoid When:**
- Multi-user apps without context isolation
- Real-time data queries (stock prices, weather)
- Personalized responses without user context

### Async Support & Streaming

```python
import asyncio
from llmswap import AsyncLLMClient

async def main():
    client = AsyncLLMClient(provider="openai")
    
    # Async query
    response = await client.query("Explain quantum computing")
    print(response.content)
    
    # Streaming response
    print("Streaming: ", end="")
    async for chunk in client.stream("Write a haiku"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

### Provider Auto-Detection & Fallback

```python
# Auto-detection
client = LLMClient()
print(f"Using: {client.get_current_provider()}")

# Automatic fallback when provider fails
client = LLMClient(fallback=True)
response = client.query("Hello world")
print(f"Succeeded with: {response.provider}")

# Check available providers
available = client.list_available_providers()
print(f"Available: {available}")
```

### Application Integration Examples

#### Building a Chatbot
```python
from llmswap import LLMClient

class SimpleChatbot:
    def __init__(self):
        self.llm = LLMClient(cache_enabled=True)
        
    def chat(self, message, user_id=None):
        cache_context = {"user_id": user_id} if user_id else None
        response = self.llm.query(
            f"User: {message}\\nAssistant:",
            cache_context=cache_context
        )
        return response.content
        
    def get_provider(self):
        return f"Using {self.llm.get_current_provider()}"

# Usage
bot = SimpleChatbot()
print(bot.chat("Hello!", user_id="user123"))
```

#### Web Application Integration
```python
from flask import Flask, request, jsonify
from llmswap import LLMClient

app = Flask(__name__)
client = LLMClient(cache_enabled=True)

@app.route('/api/ask', methods=['POST'])
def ask_ai():
    data = request.get_json()
    question = data.get('question')
    user_id = data.get('user_id')
    
    response = client.query(
        question,
        cache_context={"user_id": user_id}
    )
    
    return jsonify({
        'answer': response.content,
        'provider': response.provider,
        'cached': response.from_cache
    })
```

---

## 🌟 Supported Providers & Models

| Provider | Models | Setup |
|----------|---------|-------|
| **Anthropic** | Claude 3.5 (Sonnet, Haiku, Opus) | `export ANTHROPIC_API_KEY=...` |
| **OpenAI** | GPT-3.5, GPT-4, GPT-4o | `export OPENAI_API_KEY=...` |
| **Google** | Gemini 1.5 (Flash, Pro) | `export GEMINI_API_KEY=...` |
| **IBM watsonx** | Granite, Llama, foundation models | `export WATSONX_API_KEY=...` |
| **Ollama** | 100+ local models (FREE) | Run Ollama locally |

### Free Local Models with Ollama

No API keys needed - run AI models locally:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull popular models
ollama pull llama3.2        # Meta's latest
ollama pull mistral         # Mistral 7B
ollama pull qwen2.5-coder   # Code specialist
ollama pull phi3            # Microsoft's efficient model

# Use with llmswap
llmswap ask "Explain Python" --provider ollama
```

```python
# Python usage with local models
client = LLMClient(provider="ollama", model="llama3.2")
response = client.query("What is machine learning?")
```

**Popular Ollama Models:**
- `llama3.2` (1B, 3B, 8B) - Meta's latest
- `mistral` (7B) - Fast and capable
- `qwen2.5-coder` (7B) - Code specialist
- `phi3` (3.8B) - Microsoft's efficient model
- `gemma2` (2B, 9B) - Google's open model

### Enterprise Models with IBM watsonx

```python
# Set environment variables
# export WATSONX_API_KEY="your-ibm-cloud-api-key"
# export WATSONX_PROJECT_ID="your-project-id"

client = LLMClient(provider="watsonx")
client = LLMClient(provider="watsonx", model="ibm/granite-3-8b-instruct")

# Popular watsonx models
client = LLMClient(provider="watsonx", model="meta-llama/llama-3-70b-instruct")
client = LLMClient(provider="watsonx", model="mistralai/mixtral-8x7b-instruct-v01")
```

---

## 💡 Real-World Examples & Use Cases

### CLI Examples - Terminal Workflows

#### Daily Developer Workflow
```bash
# Morning: Check last night's errors
llmswap logs --analyze overnight.log

# Code review before commit
llmswap review changes.py --focus security

# Debug production issue
llmswap debug --error "$(tail -1 error.log)"

# Get quick help
llmswap ask "How to optimize PostgreSQL query"

# Interactive problem solving
llmswap chat
```

#### CI/CD Integration
```yaml
# GitHub Actions
- name: AI Code Review
  run: |
    pip install llmswap
    llmswap review src/*.py --focus security --quiet
```

#### Shell Automation
```bash
#!/bin/bash
# Smart deployment script

# Pre-deployment checks
echo "Running AI code review..."
llmswap review app.py --focus bugs --quiet

if [ $? -eq 0 ]; then
    echo "Code review passed, deploying..."
    ./deploy.sh
else
    echo "Code review failed, fixing issues..."
    llmswap review app.py --focus bugs
fi
```

### Python SDK Examples - Application Development

#### AI-Powered Code Assistant
```python
from llmswap import LLMClient

class AICodeAssistant:
    def __init__(self):
        self.client = LLMClient(cache_enabled=True)
    
    def review_code(self, code, focus="general"):
        prompt = f"Review this code for {focus}: {code}"
        response = self.client.query(prompt)
        return response.content
    
    def debug_error(self, error_msg):
        prompt = f"Debug this error: {error_msg}"
        response = self.client.query(prompt)
        return response.content
    
    def suggest_optimization(self, code):
        prompt = f"Suggest optimizations for: {code}"
        response = self.client.query(prompt)
        return response.content

# Usage
assistant = AICodeAssistant()
review = assistant.review_code(source_code, focus="security")
debug_help = assistant.debug_error("IndexError: list index out of range")
```

#### Multi-User Application with Caching
```python
from llmswap import LLMClient

class AIHelpDesk:
    def __init__(self):
        self.client = LLMClient(
            cache_enabled=True,
            cache_ttl=3600  # 1 hour cache
        )
    
    def answer_question(self, question, user_id, category="general"):
        # Cache per user and category
        cache_context = {
            "user_id": user_id,
            "category": category
        }
        
        response = self.client.query(
            f"Answer this {category} question: {question}",
            cache_context=cache_context
        )
        
        return {
            "answer": response.content,
            "cached": response.from_cache,
            "provider": response.provider
        }

# Usage
helpdesk = AIHelpDesk()
result = helpdesk.answer_question(
    "How to reset password?", 
    user_id="user123", 
    category="support"
)
```

---

## 🚀 Perfect for Hackathons & Students

**Built from hackathon experience to help developers ship faster:**

### Why llmswap for Hackathons?

- **⚡ Move Fast** - One line setup, focus on your idea not infrastructure
- **💰 Stay Within Budget** - Caching saves API costs, free local models available
- **🔄 Experiment Freely** - Switch between providers instantly, find what works
- **📈 Scale Easily** - Start with free tiers, upgrade when needed
- **👥 Multi-User Ready** - Build apps that serve your whole team/class
- **🎯 Learn Best Practices** - Production-ready patterns from day one

### Hackathon Starter Template

```python
# Perfect hackathon starter - works with any API key you have
from llmswap import LLMClient

# Enable caching to save money from day 1
client = LLMClient(cache_enabled=True)

# Build your idea - switching providers is easy
response = client.query("Help me build an AI-powered app")
print(response.content)

# If one provider is down, try another
client.set_provider("anthropic")  # or "openai", "gemini", "ollama"
```

### Student Examples

```bash
# Free local development (no API costs)
llmswap ask "Explain this algorithm" --provider ollama

# When you need better quality for final project
llmswap ask "Professional explanation of machine learning" --provider claude

# Get coding help
llmswap review homework.py --focus bugs
llmswap debug --error "Your error message here"
```

---

## 📋 Migration & Integration Guide

### From Direct Provider Usage

```python
# BEFORE: Direct OpenAI usage
import openai
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
content = response.choices[0].message.content

# AFTER: llmswap (works with any provider!)
from llmswap import LLMClient
client = LLMClient()
response = client.query("Hello")
content = response.content
```

### From LangChain

```python
# BEFORE: LangChain complexity
from langchain.llms import OpenAI
from langchain.schema import HumanMessage

llm = OpenAI(temperature=0.9)
messages = [HumanMessage(content="Hello")]
response = llm(messages)

# AFTER: llmswap simplicity
from llmswap import LLMClient
client = LLMClient()
response = client.query("Hello")
```

---

## 🔧 Configuration & Advanced Usage

### Environment Variables
```bash
# API Keys (set at least one)
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"

# IBM watsonx (enterprise models)
export WATSONX_API_KEY="your-ibm-cloud-api-key"
export WATSONX_PROJECT_ID="your-watsonx-project-id"

# Ollama (if using local models)
export OLLAMA_URL="http://localhost:11434"  # default
```

### Programmatic Configuration
```python
# Custom configuration
client = LLMClient(
    provider="anthropic",
    api_key="your-key-here",
    model="claude-3-opus-20240229",
    cache_enabled=True,
    cache_ttl=1800,
    fallback=True
)
```

### Response Details
```python
response = client.query("What is OpenStack?")

print(f"Content: {response.content}")
print(f"Provider: {response.provider}")
print(f"Model: {response.model}")
print(f"From cache: {response.from_cache}")
print(f"Created: {response.created_at}")
```

---

## 🏗️ Project Information

### Requirements
- Python 3.8 or higher
- At least one API key (Anthropic, OpenAI, Google, IBM) OR Ollama for local models

### Installation
```bash
pip install llmswap
```

### Development Setup
```bash
git clone https://github.com/sreenathmmenon/llmswap
cd llmswap
pip install -e .
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **GitHub**: https://github.com/sreenathmmenon/llmswap
- **PyPI**: https://pypi.org/project/llmswap/
- **Issues**: https://github.com/sreenathmmenon/llmswap/issues

---

## ❓ FAQ

**Q: Is llmswap a CLI tool or Python library?**  
A: **Both!** Install once, use both ways:
- CLI: `llmswap ask "question"` in terminal
- Python: `from llmswap import LLMClient` in code

**Q: Do I need to write Python code to use llmswap?**  
A: **No!** The CLI works standalone in terminal without any Python code.

**Q: Can I use llmswap in bash scripts?**  
A: **Yes!** The CLI is perfect for shell scripting and automation.

**Q: Which interface should I use?**  
A: Use CLI for terminal/DevOps work, Python SDK for building applications.

**Q: Does caching work across different providers?**  
A: No, cache keys include the provider, so switching providers will create new cache entries.

**Q: Is it safe to use caching in production?**  
A: Yes, but ensure you use `cache_context` for user isolation in multi-user applications.

---

**Transform your development workflow with AI. Terminal tools for instant productivity. Python SDK for powerful applications.**

*Star this repo if llmswap helps simplify your AI integration.*