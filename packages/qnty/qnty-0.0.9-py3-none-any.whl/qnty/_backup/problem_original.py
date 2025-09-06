"""
Core EngineeringProblem class for engineering problem solving.

This module provides the main EngineeringProblem class that coordinates
all aspects of engineering problem definition, solving, and analysis.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from qnty.equations import Equation, EquationSystem

if TYPE_CHECKING:
    from qnty.expressions import BinaryOperation, Constant, VariableReference
from qnty.utils.logging import get_logger
from qnty.solving.order import Order
from qnty.problem.reconstruction import EquationReconstructor
from qnty.problem.metaclass import ProblemMeta
from qnty.solving.solvers import SolverManager
from qnty.quantities import Quantity as Qty
from qnty.quantities import TypeSafeVariable as Variable
from qnty.generated.units import DimensionlessUnits

# Constants
MAX_ITERATIONS_DEFAULT = 100
TOLERANCE_DEFAULT = 1e-10
MATHEMATICAL_OPERATORS = ['+', '-', '*', '/', ' / ', ' * ', ' + ', ' - ']
COMMON_COMPOSITE_VARIABLES = ['P', 'c', 'S', 'E', 'W', 'Y']


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


class Problem(metaclass=ProblemMeta):
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
       class MyProblem(EngineeringProblem):
           x = Variable("x", Qty(5.0, length))
           y = Variable("y", Qty(0.0, length), is_known=False)
           eq = y.equals(x * 2)
    
    2. Programmatic Pattern (For dynamic problems):
       problem = EngineeringProblem("Dynamic Problem")
       problem.add_variables(x, y)
       problem.add_equation(y.equals(x * 2))
    
    3. Composition Pattern (For reusable sub-problems):
       class ComposedProblem(EngineeringProblem):
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
        sub_problems (dict[str, EngineeringProblem]): Integrated sub-problems
    """
    
    def __init__(self, name: str | None = None, description: str = ""):
        # Handle subclass mode (class-level name/description) vs explicit name
        self.name = name or getattr(self.__class__, 'name', self.__class__.__name__)
        self.description = description or getattr(self.__class__, 'description', "")
        
        # Core storage
        self.variables: dict[str, Variable] = {}
        self.equations: list[Equation] = []
        
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
        self.validation_checks: list[Callable] = []
        
        self.logger = get_logger()
        self.solver_manager = SolverManager(self.logger)
        
        # Sub-problem composition support
        self.sub_problems: dict[str, Problem] = {}
        self.variable_aliases: dict[str, str] = {}  # Maps alias -> original variable symbol
        
        # Initialize equation reconstructor
        self.equation_reconstructor = EquationReconstructor(self)
        
        # Auto-populate from class-level variables and equations (subclass pattern)
        self._extract_from_class_variables()

    def _extract_from_class_variables(self):
        """Extract variables, equations, and sub-problems from class-level definitions."""
        self._extract_sub_problems()
        self._extract_direct_variables()
        self._recreate_validation_checks()
        self._create_composite_equations()
        self._extract_equations()

    def _extract_sub_problems(self):
        """Extract and integrate sub-problems from class-level definitions."""
        if hasattr(self.__class__, '_original_sub_problems'):
            original_sub_problems = getattr(self.__class__, '_original_sub_problems', {})
            for attr_name, sub_problem in original_sub_problems.items():
                self._integrate_sub_problem(sub_problem, attr_name)

    def _extract_direct_variables(self):
        """Extract direct variables from class-level definitions."""
        processed_symbols = set()
        
        # Single pass through class attributes to collect variables
        for attr_name, attr_value in self._get_class_attributes():
            if isinstance(attr_value, Variable):
                # Set symbol based on attribute name (T_bar, P, etc.)
                attr_value.symbol = attr_name
                
                # Skip if we've already processed this symbol
                if attr_value.symbol in processed_symbols:
                    continue
                processed_symbols.add(attr_value.symbol)
                
                # Clone variable to avoid shared state between instances
                cloned_var = self._clone_variable(attr_value)
                self.add_variable(cloned_var)
                # Set the same cloned variable object as instance attribute
                # Use super() to bypass our custom __setattr__ during initialization
                super().__setattr__(attr_name, cloned_var)

    def _extract_equations(self):
        """Extract and process equations from class-level definitions."""
        equations_to_process = self._collect_class_equations()
        
        for attr_name, equation in equations_to_process:
            try:
                if self._process_equation(attr_name, equation):
                    setattr(self, attr_name, equation)
            except Exception as e:
                # Log but continue - some equations might fail during class definition
                self.logger.warning(f"Failed to process equation {attr_name}: {e}")
                # Still set the original equation as attribute
                setattr(self, attr_name, equation)

    def _get_class_attributes(self) -> list[tuple[str, Any]]:
        """Get all non-private class attributes efficiently."""
        return [(attr_name, getattr(self.__class__, attr_name))
                for attr_name in dir(self.__class__)
                if not attr_name.startswith('_')]

    def _collect_class_equations(self) -> list[tuple[str, Equation]]:
        """Collect all equation objects from class attributes."""
        equations_to_process = []
        for attr_name, attr_value in self._get_class_attributes():
            if isinstance(attr_value, Equation):
                equations_to_process.append((attr_name, attr_value))
        return equations_to_process

    def _process_equation(self, attr_name: str, equation: Equation) -> bool:
        """Process a single equation and add it to the problem if valid."""
        return self._process_equation_impl(attr_name, equation)
    
    def _process_equation_impl(self, attr_name: str, equation: Equation) -> bool:
        """
        Process a single equation and determine if it should be added.
        Returns True if the equation was successfully processed.
        """
        # First, update variable references to use symbols instead of names
        updated_equation = self._update_equation_variable_references(equation)
        
        # Check if this equation contains delayed expressions
        try:
            has_delayed = self.equation_reconstructor.contains_delayed_expressions(updated_equation)
            if has_delayed:
                return self._handle_delayed_equation(attr_name, updated_equation)
        except Exception as e:
            self.logger.debug(f"Error checking delayed expressions for {attr_name}: {e}")
        
        # Check if this equation has invalid self-references
        try:
            has_self_ref = self._has_invalid_self_references(updated_equation)
            if has_self_ref:
                self.logger.debug(f"Skipping invalid self-referencing equation {attr_name}: {updated_equation}")
                return False
        except Exception as e:
            self.logger.debug(f"Error checking self-references for {attr_name}: {e}")
        
        # Check if equation references non-existent variables
        try:
            has_missing = self._equation_has_missing_variables(updated_equation)
            if has_missing:
                return self._handle_equation_with_missing_variables(attr_name, updated_equation)
        except Exception as e:
            self.logger.debug(f"Error checking missing variables for {attr_name}: {e}")
        
        # Process valid equation
        self.add_equation(updated_equation)
        return True

    def _handle_delayed_equation(self, attr_name: str, equation: Equation) -> bool:
        """Handle equations with delayed expressions."""
        resolved_equation = self.equation_reconstructor.resolve_delayed_equation(equation)
        if resolved_equation:
            self.add_equation(resolved_equation)
            setattr(self, attr_name, resolved_equation)
            return True
        else:
            self.logger.debug(f"Skipping unresolvable delayed equation {attr_name}: {equation}")
            return False

    def _handle_equation_with_missing_variables(self, attr_name: str, equation: Equation) -> bool:
        """Handle equations that reference missing variables."""
        # Handle conditional equations more carefully
        if self._is_conditional_equation(equation):
            return self._handle_conditional_equation(attr_name, equation)
        
        # Only attempt reconstruction for simple mathematical expressions from composition
        if self.equation_reconstructor.should_attempt_reconstruction(equation):
            return self._attempt_equation_reconstruction(attr_name, equation)
        else:
            # Skip other problematic equations
            self.logger.debug(f"Skipping equation with missing variables {attr_name}: {equation}")
            return False

    def _handle_conditional_equation(self, attr_name: str, equation: Equation) -> bool:
        """Handle conditional equations with missing variables."""
        missing_vars = equation.get_all_variables() - set(self.variables.keys())
        
        
        # Skip conditional equations from sub-problems in composed systems
        if self.sub_problems and self._is_conditional_equation_from_subproblem(equation, attr_name):
            self.logger.debug(f"Skipping conditional equation {attr_name} from sub-problem in composed system")
            return False
        
        # Check for composite expressions that might be reconstructable
        unresolvable_vars = [var for var in missing_vars
                           if any(op in var for op in MATHEMATICAL_OPERATORS)]
        
        if self.sub_problems and unresolvable_vars:
            # Before skipping, try to reconstruct conditional equations with composite expressions
            self.logger.debug(f"Attempting to reconstruct conditional equation {attr_name} with composite variables: {unresolvable_vars}")
            reconstructed_equation = self.equation_reconstructor.reconstruct_composite_expressions_generically(equation)
            if reconstructed_equation:
                self.logger.debug(f"Successfully reconstructed conditional equation {attr_name}: {reconstructed_equation}")
                self.add_equation(reconstructed_equation)
                setattr(self, attr_name, reconstructed_equation)
                return True
            else:
                self.logger.debug(f"Failed to reconstruct conditional equation {attr_name}, trying simple substitution")
                # Try simple substitution for basic arithmetic expressions
                reconstructed_equation = self._try_simple_substitution(equation, missing_vars)
                if reconstructed_equation:
                    self.add_equation(reconstructed_equation)
                    return True
                else:
                    self.add_equation(equation)
                    return True
        else:
            # Try to add the conditional equation even with missing simple variables
            self.add_equation(equation)
            return True

    def _try_simple_substitution(self, _equation: Equation, _missing_vars: set[str]) -> Equation | None:
        """
        Try simple substitution for basic arithmetic expressions in conditional equations.
        
        The real issue is that nested expressions in conditionals aren't being handled properly.
        For now, just return None and let the equation be added as-is.
        """
        return None

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
            symbol = getattr(expr, 'symbol', None)
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
            
        elif hasattr(expr, 'operand'):
            # Recursively fix operand
            fixed_operand = self._fix_expression_variables(expr.operand)
            return type(expr)(expr.operator, fixed_operand)
            
        elif hasattr(expr, 'function_name'):
            # Recursively fix left and right operands
            fixed_left = self._fix_expression_variables(expr.left)
            fixed_right = self._fix_expression_variables(expr.right)
            return type(expr)(expr.function_name, fixed_left, fixed_right)
            
        elif isinstance(expr, Constant):
            return expr
            
        else:
            # Unknown expression type, return as-is
            return expr

    def _attempt_equation_reconstruction(self, attr_name: str, equation: Equation) -> bool:
        """Attempt to reconstruct equations with composite expressions."""
        missing_vars = equation.get_all_variables() - set(self.variables.keys())
        self.logger.debug(f"Attempting to reconstruct equation {attr_name} with missing variables: {missing_vars}")
        
        reconstructed_equation = self.equation_reconstructor.reconstruct_composite_expressions_generically(equation)
        if reconstructed_equation:
            self.logger.debug(f"Successfully reconstructed {attr_name}: {reconstructed_equation}")
            self.add_equation(reconstructed_equation)
            setattr(self, attr_name, reconstructed_equation)
            return True
        else:
            self.logger.debug(f"Failed to reconstruct equation {attr_name}: {equation}")
            return False
    
    def _integrate_sub_problem(self, sub_problem: Problem, namespace: str) -> None:
        """
        Integrate a sub-problem by flattening its variables with namespace prefixes.
        Creates a simple dotted access pattern: self.header.P becomes self.header_P
        """
        self.sub_problems[namespace] = sub_problem
        
        # Get proxy configurations if available
        proxy_configs = getattr(self.__class__, '_proxy_configurations', {}).get(namespace, {})
        
        # Create a namespace object for dotted access (self.header.P)
        namespace_obj = type('SubProblemNamespace', (), {})()
        
        # Add all sub-problem variables with namespace prefixes
        for var_symbol, var in sub_problem.variables.items():
            namespaced_var = self._create_namespaced_variable(var, var_symbol, namespace, proxy_configs)
            self.add_variable(namespaced_var)
            
            # Set both namespaced access (self.header_P) and dotted access (self.header.P)
            if namespaced_var.symbol is not None:
                super().__setattr__(namespaced_var.symbol, namespaced_var)
            setattr(namespace_obj, var_symbol, namespaced_var)
        
        # Set the namespace object for dotted access
        super().__setattr__(namespace, namespace_obj)
        
        # Also add all sub-problem equations (they'll be namespaced automatically)
        for equation in sub_problem.equations:
            try:
                # Skip conditional equations for variables that are overridden to known values in composition
                if self._should_skip_subproblem_equation(equation, namespace):
                    continue
                    
                namespaced_equation = self._namespace_equation(equation, namespace)
                if namespaced_equation:
                    self.add_equation(namespaced_equation)
            except Exception as e:
                self.logger.debug(f"Failed to namespace equation from {namespace}: {e}")

    def _create_namespaced_variable(self, var: Variable, var_symbol: str, namespace: str, proxy_configs: dict) -> Variable:
        """Create a namespaced variable with proper configuration."""
        namespaced_symbol = f"{namespace}_{var_symbol}"
        namespaced_var = self._clone_variable(var)
        namespaced_var.symbol = namespaced_symbol
        namespaced_var.name = f"{var.name} ({namespace.title()})"
        
        # Apply proxy configuration if available
        if var_symbol in proxy_configs:
            config = proxy_configs[var_symbol]
            namespaced_var.quantity = config['quantity']
            namespaced_var.is_known = config['is_known']
        
        return namespaced_var

    def _namespace_equation(self, equation: Equation, namespace: str) -> Equation | None:
        """
        Create a namespaced version of an equation by prefixing all variable references.
        """
        try:
            # Get all variable symbols in the equation
            variables_in_eq = equation.get_all_variables()
            
            # Create mapping from original symbols to namespaced symbols
            symbol_mapping = {}
            for var_symbol in variables_in_eq:
                namespaced_symbol = f"{namespace}_{var_symbol}"
                if namespaced_symbol in self.variables:
                    symbol_mapping[var_symbol] = namespaced_symbol
            
            if not symbol_mapping:
                return None
            
            # Create new equation with namespaced references
            # For LHS, we need a Variable object to call .equals()
            # For RHS, we need proper expression structure
            namespaced_lhs = self._namespace_expression_for_lhs(equation.lhs, symbol_mapping)
            namespaced_rhs = self._namespace_expression(equation.rhs, symbol_mapping)
            
            if namespaced_lhs and namespaced_rhs:
                equals_method = getattr(namespaced_lhs, 'equals', None)
                if equals_method:
                    return equals_method(namespaced_rhs)
            
            return None
            
        except Exception:
            return None

    def _namespace_expression(self, expr, symbol_mapping):
        """
        Create a namespaced version of an expression by replacing variable references.
        """
        
        # Handle variable references
        if isinstance(expr, VariableReference):
            return self._namespace_variable_reference(expr, symbol_mapping)
        elif hasattr(expr, 'symbol') and expr.symbol in symbol_mapping:
            return self._namespace_variable_object(expr, symbol_mapping)
        
        # Handle operations
        elif isinstance(expr, BinaryOperation):
            return self._namespace_binary_operation(expr, symbol_mapping)
        elif hasattr(expr, 'operand'):
            return self._namespace_unary_operation(expr, symbol_mapping)
        elif hasattr(expr, 'function_name'):
            return self._namespace_binary_function(expr, symbol_mapping)
        elif isinstance(expr, Constant):
            return expr
        else:
            return expr

    def _namespace_variable_reference(self, expr, symbol_mapping):
        """Namespace a VariableReference object."""
        if expr.symbol in symbol_mapping:
            namespaced_symbol = symbol_mapping[expr.symbol]
            if namespaced_symbol in self.variables:
                return VariableReference(self.variables[namespaced_symbol])
        return expr

    def _namespace_variable_object(self, expr, symbol_mapping):
        """Namespace a Variable object."""
        namespaced_symbol = symbol_mapping[expr.symbol]
        if namespaced_symbol in self.variables:
            # Return VariableReference for use in expressions, not the Variable itself
            return VariableReference(self.variables[namespaced_symbol])
        return expr

    def _namespace_binary_operation(self, expr, symbol_mapping):
        """Namespace a BinaryOperation."""
        namespaced_left = self._namespace_expression(expr.left, symbol_mapping)
        namespaced_right = self._namespace_expression(expr.right, symbol_mapping)
        return BinaryOperation(expr.operator, namespaced_left, namespaced_right)

    def _namespace_unary_operation(self, expr, symbol_mapping):
        """Namespace a UnaryFunction."""
        namespaced_operand = self._namespace_expression(expr.operand, symbol_mapping)
        return type(expr)(expr.operator, namespaced_operand)

    def _namespace_binary_function(self, expr, symbol_mapping):
        """Namespace a BinaryFunction."""
        namespaced_left = self._namespace_expression(expr.left, symbol_mapping)
        namespaced_right = self._namespace_expression(expr.right, symbol_mapping)
        return type(expr)(expr.function_name, namespaced_left, namespaced_right)

    def _namespace_expression_for_lhs(self, expr, symbol_mapping):
        """
        Create a namespaced version of an expression for LHS, returning Variable objects.
        """
        
        if isinstance(expr, VariableReference):
            symbol = getattr(expr, 'symbol', None)
            if symbol and symbol in symbol_mapping:
                namespaced_symbol = symbol_mapping[symbol]
                if namespaced_symbol in self.variables:
                    return self.variables[namespaced_symbol]
            # If we can't find a mapping, return None since VariableReference doesn't have .equals()
            return None
        elif hasattr(expr, 'symbol') and expr.symbol in symbol_mapping:
            # This is a Variable object
            namespaced_symbol = symbol_mapping[expr.symbol]
            if namespaced_symbol in self.variables:
                return self.variables[namespaced_symbol]
            return expr
        else:
            return expr

    def _clone_variable(self, variable: Variable) -> Variable:
        """Create a copy of a variable to avoid shared state without corrupting global units."""
        # Create a new Variable with the same properties but avoid deepcopy
        # which can corrupt global unit objects
        cloned = Variable(
            name=variable.name,
            expected_dimension=variable.expected_dimension,
            is_known=variable.is_known
        )
        # Set attributes that are not part of constructor
        cloned.symbol = variable.symbol
        cloned.quantity = variable.quantity  # Keep reference to same quantity - units must not be copied
        
        # Ensure the cloned variable has fresh validation checks
        if hasattr(variable, 'validation_checks'):
            try:
                setattr(cloned, 'validation_checks', [])
            except (AttributeError, TypeError):
                # validation_checks might be read-only or not settable
                pass
        return cloned

    def _recreate_validation_checks(self):
        """Collect and integrate validation checks from class-level Check objects."""
        # Clear existing checks
        self.validation_checks = []
        
        # Collect Check objects from metaclass
        class_checks = getattr(self.__class__, '_class_checks', {})
        
        for check in class_checks.values():
            # Create a validation function from the Check object
            def make_check_function(check_obj):
                def check_function(problem_instance):
                    return check_obj.evaluate(problem_instance.variables)
                return check_function
            
            self.validation_checks.append(make_check_function(check))

    def _create_composite_equations(self):
        """
        Create composite equations for common patterns in sub-problems.
        This handles equations like P = min(header.P, branch.P) automatically.
        """
        if not self.sub_problems:
            return
        
        # Common composite patterns to auto-generate
        for var_name in COMMON_COMPOSITE_VARIABLES:
            # Check if this variable exists in multiple sub-problems
            sub_problem_vars = []
            for namespace in self.sub_problems:
                namespaced_symbol = f"{namespace}_{var_name}"
                if namespaced_symbol in self.variables:
                    sub_problem_vars.append(self.variables[namespaced_symbol])
            
            # If we have the variable in multiple sub-problems and no direct variable exists
            if len(sub_problem_vars) >= 2 and var_name in self.variables:
                # Check if a composite equation already exists
                equation_attr_name = f"{var_name}_eqn"
                if hasattr(self.__class__, equation_attr_name):
                    # Skip auto-creation since explicit equation exists
                    continue
                    
                # Auto-create composite equation
                try:
                    from qnty.expressions import min_expr
                    composite_var = self.variables[var_name]
                    if not composite_var.is_known:  # Only for unknown variables
                        composite_expr = min_expr(*sub_problem_vars)
                        equals_method = getattr(composite_var, 'equals', None)
                        if equals_method:
                            composite_eq = equals_method(composite_expr)
                            self.add_equation(composite_eq)
                            setattr(self, f"{var_name}_eqn", composite_eq)
                except Exception as e:
                    self.logger.debug(f"Failed to create composite equation for {var_name}: {e}")

    def _get_equation_lhs_symbol(self, equation: Equation) -> str | None:
        """Safely extract the symbol from equation's left-hand side."""
        return getattr(equation.lhs, 'symbol', None)

    def _is_conditional_equation(self, equation: Equation) -> bool:
        """Check if an equation is a conditional equation."""
        return 'cond(' in str(equation)

    def _equation_has_missing_variables(self, equation: Equation) -> bool:
        """Check if an equation references variables that don't exist in this problem."""
        try:
            all_vars = equation.get_all_variables()
            missing_vars = [var for var in all_vars if var not in self.variables]
            return len(missing_vars) > 0
        except Exception:
            return False

    def _has_invalid_self_references(self, equation: Equation) -> bool:
        """
        Check if an equation has invalid self-references.
        This catches malformed equations like 'c = max(c, c)' from class definition.
        """
        try:
            # Get LHS variable - check if it has symbol attribute
            lhs_symbol = self._get_equation_lhs_symbol(equation)
            if lhs_symbol is None:
                return False
            
            # Get all variables referenced in RHS
            rhs_vars = equation.rhs.get_variables() if hasattr(equation.rhs, 'get_variables') else set()
            
            # Check if the LHS variable appears multiple times in RHS (indicating self-reference)
            # This is a heuristic - a proper implementation would parse the expression tree
            equation_str = str(equation)
            if lhs_symbol in rhs_vars:
                # For conditional equations, self-references are often valid (as fallback values)
                if 'cond(' in equation_str:
                    return False  # Allow self-references in conditional equations
                
                # Count occurrences of the variable in the equation string
                count = equation_str.count(lhs_symbol)
                if count > 2:  # LHS + multiple RHS occurrences
                    return True
            
            return False
            
        except Exception:
            return False


    def _is_conditional_equation_from_subproblem(self, equation: Equation, _equation_name: str) -> bool:
        """
        Check if a conditional equation comes from a sub-problem and should be skipped in composed systems.
        
        In composed systems, if a sub-problem's conditional variable is already set to a known value,
        we don't want to include the conditional equation that would override that known value.
        """
        try:
            # Check if this is a conditional equation with a known LHS variable
            lhs_symbol = self._get_equation_lhs_symbol(equation)
            if lhs_symbol is not None:
                
                # Check if the LHS variable already exists and is known
                if lhs_symbol in self.variables:
                    var = self.variables[lhs_symbol]
                    # If the variable is already known (set explicitly in composition),
                    # and this conditional equation references missing variables, skip it
                    missing_vars = equation.get_all_variables() - set(self.variables.keys())
                    if missing_vars and var.is_known:
                        # This is a sub-problem's conditional equation for a variable that's already known
                        # No point including it since the value is already determined
                        return True
            
            return False
            
        except Exception:
            return False

    def _should_skip_subproblem_equation(self, equation: Equation, namespace: str) -> bool:
        """
        Check if an equation from a sub-problem should be skipped during integration.
        
        Skip conditional equations for variables that are set to known values in the composed problem.
        """
        try:
            # Check if this is a conditional equation
            if not self._is_conditional_equation(equation):
                return False
                
            # Check if the LHS variable would be set to a known value in composition
            original_symbol = self._get_equation_lhs_symbol(equation)
            if original_symbol is not None:
                namespaced_symbol = f"{namespace}_{original_symbol}"
                
                # Check if this namespaced variable exists and is already known
                if namespaced_symbol in self.variables:
                    var = self.variables[namespaced_symbol]
                    if var.is_known:
                        # The variable is already set to a known value in composition,
                        # so skip the conditional equation that would override it
                        self.logger.debug(f"Skipping conditional equation for {namespaced_symbol} (already known: {var.quantity})")
                        return True
            
            return False
            
        except Exception:
            return False

    # =============================================================================
    # VARIABLE MANAGEMENT METHODS
    # =============================================================================

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
            setattr(variable, '_parent_problem', self)
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

    def mark_unknown(self, *symbols: str) -> Problem:
        """Mark variables as unknown (to be solved for)."""
        for symbol in symbols:
            if symbol in self.variables:
                self.variables[symbol].mark_unknown()
            else:
                raise VariableNotFoundError(f"Variable '{symbol}' not found in problem '{self.name}'")
        self.is_solved = False
        self._invalidate_caches()
        return self
    
    def mark_known(self, **symbol_values: Qty) -> Problem:
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

    # =============================================================================
    # EQUATION MANAGEMENT METHODS
    # =============================================================================

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

    def _handle_missing_variables(self, missing_vars: list[str]) -> None:
        """Handle missing variables by creating placeholders for simple symbols."""
        for missing_var in missing_vars:
            if self._is_simple_variable_symbol(missing_var):
                self._create_placeholder_variable(missing_var)

    def _is_simple_variable_symbol(self, symbol: str) -> bool:
        """Check if a symbol looks like a simple variable identifier."""
        return (symbol.isidentifier() and
                not any(char in symbol for char in ['(', ')', '+', '-', '*', '/', ' ']))

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

    def add_equations(self, *equations: Equation) -> Problem:
        """Add multiple equations to the problem."""
        for eq in equations:
            self.add_equation(eq)
        return self

    # =============================================================================
    # PROBLEM SOLVING METHODS
    # =============================================================================

    def solve(self, max_iterations: int = MAX_ITERATIONS_DEFAULT, tolerance: float = TOLERANCE_DEFAULT) -> dict[str, Variable]:
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
        self.dependency_graph = Order()
        
        # Get known variables
        known_vars = self.get_known_symbols()
        
        # Add dependencies from equations
        for equation in self.equations:
            self.dependency_graph.add_equation(equation, known_vars)

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

    # =============================================================================
    # SYSTEM ANALYSIS METHODS
    # =============================================================================

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

    def reset_solution(self):
        """Reset the problem to unsolved state."""
        self.is_solved = False
        self.solution = {}
        self.solving_history = []
        
        # Reset unknown variables to unknown state
        for var in self.variables.values():
            if not var.is_known:
                var.is_known = False

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

    # =============================================================================
    # VALIDATION AND WARNING SYSTEM
    # =============================================================================

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

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    def copy(self) -> Problem:
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

    # =============================================================================
    # SPECIAL METHODS FOR ATTRIBUTE ACCESS
    # =============================================================================

    def __setattr__(self, name: str, value: Any) -> None:
        """Custom attribute setting to maintain variable synchronization."""
        # During initialization, use normal attribute setting
        if not hasattr(self, 'variables') or name.startswith('_'):
            super().__setattr__(name, value)
            return
        
        # If setting a variable that exists in our variables dict, update both
        if isinstance(value, Variable) and name in self.variables:
            self.variables[name] = value
        
        super().__setattr__(name, value)

    def __getitem__(self, key: str) -> Variable:
        """Allow dict-like access to variables."""
        return self.get_variable(key)

    def __setitem__(self, key: str, value: Variable) -> None:
        """Allow dict-like assignment of variables."""
        # Update the symbol to match the key if they differ
        if value.symbol != key:
            value.symbol = key
        self.add_variable(value)
    
    def _update_equation_variable_references(self, equation: Equation) -> Equation:
        """Update VariableReference objects in equation to use symbols instead of names."""
        from qnty.expressions import VariableReference
        
        # Update LHS if it's a VariableReference
        updated_lhs = equation.lhs
        if isinstance(equation.lhs, VariableReference):
            # Find the variable by name and update to use symbol
            var_name = equation.lhs.variable.name
            matching_var = None
            for var in self.variables.values():
                if var.name == var_name:
                    matching_var = var
                    break
            if matching_var and matching_var.symbol:
                updated_lhs = VariableReference(matching_var)
        
        # Update RHS by recursively updating expressions
        updated_rhs = self._update_expression_variable_references(equation.rhs)
        
        # Create new equation with updated references
        return Equation(equation.name, updated_lhs, updated_rhs)
    
    def _update_expression_variable_references(self, expr):
        """Recursively update VariableReference objects in expression tree."""
        from qnty.expressions import VariableReference, BinaryOperation, Constant
        
        if isinstance(expr, VariableReference):
            # Find the variable by name and update to use symbol
            var_name = expr.variable.name
            matching_var = None
            for var in self.variables.values():
                if var.name == var_name:
                    matching_var = var
                    break
            if matching_var and matching_var.symbol:
                return VariableReference(matching_var)
            return expr
        elif isinstance(expr, BinaryOperation):
            updated_left = self._update_expression_variable_references(expr.left)
            updated_right = self._update_expression_variable_references(expr.right)
            return BinaryOperation(expr.operator, updated_left, updated_right)
        elif isinstance(expr, Constant):
            return expr
        else:
            # Return unknown expression types as-is
            return expr
