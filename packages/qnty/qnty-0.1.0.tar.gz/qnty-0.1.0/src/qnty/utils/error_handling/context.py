"""
Error context and utility functions for error handling.

This module provides context management and utility functions to support
consistent error reporting throughout the library.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ErrorContext:
    """Context information for errors to aid in debugging."""

    module: str
    function: str
    operation: str
    variables: dict[str, Any] | None = None
    additional_info: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for error logging."""
        return {"module": self.module, "function": self.function, "operation": self.operation, "variables": self.variables, "additional_info": self.additional_info}


def get_dimension_string(obj: Any) -> str:
    """Get dimension string representation for error messages."""
    if hasattr(obj, "_dimension_sig"):
        return str(obj._dimension_sig)
    elif hasattr(obj, "unit") and hasattr(obj.unit, "dimension"):
        return str(obj.unit.dimension)
    else:
        return f"{type(obj).__name__}"


def create_context(module: str, function: str, operation: str, **kwargs) -> ErrorContext:
    """Create error context for consistent error reporting."""
    return ErrorContext(module=module, function=function, operation=operation, additional_info=kwargs)
