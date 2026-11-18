"""
LLM service implementations for offline operation.

Provides mock and deterministic LLM implementations for 100% offline RAG.
"""

import asyncio
from typing import List, Dict, Any
from app.core.exceptions import LLMError
from app.domain.interfaces import LLMService
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockLLMService(LLMService):
    """
    Mock LLM service for offline operation.

    Generates contextual responses based on retrieval results.
    """

    def __init__(self, model_name: str = "mock-gpt"):
        """
        Initialize mock LLM service.

        Args:
            model_name: Name of the model
        """
        self.model_name = model_name
        self.temperature = 0.7
        logger.info(f"Initialized MockLLMService with model {model_name}")

    async def generate(
        self, prompt: str, max_tokens: int = 512, temperature: float = 0.7
    ) -> str:
        """
        Generate text using mock LLM.

        Args:
            prompt: Prompt text
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature

        Returns:
            str: Generated text

        Raises:
            LLMError: If generation fails
        """
        try:
            return await asyncio.to_thread(self._generate_sync, prompt, max_tokens)
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise LLMError(f"Failed to generate text: {str(e)}")

    def _generate_sync(self, prompt: str, max_tokens: int = 512) -> str:
        """
        Synchronous text generation.

        Extracts context from prompt and generates response.
        """
        # Parse context from prompt
        lines = prompt.split("\n")
        context_lines = []
        question = ""

        in_context = False
        for line in lines:
            if "Context:" in line:
                in_context = True
                continue
            elif "Question:" in line:
                in_context = False
                question = line.replace("Question:", "").strip()
                continue

            if in_context and line.strip():
                context_lines.append(line.strip())

        context = " ".join(context_lines[:3])  # Use first 3 lines of context

        # Generate response based on question and context
        responses = {
            "what": f"Based on the provided information: {context}. This addresses your question about what.",
            "how": f"Here's how to approach this: {context}. These steps should help you accomplish your goal.",
            "why": f"The reason for this is: {context}. This explains the underlying cause.",
            "when": f"The timing is important: {context}. This describes when events occur.",
            "where": f"The location is: {context}. This specifies where things happen.",
        }

        question_lower = question.lower()
        response = None

        for key in responses:
            if key in question_lower:
                response = responses[key]
                break

        if not response:
            response = f"Based on the context provided: {context}. This information is relevant to your question: {question}"

        # Truncate to max_tokens (rough approximation: 4 chars per token)
        max_chars = max_tokens * 4
        if len(response) > max_chars:
            response = response[:max_chars] + "..."

        logger.debug(f"Generated response of length {len(response)}")
        return response

    async def generate_with_history(
        self, messages: List[Dict[str, str]], max_tokens: int = 512
    ) -> str:
        """
        Generate response with conversation history.

        Args:
            messages: List of messages in conversation
            max_tokens: Maximum tokens to generate

        Returns:
            str: Generated response

        Raises:
            LLMError: If generation fails
        """
        try:
            return await asyncio.to_thread(
                self._generate_with_history_sync, messages, max_tokens
            )
        except Exception as e:
            logger.error(f"Error generating with history: {str(e)}")
            raise LLMError(f"Failed to generate with history: {str(e)}")

    def _generate_with_history_sync(
        self, messages: List[Dict[str, str]], max_tokens: int = 512
    ) -> str:
        """Synchronous generation with history."""
        if not messages:
            return "No messages provided."

        # Get last user message
        last_user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break

        if not last_user_message:
            return "Could not find user message to respond to."

        # Generate response
        response = f"I understand you asked: '{last_user_message}'. "
        response += "Based on our conversation history, here's my response: "
        response += "I've considered the context and here's what I can tell you."

        max_chars = max_tokens * 4
        if len(response) > max_chars:
            response = response[:max_chars] + "..."

        return response

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model": self.model_name,
            "type": "mock",
            "offline": True,
            "max_tokens": 2048,
        }


class DeterministicLLMService(LLMService):
    """
    Deterministic LLM service for offline operation.

    Generates reproducible responses from context.
    """

    def __init__(self, model_name: str = "deterministic-gpt"):
        """
        Initialize deterministic LLM service.

        Args:
            model_name: Name of the model
        """
        self.model_name = model_name
        logger.info(f"Initialized DeterministicLLMService with model {model_name}")

    async def generate(
        self, prompt: str, max_tokens: int = 512, temperature: float = 0.7
    ) -> str:
        """
        Generate text using deterministic LLM.

        Args:
            prompt: Prompt text
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature

        Returns:
            str: Generated text
        """
        try:
            return await asyncio.to_thread(self._generate_sync, prompt, max_tokens)
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise LLMError(f"Failed to generate text: {str(e)}")

    def _generate_sync(self, prompt: str, max_tokens: int = 512) -> str:
        """
        Synchronous deterministic text generation.

        Extracts content and synthesizes a response.
        """
        # Extract context from prompt structure
        sections = prompt.split("\n\n")
        context_sections = []

        for section in sections:
            if section.strip() and not section.startswith(("Context:", "Question:")):
                context_sections.append(section.strip())

        # Build response from context
        if context_sections:
            context_text = " ".join(context_sections[:2])
            response = f"Based on the provided information: {context_text}\n\n"
            response += "This information directly addresses your query. "
            response += "The key points are: the content is relevant and comprehensive."
        else:
            response = "The provided context is relevant to your question. "
            response += "I can offer the following insights based on the information given."

        # Ensure we don't exceed max_tokens
        max_chars = max_tokens * 4
        if len(response) > max_chars:
            response = response[:max_chars].rsplit(" ", 1)[0] + "..."

        return response

    async def generate_with_history(
        self, messages: List[Dict[str, str]], max_tokens: int = 512
    ) -> str:
        """
        Generate response with conversation history.

        Args:
            messages: List of messages in conversation
            max_tokens: Maximum tokens to generate

        Returns:
            str: Generated response
        """
        try:
            return await asyncio.to_thread(
                self._generate_with_history_sync, messages, max_tokens
            )
        except Exception as e:
            logger.error(f"Error generating with history: {str(e)}")
            raise LLMError(f"Failed to generate: {str(e)}")

    def _generate_with_history_sync(
        self, messages: List[Dict[str, str]], max_tokens: int = 512
    ) -> str:
        """Synchronous generation with history."""
        # Count messages for context
        user_messages = sum(1 for m in messages if m.get("role") == "user")
        assistant_messages = sum(1 for m in messages if m.get("role") == "assistant")

        response = f"Thank you for continuing our conversation. "
        response += f"I see we've had {user_messages} user messages. "

        if assistant_messages > 0:
            response += f"Based on our exchange so far, "

        response += "I can provide you with a comprehensive response. "
        response += "Please feel free to ask clarifying questions if needed."

        max_chars = max_tokens * 4
        if len(response) > max_chars:
            response = response[:max_chars].rsplit(" ", 1)[0] + "..."

        return response

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model": self.model_name,
            "type": "deterministic",
            "offline": True,
            "max_tokens": 2048,
        }


class LLMServiceFactory:
    """Factory for creating LLM service instances."""

    @staticmethod
    def create(model_type: str = "mock") -> LLMService:
        """
        Create LLM service instance.

        Args:
            model_type: Type of LLM service (mock, deterministic)

        Returns:
            LLMService: LLM service instance

        Raises:
            LLMError: If model type is not supported
        """
        if model_type == "mock":
            return MockLLMService()
        elif model_type == "deterministic":
            return DeterministicLLMService()
        else:
            raise LLMError(f"Unknown LLM model type: {model_type}")
