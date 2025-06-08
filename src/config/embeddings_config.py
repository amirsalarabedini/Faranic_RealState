import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from openai import OpenAI

# Load environment variables
load_dotenv()

class SimpleOpenAIEmbeddings(Embeddings):
    """Custom embeddings class that works reliably with Metis API"""
    
    def __init__(self, model: str = "text-embedding-3-small", base_url: str = "https://api.metisai.ir/openai/v1", api_key: str = None):
        self.model = model
        self.base_url = base_url
        self.client = OpenAI(
            api_key=api_key or os.getenv("METIS_API_KEY"),
            base_url=base_url
        )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model,
                encoding_format="float",
                dimensions=1024
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise ValueError(f"Failed to embed documents: {str(e)}")
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model,
                encoding_format="float",
                dimensions=1024
            )
            return response.data[0].embedding
        except Exception as e:
            raise ValueError(f"Failed to embed query: {str(e)}")

# Embeddings Provider Configuration
EMBEDDINGS_PROVIDERS = {
    "openai": {
        "base_url": "https://api.metisai.ir/openai/v1",
        "class": SimpleOpenAIEmbeddings,
        "models": {
            "text-embedding-3-small": {"api_key_env": "METIS_API_KEY"},
            "text-embedding-3-large": {"api_key_env": "METIS_API_KEY"}
        }
    }
    
}

# Default configuration - can be overridden by environment variables
DEFAULT_EMBEDDINGS_CONFIG = {
    "base_url": "https://api.metisai.ir/openai/v1",  # Use Metis API
    "provider": os.getenv("EMBEDDINGS_PROVIDER", "openai"),
    "model": os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small"),
    "chunk_size": int(os.getenv("EMBEDDINGS_CHUNK_SIZE", "1000"))
}

def get_embeddings(
    base_url: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    chunk_size: Optional[int] = None,
    **kwargs
):
    """
    Factory function to get an embeddings instance based on provider and model.
    
    Args:
        base_url: API base URL
        provider: Embeddings provider ('openai')
        model: Specific model name
        chunk_size: Chunk size for embeddings
        **kwargs: Additional model parameters
    
    Returns:
        Embeddings instance
    """
    # Use provided values or fall back to defaults
    base_url = base_url or DEFAULT_EMBEDDINGS_CONFIG["base_url"]
    provider = provider or DEFAULT_EMBEDDINGS_CONFIG["provider"]
    model = model or DEFAULT_EMBEDDINGS_CONFIG["model"]
    chunk_size = chunk_size if chunk_size is not None else DEFAULT_EMBEDDINGS_CONFIG["chunk_size"]
    
    # Validate provider
    if provider not in EMBEDDINGS_PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider}. Available: {list(EMBEDDINGS_PROVIDERS.keys())}")
    
    provider_config = EMBEDDINGS_PROVIDERS[provider]
    
    # Validate model for the provider
    if model not in provider_config["models"]:
        available_models = list(provider_config["models"].keys())
        raise ValueError(f"Unsupported model '{model}' for provider '{provider}'. Available: {available_models}")
    
    model_config = provider_config["models"][model]
    embeddings_class = provider_config["class"]
    
    # Get API key
    api_key_env = model_config["api_key_env"]
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        raise ValueError(f"API key not found in environment variable: {api_key_env}")
    
    # Prepare initialization parameters
    init_params = {
        "model": model,
        "base_url": base_url,
        "api_key": api_key
    }
    
    # Create and return embeddings instance
    try:
        return embeddings_class(**init_params)
    except Exception as e:
        raise ValueError(f"Failed to initialize {provider} embeddings with model {model}: {str(e)}")

def list_available_embeddings_models() -> Dict[str, list]:
    """
    List all available embeddings models for each provider.
    
    Returns:
        Dictionary with providers as keys and list of models as values
    """
    return {
        provider: list(config["models"].keys())
        for provider, config in EMBEDDINGS_PROVIDERS.items()
    }

def get_current_embeddings_config() -> Dict[str, Any]:
    """
    Get the current embeddings configuration.
    
    Returns:
        Current configuration dictionary
    """
    return DEFAULT_EMBEDDINGS_CONFIG.copy()

# Convenience function for getting default embeddings
def get_default_embeddings():
    """Get embeddings with default configuration."""
    return get_embeddings()

# For backward compatibility and specific use cases
def get_openai_embeddings(model: str = "text-embedding-3-small", chunk_size: int = 1000):
    """Get OpenAI embeddings instance."""
    return get_embeddings(provider="openai", model=model, chunk_size=chunk_size) 