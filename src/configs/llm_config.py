import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# LLM Provider Configuration
LLM_PROVIDERS = {
    "openai": {
        "base_url": "https://openrouter.ai/api/v1",
        "class": ChatOpenAI,
        "models": {
            "gpt-4o-mini": {"api_key_env": "OPENAI_API_KEY"},
            "gpt-4.1-mini": {"api_key_env": "OPENAI_API_KEY"},
            "gpt-4o": {"api_key_env": "OPENAI_API_KEY"},
            "gpt-4.1": {"api_key_env": "OPENAI_API_KEY"}
        }
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "class": ChatGoogleGenerativeAI,
        "models": {
            "gemini-1.5-flash": {"api_key_env": "GEMINI_API_KEY"},
            "gemini-1.5-pro": {"api_key_env": "GEMINI_API_KEY"},
            "gemini-2.0-flash": {"api_key_env": "GEMINI_API_KEY"},
            "gemini-2.0-flash-lite": {"api_key_env": "GEMINI_API_KEY"}
        }
    }
}

def get_llm(
    provider: str,
    model: str,
    temperature: float = 0.1,
    base_url: Optional[str] = None,
    **kwargs
):
    """
    Factory function to get an LLM instance based on provider and model.
    
    Args:
        provider: LLM provider ('openai', 'gemini')
        model: Specific model name
        temperature: Model temperature
        base_url: Optional base URL to override provider default
        **kwargs: Additional model parameters
    
    Returns:
        LLM instance
    """
    # Validate provider
    if provider not in LLM_PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider}. Available: {list(LLM_PROVIDERS.keys())}")
    
    provider_config = LLM_PROVIDERS[provider]

    # Use provider's base_url if not explicitly provided
    if base_url is None:
        base_url = provider_config.get("base_url")
    
    # Validate model for the provider
    if model not in provider_config["models"]:
        available_models = list(provider_config["models"].keys())
        raise ValueError(f"Unsupported model '{model}' for provider '{provider}'. Available: {available_models}")
    
    model_config = provider_config["models"][model]
    llm_class = provider_config["class"]
    
    # Get API key
    api_key_env = model_config["api_key_env"]
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        raise ValueError(f"API key not found in environment variable: {api_key_env}")
    
    # Prepare initialization parameters
    init_params = {
        "model": model,
        "temperature": temperature,
        **kwargs
    }
    
    # Add provider-specific API key parameter
    if provider == "openai":
        init_params["openai_api_key"] = api_key
        init_params["base_url"] = base_url
    elif provider == "gemini":
        init_params["google_api_key"] = api_key
    
    # Create and return LLM instance
    try:
        return llm_class(**init_params)
    except Exception as e:
        raise ValueError(f"Failed to initialize {provider} LLM with model {model}: {str(e)}")

def list_available_models() -> Dict[str, list]:
    """
    List all available models for each provider.
    
    Returns:
        Dictionary with providers as keys and list of models as values
    """
    return {
        provider: list(config["models"].keys())
        for provider, config in LLM_PROVIDERS.items()
    }

# Convenience function for getting default LLM
def get_default_llm():
    """Get LLM with default configuration from environment variables."""
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    return get_llm(provider=provider, model=model, temperature=temperature)

# For backward compatibility and specific use cases
def get_openai_llm(model: str = "gpt-3.5-turbo", temperature: float = 0.1):
    """Get OpenAI LLM instance."""
    return get_llm(provider="openai", model=model, temperature=temperature)

def get_gemini_llm(model: str = "gemini-2.0-flash", temperature: float = 0.1):
    """Get Gemini LLM instance."""
    return get_llm(provider="gemini", model=model, temperature=temperature) 