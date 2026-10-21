from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.schemas.knowledge import IngestionResponse
from app.services.document_loader import DocumentValidationError
from app.services.ingestion_service import KnowledgeIngestionService


router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


@router.post(
    "/documents",
    response_model=IngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_knowledge_document(
    file: Annotated[UploadFile, File(...)],
) -> IngestionResponse:
    filename = file.filename or ""
    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    try:
        content = await file.read(max_bytes + 1)
    finally:
        await file.close()

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.max_upload_size_mb} MB limit.",
        )

    service = None

    try:
        service = KnowledgeIngestionService()
        result = await service.ingest(filename, content)
        return IngestionResponse(**result)

    except DocumentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except RuntimeError as exc:
        # Missing configuration, incompatible collection, or setup failures.
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    except Exception as exc:
        # Do not expose API keys, request payloads, or provider internals.
        raise HTTPException(
            status_code=502,
            detail="Document ingestion failed. Check the server logs and service connectivity.",
        ) from exc

    finally:
        if service is not None:
            await service.close()