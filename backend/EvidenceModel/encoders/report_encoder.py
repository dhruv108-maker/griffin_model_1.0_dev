import torch
import torch.nn.functional as F

from typing import List
from transformers import AutoModel, AutoTokenizer

from backend.Schemas.schemas import EvidenceToken


class ReportEncoder:
    """
    Griffin Report Encoder

    Encodes Griffin Evidence Tokens into dense semantic embeddings
    using a BGE transformer backbone.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-en-v1.5",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.model_name = model_name
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(device)
        self.model.eval()

    def encode(
        self,
        tokens: List[EvidenceToken],
        batch_size: int = 16,
    ) -> List[EvidenceToken]:
        if not tokens:
            return tokens

        texts = [token.text for token in tokens]
        embeddings = []

        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            encoded = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**encoded)
                pooled = self._mean_pooling(
                    outputs.last_hidden_state,
                    encoded["attention_mask"],
                )
                pooled = F.normalize(pooled, p=2, dim=1)
                embeddings.extend(pooled.cpu().tolist())

        dimension = len(embeddings[0]) if embeddings else 0
        for token, embedding in zip(tokens, embeddings):
            token.embedding = embedding
            token.embedding_model = self.model_name
            token.embedding_dimension = dimension

        return tokens

    @staticmethod
    def _mean_pooling(
        token_embeddings: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        summed = torch.sum(token_embeddings * mask, dim=1)
        counts = torch.clamp(mask.sum(dim=1), min=1e-9)
        return summed / counts
