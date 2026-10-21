
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import Customer
from app.db.session import get_db


async def get_current_customer(
    x_dev_customer_id: Annotated[
        str | None, Header()
    ] = None,
    db: AsyncSession = Depends(get_db),
) -> Customer:
    # This header is a development convenience, NOT authentication.
    if settings.environment != "development":
        raise HTTPException(
            status_code=501,
            detail="Configure real authentication before enabling these APIs",
        )

    if not x_dev_customer_id:
        raise HTTPException(
            status_code=401,
            detail="X-Dev-Customer-ID header is required",
        )

    result = await db.execute(
        select(Customer).where(
            Customer.external_id == x_dev_customer_id
        )
    )
    customer = result.scalar_one_or_none()

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer
