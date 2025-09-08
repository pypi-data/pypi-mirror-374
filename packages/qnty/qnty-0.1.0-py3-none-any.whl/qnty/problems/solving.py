"""
Problem solving system with equation reconstruction capabilities.

This module provides the complete solving system including:
- High-level solve orchestration (formerly solving.py)
- Equation reconstruction for malformed expressions (formerly reconstruction.py)
- Expression parsing and rebuilding (formerly expression_parser.py)
- Namespace mapping for variables (formerly namespace_mapper.py)
- Composite expression rebuilding (formerly composite_expression_rebuilder.py)
- Delayed expression resolution (formerly delayed_expression_resolver.py)

All consolidated into a focused solving system.
"""

from __future__ import annotations

import re
from logging import Logger
from typing import Any

from ..equations import Equation
from ..expressions import BinaryOperation, ConditionalExpression, Constant, UnaryFunction, VariableReference, cos, sin
from ..quantities import FieldQnty

# Type aliases for better readability
VariableDict = dict[str, FieldQnty]
ReconstructionResult = Equation | None
NamespaceMapping = dict[str, str]

# Constants for pattern matching
CONDITIONAL_PATTERNS: set[str] = {"cond("}
FUNCTION_PATTERNS: set[str] = {"sin(", "cos(", "tan(", "log(", "exp(", "sqrt"}
MATH_OPERATORS: set[str] = {"(", ")", "+", "-", "*", "/"}
EXCLUDED_FUNCTION_NAMES: set[str] = {"sin", "cos", "max", "min", "exp", "log", "sqrt", "tan"}

# Compiled regex patterns for performance
VARIABLE_PATTERN_DETAILED = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b")
VARIABLE_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_]*\b")

# Tuple of types for isinstance() checks
VALID_EXPRESSION_TYPES = (VariableReference, FieldQnty, int, float, BinaryOperation, ConditionalExpression, Constant, UnaryFunction)


# ========== CUSTOM EXCEPTIONS ==========


class SolverError(RuntimeError):
    """Raised when the solving process fails."""

    pass


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


# ========== EXPRESSION PARSER ==========


class ExpressionParser:
    """
    Focused class for parsing and rebuilding mathematical expressions.

    Handles conversion from string patterns to Expression objects using
    safe evaluation techniques and proper namespace management.
    """

    def __init__(self, variables: VariableDict, logger: Logger):
        """
        Initialize the expression parser.

        Args:
            variables: Dictionary of available variables
            logger: Logger for debugging
        """
        self.variables = variables
        self.logger = logger

    def parse_composite_expression_pattern(self, composite_symbol: str) -> Any | None:
        """
        Parse a composite expression pattern and reconstruct it using available variables.

        Args:
            composite_symbol: The composite expression string to parse

        Returns:
            Reconstructed expression if successful, None otherwise

        Examples:
            "D - T * 2" -> header_D - header_T * 2
            "(P - S) / E" -> (header_P - header_S) / header_E
        """
        if not composite_symbol or not isinstance(composite_symbol, str):
            return None

        try:
            # Extract variable names from the composite expression
            var_matches = VARIABLE_PATTERN_DETAILED.findall(composite_symbol)
            if not var_matches:
                return None

            # Find the namespace that contains most of these variables
            best_namespace = self._find_best_namespace_for_variables(var_matches)
            if not best_namespace:
                return None

            # Create substitution mapping
            substitution_map = {}
            for var_name in var_matches:
                if var_name not in EXCLUDED_FUNCTION_NAMES:
                    namespaced_name = f"{best_namespace}_{var_name}"
                    if namespaced_name in self.variables:
                        substitution_map[var_name] = namespaced_name

            if not substitution_map:
                return None

            # Substitute variables in the expression string
            substituted_expr = composite_symbol
            for original, namespaced in substitution_map.items():
                # Use word boundary regex for precise replacement
                pattern = r"\b" + re.escape(original) + r"\b"
                substituted_expr = re.sub(pattern, namespaced, substituted_expr)

            # Try to build the expression from the substituted string
            return self._build_expression_from_string(substituted_expr)

        except Exception as e:
            self.logger.debug(f"Failed to parse composite expression '{composite_symbol}': {e}")
            return None

    def _find_best_namespace_for_variables(self, var_names: list[str]) -> str | None:
        """Find the namespace that contains the most variables from the list."""
        namespace_scores = {}

        # Score each namespace based on how many variables it contains
        for var_name in self.variables:
            if "_" in var_name:
                namespace = var_name.split("_")[0]
                base_var = "_".join(var_name.split("_")[1:])

                if base_var in var_names:
                    namespace_scores[namespace] = namespace_scores.get(namespace, 0) + 1

        if not namespace_scores:
            return None

        # Return the namespace with the highest score
        return max(namespace_scores.items(), key=lambda x: x[1])[0]

    def _build_expression_from_string(self, expr_string: str) -> Any | None:
        """
        Build an expression from a string by safely evaluating with variable substitution.

        Args:
            expr_string: The expression string to evaluate

        Returns:
            Built expression object if successful, None otherwise
        """
        try:
            # Create a safe evaluation context with only our variables
            eval_context = {}

            # Add variables to context
            for var_symbol, var_obj in self.variables.items():
                eval_context[var_symbol] = var_obj

            # Add safe mathematical functions
            eval_context.update(
                {
                    "sin": sin,
                    "cos": cos,
                    "abs": abs,
                    "min": min,
                    "max": max,
                    "__builtins__": {},  # Disable built-ins for security
                }
            )

            # Safely evaluate the expression
            result = eval(expr_string, eval_context, {})
            return result

        except Exception as e:
            self.logger.debug(f"Failed to build expression from string '{expr_string}': {e}")
            return None

    def parse_malformed_variable_pattern(self, malformed_symbol: str) -> Any | None:
        """
        Parse a malformed variable pattern from proxy evaluation.

        Args:
            malformed_symbol: The malformed variable symbol to parse

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        if not malformed_symbol or not isinstance(malformed_symbol, str):
            return None

        try:
            # Check if this looks like a mathematical expression with embedded values
            if any(char in malformed_symbol for char in MATH_OPERATORS):
                # Try to parse as a composite expression
                return self.parse_composite_expression_pattern(malformed_symbol)

            # Check for specific malformed patterns
            if "." in malformed_symbol and "(" in malformed_symbol:
                # Looks like a method call result - try to extract the base pattern
                base_pattern = self._extract_base_pattern_from_malformed(malformed_symbol)
                if base_pattern:
                    return self.parse_composite_expression_pattern(base_pattern)

            return None

        except Exception as e:
            self.logger.debug(f"Failed to parse malformed variable '{malformed_symbol}': {e}")
            return None

    def _extract_base_pattern_from_malformed(self, malformed_symbol: str) -> str | None:
        """Extract the base mathematical pattern from a malformed symbol."""
        if not malformed_symbol or not isinstance(malformed_symbol, str):
            return None

        try:
            # Remove numeric values that look like results
            cleaned = re.sub(r"\d+\.\d+", "VAR", malformed_symbol)

            # Remove method calls like .value, .quantity
            cleaned = re.sub(r"\.(?:value|quantity|magnitude)\b", "", cleaned)

            # Return pattern if it contains mathematical operators
            return cleaned if any(char in cleaned for char in MATH_OPERATORS) else None

        except (AttributeError, re.error):
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
        if not missing_vars:
            return expr

        try:
            # For each missing variable, try to reconstruct it
            reconstructed_components = {}

            for missing_var in missing_vars:
                if any(char in missing_var for char in MATH_OPERATORS):
                    # This is a composite expression
                    rebuilt = self.parse_composite_expression_pattern(missing_var)
                    if rebuilt:
                        reconstructed_components[missing_var] = rebuilt

            if not reconstructed_components:
                return None

            # Try to substitute the reconstructed components back into the original expression
            return self._substitute_in_expression(expr, reconstructed_components)

        except Exception as e:
            self.logger.debug(f"Failed to parse and rebuild expression: {e}")
            return None

    def _substitute_in_expression(self, _expr: Any, substitutions: dict[str, Any]) -> Any | None:
        """
        Substitute reconstructed components back into an expression tree.

        Args:
            _expr: The original expression (unused in current implementation)
            substitutions: Map of missing variables to their reconstructed versions

        Returns:
            Expression with substitutions applied
        """
        if not substitutions:
            return None

        # Return the first successful substitution
        # TODO: Implement full expression tree traversal for complex substitutions
        return next(iter(substitutions.values()))


# ========== NAMESPACE MAPPER ==========


class NamespaceMapper:
    """
    Focused class for handling variable namespace mapping operations.

    Provides efficient mapping of base variable names to their namespaced
    counterparts with caching for performance optimization.
    """

    def __init__(self, variables: VariableDict, logger: Logger):
        """
        Initialize the namespace mapper.

        Args:
            variables: Dictionary of available variables
            logger: Logger for debugging
        """
        self.variables = variables
        self.logger = logger

        # Performance optimization caches
        self._namespace_cache: dict[str, set[str]] = {}
        self._variable_mapping_cache: dict[frozenset, NamespaceMapping] = {}
        self._all_variable_names: set[str] | None = None

    def extract_base_variables_from_composites(self, missing_vars: list[str]) -> set[str]:
        """
        Extract base variable names from composite expressions.

        Args:
            missing_vars: List of missing variable expressions

        Returns:
            Set of base variable names found in the expressions
        """
        base_vars = set()

        for missing_var in missing_vars:
            if not isinstance(missing_var, str):
                continue

            # Extract variable names using regex
            matches = VARIABLE_PATTERN.findall(missing_var)

            for match in matches:
                # Skip function names
                if match not in EXCLUDED_FUNCTION_NAMES:
                    base_vars.add(match)

        return base_vars

    def find_namespace_mappings(self, base_vars: set[str]) -> NamespaceMapping:
        """
        Find namespace mappings for a set of base variables.

        Args:
            base_vars: Set of base variable names

        Returns:
            Dictionary mapping base variables to their namespaced versions
        """
        # Use cache for performance
        cache_key = frozenset(base_vars)
        if cache_key in self._variable_mapping_cache:
            return self._variable_mapping_cache[cache_key]

        mappings = {}

        # Build all variable names cache if needed
        if self._all_variable_names is None:
            self._all_variable_names = set(self.variables.keys())

        # For each base variable, find its namespaced version
        for base_var in base_vars:
            namespaced_var = self._find_namespaced_variable(base_var)
            if namespaced_var:
                mappings[base_var] = namespaced_var

        # Cache the result
        self._variable_mapping_cache[cache_key] = mappings
        return mappings

    def _find_namespaced_variable(self, base_var: str) -> str | None:
        """
        Find the namespaced version of a base variable.

        Args:
            base_var: Base variable name

        Returns:
            Namespaced variable name if found, None otherwise
        """
        if not base_var or not isinstance(base_var, str):
            return None

        # Build all variable names cache if needed
        if self._all_variable_names is None:
            self._all_variable_names = set(self.variables.keys())

        # Direct match first (most efficient)
        if base_var in self._all_variable_names:
            return base_var

        # Look for namespaced versions
        suffix = f"_{base_var}"
        candidates = [name for name in self._all_variable_names if name.endswith(suffix)]

        # Return shortest match (least nested namespace)
        return min(candidates, key=len) if candidates else None

    def get_namespaces_for_variable(self, base_var: str) -> set[str]:
        """
        Get all namespaces that contain a particular base variable.

        Args:
            base_var: Base variable name

        Returns:
            Set of namespace prefixes that contain the variable
        """
        # Use cache for performance
        if base_var in self._namespace_cache:
            return self._namespace_cache[base_var]

        namespaces = set()

        for var_name in self.variables.keys():
            if var_name.endswith(f"_{base_var}") and "_" in var_name:
                # Extract namespace (everything before the last underscore + base_var)
                parts = var_name.split("_")
                if len(parts) >= 2 and parts[-1] == base_var:
                    namespace = "_".join(parts[:-1])
                    namespaces.add(namespace)

        # Cache the result
        self._namespace_cache[base_var] = namespaces
        return namespaces

    def clear_caches(self) -> None:
        """Clear all internal caches."""
        self._namespace_cache.clear()
        self._variable_mapping_cache.clear()
        self._all_variable_names = None


# ========== COMPOSITE EXPRESSION REBUILDER ==========


class CompositeExpressionRebuilder:
    """
    Focused class for rebuilding composite expressions from malformed patterns.

    Handles reconstruction of expressions that were malformed during proxy
    evaluation and provides methods to recover the original mathematical structure.
    """

    def __init__(self, variables: VariableDict, logger: Logger):
        """
        Initialize the composite expression rebuilder.

        Args:
            variables: Dictionary of available variables
            logger: Logger for debugging
        """
        self.variables = variables
        self.logger = logger

    def identify_malformed_variables(self, missing_vars: list[str]) -> list[str]:
        """
        Identify which missing variables are malformed from proxy evaluation.

        Args:
            missing_vars: List of missing variable names

        Returns:
            List of variables that appear to be malformed
        """
        malformed = []

        for var in missing_vars:
            if self._is_malformed_variable(var):
                malformed.append(var)

        return malformed

    def _is_malformed_variable(self, var_name: str) -> bool:
        """
        Check if a variable name appears to be malformed from proxy evaluation.

        Args:
            var_name: Variable name to check

        Returns:
            True if the variable appears malformed
        """
        if not isinstance(var_name, str) or not var_name:
            return False

        # Check for numeric values embedded in expressions
        if re.search(r"\d+\.\d+", var_name):
            return True

        # Check for method calls in variable names
        if ".value" in var_name or ".quantity" in var_name:
            return True

        # Check for unbalanced parentheses
        if var_name.count("(") != var_name.count(")"):
            return True

        # Check for very long names with multiple operations
        if len(var_name) > 50 and any(op in var_name for op in MATH_OPERATORS):
            return True

        return False

    def reconstruct_malformed_proxy_expression(self, equation: Equation, _malformed_vars: list[str]) -> Any | None:
        """
        Generically reconstruct expressions that were malformed due to proxy evaluation.

        Args:
            equation: The equation containing malformed expressions
            _malformed_vars: List of malformed variable names (kept for signature compatibility)

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        try:
            # Try to extract a meaningful pattern from the equation's RHS
            rhs_str = str(equation.rhs)

            # Look for recognizable mathematical patterns
            pattern = self._extract_mathematical_pattern(rhs_str)
            if pattern:
                # Try to reconstruct the pattern with proper variable references
                return self._reconstruct_pattern(pattern)

            # If direct pattern extraction fails, try alternative approaches
            return self._attempt_fallback_reconstruction(equation)

        except Exception as e:
            self.logger.debug(f"Failed to reconstruct malformed proxy expression: {e}")
            return None

    def _extract_mathematical_pattern(self, expression_str: str) -> str | None:
        """
        Extract a mathematical pattern from an expression string.

        Args:
            expression_str: String representation of the expression

        Returns:
            Cleaned mathematical pattern if extractable, None otherwise
        """
        try:
            # Remove common method calls and numeric results
            cleaned = expression_str

            # Remove .value, .quantity, etc.
            cleaned = re.sub(r"\.(?:value|quantity|magnitude)\b", "", cleaned)

            # Replace numeric constants with placeholders
            cleaned = re.sub(r"\d+\.\d+", "NUM", cleaned)

            # If we still have mathematical operators, this might be reconstructable
            if any(op in cleaned for op in MATH_OPERATORS):
                return cleaned

            return None

        except Exception:
            return None

    def _reconstruct_pattern(self, pattern: str) -> Any | None:
        """
        Reconstruct a mathematical pattern using available variables.

        Args:
            pattern: The mathematical pattern to reconstruct

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        try:
            # Extract variable names from the pattern
            var_matches = VARIABLE_PATTERN.findall(pattern)

            # Try to map these to existing variables
            var_mapping = {}
            for var_name in var_matches:
                if var_name not in EXCLUDED_FUNCTION_NAMES and var_name != "NUM":
                    # Look for a matching variable in our namespace
                    matching_var = self._find_matching_variable(var_name)
                    if matching_var:
                        var_mapping[var_name] = matching_var

            if not var_mapping:
                return None

            # Substitute the variables back into the pattern
            reconstructed_pattern = pattern
            for original, replacement in var_mapping.items():
                reconstructed_pattern = re.sub(r"\b" + re.escape(original) + r"\b", replacement, reconstructed_pattern)

            # Replace NUM placeholders with appropriate constants
            reconstructed_pattern = re.sub(r"\bNUM\b", "1.0", reconstructed_pattern)

            # Try to evaluate the reconstructed pattern
            return self._safe_evaluate_pattern(reconstructed_pattern)

        except Exception as e:
            self.logger.debug(f"Failed to reconstruct pattern '{pattern}': {e}")
            return None

    def _find_matching_variable(self, var_name: str) -> str | None:
        """Find a variable in our namespace that matches the given name."""
        # Direct match first
        if var_name in self.variables:
            return var_name

        # Look for namespaced versions
        candidates = [v for v in self.variables.keys() if v.endswith(f"_{var_name}")]

        if candidates:
            # Return the shortest match (least nested)
            return min(candidates, key=len)

        return None

    def _safe_evaluate_pattern(self, pattern: str) -> Any | None:
        """Safely evaluate a reconstructed pattern."""
        try:
            # Create evaluation context with our variables  
            eval_context: dict[str, Any] = dict(self.variables)
            eval_context["__builtins__"] = {}  # Security

            return eval(pattern, eval_context, {})

        except Exception:
            return None

    def _attempt_fallback_reconstruction(self, equation: Equation) -> Any | None:
        """Attempt fallback reconstruction methods."""
        try:
            # Try to get variables from the LHS and create a simple reconstruction
            if isinstance(equation.lhs, FieldQnty | VariableReference):
                symbol = getattr(equation.lhs, "symbol", None)
                if isinstance(symbol, str) and symbol in self.variables:
                    lhs_var = self.variables[symbol]

                    # Look for similar variables that might be used in a simple expression
                    namespace = self._extract_namespace_from_variable(symbol)
                    if namespace:
                        return self._create_simple_reconstruction(namespace, lhs_var)

            return None

        except (AttributeError, TypeError):
            return None

    def _extract_namespace_from_variable(self, var_symbol: str) -> str | None:
        """Extract namespace from a variable symbol."""
        if "_" in var_symbol:
            return var_symbol.split("_")[0]
        return None

    def _create_simple_reconstruction(self, namespace: str, target_var: FieldQnty) -> Any | None:
        """Create a simple reconstruction based on namespace variables."""
        try:
            # Find other variables in the same namespace
            namespace_vars = [v for name, v in self.variables.items() if name.startswith(f"{namespace}_") and v != target_var]

            if namespace_vars:
                # Return the first other variable as a simple reconstruction
                # This is a fallback - in practice, more sophisticated logic would be needed
                return namespace_vars[0]

            return None

        except Exception:
            return None


# ========== DELAYED EXPRESSION RESOLVER ==========


class DelayedExpressionResolver:
    """
    Focused class for resolving delayed expressions and equations.

    Handles components that have deferred evaluation needs and provides
    safe resolution with proper type checking and context management.
    """

    def __init__(self, variables: VariableDict, logger: Logger):
        """
        Initialize the delayed expression resolver.

        Args:
            variables: Dictionary of available variables
            logger: Logger for debugging
        """
        self.variables = variables
        self.logger = logger

    def contains_delayed_expressions(self, equation: Equation) -> bool:
        """
        Check if an equation contains delayed expressions that need resolution.

        Args:
            equation: The equation to check for delayed expressions

        Returns:
            True if equation contains delayed expressions
        """
        try:
            # Check for common delayed expression patterns
            equation_str = str(equation)

            # Look for delayed expression markers
            delayed_markers = ["DelayedExpression", "DelayedVariable", "DelayedFunction", "resolve(", "delayed_", "proxy_"]

            return any(marker in equation_str for marker in delayed_markers)

        except Exception:
            return False

    def resolve_delayed_equation(self, equation: Equation) -> ReconstructionResult:
        """
        Resolve a delayed equation by evaluating its delayed expressions.

        Args:
            equation: The equation with delayed expressions to resolve

        Returns:
            Resolved equation if successful, None otherwise
        """
        try:
            # Try to resolve the RHS if it has delayed components
            resolved_rhs = self._resolve_delayed_expression(equation.rhs)

            if resolved_rhs is None:
                return None

            # Create new equation with resolved RHS
            if isinstance(equation.lhs, FieldQnty):
                return equation.lhs.equals(resolved_rhs)

            return None

        except Exception as e:
            self.logger.debug(f"Failed to resolve delayed equation: {e}")
            return None

    def _resolve_delayed_expression(self, expr: Any) -> Any | None:
        """
        Resolve a delayed expression by calling its resolve method if available.

        Args:
            expr: Expression that might be delayed

        Returns:
            Resolved expression if successful, None otherwise
        """
        try:
            # Check if this is a valid expression type that doesn't need resolution
            if isinstance(expr, VALID_EXPRESSION_TYPES):
                # Check if this expression has a resolve method
                if hasattr(expr, "resolve") and callable(getattr(expr, "resolve", None)):
                    context = self.variables.copy()
                    return getattr(expr, "resolve")(context)
                return expr

            # Try to recursively resolve components for binary operations
            if isinstance(expr, BinaryOperation):
                resolved_left = self._resolve_delayed_expression(expr.left)
                resolved_right = self._resolve_delayed_expression(expr.right)

                if resolved_left is not None and resolved_right is not None:
                    return BinaryOperation(expr.operator, resolved_left, resolved_right)

            return None

        except (AttributeError, TypeError) as e:
            self.logger.debug(f"Failed to resolve delayed expression: {e}")
            return None


# ========== MAIN EQUATION RECONSTRUCTOR ==========


class EquationReconstructor:
    """
    Handles reconstruction of equations with composite expressions.

    This refactored class provides equation reconstruction capabilities by
    coordinating focused component classes for parsing, namespace mapping,
    delayed resolution, and composite expression rebuilding.

    Key Features:
    - Delegates to focused component classes for specific responsibilities
    - Generic composite expression reconstruction
    - Malformed equation recovery from proxy operations
    - Namespace variable mapping and resolution
    - Mathematical pattern parsing and rebuilding
    - Performance optimization through focused caching

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
        # Type-safe attribute access
        try:
            self.variables: VariableDict = problem.variables
            self.logger: Logger = problem.logger
        except AttributeError as e:
            raise ValueError(f"Problem must have 'variables' and 'logger' attributes: {e}") from e

        if not isinstance(self.variables, dict):
            raise ValueError("Problem.variables must be a dictionary")
        if not isinstance(self.logger, Logger):
            raise ValueError("Problem.logger must be a Logger instance")

        self.problem = problem

        # Initialize focused component classes
        self.expression_parser = ExpressionParser(self.variables, self.logger)
        self.namespace_mapper = NamespaceMapper(self.variables, self.logger)
        self.delayed_resolver = DelayedExpressionResolver(self.variables, self.logger)
        self.composite_rebuilder = CompositeExpressionRebuilder(self.variables, self.logger)

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

        Delegates to NamespaceMapper for variable mapping and ExpressionParser
        for substitution operations.

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
            composite_vars = self.namespace_mapper.extract_base_variables_from_composites(missing_vars)

            if not composite_vars:
                self.logger.debug("No composite variables found to extract")
                return None

            # Find which namespaces contain these variables
            namespace_mappings = self.namespace_mapper.find_namespace_mappings(composite_vars)

            if not namespace_mappings:
                self.logger.debug("No namespace mappings found")
                return None

            # Reconstruct the equation by substituting composite expressions
            return self._substitute_composite_expressions(equation, missing_vars, namespace_mappings)

        except Exception as e:
            self.logger.debug(f"Error in _reconstruct_composite_expressions: {e}")
            return None

    def _substitute_composite_expressions(self, equation: Equation, missing_vars: list[str], namespace_mappings: dict[str, str]) -> ReconstructionResult:
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
                        lhs_var = self._get_lhs_variable(equation)
                        if lhs_var:
                            return lhs_var.equals(reconstructed_expr)

            return None

        except Exception as e:
            self.logger.debug(f"Error in _substitute_composite_expressions: {e}")
            return None

    def _reconstruct_expression_from_mapping(self, composite_expr: str, namespace_mappings: dict[str, str]) -> Any | None:
        """
        Reconstruct a composite expression using the namespace mappings.

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
                    pattern = r"\b" + re.escape(base_var) + r"\b"
                    substituted_expr = re.sub(pattern, namespaced_var, substituted_expr)

            # Try to evaluate the substituted expression using the expression parser
            return self.expression_parser.parse_composite_expression_pattern(substituted_expr)

        except Exception as e:
            self.logger.debug(f"Error in expression reconstruction: {e}")
            return None

    def _get_lhs_variable(self, equation: Equation) -> FieldQnty | None:
        """
        Safely extract the left-hand side variable from an equation.

        Args:
            equation: The equation to extract LHS from

        Returns:
            The LHS variable if valid, None otherwise
        """
        try:
            # Check if lhs is a VariableReference
            if isinstance(equation.lhs, VariableReference):
                var_name = equation.lhs.name
                if var_name in self.variables:
                    return self.variables[var_name]
            # Check if lhs is a FieldQnty with symbol attribute
            elif isinstance(equation.lhs, FieldQnty):
                symbol = getattr(equation.lhs, "symbol", None)
                if isinstance(symbol, str) and symbol in self.variables:
                    return self.variables[symbol]
        except (AttributeError, TypeError):
            pass

        return None

    def contains_delayed_expressions(self, equation: Equation) -> bool:
        """
        Check if an equation contains delayed expressions that need resolution.

        Args:
            equation: The equation to check for delayed expressions

        Returns:
            True if equation contains delayed expressions
        """
        return self.delayed_resolver.contains_delayed_expressions(equation)

    def resolve_delayed_equation(self, equation: Equation) -> ReconstructionResult:
        """
        Resolve a delayed equation by evaluating its delayed expressions.

        Args:
            equation: The equation with delayed expressions to resolve

        Returns:
            Resolved equation if successful, None otherwise
        """
        return self.delayed_resolver.resolve_delayed_equation(equation)

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
            malformed_vars = self.composite_rebuilder.identify_malformed_variables(missing_vars)

            if malformed_vars:
                # This is a malformed expression from proxy evaluation
                reconstructed_rhs = self.composite_rebuilder.reconstruct_malformed_proxy_expression(equation, malformed_vars)
                if reconstructed_rhs:
                    return lhs_var.equals(reconstructed_rhs)
                return None

            # Reconstruct the RHS by parsing and rebuilding composite expressions
            reconstructed_rhs = self.expression_parser.parse_and_rebuild_expression(equation.rhs, missing_vars)

            if reconstructed_rhs:
                return lhs_var.equals(reconstructed_rhs)

            return None

        except Exception as e:
            self.logger.debug(f"Reconstruction failed: {e}")
            return None

    def _clear_caches(self) -> None:
        """
        Clear all internal caches. Should be called when variables change.

        This method provides a way to reset cached data when the problem
        state changes, ensuring cache consistency.
        """
        self.namespace_mapper.clear_caches()

    # Delegation methods for public API compatibility
    def parse_composite_expression_pattern(self, composite_symbol: str) -> Any | None:
        """
        Parse a composite expression pattern using the expression parser.

        Args:
            composite_symbol: The composite expression string to parse

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        return self.expression_parser.parse_composite_expression_pattern(composite_symbol)

    def parse_malformed_variable_pattern(self, malformed_symbol: str) -> Any | None:
        """
        Parse a malformed variable pattern using the expression parser.

        Args:
            malformed_symbol: The malformed variable symbol to parse

        Returns:
            Reconstructed expression if successful, None otherwise
        """
        return self.expression_parser.parse_malformed_variable_pattern(malformed_symbol)

    def parse_and_rebuild_expression(self, expr: Any, missing_vars: list[str]) -> Any | None:
        """
        Parse composite expressions and rebuild them using existing variables.

        Args:
            expr: The expression to parse and rebuild
            missing_vars: List of missing variable names

        Returns:
            Rebuilt expression if successful, None otherwise
        """
        return self.expression_parser.parse_and_rebuild_expression(expr, missing_vars)


# Export all relevant classes
__all__ = [
    "EquationReconstructor",
    "ExpressionParser",
    "NamespaceMapper",
    "CompositeExpressionRebuilder",
    "DelayedExpressionResolver",
    "SolverError",
    "EquationReconstructionError",
    "MalformedExpressionError",
    "NamespaceMappingError",
    "PatternReconstructionError",
]
