"""
Expression System Package
=========================

Mathematical expressions for building equation trees with qnty variables.
"""

# Core AST classes
# Helper functions
# Scope discovery service
from ..utils.scope_discovery import ScopeDiscoveryService
from .functions import abs_expr, cond_expr, cos, exp, ln, log10, max_expr, min_expr, sin, sqrt, tan
from .nodes import BinaryOperation, ConditionalExpression, Constant, Expression, UnaryFunction, VariableReference, wrap_operand

# Define public API
__all__ = [
    # Core AST classes
    "Expression",
    "VariableReference",
    "Constant",
    "BinaryOperation",
    "UnaryFunction",
    "ConditionalExpression",
    # Helper functions
    "sin",
    "cos",
    "tan",
    "sqrt",
    "abs_expr",
    "ln",
    "log10",
    "exp",
    "cond_expr",
    "min_expr",
    "max_expr",
    # Utilities
    "wrap_operand",
    # Scope discovery
    "ScopeDiscoveryService",
]
