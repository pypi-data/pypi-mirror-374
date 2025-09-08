"""
Error handling infrastructure for the Qnty library.

This package provides comprehensive error handling capabilities including
custom exceptions, error handlers, and context management.

Public API:
- Exception classes: QntyError, DimensionalError, UnitConversionError, etc.
- Error handling: ErrorHandler, ErrorHandlerMixin
- Context management: ErrorContext
- Convenience functions: require_variable, ensure_not_zero, safe_evaluate
"""

# Import all exception classes
# Import context management
from .context import (
    ErrorContext,
    create_context,
    get_dimension_string,
)
from .exceptions import (
    ERROR_MESSAGES,
    DimensionalError,
    DivisionByZeroError,
    EquationSolvingError,
    ExpressionEvaluationError,
    QntyError,
    UnitConversionError,
    VariableNotFoundError,
)

# Import handlers and utilities
from .handlers import (
    ErrorHandler,
    ErrorHandlerMixin,
    ensure_not_zero,
    get_error_handler,
    require_variable,
    safe_evaluate,
    set_error_handler,
)

# Define public API
__all__ = [
    # Exception classes
    "QntyError",
    "DimensionalError",
    "UnitConversionError",
    "VariableNotFoundError",
    "EquationSolvingError",
    "ExpressionEvaluationError",
    "DivisionByZeroError",
    "ERROR_MESSAGES",
    # Context management
    "ErrorContext",
    "get_dimension_string",
    "create_context",
    # Handlers and utilities
    "ErrorHandler",
    "ErrorHandlerMixin",
    "get_error_handler",
    "set_error_handler",
    "require_variable",
    "ensure_not_zero",
    "safe_evaluate",
]
