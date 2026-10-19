import io
from datetime import datetime, timezone, timedelta
import pytest
import pymupdf
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.core.roles import UserRole
from backend.app.core.security import create_access_token
from backend.app.models.user import User
from backend.app.services.document_parser import DocumentParser
from backend.app.rules import (
    RuleStatus,
    EvaluationContext,
    RulesEngine,
    DocumentPresenceRule,
    IdentifierFormattingRule,
    CertificateExpirationRule,
    CrossDocumentConsistencyRule,
)


# Helper: Generate in-memory synthetic PDF with PyMuPDF
def create_synthetic_pdf(text_lines, num_pages=1):
    doc = pymupdf.open()
    for _ in range(num_pages):
        page = doc.new_page(width=595, height=842)
        y = 50
        for line in text_lines:
            page.insert_text((50, y), line, fontsize=11)
            y += 25
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ==============================================================================
# 1. Upload Validation Edge Cases
# ==============================================================================

@pytest.mark.asyncio
async def test_upload_edge_cases():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # A. Malicious binary pretending to be PDF (Windows PE executable header)
        pe_fake_pdf = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00FAKE_WINDOWS_BINARY"
        res_spoofed = await client.post(
            f"{settings.API_V1_PREFIX}/documents/upload",
            files={"file": ("malware_payload.pdf", pe_fake_pdf, "application/pdf")}
        )
        assert res_spoofed.status_code == 415
        assert "does not match allowed" in res_spoofed.json()["detail"]

        # B. Disallowed extension (.sh)
        res_sh = await client.post(
            f"{settings.API_V1_PREFIX}/documents/upload",
            files={"file": ("script.sh", b"#!/bin/bash\necho dangerous", "application/x-sh")}
        )
        assert res_sh.status_code == 400
        assert "not supported" in res_sh.json()["detail"]

        # C. Zero-byte file
        res_empty = await client.post(
            f"{settings.API_V1_PREFIX}/documents/upload",
            files={"file": ("empty.pdf", b"", "application/pdf")}
        )
        assert res_empty.status_code == 400
        assert "empty" in res_empty.json()["detail"]

        # D. Uppercase extension (.PDF) with valid PDF bytes
        valid_synthetic_pdf = create_synthetic_pdf(["Government e-Marketplace Certificate", "Valid Document"])
        res_upper = await client.post(
            f"{settings.API_V1_PREFIX}/documents/upload",
            files={"file": ("LEGAL_DOCUMENT.PDF", valid_synthetic_pdf, "application/pdf")}
        )
        assert res_upper.status_code == 201
        assert res_upper.json()["mime_type"] == "application/pdf"
        assert res_upper.json()["file_size_bytes"] > 0


# ==============================================================================
# 2. Document Extraction Edge Cases (PyMuPDF)
# ==============================================================================

def test_document_parser_extraction_edge_cases():
    parser = DocumentParser()

    # A. Multi-page synthetic PDF with Indian currency & Unicode characters
    lines = [
        "TechNova Infotech Private Limited",
        "FORM GST REG-06",
        "GSTIN: 27AABCT2341P1ZB",
        "Turnover: ₹5,00,00,000 (Five Crore Rupees)",
        "Registered Office: Andheri East, Mumbai — 400093"
    ]
    multi_page_pdf = create_synthetic_pdf(lines, num_pages=3)
    res = parser.parse_document(
        file_input=multi_page_pdf,
        document_id="doc-synth-multipage",
        filename="gst_multi.pdf",
        document_type_hint="GST_CERTIFICATE"
    )

    assert res.page_count == 3
    assert "TechNova" in res.raw_text
    assert "gstin" in res.fields
    assert res.fields["gstin"].extracted_value == "27AABCT2341P1ZB"
    assert res.fields["gstin"].bounding_box is not None
    assert res.fields["gstin"].page_number == 1

    # B. Synthetic PDF with empty text page (graceful handling, 0 tokens, no exception)
    empty_doc = pymupdf.open()
    empty_doc.new_page(width=595, height=842)  # blank page
    empty_bytes = empty_doc.tobytes()
    empty_doc.close()

    empty_res = parser.parse_document(
        file_input=empty_bytes,
        document_id="doc-blank",
        filename="blank.pdf"
    )
    assert empty_res.page_count == 1
    assert empty_res.raw_text.strip() == ""

    # C. Corrupted bytes handling raises ValueError/RuntimeError
    with pytest.raises(Exception):
        parser.parse_document(
            file_input=b"CORRUPTED_NON_PDF_STREAM",
            document_id="doc-corrupt",
            filename="corrupt.pdf"
        )


# ==============================================================================
# 3. Deterministic Rules Engine Edge Cases
# ==============================================================================

def test_deterministic_rules_edge_cases():
    parser = DocumentParser()
    rules_engine = RulesEngine()

    # A. Expired / Cancelled GST Certificate -> NON_COMPLIANT
    cancelled_gst = create_synthetic_pdf([
        "FORM GST REG-06",
        "GSTIN: 07AAACA9921K1ZN",
        "Legal Name: Apex Systems LLP",
        "Period of Validity: Cancelled w.e.f. 14/01/2024",
    ])
    pan_doc = create_synthetic_pdf([
        "PERMANENT ACCOUNT NUMBER: AAACA9921K",
        "APEX SYSTEMS LLP",
    ])

    docs_cancelled = {
        "GST_CERTIFICATE": parser.parse_document(cancelled_gst, "doc-c1", "gst_cancelled.pdf"),
        "PAN_CARD": parser.parse_document(pan_doc, "doc-c2", "pan.pdf")
    }

    ctx_cancelled = EvaluationContext(
        vendor_id="vendor-cancelled",
        vendor_name="Apex Systems LLP",
        tender_id="GeM/2026/B/89412",
        documents=docs_cancelled
    )
    res_cancelled = rules_engine.evaluate_dossier(ctx_cancelled)
    assert res_cancelled.overall_status == "NON_COMPLIANT"
    assert any("GST" in f.rule_id or "VALIDITY" in f.rule_id for f in res_cancelled.findings if f.status == RuleStatus.FAIL)

    # B. PAN / GSTIN Mismatch -> NON_COMPLIANT
    valid_gst = create_synthetic_pdf([
        "FORM GST REG-06",
        "GSTIN: 27AABCT2341P1ZB",
        "Legal Name: TechNova Infotech Pvt Ltd",
        "Period of Validity: From 15/04/2021 to Unlimited",
    ])
    mismatched_pan = create_synthetic_pdf([
        "PERMANENT ACCOUNT NUMBER: ZZZZZ9999Z",  # Completely different PAN
        "Name: TechNova Infotech Pvt Ltd",
    ])
    docs_mismatched = {
        "GST_CERTIFICATE": parser.parse_document(valid_gst, "doc-m1", "gst.pdf"),
        "PAN_CARD": parser.parse_document(mismatched_pan, "doc-m2", "pan.pdf")
    }
    ctx_mismatch = EvaluationContext(
        vendor_id="vendor-mismatch",
        vendor_name="TechNova Infotech Pvt Ltd",
        tender_id="GeM/2026/B/89412",
        documents=docs_mismatched
    )
    res_mismatch = rules_engine.evaluate_dossier(ctx_mismatch)
    assert res_mismatch.overall_status == "NON_COMPLIANT"
    assert any("PAN" in f.rule_id for f in res_mismatch.findings if f.status == RuleStatus.FAIL)

    # C. Missing Mandatory Document -> NON_COMPLIANT
    docs_missing = {
        "GST_CERTIFICATE": parser.parse_document(valid_gst, "doc-only-gst", "gst.pdf")
    }
    ctx_missing = EvaluationContext(
        vendor_id="vendor-missing-pan",
        vendor_name="TechNova Infotech Pvt Ltd",
        tender_id="GeM/2026/B/89412",
        documents=docs_missing
    )
    res_missing = rules_engine.evaluate_dossier(ctx_missing)
    assert res_missing.overall_status == "NON_COMPLIANT"
    assert any(f.status == RuleStatus.FAIL and "PRESENCE" in f.rule_id for f in res_missing.findings)


# ==============================================================================
# 4. Role Permissions Edge Cases
# ==============================================================================

@pytest.mark.asyncio
async def test_role_permissions_edge_cases():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # A. Expired JWT token returns 401
        expired_token = create_access_token(
            subject="user-officer-default",
            role=UserRole.PROCUREMENT_OFFICER.value,
            org_id="org-gem-meity",
            expires_delta=timedelta(seconds=-10)  # already expired
        )
        expired_res = await client.get(
            f"{settings.API_V1_PREFIX}/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert expired_res.status_code == 401
        assert "expired" in expired_res.json()["detail"].lower()

        # B. Tampered token signature returns 401
        tampered_token = expired_token[:-8] + "TAMPERED"
        tampered_res = await client.get(
            f"{settings.API_V1_PREFIX}/auth/me",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )
        assert tampered_res.status_code == 401

        # C. Deactivated user returns 403
        db = SessionLocal()
        deact_user = db.query(User).filter(User.email == "deactivated_user@gem.gov.in").first()
        if not deact_user:
            deact_user = User(
                id="user-deactivated-edge",
                organization_id="org-gem-meity",
                email="deactivated_user@gem.gov.in",
                full_name="Deactivated Officer",
                hashed_password="mock",
                role=UserRole.PROCUREMENT_OFFICER.value,
                is_active=False
            )
            db.add(deact_user)
            db.commit()

        uid = deact_user.id
        urole = deact_user.role
        uorg = deact_user.organization_id
        db.close()

        deact_token = create_access_token(
            subject=uid,
            role=urole,
            org_id=uorg
        )
        deact_res = await client.get(
            f"{settings.API_V1_PREFIX}/auth/me",
            headers={"Authorization": f"Bearer {deact_token}"}
        )
        assert deact_res.status_code == 403
        assert "deactivated" in deact_res.json()["detail"].lower()
