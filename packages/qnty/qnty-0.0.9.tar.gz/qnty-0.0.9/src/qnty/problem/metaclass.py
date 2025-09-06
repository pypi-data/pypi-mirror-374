"""
Metaclass system for EngineeringProblem composition.

This module provides the metaclass infrastructure that enables clean
sub-problem composition syntax at the class definition level. The system
automatically detects and proxies sub-problems during class creation,
allowing for natural dotted access in equations.

Key Features:
- Automatic sub-problem detection and proxying
- Clean composition syntax with dotted access
- Proper namespace isolation and variable management
- Comprehensive error handling and validation

Example Usage:
    class BranchReinforcementProblem(EngineeringProblem):
        # Sub-problems are automatically detected and proxied
        header = create_straight_pipe_internal()
        branch = create_straight_pipe_internal()
        
        # Configure sub-problem variables with fluent API
        header.D.set(2.375).inch
        branch.D.set(1.315).inch
        
        # Equations can naturally reference sub-problem variables
        d_1_eqn = d_1.equals((branch.D - 2 * (branch.T_n - branch.c)) / sin(beta))
        
        # The metaclass handles all the complex namespace management automatically
"""

from __future__ import annotations

from typing import Any

from ..validation.rules import Rules
from .composition import SubProblemProxy

# Constants for better maintainability
RESERVED_ATTRIBUTES: set[str] = {'name', 'description'}
PRIVATE_ATTRIBUTE_PREFIX = '_'
SUB_PROBLEM_REQUIRED_ATTRIBUTES: tuple[str, ...] = ('variables', 'equations')


# Custom exceptions for better error handling
class MetaclassError(Exception):
    """Base exception for metaclass-related errors."""
    pass


class SubProblemProxyError(MetaclassError):
    """Raised when sub-problem proxy creation fails."""
    pass


class NamespaceError(MetaclassError):
    """Raised when namespace operations fail."""
    pass


class ProblemMeta(type):
    """
    Metaclass that processes class-level sub-problems to create proper namespace proxies
    BEFORE any equations are evaluated.
    
    This metaclass enables clean composition syntax like:
        class MyProblem(EngineeringProblem):
            header = create_pipe_problem()
            branch = create_pipe_problem()
            # Equations can reference header.P, branch.T, etc.
    """
    
    # Declare the attributes that will be dynamically added to created classes
    _original_sub_problems: dict[str, Any]
    _proxy_configurations: dict[str, dict[str, Any]]
    _class_checks: dict[str, Any]
    
    @classmethod
    def __prepare__(mcs, *args, **kwargs) -> ProxiedNamespace:
        """
        Called before the class body is evaluated.
        Returns a custom namespace that proxies sub-problems.
        
        Args:
            *args: Positional arguments (name, bases) - unused but required by protocol
            **kwargs: Additional keyword arguments - unused but required by protocol
            
        Returns:
            ProxiedNamespace that will handle sub-problem proxying
        """
        # Parameters are required by metaclass protocol but not used in this implementation
        del args, kwargs  # Explicitly acknowledge unused parameters
        return ProxiedNamespace()
    
    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: ProxiedNamespace, **kwargs) -> type:
        """
        Create the new class with properly integrated sub-problems.
        
        Args:
            name: Name of the class being created
            bases: Base classes
            namespace: The ProxiedNamespace containing proxied sub-problems
            **kwargs: Additional keyword arguments - unused but required by protocol
            
        Returns:
            The newly created class with metaclass attributes
            
        Raises:
            MetaclassError: If class creation fails due to metaclass issues
        """
        # kwargs is required by metaclass protocol but not used in this implementation
        del kwargs  # Explicitly acknowledge unused parameter
        try:
            # Validate the namespace
            if not isinstance(namespace, ProxiedNamespace):
                raise MetaclassError(f"Expected ProxiedNamespace, got {type(namespace)}")
            
            # Extract the original sub-problems and proxy objects from the namespace
            sub_problem_proxies = getattr(namespace, '_sub_problem_proxies', {})
            proxy_objects = getattr(namespace, '_proxy_objects', {})
            
            # Validate that proxy objects are consistent
            if set(sub_problem_proxies.keys()) != set(proxy_objects.keys()):
                raise MetaclassError("Inconsistent proxy state: sub-problem and proxy object keys don't match")
            
            # Create the class normally
            cls = super().__new__(mcs, name, bases, dict(namespace))
            
            # Store the original sub-problems and proxy configurations for later integration
            cls._original_sub_problems = sub_problem_proxies
            
            # Extract configurations safely with error handling
            proxy_configurations = {}
            for proxy_name, proxy in proxy_objects.items():
                try:
                    # Cache configurations to avoid recomputation
                    if not hasattr(proxy, '_cached_configurations'):
                        proxy._cached_configurations = proxy.get_configurations()
                    proxy_configurations[proxy_name] = proxy._cached_configurations
                except Exception as e:
                    raise SubProblemProxyError(f"Failed to get configurations from proxy '{proxy_name}': {e}") from e
            
            cls._proxy_configurations = proxy_configurations
            
            # Collect Check objects from class attributes
            checks = {}
            for attr_name, attr_value in namespace.items():
                if isinstance(attr_value, Rules):
                    checks[attr_name] = attr_value
            
            cls._class_checks = checks
            
            return cls
            
        except Exception as e:
            # Re-raise MetaclassError and SubProblemProxyError as-is
            if isinstance(e, MetaclassError | SubProblemProxyError):
                raise
            # Wrap other exceptions
            raise MetaclassError(f"Failed to create class '{name}': {e}") from e


class ProxiedNamespace(dict):
    """
    Custom namespace that automatically proxies sub-problems as they're added.
    
    This namespace intercepts class attribute assignments during class creation
    and automatically wraps EngineeringProblem objects in SubProblemProxy objects.
    This enables clean composition syntax where sub-problems can be referenced
    with dot notation in equations.
    
    Example:
        class ComposedProblem(EngineeringProblem):
            header = create_pipe_problem()  # Gets proxied automatically
            branch = create_pipe_problem()  # Gets proxied automatically
            # Now equations can use header.P, branch.T, etc.
    """
    
    def __init__(self) -> None:
        """Initialize the proxied namespace with empty storage."""
        super().__init__()
        self._sub_problem_proxies: dict[str, Any] = {}
        self._proxy_objects: dict[str, SubProblemProxy] = {}
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Intercept attribute assignment and proxy sub-problems automatically.
        
        Args:
            key: The attribute name being set
            value: The value being assigned
            
        Raises:
            NamespaceError: If namespace operation fails
            SubProblemProxyError: If proxy creation fails
        """
        try:
            if self._is_sub_problem(key, value):
                self._create_and_store_proxy(key, value)
            elif self._is_variable_with_auto_symbol(value):
                self._set_variable_symbol_and_store(key, value)
            else:
                super().__setitem__(key, value)
        except Exception as e:
            if isinstance(e, NamespaceError | SubProblemProxyError):
                raise
            raise NamespaceError(f"Failed to set attribute '{key}': {e}") from e
    
    def _is_sub_problem(self, key: str, value: Any) -> bool:
        """
        Determine if a value should be treated as a sub-problem.
        
        Args:
            key: The attribute name
            value: The value being assigned
            
        Returns:
            True if this should be proxied as a sub-problem
        """
        # Quick checks first (fail fast)
        if key.startswith(PRIVATE_ATTRIBUTE_PREFIX) or key in RESERVED_ATTRIBUTES:
            return False
        
        # Check for None or basic types that definitely aren't sub-problems
        if value is None or isinstance(value, str | int | float | bool | list | dict):
            return False
        
        # Cache hasattr results to avoid repeated attribute lookups
        if not hasattr(self, '_attr_cache'):
            self._attr_cache = {}
        
        # Use object id as cache key since objects are unique
        cache_key = (id(value), tuple(SUB_PROBLEM_REQUIRED_ATTRIBUTES))
        if cache_key not in self._attr_cache:
            self._attr_cache[cache_key] = all(hasattr(value, attr) for attr in SUB_PROBLEM_REQUIRED_ATTRIBUTES)
        
        return self._attr_cache[cache_key]
    
    def _is_variable_with_auto_symbol(self, value: Any) -> bool:
        """
        Determine if a value is a Variable that needs automatic symbol assignment.
        
        Args:
            value: The value being assigned
            
        Returns:
            True if this is a Variable with symbol == "<auto>"
        """
        # Import Variable here to avoid circular imports
        try:
            from qnty.quantities.quantity import TypeSafeVariable as Variable
            return isinstance(value, Variable) and value.symbol == "<auto>"
        except ImportError:
            return False
    
    def _set_variable_symbol_and_store(self, key: str, value: Any) -> None:
        """
        Set the variable's symbol to the attribute name and store it.
        
        Args:
            key: The attribute name to use as symbol
            value: The Variable object
        """
        try:
            # Set the symbol to the attribute name
            value.symbol = key
            # Store the modified variable
            super().__setitem__(key, value)
        except Exception as e:
            raise NamespaceError(f"Failed to set symbol for variable '{key}': {e}") from e
    
    def _create_and_store_proxy(self, key: str, value: Any) -> None:
        """
        Create a proxy for the sub-problem and store references.
        
        Args:
            key: The attribute name for the sub-problem
            value: The sub-problem object to proxy
            
        Raises:
            SubProblemProxyError: If proxy creation fails
            NamespaceError: If key already exists as a sub-problem
        """
        # Check for conflicts
        if key in self._sub_problem_proxies:
            raise NamespaceError(f"Sub-problem '{key}' already exists in namespace")
        
        try:
            # Store the original sub-problem
            self._sub_problem_proxies[key] = value
            
            # Create and store the proxy
            proxy = SubProblemProxy(value, key)
            self._proxy_objects[key] = proxy
            
            # Set the proxy in the namespace
            super().__setitem__(key, proxy)
            
        except Exception as e:
            # Clean up partial state on failure
            self._sub_problem_proxies.pop(key, None)
            self._proxy_objects.pop(key, None)
            raise SubProblemProxyError(f"Failed to create proxy for sub-problem '{key}': {e}") from e
