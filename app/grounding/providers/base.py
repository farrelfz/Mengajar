"""
Abstract Base Class for Knowledge Providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from app.grounding.contracts import Evidence, KnowledgeDocument, KnowledgeSource
from app.grounding.providers.contracts import KnowledgeQuery


class KnowledgeProvider(ABC):
    """Abstract interface for knowledge retrieval providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier of the provider instance."""
        pass

    @abstractmethod
    def search(self, query: KnowledgeQuery) -> list[Evidence]:
        """Search and return candidate evidence snippets."""
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        """Retrieve a document by ID."""
        pass

    @abstractmethod
    def get_source(self, source_id: str) -> KnowledgeSource | None:
        """Retrieve source container metadata by ID."""
        pass

    def health_check(self) -> bool:
        """Verify provider operational status."""
        return True
