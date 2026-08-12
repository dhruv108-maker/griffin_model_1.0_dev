from sqlalchemy.orm import Session
from datetime import datetime
import traceback

from backend.Database.models import Evaluation, BatchJob, GeneratedReport, Report, Curriculum, JobStatus
from backend.Services.griffin_services import GriffinService

class EvaluationService:

    @staticmethod
    def create_evaluation(db: Session, project_id: str, curriculum_id: str, name: str) -> Evaluation:
        eval_obj = Evaluation(
            project_id=project_id,
            curriculum_id=curriculum_id,
            name=name,
            status=JobStatus.PENDING
        )
        db.add(eval_obj)
        db.commit()
        db.refresh(eval_obj)
        return eval_obj

    @staticmethod
    def run_async_evaluation(evaluation_id: str, report_ids: list[str]):
        """Background worker that runs Griffin pipeline and updates status."""
        from backend.Database.database import SessionLocal
        db = SessionLocal()
        try:
            job = BatchJob(
                evaluation_id=evaluation_id,
                status=JobStatus.PROCESSING,
                progress_percentage=0.0,
                started_at=datetime.utcnow()
            )
            db.add(job)
            
            eval_obj = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
            if eval_obj:
                eval_obj.status = JobStatus.PROCESSING
            db.commit()

            total_reports = len(report_ids)
            
            curriculum = db.query(Curriculum).filter(Curriculum.id == eval_obj.curriculum_id).first() if eval_obj else None
            curriculum_file_path = curriculum.file_path if (curriculum and curriculum.file_path) else "/tmp/storage/curriculum.pdf"

            for idx, r_id in enumerate(report_ids):
                report = db.query(Report).filter(Report.id == r_id).first()
                report_file_path = report.file_path if (report and report.file_path) else "/tmp/storage/report.pdf"
                
                metadata = {
                    "title": report.title if report else "Report",
                    "student_name": report.student_name if report else "Student",
                    "total_pages": report.total_pages if report else 1
                }

                # Callback to save stage-by-stage progress logs
                def on_stage_update(stage_msg: str, stage_progress: float):
                    base_progress = (idx / max(total_reports, 1)) * 100.0
                    step_contribution = (stage_progress / 100.0) * (100.0 / max(total_reports, 1))
                    overall_progress = min(round(base_progress + step_contribution, 2), 100.0)
                    
                    job.progress_percentage = overall_progress
                    
                    current_logs = list(job.logs or [])
                    timestamp = datetime.utcnow().strftime("%H:%M:%S")
                    current_logs.append(f"[{timestamp}] {stage_msg}")
                    job.logs = current_logs
                    db.commit()

                # Run Griffin Core
                result_json = GriffinService.process_report(
                    report_file_path=report_file_path,
                    curriculum_file_path=curriculum_file_path,
                    metadata=metadata,
                    on_stage_update=on_stage_update
                )

                # Persist griffin_result.json payload
                gen_report = GeneratedReport(
                    evaluation_id=evaluation_id,
                    report_id=r_id,
                    griffin_result=result_json
                )
                db.add(gen_report)

                # Progress update
                progress = round(((idx + 1) / max(total_reports, 1)) * 100.0, 2)
                job.progress_percentage = progress
                db.commit()

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            if eval_obj:
                eval_obj.status = JobStatus.COMPLETED
            db.commit()

        except Exception as e:
            db.rollback()
            try:
                job.status = JobStatus.FAILED
                job.error_message = str(e) + "\n" + traceback.format_exc()
                if eval_obj:
                    eval_obj.status = JobStatus.FAILED
                db.commit()
            except Exception:
                pass
        finally:
            db.close()