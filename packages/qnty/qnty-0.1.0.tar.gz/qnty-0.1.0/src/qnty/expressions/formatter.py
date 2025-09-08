"""
Expression String Formatting System
===================================

Centralized formatting logic for mathematical expressions with proper
operator precedence handling and readable output generation.
"""

from __future__ import annotations

from typing import Any

from .types import BinaryOperationProtocol, ConditionalExpressionProtocol, ConstantProtocol, ExpressionProtocol, UnaryFunctionProtocol, VariableReferenceProtocol


class ExpressionFormatter:
    """
    Handles string representation of expressions with proper precedence rules.

    Centralizes complex formatting logic that was previously scattered across
    expression classes, making it easier to maintain and extend.
    """

    # Operator precedence levels (higher number = higher precedence)
    OPERATOR_PRECEDENCE = {
        # Comparison operators (lowest precedence)
        "<": 0,
        "<=": 0,
        ">": 0,
        ">=": 0,
        "==": 0,
        "!=": 0,
        # Arithmetic operators
        "+": 1,
        "-": 1,  # Addition/subtraction
        "*": 2,
        "/": 2,  # Multiplication/division
        "**": 3,  # Exponentiation (highest precedence)
    }

    # Right-associative operators (most are left-associative by default)
    RIGHT_ASSOCIATIVE = {"**"}

    # Left-associative operators that need special parenthesization
    LEFT_ASSOCIATIVE_SPECIAL = {"-", "/"}

    @staticmethod
    def format_binary_operation(binary_op: BinaryOperationProtocol, can_auto_evaluate: bool = False, auto_eval_variables: dict[str, Any] | None = None) -> str:
        """
        Format binary operation with proper parenthesization.

        Args:
            binary_op: The binary operation to format
            can_auto_evaluate: Whether auto-evaluation should be attempted
            auto_eval_variables: Variables for auto-evaluation

        Returns:
            Formatted string representation
        """
        # Try auto-evaluation first if requested
        if can_auto_evaluate and auto_eval_variables:
            evaluation_result = ExpressionFormatter._try_evaluate(binary_op, auto_eval_variables)
            if evaluation_result is not None:
                return str(evaluation_result)

        # Get string representations of operands
        left_str = str(binary_op.left)
        right_str = str(binary_op.right)

        # Apply parenthesization rules
        left_str = ExpressionFormatter._maybe_parenthesize_left(binary_op.left, binary_op.operator, left_str)
        right_str = ExpressionFormatter._maybe_parenthesize_right(binary_op.right, binary_op.operator, right_str)

        return f"{left_str} {binary_op.operator} {right_str}"

    @staticmethod
    def _maybe_parenthesize_left(left_expr: ExpressionProtocol, operator: str, left_str: str) -> str:
        """Add parentheses to left operand if needed for precedence."""
        if not ExpressionFormatter._is_binary_operation(left_expr):
            return left_str

        left_precedence = ExpressionFormatter._get_expression_precedence(left_expr)
        current_precedence = ExpressionFormatter.get_operator_precedence(operator)

        # Left side needs parentheses only if its precedence is strictly lower
        if left_precedence < current_precedence:
            return f"({left_str})"

        return left_str

    @staticmethod
    def _maybe_parenthesize_right(right_expr: ExpressionProtocol, operator: str, right_str: str) -> str:
        """Add parentheses to right operand if needed for precedence and associativity."""
        if not ExpressionFormatter._is_binary_operation(right_expr):
            return right_str

        right_precedence = ExpressionFormatter._get_expression_precedence(right_expr)
        current_precedence = ExpressionFormatter.get_operator_precedence(operator)

        # Right side needs parentheses if:
        # 1. Its precedence is strictly lower, OR
        # 2. Same precedence AND current operator is left-associative (-, /)
        needs_parentheses = right_precedence < current_precedence or (right_precedence == current_precedence and operator in ExpressionFormatter.LEFT_ASSOCIATIVE_SPECIAL)

        if needs_parentheses:
            return f"({right_str})"

        return right_str

    @staticmethod
    def format_unary_function(func: UnaryFunctionProtocol) -> str:
        """Format unary function call."""
        return f"{func.function_name}({func.operand})"

    @staticmethod
    def format_conditional_expression(cond_expr: ConditionalExpressionProtocol) -> str:
        """Format conditional expression in if-then-else form."""
        return f"if({cond_expr.condition}, {cond_expr.true_expr}, {cond_expr.false_expr})"

    @staticmethod
    def format_variable_reference(var_ref: VariableReferenceProtocol) -> str:
        """Format variable reference (just the name)."""
        return var_ref.name

    @staticmethod
    def format_constant(constant: ConstantProtocol) -> str:
        """Format constant value."""
        return str(constant.value)

    @staticmethod
    def is_operator_right_associative(operator: str) -> bool:
        """Check if operator is right-associative."""
        return operator in ExpressionFormatter.RIGHT_ASSOCIATIVE

    @staticmethod
    def get_operator_precedence(operator: str) -> int:
        """Get precedence level for operator."""
        return ExpressionFormatter.OPERATOR_PRECEDENCE.get(operator, 0)

    @staticmethod
    def _try_evaluate(expression: ExpressionProtocol, variables: dict[str, Any]) -> Any | None:
        """
        Safely attempt to evaluate an expression.

        Args:
            expression: Expression to evaluate
            variables: Variable context for evaluation

        Returns:
            Evaluation result or None if evaluation failed
        """
        try:
            return expression.evaluate(variables)
        except (KeyError, ValueError, TypeError, ZeroDivisionError, AttributeError):
            # Catch specific exceptions that are expected during evaluation
            return None

    @staticmethod
    def _is_binary_operation(expr: ExpressionProtocol) -> bool:
        """Check if expression is a binary operation using duck typing."""
        return hasattr(expr, "operator") and hasattr(expr, "left") and hasattr(expr, "right")

    @staticmethod
    def _get_expression_precedence(expr: ExpressionProtocol) -> int:
        """Get precedence of an expression if it's a binary operation."""
        if ExpressionFormatter._is_binary_operation(expr):
            # We know it's a binary operation from the check above, so it has an operator
            binary_op = expr  # type: ignore[assignment]
            return ExpressionFormatter.get_operator_precedence(binary_op.operator)  # type: ignore[attr-defined]
        return 0

    @staticmethod
    def format_expression_with_auto_eval(expr: ExpressionProtocol) -> str:
        """
        Format expression, attempting auto-evaluation if possible.

        This is a convenience method that handles the common pattern of
        trying to auto-evaluate before falling back to symbolic representation.
        """
        # Check if auto-evaluation is possible for binary operations
        if ExpressionFormatter._is_binary_operation(expr) and hasattr(expr, "_can_auto_evaluate"):
            # We know it's a binary operation with auto-evaluation capability
            binary_op = expr  # type: ignore[assignment]
            can_eval, variables = binary_op._can_auto_evaluate()  # type: ignore[attr-defined]
            return ExpressionFormatter.format_binary_operation(binary_op, can_auto_evaluate=can_eval, auto_eval_variables=variables)  # type: ignore[arg-type]
        else:
            # For other expression types, just use their standard string representation
            return str(expr)
