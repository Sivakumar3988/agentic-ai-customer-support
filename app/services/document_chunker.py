from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.services.document_loader import ExtractedDocument


def chunk_document(document: ExtractedDocument) -> list[dict]:
    if settings.chunk_overlap >= settings.chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )

    documents = splitter.create_documents(
        texts=[document.text],
        metadatas=[
            {
                "filename": document.filename,
                "file_type": document.file_type,
            }
        ],
    )

    chunks = []

    for index, item in enumerate(documents):
        content = item.page_content.strip()

        if not content:
            continue

        chunks.append(
            {
                "chunk_index": index,
                "text": content,
                "start_index": item.metadata.get("start_index", 0),
                "filename": document.filename,
                "file_type": document.file_type,
            }
        )

    if not chunks:
        raise ValueError("Document did not produce any usable chunks.")

    return chunks