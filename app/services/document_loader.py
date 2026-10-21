from dataclasses import dataclass
from pathlib import Path
import re

import fitz


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


class DocumentValidationError(ValueError):
    """Raised when a document cannot be safely processed."""


@dataclass
class ExtractedDocument:
    text: str
    filename: str
    file_type: str


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_document(
    filename: str,
    content: bytes,
) -> ExtractedDocument:
    if not filename or not content:
        raise DocumentValidationError("Filename and file content are required.")

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise DocumentValidationError(
            "Unsupported file type. Upload a PDF, TXT, or Markdown file."
        )

    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise DocumentValidationError(
                "The uploaded file does not appear to be a valid PDF."
            )

        try:
            with fitz.open(stream=content, filetype="pdf") as pdf:
                pages = [page.get_text("text") for page in pdf]
                text = "\n\n".join(pages)
        except Exception as exc:
            raise DocumentValidationError(
                "Unable to read the PDF file."
            ) from exc

    else:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DocumentValidationError(
                "TXT and Markdown files must use UTF-8 encoding."
            ) from exc

    text = clean_text(text)

    if not text:
        raise DocumentValidationError(
            "No extractable text was found. This may be a scanned PDF; "
            "OCR support will be added separately."
        )

    return ExtractedDocument(
        text=text,
        filename=Path(filename).name,
        file_type=extension.lstrip("."),
    )