"""
Expression System Package
=========================

Mathematical expressions for building equation trees with qnty variables.
"""

# Core AST classes
from .nodes import (
    Expression,
    VariableReference,
    Constant,
    BinaryOperation,
    UnaryFunction,
    ConditionalExpression
)

# Helper functions
from .functions import (
    sin,
    cos,
    tan,
    sqrt,
    abs_expr,
    ln,
    log10,
    exp,
    cond_expr,
    min_expr,
    max_expr
)

# Cache utilities
from .cache import wrap_operand

# Define public API
__all__ = [
    # Core AST classes
    'Expression',
    'VariableReference',
    'Constant',
    'BinaryOperation',
    'UnaryFunction',
    'ConditionalExpression',
    
    # Helper functions
    'sin',
    'cos',
    'tan',
    'sqrt',
    'abs_expr',
    'ln',
    'log10',
    'exp',
    'cond_expr',
    'min_expr',
    'max_expr',
    
    # Utilities
    'wrap_operand'
]