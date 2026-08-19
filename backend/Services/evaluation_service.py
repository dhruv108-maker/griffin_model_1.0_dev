import os
import queue
import traceback
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime

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
from backend.Services.evaluation_events import EvaluationEventBus
from backend.Services.griffin_services import GriffinService


class EvaluationService:
    """Coordinates product evaluation jobs; GriffinCore remains the source of truth."""

    @staticmethod
    def create_evaluation(db: Session, project_id: str, curriculum_id: str, name: str) -> Evaluation:
        curriculum = (
            db.query(Curriculum)
            .filter(Curriculum.id == curriculum_id, Curriculum.project_id == project_id)
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
    def _worker_count(report_count: int) -> int:
        configured = os.getenv("GRIFFIN_MAX_CONCURRENT_REPORTS", "2")
        try:
            configured_count = int(configured)
        except ValueError:
            configured_count = 2
        return max(1, min(configured_count, report_count))

    @staticmethod
    def _publish(
        evaluation_id: str,
        status: str,
        progress: float,
        logs: list[str],
        error: str | None = None,
        report_id: str | None = None,
        stage: str | None = None,
    ) -> None:
        EvaluationEventBus.publish(
            evaluation_id,
            {
                "type": "status",
                "evaluation_id": evaluation_id,
                "status": status,
                "progress": round(progress, 2),
                "logs": logs[-100:],
                "error": error,
                "report_id": report_id,
                "stage": stage,
            },
        )

    @staticmethod
    def _evaluate_report(
        report_id: str,
        title: str,
        student_name: str | None,
        total_pages: int,
        report_file_path: str,
        curriculum_file_path: str,
        curriculum_schema: dict | None,
        events: queue.Queue,
    ):
        metadata = {
            "title": title,
            "student_name": student_name,
            "student": student_name,
            "total_pages": total_pages,
        }

        def on_stage_update(stage_msg: str, stage_progress: float) -> None:
            events.put((report_id, stage_msg, float(stage_progress)))

        result = GriffinService.process_report(
            report_file_path=report_file_path,
            curriculum_file_path=curriculum_file_path,
            curriculum_schema=curriculum_schema,
            metadata=metadata,
            on_stage_update=on_stage_update,
        )
        return report_id, result

    @staticmethod
    def _drain_progress_events(
        events: queue.Queue,
        progress_by_report: dict[str, float],
        logs: list[str],
    ) -> bool:
        changed = False
        while True:
            try:
                report_id, stage_msg, stage_progress = events.get_nowait()
            except queue.Empty:
                break

            progress_by_report[report_id] = max(0.0, min(100.0, stage_progress))
            logs.append(stage_msg)
            changed = True
        return changed

    @staticmethod
    def run_async_evaluation(evaluation_id: str, report_ids: list[str]) -> None:
        """Evaluate independent reports concurrently and publish live progress."""
        db = SessionLocal()
        job = None
        evaluation = None

        try:
            evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
            if evaluation is None:
                raise ValueError(f"Evaluation {evaluation_id} not found")
            if not report_ids:
                raise ValueError("At least one report is required")

            curriculum = db.query(Curriculum).filter(Curriculum.id == evaluation.curriculum_id).first()
            if curriculum is None or not curriculum.file_path:
                raise ValueError("Evaluation curriculum file is missing")
            if not os.path.isfile(curriculum.file_path):
                raise ValueError("Evaluation curriculum file does not exist")
            if not curriculum.parsed_schema or not curriculum.parsed_schema.get("roots"):
                raise ValueError("Evaluation curriculum parsed_schema is missing; re-upload the curriculum")

            reports = (
                db.query(Report)
                .filter(Report.id.in_(report_ids), Report.project_id == evaluation.project_id)
                .all()
            )
            reports_by_id = {report.id: report for report in reports}
            missing_ids = [report_id for report_id in report_ids if report_id not in reports_by_id]
            if missing_ids:
                raise ValueError(f"Reports not found in project: {', '.join(missing_ids)}")

            reports = [reports_by_id[report_id] for report_id in report_ids]
            for report in reports:
                if not report.file_path or not os.path.isfile(report.file_path):
                    raise ValueError(f"Report file is missing: {report.title}")

            existing_rows = (
                db.query(GeneratedReport)
                .filter(
                    GeneratedReport.evaluation_id == evaluation_id,
                    GeneratedReport.report_id.in_(report_ids),
                )
                .all()
            )
            existing_by_report_id = {row.report_id: row for row in existing_rows}

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
            max_workers = EvaluationService._worker_count(total_reports)
            logs = [
                f"Starting {total_reports} report(s) with {max_workers} parallel Griffin worker(s)."
            ]
            job.logs = logs
            db.commit()
            EvaluationService._publish(evaluation_id, "PROCESSING", 0.0, logs)

            events: queue.Queue = queue.Queue()
            progress_by_report = {report.id: 0.0 for report in reports}

            worker_args = [
                (
                    report.id,
                    report.title,
                    report.student_name,
                    report.total_pages,
                    report.file_path,
                    curriculum.file_path,
                    curriculum.parsed_schema,
                    events,
                )
                for report in reports
            ]

            with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="griffin-eval") as executor:
                pending = {
                    executor.submit(EvaluationService._evaluate_report, *args): args[0]
                    for args in worker_args
                }

                while pending:
                    db.refresh(evaluation)
                    db.refresh(job)

                    if evaluation.status == JobStatus.CANCELLED or job.status == JobStatus.CANCELLED:
                        for future in pending:
                            future.cancel()
                        EvaluationService._publish(
                            evaluation_id,
                            "CANCELLED",
                            job.progress_percentage,
                            logs,
                        )
                        return

                    EvaluationService._drain_progress_events(events, progress_by_report, logs)
                    completed, _ = wait(pending, timeout=0.25, return_when=FIRST_COMPLETED)

                    for future in completed:
                        report_id = pending.pop(future)
                        result_report_id, result_json = future.result()
                        if result_report_id != report_id:
                            raise RuntimeError("Griffin worker returned mismatched report id")

                        existing = existing_by_report_id.get(report_id)
                        if existing:
                            existing.griffin_result = result_json
                        else:
                            existing = GeneratedReport(
                                evaluation_id=evaluation_id,
                                report_id=report_id,
                                griffin_result=result_json,
                            )
                            db.add(existing)
                            existing_by_report_id[report_id] = existing

                        progress_by_report[report_id] = 100.0
                        logs.append(f"Report {report_id} evaluation completed.")

                    if completed or not events.empty():
                        EvaluationService._drain_progress_events(events, progress_by_report, logs)
                        job.progress_percentage = round(
                            min(100.0, sum(progress_by_report.values()) / total_reports),
                            2,
                        )
                        job.logs = logs[-500:]
                        db.commit()

                        active_report = next(
                            (report_id for report_id, progress in progress_by_report.items() if progress < 100.0),
                            None,
                        )
                        latest_stage = logs[-1] if logs else None
                        EvaluationService._publish(
                            evaluation_id,
                            "PROCESSING",
                            job.progress_percentage,
                            logs,
                            report_id=active_report,
                            stage=latest_stage,
                        )

            job.status = JobStatus.COMPLETED
            job.progress_percentage = 100.0
            job.completed_at = datetime.utcnow()
            evaluation.status = JobStatus.COMPLETED
            job.logs = logs[-500:]
            db.commit()
            EvaluationService._publish(evaluation_id, "COMPLETED", 100.0, logs)

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
                EvaluationService._publish(
                    evaluation_id,
                    "CANCELLED",
                    job.progress_percentage if job else 0.0,
                    job.logs if job else [],
                )
            else:
                if job is not None:
                    job.status = JobStatus.FAILED
                    job.error_message = f"{exc}\n{traceback.format_exc()}"
                    job.completed_at = datetime.utcnow()
                if evaluation is not None:
                    evaluation.status = JobStatus.FAILED
                db.commit()
                EvaluationService._publish(
                    evaluation_id,
                    "FAILED",
                    job.progress_percentage if job else 0.0,
                    job.logs if job else [],
                    error=str(exc),
                )
            db.commit()
        finally:
            db.close()
