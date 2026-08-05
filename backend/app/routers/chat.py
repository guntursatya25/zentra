import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_current_user
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    Citation,
    ConversationOut,
    FeedbackRequest,
    MessageOut,
)
from app.services.audit import log_audit
from app.services.rag import answer_query
from app.services.vector_search import search_chunks

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
):
    """Send a message and get AI response grounded in document chunks."""
    # Resolve or create conversation
    try:
        conv_id = uuid.UUID(body.conversation_id) if body.conversation_id else uuid.uuid4()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation_id format")
    if body.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conv_id, Conversation.user_id == user.id
            )
        )
        conv = result.scalar_one_or_none()
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    else:
        conv = Conversation(
            id=conv_id,
            user_id=user.id,
            title=body.message[:80] + ("…" if len(body.message) > 80 else ""),
        )
        db.add(conv)
        await db.commit()

    # Save user message and update conversation timestamp
    from datetime import datetime, timezone
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    conv.updated_at = datetime.now(timezone.utc)  # FIX: bubble conversation to top of list

    # ── RAG pipeline ──
    # 1. Vector search — find relevant chunks
    chunks = await search_chunks(
        db,
        query=body.message,
        top_k=8,
        category_ids=body.category_filter,
    )

    # 2. Generate answer via LLM
    result = await answer_query(body.message, chunks)

    # 3. Save AI response
    citations_data = result.get("citations", [])
    ai_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=result["answer"],
        citations=citations_data,
    )
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)

    # Audit log for chat query
    ip = request.client.host if request and request.client else None
    await log_audit(
        db, user.id, "chat_query", "conversation", str(conv.id),
        {"question": body.message[:100], "citations_count": len(citations_data)},
        ip,
    )

    return ChatResponse(
        conversation_id=str(conv.id),
        message_id=str(ai_msg.id),
        answer=ai_msg.content,
        citations=[Citation(**c) for c in citations_data],
    )


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
    )
    return [
        ConversationOut(
            id=str(c.id), title=c.title,
            created_at=c.created_at, updated_at=c.updated_at,
        )
        for c in result.scalars().all()
    ]


@router.get("/conversations/{conv_id}")
async def get_conversation(
    conv_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conv_id, Conversation.user_id == user.id
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    msgs_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    messages = [
        MessageOut(
            id=str(m.id), role=m.role, content=m.content,
            citations=m.citations, feedback=m.feedback,
            created_at=m.created_at,
        )
        for m in msgs_result.scalars().all()
    ]

    return {
        "conversation": ConversationOut(
            id=str(conv.id), title=conv.title,
            created_at=conv.created_at, updated_at=conv.updated_at,
        ),
        "messages": messages,
    }


@router.delete("/conversations/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conv_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conv_id, Conversation.user_id == user.id
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    ip = request.client.host if request and request.client else None
    await log_audit(db, user.id, "delete", "conversation", str(conv.id), None, ip)

    await db.delete(conv)
    await db.commit()


@router.post("/messages/{msg_id}/feedback", status_code=status.HTTP_204_NO_CONTENT)
async def send_feedback(
    msg_id: uuid.UUID,
    body: FeedbackRequest,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
):
    if body.feedback not in ("up", "down"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback must be 'up' or 'down'")

    result = await db.execute(
        select(Message).join(Conversation).where(
            Message.id == msg_id,
            Conversation.user_id == user.id,
        )
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    msg.feedback = body.feedback
    await db.commit()

    ip = request.client.host if request and request.client else None
    await log_audit(
        db, user.id, "feedback", "message", str(msg_id),
        {"feedback": body.feedback},
        ip,
    )
