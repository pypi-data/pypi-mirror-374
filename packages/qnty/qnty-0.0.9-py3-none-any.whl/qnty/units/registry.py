"""
Unit System
===========

Unit definitions, constants and registry for the high-performance unit system.
"""

from dataclasses import dataclass

from ..generated.dimensions import DimensionSignature
from .prefixes import SIPrefix, StandardPrefixes


@dataclass(frozen=True, slots=True)
class UnitDefinition:
    """Immutable unit definition optimized for performance."""
    name: str
    symbol: str
    dimension: DimensionSignature
    si_factor: float
    si_offset: float = 0.0
    base_unit_name: str | None = None  # Base unit without prefix
    prefix: SIPrefix | None = None      # SI prefix if applicable
    
    @classmethod
    def with_prefix(cls, base_def: 'UnitDefinition', prefix: SIPrefix) -> 'UnitDefinition':
        """Create a new unit definition with an SI prefix."""
        return cls(
            name=prefix.apply_to_name(base_def.name),
            symbol=prefix.apply_to_symbol(base_def.symbol),
            dimension=base_def.dimension,
            si_factor=base_def.si_factor * prefix.factor,
            si_offset=base_def.si_offset,
            base_unit_name=base_def.name,
            prefix=prefix
        )


class UnitConstant:
    """Unit constant that provides type safety and performance."""
    
    __slots__ = ('definition', 'name', 'symbol', 'dimension', 'si_factor', '_hash_cache')
    
    def __init__(self, definition: UnitDefinition):
        self.definition = definition
        self.name = definition.name
        self.symbol = definition.symbol
        self.dimension = definition.dimension
        self.si_factor = definition.si_factor
        # Cache expensive hash operation
        self._hash_cache = hash(self.name)
    
    def __str__(self):
        return self.symbol
    
    def __eq__(self, other) -> bool:
        """Ultra-fast equality check for unit constants."""
        # Fast path: check type first without isinstance() overhead
        return type(other) is UnitConstant and self.name == other.name
    
    def __hash__(self) -> int:
        """Enable unit constants as dictionary keys with cached hash."""
        return self._hash_cache


class Registry:
    """Ultra-fast registry with pre-computed conversion tables."""
    
    __slots__ = ('units', 'conversion_table', 'dimensional_groups', '_finalized',
                 'base_units', 'prefixable_units', '_conversion_cache', '_dimension_cache')
    
    def __init__(self):
        self.units: dict[str, UnitDefinition] = {}
        self.conversion_table: dict[tuple[str, str], float] = {}  # (from_unit, to_unit) -> factor
        self.dimensional_groups: dict[int | float, list[UnitDefinition]] = {}
        self._finalized = False
        self.base_units: dict[str, UnitDefinition] = {}  # Track base units for prefix generation
        self.prefixable_units: set[str] = set()  # Track which units can have prefixes
        # Small cache for frequently used conversions to reduce table lookups
        self._conversion_cache: dict[tuple[str, str], float] = {}
        # Cache for common dimension mappings (used by variable.py)
        self._dimension_cache: dict[int | float, UnitConstant] = {}

        # Registry starts empty - units are registered via register_all_units() in __init__.py
    
    
    def register_unit(self, unit_def: UnitDefinition) -> None:
        """Register a single unit definition."""
        if self._finalized:
            raise RuntimeError("Cannot register units after registry is finalized")
            
        self.units[unit_def.name] = unit_def
        
        # Group by dimension - optimized to avoid repeated signature access
        dim_sig = unit_def.dimension._signature
        try:
            self.dimensional_groups[dim_sig].append(unit_def)
        except KeyError:
            self.dimensional_groups[dim_sig] = [unit_def]
    
    def register_with_prefixes(
            self,
            unit_def: UnitDefinition,
            prefixes: list[StandardPrefixes] | None = None
        ) -> None:
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
        """Pre-compute all unit conversions for maximum speed with optimized algorithms."""
        self.conversion_table.clear()  # Clear existing conversions
        self._conversion_cache.clear()  # Clear cache
        
        for group in self.dimensional_groups.values():
            group_size = len(group)
            if group_size <= 1:
                continue  # Skip groups with single units
            
            # Ultra-optimized: pre-compute all factors and names in single pass
            unit_data = [(unit.name, unit.si_factor) for unit in group]
            
            # Vectorized approach: compute all combinations efficiently
            for i in range(group_size):
                from_name, from_si = unit_data[i]
                for j in range(group_size):
                    if i != j:  # Skip same unit conversion
                        to_name, to_si = unit_data[j]
                        # Pre-compute factor - avoid repeated division
                        factor = from_si / to_si
                        self.conversion_table[(from_name, to_name)] = factor
    
    def convert(self, value: float, from_unit: UnitConstant, to_unit: UnitConstant) -> float:
        """Ultra-fast conversion with optimized equality check and caching."""
        # Ultra-fast path: avoid expensive equality check by comparing names directly
        if from_unit.name == to_unit.name:
            return value
        
        key = (from_unit.name, to_unit.name)
        
        # Check small cache first for frequently used conversions
        try:
            return value * self._conversion_cache[key]
        except KeyError:
            pass
        
        # O(1) lookup for pre-computed conversions
        try:
            factor = self.conversion_table[key]
            # Cache frequently used conversions (keep cache small)
            if len(self._conversion_cache) < 50:
                self._conversion_cache[key] = factor
            return value * factor
        except KeyError:
            pass
        
        # Fallback (shouldn't happen for registered units)
        factor = from_unit.si_factor / to_unit.si_factor
        if len(self._conversion_cache) < 50:
            self._conversion_cache[key] = factor
        return value * factor


# Global high-performance registry
registry = Registry()
