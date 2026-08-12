from __future__ import annotations
import math
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ValidatorMetricsResult:
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    roc_auc: Optional[float] = None


def calculate_validator_metrics(
    y_true: List[int],
    y_pred: List[int],
    y_prob: Optional[List[float]] = None
) -> ValidatorMetricsResult:
    """
    Computes classification performance metrics for the EvidenceValidator cross-encoder.
    """
    if not y_true or len(y_true) != len(y_pred):
        return ValidatorMetricsResult()

    total = len(y_true)
    tp = sum(1 for gt, pred in zip(y_true, y_pred) if gt == 1 and pred == 1)
    tn = sum(1 for gt, pred in zip(y_true, y_pred) if gt == 0 and pred == 0)
    fp = sum(1 for gt, pred in zip(y_true, y_pred) if gt == 0 and pred == 1)
    fn = sum(1 for gt, pred in zip(y_true, y_pred) if gt == 1 and pred == 0)

    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    auc = None
    if y_prob is not None and len(y_prob) == total and len(set(y_true)) > 1:
        auc = _compute_roc_auc(y_true, y_prob)

    return ValidatorMetricsResult(
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1,
        roc_auc=auc
    )


def _compute_roc_auc(y_true: List[int], y_prob: List[float]) -> float:
    """Computes Area Under ROC Curve via Mann-Whitney U test formula."""
    pos_indices = [i for i, label in enumerate(y_true) if label == 1]
    neg_indices = [i for i, label in enumerate(y_true) if label == 0]

    n_pos = len(pos_indices)
    n_neg = len(neg_indices)

    if n_pos == 0 or n_neg == 0:
        return 0.0

    # Calculate rank sums
    combined = sorted(enumerate(y_prob), key=lambda x: x[1])
    ranks = [0.0] * len(y_prob)
    
    # Handle tied ranks mathematically
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][1] == combined[i][1]:
            j += 1
        rank_val = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[combined[k][0]] = rank_val
        i = j

    pos_rank_sum = sum(ranks[idx] for idx in pos_indices)
    u_stat = pos_rank_sum - (n_pos * (n_pos + 1)) / 2.0
    return float(u_stat / (n_pos * n_neg))