from __future__ import annotations
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from backend.Schemas.schemas import EvidenceGraph


@dataclass
class GraphMetricsResult:
    curriculum_coverage: float = 0.0
    evidence_density: float = 0.0
    duplicate_edge_rate: float = 0.0
    hallucination_rate: float = 0.0
    average_confidence: float = 0.0


def calculate_graph_metrics(
    graph: EvidenceGraph,
    all_topic_ids: List[int],
    ground_truth_map: Dict[int, Set[str]]
) -> GraphMetricsResult:
    """
    Calculates structural and topological validity metrics directly from EvidenceGraph.
    """
    if not all_topic_ids:
        return GraphMetricsResult()

    # Find topic -> evidence -> paragraph mappings in graph
    topic_evidence_edges = [edge for edge in graph.edges if edge.relation == "HAS_EVIDENCE"]
    evidence_para_edges = [edge for edge in graph.edges if edge.relation == "EXTRACTED_FROM"]

    evidence_to_para: Dict[str, str] = {e.source: e.target for e in evidence_para_edges}

    mapped_topics: Set[int] = set()
    total_evidence_nodes = 0
    unique_pairs: Set[Tuple[int, str]] = set()
    total_accepted_edges = 0
    confidence_scores: List[float] = []
    hallucinations = 0

    for edge in topic_evidence_edges:
        # Edge source is "topic_{id}"
        try:
            topic_id = int(edge.source.replace("topic_", ""))
        except ValueError:
            continue

        evidence_node_id = edge.target
        para_id = evidence_to_para.get(evidence_node_id)

        mapped_topics.add(topic_id)
        total_evidence_nodes += 1
        total_accepted_edges += 1
        confidence_scores.append(edge.confidence)

        if para_id:
            pair = (topic_id, para_id)
            unique_pairs.add(pair)
            
            # Check if this accepted mapping is absent from Ground Truth
            gt_paras = ground_truth_map.get(topic_id, set())
            if para_id not in gt_paras:
                hallucinations += 1

    curriculum_coverage = len(mapped_topics) / len(all_topic_ids)
    evidence_density = total_evidence_nodes / len(mapped_topics) if mapped_topics else 0.0
    
    duplicates = total_accepted_edges - len(unique_pairs)
    duplicate_edge_rate = duplicates / total_accepted_edges if total_accepted_edges > 0 else 0.0
    
    hallucination_rate = hallucinations / total_accepted_edges if total_accepted_edges > 0 else 0.0
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

    return GraphMetricsResult(
        curriculum_coverage=curriculum_coverage,
        evidence_density=evidence_density,
        duplicate_edge_rate=duplicate_edge_rate,
        hallucination_rate=hallucination_rate,
        average_confidence=avg_confidence
    )