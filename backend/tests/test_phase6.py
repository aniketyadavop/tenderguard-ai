import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import Session
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.core.security import decode_access_token
from backend.app.services.report_service import sanitize_csv_cell
from backend.app.services.audit_service import AuditService
from backend.app.models.audit import AuditEvent
from backend.app.models.vendor import Vendor


@pytest.mark.asyncio
async def test_auth_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Successful Admin Login
        login_res = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            json={"email": "admin@gem.gov.in", "password": "AdminPassword123!"}
        )
        assert login_res.status_code == 200
        data = login_res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "ADMIN"
        assert data["expires_in_seconds"] == 1800

        token = data["access_token"]
        # Verify token claims
        payload = decode_access_token(token)
        assert payload["role"] == "ADMIN"
        assert payload["exp"] > payload["iat"]

        # 2. Access /me endpoint with Bearer token
        me_res = await client.get(
            f"{settings.API_V1_PREFIX}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["email"] == "admin@gem.gov.in"
        assert me_data["role"] == "ADMIN"

        # 3. Invalid password rejected
        bad_login = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            json={"email": "admin@gem.gov.in", "password": "WrongPassword!"}
        )
        assert bad_login.status_code == 401
        assert "Incorrect" in bad_login.json()["detail"]

        # 4. Access /me with invalid token rejected
        bad_me = await client.get(
            f"{settings.API_V1_PREFIX}/auth/me",
            headers={"Authorization": "Bearer invalid.token.value"}
        )
        assert bad_me.status_code == 401


@pytest.mark.asyncio
async def test_rbac_authorization():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get tokens for different roles
        officer_login = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            json={"email": "officer@gem.gov.in", "password": "OfficerPassword123!"}
        )
        officer_token = officer_login.json()["access_token"]

        reviewer_login = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            json={"email": "reviewer@gem.gov.in", "password": "ReviewerPassword123!"}
        )
        reviewer_token = reviewer_login.json()["access_token"]

        vendor_login = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            json={"email": "vendor@technova.in", "password": "VendorPassword123!"}
        )
        vendor_token = vendor_login.json()["access_token"]

        auditor_login = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            json={"email": "auditor@cag.gov.in", "password": "AuditorPassword123!"}
        )
        auditor_token = auditor_login.json()["access_token"]

        # 1. Reviewer can post review decision
        rev_payload = {
            "vendor_id": "vendor-1",
            "action": "APPROVED",
            "notes": "Reviewed and confirmed valid."
        }
        rev_res = await client.post(
            f"{settings.API_V1_PREFIX}/review/decision",
            json=rev_payload,
            headers={"Authorization": f"Bearer {reviewer_token}"}
        )
        assert rev_res.status_code == 201

        # 2. Vendor FORBIDDEN from posting review decisions
        vendor_rev_res = await client.post(
            f"{settings.API_V1_PREFIX}/review/decision",
            json=rev_payload,
            headers={"Authorization": f"Bearer {vendor_token}"}
        )
        assert vendor_rev_res.status_code == 403
        assert "Access denied" in vendor_rev_res.json()["detail"]

        # 3. Read-only auditor can view audit events
        audit_res = await client.get(
            f"{settings.API_V1_PREFIX}/audit/events",
            headers={"Authorization": f"Bearer {auditor_token}"}
        )
        assert audit_res.status_code == 200

        # 4. Read-only auditor FORBIDDEN from review overrides
        auditor_rev_res = await client.post(
            f"{settings.API_V1_PREFIX}/review/decision",
            json=rev_payload,
            headers={"Authorization": f"Bearer {auditor_token}"}
        )
        assert auditor_rev_res.status_code == 403


@pytest.mark.asyncio
async def test_audit_service_and_tamper_verification():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        officer_login = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            json={"email": "officer@gem.gov.in", "password": "OfficerPassword123!"}
        )
        token = officer_login.json()["access_token"]

        # 1. Log an event manually
        db = SessionLocal()
        event = AuditService.log_event(
            db=db,
            organization_id="org-gem-meity",
            event_type="TEST_SECURITY_ACTION",
            entity_type="Vendor",
            entity_id="vendor-1",
            actor_id="user-officer-default",
            actor_role="PROCUREMENT_OFFICER",
            description="Testing cryptographic audit verification."
        )
        db.commit()
        event_id = event.id
        db.close()

        # 2. Query verify endpoint
        verify_res = await client.get(
            f"{settings.API_V1_PREFIX}/audit/verify/{event_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert verify_res.status_code == 200
        data = verify_res.json()
        assert data["is_tamper_free"] is True
        assert data["verification_status"] == "AUTHENTIC_AND_VERIFIED"

        # 3. Simulate unauthorized tamper in database
        db = SessionLocal()
        tampered_event = db.query(AuditEvent).filter(AuditEvent.id == event_id).first()
        tampered_event.description = "Tampered description trying to fake audit trail!"
        db.commit()
        db.close()

        # 4. Verification detects tampering
        tamper_res = await client.get(
            f"{settings.API_V1_PREFIX}/audit/verify/{event_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert tamper_res.status_code == 200
        tamper_data = tamper_res.json()
        assert tamper_data["is_tamper_free"] is False
        assert tamper_data["verification_status"] == "TAMPER_DETECTED"


@pytest.mark.asyncio
async def test_reports_csv_and_pdf():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        officer_login = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            json={"email": "officer@gem.gov.in", "password": "OfficerPassword123!"}
        )
        token = officer_login.json()["access_token"]

        # 1. Download Sanitized Vendor CSV
        csv_res = await client.get(
            f"{settings.API_V1_PREFIX}/reports/vendors/vendor-1/csv",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.headers["content-type"]
        assert "attachment" in csv_res.headers["content-disposition"]
        csv_text = csv_res.text
        assert "TechNova Infotech Pvt. Ltd." in csv_text
        assert "AABCT2341P" in csv_text

        # 2. Download Official PDF Certificate
        pdf_res = await client.get(
            f"{settings.API_V1_PREFIX}/reports/vendors/vendor-1/pdf",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert pdf_res.status_code == 200
        assert "application/pdf" in pdf_res.headers["content-type"]
        assert "attachment" in pdf_res.headers["content-disposition"]
        # PDF magic bytes
        assert pdf_res.content.startswith(b"%PDF-")
        assert len(pdf_res.content) > 1000

        # 3. Download Tender Bidder Summary CSV
        tender_res = await client.get(
            f"{settings.API_V1_PREFIX}/reports/tenders/tender-gem-89412/summary-csv",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert tender_res.status_code == 200
        assert "text/csv" in tender_res.headers["content-type"]
        assert "GeM/2026/B/89412" in tender_res.text


def test_csv_formula_injection_sanitization():
    # Dangerous spreadsheet formulas
    malicious_inputs = [
        "=cmd|' /C calc'!A0",
        "+1+2",
        "-5*2",
        "@SUM(A1:A10)",
        "|calc.exe",
        "%COMSPEC%",
        "\tMALICIOUS_TAB",
        "\rMALICIOUS_RETURN"
    ]
    for inp in malicious_inputs:
        sanitized = sanitize_csv_cell(inp)
        assert sanitized.startswith("'"), f"Failed to sanitize formula injection for: {inp}"

    # Benign inputs should remain untouched
    benign_inputs = [
        "TechNova Infotech Pvt. Ltd.",
        "27AABCT2341P1ZB",
        "Valid until 31/12/2027",
        "Form REG-06"
    ]
    for inp in benign_inputs:
        sanitized = sanitize_csv_cell(inp)
        assert not sanitized.startswith("'"), f"Benign input was unnecessarily escaped: {inp}"
        assert sanitized == inp
