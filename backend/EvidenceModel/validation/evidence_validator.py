import torch

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from backend.Schemas.schemas import (
    EvidenceToken,
    ValidatedEvidence,
)


class EvidenceValidator:
    """
    Griffin Evidence Validator

    Uses a Cross-Encoder to validate semantic matches produced by the
    dense retrieval stage.

    Input
    -----
    Curriculum Topic
            +
    Evidence Token

    Output
    ------
    ValidatedEvidence
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):

        self.device = device
        self.model_name = model_name

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(model_name)
            .to(device)
        )

        self.model.eval()

    def validate(
        self,
        topic_text: str,
        token: EvidenceToken,
        similarity_score: float,
    ) -> ValidatedEvidence:
        """
        Validate a retrieved EvidenceToken against a curriculum topic.
        """

        inputs = self.tokenizer(
            topic_text,
            token.text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():

            logits = self.model(**inputs).logits

            confidence = float(
                torch.sigmoid(logits).squeeze().cpu().item()
            )

        # ------------------------------------------------------------------
        # Hybrid confidence score
        # ------------------------------------------------------------------

        reasoning_score = (
            similarity_score * 0.40
            + confidence * 0.60
        )

        reasoning_score = max(
            0.0,
            min(
                1.0,
                reasoning_score,
            ),
        )

        explanation = (
            f"Evidence token demonstrates semantic alignment with "
            f"curriculum topic '{topic_text}'. "
            f"Cross-encoder confidence={confidence:.3f}, "
            f"dense similarity={similarity_score:.3f}."
        )

        return ValidatedEvidence(
            topic_id=-1,  # Assigned by GriffinCore
            token_id=token.token_id,
            page_number=token.page_number,
            similarity=similarity_score,
            confidence=confidence,
            reasoning_score=reasoning_score,
            explanation=explanation,
        )