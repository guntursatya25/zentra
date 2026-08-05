from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    message: str
    category_filter: list[int] | None = None


class Citation(BaseModel):
    document_name: str
    bab: str | None
    pasal: str | None
    ayat: str | None
    excerpt: str


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    citations: list[Citation] = []


class ConversationOut(BaseModel):
    id: str
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    citations: list[dict] | None = None
    feedback: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackRequest(BaseModel):
    feedback: str  # "up" or "down"
