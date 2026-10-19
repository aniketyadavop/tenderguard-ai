import os
import uuid
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.roles import UserRole
from backend.app.models.user import User
from backend.app.schemas.upload import FileUploadResponse
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import require_roles

router = APIRouter()

# Magic bytes signatures for content-type verification
MAGIC_BYTES = {
    "application/pdf": [b"%PDF-"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/jpg": [b"\xff\xd8\xff"],
}


def verify_magic_bytes(header: bytes, reported_type: str) -> str:
    """
    Verifies that the file header matches authentic magic bytes
    to prevent file extension spoofing attacks.
    """
    # Check reported type first
    signatures = MAGIC_BYTES.get(reported_type, [])
    for sig in signatures:
        if header.startswith(sig):
            return reported_type

    # Fallback check against all known allowed signatures
    for mime_type, sig_list in MAGIC_BYTES.items():
        for sig in sig_list:
            if header.startswith(sig):
                return mime_type

    return ""


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Secure Document Upload",
    description="Upload statutory vendor document (PDF/PNG/JPEG) with size, MIME, and magic byte validation."
)
async def upload_document(
    file: UploadFile = File(..., description="Document file (PDF, PNG, or JPEG, max 25MB)"),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER, UserRole.VENDOR)),
    db: Session = Depends(get_db)
) -> FileUploadResponse:
    # 1. Sanitize filename
    original_filename = os.path.basename(file.filename or "uploaded_document")
    ext = os.path.splitext(original_filename)[1].lower()

    if ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' is not supported. Allowed formats: PDF, PNG, JPEG."
        )

    # 2. Read file in chunks with max size validation and compute SHA-256
    sha256 = hashlib.sha256()
    total_size = 0
    chunk_size = 64 * 1024  # 64 KB
    header_bytes = b""
    content_chunks = []

    while chunk := await file.read(chunk_size):
        total_size += len(chunk)
        if total_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds statutory maximum limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB."
            )
        if len(header_bytes) < 32:
            header_bytes += chunk[: 32 - len(header_bytes)]
        sha256.update(chunk)
        content_chunks.append(chunk)

    if total_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    # 3. Verify magic bytes signature
    reported_content_type = file.content_type or ""
    verified_mime_type = verify_magic_bytes(header_bytes, reported_content_type)
    if not verified_mime_type or verified_mime_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File content does not match allowed document types (PDF, PNG, JPEG)."
        )

    # 4. Generate server-controlled file identifier
    file_id = str(uuid.uuid4())
    sha256_hash = sha256.hexdigest()

    # 5. Secure storage handling (quarantined server-controlled name)
    os.makedirs(settings.UPLOAD_STORAGE_DIR, exist_ok=True)
    stored_filename = f"{file_id}{ext}"
    stored_path = os.path.join(settings.UPLOAD_STORAGE_DIR, stored_filename)

    with open(stored_path, "wb") as f:
        for chunk in content_chunks:
            f.write(chunk)

    # 6. Record AuditEvent
    AuditService.log_event(
        db=db,
        organization_id=current_user.organization_id,
        event_type="DOCUMENT_UPLOAD",
        entity_type="VendorDocument",
        entity_id=file_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        description=f"User '{current_user.email}' uploaded statutory document '{original_filename}' ({total_size} bytes, SHA-256: {sha256_hash[:16]}...).",
        metadata={"filename": original_filename, "size": total_size, "mime": verified_mime_type}
    )
    db.commit()

    return FileUploadResponse(
        file_id=file_id,
        file_name=original_filename,
        file_size_bytes=total_size,
        mime_type=verified_mime_type,
        sha256_hash=sha256_hash,
        uploaded_at=datetime.now(timezone.utc),
        zero_retention_flag=settings.ZERO_RETENTION_MODE
    )
