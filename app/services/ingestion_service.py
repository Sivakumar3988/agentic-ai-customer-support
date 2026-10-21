from uuid import NAMESPACE_URL, uuid4, uuid5
from datetime import datetime, timezone

from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient, models

from app.core.config import settings
from app.services.document_chunker import chunk_document
from app.services.document_loader import extract_document


class KnowledgeIngestionService:
    def __init__(self) -> None:
        if settings.openai_api_key is None:
            raise RuntimeError("OPENAI_API_KEY is required for ingestion.")

        self.openai = AsyncOpenAI(
            api_key=settings.openai_api_key.get_secret_value()
        )
        self.qdrant = AsyncQdrantClient(url=settings.qdrant_url)

    async def ensure_collection(self) -> None:
        collection_name = settings.qdrant_collection

        if await self.qdrant.collection_exists(collection_name):
            info = await self.qdrant.get_collection(collection_name)
            vector_config = info.config.params.vectors

            if (
                not isinstance(vector_config, dict)
                and vector_config.size != settings.embedding_dimensions
            ):
                raise RuntimeError(
                    "Qdrant collection dimensions do not match "
                    "EMBEDDING_DIMENSIONS. Use a compatible collection."
                )

            if isinstance(vector_config, dict):
                raise RuntimeError(
                    "This service expects a single-vector Qdrant collection. "
                    "The existing collection uses named vectors."
                )
            return

        await self.qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=settings.embedding_dimensions,
                distance=models.Distance.COSINE,
            ),
        )

    async def create_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        vectors: list[list[float]] = []
        batch_size = 64

        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]

            response = await self.openai.embeddings.create(
                model=settings.embedding_model,
                input=batch,
                dimensions=settings.embedding_dimensions,
            )

            ordered = sorted(response.data, key=lambda item: item.index)
            vectors.extend(item.embedding for item in ordered)

        if len(vectors) != len(texts):
            raise RuntimeError("Embedding count does not match chunk count.")

        return vectors

    async def ingest(
        self,
        filename: str,
        content: bytes,
    ) -> dict:
        document = extract_document(filename, content)
        chunks = chunk_document(document)

        await self.ensure_collection()

        document_id = str(uuid4())
        vectors = await self.create_embeddings(
            [chunk["text"] for chunk in chunks]
        )

        now = datetime.now(timezone.utc).isoformat()
        points = []

        for chunk, vector in zip(chunks, vectors):
            # Deterministic point IDs within this document.
            point_id = str(
                uuid5(
                    NAMESPACE_URL,
                    f"{document_id}:{chunk['chunk_index']}",
                )
            )

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "document_id": document_id,
                        "filename": document.filename,
                        "file_type": document.file_type,
                        "chunk_index": chunk["chunk_index"],
                        "start_index": chunk["start_index"],
                        "text": chunk["text"],
                        "uploaded_at": now,
                    },
                )
            )

        # Upload in batches to keep memory and request sizes manageable.
        for start in range(0, len(points), 100):
            await self.qdrant.upsert(
                collection_name=settings.qdrant_collection,
                points=points[start : start + 100],
                wait=True,
            )

        return {
            "document_id": document_id,
            "filename": document.filename,
            "file_type": document.file_type,
            "total_characters": len(document.text),
            "total_chunks": len(chunks),
            "collection": settings.qdrant_collection,
        }

    async def close(self) -> None:
        await self.qdrant.close()
        await self.openai.close()