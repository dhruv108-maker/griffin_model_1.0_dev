"""
Utility Functions for Griffin Report Tokenizer
=============================================
Information theory, regex patterns, text entropy calculations, and semantic signature helpers.
"""

from __future__ import annotations
import re
import math
import hashlib
from typing import List, Set, Tuple


TECHNICAL_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "up", "about", "into", "through", "after", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did", "this", "that",
    "these", "those", "it", "its", "we", "our", "they", "their", "report", "project",
    "page", "figure", "table", "above", "below", "shown", "given", "used", "using"
}

TECHNICAL_INDICATORS = {
    "algorithm", "architecture", "model", "equation", "function", "dataset", "matrix",
    "vector", "loss", "accuracy", "precision", "recall", "f1-score", "gradient",
    "optimizer", "layer", "transformer", "neural", "network", "tensor", "encoder",
    "decoder", "embedding", "pipeline", "classification", "regression", "clustering",
    "latency", "throughput", "complexity", "theorem", "lemma", "proof", "parameter"
}


def calculate_shannon_entropy(text: str) -> float:
    """Calculates byte-level Shannon Entropy to gauge information density."""
    if not text:
        return 0.0
    text_bytes = text.encode("utf-8")
    length = len(text_bytes)
    freq: dict[int, int] = {}
    for byte in text_bytes:
        freq[byte] = freq.get(byte, 0) + 1
    
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return float(entropy / 8.0)  # Normalized [0, 1]


def extract_formulas(text: str) -> List[str]:
    """Extracts mathematical formula references and equations."""
    patterns = [
        r"Eq\.\s*\d+[\.\d]*",
        r"Equation\s*\(\d+\)",
        r"\$\$.*?\$\$",
        r"\$.*?\$",
        r"[a-zA-Z_]\w*\s*=\s*[\d\w\+\-\*/\(\)\^]+"
    ]
    matches = []
    for p in patterns:
        found = re.findall(p, text, flags=re.IGNORECASE)
        matches.extend(found)
    return list(set(matches))


def extract_figure_and_table_refs(text: str) -> Tuple[List[str], List[str]]:
    """Extracts figure and table citations within the block text."""
    fig_pattern = r"(?:Fig\.|Figure)\s*\d+(?:\.\d+)*"
    tbl_pattern = r"(?:Table|Tbl)\s*\d+(?:\.\d+)*"
    
    figures = list(set(re.findall(fig_pattern, text, flags=re.IGNORECASE)))
    tables = list(set(re.findall(tbl_pattern, text, flags=re.IGNORECASE)))
    return figures, tables


def extract_academic_citations(text: str) -> List[str]:
    """Extracts academic bracketed or author-year citations."""
    patterns = [
        r"\[\d+(?:,\s*\d+)*\]",
        r"\([A-Z][a-z]+(?:\s+et\s+al\.)?,\s*\d{4}\)"
    ]
    citations = []
    for p in patterns:
        found = re.findall(p, text)
        citations.extend(found)
    return list(set(citations))


def compute_simhash_signature(text: str) -> str:
    """Generates a 64-bit SimHash fingerprint for semantic deduplication."""
    clean_text = re.sub(r"\W+", " ", text.lower()).strip()
    words = clean_text.split()
    if not words:
        return "0" * 16

    v = [0] * 64
    for word in words:
        word_hash = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
        for i in range(64):
            bit = (word_hash >> i) & 1
            v[i] += 1 if bit else -1

    fingerprint = 0
    for i in range(64):
        if v[i] >= 0:
            fingerprint |= (1 << i)
    return f"{fingerprint:016x}"