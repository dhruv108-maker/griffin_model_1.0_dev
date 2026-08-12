import numpy as np

from typing import Any, Dict, List

from backend.Schemas.schemas import (
    CandidateEvidence,
    EvidenceToken,
)


class EvidenceRetriever:
    """
    Griffin Evidence Retriever

    Performs dense semantic retrieval between:

        Curriculum Topic Embeddings
                    ↓
            Evidence Token Embeddings

    Returns the Top-K candidate evidence tokens for every curriculum topic.
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def retrieve(
        self,
        encoded_topics: List[Dict[str, Any]],
        encoded_tokens: List[EvidenceToken],
    ) -> List[CandidateEvidence]:

        if not encoded_topics or not encoded_tokens:
            return []

        # ------------------------------------------------------------------
        # Filter invalid topic embeddings
        # ------------------------------------------------------------------

        valid_topics = [
            topic
            for topic in encoded_topics
            if topic.get("embedding") is not None
        ]

        # ------------------------------------------------------------------
        # Filter invalid evidence embeddings
        # ------------------------------------------------------------------

        valid_tokens = [
            token
            for token in encoded_tokens
            if token.embedding is not None
        ]

        if not valid_topics or not valid_tokens:
            return []

        topic_embeddings = np.asarray(
            [topic["embedding"] for topic in valid_topics],
            dtype=np.float32,
        )

        token_embeddings = np.asarray(
            [token.embedding for token in valid_tokens],
            dtype=np.float32,
        )

        # ------------------------------------------------------------------
        # Cosine Similarity
        # Embeddings are already L2-normalized by ReportEncoder.
        # ------------------------------------------------------------------

        similarity_matrix = topic_embeddings @ token_embeddings.T

        candidates: List[CandidateEvidence] = []

        for topic_index, topic in enumerate(valid_topics):

            top_indices = np.argsort(
                -similarity_matrix[topic_index]
            )[: self.top_k]

            for token_index in top_indices:

                token = valid_tokens[token_index]

                candidates.append(
                    CandidateEvidence(
                        topic_id=topic["id"],
                        token_id=token.token_id,
                        similarity_score=float(
                            similarity_matrix[topic_index][token_index]
                        ),
                    )
                )

        return candidates