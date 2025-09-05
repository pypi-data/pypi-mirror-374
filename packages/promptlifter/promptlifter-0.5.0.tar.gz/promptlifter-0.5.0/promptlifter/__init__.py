"""
PromptLifter - LLM-powered conversation interface with intelligent context management.

A simplified conversation-focused assistant that provides intelligent context
management, optional search integration, and optimized LLM interactions for
conversational AI.
"""

__version__ = "0.5.0"
__author__ = "PromptLifter Team"
__description__ = "LLM-powered conversation interface with context management"

from .config import validate_config
from .conversation_llm import ConversationConfig, ConversationLLM, quick_chat

__all__ = [
    # Main conversation interface
    "ConversationLLM",
    "ConversationConfig",
    "quick_chat",
    # Configuration
    "validate_config",
    # Package info
    "__version__",
    "__author__",
    "__description__",
]
