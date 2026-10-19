from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.tender import Tender
    from backend.app.models.vendor import Vendor
    from backend.app.models.audit import AuditEvent


class Organization(Base, TimestampMixin):
    """
    Tenant entity. All procurement evaluations, vendors, tenders,
    and audit events are strictly partitioned by organization.
    """
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    org_type: Mapped[str] = mapped_column(
        String(50),
        default="GOVERNMENT_DEPARTMENT",
        nullable=False,
        comment="GOVERNMENT_DEPARTMENT | PROCURING_ENTITY | VENDOR_ENTERPRISE"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    tenders: Mapped[List["Tender"]] = relationship("Tender", back_populates="organization", cascade="all, delete-orphan")
    vendors: Mapped[List["Vendor"]] = relationship("Vendor", back_populates="organization", cascade="all, delete-orphan")
    audit_events: Mapped[List["AuditEvent"]] = relationship("AuditEvent", back_populates="organization", cascade="all, delete-orphan")
