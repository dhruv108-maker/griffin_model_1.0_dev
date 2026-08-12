from __future__ import annotations
import math
from typing import List, Dict, Set, Any
from dataclasses import dataclass, field


@dataclass
class RetrievalMetricsResult:
    precision_at_k: Dict[int, float] = field(default_factory=dict)
    recall_at_k: Dict[int, float] = field(default_factory=dict)
    mrr: float = 0.0
    ndcg_at_k: Dict[int, float] = field(default_factory=dict)


def precision_at_k(retrieved: List[str], ground_truth: Set[str], k: int) -> float:
    """Calculates Precision@K: Ratio of relevant retrieved items in top-K."""
    if k <= 0:
        return 0.0
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    relevant_retrieved = sum(1 for item in top_k if item in ground_truth)
    return relevant_retrieved / k


def recall_at_k(retrieved: List[str], ground_truth: Set[str], k: int) -> float:
    """Calculates Recall@K: Ratio of relevant items found in top-K out of all ground truth."""
    if not ground_truth or k <= 0:
        return 0.0
    top_k = retrieved[:k]
    relevant_retrieved = sum(1 for item in top_k if item in ground_truth)
    return relevant_retrieved / len(ground_truth)


def mean_reciprocal_rank(all_retrieved: List[List[str]], all_ground_truth: List[Set[str]]) -> float:
    """Calculates Mean Reciprocal Rank (MRR) across all queries."""
    if not all_retrieved or len(all_retrieved) != len(all_ground_truth):
        return 0.0

    reciprocal_ranks = []
    for retrieved, gt in zip(all_retrieved, all_ground_truth):
        rank_found = 0.0
        for idx, item in enumerate(retrieved, start=1):
            if item in gt:
                rank_found = 1.0 / idx
                break
        reciprocal_ranks.append(rank_found)

    return sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0


def ndcg_at_k(retrieved: List[str], ground_truth: Set[str], k: int) -> float:
    """Calculates Normalized Discounted Cumulative Gain (nDCG@K) for binary relevance."""
    if not ground_truth or k <= 0:
        return 0.0

    top_k = retrieved[:k]
    dcg = 0.0
    for idx, item in enumerate(top_k, start=1):
        rel = 1.0 if item in ground_truth else 0.0
        dcg += rel / math.log2(idx + 1)

    # Ideal DCG: perfect ordering of relevant items up to min(k, |GT|)
    idcg = 0.0
    ideal_hits = min(k, len(ground_truth))
    for idx in range(1, ideal_hits + 1):
        idcg += 1.0 / math.log2(idx + 1)

    if idcg == 0.0:
        return 0.0

    return dcg / idcg


def calculate_retrieval_metrics(
    retrieved_map: Dict[int, List[str]],
    ground_truth_map: Dict[int, Set[str]],
    k_list: List[int] = [1, 3, 5]
) -> RetrievalMetricsResult:
    """
    Computes aggregated Precision@K, Recall@K, MRR, and nDCG@K over all topics.
    """
    all_retrieved = []
    all_gt = []

    p_at_k_accum: Dict[int, List[float]] = {k: [] for k in k_list}
    r_at_k_accum: Dict[int, List[float]] = {k: [] for k in k_list}
    ndcg_at_k_accum: Dict[int, List[float]] = {k: [] for k in k_list}

    for topic_id, retrieved_list in retrieved_map.items():
        gt_set = ground_truth_map.get(topic_id, set())
        all_retrieved.append(retrieved_list)
        all_gt.append(gt_set)

        for k in k_list:
            p_at_k_accum[k].append(precision_at_k(retrieved_list, gt_set, k))
            r_at_k_accum[k].append(recall_at_k(retrieved_list, gt_set, k))
            ndcg_at_k_accum[k].append(ndcg_at_k(retrieved_list, gt_set, k))

    mrr_score = mean_reciprocal_rank(all_retrieved, all_gt)

    mean_p = {k: float(sum(vals) / len(vals)) if vals else 0.0 for k, vals in p_at_k_accum.items()}
    mean_r = {k: float(sum(vals) / len(vals)) if vals else 0.0 for k, vals in r_at_k_accum.items()}
    mean_ndcg = {k: float(sum(vals) / len(vals)) if vals else 0.0 for k, vals in ndcg_at_k_accum.items()}

    return RetrievalMetricsResult(
        precision_at_k=mean_p,
        recall_at_k=mean_r,
        mrr=mrr_score,
        ndcg_at_k=mean_ndcg
    )