import re
from typing import Any, Dict, List

from backend.Schemas.schemas import (
    GriffinDocument,
    GriffinStatistics,
    InputToken,
    InputTokenType,
    EvidenceToken,
    ReportMetadata,
)


class DocumentStructureParser:
    """
    Griffin Document Structure Parser

    Responsibilities
    ----------------
    - Parse page blocks
    - Detect document hierarchy
    - Generate InputTokens
    - Generate initial EvidenceTokens
    - Build GriffinDocument

    Does NOT perform:
        - embeddings
        - semantic enrichment
        - retrieval
        - validation
        - graph construction
    """

    IGNORED_HEADERS = {
        "certificate",
        "declaration",
        "acknowledgement",
        "acknowledgments",
        "table of contents",
        "contents",
        "abstract",
    }

    def parse(
        self,
        pdf_pages: List[Dict[str, Any]],
        metadata: ReportMetadata,
    ) -> GriffinDocument:

        input_tokens: List[InputToken] = []
        evidence_tokens: List[EvidenceToken] = []

        chapter = None
        section = None
        subsection = None
        heading = None

        token_index = 0

        for page_index, page in enumerate(pdf_pages):

            page_number = page_index + 1

            for block in page.get("blocks", []):

                text = block.get("text", "").strip()

                if not text:
                    continue

                if text.lower() in self.IGNORED_HEADERS:
                    continue

                bbox = block.get("bbox")

                # ----------------------------------------------------------
                # Heading
                # ----------------------------------------------------------

                if self._is_heading(text):

                    level = self._heading_level(text)

                    if level == 1:
                        chapter = text
                        section = None
                        subsection = None

                    elif level == 2:
                        section = text
                        subsection = None

                    else:
                        subsection = text

                    heading = text

                    input_tokens.append(
                        InputToken(
                            token_id=f"in_{token_index}",
                            token_type=InputTokenType.NAVIGATION,
                            page_number=page_number,
                            text=text,
                            chapter=chapter,
                            section=section,
                            subsection=subsection,
                            heading=heading,
                            bbox=bbox,
                        )
                    )

                    token_index += 1
                    continue

                # ----------------------------------------------------------
                # Input Token
                # ----------------------------------------------------------

                input_token = InputToken(
                    token_id=f"in_{token_index}",
                    token_type=InputTokenType.EVIDENCE,
                    page_number=page_number,
                    text=text,
                    chapter=chapter,
                    section=section,
                    subsection=subsection,
                    heading=heading,
                    bbox=bbox,
                )

                input_tokens.append(input_token)

                # ----------------------------------------------------------
                # Evidence Token
                # ----------------------------------------------------------

                evidence_tokens.append(
                    EvidenceToken(
                        token_id=f"ev_{token_index}",
                        page_number=page_number,
                        chapter=chapter,
                        section=section,
                        subsection=subsection,
                        heading=heading,
                        text=text,
                        token_type="EVIDENCE",
                        category="TEXT",
                        source_page=page_number,
                        source_bbox=bbox,
                        source_id=input_token.token_id,
                    )
                )

                token_index += 1

        statistics = GriffinStatistics(
            total_pages=len(pdf_pages),
            total_input_tokens=len(input_tokens),
            total_evidence_tokens=len(evidence_tokens),
        )

        return GriffinDocument(
            version="1.0",
            metadata=metadata,
            statistics=statistics,
            input_tokens=input_tokens,
            tokens=evidence_tokens,
        )

    @staticmethod
    def _is_heading(text: str) -> bool:
        """
        Detect whether a text block is a heading.
        """

        if len(text) > 120:
            return False

        if text.isupper():
            return True

        return bool(
            re.match(
                r"^(chapter\s+\d+|\d+(\.\d+)*\s+)",
                text,
                re.IGNORECASE,
            )
        )

    @staticmethod
    def _heading_level(text: str) -> int:
        """
        Estimate hierarchy level.

        Examples
        --------
        Chapter 1      -> 1
        1              -> 1
        1.1            -> 2
        1.1.1          -> 3
        """

        text = text.strip()

        if re.match(r"^chapter\s+\d+", text, re.IGNORECASE):
            return 1

        match = re.match(r"^(\d+(\.\d+)*)", text)

        if not match:
            return 1

        numbering = match.group(1)

        return numbering.count(".") + 1