import hashlib
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.review import HumanReview
from backend.app.models.vendor import Vendor
from backend.app.models.document import VendorDocument
from backend.app.models.organization import Organization
from backend.app.models.user import User
from backend.app.models.audit import AuditEvent
from backend.app.schemas.review import ReviewDecisionRequest, HumanReviewResponse

from backend.app.core.roles import UserRole
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import require_roles, get_current_user

router = APIRouter()


def get_or_create_officer_user(db: Session, org_id: str, officer_id: Optional[str] = None) -> User:
    """Ensures a valid procurement officer user exists for audit tracking."""
    # Ensure Organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        org = Organization(
            id=org_id,
            name="Ministry of Electronics & IT / GeM Portal",
            code="MeitY-GeM-4.0",
            org_type="GOVERNMENT_DEPARTMENT"
        )
        db.add(org)
        db.flush()

    if officer_id:
        user = db.query(User).filter(User.id == officer_id).first()
        if user:
            return user

    # Default procurement officer
    user = db.query(User).filter(User.organization_id == org_id, User.email == "officer@gem.gov.in").first()
    if not user:
        user = User(
            id="user-officer-default",
            organization_id=org_id,
            email="officer@gem.gov.in",
            full_name="Competent Procurement Officer",
            hashed_password="hashed_demo_secret",
            role="PROCUREMENT_OFFICER"
        )
        db.add(user)
        db.flush()
    return user


@router.post(
    "/decision",
    response_model=HumanReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Procurement Officer Sign-Off / Override",
    description="Records human officer decision (Approve with Exemption, Confirm Disqualification, or Request 48h Clarification)."
)
def record_review_decision(
    req: ReviewDecisionRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER, UserRole.REVIEWER)),
    db: Session = Depends(get_db)
):
    vendor = db.query(Vendor).filter(Vendor.id == req.vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID '{req.vendor_id}' not found."
        )

    # 1. Resolve Reviewer User from authenticated session or explicit reviewer_id
    officer = current_user
    if req.reviewer_id and req.reviewer_id != current_user.id:
        explicit_user = db.query(User).filter(User.id == req.reviewer_id).first()
        if explicit_user:
            officer = explicit_user

    # 2. Create HumanReview Record
    action_upper = req.action.upper()
    if action_upper not in ["APPROVED", "DISQUALIFIED", "CLARIFICATION_REQUESTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be one of: 'APPROVED', 'DISQUALIFIED', 'CLARIFICATION_REQUESTED'."
        )

    review_record = HumanReview(
        vendor_id=req.vendor_id,
        organization_id=vendor.organization_id,
        vendor_document_id=req.vendor_document_id,
        reviewer_id=officer.id,
        action=action_upper,
        notes=req.notes,
        exemption_granted=req.exemption_granted,
        clarification_deadline=req.clarification_deadline,
        clarification_notice_text=req.clarification_notice_text
    )
    db.add(review_record)
    db.flush()

    # 3. Update target document & vendor status accordingly
    if req.vendor_document_id:
        doc = db.query(VendorDocument).filter(VendorDocument.id == req.vendor_document_id).first()
        if doc:
            if action_upper == "APPROVED":
                doc.status = "COMPLIANT"
            elif action_upper == "DISQUALIFIED":
                doc.status = "NON_COMPLIANT"
            elif action_upper == "CLARIFICATION_REQUESTED":
                doc.status = "REQUIRES_REVIEW"

    if action_upper == "DISQUALIFIED":
        vendor.overall_status = "NON_COMPLIANT"
    elif action_upper == "APPROVED":
        # Check if all other documents are compliant
        other_docs = db.query(VendorDocument).filter(VendorDocument.vendor_id == req.vendor_id).all()
        if all(d.status == "COMPLIANT" for d in other_docs):
            vendor.overall_status = "COMPLIANT"

    # 4. Generate Tamper-Evident Cryptographic Audit Event via AuditService
    AuditService.log_event(
        db=db,
        organization_id=vendor.organization_id,
        event_type="OFFICER_OVERRIDE_RECORDED",
        entity_type="HumanReview",
        entity_id=review_record.id,
        actor_id=officer.id,
        actor_role=officer.role,
        description=f"Reviewer ({officer.full_name}) recorded decision: {action_upper}. Notes: {req.notes}",
        metadata={
            "action": action_upper,
            "vendor_id": req.vendor_id,
            "vendor_document_id": req.vendor_document_id,
            "exemption_granted": req.exemption_granted,
            "clarification_deadline": req.clarification_deadline.isoformat() if req.clarification_deadline else None
        }
    )

    db.commit()
    db.refresh(review_record)

    return HumanReviewResponse(
        id=review_record.id,
        vendor_id=review_record.vendor_id,
        vendor_document_id=review_record.vendor_document_id,
        reviewer_id=review_record.reviewer_id,
        action=review_record.action,
        notes=review_record.notes,
        exemption_granted=review_record.exemption_granted,
        clarification_deadline=review_record.clarification_deadline,
        clarification_notice_text=review_record.clarification_notice_text,
        created_at=review_record.created_at
    )


@router.get(
    "/history/{vendor_id}",
    response_model=List[HumanReviewResponse],
    summary="Get Human Review History",
    description="Retrieves the chronological procurement officer review trail for a vendor."
)
def get_review_history(
    vendor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reviews = (
        db.query(HumanReview)
        .filter(HumanReview.vendor_id == vendor_id)
        .order_by(HumanReview.created_at.desc())
        .all()
    )
    return [
        HumanReviewResponse(
            id=r.id,
            vendor_id=r.vendor_id,
            vendor_document_id=r.vendor_document_id,
            reviewer_id=r.reviewer_id,
            action=r.action,
            notes=r.notes,
            exemption_granted=r.exemption_granted,
            clarification_deadline=r.clarification_deadline,
            clarification_notice_text=r.clarification_notice_text,
            created_at=r.created_at
        )
        for r in reviews
    ]
