from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.extraction import BoundingBox, DocumentExtractionResult


class RuleStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW = "REVIEW"
    UNVERIFIED = "UNVERIFIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class RuleSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class RuleFinding(BaseModel):
    """
    Standardized, explainable finding emitted by a deterministic compliance rule.
    """
    rule_id: str = Field(..., description="Machine-readable rule code (e.g. 'RULE_PAN_GSTIN_MATCH')")
    rule_name: str = Field(..., description="Human-readable rule title")
    document_type: str = Field(..., description="Document type evaluated")
    status: RuleStatus = Field(..., description="PASS | FAIL | REVIEW | UNVERIFIED | NOT_APPLICABLE")
    severity: RuleSeverity = Field(RuleSeverity.INFO, description="CRITICAL | WARNING | INFO")
    title: str = Field(..., description="Headline describing finding")
    simple_reason: str = Field(..., description="Plain English justification with zero legal jargon")
    expected_rule: str = Field(..., description="Statutory rule citation from GeM / GFR 2017")
    confidence: str = Field("99.0%", description="Confidence percentage string")
    field_name: Optional[str] = Field(None, description="Specific field associated with finding")
    evidence_reference: Optional[str] = Field(None, description="Spatial evidence trace reference")
    bounding_box: Optional[BoundingBox] = Field(None, description="2D bounding box on the source document")


class EvaluationContext(BaseModel):
    """
    Complete context passed into the deterministic rules engine.
    """
    vendor_id: str
    vendor_name: str
    tender_id: str = "GeM/2026/B/89412"
    tender_deadline: str = "2026-10-18"
    validity_requirement: str = "2026-11-30"
    mandatory_document_types: List[str] = Field(
        default_factory=lambda: ["GST_CERTIFICATE", "PAN_CARD", "OEM_MAF"]
    )
    claimed_exemptions: List[str] = Field(default_factory=list)
    documents: Dict[str, DocumentExtractionResult] = Field(default_factory=dict)


class BaseRule(ABC):
    """
    Abstract pluggable deterministic compliance rule.
    """
    rule_id: str = "BASE_RULE"
    rule_name: str = "Base Rule"
    description: str = ""
    document_type: str = "ALL"

    @abstractmethod
    def evaluate(self, context: EvaluationContext) -> List[RuleFinding]:
        """
        Executes deterministic evaluation against the context and returns findings.
        """
        pass
