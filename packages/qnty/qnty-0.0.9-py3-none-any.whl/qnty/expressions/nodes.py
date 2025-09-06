"""
Expression AST Nodes
===================

Core abstract syntax tree nodes for mathematical expressions.
"""

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..quantities.quantity import Quantity, TypeSafeVariable

from ..generated.units import DimensionlessUnits
from ..quantities.quantity import Quantity, TypeSafeVariable
from .cache import _EXPRESSION_RESULT_CACHE, _MAX_EXPRESSION_CACHE_SIZE, wrap_operand


class Expression(ABC):
    """Abstract base class for mathematical expressions."""
    
    # Class-level optimization settings
    _scope_cache = {}
    _auto_eval_enabled = False  # Disabled by default for performance
    _max_scope_cache_size = 100  # Limit scope cache size
    
    @abstractmethod
    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'Quantity':
        """Evaluate the expression given variable values."""
        pass
    
    @abstractmethod
    def get_variables(self) -> set[str]:
        """Get all variable symbols used in this expression."""
        pass
    
    @abstractmethod
    def simplify(self) -> 'Expression':
        """Simplify the expression."""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    def _discover_variables_from_scope(self) -> dict[str, 'TypeSafeVariable']:
        """Automatically discover variables from the calling scope (optimized)."""
        # Skip if auto-evaluation is disabled
        if not self._auto_eval_enabled:
            return {}
            
        # Check cache first with size limit
        cache_key = id(self)
        if cache_key in self._scope_cache:
            return self._scope_cache[cache_key]
            
        # Clean cache if it gets too large
        if len(self._scope_cache) >= self._max_scope_cache_size:
            self._scope_cache.clear()
            
        import inspect
        
        # Get the frame that called this method (skip through __str__ calls)
        frame = inspect.currentframe()
        try:
            # Skip frames until we find one outside the expression system (with depth limit)
            depth = 0
            max_depth = 6  # Reduced from unlimited for performance
            while frame and depth < max_depth and (
                frame.f_code.co_filename.endswith('expression.py') or
                frame.f_code.co_name in ['__str__', '__repr__']
            ):
                frame = frame.f_back
                depth += 1
            
            if not frame:
                return {}
                
            # Get required variables first to optimize search
            required_vars = self.get_variables()
            if not required_vars:
                return {}
                
            discovered = {}
            
            # Search locals first (most common case)
            local_vars = frame.f_locals
            for var_name in required_vars:
                # Direct lookup first (fastest)
                if var_name in local_vars:
                    obj = local_vars[var_name]
                    if isinstance(obj, TypeSafeVariable):
                        discovered[var_name] = obj
                        continue
            
            # Search globals only for remaining variables
            if len(discovered) < len(required_vars):
                global_vars = frame.f_globals
                remaining_vars = required_vars - discovered.keys()
                for var_name in remaining_vars:
                    if var_name in global_vars:
                        obj = global_vars[var_name]
                        if isinstance(obj, TypeSafeVariable):
                            discovered[var_name] = obj
            
            # Cache the result
            self._scope_cache[cache_key] = discovered
            return discovered
            
        finally:
            del frame
    
    def _can_auto_evaluate(self) -> tuple[bool, dict[str, 'TypeSafeVariable']]:
        """Check if expression can be auto-evaluated from scope."""
        try:
            discovered = self._discover_variables_from_scope()
            required_vars = self.get_variables()
            
            # Check if all required variables are available and have values
            for var_name in required_vars:
                if var_name not in discovered:
                    return False, {}
                var = discovered[var_name]
                if not hasattr(var, 'quantity') or var.quantity is None:
                    return False, {}
            
            return True, discovered
            
        except Exception:
            return False, {}
    
    def __add__(self, other: Union['Expression', 'TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        return BinaryOperation('+', self, wrap_operand(other))
    
    def __radd__(self, other: Union['TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        return BinaryOperation('+', wrap_operand(other), self)
    
    def __sub__(self, other: Union['Expression', 'TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        return BinaryOperation('-', self, wrap_operand(other))
    
    def __rsub__(self, other: Union['TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        return BinaryOperation('-', wrap_operand(other), self)
    
    def __mul__(self, other: Union['Expression', 'TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        return BinaryOperation('*', self, wrap_operand(other))
    
    def __rmul__(self, other: Union['TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        return BinaryOperation('*', wrap_operand(other), self)
    
    def __truediv__(self, other: Union['Expression', 'TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        return BinaryOperation('/', self, wrap_operand(other))
    
    def __rtruediv__(self, other: Union['TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        return BinaryOperation('/', wrap_operand(other), self)
    
    def __pow__(self, other: Union['Expression', 'TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        return BinaryOperation('**', self, wrap_operand(other))
    
    def __rpow__(self, other: Union['TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        return BinaryOperation('**', wrap_operand(other), self)
    
    def __abs__(self) -> 'Expression':
        """Absolute value of the expression."""
        return UnaryFunction('abs', self)
    
    # Comparison operators for conditional expressions (consolidated)
    def _make_comparison(self, operator: str, other) -> 'BinaryOperation':
        """Helper method to create comparison operations."""
        return BinaryOperation(operator, self, wrap_operand(other))
    
    def __lt__(self, other: Union['Expression', 'TypeSafeVariable', 'Quantity', int, float]) -> 'BinaryOperation':
        return self._make_comparison('<', other)

    def __le__(self, other: Union['Expression', 'TypeSafeVariable', 'Quantity', int, float]) -> 'BinaryOperation':
        return self._make_comparison('<=', other)
    
    def __gt__(self, other: Union['Expression', 'TypeSafeVariable', 'Quantity', int, float]) -> 'BinaryOperation':
        return self._make_comparison('>', other)
    
    def __ge__(self, other: Union['Expression', 'TypeSafeVariable', 'Quantity', int, float]) -> 'BinaryOperation':
        return self._make_comparison('>=', other)
    
    @staticmethod
    def _wrap_operand(operand: Union['Expression', 'TypeSafeVariable', 'Quantity', int, float]) -> 'Expression':
        """Wrap non-Expression operands in appropriate Expression subclasses."""
        return wrap_operand(operand)


class VariableReference(Expression):
    """Reference to a variable in an expression with performance optimizations."""
    __slots__ = ('variable', '_cached_name', '_last_symbol')
    
    def __init__(self, variable: 'TypeSafeVariable'):
        self.variable = variable
        # Cache the name resolution to avoid repeated lookups
        self._cached_name = None
        self._last_symbol = None
    
    @property
    def name(self) -> str:
        """Get variable name with caching for performance."""
        current_symbol = self.variable.symbol
        if self._cached_name is None or self._last_symbol != current_symbol:
            # Use symbol for optinova compatibility, fall back to name if symbol not set
            self._cached_name = current_symbol if current_symbol else self.variable.name
            self._last_symbol = current_symbol
        return self._cached_name

    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'Quantity':
        try:
            if self.name in variable_values:
                var = variable_values[self.name]
                if var.quantity is not None:
                    return var.quantity
            elif self.variable.quantity is not None:
                return self.variable.quantity
            
            # If we reach here, no valid quantity was found
            available_vars = list(variable_values.keys()) if variable_values else []
            raise ValueError(
                f"Cannot evaluate variable '{self.name}' without value. "
                f"Available variables: {available_vars}"
            )
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error evaluating variable '{self.name}': {e}") from e
    
    def get_variables(self) -> set[str]:
        return {self.name}
    
    def simplify(self) -> 'Expression':
        return self
    
    def __str__(self) -> str:
        return self.name


class Constant(Expression):
    """Constant value in an expression."""
    __slots__ = ('value',)
    
    def __init__(self, value: 'Quantity'):
        self.value = value
    
    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'Quantity':
        del variable_values  # Suppress unused variable warning
        return self.value
    
    def get_variables(self) -> set[str]:
        return set()
    
    def simplify(self) -> 'Expression':
        return self
    
    def __str__(self) -> str:
        return str(self.value.value)


class BinaryOperation(Expression):
    """Binary operation between two expressions."""
    __slots__ = ('operator', 'left', 'right')
    
    # Operator dispatch table for better performance
    _ARITHMETIC_OPS = {'+', '-', '*', '/', '**'}
    _COMPARISON_OPS = {'<', '<=', '>', '>=', '==', '!='}
    
    def __init__(self, operator: str, left: Expression, right: Expression):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'Quantity':
        try:
            # Fast path for constant expressions (both sides are constants)
            if isinstance(self.left, Constant) and isinstance(self.right, Constant):
                cache_key = (id(self), self.operator, id(self.left.value), id(self.right.value))
                if cache_key in _EXPRESSION_RESULT_CACHE:
                    return _EXPRESSION_RESULT_CACHE[cache_key]
                
                # Clean cache if it gets too large
                if len(_EXPRESSION_RESULT_CACHE) >= _MAX_EXPRESSION_CACHE_SIZE:
                    _EXPRESSION_RESULT_CACHE.clear()
            else:
                cache_key = None
            
            left_val = self.left.evaluate(variable_values)
            right_val = self.right.evaluate(variable_values)
            
            # Fast dispatch for arithmetic operations
            if self.operator in self._ARITHMETIC_OPS:
                result = self._evaluate_arithmetic(left_val, right_val)
            elif self.operator in self._COMPARISON_OPS:
                result = self._evaluate_comparison(left_val, right_val)
            else:
                raise ValueError(f"Unknown operator: {self.operator}")
            
            # Cache result for constant expressions
            if cache_key is not None:
                _EXPRESSION_RESULT_CACHE[cache_key] = result
                
            return result
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error evaluating binary operation '{self}': {e}") from e
    
    def _evaluate_arithmetic(self, left_val: 'Quantity', right_val: 'Quantity') -> 'Quantity':
        """Evaluate arithmetic operations with fast paths."""
        # Fast path optimizations for common cases
        if self.operator == '*':
            # Fast path for multiplication by 1
            if right_val.value == 1.0:
                return left_val
            elif left_val.value == 1.0:
                return right_val
            # Fast path for multiplication by 0
            elif right_val.value == 0.0 or left_val.value == 0.0:
                return Quantity(0.0, left_val.unit if right_val.value == 0.0 else right_val.unit)
            return left_val * right_val
        elif self.operator == '+':
            # Fast path for addition with 0
            if right_val.value == 0.0:
                return left_val
            elif left_val.value == 0.0:
                return right_val
            return left_val + right_val
        elif self.operator == '-':
            # Fast path for subtraction with 0
            if right_val.value == 0.0:
                return left_val
            return left_val - right_val
        elif self.operator == '/':
            # Check for division by zero
            if abs(right_val.value) < 1e-15:
                raise ValueError(f"Division by zero in expression: {self}")
            # Fast path for division by 1
            if right_val.value == 1.0:
                return left_val
            return left_val / right_val
        elif self.operator == '**':
            # For power, right side should be dimensionless
            if isinstance(right_val.value, int | float):
                # Fast paths for common exponents
                if right_val.value == 1.0:
                    return left_val
                elif right_val.value == 0.0:
                    return Quantity(1.0, DimensionlessUnits.dimensionless)
                elif right_val.value == 2.0:
                    return left_val * left_val  # Use multiplication for squaring
                
                if right_val.value < 0 and left_val.value < 0:
                    raise ValueError(f"Negative base with negative exponent: {left_val.value}^{right_val.value}")
                result_value = left_val.value ** right_val.value
                # For power operations, we need to handle units carefully
                # This is a simplified implementation
                return Quantity(result_value, left_val.unit)
            else:
                raise ValueError("Exponent must be dimensionless number")
        else:
            # Unknown operator - should not happen
            raise ValueError(f"Unknown arithmetic operator: {self.operator}")
    
    def _evaluate_comparison(self, left_val: 'Quantity', right_val: 'Quantity') -> 'Quantity':
        """Evaluate comparison operations."""
        # Convert to same units for comparison if possible
        try:
            if left_val._dimension_sig == right_val._dimension_sig and left_val.unit != right_val.unit:
                right_val = right_val.to(left_val.unit)
        except (ValueError, TypeError, AttributeError):
            pass
        
        # Use dispatch dictionary for comparisons
        ops = {
            '<': lambda left, right: left < right,
            '<=': lambda left, right: left <= right,
            '>': lambda left, right: left > right,
            '>=': lambda left, right: left >= right,
            '==': lambda left, right: abs(left - right) < 1e-10,
            '!=': lambda left, right: abs(left - right) >= 1e-10
        }
        
        result = ops[self.operator](left_val.value, right_val.value)
        return Quantity(1.0 if result else 0.0, DimensionlessUnits.dimensionless)
    
    def get_variables(self) -> set[str]:
        return self.left.get_variables() | self.right.get_variables()
    
    def simplify(self) -> Expression:
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()
        
        # Basic simplification rules
        if isinstance(left_simplified, Constant) and isinstance(right_simplified, Constant):
            # Evaluate constant expressions
            dummy_vars = {}
            try:
                result = BinaryOperation(self.operator, left_simplified, right_simplified).evaluate(dummy_vars)
                return Constant(result)
            except (ValueError, TypeError, ArithmeticError):
                pass
        
        return BinaryOperation(self.operator, left_simplified, right_simplified)
    
    def __str__(self) -> str:
        # Try to auto-evaluate if all variables are available
        can_eval, variables = self._can_auto_evaluate()
        if can_eval:
            try:
                result = self.evaluate(variables)
                return str(result)
            except Exception:
                pass  # Fall back to symbolic representation
        
        # Handle operator precedence for cleaner string representation
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '**': 3, '<': 0, '<=': 0, '>': 0, '>=': 0, '==': 0, '!=': 0}
        left_str = str(self.left)
        right_str = str(self.right)
        
        # Add parentheses for left side when precedence is strictly lower
        if isinstance(self.left, BinaryOperation) and precedence.get(self.left.operator, 0) < precedence.get(self.operator, 0):
            left_str = f"({left_str})"
        
        # CRITICAL FIX: For right side, add parentheses when:
        # 1. Precedence is strictly lower, OR
        # 2. Precedence is equal AND operation is left-associative (-, /)
        if isinstance(self.right, BinaryOperation):
            right_prec = precedence.get(self.right.operator, 0)
            curr_prec = precedence.get(self.operator, 0)
            
            # Need parentheses if:
            # - Right has lower precedence, OR
            # - Same precedence and current operator is left-associative (- or /)
            if (right_prec < curr_prec or
                (right_prec == curr_prec and self.operator in ['-', '/'])):
                right_str = f"({right_str})"
            
        return f"{left_str} {self.operator} {right_str}"


class UnaryFunction(Expression):
    """Unary mathematical function expression."""
    __slots__ = ('function_name', 'operand')
    
    def __init__(self, function_name: str, operand: Expression):
        self.function_name = function_name
        self.operand = operand
    
    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'Quantity':
        
        operand_val = self.operand.evaluate(variable_values)
        
        if self.function_name == 'sin':
            # Assume input is in radians, result is dimensionless
            result_value = math.sin(operand_val.value)
            return Quantity(result_value, DimensionlessUnits.dimensionless)
        elif self.function_name == 'cos':
            result_value = math.cos(operand_val.value)
            return Quantity(result_value, DimensionlessUnits.dimensionless)
        elif self.function_name == 'tan':
            result_value = math.tan(operand_val.value)
            return Quantity(result_value, DimensionlessUnits.dimensionless)
        elif self.function_name == 'sqrt':
            # For sqrt, we need to handle units carefully
            result_value = math.sqrt(operand_val.value)
            # This is simplified - proper unit handling would need dimensional analysis
            return Quantity(result_value, operand_val.unit)
        elif self.function_name == 'abs':
            return Quantity(abs(operand_val.value), operand_val.unit)
        elif self.function_name == 'ln':
            # Natural log - input should be dimensionless
            result_value = math.log(operand_val.value)
            return Quantity(result_value, DimensionlessUnits.dimensionless)
        elif self.function_name == 'log10':
            result_value = math.log10(operand_val.value)
            return Quantity(result_value, DimensionlessUnits.dimensionless)
        elif self.function_name == 'exp':
            # Exponential - input should be dimensionless
            result_value = math.exp(operand_val.value)
            return Quantity(result_value, DimensionlessUnits.dimensionless)
        else:
            raise ValueError(f"Unknown function: {self.function_name}")
    
    def get_variables(self) -> set[str]:
        return self.operand.get_variables()
    
    def simplify(self) -> Expression:
        simplified_operand = self.operand.simplify()
        if isinstance(simplified_operand, Constant):
            # Evaluate constant functions at compile time
            try:
                dummy_vars = {}
                result = UnaryFunction(self.function_name, simplified_operand).evaluate(dummy_vars)
                return Constant(result)
            except (ValueError, TypeError, ArithmeticError):
                pass
        return UnaryFunction(self.function_name, simplified_operand)
    
    def __str__(self) -> str:
        return f"{self.function_name}({self.operand})"


class ConditionalExpression(Expression):
    """Conditional expression: if condition then true_expr else false_expr."""
    __slots__ = ('condition', 'true_expr', 'false_expr')
    
    def __init__(self, condition: Expression, true_expr: Expression, false_expr: Expression):
        self.condition = condition
        self.true_expr = true_expr
        self.false_expr = false_expr
    
    def evaluate(self, variable_values: dict[str, 'TypeSafeVariable']) -> 'Quantity':
        condition_val = self.condition.evaluate(variable_values)
        # Consider non-zero as True
        if abs(condition_val.value) > 1e-10:
            return self.true_expr.evaluate(variable_values)
        else:
            return self.false_expr.evaluate(variable_values)
    
    def get_variables(self) -> set[str]:
        return (self.condition.get_variables() |
                self.true_expr.get_variables() |
                self.false_expr.get_variables())
    
    def simplify(self) -> Expression:
        simplified_condition = self.condition.simplify()
        simplified_true = self.true_expr.simplify()
        simplified_false = self.false_expr.simplify()
        
        # If condition is constant, choose the appropriate branch
        if isinstance(simplified_condition, Constant):
            try:
                dummy_vars = {}
                condition_val = simplified_condition.evaluate(dummy_vars)
                if abs(condition_val.value) > 1e-10:
                    return simplified_true
                else:
                    return simplified_false
            except (ValueError, TypeError, ArithmeticError):
                pass
        
        return ConditionalExpression(simplified_condition, simplified_true, simplified_false)
    
    def __str__(self) -> str:
        return f"if({self.condition}, {self.true_expr}, {self.false_expr})"
