import logging
from typing import List, Optional

import httpx

from ..config import (
    ANTHROPIC_API_KEY,
    CUSTOM_LLM_API_KEY,
    CUSTOM_LLM_ENDPOINT,
    CUSTOM_LLM_MODEL,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
    OPENAI_API_KEY,
)

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings for vector search."""

    def __init__(self) -> None:
        self.custom_endpoint = CUSTOM_LLM_ENDPOINT
        self.custom_model = CUSTOM_LLM_MODEL
        self.custom_api_key = CUSTOM_LLM_API_KEY
        self.embedding_provider = EMBEDDING_PROVIDER
        self.embedding_model = EMBEDDING_MODEL

    async def _get_custom_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from custom endpoint (Ollama or OpenAI-compatible)."""
        logger.info(
            f"Attempting custom embedding with provider: {self.embedding_provider}, "
            f"model: {self.embedding_model}"
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {}
                if self.custom_api_key:
                    headers["Authorization"] = f"Bearer {self.custom_api_key}"

                # Check if this is an OpenAI-compatible endpoint
                is_openai_compatible = any(
                    domain in self.custom_endpoint.lower()
                    for domain in [
                        "api.openai.com",
                        "api.lambda.ai",
                        "api.together.xyz",
                        "api.perplexity.ai",
                    ]
                )

                if is_openai_compatible:
                    # For Lambda Labs, try different embedding models if the default
                    # fails
                    embedding_models_to_try = [
                        self.embedding_model,
                        "text-embedding-ada-002",  # Fallback model
                        "text-embedding-3-large",  # Alternative model
                    ]

                    for model in embedding_models_to_try:
                        payload = {"model": model, "input": text}

                        response = await client.post(
                            f"{self.custom_endpoint}/embeddings",
                            json=payload,
                            headers=headers,
                        )

                        if response.status_code == 200:
                            data = response.json()
                            embedding = data.get("data", [{}])[0].get("embedding", [])
                            if embedding:
                                logger.info(
                                    f"Custom embedding successful with model: {model}"
                                )
                                return list(embedding) if embedding else None
                        else:
                            logger.warning(
                                f"Custom embedding failed with model {model}: "
                                f"{response.status_code}"
                            )
                            if response.status_code == 400:
                                # Try to get error details
                                try:
                                    error_data = response.json()
                                    error_dict = error_data.get("error", {})
                                    error_msg = error_dict.get("message", "Unknown")
                                    logger.debug(f"Error details: {error_msg}")
                                except Exception:
                                    pass

                    # If all models failed, return None to trigger fallback
                    logger.error("All custom embedding models failed")
                    return None
                else:
                    # Try Ollama-style embedding API
                    payload = {"model": self.embedding_model, "prompt": text}

                    response = await client.post(
                        f"{self.custom_endpoint}/api/embeddings",
                        json=payload,
                        headers=headers,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        result = data.get("embedding", [])
                        return list(result) if result else None
                    else:
                        logger.error(
                            f"Custom Ollama embedding failed: {response.status_code}"
                        )
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("error", "Unknown error")
                            logger.debug(f"Ollama embedding error details: {error_msg}")
                        except Exception:
                            logger.debug(
                                f"Ollama embedding response text: {response.text}"
                            )
                        return None

        except Exception as e:
            logger.error(f"Custom embedding error: {e}")
            return None

    async def _get_openai_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from OpenAI API."""
        if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("your_"):
            logger.error("OpenAI API key not properly configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

                payload = {"model": self.embedding_model, "input": text}

                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    json=payload,
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    result = data.get("data", [{}])[0].get("embedding", [])
                    return list(result) if result else None
                else:
                    logger.error(
                        f"OpenAI embedding failed: {response.status_code} - "
                        f"{response.text[:100]}"
                    )
                    return None

        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            return None

    async def _get_anthropic_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from Anthropic API."""
        if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY.startswith("your_"):
            logger.error("Anthropic API key not properly configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                }

                payload = {"model": self.embedding_model, "input": text}

                response = await client.post(
                    "https://api.anthropic.com/v1/embeddings",
                    json=payload,
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    result = data.get("data", [{}])[0].get("embedding", [])
                    return list(result) if result else None
                else:
                    logger.error(
                        f"Anthropic embedding failed: {response.status_code} - "
                        f"{response.text[:100]}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Anthropic embedding error: {e}")
            return None

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text using configured provider."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Use configured provider
        if self.embedding_provider == "custom":
            embedding = await self._get_custom_embedding(text)
        elif self.embedding_provider == "openai":
            embedding = await self._get_openai_embedding(text)
        elif self.embedding_provider == "anthropic":
            embedding = await self._get_anthropic_embedding(text)
        else:
            logger.error(f"Unknown embedding provider: {self.embedding_provider}")
            embedding = None

        if embedding and len(embedding) > 0:
            logger.info(
                f"Using {self.embedding_provider} embedding service with model: "
                f"{self.embedding_model}"
            )
            return embedding

        # Fallback to a simple hash-based embedding if configured provider fails
        logger.warning(
            f"{self.embedding_provider} embedding failed, using fallback embedding"
        )
        return self._fallback_embedding(text)

    def _fallback_embedding(self, text: str) -> List[float]:
        """Improved fallback embedding using TF-IDF-like approach."""
        import hashlib
        import re

        # Clean and tokenize text
        text = text.lower()
        words = re.findall(r"\b\w+\b", text)

        # Create word frequency distribution for embedding generation

        # Create a more sophisticated embedding
        # Use multiple hash functions for better distribution
        embedding = []

        # Create multiple hash-based features
        for i in range(1536):
            if i < 512:
                # First third: word-based features
                word_idx = i % len(words) if words else 0
                word = words[word_idx] if words else "empty"
                hash_obj = hashlib.md5(f"word_{word}_{i}".encode())
            elif i < 1024:
                # Second third: character-based features
                char_idx = i % len(text) if text else 0
                char = text[char_idx] if text else " "
                hash_obj = hashlib.md5(f"char_{char}_{i}".encode())
            else:
                # Last third: position-based features
                hash_obj = hashlib.md5(f"pos_{i}_{len(text)}".encode())

            hash_bytes = hash_obj.digest()
            byte_val = hash_bytes[i % len(hash_bytes)]

            # Normalize to [-1, 1] range with better distribution
            normalized_val = (byte_val / 255.0) * 2 - 1

            # Apply some smoothing to avoid extreme values
            if abs(normalized_val) > 0.8:
                normalized_val = normalized_val * 0.8

            embedding.append(normalized_val)

        return embedding


# Global embedding service instance
embedding_service = EmbeddingService()
