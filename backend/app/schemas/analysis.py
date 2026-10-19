from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StartAnalysisRequest(BaseModel):
    vendor_id: str = Field(..., description="Target vendor ID to audit")
    vendor_name: str = Field(..., description="Vendor corporate name")
    organization_id: str = Field("org-gem-meity", description="Tenant organization ID")
    tender_id: str = Field("GeM/2026/B/89412", description="Tender Reference ID")
    uploaded_files: List[Dict[str, Any]] = Field(
        ...,
        description="List of uploaded file metadata [{file_id, file_name, storage_path, document_type_hint}]"
    )


class JobStatusResponse(BaseModel):
    job_id: str
    vendor_id: str
    status: str = Field(..., description="QUEUED | PROCESSING | COMPLETED | FAILED | CANCELLED")
    current_stage: int = Field(..., description="1: Spatial OCR, 2: Parsing, 3: Reconciliation, 4: Evidence")
    progress_pct: int = Field(..., description="0 to 100")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
