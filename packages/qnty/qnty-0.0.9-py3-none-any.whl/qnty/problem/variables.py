"""
Variable lifecycle management for Problem class.

This module contains all variable-related operations including adding,
getting, managing known/unknown state, and variable caching.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qnty.quantities import Quantity as Qty
    from qnty.quantities import TypeSafeVariable as Variable

from qnty.generated.units import DimensionlessUnits
from qnty.quantities import Quantity as Qty
from qnty.quantities import TypeSafeVariable as Variable


# Custom Exceptions
class VariableNotFoundError(KeyError):
    """Raised when trying to access a variable that doesn't exist."""
    pass


class VariablesMixin:
    """Mixin class providing variable management functionality."""
    
    # These attributes/methods will be provided by other mixins in the final Problem class
    variables: dict[str, Variable]
    name: str
    logger: Any
    is_solved: bool
    sub_problems: dict[str, Any]
    dependency_graph: Any
    _known_variables_cache: dict[str, Variable] | None
    _unknown_variables_cache: dict[str, Variable] | None
    _cache_dirty: bool
    
    def _invalidate_caches(self) -> None:
        """Will be provided by ProblemBase."""
        ...
    
    def _update_variable_caches(self) -> None:
        """Will be provided by ProblemBase."""
        ...

    def add_variable(self, variable: Variable) -> None:
        """
        Add a variable to the problem.
        
        The variable will be available for use in equations and can be accessed
        via both dictionary notation (problem['symbol']) and attribute notation
        (problem.symbol).
        
        Args:
            variable: Variable object to add to the problem
            
        Note:
            If a variable with the same symbol already exists, it will be replaced
            and a warning will be logged.
        """
        if variable.symbol in self.variables:
            self.logger.warning(f"Variable {variable.symbol} already exists. Replacing.")
        
        if variable.symbol is not None:
            self.variables[variable.symbol] = variable
        # Set parent problem reference for dependency invalidation
        try:
            variable._parent_problem = self
        except (AttributeError, TypeError):
            # _parent_problem might not be settable
            pass
        # Also set as instance attribute for dot notation access
        if variable.symbol is not None:
            setattr(self, variable.symbol, variable)
        self.is_solved = False
        self._invalidate_caches()

    def add_variables(self, *variables: Variable) -> None:
        """Add multiple variables to the problem."""
        for var in variables:
            self.add_variable(var)

    def get_variable(self, symbol: str) -> Variable:
        """Get a variable by its symbol."""
        if symbol not in self.variables:
            raise VariableNotFoundError(f"Variable '{symbol}' not found in problem '{self.name}'.")
        return self.variables[symbol]
    
    def get_known_variables(self) -> dict[str, Variable]:
        """Get all known variables."""
        if self._cache_dirty or self._known_variables_cache is None:
            self._update_variable_caches()
        return self._known_variables_cache.copy() if self._known_variables_cache else {}

    def get_unknown_variables(self) -> dict[str, Variable]:
        """Get all unknown variables."""
        if self._cache_dirty or self._unknown_variables_cache is None:
            self._update_variable_caches()
        return self._unknown_variables_cache.copy() if self._unknown_variables_cache else {}

    def get_known_symbols(self) -> set[str]:
        """Get symbols of all known variables."""
        return {symbol for symbol, var in self.variables.items() if var.is_known}

    def get_unknown_symbols(self) -> set[str]:
        """Get symbols of all unknown variables."""
        return {symbol for symbol, var in self.variables.items() if not var.is_known}
    
    def get_known_variable_symbols(self) -> set[str]:
        """Alias for get_known_symbols for compatibility."""
        return self.get_known_symbols()
    
    def get_unknown_variable_symbols(self) -> set[str]:
        """Alias for get_unknown_symbols for compatibility."""
        return self.get_unknown_symbols()
    
    # Properties for compatibility
    @property
    def known_variables(self) -> dict[str, Variable]:
        """Get all variables marked as known."""
        return self.get_known_variables()
    
    @property
    def unknown_variables(self) -> dict[str, Variable]:
        """Get all variables marked as unknown."""
        return self.get_unknown_variables()

    def mark_unknown(self, *symbols: str):
        """Mark variables as unknown (to be solved for)."""
        for symbol in symbols:
            if symbol in self.variables:
                self.variables[symbol].mark_unknown()
            else:
                raise VariableNotFoundError(f"Variable '{symbol}' not found in problem '{self.name}'")
        self.is_solved = False
        self._invalidate_caches()
        return self
    
    def mark_known(self, **symbol_values: Qty):
        """Mark variables as known and set their values."""
        for symbol, quantity in symbol_values.items():
            if symbol in self.variables:
                self.variables[symbol].mark_known(quantity)
            else:
                raise VariableNotFoundError(f"Variable '{symbol}' not found in problem '{self.name}'")
        self.is_solved = False
        self._invalidate_caches()
        return self

    def invalidate_dependents(self, changed_variable_symbol: str) -> None:
        """
        Mark all variables that depend on the changed variable as unknown.
        This ensures they get recalculated when the problem is re-solved.
        
        Args:
            changed_variable_symbol: Symbol of the variable whose value changed
        """
        if not hasattr(self, 'dependency_graph') or not self.dependency_graph:
            # If dependency graph hasn't been built yet, we can't invalidate
            return
            
        # Get all variables that depend on the changed variable
        dependent_vars = self.dependency_graph.graph.get(changed_variable_symbol, [])
        
        # Mark each dependent variable as unknown
        for dependent_symbol in dependent_vars:
            if dependent_symbol in self.variables:
                var = self.variables[dependent_symbol]
                # Only mark as unknown if it was previously solved (known)
                if var.is_known:
                    var.mark_unknown()
                    # Recursively invalidate variables that depend on this one
                    self.invalidate_dependents(dependent_symbol)
        
        # Mark problem as needing re-solving
        self.is_solved = False
        self._invalidate_caches()

    def _create_placeholder_variable(self, symbol: str) -> None:
        """Create a placeholder variable for a missing symbol."""
        
        placeholder_var = Variable(
            name=f"Auto-created: {symbol}",
            expected_dimension=DimensionlessUnits.dimensionless.dimension,
            is_known=False
        )
        placeholder_var.symbol = symbol
        placeholder_var.quantity = Qty(0.0, DimensionlessUnits.dimensionless)
        self.add_variable(placeholder_var)
        self.logger.debug(f"Auto-created placeholder variable: {symbol}")

    def _clone_variable(self, variable: Variable) -> Variable:
        """Create a copy of a variable to avoid shared state without corrupting global units."""
        # Create a new variable of the same exact type to preserve .equals() method
        # This ensures domain-specific variables (Length, Pressure, etc.) keep their type
        variable_type = type(variable)
        
        # Use __new__ to avoid constructor parameter issues
        cloned = variable_type.__new__(variable_type)
        
        # Initialize manually with the same attributes as the original
        cloned.name = variable.name
        cloned.symbol = variable.symbol
        cloned.expected_dimension = variable.expected_dimension
        cloned.quantity = variable.quantity  # Keep reference to same quantity - units must not be copied
        cloned.is_known = variable.is_known
        
        # Ensure the cloned variable has fresh validation checks
        if hasattr(variable, 'validation_checks'):
            try:
                cloned.validation_checks = []
            except (AttributeError, TypeError):
                # validation_checks might be read-only or not settable
                pass
        return cloned

    def _sync_variables_to_instance_attributes(self):
        """
        Sync variable objects to instance attributes after solving.
        This ensures that self.P refers to the same Variable object that's in self.variables.
        Variables maintain their original dimensional types (e.g., AreaVariable, PressureVariable).
        """
        for var_symbol, var in self.variables.items():
            # Update instance attribute if it exists
            if hasattr(self, var_symbol):
                # Variables preserve their dimensional types during solving
                setattr(self, var_symbol, var)
        
        # Also update sub-problem namespace objects
        for namespace, sub_problem in self.sub_problems.items():
            if hasattr(self, namespace):
                namespace_obj = getattr(self, namespace)
                for var_symbol in sub_problem.variables:
                    namespaced_symbol = f"{namespace}_{var_symbol}"
                    if namespaced_symbol in self.variables and hasattr(namespace_obj, var_symbol):
                        setattr(namespace_obj, var_symbol, self.variables[namespaced_symbol])
