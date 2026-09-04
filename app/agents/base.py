"""
KIR AI Document Intelligence — Agent Base Class.

Defines the contract for all orchestration agents.
Agents own specific responsibilities and communicate via Pydantic schemas.
"""

from __future__ import annotations

import abc

from app.core.exceptions import AgentError
from app.core.logging import get_logger

log = get_logger(__name__)


class BaseAgent(abc.ABC):
    """Abstract base class for all AI orchestration agents."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Agent's human-readable name."""

    @property
    @abc.abstractmethod
    def responsibility(self) -> str:
        """Agent's core responsibility."""

    def log_start(self, job_id: str | None = None, **kwargs) -> None:
        """Standardized start log."""
        log.info(f"agent.{self.name}.start", job_id=job_id, **kwargs)

    def log_complete(self, job_id: str | None = None, **kwargs) -> None:
        """Standardized completion log."""
        log.info(f"agent.{self.name}.complete", job_id=job_id, **kwargs)

    def log_failure(self, error: Exception, job_id: str | None = None, **kwargs) -> None:
        """Standardized failure log."""
        log.error(f"agent.{self.name}.failed", error=str(error), job_id=job_id, **kwargs)

    def raise_error(self, message: str, job_id: str | None = None) -> None:
        """Raise a standard AgentError."""
        raise AgentError(message, agent_name=self.name, job_id=job_id, step=self.name)
