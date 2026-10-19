import os
import io
import pytest
import fitz
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.models.organization import Organization
from backend.app.models.vendor import Vendor
from backend.app.models.document import VendorDocument, DocumentVersion
from backend.app.models.analysis import ExtractedField, ComplianceFinding, AnalysisJob
from backend.app.models.review import HumanReview
from backend.app.models.audit import AuditEvent
from backend.app.services.job_service import JobService
from backend.app.services.pipeline_service import PipelineService


def create_sample_pdf(text_lines: list) -> bytes:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    p = fitz.Point(50, 100)
    for line in text_lines:
        page.insert_text(p, line, fontsize=12)
        p.y += 24
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def setup_test_tenant(db):
    org = db.query(Organization).filter(Organization.id == "org-test-4").first()
    if not org:
        org = Organization(
            id="org-test-4",
            name="Test MeitY Procurement Org",
            code="MEITY-TEST-4",
            org_type="GOVERNMENT_DEPARTMENT"
        )
        db.add(org)
        db.commit()
    return org


def test_job_service_lifecycle():
    db = SessionLocal()
    try:
        setup_test_tenant(db)
        # Create job
        job = JobService.create_job(db, vendor_id="vendor-test-job", organization_id="org-test-4")
        assert job.status == "QUEUED"
        assert job.current_stage == 1

        # Update stage
        JobService.update_stage(db, job.id, stage=2, progress_pct=50)
        updated = JobService.get_job(db, job.id)
        assert updated.status == "PROCESSING"
        assert updated.current_stage == 2
        assert updated.progress_pct == 50

        # Complete job
        JobService.complete_job(db, job.id)
        completed = JobService.get_job(db, job.id)
        assert completed.status == "COMPLETED"
        assert completed.progress_pct == 100
        assert completed.completed_at is not None

        # Test cancel
        job_cancel = JobService.create_job(db, vendor_id="vendor-cancel", organization_id="org-test-4")
        JobService.cancel_job(db, job_cancel.id)
        cancelled = JobService.get_job(db, job_cancel.id)
        assert cancelled.status == "CANCELLED"
    finally:
        db.close()


def test_pipeline_persistence_and_file_cleanup():
    db = SessionLocal()
    try:
        setup_test_tenant(db)
        job = JobService.create_job(db, vendor_id="vendor-technova-live", organization_id="org-test-4")
        job_id = job.id

        # Create temporary file on disk
        os.makedirs(settings.UPLOAD_STORAGE_DIR, exist_ok=True)
        temp_pdf_path = os.path.join(settings.UPLOAD_STORAGE_DIR, "temp_gst_technova.pdf")
        pdf_bytes = create_sample_pdf([
            "FORM GST REG-06",
            "GSTIN: 27AABCT2341P1ZB",
            "Legal Name: TechNova Infotech Private Limited",
            "Period of Validity: From 15/04/2021 to Unlimited",
        ])
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_bytes)

        assert os.path.exists(temp_pdf_path)

        # Run pipeline
        uploaded_files = [
            {
                "file_id": "file-gst-001",
                "file_name": "gst_cert.pdf",
                "storage_path": temp_pdf_path,
                "document_type_hint": "GST"
            }
        ]

        PipelineService.run_dossier_analysis(
            job_id=job_id,
            vendor_id="vendor-technova-live",
            vendor_name="TechNova Infotech Pvt. Ltd.",
            organization_id="org-test-4",
            uploaded_files=uploaded_files,
            tender_id="GeM/2026/B/89412",
            delete_temp_files=True
        )

        # Re-query fresh from DB (clearing session cache)
        db.expire_all()
        db_job = JobService.get_job(db, job_id)
        assert db_job.status == "COMPLETED"
        assert db_job.current_stage == 4

        # 2. Verify Database records persisted
        vendor = db.query(Vendor).filter(Vendor.id == "vendor-technova-live").first()
        assert vendor is not None
        assert vendor.name == "TechNova Infotech Pvt. Ltd."

        # Verify Document & Version
        docs = db.query(VendorDocument).filter(VendorDocument.vendor_id == vendor.id).all()
        assert len(docs) > 0
        doc = docs[0]
        assert doc.document_type == "GST_CERTIFICATE"

        versions = db.query(DocumentVersion).filter(DocumentVersion.vendor_document_id == doc.id).all()
        assert len(versions) > 0
        version = versions[0]
        assert len(version.sha256_hash) == 64

        # Verify Extracted Fields with Bounding Boxes
        fields = db.query(ExtractedField).filter(ExtractedField.document_version_id == version.id).all()
        assert len(fields) > 0
        gstin_field = next((f for f in fields if f.field_key == "gstin"), None)
        assert gstin_field is not None
        assert gstin_field.field_value == "27AABCT2341P1ZB"
        assert gstin_field.bounding_box is not None
        assert "x" in gstin_field.bounding_box

        # Verify Audit Event with Cryptographic Signature
        audit_events = db.query(AuditEvent).filter(AuditEvent.entity_id == vendor.id).all()
        assert len(audit_events) > 0
        audit = audit_events[-1]
        assert len(audit.sha256_signature) == 64

        # 3. Verify Zero-Retention File Purge: File must be deleted from disk
        assert not os.path.exists(temp_pdf_path), "Zero-retention failed: Temporary file was not deleted after processing!"

    finally:
        db.close()


@pytest.mark.asyncio
async def test_human_review_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Pre-seed vendor in DB
        db = SessionLocal()
        setup_test_tenant(db)
        v = Vendor(
            id="vendor-review-demo",
            organization_id="org-test-4",
            name="Bharat Cloud Dynamics LLP",
            overall_status="REQUIRES_REVIEW",
            confidence_score=82.5,
            audit_time_seconds=4.1
        )
        db.merge(v)
        doc = VendorDocument(
            id="doc-review-oem",
            organization_id="org-test-4",
            vendor_id="vendor-review-demo",
            document_type="OEM_MAF",
            title="Manufacturer Authorization Form",
            status="REQUIRES_REVIEW"
        )
        db.merge(doc)
        db.commit()
        db.close()

        # 1. Post Officer Approval Override
        payload = {
            "vendor_id": "vendor-review-demo",
            "vendor_document_id": "doc-review-oem",
            "action": "APPROVED",
            "notes": "Reviewed faint physical OEM rubber stamp. Authorized signatory designation verified authentic against OEM portal records.",
            "exemption_granted": "Faint Seal Manual Verification Override",
            "reviewer_name": "S. Sharma, Joint Director - Procurement"
        }
        res = await client.post(f"{settings.API_V1_PREFIX}/review/decision", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["action"] == "APPROVED"
        assert "id" in data
        assert data["vendor_id"] == "vendor-review-demo"

        # 2. Verify Document Status updated in DB
        db = SessionLocal()
        updated_doc = db.query(VendorDocument).filter(VendorDocument.id == "doc-review-oem").first()
        assert updated_doc.status == "COMPLIANT"

        # Verify Audit Event was recorded
        audit = db.query(AuditEvent).filter(AuditEvent.entity_id == data["id"]).first()
        assert audit is not None
        assert audit.event_type == "OFFICER_OVERRIDE_RECORDED"
        assert len(audit.sha256_signature) == 64
        db.close()

        # 3. Get Review History
        hist_res = await client.get(f"{settings.API_V1_PREFIX}/review/history/vendor-review-demo")
        assert hist_res.status_code == 200
        history = hist_res.json()
        assert len(history) >= 1
        assert history[0]["action"] == "APPROVED"


@pytest.mark.asyncio
async def test_analysis_api_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Pre-create a queued job directly in DB to test cancel endpoint
        db = SessionLocal()
        setup_test_tenant(db)
        queued_job = JobService.create_job(db, vendor_id="vendor-cancel-api", organization_id="org-test-4")
        queued_job_id = queued_job.id
        db.close()

        # Check job status via API
        status_res = await client.get(f"{settings.API_V1_PREFIX}/analysis/jobs/{queued_job_id}")
        assert status_res.status_code == 200
        assert status_res.json()["job_id"] == queued_job_id
        assert status_res.json()["status"] == "QUEUED"

        # Cancel job via API
        cancel_res = await client.post(f"{settings.API_V1_PREFIX}/analysis/jobs/{queued_job_id}/cancel")
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "CANCELLED"

        # Also test starting a job via API
        start_payload = {
            "vendor_id": "vendor-api-start-test",
            "vendor_name": "TechNova Infotech Pvt. Ltd.",
            "organization_id": "org-test-4",
            "tender_id": "GeM/2026/B/89412",
            "uploaded_files": []
        }
        start_res = await client.post(f"{settings.API_V1_PREFIX}/analysis/start", json=start_payload)
        assert start_res.status_code == 202
        assert "job_id" in start_res.json()
