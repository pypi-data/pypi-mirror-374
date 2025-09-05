import logging
from typing import Any

from pinecone import Pinecone

from ..config import (
    PINECONE_API_KEY,
    PINECONE_FILTER_BY_SCORE,
    PINECONE_INCLUDE_SCORES,
    PINECONE_INDEX,
    PINECONE_NAMESPACE,
    PINECONE_SIMILARITY_THRESHOLD,
    PINECONE_TOP_K,
)
from .embedding_service import embedding_service

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Pinecone client lazily to avoid import-time errors
_pc_client = None


def _get_pinecone_client() -> Any:
    """Get or create Pinecone client instance."""
    global _pc_client
    if _pc_client is None:
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not configured")
        _pc_client = Pinecone(api_key=PINECONE_API_KEY)
    return _pc_client


async def run_pinecone_search(task: str) -> str:
    """Run Pinecone vector search for a research task with relevance scoring."""
    try:
        # Enhanced configuration validation
        if not PINECONE_API_KEY:
            logger.error("Pinecone API key is not configured")
            return (
                "[Error: Pinecone API key not configured - "
                "please set PINECONE_API_KEY in your .env file]"
            )

        if not PINECONE_INDEX:
            logger.error("Pinecone index is not configured")
            return (
                "[Error: Pinecone index not configured - "
                "please set PINECONE_INDEX in your .env file]"
            )

        if not PINECONE_API_KEY.strip():
            logger.error("Pinecone API key is empty")
            return "[Error: Pinecone API key is empty - " "please check your .env file]"

        # Log configuration status
        logger.info(f"Pinecone configured: {'Yes' if PINECONE_API_KEY else 'No'}")
        logger.info(f"Pinecone index: {PINECONE_INDEX}")
        logger.info(f"Similarity threshold: {PINECONE_SIMILARITY_THRESHOLD}")
        logger.info(f"Filter by score: {PINECONE_FILTER_BY_SCORE}")
        logger.info(f"Search query: {task[:50]}...")

        # Get the index
        try:
            pc_client = _get_pinecone_client()
            index = pc_client.Index(PINECONE_INDEX)
            logger.info("Successfully connected to Pinecone index")
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone index: {str(e)}")
            return f"[Error: Failed to connect to Pinecone index - {str(e)}]"

        # Generate proper embedding for the search query
        logger.info("Generating embedding for search query...")
        query_vector = await embedding_service.embed_text(task)

        if not query_vector:
            logger.error("Failed to generate embedding for search query")
            return "[Error: Failed to generate embedding for search query]"

        logger.info("Embedding generated successfully")

        # Perform vector search with configurable parameters
        logger.info(f"Performing Pinecone search with top_k={PINECONE_TOP_K}")
        response = index.query(
            vector=query_vector,
            top_k=PINECONE_TOP_K,
            include_metadata=True,
            include_values=False,  # Don't include vectors in response
            namespace=PINECONE_NAMESPACE,
        )

        matches = response.get("matches", [])
        logger.info(f"Pinecone returned {len(matches)} matches")

        if not matches:
            logger.info("No Pinecone results found")
            return "[Info: No Pinecone results found]"

        # Process matches with relevance scoring
        content_parts = []
        filtered_count = 0

        for i, match in enumerate(matches):
            score = match.get("score", 0.0)
            metadata = match.get("metadata", {})
            text = metadata.get("text", "")

            logger.info(f"Match {i+1}: score={score:.3f}, text_length={len(text)}")

            # Handle negative scores (common with hash-based embeddings)
            # For negative scores, we'll use a more lenient threshold or accept all
            # results
            effective_threshold = PINECONE_SIMILARITY_THRESHOLD

            # If scores are negative, adjust threshold logic
            if score < 0:
                logger.info(
                    f"Negative score detected ({score:.3f}), using lenient filtering"
                )
                # For negative scores, accept if they're above -0.3 (closer to 0 is
                # better)
                effective_threshold = -0.3
            elif score < 0.3:
                # For low positive scores (common with OpenAI embeddings), be more
                # lenient
                logger.info(
                    f"Low score detected ({score:.3f}), using lenient filtering"
                )
                effective_threshold = 0.2
            elif score < 0.5:
                # For medium scores, use a moderate threshold
                logger.info(
                    f"Medium score detected ({score:.3f}), using moderate filtering"
                )
                effective_threshold = 0.3

            # Filter by similarity threshold if enabled
            if PINECONE_FILTER_BY_SCORE and score < effective_threshold:
                filtered_count += 1
                logger.info(
                    f"Filtered out match {i+1} due to low score "
                    f"({score:.3f} < {effective_threshold})"
                )
                continue

            # Skip empty or None text
            if not text or not text.strip():
                logger.info(f"Skipping match {i+1} due to empty text")
                continue

            # Format the result with optional score inclusion
            if PINECONE_INCLUDE_SCORES:
                content_parts.append(f"[Score: {score:.3f}] {text}")
            else:
                content_parts.append(text)

        if not content_parts:
            if filtered_count > 0:
                logger.info(
                    f"All {filtered_count} results filtered out due to low similarity"
                )
                return (
                    f"[Info: {filtered_count} results filtered out due to low "
                    f"similarity (threshold: {PINECONE_SIMILARITY_THRESHOLD})]"
                )
            else:
                logger.info("No valid Pinecone results found")
                return "[Info: No valid Pinecone results found]"

        # Add summary information
        summary = f"Found {len(content_parts)} relevant results"
        if PINECONE_FILTER_BY_SCORE and filtered_count > 0:
            summary += f" (filtered out {filtered_count} low-similarity results)"

        if PINECONE_INCLUDE_SCORES:
            summary += f" [Similarity threshold: {PINECONE_SIMILARITY_THRESHOLD}]"

        logger.info(f"Pinecone search successful: {summary}")
        return f"{summary}\n\n" + "\n\n".join(content_parts)

    except Exception as e:
        logger.error(f"Pinecone search exception: {str(e)}")
        return f"[Error: Pinecone search failed - {str(e)}]"
