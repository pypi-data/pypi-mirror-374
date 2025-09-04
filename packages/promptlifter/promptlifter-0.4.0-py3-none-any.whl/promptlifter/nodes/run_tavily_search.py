import logging

import httpx

from ..config import TAVILY_API_KEY

# Set up logging
logger = logging.getLogger(__name__)


async def run_tavily_search(task: str) -> str:
    """Run Tavily web search for a research task."""
    try:
        # Enhanced configuration validation
        if not TAVILY_API_KEY:
            logger.error("Tavily API key is not configured")
            return (
                "[Error: Tavily API key not configured - "
                "please set TAVILY_API_KEY in your .env file]"
            )

        if not TAVILY_API_KEY.strip():
            logger.error("Tavily API key is empty")
            return "[Error: Tavily API key is empty - " "please check your .env file]"

        # Log configuration status (without exposing the key)
        logger.info(f"Tavily search configured: {'Yes' if TAVILY_API_KEY else 'No'}")
        logger.info(f"Search query: {task[:50]}...")

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Use Authorization Bearer header instead of X-API-Key
            headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
            payload = {
                "query": task,
                "search_depth": "basic",
                "include_answer": False,
                "include_raw_content": False,
                "max_results": 5,
            }

            logger.info("Making Tavily API request...")
            response = await client.post(
                "https://api.tavily.com/search", json=payload, headers=headers
            )

            logger.info(f"Tavily response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                if not results:
                    logger.info("No Tavily results found")
                    return "[Info: No Tavily results found]"

                # Extract content from results
                content_parts = []
                for result in results:
                    content = result.get("content", "")
                    if content and content.strip():
                        content_parts.append(content)

                if not content_parts:
                    logger.info("No valid Tavily results found")
                    return "[Info: No valid Tavily results found]"

                logger.info(f"Tavily search successful: {len(content_parts)} results")
                return "\n\n".join(content_parts)
            elif response.status_code == 401:
                logger.error("Tavily API 401 Unauthorized - check your API key")
                return (
                    "[Error: Tavily API key is invalid or expired - "
                    "please check your TAVILY_API_KEY]"
                )
            elif response.status_code == 429:
                logger.error("Tavily API rate limit exceeded")
                return (
                    "[Error: Tavily API rate limit exceeded - "
                    "please try again later]"
                )
            else:
                logger.error(f"Tavily API error: {response.status_code}")
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", "Unknown error")
                    return (
                        f"[Error: Tavily search failed - "
                        f"{response.status_code}: {error_msg}]"
                    )
                except Exception:
                    return f"[Error: Tavily search failed - {response.status_code}]"

    except httpx.TimeoutException:
        logger.error("Tavily search timed out")
        return "[Error: Tavily search timed out]"
    except httpx.RequestError as e:
        logger.error(f"Tavily request error: {str(e)}")
        return f"[Error: Tavily request failed - {str(e)}]"
    except Exception as e:
        logger.error(f"Tavily search exception: {str(e)}")
        return f"[Error: Tavily search failed - {str(e)}]"
