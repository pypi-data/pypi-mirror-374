"""
Exception classes for the Qnty library.

This module defines all custom exception types used throughout the library
for consistent error handling and reporting.
"""

from typing import Any


# Custom Exception Hierarchy
class QntyError(Exception):
    """Base exception for all qnty library errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        super().__init__(message)
        self.context = context or {}
        self.message = message


class DimensionalError(QntyError):
    """Raised when operations involve incompatible dimensions."""

    def __init__(self, operation: str, left_dim: str, right_dim: str, context: dict | None = None):
        message = f"Incompatible dimensions for {operation}: {left_dim} and {right_dim}"
        super().__init__(message, context)
        self.operation = operation
        self.left_dimension = left_dim
        self.right_dimension = right_dim


class UnitConversionError(QntyError):
    """Raised when unit conversions fail."""

    def __init__(self, from_unit: str, to_unit: str, reason: str = "", context: dict | None = None):
        message = f"Cannot convert from '{from_unit}' to '{to_unit}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, context)
        self.from_unit = from_unit
        self.to_unit = to_unit


class VariableNotFoundError(QntyError):
    """Raised when a required variable is not found."""

    def __init__(self, variable_name: str, available_vars: list[str] | None = None, context: dict | None = None):
        message = f"Variable '{variable_name}' not found"
        if available_vars:
            message += f". Available variables: {', '.join(available_vars)}"
        super().__init__(message, context)
        self.variable_name = variable_name
        self.available_vars = available_vars or []


class EquationSolvingError(QntyError):
    """Raised when equation solving fails."""

    def __init__(self, equation_name: str, target_var: str, reason: str = "", context: dict | None = None):
        message = f"Cannot solve equation '{equation_name}' for variable '{target_var}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, context)
        self.equation_name = equation_name
        self.target_var = target_var


class ExpressionEvaluationError(QntyError):
    """Raised when expression evaluation fails."""

    def __init__(self, expression: str, reason: str = "", context: dict | None = None):
        message = f"Cannot evaluate expression '{expression}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, context)
        self.expression = expression


class DivisionByZeroError(QntyError):
    """Raised for division by zero operations."""

    def __init__(self, dividend: str, context: dict | None = None):
        message = f"Division by zero: {dividend} / 0"
        super().__init__(message, context)
        self.dividend = dividend


# Error message templates for consistency
ERROR_MESSAGES = {
    "incompatible_dimensions": "Incompatible dimensions: {left} and {right} for operation {operation}",
    "variable_not_found": "Variable '{variable}' not found. Available: {available}",
    "unit_conversion_failed": "Cannot convert from '{from_unit}' to '{to_unit}': {reason}",
    "equation_unsolvable": "Cannot solve equation '{equation}' for variable '{variable}': {reason}",
    "division_by_zero": "Division by zero in expression: {expression}",
    "invalid_operation": "Invalid operation '{operation}' on {type}: {reason}",
}
