"""
External LLM API Wrapper
Provides a unified interface for calling external Language Model APIs.

Supports:
- OpenAI GPT models
- Mock mode for testing
- Custom endpoint configuration
- Error handling and retries
"""

import os
import time
from typing import Optional, Dict, Any
from enum import Enum

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[WARNING] 'requests' library not installed. Only mock mode available.")


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    MOCK = "mock"
    CUSTOM = "custom"


class LLMConfig:
    """Configuration for LLM API calls."""
    
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.MOCK,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        endpoint: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.provider = provider
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model
        self.endpoint = endpoint or self._get_default_endpoint()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
    
    def _get_default_endpoint(self) -> str:
        """Get default endpoint based on provider."""
        if self.provider == LLMProvider.OPENAI:
            return "https://api.openai.com/v1/chat/completions"
        return ""


# Global configuration instance
_global_config = LLMConfig()


def set_global_config(config: LLMConfig):
    """Set the global LLM configuration."""
    global _global_config
    _global_config = config


def get_global_config() -> LLMConfig:
    """Get the current global configuration."""
    return _global_config


def get_api_key() -> Optional[str]:
    """
    Get API key from configuration or environment.
    
    Returns:
        API key string or None if not found
    """
    config = get_global_config()
    
    if config.api_key:
        return config.api_key
    
    # Try to get from environment
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("\n" + "="*60)
        print("⚠️  No API key found in environment variables.")
        print("="*60)
        print("\nOptions:")
        print("1. Set environment variable: export LLM_API_KEY='your-key'")
        print("2. Use mock mode (for testing only)")
        print("3. Enter key now (will not be saved)\n")
        
        choice = input("Enter API key now or press Enter for mock mode: ").strip()
        
        if choice:
            config.api_key = choice
            return choice
        else:
            print("\n✓ Using mock mode for testing\n")
            config.provider = LLMProvider.MOCK
            return None
    
    return api_key


def llm_call(
    prompt: str,
    config: Optional[LLMConfig] = None,
    system_message: Optional[str] = None
) -> str:
    """
    Execute a call to an LLM API.
    
    Args:
        prompt: The user prompt/query
        config: Optional custom configuration (uses global if not provided)
        system_message: Optional system message for context
        
    Returns:
        The LLM response text
        
    Raises:
        RuntimeError: If API call fails after retries
    """
    if config is None:
        config = get_global_config()
    
    # Mock mode
    if config.provider == LLMProvider.MOCK or not REQUESTS_AVAILABLE:
        return _mock_llm_call(prompt)
    
    # Real API call
    if config.provider == LLMProvider.OPENAI:
        return _openai_call(prompt, config, system_message)
    
    # Custom provider
    if config.provider == LLMProvider.CUSTOM:
        return _custom_call(prompt, config, system_message)
    
    raise ValueError(f"Unsupported provider: {config.provider}")


def _mock_llm_call(prompt: str) -> str:
    """
    Mock LLM call for testing purposes.
    
    Provides simple rule-based responses for common patterns.
    """
    prompt_lower = prompt.lower()
    
    # Score queries
    if any(word in prompt_lower for word in ["score", "rate", "evaluate"]):
        return "0.85"
    
    # Analysis queries
    if any(word in prompt_lower for word in ["analyze", "analysis"]):
        return f"[MOCK ANALYSIS] Completed analysis of the requested task. Key factors identified and evaluated."
    
    # Execution queries
    if any(word in prompt_lower for word in ["execute", "run", "perform"]):
        return f"[MOCK EXECUTION] Task executed successfully. All steps completed as planned."
    
    # Validation queries
    if any(word in prompt_lower for word in ["validate", "verify", "check"]):
        return "[MOCK VALIDATION] Validation complete. Results meet expected criteria."
    
    # Default response
    return f"[MOCK OUTPUT] Processed request: {prompt[:60]}..."


def _openai_call(
    prompt: str,
    config: LLMConfig,
    system_message: Optional[str]
) -> str:
    """Call OpenAI API with retry logic."""
    if not config.api_key:
        config.api_key = get_api_key()
    
    if not config.api_key or config.api_key == "MOCK":
        return _mock_llm_call(prompt)
    
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": config.model,
        "messages": messages,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens
    }
    
    # Retry loop
    last_error = None
    for attempt in range(config.max_retries):
        try:
            response = requests.post(
                config.endpoint,
                headers=headers,
                json=data,
                timeout=config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < config.max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"[LLM API] Retry {attempt + 1}/{config.max_retries} after {wait_time}s...")
                time.sleep(wait_time)
    
    # All retries failed
    error_msg = f"LLM API call failed after {config.max_retries} attempts: {str(last_error)}"
    raise RuntimeError(error_msg)


def _custom_call(
    prompt: str,
    config: LLMConfig,
    system_message: Optional[str]
) -> str:
    """
    Call custom API endpoint.
    
    Users should implement their own logic here for custom providers.
    """
    raise NotImplementedError(
        "Custom provider not implemented. "
        "Please implement _custom_call() for your specific API."
    )


def test_connection(config: Optional[LLMConfig] = None) -> bool:
    """
    Test LLM API connection.
    
    Args:
        config: Optional configuration to test
        
    Returns:
        True if connection successful, False otherwise
    """
    if config is None:
        config = get_global_config()
    
    try:
        response = llm_call("Test connection", config)
        return bool(response)
    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
        return False


# CLI utility for testing
if __name__ == "__main__":
    print("="*60)
    print("HB-Eval System - LLM API Test Utility")
    print("="*60)
    
    # Test mock mode
    print("\n1. Testing MOCK mode:")
    set_global_config(LLMConfig(provider=LLMProvider.MOCK))
    result = llm_call("Analyze the current system performance")
    print(f"Response: {result}")
    
    # Test real API (if key available)
    print("\n2. Testing REAL API mode:")
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if api_key:
        set_global_config(LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key=api_key,
            model="gpt-3.5-turbo"
        ))
        
        if test_connection():
            print("✓ API connection successful!")
            result = llm_call("What is 2+2?")
            print(f"Response: {result}")
        else:
            print("✗ API connection failed")
    else:
        print("⚠️  No API key found. Skipping real API test.")
    
    print("\n" + "="*60)