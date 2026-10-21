# ChatRequest: validates incoming customer messages.
# ChatResponse: standardizes the response returned to the frontend.
# ConversationMessage: establishes the structure we'll use when working with conversation history.
# The status values are defined now for consistency. We won't actually perform escalation until we implement that workflow.

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(
        min_length=1,
        max_length=5000,
        description="The customer's message",
    )
    customer_id: str | None = Field(
        default=None,
        max_length=100,
        description="Customer identifier",
    )
    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID, if available",
    )


class ChatResponse(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    status: Literal["accepted", "completed", "escalated"]
    answer: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=10000)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
