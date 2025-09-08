"""
Main Problem class with consolidated functionality.

This module combines the core Problem functionality including:
- Problem base class with state management and initialization (formerly base.py)
- Variable lifecycle management (formerly variables.py)
- Equation processing pipeline (formerly equations.py)
"""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

from qnty.expressions import BinaryOperation, Constant, VariableReference
from qnty.solving.order import Order
from qnty.solving.solvers import SolverManager
from qnty.utils.logging import get_logger

from ..constants import SOLVER_DEFAULT_MAX_ITERATIONS, SOLVER_DEFAULT_TOLERANCE
from ..equations import Equation, EquationSystem
from ..quantities import FieldQnty, Quantity
from ..units import DimensionlessUnits
from .solving import EquationReconstructor

# Constants for equation processing
MATHEMATICAL_OPERATORS = ["+", "-", "*", "/", " / ", " * ", " + ", " - "]
COMMON_COMPOSITE_VARIABLES = ["P", "c", "S", "E", "W", "Y"]
MAX_ITERATIONS_DEFAULT = SOLVER_DEFAULT_MAX_ITERATIONS
TOLERANCE_DEFAULT = SOLVER_DEFAULT_TOLERANCE


# Custom Exceptions
class VariableNotFoundError(KeyError):
    """Raised when trying to access a variable that doesn't exist."""

    pass


class EquationValidationError(ValueError):
    """Raised when an equation fails validation."""

    pass


class SolverError(RuntimeError):
    """Raised when the solving process fails."""

    pass


class ValidationMixin:
    """Mixin class providing validation functionality."""

    # These attributes will be provided by other mixins in the final Problem class
    logger: Any
    warnings: list[dict[str, Any]]
    validation_checks: list[Callable]

    def add_validation_check(self, check_function: Callable) -> None:
        """Add a validation check function."""
        self.validation_checks.append(check_function)

    def validate(self) -> list[dict[str, Any]]:
        """Run all validation checks and return any warnings."""
        validation_warnings = []

        for check in self.validation_checks:
            try:
                result = check(self)
                if result:
                    validation_warnings.append(result)
            except Exception as e:
                self.logger.debug(f"Validation check failed: {e}")

        return validation_warnings

    def get_warnings(self) -> list[dict[str, Any]]:
        """Get all warnings from the problem."""
        warnings = self.warnings.copy()
        warnings.extend(self.validate())
        return warnings

    def _recreate_validation_checks(self):
        """Collect and integrate validation checks from class-level Check objects."""
        # Clear existing checks
        self.validation_checks = []

        # Collect Check objects from metaclass
        class_checks = getattr(self.__class__, "_class_checks", {})

        for check in class_checks.values():
            # Create a validation function from the Check object
            def make_check_function(check_obj):
                def check_function(problem_instance):
                    return check_obj.evaluate(problem_instance.variables)

                return check_function

            self.validation_checks.append(make_check_function(check))


class Problem(ValidationMixin):
    """
    Main container class for engineering problems.

    This class coordinates all aspects of engineering problem definition, solving, and analysis.
    It supports both programmatic problem construction and class-level inheritance patterns
    for defining domain-specific engineering problems.

    Key Features:
    - Automatic dependency graph construction and topological solving order
    - Dual solving approach: SymPy symbolic solving with numerical fallback
    - Sub-problem composition with automatic variable namespacing
    - Comprehensive validation and error handling
    - Professional report generation capabilities

    Usage Patterns:
    1. Inheritance Pattern (Recommended for domain problems):
       class MyProblem(Problem):
           x = Variable("x", Qty(5.0, length))
           y = Variable("y", Qty(0.0, length), is_known=False)
           eq = y.equals(x * 2)

    2. Programmatic Pattern (For dynamic problems):
       problem = Problem("Dynamic Problem")
       problem.add_variables(x, y)
       problem.add_equation(y.equals(x * 2))

    3. Composition Pattern (For reusable sub-problems):
       class ComposedProblem(Problem):
           sub1 = create_sub_problem()
           sub2 = create_sub_problem()
           # Equations can reference sub1.variable, sub2.variable

    Attributes:
        name (str): Human-readable name for the problem
        description (str): Detailed description of the problem
        variables (dict[str, Variable]): All variables in the problem
        equations (list[Equation]): All equations in the problem
        is_solved (bool): Whether the problem has been successfully solved
        solution (dict[str, Variable]): Solved variable values
        sub_problems (dict[str, Problem]): Integrated sub-problems
    """

    def __init__(self, name: str | None = None, description: str = ""):
        # Handle subclass mode (class-level name/description) vs explicit name
        self.name = name or getattr(self.__class__, "name", self.__class__.__name__)
        self.description = description or getattr(self.__class__, "description", "")

        # Core storage
        self.variables: dict[str, FieldQnty] = {}
        self.equations: list[Equation] = []

        # Internal systems
        self.equation_system = EquationSystem()
        self.dependency_graph = Order()

        # Solving state
        self.is_solved = False
        self.solution: dict[str, FieldQnty] = {}
        self.solving_history: list[dict[str, Any]] = []

        # Performance optimization caches
        self._known_variables_cache: dict[str, FieldQnty] | None = None
        self._unknown_variables_cache: dict[str, FieldQnty] | None = None
        self._cache_dirty = True

        # Validation and warning system
        self.warnings: list[dict[str, Any]] = []
        self.validation_checks: list[Callable] = []

        self.logger = get_logger()
        self.solver_manager = SolverManager(self.logger)

        # Sub-problem composition support
        self.sub_problems: dict[str, Any] = {}
        self.variable_aliases: dict[str, str] = {}

        # Initialize equation reconstructor
        self.equation_reconstructor = None
        self._init_reconstructor()

    def _init_reconstructor(self):
        """Initialize the equation reconstructor."""
        try:
            self.equation_reconstructor = EquationReconstructor(self)
        except Exception as e:
            self.logger.debug(f"Could not initialize equation reconstructor: {e}")
            self.equation_reconstructor = None

    # ========== CACHE MANAGEMENT ==========

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

    # ========== VARIABLE MANAGEMENT ==========

    def add_variable(self, variable: FieldQnty) -> None:
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
        if hasattr(variable, "_parent_problem"):
            setattr(variable, "_parent_problem", self)
        # Also set as instance attribute for dot notation access
        if variable.symbol is not None:
            setattr(self, variable.symbol, variable)
        self.is_solved = False
        self._invalidate_caches()

    def add_variables(self, *variables: FieldQnty) -> None:
        """Add multiple variables to the problem."""
        for var in variables:
            self.add_variable(var)

    def get_variable(self, symbol: str) -> FieldQnty:
        """Get a variable by its symbol."""
        if symbol not in self.variables:
            raise VariableNotFoundError(f"Variable '{symbol}' not found in problem '{self.name}'.")
        return self.variables[symbol]

    def get_known_variables(self) -> dict[str, FieldQnty]:
        """Get all known variables."""
        if self._cache_dirty or self._known_variables_cache is None:
            self._update_variable_caches()
        return self._known_variables_cache.copy() if self._known_variables_cache else {}

    def get_unknown_variables(self) -> dict[str, FieldQnty]:
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
    def known_variables(self) -> dict[str, FieldQnty]:
        """Get all variables marked as known."""
        return self.get_known_variables()

    @property
    def unknown_variables(self) -> dict[str, FieldQnty]:
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

    def mark_known(self, **symbol_values: Quantity):
        """Mark variables as known and set their values."""
        for symbol, quantity in symbol_values.items():
            if symbol in self.variables:
                # Set the quantity first, then mark as known
                self.variables[symbol].quantity = quantity
                self.variables[symbol].mark_known()
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
        if not hasattr(self, "dependency_graph") or not self.dependency_graph:
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
        placeholder_var = FieldQnty(name=f"Auto-created: {symbol}", expected_dimension=DimensionlessUnits.dimensionless.dimension, is_known=False)
        placeholder_var.symbol = symbol
        placeholder_var.quantity = Quantity(0.0, DimensionlessUnits.dimensionless)
        self.add_variable(placeholder_var)
        self.logger.debug(f"Auto-created placeholder variable: {symbol}")

    def _clone_variable(self, variable: FieldQnty) -> FieldQnty:
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
        if hasattr(variable, "validation_checks") and hasattr(cloned, "validation_checks"):
            cloned.validation_checks = []
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

    # ========== EQUATION MANAGEMENT ==========

    def add_equation(self, equation: Equation) -> None:
        """
        Add an equation to the problem.

        The equation will be validated to ensure all referenced variables exist.
        Missing variables that look like simple identifiers will be auto-created
        as unknown placeholders.

        Args:
            equation: Equation object to add to the problem

        Raises:
            EquationValidationError: If the equation is invalid or cannot be processed

        Note:
            Adding an equation resets the problem to unsolved state.
        """
        if equation is None:
            raise EquationValidationError("Cannot add None equation to problem")

        # Fix VariableReferences in equation to point to correct Variables
        equation = self._fix_variable_references(equation)

        # Validate that all variables in the equation exist
        try:
            equation_vars = equation.get_all_variables()
        except Exception as e:
            raise EquationValidationError(f"Failed to extract variables from equation: {e}") from e

        missing_vars = [var for var in equation_vars if var not in self.variables]

        if missing_vars:
            self._handle_missing_variables(missing_vars)

            # Check again for remaining missing variables
            equation_vars = equation.get_all_variables()
            remaining_missing = [var for var in equation_vars if var not in self.variables]
            if remaining_missing:
                self.logger.warning(f"Equation references missing variables: {remaining_missing}")

        self.equations.append(equation)
        self.equation_system.add_equation(equation)
        self.is_solved = False

    def add_equations(self, *equations: Equation):
        """Add multiple equations to the problem."""
        for eq in equations:
            self.add_equation(eq)
        return self

    def _handle_missing_variables(self, missing_vars: list[str]) -> None:
        """Handle missing variables by creating placeholders for simple symbols."""
        for missing_var in missing_vars:
            if self._is_simple_variable_symbol(missing_var):
                self._create_placeholder_variable(missing_var)

    def _is_simple_variable_symbol(self, symbol: str) -> bool:
        """Check if a symbol looks like a simple variable identifier."""
        return symbol.isidentifier() and not any(char in symbol for char in ["(", ")", "+", "-", "*", "/", " "])

    def _fix_variable_references(self, equation: Equation) -> Equation:
        """
        Fix VariableReferences in equation expressions to point to Variables in problem.variables.

        This resolves issues where expression trees contain VariableReferences pointing to
        proxy Variables from class creation time instead of the actual Variables in the problem.
        """
        try:
            # Fix the RHS expression
            fixed_rhs = self._fix_expression_variables(equation.rhs)

            # Create new equation with fixed RHS (LHS should already be correct)
            return Equation(equation.name, equation.lhs, fixed_rhs)

        except Exception as e:
            self.logger.debug(f"Error fixing variable references in equation {equation.name}: {e}")
            return equation  # Return original if fixing fails

    def _fix_expression_variables(self, expr):
        """
        Recursively fix VariableReferences in an expression tree to point to correct Variables.
        """

        if isinstance(expr, VariableReference):
            # Check if this VariableReference points to the wrong Variable
            symbol = getattr(expr, "symbol", None)
            if symbol and symbol in self.variables:
                correct_var = self.variables[symbol]
                if expr.variable is not correct_var:
                    # Create new VariableReference pointing to correct Variable
                    return VariableReference(correct_var)
            return expr

        elif isinstance(expr, BinaryOperation):
            # Recursively fix left and right operands
            fixed_left = self._fix_expression_variables(expr.left)
            fixed_right = self._fix_expression_variables(expr.right)
            return BinaryOperation(expr.operator, fixed_left, fixed_right)

        elif hasattr(expr, "operand"):
            # Recursively fix operand
            fixed_operand = self._fix_expression_variables(expr.operand)
            return type(expr)(expr.operator, fixed_operand)

        elif hasattr(expr, "function_name"):
            # Recursively fix left and right operands
            fixed_left = self._fix_expression_variables(expr.left)
            fixed_right = self._fix_expression_variables(expr.right)
            return type(expr)(expr.function_name, fixed_left, fixed_right)

        elif isinstance(expr, Constant):
            return expr

        else:
            # Unknown expression type, return as-is
            return expr

    # ========== SOLVING ==========

    def solve(self, max_iterations: int = MAX_ITERATIONS_DEFAULT, tolerance: float = TOLERANCE_DEFAULT) -> dict[str, Any]:
        """
        Solve the engineering problem by finding values for all unknown variables.

        This method orchestrates the complete solving process:
        1. Builds dependency graph from equations
        2. Determines optimal solving order using topological sorting
        3. Solves equations iteratively using symbolic/numerical methods
        4. Verifies solution against all equations
        5. Updates variable states and synchronizes instance attributes

        Args:
            max_iterations: Maximum number of solving iterations (default: 100)
            tolerance: Numerical tolerance for convergence (default: SOLVER_DEFAULT_TOLERANCE)

        Returns:
            dict mapping variable symbols to solved Variable objects

        Raises:
            SolverError: If solving fails or times out

        Example:
            >>> problem = MyEngineeringProblem()
            >>> solution = problem.solve()
            >>> print(f"Force = {solution['F'].quantity}")
        """
        self.logger.info(f"Solving problem: {self.name}")

        try:
            # Clear previous solution
            self.solution = {}
            self.is_solved = False
            self.solving_history = []

            # Build dependency graph
            self._build_dependency_graph()

            # Use solver manager to solve the system
            solve_result = self.solver_manager.solve(self.equations, self.variables, self.dependency_graph, max_iterations, tolerance)

            if solve_result.success:
                # Update variables with the result
                self.variables = solve_result.variables
                self.solving_history.extend(solve_result.steps)

                # Sync solved values back to instance attributes
                self._sync_variables_to_instance_attributes()

                # Verify solution
                self.solution = self.variables
                verification_passed = self.verify_solution()

                # Mark as solved based on solver result and verification
                if verification_passed:
                    self.is_solved = True
                    self.logger.info("Solution verified successfully")
                    return self.solution
                else:
                    self.logger.warning("Solution verification failed")
                    return self.solution
            else:
                raise SolverError(f"Solving failed: {solve_result.message}")

        except SolverError:
            raise
        except Exception as e:
            self.logger.error(f"Solving failed: {e}")
            raise SolverError(f"Unexpected error during solving: {e}") from e

    def _build_dependency_graph(self):
        """Build the dependency graph for solving order determination."""
        # Reset the dependency graph
        self.dependency_graph = Order()

        # Get known variables
        known_vars = self.get_known_symbols()

        # Add dependencies from equations
        for equation in self.equations:
            self.dependency_graph.add_equation(equation, known_vars)

    def verify_solution(self, tolerance: float = SOLVER_DEFAULT_TOLERANCE) -> bool:
        """Verify that all equations are satisfied."""
        if not self.equations:
            return True

        try:
            for equation in self.equations:
                if not equation.check_residual(self.variables, tolerance):
                    self.logger.debug(f"Equation verification failed: {equation}")
                    return False
            return True
        except Exception as e:
            self.logger.debug(f"Solution verification error: {e}")
            return False

    def analyze_system(self) -> dict[str, Any]:
        """Analyze the equation system for solvability, cycles, etc."""
        try:
            self._build_dependency_graph()
            known_vars = self.get_known_symbols()
            analysis = self.dependency_graph.analyze_system(known_vars)

            # Add some additional info
            analysis["total_equations"] = len(self.equations)
            analysis["is_determined"] = len(self.get_unknown_variables()) <= len(self.equations)

            return analysis
        except Exception as e:
            self.logger.debug(f"Dependency analysis failed: {e}")
            # Return basic analysis on failure
            return {
                "total_variables": len(self.variables),
                "known_variables": len(self.get_known_variables()),
                "unknown_variables": len(self.get_unknown_variables()),
                "total_equations": len(self.equations),
                "is_determined": len(self.get_unknown_variables()) <= len(self.equations),
                "has_cycles": False,
                "solving_order": [],
                "can_solve_completely": False,
                "unsolvable_variables": [],
            }

    # ========== UTILITY METHODS ==========

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
        if not hasattr(self, "variables") or name.startswith("_"):
            super().__setattr__(name, value)
            return

        # If setting a variable that exists in our variables dict, update both
        if isinstance(value, FieldQnty) and hasattr(self, "variables") and name in self.variables:
            self.variables[name] = value

        super().__setattr__(name, value)

    def __getitem__(self, key: str):
        """Allow dict-like access to variables."""
        return self.get_variable(key)

    def __setitem__(self, key: str, value) -> None:
        """Allow dict-like assignment of variables."""
        if isinstance(value, FieldQnty):
            # Update the symbol to match the key if they differ
            if value.symbol != key:
                value.symbol = key
            self.add_variable(value)

    # ========== CLASS-LEVEL EXTRACTION ==========
    # Note: _extract_from_class_variables() is provided by CompositionMixin in the full Problem class


# Alias for backward compatibility
EngineeringProblem = Problem

# Export all relevant classes and exceptions
__all__ = ["Problem", "EngineeringProblem", "VariableNotFoundError", "EquationValidationError", "SolverError", "ValidationMixin"]
