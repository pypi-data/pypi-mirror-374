"""
Dimension Signatures
====================

Immutable dimension signatures for ultra-fast dimensional analysis using prime number encoding.

This file contains the core DimensionSignature class that provides zero-cost dimensional
compatibility checking through compile-time type system integration.
"""

from dataclasses import dataclass
from typing import ClassVar, final

from .base import BaseDimension


@final
@dataclass(frozen=True, slots=True)
class DimensionSignature:
    """Immutable dimension signature for zero-cost dimensional analysis."""

    # Store as bit pattern for ultra-fast comparison
    _signature: int | float = 1

    # Instance cache for interning common dimensions
    _INSTANCE_CACHE: ClassVar[dict[int | float, "DimensionSignature"]] = {}

    # Maximum cache size to prevent memory issues
    _MAX_CACHE_SIZE: ClassVar[int] = 100

    def __new__(cls, signature: int | float = 1):
        """Optimized constructor with instance interning and validation."""
        # Input validation
        if not isinstance(signature, int | float):
            raise TypeError(f"Signature must be int or float, got {type(signature)}")
        if signature <= 0:
            raise ValueError(f"Signature must be positive, got {signature}")

        if signature in cls._INSTANCE_CACHE:
            return cls._INSTANCE_CACHE[signature]

        instance = object.__new__(cls)

        # Cache common signatures with size limit
        if len(cls._INSTANCE_CACHE) < cls._MAX_CACHE_SIZE:
            cls._INSTANCE_CACHE[signature] = instance

        return instance

    @classmethod
    def create(cls, length: int = 0, mass: int = 0, time: int = 0, current: int = 0, temp: int = 0, amount: int = 0, luminosity: int = 0):
        """Create dimension from exponents with efficient computation."""
        # Fast path for dimensionless
        if not any([length, mass, time, current, temp, amount, luminosity]):
            return cls(1)

        # Compute signature using tuple of (base, exponent) pairs for efficiency
        signature = 1.0
        dimensions = [
            (BaseDimension.LENGTH, length),
            (BaseDimension.MASS, mass),
            (BaseDimension.TIME, time),
            (BaseDimension.CURRENT, current),
            (BaseDimension.TEMPERATURE, temp),
            (BaseDimension.AMOUNT, amount),
            (BaseDimension.LUMINOSITY, luminosity),
        ]

        for base, exponent in dimensions:
            if exponent != 0:
                signature *= base**exponent

        return cls(signature)

    def __mul__(self, other: "DimensionSignature") -> "DimensionSignature":
        """Multiply dimensions."""
        if not isinstance(other, DimensionSignature):
            raise TypeError(f"Cannot multiply DimensionSignature with {type(other)}")
        return DimensionSignature(self._signature * other._signature)

    def __truediv__(self, other: "DimensionSignature") -> "DimensionSignature":
        """Divide dimensions."""
        if not isinstance(other, DimensionSignature):
            raise TypeError(f"Cannot divide DimensionSignature by {type(other)}")
        return DimensionSignature(self._signature / other._signature)

    def __pow__(self, power: int | float) -> "DimensionSignature":
        """Raise dimension to a power."""
        if not isinstance(power, int | float):
            raise TypeError(f"Power must be int or float, got {type(power)}")
        if power == 1:
            return self
        if power == 0:
            return DimensionSignature(1)
        return DimensionSignature(self._signature**power)

    def is_compatible(self, other: "DimensionSignature") -> bool:
        """Check dimensional compatibility."""
        if not isinstance(other, DimensionSignature):
            return False
        return self._signature == other._signature

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if self is other:
            return True
        return isinstance(other, DimensionSignature) and self._signature == other._signature

    def __hash__(self) -> int:
        """Hash based on signature."""
        return hash(self._signature)
