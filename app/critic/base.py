"""
Base Critic Abstract Interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from app.critic.context import CritiqueContext
from app.critic.contracts import CritiqueFinding, CritiquePerspective


class BaseCritic(ABC):
    """Abstract base class for all perspective-specific critics."""

    @property
    @abstractmethod
    def critic_id(self) -> str:
        """Unique identifier for this critic."""
        pass

    @property
    @abstractmethod
    def perspective(self) -> CritiquePerspective:
        """The analytical perspective of this critic."""
        pass

    @abstractmethod
    def can_critique(self, context: CritiqueContext) -> bool:
        """Determines whether the given context contains sufficient evidence for critique."""
        pass

    @abstractmethod
    def critique(self, context: CritiqueContext) -> list[CritiqueFinding]:
        """Performs analytical qualitative critique and returns structured findings."""
        pass
