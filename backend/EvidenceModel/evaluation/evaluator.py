from __future__ import annotations
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
from backend.Schemas.schemas import EvidenceGraph

from backend.EvidenceModel.evaluation.retrieval_metrics import calculate_retrieval_metrics, RetrievalMetricsResult
from backend.EvidenceModel.evaluation.validator_metrics import calculate_validator_metrics, ValidatorMetricsResult
from backend.EvidenceModel.evaluation.graph_metrics import calculate_graph_metrics, GraphMetricsResult
from backend.EvidenceModel.evaluation.runtime_metrics import RuntimeMetricsResult
from backend.EvidenceModel.evaluation.report_generator import EvaluationReportGenerator, EvaluationReportData


@dataclass
class EvaluationResult:
    retrieval: RetrievalMetricsResult
    validator: ValidatorMetricsResult
    graph: GraphMetricsResult
    runtime: RuntimeMetricsResult
    report_data: EvaluationReportData


class Evaluator:
    """
    Central evaluator enforcing separation of concerns.
    Consumes EvidenceGraph and ground truth data to produce evaluation results.
    """

    def evaluate(
        self,
        experiment_name: str,
        graph: EvidenceGraph,
        all_topic_ids: List[int],
        retrieval_candidates: Dict[int, List[str]],
        retrieval_ground_truth: Dict[int, Set[str]],
        validator_ground_truth: Optional[Tuple[List[int], List[int], List[float]]] = None,
        runtime_result: Optional[RuntimeMetricsResult] = None
    ) -> EvaluationResult:
        """
        Coordinates all evaluation modules.

        :param experiment_name: Name of evaluation run.
        :param graph: Output EvidenceGraph from Griffin.
        :param all_topic_ids: Full list of topic IDs present in curriculum.
        :param retrieval_candidates: Map of topic_id -> list of retrieved paragraph_ids.
        :param retrieval_ground_truth: Map of topic_id -> set of true relevant paragraph_ids.
        :param validator_ground_truth: Optional Tuple (y_true, y_pred, y_prob) for validator set.
        :param runtime_result: Optional recorded runtime metrics.
        """
        # 1. Retrieval Metrics
        retrieval_res = calculate_retrieval_metrics(
            retrieved_map=retrieval_candidates,
            ground_truth_map=retrieval_ground_truth
        )

        # 2. Validator Metrics
        if validator_ground_truth:
            y_true, y_pred, y_prob = validator_ground_truth
            validator_res = calculate_validator_metrics(y_true, y_pred, y_prob)
        else:
            validator_res = ValidatorMetricsResult()

        # 3. Graph Metrics
        graph_res = calculate_graph_metrics(
            graph=graph,
            all_topic_ids=all_topic_ids,
            ground_truth_map=retrieval_ground_truth
        )

        # 4. Runtime Metrics
        rt_res = runtime_result if runtime_result is not None else RuntimeMetricsResult()

        # Build Report
        report_data = EvaluationReportData(
            experiment_name=experiment_name,
            retrieval=retrieval_res,
            validator=validator_res,
            graph=graph_res,
            runtime=rt_res
        )

        return EvaluationResult(
            retrieval=retrieval_res,
            validator=validator_res,
            graph=graph_res,
            runtime=rt_res,
            report_data=report_data
        )