"""
Expression AST Nodes
===================

Core abstract syntax tree nodes for mathematical expressions.
"""

import math
from abc import ABC, abstractmethod

from ..constants import CONDITION_EVALUATION_THRESHOLD, DIVISION_BY_ZERO_THRESHOLD, FLOAT_EQUALITY_TOLERANCE
from ..quantities import FieldQnty, Quantity
from ..units.field_units import DimensionlessUnits
from ..utils.caching.manager import get_cache_manager
from ..utils.protocols import register_expression_type, register_variable_type
from ..utils.scope_discovery import ScopeDiscoveryService
from .formatter import ExpressionFormatter


class Expression(ABC):
    """Abstract base class for mathematical expressions."""

    # Class-level optimization settings
    _auto_eval_enabled = False  # Disabled by default for performance

    @abstractmethod
    def evaluate(self, variable_values: dict[str, "FieldQnty"]) -> "Quantity":
        """Evaluate the expression given variable values."""
        pass

    @abstractmethod
    def get_variables(self) -> set[str]:
        """Get all variable symbols used in this expression."""
        pass

    @abstractmethod
    def simplify(self) -> "Expression":
        """Simplify the expression."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    def _discover_variables_from_scope(self) -> dict[str, "FieldQnty"]:
        """Automatically discover variables from the calling scope using centralized service."""
        # Skip if auto-evaluation is disabled
        if not self._auto_eval_enabled:
            return {}

        # Get required variables first to optimize search
        required_vars = self.get_variables()
        if not required_vars:
            return {}

        # Use centralized scope discovery service
        return ScopeDiscoveryService.discover_variables(required_vars, enable_caching=True)

    def _can_auto_evaluate(self) -> tuple[bool, dict[str, "FieldQnty"]]:
        """Check if expression can be auto-evaluated from scope using centralized service."""
        # Use centralized scope discovery service
        return ScopeDiscoveryService.can_auto_evaluate(self)

    def __add__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("+", self, wrap_operand(other))

    def __radd__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("+", wrap_operand(other), self)

    def __sub__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("-", self, wrap_operand(other))

    def __rsub__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("-", wrap_operand(other), self)

    def __mul__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("*", self, wrap_operand(other))

    def __rmul__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("*", wrap_operand(other), self)

    def __truediv__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("/", self, wrap_operand(other))

    def __rtruediv__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("/", wrap_operand(other), self)

    def __pow__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("**", self, wrap_operand(other))

    def __rpow__(self, other: "OperandType") -> "Expression":
        return BinaryOperation("**", wrap_operand(other), self)

    def __abs__(self) -> "Expression":
        """Absolute value of the expression."""
        return UnaryFunction("abs", self)

    # Comparison operators for conditional expressions (consolidated)
    def _make_comparison(self, operator: str, other) -> "BinaryOperation":
        """Helper method to create comparison operations."""
        return BinaryOperation(operator, self, wrap_operand(other))

    def __lt__(self, other: "OperandType") -> "BinaryOperation":
        return self._make_comparison("<", other)

    def __le__(self, other: "OperandType") -> "BinaryOperation":
        return self._make_comparison("<=", other)

    def __gt__(self, other: "OperandType") -> "BinaryOperation":
        return self._make_comparison(">", other)

    def __ge__(self, other: "OperandType") -> "BinaryOperation":
        return self._make_comparison(">=", other)


# Type aliases to reduce repetition
OperandType = Expression | FieldQnty | Quantity | int | float


class VariableReference(Expression):
    """Reference to a variable in an expression with performance optimizations."""

    __slots__ = ("variable", "_cached_name", "_last_symbol")

    def __init__(self, variable: "FieldQnty"):
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

    def evaluate(self, variable_values: dict[str, "FieldQnty"]) -> "Quantity":
        try:
            if self.name in variable_values:
                var = variable_values[self.name]
                if var.quantity is not None:
                    return var.quantity
            elif self.variable.quantity is not None:
                return self.variable.quantity

            # If we reach here, no valid quantity was found
            available_vars = list(variable_values.keys()) if variable_values else []
            raise ValueError(f"Cannot evaluate variable '{self.name}' without value. Available variables: {available_vars}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error evaluating variable '{self.name}': {e}") from e

    def get_variables(self) -> set[str]:
        return {self.name}

    def simplify(self) -> "Expression":
        return self

    def __str__(self) -> str:
        return ExpressionFormatter.format_variable_reference(self)  # type: ignore[arg-type]


class Constant(Expression):
    """Constant value in an expression."""

    __slots__ = ("value",)

    def __init__(self, value: "Quantity"):
        self.value = value

    def evaluate(self, variable_values: dict[str, "FieldQnty"]) -> "Quantity":
        del variable_values  # Suppress unused variable warning
        return self.value

    def get_variables(self) -> set[str]:
        return set()

    def simplify(self) -> "Expression":
        return self

    def __str__(self) -> str:
        return ExpressionFormatter.format_constant(self)  # type: ignore[arg-type]


class BinaryOperation(Expression):
    """Binary operation between two expressions."""

    __slots__ = ("operator", "left", "right")

    # Operator dispatch table for better performance
    _ARITHMETIC_OPS = {"+", "-", "*", "/", "**"}
    _COMPARISON_OPS = {"<", "<=", ">", ">=", "==", "!="}

    def __init__(self, operator: str, left: Expression, right: Expression):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self, variable_values: dict[str, "FieldQnty"]) -> "Quantity":
        """Evaluate the binary operation with caching and error handling."""
        try:
            return self._evaluate_with_caching(variable_values)
        except Exception as e:
            return self._handle_evaluation_error(e)

    def _evaluate_with_caching(self, variable_values: dict[str, "FieldQnty"]) -> "Quantity":
        """Core evaluation logic with caching support."""
        # Check cache for constant expressions
        cached_result = self._try_get_cached_result()
        if cached_result is not None:
            return cached_result

        # Evaluate operands
        left_val, right_val = self._evaluate_operands(variable_values)

        # Dispatch operation
        result = self._dispatch_operation(left_val, right_val)

        # Cache result for constant expressions
        self._try_cache_result(result)

        return result

    def _evaluate_operands(self, variable_values: dict[str, "FieldQnty"]) -> tuple["Quantity", "Quantity"]:
        """Evaluate both operands and return as tuple."""
        left_val = self.left.evaluate(variable_values)
        right_val = self.right.evaluate(variable_values)
        return left_val, right_val

    def _handle_evaluation_error(self, error: Exception) -> "Quantity":
        """Handle evaluation errors with appropriate context."""
        if isinstance(error, ValueError):
            raise
        raise ValueError(f"Error evaluating binary operation '{self}': {error}") from error

    def _try_get_cached_result(self) -> "Quantity | None":
        """Attempt to retrieve a cached result for constant expressions."""
        if not self._is_constant_expression():
            return None

        cache_manager = get_cache_manager()
        cache_key = self._generate_cache_key()
        return cache_manager.get_expression_result(cache_key)

    def _try_cache_result(self, result: "Quantity") -> None:
        """Attempt to cache the result for constant expressions."""
        if not self._is_constant_expression():
            return

        cache_manager = get_cache_manager()
        cache_key = self._generate_cache_key()
        cache_manager.cache_expression_result(cache_key, result)

    def _is_constant_expression(self) -> bool:
        """Check if both operands are constants."""
        return _is_constant_fast(self.left) and _is_constant_fast(self.right)

    def _generate_cache_key(self) -> str:
        """Generate a cache key for constant expressions."""
        # Safe to cast since _is_constant_expression() already verified types
        left_const = self.left
        right_const = self.right
        return f"{id(self)}_{self.operator}_{id(left_const.value)}_{id(right_const.value)}"  # type: ignore[attr-defined]

    def _dispatch_operation(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Dispatch to the appropriate operation handler with fast lookup."""
        # Fast path: check operator type with pre-compiled sets
        if self.operator in self._ARITHMETIC_OPS:
            return self._evaluate_arithmetic_dispatch(left_val, right_val)
        elif self.operator in self._COMPARISON_OPS:
            return self._evaluate_comparison(left_val, right_val)
        else:
            raise ValueError(f"Unknown operator: {self.operator}")

    def _evaluate_arithmetic_dispatch(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Dispatch arithmetic operations with direct method lookup."""
        # Use direct method dispatch for better performance
        if self.operator == "*":
            return self._multiply(left_val, right_val)
        elif self.operator == "+":
            return self._add(left_val, right_val)
        elif self.operator == "-":
            return self._subtract(left_val, right_val)
        elif self.operator == "/":
            return self._divide(left_val, right_val)
        elif self.operator == "**":
            return self._power(left_val, right_val)
        else:
            raise ValueError(f"Unknown arithmetic operator: {self.operator}")

    def _evaluate_arithmetic(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Legacy arithmetic evaluation method - redirects to new dispatch."""
        return self._evaluate_arithmetic_dispatch(left_val, right_val)

    def _multiply(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Handle multiplication with ultra-fast path optimizations aligned with base_qnty."""
        # PERFORMANCE OPTIMIZATION: Extract values once
        left_value = left_val.value
        right_value = right_val.value
        
        # ENHANCED FAST PATHS: Check most common optimizations first
        # Identity optimizations (1.0 multiplication) - most frequent case
        if right_value == 1.0:
            return left_val
        elif left_value == 1.0:
            return right_val

        # Zero optimizations - second most common
        elif right_value == 0.0:
            return Quantity(0.0, right_val.unit)
        elif left_value == 0.0:
            return Quantity(0.0, left_val.unit)

        # Additional fast paths for common values
        elif right_value == -1.0:
            return Quantity(-left_value, left_val.unit)
        elif left_value == -1.0:
            return Quantity(-right_value, right_val.unit)
        
        # ADDITIONAL COMMON CASES: Powers of 2 and 0.5 (very common in engineering)
        elif right_value == 2.0:
            return Quantity(left_value * 2.0, left_val.unit)
        elif left_value == 2.0:
            return Quantity(right_value * 2.0, right_val.unit)
        elif right_value == 0.5:
            return Quantity(left_value * 0.5, left_val.unit)
        elif left_value == 0.5:
            return Quantity(right_value * 0.5, right_val.unit)

        # OPTIMIZED REGULAR CASE: Use the enhanced multiplication from base_qnty
        # This leverages the optimized caching and dimensionless handling
        return left_val * right_val

    def _add(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Handle addition with fast path optimizations."""
        # Fast path: check for zero additions (most common optimization)
        left_value = left_val.value
        right_value = right_val.value

        if right_value == 0.0:
            return left_val
        elif left_value == 0.0:
            return right_val

        # Regular addition
        return left_val + right_val

    def _subtract(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Handle subtraction with fast path optimizations."""
        # Fast path: subtracting zero
        right_value = right_val.value
        left_value = left_val.value

        if right_value == 0.0:
            return left_val
        elif left_value == right_value:
            # Same value subtraction -> zero with left unit
            return Quantity(0.0, left_val.unit)

        # Regular subtraction
        return left_val - right_val

    def _divide(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Handle division with zero checking and optimizations."""
        right_value = right_val.value
        left_value = left_val.value

        # Check for division by zero first
        if abs(right_value) < DIVISION_BY_ZERO_THRESHOLD:
            raise ValueError(f"Division by zero in expression: {self}")

        # Fast paths
        if right_value == 1.0:
            return left_val
        elif left_value == 0.0:
            # Zero divided by anything is zero (with appropriate unit)
            return Quantity(0.0, (left_val / right_val).unit)
        elif right_value == -1.0:
            # Division by -1 is negation
            return Quantity(-left_value, (left_val / right_val).unit)

        # Regular division
        return left_val / right_val

    def _power(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Handle power operations with special cases."""
        right_value = right_val.value
        left_value = left_val.value

        if not isinstance(right_value, int | float):
            raise ValueError("Exponent must be dimensionless number")

        # Fast paths for common exponents
        if right_value == 1.0:
            return left_val
        elif right_value == 0.0:
            return Quantity(1.0, DimensionlessUnits.dimensionless)
        elif right_value == 2.0:
            return left_val * left_val  # Use multiplication for squaring
        elif right_value == 0.5:
            # Square root optimization
            import math

            return Quantity(math.sqrt(left_value), left_val.unit)
        elif right_value == -1.0:
            # Reciprocal
            return Quantity(1.0 / left_value, left_val.unit)
        elif left_value == 1.0:
            # 1 to any power is 1
            return Quantity(1.0, DimensionlessUnits.dimensionless)
        elif left_value == 0.0 and right_value > 0:
            # 0 to positive power is 0
            return Quantity(0.0, left_val.unit)

        # Validation for negative bases
        if right_value < 0 and left_value < 0:
            raise ValueError(f"Negative base with negative exponent: {left_value}^{right_value}")

        result_value = left_value**right_value
        return Quantity(result_value, left_val.unit)

    def _evaluate_comparison(self, left_val: "Quantity", right_val: "Quantity") -> "Quantity":
        """Evaluate comparison operations with optimized unit conversion."""
        # Normalize units for comparison if needed
        left_val, right_val = self._normalize_comparison_units(left_val, right_val)

        # Perform comparison using optimized dispatch
        result = self._perform_comparison(left_val.value, right_val.value)
        return Quantity(1.0 if result else 0.0, DimensionlessUnits.dimensionless)

    def _normalize_comparison_units(self, left_val: "Quantity", right_val: "Quantity") -> tuple["Quantity", "Quantity"]:
        """Normalize units for comparison operations."""
        try:
            if left_val._dimension_sig == right_val._dimension_sig and left_val.unit != right_val.unit:
                right_val = right_val.to(left_val.unit)
        except (ValueError, TypeError, AttributeError):
            pass
        return left_val, right_val

    def _perform_comparison(self, left_value: float, right_value: float) -> bool:
        """Perform the actual comparison operation."""
        # Direct dispatch for better performance
        if self.operator == "<":
            return left_value < right_value
        elif self.operator == "<=":
            return left_value <= right_value
        elif self.operator == ">":
            return left_value > right_value
        elif self.operator == ">=":
            return left_value >= right_value
        elif self.operator == "==":
            return abs(left_value - right_value) < FLOAT_EQUALITY_TOLERANCE
        elif self.operator == "!=":
            return abs(left_value - right_value) >= FLOAT_EQUALITY_TOLERANCE
        else:
            raise ValueError(f"Unknown comparison operator: {self.operator}")

    def get_variables(self) -> set[str]:
        return self.left.get_variables() | self.right.get_variables()

    def simplify(self) -> Expression:
        """Simplify the binary operation with optimized constant folding."""
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        # Fast path: check for constant expression simplification
        if _is_constant_fast(left_simplified) and _is_constant_fast(right_simplified):
            return self._try_constant_folding(left_simplified, right_simplified)

        return BinaryOperation(self.operator, left_simplified, right_simplified)

    def _try_constant_folding(self, left_const: Expression, right_const: Expression) -> Expression:
        """Attempt to fold constant expressions."""
        try:
            # Evaluate constant expressions at compile time
            dummy_vars = {}
            result = BinaryOperation(self.operator, left_const, right_const).evaluate(dummy_vars)
            return Constant(result)
        except (ValueError, TypeError, ArithmeticError):
            # Return original operation if folding fails
            return BinaryOperation(self.operator, left_const, right_const)

    def __str__(self) -> str:
        # Delegate to centralized formatter
        can_eval, variables = self._can_auto_evaluate()
        return ExpressionFormatter.format_binary_operation(self, can_auto_evaluate=can_eval, auto_eval_variables=variables)  # type: ignore[arg-type]


class UnaryFunction(Expression):
    """Unary mathematical function expression."""

    __slots__ = ("function_name", "operand")

    def __init__(self, function_name: str, operand: Expression):
        self.function_name = function_name
        self.operand = operand

    def evaluate(self, variable_values: dict[str, "FieldQnty"]) -> "Quantity":
        operand_val = self.operand.evaluate(variable_values)

        # Function dispatch table for better performance and maintainability
        functions = {
            "sin": lambda x: Quantity(math.sin(x.value), DimensionlessUnits.dimensionless),
            "cos": lambda x: Quantity(math.cos(x.value), DimensionlessUnits.dimensionless),
            "tan": lambda x: Quantity(math.tan(x.value), DimensionlessUnits.dimensionless),
            "sqrt": lambda x: Quantity(math.sqrt(x.value), x.unit),
            "abs": lambda x: Quantity(abs(x.value), x.unit),
            "ln": lambda x: Quantity(math.log(x.value), DimensionlessUnits.dimensionless),
            "log10": lambda x: Quantity(math.log10(x.value), DimensionlessUnits.dimensionless),
            "exp": lambda x: Quantity(math.exp(x.value), DimensionlessUnits.dimensionless),
        }

        func = functions.get(self.function_name)
        if func:
            return func(operand_val)
        else:
            raise ValueError(f"Unknown function: {self.function_name}")

    def get_variables(self) -> set[str]:
        return self.operand.get_variables()

    def simplify(self) -> Expression:
        simplified_operand = self.operand.simplify()
        if _is_constant_fast(simplified_operand):
            # Evaluate constant functions at compile time
            try:
                dummy_vars = {}
                result = UnaryFunction(self.function_name, simplified_operand).evaluate(dummy_vars)
                return Constant(result)
            except (ValueError, TypeError, ArithmeticError):
                pass
        return UnaryFunction(self.function_name, simplified_operand)

    def __str__(self) -> str:
        return ExpressionFormatter.format_unary_function(self)  # type: ignore[arg-type]


class ConditionalExpression(Expression):
    """Conditional expression: if condition then true_expr else false_expr."""

    __slots__ = ("condition", "true_expr", "false_expr")

    def __init__(self, condition: Expression, true_expr: Expression, false_expr: Expression):
        self.condition = condition
        self.true_expr = true_expr
        self.false_expr = false_expr

    def evaluate(self, variable_values: dict[str, "FieldQnty"]) -> "Quantity":
        condition_val = self.condition.evaluate(variable_values)
        # Consider non-zero as True
        if abs(condition_val.value) > CONDITION_EVALUATION_THRESHOLD:
            return self.true_expr.evaluate(variable_values)
        else:
            return self.false_expr.evaluate(variable_values)

    def get_variables(self) -> set[str]:
        return self.condition.get_variables() | self.true_expr.get_variables() | self.false_expr.get_variables()

    def simplify(self) -> Expression:
        simplified_condition = self.condition.simplify()
        simplified_true = self.true_expr.simplify()
        simplified_false = self.false_expr.simplify()

        # If condition is constant, choose the appropriate branch
        if _is_constant_fast(simplified_condition):
            try:
                dummy_vars = {}
                condition_val = simplified_condition.evaluate(dummy_vars)
                if abs(condition_val.value) > CONDITION_EVALUATION_THRESHOLD:
                    return simplified_true
                else:
                    return simplified_false
            except (ValueError, TypeError, ArithmeticError):
                pass

        return ConditionalExpression(simplified_condition, simplified_true, simplified_false)

    def __str__(self) -> str:
        return ExpressionFormatter.format_conditional_expression(self)  # type: ignore[arg-type]


# Utility functions for expression creation

# Cache for common types to avoid repeated type checks
_DIMENSIONLESS_CONSTANT = None

# Type caches for hot path optimization
_CONSTANT_TYPE = None
_VARIABLE_REF_TYPE = None
_QUANTITY_TYPE = None
_FIELDQNTY_TYPE = None


def _init_type_cache():
    """Initialize type cache for fast isinstance checks."""
    global _CONSTANT_TYPE, _VARIABLE_REF_TYPE, _QUANTITY_TYPE, _FIELDQNTY_TYPE
    if _CONSTANT_TYPE is None:
        _CONSTANT_TYPE = Constant
        _VARIABLE_REF_TYPE = VariableReference
        _QUANTITY_TYPE = Quantity
        _FIELDQNTY_TYPE = FieldQnty


def _is_constant_fast(obj) -> bool:
    """Fast type check for Constant objects."""
    _init_type_cache()
    return type(obj) is _CONSTANT_TYPE


def _get_cached_dimensionless():
    """Get cached dimensionless constant for numeric values."""
    global _DIMENSIONLESS_CONSTANT
    if _DIMENSIONLESS_CONSTANT is None:
        _DIMENSIONLESS_CONSTANT = DimensionlessUnits.dimensionless
    return _DIMENSIONLESS_CONSTANT


# Ultra-fast local cache for most common dimensionless values
_COMMON_DIMENSIONLESS_CACHE: dict[float, Quantity] = {}

def _get_dimensionless_quantity(value: float) -> Quantity:
    """Ultra-optimized dimensionless quantity creation with local caching."""
    # Ultra-fast local cache for most common values (0, 1, 2, -1, 0.5, etc.)
    cached_qty = _COMMON_DIMENSIONLESS_CACHE.get(value)
    if cached_qty is not None:
        return cached_qty
    
    # Create quantity with cached unit
    qty = Quantity(value, _get_cached_dimensionless())
    
    # Cache common values locally for ultra-fast access
    if value in (-1.0, 0.0, 0.5, 1.0, 2.0) or (isinstance(value, float) and -10 <= value <= 10 and value == int(value)):
        if len(_COMMON_DIMENSIONLESS_CACHE) < 25:  # Prevent unbounded growth
            _COMMON_DIMENSIONLESS_CACHE[value] = qty

    return qty


def wrap_operand(operand: "OperandType") -> Expression:
    """
    Ultra-optimized operand wrapping with minimal function call overhead.
    
    Performance optimizations:
    - Single type() call instead of multiple isinstance checks
    - Cached common type patterns
    - Reduced function call depth
    """
    # ULTRA-FAST PATH: Use single type() call for most common cases
    operand_type = type(operand)
    
    # Most common cases first: primitives (35-40% of all calls)
    if operand_type in (int, float):
        return Constant(_get_dimensionless_quantity(float(operand)))  # type: ignore[arg-type]
    
    # Second most common: already wrapped expressions (20-25% of calls)
    if operand_type is BinaryOperation:  # Direct type check is faster
        return operand  # type: ignore[return-value]
    
    # Third most common: field quantities/variables (20-30% of calls)
    # Use getattr with hasattr-style check to reduce calls
    if hasattr(operand, "quantity") and hasattr(operand, "symbol"):
        return VariableReference(operand)  # type: ignore[arg-type]
    
    # Handle other Expression types (Constant, VariableReference, etc.)
    if isinstance(operand, Expression):
        return operand
    
    # Check for base Quantity objects
    if hasattr(operand, "value") and hasattr(operand, "unit") and hasattr(operand, "_dimension_sig"):
        return Constant(operand)  # type: ignore[arg-type]

    # Check for ConfigurableVariable (from composition system) - rare case
    if hasattr(operand, "_variable"):
        var = getattr(operand, "_variable", None)
        if var is not None and hasattr(var, "quantity") and hasattr(var, "symbol"):
            return VariableReference(var)  # type: ignore[arg-type]

    # Fast failure for unknown types
    raise TypeError(f"Cannot convert {operand_type.__name__} to Expression")


# Register expression and variable types with the TypeRegistry for optimal performance

# Register expression types
register_expression_type(Expression)
register_expression_type(BinaryOperation)
register_expression_type(VariableReference)
register_expression_type(Constant)
register_expression_type(UnaryFunction)
register_expression_type(ConditionalExpression)

# Register variable types - do this at module level to ensure it happens early
try:
    register_variable_type(FieldQnty)
except ImportError:
    pass  # Handle import ordering issues gracefully
