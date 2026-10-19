from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewDecisionRequest(BaseModel):
    vendor_id: str = Field(..., description="Target vendor ID under audit")
    vendor_document_id: Optional[str] = Field(None, description="Specific document under review (if applicable)")
    action: str = Field(
        ...,
        description="Officer action: 'APPROVED' | 'DISQUALIFIED' | 'CLARIFICATION_REQUESTED'"
    )
    notes: str = Field(..., description="Mandatory reason / justification for audit log")
    exemption_granted: Optional[str] = Field(None, description="Statutory exemption applied (e.g. 'EMD Waiver', 'Rule 173(i)')")
    clarification_deadline: Optional[datetime] = Field(None, description="48-hour deadline if clarification requested")
    clarification_notice_text: Optional[str] = Field(None, description="Draft notice text sent to vendor")
    reviewer_id: Optional[str] = Field(None, description="ID of the reviewing procurement officer")
    reviewer_name: Optional[str] = Field("Procurement Officer (MeitY)", description="Display name of the officer")


class HumanReviewResponse(BaseModel):
    id: str
    vendor_id: str
    vendor_document_id: Optional[str] = None
    reviewer_id: str
    action: str
    notes: str
    exemption_granted: Optional[str] = None
    clarification_deadline: Optional[datetime] = None
    clarification_notice_text: Optional[str] = None
    created_at: datetime
