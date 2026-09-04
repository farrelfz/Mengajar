"""
Observability thread-safe and task-safe context propagation system using contextvars.
"""

from __future__ import annotations

import contextvars
from typing import Optional

# Core context variables
run_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("run_id", default=None)
trace_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("trace_id", default=None)
span_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("span_id", default=None)
parent_span_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("parent_span_id", default=None)
stage_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("stage", default=None)
component_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("component", default=None)

# Configuration variable to toggle observability dynamically
enabled_var: contextvars.ContextVar[bool] = contextvars.ContextVar("observability_enabled", default=True)


class ObservabilityContextManager:
    """Helper class to manage context variables."""

    @staticmethod
    def get_run_id() -> Optional[str]:
        return run_id_var.get()

    @staticmethod
    def get_trace_id() -> Optional[str]:
        return trace_id_var.get()

    @staticmethod
    def get_span_id() -> Optional[str]:
        return span_id_var.get()

    @staticmethod
    def get_parent_span_id() -> Optional[str]:
        return parent_span_id_var.get()

    @staticmethod
    def get_stage() -> Optional[str]:
        return stage_var.get()

    @staticmethod
    def get_component() -> Optional[str]:
        return component_var.get()

    @staticmethod
    def is_enabled() -> bool:
        return enabled_var.get()

    @staticmethod
    def set_enabled(value: bool) -> None:
        enabled_var.set(value)
