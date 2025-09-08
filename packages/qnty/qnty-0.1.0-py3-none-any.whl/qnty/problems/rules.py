"""
Engineering problem checks and validation system.

This module provides a clean API for defining engineering code compliance checks,
warnings, and validation rules at the problem level rather than variable level.
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Any, Literal

from ..expressions import Expression
from ..quantities import FieldQnty, Quantity


@dataclass
class Rules:
    """
    Represents an engineering problem check (code compliance, validation, etc.).

    Checks are defined at the EngineeringProblem class level and evaluated after solving.
    They can represent code compliance rules, engineering judgment warnings, or
    validation conditions.
    """

    condition: Expression
    message: str
    warning_type: str = "VALIDATION"
    severity: Literal["INFO", "WARNING", "ERROR"] = "WARNING"
    name: str | None = None

    def __post_init__(self):
        """Generate a name if not provided."""
        if self.name is None:
            self.name = f"{self.warning_type}_{self.severity}"

    def evaluate(self, variables: dict[str, FieldQnty]) -> dict[str, Any] | None:
        """
        Evaluate the check condition and return a warning dict if condition is True.

        Args:
            variables: Dictionary of variable name -> FieldQnty object mappings

        Returns:
            Warning dictionary if condition is met, None otherwise
        """
        try:
            # Evaluate the condition expression using qnty's evaluation system
            result = self._evaluate_expression(self.condition, variables)

            if result:
                return {"type": self.warning_type, "severity": self.severity, "message": self.message, "check_name": self.name, "condition": str(self.condition)}

        except Exception as e:
            # If evaluation fails, return an error warning

            return {
                "type": "EVALUATION_ERROR",
                "severity": "ERROR",
                "message": f"Failed to evaluate check '{self.name}': {str(e)}",
                "check_name": self.name,
                "condition": str(self.condition),
                "debug_info": f"Expression type: {type(self.condition)}, Variables: {list(variables.keys())}",
                "traceback": traceback.format_exc(),
            }

        return None

    def _evaluate_expression(self, expr: Expression, variables: dict[str, FieldQnty]) -> bool:
        """
        Evaluate a qnty expression with current variable values.

        Args:
            expr: The expression to evaluate
            variables: Dictionary of variable name -> FieldQnty object mappings

        Returns:
            Boolean result of the expression evaluation
        """
        # Evaluate the expression using the qnty evaluation system
        result = expr.evaluate(variables)

        # Convert result to boolean based on type
        return self._convert_result_to_bool(result)

    def _convert_result_to_bool(self, result: Quantity) -> bool:
        """
        Convert an evaluation result to a boolean.

        Args:
            result: The result from expression evaluation

        Returns:
            Boolean interpretation of the result
        """
        # For qnty Quantity objects, check the value
        if isinstance(result, Quantity) and result.value is not None:
            return bool(result.value > 0.5)

        # Fallback for any numeric types
        try:
            return bool(float(result) > 0.5)  # type: ignore[arg-type]
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot convert expression result to boolean: {result}") from e


def add_rule(condition: Expression, message: str, warning_type: str = "VALIDATION", severity: Literal["INFO", "WARNING", "ERROR"] = "WARNING", name: str | None = None) -> Rules:
    """
    Create a new engineering problem check.

    This function is intended to be called at the class level when defining
    EngineeringProblem subclasses. It creates Check objects that will be
    automatically collected by the metaclass.

    Args:
        condition: A qnty Expression that evaluates to True when the check should trigger
        message: Descriptive message explaining what the check means
        warning_type: Category of check (e.g., "CODE_COMPLIANCE", "VALIDATION")
        severity: Severity level of the check
        name: Optional name for the check

    Returns:
        Check object that can be assigned to a class attribute

    Example:
        class MyProblem(EngineeringProblem):
            # Variables...
            P = Pressure(90, "psi")
            t = Length(0.1, "inch")
            D = Length(1.0, "inch")

            # Checks defined at class level
            thick_wall_check = add_check(
                t.geq(D / 6),
                "Thick wall condition detected - requires special consideration",
                warning_type="CODE_COMPLIANCE",
                severity="WARNING"
            )
    """
    return Rules(condition=condition, message=message, warning_type=warning_type, severity=severity, name=name)


__all__ = ["add_rule"]
