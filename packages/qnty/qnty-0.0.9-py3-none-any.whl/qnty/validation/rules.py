"""
Engineering problem checks and validation system.

This module provides a clean API for defining engineering code compliance checks,
warnings, and validation rules at the problem level rather than variable level.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from qnty.expressions import Expression as QntyExpression


@dataclass
class Rules:
    """
    Represents an engineering problem check (code compliance, validation, etc.).
    
    Checks are defined at the EngineeringProblem class level and evaluated after solving.
    They can represent code compliance rules, engineering judgment warnings, or
    validation conditions.
    """
    condition: QntyExpression
    message: str
    warning_type: str = "VALIDATION"
    severity: Literal["INFO", "WARNING", "ERROR"] = "WARNING"
    name: str | None = None
    
    def __post_init__(self):
        """Generate a name if not provided."""
        if self.name is None:
            self.name = f"{self.warning_type}_{self.severity}"
    
    def evaluate(self, variables: dict[str, Any]) -> dict[str, Any] | None:
        """
        Evaluate the check condition and return a warning dict if condition is True.
        
        Args:
            variables: Dictionary of variable name -> variable object mappings
            
        Returns:
            Warning dictionary if condition is met, None otherwise
        """
        try:
            # Evaluate the condition expression using qnty's evaluation system
            result = self._evaluate_expression(self.condition, variables)
            
            if result:
                return {
                    "type": self.warning_type,
                    "severity": self.severity,
                    "message": self.message,
                    "check_name": self.name,
                    "condition": str(self.condition)
                }
                
        except Exception as e:
            # If evaluation fails, return an error warning
            import traceback
            return {
                "type": "EVALUATION_ERROR",
                "severity": "ERROR",
                "message": f"Failed to evaluate check '{self.name}': {str(e)}",
                "check_name": self.name,
                "condition": str(self.condition),
                "debug_info": f"Expression type: {type(self.condition)}, Variables: {list(variables.keys())}",
                "traceback": traceback.format_exc()
            }
        
        return None
    
    def _evaluate_expression(self, expr: QntyExpression, variables: dict[str, Any]) -> bool:
        """
        Evaluate a qnty expression with current variable values.
        
        For qnty expressions, we can evaluate them directly since they have
        references to the variable values.
        """
        try:
            # qnty expressions have an evaluate() method that needs variable values
            if hasattr(expr, 'evaluate'):
                # Create a variable_values dict with the variable objects, not their quantities
                var_values = {}
                for var_name, var_obj in variables.items():
                    var_values[var_name] = var_obj
                
                result = expr.evaluate(var_values)
                # For boolean comparisons, result should be 1.0 (True) or 0.0 (False)
                # Handle FastQuantity type
                if hasattr(result, 'value'):  # FastQuantity
                    return bool(result.value > 0.5)
                elif hasattr(result, '__float__'):
                    # Use type: ignore to handle FastQuantity/Expression types that don't have __float__
                    return bool(float(result) > 0.5)  # type: ignore[arg-type]
                else:
                    # Last resort - try str conversion then float
                    result_str = str(result)
                    # Handle cases like "0.0 " (with units)
                    try:
                        return bool(float(result_str.split()[0]) > 0.5)
                    except (ValueError, IndexError):
                        return False
            else:
                # Try direct conversion as fallback
                if hasattr(expr, '__float__'):
                    # Use type: ignore to handle Expression types that don't have __float__
                    return bool(float(expr) > 0.5)  # type: ignore[arg-type]
                else:
                    return bool(float(str(expr)) > 0.5)
        except Exception as e:
            # If evaluation fails, assume the condition is not met
            # Re-raise to get better debugging info
            raise e


def add_rule(
    condition: QntyExpression,
    message: str,
    warning_type: str = "VALIDATION",
    severity: Literal["INFO", "WARNING", "ERROR"] = "WARNING",
    name: str | None = None
) -> Rules:
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
    return Rules(
        condition=condition,
        message=message,
        warning_type=warning_type,
        severity=severity,
        name=name
    )

__all__ = [
    "add_rule"
]
