from collections import defaultdict, deque
from typing import Any

from ..equations import Equation


class Order:
    """
    Manages dependencies between variables in a system of equations.
    Uses topological sorting to determine the correct solving order.
    """

    def __init__(self):
        # Graph structure: dependency_source -> [dependent_variables]
        self.graph = defaultdict(list)
        # Count of dependencies for each variable
        self.in_degree = defaultdict(int)
        # All variables in the system
        self.variables = set()
        # Equations that can solve for each variable
        self.solvers = defaultdict(list)  # variable -> [equations that can solve it]

    def add_equation(self, equation: Equation, known_vars: set[str]):
        """Add an equation to the dependency graph."""
        eq_vars = equation.get_all_variables()
        unknown_vars = equation.get_unknown_variables(known_vars)

        # Update variables set
        self.variables.update(eq_vars)

        # Analyze equation structure to determine dependencies and solvers
        lhs_vars = self._extract_variables_from_side(equation.lhs)
        rhs_vars = self._extract_variables_from_side(equation.rhs)

        # Handle different equation patterns
        self._process_equation_dependencies(equation, lhs_vars, rhs_vars, unknown_vars, eq_vars, known_vars)

    def add_dependency(self, dependency_source: str, dependent_variable: str):
        """
        Add a dependency: dependent_variable depends on dependency_source.
        This means dependency_source must be solved before dependent_variable.
        """
        if dependent_variable != dependency_source:  # Avoid self-dependencies
            # Add to graph
            if dependent_variable not in self.graph[dependency_source]:
                self.graph[dependency_source].append(dependent_variable)
                self.in_degree[dependent_variable] += 1

            # Ensure both variables are tracked
            self.variables.add(dependency_source)
            self.variables.add(dependent_variable)

    def remove_dependency(self, dependency_source: str, dependent_variable: str):
        """Remove a dependency between variables."""
        if dependent_variable in self.graph[dependency_source]:
            self.graph[dependency_source].remove(dependent_variable)
            self.in_degree[dependent_variable] -= 1

    def get_solving_order(self, known_vars: set[str]) -> list[str]:
        """
        Get the order in which variables should be solved using topological sort.
        Returns list of variables in solving order.
        """
        # Create a copy of in_degree for this computation
        temp_in_degree = self.in_degree.copy()
        temp_graph = defaultdict(list)

        # Initialize temp_graph with copies, ensuring all variables have entries
        for var in self.variables:
            temp_graph[var] = self.graph[var].copy() if var in self.graph else []

        # Initialize queue with variables that have no dependencies (already known)
        queue = deque()

        # Add known variables to queue first
        for var in known_vars:
            if var in self.variables:
                queue.append(var)

        # Add variables with no remaining dependencies AND have solver equations
        for var in self.variables:
            if var not in known_vars and temp_in_degree[var] == 0 and var in self.solvers:
                queue.append(var)

        solving_order = []

        while queue:
            current_var = queue.popleft()
            solving_order.append(current_var)

            # Remove this variable's influence on dependent variables
            if current_var in temp_graph:
                for dependent_var in temp_graph[current_var]:
                    temp_in_degree[dependent_var] -= 1

                    # If dependent variable has no more dependencies AND has solvers, add it to queue
                    if temp_in_degree[dependent_var] == 0 and dependent_var in self.solvers:
                        queue.append(dependent_var)

        # Filter out known variables from the result, as they don't need solving
        result = [var for var in solving_order if var not in known_vars]

        return result

    def detect_cycles(self) -> list[list[str]]:
        """
        Detect cycles in the dependency graph.
        Returns list of cycles (each cycle is a list of variables).
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = defaultdict(int)
        cycles = []
        current_path = []

        def dfs_visit(node: str) -> bool:
            """DFS visit with cycle detection. Returns True if cycle found."""
            if color[node] == GRAY:
                # Found a back edge - cycle detected
                cycle_start = current_path.index(node)
                cycle = current_path[cycle_start:] + [node]
                cycles.append(cycle)
                return True

            if color[node] == BLACK:
                return False

            # Mark as being processed
            color[node] = GRAY
            current_path.append(node)

            # Visit neighbors
            for neighbor in self.graph[node]:
                if dfs_visit(neighbor):
                    return True

            # Mark as completely processed
            color[node] = BLACK
            current_path.pop()
            return False

        # Check all variables
        for var in self.variables:
            if color[var] == WHITE:
                dfs_visit(var)

        return cycles

    def can_solve_system(self, known_vars: set[str]) -> tuple[bool, list[str]]:
        """
        Check if the system can be completely solved given known variables.
        Returns (can_solve, unsolvable_variables).
        """
        all_unknown = self.variables - known_vars

        # Find variables with no solver equations
        truly_unsolvable = self._find_truly_unsolvable_variables(all_unknown)

        # Check equation-to-variable ratio
        variables_with_solvers = all_unknown - set(truly_unsolvable)
        unique_equations = self._get_unique_equations(variables_with_solvers)

        # Simple heuristic: need at least as many equations as unknowns
        can_solve_completely = len(unique_equations) >= len(variables_with_solvers) and len(truly_unsolvable) == 0

        if can_solve_completely:
            return True, []

        # Find all unsolvable variables
        solving_order = self.get_solving_order(known_vars)
        solvable = set(solving_order)
        conditional_unsolvable = all_unknown - solvable
        unsolvable = list(set(truly_unsolvable) | conditional_unsolvable)

        return False, unsolvable

    def get_solvable_variables(self, known_vars: set[str]) -> list[str]:
        """Get variables that can be solved in the next iteration."""
        solvable = []

        for var in self.variables:
            if var not in known_vars:
                # Check if all dependencies of this variable are known
                dependencies_known = True
                for dep_source in self.graph:
                    if var in self.graph[dep_source] and dep_source not in known_vars:
                        dependencies_known = False
                        break

                if dependencies_known and var in self.solvers:
                    solvable.append(var)

        return solvable

    def get_equation_for_variable(self, var: str, known_vars: set[str]) -> Equation | None:
        """Get an equation that can solve for the given variable."""
        if var not in self.solvers:
            return None

        # Find the first equation that can solve for this variable
        for equation in self.solvers[var]:
            if equation.can_solve_for(var, known_vars):
                return equation

        return None

    def get_strongly_connected_components(self) -> list[set[str]]:
        """
        Find strongly connected components in the dependency graph.
        Variables in the same SCC must be solved simultaneously.
        """
        # Tarjan's algorithm for finding SCCs
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        components = []

        def strongconnect(node: str):
            index[node] = index_counter[0]
            lowlinks[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack[node] = True

            for neighbor in self.graph[node]:
                if neighbor not in index:
                    strongconnect(neighbor)
                    lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
                elif on_stack[neighbor]:
                    lowlinks[node] = min(lowlinks[node], index[neighbor])

            if lowlinks[node] == index[node]:
                component = set()
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.add(w)
                    if w == node:
                        break
                components.append(component)

        for node in self.variables:
            if node not in index:
                strongconnect(node)

        # Filter out single-node components (unless they have self-loops)
        significant_components = []
        for component in components:
            if len(component) > 1:
                significant_components.append(component)
            elif len(component) == 1:
                node = next(iter(component))
                if node in self.graph[node]:  # Self-loop
                    significant_components.append(component)

        return significant_components

    def analyze_system(self, known_vars: set[str]) -> dict[str, Any]:
        """
        Perform comprehensive analysis of the equation system.
        Returns analysis results including cycles, SCCs, solvability, etc.
        """
        analysis = {}

        # Basic info
        analysis["total_variables"] = len(self.variables)
        analysis["known_variables"] = len(known_vars)
        analysis["unknown_variables"] = len(self.variables - known_vars)

        # Solving order
        analysis["solving_order"] = self.get_solving_order(known_vars)

        # Solvability
        can_solve, unsolvable = self.can_solve_system(known_vars)
        analysis["can_solve_completely"] = can_solve
        analysis["unsolvable_variables"] = unsolvable

        # Cycles and SCCs
        analysis["cycles"] = self.detect_cycles()
        analysis["strongly_connected_components"] = self.get_strongly_connected_components()
        analysis["has_cycles"] = len(analysis["cycles"]) > 0

        # Next solvable variables
        analysis["immediately_solvable"] = self.get_solvable_variables(known_vars)

        return analysis

    def _extract_variables_from_side(self, side: Any) -> set[str]:
        """
        Extract variables from either left or right side of an equation.

        Args:
            side: The equation side (Variable or Expression)

        Returns:
            Set of variable names found in this side
        """
        # Check if it's a Variable with a symbol attribute
        if hasattr(side, "symbol") and hasattr(side, "name"):
            return {str(side.symbol) if side.symbol else str(side.name)}
        # Check if it's an Expression with get_variables method
        elif hasattr(side, "get_variables") and callable(side.get_variables):
            return side.get_variables()  # type: ignore[return-value]
        else:
            return set()

    def _process_equation_dependencies(self, equation: Equation, lhs_vars: set[str], rhs_vars: set[str], unknown_vars: set[str], eq_vars: set[str], known_vars: set[str]):
        """
        Process dependencies and solvers for an equation based on its structure.

        Args:
            equation: The equation to process
            lhs_vars: Variables on left-hand side
            rhs_vars: Variables on right-hand side
            unknown_vars: Unknown variables in the equation
            eq_vars: All variables in the equation
            known_vars: Set of known variables
        """
        # If LHS is a single variable, it depends on all variables in RHS
        if len(lhs_vars) == 1:
            lhs_var = next(iter(lhs_vars))
            if lhs_var in unknown_vars:
                self.solvers[lhs_var].append(equation)
            # Add dependencies: LHS variable depends on all RHS variables
            for rhs_var in rhs_vars:
                if rhs_var != lhs_var:
                    self.add_dependency(rhs_var, lhs_var)

        # If RHS is a single variable, it depends on all variables in LHS
        elif len(rhs_vars) == 1:
            rhs_var = next(iter(rhs_vars))
            if rhs_var in unknown_vars:
                self.solvers[rhs_var].append(equation)
            # Add dependencies: RHS variable depends on all LHS variables
            for lhs_var in lhs_vars:
                if lhs_var != rhs_var:
                    self.add_dependency(lhs_var, rhs_var)

        # For more complex cases, use can_solve_for check
        else:
            for unknown_var in unknown_vars:
                if equation.can_solve_for(unknown_var, known_vars):
                    self.solvers[unknown_var].append(equation)
                # Add dependencies: unknown_var depends on all other variables in equation
                for other_var in eq_vars:
                    if other_var != unknown_var:
                        self.add_dependency(other_var, unknown_var)

    def _find_truly_unsolvable_variables(self, all_unknown: set[str]) -> list[str]:
        """
        Find variables that have no solver equations.

        Args:
            all_unknown: Set of all unknown variables

        Returns:
            List of variables with no solver equations
        """
        truly_unsolvable = []
        for var in all_unknown:
            if var not in self.solvers or len(self.solvers[var]) == 0:
                truly_unsolvable.append(var)
        return truly_unsolvable

    def _get_unique_equations(self, variables_with_solvers: set[str]) -> set[Equation]:
        """
        Get unique equations that can solve variables.

        Args:
            variables_with_solvers: Variables that have solver equations

        Returns:
            Set of unique equations
        """
        unique_equations = set()
        for var in variables_with_solvers:
            if var in self.solvers and self.solvers[var]:
                unique_equations.add(self.solvers[var][0])
        return unique_equations

    def visualize_dependencies(self) -> str:
        """Create a text representation of the dependency graph."""
        lines = ["Dependency Graph:"]
        lines.append("=" * 20)

        for source_var in sorted(self.graph.keys()):
            if self.graph[source_var]:
                dependents = ", ".join(sorted(self.graph[source_var]))
                lines.append(f"{source_var} -> [{dependents}]")

        lines.append("")
        lines.append("In-degrees:")
        for var in sorted(self.variables):
            lines.append(f"{var}: {self.in_degree[var]}")

        return "\n".join(lines)

    def __str__(self) -> str:
        return f"DependencyGraph(variables={len(self.variables)}, equations={len(self.solvers)})"

    def __repr__(self) -> str:
        return self.__str__()
