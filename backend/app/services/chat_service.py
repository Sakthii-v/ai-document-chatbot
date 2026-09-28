from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.logging_config import logger
from app.core.exceptions import NotFoundError
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.rag_service import RAGService


class ChatService:
    def __init__(self, db: Session, rag_service: RAGService = None):
        self.db = db
        self.rag_service = rag_service or RAGService()

    def create_conversation(self, title: Optional[str] = "New Conversation") -> Conversation:
        """Create a new conversation session."""
        conv = Conversation(title=title)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        logger.info(f"Created conversation id={conv.id} title='{conv.title}'")
        return conv

    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all conversations ordered by updated_at with message counts."""
        conversations = self.db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
        result = []
        for conv in conversations:
            result.append({
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": len(conv.messages)
            })
        return result

    def get_conversation(self, conversation_id: int) -> Conversation:
        """Get conversation by ID."""
        conv = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            raise NotFoundError(f"Conversation with ID {conversation_id} not found.")
        return conv

    def delete_conversation(self, conversation_id: int) -> dict:
        """Delete conversation and all its messages."""
        conv = self.get_conversation(conversation_id)
        self.db.delete(conv)
        self.db.commit()
        logger.info(f"Deleted conversation_id={conversation_id}")
        return {"success": True, "message": f"Conversation {conversation_id} deleted successfully."}

    def get_messages(self, conversation_id: int) -> List[Message]:
        """Fetch all messages for a given conversation."""
        conv = self.get_conversation(conversation_id)
        return conv.messages

    def process_chat_message(self, question: str, conversation_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Processes user chat question via RAG and persists conversation/message history.
        """
        # 1. Get or create conversation
        if conversation_id:
            conv = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conv:
                conv = self.create_conversation(title=question[:30] + "...")
        else:
            conv = self.create_conversation(title=question[:30] + "...")

        # 2. Save user message to DB
        user_msg = Message(
            conversation_id=conv.id,
            role="user",
            content=question
        )
        self.db.add(user_msg)
        self.db.commit()

        # 3. Execute RAG pipeline
        rag_output = self.rag_service.answer_question(question)
        answer = rag_output["answer"]
        sources = rag_output["sources"]

        # 4. Save assistant message to DB
        assistant_msg = Message(
            conversation_id=conv.id,
            role="assistant",
            content=answer,
            sources=sources
        )
        self.db.add(assistant_msg)
        
        # 5. Update conversation title if it was a default title
        if conv.title == "New Conversation" or len(conv.messages) <= 2:
            conv.title = question[:35] + ("..." if len(question) > 35 else "")
        conv.updated_at = datetime.utcnow()
        
        self.db.commit()
        logger.info(f"Processed chat message for conversation_id={conv.id}")

        return {
            "conversation_id": conv.id,
            "message": answer,
            "sources": sources
        }
