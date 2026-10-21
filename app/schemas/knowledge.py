from pydantic import BaseModel, Field


class IngestionResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    total_characters: int = Field(ge=1)
    total_chunks: int = Field(ge=1)
    collection: str