from typing import List, Dict, Any

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel


class TopicEncoder:
    """Encodes curriculum UNIT/TOPIC nodes into normalized BGE embeddings."""

    ALLOWED_NODE_TYPES = {"UNIT", "TOPIC"}

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-en-v1.5",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        self.model_name = model_name

    def extract_filtered_topics(self, heem_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        extracted = []

        def recurse(nodes: List[Dict[str, Any]], parent_unit_id: int | None = None) -> None:
            for node in nodes:
                node_type = str(node.get("type", "")).upper()
                current_unit_id = node.get("id") if node_type == "UNIT" else parent_unit_id

                if node_type in self.ALLOWED_NODE_TYPES:
                    extracted.append({
                        "id": node["id"],
                        "type": node_type,
                        "text": node["text"],
                        "page": node.get("page", 0),
                        "unit_id": None if node_type == "UNIT" else current_unit_id,
                    })

                children = node.get("children") or []
                if children:
                    recurse(children, current_unit_id)

        recurse(heem_tree.get("roots", []))
        return extracted

    def encode(self, heem_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        topics = self.extract_filtered_topics(heem_tree)
        texts = [f"{topic['type']}: {topic['text']}" for topic in topics]
        if not texts:
            return []

        encoded = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**encoded)
            mask = encoded["attention_mask"].unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
            pooled = (outputs.last_hidden_state * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
            embeddings = F.normalize(pooled, p=2, dim=1).cpu().tolist()

        dimension = len(embeddings[0]) if embeddings else 0
        for topic, embedding in zip(topics, embeddings):
            topic["embedding"] = embedding
            topic["embedding_model"] = self.model_name
            topic["embedding_dimension"] = dimension

        return topics
