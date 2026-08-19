from datetime import datetime
import traceback

from sqlalchemy.orm import Session

from backend.Database.database import SessionLocal
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
    """Coordinates product evaluation jobs; GriffinCore remains the source of truth."""

    @staticmethod
    def create_evaluation(
        db: Session,
        project_id: str,
        curriculum_id: str,
        name: str,
    ) -> Evaluation:
        curriculum = (
            db.query(Curriculum)
            .filter(
                Curriculum.id == curriculum_id,
                Curriculum.project_id == project_id,
            )
            .first()
        )
        if curriculum is None:
            raise ValueError("Curriculum does not belong to the requested project")

        evaluation = Evaluation(
            project_id=project_id,
            curriculum_id=curriculum_id,
            name=name.strip() or "Griffin Evaluation",
            status=JobStatus.PENDING,
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation

    @staticmethod
    def run_async_evaluation(evaluation_id: str, report_ids: list[str]) -> None:
        """Run real Griffin evaluation and persist each report's GriffinResult."""
        db = SessionLocal()
        job = None
        evaluation = None

        try:
            evaluation = (
                db.query(Evaluation)
                .filter(Evaluation.id == evaluation_id)
                .first()
            )
            if evaluation is None:
                raise ValueError(f"Evaluation {evaluation_id} not found")
            if not report_ids:
                raise ValueError("At least one report is required")

            curriculum = (
                db.query(Curriculum)
                .filter(Curriculum.id == evaluation.curriculum_id)
                .first()
            )
            if curriculum is None or not curriculum.file_path:
                raise ValueError("Evaluation curriculum file is missing")

            reports = (
                db.query(Report)
                .filter(
                    Report.id.in_(report_ids),
                    Report.project_id == evaluation.project_id,
                )
                .all()
            )
            reports_by_id = {report.id: report for report in reports}
            missing_ids = [report_id for report_id in report_ids if report_id not in reports_by_id]
            if missing_ids:
                raise ValueError(
                    f"Reports not found in project: {', '.join(missing_ids)}"
                )

            # Preserve the user's requested report order.
            reports = [reports_by_id[report_id] for report_id in report_ids]
            report_id_set = set(report_ids)

            existing_rows = (
                db.query(GeneratedReport)
                .filter(
                    GeneratedReport.evaluation_id == evaluation_id,
                    GeneratedReport.report_id.in_(report_id_set),
                )
                .all()
            )
            existing_by_report_id = {
                row.report_id: row for row in existing_rows
            }

            job = BatchJob(
                evaluation_id=evaluation_id,
                status=JobStatus.PROCESSING,
                progress_percentage=0.0,
                started_at=datetime.utcnow(),
                logs=[],
            )
            evaluation.status = JobStatus.PROCESSING
            db.add(job)
            db.commit()
            db.refresh(job)

            total_reports = len(reports)
            logs = []

            for idx, report in enumerate(reports):
                if evaluation.status == JobStatus.CANCELLED or job.status == JobStatus.CANCELLED:
                    return

                metadata = {
                    "title": report.title,
                    "student_name": report.student_name,
                    "student": report.student_name,
                    "total_pages": report.total_pages,
                }

                def on_stage_update(stage_msg: str, stage_progress: float) -> None:
                    if evaluation.status == JobStatus.CANCELLED or job.status == JobStatus.CANCELLED:
                        raise RuntimeError("Evaluation cancelled")

                    base_progress = (idx / total_reports) * 100.0
                    step_contribution = (
                        (stage_progress / 100.0) * (100.0 / total_reports)
                    )
                    job.progress_percentage = min(
                        round(base_progress + step_contribution, 2),
                        100.0,
                    )

                    logs.append(stage_msg)
                    job.logs = logs
                    db.commit()

                result_json = GriffinService.process_report(
                    report_file_path=report.file_path,
                    curriculum_file_path=curriculum.file_path,
                    metadata=metadata,
                    on_stage_update=on_stage_update,
                )

                existing = existing_by_report_id.get(report.id)
                if existing:
                    existing.griffin_result = result_json
                else:
                    existing = GeneratedReport(
                        evaluation_id=evaluation_id,
                        report_id=report.id,
                        griffin_result=result_json,
                    )
                    db.add(existing)
                    existing_by_report_id[report.id] = existing

                job.progress_percentage = round(
                    ((idx + 1) / total_reports) * 100.0,
                    2,
                )
                job.logs = logs
                db.commit()

            job.status = JobStatus.COMPLETED
            job.progress_percentage = 100.0
            job.completed_at = datetime.utcnow()
            evaluation.status = JobStatus.COMPLETED
            db.commit()

        except Exception as exc:
            db.rollback()

            if evaluation is not None:
                evaluation = db.merge(evaluation)
            if job is not None:
                job = db.merge(job)

            if evaluation is not None and evaluation.status == JobStatus.CANCELLED:
                if job is not None:
                    job.status = JobStatus.CANCELLED
                    job.completed_at = datetime.utcnow()
            else:
                if job is not None:
                    job.status = JobStatus.FAILED
                    job.error_message = f"{exc}\n{traceback.format_exc()}"
                if evaluation is not None:
                    evaluation.status = JobStatus.FAILED

            db.commit()
        finally:
            db.close()
