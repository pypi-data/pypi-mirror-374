#!/usr/bin/env python3
"""
Script to generate comprehensive quantities.py for all variable types.

This script generates static quantity class definitions without setter classes.
The setter classes are generated separately in setters_gen.py.
"""

from pathlib import Path

try:
    from .data_processor import (
        augment_with_prefixed_units,
        calculate_statistics,
        convert_to_class_name,
        get_dimension_constant_name,
        load_unit_data,
        save_text_file,
        setup_import_path,
    )
    from .doc_generator import generate_class_docstring, generate_init_method, generate_set_method
except ImportError:
    # Handle standalone execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from .data_processor import (
        augment_with_prefixed_units,
        calculate_statistics,
        convert_to_class_name,
        get_dimension_constant_name,
        load_unit_data,
        save_text_file,
        setup_import_path,
    )
    from .doc_generator import generate_class_docstring, generate_init_method, generate_set_method


def generate_quantities(parsed_data: dict, dimension_mapping: dict) -> str:
    """Generate the quantities.py content with static class definitions for performance."""
    del dimension_mapping  # Unused but kept for API compatibility
    
    sorted_fields = sorted(parsed_data.items())
    fields_with_units = [(k, v) for k, v in sorted_fields if v.get('units')]
    
    lines = [
        '"""',
        'Quantity Classes Module - Static Edition',
        '========================================',
        '',
        'Static quantity class definitions for maximum import performance.',
        'Uses static class generation instead of dynamic type() calls.',
        'Auto-generated from unit_data.json.',
        '"""',
        '',
        'from ..quantities.typed_quantity import TypedQuantity',
        'from . import dimensions as dim',
        'from . import setters as ts',
        ''
    ]
    
    # Generate all quantity classes
    lines.append('# ===== QUANTITY CLASSES =====')
    lines.append('# Static quantity class definitions with __slots__ optimization')
    lines.append('')
    
    for field_name, field_data in fields_with_units:
        class_name = convert_to_class_name(field_name)
        setter_class_name = f"{class_name}Setter"
        dimension_constant = get_dimension_constant_name(field_name)
        display_name = field_data.get('field', class_name).lower()
        units = field_data.get('units', [])
        is_dimensionless = class_name == 'Dimensionless'
        
        # Generate class declaration and docstring
        lines.append(f'class {class_name}(TypedQuantity):')
        lines.extend(generate_class_docstring(class_name, display_name, units, is_dimensionless))
        # Class attributes
        lines.append('    __slots__ = ()')
        lines.append(f'    _setter_class = ts.{setter_class_name}')
        lines.append(f'    _expected_dimension = dim.{dimension_constant}')
        lines.append('    ')
        
        # Generate __init__ method
        lines.extend(generate_init_method(class_name, display_name, is_dimensionless, stub_only=False))
        
        # Generate set method
        lines.append('    ')
        lines.extend(generate_set_method(setter_class_name, display_name, stub_only=False))
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
    output_file = generated_path / "quantities.py"
    
    print("Loading parsed units data for quantities...")
    
    # Setup import path and load data using shared processor
    setup_import_path()
    parsed_data = load_unit_data(parsed_file)
    dimension_mapping = load_unit_data(dimension_file) if dimension_file.exists() else {}
    
    print(f"Loaded {len(parsed_data)} fields with units")
    
    # Augment data with missing prefixed units using shared processor
    print("\nAugmenting data with missing prefixed units...")
    augmented_data, generated_count = augment_with_prefixed_units(parsed_data)
    print(f"Generated {generated_count} missing prefixed units for quantities")
    
    # Count fields with units
    fields_with_units = sum(1 for field_data in augmented_data.values() if field_data.get('units'))
    print(f"Found {len(augmented_data)} total fields, {fields_with_units} fields with units")
    
    # Generate quantities file
    print("Generating quantities.py...")
    content = generate_quantities(augmented_data, dimension_mapping)
    
    # Write output file
    save_text_file(content, output_file)
    print(f"Generated quantities file: {output_file}")
    
    # Print statistics using shared calculator
    stats = calculate_statistics(augmented_data)
    print("\nStatistics:")
    print(f"  Total fields: {stats['total_fields']}")
    print(f"  Fields with units: {fields_with_units}")
    print(f"  Original units: {stats['original_units']}")
    print(f"  Total units (with prefixes): {stats['total_units']}")
    print(f"  Generated prefixed units: {stats['generated_prefixed_units']}")
    
    # Show top quantity types by unit count
    fields_by_units = [(field_name, len(field_data.get('units', [])), field_data.get('field', ''))
                       for field_name, field_data in augmented_data.items() if field_data.get('units')]
    fields_by_units.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop quantity types by unit count:")
    for field_name, unit_count, display_name in fields_by_units[:10]:
        class_name = convert_to_class_name(field_name)
        print(f"  {class_name:<25} : {unit_count:>3} units ({display_name})")


if __name__ == "__main__":
    main()
