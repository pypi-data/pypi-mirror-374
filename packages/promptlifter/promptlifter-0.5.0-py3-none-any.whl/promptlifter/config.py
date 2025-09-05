import os
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_config() -> list[str]:
    """Validate configuration settings."""
    errors = []

    # Validate custom LLM endpoint
    custom_endpoint = os.getenv("CUSTOM_LLM_ENDPOINT", "http://localhost:11434")
    if not validate_url(custom_endpoint):
        errors.append("CUSTOM_LLM_ENDPOINT must be a valid URL")

    # Validate model name
    custom_model = os.getenv("CUSTOM_LLM_MODEL", "llama3.1")
    if not custom_model or len(custom_model.strip()) == 0:
        errors.append("CUSTOM_LLM_MODEL cannot be empty")

    # Check for at least one LLM provider
    llm_providers = [
        os.getenv("CUSTOM_LLM_ENDPOINT") and os.getenv("CUSTOM_LLM_MODEL"),
        os.getenv("OPENAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("GOOGLE_API_KEY"),
    ]

    if not any(llm_providers):
        errors.append("At least one LLM provider must be configured")

    return errors


# Custom LLM Configuration (Primary)
CUSTOM_LLM_ENDPOINT = os.getenv(
    "CUSTOM_LLM_ENDPOINT", "http://localhost:11434"
)  # Default to Ollama
CUSTOM_LLM_MODEL = os.getenv("CUSTOM_LLM_MODEL", "llama3.1")  # Default to Llama 3.1
CUSTOM_LLM_API_KEY = os.getenv(
    "CUSTOM_LLM_API_KEY", ""
)  # Optional API key for custom endpoints

# Embedding Configuration
EMBEDDING_PROVIDER = os.getenv(
    "EMBEDDING_PROVIDER", "custom"
)  # custom, openai, anthropic
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "text-embedding-3-small"
)  # Model name for embeddings

# Commercial LLM Configuration (Fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Search and Vector Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
PINECONE_NAMESPACE = os.getenv(
    "PINECONE_NAMESPACE", "research"
)  # Default to "research"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Pinecone Search Configuration
PINECONE_TOP_K = int(os.getenv("PINECONE_TOP_K", "10"))  # Number of results to retrieve
PINECONE_SIMILARITY_THRESHOLD = float(
    os.getenv("PINECONE_SIMILARITY_THRESHOLD", "0.7")
)  # Minimum similarity score
PINECONE_INCLUDE_SCORES = (
    os.getenv("PINECONE_INCLUDE_SCORES", "true").lower() == "true"
)  # Include scores in output
PINECONE_FILTER_BY_SCORE = (
    os.getenv("PINECONE_FILTER_BY_SCORE", "true").lower() == "true"
)  # Filter results by score

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "custom")  # custom, openai, anthropic, google

# Conversation Context Settings
MAX_HISTORY_TOKENS = int(
    os.getenv("MAX_HISTORY_TOKENS", "4000")
)  # Maximum tokens for conversation history
MAX_CONTEXT_TOKENS = int(
    os.getenv("MAX_CONTEXT_TOKENS", "2000")
)  # Maximum tokens for context assembly
ENABLE_AUTO_SEARCH = (
    os.getenv("ENABLE_AUTO_SEARCH", "true").lower() == "true"
)  # Enable automatic search
SEARCH_RELEVANCE_THRESHOLD = float(
    os.getenv("SEARCH_RELEVANCE_THRESHOLD", "0.7")
)  # Minimum relevance score for search results
