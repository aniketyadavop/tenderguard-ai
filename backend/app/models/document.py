from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, TenantScopedMixin, generate_uuid

if TYPE_CHECKING:
    from backend.app.models.vendor import Vendor
    from backend.app.models.tender import TenderRequirement
    from backend.app.models.analysis import ExtractedField, ComplianceFinding
    from backend.app.models.review import HumanReview


class VendorDocument(Base, TimestampMixin, TenantScopedMixin):
    """
    Vendor-submitted document container (e.g. GST Certificate, PAN Card).
    Tracks version history and compliance state.
    """
    __tablename__ = "vendor_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    vendor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("vendors.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requirement_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("tender_requirements.id", ondelete="SET NULL"), index=True, nullable=True
    )
    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="GST_CERTIFICATE | PAN_CARD | UDYAM_MSME | STARTUP_INDIA | OEM_MAF | OTHER"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    form_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
        comment="PENDING | COMPLIANT | NON_COMPLIANT | REQUIRES_REVIEW"
    )

    # Relationships
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="documents")
    requirement: Mapped[Optional["TenderRequirement"]] = relationship("TenderRequirement", back_populates="vendor_documents")
    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion", back_populates="vendor_document", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["HumanReview"]] = relationship("HumanReview", back_populates="vendor_document")


class DocumentVersion(Base, TimestampMixin):
    """
    Immutable versioned file instance of an uploaded document.
    Stores cryptographic SHA-256 fingerprint and server-controlled file UUID.
    """
    __tablename__ = "document_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    vendor_document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("vendor_documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    file_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=generate_uuid, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    vendor_document: Mapped["VendorDocument"] = relationship("VendorDocument", back_populates="versions")
    extracted_fields: Mapped[List["ExtractedField"]] = relationship(
        "ExtractedField", back_populates="document_version", cascade="all, delete-orphan"
    )
    compliance_findings: Mapped[List["ComplianceFinding"]] = relationship(
        "ComplianceFinding", back_populates="document_version", cascade="all, delete-orphan"
    )
