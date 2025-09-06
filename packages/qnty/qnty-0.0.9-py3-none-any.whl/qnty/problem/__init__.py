"""
Reassembled Problem class from focused modules.

This module combines all the decomposed functionality back into a single
Problem class that maintains the same public API.
"""

from .base import ProblemBase
from .variables import VariablesMixin
from .equations import EquationsMixin  
from .solving import SolvingMixin
from .validation import ValidationMixin
from .composition_mixin import CompositionMixin
from .metaclass import ProblemMeta

# Re-export exceptions for compatibility
from .variables import VariableNotFoundError
from .equations import EquationValidationError  
from .solving import SolverError


class Problem(
    ProblemBase,
    VariablesMixin, 
    EquationsMixin,
    SolvingMixin,
    ValidationMixin,
    CompositionMixin,
    metaclass=ProblemMeta
):
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
        # Initialize the base class
        super().__init__(name, description)
        
        # Auto-populate from class-level variables and equations (subclass pattern)
        self._extract_from_class_variables()


# Alias for backward compatibility
EngineeringProblem = Problem

# Export all relevant classes and exceptions
__all__ = [
    'Problem',
    'EngineeringProblem', 
    'VariableNotFoundError',
    'EquationValidationError',
    'SolverError'
]