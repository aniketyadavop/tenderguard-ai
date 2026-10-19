import io
import pytest
import fitz
from backend.app.schemas.extraction import (
    BoundingBox,
    ExtractedEntity,
    DocumentExtractionResult,
)
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


def create_sample_pdf(text_lines: list) -> bytes:
    """Helper to generate an in-memory PDF using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 standard
    p = fitz.Point(50, 100)
    for line in text_lines:
        page.insert_text(p, line, fontsize=12)
        p.y += 24
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_pymupdf_document_parser():
    parser = DocumentParser()

    # Generate sample GST certificate PDF
    pdf_bytes = create_sample_pdf([
        "Government of India / State Tax Department",
        "Registration Certificate - FORM GST REG-06",
        "GSTIN: 27AABCT2341P1ZB",
        "Legal Name: TechNova Infotech Private Limited",
        "Period of Validity: From 15/04/2021 to Unlimited (Regular)",
        "Principal Place: Plot 42, MIDC, Mumbai 400093",
    ])

    result = parser.parse_document(
        file_input=pdf_bytes,
        document_id="doc-test-gst",
        filename="gst_certificate.pdf"
    )

    assert result.document_type == "GST_CERTIFICATE"
    assert result.page_count == 1
    assert "gstin" in result.fields

    gstin_entity = result.fields["gstin"]
    assert gstin_entity.extracted_value == "27AABCT2341P1ZB"
    assert gstin_entity.normalized_value == "27AABCT2341P1ZB"
    assert gstin_entity.page_number == 1
    assert gstin_entity.bounding_box is not None
    assert gstin_entity.bounding_box.width > 0
    assert gstin_entity.bounding_box.height > 0
    assert gstin_entity.evidence_reference is not None


def test_scenario_1_technova_compliant():
    """Scenario 1: TechNova Infotech Pvt. Ltd. -> Fully Compliant"""
    parser = DocumentParser()
    engine = RulesEngine()

    gst_pdf = create_sample_pdf([
        "FORM GST REG-06",
        "GSTIN: 27AABCT2341P1ZB",
        "Legal Name: TechNova Infotech Private Limited",
        "Period of Validity: From 15/04/2021 to Unlimited",
    ])
    pan_pdf = create_sample_pdf([
        "INCOME TAX DEPARTMENT - GOVT OF INDIA",
        "PERMANENT ACCOUNT NUMBER: AABCT2341P",
        "Name: TECHNOVA INFOTECH PRIVATE LIMITED",
        "Date of Incorporation: 12/04/2021",
    ])
    oem_pdf = create_sample_pdf([
        "MANUFACTURER AUTHORIZATION FORM (MAF)",
        "Tender Ref: GeM/2026/B/89412",
        "Partner: TechNova Infotech Pvt. Ltd.",
        "Signatory: Rajesh Krishnamurthy",
    ])
    udyam_pdf = create_sample_pdf([
        "UDYAM REGISTRATION CERTIFICATE",
        "UDYAM-MH-01-0024891",
        "NAME OF ENTERPRISE: TECHNOVA INFOTECH PRIVATE LIMITED",
        "Type of Enterprise: Micro",
    ])

    docs = {
        "GST_CERTIFICATE": parser.parse_document(gst_pdf, "doc-gst", "gst.pdf"),
        "PAN_CARD": parser.parse_document(pan_pdf, "doc-pan", "pan.pdf"),
        "OEM_MAF": parser.parse_document(oem_pdf, "doc-oem", "oem.pdf"),
        "UDYAM_MSME": parser.parse_document(udyam_pdf, "doc-udyam", "udyam.pdf"),
    }

    context = EvaluationContext(
        vendor_id="vendor-1",
        vendor_name="TechNova Infotech Pvt. Ltd.",
        tender_id="GeM/2026/B/89412",
        documents=docs
    )

    result = engine.evaluate_dossier(context)
    assert result.overall_status == "COMPLIANT"
    assert result.confidence_score >= 95.0
    assert len(result.disqualification_reasons) == 0


def test_scenario_2_apex_global_disqualified():
    """Scenario 2: Apex Global Systems Ltd. -> Disqualified (Expired GST + PAN Mismatch)"""
    parser = DocumentParser()
    engine = RulesEngine()

    gst_pdf = create_sample_pdf([
        "FORM GST REG-06",
        "GSTIN: 07AAACA9921K1ZN",
        "Legal Name: Apex Systems & Services LLP",
        "Period of Validity: Cancelled w.e.f. 14/01/2024",
    ])
    pan_pdf = create_sample_pdf([
        "INCOME TAX DEPARTMENT",
        "PERMANENT ACCOUNT NUMBER: BBACA9921K",  # Differs from GSTIN's AAACA9921K!
        "Name: APEX GLOBAL SYSTEMS LIMITED",
    ])
    oem_pdf = create_sample_pdf([
        "OEM AUTHORIZATION MAF",
        "Tender Ref: GeM/2026/B/89412",
        "Partner: Apex Global Systems Ltd.",
    ])

    docs = {
        "GST_CERTIFICATE": parser.parse_document(gst_pdf, "doc-gst", "gst.pdf"),
        "PAN_CARD": parser.parse_document(pan_pdf, "doc-pan", "pan.pdf"),
        "OEM_MAF": parser.parse_document(oem_pdf, "doc-oem", "oem.pdf"),
    }

    context = EvaluationContext(
        vendor_id="vendor-2",
        vendor_name="Apex Global Systems Ltd.",
        tender_id="GeM/2026/B/89412",
        documents=docs
    )

    result = engine.evaluate_dossier(context)
    assert result.overall_status == "NON_COMPLIANT"
    assert len(result.disqualification_reasons) >= 2

    codes = [d["code"] for d in result.disqualification_reasons]
    assert "ERR_GST_CANCELLED" in codes
    assert "ERR_PAN_MISMATCH" in codes


def test_scenario_3_bharat_cloud_requires_review():
    """Scenario 3: Bharat Cloud Dynamics LLP -> Requires Human Review (Faint Seal + Near-Expiry Window)"""
    parser = DocumentParser()
    engine = RulesEngine()

    gst_pdf = create_sample_pdf([
        "FORM GST REG-06",
        "GSTIN: 29AALFB8124Q1ZP",
        "Legal Name: Bharat Cloud Dynamics LLP",
        "Period of Validity: Unlimited",
    ])
    pan_pdf = create_sample_pdf([
        "INCOME TAX DEPARTMENT",
        "PERMANENT ACCOUNT NUMBER: AALFB8124Q",
        "Name: BHARAT CLOUD DYNAMICS LLP",
    ])
    oem_pdf = create_sample_pdf([
        "MANUFACTURER AUTHORIZATION FORM",
        "Tender Ref: GeM/2026/B/89412",
        "Partner: Bharat Cloud Dynamics LLP",
        "Official rubber seal is faint and unclear (64% confidence)",
    ])
    startup_pdf = create_sample_pdf([
        "CERTIFICATE OF RECOGNITION - DPIIT",
        "Certificate No: DIPP41920",
        "Expires: 14/12/2026 (< 60 days under 2 months remaining)",
    ])

    docs = {
        "GST_CERTIFICATE": parser.parse_document(gst_pdf, "doc-gst", "gst.pdf"),
        "PAN_CARD": parser.parse_document(pan_pdf, "doc-pan", "pan.pdf"),
        "OEM_MAF": parser.parse_document(oem_pdf, "doc-oem", "oem.pdf"),
        "STARTUP_INDIA": parser.parse_document(startup_pdf, "doc-startup", "startup.pdf"),
    }

    context = EvaluationContext(
        vendor_id="vendor-3",
        vendor_name="Bharat Cloud Dynamics LLP",
        tender_id="GeM/2026/B/89412",
        documents=docs
    )

    result = engine.evaluate_dossier(context)
    assert result.overall_status == "REQUIRES_REVIEW"
    assert len(result.review_notes) >= 2


def test_discrete_statuses_supported():
    """Verify engine and rules emit all required discrete finding statuses."""
    all_statuses = {s.value for s in RuleStatus}
    required_statuses = {"PASS", "FAIL", "REVIEW", "UNVERIFIED", "NOT_APPLICABLE"}
    assert required_statuses.issubset(all_statuses)
