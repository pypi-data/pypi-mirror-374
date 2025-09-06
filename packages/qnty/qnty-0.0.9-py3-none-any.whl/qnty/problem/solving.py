"""
High-level solve orchestration for Problem class.

This module contains the main solving logic, dependency graph building,
solution verification, and system analysis methods.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qnty.equations import Equation
    from qnty.quantities import TypeSafeVariable as Variable

# Constants
MAX_ITERATIONS_DEFAULT = 100
TOLERANCE_DEFAULT = 1e-10


# Custom Exceptions
class SolverError(RuntimeError):
    """Raised when the solving process fails."""
    pass


class SolvingMixin:
    """Mixin class providing solving orchestration functionality."""
    
    # These attributes/methods will be provided by other mixins in the final Problem class
    name: str
    logger: Any
    equations: list[Equation]
    solver_manager: Any
    
    def get_known_symbols(self) -> set[str]:
        """Will be provided by VariablesMixin."""
        ...
    
    def get_known_variables(self) -> dict[str, Variable]:
        """Will be provided by VariablesMixin."""
        ...
    
    def get_unknown_variables(self) -> dict[str, Variable]:
        """Will be provided by VariablesMixin."""
        ...
    
    def _sync_variables_to_instance_attributes(self) -> None:
        """Will be provided by VariablesMixin."""
        ...

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
            tolerance: Numerical tolerance for convergence (default: 1e-10)
            
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
            solve_result = self.solver_manager.solve(
                self.equations,
                self.variables,
                self.dependency_graph,
                max_iterations,
                tolerance
            )
            
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
        from qnty.solving.order import Order
        self.dependency_graph = Order()
        
        # Get known variables
        known_vars = self.get_known_symbols()
        
        # Add dependencies from equations
        for equation in self.equations:
            self.dependency_graph.add_equation(equation, known_vars)

    def verify_solution(self, tolerance: float = 1e-10) -> bool:
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
            analysis['total_equations'] = len(self.equations)
            analysis['is_determined'] = len(self.get_unknown_variables()) <= len(self.equations)
            
            return analysis
        except Exception as e:
            self.logger.debug(f"Dependency analysis failed: {e}")
            # Return basic analysis on failure
            return {
                'total_variables': len(self.variables),
                'known_variables': len(self.get_known_variables()),
                'unknown_variables': len(self.get_unknown_variables()),
                'total_equations': len(self.equations),
                'is_determined': len(self.get_unknown_variables()) <= len(self.equations),
                'has_cycles': False,
                'solving_order': [],
                'can_solve_completely': False,
                'unsolvable_variables': []
            }
