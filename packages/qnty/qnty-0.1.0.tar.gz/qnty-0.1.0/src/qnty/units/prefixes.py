"""
SI Prefix System
================

Standard SI prefixes for unit multiplication/division.
Provides systematic handling of metric prefixes like kilo-, milli-, micro-, etc.
"""

from dataclasses import dataclass
from enum import Enum

from ..constants.numerical import PREFIX_LOOKUP_MIN_TOLERANCE, PREFIX_LOOKUP_TOLERANCE


@dataclass(frozen=True, slots=True)
class SIPrefix:
    """
    Standard SI prefix definition.

    Attributes:
        name: Full prefix name (e.g., "kilo", "milli")
        symbol: Standard symbol (e.g., "k", "m")
        factor: Multiplication factor relative to base unit (e.g., 1000, 0.001)
    """

    name: str
    symbol: str
    factor: float

    def apply_to_name(self, base_name: str) -> str:
        """Apply prefix to a base unit name."""
        return self.name + base_name if self.name else base_name

    def apply_to_symbol(self, base_symbol: str) -> str:
        """Apply prefix to a base unit symbol."""
        return self.symbol + base_symbol if self.symbol else base_symbol


class StandardPrefixes(Enum):
    """
    Standard SI prefixes with their multiplication factors.

    From yotta (10^24) to yocto (10^-24).
    """

    # Larger prefixes (10^3 to 10^24)
    YOTTA = SIPrefix("yotta", "Y", 1e24)
    ZETTA = SIPrefix("zetta", "Z", 1e21)
    EXA = SIPrefix("exa", "E", 1e18)
    PETA = SIPrefix("peta", "P", 1e15)
    TERA = SIPrefix("tera", "T", 1e12)
    GIGA = SIPrefix("giga", "G", 1e9)
    MEGA = SIPrefix("mega", "M", 1e6)
    KILO = SIPrefix("kilo", "k", 1e3)
    HECTO = SIPrefix("hecto", "h", 1e2)
    DECA = SIPrefix("deca", "da", 1e1)

    # Base (no prefix)
    NONE = SIPrefix("", "", 1.0)

    # Smaller prefixes (10^-1 to 10^-24)
    DECI = SIPrefix("deci", "d", 1e-1)
    CENTI = SIPrefix("centi", "c", 1e-2)
    MILLI = SIPrefix("milli", "m", 1e-3)
    MICRO = SIPrefix("micro", "μ", 1e-6)
    NANO = SIPrefix("nano", "n", 1e-9)
    PICO = SIPrefix("pico", "p", 1e-12)
    FEMTO = SIPrefix("femto", "f", 1e-15)
    ATTO = SIPrefix("atto", "a", 1e-18)
    ZEPTO = SIPrefix("zepto", "z", 1e-21)
    YOCTO = SIPrefix("yocto", "y", 1e-24)


# Common prefix groups for different unit types
COMMON_LENGTH_PREFIXES: list[StandardPrefixes] = [
    StandardPrefixes.KILO,
    StandardPrefixes.CENTI,
    StandardPrefixes.MILLI,
    StandardPrefixes.MICRO,
    StandardPrefixes.NANO,
]

COMMON_MASS_PREFIXES: list[StandardPrefixes] = [
    StandardPrefixes.KILO,  # Note: kilogram is the SI base unit
    StandardPrefixes.MILLI,
    StandardPrefixes.MICRO,
]

COMMON_TIME_PREFIXES: list[StandardPrefixes] = [
    StandardPrefixes.MILLI,
    StandardPrefixes.MICRO,
    StandardPrefixes.NANO,
    StandardPrefixes.PICO,
]

COMMON_ELECTRIC_PREFIXES: list[StandardPrefixes] = [
    StandardPrefixes.KILO,
    StandardPrefixes.MILLI,
    StandardPrefixes.MICRO,
    StandardPrefixes.NANO,
    StandardPrefixes.PICO,
]

COMMON_ENERGY_PREFIXES: list[StandardPrefixes] = [
    StandardPrefixes.KILO,
    StandardPrefixes.MEGA,
    StandardPrefixes.GIGA,
]

COMMON_POWER_PREFIXES: list[StandardPrefixes] = [
    StandardPrefixes.KILO,
    StandardPrefixes.MEGA,
    StandardPrefixes.GIGA,
    StandardPrefixes.MILLI,
    StandardPrefixes.MICRO,
]

COMMON_PRESSURE_PREFIXES: list[StandardPrefixes] = [
    StandardPrefixes.KILO,
    StandardPrefixes.MEGA,
    StandardPrefixes.GIGA,
]


# Lookup dictionaries for fast prefix searches
_NAME_TO_PREFIX: dict[str, SIPrefix] = {}
_SYMBOL_TO_PREFIX: dict[str, SIPrefix] = {}
_FACTOR_TO_PREFIX: dict[float, SIPrefix] = {}


def _initialize_lookup_caches() -> None:
    """Initialize lookup caches for fast prefix lookups."""
    for prefix_enum in StandardPrefixes:
        prefix = prefix_enum.value
        _NAME_TO_PREFIX[prefix.name] = prefix
        _SYMBOL_TO_PREFIX[prefix.symbol] = prefix
        _FACTOR_TO_PREFIX[prefix.factor] = prefix


def get_prefix_by_name(name: str) -> SIPrefix | None:
    """Get a prefix by its name (e.g., 'kilo', 'milli')."""
    return _NAME_TO_PREFIX.get(name)


def get_prefix_by_symbol(symbol: str) -> SIPrefix | None:
    """Get a prefix by its symbol (e.g., 'k', 'm')."""
    return _SYMBOL_TO_PREFIX.get(symbol)


def get_prefix_by_factor(factor: float, tolerance: float = PREFIX_LOOKUP_TOLERANCE) -> SIPrefix | None:
    """Get a prefix by its multiplication factor."""
    # Check for exact match first
    if factor in _FACTOR_TO_PREFIX:
        return _FACTOR_TO_PREFIX[factor]

    # Search with tolerance if meaningful
    if tolerance > PREFIX_LOOKUP_MIN_TOLERANCE:
        for cached_factor, prefix in _FACTOR_TO_PREFIX.items():
            if abs(cached_factor - factor) < tolerance:
                return prefix
    return None


def extract_prefix_values(prefix_enums: list[StandardPrefixes]) -> list[SIPrefix]:
    """Extract SIPrefix values from StandardPrefixes enums."""
    return [prefix_enum.value for prefix_enum in prefix_enums]


# Units that should get automatic prefixes
PREFIXABLE_UNITS: dict[str, list[StandardPrefixes]] = {
    # Base SI units
    "meter": COMMON_LENGTH_PREFIXES,
    "gram": COMMON_MASS_PREFIXES,
    "second": COMMON_TIME_PREFIXES,
    "ampere": COMMON_ELECTRIC_PREFIXES,
    "kelvin": [],  # Temperature usually doesn't use prefixes
    "mole": [StandardPrefixes.MILLI, StandardPrefixes.MICRO],
    "candela": [],  # Luminous intensity rarely uses prefixes
    # Derived SI units
    "pascal": COMMON_PRESSURE_PREFIXES,
    "joule": COMMON_ENERGY_PREFIXES,
    "watt": COMMON_POWER_PREFIXES,
    "coulomb": COMMON_ELECTRIC_PREFIXES,
    "volt": COMMON_ELECTRIC_PREFIXES,
    "farad": [StandardPrefixes.MILLI, StandardPrefixes.MICRO, StandardPrefixes.NANO, StandardPrefixes.PICO],
    "ohm": [StandardPrefixes.KILO, StandardPrefixes.MEGA, StandardPrefixes.MILLI],
    "siemens": [StandardPrefixes.MILLI, StandardPrefixes.MICRO],
    "weber": [StandardPrefixes.MILLI, StandardPrefixes.MICRO],
    "tesla": [StandardPrefixes.MILLI, StandardPrefixes.MICRO, StandardPrefixes.NANO],
    "henry": [StandardPrefixes.MILLI, StandardPrefixes.MICRO, StandardPrefixes.NANO],
    "lumen": [],
    "lux": [],
    "becquerel": [StandardPrefixes.KILO, StandardPrefixes.MEGA, StandardPrefixes.GIGA],
    "gray": [StandardPrefixes.MILLI, StandardPrefixes.MICRO],
    "sievert": [StandardPrefixes.MILLI, StandardPrefixes.MICRO],
    "hertz": [StandardPrefixes.KILO, StandardPrefixes.MEGA, StandardPrefixes.GIGA],
    "newton": [StandardPrefixes.KILO, StandardPrefixes.MILLI],
    "bar": [StandardPrefixes.MILLI],  # Common non-SI unit
    "liter": [StandardPrefixes.MILLI, StandardPrefixes.MICRO],  # Common non-SI unit
}

# Initialize lookup caches on module load
_initialize_lookup_caches()
