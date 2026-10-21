# This endpoint will accept a customer's message and return a structured response. 
# For now, it will return a placeholder instead of calling an LLM; we'll connect LangGraph later.


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.db.session import get_db
from app.repositories.support_repository import (
    get_or_create_customer,
    get_or_create_conversation,
    save_message,
)
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Customer Support"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    if not request.customer_id:
        raise HTTPException(
            status_code=400,
            detail="customer_id is required for this development endpoint",
        )

    answer = (
        "Your message has been received and saved. "
        "AI response generation is not connected yet."
    )

    async with db.begin():
        customer = await get_or_create_customer(
            db, request.customer_id
        )

        conversation = await get_or_create_conversation(
            db,
            customer,
            request.conversation_id,
        )

        await save_message(
            db, conversation.id, "user", request.message
        )
        await save_message(
            db, conversation.id, "assistant", answer
        )

        conversation.updated_at = __import__(
            "datetime"
        ).datetime.now(__import__("datetime").timezone.utc)

        conversation_id = conversation.id

    return ChatResponse(
        conversation_id=conversation_id,
        status="accepted",
        answer=answer,
    )
