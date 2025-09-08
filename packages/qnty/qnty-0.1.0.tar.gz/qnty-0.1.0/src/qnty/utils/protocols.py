"""
Performance-Optimized Protocols for Qnty
=========================================

Type protocols and registration system to avoid duck typing and circular imports
while maintaining maximum performance.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class ExpressionProtocol(Protocol):
    """
    Protocol for objects that can be evaluated as expressions.

    This avoids the need to import the actual Expression class,
    preventing circular imports while maintaining type safety.
    """

    @abstractmethod
    def get_variables(self) -> set[str]:
        """Get all variable symbols used in this expression."""
        ...

    @abstractmethod
    def evaluate(self, variable_values: dict) -> object:
        """Evaluate the expression given variable values."""
        ...


@runtime_checkable
class VariableProtocol(Protocol):
    """
    Protocol for variable objects that can be discovered in scope.

    This defines the interface that the scope discovery service expects
    without importing the actual variable classes.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Variable name."""
        ...

    @property
    @abstractmethod
    def symbol(self) -> str | None:
        """Variable symbol (preferred over name for equations)."""
        ...

    @property
    @abstractmethod
    def quantity(self) -> object | None:
        """The underlying quantity object."""
        ...


class TypeRegistry:
    """
    High-performance type registry using class caching.

    This eliminates the need for duck typing by maintaining a cache
    of known types and their capabilities.
    """

    # Class-level caches for maximum performance
    _expression_types: set[type] = set()
    _variable_types: set[type] = set()
    _type_cache: dict[type, tuple[bool, bool]] = {}  # (is_expression, is_variable)

    @classmethod
    def register_expression_type(cls, expression_type: type) -> None:
        """Register a type as an expression type."""
        cls._expression_types.add(expression_type)
        cls._invalidate_cache_for_type(expression_type)

    @classmethod
    def register_variable_type(cls, variable_type: type) -> None:
        """Register a type as a variable type."""
        cls._variable_types.add(variable_type)
        cls._invalidate_cache_for_type(variable_type)

    @classmethod
    def is_expression(cls, obj: object) -> bool:
        """
        Check if object is an expression with maximum performance.

        Uses cached type checking to avoid repeated isinstance calls.
        """
        obj_type = type(obj)

        if obj_type not in cls._type_cache:
            # Check if this type is registered as an expression type
            is_expr = any(isinstance(obj, expr_type) for expr_type in cls._expression_types)

            # Also check protocol compliance as fallback
            if not is_expr:
                is_expr = isinstance(obj, ExpressionProtocol)

            # Check if it's a variable too (for dual-purpose cache entry)
            is_var = any(isinstance(obj, var_type) for var_type in cls._variable_types)
            if not is_var:
                is_var = isinstance(obj, VariableProtocol)

            cls._type_cache[obj_type] = (is_expr, is_var)

        return cls._type_cache[obj_type][0]

    @classmethod
    def is_variable(cls, obj: object) -> bool:
        """
        Check if object is a variable with maximum performance.

        Uses cached type checking to avoid repeated isinstance calls.
        """
        obj_type = type(obj)

        if obj_type not in cls._type_cache:
            # This will populate the cache for both expression and variable
            cls.is_expression(obj)

        return cls._type_cache[obj_type][1]

    @classmethod
    def _invalidate_cache_for_type(cls, type_to_invalidate: type) -> None:
        """Invalidate cache entries for a specific type."""
        # Remove any cached entries that might be affected
        keys_to_remove = [k for k in cls._type_cache.keys() if issubclass(k, type_to_invalidate)]
        for key in keys_to_remove:
            del cls._type_cache[key]

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all caches (for testing)."""
        cls._type_cache.clear()

    @classmethod
    def get_cache_stats(cls) -> dict[str, int]:
        """Get cache statistics for monitoring."""
        return {"expression_types_registered": len(cls._expression_types), "variable_types_registered": len(cls._variable_types), "cached_types": len(cls._type_cache)}


# Convenience functions for backwards compatibility
def register_expression_type(expression_type: type) -> None:
    """Register a type as an expression type."""
    TypeRegistry.register_expression_type(expression_type)


def register_variable_type(variable_type: type) -> None:
    """Register a type as a variable type."""
    TypeRegistry.register_variable_type(variable_type)


def is_expression(obj: object) -> bool:
    """Check if object is an expression."""
    return TypeRegistry.is_expression(obj)


def is_variable(obj: object) -> bool:
    """Check if object is a variable."""
    return TypeRegistry.is_variable(obj)
