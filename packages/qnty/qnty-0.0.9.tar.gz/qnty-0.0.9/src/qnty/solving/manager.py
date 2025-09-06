
from qnty.equations.equation import Equation
from qnty.quantities import TypeSafeVariable as Variable
from qnty.solving.order import Order

from .solvers.base import BaseSolver, SolveResult
from .solvers.iterative import IterativeSolver
from .solvers.simultaneous import SimultaneousEquationSolver


class SolverManager:
    """
    Manages multiple solvers and selects the best one for a given problem.
    """
    
    def __init__(self, logger=None):
        self.logger = logger
        self.solvers = [
            SimultaneousEquationSolver(logger),  # Try simultaneous first for cyclic systems
            IterativeSolver(logger),             # Fall back to iterative
        ]
    
    def solve(self, equations: list[Equation], variables: dict[str, Variable],
              dependency_graph: Order | None = None,
              max_iterations: int = 100, tolerance: float = 1e-10) -> SolveResult:
        """
        Solve the system using the best available solver.
        
        Args:
            equations: List of equations to solve
            variables: Dictionary of all variables (known and unknown)
            dependency_graph: Optional dependency graph
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
            
        Returns:
            SolveResult containing the solution
        """
        unknowns = {s for s, v in variables.items() if not v.is_known}
        
        if not unknowns:
            return SolveResult(
                variables=variables,
                steps=[],
                success=True,
                message="No unknowns to solve",
                method="NoSolver"
            )
        
        # Get system analysis if we have a dependency graph
        analysis = None
        if dependency_graph:
            known_vars = {s for s, v in variables.items() if v.is_known}
            analysis = dependency_graph.analyze_system(known_vars)
        
        # Try each solver in order of preference
        for solver in self.solvers:
            if solver.can_handle(equations, unknowns, dependency_graph, analysis):
                if self.logger:
                    self.logger.debug(f"Using {solver.__class__.__name__} for solving")
                
                result = solver.solve(equations, variables, dependency_graph,
                                    max_iterations, tolerance)
                
                if result.success:
                    return result
                else:
                    if self.logger:
                        # Use debug level for expected fallback from SimultaneousEquationSolver
                        if solver.__class__.__name__ == "SimultaneousEquationSolver":
                            self.logger.debug(f"{solver.__class__.__name__} failed: {result.message}")
                        else:
                            self.logger.warning(f"{solver.__class__.__name__} failed: {result.message}")
        
        # No solver could handle the problem
        return SolveResult(
            variables=variables,
            steps=[],
            success=False,
            message="No solver could handle this problem",
            method="NoSolver"
        )
    
    def add_solver(self, solver: BaseSolver):
        """Add a custom solver to the manager."""
        self.solvers.insert(0, solver)  # Add to beginning for highest priority
    
    def get_available_solvers(self) -> list[str]:
        """Get list of available solver names."""
        return [solver.__class__.__name__ for solver in self.solvers]
