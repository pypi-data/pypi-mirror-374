"""
Equation reconstruction system for handling composite expressions.

This module provides the advanced equation reconstruction capabilities
that allow EngineeringProblem to automatically fix malformed equations
created during composition and proxy operations.
"""

import re
from logging import Logger
from re import Pattern
from typing import Any

from qnty.equations.equation import Equation
from qnty.expressions import BinaryOperation, Constant, UnaryFunction, VariableReference, cos, sin
from qnty.quantities.expression_quantity import ExpressionQuantity as Variable
from qnty.quantities.quantity import Quantity as Qty

# No BinaryFunction in qnty - operations are handled by BinaryOperation or specific functions


# Type aliases for better readability
VariableDict = dict[str, Variable]
NamespaceMapping = dict[str, str]
ReconstructionResult = Equation | None

# Type alias for valid expression types that can be used with Variable.equals()
# This represents all types that the equals() method accepts as its expression parameter
ValidExpressionType = (
    VariableReference | BinaryOperation | UnaryFunction | Constant |
    Variable | Qty | int | float
)

# Tuple of types for isinstance() checks - extracted from ValidExpressionType
# Note: isinstance() requires a tuple of types, not a Union type, so we maintain both:
# - ValidExpressionType: for type annotations and documentation
# - VALID_EXPRESSION_TYPES: for runtime isinstance() checks
VALID_EXPRESSION_TYPES = (
    VariableReference, BinaryOperation, UnaryFunction, Constant,
    Variable, Qty, int, float
)

# Constants for better maintainability and performance
EXCLUDED_FUNCTION_NAMES: set[str] = {'sin', 'cos', 'max', 'min', 'exp', 'log', 'sqrt', 'tan'}
MATH_OPERATORS: set[str] = {'(', ')', '+', '-', '*', '/'}
CONDITIONAL_PATTERNS: set[str] = {'cond('}
FUNCTION_PATTERNS: set[str] = {'sin(', 'cos(', 'tan(', 'log(', 'exp('}

# Compiled regex patterns for performance
VARIABLE_PATTERN: Pattern[str] = re.compile(r'\b[A-Za-z][A-Za-z0-9_]*\b')
VARIABLE_PATTERN_DETAILED: Pattern[str] = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b')


# Custom exceptions for better error handling
class EquationReconstructionError(Exception):
    """Base exception for equation reconstruction errors."""
    pass


class MalformedExpressionError(EquationReconstructionError):
    """Raised when expressions are malformed and cannot be reconstructed."""
    pass


class NamespaceMappingError(EquationReconstructionError):
    """Raised when namespace mapping fails."""
    pass


class PatternReconstructionError(EquationReconstructionError):
    """Raised when mathematical pattern reconstruction fails."""
    pass


class EquationReconstructor:
    """
    Handles reconstruction of equations with composite expressions.

    This class provides advanced equation reconstruction capabilities that allow
    EngineeringProblem to automatically fix malformed equations created during
    composition and proxy operations. It uses pattern matching, namespace mapping,
    and expression parsing to reconstruct valid equations from composite symbols.

    Key Features:
    - Generic composite expression reconstruction
    - Malformed equation recovery from proxy operations
    - Namespace variable mapping and resolution
    - Mathematical pattern parsing and rebuilding
    - Performance optimization through caching

    Example Usage:
        reconstructor = EquationReconstructor(problem)
        fixed_equation = reconstructor.fix_malformed_equation(broken_equation)
    """

    def __init__(self, problem: Any) -> None:
        """
        Initialize the equation reconstructor.

        Args:
            problem: The EngineeringProblem instance containing variables and logger

        Raises:
            ValueError: If problem doesn't have required attributes
        """
        if not hasattr(problem, 'variables') or not hasattr(problem, 'logger'):
            raise ValueError("Problem must have 'variables' and 'logger' attributes")

        self.problem: Any = problem
        self.variables: VariableDict = problem.variables
        self.logger: Logger = problem.logger

        # Performance optimization: cache compiled patterns and mappings
        # Performance optimization: cache compiled patterns and mappings
        self._namespace_cache: dict[str, set[str]] = {}
        self._variable_mapping_cache: dict[frozenset, NamespaceMapping] = {}

        # Cache commonly accessed data for performance
        self._all_variable_names: set[str] | None = None

    def _is_valid_expression_type(self, obj: Any) -> bool:
        """
        Check if an object is a valid expression type for use with Variable.equals().

        Args:
            obj: The object to check

        Returns:
            True if the object is a valid expression type
        """
        return isinstance(obj, VALID_EXPRESSION_TYPES)

    def fix_malformed_equation(self, equation: Equation) -> ReconstructionResult:
        """
        Generic method to fix equations that were malformed during class definition.

        Specifically handles composite expressions like '(D - (T - c) * 2.0)' that should
        reference namespaced variables like 'branch_D', 'branch_T', 'branch_c'.

        Args:
            equation: The malformed equation to fix

        Returns:
            Fixed equation if reconstruction succeeds, None otherwise

        Raises:
            EquationReconstructionError: If equation reconstruction fails with detailed error
        """
        if equation is None:
            return None

        try:
            # Get all variables referenced in the equation
            all_vars = equation.get_all_variables()
            missing_vars = [var for var in all_vars if var not in self.variables]

            if not missing_vars:
                return equation  # Nothing to fix

            self.logger.debug(f"Found missing variables in equation: {missing_vars}")

            # Attempt to reconstruct equations with composite variables using generic approach
            fixed_equation = self._reconstruct_composite_expressions(equation, missing_vars)

            if fixed_equation:
                self.logger.debug(f"Successfully reconstructed equation: {fixed_equation}")
                return fixed_equation
            else:
                self.logger.debug("Failed to reconstruct equation")
                return None

        except Exception as e:
            self.logger.debug(f"Error in fix_malformed_equation: {e}")
            return None

    def _reconstruct_composite_expressions(self, equation: Equation, missing_vars: list[str]) -> ReconstructionResult:
        """
        Generic reconstruction of equations with composite expressions.

        Handles cases where expressions like '(D - (T - c) * 2.0)' need to be
        mapped to proper namespaced variables by analyzing the structure and
        finding the best matching variables in available namespaces.

        Args:
            equation: The equation to reconstruct
            missing_vars: List of missing variable names

        Returns:
            Reconstructed equation if successful, None otherwise

        Raises:
            NamespaceMappingError: If namespace mapping fails
        """
        if not missing_vars:
            return None

        try:
            # Extract variable symbols from composite expressions
            composite_vars = self._extract_base_variables_from_composites(missing_vars)

            if not composite_vars:
                self.logger.debug("No composite variables found to extract")
                return None

            # Find which namespaces contain these variables
            namespace_mappings = self._find_namespace_mappings(composite_vars)

            if not namespace_mappings:
                self.logger.debug("No namespace mappings found")
                return None

            # Reconstruct the equation by substituting composite expressions
            return self._substitute_composite_expressions(equation, missing_vars, namespace_mappings)

        except Exception as e:
            self.logger.debug(f"Error in _reconstruct_composite_expressions: {e}")
            return None

    def _extract_base_variables_from_composites(self, missing_vars: list[str]) -> set[str]:
        """
        Extract base variable symbols from composite expressions.

        Args:
            missing_vars: List of missing variable names from composite expressions

        Returns:
            Set of base variable symbols found in the expressions

        Example:
            '(D - (T - c) * 2.0)' -> {'D', 'T', 'c'}
        """
        if not missing_vars:
            return set()

        base_vars: set[str] = set()

        for missing_var in missing_vars:
            # Use compiled regex for better performance
            matches = VARIABLE_PATTERN.findall(missing_var)

            for match in matches:
                # Filter out obvious non-variable terms using constant set
                if match not in EXCLUDED_FUNCTION_NAMES:
                    base_vars.add(match)

        return base_vars

    def _find_namespace_mappings(self, base_vars: set[str]) -> NamespaceMapping:
        """
        Find which namespace each base variable should map to.

        Args:
            base_vars: Set of base variable symbols to map

        Returns:
            Mapping from base variable names to namespaced variable names

        Example:
            {'D': 'branch_D', 'T': 'header_T', 'c': 'branch_c'}

        Raises:
            NamespaceMappingError: If mapping fails for critical variables
        """
        if not base_vars:
            return {}

        # Use cache key for performance optimization
        cache_key = frozenset(base_vars)
        if cache_key in self._variable_mapping_cache:
            return self._variable_mapping_cache[cache_key]

        mappings: NamespaceMapping = {}

        # For each base variable, find the best namespace match
        for base_var in base_vars:
            candidates = self._find_namespace_candidates(base_var)

            # Use heuristics to pick the best candidate
            if len(candidates) == 1:
                mappings[base_var] = candidates[0]
            elif len(candidates) > 1:
                # If multiple candidates, use context clues or pick first namespace alphabetically
                best_candidate = sorted(candidates)[0]
                mappings[base_var] = best_candidate
                self.logger.debug(f"Multiple candidates for '{base_var}': {candidates}, chose '{best_candidate}'")
            else:
                self.logger.debug(f"No candidates found for base variable: {base_var}")

        # Cache the result for performance
        self._variable_mapping_cache[cache_key] = mappings
        return mappings

    def _find_namespace_candidates(self, base_var: str) -> list[str]:
        """
        Find all possible namespace candidates for a base variable.

        Args:
            base_var: Base variable name to find candidates for

        Returns:
            List of candidate namespaced variable names
        """
        candidates = []

        # Cache variable names for performance
        if self._all_variable_names is None:
            self._all_variable_names = set(self.variables.keys())

        # Look for exact matches in namespaced variables
        for var_name in self._all_variable_names:
            if '_' in var_name:
                _, var_part = var_name.split('_', 1)  # namespace not needed here
                if var_part == base_var:
                    candidates.append(var_name)

        return candidates

    def _clear_caches(self) -> None:
        """
        Clear all internal caches. Should be called when variables change.

        This method provides a way to reset cached data when the problem
        state changes, ensuring cache consistency.
        """
        self._namespace_cache.clear()
        self._variable_mapping_cache.clear()
        self._all_variable_names = None

    def _substitute_composite_expressions(self, equation: Equation, missing_vars: list[str], namespace_mappings: NamespaceMapping) -> ReconstructionResult:
        """
        Substitute composite expressions with properly namespaced variables.

        Args:
            equation: The equation to substitute expressions in
            missing_vars: List of missing variable names
            namespace_mappings: Mapping from base variables to namespaced variables

        Returns:
            Reconstructed equation if successful, None otherwise
        """
        if not missing_vars or not namespace_mappings:
            return None

        try:
            # Get the equation string representation for debugging
            eq_str = str(equation)
            self.logger.debug(f"Substituting expressions in equation: {eq_str}")

            # For each missing composite expression, try to rebuild it
            for missing_var in missing_vars:
                if missing_var in eq_str:
                    reconstructed_expr = self._reconstruct_expression_from_mapping(missing_var, namespace_mappings)
                    if reconstructed_expr:
                        # Replace the original equation's RHS or LHS
                        if isinstance(equation.lhs, VariableReference):
                            var_name = equation.lhs.name
                            if var_name and var_name in self.variables:
                                lhs_var = self.variables[var_name]
                                return lhs_var.equals(reconstructed_expr)
                        elif hasattr(equation.lhs, 'symbol'):
                            symbol = getattr(equation.lhs, 'symbol', None)
                            if symbol and symbol in self.variables:
                                lhs_var = self.variables[symbol]
                                return lhs_var.equals(reconstructed_expr)

            return None

        except Exception as e:
            self.logger.debug(f"Error in _substitute_composite_expressions: {e}")
            return None

    def _reconstruct_expression_from_mapping(self, composite_expr: str, namespace_mappings: NamespaceMapping) -> Any | None:
        """
        Reconstruct a composite expression using the namespace mappings.

        This method now uses generic parsing instead of hardcoded patterns.

        Args:
            composite_expr: The composite expression string to reconstruct
            namespace_mappings: Mapping from base variables to namespaced variables

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        if not composite_expr or not namespace_mappings:
            return None

        try:
            # Create a substitution pattern for the expression
            substituted_expr = composite_expr

            # Replace base variable names with their namespaced counterparts
            for base_var, namespaced_var in namespace_mappings.items():
                if namespaced_var in self.variables:
                    # Use word boundary regex to avoid partial matches
                    import re
                    pattern = r'\b' + re.escape(base_var) + r'\b'
                    substituted_expr = re.sub(pattern, namespaced_var, substituted_expr)

            # Try to evaluate the substituted expression using our generic parser
            return self.parse_composite_expression_pattern(substituted_expr)

        except Exception as e:
            self.logger.debug(f"Error in generic expression reconstruction: {e}")
            return None

    def _matches_common_pattern(self, expression: str) -> bool:
        """
        Check if expression matches patterns that can be reconstructed.

        Args:
            expression: The expression string to check

        Returns:
            True if expression contains mathematical operators and variables
        """
        # Generic check - any expression with mathematical operators and variable names
        return (any(char in expression for char in '+-*/()') and
                any(char.isalpha() for char in expression))

    def contains_delayed_expressions(self, equation: Equation) -> bool:
        """
        Check if an equation contains delayed expressions that need resolution.

        Args:
            equation: The equation to check for delayed expressions

        Returns:
            True if equation contains delayed expressions
        """
        if equation is None:
            return False

        try:
            # Check if the RHS contains delayed expressions
            return self._expression_has_delayed_components(equation.rhs)
        except Exception as e:
            self.logger.debug(f"Error checking delayed expressions: {e}")
            return False

    def _expression_has_delayed_components(self, expr: Any) -> bool:
        """
        Recursively check if an expression contains delayed components.

        Args:
            expr: The expression to check

        Returns:
            True if expression contains delayed components
        """
        if expr is None:
            return False

        if hasattr(expr, 'resolve'):
            # This is a delayed component
            return True

        # Check if it's an equation with delayed RHS
        if hasattr(expr, 'rhs') and hasattr(expr.rhs, 'resolve'):
            return True

        # For expressions with operands, check recursively
        if hasattr(expr, 'left') and hasattr(expr, 'right'):
            return (self._expression_has_delayed_components(expr.left) or
                    self._expression_has_delayed_components(expr.right))

        if hasattr(expr, 'operand'):
            return self._expression_has_delayed_components(expr.operand)

        if hasattr(expr, 'args'):
            return any(self._expression_has_delayed_components(arg) for arg in expr.args)

        return False

    def resolve_delayed_equation(self, equation: Equation) -> ReconstructionResult:
        """
        Resolve a delayed equation by evaluating its delayed expressions.

        Args:
            equation: The equation with delayed expressions to resolve

        Returns:
            Resolved equation if successful, None otherwise
        """
        if equation is None:
            return None

        try:
            # Create context with all current variables
            context = self.variables.copy()

            # If the RHS is delayed, resolve it
            if hasattr(equation.rhs, 'resolve'):
                resolve_method = getattr(equation.rhs, 'resolve', None)
                if callable(resolve_method):
                    resolved_rhs = resolve_method(context)
                    if resolved_rhs:
                        # Get the left-hand side variable
                        lhs_var = None
                        if isinstance(equation.lhs, VariableReference):
                            var_name = equation.lhs.name
                            if var_name in context:
                                lhs_var = context[var_name]
                        elif hasattr(equation.lhs, 'symbol'):
                            symbol = getattr(equation.lhs, 'symbol', None)
                            if isinstance(symbol, str) and symbol in context:
                                lhs_var = context[symbol]

                        if lhs_var:
                            # Type check resolved_rhs for safety
                            if self._is_valid_expression_type(resolved_rhs):
                                # Safe to use - type checker knows this is valid
                                typed_rhs: ValidExpressionType = resolved_rhs  # type: ignore[assignment]
                                return lhs_var.equals(typed_rhs)
                            else:
                                self.logger.debug(f"Resolved RHS has invalid type: {type(resolved_rhs)}")
                                return None

            return None

        except Exception as e:
            self.logger.debug(f"Error resolving delayed equation: {e}")
            return None

    def should_attempt_reconstruction(self, equation: Equation) -> bool:
        """
        Determine if we should attempt to reconstruct this equation.

        Only attempt reconstruction for simple mathematical expressions,
        not complex structures like conditionals.

        Args:
            equation: The equation to evaluate for reconstruction

        Returns:
            True if reconstruction should be attempted
        """
        if equation is None:
            return False

        try:
            equation_str = str(equation)

            # Skip conditional equations using constant set
            if any(pattern in equation_str for pattern in CONDITIONAL_PATTERNS):
                return False

            # Skip equations with complex function calls
            if any(func in equation_str for func in FUNCTION_PATTERNS):
                # These might be complex - only attempt if they're in the problematic patterns
                self.logger.debug(f"Equation contains complex functions: {equation_str}")
                pass

            # Only attempt if the missing variables look like mathematical expressions
            all_vars = equation.get_all_variables()
            missing_vars = [var for var in all_vars if var not in self.variables]

            for missing_var in missing_vars:
                # Check if this looks like a mathematical expression we can handle
                if any(char in missing_var for char in MATH_OPERATORS):
                    return True

            return False

        except Exception as e:
            self.logger.debug(f"Error in should_attempt_reconstruction: {e}")
            return False

    def reconstruct_composite_expressions_generically(self, equation: Equation) -> ReconstructionResult:
        """
        Generically reconstruct equations with composite expressions by parsing the
        composite symbols and rebuilding them from existing variables.

        Enhanced to handle malformed expressions from proxy evaluation.

        Args:
            equation: The equation to reconstruct

        Returns:
            Reconstructed equation if successful, None otherwise

        Raises:
            MalformedExpressionError: If expressions are too malformed to reconstruct
        """
        if equation is None:
            return None

        try:
            all_vars = equation.get_all_variables()
            missing_vars = [var for var in all_vars if var not in self.variables]

            if not missing_vars:
                return equation

            # Get the LHS variable with proper validation
            lhs_var = self._get_lhs_variable(equation)
            if lhs_var is None:
                return None

            # Check for malformed expressions that contain evaluated numeric values
            malformed_vars = self._identify_malformed_variables(missing_vars)

            if malformed_vars:
                # This is a malformed expression from proxy evaluation
                reconstructed_rhs = self._reconstruct_malformed_proxy_expression(equation, malformed_vars)
                if reconstructed_rhs:
                    return lhs_var.equals(reconstructed_rhs)
                return None

            # Reconstruct the RHS by parsing and rebuilding composite expressions
            reconstructed_rhs = self.parse_and_rebuild_expression(equation.rhs, missing_vars)

            if reconstructed_rhs:
                return lhs_var.equals(reconstructed_rhs)

            return None

        except Exception as e:
            self.logger.debug(f"Reconstruction failed: {e}")
            return None

    def _get_lhs_variable(self, equation: Equation) -> Variable | None:
        """
        Safely extract the left-hand side variable from an equation.

        Args:
            equation: The equation to extract LHS from

        Returns:
            The LHS variable if valid, None otherwise
        """
        # Check if lhs is a VariableReference
        if isinstance(equation.lhs, VariableReference):
            var_name = equation.lhs.name
            if var_name in self.variables:
                return self.variables[var_name]
        # Check if lhs is a Variable with symbol attribute
        elif hasattr(equation.lhs, 'symbol'):
            symbol = getattr(equation.lhs, 'symbol', None)
            if isinstance(symbol, str) and symbol in self.variables:
                return self.variables[symbol]

        return None

    def _identify_malformed_variables(self, missing_vars: list[str]) -> list[str]:
        """
        Identify variables that are malformed due to proxy evaluation.

        Args:
            missing_vars: List of missing variable names

        Returns:
            List of malformed variable names
        """
        # Look for missing variables that have composite patterns (parentheses and operators)
        return [var for var in missing_vars
                if ('(' in var and ')' in var and
                    any(op in var for op in MATH_OPERATORS))]

    def _reconstruct_malformed_proxy_expression(self, equation: Equation, malformed_vars: list[str]) -> Any | None:  # noqa: ARG002
        """
        Generically reconstruct expressions that were malformed due to proxy evaluation.

        Args:
            equation: The equation containing malformed expressions
            malformed_vars: List of malformed variable names (kept for signature compatibility)

        Returns:
            Reconstructed expression if successful, None otherwise

        Note:
            Malformed variables look like: "(var1 - (var2 - var3) * 2.0) = 1.315 in"
            We extract the mathematical pattern and rebuild it symbolically using existing variables.
            The malformed_vars parameter is kept for potential future use and API consistency.
        """
        eq_str = str(equation)
        self.logger.debug(f"Reconstructing malformed equation: {eq_str}")

        try:
            # Extract the RHS expression from the equation
            if hasattr(equation, 'rhs'):
                rhs_expr = equation.rhs
                return self._rebuild_expression_from_malformed(rhs_expr)
        except Exception as e:
            self.logger.debug(f"Failed to reconstruct malformed expression: {e}")

        return None

    def _rebuild_expression_from_malformed(self, expr: Any) -> Any | None:
        """
        Recursively rebuild an expression that contains malformed variable references.
        """
        if isinstance(expr, VariableReference):
            # Check if this is a malformed variable reference
            var_symbol = expr.name
            if ' = ' in var_symbol:
                # This is malformed - try to extract the original pattern
                return self.parse_malformed_variable_pattern(var_symbol)
            elif var_symbol in self.variables:
                return expr
            elif (any(op in var_symbol for op in ['+', '-', '*', '/']) and
                  any(char.isalpha() for char in var_symbol) and var_symbol.count('_') >= 1):
                # This is a composite expression pattern - try to parse and rebuild it
                return self.parse_composite_expression_pattern(var_symbol)
            else:
                return None

        elif hasattr(expr, 'symbol') and isinstance(getattr(expr, 'symbol', None), str):
            # This might be a malformed Variable object (not VariableReference)
            var_symbol = expr.symbol
            if ' = ' in var_symbol:
                # This is malformed - try to extract the original pattern
                return self.parse_malformed_variable_pattern(var_symbol)
            elif var_symbol in self.variables:
                return self.variables[var_symbol]
            else:
                return None

        elif isinstance(expr, BinaryOperation):
            # Recursively rebuild operands
            left_rebuilt = self._rebuild_expression_from_malformed(expr.left)
            right_rebuilt = self._rebuild_expression_from_malformed(expr.right)

            if left_rebuilt and right_rebuilt:
                return BinaryOperation(expr.operator, left_rebuilt, right_rebuilt)

        elif isinstance(expr, UnaryFunction):
            operand_rebuilt = self._rebuild_expression_from_malformed(expr.operand)
            if operand_rebuilt:
                if expr.function_name == 'sin':
                    return sin(operand_rebuilt)
                elif expr.function_name == 'cos':
                    return cos(operand_rebuilt)
                else:
                    return UnaryFunction(expr.function_name, operand_rebuilt)

        elif isinstance(expr, Constant):
            return expr

        return None

    def parse_composite_expression_pattern(self, composite_symbol: str) -> Any | None:
        """
        Parse a composite expression pattern and reconstruct it using available variables.

        Args:
            composite_symbol: The composite expression string to parse

        Returns:
            Reconstructed expression if successful, None otherwise

        Examples:
            - "(branch_D - (branch_T_n - branch_c) * 2.0)" -> branch_D - 2.0 * (branch_T_n - branch_c)
            - "(header_T - header_c) * 2.5" -> (header_T - header_c) * 2.5
            - "d_2 * 2.0" -> d_2 * 2.0
            - "S_r / header_S" -> S_r / header_S
        """
        if not composite_symbol:
            return None

        pattern = composite_symbol

        # Handle simple patterns first (variable op constant/variable)
        simple_result = self._handle_simple_composite_patterns(pattern)
        if simple_result:
            return simple_result

        # Remove outer parentheses if the entire pattern is wrapped
        pattern = self._remove_outer_parentheses(pattern)

        # Extract variable names that exist in our system using compiled regex
        potential_vars = VARIABLE_PATTERN_DETAILED.findall(pattern)
        existing_vars = [var for var in potential_vars if var in self.variables]

        if len(existing_vars) < 1:
            self.logger.debug(f"No existing variables found in pattern: {pattern}")
            return None

        # Try to rebuild the mathematical pattern
        return self._rebuild_mathematical_pattern(pattern, existing_vars)

    def _handle_simple_composite_patterns(self, pattern: str) -> Any | None:
        """
        Handle simple composite patterns like 'var * const' or 'var1 / var2'.

        Args:
            pattern: The pattern string to handle

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        pattern = pattern.strip()

        # Handle patterns like "d_2 * 2.0"
        if ' * ' in pattern:
            parts = pattern.split(' * ', 1)
            if len(parts) == 2:
                left_part, right_part = parts
                left_part = left_part.strip()
                right_part = right_part.strip()

                # Check if left is variable and right is number
                if left_part in self.variables:
                    try:
                        right_value = float(right_part)
                        left_var_ref = VariableReference(self.variables[left_part])
                        return left_var_ref * right_value
                    except ValueError:
                        # Right part is not a number, check if it's a variable
                        if right_part in self.variables:
                            left_var_ref = VariableReference(self.variables[left_part])
                            right_var_ref = VariableReference(self.variables[right_part])
                            return left_var_ref * right_var_ref

        # Handle patterns like "S_r / header_S"
        elif ' / ' in pattern:
            parts = pattern.split(' / ', 1)
            if len(parts) == 2:
                left_part, right_part = parts
                left_part = left_part.strip()
                right_part = right_part.strip()

                # Check if both are variables
                if left_part in self.variables and right_part in self.variables:
                    left_var_ref = VariableReference(self.variables[left_part])
                    right_var_ref = VariableReference(self.variables[right_part])
                    return left_var_ref / right_var_ref

                # Check if left is variable and right is number
                elif left_part in self.variables:
                    try:
                        right_value = float(right_part)
                        left_var_ref = VariableReference(self.variables[left_part])
                        return left_var_ref / right_value
                    except ValueError:
                        pass

        # Handle patterns like "var + const", "var - const"
        elif ' + ' in pattern or ' - ' in pattern:
            # Find the operator
            if ' + ' in pattern:
                operator = '+'
                parts = pattern.split(' + ', 1)
            else:
                operator = '-'
                parts = pattern.split(' - ', 1)

            if len(parts) == 2:
                left_part, right_part = parts
                left_part = left_part.strip()
                right_part = right_part.strip()

                if left_part in self.variables:
                    left_var_ref = VariableReference(self.variables[left_part])

                    # Try as number first
                    try:
                        right_value = float(right_part)
                        if operator == '+':
                            return left_var_ref + right_value
                        else:
                            return left_var_ref - right_value
                    except ValueError:
                        # Try as variable
                        if right_part in self.variables:
                            right_var_ref = VariableReference(self.variables[right_part])
                            if operator == '+':
                                return left_var_ref + right_var_ref
                            else:
                                return left_var_ref - right_var_ref

        return None

    def _remove_outer_parentheses(self, pattern: str) -> str:
        """
        Remove outer parentheses if they wrap the entire expression.

        Args:
            pattern: The pattern string to process

        Returns:
            Pattern with outer parentheses removed if appropriate
        """
        if not pattern.startswith('(') or not pattern.endswith(')'):
            return pattern

        # Count parentheses to make sure we're removing the outermost pair
        paren_count = 0
        for char in pattern[1:-1]:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count < 0:
                    return pattern  # Don't remove - they don't wrap everything

        # We made it through without breaking, so the outer parens wrap everything
        return pattern[1:-1]

    def parse_malformed_variable_pattern(self, malformed_symbol: str) -> Any | None:
        """
        Parse a malformed variable symbol and reconstruct it using available variables.

        Args:
            malformed_symbol: The malformed variable symbol to parse

        Returns:
            Reconstructed expression if successful, None otherwise

        Examples:
            - "(var1 - (var2 - var3) * 2.0) = 1.315 in" -> var1 - 2.0 * (var2 - var3)
            - "(var1 + var2) = 0.397 in" -> var1 + var2
        """
        if not malformed_symbol or ' = ' not in malformed_symbol:
            return None

        pattern = malformed_symbol.split(' = ')[0].strip()

        # Remove outer parentheses if present
        pattern = self._remove_outer_parentheses(pattern)

        # Extract variable names that exist in our system using compiled regex
        potential_vars = VARIABLE_PATTERN_DETAILED.findall(pattern)
        existing_vars = [var for var in potential_vars if var in self.variables]

        if len(existing_vars) < 2:
            self.logger.debug(f"Insufficient variables in malformed pattern: {pattern}")
            return None

        # Try to rebuild common mathematical patterns
        return self._rebuild_mathematical_pattern(pattern, existing_vars)

    def _rebuild_mathematical_pattern(self, pattern: str, existing_vars: list[str]) -> Any | None:
        """
        Rebuild mathematical expressions from string patterns using existing variables.

        Args:
            pattern: The mathematical pattern string to rebuild
            existing_vars: List of existing variable names to use

        Returns:
            Reconstructed expression if successful, None otherwise

        Note:
            Uses eval() in a controlled namespace with only VariableReference objects
            to ensure we get Expression objects instead of evaluated Variables.
        """
        if not pattern or not existing_vars:
            return None

        try:
            # Build secure namespace with VariableReference objects
            namespace: dict[str, Any] = {'__builtins__': {}}

            # Add VariableReference objects to namespace for secure evaluation
            for var_name in existing_vars:
                if var_name in self.variables:
                    # Create VariableReference to get Expression objects instead of raw values
                    var_ref = VariableReference(self.variables[var_name])
                    namespace[var_name] = var_ref
                else:
                    self.logger.debug(f"Variable '{var_name}' not found in available variables")

            # Evaluate the pattern to create the expression
            self.logger.debug(f"Rebuilding pattern: '{pattern}' with vars: {existing_vars}")
            result = eval(pattern, namespace)
            self.logger.debug(f"Rebuild result: {result} (type: {type(result)})")

            return result

        except Exception as e:
            self.logger.debug(f"Failed to rebuild pattern '{pattern}': {e}")
            return None

    def parse_and_rebuild_expression(self, expr: Any, missing_vars: list[str]) -> Any | None:
        """
        Parse composite expressions and rebuild them using existing variables.

        Args:
            expr: The expression to parse and rebuild
            missing_vars: List of missing variable names

        Returns:
            Rebuilt expression if successful, None otherwise
        """
        if expr is None:
            return None

        if isinstance(expr, VariableReference):
            if expr.name in missing_vars:
                # This is a composite expression - try to parse and rebuild it
                return self.parse_composite_expression_pattern(expr.name)
            return expr

        elif isinstance(expr, BinaryOperation):
            # Recursively rebuild operands
            left_rebuilt = self.parse_and_rebuild_expression(expr.left, missing_vars)
            right_rebuilt = self.parse_and_rebuild_expression(expr.right, missing_vars)

            if left_rebuilt and right_rebuilt:
                return BinaryOperation(expr.operator, left_rebuilt, right_rebuilt)

        elif isinstance(expr, UnaryFunction):
            # Recursively rebuild operand
            operand_rebuilt = self.parse_and_rebuild_expression(expr.operand, missing_vars)

            if operand_rebuilt:
                return UnaryFunction(expr.function_name, operand_rebuilt)

        # Note: There's no BinaryFunction class - binary functions are handled by
        # specific function calls like min_expr, max_expr or BinaryOperation

        elif isinstance(expr, Constant):
            return expr

        return None
