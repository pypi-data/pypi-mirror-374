"""
Unit System
===========

Unit definitions, constants and registry for the high-performance unit system.
"""

from dataclasses import dataclass

from ..dimensions import DimensionSignature
from .prefixes import SIPrefix, StandardPrefixes


@dataclass(frozen=True, slots=True)
class UnitDefinition:
    """Immutable unit definition for the unit system."""

    name: str
    symbol: str
    dimension: DimensionSignature
    si_factor: float
    si_offset: float = 0.0
    base_unit_name: str | None = None  # Base unit without prefix
    prefix: SIPrefix | None = None  # SI prefix if applicable

    @classmethod
    def with_prefix(cls, base_def: "UnitDefinition", prefix: SIPrefix) -> "UnitDefinition":
        """Create a new unit definition with an SI prefix."""
        return cls(
            name=prefix.apply_to_name(base_def.name),
            symbol=prefix.apply_to_symbol(base_def.symbol),
            dimension=base_def.dimension,
            si_factor=base_def.si_factor * prefix.factor,
            si_offset=base_def.si_offset,
            base_unit_name=base_def.name,
            prefix=prefix,
        )


class UnitConstant:
    """Unit constant that provides type safety."""

    __slots__ = ("definition", "name", "symbol", "dimension", "si_factor", "_hash_cache")

    def __init__(self, definition: UnitDefinition):
        self.definition = definition
        self.name = definition.name
        self.symbol = definition.symbol
        self.dimension = definition.dimension
        self.si_factor = definition.si_factor
        self._hash_cache = hash(self.name)

    def __str__(self) -> str:
        return self.symbol

    def __eq__(self, other) -> bool:
        """Equality check for unit constants."""
        return isinstance(other, UnitConstant) and self.name == other.name

    def __hash__(self) -> int:
        """Enable unit constants as dictionary keys."""
        return self._hash_cache


class Registry:
    """Unit registry with pre-computed conversion tables."""

    __slots__ = ("units", "conversion_table", "dimensional_groups", "_finalized", "base_units", "prefixable_units", "_conversion_cache", "_dimension_cache")

    def __init__(self):
        self.units: dict[str, UnitDefinition] = {}
        self.conversion_table: dict[tuple[str, str], float] = {}  # (from_unit, to_unit) -> factor
        self.dimensional_groups: dict[int | float, list[UnitDefinition]] = {}
        self._finalized = False
        self.base_units: dict[str, UnitDefinition] = {}  # Track base units for prefix generation
        self.prefixable_units: set[str] = set()  # Track which units can have prefixes
        # Cache for frequently used conversions
        self._conversion_cache: dict[tuple[str, str], float] = {}
        # Cache for common dimension mappings
        self._dimension_cache: dict[int | float, UnitConstant] = {}

    def register_unit(self, unit_def: UnitDefinition) -> None:
        """Register a single unit definition."""
        if self._finalized:
            raise RuntimeError("Cannot register units after registry is finalized")

        self.units[unit_def.name] = unit_def

        # Group by dimension
        dim_sig = unit_def.dimension._signature
        if dim_sig in self.dimensional_groups:
            self.dimensional_groups[dim_sig].append(unit_def)
        else:
            self.dimensional_groups[dim_sig] = [unit_def]

    def register_with_prefixes(self, unit_def: UnitDefinition, prefixes: list[StandardPrefixes] | None = None) -> None:
        """
        Register a unit and automatically generate prefixed variants.

        Args:
            unit_def: The base unit definition
            prefixes: List of StandardPrefixes enum values to apply. If None, uses common prefixes.
        """
        if self._finalized:
            raise RuntimeError("Cannot register units after registry is finalized")

        # Register base unit
        self.register_unit(unit_def)
        self.base_units[unit_def.name] = unit_def
        self.prefixable_units.add(unit_def.name)

        # Generate and register prefixed variants
        if prefixes:
            for prefix_enum in prefixes:
                prefix = prefix_enum.value
                if prefix.name:  # Skip NONE prefix (empty name)
                    prefixed_unit = UnitDefinition.with_prefix(unit_def, prefix)
                    self.register_unit(prefixed_unit)

    def finalize_registration(self) -> None:
        """Called after all units registered to precompute conversions."""
        if not self._finalized:
            self._precompute_conversions()
            self._finalized = True

    def _precompute_conversions(self) -> None:
        """Pre-compute all unit conversions for fast lookup."""
        self.conversion_table.clear()
        self._conversion_cache.clear()

        for group in self.dimensional_groups.values():
            if len(group) <= 1:
                continue  # Skip groups with single units

            # Compute conversion factors for all unit pairs
            for from_unit in group:
                for to_unit in group:
                    if from_unit != to_unit:
                        factor = from_unit.si_factor / to_unit.si_factor
                        self.conversion_table[(from_unit.name, to_unit.name)] = factor

    def convert(self, value: float, from_unit: UnitConstant, to_unit: UnitConstant) -> float:
        """Convert a value between units with optimized lookups."""
        # ULTRA-FAST PATH: Same unit - no conversion needed (most common case)
        if from_unit.name == to_unit.name:
            return value

        # OPTIMIZATION: Extract names once to avoid repeated attribute access
        from_name = from_unit.name
        to_name = to_unit.name
        key = (from_name, to_name)

        # STREAMLINED CACHE: Direct dictionary access with batched operations
        conversion_cache = self._conversion_cache
        if key in conversion_cache:
            return value * conversion_cache[key]

        # OPTIMIZED LOOKUP: Direct table access
        conversion_table = self.conversion_table
        if key in conversion_table:
            factor = conversion_table[key]
            # Cache frequently used conversions - direct assignment for speed
            if len(conversion_cache) < 50:
                conversion_cache[key] = factor
            return value * factor

        # FAST FALLBACK: Direct SI factor calculation with caching
        from_si = from_unit.si_factor
        to_si = to_unit.si_factor
        factor = from_si / to_si
        if len(conversion_cache) < 50:
            conversion_cache[key] = factor
        return value * factor


# Global unit registry
registry = Registry()
