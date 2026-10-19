import io
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.models import (
    Base,
    Organization,
    User,
    Tender,
    TenderRequirement,
    Vendor,
    VendorDocument,
    DocumentVersion,
    AnalysisJob,
    ExtractedField,
    ComplianceFinding,
    HumanReview,
    AuditEvent,
)


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == settings.PROJECT_NAME


@pytest.mark.asyncio
async def test_secure_pdf_upload():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Construct authentic dummy PDF bytes with %PDF- header
        pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        files = {
            "file": ("gst_certificate.pdf", io.BytesIO(pdf_bytes), "application/pdf")
        }
        response = await client.post(f"{settings.API_V1_PREFIX}/documents/upload", files=files)
        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        assert data["file_name"] == "gst_certificate.pdf"
        assert data["mime_type"] == "application/pdf"
        assert len(data["sha256_hash"]) == 64
        assert data["file_size_bytes"] == len(pdf_bytes)


@pytest.mark.asyncio
async def test_upload_spoofed_file_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # A file with .pdf extension but fake / non-PDF content (e.g. bash script or exe)
        fake_bytes = b"echo 'malicious script'; exit 0"
        files = {
            "file": ("malicious.pdf", io.BytesIO(fake_bytes), "application/pdf")
        }
        response = await client.post(f"{settings.API_V1_PREFIX}/documents/upload", files=files)
        # Should be rejected with 415 Unsupported Media Type due to failed magic bytes check
        assert response.status_code == 415


@pytest.mark.asyncio
async def test_upload_empty_file_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "file": ("empty.pdf", io.BytesIO(b""), "application/pdf")
        }
        response = await client.post(f"{settings.API_V1_PREFIX}/documents/upload", files=files)
        assert response.status_code == 400


def test_models_and_tenant_isolation():
    # Verify all 12 requested models are present
    expected_tables = {
        "organizations",
        "users",
        "tenders",
        "tender_requirements",
        "vendors",
        "vendor_documents",
        "document_versions",
        "analysis_jobs",
        "extracted_fields",
        "compliance_findings",
        "human_reviews",
        "audit_events",
    }
    registered_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(registered_tables)

    # Verify tenant isolation on tenant-scoped tables
    tenant_tables = [
        "users",
        "tenders",
        "vendors",
        "vendor_documents",
        "analysis_jobs",
        "human_reviews",
        "audit_events",
    ]
    for table_name in tenant_tables:
        table = Base.metadata.tables[table_name]
        assert "organization_id" in table.c, f"Table {table_name} must have organization_id for tenant isolation"
        col = table.c["organization_id"]
        assert not col.nullable, f"organization_id in {table_name} must be non-nullable"
        assert len(col.foreign_keys) > 0, f"organization_id in {table_name} must be a ForeignKey to organizations"
