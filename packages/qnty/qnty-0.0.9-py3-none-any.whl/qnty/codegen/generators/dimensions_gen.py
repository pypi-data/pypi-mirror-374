#!/usr/bin/env python3
"""
Dimension generator for qnty library.

This script generates the dimensions.py file from unit_data.json, creating
all necessary dimension signatures programmatically without hardcoding.
"""

import json
from pathlib import Path
from typing import Any

# Configuration
BASE_DIMENSIONS = {
    'LENGTH': {'prime': 2, 'params': {'length': 1}},
    'MASS': {'prime': 3, 'params': {'mass': 1}},
    'TIME': {'prime': 5, 'params': {'time': 1}},
    'CURRENT': {'prime': 7, 'params': {'current': 1}},
    'TEMPERATURE': {'prime': 11, 'params': {'temp': 1}},
    'AMOUNT': {'prime': 13, 'params': {'amount': 1}},
    'LUMINOSITY': {'prime': 17, 'params': {'luminosity': 1}},
    'DIMENSIONLESS': {'prime': 1, 'params': {}},
}

DIMENSION_SYMBOLS = {
    'length': 'L',
    'mass': 'M',
    'time': 'T',
    'current': 'A',
    'temp': 'Θ',
    'amount': 'N',
    'luminosity': 'J',
}

# All dimensions will be explicitly defined - no lazy loading needed


class DimensionGenerator:
    """Generator for dimensions.py file."""

    def __init__(self, data_path: Path, output_path: Path, out_dir: Path):
        """Initialize with paths."""
        self.data_path = data_path
        self.output_path = output_path
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

        # Load unit data
        with open(self.data_path, encoding='utf-8') as f:
            self.unit_data: dict[str, Any] = json.load(f)

        # Track all discovered dimensions
        self.all_dimensions: dict[str, dict[str, int]] = {}
        self.common_signatures: dict[tuple[int, ...], float] = {}  # For cache optimization

    def calculate_signature(self, dims: dict[str, int]) -> float:
        """Calculate prime factorization signature for dimensions."""
        if not dims:
            return 1.0

        signature = 1.0
        prime_map = {
            'length': 2,
            'mass': 3,
            'time': 5,
            'current': 7,
            'temp': 11,
            'amount': 13,
            'luminosity': 17,
        }

        for dim_name, power in dims.items():
            if power != 0 and dim_name in prime_map:
                signature *= prime_map[dim_name] ** power

        return signature

    def tuple_from_dims(self, dims: dict[str, int]) -> tuple[int, ...]:
        """Create ordered tuple for dimension cache key."""
        return (
            dims.get('length', 0),
            dims.get('mass', 0),
            dims.get('time', 0),
            dims.get('current', 0),
            dims.get('temp', 0),
            dims.get('amount', 0),
            dims.get('luminosity', 0),
        )

    def format_dimension_comment(self, dims: dict[str, int]) -> str:
        """Create readable comment for a dimension."""
        if not dims:
            return "Dimensionless"

        parts = []
        for dim, power in sorted(dims.items()):
            if power != 0:
                symbol = DIMENSION_SYMBOLS.get(dim, dim[0].upper())
                if power == 1:
                    parts.append(symbol)
                else:
                    parts.append(f"{symbol}^{power}")

        return ' '.join(parts) if parts else "Dimensionless"

    def extract_all_dimensions(self) -> None:
        """Extract all unique dimensions from unit data."""
        # Add base dimensions
        for name, config in BASE_DIMENSIONS.items():
            self.all_dimensions[name] = config['params']

        # Extract from unit data
        for field_name, field_data in self.unit_data.items():
            dims = field_data.get('dimensions', {})
            name = field_name.upper()

            # Skip if it's a base dimension
            if name not in BASE_DIMENSIONS:
                self.all_dimensions[name] = dims

        # Build common signatures cache (programmatically)
        for _name, dims in self.all_dimensions.items():
            dim_tuple = self.tuple_from_dims(dims)
            signature = self.calculate_signature(dims)
            self.common_signatures[dim_tuple] = signature

    def generate_common_signatures_dict(self) -> list[str]:
        """Generate the _COMMON_SIGNATURES dictionary programmatically."""
        lines = []
        lines.append("    # Pre-computed signature cache for common dimensions")
        lines.append("    _COMMON_SIGNATURES: ClassVar[dict[tuple[int, ...], int | float]] = {")

        # Sort by complexity (number of non-zero dimensions) and then alphabetically
        sorted_sigs = sorted(self.common_signatures.items(),
                           key=lambda x: (sum(abs(v) for v in x[0]), x[0]))

        # Limit to most common ones to avoid huge cache
        max_cache_entries = 50
        for dim_tuple, signature in sorted_sigs[:max_cache_entries]:
            # Find dimensions with this signature for comment
            matching_dims = [name for name, dims in self.all_dimensions.items()
                           if self.tuple_from_dims(dims) == dim_tuple]

            if matching_dims:
                # Pick the shortest/most descriptive name
                best_name = min(matching_dims, key=len)
                dims = self.all_dimensions[best_name]
                comment = self.format_dimension_comment(dims)

                # Format the signature value nicely
                if signature == int(signature):
                    sig_str = str(int(signature))
                else:
                    sig_str = f"{signature:.10g}"  # Use general format to avoid long decimals

                lines.append(f"        {dim_tuple}: {sig_str},  # {comment}")

        lines.append("    }")

        return lines

    def generate_header(self) -> list[str]:
        """Generate the file header."""
        lines = [
            '"""',
            'Dimension System',
            '================',
            '',
            'Compile-time dimensional analysis using type system for ultra-fast operations.',
            '',
            'This file is auto-generated by codegen/generators/dimensions_gen.py',
            'DO NOT EDIT MANUALLY - changes will be overwritten.',
            '"""',
            '',
            'from dataclasses import dataclass',
            'from enum import IntEnum',
            'from typing import ClassVar, final',
            '',
            '',
        ]
        return lines

    def generate_base_dimension_class(self) -> list[str]:
        """Generate the BaseDimension IntEnum."""
        lines = [
            'class BaseDimension(IntEnum):',
            '    """Base dimensions as prime numbers for efficient bit operations."""',
        ]

        for name, config in BASE_DIMENSIONS.items():
            if name == 'DIMENSIONLESS':
                lines.append(f"    {name} = {config['prime']}  # Must be 1 to act as multiplicative identity")
            else:
                lines.append(f"    {name} = {config['prime']}")

        lines.extend(['', ''])
        return lines

    def generate_dimension_signature_class(self) -> list[str]:
        """Generate the DimensionSignature class."""
        lines = [
            '@final',
            '@dataclass(frozen=True, slots=True)',
            'class DimensionSignature:',
            '    """Immutable dimension signature for zero-cost dimensional analysis."""',
            '    ',
            '    # Store as bit pattern for ultra-fast comparison',
            '    _signature: int | float = 1',
            '    ',
        ]

        # Add common signatures cache
        lines.extend(self.generate_common_signatures_dict())

        lines.extend([
            '    ',
            '    # Instance cache for interning common dimensions',
            '    _INSTANCE_CACHE: ClassVar[dict[int | float, "DimensionSignature"]] = {}',
            '    ',
            '    def __new__(cls, signature: int | float = 1):',
            '        """Optimized constructor with instance interning."""',
            '        if signature in cls._INSTANCE_CACHE:',
            '            return cls._INSTANCE_CACHE[signature]',
            '        ',
            '        instance = object.__new__(cls)',
            '        ',
            '        # Cache common signatures',
            '        if len(cls._INSTANCE_CACHE) < 100:  # Limit cache size',
            '            cls._INSTANCE_CACHE[signature] = instance',
            '        ',
            '        return instance',
            '    ',
            '    @classmethod',
            '    def create(cls, length=0, mass=0, time=0, current=0, temp=0, amount=0, luminosity=0):',
            '        """Create dimension from exponents with optimized lookup."""',
            '        # Check cache first',
            '        key = (length, mass, time, current, temp, amount, luminosity)',
            '        if key in cls._COMMON_SIGNATURES:',
            '            return cls(cls._COMMON_SIGNATURES[key])',
            '        ',
            '        # Fast path for dimensionless',
            '        if not any([length, mass, time, current, temp, amount, luminosity]):',
            '            return cls(1)',
            '        ',
            '        # Compute signature',
            '        signature = 1',
            '        if length != 0:',
            '            signature *= BaseDimension.LENGTH ** length',
            '        if mass != 0:',
            '            signature *= BaseDimension.MASS ** mass',
            '        if time != 0:',
            '            signature *= BaseDimension.TIME ** time',
            '        if current != 0:',
            '            signature *= BaseDimension.CURRENT ** current',
            '        if temp != 0:',
            '            signature *= BaseDimension.TEMPERATURE ** temp',
            '        if amount != 0:',
            '            signature *= BaseDimension.AMOUNT ** amount',
            '        if luminosity != 0:',
            '            signature *= BaseDimension.LUMINOSITY ** luminosity',
            '        ',
            '        return cls(signature)',
            '    ',
            '    def __mul__(self, other):',
            '        """Multiply dimensions."""',
            '        return DimensionSignature(self._signature * other._signature)',
            '    ',
            '    def __truediv__(self, other):',
            '        """Divide dimensions."""',
            '        return DimensionSignature(self._signature / other._signature)',
            '    ',
            '    def __pow__(self, power):',
            '        """Raise dimension to a power."""',
            '        if power == 1:',
            '            return self',
            '        if power == 0:',
            '            return DimensionSignature(1)',
            '        return DimensionSignature(self._signature ** power)',
            '    ',
            '    def is_compatible(self, other):',
            '        """Check dimensional compatibility."""',
            '        return self._signature == other._signature',
            '    ',
            '    def __eq__(self, other):',
            '        """Check equality."""',
            '        if self is other:',
            '            return True',
            '        return isinstance(other, DimensionSignature) and self._signature == other._signature',
            '    ',
            '    def __hash__(self):',
            '        """Hash based on signature."""',
            '        return hash(self._signature)',
            '',
            '',
        ])

        return lines

    def generate_dimension_constants(self) -> list[str]:
        """Generate dimension constant definitions."""
        lines = []

        # Generate signature lookup dictionary
        lines.append('# Pre-computed dimension signatures for all dimensions')
        lines.append('_DIMENSION_SIGNATURES = {')

        for name in sorted(self.all_dimensions.keys()):
            dims = self.all_dimensions[name]
            signature = self.calculate_signature(dims)
            comment = self.format_dimension_comment(dims)

            if signature == int(signature):
                sig_str = str(int(signature))
            else:
                sig_str = f"{signature:.10g}"

            lines.append(f'    "{name}": {sig_str},  # {comment}')

        lines.append('}')
        lines.append('')

        # Lazy loading infrastructure
        lines.extend([
            '# Lazy loading cache',
            '_dimension_cache: dict[str, DimensionSignature] = {}',
            '',
            'def __getattr__(name: str) -> DimensionSignature:',
            '    """Lazy load dimension constants."""',
            '    if name in _DIMENSION_SIGNATURES:',
            '        if name not in _dimension_cache:',
            '            _dimension_cache[name] = DimensionSignature(_DIMENSION_SIGNATURES[name])',
            '        return _dimension_cache[name]',
            '    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")',
            '',
        ])

        # Generate ALL dimensions found in unit data - no hardcoded mappings
        lines.append('# All dimension constants generated from unit data')

        # Generate constants for ALL fields in the JSON data
        for field_name in sorted(self.unit_data.keys()):
            field_data = self.unit_data[field_name]
            dims = field_data.get('dimensions', {})
            const_name = field_name.upper()
            
            signature = self.calculate_signature(dims)
            comment = self.format_dimension_comment(dims)

            if signature == int(signature):
                sig_str = str(int(signature))
            else:
                sig_str = f"{signature:.10g}"

            lines.append(f'{const_name} = DimensionSignature({sig_str})  # {comment}')

        lines.append('')

        return lines

    def generate_exports(self) -> list[str]:
        """Generate __all__ export list."""
        lines = [
            '# Module exports',
            '__all__ = [',
            '    "BaseDimension",',
            '    "DimensionSignature",',
        ]

        # Add all dimensions from unit data
        for field_name in sorted(self.unit_data.keys()):
            const_name = field_name.upper()
            lines.append(f'    "{const_name}",')

        lines.extend([
            ']',
            '',
        ])

        return lines

    def generate(self) -> None:
        """Generate the complete dimensions.py file."""
        # Extract all dimensions from data
        self.extract_all_dimensions()

        # Build the file content
        lines = []
        lines.extend(self.generate_header())
        lines.extend(self.generate_base_dimension_class())
        lines.extend(self.generate_dimension_signature_class())
        lines.extend(self.generate_dimension_constants())
        lines.extend(self.generate_exports())

        # Write the file with newline at end
        content = '\n'.join(lines) + '\n'
        self.output_path.write_text(content, encoding='utf-8')
        print(f"Generated {self.output_path}")

        # Save metadata to out directory
        metadata = {
            'total_dimensions': len(self.all_dimensions),
            'generated_dimensions': sorted(self.unit_data.keys()),
            'base_dimensions': list(BASE_DIMENSIONS.keys()),
            'signatures_cached': len(self.common_signatures),
        }

        metadata_path = self.out_dir / 'dimension_metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved metadata to {metadata_path}")


def main() -> None:
    """Main entry point."""
    # Set up paths
    generator_dir = Path(__file__).parent
    data_path = generator_dir / 'data' / 'unit_data.json'
    output_path = generator_dir.parent.parent / 'generated' / 'dimensions.py'
    out_dir = generator_dir / 'out'

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Run generator
    generator = DimensionGenerator(data_path, output_path, out_dir)
    generator.generate()

    print("\nDimension generation complete!")
    print(f"  - Total dimensions: {len(generator.all_dimensions)}")
    print(f"  - Cached signatures: {len(generator.common_signatures)}")


if __name__ == "__main__":
    main()
