"""
Core Problem base class with state management and initialization.

This module contains the foundational Problem class with core state,
initialization logic, caching, and utility methods.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qnty.quantities import TypeSafeVariable as Variable

from qnty.equations import EquationSystem
from qnty.problem.reconstruction import EquationReconstructor
from qnty.solving.order import Order
from qnty.solving.solvers import SolverManager
from qnty.utils.logging import get_logger


class ProblemBase:
    """
    Base class for Problem with core state management and initialization.
    
    This class provides the foundational structure for engineering problems,
    including variable storage, equation management, caching, and logging.
    """
    
    def __init__(self, name: str | None = None, description: str = ""):
        # Handle subclass mode (class-level name/description) vs explicit name
        self.name = name or getattr(self.__class__, 'name', self.__class__.__name__)
        self.description = description or getattr(self.__class__, 'description', "")
        
        # Core storage
        self.variables: dict[str, Variable] = {}
        self.equations: list = []  # Will be properly typed when importing Equation
        
        # Internal systems
        self.equation_system = EquationSystem()
        self.dependency_graph = Order()
        
        # Solving state
        self.is_solved = False
        self.solution: dict[str, Variable] = {}
        self.solving_history: list[dict[str, Any]] = []
        
        # Performance optimization caches
        self._known_variables_cache: dict[str, Variable] | None = None
        self._unknown_variables_cache: dict[str, Variable] | None = None
        self._cache_dirty = True
        
        # Validation and warning system
        self.warnings: list[dict[str, Any]] = []
        self.validation_checks: list = []  # Will be properly typed when importing Callable
        
        self.logger = get_logger()
        self.solver_manager = SolverManager(self.logger)
        
        # Sub-problem composition support
        self.sub_problems: dict[str, Any] = {}  # Will be properly typed as Problem
        self.variable_aliases: dict[str, str] = {}  # Maps alias -> original variable symbol
        
        # Initialize equation reconstructor
        self.equation_reconstructor = EquationReconstructor(self)

    def _invalidate_caches(self) -> None:
        """Invalidate performance caches when variables change."""
        self._cache_dirty = True

    def _update_variable_caches(self) -> None:
        """Update the variable caches for performance."""
        if not self._cache_dirty:
            return
            
        self._known_variables_cache = {symbol: var for symbol, var in self.variables.items() if var.is_known}
        self._unknown_variables_cache = {symbol: var for symbol, var in self.variables.items() if not var.is_known}
        self._cache_dirty = False

    def reset_solution(self):
        """Reset the problem to unsolved state."""
        self.is_solved = False
        self.solution = {}
        self.solving_history = []
        
        # Reset unknown variables to unknown state
        for var in self.variables.values():
            if not var.is_known:
                var.is_known = False

    def copy(self):
        """Create a copy of this problem."""
        from copy import deepcopy
        return deepcopy(self)

    def __str__(self) -> str:
        """String representation of the problem."""
        status = "SOLVED" if self.is_solved else "UNSOLVED"
        return f"EngineeringProblem('{self.name}', vars={len(self.variables)}, eqs={len(self.equations)}, {status})"

    def __repr__(self) -> str:
        """Detailed representation of the problem."""
        return self.__str__()

    def __setattr__(self, name: str, value: Any) -> None:
        """Custom attribute setting to maintain variable synchronization."""
        # During initialization, use normal attribute setting
        if not hasattr(self, 'variables') or name.startswith('_'):
            super().__setattr__(name, value)
            return
        
        # Import here to avoid circular imports
        try:
            from qnty.quantities import TypeSafeVariable as Variable
            # If setting a variable that exists in our variables dict, update both
            if isinstance(value, Variable) and name in self.variables:
                self.variables[name] = value
        except ImportError:
            pass
        
        super().__setattr__(name, value)

    def __getitem__(self, key: str):
        """Allow dict-like access to variables."""
        from .variables import VariablesMixin
        # Type ignore: self will have VariablesMixin via multiple inheritance
        return VariablesMixin.get_variable(self, key)  # type: ignore[arg-type]

    def __setitem__(self, key: str, value) -> None:
        """Allow dict-like assignment of variables."""
        # Import here to avoid circular imports
        try:
            from qnty.quantities import TypeSafeVariable as Variable
            if isinstance(value, Variable):
                # Update the symbol to match the key if they differ
                if value.symbol != key:
                    value.symbol = key
                from .variables import VariablesMixin
                # Type ignore: self will have VariablesMixin via multiple inheritance
                VariablesMixin.add_variable(self, value)  # type: ignore[arg-type]
        except ImportError:
            pass
