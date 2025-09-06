#!/usr/bin/env python3
"""
Unit Data Processing Utilities
==============================

Shared utilities for processing unit data consistently across all generators.
Handles prefix augmentation, data normalization, and statistics calculation.
"""

import json
import sys
from pathlib import Path
from typing import Any


def setup_import_path() -> None:
    """Add src path to import qnty package."""
    # Go up from generators/ to src/
    src_path = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(src_path))


def load_unit_data(data_path: Path) -> dict[str, Any]:
    """Load and return unit data from JSON file."""
    with open(data_path, encoding='utf-8') as f:
        return json.load(f)


def augment_with_prefixed_units(raw_data: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """
    Add missing prefixed units to the data consistently.
    
    This is the canonical implementation used by all generators to ensure
    they all see the same augmented data structure.
    
    Returns:
        Tuple of (augmented_data, generated_count)
    """
    # Import prefixes (setup_import_path should be called first)
    from qnty.units.prefixes import PREFIXABLE_UNITS, StandardPrefixes
    
    # Create deep copy of data with consistent structure
    augmented_data = {}
    for field_name, field_data in raw_data.items():
        augmented_data[field_name] = {
            'field': field_data.get('field', field_name),
            'normalized_field': field_data.get('normalized_field', field_name),
            'dimensions': field_data.get('dimensions', {}),
            'si_base_unit': field_data.get('si_base_unit', ''),
            'imperial_base_unit': field_data.get('imperial_base_unit', ''),
            'units': list(field_data.get('units', []))  # Deep copy the units list
        }
    
    # Track existing units globally to avoid duplicates
    existing_units = set()
    for field_data in augmented_data.values():
        for unit in field_data['units']:
            existing_units.add(unit.get('normalized_name', ''))
    
    generated_count = 0
    
    # Process each field to find prefixable base units
    for field_data in augmented_data.values():
        # Copy list since we'll modify it during iteration
        original_units = list(field_data['units'])
        
        for unit_data in original_units:
            unit_name = unit_data.get('normalized_name', '')
            
            # Check if this unit is in our prefixable units list
            if unit_name in PREFIXABLE_UNITS:
                prefixes = PREFIXABLE_UNITS[unit_name]
                
                # Generate prefixed variants
                for prefix_enum in prefixes:
                    if prefix_enum == StandardPrefixes.NONE:
                        continue
                    
                    prefix = prefix_enum.value
                    prefixed_name = prefix.apply_to_name(unit_name)
                    
                    # Only add if it doesn't already exist globally
                    if prefixed_name not in existing_units:
                        # Create prefixed unit with consistent structure
                        prefixed_unit = {
                            'name': prefix.apply_to_name(unit_data.get('name', unit_name)),
                            'normalized_name': prefixed_name,
                            'notation': prefix.apply_to_symbol(unit_data.get('notation', '')),
                            'si_conversion': unit_data.get('si_conversion', 1.0) * prefix.factor,
                            'imperial_conversion': unit_data.get('imperial_conversion', 1.0) * prefix.factor,
                            'aliases': [
                                prefix.apply_to_symbol(unit_data.get('notation', ''))
                            ] if unit_data.get('notation') else [],
                            'generated_from_prefix': True  # Mark as generated
                        }
                        
                        field_data['units'].append(prefixed_unit)
                        existing_units.add(prefixed_name)
                        generated_count += 1
    
    return augmented_data, generated_count


def convert_to_class_name(field_name: str) -> str:
    """Convert field name to PascalCase class name consistently."""
    words = field_name.split('_')
    return ''.join(word.capitalize() for word in words)


def get_dimension_constant_name(field_name: str) -> str:
    """Get dimension constant name - just convert to uppercase."""
    return field_name.upper()


def calculate_statistics(unit_data: dict[str, Any]) -> dict[str, Any]:
    """Calculate statistics for the unit data."""
    total_units = sum(len(field_data.get('units', [])) for field_data in unit_data.values())
    total_fields = len(unit_data)
    
    # Count generated units
    generated_units = sum(
        sum(1 for unit in field_data.get('units', []) if unit.get('generated_from_prefix', False))
        for field_data in unit_data.values()
    )
    
    return {
        'total_units': total_units,
        'total_fields': total_fields,
        'generated_prefixed_units': generated_units,
        'original_units': total_units - generated_units
    }


def get_unit_names_and_aliases(unit_data: dict[str, Any]) -> tuple[str, list[str]]:
    """
    Extract the primary unit name and aliases consistently for all generators.
    
    Uses normalized_name as the primary identifier, with notation and aliases
    as additional identifiers. Does NOT use the full 'name' field to avoid
    inconsistencies between generators.
    
    Returns:
        Tuple of (primary_name, aliases_list)
    """
    import re
    
    def sanitize_name(name: str) -> str:
        """Sanitize a name to be a valid Python identifier."""
        if not name:
            return 'unnamed'
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = 'unit_' + sanitized
        # Remove double underscores and trailing underscores
        sanitized = re.sub(r'_+', '_', sanitized).strip('_')
        
        # Check for Python reserved words and keywords
        import keyword
        if keyword.iskeyword(sanitized) or sanitized in ['in', 'and', 'or', 'not', 'is']:
            sanitized = sanitized + '_unit'
        
        return sanitized if sanitized else 'unnamed'
    
    # Use normalized_name as primary - this is the canonical identifier
    primary_name = sanitize_name(unit_data.get('normalized_name', ''))
    
    # Collect aliases from notation and aliases fields only (NOT full name)
    aliases = []
    
    # Add notation as alias if different from primary
    notation = unit_data.get('notation', '')
    if notation:
        notation_sanitized = sanitize_name(notation)
        if notation_sanitized != primary_name and notation_sanitized not in aliases:
            aliases.append(notation_sanitized)
    
    # Add explicit aliases from the aliases field
    raw_aliases = unit_data.get('aliases', [])
    for alias in raw_aliases:
        sanitized_alias = sanitize_name(alias)
        if sanitized_alias != primary_name and sanitized_alias not in aliases:
            aliases.append(sanitized_alias)
    
    return primary_name, aliases


def save_text_file(content: str, file_path: Path) -> None:
    """Save text content to file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def load_json_data(file_path: Path) -> dict[str, Any]:
    """Load JSON data from file."""
    with open(file_path, encoding='utf-8') as f:
        return json.load(f)


def save_metadata(metadata: dict[str, Any], output_path: Path, generator_name: str) -> None:
    """Save generator metadata to JSON file."""
    metadata_path = output_path / f'{generator_name}_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved {generator_name} metadata to {metadata_path}")


def escape_string(s: str) -> str:
    """Escape quotes and backslashes in string for Python code generation."""
    return s.replace('\\', '\\\\').replace('"', '\\"') if s else ''


def is_valid_python_identifier(name: str) -> bool:
    """Check if a string is a valid Python identifier."""
    import keyword
    return bool(name and name.isidentifier() and not keyword.iskeyword(name))


def sanitize_python_name(name: str) -> str:
    """Convert name to valid Python identifier."""
    import re
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = '_' + sanitized
    
    # Remove double underscores and trailing underscores
    sanitized = re.sub(r'_+', '_', sanitized).strip('_')
    
    return sanitized if sanitized else 'unnamed'


def get_standard_generator_paths(generator_file: Path) -> dict[str, Path]:
    """Get standard paths used by generators."""
    generator_dir = generator_file.parent
    return {
        'generator_dir': generator_dir,
        'data_path': generator_dir / 'data' / 'unit_data.json',
        'output_dir': generator_dir / 'out',
        'generated_dir': generator_dir.parent.parent / 'generated',
        'src_dir': generator_dir.parent.parent
    }


def identify_base_units_needing_prefixes(parsed_data: dict[str, Any]) -> dict[str, list]:
    """Identify base SI units that should have prefixes generated."""
    from qnty.units.prefixes import PREFIXABLE_UNITS
    
    base_units = {}
    
    # Look through all units to find base SI units that are in PREFIXABLE_UNITS
    for field_name, field_data in parsed_data.items():
        for unit_data in field_data['units']:
            unit_name = unit_data['normalized_name']
            if unit_name in PREFIXABLE_UNITS:
                # This is a base unit that should have prefixes
                # Store all occurrences of the unit, not just the last one
                if unit_name not in base_units:
                    base_units[unit_name] = []
                
                base_units[unit_name].append({
                    'unit_data': unit_data,
                    'field_name': field_name,
                    'prefixes': PREFIXABLE_UNITS[unit_name]
                })
    
    return base_units


def generate_prefixed_unit_data(base_unit_data: dict[str, Any], prefix, field_data: dict[str, Any]) -> dict[str, Any]:
    """Generate unit data for a prefixed variant of a base unit."""
    prefix_def = prefix.value
    
    # Apply prefix to name and symbol
    prefixed_name = prefix_def.apply_to_name(base_unit_data['normalized_name'])
    # Use the field's si_base_unit instead of unit-level data
    prefixed_symbol = prefix_def.apply_to_symbol(field_data.get('si_base_unit', base_unit_data.get('notation', '')))
    
    # Calculate new SI factor
    base_factor = base_unit_data.get('si_conversion', 1.0)
    new_factor = base_factor * prefix_def.factor
    
    # Create new unit data using new structure
    return {
        'name': prefix_def.apply_to_name(base_unit_data['name']),
        'normalized_name': prefixed_name,
        'notation': prefixed_symbol,
        'si_conversion': new_factor,
        'imperial_conversion': base_unit_data.get('imperial_conversion', 1.0),
        'aliases': [prefixed_symbol] if prefixed_symbol else [],
        'generated_from_prefix': True  # Mark as generated for identification
    }


def augment_parsed_data_with_prefixes(parsed_data: dict[str, Any]) -> dict[str, Any]:
    """Add missing prefixed units to the parsed data."""
    from qnty.units.prefixes import StandardPrefixes
    
    # Make a deep copy to avoid modifying the original
    augmented_data = {}
    for key, value in parsed_data.items():
        augmented_data[key] = {
            'field': value['field'],
            'normalized_field': value['normalized_field'],
            'dimensions': value.get('dimensions', {}),
            'units': list(value['units'])  # Copy the units list
        }
    
    # Find base units that need prefixes
    base_units = identify_base_units_needing_prefixes(parsed_data)
    
    # Track existing unit names to avoid duplicates
    existing_units = set()
    for field_data in augmented_data.values():
        for unit in field_data['units']:
            existing_units.add(unit['normalized_name'])
    
    # Generate and add missing prefixed units
    generated_count = 0
    for unit_name, base_entries in base_units.items():
        # Process each field where this unit appears
        for base_info in base_entries:
            base_unit = base_info['unit_data']
            field_name = base_info['field_name']
            prefixes = base_info['prefixes']
            
            for prefix in prefixes:
                if prefix == StandardPrefixes.NONE:
                    continue  # Skip NONE prefix
                    
                prefix_def = prefix.value
                prefixed_name = prefix_def.apply_to_name(unit_name)
                
                # Only add if it doesn't already exist globally
                if prefixed_name not in existing_units:
                    prefixed_unit = generate_prefixed_unit_data(base_unit, prefix, augmented_data[field_name])
                    augmented_data[field_name]['units'].append(prefixed_unit)
                    existing_units.add(prefixed_name)
                    generated_count += 1
    
    print(f"Generated {generated_count} missing prefixed units for type stubs")
    return augmented_data
