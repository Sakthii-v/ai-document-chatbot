from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    MessageSchema
)
from app.services.chat_service import ChatService

router = APIRouter(tags=["Chat & Conversations"])


@router.post("/chat", response_model=ChatResponse, summary="Send question to RAG chatbot")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Query the document knowledge base using RAG and local LLM.
    Returns generated answer and source citations with metadata.
    """
    service = ChatService(db)
    result = service.process_chat_message(
        question=request.message,
        conversation_id=request.conversation_id
    )
    return result


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED, summary="Create new conversation")
def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Create a new empty conversation session."""
    service = ChatService(db)
    conv = service.create_conversation(title=request.title)
    return conv


@router.get("/conversations", response_model=List[ConversationResponse], summary="List all conversations")
def list_conversations(db: Session = Depends(get_db)):
    """Fetch history of all chat conversations."""
    service = ChatService(db)
    return service.list_conversations()


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse, summary="Get conversation details with messages")
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Fetch single conversation with all past user and assistant messages."""
    service = ChatService(db)
    conv = service.get_conversation(conversation_id)
    return conv


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageSchema], summary="Get messages for conversation")
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Fetch all messages for a specific conversation ID."""
    service = ChatService(db)
    messages = service.get_messages(conversation_id)
    return messages


@router.delete("/conversations/{conversation_id}", summary="Delete conversation history")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Delete a conversation and its messages."""
    service = ChatService(db)
    return service.delete_conversation(conversation_id)
