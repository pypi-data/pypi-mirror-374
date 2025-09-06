from ..quantities.quantity import TypeSafeVariable
from .equation import Equation


class EquationSystem:
    """
    System of equations that can be solved together.
    Optimized with __slots__ for memory efficiency.
    """
    __slots__ = ('equations', 'variables', '_known_cache', '_unknown_cache')
    
    def __init__(self, equations: list[Equation] | None = None):
        self.equations = equations or []
        self.variables = {}  # Dict[str, TypeSafeVariable]
        self._known_cache: set[str] | None = None  # Cache for known variables
        self._unknown_cache: set[str] | None = None  # Cache for unknown variables
    
    def add_equation(self, equation: Equation):
        """Add an equation to the system."""
        self.equations.append(equation)
        self._invalidate_caches()
    
    def add_variable(self, variable: TypeSafeVariable):
        """Add a variable to the system."""
        self.variables[variable.name] = variable
        self._invalidate_caches()
    
    def _invalidate_caches(self):
        """Invalidate cached known/unknown variable sets."""
        self._known_cache = None
        self._unknown_cache = None
    
    def get_known_variables(self) -> set[str]:
        """Get names of all known variables (cached)."""
        if self._known_cache is None:
            self._known_cache = {name for name, var in self.variables.items() if var.is_known and var.quantity is not None}
        return self._known_cache
    
    def get_unknown_variables(self) -> set[str]:
        """Get names of all unknown variables (cached)."""
        if self._unknown_cache is None:
            self._unknown_cache = {name for name, var in self.variables.items() if not var.is_known or var.quantity is None}
        return self._unknown_cache
    
    def can_solve_any(self) -> bool:
        """Check if any equation can be solved with current known variables."""
        known_vars = self.get_known_variables()
        unknown_vars = self.get_unknown_variables()
        
        for equation in self.equations:
            for unknown_var in unknown_vars:
                if equation.can_solve_for(unknown_var, known_vars):
                    return True
        return False
    
    def solve_step(self) -> bool:
        """Solve one step - find and solve one equation. Returns True if progress made."""
        known_vars = self.get_known_variables()
        unknown_vars = self.get_unknown_variables()
        
        # Find an equation that can be solved
        for equation in self.equations:
            for unknown_var in unknown_vars:
                if equation.can_solve_for(unknown_var, known_vars):
                    # Solve for this variable
                    equation.solve_for(unknown_var, self.variables)
                    # Invalidate caches since variable states have changed
                    self._invalidate_caches()
                    return True  # Progress made
        
        return False  # No progress possible
    
    def solve(self, max_iterations: int = 100) -> bool:
        """Solve the system iteratively. Returns True if fully solved."""
        for _ in range(max_iterations):
            if not self.can_solve_any():
                break
            if not self.solve_step():
                break
        
        # Check if all variables are known
        unknown_vars = self.get_unknown_variables()
        return len(unknown_vars) == 0
    
    def get_solving_order(self) -> list[str]:
        """
        Get the order in which variables can be solved.
        Optimized to avoid creating full system copies.
        """
        order = []
        # Track known variables without modifying the original
        simulated_known = self.get_known_variables().copy()
        
        # Continue until no more variables can be solved
        max_iterations = len(self.variables)  # Prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            unknown_vars = {name for name in self.variables.keys() if name not in simulated_known}
            if not unknown_vars:
                break
                
            found_solvable = False
            # Find next solvable variable
            for equation in self.equations:
                for unknown_var in unknown_vars:
                    if equation.can_solve_for(unknown_var, simulated_known):
                        order.append(unknown_var)
                        # Simulate marking as known for next iteration
                        simulated_known.add(unknown_var)
                        found_solvable = True
                        break
                if found_solvable:
                    break
            
            if not found_solvable:
                break  # No more progress possible
                
            iterations += 1
        
        return order
    
    def __str__(self) -> str:
        return f"EquationSystem({len(self.equations)} equations, {len(self.variables)} variables)"
    
    def __repr__(self) -> str:
        return f"EquationSystem(equations={self.equations!r})"
