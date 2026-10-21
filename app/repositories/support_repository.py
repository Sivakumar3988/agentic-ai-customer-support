
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Customer, Conversation, Message, SupportTicket


async def get_or_create_customer(
    db: AsyncSession,
    external_id: str,
) -> Customer:
    result = await db.execute(
        select(Customer).where(Customer.external_id == external_id)
    )
    customer = result.scalar_one_or_none()

    if customer is None:
        customer = Customer(external_id=external_id)
        db.add(customer)
        await db.flush()

    return customer


async def get_or_create_conversation(
    db: AsyncSession,
    customer: Customer,
    conversation_id: UUID | None = None,
) -> Conversation:
    if conversation_id is not None:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id
            )
        )
        conversation = result.scalar_one_or_none()

        if conversation is not None:
            if conversation.customer_id != customer.id:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found",
                )
            return conversation

        # Allow a new conversation to use a client-provided UUID.
        conversation = Conversation(
            id=conversation_id,
            customer_id=customer.id,
        )
    else:
        conversation = Conversation(customer_id=customer.id)

    db.add(conversation)
    await db.flush()
    return conversation


async def save_message(
    db: AsyncSession,
    conversation_id: UUID,
    role: str,
    content: str,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    db.add(message)
    await db.flush()
    return message


async def create_support_ticket(
    db: AsyncSession,
    conversation_id: UUID,
    subject: str,
    description: str,
    priority: str = "medium",
) -> SupportTicket:
    ticket = SupportTicket(
        ticket_number=f"TKT-{uuid4().hex[:12].upper()}",
        conversation_id=conversation_id,
        subject=subject,
        description=description,
        priority=priority,
        status="open",
    )
    db.add(ticket)
    await db.flush()
    return ticket
