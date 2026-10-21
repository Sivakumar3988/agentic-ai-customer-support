
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_customer
from app.db.models import Conversation, Customer, SupportTicket
from app.db.session import get_db
from app.repositories.support_repository import create_support_ticket
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["Support Tickets"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentCustomer = Annotated[Customer, Depends(get_current_customer)]


async def get_customer_ticket(
    db: AsyncSession,
    customer_id: UUID,
    ticket_id: UUID,
) -> SupportTicket:
    result = await db.execute(
        select(SupportTicket)
        .join(
            Conversation,
            SupportTicket.conversation_id == Conversation.id,
        )
        .where(
            SupportTicket.id == ticket_id,
            Conversation.customer_id == customer_id,
        )
    )
    ticket = result.scalar_one_or_none()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@router.post("", response_model=TicketRead, status_code=201)
async def create_ticket(
    request: TicketCreate,
    db: DbSession,
    customer: CurrentCustomer,
):
    async with db.begin():
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.customer_id == customer.id,
            )
        )
        conversation = result.scalar_one_or_none()

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        ticket = await create_support_ticket(
            db=db,
            conversation_id=conversation.id,
            subject=request.subject,
            description=request.description,
            priority=request.priority,
        )
        await db.flush()
        await db.refresh(ticket)

    return ticket


@router.get("", response_model=list[TicketRead])
async def list_tickets(
    db: DbSession,
    customer: CurrentCustomer,
    status: str | None = Query(default=None),
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    query = (
        select(SupportTicket)
        .join(
            Conversation,
            SupportTicket.conversation_id == Conversation.id,
        )
        .where(Conversation.customer_id == customer.id)
    )

    if status is not None:
        if status not in {"open", "in_progress", "resolved", "closed"}:
            raise HTTPException(
                status_code=422,
                detail="Invalid ticket status",
            )
        query = query.where(SupportTicket.status == status)

    result = await db.execute(
        query.order_by(
            SupportTicket.created_at.desc(),
            SupportTicket.id,
        )
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket(
    ticket_id: UUID,
    db: DbSession,
    customer: CurrentCustomer,
):
    return await get_customer_ticket(db, customer.id, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketRead)
async def update_ticket(
    ticket_id: UUID,
    request: TicketUpdate,
    db: DbSession,
    customer: CurrentCustomer,
):
    changes = request.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=422,
            detail="Provide at least one field to update",
        )

    async with db.begin():
        ticket = await get_customer_ticket(
            db, customer.id, ticket_id
        )

        for field, value in changes.items():
            setattr(ticket, field, value)

        await db.flush()
        await db.refresh(ticket)

    return ticket
