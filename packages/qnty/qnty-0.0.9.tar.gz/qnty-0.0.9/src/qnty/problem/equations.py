"""
Equation processing pipeline for Problem class.

This module contains all equation-related operations including adding equations,
processing equation validation, handling missing variables, and equation reconstruction.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qnty.equations import Equation
    from qnty.quantities import TypeSafeVariable as Variable

from qnty.equations import Equation

# Constants for equation processing
MATHEMATICAL_OPERATORS = ['+', '-', '*', '/', ' / ', ' * ', ' + ', ' - ']
COMMON_COMPOSITE_VARIABLES = ['P', 'c', 'S', 'E', 'W', 'Y']


# Custom Exceptions
class EquationValidationError(ValueError):
    """Raised when an equation fails validation."""
    pass


class EquationsMixin:
    """Mixin class providing equation management functionality."""
    
    # These attributes/methods will be provided by other mixins in the final Problem class
    variables: dict[str, Variable]
    equations: list[Equation]
    equation_system: Any
    sub_problems: dict[str, Any]
    logger: Any
    equation_reconstructor: Any
    
    def _create_placeholder_variable(self, _symbol: str) -> None:
        """Will be provided by VariablesMixin."""
        ...

    def add_equation(self, equation: Equation) -> None:
        """
        Add an equation to the problem.
        
        The equation will be validated to ensure all referenced variables exist.
        Missing variables that look like simple identifiers will be auto-created
        as unknown placeholders.
        
        Args:
            equation: Equation object to add to the problem
            
        Raises:
            EquationValidationError: If the equation is invalid or cannot be processed
            
        Note:
            Adding an equation resets the problem to unsolved state.
        """
        if equation is None:
            raise EquationValidationError("Cannot add None equation to problem")
        
        # Fix VariableReferences in equation to point to correct Variables
        equation = self._fix_variable_references(equation)
        
        # Validate that all variables in the equation exist
        try:
            equation_vars = equation.get_all_variables()
        except Exception as e:
            raise EquationValidationError(f"Failed to extract variables from equation: {e}") from e
        
        missing_vars = [var for var in equation_vars if var not in self.variables]
        
        if missing_vars:
            self._handle_missing_variables(missing_vars)
            
            # Check again for remaining missing variables
            equation_vars = equation.get_all_variables()
            remaining_missing = [var for var in equation_vars if var not in self.variables]
            if remaining_missing:
                self.logger.warning(f"Equation references missing variables: {remaining_missing}")
        
        self.equations.append(equation)
        self.equation_system.add_equation(equation)
        self.is_solved = False

    def add_equations(self, *equations: Equation):
        """Add multiple equations to the problem."""
        for eq in equations:
            self.add_equation(eq)
        return self

    def _handle_missing_variables(self, missing_vars: list[str]) -> None:
        """Handle missing variables by creating placeholders for simple symbols."""
        for missing_var in missing_vars:
            if self._is_simple_variable_symbol(missing_var):
                self._create_placeholder_variable(missing_var)

    def _is_simple_variable_symbol(self, symbol: str) -> bool:
        """Check if a symbol looks like a simple variable identifier."""
        return (symbol.isidentifier() and
                not any(char in symbol for char in ['(', ')', '+', '-', '*', '/', ' ']))

    def _process_equation(self, attr_name: str, equation: Equation) -> bool:
        """Process a single equation and add it to the problem if valid."""
        return self._process_equation_impl(attr_name, equation)
    
    def _process_equation_impl(self, attr_name: str, equation: Equation) -> bool:
        """
        Process a single equation and determine if it should be added.
        Returns True if the equation was successfully processed.
        """
        # First, update variable references to use symbols instead of names
        updated_equation = self._update_equation_variable_references(equation)
        
        # Check if this equation contains delayed expressions
        try:
            has_delayed = self.equation_reconstructor.contains_delayed_expressions(updated_equation)
            if has_delayed:
                return self._handle_delayed_equation(attr_name, updated_equation)
        except Exception as e:
            self.logger.debug(f"Error checking delayed expressions for {attr_name}: {e}")
        
        # Check if this equation has invalid self-references
        try:
            has_self_ref = self._has_invalid_self_references(updated_equation)
            if has_self_ref:
                self.logger.debug(f"Skipping invalid self-referencing equation {attr_name}: {updated_equation}")
                return False
        except Exception as e:
            self.logger.debug(f"Error checking self-references for {attr_name}: {e}")
        
        # Check if equation references non-existent variables
        try:
            has_missing = self._equation_has_missing_variables(updated_equation)
            if has_missing:
                return self._handle_equation_with_missing_variables(attr_name, updated_equation)
        except Exception as e:
            self.logger.debug(f"Error checking missing variables for {attr_name}: {e}")
        
        # Process valid equation
        self.add_equation(updated_equation)
        return True

    def _handle_delayed_equation(self, attr_name: str, equation: Equation) -> bool:
        """Handle equations with delayed expressions."""
        resolved_equation = self.equation_reconstructor.resolve_delayed_equation(equation)
        if resolved_equation:
            self.add_equation(resolved_equation)
            setattr(self, attr_name, resolved_equation)
            return True
        else:
            self.logger.debug(f"Skipping unresolvable delayed equation {attr_name}: {equation}")
            return False

    def _handle_equation_with_missing_variables(self, attr_name: str, equation: Equation) -> bool:
        """Handle equations that reference missing variables."""
        # Handle conditional equations more carefully
        if self._is_conditional_equation(equation):
            return self._handle_conditional_equation(attr_name, equation)
        
        # Only attempt reconstruction for simple mathematical expressions from composition
        if self.equation_reconstructor.should_attempt_reconstruction(equation):
            return self._attempt_equation_reconstruction(attr_name, equation)
        else:
            # Skip other problematic equations
            self.logger.debug(f"Skipping equation with missing variables {attr_name}: {equation}")
            return False

    def _handle_conditional_equation(self, attr_name: str, equation: Equation) -> bool:
        """Handle conditional equations with missing variables."""
        missing_vars = equation.get_all_variables() - set(self.variables.keys())
        
        # Skip conditional equations from sub-problems in composed systems
        if self.sub_problems and self._is_conditional_equation_from_subproblem(equation, attr_name):
            self.logger.debug(f"Skipping conditional equation {attr_name} from sub-problem in composed system")
            return False
        
        # Check for composite expressions that might be reconstructable
        unresolvable_vars = [var for var in missing_vars
                           if any(op in var for op in MATHEMATICAL_OPERATORS)]
        
        if self.sub_problems and unresolvable_vars:
            # Before skipping, try to reconstruct conditional equations with composite expressions
            self.logger.debug(f"Attempting to reconstruct conditional equation {attr_name} with composite variables: {unresolvable_vars}")
            reconstructed_equation = self.equation_reconstructor.reconstruct_composite_expressions_generically(equation)
            if reconstructed_equation:
                self.logger.debug(f"Successfully reconstructed conditional equation {attr_name}: {reconstructed_equation}")
                self.add_equation(reconstructed_equation)
                setattr(self, attr_name, reconstructed_equation)
                return True
            else:
                self.logger.debug(f"Failed to reconstruct conditional equation {attr_name}, trying simple substitution")
                # Try simple substitution for basic arithmetic expressions
                reconstructed_equation = self._try_simple_substitution(equation, missing_vars)
                if reconstructed_equation:
                    self.add_equation(reconstructed_equation)
                    return True
                else:
                    self.add_equation(equation)
                    return True
        else:
            # Try to add the conditional equation even with missing simple variables
            self.add_equation(equation)
            return True

    def _try_simple_substitution(self, _equation: Equation, _missing_vars: set[str]) -> Equation | None:
        """
        Try simple substitution for basic arithmetic expressions in conditional equations.
        
        The real issue is that nested expressions in conditionals aren't being handled properly.
        For now, just return None and let the equation be added as-is.
        """
        return None

    def _attempt_equation_reconstruction(self, attr_name: str, equation: Equation) -> bool:
        """Attempt to reconstruct equations with composite expressions."""
        missing_vars = equation.get_all_variables() - set(self.variables.keys())
        self.logger.debug(f"Attempting to reconstruct equation {attr_name} with missing variables: {missing_vars}")
        
        reconstructed_equation = self.equation_reconstructor.reconstruct_composite_expressions_generically(equation)
        if reconstructed_equation:
            self.logger.debug(f"Successfully reconstructed {attr_name}: {reconstructed_equation}")
            self.add_equation(reconstructed_equation)
            setattr(self, attr_name, reconstructed_equation)
            return True
        else:
            self.logger.debug(f"Failed to reconstruct equation {attr_name}: {equation}")
            return False

    def _get_equation_lhs_symbol(self, equation: Equation) -> str | None:
        """Safely extract the symbol from equation's left-hand side."""
        return getattr(equation.lhs, 'symbol', None)

    def _is_conditional_equation(self, equation: Equation) -> bool:
        """Check if an equation is a conditional equation."""
        return 'cond(' in str(equation)

    def _equation_has_missing_variables(self, equation: Equation) -> bool:
        """Check if an equation references variables that don't exist in this problem."""
        try:
            all_vars = equation.get_all_variables()
            missing_vars = [var for var in all_vars if var not in self.variables]
            return len(missing_vars) > 0
        except Exception:
            return False

    def _has_invalid_self_references(self, equation: Equation) -> bool:
        """
        Check if an equation has invalid self-references.
        This catches malformed equations like 'c = max(c, c)' from class definition.
        """
        try:
            # Get LHS variable - check if it has symbol attribute
            lhs_symbol = self._get_equation_lhs_symbol(equation)
            if lhs_symbol is None:
                return False
            
            # Get all variables referenced in RHS
            rhs_vars = equation.rhs.get_variables() if hasattr(equation.rhs, 'get_variables') else set()
            
            # Check if the LHS variable appears multiple times in RHS (indicating self-reference)
            # This is a heuristic - a proper implementation would parse the expression tree
            equation_str = str(equation)
            if lhs_symbol in rhs_vars:
                # For conditional equations, self-references are often valid (as fallback values)
                if 'cond(' in equation_str:
                    return False  # Allow self-references in conditional equations
                
                # Count occurrences of the variable in the equation string
                count = equation_str.count(lhs_symbol)
                if count > 2:  # LHS + multiple RHS occurrences
                    return True
            
            return False
            
        except Exception:
            return False

    def _is_conditional_equation_from_subproblem(self, equation: Equation, _equation_name: str) -> bool:
        """
        Check if a conditional equation comes from a sub-problem and should be skipped in composed systems.
        
        In composed systems, if a sub-problem's conditional variable is already set to a known value,
        we don't want to include the conditional equation that would override that known value.
        """
        try:
            # Check if this is a conditional equation with a known LHS variable
            lhs_symbol = self._get_equation_lhs_symbol(equation)
            if lhs_symbol is not None:
                
                # Check if the LHS variable already exists and is known
                if lhs_symbol in self.variables:
                    var = self.variables[lhs_symbol]
                    # If the variable is already known (set explicitly in composition),
                    # and this conditional equation references missing variables, skip it
                    missing_vars = equation.get_all_variables() - set(self.variables.keys())
                    if missing_vars and var.is_known:
                        # This is a sub-problem's conditional equation for a variable that's already known
                        # No point including it since the value is already determined
                        return True
            
            return False
            
        except Exception:
            return False

    def _fix_variable_references(self, equation: Equation) -> Equation:
        """
        Fix VariableReferences in equation expressions to point to Variables in problem.variables.
        
        This resolves issues where expression trees contain VariableReferences pointing to
        proxy Variables from class creation time instead of the actual Variables in the problem.
        """
        try:
            # Fix the RHS expression
            fixed_rhs = self._fix_expression_variables(equation.rhs)
            
            # Create new equation with fixed RHS (LHS should already be correct)
            return Equation(equation.name, equation.lhs, fixed_rhs)
            
        except Exception as e:
            self.logger.debug(f"Error fixing variable references in equation {equation.name}: {e}")
            return equation  # Return original if fixing fails

    def _fix_expression_variables(self, expr):
        """
        Recursively fix VariableReferences in an expression tree to point to correct Variables.
        """
        from qnty.expressions import BinaryOperation, Constant, VariableReference
        
        if isinstance(expr, VariableReference):
            # Check if this VariableReference points to the wrong Variable
            symbol = getattr(expr, 'symbol', None)
            if symbol and symbol in self.variables:
                correct_var = self.variables[symbol]
                if expr.variable is not correct_var:
                    # Create new VariableReference pointing to correct Variable
                    return VariableReference(correct_var)
            return expr
            
        elif isinstance(expr, BinaryOperation):
            # Recursively fix left and right operands
            fixed_left = self._fix_expression_variables(expr.left)
            fixed_right = self._fix_expression_variables(expr.right)
            return BinaryOperation(expr.operator, fixed_left, fixed_right)
            
        elif hasattr(expr, 'operand'):
            # Recursively fix operand
            fixed_operand = self._fix_expression_variables(expr.operand)
            return type(expr)(expr.operator, fixed_operand)
            
        elif hasattr(expr, 'function_name'):
            # Recursively fix left and right operands
            fixed_left = self._fix_expression_variables(expr.left)
            fixed_right = self._fix_expression_variables(expr.right)
            return type(expr)(expr.function_name, fixed_left, fixed_right)
            
        elif isinstance(expr, Constant):
            return expr
            
        else:
            # Unknown expression type, return as-is
            return expr

    def _update_equation_variable_references(self, equation: Equation) -> Equation:
        """Update VariableReference objects in equation to use symbols instead of names."""
        from qnty.expressions import VariableReference
        
        # Update LHS if it's a VariableReference
        updated_lhs = equation.lhs
        if isinstance(equation.lhs, VariableReference):
            # Find the variable by name and update to use symbol
            var_name = equation.lhs.variable.name
            matching_var = None
            for var in self.variables.values():
                if var.name == var_name:
                    matching_var = var
                    break
            if matching_var and matching_var.symbol:
                updated_lhs = VariableReference(matching_var)
        
        # Update RHS by recursively updating expressions
        updated_rhs = self._update_expression_variable_references(equation.rhs)
        
        # Create new equation with updated references
        return Equation(equation.name, updated_lhs, updated_rhs)
    
    def _update_expression_variable_references(self, expr):
        """Recursively update VariableReference objects in expression tree."""
        from qnty.expressions import BinaryOperation, Constant, VariableReference
        
        if isinstance(expr, VariableReference):
            # Find the variable by name and update to use symbol
            var_name = expr.variable.name
            matching_var = None
            for var in self.variables.values():
                if var.name == var_name:
                    matching_var = var
                    break
            if matching_var and matching_var.symbol:
                return VariableReference(matching_var)
            return expr
        elif isinstance(expr, BinaryOperation):
            updated_left = self._update_expression_variable_references(expr.left)
            updated_right = self._update_expression_variable_references(expr.right)
            return BinaryOperation(expr.operator, updated_left, updated_right)
        elif isinstance(expr, Constant):
            return expr
        else:
            # Return unknown expression types as-is
            return expr
