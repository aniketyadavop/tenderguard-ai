from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, TenantScopedMixin, generate_uuid

if TYPE_CHECKING:
    from backend.app.models.organization import Organization
    from backend.app.models.tender import Tender
    from backend.app.models.document import VendorDocument
    from backend.app.models.analysis import AnalysisJob
    from backend.app.models.review import HumanReview


class Vendor(Base, TimestampMixin, TenantScopedMixin):
    """
    Bidding entity submitting compliance dossiers for tender audit.
    """
    __tablename__ = "vendors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tender_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("tenders.id", ondelete="SET NULL"), index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cin: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pan: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    gstin: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    
    # Audit outcome
    overall_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
        comment="PENDING | COMPLIANT | NON_COMPLIANT | REQUIRES_REVIEW"
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    audit_time_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="vendors")
    tender: Mapped[Optional["Tender"]] = relationship("Tender", back_populates="vendors")
    documents: Mapped[List["VendorDocument"]] = relationship(
        "VendorDocument", back_populates="vendor", cascade="all, delete-orphan"
    )
    analysis_jobs: Mapped[List["AnalysisJob"]] = relationship(
        "AnalysisJob", back_populates="vendor", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["HumanReview"]] = relationship(
        "HumanReview", back_populates="vendor", cascade="all, delete-orphan"
    )
