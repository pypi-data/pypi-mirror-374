"""
Public facade for quantity dimension classes.

End users import:
    from qnty.quantity import Pressure, Length
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# Explicit public API (trim as needed)
__all__ = [
    "AbsorbedDose",
    "Pressure",
    "Length",
    "Temperature",
    "Force",
    "Area",
    "Volume",
    # ... add remaining exported dimension classes ...
]

# Internal lazy module cache
__generated_module: Any | None = None


def _load():
    global __generated_module
    if __generated_module is None:
        from ..generated import quantities  # local import for speed on cold start
        __generated_module = quantities
    return __generated_module


# Inject attributes lazily
def __getattr__(name: str):
    if name in __all__:
        mod = _load()
        try:
            return getattr(mod, name)
        except AttributeError:
            raise AttributeError(f"{name} not found in generated quantities") from None
    raise AttributeError(f"module 'qnty.quantities' has no attribute '{name}'")


# Support dir() so tooling/REPLs see symbols
def __dir__():
    return sorted(set(globals().keys()) | set(__all__))


# Static type checking: directly import symbols so type checkers see them.
if TYPE_CHECKING:  # pragma: no cover
    from ..generated.quantities import (
        AbsorbedDose,
        Area,
        Force,
        Length,
        Pressure,
        Temperature,
        Volume,
        # ... mirror list in __all__ ...
    )
