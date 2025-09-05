"""
Query Classifier for determining if search is needed using LLM-based classification.

This module provides intelligent query classification using a specialized LLM system
prompt to determine whether external search is needed for a given query and
conversation context.
"""

import json
import logging
from typing import Any, Dict

from ..nodes.llm_service import llm_service

logger = logging.getLogger(__name__)


class QueryClassifier:
    """
    LLM-based query classifier for determining search necessity.

    Uses a specialized system prompt to analyze queries and conversation
    context to determine if external search is needed.
    """

    def __init__(self) -> None:
        """Initialize the query classifier."""
        self.system_prompt = self._create_classification_prompt()
        logger.info("QueryClassifier initialized with LLM-based classification")

    def _create_classification_prompt(self) -> str:
        """Create the specialized system prompt for query classification."""
        prompt_parts = [
            "You are a specialized query classifier for determining whether",
            " external search is needed for user queries.\n\n",
            "Your task is to analyze a user query and conversation history",
            " to determine if the query requires external search (web search,",
            " knowledge base, etc.) or if it can be answered using only the",
            " conversation context.\n\n",
            "CLASSIFICATION CRITERIA:\n\n",
            "SEARCH NEEDED (return true) when:\n",
            "- Query asks for current/recent information (news, weather,",
            " stock prices, etc.)\n",
            "- Query requests specific data, statistics, or research\n",
            "- Query asks for comparisons between entities\n",
            "- Query is about topics not covered in conversation history\n",
            "- Query is very short and lacks context\n",
            "- Query asks for factual information that changes frequently\n\n",
            "NO SEARCH NEEDED (return false) when:\n",
            "- Query is conversational/greeting (hello, how are you,",
            " thanks, etc.)\n",
            "- Query is a follow-up to previous conversation (examples,",
            " clarifications, elaborations)\n",
            "- Query can be answered from existing conversation context\n",
            "- Query is asking for explanations of previously discussed",
            " topics\n",
            "- Query is asking for more details about something already",
            " mentioned\n\n",
            "CONVERSATION CONTEXT ANALYSIS:\n",
            "- If conversation history is substantial (>50 words), be more",
            " conservative about search\n",
            '- Look for follow-up patterns: "give me an example",',
            ' "tell me more", "what about", "five day forecast"\n',
            "- Consider if the query relates to previously discussed topics",
            " or locations\n\n",
            "ENHANCED QUERY GENERATION:\n",
            "When should_search is true, create an enhanced_query that",
            " includes:\n",
            "- The original query\n",
            "- Relevant context from conversation history (locations,",
            " topics, entities)\n",
            "- Additional keywords that would improve search results\n",
            "- Examples:\n",
            '  * "What is five day forecast?" + history mentioning "Dallas"',
            ' → "What is five day forecast Dallas"\n',
            '  * "Tell me more about it" + history about "machine learning"',
            ' → "Tell me more about machine learning"\n',
            '  * "What\'s the price?" + history about "iPhone 15"',
            ' → "What\'s the price iPhone 15"\n\n',
            "RESPONSE FORMAT:\n",
            "Return ONLY a JSON object with this exact structure:\n",
            "{\n",
            '    "should_search": true/false,\n',
            '    "reasoning": "Brief explanation of the decision",\n',
            '    "confidence": 0.0-1.0,\n',
            '    "enhanced_query": "Enhanced search query with relevant',
            ' context (only if should_search is true, otherwise null)"\n',
            "}\n\n",
            "Examples:\n",
            'Query: "What is the weather in Dallas?"\n',
            'History: ""\n',
            'Response: {"should_search": true, "reasoning": "Current weather',
            ' information needed", "confidence": 0.9, "enhanced_query":',
            ' "What is the weather in Dallas?"}\n\n',
            'Query: "What is five day forecast?"\n',
            'History: "User: What is Dallas current weather? Assistant:',
            ' The current weather in Dallas is..."\n',
            'Response: {"should_search": true, "reasoning": "Follow-up',
            ' forecast request needs search", "confidence": 0.8,',
            ' "enhanced_query": "What is five day forecast Dallas"}\n\n',
            'Query: "Hello, how are you?"\n',
            'History: "Previous conversation..."\n',
            'Response: {"should_search": false, "reasoning":',
            ' "Conversational greeting", "confidence": 0.95,',
            ' "enhanced_query": null}',
        ]
        return "".join(prompt_parts)

    async def classify_query(
        self, query: str, conversation_history: str = ""
    ) -> Dict[str, Any]:
        """
        Classify whether a query needs external search.

        Args:
            query: The user query to classify
            conversation_history: Existing conversation context

        Returns:
            Dictionary with classification results:
            {
                "should_search": bool,
                "reasoning": str,
                "confidence": float
            }
        """
        try:
            # Prepare the classification request
            history_text = (
                conversation_history
                if conversation_history
                else "No conversation history available."
            )
            user_message = (
                f'Query to classify: "{query}"\n\n'
                f"Conversation History:\n{history_text}\n\n"
                "Classify this query and return the JSON response."
            )

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ]

            logger.info(f"Classifying query: {query[:50]}...")

            # Get classification from LLM
            response = await llm_service.generate(messages, max_tokens=200)

            # Parse the JSON response
            try:
                # Extract JSON from response (handle potential extra text)
                json_start = response.find("{")
                json_end = response.rfind("}") + 1

                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    classification = json.loads(json_str)

                    # Validate the response structure
                    if all(
                        key in classification
                        for key in [
                            "should_search",
                            "reasoning",
                            "confidence",
                            "enhanced_query",
                        ]
                    ):
                        logger.info(f"Classification result: {classification}")
                        return Dict[str, Any](classification)
                    else:
                        logger.warning(
                            f"Invalid classification structure: {classification}"
                        )
                else:
                    logger.warning(f"Could not extract JSON from response: {response}")

            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse classification JSON: {e}, "
                    f"response: {response}"
                )

            # Fallback to default classification
            return self._fallback_classification(query, conversation_history)

        except Exception as e:
            logger.error(f"Query classification failed: {e}")
            return self._fallback_classification(query, conversation_history)

    def _fallback_classification(
        self, query: str, conversation_history: str
    ) -> Dict[str, Any]:
        """
        Fallback classification when LLM classification fails.

        Args:
            query: The user query
            conversation_history: Existing conversation context

        Returns:
            Fallback classification result
        """
        query_lower = query.lower()

        # Simple fallback logic
        conversational_patterns = [
            "hello",
            "hi",
            "hey",
            "how are you",
            "thanks",
            "thank you",
            "goodbye",
            "bye",
        ]

        search_indicators = [
            "latest",
            "recent",
            "current",
            "new",
            "today",
            "weather",
            "forecast",
            "news",
            "price",
            "cost",
            "research",
            "data",
            "statistics",
        ]

        # Check for conversational patterns
        for pattern in conversational_patterns:
            if pattern in query_lower:
                return {
                    "should_search": False,
                    "reasoning": "Conversational query detected",
                    "confidence": 0.7,
                    "enhanced_query": None,
                }

        # Check for search indicators
        for indicator in search_indicators:
            if indicator in query_lower:
                return {
                    "should_search": True,
                    "reasoning": f"Search indicator detected: {indicator}",
                    "confidence": 0.7,
                    "enhanced_query": query,  # Use original query as fallback
                }

        # Default based on conversation history
        has_history = conversation_history and len(conversation_history.split()) > 50

        if has_history:
            return {
                "should_search": False,
                "reasoning": "Sufficient conversation history available",
                "confidence": 0.6,
                "enhanced_query": None,
            }
        else:
            return {
                "should_search": True,
                "reasoning": "Limited conversation history",
                "confidence": 0.6,
                "enhanced_query": query,  # Use original query as fallback
            }

    async def should_use_search(
        self, query: str, conversation_history: str = ""
    ) -> bool:
        """
        Determine if search is needed (main interface method).

        Args:
            query: Current user query
            conversation_history: Existing conversation context

        Returns:
            True if search should be used
        """
        classification = await self.classify_query(query, conversation_history)
        return bool(classification["should_search"])

    async def get_enhanced_search_query(
        self, query: str, conversation_history: str = ""
    ) -> str:
        """
        Get enhanced search query with context (only if search is needed).

        Args:
            query: Current user query
            conversation_history: Existing conversation context

        Returns:
            Enhanced search query if search is needed, otherwise original query
        """
        classification = await self.classify_query(query, conversation_history)

        if classification["should_search"] and classification["enhanced_query"]:
            return str(classification["enhanced_query"])
        else:
            return query
