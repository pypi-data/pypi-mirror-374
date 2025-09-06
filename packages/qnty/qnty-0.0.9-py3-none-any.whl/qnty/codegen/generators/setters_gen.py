#!/usr/bin/env python3
"""
Script to generate comprehensive setters.py for all variable setters.

This script generates static setter class definitions with unit properties
for the fluent API with dimension-specific unit properties.
"""

from pathlib import Path

try:
    from .data_processor import (
        augment_with_prefixed_units,
        calculate_statistics,
        convert_to_class_name,
        get_dimension_constant_name,
        get_unit_names_and_aliases,
        load_unit_data,
        save_text_file,
        setup_import_path,
    )
except ImportError:
    from .data_processor import (
        augment_with_prefixed_units,
        calculate_statistics,
        convert_to_class_name,
        get_dimension_constant_name,
        get_unit_names_and_aliases,
        load_unit_data,
        save_text_file,
        setup_import_path,
    )


def generate_setters(parsed_data: dict, dimension_mapping: dict) -> str:
    """Generate the setters.py content with static setter class definitions."""
    
    sorted_fields = sorted(parsed_data.items())
    fields_with_units = [(k, v) for k, v in sorted_fields if v.get('units')]
    
    lines = [
        '"""',
        'Setter Classes Module - Static Edition',
        '======================================',
        '',
        'Static setter class definitions for maximum import performance.',
        'Provides fluent API unit properties for all variable types.',
        'Auto-generated from unit_data.json.',
        '"""',
        '',
        'from ..quantities.quantity import Quantity, TypeSafeSetter',
        'from . import units',
        ''
    ]
    
    # Generate all setter classes
    lines.append('# ===== SETTER CLASSES =====')
    lines.append('# Static setter class definitions with __slots__ optimization')
    lines.append('')
    
    for field_name, field_data in fields_with_units:
        class_name = convert_to_class_name(field_name)
        setter_class_name = f"{class_name}Setter"
        get_dimension_constant_name(field_name)
        units_class_name = f"{class_name}Units"
        
        lines.append(f'class {setter_class_name}(TypeSafeSetter):')
        lines.append(f'    """{class_name}-specific setter with optimized unit properties."""')
        lines.append('    __slots__ = ()')
        lines.append('    ')
        
        # Generate property for each unit, avoiding duplicates
        generated_properties = set()
        
        for unit_data in field_data['units']:
            primary_name, aliases = get_unit_names_and_aliases(unit_data)
            # Use primary name for the main property
            property_name = primary_name
            
            # Skip if this property name was already generated
            if property_name in generated_properties:
                continue
            
            generated_properties.add(property_name)
            
            lines.append('    @property')
            lines.append(f'    def {property_name}(self):')
            unit_display_name = unit_data.get('name', primary_name)
            # Escape backslashes in the docstring to avoid escape sequence warnings
            escaped_name = unit_display_name.replace('\\', '\\\\')
            lines.append(f'        """Set value using {escaped_name} units."""')
            lines.append(f'        unit_const = units.{units_class_name}.{property_name}')
            lines.append('        self.variable.quantity = Quantity(self.value, unit_const)')
            lines.append('        return self.variable')
            lines.append('    ')
            
            # Add alias properties using shared processing
            for alias in aliases:
                # Only add if different from main property and not already generated
                if (alias != property_name and
                    alias.isidentifier() and
                    alias not in generated_properties):
                    generated_properties.add(alias)
                    lines.append('    @property')
                    lines.append(f'    def {alias}(self):')
                    lines.append(f'        """Set value using {alias} units (alias for {primary_name})."""')
                    lines.append(f'        return self.{property_name}')
                    lines.append('    ')
        
        lines.append('')
    
    return '\n'.join(lines) + '\n'


def main():
    """Main execution function."""
    # Setup paths using pathlib
    base_path = Path(__file__).parents[4]  # Go up to qnty root
    data_path = Path(__file__).parent / "data"
    output_path = Path(__file__).parent / "out"
    generated_path = base_path / "src" / "qnty" / "generated"
    
    # Ensure output directories exist
    output_path.mkdir(exist_ok=True)
    generated_path.mkdir(exist_ok=True)
    
    parsed_file = data_path / "unit_data.json"
    dimension_file = output_path / "dimension_mapping.json"
    output_file = generated_path / "setters.py"
    
    print("Loading parsed units data for setters...")
    
    # Setup import path and load data using shared processor
    setup_import_path()
    parsed_data = load_unit_data(parsed_file)
    dimension_mapping = load_unit_data(dimension_file) if dimension_file.exists() else {}
    
    print(f"Loaded {len(parsed_data)} fields with units")
    
    # Augment data with missing prefixed units using shared processor
    print("\nAugmenting data with missing prefixed units...")
    augmented_data, generated_count = augment_with_prefixed_units(parsed_data)
    print(f"Generated {generated_count} missing prefixed units for setters")
    
    # Count fields with units
    fields_with_units = sum(1 for field_data in augmented_data.values() if field_data.get('units'))
    print(f"Found {len(augmented_data)} total fields, {fields_with_units} fields with units")
    
    # Generate setters file
    print("Generating setters.py...")
    content = generate_setters(augmented_data, dimension_mapping)
    
    # Write output file
    save_text_file(content, output_file)
    print(f"Generated setters file: {output_file}")
    
    # Print statistics using shared calculator
    stats = calculate_statistics(augmented_data)
    print("\nStatistics:")
    print(f"  Total fields: {stats['total_fields']}")
    print(f"  Fields with units: {fields_with_units}")
    print(f"  Original units: {stats['original_units']}")
    print(f"  Total units (with prefixes): {stats['total_units']}")
    print(f"  Generated prefixed units: {stats['generated_prefixed_units']}")
    
    # Show top setter types by unit count
    fields_by_units = [(field_name, len(field_data.get('units', [])), field_data.get('field', ''))
                       for field_name, field_data in augmented_data.items() if field_data.get('units')]
    fields_by_units.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop setter types by unit property count:")
    for field_name, unit_count, display_name in fields_by_units[:10]:
        class_name = convert_to_class_name(field_name)
        print(f"  {class_name}Setter{'':<15} : {unit_count:>3} properties ({display_name})")


if __name__ == "__main__":
    main()
