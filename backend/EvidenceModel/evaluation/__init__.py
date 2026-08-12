"""
Griffin Core Evaluation Module
==============================
Provides independent evaluation metrics, graph analysis, benchmark execution,
and experiment reporting for Griffin Core evidence discovery.
"""

from backend.EvidenceModel.evaluation.evaluator import Evaluator, EvaluationResult
from backend.EvidenceModel.evaluation.report_generator import EvaluationReportGenerator
from backend.EvidenceModel.evaluation.benchmark_runner import BenchmarkRunner

__all__ = [
    "Evaluator",
    "EvaluationResult",
    "EvaluationReportGenerator",
    "BenchmarkRunner",
]