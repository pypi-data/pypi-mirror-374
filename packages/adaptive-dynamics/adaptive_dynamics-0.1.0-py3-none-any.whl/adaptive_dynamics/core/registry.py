"""Registry system for adaptive dynamics components."""

import inspect
import logging
from typing import Any, Generic, TypeVar

T = TypeVar('T')

logger = logging.getLogger(__name__)


class Registry(Generic[T]):
    """
    A generic registry for components.
    
    This registry allows registration and retrieval of components by name.
    It's useful for plugins, factory patterns, and dynamic component loading.
    """
    
    def __init__(self, base_type: type[T]):
        """
        Initialize a registry for a specific base type.
        
        Args:
            base_type: The base type or interface for registered components
        """
        self._registry: dict[str, type[T]] = {}
        self._base_type = base_type
    
    def register(self, name: str, cls: type[T]) -> type[T]:
        """
        Register a component class.
        
        Args:
            name: Unique name for the component
            cls: Component class to register
            
        Returns:
            The registered class (for decorator usage)
            
        Raises:
            TypeError: If cls is not a subclass of the registry's base type
            ValueError: If name is already registered
        """
        if not inspect.isclass(cls) or not issubclass(cls, self._base_type):
            raise TypeError(f"{cls.__name__} is not a subclass of {self._base_type.__name__}")
        
        if name in self._registry:
            raise ValueError(f"Component '{name}' is already registered")
        
        self._registry[name] = cls
        logger.debug(f"Registered {cls.__name__} as '{name}'")
        return cls
    
    def decorator(self, name: str | None = None):
        """
        Create a decorator for registering a class.
        
        Args:
            name: Optional name for registration, defaults to class name
            
        Returns:
            A decorator function
        """
        def decorator(cls: type[T]) -> type[T]:
            nonlocal name
            if name is None:
                name = cls.__name__
            return self.register(name, cls)
        return decorator
    
    def get(self, name: str) -> type[T]:
        """
        Get a registered component class by name.
        
        Args:
            name: Name of the registered component
            
        Returns:
            The registered component class
            
        Raises:
            KeyError: If name is not registered
        """
        if name not in self._registry:
            raise KeyError(f"Component '{name}' is not registered")
        
        return self._registry[name]
    
    def create(self, name: str, *args: Any, **kwargs: Any) -> T:
        """
        Create an instance of a registered component.
        
        Args:
            name: Name of the registered component
            *args: Positional arguments for the constructor
            **kwargs: Keyword arguments for the constructor
            
        Returns:
            An instance of the registered component
        """
        cls = self.get(name)
        return cls(*args, **kwargs)
    
    def names(self) -> set[str]:
        """Get all registered component names."""
        return set(self._registry.keys())
    
    def classes(self) -> dict[str, type[T]]:
        """Get all registered component classes."""
        return dict(self._registry)


# Example usage
# class Optimizer: pass
# optimizer_registry = Registry(Optimizer)