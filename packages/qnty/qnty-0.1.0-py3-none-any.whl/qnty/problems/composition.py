"""
Sub-problem composition system for EngineeringProblem.

This module provides the complete sub-problem integration system including:
- Sub-problem proxy objects for clean composition syntax
- Namespace handling and variable mapping
- Composite equation creation
- Metaclass system for automatic proxy creation

Combined from composition.py and composition_mixin.py for focused functionality.
"""

from __future__ import annotations

from typing import Any

from ..equations import Equation
from ..expressions import BinaryOperation, ConditionalExpression, Constant, VariableReference, max_expr, min_expr, sin
from ..expressions.nodes import wrap_operand
from ..quantities import Dimensionless, FieldQnty
from .rules import Rules

# Constants for composition
MATHEMATICAL_OPERATORS = ["+", "-", "*", "/", " / ", " * ", " + ", " - "]
COMMON_COMPOSITE_VARIABLES = ["P", "c", "S", "E", "W", "Y"]

# Constants for metaclass
RESERVED_ATTRIBUTES: set[str] = {"name", "description"}
PRIVATE_ATTRIBUTE_PREFIX = "_"
SUB_PROBLEM_REQUIRED_ATTRIBUTES: tuple[str, ...] = ("variables", "equations")


# ========== COMPOSITION CLASSES ==========


class ArithmeticOperationsMixin:
    """Mixin providing common arithmetic operations that create DelayedExpression objects."""

    def __add__(self, other):
        return DelayedExpression("+", self, other)

    def __radd__(self, other):
        return DelayedExpression("+", other, self)

    def __sub__(self, other):
        return DelayedExpression("-", self, other)

    def __rsub__(self, other):
        return DelayedExpression("-", other, self)

    def __mul__(self, other):
        return DelayedExpression("*", self, other)

    def __rmul__(self, other):
        return DelayedExpression("*", other, self)

    def __truediv__(self, other):
        return DelayedExpression("/", self, other)

    def __rtruediv__(self, other):
        return DelayedExpression("/", other, self)


class DelayedEquation:
    """
    Stores an equation definition that will be evaluated later when proper context is available.
    """

    def __init__(self, lhs_symbol, rhs_factory, name=None):
        self.lhs_symbol = lhs_symbol
        self.rhs_factory = rhs_factory  # Function that creates the RHS expression
        self.name = name or f"{lhs_symbol}_equation"

    def evaluate(self, context):
        """Evaluate the equation with the given context (namespace with variables)."""
        if self.lhs_symbol not in context:
            return None

        lhs_var = context[self.lhs_symbol]

        try:
            # Call the factory function with the context to create the RHS
            rhs_expr = self.rhs_factory(context)
            return lhs_var.equals(rhs_expr)
        except Exception:
            return None


class SubProblemProxy:
    """
    Proxy object that represents a sub-problem and provides namespaced variable access
    during class definition. Returns properly namespaced variables immediately to prevent
    malformed expressions.
    """

    def __init__(self, sub_problem, namespace):
        self._sub_problem = sub_problem
        self._namespace = namespace
        self._variable_cache = {}
        self._variable_configurations = {}  # Track configurations applied to variables
        # Global registry to track which expressions involve proxy variables
        if not hasattr(SubProblemProxy, "_expressions_with_proxies"):
            SubProblemProxy._expressions_with_proxies = set()

    def __getattr__(self, name):
        # Handle internal Python attributes to prevent recursion during deepcopy
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        if name in self._variable_cache:
            return self._variable_cache[name]

        try:
            attr_value = getattr(self._sub_problem, name)
            if isinstance(attr_value, FieldQnty):
                # Create a properly namespaced variable immediately
                namespaced_var = self._create_namespaced_variable(attr_value)
                self._variable_cache[name] = namespaced_var
                return namespaced_var
            return attr_value
        except AttributeError as e:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'") from e

    def _create_namespaced_variable(self, original_var):
        """Create a Variable with namespaced symbol for proper expression creation."""
        namespaced_symbol = f"{self._namespace}_{original_var.symbol}"

        # Create new Variable with namespaced symbol that tracks modifications
        namespaced_var = ConfigurableVariable(
            symbol=namespaced_symbol,
            name=f"{original_var.name} ({self._namespace.title()})",
            quantity=original_var.quantity,
            is_known=original_var.is_known,
            proxy=self,
            original_symbol=original_var.symbol,
        )

        return namespaced_var

    def track_configuration(self, original_symbol, quantity, is_known):
        """Track a configuration change made to a variable."""
        self._variable_configurations[original_symbol] = {"quantity": quantity, "is_known": is_known}

    def get_configurations(self):
        """Get all tracked configurations."""
        return self._variable_configurations.copy()


class ConfigurableVariable:
    """
    A Variable wrapper that can track configuration changes and report them back to its proxy.
    This acts as a proxy around the actual qnty Variable rather than inheriting from it.
    """

    def __init__(self, symbol, name, quantity, is_known=True, proxy=None, original_symbol=None):
        # Store the actual variable (we'll delegate to it)
        # Create a variable of the appropriate type based on the original
        # For now, we'll create a Dimensionless variable and update it
        self._variable = Dimensionless(name)

        # Set the properties
        self._variable.symbol = symbol
        self._variable.quantity = quantity
        self._variable.is_known = is_known

        # Store proxy information
        self._proxy = proxy
        self._original_symbol = original_symbol

    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped variable."""
        return getattr(self._variable, name)

    # Delegate arithmetic operations to the wrapped variable
    def __add__(self, other):
        return self._variable.__add__(other)

    def __radd__(self, other):
        return self._variable.__radd__(other)

    def __sub__(self, other):
        return self._variable.__sub__(other)

    def __rsub__(self, other):
        return self._variable.__rsub__(other)

    def __mul__(self, other):
        return self._variable.__mul__(other)

    def __rmul__(self, other):
        return self._variable.__rmul__(other)

    def __truediv__(self, other):
        return self._variable.__truediv__(other)

    def __rtruediv__(self, other):
        return self._variable.__rtruediv__(other)

    def __pow__(self, other):
        return self._variable.__pow__(other)

    def __neg__(self):
        # Implement negation as multiplication by -1, consistent with other arithmetic operations
        return self._variable * (-1)

    # Comparison operations
    def __lt__(self, other):
        return self._variable.__lt__(other)

    def __le__(self, other):
        return self._variable.__le__(other)

    def __gt__(self, other):
        return self._variable.__gt__(other)

    def __ge__(self, other):
        return self._variable.__ge__(other)

    def __eq__(self, other):
        return self._variable.__eq__(other)

    def __ne__(self, other):
        return self._variable.__ne__(other)

    def __setattr__(self, name, value):
        """Delegate attribute setting to the wrapped variable when appropriate."""
        if name.startswith("_") or name in ("_variable", "_proxy", "_original_symbol"):
            super().__setattr__(name, value)
        else:
            setattr(self._variable, name, value)

    def set(self, value):
        """Override set method to track configuration changes."""
        result = self._variable.set(value)
        if self._proxy and self._original_symbol:
            # Track this configuration change
            self._proxy.track_configuration(self._original_symbol, self._variable.quantity, self._variable.is_known)
        return result

    def update(self, value=None, unit=None, quantity=None, is_known=None):
        """Override update method to track configuration changes."""
        result = self._variable.update(value, unit, quantity, is_known)
        if self._proxy and self._original_symbol:
            # Track this configuration change
            self._proxy.track_configuration(self._original_symbol, self._variable.quantity, self._variable.is_known)
        return result

    def mark_known(self):
        """Override mark_known to track configuration changes."""
        result = self._variable.mark_known()
        if self._proxy and self._original_symbol:
            # Track this configuration change
            self._proxy.track_configuration(self._original_symbol, self._variable.quantity, self._variable.is_known)
        return result

    def mark_unknown(self):
        """Override mark_unknown to track configuration changes."""
        result = self._variable.mark_unknown()
        if self._proxy and self._original_symbol:
            # Track this configuration change
            self._proxy.track_configuration(self._original_symbol, self._variable.quantity, self._variable.is_known)
        return result


class DelayedVariableReference(ArithmeticOperationsMixin):
    """
    A placeholder for a variable that will be resolved to its namespaced version later.
    Supports arithmetic operations that create delayed expressions.
    """

    def __init__(self, namespace, symbol, original_var):
        self.namespace = namespace
        self.symbol = symbol
        self.original_var = original_var
        self._namespaced_symbol = f"{namespace}_{symbol}"

    def resolve(self, context):
        """Resolve to the actual namespaced variable from context."""
        return context.get(self._namespaced_symbol)


class DelayedExpression(ArithmeticOperationsMixin):
    """
    Represents an arithmetic expression that will be resolved later when context is available.
    Supports chaining of operations.
    """

    def __init__(self, operation, left, right):
        self.operation = operation
        self.left = left
        self.right = right

    def resolve(self, context):
        """Resolve this expression to actual Variable/Expression objects."""
        left_resolved = self._resolve_operand(self.left, context)
        right_resolved = self._resolve_operand(self.right, context)

        if left_resolved is None or right_resolved is None:
            return None

        # Create the actual expression
        if self.operation == "+":
            return left_resolved + right_resolved
        elif self.operation == "-":
            return left_resolved - right_resolved
        elif self.operation == "*":
            return left_resolved * right_resolved
        elif self.operation == "/":
            return left_resolved / right_resolved
        else:
            return BinaryOperation(self.operation, left_resolved, right_resolved)

    def _resolve_operand(self, operand, context):
        """Resolve a single operand to a Variable/Expression."""
        if isinstance(operand, DelayedVariableReference | DelayedExpression | DelayedFunction):
            return operand.resolve(context)
        else:
            # It's a literal value or Variable
            return operand


class DelayedFunction(ArithmeticOperationsMixin):
    """
    Represents a function call that will be resolved later when context is available.
    """

    def __init__(self, func_name, *args):
        self.func_name = func_name
        self.args = args

    def resolve(self, context):
        """Resolve function call with given context."""
        # Resolve all arguments
        resolved_args = []
        for arg in self.args:
            if isinstance(arg, DelayedVariableReference | DelayedExpression | DelayedFunction):
                resolved_arg = arg.resolve(context)
                if resolved_arg is None:
                    return None
                resolved_args.append(resolved_arg)
            else:
                resolved_args.append(arg)

        # Call the appropriate function
        if self.func_name == "sin":
            return sin(resolved_args[0])
        elif self.func_name == "min_expr":
            return min_expr(*resolved_args)
        elif self.func_name == "max_expr":
            return max_expr(*resolved_args)
        else:
            # Generic function call
            return None


# Delayed function factories
def delayed_sin(expr):
    return DelayedFunction("sin", expr)


def delayed_min_expr(*args):
    return DelayedFunction("min_expr", *args)


def delayed_max_expr(*args):
    return DelayedFunction("max_expr", *args)


# ========== COMPOSITION MIXIN ==========


class CompositionMixin:
    """Mixin class providing sub-problem composition functionality."""

    # These attributes/methods will be provided by other mixins in the final Problem class
    variables: dict[str, FieldQnty]
    sub_problems: dict[str, Any]
    logger: Any

    def add_variable(self, variable: FieldQnty) -> None:
        """Will be provided by Problem class."""
        del variable  # Unused in stub method
        ...

    def add_equation(self, equation: Equation) -> None:
        """Will be provided by Problem class."""
        del equation  # Unused in stub method
        ...

    def _clone_variable(self, variable: FieldQnty) -> FieldQnty:
        """Will be provided by Problem class."""
        return variable  # Stub method - return input as placeholder

    def _recreate_validation_checks(self) -> None:
        """Will be provided by ValidationMixin."""
        ...

    def _extract_from_class_variables(self):
        """Extract variables, equations, and sub-problems from class-level definitions."""
        self._extract_sub_problems()
        self._extract_direct_variables()
        self._recreate_validation_checks()
        self._create_composite_equations()
        self._extract_equations()

    def _extract_sub_problems(self):
        """Extract and integrate sub-problems from class-level definitions."""
        if hasattr(self.__class__, "_original_sub_problems"):
            original_sub_problems = getattr(self.__class__, "_original_sub_problems", {})
            for attr_name, sub_problem in original_sub_problems.items():
                self._integrate_sub_problem(sub_problem, attr_name)

    def _extract_direct_variables(self):
        """Extract direct variables from class-level definitions."""
        processed_symbols = set()

        # Single pass through class attributes to collect variables
        for attr_name, attr_value in self._get_class_attributes():
            if isinstance(attr_value, FieldQnty):
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
                # Add equation to the problem
                self.add_equation(equation)
                # Set the equation as an instance attribute
                setattr(self, attr_name, equation)
            except Exception as e:
                # Log but continue - some equations might fail during class definition
                self.logger.warning(f"Failed to process equation {attr_name}: {e}")
                # Still set the original equation as attribute
                setattr(self, attr_name, equation)

    def _get_class_attributes(self) -> list[tuple[str, Any]]:
        """Get all non-private class attributes efficiently."""
        return [(attr_name, getattr(self.__class__, attr_name)) for attr_name in dir(self.__class__) if not attr_name.startswith("_")]

    def _collect_class_equations(self) -> list[tuple[str, Any]]:
        """Collect all equation objects from class attributes."""
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
        proxy_configs = getattr(self.__class__, "_proxy_configurations", {}).get(namespace, {})

        namespace_obj = self._create_namespace_object(sub_problem, namespace, proxy_configs)
        super().__setattr__(namespace, namespace_obj)

        self._integrate_sub_problem_equations(sub_problem, namespace)

    def _create_namespace_object(self, sub_problem, namespace: str, proxy_configs: dict):
        """Create namespace object with all sub-problem variables."""
        namespace_obj = type("SubProblemNamespace", (), {})()

        for var_symbol, var in sub_problem.variables.items():
            namespaced_var = self._create_namespaced_variable(var, var_symbol, namespace, proxy_configs)
            self.add_variable(namespaced_var)

            # Set both namespaced access (self.header_P) and dotted access (self.header.P)
            if namespaced_var.symbol is not None:
                super().__setattr__(namespaced_var.symbol, namespaced_var)
            setattr(namespace_obj, var_symbol, namespaced_var)

        return namespace_obj

    def _integrate_sub_problem_equations(self, sub_problem, namespace: str):
        """Integrate equations from sub-problem with proper namespacing."""
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

    def _create_namespaced_variable(self, var: FieldQnty, var_symbol: str, namespace: str, proxy_configs: dict) -> FieldQnty:
        """Create a namespaced variable with proper configuration."""
        namespaced_symbol = f"{namespace}_{var_symbol}"
        namespaced_var = self._clone_variable(var)
        namespaced_var.symbol = namespaced_symbol
        namespaced_var.name = f"{var.name} ({namespace.title()})"

        # Apply proxy configuration if available
        if var_symbol in proxy_configs:
            config = proxy_configs[var_symbol]
            namespaced_var.quantity = config["quantity"]
            namespaced_var.is_known = config["is_known"]

        return namespaced_var

    def _namespace_equation(self, equation, namespace: str):
        """
        Create a namespaced version of an equation by prefixing all variable references.
        """
        try:
            # Get all variable symbols in the equation
            variables_in_eq = equation.get_all_variables()

            # Create mapping from original symbols to namespaced symbols
            symbol_mapping = self._create_symbol_mapping(variables_in_eq, namespace)
            if not symbol_mapping:
                return None

            # Create new equation with namespaced references
            return self._create_namespaced_equation(equation, symbol_mapping)

        except Exception:
            return None

    def _create_symbol_mapping(self, variables_in_eq: set[str], namespace: str) -> dict[str, str]:
        """Create mapping from original symbols to namespaced symbols."""
        symbol_mapping = {}
        for var_symbol in variables_in_eq:
            namespaced_symbol = f"{namespace}_{var_symbol}"
            if namespaced_symbol in self.variables:
                symbol_mapping[var_symbol] = namespaced_symbol
        return symbol_mapping

    def _create_namespaced_equation(self, equation: Equation, symbol_mapping: dict[str, str]) -> Equation | None:
        """Create new equation with namespaced references."""
        # For LHS, we need a Variable object to call .equals()
        # For RHS, we need proper expression structure
        namespaced_lhs = self._namespace_expression_for_lhs(equation.lhs, symbol_mapping)
        namespaced_rhs = self._namespace_expression(equation.rhs, symbol_mapping)

        if namespaced_lhs and namespaced_rhs and hasattr(namespaced_lhs, "equals"):
            return namespaced_lhs.equals(namespaced_rhs)
        return None

    def _namespace_expression(self, expr, symbol_mapping):
        """
        Create a namespaced version of an expression by replacing variable references.
        """
        # Handle variable references
        if isinstance(expr, VariableReference):
            return self._namespace_variable_reference(expr, symbol_mapping)
        elif isinstance(expr, FieldQnty) and expr.symbol in symbol_mapping:
            return self._namespace_variable_object(expr, symbol_mapping)

        # Handle operations
        elif isinstance(expr, BinaryOperation):
            return self._namespace_binary_operation(expr, symbol_mapping)
        elif isinstance(expr, ConditionalExpression):
            return self._namespace_conditional_expression(expr, symbol_mapping)
        elif self._is_unary_operation(expr):
            return self._namespace_unary_operation(expr, symbol_mapping)
        elif self._is_binary_function(expr):
            return self._namespace_binary_function(expr, symbol_mapping)
        elif isinstance(expr, Constant):
            return expr
        else:
            return expr

    def _namespace_variable_reference(self, expr: VariableReference, symbol_mapping: dict[str, str]) -> VariableReference:
        """Namespace a VariableReference object."""
        # VariableReference uses the 'name' property which returns the symbol if available
        symbol = expr.name
        if symbol in symbol_mapping:
            namespaced_symbol = symbol_mapping[symbol]
            if namespaced_symbol in self.variables:
                return VariableReference(self.variables[namespaced_symbol])
        return expr

    def _namespace_variable_object(self, expr: FieldQnty, symbol_mapping: dict[str, str]) -> VariableReference | FieldQnty:
        """Namespace a Variable object."""
        if expr.symbol is None:
            return expr
        namespaced_symbol = symbol_mapping[expr.symbol]
        if namespaced_symbol in self.variables:
            # Return VariableReference for use in expressions, not the Variable itself
            return VariableReference(self.variables[namespaced_symbol])
        return expr

    def _namespace_binary_operation(self, expr: BinaryOperation, symbol_mapping: dict[str, str]) -> BinaryOperation:
        """Namespace a BinaryOperation."""
        namespaced_left = self._namespace_expression(expr.left, symbol_mapping)
        namespaced_right = self._namespace_expression(expr.right, symbol_mapping)
        return BinaryOperation(expr.operator, wrap_operand(namespaced_left), wrap_operand(namespaced_right))

    def _namespace_unary_operation(self, expr, symbol_mapping):
        """Namespace a UnaryFunction."""
        namespaced_operand = self._namespace_expression(expr.operand, symbol_mapping)
        return type(expr)(expr.operator, namespaced_operand)

    def _namespace_binary_function(self, expr, symbol_mapping):
        """Namespace a BinaryFunction."""
        namespaced_left = self._namespace_expression(expr.left, symbol_mapping)
        namespaced_right = self._namespace_expression(expr.right, symbol_mapping)
        return type(expr)(expr.function_name, namespaced_left, namespaced_right)

    def _namespace_conditional_expression(self, expr: ConditionalExpression, symbol_mapping: dict[str, str]) -> ConditionalExpression:
        """Namespace a ConditionalExpression."""
        namespaced_condition = self._namespace_expression(expr.condition, symbol_mapping)
        namespaced_true_expr = self._namespace_expression(expr.true_expr, symbol_mapping)
        namespaced_false_expr = self._namespace_expression(expr.false_expr, symbol_mapping)

        return ConditionalExpression(wrap_operand(namespaced_condition), wrap_operand(namespaced_true_expr), wrap_operand(namespaced_false_expr))

    def _namespace_expression_for_lhs(self, expr, symbol_mapping: dict[str, str]) -> FieldQnty | None:
        """
        Create a namespaced version of an expression for LHS, returning Variable objects.
        """
        if isinstance(expr, VariableReference):
            # VariableReference uses the 'name' property which returns the symbol if available
            symbol = expr.name
            if symbol and symbol in symbol_mapping:
                namespaced_symbol = symbol_mapping[symbol]
                if namespaced_symbol in self.variables:
                    return self.variables[namespaced_symbol]
            # If we can't find a mapping, return None since VariableReference doesn't have .equals()
            return None
        elif isinstance(expr, FieldQnty) and expr.symbol in symbol_mapping:
            # This is a Variable object
            namespaced_symbol = symbol_mapping[expr.symbol]
            if namespaced_symbol in self.variables:
                return self.variables[namespaced_symbol]
            return expr
        else:
            return expr

    def _is_unary_operation(self, expr) -> bool:
        """Check if expression is a unary operation."""
        # UnaryFunction and similar classes have an 'operand' attribute
        return hasattr(expr, "operand") and hasattr(expr, "operator")

    def _is_binary_function(self, expr) -> bool:
        """Check if expression is a binary function."""
        # BinaryFunction classes have 'function_name', 'left', and 'right' attributes
        return hasattr(expr, "function_name") and hasattr(expr, "left") and hasattr(expr, "right")

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
                    composite_var = self.variables[var_name]
                    if not composite_var.is_known:  # Only for unknown variables
                        composite_expr = min_expr(*sub_problem_vars)
                        equals_method = getattr(composite_var, "equals", None)
                        if equals_method:
                            composite_eq = equals_method(composite_expr)
                            self.add_equation(composite_eq)
                            setattr(self, f"{var_name}_eqn", composite_eq)
                except Exception as e:
                    self.logger.debug(f"Failed to create composite equation for {var_name}: {e}")

    # Placeholder methods that will be provided by Problem class
    def _process_equation(self, attr_name: str, equation: Equation) -> bool:
        """Will be provided by Problem class."""
        del attr_name, equation  # Unused in stub method
        return True

    def _is_conditional_equation(self, _equation: Equation) -> bool:
        """Will be provided by Problem class."""
        return "cond(" in str(_equation)

    def _get_equation_lhs_symbol(self, equation: Equation) -> str | None:
        """Will be provided by Problem class."""
        return getattr(equation.lhs, "symbol", None)


# ========== METACLASS SYSTEM ==========


# Custom exceptions for better error handling
class MetaclassError(Exception):
    """Base exception for metaclass-related errors."""

    pass


class SubProblemProxyError(MetaclassError):
    """Raised when sub-problem proxy creation fails."""

    pass


class NamespaceError(MetaclassError):
    """Raised when namespace operations fail."""

    pass


class ProblemMeta(type):
    """
    Metaclass that processes class-level sub-problems to create proper namespace proxies
    BEFORE any equations are evaluated.

    This metaclass enables clean composition syntax like:
        class MyProblem(EngineeringProblem):
            header = create_pipe_problem()
            branch = create_pipe_problem()
            # Equations can reference header.P, branch.T, etc.
    """

    # Declare the attributes that will be dynamically added to created classes
    _original_sub_problems: dict[str, Any]
    _proxy_configurations: dict[str, dict[str, Any]]
    _class_checks: dict[str, Any]

    @classmethod
    def __prepare__(mcs, *args, **kwargs) -> ProxiedNamespace:
        """
        Called before the class body is evaluated.
        Returns a custom namespace that proxies sub-problems.

        Args:
            *args: Positional arguments (name, bases) - unused but required by protocol
            **kwargs: Additional keyword arguments - unused but required by protocol

        Returns:
            ProxiedNamespace that will handle sub-problem proxying
        """
        # Parameters are required by metaclass protocol but not used in this implementation
        del args, kwargs  # Explicitly acknowledge unused parameters
        return ProxiedNamespace()

    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: ProxiedNamespace, **kwargs) -> type:
        """
        Create the new class with properly integrated sub-problems.

        Args:
            name: Name of the class being created
            bases: Base classes
            namespace: The ProxiedNamespace containing proxied sub-problems
            **kwargs: Additional keyword arguments - unused but required by protocol

        Returns:
            The newly created class with metaclass attributes

        Raises:
            MetaclassError: If class creation fails due to metaclass issues
        """
        # kwargs is required by metaclass protocol but not used in this implementation
        del kwargs  # Explicitly acknowledge unused parameter
        try:
            # Validate the namespace
            if not isinstance(namespace, ProxiedNamespace):
                raise MetaclassError(f"Expected ProxiedNamespace, got {type(namespace)}")

            # Extract the original sub-problems and proxy objects from the namespace
            sub_problem_proxies = getattr(namespace, "_sub_problem_proxies", {})
            proxy_objects = getattr(namespace, "_proxy_objects", {})

            # Validate that proxy objects are consistent
            if set(sub_problem_proxies.keys()) != set(proxy_objects.keys()):
                raise MetaclassError("Inconsistent proxy state: sub-problem and proxy object keys don't match")

            # Create the class normally
            cls = super().__new__(mcs, name, bases, dict(namespace))

            # Store the original sub-problems and proxy configurations for later integration
            cls._original_sub_problems = sub_problem_proxies

            # Extract configurations safely with error handling
            proxy_configurations = {}
            for proxy_name, proxy in proxy_objects.items():
                try:
                    # Cache configurations to avoid recomputation
                    if not hasattr(proxy, "_cached_configurations"):
                        proxy._cached_configurations = proxy.get_configurations()
                    proxy_configurations[proxy_name] = proxy._cached_configurations
                except Exception as e:
                    raise SubProblemProxyError(f"Failed to get configurations from proxy '{proxy_name}': {e}") from e

            cls._proxy_configurations = proxy_configurations

            # Collect Check objects from class attributes
            checks = {}
            for attr_name, attr_value in namespace.items():
                if isinstance(attr_value, Rules):
                    checks[attr_name] = attr_value

            cls._class_checks = checks

            return cls

        except Exception as e:
            # Re-raise MetaclassError and SubProblemProxyError as-is
            if isinstance(e, MetaclassError | SubProblemProxyError):
                raise
            # Wrap other exceptions
            raise MetaclassError(f"Failed to create class '{name}': {e}") from e


class ProxiedNamespace(dict):
    """
    Custom namespace that automatically proxies sub-problems as they're added.

    This namespace intercepts class attribute assignments during class creation
    and automatically wraps EngineeringProblem objects in SubProblemProxy objects.
    This enables clean composition syntax where sub-problems can be referenced
    with dot notation in equations.

    Example:
        class ComposedProblem(EngineeringProblem):
            header = create_pipe_problem()  # Gets proxied automatically
            branch = create_pipe_problem()  # Gets proxied automatically
            # Now equations can use header.P, branch.T, etc.
    """

    def __init__(self) -> None:
        """Initialize the proxied namespace with empty storage."""
        super().__init__()
        self._sub_problem_proxies: dict[str, Any] = {}
        self._proxy_objects: dict[str, SubProblemProxy] = {}

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Intercept attribute assignment and proxy sub-problems automatically.

        Args:
            key: The attribute name being set
            value: The value being assigned

        Raises:
            NamespaceError: If namespace operation fails
            SubProblemProxyError: If proxy creation fails
        """
        try:
            if self._is_sub_problem(key, value):
                self._create_and_store_proxy(key, value)
            elif self._is_variable_with_auto_symbol(value):
                self._set_variable_symbol_and_store(key, value)
            else:
                super().__setitem__(key, value)
        except Exception as e:
            if isinstance(e, NamespaceError | SubProblemProxyError):
                raise
            raise NamespaceError(f"Failed to set attribute '{key}': {e}") from e

    def _is_sub_problem(self, key: str, value: Any) -> bool:
        """
        Determine if a value should be treated as a sub-problem.

        Args:
            key: The attribute name
            value: The value being assigned

        Returns:
            True if this should be proxied as a sub-problem
        """
        # Quick checks first (fail fast)
        if key.startswith(PRIVATE_ATTRIBUTE_PREFIX) or key in RESERVED_ATTRIBUTES:
            return False

        # Check for None or basic types that definitely aren't sub-problems
        if value is None or isinstance(value, str | int | float | bool | list | dict):
            return False

        # Cache hasattr results to avoid repeated attribute lookups
        if not hasattr(self, "_attr_cache"):
            self._attr_cache = {}

        # Use object id as cache key since objects are unique
        cache_key = (id(value), tuple(SUB_PROBLEM_REQUIRED_ATTRIBUTES))
        if cache_key not in self._attr_cache:
            self._attr_cache[cache_key] = all(hasattr(value, attr) for attr in SUB_PROBLEM_REQUIRED_ATTRIBUTES)

        return self._attr_cache[cache_key]

    def _is_variable_with_auto_symbol(self, value: Any) -> bool:
        """
        Determine if a value is a Variable that needs automatic symbol assignment.

        Args:
            value: The value being assigned

        Returns:
            True if this is a Variable that needs automatic symbol assignment
        """
        # Import Variable here to avoid circular imports
        try:
            if not isinstance(value, FieldQnty):
                return False
            # Auto-assign symbol if:
            # 1. Symbol is explicitly "<auto>", OR
            # 2. Symbol equals the variable name (default behavior, no explicit symbol set)
            return value.symbol == "<auto>" or value.symbol == value.name
        except ImportError:
            return False

    def _set_variable_symbol_and_store(self, key: str, value: Any) -> None:
        """
        Set the variable's symbol to the attribute name and store it.

        Args:
            key: The attribute name to use as symbol
            value: The Variable object
        """
        try:
            # Set the symbol to the attribute name
            value.symbol = key
            # Store the modified variable
            super().__setitem__(key, value)
        except Exception as e:
            raise NamespaceError(f"Failed to set symbol for variable '{key}': {e}") from e

    def _create_and_store_proxy(self, key: str, value: Any) -> None:
        """
        Create a proxy for the sub-problem and store references.

        Args:
            key: The attribute name for the sub-problem
            value: The sub-problem object to proxy

        Raises:
            SubProblemProxyError: If proxy creation fails
            NamespaceError: If key already exists as a sub-problem
        """
        # Check for conflicts
        if key in self._sub_problem_proxies:
            raise NamespaceError(f"Sub-problem '{key}' already exists in namespace")

        try:
            # Store the original sub-problem
            self._sub_problem_proxies[key] = value

            # Create and store the proxy
            proxy = SubProblemProxy(value, key)
            self._proxy_objects[key] = proxy

            # Set the proxy in the namespace
            super().__setitem__(key, proxy)

        except Exception as e:
            # Clean up partial state on failure
            self._sub_problem_proxies.pop(key, None)
            self._proxy_objects.pop(key, None)
            raise SubProblemProxyError(f"Failed to create proxy for sub-problem '{key}': {e}") from e


# Export all relevant classes
__all__ = [
    "CompositionMixin",
    "ProblemMeta",
    "ProxiedNamespace",
    "SubProblemProxy",
    "ConfigurableVariable",
    "DelayedEquation",
    "DelayedVariableReference",
    "DelayedExpression",
    "DelayedFunction",
    "delayed_sin",
    "delayed_min_expr",
    "delayed_max_expr",
    "MetaclassError",
    "SubProblemProxyError",
    "NamespaceError",
]
