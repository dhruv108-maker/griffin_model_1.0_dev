import gzip
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pypdf


_CACHE_DIR = Path("data") / "curriculum_cache"
_CACHE_VERSION = "v1"

# Hot-path regexes are compiled once instead of for every source line.
_RE_WS = re.compile(r"\s+")
_RE_LEADING_LAYOUT = re.compile(r"^[•\-\*\d\.\:\s]+")
_RE_PAGE_NOISE = re.compile(r"(?i)^(page\s*\d+(\s*of\s*\d+)?|\d+\s*/\s*\d+)$")
_RE_PAGE_HEADER = re.compile(r"(?i)^(curriculum|syllabus|department of|faculty of).*page")
_RE_DIVIDER = re.compile(r"^[\-\_\=\|\s]{3,}$")
_RE_COURSE_NAME = re.compile(r"(?i)COURSE NAME\s*[:\-]*\s*")
_RE_COURSE = re.compile(r"(?i)(?:COURSE NAME|DATABASE MANAGEMENT SYSTEM)")
_RE_COURSE_OBJECTIVES = re.compile(r"(?i)^Course Objectives")
_RE_UNIT = re.compile(r"(?i)^Unit\s+\d+")
_RE_CO_SECTION = re.compile(r"(?i)^Course Outcomes")
_RE_PO_SECTION = re.compile(r"(?i)^(Programme Outcomes|POs)")
_RE_PSO_SECTION = re.compile(r"(?i)^(Programme Specific Outcomes|PSOs)")
_RE_PRACTICAL_SECTION = re.compile(r"(?i)^(Practicals|Laboratory Work|Experiments|Lab Sessions)")
_RE_PEDAGOGY_SECTION = re.compile(r"(?i)^(Pedagogy|Teaching Methodology|Instructional Strategies)")
_RE_ASSESSMENT_SECTION = re.compile(r"(?i)^Evaluation Scheme")
_RE_RESOURCE_SECTION = re.compile(r"(?i)^(Learning Resources|Reference Books)")
_RE_NEW_ITEM = re.compile(r"^(\d+[\.\:]|CO\d+|PO\d+|PSO\d+|\u2022|\-)", re.IGNORECASE)
_RE_HOURS = re.compile(r"\(?\b(\d+)\s*(?:hours?|hrs?|L|Lectures?)\b\)?", re.IGNORECASE)
_RE_WEIGHTAGE = re.compile(r"\(?\b(?:weightage\s*[:\-]?\s*)?(\d+\s*%|\d+\s*marks?)\b\)?", re.IGNORECASE)
_RE_CO = re.compile(r"\b(CO\d+)\b", re.IGNORECASE)
_RE_CO_BLOCK = re.compile(r"\[?\b(?:CO\d+(?:\s*,\s*)?)+\b\]?", re.IGNORECASE)
_RE_EMPTY_PARENS = re.compile(r"\(\s*\)")
_RE_COURSE_CODE = re.compile(r"(?i)Course\s*Code\s*[:\-]\s*(.*)")
_RE_CREDITS = re.compile(r"(?i)Credits?\s*[:\-]\s*(\d+(\.\d+)?)")
_RE_PREREQ = re.compile(r"(?i)Prerequisite[s]?\s*[:\-]\s*(.*)")
_RE_TOTAL_HOURS = re.compile(r"(?i)Total\s*Hours\s*[:\-]\s*(\d+)")
_RE_MARKS = re.compile(r"(?i)Marks\s*[:\-]\s*(.*)")

_META_PATTERNS = (
    (_RE_COURSE_CODE, "course_code"),
    (_RE_CREDITS, "credits"),
    (_RE_PREREQ, "prerequisites"),
    (_RE_TOTAL_HOURS, "total_hours"),
    (_RE_MARKS, "marks_distribution"),
)

_CONTAINER_TYPES = {
    "OBJECTIVE", "UNIT", "CO", "PO", "PSO", "ASSESSMENT",
    "RESOURCE", "PRACTICAL", "PEDAGOGY", "METADATA",
}


def _cache_key(pdf_path: str) -> str:
    path = Path(pdf_path).resolve()
    stat = path.stat()
    # File identity + size + mtime protects cache correctness without hashing
    # the entire PDF on every evaluation.
    identity = f"{_CACHE_VERSION}|{path}|{stat.st_size}|{stat.st_mtime_ns}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _cache_path(pdf_path: str) -> Path:
    return _CACHE_DIR / f"{_cache_key(pdf_path)}.json.gz"


def _load_cached(pdf_path: str) -> Optional[Dict[str, Any]]:
    path = _cache_path(pdf_path)
    if not path.exists():
        return None
    try:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            payload = json.load(handle)
        if payload.get("cache_version") != _CACHE_VERSION:
            return None
        return payload["tree"]
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return None


def _save_cached(pdf_path: str, tree: Dict[str, Any]) -> None:
    path = _cache_path(pdf_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    payload = {"cache_version": _CACHE_VERSION, "tree": tree}
    try:
        with gzip.open(tmp, "wt", encoding="utf-8", compresslevel=6) as handle:
            json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
        tmp.replace(path)
    except OSError:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


class EvidenceTransformer:
    def __init__(self):
        self.counter = 0

    def transform(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        if not tree or "roots" not in tree:
            return tree

        roots = self._canonicalize_roots(tree["roots"])
        cleaned_roots = []
        for root in roots:
            cleaned = self._process_node(root)
            if cleaned:
                cleaned_roots.append(cleaned)

        self.counter = 0
        for root in cleaned_roots:
            self._reindex_node(root)

        return {"roots": cleaned_roots}

    def _canonicalize_roots(self, roots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not roots:
            return []
        primary = roots[0]
        primary.setdefault("metadata", {})
        for secondary in roots[1:]:
            primary["children"].extend(secondary.get("children", []))
            primary["metadata"].update(secondary.get("metadata", {}))
        return [primary]

    def _process_node(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        children = node.get("children")
        if not children:
            return node

        unique_children = []
        seen = set()
        for child in children:
            processed = self._process_node(child)
            if not processed:
                continue
            norm_text = _RE_WS.sub(" ", processed["text"].lower().strip())
            key = (processed["type"], norm_text)
            if key not in seen:
                seen.add(key)
                unique_children.append(processed)

        node["children"] = unique_children
        if node["type"] in _CONTAINER_TYPES and not unique_children:
            return None
        return node

    def _reindex_node(self, node: Dict[str, Any]) -> None:
        node["id"] = self.counter
        self.counter += 1
        for child in node.get("children", []):
            self._reindex_node(child)


class CurriculumEvidenceExtractor:
    """Lossless optimized replacement for the production curriculum parser."""

    def __init__(self):
        self.node_id = 0
        self.transformer = EvidenceTransformer()

    def _next_id(self) -> int:
        value = self.node_id
        self.node_id += 1
        return value

    def _create_node(
        self,
        node_type: str,
        text: str,
        page: int,
        confidence: float = 0.99,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        node = {
            "id": self._next_id(),
            "type": node_type,
            "text": self._clean_layout_artifacts(text),
            "page": page,
            "confidence": confidence,
            "attributes": attributes or {},
            "children": [],
        }
        if node_type == "COURSE":
            node["metadata"] = {}
        return node

    @staticmethod
    def _clean_layout_artifacts(text: str) -> str:
        text = _RE_LEADING_LAYOUT.sub("", text)
        text = text.replace("|", " ")
        text = _RE_WS.sub(" ", text).strip()
        return text

    @staticmethod
    def _is_noise(line: str) -> bool:
        return bool(
            _RE_PAGE_NOISE.match(line)
            or _RE_PAGE_HEADER.match(line)
            or _RE_DIVIDER.match(line)
        )

    def _parse_attributes_and_cos(
        self, raw_text: str
    ) -> Tuple[str, Dict[str, Any], List[str]]:
        attributes: Dict[str, Any] = {}
        text = raw_text

        hours_match = _RE_HOURS.search(text)
        if hours_match:
            attributes["hours"] = hours_match.group(0).strip("()")
            text = text.replace(hours_match.group(0), "", 1)

        weightage_match = _RE_WEIGHTAGE.search(text)
        if weightage_match:
            attributes["weightage"] = weightage_match.group(1)
            text = text.replace(weightage_match.group(0), "", 1)

        co_matches = _RE_CO.findall(text)
        embedded_cos: List[str] = []
        if co_matches:
            embedded_cos = list(dict.fromkeys(co.upper() for co in co_matches))
            text = _RE_CO_BLOCK.sub("", text)
            text = _RE_EMPTY_PARENS.sub("", text)

        return self._clean_layout_artifacts(text), attributes, embedded_cos

    def _extract_metadata(self, line: str, course_node: Dict[str, Any]) -> bool:
        for pattern, key in _META_PATTERNS:
            match = pattern.search(line)
            if match:
                course_node["metadata"][key] = match.group(1).strip()
                return True
        return False

    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        cached = _load_cached(pdf_path)
        if cached is not None:
            return cached

        self.node_id = 0
        reader = pypdf.PdfReader(pdf_path)
        roots: List[Dict[str, Any]] = []
        current_course = None
        current_section = None
        last_leaf_node = None

        # One sequential PDF pass; no lossy sampling or page skipping.
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            for raw_line in text.splitlines():
                line = raw_line.strip()
                if not line or self._is_noise(line):
                    continue

                if _RE_COURSE.search(line):
                    clean_title = _RE_COURSE_NAME.sub("", line)
                    if clean_title:
                        current_course = self._create_node("COURSE", clean_title, page_num)
                        roots.append(current_course)
                        current_section = None
                        last_leaf_node = None
                    continue

                if current_course is None:
                    continue

                if self._extract_metadata(line, current_course):
                    meta_section = next(
                        (child for child in current_course["children"] if child["type"] == "METADATA"),
                        None,
                    )
                    if meta_section is None:
                        meta_section = self._create_node("METADATA", "Course Metadata", page_num)
                        current_course["children"].append(meta_section)
                    meta_section["children"].append(
                        self._create_node("METADATA", line, page_num)
                    )
                    continue

                if _RE_COURSE_OBJECTIVES.match(line):
                    current_section = self._create_node("OBJECTIVE", "Course Objectives", page_num)
                elif _RE_UNIT.match(line):
                    clean_text, attrs, _ = self._parse_attributes_and_cos(line)
                    current_section = self._create_node("UNIT", clean_text, page_num, attributes=attrs)
                elif _RE_CO_SECTION.match(line):
                    current_section = self._create_node("CO", "Course Outcomes", page_num)
                elif _RE_PO_SECTION.match(line):
                    current_section = self._create_node("PO", "Programme Outcomes", page_num)
                elif _RE_PSO_SECTION.match(line):
                    current_section = self._create_node("PSO", "Programme Specific Outcomes", page_num)
                elif _RE_PRACTICAL_SECTION.match(line):
                    current_section = self._create_node("PRACTICAL", "Practicals", page_num)
                elif _RE_PEDAGOGY_SECTION.match(line):
                    current_section = self._create_node("PEDAGOGY", "Pedagogy & Teaching Methodology", page_num)
                elif _RE_ASSESSMENT_SECTION.match(line):
                    current_section = self._create_node("ASSESSMENT", "Evaluation Scheme", page_num)
                elif _RE_RESOURCE_SECTION.match(line):
                    current_section = self._create_node("RESOURCE", "Learning Resources", page_num)
                else:
                    current_section = None if current_section is None else current_section

                # Header branches create and append a section; no leaf processing on that line.
                if line is not raw_line and current_section is not None:
                    pass

                section_was_header = (
                    _RE_COURSE_OBJECTIVES.match(line)
                    or _RE_UNIT.match(line)
                    or _RE_CO_SECTION.match(line)
                    or _RE_PO_SECTION.match(line)
                    or _RE_PSO_SECTION.match(line)
                    or _RE_PRACTICAL_SECTION.match(line)
                    or _RE_PEDAGOGY_SECTION.match(line)
                    or _RE_ASSESSMENT_SECTION.match(line)
                    or _RE_RESOURCE_SECTION.match(line)
                )
                if section_was_header:
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                if current_section is None:
                    continue

                is_new_item = bool(_RE_NEW_ITEM.match(line))
                if not is_new_item and last_leaf_node is not None and not line.startswith("Unit"):
                    additional_text, add_attrs, add_cos = self._parse_attributes_and_cos(line)
                    if additional_text:
                        last_leaf_node["text"] += f" {additional_text}"
                    last_leaf_node["attributes"].update(add_attrs)
                    for co_code in add_cos:
                        last_leaf_node["children"].append(
                            self._create_node("CO", f"Mapped Outcome: {co_code}", page_num)
                        )
                    continue

                clean_line, line_attrs, embedded_cos = self._parse_attributes_and_cos(line)
                if not clean_line:
                    continue

                section_type = current_section["type"]
                if section_type == "UNIT":
                    node = self._create_node("TOPIC", clean_line, page_num, attributes=line_attrs)
                    for co_code in embedded_cos:
                        node["children"].append(
                            self._create_node("CO", f"Mapped Outcome: {co_code}", page_num)
                        )
                elif section_type == "PRACTICAL":
                    node = self._create_node("PRACTICAL", clean_line, page_num, attributes=line_attrs)
                elif section_type == "PEDAGOGY":
                    node = self._create_node("PEDAGOGY", clean_line, page_num, attributes=line_attrs)
                elif section_type in {"OBJECTIVE", "ASSESSMENT", "RESOURCE"}:
                    node = self._create_node(section_type, clean_line, page_num, attributes=line_attrs)
                elif section_type in {"CO", "PO", "PSO"}:
                    node = self._create_node(section_type, clean_line, page_num, attributes=line_attrs)
                else:
                    continue

                current_section["children"].append(node)
                last_leaf_node = node

        tree = self.transformer.transform({"roots": roots})
        _save_cached(pdf_path, tree)
        return tree
