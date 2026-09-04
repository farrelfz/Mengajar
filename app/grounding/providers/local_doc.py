"""
Local Document Knowledge Provider: Loads Markdown and Text files directly into structured knowledge chunks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from app.grounding.contracts import (
    KnowledgeDocument,
    KnowledgeSource,
    KnowledgeSourceType,
    SourceAuthority,
)
from app.grounding.providers.in_memory import InMemoryKnowledgeProvider


class LocalDocumentKnowledgeProvider(InMemoryKnowledgeProvider):
    """Parses local markdown files and populates knowledge structures."""

    def __init__(self, provider_id: str = "local_doc_provider") -> None:
        super().__init__(provider_id=provider_id)

    def load_markdown_file(self, filepath: Path | str, domain: str = "general", authority: SourceAuthority = SourceAuthority.PRIMARY) -> None:
        path = Path(filepath)
        if not path.exists():
            return

        text = path.read_text(encoding="utf-8")
        src_id = f"src_{path.stem}"
        doc_id = f"doc_{path.stem}"

        source = KnowledgeSource(
            source_id=src_id,
            source_type=KnowledgeSourceType.LOCAL_DOCUMENT,
            title=path.stem.replace("_", " ").title(),
            authority=authority,
            domain=domain,
            uri=str(path.resolve()),
        )
        self.add_source(source)

        document = KnowledgeDocument(
            document_id=doc_id,
            source_id=src_id,
            title=source.title,
            content=text,
            domain=domain,
        )
        self.add_document(document)
