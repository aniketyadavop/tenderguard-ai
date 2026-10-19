import uuid
import hashlib
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.vendor import Vendor
from backend.app.models.document import VendorDocument, DocumentVersion
from backend.app.models.analysis import ExtractedField, ComplianceFinding
from backend.app.models.audit import AuditEvent
from backend.app.schemas.extraction import DocumentExtractionResult
from backend.app.rules.engine import DossierEvaluationResult


class PersistenceService:
    """
    Transactional persistence service for saving extraction outputs,
    bounding box geometries, compliance findings, and audit trails.
    """

    @staticmethod
    def persist_dossier_results(
        db: Session,
        vendor_id: str,
        organization_id: str,
        extraction_results: List[DocumentExtractionResult],
        evaluation_result: DossierEvaluationResult,
        audit_time_seconds: float = 3.5
    ) -> Vendor:
        # 1. Fetch and update Vendor record
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            vendor = Vendor(
                id=vendor_id,
                organization_id=organization_id,
                name=evaluation_result.vendor_name,
                overall_status=evaluation_result.overall_status,
                confidence_score=evaluation_result.confidence_score,
                audit_time_seconds=audit_time_seconds,
                summary=evaluation_result.summary
            )
            db.add(vendor)
            db.flush()
        else:
            if evaluation_result.vendor_name:
                vendor.name = evaluation_result.vendor_name
            vendor.overall_status = evaluation_result.overall_status
            vendor.confidence_score = evaluation_result.confidence_score
            vendor.audit_time_seconds = audit_time_seconds
            vendor.summary = evaluation_result.summary

        # Map document_type to list of findings for that document
        findings_by_doc_type: Dict[str, List[Any]] = {}
        for finding in evaluation_result.findings:
            findings_by_doc_type.setdefault(finding.document_type, []).append(finding)

        # 2. Persist Documents, Versions, Extracted Fields, and Findings
        for doc_res in extraction_results:
            vendor_doc = db.query(VendorDocument).filter(
                VendorDocument.vendor_id == vendor_id,
                VendorDocument.document_type == doc_res.document_type
            ).first()

            doc_status = "COMPLIANT"
            doc_findings = findings_by_doc_type.get(doc_res.document_type, [])
            if any(f.status.value == "FAIL" for f in doc_findings):
                doc_status = "NON_COMPLIANT"
            elif any(f.status.value == "REVIEW" for f in doc_findings):
                doc_status = "REQUIRES_REVIEW"

            if not vendor_doc:
                vendor_doc = VendorDocument(
                    id=doc_res.document_id if not db.query(VendorDocument).filter(VendorDocument.id == doc_res.document_id).first() else str(uuid.uuid4()),
                    organization_id=organization_id,
                    vendor_id=vendor_id,
                    document_type=doc_res.document_type,
                    title=doc_res.title,
                    form_type=doc_res.form_type,
                    status=doc_status
                )
                db.add(vendor_doc)
                db.flush()
            else:
                vendor_doc.status = doc_status

            # Extract or compute document version SHA256
            sha256_hash = hashlib.sha256(doc_res.raw_text.encode("utf-8")).hexdigest()

            # Create DocumentVersion with unique server UUID
            doc_version = DocumentVersion(
                vendor_document_id=vendor_doc.id,
                version_number=1,
                file_id=str(uuid.uuid4()),
                file_name=doc_res.metadata.get("filename", f"{doc_res.document_type.lower()}.pdf"),
                file_size_bytes=len(doc_res.raw_text.encode("utf-8")),
                mime_type="application/pdf",
                sha256_hash=sha256_hash,
                page_count=doc_res.page_count
            )
            db.add(doc_version)
            db.flush()

            # Persist Extracted Fields with normalized bounding boxes
            for field_name, entity in doc_res.fields.items():
                bbox_dict = None
                if entity.bounding_box:
                    bbox_dict = entity.bounding_box.model_dump()

                val_status = "VALID"
                if entity.bounding_box and entity.bounding_box.status == "invalid":
                    val_status = "INVALID"
                elif entity.bounding_box and entity.bounding_box.status == "warning":
                    val_status = "WARNING"

                extracted_field = ExtractedField(
                    document_version_id=doc_version.id,
                    field_key=entity.field_name,
                    field_value=entity.extracted_value,
                    normalized_value=entity.normalized_value,
                    confidence=entity.confidence,
                    page_number=entity.page_number,
                    bounding_box=bbox_dict,
                    validation_status=val_status
                )
                db.add(extracted_field)

            # Persist Compliance Findings
            for finding in doc_findings:
                cf = ComplianceFinding(
                    document_version_id=doc_version.id,
                    rule_code=finding.rule_id,
                    severity=finding.severity.value,
                    title=finding.title,
                    simple_reason=finding.simple_reason,
                    expected_rule=finding.expected_rule,
                    confidence=finding.confidence,
                    status=finding.status.value,
                    page_number=1
                )
                db.add(cf)

        # 3. Create AuditEvent with Cryptographic Signature
        now_utc = datetime.now(timezone.utc)
        audit_payload = f"{vendor_id}|{evaluation_result.overall_status}|{evaluation_result.confidence_score}|{now_utc.isoformat()}"
        sha256_sig = hashlib.sha256(audit_payload.encode("utf-8")).hexdigest()

        audit_event = AuditEvent(
            organization_id=organization_id,
            event_type="ANALYSIS_COMPLETED",
            entity_type="Vendor",
            entity_id=vendor_id,
            description=f"Automated compliance audit finished. Overall verdict: {evaluation_result.overall_status} ({evaluation_result.confidence_score}%)",
            metadata_json={
                "overall_status": evaluation_result.overall_status,
                "confidence_score": evaluation_result.confidence_score,
                "disqualification_count": len(evaluation_result.disqualification_reasons),
                "review_count": len(evaluation_result.review_notes),
            },
            sha256_signature=sha256_sig
        )
        db.add(audit_event)

        db.commit()
        db.refresh(vendor)
        return vendor
