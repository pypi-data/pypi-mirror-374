"""
Equation System
===============

Mathematical equations for qnty variables with solving capabilities.
"""

from __future__ import annotations

import logging
from typing import cast

from ..constants import SOLVER_DEFAULT_TOLERANCE
from ..expressions import Expression, VariableReference
from ..quantities import FieldQnty
from ..utils.scope_discovery import ScopeDiscoveryService

_logger = logging.getLogger(__name__)

# Global optimization flags
_SCOPE_DISCOVERY_ENABLED = False  # Disabled by default due to high overhead


class Equation:
    """
    Represents a mathematical equation with left-hand side equal to right-hand side.
    Optimized with __slots__ for memory efficiency.
    """

    __slots__ = ("name", "lhs", "rhs", "_variables")

    def __init__(self, name: str, lhs: FieldQnty | Expression, rhs: Expression):
        self.name = name

        # Convert Variable to VariableReference if needed - use isinstance for performance
        if isinstance(lhs, FieldQnty):
            self.lhs = VariableReference(lhs)
        else:
            # It's already an Expression
            self.lhs = cast(Expression, lhs)

        self.rhs = rhs
        self._variables: set[str] | None = None  # Lazy initialization for better performance

    def get_all_variables(self) -> set[str]:
        """Get all variable names used in this equation."""
        if self._variables is None:
            # Both lhs and rhs should be Expressions after __init__ conversion
            lhs_vars = self.lhs.get_variables()
            rhs_vars = self.rhs.get_variables()
            self._variables = lhs_vars | rhs_vars
        return self._variables

    @property
    def variables(self) -> set[str]:
        """Get all variable names used in this equation (cached property)."""
        return self.get_all_variables()

    def get_unknown_variables(self, known_vars: set[str]) -> set[str]:
        """Get variables that are unknown (not in known_vars set)."""
        return self.variables - known_vars

    def get_known_variables(self, known_vars: set[str]) -> set[str]:
        """Get variables that are known (in known_vars set)."""
        return self.variables & known_vars

    def can_solve_for(self, target_var: str, known_vars: set[str]) -> bool:
        """Check if this equation can solve for target_var given known_vars."""
        if target_var not in self.variables:
            return False

        # Direct assignment case: lhs is the variable
        if isinstance(self.lhs, VariableReference) and self.lhs.name == target_var:
            rhs_vars = self.rhs.get_variables()
            return rhs_vars.issubset(known_vars)

        # General case: can solve if target_var is the only unknown
        unknown_vars = self.get_unknown_variables(known_vars)
        return unknown_vars == {target_var}

    def solve_for(self, target_var: str, variable_values: dict[str, FieldQnty]) -> FieldQnty:
        """
        Solve the equation for target_var.
        Returns the target variable with updated quantity.
        """
        if target_var not in self.variables:
            raise ValueError(f"Variable '{target_var}' not found in equation")

        # Only handle direct assignment: target = expression
        if not (isinstance(self.lhs, VariableReference) and self.lhs.name == target_var):
            raise NotImplementedError(f"Cannot solve for {target_var} in equation {self}. Only direct assignment equations (var = expression) are supported.")

        # Direct assignment: target_var = rhs
        result_qty = self.rhs.evaluate(variable_values)

        # Get the variable object to update
        var_obj = variable_values.get(target_var)
        if var_obj is None:
            raise ValueError(f"Variable '{target_var}' not found in variable_values")

        # Convert result to the target variable's original unit if it had one
        if var_obj.quantity is not None and var_obj.quantity.unit is not None:
            try:
                result_qty = result_qty.to(var_obj.quantity.unit)
            except (ValueError, TypeError, AttributeError) as e:
                _logger.debug(f"Unit conversion failed for {target_var}: {e}. Using calculated unit.")

        # Update the variable and return it
        var_obj.quantity = result_qty
        var_obj.is_known = True
        return var_obj

    def check_residual(self, variable_values: dict[str, FieldQnty], tolerance: float = SOLVER_DEFAULT_TOLERANCE) -> bool:
        """
        Check if equation is satisfied by evaluating residual (LHS - RHS).
        Returns True if |residual| < tolerance, accounting for units.
        """
        try:
            # Both lhs and rhs should be Expressions after __init__ conversion
            lhs_value = self.lhs.evaluate(variable_values)
            rhs_value = self.rhs.evaluate(variable_values)

            # Check dimensional compatibility using public API
            if not self._are_dimensionally_compatible(lhs_value, rhs_value):
                return False

            # Convert to same units for comparison
            rhs_converted = rhs_value.to(lhs_value.unit)
            residual = abs(lhs_value.value - rhs_converted.value)

            return residual < tolerance
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            _logger.debug(f"Expected error in residual check for equation '{self.name}': {e}")
            return False
        except Exception as e:
            error_msg = f"Unexpected error in residual check for equation '{self.name}': {e}"
            _logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _discover_variables_from_scope(self) -> dict[str, FieldQnty]:
        """
        Automatically discover variables from the calling scope using centralized service.
        """
        if not _SCOPE_DISCOVERY_ENABLED:
            return {}

        # Use centralized scope discovery service
        return ScopeDiscoveryService.discover_variables(self.variables, enable_caching=True)

    def _are_dimensionally_compatible(self, lhs_value, rhs_value) -> bool:
        """Check if two quantities are dimensionally compatible."""
        try:
            # Try to convert - if successful, they're compatible
            rhs_value.to(lhs_value.unit)
            return True
        except (ValueError, TypeError, AttributeError):
            return False

    def _analyze_variable_states(self, discovered: dict[str, FieldQnty]) -> dict[str, str]:
        """Analyze which variables are known vs unknown."""
        states = {}
        for var_name in self.variables:
            if var_name not in discovered:
                states[var_name] = "missing"
            else:
                var = discovered[var_name]
                if hasattr(var, "is_known") and not var.is_known:
                    states[var_name] = "unknown"
                elif hasattr(var, "quantity") and var.quantity is not None:
                    states[var_name] = "known"
                else:
                    states[var_name] = "unknown"
        return states

    def _determine_solvability(self, states: dict[str, str], discovered: dict[str, FieldQnty]) -> tuple[bool, str, dict[str, FieldQnty]]:
        """Determine if equation can be solved based on variable states."""
        if "missing" in states.values():
            return False, "", {}

        unknowns = [name for name, state in states.items() if state == "unknown"]

        # Can only auto-solve if there's exactly one unknown
        if len(unknowns) == 1:
            return True, unknowns[0], discovered

        return False, "", {}

    def _can_auto_solve(self) -> tuple[bool, str, dict[str, FieldQnty]]:
        """Check if equation can be auto-solved from scope using centralized service."""
        try:
            discovered = self._discover_variables_from_scope()
            if not discovered:
                return False, "", {}

            variable_states = self._analyze_variable_states(discovered)
            return self._determine_solvability(variable_states, discovered)

        except (AttributeError, KeyError, ValueError, TypeError) as e:
            _logger.debug(f"Cannot auto-solve equation '{self.name}': {e}")
            return False, "", {}

    def _try_auto_solve(self) -> bool:
        """Try to automatically solve the equation if possible."""
        try:
            can_solve, target_var, variables = self._can_auto_solve()
            if can_solve:
                self.solve_for(target_var, variables)
                return True
            return False
        except (AttributeError, KeyError, ValueError, TypeError) as e:
            _logger.debug(f"Auto-solve failed for equation '{self.name}': {e}")
            return False

    def __str__(self) -> str:
        # Try to auto-solve if possible before displaying
        self._try_auto_solve()
        return f"{self.lhs} = {self.rhs}"

    def __repr__(self) -> str:
        return f"Equation(name='{self.name}', lhs={self.lhs!r}, rhs={self.rhs!r})"
