"""
Composition system for EngineeringProblem sub-problems.

This module provides the infrastructure for composing engineering problems
from reusable sub-problems with clean syntax and automatic integration.
"""

from qnty.expressions import BinaryOperation, max_expr, min_expr, sin
from qnty.generated.quantities import Dimensionless
from qnty.quantities.quantity import TypeSafeVariable as Variable


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
        if not hasattr(SubProblemProxy, '_expressions_with_proxies'):
            SubProblemProxy._expressions_with_proxies = set()
        
    def __getattr__(self, name):
        # Handle internal Python attributes to prevent recursion during deepcopy
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
            
        if name in self._variable_cache:
            return self._variable_cache[name]
            
        if hasattr(self._sub_problem, name):
            attr_value = getattr(self._sub_problem, name)
            if isinstance(attr_value, Variable):
                # Create a properly namespaced variable immediately
                namespaced_var = self._create_namespaced_variable(attr_value)
                self._variable_cache[name] = namespaced_var
                return namespaced_var
        
        return getattr(self._sub_problem, name)
    
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
            original_symbol=original_var.symbol
        )
        
        return namespaced_var
    
    def track_configuration(self, original_symbol, quantity, is_known):
        """Track a configuration change made to a variable."""
        self._variable_configurations[original_symbol] = {
            'quantity': quantity,
            'is_known': is_known
        }
    
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
        if name.startswith('_') or name in ('_variable', '_proxy', '_original_symbol'):
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
    
    def mark_known(self, quantity=None):
        """Override mark_known to track configuration changes."""
        result = self._variable.mark_known(quantity)
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


class DelayedVariableReference:
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
    
    def __add__(self, other):
        return DelayedExpression('+', self, other)
    
    def __radd__(self, other):
        return DelayedExpression('+', other, self)
    
    def __sub__(self, other):
        return DelayedExpression('-', self, other)
    
    def __rsub__(self, other):
        return DelayedExpression('-', other, self)
    
    def __mul__(self, other):
        return DelayedExpression('*', self, other)
    
    def __rmul__(self, other):
        return DelayedExpression('*', other, self)
    
    def __truediv__(self, other):
        return DelayedExpression('/', self, other)
    
    def __rtruediv__(self, other):
        return DelayedExpression('/', other, self)


class DelayedExpression:
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
        if self.operation == '+':
            return left_resolved + right_resolved
        elif self.operation == '-':
            return left_resolved - right_resolved
        elif self.operation == '*':
            return left_resolved * right_resolved
        elif self.operation == '/':
            return left_resolved / right_resolved
        else:
            return BinaryOperation(self.operation, left_resolved, right_resolved)
    
    def _resolve_operand(self, operand, context):
        """Resolve a single operand to a Variable/Expression."""
        if isinstance(operand, DelayedVariableReference):
            return operand.resolve(context)
        elif isinstance(operand, DelayedExpression):
            return operand.resolve(context)
        elif hasattr(operand, 'resolve'):
            return operand.resolve(context)
        else:
            # It's a literal value or Variable
            return operand
    
    def __add__(self, other):
        return DelayedExpression('+', self, other)
    
    def __radd__(self, other):
        return DelayedExpression('+', other, self)
    
    def __sub__(self, other):
        return DelayedExpression('-', self, other)
    
    def __rsub__(self, other):
        return DelayedExpression('-', other, self)
    
    def __mul__(self, other):
        return DelayedExpression('*', self, other)
    
    def __rmul__(self, other):
        return DelayedExpression('*', other, self)
    
    def __truediv__(self, other):
        return DelayedExpression('/', self, other)
    
    def __rtruediv__(self, other):
        return DelayedExpression('/', other, self)


class DelayedFunction:
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
            if hasattr(arg, 'resolve'):
                resolved_arg = arg.resolve(context)
                if resolved_arg is None:
                    return None
                resolved_args.append(resolved_arg)
            else:
                resolved_args.append(arg)
        
        # Call the appropriate function
        if self.func_name == 'sin':
            return sin(resolved_args[0])
        elif self.func_name == 'min_expr':
            return min_expr(*resolved_args)
        elif self.func_name == 'max_expr':
            return max_expr(*resolved_args)
        else:
            # Generic function call
            return None
    
    def __add__(self, other):
        return DelayedExpression('+', self, other)
    
    def __radd__(self, other):
        return DelayedExpression('+', other, self)
    
    def __sub__(self, other):
        return DelayedExpression('-', self, other)
    
    def __rsub__(self, other):
        return DelayedExpression('-', other, self)
    
    def __mul__(self, other):
        return DelayedExpression('*', self, other)
    
    def __rmul__(self, other):
        return DelayedExpression('*', other, self)
    
    def __truediv__(self, other):
        return DelayedExpression('/', self, other)
    
    def __rtruediv__(self, other):
        return DelayedExpression('/', other, self)


# Delayed function factories
def delayed_sin(expr):
    return DelayedFunction('sin', expr)

def delayed_min_expr(*args):
    return DelayedFunction('min_expr', *args)

def delayed_max_expr(*args):
    return DelayedFunction('max_expr', *args)
