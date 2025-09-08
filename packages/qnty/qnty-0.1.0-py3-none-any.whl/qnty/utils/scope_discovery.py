"""
Scope Discovery Service
=======================

Centralized service for automatically discovering variables from the calling scope.
Consolidates all scope inspection logic used across expressions, equations, and variable solving.

This module uses protocol-based design to avoid circular imports and duck typing performance issues.
"""

import inspect
import logging
from typing import Any

from .protocols import TypeRegistry

# Setup logging for better debugging
_logger = logging.getLogger(__name__)


class ScopeDiscoveryService:
    """
    Centralized service for scope discovery operations.

    Provides optimized variable discovery from calling scopes with caching,
    depth limits, and consistent error handling.
    """

    # Class-level optimization settings
    _scope_cache = {}
    _frame_cache = {}
    _variable_name_cache = {}
    _max_scope_cache_size = 200  # Increased cache size
    _max_frame_cache_size = 50
    _max_search_depth = 8
    _cache_hit_count = 0
    _cache_miss_count = 0

    @classmethod
    def discover_variables(cls, required_vars: set[str], enable_caching: bool = True) -> dict[str, Any]:
        """
        Discover variables from the calling scope with enhanced caching.

        Args:
            required_vars: Set of variable names to find
            enable_caching: Whether to use caching for performance

        Returns:
            Dictionary mapping variable names to variable instances
        """
        if not required_vars:
            return {}

        # Check cache first if enabled
        if enable_caching:
            cache_key = frozenset(required_vars)
            if cache_key in cls._scope_cache:
                cls._cache_hit_count += 1
                _logger.debug(f"Cache hit for variables: {required_vars}")
                return cls._scope_cache[cache_key]

            cls._cache_miss_count += 1

            # Clean cache if it gets too large (LRU-style)
            if len(cls._scope_cache) >= cls._max_scope_cache_size:
                # Remove oldest 25% of entries
                items_to_remove = len(cls._scope_cache) // 4
                for _ in range(items_to_remove):
                    cls._scope_cache.pop(next(iter(cls._scope_cache)))
                _logger.debug(f"Cleaned {items_to_remove} entries from scope cache")

        # Get the calling frame with caching
        frame = cls._get_cached_user_frame()
        if frame is None:
            _logger.debug("No user frame found")
            return {}

        try:
            discovered = cls._search_frame_for_variables(frame, required_vars)

            # Cache the result if caching is enabled and successful
            if enable_caching and required_vars:
                cache_key = frozenset(required_vars)
                cls._scope_cache[cache_key] = discovered
                _logger.debug(f"Cached discovery result for variables: {required_vars}")

            return discovered

        except Exception as e:
            _logger.warning(f"Error during variable discovery: {e}")
            return {}

    @classmethod
    def can_auto_evaluate(cls, expression: Any) -> tuple[bool, dict[str, Any]]:
        """
        Check if expression can be auto-evaluated from scope.

        Args:
            expression: Expression to check for auto-evaluation

        Returns:
            Tuple of (can_evaluate, discovered_variables)
        """
        try:
            # Use protocol-based checking instead of duck typing
            if not TypeRegistry.is_expression(expression):
                return False, {}

            required_vars = expression.get_variables()
            if not required_vars:
                return True, {}  # No variables needed, can evaluate

            discovered = cls.discover_variables(required_vars, enable_caching=True)

            # Check if all required variables are available and have values
            for var_name in required_vars:
                if var_name not in discovered:
                    _logger.debug(f"Variable '{var_name}' not found in scope")
                    return False, {}

                var = discovered[var_name]
                if not hasattr(var, "quantity") or var.quantity is None:
                    _logger.debug(f"Variable '{var_name}' has no quantity")
                    return False, {}

            _logger.debug(f"Expression can be auto-evaluated with variables: {list(discovered.keys())}")
            return True, discovered

        except Exception as e:
            _logger.warning(f"Error during auto-evaluation check: {e}")
            return False, {}

    @classmethod
    def find_variables_in_scope(cls, filter_func=None) -> dict[str, Any]:
        """
        Find all UnifiedVariable instances in the calling scope.

        Args:
            filter_func: Optional function to filter variables (var) -> bool

        Returns:
            Dictionary mapping variable names/symbols to variable instances
        """
        frame = inspect.currentframe()
        if frame is None:
            _logger.warning("Unable to access current frame")
            return {}

        try:
            frame = cls._find_user_frame(frame)
            if frame is None:
                return {}

            discovered = {}

            # Search locals first
            for obj in frame.f_locals.values():
                if TypeRegistry.is_variable(obj):
                    if filter_func is None or filter_func(obj):
                        var_name = cls._get_variable_name(obj)
                        if var_name:
                            discovered[var_name] = obj

            # Search globals for remaining variables
            for obj in frame.f_globals.values():
                if TypeRegistry.is_variable(obj):
                    if filter_func is None or filter_func(obj):
                        var_name = cls._get_variable_name(obj)
                        if var_name and var_name not in discovered:
                            discovered[var_name] = obj

            return discovered

        finally:
            del frame

    @classmethod
    def _get_cached_user_frame(cls) -> Any | None:
        """
        Get user frame with caching to reduce repeated frame traversal.

        Returns:
            User frame or None if not found
        """
        # Get current frame for cache key generation
        current_frame = inspect.currentframe()
        if current_frame is None:
            return None

        try:
            # Create cache key based on frame signature
            frame_id = id(current_frame)

            # Check frame cache first
            if frame_id in cls._frame_cache:
                cached_frame = cls._frame_cache[frame_id]
                if cached_frame is not None:
                    return cached_frame

            # Clean frame cache if too large
            if len(cls._frame_cache) >= cls._max_frame_cache_size:
                cls._frame_cache.clear()

            # Find user frame using optimized search
            user_frame = cls._find_user_frame_optimized(current_frame)

            # Cache the result
            cls._frame_cache[frame_id] = user_frame
            return user_frame

        finally:
            del current_frame

    @classmethod
    def _find_user_frame_optimized(cls, current_frame: Any) -> Any | None:
        """
        Optimized frame search with precompiled patterns.

        Args:
            current_frame: Starting frame

        Returns:
            User frame or None if not found within depth limit
        """
        frame = current_frame
        depth = 0

        # Pre-compiled sets for faster lookups
        internal_file_endings = frozenset(["expression.py", "equation.py", "nodes.py", "scope_discovery.py", "expression_quantity.py", "unified_variable.py", "field_qnty.py"])
        internal_function_names = frozenset(["__str__", "__repr__", "_can_auto_evaluate", "_discover_variables_from_scope", "solve_from", "evaluate"])

        while frame and depth < cls._max_search_depth:
            code = frame.f_code
            filename = code.co_filename
            function_name = code.co_name

            # Fast check: is this frame internal?
            is_internal = any(filename.endswith(ending) for ending in internal_file_endings) or function_name in internal_function_names

            if not is_internal:
                _logger.debug(f"Found user frame at depth {depth}: {filename}:{function_name}")
                return frame

            frame = frame.f_back
            depth += 1

        _logger.debug(f"No user frame found within {cls._max_search_depth} levels")
        return None

    @classmethod
    def _find_user_frame(cls, current_frame: Any) -> Any | None:
        """
        Legacy method for backward compatibility.
        """
        return cls._find_user_frame_optimized(current_frame)

    @classmethod
    def _search_frame_for_variables(cls, frame: Any, required_vars: set[str]) -> dict[str, Any]:
        """
        Search a specific frame for required variables.

        Args:
            frame: Frame to search
            required_vars: Set of variable names to find

        Returns:
            Dictionary of found variables
        """
        discovered = {}

        # Search locals first (most common case)
        local_vars = frame.f_locals
        for var_name in required_vars:
            # Direct lookup first (fastest)
            if var_name in local_vars:
                obj = local_vars[var_name]
                if TypeRegistry.is_variable(obj):
                    discovered[var_name] = obj
                    continue

        # Get globals once for reuse
        global_vars = frame.f_globals

        # Search globals only for remaining variables
        if len(discovered) < len(required_vars):
            remaining_vars = required_vars - discovered.keys()
            for var_name in remaining_vars:
                if var_name in global_vars:
                    obj = global_vars[var_name]
                    if TypeRegistry.is_variable(obj):
                        discovered[var_name] = obj

        # Search by symbol/name for remaining variables (optimized)
        if len(discovered) < len(required_vars):
            remaining_vars = required_vars - discovered.keys()
            cls._search_by_symbol_name_optimized(local_vars, global_vars, remaining_vars, discovered)

        _logger.debug(f"Found {len(discovered)} of {len(required_vars)} required variables")
        return discovered

    @classmethod
    def _search_by_symbol_name_optimized(cls, local_vars: dict, global_vars: dict, remaining_vars: set[str], discovered: dict[str, Any]) -> None:
        """Optimized search for variables by their symbol/name attribute."""
        # Convert to list once to avoid repeated set operations
        remaining_list = list(remaining_vars)

        # Search locals by symbol/name with early termination
        for obj in local_vars.values():
            if not remaining_list:  # Check list instead of set
                break
            if TypeRegistry.is_variable(obj):
                obj_name = cls._get_variable_name(obj)
                if obj_name in remaining_vars:  # Still check set for O(1) lookup
                    discovered[obj_name] = obj
                    remaining_list.remove(obj_name)
                    remaining_vars.remove(obj_name)

        # Search globals by symbol/name if still needed
        if remaining_list:
            for obj in global_vars.values():
                if not remaining_list:
                    break
                if TypeRegistry.is_variable(obj):
                    obj_name = cls._get_variable_name(obj)
                    if obj_name in remaining_vars:
                        discovered[obj_name] = obj
                        remaining_list.remove(obj_name)
                        remaining_vars.remove(obj_name)

    @classmethod
    def _search_by_symbol_name(cls, local_vars: dict, global_vars: dict, remaining_vars: set[str], discovered: dict[str, Any]) -> None:
        """Legacy method for backward compatibility."""
        cls._search_by_symbol_name_optimized(local_vars, global_vars, remaining_vars, discovered)

    @classmethod
    def _get_variable_name(cls, var) -> str | None:
        """
        Get the name/symbol to use for a variable with caching.

        Args:
            var: Variable instance

        Returns:
            Variable name/symbol or None if not available
        """
        var_id = id(var)

        # Check cache first
        if var_id in cls._variable_name_cache:
            return cls._variable_name_cache[var_id]

        try:
            # Prefer symbol over name for equation solving
            name = var.symbol if var.symbol else var.name

            # Cache the result
            cls._variable_name_cache[var_id] = name
            return name
        except (AttributeError, TypeError):
            cls._variable_name_cache[var_id] = None
            return None

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all caches for testing or memory management."""
        cls._scope_cache.clear()
        cls._frame_cache.clear()
        cls._variable_name_cache.clear()
        cls._cache_hit_count = 0
        cls._cache_miss_count = 0
        TypeRegistry.clear_cache()
        _logger.debug("Cleared all scope discovery caches")

    @classmethod
    def get_cache_stats(cls) -> dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = cls._cache_hit_count + cls._cache_miss_count
        hit_rate = (cls._cache_hit_count / total_requests * 100) if total_requests > 0 else 0

        return {
            "scope_cache_size": len(cls._scope_cache),
            "frame_cache_size": len(cls._frame_cache),
            "variable_name_cache_size": len(cls._variable_name_cache),
            "cache_hits": cls._cache_hit_count,
            "cache_misses": cls._cache_miss_count,
            "hit_rate_percent": round(hit_rate, 2),
        }

    @classmethod
    def set_max_depth(cls, depth: int) -> None:
        """Set maximum search depth for scope discovery."""
        if depth > 0:
            cls._max_search_depth = depth
            _logger.debug(f"Set max search depth to {depth}")
        else:
            raise ValueError("Depth must be positive")

    @classmethod
    def enable_debug_logging(cls) -> None:
        """Enable debug logging for scope discovery operations."""
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    @classmethod
    def disable_debug_logging(cls) -> None:
        """Disable debug logging for scope discovery operations."""
        logging.getLogger(__name__).setLevel(logging.WARNING)


# Convenience function for backward compatibility
def discover_variables_from_scope(required_vars: set[str]) -> dict[str, Any]:
    """
    Convenience function to discover variables from scope.

    Args:
        required_vars: Set of variable names to find

    Returns:
        Dictionary mapping variable names to variable instances
    """
    return ScopeDiscoveryService.discover_variables(required_vars)
