# APICrusher - Cut AI API Costs by 63-99%

![Version](https://img.shields.io/pypi/v/apicrusher)
![Python](https://img.shields.io/pypi/pyversions/apicrusher)
![License](https://img.shields.io/badge/License-MIT-yellow)

Stop bleeding money on AI APIs. APICrusher automatically routes your requests to cheaper models when possible, saving you 63-99% on costs across OpenAI, Anthropic, Google, and 12+ other providers.

## The Problem

You're using GPT-4 for everything. Even for "What's 2+2?" That's like hiring a surgeon to put on a band-aid. We proved companies waste thousands per month on overkill AI models.

## The Solution

APICrusher intelligently routes your API calls:
- Simple queries → Cheap models (99% savings)
- Complex tasks → Premium models (when actually needed)
- Duplicate requests → Instant cache (100% savings)

**Result: Same quality, 63-99% cheaper.**

## Installation

```bash
pip install apicrusher
```

## Quick Start

### 1. Get Your Access Key

APICrusher is a paid service ($99/month or $990/year). Get your access key at [apicrusher.com](https://apicrusher.com).

### 2. Drop-In Replacement (2 Lines of Code)

```python
# Before: Expensive
from openai import OpenAI
client = OpenAI(api_key="your-openai-key")

# After: 63-99% Cheaper
from apicrusher import OpenAI
client = OpenAI(
    api_key="your-openai-key",
    apicrusher_key="apc_live_your_key"  # Get at apicrusher.com
)
```

That's it. Your code stays exactly the same, but now costs 63-99% less.

### 3. Watch Your Savings

```python
# Everything works identically
response = client.chat.completions.create(
    model="gpt-4",  # Automatically routes to gpt-4o-mini when appropriate
    messages=[{"role": "user", "content": "What's 2+2?"}]
)

# View real-time savings
client.print_savings_summary()
# Output: Total saved: $47.23 | Cache hits: 34% | Avg reduction: 73%
```

## Universal Provider Support

APICrusher works with **ALL major AI providers** using the same interface:

```python
from apicrusher import OpenAI

client = OpenAI(
    # Add any provider keys you use
    api_key="your-openai-key",
    anthropic_api_key="your-anthropic-key",
    google_api_key="your-google-key",
    groq_api_key="your-groq-key",
    
    # Your APICrusher optimization key
    apicrusher_key="apc_live_your_key"
)

# Automatically optimizes across ALL providers
response = client.chat.completions.create(
    model="claude-3-opus",  # Routes to claude-3-haiku for simple tasks
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Supported Providers
- **OpenAI**: GPT-4, GPT-4o, O1, GPT-5
- **Anthropic**: Claude 3.5, Claude 4, Opus, Sonnet, Haiku
- **Google**: Gemini Pro, Gemini Flash, Gemini 2.0
- **Groq**: Llama 3.1, Mixtral, Ultra-fast inference
- **Cohere**: Command R, Command R+
- **Meta**: Llama 3.1 (8B to 405B)
- **Mistral**: Large, Medium, Small models
- **Perplexity**: Sonar models with web search
- **xAI**: Grok and Grok-mini
- **Amazon Bedrock**: Titan, Claude via AWS
- **Together AI**: Open source model hosting
- **Replicate**: Custom and fine-tuned models

## Pricing

| Plan | Price | Savings | ROI |
|------|-------|---------|-----|
| **Monthly** | $99/month | 63-99% on API costs | Pays for itself in 1-3 days |
| **Yearly** | $990/year | Save 2 months + API savings | 10-50x return |

**Free Trial**: 7-day trial with full optimization features. Cancel anytime.

## Real Examples

### Before APICrusher
```python
# You're doing this (expensive)
response = openai.chat.completions.create(
    model="gpt-4",  # $0.03 per 1K tokens
    messages=[{"role": "user", "content": "Format this date: 2024-01-15"}]
)
# Cost: $0.0021 for a simple formatting task
```

### After APICrusher
```python
# Same code, automatic optimization
response = client.chat.completions.create(
    model="gpt-4",  # APICrusher routes to gpt-4o-mini
    messages=[{"role": "user", "content": "Format this date: 2024-01-15"}]
)
# Cost: $0.000015 (99.3% savings)
# You write the same code, we handle the optimization
```

## Advanced Configuration

```python
from apicrusher import OpenAI

client = OpenAI(
    # Required
    api_key="your-openai-key",
    apicrusher_key="apc_live_your_key",
    
    # Optional: Add more providers
    anthropic_api_key="sk-ant-...",
    google_api_key="AIza...",
    
    # Optional: Redis for distributed caching
    redis_url="redis://localhost:6379",
    
    # Optional: Custom complexity threshold (0.0-1.0)
    complexity_threshold=0.3  # Lower = more aggressive optimization
)
```

## How It Works

1. **Complexity Analysis**: APICrusher analyzes each request in real-time
2. **Smart Routing**: Routes to the cheapest capable model
3. **Response Caching**: Duplicate requests served instantly
4. **Quality Preservation**: Complex tasks still use premium models
5. **Transparent**: You see exactly what's happening in logs

## Dashboard & Analytics

Every APICrusher account includes:
- Real-time cost savings dashboard
- Model routing analytics
- Usage patterns and optimization opportunities
- CSV/Excel export for finance teams
- Billing portal for subscription management

Access at [apicrusher.com/dashboard](https://apicrusher.com/dashboard)

## Enterprise Features

For companies spending $10K+/month on AI:
- Self-hosted deployment options
- Custom model routing rules
- SSO/SAML authentication
- SLA guarantees
- Dedicated support

Contact: hello@apicrusher.com

## Security & Privacy

- **Your API keys stay local** - Never sent to our servers
- **No prompt logging** - We never see your data
- **SOC2 compliant** - Enterprise-grade security
- **GDPR compliant** - Full data privacy

## Support

- **Email**: hello@apicrusher.com
- **Response time**: Within 24 hours for all customers

## FAQ

**Q: Will this break my existing code?**  
A: No. APICrusher is a drop-in replacement. Your code stays exactly the same.

**Q: What if I need GPT-4 for complex tasks?**  
A: APICrusher automatically detects complexity. Complex tasks still use GPT-4.

**Q: Can I try it before paying?**  
A: Yes. 7-day free trial with full features. Cancel anytime.

**Q: How much will I actually save?**  
A: Most customers save 63-99%. If you're spending $1000/month, expect to save $630-$990.

**Q: Is there a free version?**  
A: No. APICrusher is a premium optimization service. The value is in the optimization engine, not the SDK.

## The Bottom Line

You're overpaying for AI by 63-99%. APICrusher fixes that with 2 lines of code.

**Get your access key and start saving: [apicrusher.com](https://apicrusher.com)**

---

*APICrusher - Because GPT-5 for "Hello World" is just burning money.*
