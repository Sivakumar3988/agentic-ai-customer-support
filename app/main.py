
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.core.config import settings
from app.db.base import Base
from app.db.models import Customer, Conversation, Message, SupportTicket
from app.db.session import engine
from app.api.conversations import router as conversations_router
from app.api.tickets import router as tickets_router
from app.api.knowledge import router as knowledge_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment == "development":
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for our Agentic AI Customer Support System",
    lifespan=lifespan,
)

app.include_router(chat_router, prefix=settings.api_v1_prefix)
app.include_router(
    conversations_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(tickets_router, prefix=settings.api_v1_prefix)
app.include_router(
    knowledge_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": settings.app_name,
        "status": "healthy",
        "version": settings.app_version,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
