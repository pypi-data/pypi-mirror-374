"""
LLM Integration for Cognix
Handles communication with OpenAI and Anthropic APIs
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Generator
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class LLMResponse:
    """Response from LLM"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    timestamp: float


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> LLMResponse:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def stream_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Generator[str, None, None]:
        """Stream response from LLM"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", base_url: str = None):
        """Initialize OpenAI provider with optional base URL for OpenRouter support"""
        self.api_key = api_key
        self.model = model
        
        try:
            import openai
            
            # OpenRouter または他のOpenAI互換サービス対応
            if base_url:
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    default_headers={
                        "HTTP-Referer": "https://github.com/cognix-dev/cognix",
                        "X-Title": "Cognix"
                    }
                )
            else:
                # 通常のOpenAI API
                self.client = openai.OpenAI(api_key=api_key)
                
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def _get_params_for_model(self, max_tokens: int, temperature: float) -> dict:
        """Get appropriate parameters based on model"""
        params = {}
        
        # Token parameter
        if self.model.startswith("gpt-5") or self.model.startswith("o1"):
            params["max_completion_tokens"] = max_tokens
            # GPT-5 only supports temperature = 1
            if temperature != 1.0:
                # Silent adjustment for GPT-5
                pass
            # Don't set temperature for GPT-5 (uses default 1)
        else:
            params["max_tokens"] = max_tokens
            params["temperature"] = temperature
        
        return params
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> LLMResponse:
        """Generate response from OpenAI"""
        try:
            # Base parameters
            params = {
                "model": self.model,
                "messages": messages,
            }
            
            # Add model-specific parameters
            params.update(self._get_params_for_model(max_tokens, temperature))
            
            response = self.client.chat.completions.create(**params)
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                finish_reason=response.choices[0].finish_reason,
                timestamp=time.time()
            )
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def stream_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Generator[str, None, None]:
        """Stream response from OpenAI"""
        try:
            # Base parameters
            params = {
                "model": self.model,
                "messages": messages,
                "stream": True
            }
            
            # Add model-specific parameters
            params.update(self._get_params_for_model(max_tokens, temperature))
            
            stream = self.client.chat.completions.create(**params)
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"OpenAI streaming error: {e}")

class AnthropicProvider(LLMProvider):
    """Anthropic API provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """Initialize Anthropic provider"""
        self.api_key = api_key
        self.model = model
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> tuple:
        """Convert messages to Anthropic format"""
        system_message = ""
        converted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                converted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return system_message, converted_messages
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> LLMResponse:
        """Generate response from Anthropic"""
        try:
            system_message, converted_messages = self._convert_messages(messages)
            
            kwargs = {
                "model": self.model,
                "messages": converted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if system_message:
                kwargs["system"] = system_message
            
            response = self.client.messages.create(**kwargs)
            
            return LLMResponse(
                content=response.content[0].text,
                model=self.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                finish_reason=response.stop_reason,
                timestamp=time.time()
            )
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")
    
    def stream_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Generator[str, None, None]:
        """Stream response from Anthropic"""
        try:
            system_message, converted_messages = self._convert_messages(messages)
            
            kwargs = {
                "model": self.model,
                "messages": converted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            if system_message:
                kwargs["system"] = system_message
            
            stream = self.client.messages.create(**kwargs)
            
            for chunk in stream:
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text
                    
        except Exception as e:
            raise Exception(f"Anthropic streaming error: {e}")


class LLMManager:
    """Manages LLM providers and interactions"""

    # OpenRouter形式のモデル名を処理する関数
    @staticmethod
    def normalize_model_name(model: str) -> str:
        """OpenRouter形式のモデル名を正規化"""
        # openai/gpt-oss-120b:free -> gpt-oss-120b
        if "/" in model:
            parts = model.split("/")
            model = parts[-1]  # プロバイダー部分を削除
        if ":" in model:
            model = model.split(":")[0]  # :free などのサフィックスを削除
        return model

    # MODEL_PROVIDERS辞書を完全に置き換え
    MODEL_PROVIDERS = {
        # OpenAI models
        "gpt-4": "openai",
        "gpt-4-turbo": "openai",
        "gpt-4-turbo-preview": "openai",
        "gpt-3.5-turbo": "openai",
        "gpt-4o": "openai",                    # 新規追加
        "gpt-4o-mini": "openai",               # 新規追加
        "gpt-4.1": "openai",                   # 新規追加
        "gpt-4.1-mini": "openai",              # 新規追加
        "gpt-4.1-nano": "openai",              # 新規追加
        
        # Anthropic models（既存のまま）
        "claude-opus-4-20250514": "anthropic",
        "claude-sonnet-4-20250514": "anthropic",
        "claude-3-5-sonnet-20241022": "anthropic",
        "claude-3-7-sonnet-20250219": "anthropic",
    }

    # エイリアス名を正確なモデル名にマップ
    # MODEL_ALIASES辞書も更新
    MODEL_ALIASES = {
        "claude-opus-4": "claude-opus-4-20250514",
        "claude-sonnet-4": "claude-sonnet-4-20250514",
        "claude-3.7-sonnet": "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet": "claude-3-5-sonnet-20241022",
        # OpenAI aliases 新規追加
        "gpt4": "gpt-4",
        "gpt4o": "gpt-4o",
        "gpt-4-omni": "gpt-4o",
    }

    def get_provider_for_model(self, model: str) -> LLMProvider:
        """Get provider for a specific model"""
        # OpenRouter形式のモデル名を正規化
        normalized_model = self.normalize_model_name(model)
        
        # エイリアス名を正確な名前に変換
        actual_model = self.MODEL_ALIASES.get(normalized_model, normalized_model)
        
        provider_name = self.MODEL_PROVIDERS.get(actual_model)
        
        if not provider_name:
            # OpenRouter経由の場合はopenaiプロバイダーを使用
            if os.getenv("OPENAI_BASE_URL"):
                provider_name = "openai"
            else:
                raise ValueError(f"Unknown model: {model}")
        
        provider = self.providers.get(provider_name)
        if not provider:
            raise Exception(f"Provider {provider_name} not available for model {model}")
        
        # プロバイダーに元のモデル名を設定（OpenRouter用）
        provider.model = model  # 正規化前の元の名前を保持
        return provider

    def __init__(self, config):
        """Initialize LLM manager"""
        self.config = config
        self.providers: Dict[str, LLMProvider] = {}
        
        # Handle both Config objects and dict configs
        if hasattr(config, 'get'):
            self.current_model = config.get("model", "claude-sonnet-4-20250514")
        else:
            self.current_model = config.get("model", "claude-sonnet-4-20250514")
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        
        """Initialize LLM providers based on available API keys"""

        # Use config's centralized get_api_key method which handles .env files
        from cognix.config import Config
        
        # Get config instance if it's a dict (backwards compatibility)
        if isinstance(self.config, dict):
            config_obj = Config()
        else:
            config_obj = self.config
        
        # Initialize OpenAI provider
        openai_key = config_obj.get_api_key("openai")
        if openai_key:
            try:
                # base_url を環境変数から取得
                base_url = os.getenv("OPENAI_BASE_URL")
                self.providers["openai"] = OpenAIProvider(
                    openai_key, 
                    base_url=base_url
                )
                
                if os.getenv('COGNIX_DEBUG') or os.getenv('DEBUG'):
                    if base_url:
                        print(f"Debug: OpenAI provider initialized with base URL: {base_url}")
                    else:
                        print(f"Debug: OpenAI provider initialized successfully")
            except ImportError as e:
                print(f"Warning: {e}")
        else:
            if os.getenv('COGNIX_DEBUG') or os.getenv('DEBUG'):
                print("Debug: No OpenAI API key found")
        
        # Initialize Anthropic provider
        anthropic_key = config_obj.get_api_key("anthropic")
        if anthropic_key:
            try:
                self.providers["anthropic"] = AnthropicProvider(anthropic_key)
                if os.getenv('COGNIX_DEBUG') or os.getenv('DEBUG'):
                    print(f"Debug: Anthropic provider initialized successfully")
            except ImportError as e:
                print(f"Warning: {e}")
        else:
            if os.getenv('COGNIX_DEBUG') or os.getenv('DEBUG'):
                print("Debug: No Anthropic API key found")
        
        if not self.providers:
            self._show_immediate_setup_help()
            raise Exception("No LLM providers available. Please set API keys for OpenAI or Anthropic.")
    
    def _detect_available_models(self):
        """Auto-detect available models from OpenAI API"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.providers["openai"].api_key)
            models = client.models.list()
            
            for model in models:
                model_id = model.id
                if model_id.startswith(('gpt-', 'o1-')) and model_id not in self.MODEL_PROVIDERS:
                    self.MODEL_PROVIDERS[model_id] = "openai"
                    if os.getenv('COGNIX_DEBUG'):
                        print(f"Debug: Auto-detected model: {model_id}")
                        
        except Exception as e:
            if os.getenv('COGNIX_DEBUG'):
                print(f"Debug: Could not auto-detect models: {e}")

    def _show_immediate_setup_help(self):
        """Show immediate setup help with specific next steps"""
        print("\n" + "⚠️  API KEY REQUIRED")
        print("="*50)
        
        env_path = Path.cwd() / ".env"
        env_exists = env_path.exists()
        
        if env_exists:
            print("Found .env file, but no valid API keys detected.")
            print(f"📄 Edit: {env_path}")
            print()
            print("Make sure you have one of these lines (uncommented):")
            print("   ANTHROPIC_API_KEY=sk-ant-your_key_here")
            print("   OPENAI_API_KEY=sk-your_key_here")
        else:
            print("No .env file found. Quick setup:")
            print()
            print(f"1. Create: {env_path}")
            print("2. Add one of these lines:")
            print("   ANTHROPIC_API_KEY=sk-ant-your_key_here")
            print("   OPENAI_API_KEY=sk-your_key_here")
            print()
            print("Or create it now with:")
            print(f"   echo 'ANTHROPIC_API_KEY=your_key' > {env_path}")
        
        print()
        print("🔗 Get API keys:")
        print("   • Anthropic: https://console.anthropic.com/")
        print("   • OpenAI: https://platform.openai.com/api-keys")
        print("="*50)    
    
    def generate_response(
        self,
        prompt: str,
        context: str = "",
        conversation_history: List[Dict[str, str]] = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_prompt: str = None
    ) -> LLMResponse:
        """Generate response using configured LLM"""
        model = model or self.current_model
        provider = self.get_provider_for_model(model)
        
        # Build messages
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif context:
            system_content = f"You are Claude Code, an AI assistant helping with software development.\n\nProject Context:\n{context}"
            messages.append({"role": "system", "content": system_content})
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
              
        return provider.generate_response(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def stream_response(
        self,
        prompt: str,
        context: str = "",
        conversation_history: List[Dict[str, str]] = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_prompt: str = None
    ) -> Generator[str, None, None]:
        """Stream response using configured LLM"""
        model = model or self.current_model
        provider = self.get_provider_for_model(model)
        
        # Build messages
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif context:
            system_content = f"You are Claude Code, an AI assistant helping with software development.\n\nProject Context:\n{context}"
            messages.append({"role": "system", "content": system_content})
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        yield from provider.stream_response(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def get_available_models(self) -> List[str]:
        """Get list of available models including OpenRouter"""
        available_models = []
        
        # 定義済みモデルを追加
        for model, provider_name in self.MODEL_PROVIDERS.items():
            if (provider_name in self.providers and 
                model not in self.MODEL_ALIASES):
                available_models.append(model)
        
        # OpenRouterの場合は、設定されているが利用可能かは実行時に判断
        # ここでは何も追加しない
        
        return sorted(available_models)
    
    def set_model(self, model: str):
        """Set the current model"""
        # Consider OpenRouter format
        if os.getenv("OPENAI_BASE_URL") and "/" in model:
            # For OpenRouter models, set as-is
            self.current_model = model
            return
        
        # Convert alias names to actual names
        actual_model = self.MODEL_ALIASES.get(model, model)
        
        if actual_model not in self.MODEL_PROVIDERS:
            # Also check aliases
            if model not in self.MODEL_ALIASES:
                # Allow OpenRouter models
                if os.getenv("OPENAI_BASE_URL"):
                    self.current_model = model
                    return
                raise ValueError(f"Unknown model: {model}")
        
        provider_name = self.MODEL_PROVIDERS[actual_model]
        if provider_name not in self.providers:
            raise Exception(f"Provider {provider_name} not available")
        
        self.current_model = model  # Changed: use original model name instead of actual_model
    
    def get_model_info(self, model: str = None) -> Dict[str, Any]:
        """Get information about a model"""
        model = model or self.current_model
        provider_name = self.MODEL_PROVIDERS.get(model)
        
        if not provider_name:
            return {"error": f"Unknown model: {model}"}
        
        provider_available = provider_name in self.providers
        
        return {
            "model": model,
            "provider": provider_name,
            "available": provider_available,
            "current": model == self.current_model
        }


class CodeAssistant:
    """High-level code assistant interface"""
    
    def __init__(self, llm_manager: LLMManager):
        """Initialize code assistant"""
        self.llm = llm_manager
    
    def suggest_code_improvements(self, code: str, language: str = None) -> str:
        """Suggest improvements for code"""
        system_prompt = """You are an expert code reviewer. Analyze the provided code and suggest specific improvements focusing on:
1. Code quality and readability
2. Performance optimizations
3. Best practices for the language
4. Security considerations
5. Error handling

Provide concrete suggestions with explanations."""
        
        prompt = f"Review this code"
        if language:
            prompt += f" ({language})"
        prompt += f":\n\n```\n{code}\n```"
        
        response = self.llm.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )
        
        return response.content
    
    def explain_code(self, code: str, language: str = None) -> str:
        """Explain what code does"""
        system_prompt = """You are a code documentation expert. Explain code clearly and concisely, covering:
1. Overall purpose and functionality
2. Key algorithms or logic
3. Input/output behavior
4. Important implementation details
5. Potential use cases

Write explanations that are accessible to developers at different skill levels."""
        
        prompt = f"Explain this code"
        if language:
            prompt += f" ({language})"
        prompt += f":\n\n```\n{code}\n```"
        
        response = self.llm.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )
        
        return response.content
    
    def generate_diff_suggestion(
        self,
        original_code: str,
        user_request: str,
        language: str = None,
        context: str = ""
    ) -> str:
        """Generate code diff suggestion"""
        system_prompt = f"""You are Claude Code, an AI coding assistant. Generate precise code modifications based on user requests.

Rules:
1. Provide specific, actionable code changes
2. Explain the reasoning behind changes
3. Use proper diff format when showing changes
4. Consider the broader context of the codebase
5. Follow best practices for the programming language

{context}"""
        
        prompt = f"I have this code"
        if language:
            prompt += f" ({language})"
        prompt += f":\n\n```\n{original_code}\n```\n\nUser request: {user_request}\n\nPlease suggest specific changes and explain your reasoning."
        
        response = self.llm.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4
        )
        
        return response.content
    
    def generate_test_cases(self, code: str, language: str = None) -> str:
        """Generate test cases for code"""
        system_prompt = """You are a test automation expert. Generate comprehensive test cases that cover:
1. Normal/expected behavior
2. Edge cases and boundary conditions
3. Error conditions and exception handling
4. Performance considerations (if applicable)

Use appropriate testing frameworks for the language and provide runnable test code."""
        
        prompt = f"Generate test cases for this code"
        if language:
            prompt += f" ({language})"
        prompt += f":\n\n```\n{code}\n```"
        
        response = self.llm.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4
        )
        
        return response.content
    
    def refactor_code(self, code: str, refactor_type: str, language: str = None) -> str:
        """Refactor code based on specific type"""
        system_prompt = f"""You are an expert code refactoring specialist. Perform {refactor_type} refactoring while:
1. Maintaining the same functionality
2. Improving code structure and readability
3. Following language-specific best practices
4. Providing clear before/after comparisons
5. Explaining the benefits of the changes"""
        
        prompt = f"Refactor this code"
        if language:
            prompt += f" ({language})"
        prompt += f" using {refactor_type} refactoring:\n\n```\n{code}\n```"
        
        response = self.llm.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4
        )
        
        return response.content