import re
from copy import deepcopy
from typing import Any, Dict, List


_HEADER_RE = re.compile(
    r"(?:School of Science.*?B\.Sc\.\s*Data Science,?\s*Course Curriculum.*?Course Content\s*\(Theory\))",
    re.IGNORECASE,
)
_BOUNDARY_RE = re.compile(
    r"\b(?:Instructional Method and Pedagogy|Course Outcome|Course Outcomes|List of Practical|List Of Practical|List Of Tutorial)\b.*$",
    re.IGNORECASE,
)
_WEIGHTAGE_RE = re.compile(
    r"(?:\b\d+\s*%\s*\d*\b|\b\d+\s*%\b|\b%\s*\d+)\s*$",
    re.IGNORECASE,
)
_MARKER_RE = re.compile(r"\b(?:Weightage|Contact hours)\b.*$", re.IGNORECASE)
_MULTI_SPACE_RE = re.compile(r"\s+")


def _clean_topic(text: str) -> str:
    text = _HEADER_RE.sub(" ", text)
    text = _BOUNDARY_RE.sub("", text)
    text = _MARKER_RE.sub("", text)
    text = _WEIGHTAGE_RE.sub("", text)
    text = re.sub(r"\b(?:\d+\s*%|%\s*\d+)\b", "", text)
    text = re.sub(r"\s+\d+(?:\.\d+)?\s*$", "", text)
    text = _MULTI_SPACE_RE.sub(" ", text).strip(" ,;:-")
    return text


def _split_topic_text(text: str) -> List[str]:
    cleaned = _clean_topic(text)
    if not cleaned:
        return []

    # PDF table extraction frequently collapses many syllabus concepts into one
    # line. Comma-separated items are safe atomic boundaries for this corpus.
    # Semicolon/hyphen phrases remain intact because they often represent one concept.
    parts = [part.strip(" ,;:-") for part in re.split(r"\s*,\s*", cleaned)]
    parts = [part for part in parts if len(part) >= 3]
    return parts or [cleaned]


def normalize_curriculum_tree(tree: Dict[str, Any]) -> Dict[str, Any]:
    """Convert parser output into clean unit/topic structure for semantic mapping."""
    normalized = deepcopy(tree)
    next_id = 0

    def walk(node: Dict[str, Any]) -> None:
        nonlocal next_id
        node["id"] = next_id
        next_id += 1

        children = node.get("children") or []
        node_type = str(node.get("type", "")).upper()
        rebuilt: List[Dict[str, Any]] = []

        for child in children:
            child_type = str(child.get("type", "")).upper()

            if node_type == "UNIT" and child_type == "TOPIC":
                pieces = _split_topic_text(str(child.get("text", "")))
                for piece in pieces:
                    item = dict(child)
                    item["text"] = piece
                    item["children"] = []
                    item["attributes"] = dict(child.get("attributes") or {})
                    rebuilt.append(item)
                continue

            walk(child)
            rebuilt.append(child)

        node["children"] = rebuilt

    for root in normalized.get("roots", []):
        walk(root)

    return normalized
