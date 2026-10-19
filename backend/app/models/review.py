from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, TenantScopedMixin, generate_uuid

if TYPE_CHECKING:
    from backend.app.models.vendor import Vendor
    from backend.app.models.document import VendorDocument
    from backend.app.models.user import User


class HumanReview(Base, TimestampMixin, TenantScopedMixin):
    """
    Human-in-the-Loop decision record made by a Procurement Officer.
    Preserves audit integrity ensuring AI recommendations are reviewed or overridden by human authority.
    """
    __tablename__ = "human_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    vendor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("vendors.id", ondelete="CASCADE"), index=True, nullable=False
    )
    vendor_document_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("vendor_documents.id", ondelete="SET NULL"), index=True, nullable=True
    )
    reviewer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="APPROVED | DISQUALIFIED | CLARIFICATION_REQUESTED"
    )
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    exemption_granted: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    clarification_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    clarification_notice_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="reviews")
    vendor_document: Mapped[Optional["VendorDocument"]] = relationship("VendorDocument", back_populates="reviews")
    reviewer: Mapped["User"] = relationship("User", back_populates="reviews_performed")
