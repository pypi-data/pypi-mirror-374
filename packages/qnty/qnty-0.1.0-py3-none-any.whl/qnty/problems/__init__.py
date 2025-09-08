"""
Consolidated Problem system for engineering calculations.

This module provides a streamlined Problem system with 4 focused files instead of 15+:
- problem.py: Main Problem class with variable and equation management
- composition.py: Sub-problem composition with metaclass system
- solving.py: Problem solving with equation reconstruction
- validation.py: Problem validation integration

The system maintains full backward compatibility with the original Problem API.
"""

from .composition import (
    CompositionMixin,
    ConfigurableVariable,
    DelayedEquation,
    DelayedExpression,
    DelayedFunction,
    DelayedVariableReference,
    MetaclassError,
    NamespaceError,
    ProblemMeta,
    ProxiedNamespace,
    SubProblemProxy,
    SubProblemProxyError,
    delayed_max_expr,
    delayed_min_expr,
    delayed_sin,
)
from .problem import EquationValidationError, SolverError, ValidationMixin, VariableNotFoundError
from .problem import Problem as BaseProblem
from .solving import (
    CompositeExpressionRebuilder,
    DelayedExpressionResolver,
    EquationReconstructionError,
    EquationReconstructor,
    ExpressionParser,
    MalformedExpressionError,
    NamespaceMapper,
    NamespaceMappingError,
    PatternReconstructionError,
)

# ValidationMixin is already imported from .problem above

# ========== INTEGRATED PROBLEM CLASS ==========


class Problem(BaseProblem, CompositionMixin, metaclass=ProblemMeta):
    """
    Main container class for engineering problems with composition support.

    This class integrates all aspects of engineering problem definition, solving, and analysis.
    It supports both programmatic problem construction and class-level inheritance patterns
    for defining domain-specific engineering problems with sub-problem composition.

    Key Features:
    - Automatic dependency graph construction and topological solving order
    - Dual solving approach: SymPy symbolic solving with numerical fallback
    - Sub-problem composition with automatic variable namespacing
    - Comprehensive validation and error handling
    - Professional report generation capabilities

    Usage Patterns:
    1. Inheritance Pattern (Recommended for domain problems):
       class MyProblem(Problem):
           x = Variable("x", Qty(5.0, length))
           y = Variable("y", Qty(0.0, length), is_known=False)
           eq = y.equals(x * 2)

    2. Programmatic Pattern (For dynamic problems):
       problem = Problem("Dynamic Problem")
       problem.add_variables(x, y)
       problem.add_equation(y.equals(x * 2))

    3. Composition Pattern (For reusable sub-problems):
       class ComposedProblem(Problem):
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
        sub_problems (dict[str, Problem]): Integrated sub-problems
    """

    def __init__(self, name: str | None = None, description: str = ""):
        # Initialize the base Problem class
        super().__init__(name, description)

        # Auto-populate from class-level variables and equations (subclass pattern)
        # This is handled by the CompositionMixin via _extract_from_class_variables()
        self._extract_from_class_variables()


# ========== BACKWARD COMPATIBILITY ALIASES ==========

# Alias for backward compatibility
EngineeringProblem = Problem

# Export all relevant classes and exceptions for compatibility
__all__ = [
    # Main classes
    "Problem",
    "EngineeringProblem",
    # Mixins
    "ValidationMixin",
    "CompositionMixin",
    # Metaclass system
    "ProblemMeta",
    "ProxiedNamespace",
    # Composition classes
    "SubProblemProxy",
    "ConfigurableVariable",
    "DelayedEquation",
    "DelayedVariableReference",
    "DelayedExpression",
    "DelayedFunction",
    # Delayed function factories
    "delayed_sin",
    "delayed_min_expr",
    "delayed_max_expr",
    # Reconstruction system
    "EquationReconstructor",
    "ExpressionParser",
    "NamespaceMapper",
    "CompositeExpressionRebuilder",
    "DelayedExpressionResolver",
    # Exceptions
    "VariableNotFoundError",
    "EquationValidationError",
    "SolverError",
    "MetaclassError",
    "SubProblemProxyError",
    "NamespaceError",
    "EquationReconstructionError",
    "MalformedExpressionError",
    "NamespaceMappingError",
    "PatternReconstructionError",
]
