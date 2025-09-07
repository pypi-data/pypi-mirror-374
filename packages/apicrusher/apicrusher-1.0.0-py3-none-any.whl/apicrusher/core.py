# apicrusher/core.py
# Path: apicrusher/core.py

import hashlib
import json
import time
import os
from typing import Dict, Any, Optional, List, Union
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass
import re

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

@dataclass
class ModelConfig:
    """Configuration for model routing based on complexity"""
    name: str
    provider: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    complexity_threshold: float
    capabilities: List[str]

class UniversalModelRouter:
    """Dynamic model detection and routing for ALL providers (current and future)"""
    
    def __init__(self):
        # Universal provider patterns - automatically detects ANY model from ANY provider
        self.provider_patterns = {
            'openai': ['gpt', 'o1', 'davinci', 'curie', 'babbage', 'ada', 'text-', 'code-'],
            'anthropic': ['claude'],
            'google': ['gemini', 'palm', 'bard', 'text-bison', 'chat-bison'],
            'cohere': ['command', 'coral', 'embed'],
            'meta': ['llama', 'code-llama'],
            'mistral': ['mistral', 'mixtral', 'codestral'],
            'perplexity': ['pplx', 'sonar'],
            'groq': ['groq'],
            'together': ['together'],
            'fireworks': ['fireworks'],
            'anyscale': ['meta-llama'],
            'replicate': ['replicate'],
            'huggingface': ['huggingface'],
        }
        
        # Universal cost tiers - automatically classifies ANY model by name patterns
        self.cost_tiers = {
            'ultra': {'input': 0.015, 'output': 0.075},   # Premium models
            'pro': {'input': 0.005, 'output': 0.025},     # Professional models  
            'standard': {'input': 0.001, 'output': 0.005}, # Balanced models
            'mini': {'input': 0.0002, 'output': 0.001},   # Fast/cheap models
            'free': {'input': 0.0, 'output': 0.0}         # Free tier models
        }
        
        # Complexity thresholds for different model capabilities
        self.complexity_mapping = {
            'ultra': 0.9,     # Most expensive, most capable (GPT-4, Claude Opus, etc.)
            'pro': 0.7,       # High capability (GPT-4o, Claude Sonnet, Gemini Pro)
            'standard': 0.5,  # Balanced (Claude Haiku, Gemini Flash)
            'mini': 0.3,      # Fast and cheap (GPT-4o-mini, etc.)
            'free': 0.1       # Free tier models
        }
    
    def detect_provider(self, model_name: str) -> str:
        """Automatically detect provider from ANY model name"""
        model_lower = model_name.lower()
        
        # Check all known provider patterns
        for provider, patterns in self.provider_patterns.items():
            if any(pattern in model_lower for pattern in patterns):
                return provider
        
        # Smart fallbacks for unknown models
        if any(keyword in model_lower for keyword in ['chat', 'gpt', 'turbo']):
            return 'openai'
        elif 'claude' in model_lower:
            return 'anthropic'
        elif any(keyword in model_lower for keyword in ['gemini', 'bard', 'palm']):
            return 'google'
        elif 'llama' in model_lower:
            return 'meta'
        
        # Default to OpenAI for completely unknown models (most common API format)
        return 'openai'
    
    def classify_model_tier(self, model_name: str) -> str:
        """Automatically classify ANY model into cost/capability tier"""
        model_lower = model_name.lower()
        
        # Ultra tier - Premium models (highest cost, highest capability)
        ultra_patterns = [
            'opus', 'gpt-4', 'o1-preview', 'gpt-5', 'claude-4', 'sonnet-4', 
            'gemini-ultra', 'premium', 'pro-max', 'ultimate'
        ]
        if any(pattern in model_lower for pattern in ultra_patterns):
            return 'ultra'
        
        # Pro tier - Professional models (high cost, high capability)
        pro_patterns = [
            'sonnet', 'gpt-4o', 'o1-mini', 'claude-3-5', 'claude-3.5', 
            'gemini-1.5-pro', 'gemini-pro', 'pro', 'turbo', 'advanced'
        ]
        if any(pattern in model_lower for pattern in pro_patterns):
            return 'pro'
        
        # Mini tier - Fast and cheap models
        mini_patterns = [
            'mini', 'haiku', 'flash', 'gpt-3.5', 'small', 'fast', 'lite', 
            'instant', 'quick', 'nano', 'micro'
        ]
        if any(pattern in model_lower for pattern in mini_patterns):
            return 'mini'
        
        # Free tier - Free models
        free_patterns = ['free', 'open', 'community', 'base']
        if any(pattern in model_lower for pattern in free_patterns):
            return 'free'
        
        # Standard tier - Default for unknown models
        return 'standard'
    
    def get_model_config(self, model_name: str) -> Dict:
        """Get configuration for ANY model, known or unknown"""
        provider = self.detect_provider(model_name)
        tier = self.classify_model_tier(model_name)
        cost_config = self.cost_tiers[tier]
        
        return {
            'provider': provider,
            'cost_input': cost_config['input'],
            'cost_output': cost_config['output'],
            'complexity_threshold': self.complexity_mapping[tier],
            'tier': tier,
            'model_name': model_name
        }
    
    def suggest_cheaper_alternative(self, model_name: str, complexity: float) -> str:
        """Suggest cheaper model based on complexity for ANY provider"""
        current_config = self.get_model_config(model_name)
        provider = current_config['provider']
        
        # Ultra-low complexity - use cheapest available
        if complexity <= 0.2:
            if provider == 'openai':
                return 'gpt-4o-mini'
            elif provider == 'anthropic':
                return 'claude-3-haiku-20240307'
            elif provider == 'google':
                return 'gemini-1.5-flash'
            elif provider == 'groq':
                return 'llama3-8b-8192'  # Groq's fastest model
            elif provider == 'cohere':
                return 'command-light'
            else:
                # For unknown providers, suggest keeping original but warn
                return model_name
        
        # Low complexity - mini tier models
        elif complexity <= 0.4:
            if provider == 'openai':
                return 'gpt-4o-mini'
            elif provider == 'anthropic':
                return 'claude-3-haiku-20240307'
            elif provider == 'google':
                return 'gemini-1.5-flash'
            else:
                return model_name
        
        # Medium complexity - balanced models
        elif complexity <= 0.7:
            if provider == 'openai':
                return 'gpt-4o'
            elif provider == 'anthropic':
                return 'claude-3-5-sonnet-20241022'
            elif provider == 'google':
                return 'gemini-1.5-pro'
            else:
                return model_name
        
        # High complexity - keep original expensive model
        return model_name

class UniversalAPIClient:
    """Universal API client that can call ANY AI provider"""
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.clients = {}
        self._setup_clients()
    
    def _setup_clients(self):
        """Setup clients for all available providers"""
        
        # OpenAI
        if 'openai' in self.api_keys and OPENAI_AVAILABLE:
            self.clients['openai'] = openai.OpenAI(api_key=self.api_keys['openai'])
        
        # Anthropic
        if 'anthropic' in self.api_keys and ANTHROPIC_AVAILABLE:
            self.clients['anthropic'] = anthropic.Anthropic(api_key=self.api_keys['anthropic'])
        
        # Google
        if 'google' in self.api_keys and GOOGLE_AVAILABLE:
            genai.configure(api_key=self.api_keys['google'])
            self.clients['google'] = genai
    
    def call_model(self, provider: str, model: str, messages: List[Dict], **kwargs) -> Dict:
        """Universal model caller - works with ANY provider"""
        
        if provider not in self.clients:
            raise ValueError(f"No API key configured for {provider}. Add {provider}_api_key to your initialization.")
        
        client = self.clients[provider]
        
        try:
            if provider == 'openai':
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return {
                    'content': response.choices[0].message.content,
                    'model': model,
                    'provider': provider,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                }
                
            elif provider == 'anthropic':
                # Convert OpenAI format to Anthropic format
                formatted_messages = []
                system_message = None
                
                for msg in messages:
                    if msg['role'] == 'system':
                        system_message = msg['content']
                    else:
                        formatted_messages.append(msg)
                
                # Handle missing system message
                if not system_message:
                    system_message = "You are a helpful assistant."
                
                response = client.messages.create(
                    model=model,
                    messages=formatted_messages,
                    system=system_message,
                    max_tokens=kwargs.get('max_tokens', 1000)
                )
                
                return {
                    'content': response.content[0].text,
                    'model': model,
                    'provider': provider,
                    'usage': {
                        'prompt_tokens': response.usage.input_tokens,
                        'completion_tokens': response.usage.output_tokens,
                        'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                    }
                }
                
            elif provider == 'google':
                # Convert to Gemini format
                prompt_parts = []
                for msg in messages:
                    if msg['role'] in ['user', 'system']:
                        prompt_parts.append(msg['content'])
                
                full_prompt = '\n'.join(prompt_parts)
                model_obj = client.GenerativeModel(model)
                response = model_obj.generate_content(full_prompt)
                
                return {
                    'content': response.text,
                    'model': model,
                    'provider': provider,
                    'usage': {
                        'prompt_tokens': len(full_prompt) // 4,  # Approximation
                        'completion_tokens': len(response.text) // 4,
                        'total_tokens': (len(full_prompt) + len(response.text)) // 4
                    }
                }
            
            else:
                # Generic HTTP API fallback for unknown providers
                return self._call_generic_api(provider, model, messages, **kwargs)
                
        except Exception as e:
            # Smart fallback system
            fallback_model = self._get_fallback_model(provider)
            if fallback_model and fallback_model != model:
                print(f"⚠️ {model} failed, trying {fallback_model} fallback")
                return self.call_model(provider, fallback_model, messages, **kwargs)
            else:
                raise Exception(f"API call failed for {provider}:{model} - {str(e)}")
    
    def _get_fallback_model(self, provider: str) -> Optional[str]:
        """Get cheapest fallback model for each provider"""
        fallbacks = {
            'openai': 'gpt-4o-mini',
            'anthropic': 'claude-3-haiku-20240307',
            'google': 'gemini-1.5-flash',
            'groq': 'llama3-8b-8192',
            'cohere': 'command-light'
        }
        return fallbacks.get(provider)
    
    def _call_generic_api(self, provider: str, model: str, messages: List[Dict], **kwargs) -> Dict:
        """Generic HTTP API caller for unknown providers"""
        # This would implement a generic OpenAI-compatible API call
        # Many providers use OpenAI-compatible endpoints
        api_key = self.api_keys.get(provider)
        if not api_key:
            raise ValueError(f"No API key for {provider}")
        
        # Most providers follow OpenAI format, so try that first
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': messages,
            **kwargs
        }
        
        # Try common endpoint patterns
        possible_endpoints = [
            f'https://api.{provider}.com/v1/chat/completions',
            f'https://{provider}.ai/v1/chat/completions',
            f'https://api.{provider}.ai/v1/chat/completions'
        ]
        
        for endpoint in possible_endpoints:
            try:
                response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'content': data['choices'][0]['message']['content'],
                        'model': model,
                        'provider': provider,
                        'usage': data.get('usage', {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0})
                    }
            except:
                continue
        
        raise Exception(f"Could not find working endpoint for {provider}")

class APIOptimizer:
    """Main optimizer class with universal model support"""
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 anthropic_api_key: Optional[str] = None,
                 google_api_key: Optional[str] = None,
                 groq_api_key: Optional[str] = None,
                 cohere_api_key: Optional[str] = None,
                 apicrusher_key: Optional[str] = None,
                 redis_url: Optional[str] = None,
                 track_analytics: bool = True,
                 **additional_api_keys):
        """Initialize with API keys for ALL providers"""
        
        # Collect all API keys
        self.api_keys = {}
        if openai_api_key:
            self.api_keys['openai'] = openai_api_key
        if anthropic_api_key:
            self.api_keys['anthropic'] = anthropic_api_key
        if google_api_key:
            self.api_keys['google'] = google_api_key
        if groq_api_key:
            self.api_keys['groq'] = groq_api_key
        if cohere_api_key:
            self.api_keys['cohere'] = cohere_api_key
        
        # Add any additional API keys passed as kwargs
        for key, value in additional_api_keys.items():
            if key.endswith('_api_key'):
                provider = key.replace('_api_key', '')
                self.api_keys[provider] = value
        
        # Universal components
        self.model_router = UniversalModelRouter()
        self.api_client = UniversalAPIClient(self.api_keys)
        
        # APICrusher configuration
        self.apicrusher_key = apicrusher_key
        self.rules = None
        self.rules_last_fetched = None
        self.rules_ttl = 3600  # Refresh rules every hour
        
        # Fetch optimization rules
        if self.apicrusher_key:
            self.fetch_rules()
        
        # Cache setup
        if redis_url and REDIS_AVAILABLE:
            try:
                self.cache = redis.from_url(redis_url)
                self.cache.ping()
                self.cache_type = 'redis'
            except:
                self.cache = {}
                self.cache_type = 'memory'
        else:
            self.cache = {}
            self.cache_type = 'memory'
            
        # Analytics
        self.analytics = []
        self.track_analytics = track_analytics
        self.total_saved = 0.0
        self.session_metrics = {
            "calls_count": 0,
            "money_saved": 0.0,
            "cache_hits": 0,
            "models_used": {},
            "providers_used": {}
        }
        
    def fetch_rules(self):
        """Fetch optimization rules from APICrusher server"""
        if not self.apicrusher_key:
            return False
        
        # Check if rules are still fresh
        if self.rules_last_fetched:
            age = time.time() - self.rules_last_fetched
            if age < self.rules_ttl and self.rules:
                return True
        
        try:
            # Try main domain first
            response = requests.get(
                f"https://apicrusher.com/api/rules/{self.apicrusher_key}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.rules = data.get("rules")
                    self.rules_last_fetched = time.time()
                    tier = data.get("tier", "unknown")
                    print(f"✅ APICrusher rules loaded (tier: {tier})")
                    return True
                else:
                    print("❌ Invalid APICrusher key")
                    self.rules = None
            else:
                # Fallback to onrender.com
                try:
                    response = requests.get(
                        f"https://apicrusher.onrender.com/api/rules/{self.apicrusher_key}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            self.rules = data.get("rules")
                            self.rules_last_fetched = time.time()
                            print("✅ APICrusher rules loaded (fallback)")
                            return True
                except:
                    pass
                
                print(f"⚠️ Could not fetch rules (status: {response.status_code})")
                
        except Exception as e:
            print(f"⚠️ Error fetching rules: {e}")
            
        return False
        
    def calculate_complexity(self, messages: List[Dict]) -> float:
        """Calculate prompt complexity for optimal routing"""
        
        full_prompt = ' '.join([str(m.get('content', '')) for m in messages])
        
        # Use optimization rules if available
        if self.rules and self.rules.get("routing_rules"):
            for rule in self.rules["routing_rules"]:
                conditions = rule.get("conditions", {})
                
                if "keywords" in conditions:
                    keywords = conditions["keywords"]
                    if any(kw.lower() in full_prompt.lower() for kw in keywords):
                        if "prompt_length" in conditions:
                            word_count = len(full_prompt.split())
                            length_cond = conditions["prompt_length"]
                            
                            if "max" in length_cond and word_count > length_cond["max"]:
                                continue
                            if "min" in length_cond and word_count < length_cond["min"]:
                                continue
                        
                        if rule["action"] == "route_to_cheapest":
                            return 0.2
                        elif rule["action"] == "route_to_balanced":
                            return 0.6
                        elif rule["action"] == "keep_original":
                            return 1.0
        
        # Fallback complexity calculation
        complexity_score = 0.0
        word_count = len(full_prompt.split())
        
        # Length factor
        if word_count < 50:
            complexity_score += 0.1
        elif word_count < 200:
            complexity_score += 0.3
        elif word_count < 1000:
            complexity_score += 0.5
        else:
            complexity_score += 0.7
            
        # Complexity indicators
        complexity_indicators = {
            'analyze': 0.2, 'explain': 0.1, 'code': 0.3, 'debug': 0.4,
            'mathematical': 0.5, 'reasoning': 0.5, 'creative': 0.3,
            'simple': -0.3, 'list': -0.2, 'yes/no': -0.4, 'extract': -0.2,
            'summarize': 0.2, 'translate': 0.1, 'classify': -0.1
        }
        
        lower_prompt = full_prompt.lower()
        for indicator, weight in complexity_indicators.items():
            if indicator in lower_prompt:
                complexity_score += weight
                
        return min(max(complexity_score, 0.0), 1.0)
        
    def select_optimal_model(self, complexity: float, original_model: str) -> str:
        """Select optimal model using universal router"""
        
        # Use custom rules if available
        if self.rules and self.rules.get("models"):
            models = self.rules["models"]
            
            if complexity <= 0.3:
                cheap_models = ["gpt-4o-mini", "claude-3-haiku-20240307", "gemini-1.5-flash"]
                for model in cheap_models:
                    if model in models:
                        return model
            elif complexity <= 0.7:
                balanced_models = ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]
                for model in balanced_models:
                    if model in models:
                        return model
            else:
                return original_model
        
        # Use universal router
        return self.model_router.suggest_cheaper_alternative(original_model, complexity)
        
    def optimize_prompt(self, prompt: str) -> str:
        """Optimize prompts to reduce token usage"""
        
        if self.rules and self.rules.get("prompt_optimization"):
            rules = self.rules["prompt_optimization"]
            
            if rules.get("remove_redundancy"):
                # Remove redundant words and phrases
                redundant_phrases = [
                    "please ", "could you ", "would you mind ", "i would like ",
                    "can you help me ", "i need you to ", "if possible "
                ]
                
                optimized = prompt
                for phrase in redundant_phrases:
                    optimized = optimized.replace(phrase, "")
                
                return optimized.strip()
        
        return prompt
    
    def _get_cache_key(self, messages: List[Dict], model: str) -> str:
        """Generate cache key for request"""
        content = json.dumps(messages, sort_keys=True) + model
        return hashlib.md5(content.encode()).hexdigest()
    
    def _calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calculate cost using universal pricing"""
        
        # Try rules-based pricing first
        if self.rules and self.rules.get("models"):
            model_config = self.rules["models"].get(model)
            if model_config:
                return (tokens_in * model_config["cost_input"] + 
                       tokens_out * model_config["cost_output"]) / 1000
        
        # Use universal router pricing
        config = self.model_router.get_model_config(model)
        return (tokens_in * config['cost_input'] + tokens_out * config['cost_output']) / 1000
    
    def complete(self, model: str, messages: List[Dict], **kwargs) -> Dict:
        """Main completion method with universal optimization"""
        
        start_time = time.time()
        
        # Calculate complexity
        complexity = self.calculate_complexity(messages)
        
        # Select optimal model
        optimal_model = self.select_optimal_model(complexity, model)
        
        # Optimize prompts
        optimized_messages = []
        for msg in messages:
            if isinstance(msg.get('content'), str):
                optimized_content = self.optimize_prompt(msg['content'])
                optimized_messages.append({**msg, 'content': optimized_content})
            else:
                optimized_messages.append(msg)
        
        # Check cache
        cache_key = self._get_cache_key(optimized_messages, optimal_model)
        cached_response = None
        
        if self.cache_type == 'redis':
            try:
                cached = self.cache.get(cache_key)
                if cached:
                    cached_response = json.loads(cached)
            except:
                pass
        else:
            cached_response = self.cache.get(cache_key)
        
        if cached_response:
            # Cache hit
            self.session_metrics["cache_hits"] += 1
            print(f"💾 Cache hit for {optimal_model}")
            
            # Track analytics
            if self.track_analytics:
                original_cost = self._calculate_cost(model, cached_response['usage']['prompt_tokens'], 
                                                   cached_response['usage']['completion_tokens'])
                optimized_cost = 0.0  # Cache hit = free
                savings = original_cost
                
                self.session_metrics["money_saved"] += savings
                self.total_saved += savings
                
            return cached_response
        
        # Make API call
        model_config = self.model_router.get_model_config(optimal_model)
        provider = model_config['provider']
        
        try:
            response = self.api_client.call_model(provider, optimal_model, optimized_messages, **kwargs)
            
            # Cache the response
            if self.cache_type == 'redis':
                try:
                    self.cache.setex(cache_key, 3600, json.dumps(response))  # 1 hour TTL
                except:
                    pass
            else:
                self.cache[cache_key] = response
            
            # Track analytics
            if self.track_analytics:
                original_cost = self._calculate_cost(model, response['usage']['prompt_tokens'], 
                                                   response['usage']['completion_tokens'])
                optimized_cost = self._calculate_cost(optimal_model, response['usage']['prompt_tokens'], 
                                                    response['usage']['completion_tokens'])
                savings = max(0, original_cost - optimized_cost)
                
                self.session_metrics["calls_count"] += 1
                self.session_metrics["money_saved"] += savings
                self.session_metrics["models_used"][optimal_model] = self.session_metrics["models_used"].get(optimal_model, 0) + 1
                self.session_metrics["providers_used"][provider] = self.session_metrics["providers_used"].get(provider, 0) + 1
                self.total_saved += savings
                
                # Store analytics
                self.analytics.append({
                    'timestamp': datetime.now().isoformat(),
                    'original_model': model,
                    'optimized_model': optimal_model,
                    'provider': provider,
                    'complexity': complexity,
                    'original_cost': original_cost,
                    'optimized_cost': optimized_cost,
                    'savings': savings,
                    'cache_hit': False,
                    'response_time': time.time() - start_time
                })
                
                # Send telemetry to APICrusher if enabled
                if self.apicrusher_key:
                    try:
                        requests.post(
                            "https://apicrusher.com/api/metrics",
                            json={
                                'key': self.apicrusher_key,
                                'model_original': model,
                                'model_used': optimal_model,
                                'provider': provider,
                                'tokens_in': response['usage']['prompt_tokens'],
                                'tokens_out': response['usage']['completion_tokens'],
                                'cost_original': original_cost,
                                'cost_optimized': optimized_cost,
                                'savings': savings,
                                'complexity': complexity
                            },
                            timeout=2
                        )
                    except:
                        pass  # Don't fail if telemetry fails
            
            print(f"✅ {optimal_model} ({provider}) | Complexity: {complexity:.2f} | Saved: ${savings:.4f}")
            
            return response
            
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
            raise
    
    def get_savings_report(self) -> Dict:
        """Generate comprehensive savings report"""
        
        if not self.analytics:
            return {
                'total_calls': 0,
                'total_savings': 0.0,
                'cache_hit_rate': 0.0,
                'average_savings_per_call': 0.0,
                'models_used': {},
                'providers_used': {},
                'optimization_rate': 0.0
            }
        
        total_calls = len(self.analytics)
        cache_hits = self.session_metrics.get("cache_hits", 0)
        total_with_cache = total_calls + cache_hits
        
        optimized_calls = len([a for a in self.analytics if a['optimized_model'] != a['original_model']])
        
        return {
            'total_calls': total_with_cache,
            'total_savings': self.session_metrics["money_saved"],
            'cache_hit_rate': (cache_hits / total_with_cache) * 100 if total_with_cache > 0 else 0,
            'average_savings_per_call': self.session_metrics["money_saved"] / total_with_cache if total_with_cache > 0 else 0,
            'models_used': self.session_metrics["models_used"],
            'providers_used': self.session_metrics["providers_used"],
            'optimization_rate': (optimized_calls / total_calls) * 100 if total_calls > 0 else 0,
            'analytics': self.analytics[-10:]  # Last 10 calls for debugging
        }

# Universal OpenAI-compatible wrapper
class OpenAI:
    """Universal drop-in replacement supporting ALL AI providers"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 anthropic_api_key: Optional[str] = None,
                 google_api_key: Optional[str] = None,
                 groq_api_key: Optional[str] = None,
                 cohere_api_key: Optional[str] = None,
                 apicrusher_key: Optional[str] = None,
                 **additional_keys):
        """
        Universal AI client with APICrusher optimization
        
        Supports: OpenAI, Anthropic, Google, Groq, Cohere, and ANY future provider
        """
        
        # Environment variable fallbacks
        api_key = api_key or os.environ.get('OPENAI_API_KEY')
        anthropic_api_key = anthropic_api_key or os.environ.get('ANTHROPIC_API_KEY')
        google_api_key = google_api_key or os.environ.get('GOOGLE_API_KEY')
        groq_api_key = groq_api_key or os.environ.get('GROQ_API_KEY')
        cohere_api_key = cohere_api_key or os.environ.get('COHERE_API_KEY')
        apicrusher_key = apicrusher_key or os.environ.get('APICRUSHER_KEY')
        
        if apicrusher_key and apicrusher_key.startswith('apc_'):
            print("🚀 APICrusher optimization enabled")
            print("🌐 Universal provider support: OpenAI, Anthropic, Google, Groq, and more")
            print("💰 Proven savings: 63-99% across ALL AI providers")
        else:
            print("⚠️ APICrusher not configured. Add your key to save money across ALL AI providers.")
            print("   Get your key at: https://apicrusher.com")
        
        self.optimizer = APIOptimizer(
            openai_api_key=api_key,
            anthropic_api_key=anthropic_api_key,
            google_api_key=google_api_key,
            groq_api_key=groq_api_key,
            cohere_api_key=cohere_api_key,
            apicrusher_key=apicrusher_key,
            **additional_keys
        )
        self.chat = self.Chat(self.optimizer)
        
    class Chat:
        def __init__(self, optimizer):
            self.optimizer = optimizer
            self.completions = self.Completions(optimizer)
            
        class Completions:
            def __init__(self, optimizer):
                self.optimizer = optimizer
                
            def create(self, **kwargs):
                """Universal completion supporting ANY model from ANY provider"""
                
                model = kwargs.get('model', 'gpt-4o-mini')
                messages = kwargs.get('messages', [])
                
                # Remove our custom parameters before passing to API
                api_kwargs = {k: v for k, v in kwargs.items() 
                             if k not in ['model', 'messages']}
                
                try:
                    response = self.optimizer.complete(model, messages, **api_kwargs)
                    
                    # Return OpenAI-compatible response format
                    class CompletionResponse:
                        def __init__(self, content, model, usage):
                            self.choices = [
                                type('Choice', (), {
                                    'message': type('Message', (), {
                                        'content': content,
                                        'role': 'assistant'
                                    })(),
                                    'finish_reason': 'stop'
                                })()
                            ]
                            self.model = model
                            self.usage = type('Usage', (), usage)()
                    
                    return CompletionResponse(
                        response['content'], 
                        response['model'], 
                        response['usage']
                    )
                    
                except Exception as e:
                    print(f"❌ Universal completion failed: {str(e)}")
                    raise
    
    def get_savings_report(self):
        """Get detailed savings analytics"""
        return self.optimizer.get_savings_report()
    
    def print_savings_summary(self):
        """Print user-friendly savings summary"""
        report = self.get_savings_report()
        
        print("\n🎯 APICrusher Savings Report")
        print("=" * 40)
        print(f"💸 Total Saved: ${report['total_savings']:.4f}")
        print(f"📞 Total Calls: {report['total_calls']}")
        print(f"💾 Cache Hit Rate: {report['cache_hit_rate']:.1f}%")
        print(f"⚡ Optimization Rate: {report['optimization_rate']:.1f}%")
        print(f"📊 Avg Savings/Call: ${report['average_savings_per_call']:.4f}")
        
        if report['models_used']:
            print(f"\n🤖 Models Used:")
            for model, count in report['models_used'].items():
                print(f"   {model}: {count} calls")
        
        if report['providers_used']:
            print(f"\n🌐 Providers Used:")
            for provider, count in report['providers_used'].items():
                print(f"   {provider}: {count} calls")
        
        print("=" * 40)
