import gzip
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import pypdf


_CACHE_DIR = Path("data") / "curriculum_cache"
_CACHE_VERSION = "v2"

# Compile hot-path regular expressions once. The parser can process hundreds of
# pages and thousands of lines, so recompiling these patterns per line is costly.
_RE_WS = re.compile(r"\s+")
_RE_LEADING_LAYOUT = re.compile(r"^[•\-\*\d\.\:\s]+")
_RE_PAGE_NOISE = re.compile(r"(?i)^(page\s*\d+(\s*of\s*\d+)?|\d+\s*/\s*\d+)$")
_RE_PAGE_HEADER = re.compile(r"(?i)^(curriculum|syllabus|department of|faculty of).*page")
_RE_DIVIDER = re.compile(r"^[\-\_\=\|\s]{3,}$")
_RE_COURSE_TRIGGER = re.compile(r"(?:COURSE NAME|DATABASE MANAGEMENT SYSTEM)", re.IGNORECASE)
_RE_COURSE_NAME = re.compile(r"COURSE NAME\s*[:\-]*\s*", re.IGNORECASE)
_RE_OBJECTIVES = re.compile(r"^Course Objectives", re.IGNORECASE)
_RE_UNIT = re.compile(r"^Unit\s+\d+", re.IGNORECASE)
_RE_CO_SECTION = re.compile(r"^Course Outcomes", re.IGNORECASE)
_RE_PO_SECTION = re.compile(r"^(Programme Outcomes|POs)", re.IGNORECASE)
_RE_PSO_SECTION = re.compile(r"^(Programme Specific Outcomes|PSOs)", re.IGNORECASE)
_RE_PRACTICAL_SECTION = re.compile(r"^(Practicals|Laboratory Work|Experiments|Lab Sessions)", re.IGNORECASE)
_RE_PEDAGOGY_SECTION = re.compile(r"^(Pedagogy|Teaching Methodology|Instructional Strategies)", re.IGNORECASE)
_RE_ASSESSMENT_SECTION = re.compile(r"^Evaluation Scheme", re.IGNORECASE)
_RE_RESOURCE_SECTION = re.compile(r"^(Learning Resources|Reference Books)", re.IGNORECASE)
_RE_NEW_ITEM = re.compile(r"^(\d+[\.\:]|CO\d+|PO\d+|PSO\d+|\u2022|\-)", re.IGNORECASE)
_RE_HOURS = re.compile(r"\(?\b(\d+)\s*(?:hours?|hrs?|L|Lectures?)\b\)?", re.IGNORECASE)
_RE_WEIGHTAGE = re.compile(r"\(?\b(?:weightage\s*[:\-]?\s*)?(\d+\s*%|\d+\s*marks?)\b\)?", re.IGNORECASE)
_RE_CO = re.compile(r"\b(CO\d+)\b", re.IGNORECASE)
_RE_CO_BLOCK = re.compile(r"\[?\b(?:CO\d+(?:\s*,\s*)?)+\b\]?", re.IGNORECASE)
_RE_EMPTY_PARENS = re.compile(r"\(\s*\)")
_RE_COURSE_CODE = re.compile(r"Course\s*Code\s*[:\-]\s*(.*)", re.IGNORECASE)
_RE_CREDITS = re.compile(r"Credits?\s*[:\-]\s*(\d+(\.\d+)?)", re.IGNORECASE)
_RE_PREREQUISITES = re.compile(r"Prerequisite[s]?\s*[:\-]\s*(.*)", re.IGNORECASE)
_RE_TOTAL_HOURS = re.compile(r"Total\s*Hours\s*[:\-]\s*(\d+)", re.IGNORECASE)
_RE_MARKS = re.compile(r"Marks\s*[:\-]\s*(.*)", re.IGNORECASE)

_META_PATTERNS = (
    (_RE_COURSE_CODE, "course_code"),
    (_RE_CREDITS, "credits"),
    (_RE_PREREQUISITES, "prerequisites"),
    (_RE_TOTAL_HOURS, "total_hours"),
    (_RE_MARKS, "marks_distribution"),
)

_CONTAINER_TYPES = {
    "OBJECTIVE",
    "UNIT",
    "CO",
    "PO",
    "PSO",
    "ASSESSMENT",
    "RESOURCE",
    "PRACTICAL",
    "PEDAGOGY",
    "METADATA",
}


def _cache_path(pdf_path: str) -> Path:
    path = Path(pdf_path).resolve()
    stat = path.stat()
    # Fingerprint uses immutable path + size + mtime. This avoids hashing a
    # potentially 200+ page PDF on every evaluation while invalidating on normal
    # file replacement/edit operations.
    fingerprint = f"{_CACHE_VERSION}|{path}|{stat.st_size}|{stat.st_mtime_ns}"
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
    return _CACHE_DIR / f"{digest}.json.gz"


def _load_cached(pdf_path: str) -> Optional[Dict[str, Any]]:
    cache_path = _cache_path(pdf_path)
    if not cache_path.exists():
        return None

    try:
        with gzip.open(cache_path, "rt", encoding="utf-8") as handle:
            payload = json.load(handle)
        if payload.get("cache_version") != _CACHE_VERSION:
            return None
        return payload.get("tree")
    except (OSError, EOFError, ValueError, KeyError, json.JSONDecodeError):
        # Corrupt/stale cache should never prevent a fresh parse.
        return None


def _save_cached(pdf_path: str, tree: Dict[str, Any]) -> None:
    cache_path = _cache_path(pdf_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = cache_path.with_suffix(cache_path.suffix + ".tmp")
    payload = {
        "cache_version": _CACHE_VERSION,
        "tree": tree,
    }

    try:
        with gzip.open(temp_path, "wt", encoding="utf-8", compresslevel=6) as handle:
            json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
        temp_path.replace(cache_path)
    except OSError:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


class EvidenceTransformer:
    """
    Post-processing transformer to clean hierarchy, prune empty structural containers,
    deduplicate nodes, merge duplicate course roots, and re-index contiguous IDs.
    """

    def __init__(self):
        self.counter = 0

    def transform(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """Executes full normalization and cleaning hierarchy pipeline."""
        if not tree or "roots" not in tree:
            return tree

        canonical_roots = self._canonicalize_roots(tree["roots"])

        cleaned_roots = []
        for root in canonical_roots:
            cleaned_root = self._process_node(root)
            if cleaned_root:
                cleaned_roots.append(cleaned_root)

        self.counter = 0
        for root in cleaned_roots:
            self._reindex_node(root)

        return {"roots": cleaned_roots}

    def _canonicalize_roots(self, roots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidates multiple detected COURSE roots into one canonical root."""
        if not roots:
            return []

        primary_root = roots[0]
        primary_root.setdefault("metadata", {})

        for secondary_root in roots[1:]:
            primary_root["children"].extend(secondary_root.get("children", []))
            primary_root["metadata"].update(secondary_root.get("metadata", {}))

        return [primary_root]

    def _process_node(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recursively cleans text, deduplicates children, and prunes empty containers."""
        children = node.get("children")
        if not children:
            return node

        seen_keys = set()
        unique_children = []

        for child in children:
            processed_child = self._process_node(child)
            if not processed_child:
                continue

            norm_text = _RE_WS.sub(" ", processed_child["text"].lower().strip())
            sig_key = (processed_child["type"], norm_text)

            if sig_key not in seen_keys:
                seen_keys.add(sig_key)
                unique_children.append(processed_child)

        node["children"] = unique_children

        if node["type"] in _CONTAINER_TYPES and not unique_children:
            return None

        return node

    def _reindex_node(self, node: Dict[str, Any]) -> None:
        """Assigns sequential, contiguous integer IDs across the tree structure."""
        node["id"] = self.counter
        self.counter += 1
        for child in node.get("children", []):
            self._reindex_node(child)


class CurriculumEvidenceExtractor:
    """
    Lossless optimized rule-based extractor & parser for curriculum documents.

    The semantic extraction rules remain unchanged. Performance improvements are
    limited to compiled hot-path regexes, reduced repeated list scans, state reset,
    and compressed on-disk caching of the final normalized tree.
    """

    def __init__(self):
        self.node_id = 0
        self.transformer = EvidenceTransformer()

    def _next_id(self) -> int:
        current_id = self.node_id
        self.node_id += 1
        return current_id

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
        """Strips bullet points, table lines, residual numbers, and dangling layout noise."""
        text = _RE_LEADING_LAYOUT.sub("", text)
        text = text.replace("|", " ")
        text = _RE_WS.sub(" ", text).strip()
        return text

    @staticmethod
    def _is_noise(line: str) -> bool:
        """Filters headers, footers, page numbering, and structural table margins."""
        return bool(
            _RE_PAGE_NOISE.match(line)
            or _RE_PAGE_HEADER.match(line)
            or _RE_DIVIDER.match(line)
        )

    def _parse_attributes_and_cos(
        self,
        raw_text: str,
    ) -> Tuple[str, Dict[str, Any], List[str]]:
        """
        Extracts weightage/contact hours into attributes and parses inline COs
        into standalone entities while cleaning the source text.
        """
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

        cleaned_text = self._clean_layout_artifacts(text)
        return cleaned_text, attributes, embedded_cos

    def _extract_metadata(self, line: str, course_node: Dict[str, Any]) -> bool:
        """Separates metadata from semantic evidence into dedicated fields/nodes."""
        for pattern, key in _META_PATTERNS:
            match = pattern.search(line)
            if match:
                course_node["metadata"][key] = match.group(1).strip()
                return True
        return False

    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Parse once, normalize once, and cache the exact final tree losslessly."""
        cached_tree = _load_cached(pdf_path)
        if cached_tree is not None:
            return cached_tree

        # Reset state so extractor reuse cannot carry IDs across documents.
        self.node_id = 0

        reader = pypdf.PdfReader(pdf_path)
        roots: List[Dict[str, Any]] = []
        current_course = None
        current_section = None
        last_leaf_node = None
        metadata_section = None

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            for raw_line in text.splitlines():
                line = raw_line.strip()
                if not line or self._is_noise(line):
                    continue

                if _RE_COURSE_TRIGGER.search(line):
                    clean_title = _RE_COURSE_NAME.sub("", line)
                    if clean_title:
                        current_course = self._create_node("COURSE", clean_title, page_num)
                        roots.append(current_course)
                        current_section = None
                        last_leaf_node = None
                        metadata_section = None
                    continue

                if current_course is None:
                    continue

                if self._extract_metadata(line, current_course):
                    if metadata_section is None:
                        metadata_section = self._create_node(
                            "METADATA",
                            "Course Metadata",
                            page_num,
                        )
                        current_course["children"].append(metadata_section)

                    metadata_section["children"].append(
                        self._create_node("METADATA", line, page_num)
                    )
                    continue

                section_type = None
                section_text = None

                if _RE_OBJECTIVES.match(line):
                    section_type, section_text = "OBJECTIVE", "Course Objectives"
                elif _RE_UNIT.match(line):
                    clean_text, attrs, _ = self._parse_attributes_and_cos(line)
                    current_section = self._create_node(
                        "UNIT",
                        clean_text,
                        page_num,
                        attributes=attrs,
                    )
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue
                elif _RE_CO_SECTION.match(line):
                    section_type, section_text = "CO", "Course Outcomes"
                elif _RE_PO_SECTION.match(line):
                    section_type, section_text = "PO", "Programme Outcomes"
                elif _RE_PSO_SECTION.match(line):
                    section_type, section_text = "PSO", "Programme Specific Outcomes"
                elif _RE_PRACTICAL_SECTION.match(line):
                    section_type, section_text = "PRACTICAL", "Practicals"
                elif _RE_PEDAGOGY_SECTION.match(line):
                    section_type, section_text = "PEDAGOGY", "Pedagogy & Teaching Methodology"
                elif _RE_ASSESSMENT_SECTION.match(line):
                    section_type, section_text = "ASSESSMENT", "Evaluation Scheme"
                elif _RE_RESOURCE_SECTION.match(line):
                    section_type, section_text = "RESOURCE", "Learning Resources"

                if section_type is not None:
                    current_section = self._create_node(
                        section_type,
                        section_text,
                        page_num,
                    )
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                if current_section is None:
                    continue

                is_new_item = bool(_RE_NEW_ITEM.match(line))

                # Merge wrapped sentences into the previous semantic node exactly
                # as before, while avoiding repeated regex compilation.
                if not is_new_item and last_leaf_node and not line.startswith("Unit"):
                    additional_text, add_attrs, add_cos = self._parse_attributes_and_cos(line)
                    if additional_text:
                        last_leaf_node["text"] += f" {additional_text}"
                    last_leaf_node["attributes"].update(add_attrs)

                    for co_code in add_cos:
                        last_leaf_node["children"].append(
                            self._create_node(
                                "CO",
                                f"Mapped Outcome: {co_code}",
                                page_num,
                            )
                        )
                    continue

                clean_line, line_attrs, embedded_cos = self._parse_attributes_and_cos(line)
                if not clean_line:
                    continue

                section_type = current_section["type"]

                if section_type == "UNIT":
                    topic_node = self._create_node(
                        "TOPIC",
                        clean_line,
                        page_num,
                        attributes=line_attrs,
                    )
                    for co_code in embedded_cos:
                        topic_node["children"].append(
                            self._create_node(
                                "CO",
                                f"Mapped Outcome: {co_code}",
                                page_num,
                            )
                        )
                    current_section["children"].append(topic_node)
                    last_leaf_node = topic_node

                elif section_type == "PRACTICAL":
                    practical_node = self._create_node(
                        "PRACTICAL",
                        clean_line,
                        page_num,
                        attributes=line_attrs,
                    )
                    current_section["children"].append(practical_node)
                    last_leaf_node = practical_node

                elif section_type == "PEDAGOGY":
                    pedagogy_node = self._create_node(
                        "PEDAGOGY",
                        clean_line,
                        page_num,
                        attributes=line_attrs,
                    )
                    current_section["children"].append(pedagogy_node)
                    last_leaf_node = pedagogy_node

                elif section_type in {"OBJECTIVE", "ASSESSMENT", "RESOURCE"}:
                    leaf_node = self._create_node(
                        section_type,
                        clean_line,
                        page_num,
                        attributes=line_attrs,
                    )
                    current_section["children"].append(leaf_node)
                    last_leaf_node = leaf_node

                elif section_type in {"CO", "PO", "PSO"}:
                    outcome_node = self._create_node(
                        section_type,
                        clean_line,
                        page_num,
                        attributes=line_attrs,
                    )
                    current_section["children"].append(outcome_node)
                    last_leaf_node = outcome_node

        raw_output = {"roots": roots}
        structured_output = self.transformer.transform(raw_output)
        _save_cached(pdf_path, structured_output)
        return structured_output


if __name__ == "__main__":
    extractor = CurriculumEvidenceExtractor()
    structured_output = extractor.parse_pdf(r"backend\rl\Database\Samples\curr_test.pdf")

    output_filepath = "curriculum_evidence_final.json"
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(structured_output, f, indent=4, ensure_ascii=False)

    print(f"Extraction successful! Clean evidence tree dumped to {output_filepath}")
