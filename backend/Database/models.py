from datetime import datetime
import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.Database.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), nullable=True, index=True)

    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    workspace = relationship("Workspace", back_populates="projects")
    curriculums = relationship("Curriculum", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="project", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="project", cascade="all, delete-orphan")


class Curriculum(Base, TimestampMixin):
    __tablename__ = "curriculums"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    parsed_schema = Column(JSON, nullable=True)

    project = relationship("Project", back_populates="curriculums")
    evaluations = relationship("Evaluation", back_populates="curriculum")


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    student_name = Column(String(255), nullable=True)
    file_path = Column(String(512), nullable=False)
    total_pages = Column(Integer, default=0, nullable=False)

    project = relationship("Project", back_populates="reports")
    generated_reports = relationship("GeneratedReport", back_populates="report", cascade="all, delete-orphan")


class Evaluation(Base, TimestampMixin):
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    curriculum_id = Column(String(36), ForeignKey("curriculums.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)

    project = relationship("Project", back_populates="evaluations")
    curriculum = relationship("Curriculum", back_populates="evaluations")
    batch_jobs = relationship("BatchJob", back_populates="evaluation", cascade="all, delete-orphan")
    generated_reports = relationship("GeneratedReport", back_populates="evaluation", cascade="all, delete-orphan")


class BatchJob(Base, TimestampMixin):
    __tablename__ = "batch_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    error_message = Column(Text, nullable=True)
    logs = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    evaluation = relationship("Evaluation", back_populates="batch_jobs")


class GeneratedReport(Base, TimestampMixin):
    __tablename__ = "generated_reports"
    __table_args__ = (
        UniqueConstraint("evaluation_id", "report_id", name="uq_evaluation_report_result"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=False)
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False)
    griffin_result = Column(JSON, nullable=False)

    evaluation = relationship("Evaluation", back_populates="generated_reports")
    report = relationship("Report", back_populates="generated_reports")


class Chat(Base, TimestampMixin):
    __tablename__ = "chats"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=True)
    title = Column(String(255), nullable=False)

    project = relationship("Project", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chat_id = Column(String(36), ForeignKey("chats.id"), nullable=False)
    sender = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)

    chat = relationship("Chat", back_populates="messages")
