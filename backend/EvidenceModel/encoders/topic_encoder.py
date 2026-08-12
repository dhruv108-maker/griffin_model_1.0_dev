from typing import List, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModel
from backend.Schemas.schemas import CurriculumNodeType


class TopicEncoder:
    # Explicit list of permitted node types for semantic evidence matching
    ALLOWED_NODE_TYPES = {"UNIT", "TOPIC"}

    def __init__(
        self, 
        model_name: str = "BAAI/bge-large-en-v1.5", 
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def extract_filtered_topics(self, heem_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        extracted = []

        def recurse(nodes: List[Dict[str, Any]]):
            for node in nodes:
                node_type = str(node.get("type", "")).upper()
                
                # Keep strictly UNIT and TOPIC nodes
                if node_type in self.ALLOWED_NODE_TYPES:
                    extracted.append({
                        "id": node["id"],
                        "type": node_type,
                        "text": node["text"],
                        "page": node.get("page", 0)
                    })
                
                # Recurse down children regardless of current node type
                if "children" in node and node["children"]:
                    recurse(node["children"])

        recurse(heem_tree.get("roots", []))
        return extracted

    def encode(self, heem_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        topics = self.extract_filtered_topics(heem_tree)
        texts = [f"{t['type']}: {t['text']}" for t in topics]
        
        if not texts:
            return []

        encoded = self.tokenizer(
            texts, padding=True, truncation=True, max_length=256, return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**encoded)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1).cpu().tolist()

        for t, emb in zip(topics, embeddings):
            t["embedding"] = emb

        return topics