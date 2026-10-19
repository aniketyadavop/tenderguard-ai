from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, TenantScopedMixin, generate_uuid

if TYPE_CHECKING:
    from backend.app.models.vendor import Vendor
    from backend.app.models.document import DocumentVersion


class AnalysisJob(Base, TimestampMixin, TenantScopedMixin):
    """
    Asynchronous document verification job tracking the 4-stage pipeline.
    Stage 1: Spatial OCR Extraction
    Stage 2: Vision-Language Entity Parsing
    Stage 3: Cross-Document Reconciliation
    Stage 4: Explainability Tree & Evidence Generation
    """
    __tablename__ = "analysis_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    vendor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("vendors.id", ondelete="CASCADE"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="QUEUED",
        nullable=False,
        comment="QUEUED | PROCESSING | COMPLETED | FAILED"
    )
    current_stage: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    progress_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="analysis_jobs")


class ExtractedField(Base, TimestampMixin):
    """
    Spatial entity extracted from document pages with 2D bounding boxes.
    """
    __tablename__ = "extracted_fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("document_versions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    field_key: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    field_value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    bounding_box: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Percentage coordinates: {x, y, width, height, label, status, text}"
    )
    validation_status: Mapped[str] = mapped_column(
        String(50),
        default="VALID",
        nullable=False,
        comment="VALID | INVALID | WARNING"
    )

    # Relationships
    document_version: Mapped["DocumentVersion"] = relationship("DocumentVersion", back_populates="extracted_fields")


class ComplianceFinding(Base, TimestampMixin):
    """
    Explainable AI audit result evaluated against procurement tender rules.
    """
    __tablename__ = "compliance_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("document_versions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    rule_code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(50),
        default="INFO",
        nullable=False,
        comment="FATAL | WARNING | INFO"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    simple_reason: Mapped[str] = mapped_column(Text, nullable=False)
    expected_rule: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), default="99.0%", nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="COMPLIANT",
        nullable=False,
        comment="COMPLIANT | NON_COMPLIANT | REQUIRES_REVIEW"
    )
    page_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    document_version: Mapped["DocumentVersion"] = relationship("DocumentVersion", back_populates="compliance_findings")
