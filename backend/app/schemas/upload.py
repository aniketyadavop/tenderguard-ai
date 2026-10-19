from datetime import datetime
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    file_id: str = Field(..., description="Server-controlled unique file UUID")
    file_name: str = Field(..., description="Sanitized original filename")
    file_size_bytes: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="Verified MIME type")
    sha256_hash: str = Field(..., description="Cryptographic SHA-256 hash of file content")
    uploaded_at: datetime = Field(..., description="Upload timestamp (UTC)")
    zero_retention_flag: bool = Field(True, description="Indicates whether zero-retention ephemeral processing is active")
