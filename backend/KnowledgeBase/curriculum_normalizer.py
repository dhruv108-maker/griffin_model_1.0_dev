import re
from copy import deepcopy
from typing import Any, Dict, List


_HEADER_RE = re.compile(
    r"(?:School of Science|Faculty of .*?|Department of .*?)\s+"
    r"B\.Sc\.\s+Data Science,?\s*Course Curriculum.*?Course Content\s*\(Theory\)",
    re.IGNORECASE,
)
_PRACTICAL_MARKER_RE = re.compile(r"\bList of Practical\b", re.IGNORECASE)
_WEIGHTAGE_RE = re.compile(r"(?:\b\d+\s*%\s*\d*\b|\b%\s*\d+\b|\bWeightage\b.*)$", re.IGNORECASE)
_MULTI_SPACE_RE = re.compile(r"\s+")
_PRACTICAL_TOPIC_RE = re.compile(r"^(demonstrat|create table|create database|create a database)", re.IGNORECASE)


def _clean_topic(text: str) -> str:
    text = _HEADER_RE.sub(" ", text)
    text = re.sub(r"\b(?:Weightage|Contact hours|List of Practical)\b.*$", "", text, flags=re.IGNORECASE)
    text = _WEIGHTAGE_RE.sub("", text)
    text = text.replace("%", " ")
    text = text.replace(" 7 2", " ").replace(" 7 3", " ").replace(" 10 5", " ")
    text = _MULTI_SPACE_RE.sub(" ", text).strip(" ,;:-")
    return text


def _split_topic_text(text: str) -> List[str]:
    cleaned = _clean_topic(text)
    if not cleaned:
        return []

    # PDF table extraction commonly collapses an entire syllabus row into one
    # comma-separated string. Treat each comma-delimited concept as an atomic
    # topic. This is deterministic and does not alter the underlying wording.
    parts = [part.strip(" ,;:-") for part in re.split(r"\s*,\s*", cleaned)]
    parts = [part for part in parts if len(part) >= 3]
    return parts or [cleaned]


def normalize_curriculum_tree(tree: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize parser output into atomic curriculum topics for semantic mapping."""
    normalized = deepcopy(tree)
    next_id = 0

    def walk(node: Dict[str, Any]) -> None:
        nonlocal next_id
        node["id"] = next_id
        next_id += 1

        children = node.get("children") or []
        if not children:
            return

        new_children: List[Dict[str, Any]] = []
        for child in children:
            child_type = str(child.get("type", "")).upper()

            if child_type == "TOPIC" and str(node.get("type", "")).upper() == "UNIT":
                pieces = _split_topic_text(child.get("text", ""))
                for piece in pieces:
                    item = dict(child)
                    item["text"] = piece
                    item["children"] = []
                    item["attributes"] = dict(child.get("attributes") or {})

                    if _PRACTICAL_MARKER_RE.search(piece) or _PRACTICAL_TOPIC_RE.match(piece):
                        item["type"] = "PRACTICAL"
                    new_children.append(item)
                continue

            # Flatten any accidental topic-list text under nested topic nodes.
            walk(child)
            new_children.append(child)

        node["children"] = new_children

    for root in normalized.get("roots", []):
        walk(root)

    return normalized
