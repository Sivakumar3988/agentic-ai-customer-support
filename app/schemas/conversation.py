
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime


class MessagePage(BaseModel):
    items: list[MessageRead]
    limit: int
    offset: int
    total: int
    has_more: bool
