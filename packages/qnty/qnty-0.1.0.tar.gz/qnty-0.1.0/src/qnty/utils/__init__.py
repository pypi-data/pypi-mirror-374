"""Shared utilities and helper functions."""

from .protocols import ExpressionProtocol, TypeRegistry, VariableProtocol, is_expression, is_variable, register_expression_type, register_variable_type
from .scope_discovery import ScopeDiscoveryService, discover_variables_from_scope

__all__ = [
    "ScopeDiscoveryService",
    "discover_variables_from_scope",
    "TypeRegistry",
    "ExpressionProtocol",
    "VariableProtocol",
    "register_expression_type",
    "register_variable_type",
    "is_expression",
    "is_variable",
]
