"""
Sub-problem composition functionality for Problem class.

This module contains all the sub-problem integration logic,
namespace handling, and composite equation creation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qnty.quantities import TypeSafeVariable as Variable

# Constants for composition
MATHEMATICAL_OPERATORS = ['+', '-', '*', '/', ' / ', ' * ', ' + ', ' - ']
COMMON_COMPOSITE_VARIABLES = ['P', 'c', 'S', 'E', 'W', 'Y']


class CompositionMixin:
    """Mixin class providing sub-problem composition functionality."""
    
    # These attributes/methods will be provided by other mixins in the final Problem class
    variables: dict[str, Variable]
    sub_problems: dict[str, Any]
    logger: Any
    
    def add_variable(self, _variable: Variable) -> None:
        """Will be provided by VariablesMixin."""
        ...
    
    def add_equation(self, _equation: Any) -> None:
        """Will be provided by EquationsMixin."""
        ...
    
    def _clone_variable(self, _variable: Variable) -> Variable:
        """Will be provided by VariablesMixin."""
        ...
    
    def _process_equation(self, _attr_name: str, _equation: Any) -> bool:
        """Will be provided by EquationsMixin."""
        ...
    
    def _recreate_validation_checks(self) -> None:
        """Will be provided by ValidationMixin."""
        ...
    
    def _is_conditional_equation(self, _equation: Any) -> bool:
        """Will be provided by EquationsMixin."""
        ...
    
    def _get_equation_lhs_symbol(self, _equation: Any) -> str | None:
        """Will be provided by EquationsMixin."""
        ...

    def _extract_from_class_variables(self):
        """Extract variables, equations, and sub-problems from class-level definitions."""
        self._extract_sub_problems()
        self._extract_direct_variables()
        self._recreate_validation_checks()  # type: ignore[attr-defined]
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
        from qnty.quantities import TypeSafeVariable as Variable
        
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

    def _collect_class_equations(self) -> list[tuple[str, Any]]:
        """Collect all equation objects from class attributes."""
        from qnty.equations import Equation
        
        equations_to_process = []
        for attr_name, attr_value in self._get_class_attributes():
            if isinstance(attr_value, Equation):
                equations_to_process.append((attr_name, attr_value))
        return equations_to_process
    
    def _integrate_sub_problem(self, sub_problem, namespace: str) -> None:
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

    def _namespace_equation(self, equation, namespace: str):
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
        from qnty.expressions import BinaryOperation, ConditionalExpression, Constant, VariableReference
        
        # Handle variable references
        if isinstance(expr, VariableReference):
            return self._namespace_variable_reference(expr, symbol_mapping)
        elif hasattr(expr, 'symbol') and expr.symbol in symbol_mapping:
            return self._namespace_variable_object(expr, symbol_mapping)
        
        # Handle operations
        elif isinstance(expr, BinaryOperation):
            return self._namespace_binary_operation(expr, symbol_mapping)
        elif isinstance(expr, ConditionalExpression):
            return self._namespace_conditional_expression(expr, symbol_mapping)
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
        from qnty.expressions import VariableReference
        
        # VariableReference uses the 'name' property which returns the symbol if available
        symbol = expr.name
        if symbol in symbol_mapping:
            namespaced_symbol = symbol_mapping[symbol]
            if namespaced_symbol in self.variables:
                return VariableReference(self.variables[namespaced_symbol])
        return expr

    def _namespace_variable_object(self, expr, symbol_mapping):
        """Namespace a Variable object."""
        from qnty.expressions import VariableReference
        
        namespaced_symbol = symbol_mapping[expr.symbol]
        if namespaced_symbol in self.variables:
            # Return VariableReference for use in expressions, not the Variable itself
            return VariableReference(self.variables[namespaced_symbol])
        return expr

    def _namespace_binary_operation(self, expr, symbol_mapping):
        """Namespace a BinaryOperation."""
        from qnty.expressions import BinaryOperation
        
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

    def _namespace_conditional_expression(self, expr, symbol_mapping):
        """Namespace a ConditionalExpression."""
        from qnty.expressions import ConditionalExpression
        
        namespaced_condition = self._namespace_expression(expr.condition, symbol_mapping)
        namespaced_true_expr = self._namespace_expression(expr.true_expr, symbol_mapping)
        namespaced_false_expr = self._namespace_expression(expr.false_expr, symbol_mapping)
        
        return ConditionalExpression(namespaced_condition, namespaced_true_expr, namespaced_false_expr)

    def _namespace_expression_for_lhs(self, expr, symbol_mapping):
        """
        Create a namespaced version of an expression for LHS, returning Variable objects.
        """
        from qnty.expressions import VariableReference
        
        if isinstance(expr, VariableReference):
            # VariableReference uses the 'name' property which returns the symbol if available
            symbol = expr.name
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

    def _should_skip_subproblem_equation(self, equation, namespace: str) -> bool:
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
