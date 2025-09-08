"""
Base Dimensions
===============

Core base dimensions using prime number encoding for efficient dimensional analysis.

This file contains the fundamental dimensional primitives for the qnty system.
"""

from dataclasses import dataclass
from enum import IntEnum
from types import MappingProxyType


class BaseDimension(IntEnum):
    """Base dimensions as prime numbers for efficient bit operations."""

    DIMENSIONLESS = 1  # Must be 1 to act as identity
    LENGTH = 2
    MASS = 3
    TIME = 5
    CURRENT = 7
    TEMPERATURE = 11
    AMOUNT = 13
    LUMINOSITY = 17


@dataclass(frozen=True)
class DimensionConfig:
    """Immutable configuration for a base dimension."""
    prime: BaseDimension
    params: MappingProxyType[str, int]


# Immutable dimension symbols for display
DIMENSION_SYMBOLS: MappingProxyType[str, str] = MappingProxyType(
    {
        "length": "L",
        "mass": "M",
        "time": "T",
        "current": "A",
        "temp": "Θ",
        "amount": "N",
        "luminosity": "J",
    }
)

# Immutable base dimensions configuration for generators
BASE_DIMENSIONS: MappingProxyType[str, DimensionConfig] = MappingProxyType(
    {
        "LENGTH": DimensionConfig(
            BaseDimension.LENGTH,
            MappingProxyType({"length": 1})
        ),
        "MASS": DimensionConfig(
            BaseDimension.MASS,
            MappingProxyType({"mass": 1})
        ),
        "TIME": DimensionConfig(
            BaseDimension.TIME,
            MappingProxyType({"time": 1})
        ),
        "CURRENT": DimensionConfig(
            BaseDimension.CURRENT,
            MappingProxyType({"current": 1})
        ),
        "TEMPERATURE": DimensionConfig(
            BaseDimension.TEMPERATURE,
            MappingProxyType({"temp": 1})
        ),
        "AMOUNT": DimensionConfig(
            BaseDimension.AMOUNT,
            MappingProxyType({"amount": 1})
        ),
        "LUMINOSITY": DimensionConfig(
            BaseDimension.LUMINOSITY,
            MappingProxyType({"luminosity": 1})
        ),
        "DIMENSIONLESS": DimensionConfig(
            BaseDimension.DIMENSIONLESS,
            MappingProxyType({})
        ),
    }
)

# Immutable prime mapping for signature calculations
PRIME_MAP: MappingProxyType[str, BaseDimension] = MappingProxyType(
    {
        "length": BaseDimension.LENGTH,
        "mass": BaseDimension.MASS,
        "time": BaseDimension.TIME,
        "current": BaseDimension.CURRENT,
        "temp": BaseDimension.TEMPERATURE,
        "amount": BaseDimension.AMOUNT,
        "luminosity": BaseDimension.LUMINOSITY,
    }
)
