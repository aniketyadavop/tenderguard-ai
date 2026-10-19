import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.models.audit import AuditEvent
from backend.app.core.config import settings


def format_event_timestamp(dt: Optional[datetime]) -> str:
    """Produces a deterministic, timezone-normalized ISO-8601 second-precision timestamp string."""
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_audit_signature(
    organization_id: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    actor_id: Optional[str],
    description: str,
    timestamp_iso: str,
    salt: str = settings.SECRET_KEY
) -> str:
    """
    Computes a cryptographic tamper-evident SHA-256 signature
    across the immutable audit event properties.
    """
    payload = (
        f"{organization_id}|{event_type}|{entity_type}|{entity_id}|"
        f"{actor_id or 'ANONYMOUS'}|{description}|{timestamp_iso}|{salt}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AuditService:
    """
    Centralized AuditEvent Logging Service for statutory compliance,
    tamper evidence, and oversight under GFR 2017 & GeM guidelines.
    """

    @staticmethod
    def log_event(
        db: Session,
        organization_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        actor_id: Optional[str] = None,
        actor_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Creates, cryptographically signs, and persists an AuditEvent record.
        """
        now = datetime.now(timezone.utc)
        iso_str = format_event_timestamp(now)

        sig = compute_audit_signature(
            organization_id=organization_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            description=description,
            timestamp_iso=iso_str
        )

        event = AuditEvent(
            organization_id=organization_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            actor_role=actor_role,
            ip_address=ip_address,
            description=description,
            metadata_json=metadata or {},
            sha256_signature=sig,
            created_at=now
        )
        db.add(event)
        db.flush()
        return event

    @staticmethod
    def verify_event_integrity(event: AuditEvent) -> bool:
        """
        Verifies if the AuditEvent record has remained untampered.
        """
        iso_str = format_event_timestamp(event.created_at)
        expected = compute_audit_signature(
            organization_id=event.organization_id,
            event_type=event.event_type,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            actor_id=event.actor_id,
            description=event.description,
            timestamp_iso=iso_str
        )
        return expected == event.sha256_signature

    @staticmethod
    def list_events(
        db: Session,
        organization_id: Optional[str] = None,
        event_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[AuditEvent]:
        """
        Retrieves paginated audit events ordered by creation timestamp descending.
        """
        query = db.query(AuditEvent)
        if organization_id:
            query = query.filter(AuditEvent.organization_id == organization_id)
        if event_type:
            query = query.filter(AuditEvent.event_type == event_type)
        if entity_type:
            query = query.filter(AuditEvent.entity_type == entity_type)
        if actor_id:
            query = query.filter(AuditEvent.actor_id == actor_id)

        return query.order_by(desc(AuditEvent.created_at)).offset(skip).limit(limit).all()
