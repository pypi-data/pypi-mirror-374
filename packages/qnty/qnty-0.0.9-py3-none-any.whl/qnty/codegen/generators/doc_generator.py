"""
Documentation Generation Helper
==============================

Shared functions for generating consistent documentation across
quantities.py and quantities.pyi files.
"""

try:
    from .data_processor import get_unit_names_and_aliases
except ImportError:
    # Handle standalone execution
    from .data_processor import get_unit_names_and_aliases


def generate_class_docstring(class_name: str, display_name: str, units: list, is_dimensionless: bool = False) -> list[str]:
    """Generate comprehensive class docstring for quantity classes."""
    # Get example units for documentation
    example_units = []
    for unit in units[:3]:  # Take first 3 units as examples
        primary_name, _ = get_unit_names_and_aliases(unit)
        example_units.append(f'"{primary_name}"')
    
    unit_examples = ', '.join(example_units) if example_units else '"unit"'
    
    lines = [
        '    """',
        f'    Type-safe {display_name} quantity with expression capabilities.',
        '    ',
    ]
    
    if is_dimensionless:
        lines.extend([
            '    Constructor Options:',
            '    -------------------',
            f'    - {class_name}("variable_name") -> Create unknown {display_name}',
            f'    - {class_name}(value, "variable_name") -> Create known {display_name}',
            '    ',
            '    Examples:',
            '    ---------',
            f'    >>> unknown = {class_name}("efficiency")  # Unknown {display_name}',
            f'    >>> known = {class_name}(0.85, "thermal_efficiency")  # Known {display_name}',
        ])
    else:
        lines.extend([
            '    Constructor Options:',
            '    -------------------',
            f'    - {class_name}("variable_name") -> Create unknown {display_name}',
            f'    - {class_name}(value, "unit", "variable_name") -> Create known {display_name}',
            '    ',
            '    Examples:',
            '    ---------',
            f'    >>> unknown = {class_name}("pressure")  # Unknown {display_name}',
            f'    >>> known = {class_name}(100, {unit_examples.split(",")[0] if unit_examples else "unit"}, "inlet_pressure")  # Known {display_name}',
            '    ',
            f'    Available units: {unit_examples}',
        ])
    
    lines.append('    """')
    return lines


def generate_init_method(class_name: str, display_name: str, is_dimensionless: bool = False, stub_only: bool = False) -> list[str]:
    """Generate __init__ method with proper type hints."""
    del class_name  # Unused but kept for API compatibility
    lines = []
    
    if is_dimensionless:
        lines.append('    def __init__(self, name_or_value: str | int | float, name: str | None = None, is_known: bool = True):')
        if not stub_only:
            lines.extend([
                '        """',
                f'        Initialize {display_name} quantity.',
                '        ',
                '        Args:',
                '            name_or_value: Variable name (str) if unknown, or value (int/float) if known',
                '            name: Variable name (required if providing value)',
                '            is_known: Whether the variable has a known value',
                '        """',
                '        if name is None:',
                '            # Single argument: name only (unknown variable)',
                '            super().__init__(name_or_value, is_known=is_known)',
                '        else:',
                '            # Two arguments: value and name (known variable)',
                '            super().__init__(name_or_value, name, is_known=is_known)',
            ])
        else:
            lines.append(' ...')
    else:
        lines.append('    def __init__(self, name_or_value: str | int | float, unit: str | None = None, name: str | None = None, is_known: bool = True):')
        if not stub_only:
            lines.extend([
                '        """',
                f'        Initialize {display_name} quantity.',
                '        ',
                '        Args:',
                '            name_or_value: Variable name (str) if unknown, or value (int/float) if known',
                '            unit: Unit string (required if providing value)',
                '            name: Variable name (required if providing value)',
                '            is_known: Whether the variable has a known value',
                '        """',
                '        if unit is None and name is None:',
                '            # Single argument: name only (unknown variable)',
                '            super().__init__(name_or_value, is_known=is_known)',
                '        elif unit is not None and name is not None:',
                '            # Three arguments: value, unit, name (known variable)',
                '            super().__init__(name_or_value, unit, name, is_known=is_known)',
                '        else:',
                '            raise ValueError("Must provide either just name (unknown) or value, unit, and name (known)")',
            ])
        else:
            lines.append(' ...')
    
    return lines


def generate_set_method(setter_class_name: str, display_name: str, stub_only: bool = False) -> list[str]:
    """Generate set method with comprehensive documentation."""
    lines = [
        f'    def set(self, value: int | float) -> ts.{setter_class_name}:',
        '        """',
        f'        Create a setter for this {display_name} quantity.',
        '        ',
        '        Args:',
        '            value: The numeric value to set',
        '        ',
        '        Returns:',
        f'            {setter_class_name}: A setter with unit properties like .meters, .inches, etc.',
        '        ',
        '        Example:',
        '            >>> length = Length("beam_length")',
        '            >>> length.set(100).millimeters  # Sets to 100 mm',
        '        """',
    ]
    
    if stub_only:
        lines.append('        ...')
    else:
        lines.append(f'        return ts.{setter_class_name}(self, value)')
    
    return lines
