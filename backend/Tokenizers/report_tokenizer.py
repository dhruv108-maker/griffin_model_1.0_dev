class GriffinReportTokenizer:

    def tokenize(self, path):

        blocks = self._parse_document(path)

        structured = self._extract_structure(blocks)

        metadata = self._extract_metadata(structured)

        input_tokens = self._build_input_tokens(structured)

        enriched_tokens = self._enrich_tokens(input_tokens)

        griffin_tokens = self._build_griffin_tokens(enriched_tokens)

        return GriffinDocument(
            version="1.0",
            metadata=metadata,
            statistics=self._build_statistics(
                metadata,
                input_tokens,
                griffin_tokens,
            ),
            input_tokens=input_tokens,
            tokens=griffin_tokens,
        )