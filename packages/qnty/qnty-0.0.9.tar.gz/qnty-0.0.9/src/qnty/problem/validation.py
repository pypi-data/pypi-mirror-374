"""
Problem-validation integration for Problem class.

This module contains validation check management and execution
integrated with the Problem system.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class ValidationMixin:
    """Mixin class providing validation functionality."""
    
    # These attributes will be provided by other mixins in the final Problem class
    logger: Any
    warnings: list[dict[str, Any]]
    validation_checks: list[Callable]

    def add_validation_check(self, check_function: Callable) -> None:
        """Add a validation check function."""
        self.validation_checks.append(check_function)

    def validate(self) -> list[dict[str, Any]]:
        """Run all validation checks and return any warnings."""
        validation_warnings = []
        
        for check in self.validation_checks:
            try:
                result = check(self)
                if result:
                    validation_warnings.append(result)
            except Exception as e:
                self.logger.debug(f"Validation check failed: {e}")
        
        return validation_warnings

    def get_warnings(self) -> list[dict[str, Any]]:
        """Get all warnings from the problem."""
        warnings = self.warnings.copy()
        warnings.extend(self.validate())
        return warnings

    def _recreate_validation_checks(self):
        """Collect and integrate validation checks from class-level Check objects."""
        # Clear existing checks
        self.validation_checks = []
        
        # Collect Check objects from metaclass
        class_checks = getattr(self.__class__, '_class_checks', {})
        
        for check in class_checks.values():
            # Create a validation function from the Check object
            def make_check_function(check_obj):
                def check_function(problem_instance):
                    return check_obj.evaluate(problem_instance.variables)
                return check_function
            
            self.validation_checks.append(make_check_function(check))
