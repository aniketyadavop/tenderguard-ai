from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.analysis import StartAnalysisRequest, JobStatusResponse
from backend.app.services.job_service import JobService
from backend.app.services.pipeline_service import PipelineService

from backend.app.core.roles import UserRole
from backend.app.models.user import User
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import require_roles, get_current_user

router = APIRouter()


@router.post(
    "/start",
    response_model=JobStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start Asynchronous Document Verification",
    description="Queues a multi-document vendor filing into the background verification pipeline."
)
def start_analysis(
    req: StartAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER, UserRole.REVIEWER, UserRole.VENDOR)),
    db: Session = Depends(get_db)
):
    # 1. Initialize tracked job in database with vendor and organization
    job = JobService.create_job(
        db=db,
        vendor_id=req.vendor_id,
        organization_id=req.organization_id,
        vendor_name=req.vendor_name
    )

    # Log audit event
    AuditService.log_event(
        db=db,
        organization_id=req.organization_id,
        event_type="ANALYSIS_JOB_QUEUED",
        entity_type="AnalysisJob",
        entity_id=job.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        description=f"User '{current_user.email}' queued document verification job '{job.id}' for vendor '{req.vendor_name}'.",
        metadata={"vendor_id": req.vendor_id, "files_count": len(req.uploaded_files)}
    )
    db.commit()

    # 2. Queue background task
    background_tasks.add_task(
        PipelineService.run_dossier_analysis,
        job_id=job.id,
        vendor_id=req.vendor_id,
        vendor_name=req.vendor_name,
        organization_id=req.organization_id,
        uploaded_files=req.uploaded_files,
        tender_id=req.tender_id,
        delete_temp_files=True
    )

    return JobStatusResponse(
        job_id=job.id,
        vendor_id=job.vendor_id,
        status=job.status,
        current_stage=job.current_stage,
        progress_pct=job.progress_pct,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get Analysis Job Status",
    description="Polls real-time state, stage (1-4), and progress percentage of an ongoing verification job."
)
def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = JobService.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis job with ID '{job_id}' not found."
        )

    return JobStatusResponse(
        job_id=job.id,
        vendor_id=job.vendor_id,
        status=job.status,
        current_stage=job.current_stage,
        progress_pct=job.progress_pct,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message
    )


@router.post(
    "/jobs/{job_id}/cancel",
    response_model=JobStatusResponse,
    summary="Cancel Analysis Job",
    description="Halts processing and marks the analysis job as CANCELLED."
)
def cancel_job(
    job_id: str,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER, UserRole.REVIEWER)),
    db: Session = Depends(get_db)
):
    job = JobService.cancel_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis job with ID '{job_id}' not found."
        )

    return JobStatusResponse(
        job_id=job.id,
        vendor_id=job.vendor_id,
        status=job.status,
        current_stage=job.current_stage,
        progress_pct=job.progress_pct,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message
    )
