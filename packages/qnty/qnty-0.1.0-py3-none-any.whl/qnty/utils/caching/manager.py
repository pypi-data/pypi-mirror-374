"""
Unified Cache Management System
===============================

Centralized caching infrastructure for all qnty operations, providing
consistent cache policies, monitoring, and memory management.
"""

from __future__ import annotations

from typing import Any, TypeVar
from weakref import WeakValueDictionary

# Type variables for cache keys and values
K = TypeVar("K")
V = TypeVar("V")


class CacheStats:
    """Statistics tracking for cache performance analysis."""

    def __init__(self, name: str):
        self.name = name
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def hit(self):
        """Record a cache hit."""
        self.hits += 1

    def miss(self):
        """Record a cache miss."""
        self.misses += 1

    def evict(self):
        """Record a cache eviction."""
        self.evictions += 1

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def __str__(self) -> str:
        return f"{self.name}: {self.hits}/{self.hits + self.misses} hits ({self.hit_rate:.1%}), {self.evictions} evictions"


class UnifiedCacheManager:
    """
    Centralized cache manager for all qnty operations.

    Provides consistent caching policies, memory management, and performance
    monitoring across all library components.
    """

    # Cache size limits (tuned based on typical usage patterns)
    UNIT_PROPERTY_CACHE_SIZE = 200
    AVAILABLE_UNITS_CACHE_SIZE = 50
    EXPRESSION_CACHE_SIZE = 300
    TYPE_CHECK_CACHE_SIZE = 100
    DIMENSIONLESS_CACHE_SIZE = 50
    DIMENSION_SIGNATURE_CACHE_SIZE = 500
    VALIDATION_CACHE_SIZE = 150
    SMALL_INTEGER_CACHE_SIZE = 100
    MULTIPLICATION_CACHE_SIZE = 100
    DIVISION_CACHE_SIZE = 100

    def __init__(self):
        # Core caches with different policies
        self._unit_property_cache: dict[tuple[type, str], str | None] = {}
        self._available_units_cache: dict[type, list[str]] = {}
        self._expression_result_cache: dict[str, Any] = {}
        self._type_check_cache: dict[type, bool] = {}
        self._dimensionless_cache: dict[float, Any] = {}
        self._validation_cache: dict[tuple[type, str], bool] = {}

        # Quantity-specific caches
        self._small_integer_cache: dict[tuple[int, str], Any] = {}
        self._multiplication_cache: dict[tuple[Any, Any], Any] = {}
        self._division_cache: dict[tuple[Any, Any], Any] = {}
        self._dimension_cache: dict[Any, Any] = {}

        # Weak reference caches for object-based keys
        self._dimension_signature_cache: WeakValueDictionary = WeakValueDictionary()

        # Statistics tracking
        self._stats = {
            "unit_property": CacheStats("Unit Property"),
            "available_units": CacheStats("Available Units"),
            "expression_result": CacheStats("Expression Result"),
            "type_check": CacheStats("Type Check"),
            "dimensionless": CacheStats("Dimensionless"),
            "validation": CacheStats("Validation"),
            "small_integer": CacheStats("Small Integer"),
            "multiplication": CacheStats("Multiplication"),
            "division": CacheStats("Division"),
            "dimension": CacheStats("Dimension"),
        }

    # Unit Property Cache Operations
    def get_unit_property(self, setter_class: type, unit: str) -> str | None:
        """Get cached unit property mapping."""
        key = (setter_class, unit)
        if key in self._unit_property_cache:
            self._stats["unit_property"].hit()
            return self._unit_property_cache[key]

        self._stats["unit_property"].miss()
        return None

    def cache_unit_property(self, setter_class: type, unit: str, property_name: str | None) -> None:
        """Cache unit property mapping."""
        key = (setter_class, unit)
        self._unit_property_cache[key] = property_name

        # Enforce cache size limit
        if len(self._unit_property_cache) > self.UNIT_PROPERTY_CACHE_SIZE:
            self._evict_oldest("unit_property", self._unit_property_cache, self.UNIT_PROPERTY_CACHE_SIZE // 4)

    # Available Units Cache Operations
    def get_available_units(self, setter_class: type) -> list[str] | None:
        """Get cached available units for a setter class."""
        if setter_class in self._available_units_cache:
            self._stats["available_units"].hit()
            return self._available_units_cache[setter_class]

        self._stats["available_units"].miss()
        return None

    def cache_available_units(self, setter_class: type, units: list[str]) -> None:
        """Cache available units for a setter class."""
        self._available_units_cache[setter_class] = units

        if len(self._available_units_cache) > self.AVAILABLE_UNITS_CACHE_SIZE:
            self._evict_oldest("available_units", self._available_units_cache, self.AVAILABLE_UNITS_CACHE_SIZE // 4)

    # Type Check Cache Operations
    def get_type_check(self, obj_type: type) -> bool | None:
        """Get cached type check result."""
        if obj_type in self._type_check_cache:
            self._stats["type_check"].hit()
            return self._type_check_cache[obj_type]

        self._stats["type_check"].miss()
        return None

    def cache_type_check(self, obj_type: type, result: bool) -> None:
        """Cache type check result."""
        self._type_check_cache[obj_type] = result

        if len(self._type_check_cache) > self.TYPE_CHECK_CACHE_SIZE:
            self._evict_oldest("type_check", self._type_check_cache, self.TYPE_CHECK_CACHE_SIZE // 4)

    # Dimensionless Quantity Cache Operations
    def get_dimensionless_quantity(self, value: float) -> Any | None:
        """Get cached dimensionless quantity."""
        if value in self._dimensionless_cache:
            self._stats["dimensionless"].hit()
            return self._dimensionless_cache[value]

        self._stats["dimensionless"].miss()
        return None

    def cache_dimensionless_quantity(self, value: float, quantity: Any) -> None:
        """Cache dimensionless quantity for common values."""
        # Only cache small integer/simple values to prevent memory bloat
        if -10 <= value <= 10 and (value == int(value) or value in [0.5, 0.25, 0.75]):
            self._dimensionless_cache[value] = quantity

            if len(self._dimensionless_cache) > self.DIMENSIONLESS_CACHE_SIZE:
                self._evict_oldest("dimensionless", self._dimensionless_cache, self.DIMENSIONLESS_CACHE_SIZE // 4)

    # Validation Cache Operations
    def get_validation_result(self, setter_class: type, unit: str) -> bool | None:
        """Get cached validation result."""
        key = (setter_class, unit)
        if key in self._validation_cache:
            self._stats["validation"].hit()
            return self._validation_cache[key]

        self._stats["validation"].miss()
        return None

    def cache_validation_result(self, setter_class: type, unit: str, is_valid: bool) -> None:
        """Cache validation result."""
        key = (setter_class, unit)
        self._validation_cache[key] = is_valid

        if len(self._validation_cache) > self.VALIDATION_CACHE_SIZE:
            self._evict_oldest("validation", self._validation_cache, self.VALIDATION_CACHE_SIZE // 4)

    # Expression Result Cache Operations (for future use)
    def get_expression_result(self, expression_key: str) -> Any | None:
        """Get cached expression evaluation result."""
        if expression_key in self._expression_result_cache:
            self._stats["expression_result"].hit()
            return self._expression_result_cache[expression_key]

        self._stats["expression_result"].miss()
        return None

    def cache_expression_result(self, expression_key: str, result: Any) -> None:
        """Cache expression evaluation result."""
        self._expression_result_cache[expression_key] = result

        if len(self._expression_result_cache) > self.EXPRESSION_CACHE_SIZE:
            self._evict_oldest("expression_result", self._expression_result_cache, self.EXPRESSION_CACHE_SIZE // 4)

    # Quantity-specific Cache Operations
    def get_cached_quantity(self, value: int | float, unit_name: str) -> Any | None:
        """Get cached quantity for small integers."""
        if isinstance(value, int | float) and -10 <= value <= 10 and value == int(value):
            key = (int(value), unit_name)
            if key in self._small_integer_cache:
                self._stats["small_integer"].hit()
                return self._small_integer_cache[key]

        self._stats["small_integer"].miss()
        return None

    def cache_quantity(self, value: int | float, unit_name: str, quantity: Any) -> None:
        """Cache quantity if it's a small integer."""
        if isinstance(value, int | float) and -10 <= value <= 10 and value == int(value):
            key = (int(value), unit_name)
            self._small_integer_cache[key] = quantity

            if len(self._small_integer_cache) > self.SMALL_INTEGER_CACHE_SIZE:
                self._evict_oldest("small_integer", self._small_integer_cache, self.SMALL_INTEGER_CACHE_SIZE // 4)

    def get_multiplication_result(self, left_sig: Any, right_sig: Any) -> Any | None:
        """Get cached multiplication result."""
        key = (left_sig, right_sig)
        if key in self._multiplication_cache:
            self._stats["multiplication"].hit()
            return self._multiplication_cache[key]

        self._stats["multiplication"].miss()
        return None

    def cache_multiplication_result(self, left_sig: Any, right_sig: Any, result_unit: Any) -> None:
        """Cache multiplication result."""
        key = (left_sig, right_sig)
        self._multiplication_cache[key] = result_unit

        if len(self._multiplication_cache) > self.MULTIPLICATION_CACHE_SIZE:
            self._evict_oldest("multiplication", self._multiplication_cache, self.MULTIPLICATION_CACHE_SIZE // 4)

    def get_division_result(self, left_sig: Any, right_sig: Any) -> Any | None:
        """Get cached division result."""
        key = (left_sig, right_sig)
        if key in self._division_cache:
            self._stats["division"].hit()
            return self._division_cache[key]

        self._stats["division"].miss()
        return None

    def cache_division_result(self, left_sig: Any, right_sig: Any, result_unit: Any) -> None:
        """Cache division result."""
        key = (left_sig, right_sig)
        self._division_cache[key] = result_unit

        if len(self._division_cache) > self.DIVISION_CACHE_SIZE:
            self._evict_oldest("division", self._division_cache, self.DIVISION_CACHE_SIZE // 4)

    def get_dimension_unit(self, dimension_sig: Any) -> Any | None:
        """Get cached unit for dimension signature."""
        if dimension_sig in self._dimension_cache:
            self._stats["dimension"].hit()
            return self._dimension_cache[dimension_sig]

        self._stats["dimension"].miss()
        return None

    def cache_dimension_unit(self, dimension_sig: Any, unit: Any) -> None:
        """Cache unit for dimension signature."""
        self._dimension_cache[dimension_sig] = unit

    def initialize_dimension_cache(self, initial_mappings: dict[Any, Any]) -> None:
        """Initialize dimension cache with common mappings."""
        self._dimension_cache.update(initial_mappings)

    def initialize_operation_caches(self, multiplication_mappings: dict[tuple[Any, Any], Any], division_mappings: dict[tuple[Any, Any], Any]) -> None:
        """Initialize multiplication and division caches with common operations."""
        self._multiplication_cache.update(multiplication_mappings)
        self._division_cache.update(division_mappings)

    # Cache Management Operations
    def _evict_oldest(self, cache_name: str, cache_dict: dict, evict_count: int) -> None:
        """Evict oldest entries from cache."""
        # Simple FIFO eviction - remove first N items
        keys_to_remove = list(cache_dict.keys())[:evict_count]
        for key in keys_to_remove:
            del cache_dict[key]
            self._stats[cache_name].evict()

    def clear_cache(self, cache_name: str | None = None) -> None:
        """Clear specific cache or all caches."""
        if cache_name is None:
            # Clear all caches
            self._unit_property_cache.clear()
            self._available_units_cache.clear()
            self._expression_result_cache.clear()
            self._type_check_cache.clear()
            self._dimensionless_cache.clear()
            self._validation_cache.clear()
            self._dimension_signature_cache.clear()
            self._small_integer_cache.clear()
            self._multiplication_cache.clear()
            self._division_cache.clear()
            self._dimension_cache.clear()
        else:
            # Clear specific cache
            cache_map = {
                "unit_property": self._unit_property_cache,
                "available_units": self._available_units_cache,
                "expression_result": self._expression_result_cache,
                "type_check": self._type_check_cache,
                "dimensionless": self._dimensionless_cache,
                "validation": self._validation_cache,
                "small_integer": self._small_integer_cache,
                "multiplication": self._multiplication_cache,
                "division": self._division_cache,
                "dimension": self._dimension_cache,
            }
            if cache_name in cache_map:
                cache_map[cache_name].clear()

    def get_cache_stats(self) -> dict[str, CacheStats]:
        """Get performance statistics for all caches."""
        return self._stats.copy()

    def get_cache_sizes(self) -> dict[str, int]:
        """Get current size of all caches."""
        return {
            "unit_property": len(self._unit_property_cache),
            "available_units": len(self._available_units_cache),
            "expression_result": len(self._expression_result_cache),
            "type_check": len(self._type_check_cache),
            "dimensionless": len(self._dimensionless_cache),
            "validation": len(self._validation_cache),
            "dimension_signature": len(self._dimension_signature_cache),
            "small_integer": len(self._small_integer_cache),
            "multiplication": len(self._multiplication_cache),
            "division": len(self._division_cache),
            "dimension": len(self._dimension_cache),
        }

    def get_memory_usage_estimate(self) -> int:
        """Estimate memory usage in bytes (rough approximation)."""
        # Rough estimates based on typical key/value sizes
        estimates = {
            "unit_property": len(self._unit_property_cache) * 200,  # tuple keys + string values
            "available_units": len(self._available_units_cache) * 500,  # type keys + list values
            "expression_result": len(self._expression_result_cache) * 300,  # string keys + object values
            "type_check": len(self._type_check_cache) * 100,  # type keys + bool values
            "dimensionless": len(self._dimensionless_cache) * 150,  # float keys + quantity values
            "validation": len(self._validation_cache) * 150,  # tuple keys + bool values
            "small_integer": len(self._small_integer_cache) * 200,  # tuple keys + quantity values
            "multiplication": len(self._multiplication_cache) * 250,  # tuple keys + unit values
            "division": len(self._division_cache) * 250,  # tuple keys + unit values
            "dimension": len(self._dimension_cache) * 200,  # signature keys + unit values
        }
        return sum(estimates.values())


# Global cache manager instance
_cache_manager: UnifiedCacheManager | None = None


def get_cache_manager() -> UnifiedCacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = UnifiedCacheManager()
    return _cache_manager


# Convenience functions for common operations
def clear_all_caches() -> None:
    """Clear all caches - useful for testing and memory management."""
    get_cache_manager().clear_cache()


def get_cache_statistics() -> dict[str, str]:
    """Get formatted cache statistics."""
    stats = get_cache_manager().get_cache_stats()
    return {name: str(stat) for name, stat in stats.items()}


def get_memory_usage() -> str:
    """Get formatted memory usage estimate."""
    bytes_used = get_cache_manager().get_memory_usage_estimate()
    if bytes_used < 1024:
        return f"{bytes_used} bytes"
    elif bytes_used < 1024 * 1024:
        return f"{bytes_used / 1024:.1f} KB"
    else:
        return f"{bytes_used / (1024 * 1024):.1f} MB"
