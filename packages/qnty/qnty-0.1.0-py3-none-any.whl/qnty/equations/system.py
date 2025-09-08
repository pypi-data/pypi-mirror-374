from ..quantities import FieldQnty
from .equation import Equation


class EquationSystem:
    """
    System of equations that can be solved together.
    Optimized with __slots__ for memory efficiency.
    """

    __slots__ = ("equations", "variables", "_known_cache", "_unknown_cache")

    def __init__(self, equations: list[Equation] | None = None):
        self.equations = equations or []
        self.variables: dict[str, FieldQnty] = {}  # Dict[str, FieldQnty]
        self._known_cache: set[str] | None = None  # Cache for known variables
        self._unknown_cache: set[str] | None = None  # Cache for unknown variables

    def add_equation(self, equation: Equation):
        """Add an equation to the system."""
        self.equations.append(equation)
        self._invalidate_caches()

    def add_variable(self, variable: FieldQnty):
        """Add a variable to the system."""
        self.variables[variable.name] = variable
        self._invalidate_caches()

    def _invalidate_caches(self):
        """Invalidate cached known/unknown variable sets."""
        self._known_cache = None
        self._unknown_cache = None

    def _is_variable_known(self, var: FieldQnty) -> bool:
        """Determine if a variable should be considered known."""
        return var.is_known and var.quantity is not None

    def get_known_variables(self) -> set[str]:
        """Get names of all known variables (cached)."""
        if self._known_cache is None:
            self._known_cache = {name for name, var in self.variables.items() if self._is_variable_known(var)}
        return self._known_cache

    def get_unknown_variables(self) -> set[str]:
        """Get names of all unknown variables (cached)."""
        if self._unknown_cache is None:
            self._unknown_cache = {name for name, var in self.variables.items() if not self._is_variable_known(var)}
        return self._unknown_cache

    def _find_solvable_equation_variable_pair(self, known_vars: set[str], unknown_vars: set[str]) -> tuple[Equation, str] | None:
        """Find the first equation-variable pair that can be solved."""
        for equation in self.equations:
            for unknown_var in unknown_vars:
                if equation.can_solve_for(unknown_var, known_vars):
                    return equation, unknown_var
        return None

    def can_solve_any(self) -> bool:
        """Check if any equation can be solved with current known variables."""
        known_vars = self.get_known_variables()
        unknown_vars = self.get_unknown_variables()
        return self._find_solvable_equation_variable_pair(known_vars, unknown_vars) is not None

    def solve_step(self) -> bool:
        """Solve one step - find and solve one equation. Returns True if progress made."""
        known_vars = self.get_known_variables()
        unknown_vars = self.get_unknown_variables()

        pair = self._find_solvable_equation_variable_pair(known_vars, unknown_vars)
        if pair is None:
            return False

        equation, unknown_var = pair
        equation.solve_for(unknown_var, self.variables)
        self._invalidate_caches()
        return True

    def solve(self, max_iterations: int = 100) -> bool:
        """Solve the system iteratively. Returns True if fully solved."""
        if max_iterations <= 0:
            raise ValueError("max_iterations must be positive")

        for _ in range(max_iterations):
            if not self.can_solve_any():
                break
            if not self.solve_step():
                break

        # Check if all variables are known
        unknown_vars = self.get_unknown_variables()
        return len(unknown_vars) == 0

    def _get_next_solvable_variable(self, simulated_known: set[str]) -> str | None:
        """Find the next variable that can be solved given current known variables."""
        unknown_vars = {name for name in self.variables.keys() if name not in simulated_known}
        if not unknown_vars:
            return None

        for equation in self.equations:
            for unknown_var in unknown_vars:
                if equation.can_solve_for(unknown_var, simulated_known):
                    return unknown_var
        return None

    def get_solving_order(self) -> list[str]:
        """
        Get the order in which variables can be solved.
        Optimized to avoid creating full system copies.
        """
        order = []
        simulated_known = self.get_known_variables().copy()

        max_iterations = len(self.variables)  # Prevent infinite loops
        for _ in range(max_iterations):
            next_var = self._get_next_solvable_variable(simulated_known)
            if next_var is None:
                break

            order.append(next_var)
            simulated_known.add(next_var)

        return order

    def __str__(self) -> str:
        known_count = len(self.get_known_variables())
        total_vars = len(self.variables)
        return f"EquationSystem({len(self.equations)} equations, {known_count}/{total_vars} variables known)"

    def __repr__(self) -> str:
        return f"EquationSystem(equations={self.equations!r})"
