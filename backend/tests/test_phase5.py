import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.services.seed_data import seed_database_benchmarks


@pytest.fixture(autouse=True)
def ensure_db_seeded():
    db = SessionLocal()
    seed_database_benchmarks(db)
    db.close()


@pytest.mark.asyncio
async def test_get_current_tender_specs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(f"{settings.API_V1_PREFIX}/vendors/tenders/current")
        assert res.status_code == 200
        data = res.json()
        assert data["tenderId"] == "GeM/2026/B/89412"
        assert "Ministry of Electronics" in data["department"]
        assert len(data["mandatoryDocuments"]) >= 3


@pytest.mark.asyncio
async def test_list_and_get_vendor_dossier():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. List vendors
        res = await client.get(f"{settings.API_V1_PREFIX}/vendors")
        assert res.status_code == 200
        vendors = res.json()
        assert len(vendors) >= 3

        # 2. Get specific vendor dossier (TechNova)
        dossier_res = await client.get(f"{settings.API_V1_PREFIX}/vendors/vendor-1")
        assert dossier_res.status_code == 200
        dossier = dossier_res.json()
        assert dossier["id"] == "vendor-1"
        assert dossier["name"] == "TechNova Infotech Pvt. Ltd."
        assert dossier["overallStatus"] == "COMPLIANT"
        assert len(dossier["documents"]) >= 4

        # Check document structure for frontend DocumentRenderer
        doc = dossier["documents"][0]
        assert "id" in doc
        assert "title" in doc
        assert "extractedData" in doc
        assert "evaluation" in doc
        assert "boundingBoxes" in doc
        assert len(doc["boundingBoxes"]) > 0


@pytest.mark.asyncio
async def test_vendor_disqualification_dossier():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(f"{settings.API_V1_PREFIX}/vendors/vendor-2")
        assert res.status_code == 200
        dossier = res.json()
        assert dossier["overallStatus"] == "NON_COMPLIANT"
        assert len(dossier["disqualificationReasons"]) > 0
