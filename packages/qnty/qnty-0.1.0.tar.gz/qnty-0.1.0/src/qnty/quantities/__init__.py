"""
Core Quantities Package
=====================

High-performance quantity and variable systems.
"""

from .base_qnty import Quantity
from .field_qnty import *
from .field_qnty import FieldQnty
from .field_vars import *

# Register types with TypeRegistry for performance optimization
try:
    from ..utils.protocols import register_variable_type

    register_variable_type(FieldQnty)
    # Also register all generated field variable types
    import inspect
    import sys

    current_module = sys.modules[__name__]
    for _name, obj in inspect.getmembers(current_module, inspect.isclass):
        if hasattr(obj, "_dimension") and issubclass(obj, FieldQnty):
            register_variable_type(obj)
except ImportError:
    pass  # Handle import ordering gracefully

__all__ = ["Quantity", "FieldQnty"]
