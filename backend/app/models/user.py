from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, TenantScopedMixin, generate_uuid

if TYPE_CHECKING:
    from backend.app.models.organization import Organization
    from backend.app.models.review import HumanReview


class User(Base, TimestampMixin, TenantScopedMixin):
    """
    User entity with tenant isolation. Email is uniquely scoped per organization.
    """
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("organization_id", "email", name="uq_user_tenant_email"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50),
        default="PROCUREMENT_OFFICER",
        nullable=False,
        comment="PROCUREMENT_OFFICER | EVALUATOR | AUDITOR | VENDOR_REPRESENTATIVE | GUEST"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")
    reviews_performed: Mapped[List["HumanReview"]] = relationship("HumanReview", back_populates="reviewer")
