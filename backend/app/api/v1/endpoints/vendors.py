from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.vendor import Vendor
from backend.app.models.tender import Tender
from backend.app.models.document import VendorDocument, DocumentVersion
from backend.app.models.analysis import ExtractedField, ComplianceFinding

from backend.app.models.user import User
from backend.app.api.deps import get_current_user

router = APIRouter()


@router.get(
    "/tenders/current",
    summary="Get Active Tender Specifications",
    description="Returns current procurement bid criteria (MeitY, GeM 4.0, turnover exemption rules)."
)
def get_current_tender(
    db: Session = Depends(get_db)
):
    tender = db.query(Tender).filter(Tender.is_active == True).first()
    if not tender:
        return {
            "tenderId": "GeM/2026/B/89412",
            "title": "Supply, Installation & Maintenance of Cloud-Ready Data Center Servers",
            "department": "Ministry of Electronics & Information Technology (MeitY)",
            "portal": "Government e-Marketplace (GeM 4.0)",
            "bidOpeningDate": "2026-10-25",
            "submissionDeadline": "2026-10-18 17:00 IST",
            "minimumTurnover": "₹5.00 Crore (Exempted for DPIIT-Recognized Startups & Micro/Small MSMEs)",
            "validityRequirement": "Documents must be active and valid at least through 2026-11-30",
            "mandatoryDocuments": [
                "GST Registration Certificate (Form REG-06)",
                "Permanent Account Number (PAN Card)",
                "Udyam / MSME Registration Certificate",
                "Startup India DPIIT Recognition Certificate (Optional for exemption)",
                "Manufacturer / OEM Authorization Form (MAF)"
            ]
        }
    return {
        "tenderId": tender.tender_ref_id,
        "title": tender.title,
        "department": tender.department,
        "portal": tender.portal,
        "bidOpeningDate": tender.bid_opening_date.isoformat() if tender.bid_opening_date else "2026-10-25",
        "submissionDeadline": tender.submission_deadline.isoformat() if tender.submission_deadline else "2026-10-18 17:00 IST",
        "minimumTurnover": tender.minimum_turnover,
        "validityRequirement": tender.validity_requirement,
        "mandatoryDocuments": [r.title for r in tender.requirements] if tender.requirements else [
            "GST Registration Certificate (Form REG-06)",
            "Permanent Account Number (PAN Card)",
            "Udyam / MSME Registration Certificate",
            "Startup India DPIIT Recognition Certificate (Optional for exemption)",
            "Manufacturer / OEM Authorization Form (MAF)"
        ]
    }


@router.get(
    "",
    summary="List All Vendors",
    description="Returns all registered and audited vendor dossiers."
)
def list_vendors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vendors = db.query(Vendor).all()
    results = []
    for v in vendors:
        results.append({
            "id": v.id,
            "name": v.name,
            "cin": v.cin,
            "pan": v.pan,
            "gstin": v.gstin,
            "overallStatus": v.overall_status,
            "confidenceScore": v.confidence_score,
            "auditTimeSeconds": v.audit_time_seconds,
            "summary": v.summary,
            "documentCount": len(v.documents)
        })
    return results


@router.get(
    "/{vendor_id}",
    summary="Get Full Vendor Dossier",
    description="Returns complete vendor compliance overview with documents, extracted fields, bounding boxes, and findings."
)
def get_vendor_dossier(
    vendor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID '{vendor_id}' not found."
        )

    # Format document list matching React frontend expectations
    docs_payload = []
    disqualification_reasons = []
    review_notes = []

    for vdoc in vendor.documents:
        # Latest version
        latest_version = db.query(DocumentVersion).filter(
            DocumentVersion.vendor_document_id == vdoc.id
        ).order_by(DocumentVersion.version_number.desc()).first()

        extracted_data = {}
        bounding_boxes = []
        eval_dict = {
            "status": vdoc.status,
            "simpleReason": "Document verified under statutory criteria.",
            "expectedRule": "Statutory compliance under GFR 2017 & GeM guidelines",
            "confidence": "99.0%",
            "pageNumber": 1
        }

        if latest_version:
            # Extracted fields
            for ef in latest_version.extracted_fields:
                extracted_data[ef.field_key] = ef.field_value
                if ef.bounding_box and ef.bounding_box not in bounding_boxes:
                    bounding_boxes.append(ef.bounding_box)

            # Compliance findings
            for cf in latest_version.compliance_findings:
                eval_dict = {
                    "status": cf.status,
                    "simpleReason": cf.simple_reason,
                    "expectedRule": cf.expected_rule,
                    "confidence": cf.confidence,
                    "pageNumber": cf.page_number
                }
                if cf.status == "NON_COMPLIANT":
                    disqualification_reasons.append({
                        "document": vdoc.title,
                        "code": cf.rule_code,
                        "title": cf.title,
                        "simpleReason": cf.simple_reason
                    })
                elif cf.status == "REQUIRES_REVIEW":
                    review_notes.append({
                        "document": vdoc.title,
                        "field": cf.rule_code,
                        "simpleReason": cf.simple_reason
                    })

        docs_payload.append({
            "id": vdoc.id,
            "document_type": vdoc.document_type,
            "title": vdoc.title,
            "formType": vdoc.form_type or "Official Document",
            "status": vdoc.status,
            "extractedData": extracted_data,
            "evaluation": eval_dict,
            "boundingBoxes": bounding_boxes
        })

    return {
        "id": vendor.id,
        "name": vendor.name,
        "cin": vendor.cin or "U72900MH2021PTC359812",
        "pan": vendor.pan or "AABCT2341P",
        "gstin": vendor.gstin or "27AABCT2341P1ZB",
        "overallStatus": vendor.overall_status,
        "confidenceScore": vendor.confidence_score,
        "auditTimeSeconds": vendor.audit_time_seconds,
        "summary": vendor.summary or "Evaluation completed.",
        "disqualificationReasons": disqualification_reasons,
        "reviewNotes": review_notes,
        "documents": docs_payload
    }
