"""
High-Performance Quantity and Variables
========================================

FastQuantity class and type-safe variables optimized for engineering calculations
with dimensional safety.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Self, TypeVar

from ..generated.dimensions import (
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
from ..generated.dimensions import (
    ENERGY_HEAT_WORK as ENERGY,
)
from ..generated.units import AreaUnits, DimensionlessUnits, LengthUnits, PressureUnits, VolumeUnits
from ..units.registry import UnitConstant, UnitDefinition, registry

if TYPE_CHECKING:
    from ..problem.variables import VariablesMixin

# TypeVar for generic dimensional types
DimensionType = TypeVar("DimensionType", bound="Quantity")


# Removed object pool system - benchmarking showed it was counter-productive
# Simple cache for small integer values only (most common case)
_SMALL_INTEGER_CACHE: dict[tuple[int, str], Quantity] = {}

# Pre-computed error message templates to eliminate f-string overhead
ERROR_TEMPLATES = {
    "incompatible_add": "Cannot add {} and {}",
    "incompatible_subtract": "Cannot subtract {} from {}",
    "incompatible_dimension": "Unit {} incompatible with expected dimension",
    "unit_not_found": "Unit '{}' not found for {}. Available units: {}",
    "unknown_function": "Unknown function: {}",
    "incompatible_comparison": "Cannot compare incompatible dimensions",
}

# Cache for multiplication/division results - keyed by dimension signature pairs
_MULTIPLICATION_CACHE = {}
_DIVISION_CACHE = {}


# Pre-initialize common dimension cache for performance
def _initialize_dimension_cache():
    """Initialize dimension cache at module load to avoid runtime checks."""
    if not registry._dimension_cache:
        registry._dimension_cache = {
            DIMENSIONLESS._signature: DimensionlessUnits.dimensionless,
            LENGTH._signature: LengthUnits.millimeter,
            PRESSURE._signature: PressureUnits.Pa,
            AREA._signature: AreaUnits.square_millimeter,
            VOLUME._signature: VolumeUnits.cubic_millimeter,  # mm³
            FORCE._signature: UnitConstant(UnitDefinition("newton", "N", FORCE, 1.0)),
            ENERGY._signature: UnitConstant(UnitDefinition("joule", "J", ENERGY, 1.0)),
            SURFACE_TENSION._signature: UnitConstant(UnitDefinition("newton_per_meter", "N/m", SURFACE_TENSION, 1.0)),
            ENERGY_PER_UNIT_AREA._signature: UnitConstant(UnitDefinition("joule_per_square_meter", "J/m²", ENERGY_PER_UNIT_AREA, 1.0)),
        }

    # Pre-populate multiplication cache with comprehensive engineering combinations
    global _MULTIPLICATION_CACHE, _DIVISION_CACHE

    # Create basic unit constants for common results
    force_unit = UnitConstant(UnitDefinition("newton", "N", FORCE, 1.0))
    energy_unit = UnitConstant(UnitDefinition("joule", "J", ENERGY, 1.0))

    _MULTIPLICATION_CACHE = {
        # Basic geometric combinations
        (LENGTH._signature, LENGTH._signature): AreaUnits.square_millimeter,
        (LENGTH._signature, AREA._signature): VolumeUnits.cubic_millimeter,
        (AREA._signature, LENGTH._signature): VolumeUnits.cubic_millimeter,
        # Force and pressure combinations
        (PRESSURE._signature, AREA._signature): force_unit,
        (AREA._signature, PRESSURE._signature): force_unit,
        # Energy combinations
        (FORCE._signature, LENGTH._signature): energy_unit,
        (LENGTH._signature, FORCE._signature): energy_unit,
    }

    _DIVISION_CACHE = {
        # Basic geometric divisions
        (AREA._signature, LENGTH._signature): LengthUnits.millimeter,
        (VOLUME._signature, AREA._signature): LengthUnits.millimeter,
        (VOLUME._signature, LENGTH._signature): AreaUnits.square_millimeter,
        # Force and pressure divisions
        (FORCE._signature, AREA._signature): PressureUnits.Pa,
        # Energy divisions
        (ENERGY._signature, FORCE._signature): LengthUnits.meter,
        (ENERGY._signature, LENGTH._signature): force_unit,
    }


class TypeSafeSetter:
    """Basic type-safe setter that accepts compatible units."""

    def __init__(self, variable: TypeSafeVariable, value: float):
        self.variable = variable
        self.value = value

    def with_unit(self, unit: UnitConstant) -> TypeSafeVariable:
        """Set with type-safe unit constant."""
        if not self.variable.expected_dimension.is_compatible(unit.dimension):
            raise TypeError(ERROR_TEMPLATES["incompatible_dimension"].format(unit.name))

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
        # Only cache small integers (most common case in engineering)
        if isinstance(value, int | float) and -10 <= value <= 10 and value == int(value):
            cache_key = (int(value), unit.name)
            if cache_key in _SMALL_INTEGER_CACHE:
                return _SMALL_INTEGER_CACHE[cache_key]
            
            # Create and cache if under limit
            if len(_SMALL_INTEGER_CACHE) < 100:  # Small cache limit
                obj = cls(float(value), unit)
                _SMALL_INTEGER_CACHE[cache_key] = obj
                return obj
        
        # Regular creation for everything else
        return cls(value, unit)

    def __str__(self) -> str:
        # Optimized string representation (caching removed for simplicity)
        return f"{self.value} {self.unit.symbol}"

    def __repr__(self) -> str:
        return f"FastQuantity({self.value}, {self.unit.name})"

    # Ultra-fast arithmetic with dimensional checking
    def __add__(self, other: Quantity) -> Quantity:
        # Optimized addition with early exit and bulk operations
        self_sig, other_sig = self._dimension_sig, other._dimension_sig
        if self_sig != other_sig:
            raise ValueError(ERROR_TEMPLATES["incompatible_add"].format(self.unit.name, other.unit.name))

        # Ultra-fast path: compare unit names directly
        if self.unit.name == other.unit.name:
            return Quantity(self.value + other.value, self.unit)

        # Convert using cached SI factors (avoid repeated attribute access)
        self_si, other_si = self._si_factor, other._si_factor
        other_value = other.value * other_si / self_si
        return Quantity(self.value + other_value, self.unit)

    def __sub__(self, other: Quantity) -> Quantity:
        # Optimized subtraction with early exit and bulk operations
        self_sig, other_sig = self._dimension_sig, other._dimension_sig
        if self_sig != other_sig:
            raise ValueError(ERROR_TEMPLATES["incompatible_subtract"].format(other.unit.name, self.unit.name))

        # Ultra-fast path: compare unit names directly
        if self.unit.name == other.unit.name:
            return Quantity(self.value - other.value, self.unit)

        # Convert using cached SI factors (avoid repeated attribute access)
        self_si, other_si = self._si_factor, other._si_factor
        other_value = other.value * other_si / self_si
        return Quantity(self.value - other_value, self.unit)

    def __mul__(self, other: Quantity | float | int | TypeSafeVariable) -> Quantity:
        # Fast path for numeric types - use type() for speed
        if isinstance(other, int | float):
            return Quantity(self.value * other, self.unit)

        # Handle TypeSafeVariable objects by using their quantity
        # Check for quantity attribute without importing (duck typing)
        if hasattr(other, "quantity") and getattr(other, "quantity", None) is not None:
            other = other.quantity  # type: ignore

        # Type narrowing: at this point other should be FastQuantity
        if not isinstance(other, Quantity):
            raise TypeError(f"Expected FastQuantity, got {type(other)}")

        # Check multiplication cache first
        cache_key = (self._dimension_sig, other._dimension_sig)
        if cache_key in _MULTIPLICATION_CACHE:
            result_unit = _MULTIPLICATION_CACHE[cache_key]
            # Fast computation with cached unit
            result_si_value = (self.value * self._si_factor) * (other.value * other._si_factor)
            return Quantity(result_si_value / result_unit.si_factor, result_unit)

        # Fast dimensional analysis using cached signatures
        result_dimension_sig = self._dimension_sig * other._dimension_sig

        # Use cached SI factors for conversion (bulk operations)
        self_si, other_si = self._si_factor, other._si_factor
        result_si_value = (self.value * self_si) * (other.value * other_si)

        # Fast path for common dimension combinations
        result_unit = self._find_result_unit_fast(result_dimension_sig)
        result_value = result_si_value / result_unit.si_factor

        # Cache the result for future use (limit cache size)
        if len(_MULTIPLICATION_CACHE) < 100:
            _MULTIPLICATION_CACHE[cache_key] = result_unit

        return Quantity(result_value, result_unit)

    def __rmul__(self, other: float | int) -> Quantity:
        """Reverse multiplication for cases like 2 * quantity."""
        if isinstance(other, int | float):
            return Quantity(other * self.value, self.unit)
        return NotImplemented

    def __truediv__(self, other: Quantity | float | int | TypeSafeVariable) -> Quantity:
        # Fast path for numeric types - use type() for speed
        if isinstance(other, int | float):
            return Quantity(self.value / other, self.unit)

        # Handle TypeSafeVariable objects by using their quantity
        if hasattr(other, "quantity") and getattr(other, "quantity", None) is not None:
            other = other.quantity  # type: ignore

        # Type narrowing: at this point other should be FastQuantity
        if not isinstance(other, Quantity):
            raise TypeError(f"Expected FastQuantity, got {type(other)}")

        # Check division cache first
        cache_key = (self._dimension_sig, other._dimension_sig)
        if cache_key in _DIVISION_CACHE:
            result_unit = _DIVISION_CACHE[cache_key]
            # Fast computation with cached unit
            result_si_value = (self.value * self._si_factor) / (other.value * other._si_factor)
            return Quantity(result_si_value / result_unit.si_factor, result_unit)

        # Fast dimensional analysis using cached signatures
        result_dimension_sig = self._dimension_sig / other._dimension_sig

        # Use cached SI factors for conversion (bulk operations)
        self_si, other_si = self._si_factor, other._si_factor
        result_si_value = (self.value * self_si) / (other.value * other_si)

        # Fast path for common dimension combinations
        result_unit = self._find_result_unit_fast(result_dimension_sig)
        result_value = result_si_value / result_unit.si_factor

        # Cache the result for future use (limit cache size)
        if len(_DIVISION_CACHE) < 100:
            _DIVISION_CACHE[cache_key] = result_unit

        return Quantity(result_value, result_unit)

    def _find_result_unit_fast(self, result_dimension_sig: int | float) -> UnitConstant:
        """Ultra-fast unit finding using pre-cached dimension signatures."""

        # O(1) lookup for common dimensions (cache initialized at module load)
        if result_dimension_sig in registry._dimension_cache:
            return registry._dimension_cache[result_dimension_sig]

        # For rare combined dimensions, create SI base unit with descriptive name
        result_dimension = DimensionSignature(result_dimension_sig)

        # Create descriptive name based on dimensional analysis
        si_name = self._create_si_unit_name(result_dimension)
        si_symbol = self._create_si_unit_symbol(result_dimension)

        temp_unit = UnitDefinition(name=si_name, symbol=si_symbol, dimension=result_dimension, si_factor=1.0)
        result_unit = UnitConstant(temp_unit)

        # Cache for future use
        registry._dimension_cache[result_dimension_sig] = result_unit
        return result_unit

    def _create_si_unit_name(self, dimension: DimensionSignature) -> str:
        """Create descriptive SI unit name based on dimensional analysis."""
        # For now, return a generic SI unit name. In the future, this could be enhanced
        # to parse the dimension signature and create descriptive names like "newton_per_meter"
        return f"si_derived_unit_{abs(hash(dimension._signature)) % 10000}"

    def _create_si_unit_symbol(self, dimension: DimensionSignature) -> str:
        """Create SI unit symbol based on dimensional analysis."""
        # For complex units, return descriptive symbol based on common engineering units
        # Use dimension signature for unique symbol generation
        return f"SI_{abs(hash(dimension._signature)) % 1000}"

    def _find_result_unit(self, result_dimension: DimensionSignature) -> UnitConstant:
        """Legacy method - kept for compatibility."""
        return self._find_result_unit_fast(result_dimension._signature)

    # Ultra-fast comparisons
    def __lt__(self, other: Quantity) -> bool:
        # Optimized comparison with bulk operations
        if self._dimension_sig != other._dimension_sig:
            raise ValueError(ERROR_TEMPLATES["incompatible_comparison"])

        # Fast path for same units (use name comparison for speed)
        if self.unit.name == other.unit.name:
            return self.value < other.value

        # Convert using cached SI factors (bulk assignment)
        self_si, other_si = self._si_factor, other._si_factor
        return self.value < (other.value * other_si / self_si)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Quantity):
            return False
        if self._dimension_sig != other._dimension_sig:
            return False

        # Fast path for same units (use name comparison)
        if self.unit.name == other.unit.name:
            return abs(self.value - other.value) < 1e-10

        # Convert using cached SI factors (bulk assignment)
        self_si, other_si = self._si_factor, other._si_factor
        return abs(self.value - (other.value * other_si / self_si)) < 1e-10

    def to(self, target_unit: UnitConstant) -> Quantity:
        """Ultra-fast unit conversion with optimized same-unit check."""
        # Ultra-fast same unit check using name comparison
        if self.unit.name == target_unit.name:
            return Quantity(self.value, target_unit)

        # Direct SI factor conversion - avoid registry lookup
        converted_value = self.value * self._si_factor / target_unit.si_factor
        return Quantity(converted_value, target_unit)


class TypeSafeVariable(Generic[DimensionType]):
    """
    Base class for type-safe variables with dimensional checking.

    This is a simple data container without dependencies on expressions or equations.
    Mathematical operations are added by subclasses or mixins.
    """

    # Class attribute defining which setter to use - subclasses can override
    _setter_class = TypeSafeSetter

    def __init__(self, name: str, expected_dimension, is_known: bool = True):
        self.name = name
        self.symbol: str | None = None  # Will be set by EngineeringProblem to attribute name
        self.expected_dimension = expected_dimension
        self.quantity: Quantity | None = None
        self.is_known = is_known
        self._parent_problem: VariablesMixin | None = None  # Set by EngineeringProblem when added
        self.validation_checks: list = []  # List for validation checks

    def set(self, value: float):
        """Create a setter for this variable using the class-specific setter type."""
        return self._setter_class(self, value)

    @property
    def unknown(self) -> Self:
        """Mark this variable as unknown using fluent API."""
        self.is_known = False
        return self

    @property
    def known(self) -> Self:
        """Mark this variable as known using fluent API."""
        self.is_known = True
        return self

    def update(self, value=None, unit=None, quantity=None, is_known=None):
        """Update variable properties flexibly."""
        if quantity is not None:
            self.quantity = quantity
        elif value is not None:
            # Create setter and call the appropriate unit property
            setter = self.set(value)
            if unit is not None:
                # Try to find the unit property on the setter
                if hasattr(setter, unit):
                    getattr(setter, unit)
                elif hasattr(setter, unit + "s"):  # Handle singular/plural
                    getattr(setter, unit + "s")
                elif unit.endswith("s") and hasattr(setter, unit[:-1]):  # Handle plural to singular
                    getattr(setter, unit[:-1])
                else:
                    raise ValueError(f"Unit '{unit}' not found for {self.__class__.__name__}")
            else:
                # If no unit specified, we can't automatically choose a unit
                # The caller should specify either a unit or a quantity
                raise ValueError("Must specify either 'unit' with 'value' or provide 'quantity' directly")
        if is_known is not None:
            self.is_known = is_known
        return self  # For method chaining

    def mark_known(self, quantity=None):
        """Mark variable as known, optionally updating its value."""
        self.is_known = True
        if quantity is not None:
            self.quantity = quantity
        return self  # For method chaining

    def mark_unknown(self):
        """Mark variable as unknown."""
        self.is_known = False
        return self  # For method chaining

    def __str__(self):
        return f"{self.name}: {self.quantity}" if self.quantity else f"{self.name}: unset"


# Initialize dimension cache at module load for performance
_initialize_dimension_cache()
