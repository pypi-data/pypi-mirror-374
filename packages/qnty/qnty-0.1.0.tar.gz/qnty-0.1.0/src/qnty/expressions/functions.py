"""
Expression Helper Functions
==========================

Convenience functions for creating mathematical expressions.
"""

from ..quantities import FieldQnty, Quantity
from .nodes import BinaryOperation, ConditionalExpression, Expression, UnaryFunction, wrap_operand

# Type aliases for better maintainability
ExpressionOperand = Expression | FieldQnty | Quantity | int | float
ConditionalOperand = Expression | BinaryOperation


def _create_unary_function(name: str, docstring: str):
    """Factory function for creating unary mathematical functions."""

    def func(expr: ExpressionOperand) -> UnaryFunction:
        return UnaryFunction(name, wrap_operand(expr))

    func.__name__ = name
    func.__doc__ = docstring
    return func


def _create_comparison_expr(expressions: tuple[ExpressionOperand, ...], comparator: str) -> Expression:
    """Create min/max expression using specified comparator."""
    if len(expressions) < 2:
        raise ValueError(f"{comparator}_expr requires at least 2 arguments")

    wrapped_expressions = [wrap_operand(expr) for expr in expressions]
    result = wrapped_expressions[0]

    for expr in wrapped_expressions[1:]:
        if comparator == "min":
            # min(a, b) = if(a < b, a, b)
            result = cond_expr(result < expr, result, expr)
        else:  # max
            # max(a, b) = if(a > b, a, b)
            result = cond_expr(result > expr, result, expr)

    return result


# Mathematical functions (generated via factory)
sin = _create_unary_function("sin", "Sine function.")
cos = _create_unary_function("cos", "Cosine function.")
tan = _create_unary_function("tan", "Tangent function.")
sqrt = _create_unary_function("sqrt", "Square root function.")
abs_expr = _create_unary_function("abs", "Absolute value function.")
ln = _create_unary_function("ln", "Natural logarithm function.")
log10 = _create_unary_function("log10", "Base-10 logarithm function.")
exp = _create_unary_function("exp", "Exponential function.")


def cond_expr(
    condition: ConditionalOperand,
    true_expr: ExpressionOperand,
    false_expr: ExpressionOperand,
) -> ConditionalExpression:
    """Conditional expression: if condition then true_expr else false_expr."""
    wrapped_condition = condition if isinstance(condition, Expression) else condition
    return ConditionalExpression(wrapped_condition, wrap_operand(true_expr), wrap_operand(false_expr))


def min_expr(*expressions: ExpressionOperand) -> Expression:
    """Minimum of multiple expressions."""
    return _create_comparison_expr(expressions, "min")


def max_expr(*expressions: ExpressionOperand) -> Expression:
    """Maximum of multiple expressions."""
    return _create_comparison_expr(expressions, "max")
