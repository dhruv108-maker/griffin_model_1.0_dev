from __future__ import annotations
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from backend.EvidenceModel.evaluation.retrieval_metrics import RetrievalMetricsResult
from backend.EvidenceModel.evaluation.validator_metrics import ValidatorMetricsResult
from backend.EvidenceModel.evaluation.graph_metrics import GraphMetricsResult
from backend.EvidenceModel.evaluation.runtime_metrics import RuntimeMetricsResult


@dataclass
class EvaluationReportData:
    experiment_name: str
    retrieval: RetrievalMetricsResult
    validator: ValidatorMetricsResult
    graph: GraphMetricsResult
    runtime: RuntimeMetricsResult


class EvaluationReportGenerator:
    """Generates structured evaluation reports and formatted CLI outputs."""

    def __init__(self, data: EvaluationReportData):
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self.data)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def render_console_report(self) -> str:
        d = self.data
        line = "=" * 70
        subline = "-" * 70

        ret_p = ", ".join([f"P@{k}: {v:.4f}" for k, v in d.retrieval.precision_at_k.items()])
        ret_r = ", ".join([f"R@{k}: {v:.4f}" for k, v in d.retrieval.recall_at_k.items()])
        ret_ndcg = ", ".join([f"nDCG@{k}: {v:.4f}" for k, v in d.retrieval.ndcg_at_k.items()])

        auc_str = f"{d.validator.roc_auc:.4f}" if d.validator.roc_auc is not None else "N/A"
        gpu_str = f"{d.runtime.gpu_memory_mb:.2f} MB" if d.runtime.gpu_memory_mb is not None else "N/A"

        stages_str = "\n".join([f"    - {k}: {v:.4f}s" for k, v in d.runtime.stage_runtimes.items()])

        report = f"""
{line}
GRIFFIN CORE RESEARCH EVALUATION REPORT
Experiment: {d.experiment_name}
{line}

1. RETRIEVAL METRICS
{subline}
  * Precision : {ret_p}
  * Recall    : {ret_r}
  * nDCG      : {ret_ndcg}
  * MRR       : {d.retrieval.mrr:.4f}

2. VALIDATOR METRICS (Cross-Encoder Entailment)
{subline}
  * Accuracy  : {d.validator.accuracy:.4f}
  * Precision : {d.validator.precision:.4f}
  * Recall    : {d.validator.recall:.4f}
  * F1-Score  : {d.validator.f1_score:.4f}
  * ROC AUC   : {auc_str}

3. GRAPH & TOPOLOGY METRICS
{subline}
  * Curriculum Coverage  : {d.graph.curriculum_coverage * 100:.2f}%
  * Evidence Density     : {d.graph.evidence_density:.2f} nodes/topic
  * Duplicate Edge Rate  : {d.graph.duplicate_edge_rate * 100:.2f}%
  * Hallucination Rate   : {d.graph.hallucination_rate * 100:.2f}%
  * Average Confidence   : {d.graph.average_confidence:.4f}

4. RUNTIME & SYSTEM PERFORMANCE
{subline}
  * Total Runtime  : {d.runtime.total_runtime_seconds:.4f} seconds
  * Peak CPU RAM   : {d.runtime.peak_memory_mb:.2f} MB
  * GPU VRAM       : {gpu_str}
  * Stage Breakdown:
{stages_str}

{line}
OVERALL SUMMARY: Coverage={d.graph.curriculum_coverage*100:.1f}% | Precision@1={d.retrieval.precision_at_k.get(1, 0.0):.4f} | F1={d.validator.f1_score:.4f}
{line}
"""
        return report