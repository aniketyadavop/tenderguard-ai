from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, TenantScopedMixin, generate_uuid

if TYPE_CHECKING:
    from backend.app.models.organization import Organization
    from backend.app.models.vendor import Vendor
    from backend.app.models.document import VendorDocument


class Tender(Base, TimestampMixin, TenantScopedMixin):
    """
    Tender specifications under GeM / CPPP guidelines.
    """
    __tablename__ = "tenders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tender_ref_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False)
    portal: Mapped[str] = mapped_column(String(100), default="Government e-Marketplace (GeM 4.0)", nullable=False)
    bid_opening_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submission_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    minimum_turnover: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    validity_requirement: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="tenders")
    requirements: Mapped[List["TenderRequirement"]] = relationship(
        "TenderRequirement", back_populates="tender", cascade="all, delete-orphan"
    )
    vendors: Mapped[List["Vendor"]] = relationship("Vendor", back_populates="tender")


class TenderRequirement(Base, TimestampMixin):
    """
    Specific mandatory or optional document checklist item required for a tender.
    """
    __tablename__ = "tender_requirements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tender_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenders.id", ondelete="CASCADE"), index=True, nullable=False
    )
    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="GST_CERTIFICATE | PAN_CARD | UDYAM_MSME | STARTUP_INDIA | OEM_MAF"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rule_code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    validation_criteria: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    tender: Mapped["Tender"] = relationship("Tender", back_populates="requirements")
    vendor_documents: Mapped[List["VendorDocument"]] = relationship("VendorDocument", back_populates="requirement")
