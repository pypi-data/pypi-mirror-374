"""
Expression Type Definitions
===========================

Type definitions and protocols to avoid circular imports.
"""

from __future__ import annotations

from typing import Protocol
from ..quantities import FieldQnty, Quantity


class ExpressionProtocol(Protocol):
    """Protocol for expression objects."""

    def evaluate(self, variable_values: dict[str, FieldQnty]) -> Quantity:
        """Evaluate the expression with given variables."""
        ...


class VariableReferenceProtocol(Protocol):
    """Protocol for variable reference objects."""

    name: str

    def evaluate(self, variable_values: dict[str, FieldQnty]) -> Quantity:
        """Evaluate the variable reference."""
        ...


class ConstantProtocol(Protocol):
    """Protocol for constant objects."""

    value: Quantity

    def evaluate(self, variable_values: dict[str, FieldQnty]) -> Quantity:
        """Evaluate the constant."""
        ...


class BinaryOperationProtocol(Protocol):
    """Protocol for binary operation objects."""

    left: ExpressionProtocol
    right: ExpressionProtocol
    operator: str

    def evaluate(self, variable_values: dict[str, FieldQnty]) -> Quantity:
        """Evaluate the binary operation."""
        ...

    def _can_auto_evaluate(self) -> tuple[bool, dict[str, FieldQnty] | None]:
        """Check if auto-evaluation is possible."""
        ...


class UnaryFunctionProtocol(Protocol):
    """Protocol for unary function objects."""

    function_name: str
    operand: ExpressionProtocol


class ConditionalExpressionProtocol(Protocol):
    """Protocol for conditional expression objects."""

    condition: ExpressionProtocol
    true_expr: ExpressionProtocol
    false_expr: ExpressionProtocol
