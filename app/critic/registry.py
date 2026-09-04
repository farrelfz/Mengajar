"""
Dynamic Critic Registry supporting built-in and external plugin critics.
"""

from __future__ import annotations

from app.critic.base import BaseCritic


class CriticRegistry:
    """Registry managing available perspective and domain plugin critics."""

    def __init__(self) -> None:
        self._critics: dict[str, BaseCritic] = {}

    def register(self, critic: BaseCritic) -> None:
        """Registers a critic instance."""
        self._critics[critic.critic_id] = critic

    def unregister(self, critic_id: str) -> None:
        """Unregisters a critic by ID."""
        if critic_id in self._critics:
            del self._critics[critic_id]

    def get_all(self) -> list[BaseCritic]:
        """Returns all registered critics in deterministic key order."""
        return [self._critics[k] for k in sorted(self._critics.keys())]

    def get(self, critic_id: str) -> BaseCritic | None:
        """Gets a specific critic by ID."""
        return self._critics.get(critic_id)

    def count(self) -> int:
        """Returns number of registered critics."""
        return len(self._critics)
