
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_customer
from app.db.models import Conversation, Customer, Message
from app.db.session import get_db
from app.schemas.conversation import (
    ConversationSummary,
    MessagePage,
    MessageRead,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentCustomer = Annotated[Customer, Depends(get_current_customer)]


@router.get("", response_model=list[ConversationSummary])
async def list_conversations(
    db: DbSession,
    customer: CurrentCustomer,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.customer_id == customer.id)
        .order_by(Conversation.updated_at.desc(), Conversation.id)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.get(
    "/{conversation_id}/messages",
    response_model=MessagePage,
)
async def list_messages(
    conversation_id: UUID,
    db: DbSession,
    customer: CurrentCustomer,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    conversation_result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.customer_id == customer.id,
        )
    )
    conversation = conversation_result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    total_result = await db.execute(
        select(func.count())
        .select_from(Message)
        .where(Message.conversation_id == conversation_id)
    )
    total = total_result.scalar_one()

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
        .limit(limit)
        .offset(offset)
    )
    items = result.scalars().all()

    return MessagePage(
        items=items,
        limit=limit,
        offset=offset,
        total=total,
        has_more=offset + len(items) < total,
    )
