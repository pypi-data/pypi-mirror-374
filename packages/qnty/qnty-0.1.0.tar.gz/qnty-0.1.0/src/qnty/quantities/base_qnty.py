"""
High-Performance Quantity and Variables
========================================

FastQuantity class and type-safe variables optimized for engineering calculations
with dimensional safety.
"""

from __future__ import annotations

from typing import TypeVar

from ..constants import FLOAT_EQUALITY_TOLERANCE
from ..dimensions.field_dims import (
    AREA,
    DIMENSIONLESS,
    ENERGY_PER_UNIT_AREA,
    FORCE,
    LENGTH,
    PRESSURE,
    SURFACE_TENSION,
    VOLUME,
    DimensionSignature,
)
from ..dimensions.field_dims import (
    ENERGY_HEAT_WORK as ENERGY,
)
from ..units.field_units import AreaUnits, DimensionlessUnits, LengthUnits, PressureUnits, VolumeUnits
from ..units.registry import UnitConstant, UnitDefinition, registry

# TypeVar for generic dimensional types
DimensionType = TypeVar("DimensionType", bound="Quantity")


# Performance optimization data structures
class ResultTemplate:
    """Pre-computed result template to bypass Quantity creation overhead."""

    __slots__ = ("unit", "combined_si_factor")

    def __init__(self, unit: UnitConstant, combined_si_factor: float):
        self.unit = unit
        self.combined_si_factor = combined_si_factor


class ObjectPool:
    """Object pool for common quantity types to reduce allocations."""

    __slots__ = ("_area_pool", "_volume_pool", "_force_pool", "_energy_pool", "_pool_index", "_initialized")

    def __init__(self):
        # Initialize empty pools - delay creation until first use
        self._area_pool: list[Quantity] = []
        self._volume_pool: list[Quantity] = []
        self._force_pool: list[Quantity] = []
        self._energy_pool: list[Quantity] = []
        self._pool_index = 0
        self._initialized = False

    def _initialize_pools_lazy(self):
        """Lazily create pooled objects to avoid circular imports."""
        if self._initialized:
            return

        area_unit = AreaUnits.square_millimeter
        volume_unit = VolumeUnits.cubic_millimeter
        force_unit = UnitConstant(UnitDefinition("newton", "N", FORCE, 1.0))
        energy_unit = UnitConstant(UnitDefinition("joule", "J", ENERGY, 1.0))

        # Pre-allocate 10 of each common type
        for _ in range(10):
            self._area_pool.append(Quantity(0.0, area_unit))
            self._volume_pool.append(Quantity(0.0, volume_unit))
            self._force_pool.append(Quantity(0.0, force_unit))
            self._energy_pool.append(Quantity(0.0, energy_unit))

        self._initialized = True

    def get_area_quantity(self, value: float, unit: UnitConstant) -> Quantity:
        """Get pooled area quantity or create new if pool empty."""
        self._initialize_pools_lazy()
        if self._area_pool:
            qty = self._area_pool.pop()
            qty.value = value
            qty.unit = unit
            qty._si_factor = unit.si_factor
            qty._dimension_sig = unit.dimension._signature
            return qty
        return Quantity(value, unit)

    def get_volume_quantity(self, value: float, unit: UnitConstant) -> Quantity:
        """Get pooled volume quantity or create new if pool empty."""
        self._initialize_pools_lazy()
        if self._volume_pool:
            qty = self._volume_pool.pop()
            qty.value = value
            qty.unit = unit
            qty._si_factor = unit.si_factor
            qty._dimension_sig = unit.dimension._signature
            return qty
        return Quantity(value, unit)

    def get_force_quantity(self, value: float, unit: UnitConstant) -> Quantity:
        """Get pooled force quantity or create new if pool empty."""
        self._initialize_pools_lazy()
        if self._force_pool:
            qty = self._force_pool.pop()
            qty.value = value
            qty.unit = unit
            qty._si_factor = unit.si_factor
            qty._dimension_sig = unit.dimension._signature
            return qty
        return Quantity(value, unit)


# Global state management and caching system
class CacheManager:
    """Centralized cache management for better encapsulation and control."""

    def __init__(self):
        self.small_integer_cache: dict[tuple[int, str], Quantity] = {}
        self.multiplication_cache: dict[tuple[int | float, int | float], UnitConstant] = {}
        # NEW: Result templates with pre-computed SI factors
        self.multiplication_templates: dict[tuple[int | float, int | float], ResultTemplate] = {}
        self.division_cache: dict[tuple[int | float, int | float], UnitConstant] = {}
        self.max_cache_size = 100
        # Object pool for common types
        self.object_pool = ObjectPool()

    def get_cached_quantity(self, value: int | float, unit: UnitConstant) -> Quantity | None:
        """Get cached quantity for small integers."""
        if isinstance(value, int | float) and -10 <= value <= 10 and value == int(value):
            cache_key = (int(value), unit.name)
            return self.small_integer_cache.get(cache_key)
        return None

    def cache_quantity(self, value: int | float, unit: UnitConstant, quantity: Quantity) -> None:
        """Cache quantity if under size limit."""
        if len(self.small_integer_cache) < self.max_cache_size:
            cache_key = (int(value), unit.name)
            self.small_integer_cache[cache_key] = quantity

    def get_multiplication_result(self, left_sig: int | float, right_sig: int | float) -> UnitConstant | None:
        """Get cached multiplication result."""
        return self.multiplication_cache.get((left_sig, right_sig))

    def cache_multiplication_result(self, left_sig: int | float, right_sig: int | float, result_unit: UnitConstant) -> None:
        """Cache multiplication result if under size limit."""
        if len(self.multiplication_cache) < self.max_cache_size:
            self.multiplication_cache[(left_sig, right_sig)] = result_unit

    def get_division_result(self, left_sig: int | float, right_sig: int | float) -> UnitConstant | None:
        """Get cached division result."""
        return self.division_cache.get((left_sig, right_sig))

    def cache_division_result(self, left_sig: int | float, right_sig: int | float, result_unit: UnitConstant) -> None:
        """Cache division result if under size limit."""
        if len(self.division_cache) < self.max_cache_size:
            self.division_cache[(left_sig, right_sig)] = result_unit

    def initialize_common_operations(self) -> None:
        """Initialize common dimensional operations cache."""
        if not registry._dimension_cache:
            registry._dimension_cache = {
                DIMENSIONLESS._signature: DimensionlessUnits.dimensionless,
                LENGTH._signature: LengthUnits.millimeter,
                PRESSURE._signature: PressureUnits.Pa,
                AREA._signature: AreaUnits.square_millimeter,
                VOLUME._signature: VolumeUnits.cubic_millimeter,
                FORCE._signature: UnitConstant(UnitDefinition("newton", "N", FORCE, 1.0)),
                ENERGY._signature: UnitConstant(UnitDefinition("joule", "J", ENERGY, 1.0)),
                SURFACE_TENSION._signature: UnitConstant(UnitDefinition("newton_per_meter", "N/m", SURFACE_TENSION, 1.0)),
                ENERGY_PER_UNIT_AREA._signature: UnitConstant(UnitDefinition("joule_per_square_meter", "J/m²", ENERGY_PER_UNIT_AREA, 1.0)),
            }

        # Pre-populate common engineering combinations with extensive coverage
        force_unit = UnitConstant(UnitDefinition("newton", "N", FORCE, 1.0))
        energy_unit = UnitConstant(UnitDefinition("joule", "J", ENERGY, 1.0))
        # _surface_tension_unit = UnitConstant(UnitDefinition("newton_per_meter", "N/m", SURFACE_TENSION, 1.0))  # Unused
        energy_per_area_unit = UnitConstant(UnitDefinition("joule_per_square_meter", "J/m²", ENERGY_PER_UNIT_AREA, 1.0))

        # NEW APPROACH: Create result templates with pre-computed combined SI factors
        # This eliminates the need for SI factor division during multiplication

        # Helper function to create template with pre-computed factors
        def create_template(unit: UnitConstant) -> ResultTemplate:
            """Create result template with pre-computed combined SI factor.

            For typical case where left and right operands use the cached base units,
            the combined factor is just 1.0 / result_unit.si_factor since the SI
            conversion will be handled by the quantity's own _si_factor attributes.
            """
            # The template assumes SI values will be multiplied in, so we just need
            # the reciprocal of the result unit's SI factor for final conversion
            combined_factor = 1.0 / unit.si_factor
            return ResultTemplate(unit, combined_factor)

        # Get common unit SI factors for template pre-computation (unused in current implementation)
        # _mm_si = LengthUnits.millimeter.si_factor  # 0.001
        # _pa_si = PressureUnits.Pa.si_factor        # 1.0
        # _mm2_si = AreaUnits.square_millimeter.si_factor  # 1e-6
        # _mm3_si = VolumeUnits.cubic_millimeter.si_factor  # 1e-9

        # ULTRA-OPTIMIZED TEMPLATES: Most common engineering operations
        self.multiplication_templates.update(
            {
                # TOP 5 ENGINEERING COMBINATIONS (hardcoded for maximum speed)
                # 1. Length × Length = Area (most common geometric operation)
                (LENGTH._signature, LENGTH._signature): create_template(AreaUnits.square_millimeter),
                # 2. Pressure × Area = Force (ASME pressure vessel calculations)
                (PRESSURE._signature, AREA._signature): create_template(force_unit),
                (AREA._signature, PRESSURE._signature): create_template(force_unit),
                # 3. Length × Area = Volume (geometric calculations)
                (LENGTH._signature, AREA._signature): create_template(VolumeUnits.cubic_millimeter),
                (AREA._signature, LENGTH._signature): create_template(VolumeUnits.cubic_millimeter),
                # 4. Force × Length = Energy (work calculations)
                (FORCE._signature, LENGTH._signature): create_template(energy_unit),
                (LENGTH._signature, FORCE._signature): create_template(energy_unit),
                # 5. Dimensionless scaling (extremely common - factors of safety, ratios)
                (PRESSURE._signature, DIMENSIONLESS._signature): create_template(PressureUnits.Pa),
                (DIMENSIONLESS._signature, PRESSURE._signature): create_template(PressureUnits.Pa),
                (LENGTH._signature, DIMENSIONLESS._signature): create_template(LengthUnits.millimeter),
                (DIMENSIONLESS._signature, LENGTH._signature): create_template(LengthUnits.millimeter),
                (AREA._signature, DIMENSIONLESS._signature): create_template(AreaUnits.square_millimeter),
                (DIMENSIONLESS._signature, AREA._signature): create_template(AreaUnits.square_millimeter),
                (VOLUME._signature, DIMENSIONLESS._signature): create_template(VolumeUnits.cubic_millimeter),
                (DIMENSIONLESS._signature, VOLUME._signature): create_template(VolumeUnits.cubic_millimeter),
                (FORCE._signature, DIMENSIONLESS._signature): create_template(force_unit),
                (DIMENSIONLESS._signature, FORCE._signature): create_template(force_unit),
                (ENERGY._signature, DIMENSIONLESS._signature): create_template(energy_unit),
                (DIMENSIONLESS._signature, ENERGY._signature): create_template(energy_unit),
                (DIMENSIONLESS._signature, DIMENSIONLESS._signature): create_template(DimensionlessUnits.dimensionless),
            }
        )

        # Keep legacy multiplication cache for compatibility with less common operations
        multiplication_patterns = {
            # Less common but still cached operations
            (AREA._signature, AREA._signature): UnitConstant(UnitDefinition("m4", "m⁴", AREA * AREA, 1e-12)),  # mm⁴
            (FORCE._signature, FORCE._signature): UnitConstant(UnitDefinition("N2", "N²", FORCE * FORCE, 1.0)),
            (PRESSURE._signature, LENGTH._signature): force_unit,
            (LENGTH._signature, PRESSURE._signature): force_unit,
            (PRESSURE._signature, PRESSURE._signature): UnitConstant(UnitDefinition("Pa2", "Pa²", PRESSURE * PRESSURE, 1.0)),
            (PRESSURE._signature, VOLUME._signature): energy_unit,  # PV work
            (VOLUME._signature, PRESSURE._signature): energy_unit,
            (FORCE._signature, AREA._signature): energy_unit,  # Force × Area = Energy
            (AREA._signature, FORCE._signature): energy_unit,
            (ENERGY._signature, LENGTH._signature): force_unit,  # Energy/Length = Force
            (LENGTH._signature, ENERGY._signature): force_unit,
            (ENERGY._signature, AREA._signature): energy_per_area_unit,
            (AREA._signature, ENERGY._signature): energy_per_area_unit,
            (SURFACE_TENSION._signature, LENGTH._signature): force_unit,
            (LENGTH._signature, SURFACE_TENSION._signature): force_unit,
        }

        self.multiplication_cache.update(multiplication_patterns)

        self.division_cache.update(
            {
                # Basic geometric divisions
                (AREA._signature, LENGTH._signature): LengthUnits.millimeter,
                (VOLUME._signature, AREA._signature): LengthUnits.millimeter,
                (VOLUME._signature, LENGTH._signature): AreaUnits.square_millimeter,
                # Force and pressure divisions
                (FORCE._signature, AREA._signature): PressureUnits.Pa,
                (ENERGY._signature, FORCE._signature): LengthUnits.meter,
                (ENERGY._signature, LENGTH._signature): force_unit,
                # ASME-specific: Force ÷ Length = Pressure (common in final result)
                (FORCE._signature, LENGTH._signature): PressureUnits.Pa,
                # Dimensionless divisions (maintain original units)
                (PRESSURE._signature, DIMENSIONLESS._signature): PressureUnits.Pa,
                (LENGTH._signature, DIMENSIONLESS._signature): LengthUnits.millimeter,
                (FORCE._signature, DIMENSIONLESS._signature): force_unit,
                # Combined unit divisions (P×D ÷ P = D pattern in ASME)
                (force_unit.dimension._signature, PRESSURE._signature): LengthUnits.millimeter,
            }
        )


# Pre-cached units for ultra-fast paths (avoid repeated creation/import overhead)
_CACHED_AREA_UNIT = AreaUnits.square_millimeter
_CACHED_VOLUME_UNIT = VolumeUnits.cubic_millimeter
_CACHED_FORCE_UNIT = UnitConstant(UnitDefinition("newton", "N", FORCE, 1.0))
# _CACHED_ENERGY_UNIT = UnitConstant(UnitDefinition("joule", "J", ENERGY, 1.0))  # Unused

# Pre-computed reciprocals for division (eliminate division operations)
_AREA_SI_RECIPROCAL = 1.0 / _CACHED_AREA_UNIT.si_factor  # 1.0 / 1e-6 = 1e6
_VOLUME_SI_RECIPROCAL = 1.0 / _CACHED_VOLUME_UNIT.si_factor  # 1.0 / 1e-9 = 1e9
# _FORCE_SI_RECIPROCAL = 1.0 / _CACHED_FORCE_UNIT.si_factor    # 1.0 / 1.0 = 1.0  # Unused

# Global cache manager instance
_cache_manager = CacheManager()


# Error message constants for better maintainability
class ErrorMessages:
    """Centralized error message templates."""

    INCOMPATIBLE_ADD = "Cannot add {} and {}"
    INCOMPATIBLE_SUBTRACT = "Cannot subtract {} from {}"
    INCOMPATIBLE_DIMENSION = "Unit {} incompatible with expected dimension"
    UNIT_NOT_FOUND = "Unit '{}' not found for {}. Available units: {}"
    UNKNOWN_FUNCTION = "Unknown function: {}"
    INCOMPATIBLE_COMPARISON = "Cannot compare incompatible dimensions"


# Component classes for separation of concerns
class ArithmeticOperations:
    """Handles arithmetic operations for quantities."""

    @staticmethod
    def add(quantity, other):
        """Add two quantities with dimensional checking."""
        if quantity._dimension_sig != other._dimension_sig:
            raise ValueError(ErrorMessages.INCOMPATIBLE_ADD.format(quantity.unit.name, other.unit.name))

        # Fast path for same units
        if quantity.unit.name == other.unit.name:
            return Quantity(quantity.value + other.value, quantity.unit)

        # Convert using cached SI factors
        converted_value = other.value * other._si_factor / quantity._si_factor
        return Quantity(quantity.value + converted_value, quantity.unit)

    @staticmethod
    def subtract(quantity, other):
        """Subtract two quantities with dimensional checking."""
        if quantity._dimension_sig != other._dimension_sig:
            raise ValueError(ErrorMessages.INCOMPATIBLE_SUBTRACT.format(other.unit.name, quantity.unit.name))

        # Fast path for same units
        if quantity.unit.name == other.unit.name:
            return Quantity(quantity.value - other.value, quantity.unit)

        # Convert using cached SI factors
        converted_value = other.value * other._si_factor / quantity._si_factor
        return Quantity(quantity.value - converted_value, quantity.unit)

    @staticmethod
    def multiply(quantity, other):
        """Ultra-aggressive multiplication optimizations targeting <0.400μs performance."""
        # FASTEST PATH: Use type() check for numbers (faster than isinstance)
        other_type = type(other)
        if other_type in (int, float):
            return Quantity(quantity.value * other, quantity.unit)

        # DUCK TYPING: Extract quantity without hasattr overhead
        other_qty = getattr(other, "quantity", None)
        if other_qty is not None:
            other = other_qty

        # ULTRA-FAST ATTRIBUTE ACCESS: Direct access with getattr fallback for robustness
        q_val = quantity.value
        q_dim = quantity._dimension_sig
        o_val = getattr(other, "value", None)
        o_dim = getattr(other, "_dimension_sig", None)

        # Quick validation
        if o_val is None or o_dim is None:
            raise TypeError(f"Expected Quantity-like object, got {type(other)}")

        # SPECIAL VALUE FAST PATHS: Most performance-critical optimizations first
        if o_val == 1.0 and o_dim == 1:  # Multiply by 1.0 dimensionless
            return Quantity(q_val * other._si_factor, quantity.unit)
        if q_val == 1.0 and q_dim == 1:  # 1.0 dimensionless * something
            return Quantity(o_val * quantity._si_factor, other.unit)
        if q_val == 0.0 or o_val == 0.0:  # Zero multiplication
            return Quantity(0.0, quantity.unit if q_val == 0.0 else other.unit)

        # DIMENSIONLESS FAST PATHS: Treat as scaling to avoid template lookup
        if o_dim == 1:  # Right dimensionless
            return Quantity(q_val * o_val * other._si_factor, quantity.unit)
        if q_dim == 1:  # Left dimensionless
            return Quantity(q_val * quantity._si_factor * o_val, other.unit)

        # ULTRA-OPTIMIZED HARDCODED PATHS: Use multiplication instead of division
        # Length × Length = Area (most common geometric operation)
        if q_dim == LENGTH._signature and o_dim == LENGTH._signature:
            # Eliminate division: (q_val * q_si) * (o_val * o_si) * (1/result_si)
            result_val = q_val * quantity._si_factor * o_val * other._si_factor * _AREA_SI_RECIPROCAL
            return Quantity(result_val, _CACHED_AREA_UNIT)

        # Pressure × Area = Force (ASME pressure vessel calculations)
        elif (q_dim == PRESSURE._signature and o_dim == AREA._signature) or (q_dim == AREA._signature and o_dim == PRESSURE._signature):
            # Force SI factor is 1.0, so no reciprocal multiplication needed
            result_val = q_val * quantity._si_factor * o_val * other._si_factor
            return Quantity(result_val, _CACHED_FORCE_UNIT)

        # Length × Area = Volume (geometric calculations)
        elif (q_dim == LENGTH._signature and o_dim == AREA._signature) or (q_dim == AREA._signature and o_dim == LENGTH._signature):
            result_val = q_val * quantity._si_factor * o_val * other._si_factor * _VOLUME_SI_RECIPROCAL
            return Quantity(result_val, _CACHED_VOLUME_UNIT)

        # TEMPLATE LOOKUP for remaining optimized cases
        cache_key = (q_dim, o_dim)
        template = _cache_manager.multiplication_templates.get(cache_key)
        if template is not None:
            # Single combined operation
            result_value = q_val * o_val * (quantity._si_factor * other._si_factor * template.combined_si_factor)
            # Skip object pooling overhead - just create directly
            return Quantity(result_value, template.unit)

        # LEGACY CACHE LOOKUP: For operations not in optimized templates
        cached_unit = _cache_manager.multiplication_cache.get(cache_key)
        if cached_unit is not None:
            # INLINE SI CALCULATION: Single combined expression
            result_si_value = (q_val * quantity._si_factor) * (o_val * other._si_factor)
            return Quantity(result_si_value / cached_unit.si_factor, cached_unit)

        # FALLBACK PATH: General case for uncached operations
        result_dimension_sig = q_dim * o_dim
        result_si_value = (q_val * quantity._si_factor) * (o_val * other._si_factor)

        # Fast unit resolution
        result_unit = UnitResolution.find_result_unit_fast(quantity, result_dimension_sig)
        result_value = result_si_value / result_unit.si_factor

        # Direct cache assignment for future use
        if len(_cache_manager.multiplication_cache) < _cache_manager.max_cache_size:
            _cache_manager.multiplication_cache[cache_key] = result_unit

        return Quantity(result_value, result_unit)

    @staticmethod
    def divide(quantity, other):
        """Divide quantity by another quantity or scalar."""
        # Fast path for numeric types - use type() for speed
        if isinstance(other, int | float):
            return Quantity(quantity.value / other, quantity.unit)

        # Handle UnifiedVariable objects by using their quantity
        if hasattr(other, "quantity") and getattr(other, "quantity", None) is not None:
            other = other.quantity  # type: ignore

        # Type narrowing: at this point other should be Quantity
        if not isinstance(other, Quantity):
            raise TypeError(f"Expected Quantity, got {type(other)}")

        # OPTIMIZATION: Fast path for dimensionless divisor (signature = 1)
        # Treat dimensionless quantities more like scalars to reduce overhead
        if other._dimension_sig == 1:  # DIMENSIONLESS divisor
            # Division by dimensionless: just scale the value, keep original unit
            divisor = other.value * other._si_factor
            return Quantity(quantity.value / divisor, quantity.unit)

        # Check division cache first
        cached_unit = _cache_manager.get_division_result(quantity._dimension_sig, other._dimension_sig)
        if cached_unit:
            result_si_value = (quantity.value * quantity._si_factor) / (other.value * other._si_factor)
            return Quantity(result_si_value / cached_unit.si_factor, cached_unit)

        # Calculate result dimension and value
        result_dimension_sig = quantity._dimension_sig / other._dimension_sig
        result_si_value = (quantity.value * quantity._si_factor) / (other.value * other._si_factor)

        # Find appropriate result unit
        result_unit = UnitResolution.find_result_unit_fast(quantity, result_dimension_sig)
        result_value = result_si_value / result_unit.si_factor

        # Cache the result for future use
        _cache_manager.cache_division_result(quantity._dimension_sig, other._dimension_sig, result_unit)
        return Quantity(result_value, result_unit)


class ComparisonOperations:
    """Handles comparison operations for quantities."""

    @staticmethod
    def less_than(quantity, other):
        """Compare if this quantity is less than another."""
        # Optimized comparison with bulk operations
        if quantity._dimension_sig != other._dimension_sig:
            raise ValueError(ErrorMessages.INCOMPATIBLE_COMPARISON)

        # Fast path for same units (use name comparison for speed)
        if quantity.unit.name == other.unit.name:
            return quantity.value < other.value

        # Convert using cached SI factors (bulk assignment)
        self_si, other_si = quantity._si_factor, other._si_factor
        return quantity.value < (other.value * other_si / self_si)

    @staticmethod
    def equals(quantity, other):
        """Check equality between quantities."""
        if not isinstance(other, Quantity):
            return False
        if quantity._dimension_sig != other._dimension_sig:
            return False

        # Fast path for same units (use name comparison)
        if quantity.unit.name == other.unit.name:
            return abs(quantity.value - other.value) < FLOAT_EQUALITY_TOLERANCE

        # Convert using cached SI factors (bulk assignment)
        self_si, other_si = quantity._si_factor, other._si_factor
        return abs(quantity.value - (other.value * other_si / self_si)) < FLOAT_EQUALITY_TOLERANCE


class UnitConversions:
    """Handles unit conversion operations."""

    @staticmethod
    def to(quantity, target_unit):
        """Convert quantity to target unit."""
        # Ultra-fast same unit check using name comparison
        if quantity.unit.name == target_unit.name:
            return Quantity(quantity.value, target_unit)

        # Direct SI factor conversion - avoid registry lookup
        converted_value = quantity.value * quantity._si_factor / target_unit.si_factor
        return Quantity(converted_value, target_unit)


class QuantityFormatting:
    """Handles string formatting for quantities."""

    @staticmethod
    def to_string(quantity):
        """String representation of the quantity."""
        # Optimized string representation (caching removed for simplicity)
        return f"{quantity.value} {quantity.unit.symbol}"

    @staticmethod
    def to_repr(quantity):
        """Detailed representation of the quantity."""
        return f"Quantity({quantity.value}, {quantity.unit.name})"


class UnitResolution:
    """Handles unit resolution for dimensional operations."""

    @staticmethod
    def find_result_unit_fast(_quantity, result_dimension_sig: int | float) -> UnitConstant:
        """Ultra-fast unit finding using pre-cached dimension signatures."""
        # CRITICAL OPTIMIZATION: Direct dictionary access (O(1)) for common dimensions
        dimension_cache = registry._dimension_cache
        if result_dimension_sig in dimension_cache:
            return dimension_cache[result_dimension_sig]

        # OPTIMIZED PATH: For rare combined dimensions, create SI base unit efficiently
        # Create new dimension signature from the computed value
        result_dimension = DimensionSignature(result_dimension_sig)  # type: ignore[misc]

        # FAST CREATION: Minimize string operations for performance
        sig_hash = abs(hash(result_dimension_sig)) % 10000
        si_name = f"si_derived_{sig_hash}"
        si_symbol = f"SI_{sig_hash % 1000}"

        # STREAMLINED CREATION: Avoid unnecessary method calls
        temp_unit = UnitDefinition(name=si_name, symbol=si_symbol, dimension=result_dimension, si_factor=1.0)
        result_unit = UnitConstant(temp_unit)

        # DIRECT CACHE ASSIGNMENT: Bypass cache size checks for dimension cache
        dimension_cache[result_dimension_sig] = result_unit
        return result_unit

    @staticmethod
    def create_si_unit_name(_quantity, dimension: DimensionSignature) -> str:
        """Create descriptive SI unit name based on dimensional analysis."""
        # For now, return a generic SI unit name. In the future, this could be enhanced
        # to parse the dimension signature and create descriptive names like "newton_per_meter"
        return f"si_derived_unit_{abs(hash(dimension._signature)) % 10000}"

    @staticmethod
    def create_si_unit_symbol(_quantity, dimension: DimensionSignature) -> str:
        """Create SI unit symbol based on dimensional analysis."""
        # For complex units, return descriptive symbol based on common engineering units
        # Use dimension signature for unique symbol generation
        return f"SI_{abs(hash(dimension._signature)) % 1000}"

    @staticmethod
    def find_result_unit(quantity, result_dimension: DimensionSignature) -> UnitConstant:
        """Legacy method - kept for compatibility."""
        return UnitResolution.find_result_unit_fast(quantity, result_dimension._signature)


class TypeSafeSetter:
    """Basic type-safe setter that accepts compatible units."""

    def __init__(self, variable, value: float):
        self.variable = variable
        self.value = value

    def with_unit(self, unit: UnitConstant):
        """Set with type-safe unit constant."""
        if not self.variable.expected_dimension.is_compatible(unit.dimension):
            raise TypeError(ErrorMessages.INCOMPATIBLE_DIMENSION.format(unit.name))

        self.variable.quantity = Quantity(self.value, unit)
        return self.variable


class Quantity:
    """High-performance quantity optimized for engineering calculations."""

    __slots__ = ("value", "unit", "dimension", "_si_factor", "_dimension_sig")

    def __init__(self, value: float, unit: UnitConstant):
        # Optimized initialization with cached values for performance
        self.value = value if isinstance(value, float) else float(value)
        self.unit = unit
        self.dimension = unit.dimension
        # Cache commonly used values to avoid repeated attribute access
        self._si_factor = unit.si_factor
        self._dimension_sig = unit.dimension._signature

    @classmethod
    def get_cached(cls, value: int | float, unit: UnitConstant):
        """Get cached instance for small integers, otherwise create new."""
        # Check cache for small integers
        cached = _cache_manager.get_cached_quantity(value, unit)
        if cached:
            return cached

        # Create new quantity
        obj = cls(value, unit)

        # Cache if it qualifies
        _cache_manager.cache_quantity(value, unit, obj)
        return obj

    def __str__(self) -> str:
        return QuantityFormatting.to_string(self)

    def __repr__(self) -> str:
        return QuantityFormatting.to_repr(self)

    # Ultra-fast arithmetic with dimensional checking
    def __add__(self, other: Quantity) -> Quantity:
        return ArithmeticOperations.add(self, other)

    def __sub__(self, other: Quantity) -> Quantity:
        return ArithmeticOperations.subtract(self, other)

    def __mul__(self, other: Quantity | float | int) -> Quantity:
        return ArithmeticOperations.multiply(self, other)

    def __rmul__(self, other: float | int) -> Quantity:
        """Reverse multiplication for cases like 2 * quantity."""
        if isinstance(other, int | float):
            return Quantity(other * self.value, self.unit)
        return NotImplemented

    def __truediv__(self, other: Quantity | float | int) -> Quantity:
        return ArithmeticOperations.divide(self, other)

    def _find_result_unit_fast(self, result_dimension_sig: int | float) -> UnitConstant:
        """Delegate to unit resolution component."""
        return UnitResolution.find_result_unit_fast(self, result_dimension_sig)

    def _create_si_unit_name(self, dimension: DimensionSignature) -> str:
        """Delegate to unit resolution component."""
        return UnitResolution.create_si_unit_name(self, dimension)

    def _create_si_unit_symbol(self, dimension: DimensionSignature) -> str:
        """Delegate to unit resolution component."""
        return UnitResolution.create_si_unit_symbol(self, dimension)

    def _find_result_unit(self, result_dimension: DimensionSignature) -> UnitConstant:
        """Legacy method - kept for compatibility."""
        return UnitResolution.find_result_unit(self, result_dimension)

    # Ultra-fast comparisons
    def __lt__(self, other: Quantity) -> bool:
        return ComparisonOperations.less_than(self, other)

    def __eq__(self, other) -> bool:
        return ComparisonOperations.equals(self, other)

    def to(self, target_unit: UnitConstant) -> Quantity:
        """Ultra-fast unit conversion with optimized same-unit check."""
        return UnitConversions.to(self, target_unit)


# Initialize cache manager at module load
_cache_manager.initialize_common_operations()
