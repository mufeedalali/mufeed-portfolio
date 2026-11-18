"""
Chat service for multi-turn conversation.

Maintains conversation history and provides contextual responses.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.exceptions import ValidationError
from app.domain.models import ChatMessage, RAGResponse
from app.services.rag_service import RAGService
from app.core.logging import get_logger
import uuid

logger = get_logger(__name__)


class ChatService:
    """
    Service for managing chat conversations.

    Maintains conversation history and coordinates RAG generation.
    """

    def __init__(self, rag_service: RAGService):
        """
        Initialize chat service.

        Args:
            rag_service: RAG service for generating answers
        """
        self.rag_service = rag_service
        self.conversations: Dict[str, List[ChatMessage]] = {}
        logger.info("Initialized ChatService")

    async def create_conversation(self) -> str:
        """
        Create a new conversation.

        Returns:
            str: Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = []
        logger.info(f"Created conversation: {conversation_id}")
        return conversation_id

    async def send_message(
        self, conversation_id: str, user_message: str
    ) -> Dict[str, Any]:
        """
        Send a message in a conversation.

        Args:
            conversation_id: ID of conversation
            user_message: User's message

        Returns:
            Dict[str, Any]: Response with generated message and metadata

        Raises:
            ValidationError: If conversation not found
        """
        try:
            if conversation_id not in self.conversations:
                raise ValidationError(f"Conversation not found: {conversation_id}")

            # Add user message
            user_msg = ChatMessage(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role="user",
                content=user_message,
            )
            self.conversations[conversation_id].append(user_msg)
            logger.info(f"Added user message to conversation {conversation_id}")

            # Generate response using RAG
            rag_response = await self.rag_service.query(user_message)

            # Add assistant message
            assistant_msg = ChatMessage(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role="assistant",
                content=rag_response.answer,
                metadata={
                    "sources": rag_response.sources,
                    "confidence": rag_response.confidence_score,
                    "generation_time_ms": rag_response.generation_time_ms,
                },
            )
            self.conversations[conversation_id].append(assistant_msg)
            logger.info(f"Added assistant message to conversation {conversation_id}")

            return {
                "message_id": assistant_msg.id,
                "content": assistant_msg.content,
                "sources": rag_response.sources,
                "confidence": rag_response.confidence_score,
                "generation_time_ms": rag_response.generation_time_ms,
            }

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

    async def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history.

        Args:
            conversation_id: ID of conversation

        Returns:
            List[Dict[str, Any]]: Conversation messages

        Raises:
            ValidationError: If conversation not found
        """
        if conversation_id not in self.conversations:
            raise ValidationError(f"Conversation not found: {conversation_id}")

        messages = []
        for msg in self.conversations[conversation_id]:
            messages.append(
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata,
                }
            )

        return messages

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: ID of conversation

        Returns:
            bool: True if successful

        Raises:
            ValidationError: If conversation not found
        """
        if conversation_id not in self.conversations:
            raise ValidationError(f"Conversation not found: {conversation_id}")

        del self.conversations[conversation_id]
        logger.info(f"Deleted conversation: {conversation_id}")
        return True

    async def get_all_conversations(self) -> List[Dict[str, Any]]:
        """
        Get all conversations.

        Returns:
            List[Dict[str, Any]]: List of conversations with metadata
        """
        conversations = []

        for conv_id, messages in self.conversations.items():
            if messages:
                last_message = messages[-1]
                conversations.append(
                    {
                        "id": conv_id,
                        "message_count": len(messages),
                        "last_message": last_message.content[:100],
                        "last_timestamp": last_message.timestamp.isoformat(),
                    }
                )

        return conversations

    async def clear_old_conversations(self, max_age_hours: int = 24) -> int:
        """
        Clear conversations older than specified age.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            int: Number of conversations cleared
        """
        now = datetime.now()
        max_age_seconds = max_age_hours * 3600
        cleared = 0

        conv_ids_to_delete = []
        for conv_id, messages in self.conversations.items():
            if messages:
                last_message_time = messages[-1].timestamp
                age_seconds = (now - last_message_time).total_seconds()

                if age_seconds > max_age_seconds:
                    conv_ids_to_delete.append(conv_id)

        for conv_id in conv_ids_to_delete:
            del self.conversations[conv_id]
            cleared += 1

        logger.info(f"Cleared {cleared} old conversations")
        return cleared
