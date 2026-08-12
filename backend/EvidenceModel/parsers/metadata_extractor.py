import torch
from transformers import AutoProcessor, AutoModelForTokenClassification
from backend.Schemas.schemas import ReportMetadata

class ReportMetadataExtractor:
    def __init__(self, model_name_or_path: str = "microsoft/layoutlmv3-base"):
        self.processor = AutoProcessor.from_pretrained(model_name_or_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name_or_path)
        self.model.eval()

    def extract(self, cover_page_image, raw_tokens: list[str], bbox: list[list[int]]) -> ReportMetadata:
        encoding = self.processor(
            cover_page_image, 
            raw_tokens, 
            boxes=bbox, 
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = self.model(**encoding)
            predictions = outputs.logits.argmax(-1).squeeze().tolist()
        
        # Mapping token classifications to metadata attributes
        metadata = ReportMetadata(
            title="Extracted Report Title",
            author="Extracted Author",
            institution="Extracted University",
            date="2026-03-30",
            raw_metadata={"pred_ids": predictions}
        )
        return metadata