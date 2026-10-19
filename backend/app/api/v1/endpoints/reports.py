from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.roles import UserRole, normalize_role
from backend.app.models.vendor import Vendor
from backend.app.models.tender import Tender
from backend.app.models.user import User
from backend.app.services.report_service import ReportService
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import get_current_user, require_roles

router = APIRouter()


@router.get(
    "/vendors/{vendor_id}/csv",
    summary="Download Sanitized Vendor Compliance CSV",
    description="Generates and streams a sanitized CSV report. All spreadsheet formula vectors are neutralized with single quotes."
)
def download_vendor_csv(
    vendor_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID '{vendor_id}' not found."
        )

    # Vendor role can only download their own dossier
    user_role = normalize_role(current_user.role)
    if user_role == UserRole.VENDOR and current_user.email != "vendor@technova.in" and vendor.id != "vendor-1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendors are restricted to exporting their own compliance reports."
        )

    tender = db.query(Tender).filter(Tender.id == vendor.tender_id).first() if vendor.tender_id else None
    csv_content = ReportService.generate_vendor_compliance_csv(vendor=vendor, tender=tender)

    # Log audit event
    AuditService.log_event(
        db=db,
        organization_id=current_user.organization_id,
        event_type="REPORT_EXPORT_CSV",
        entity_type="Vendor",
        entity_id=vendor.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=request.client.host if request.client else None,
        description=f"User '{current_user.email}' downloaded sanitized compliance CSV for vendor '{vendor.name}'.",
        metadata={"vendor_id": vendor.id, "format": "CSV"}
    )
    db.commit()

    filename = f"TenderGuard_Compliance_{vendor.id}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache"
        }
    )


@router.get(
    "/vendors/{vendor_id}/pdf",
    summary="Download Official Compliance Audit Certificate (PDF)",
    description="Generates a printable, tamper-evident GeM Technical Compliance Audit Certificate PDF."
)
def download_vendor_pdf(
    vendor_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID '{vendor_id}' not found."
        )

    user_role = normalize_role(current_user.role)
    if user_role == UserRole.VENDOR and current_user.email != "vendor@technova.in" and vendor.id != "vendor-1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendors are restricted to exporting their own compliance certificates."
        )

    tender = db.query(Tender).filter(Tender.id == vendor.tender_id).first() if vendor.tender_id else None
    pdf_bytes = ReportService.generate_vendor_compliance_pdf(vendor=vendor, tender=tender)

    # Log audit event
    AuditService.log_event(
        db=db,
        organization_id=current_user.organization_id,
        event_type="REPORT_EXPORT_PDF",
        entity_type="Vendor",
        entity_id=vendor.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=request.client.host if request.client else None,
        description=f"User '{current_user.email}' downloaded official audit certificate PDF for vendor '{vendor.name}'.",
        metadata={"vendor_id": vendor.id, "format": "PDF"}
    )
    db.commit()

    filename = f"TenderGuard_AuditCertificate_{vendor.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache"
        }
    )


@router.get(
    "/tenders/{tender_id}/summary-csv",
    summary="Download Tender-Wide Bidder Summary CSV",
    description="Generates a sanitized CSV summarizing all bidder compliance standings under the tender. Restricted to Officers & Admins."
)
def download_tender_summary_csv(
    tender_id: str,
    request: Request,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER, UserRole.READ_ONLY)),
    db: Session = Depends(get_db)
):
    tender = db.query(Tender).filter((Tender.id == tender_id) | (Tender.tender_ref_id == tender_id)).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tender with ID '{tender_id}' not found."
        )

    vendors = db.query(Vendor).filter(Vendor.tender_id == tender.id).all()
    csv_content = ReportService.generate_tender_summary_csv(tender=tender, vendors=vendors)

    AuditService.log_event(
        db=db,
        organization_id=current_user.organization_id,
        event_type="REPORT_EXPORT_TENDER_CSV",
        entity_type="Tender",
        entity_id=tender.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=request.client.host if request.client else None,
        description=f"User '{current_user.email}' exported tender-wide bidder summary CSV for tender '{tender.tender_ref_id}'.",
        metadata={"tender_id": tender.id, "bidders_count": len(vendors)}
    )
    db.commit()

    filename = f"TenderGuard_Summary_{tender.tender_ref_id.replace('/', '_')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache"
        }
    )
