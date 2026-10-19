from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.roles import UserRole
from backend.app.models.audit import AuditEvent
from backend.app.models.user import User
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import require_roles, get_current_user

router = APIRouter()


@router.get(
    "/events",
    summary="List Audit Log Events",
    description="Returns tamper-evident audit events under GFR 2017 & GeM guidelines. Restricted to Admins, Officers, and Auditors."
)
def list_audit_events(
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g. HUMAN_REVIEW_OVERRIDE)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (e.g. ComplianceFinding)"),
    actor_id: Optional[str] = Query(None, description="Filter by actor user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER, UserRole.READ_ONLY)),
    db: Session = Depends(get_db)
):
    events = AuditService.list_events(
        db=db,
        organization_id=current_user.organization_id if current_user.role != UserRole.ADMIN.value else None,
        event_type=event_type,
        entity_type=entity_type,
        actor_id=actor_id,
        skip=skip,
        limit=limit
    )

    results = []
    for e in events:
        results.append({
            "id": e.id,
            "organization_id": e.organization_id,
            "event_type": e.event_type,
            "entity_type": e.entity_type,
            "entity_id": e.entity_id,
            "actor_id": e.actor_id,
            "actor_role": e.actor_role,
            "ip_address": e.ip_address,
            "description": e.description,
            "metadata": e.metadata_json,
            "sha256_signature": e.sha256_signature,
            "created_at": e.created_at.isoformat() if e.created_at else None
        })
    return results


@router.get(
    "/events/{event_id}",
    summary="Get Single Audit Event",
    description="Retrieves a specific immutable audit event by ID."
)
def get_audit_event(
    event_id: str,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER, UserRole.READ_ONLY)),
    db: Session = Depends(get_db)
):
    event = db.query(AuditEvent).filter(AuditEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit event with ID '{event_id}' not found."
        )
    return {
        "id": event.id,
        "organization_id": event.organization_id,
        "event_type": event.event_type,
        "entity_type": event.entity_type,
        "entity_id": event.entity_id,
        "actor_id": event.actor_id,
        "actor_role": event.actor_role,
        "ip_address": event.ip_address,
        "description": event.description,
        "metadata": event.metadata_json,
        "sha256_signature": event.sha256_signature,
        "created_at": event.created_at.isoformat() if event.created_at else None
    }


@router.get(
    "/verify/{event_id}",
    summary="Verify Audit Event Cryptographic Integrity",
    description="Validates the SHA-256 tamper-evident cryptographic signature of an audit record."
)
def verify_audit_integrity(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(AuditEvent).filter(AuditEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit event with ID '{event_id}' not found."
        )

    is_valid = AuditService.verify_event_integrity(event)
    return {
        "event_id": event.id,
        "event_type": event.event_type,
        "sha256_signature": event.sha256_signature,
        "is_tamper_free": is_valid,
        "verification_status": "AUTHENTIC_AND_VERIFIED" if is_valid else "TAMPER_DETECTED",
        "verified_at": datetime.now(timezone.utc).isoformat()
    }
