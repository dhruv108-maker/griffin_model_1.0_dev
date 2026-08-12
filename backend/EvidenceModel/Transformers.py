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
