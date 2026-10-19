from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.analysis import AnalysisJob
from backend.app.models.vendor import Vendor
from backend.app.models.organization import Organization


class JobService:
    """
    Manages the lifecycle and state transitions of asynchronous document analysis jobs.
    Supported states: QUEUED, PROCESSING, COMPLETED, FAILED, CANCELLED.
    Enforces referential integrity by guaranteeing parent tenant and vendor exist.
    """

    @staticmethod
    def create_job(
        db: Session,
        vendor_id: str,
        organization_id: str,
        vendor_name: Optional[str] = None
    ) -> AnalysisJob:
        # 1. Ensure Organization exists
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            org = Organization(
                id=organization_id,
                name="Procuring Department (MeitY / GeM)",
                code=f"ORG-{organization_id[:12].upper()}",
                org_type="GOVERNMENT_DEPARTMENT"
            )
            db.add(org)
            db.flush()

        # 2. Ensure Vendor exists
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            vendor = Vendor(
                id=vendor_id,
                organization_id=organization_id,
                name=vendor_name or "Bidding Vendor Dossier",
                overall_status="PENDING"
            )
            db.add(vendor)
            db.flush()

        # 3. Create Analysis Job
        job = AnalysisJob(
            vendor_id=vendor_id,
            organization_id=organization_id,
            status="QUEUED",
            current_stage=1,
            progress_pct=0,
            started_at=datetime.now(timezone.utc)
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def update_stage(
        db: Session,
        job_id: str,
        stage: int,
        progress_pct: int,
        status: str = "PROCESSING"
    ) -> Optional[AnalysisJob]:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job or job.status in ["CANCELLED", "FAILED"]:
            return job

        job.status = status
        job.current_stage = stage
        job.progress_pct = progress_pct
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def complete_job(db: Session, job_id: str) -> Optional[AnalysisJob]:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            return None

        job.status = "COMPLETED"
        job.current_stage = 4
        job.progress_pct = 100
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def fail_job(db: Session, job_id: str, error_message: str) -> Optional[AnalysisJob]:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            return None

        job.status = "FAILED"
        job.error_message = error_message
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def cancel_job(db: Session, job_id: str) -> Optional[AnalysisJob]:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            return None

        if job.status not in ["COMPLETED", "FAILED"]:
            job.status = "CANCELLED"
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(job)
        return job

    @staticmethod
    def get_job(db: Session, job_id: str) -> Optional[AnalysisJob]:
        return db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
