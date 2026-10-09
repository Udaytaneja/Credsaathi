import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


class DocumentBase(BaseModel):
    name: str
    document_type: str
    mime_type: str
    file_size_bytes: int


class DocumentCreate(DocumentBase):
    storage_path: str
    application_id: uuid.UUID | None = None


class DocumentResponse(DocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    application_id: uuid.UUID | None = None
    storage_path: str
    status: str
    extracted_data: dict[str, Any] | None = None
    review_required: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
