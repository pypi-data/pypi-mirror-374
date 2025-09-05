# llmswap v4.0.0 CLI Testing Commands

## Setup
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
cd /path/to/llmswap
```

## 1. Basic CLI Commands

### Help & Version
```bash
python -m llmswap --help
python -m llmswap --version
```

### Ask Command (Quick queries)
```bash
python -m llmswap ask "What is Python?"
python -m llmswap ask "Explain recursion in simple terms"
python -m llmswap ask "What are the top 5 Python frameworks?"
```

### Interactive Chat
```bash
python -m llmswap chat
# In chat mode, try:
# > Hello, I'm building a web API
# > What's the best Python framework?
# > Show me a FastAPI example
# > quit
```

## 2. Code Review Features

### Create a test file first:
```bash
cat > sample_code.py << 'EOF'
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total

def find_maximum(items):
    max_val = items[0]
    for item in items:
        if item > max_val:
            max_val = item
    return max_val

data = [1, 2, 3, 4, 5]
result = calculate_sum(data)
maximum = find_maximum(data)
print(f"Sum: {result}, Max: {maximum}")
EOF
```

### Review with different focus areas:
```bash
python -m llmswap review sample_code.py --focus general
python -m llmswap review sample_code.py --focus performance
python -m llmswap review sample_code.py --focus security
python -m llmswap review sample_code.py --focus bugs
```

## 3. Debug Command

### Common Python errors:
```bash
python -m llmswap debug --error "TypeError: 'int' object is not subscriptable"
python -m llmswap debug --error "IndexError: list index out of range"
python -m llmswap debug --error "KeyError: 'missing_key'"
python -m llmswap debug --error "AttributeError: 'NoneType' object has no attribute 'split'"
```

## 4. Advanced Log Analysis

### Create sample log files:
```bash
# Create sample application log
cat > app.log << 'EOF'
2024-01-17 10:30:15 INFO  [main] Application starting
2024-01-17 10:30:16 INFO  [database] Connected to PostgreSQL
2024-01-17 10:30:20 ERROR [auth] Login failed for user: admin
2024-01-17 10:30:25 WARN  [cache] Redis connection timeout
2024-01-17 10:30:30 ERROR [api] Request timeout for endpoint /users
2024-01-17 10:30:35 INFO  [auth] User login successful: john_doe
2024-01-17 10:30:40 ERROR [database] Connection pool exhausted
EOF

# Create sample API log  
cat > api.log << 'EOF'
2024-01-17 10:30:18 INFO  [request-123] GET /api/users - 200 OK
2024-01-17 10:30:22 ERROR [request-124] POST /api/login - 401 Unauthorized
2024-01-17 10:30:28 WARN  [request-125] GET /api/data - 504 Timeout
2024-01-17 10:30:32 INFO  [request-126] GET /api/health - 200 OK
2024-01-17 10:30:38 ERROR [request-127] POST /api/users - 500 Internal Server Error
EOF
```

### Basic log analysis:
```bash
python -m llmswap logs --analyze app.log
python -m llmswap logs --analyze api.log --format detailed
python -m llmswap logs --analyze api.log --format timeline
```

### Advanced filtering:
```bash
# Filter by log level
python -m llmswap logs --analyze app.log --level error
python -m llmswap logs --analyze app.log --level warn

# Filter by terms
python -m llmswap logs --analyze app.log --terms "error,timeout,failed"
python -m llmswap logs --analyze api.log --terms "500,401,404"

# Exclude terms
python -m llmswap logs --analyze app.log --exclude-terms "info,debug"

# Filter by request ID
python -m llmswap logs --analyze api.log --request-id "request-124"
```

### Multi-log correlation:
```bash
# Analyze multiple logs together
python -m llmswap logs --analyze "app.log,api.log" --correlate
python -m llmswap logs --analyze "app.log,api.log" --terms "error" --correlate --format detailed
```

## 5. Provider-Specific Testing

### Test with different providers (if configured):
```bash
python -m llmswap ask "Hello world" --provider anthropic
python -m llmswap ask "Hello world" --provider openai
python -m llmswap ask "Hello world" --provider gemini
```

### Test caching:
```bash
# First query (will be cached)
python -m llmswap ask "What is the capital of Japan?"

# Second identical query (should be much faster)
python -m llmswap ask "What is the capital of Japan?"

# Bypass cache
python -m llmswap ask "What is the capital of Japan?" --no-cache
```

## 6. Real-world Testing Scenarios

### Web Development Help:
```bash
python -m llmswap ask "Best practices for REST API design"
python -m llmswap ask "How to handle authentication in web apps?"
python -m llmswap chat
# In chat: "I'm building a user management system"
# "What database should I use?"
# "Show me a user model example"
```

### Debugging Session:
```bash
python -m llmswap debug --error "ModuleNotFoundError: No module named 'requests'"
python -m llmswap debug --error "ConnectionError: Max retries exceeded"
```

### Code Review Session:
```bash
# Create a more complex file for review
cat > complex_code.py << 'EOF'
import requests
import json

def fetch_user_data(user_id):
    url = f"https://api.example.com/users/{user_id}"
    response = requests.get(url)
    data = json.loads(response.text)
    return data['user']

def process_users(user_ids):
    results = []
    for id in user_ids:
        user = fetch_user_data(id)
        results.append(user)
    return results

users = process_users([1, 2, 3, 4, 5])
print(users)
EOF

python -m llmswap review complex_code.py --focus security
python -m llmswap review complex_code.py --focus performance  
python -m llmswap review complex_code.py --focus bugs
```

## 7. Performance Testing

### Time different query types:
```bash
# Short query
time python -m llmswap ask "2+2"

# Medium query  
time python -m llmswap ask "Explain object-oriented programming"

# Long query
time python -m llmswap ask "Write a comprehensive guide to Python web development including frameworks, databases, deployment, and best practices"
```

## 8. Expected Output Examples

When you run these commands, you should see:

### Analytics in action:
- Cost estimates before queries
- Token counting and usage
- Provider comparisons
- Cache hit/miss information

### CLI Features:
- Rich formatted output
- Error handling with helpful messages
- Context-aware responses in chat mode
- Detailed code reviews with specific suggestions

### New v4.0.0 Capabilities:
- Real-time cost tracking
- Provider optimization suggestions
- Advanced log filtering and correlation
- Privacy-first analytics (no queries stored)

## Cleanup
```bash
# Remove test files when done
rm -f sample_code.py complex_code.py app.log api.log
```

## Quick Test Script

Run this to test everything quickly:
```bash
export ANTHROPIC_API_KEY="your-key-here"
python test_v4_features.py
```

This will demonstrate all new v4.0.0 features with real output!