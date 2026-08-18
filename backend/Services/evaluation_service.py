from datetime import datetime
import traceback

from sqlalchemy.orm import Session

from backend.Database.models import (
    BatchJob,
    Curriculum,
    Evaluation,
    GeneratedReport,
    JobStatus,
    Report,
)
from backend.Services.griffin_services import GriffinService


class EvaluationService:

    @staticmethod
    def create_evaluation(
        db: Session,
        project_id: str,
        curriculum_id: str,
        name: str,
        report_ids: list[str],
    ) -> Evaluation:
        if not report_ids:
            raise ValueError("At least one report is required for evaluation")

        curriculum = (
            db.query(Curriculum)
            .filter(
                Curriculum.id == curriculum_id,
                Curriculum.project_id == project_id,
            )
            .first()
        )
        if curriculum is None:
            raise ValueError("Curriculum does not belong to the selected project")
        if not curriculum.file_path:
            raise ValueError("Selected curriculum has no stored file")

        reports = (
            db.query(Report)
            .filter(
                Report.project_id == project_id,
                Report.id.in_(report_ids),
            )
            .all()
        )
        if len(reports) != len(set(report_ids)):
            raise ValueError("One or more selected reports do not belong to the project")
        if any(not report.file_path for report in reports):
            raise ValueError("One or more selected reports has no stored file")

        eval_obj = Evaluation(
            project_id=project_id,
            curriculum_id=curriculum_id,
            name=name,
            status=JobStatus.PENDING,
        )
        db.add(eval_obj)
        db.flush()

        # Create the job before returning the evaluation so the first
        # status request cannot race the background worker startup.
        job = BatchJob(
            evaluation_id=eval_obj.id,
            status=JobStatus.PENDING,
            progress_percentage=0.0,
            logs=[],
        )
        db.add(job)
        db.commit()
        db.refresh(eval_obj)
        return eval_obj

    @staticmethod
    def run_async_evaluation(evaluation_id: str, report_ids: list[str]):
        """Run the existing Griffin pipeline and persist one result per report."""
        from backend.Database.database import SessionLocal

        db = SessionLocal()
        job = None
        eval_obj = None
        try:
            eval_obj = (
                db.query(Evaluation)
                .filter(Evaluation.id == evaluation_id)
                .first()
            )
            if eval_obj is None:
                raise ValueError("Evaluation not found")

            job = (
                db.query(BatchJob)
                .filter(BatchJob.evaluation_id == evaluation_id)
                .order_by(BatchJob.created_at.desc())
                .first()
            )
            if job is None:
                raise ValueError("Evaluation job not found")

            curriculum = (
                db.query(Curriculum)
                .filter(Curriculum.id == eval_obj.curriculum_id)
                .first()
            )
            if curriculum is None or not curriculum.file_path:
                raise ValueError("Evaluation curriculum file is unavailable")

            reports = (
                db.query(Report)
                .filter(
                    Report.project_id == eval_obj.project_id,
                    Report.id.in_(report_ids),
                )
                .all()
            )
            report_by_id = {report.id: report for report in reports}
            missing_ids = [report_id for report_id in report_ids if report_id not in report_by_id]
            if missing_ids:
                raise ValueError(f"Evaluation reports not found: {', '.join(missing_ids)}")

            job.status = JobStatus.PROCESSING
            job.progress_percentage = 0.0
            job.started_at = datetime.utcnow()
            eval_obj.status = JobStatus.PROCESSING
            db.commit()

            total_reports = len(report_ids)
            for idx, report_id in enumerate(report_ids):
                report = report_by_id[report_id]
                if not report.file_path:
                    raise ValueError(f"Report {report_id} has no stored file")

                metadata = {
                    "title": report.title,
                    "student": report.student_name,
                    "student_name": report.student_name,
                    "total_pages": report.total_pages,
                }

                def on_stage_update(stage_msg: str, stage_progress: float):
                    base_progress = (idx / total_reports) * 100.0
                    step_contribution = (stage_progress / 100.0) * (100.0 / total_reports)
                    job.progress_percentage = min(
                        round(base_progress + step_contribution, 2),
                        100.0,
                    )
                    current_logs = list(job.logs or [])
                    timestamp = datetime.utcnow().strftime("%H:%M:%S")
                    current_logs.append(f"[{timestamp}] {stage_msg}")
                    job.logs = current_logs
                    db.commit()

                result_json = GriffinService.process_report(
                    report_file_path=report.file_path,
                    curriculum_file_path=curriculum.file_path,
                    metadata=metadata,
                    on_stage_update=on_stage_update,
                )

                gen_report = GeneratedReport(
                    evaluation_id=evaluation_id,
                    report_id=report_id,
                    griffin_result=result_json,
                )
                db.add(gen_report)
                job.progress_percentage = round(((idx + 1) / total_reports) * 100.0, 2)
                db.commit()

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.progress_percentage = 100.0
            eval_obj.status = JobStatus.COMPLETED
            db.commit()

        except Exception as exc:
            db.rollback()
            try:
                if job is None and evaluation_id:
                    job = (
                        db.query(BatchJob)
                        .filter(BatchJob.evaluation_id == evaluation_id)
                        .order_by(BatchJob.created_at.desc())
                        .first()
                    )
                if eval_obj is None and evaluation_id:
                    eval_obj = (
                        db.query(Evaluation)
                        .filter(Evaluation.id == evaluation_id)
                        .first()
                    )
                if job:
                    job.status = JobStatus.FAILED
                    job.error_message = f"{exc}\n{traceback.format_exc()}"
                if eval_obj:
                    eval_obj.status = JobStatus.FAILED
                db.commit()
            except Exception:
                pass
        finally:
            db.close()
