import os
import time
from typing import List, Dict, Any
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.services.document_parser import DocumentParser
from backend.app.services.job_service import JobService
from backend.app.services.persistence_service import PersistenceService
from backend.app.rules.engine import RulesEngine
from backend.app.rules.base import EvaluationContext


class PipelineService:
    """
    Coordinates asynchronous background execution of the 4-stage verification pipeline:
    Stage 1: Spatial OCR Extraction
    Stage 2: Vision-Language Entity Parsing
    Stage 3: Cross-Document Reconciliation
    Stage 4: Explainability Tree & Evidence Generation
    Guarantees strict zero-retention ephemeral file deletion upon completion or failure.
    """

    @staticmethod
    def run_dossier_analysis(
        job_id: str,
        vendor_id: str,
        vendor_name: str,
        organization_id: str,
        uploaded_files: List[Dict[str, Any]],
        tender_id: str = "GeM/2026/B/89412",
        delete_temp_files: bool = True
    ) -> None:
        db = SessionLocal()
        start_time = time.time()
        parser = DocumentParser()
        rules_engine = RulesEngine()

        try:
            # Stage 1: Spatial OCR Extraction
            JobService.update_stage(db, job_id, stage=1, progress_pct=25, status="PROCESSING")
            extracted_docs = []

            for file_info in uploaded_files:
                file_path = file_info.get("storage_path")
                file_id = file_info.get("file_id")
                filename = file_info.get("file_name", "document.pdf")
                doc_type_hint = file_info.get("document_type_hint")

                if file_path and os.path.exists(file_path):
                    doc_res = parser.parse_document(
                        file_input=file_path,
                        document_id=file_id,
                        filename=filename,
                        document_type_hint=doc_type_hint
                    )
                    extracted_docs.append(doc_res)

            # Stage 2: Vision-Language Entity Parsing
            JobService.update_stage(db, job_id, stage=2, progress_pct=50, status="PROCESSING")
            docs_by_type = {doc.document_type: doc for doc in extracted_docs}

            # Stage 3: Cross-Document Reconciliation
            JobService.update_stage(db, job_id, stage=3, progress_pct=75, status="PROCESSING")
            eval_context = EvaluationContext(
                vendor_id=vendor_id,
                vendor_name=vendor_name,
                tender_id=tender_id,
                documents=docs_by_type
            )
            evaluation_result = rules_engine.evaluate_dossier(eval_context)

            # Stage 4: Explainability Tree & Evidence Generation + Persistence
            JobService.update_stage(db, job_id, stage=4, progress_pct=95, status="PROCESSING")
            elapsed_seconds = round(time.time() - start_time, 2)

            PersistenceService.persist_dossier_results(
                db=db,
                vendor_id=vendor_id,
                organization_id=organization_id,
                extraction_results=extracted_docs,
                evaluation_result=evaluation_result,
                audit_time_seconds=elapsed_seconds
            )

            # Complete job
            JobService.complete_job(db, job_id)

        except Exception as exc:
            db.rollback()
            JobService.fail_job(db, job_id, error_message=str(exc))
        finally:
            db.close()
            # Mandatory Zero-Retention Cleanup: Safely purge raw uploaded files from storage
            if delete_temp_files and settings.ZERO_RETENTION_MODE:
                for file_info in uploaded_files:
                    path = file_info.get("storage_path")
                    if path and os.path.exists(path):
                        try:
                            os.remove(path)
                        except Exception:
                            pass
