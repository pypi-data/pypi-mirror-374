"""
Problem-validation integration for Problem class.

This module provides validation functionality through a mixin pattern,
allowing Problems to run validation checks and collect warnings.

Key features:
- Type-safe validation check management
- Robust error handling for validation failures
- Integration with Problem metaclass system
- Proper closure handling to avoid late binding issues
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, Protocol


class ValidationResult(Protocol):
    """Protocol for validation check results."""

    def evaluate(self, variables: dict[str, Any]) -> dict[str, Any] | None:
        """Evaluate the validation check."""
        ...


class ProblemAttributes(Protocol):
    """Protocol defining expected attributes for validation mixin."""

    logger: logging.Logger
    warnings: list[dict[str, Any]]
    validation_checks: list[Callable[[Any], dict[str, Any] | None]]
    variables: dict[str, Any]


class ValidationMixin:
    """Mixin class providing validation functionality."""

    # These attributes will be provided by other mixins in the final Problem class
    logger: logging.Logger
    warnings: list[dict[str, Any]]
    validation_checks: list[Callable[[Any], dict[str, Any] | None]]
    variables: dict[str, Any]

    def add_validation_check(self, check_function: Callable[[Any], dict[str, Any] | None]) -> None:
        """Add a validation check function."""
        if not callable(check_function):
            raise TypeError("check_function must be callable")
        self.validation_checks.append(check_function)

    def validate(self) -> list[dict[str, Any]]:
        """Run all validation checks and return any warnings."""
        validation_warnings: list[dict[str, Any]] = []

        for check in self.validation_checks:
            if not callable(check):
                self.logger.warning(f"Skipping non-callable validation check: {check}")
                continue

            try:
                result = check(self)
                if result is not None and isinstance(result, dict):
                    validation_warnings.append(result)
                elif result is not None:
                    self.logger.warning(f"Validation check returned non-dict result: {type(result)}")
            except Exception as e:
                self.logger.debug(f"Validation check failed: {e}")

        return validation_warnings

    def get_warnings(self) -> list[dict[str, Any]]:
        """Get all warnings from the problem."""
        try:
            warnings = self.warnings.copy() if hasattr(self, "warnings") and self.warnings else []
        except (AttributeError, TypeError):
            warnings = []
            self.logger.warning("Problem warnings attribute is not properly initialized")

        try:
            validation_warnings = self.validate()
            warnings.extend(validation_warnings)
        except Exception as e:
            self.logger.error(f"Failed to run validation: {e}")

        return warnings

    def _recreate_validation_checks(self) -> None:
        """Collect and integrate validation checks from class-level Check objects."""
        # Clear existing checks
        self.validation_checks = []

        # Safely get class checks
        try:
            class_checks: dict[str, ValidationResult] = getattr(self.__class__, "_class_checks", {})
        except AttributeError:
            self.logger.debug("No class checks found")
            return

        if not isinstance(class_checks, dict):
            self.logger.warning(f"Expected dict for _class_checks, got {type(class_checks)}")
            return

        # Create validation functions from Check objects
        for check_name, check_obj in class_checks.items():
            if not hasattr(check_obj, "evaluate"):
                self.logger.warning(f"Check object '{check_name}' missing 'evaluate' method")
                continue

            validation_function = self._create_validation_function(check_obj)
            self.validation_checks.append(validation_function)

    def _create_validation_function(self, check_obj: ValidationResult) -> Callable[[Any], dict[str, Any] | None]:
        """Create a validation function from a check object, avoiding closure issues."""

        def check_function(problem_instance: Any) -> dict[str, Any] | None:
            try:
                if not hasattr(problem_instance, "variables"):
                    return None
                return check_obj.evaluate(problem_instance.variables)
            except Exception as e:
                if hasattr(problem_instance, "logger"):
                    problem_instance.logger.debug(f"Validation check evaluation failed: {e}")
                return None

        return check_function
