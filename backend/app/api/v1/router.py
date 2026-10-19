from fastapi import APIRouter
from backend.app.api.v1.endpoints import upload, analysis, review, vendors, auth, audit, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Security"])
api_router.include_router(vendors.router, prefix="/vendors", tags=["Vendors"])
api_router.include_router(upload.router, prefix="/documents", tags=["Documents"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(review.router, prefix="/review", tags=["Review"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Trail"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports & Export"])
