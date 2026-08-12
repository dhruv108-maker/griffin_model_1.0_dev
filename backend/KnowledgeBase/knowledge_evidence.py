import json
import re
from typing import Dict, List, Any, Optional, Tuple
import pypdf

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

        # 1. Merge duplicate course roots into one canonical root
        canonical_roots = self._canonicalize_roots(tree["roots"])

        # 2. Process hierarchy, prune empty sections and residual layout noise
        cleaned_roots = []
        for root in canonical_roots:
            cleaned_root = self._process_node(root)
            if cleaned_root:
                cleaned_roots.append(cleaned_root)

        # 3. Re-index all node IDs sequentially from 0
        self.counter = 0
        for root in cleaned_roots:
            self._reindex_node(root)

        return {"roots": cleaned_roots}

    def _canonicalize_roots(self, roots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidates multiple detected COURSE roots into a single canonical root."""
        if not roots:
            return []

        primary_root = roots[0]
        if "metadata" not in primary_root:
            primary_root["metadata"] = {}

        for secondary_root in roots[1:]:
            primary_root["children"].extend(secondary_root.get("children", []))
            if "metadata" in secondary_root:
                primary_root["metadata"].update(secondary_root["metadata"])

        return [primary_root]

    def _process_node(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recursively cleans text, deduplicates children, and prunes empty containers."""
        if not node.get("children"):
            return node

        processed_children = []
        for child in node["children"]:
            processed_child = self._process_node(child)
            if processed_child:
                processed_children.append(processed_child)

        # Deduplicate children based on node type and normalized text
        seen_keys = set()
        unique_children = []
        for child in processed_children:
            norm_text = re.sub(r"\s+", " ", child["text"].lower().strip())
            sig_key = (child["type"], norm_text)

            if sig_key not in seen_keys:
                seen_keys.add(sig_key)
                unique_children.append(child)

        node["children"] = unique_children

        # Prune empty container/section nodes
        container_types = ["OBJECTIVE", "UNIT", "CO", "PO", "PSO", "ASSESSMENT", "RESOURCE", "PRACTICAL", "PEDAGOGY", "METADATA"]
        if node["type"] in container_types and len(node["children"]) == 0:
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
    Rule-based extractor & parser for curriculum documents that enforces clean
    semantic separation, metadata isolation, and layout artifact removal.
    """
    def __init__(self):
        self.node_id = 0
        self.transformer = EvidenceTransformer()

    def _next_id(self) -> int:
        current_id = self.node_id
        self.node_id += 1
        return current_id

    def _create_node(self, node_type: str, text: str, page: int, confidence: float = 0.99, attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        node = {
            "id": self._next_id(),
            "type": node_type,
            "text": self._clean_layout_artifacts(text),
            "page": page,
            "confidence": confidence,
            "attributes": attributes or {},
            "children": []
        }
        if node_type == "COURSE":
            node["metadata"] = {}
        return node

    def _clean_layout_artifacts(self, text: str) -> str:
        """Strips bullet points, table lines, residual numbers, and dangling layout noise."""
        text = re.sub(r"^[•\-\*\d\.\:\s]+", "", text)  # Leading bullets & numbers
        text = re.sub(r"\|", " ", text)                # Table border pipes
        text = re.sub(r"[\t\r\n]+", " ", text)         # Layout linebreaks
        text = re.sub(r"\s+", " ", text).strip()        # Extra spaces
        return text

    def _is_noise(self, line: str) -> bool:
        """Filters headers, footers, page numbering, and structural table margins."""
        if re.match(r"(?i)^(page\s*\d+(\s*of\s*\d+)?|\d+\s*/\s*\d+)$", line):
            return True
        if re.match(r"(?i)^(curriculum|syllabus|department of|faculty of).*page", line):
            return True
        if re.match(r"^[\-\_\=\|\s]{3,}$", line):  # Divider lines
            return True
        return False

    def _parse_attributes_and_cos(self, raw_text: str) -> Tuple[str, Dict[str, Any], List[str]]:
        """
        Extracts weightage/contact hours into attributes and parses inline COs
        into standalone entities while cleaning the source text.
        """
        attributes = {}
        embedded_cos = []
        text = raw_text

        # Extract Contact Hours (e.g., "8 Hours", "10 Hrs", "[4L]")
        hours_match = re.search(r"\(?\b(\d+)\s*(?:hours?|hrs?|L|Lectures?)\b\)?", text, re.IGNORECASE)
        if hours_match:
            attributes["hours"] = hours_match.group(0).strip("()")
            text = text.replace(hours_match.group(0), "")

        # Extract Weightage (e.g., "15%", "20 Marks", "Weightage: 10%")
        weightage_match = re.search(r"\(?\b(?:weightage\s*[:\-]?\s*)?(\d+\s*%|\d+\s*marks?)\b\)?", text, re.IGNORECASE)
        if weightage_match:
            attributes["weightage"] = weightage_match.group(1)
            text = text.replace(weightage_match.group(0), "")

        # Extract Embedded CO References (e.g., "[CO1, CO2]", "(CO3)")
        co_matches = re.findall(r"\b(CO\d+)\b", text, re.IGNORECASE)
        if co_matches:
            embedded_cos = list(dict.fromkeys([co.upper() for co in co_matches]))
            text = re.sub(r"\[?\b(?:CO\d+(?:\s*,\s*)?)+\b\]?", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\(\s*\)", "", text)  # Remove empty remaining parentheses

        cleaned_text = self._clean_layout_artifacts(text)
        return cleaned_text, attributes, embedded_cos

    def _extract_metadata(self, line: str, course_node: Dict[str, Any]) -> bool:
        """Separates metadata from semantic evidence into dedicated fields/nodes."""
        meta_patterns = [
            (r"(?i)Course\s*Code\s*[:\-]\s*(.*)", "course_code"),
            (r"(?i)Credits?\s*[:\-]\s*(\d+(\.\d+)?)", "credits"),
            (r"(?i)Prerequisite[s]?\s*[:\-]\s*(.*)", "prerequisites"),
            (r"(?i)Total\s*Hours\s*[:\-]\s*(\d+)", "total_hours"),
            (r"(?i)Marks\s*[:\-]\s*(.*)", "marks_distribution")
        ]
        for pattern, key in meta_patterns:
            match = re.search(pattern, line)
            if match:
                val = match.group(1).strip()
                course_node["metadata"][key] = val
                return True
        return False

    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        reader = pypdf.PdfReader(pdf_path)
        roots = []
        current_course = None
        current_section = None
        last_leaf_node = None

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            lines = [line.strip() for line in text.splitlines() if line.strip()]

            for line in lines:
                # 1. Strip Header/Footer & Layout Noise
                if self._is_noise(line):
                    continue

                # 2. Detect Course Root
                if "COURSE NAME" in line.upper() or "DATABASE MANAGEMENT SYSTEM" in line.upper():
                    clean_title = re.sub(r"(?i)COURSE NAME\s*[:\-]*\s*", "", line)
                    if clean_title:
                        current_course = self._create_node("COURSE", clean_title, page_num)
                        roots.append(current_course)
                        current_section = None
                        last_leaf_node = None
                    continue

                if current_course is None:
                    continue

                # 3. Extract Metadata into Attributes / Isolated Node
                if self._extract_metadata(line, current_course):
                    # Ensure a dedicated METADATA container exists
                    meta_section = next((c for c in current_course["children"] if c["type"] == "METADATA"), None)
                    if not meta_section:
                        meta_section = self._create_node("METADATA", "Course Metadata", page_num)
                        current_course["children"].append(meta_section)
                    
                    meta_leaf = self._create_node("METADATA", line, page_num)
                    meta_section["children"].append(meta_leaf)
                    continue

                # 4. Detect Section Headers (Dedicated Node Types)
                if re.match(r"(?i)^Course Objectives", line):
                    current_section = self._create_node("OBJECTIVE", "Course Objectives", page_num)
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                elif re.match(r"(?i)^Unit\s+\d+", line):
                    clean_text, attrs, _ = self._parse_attributes_and_cos(line)
                    current_section = self._create_node("UNIT", clean_text, page_num, attributes=attrs)
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                elif re.match(r"(?i)^Course Outcomes", line):
                    current_section = self._create_node("CO", "Course Outcomes", page_num)
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                elif re.match(r"(?i)^(Programme Outcomes|POs)", line):
                    current_section = self._create_node("PO", "Programme Outcomes", page_num)
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                elif re.match(r"(?i)^(Programme Specific Outcomes|PSOs)", line):
                    current_section = self._create_node("PSO", "Programme Specific Outcomes", page_num)
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                elif re.match(r"(?i)^(Practicals|Laboratory Work|Experiments|Lab Sessions)", line):
                    current_section = self._create_node("PRACTICAL", "Practicals", page_num)
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                elif re.match(r"(?i)^(Pedagogy|Teaching Methodology|Instructional Strategies)", line):
                    current_section = self._create_node("PEDAGOGY", "Pedagogy & Teaching Methodology", page_num)
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                elif re.match(r"(?i)^Evaluation Scheme", line):
                    current_section = self._create_node("ASSESSMENT", "Evaluation Scheme", page_num)
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                elif re.match(r"(?i)^(Learning Resources|Reference Books)", line):
                    current_section = self._create_node("RESOURCE", "Learning Resources", page_num)
                    current_course["children"].append(current_section)
                    last_leaf_node = None
                    continue

                # 5. Extract Leaf Nodes, Process Attributes & Standalone CO Nodes
                if current_section:
                    is_new_item = bool(re.match(r"^(\d+[\.\:]|CO\d+|PO\d+|PSO\d+|\u2022|\-)", line, re.IGNORECASE))

                    # Merge wrapped sentences with previous leaf node
                    if not is_new_item and last_leaf_node and not line.startswith("Unit"):
                        additional_text, add_attrs, add_cos = self._parse_attributes_and_cos(line)
                        if additional_text:
                            last_leaf_node["text"] += f" {additional_text}"
                        last_leaf_node["attributes"].update(add_attrs)
                        
                        # Add newly discovered embedded COs as child nodes
                        for co_code in add_cos:
                            co_node = self._create_node("CO", f"Mapped Outcome: {co_code}", page_num)
                            last_leaf_node["children"].append(co_node)
                        continue

                    # Parse inline attributes and embedded CO references
                    clean_line, line_attrs, embedded_cos = self._parse_attributes_and_cos(line)
                    if not clean_line:
                        continue

                    # Unit Topics
                    if current_section["type"] == "UNIT":
                        topic_node = self._create_node("TOPIC", clean_line, page_num, attributes=line_attrs)
                        
                        # Extract embedded COs into standalone CO nodes
                        for co_code in embedded_cos:
                            co_child = self._create_node("CO", f"Mapped Outcome: {co_code}", page_num)
                            topic_node["children"].append(co_child)

                        current_section["children"].append(topic_node)
                        last_leaf_node = topic_node

                    # Practicals
                    elif current_section["type"] == "PRACTICAL":
                        practical_node = self._create_node("PRACTICAL", clean_line, page_num, attributes=line_attrs)
                        current_section["children"].append(practical_node)
                        last_leaf_node = practical_node

                    # Pedagogy
                    elif current_section["type"] == "PEDAGOGY":
                        pedagogy_node = self._create_node("PEDAGOGY", clean_line, page_num, attributes=line_attrs)
                        current_section["children"].append(pedagogy_node)
                        last_leaf_node = pedagogy_node

                    # Objectives / Assessment / Resources
                    elif current_section["type"] in ["OBJECTIVE", "ASSESSMENT", "RESOURCE"]:
                        leaf_node = self._create_node(current_section["type"], clean_line, page_num, attributes=line_attrs)
                        current_section["children"].append(leaf_node)
                        last_leaf_node = leaf_node

                    # Course & Programme Outcomes
                    elif current_section["type"] in ["CO", "PO", "PSO"]:
                        outcome_node = self._create_node(current_section["type"], clean_line, page_num, attributes=line_attrs)
                        current_section["children"].append(outcome_node)
                        last_leaf_node = outcome_node

        raw_output = {"roots": roots}
        return self.transformer.transform(raw_output)


# Execution Entrypoint
if __name__ == "__main__":
    extractor = CurriculumEvidenceExtractor()
    structured_output = extractor.parse_pdf(r"backend\rl\Database\Samples\curr_test.pdf")

    # Output directly to final JSON format
    output_filepath = "curriculum_evidence_final.json"
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(structured_output, f, indent=4, ensure_ascii=False)

    print(f"Extraction successful! Clean evidence tree dumped to {output_filepath}")