from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ...equations import Equation
from ...quantities import FieldQnty
from ..order import Order


class SolveError(Exception):
    """Exception raised when solving fails."""


@dataclass
class SolveResult:
    """Result of a solve operation."""

    variables: dict[str, FieldQnty]
    steps: list[dict[str, Any]] = field(default_factory=list)
    success: bool = True
    message: str = ""
    method: str = ""
    iterations: int = 0


class BaseSolver(ABC):
    """Base class for all equation solvers."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger
        self.steps: list[dict[str, Any]] = []

    @abstractmethod
    def can_handle(self, equations: list[Equation], unknowns: set[str], dependency_graph: Order | None = None, analysis: dict[str, Any] | None = None) -> bool:
        """
        Check if this solver can handle the given problem.

        Args:
            equations: List of equations to solve
            unknowns: Set of unknown variable symbols
            dependency_graph: Optional dependency graph for analysis
            analysis: Optional system analysis results

        Returns:
            True if this solver can handle the problem
        """
        ...

    @abstractmethod
    def solve(self, equations: list[Equation], variables: dict[str, FieldQnty], dependency_graph: Order | None = None, max_iterations: int = 100, tolerance: float = 1e-10) -> SolveResult:
        """
        Solve the system of equations.

        Args:
            equations: List of equations to solve
            variables: Dictionary of all variables (known and unknown)
            dependency_graph: Optional dependency graph
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance

        Returns:
            SolveResult containing the solution
        """
        ...

    def _log_step(self, iteration: int, variable: str, equation: str, result: str, method: str | None = None):
        """Log a solving step."""
        step = {"iteration": iteration, "variable": variable, "equation": equation, "result": result, "method": method or self.__class__.__name__}
        self.steps.append(step)
        if self.logger:
            self.logger.debug("Solved %s = %s", variable, result)

    def _get_known_variables(self, variables: dict[str, FieldQnty]) -> set[str]:
        """Get symbols of known variables."""
        return {s for s, v in variables.items() if v.is_known}

    def _get_unknown_variables(self, variables: dict[str, FieldQnty]) -> set[str]:
        """Get symbols of unknown variables."""
        return {s for s, v in variables.items() if not v.is_known}
