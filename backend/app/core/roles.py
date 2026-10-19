from enum import Enum
from typing import Set


class UserRole(str, Enum):
    """
    Standard Role-Based Access Control (RBAC) definitions
    for TenderGuard AI Government Procurement Verification.
    """
    ADMIN = "ADMIN"
    PROCUREMENT_OFFICER = "PROCUREMENT_OFFICER"
    REVIEWER = "REVIEWER"
    VENDOR = "VENDOR"
    READ_ONLY = "READ_ONLY"


# Aliases for legacy / demo roles
ROLE_ALIASES = {
    "EVALUATOR": UserRole.REVIEWER,
    "AUDITOR": UserRole.READ_ONLY,
    "GUEST": UserRole.READ_ONLY,
    "VENDOR_REPRESENTATIVE": UserRole.VENDOR,
    "SUPERUSER": UserRole.ADMIN,
}


def normalize_role(role_str: str) -> UserRole:
    """Normalizes any role string or alias to a canonical UserRole."""
    normalized = role_str.strip().upper()
    if normalized in ROLE_ALIASES:
        return ROLE_ALIASES[normalized]
    try:
        return UserRole(normalized)
    except ValueError:
        return UserRole.READ_ONLY
