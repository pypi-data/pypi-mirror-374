from typing import Any

from qnty.equations.equation import Equation
from qnty.expressions import VariableReference
from qnty.quantities import TypeSafeVariable as Variable
from qnty.solving.order import Order

from .base import BaseSolver, SolveResult


class IterativeSolver(BaseSolver):
    """
    Iterative solver that follows dependency order like solving engineering problems by hand.
    
    This solver works by:
    1. Using dependency graph to determine the correct solving order
    2. Solving variables one by one in dependency order (just like manual solving)
    3. Preserving units throughout with Pint integration
    4. Verifying each solution with residual checking
    5. Repeating until all unknowns are solved
    
    This approach mirrors how engineers solve problems by hand: solve what you can
    with what you know, then use those results to solve the next level of dependencies.
    """
    
    def can_handle(self, equations: list[Equation], unknowns: set[str],
                   dependency_graph: Order | None = None,
                   analysis: dict[str, Any] | None = None) -> bool:
        """
        Can handle any system that doesn't have cycles and has at least one unknown.
        """
        if not unknowns:
            return False
            
        # The IterativeSolver can now handle cycles through iterative convergence
        # if analysis and analysis.get('has_cycles', False):
        #     return False
            
        # If we have a dependency graph, we can try to solve
        if dependency_graph:
            return True
            
        # As a fallback, we can try to handle any system
        return len(unknowns) > 0
    
    def solve(self, equations: list[Equation], variables: dict[str, Variable],
              dependency_graph: Order | None = None,
              max_iterations: int = 100, tolerance: float = 1e-10) -> SolveResult:
        """
        Solve the system iteratively using dependency graph.
        """
        self.steps = []
        
        if not dependency_graph:
            return SolveResult(
                variables=variables,
                steps=self.steps,
                success=False,
                message="Dependency graph required for iterative solving",
                method="IterativeSolver"
            )
        
        # Make a copy of variables to work with
        working_vars = dict(variables.items())
        known_vars = self._get_known_variables(working_vars)
        
        if self.logger:
            self.logger.debug(f"Starting iterative solve with {len(known_vars)} known variables")
        
        # Iterative solving
        iteration = -1  # Initialize to handle case where loop doesn't run
        for iteration in range(max_iterations):
            iteration_start = len(known_vars)
            
            # Get variables that can be solved in this iteration
            solvable = dependency_graph.get_solvable_variables(known_vars)
            
            # Fallback: attempt direct equations for remaining unknowns
            if not solvable:
                remaining_unknowns = [v for v in self._get_unknown_variables(working_vars)
                                    if v not in known_vars]
                for var_symbol in remaining_unknowns:
                    for eq in equations:
                        if eq.can_solve_for(var_symbol, known_vars):
                            solvable.append(var_symbol)
                            break
            
            if not solvable:
                # Try to break conditional cycles
                remaining_unknowns = [v for v in self._get_unknown_variables(working_vars)
                                    if v not in known_vars]
                if remaining_unknowns:
                    # Look for conditional equations that can be evaluated
                    for var_symbol in remaining_unknowns:
                        for eq in equations:
                            # Check if LHS is a VariableReference with matching name
                            if (isinstance(eq.lhs, VariableReference) and
                                eq.lhs.name == var_symbol and
                                'ConditionalExpression' in str(type(eq.rhs))):
                                # This is a conditional equation - try to solve it
                                try:
                                    solved_var = eq.solve_for(var_symbol, working_vars)
                                    working_vars[var_symbol] = solved_var
                                    known_vars.add(var_symbol)
                                    solvable = [var_symbol]  # Mark as solved this iteration
                                    if self.logger:
                                        self.logger.debug(f"Solved conditional cycle: {var_symbol} = {solved_var.quantity}")
                                    break
                                except Exception:
                                    continue
                        if solvable:
                            break
                
                if not solvable:
                    break  # No more variables can be solved
            
            if self.logger:
                self.logger.debug(f"Iteration {iteration + 1} solvable: {solvable}")
            
            # Solve for each solvable variable
            for var_symbol in solvable:
                equation = dependency_graph.get_equation_for_variable(var_symbol, known_vars)
                if equation is None:
                    # Try any equation that can solve it
                    for eq in equations:
                        if eq.can_solve_for(var_symbol, known_vars):
                            equation = eq
                            break
                
                if equation is None:
                    continue
                    
                try:
                    solved_var = equation.solve_for(var_symbol, working_vars)
                    working_vars[var_symbol] = solved_var
                    known_vars.add(var_symbol)
                    
                    # Verify solution by checking residual (like checking work by hand)
                    if equation.check_residual(working_vars, tolerance):
                        if self.logger:
                            self.logger.debug(f"Solution verified for {var_symbol}")
                    else:
                        if self.logger:
                            self.logger.warning(f"Residual check failed for {var_symbol}")
                    
                    self._log_step(
                        iteration + 1,
                        var_symbol,
                        str(equation),
                        str(solved_var.quantity),
                        'iterative'
                    )
                    
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Failed to solve for {var_symbol}: {e}")
                    return SolveResult(
                        variables=working_vars,
                        steps=self.steps,
                        success=False,
                        message=f"Failed to solve for {var_symbol}: {e}",
                        method="IterativeSolver",
                        iterations=iteration + 1
                    )
            
            # Check for progress
            if len(known_vars) == iteration_start:
                if self.logger:
                    self.logger.warning("No progress made, stopping early")
                break
        
        # Check if we solved all unknowns
        remaining_unknowns = self._get_unknown_variables(working_vars)
        success = len(remaining_unknowns) == 0
        
        message = "All variables solved" if success else f"Could not solve: {remaining_unknowns}"
        
        return SolveResult(
            variables=working_vars,
            steps=self.steps,
            success=success,
            message=message,
            method="IterativeSolver",
            iterations=iteration + 1
        )
