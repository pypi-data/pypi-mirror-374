"""Numerical utilities for Adaptive Dynamics Toolkit."""

from collections.abc import Callable

import numpy as np

from .config import config


def float_type() -> type:
    """Get the current floating point type from configuration."""
    precision = config.get("numerics.float_precision", "float64")
    return getattr(np, precision)


def epsilon() -> float:
    """Get the current epsilon value for numerical comparisons."""
    return config.get("numerics.epsilon", 1e-12)


def is_close(a: float, b: float, rtol: float | None = None, 
             atol: float | None = None) -> bool:
    """
    Check if two values are close within tolerance.
    
    Args:
        a: First value
        b: Second value
        rtol: Relative tolerance (defaults to config value)
        atol: Absolute tolerance (defaults to config value)
        
    Returns:
        True if values are close, False otherwise
    """
    if rtol is None:
        rtol = epsilon()
    if atol is None:
        atol = epsilon()
    
    return np.isclose(a, b, rtol=rtol, atol=atol)


def solve_fixed_point(
    func: Callable[[float], float],
    x0: float,
    tol: float | None = None,
    max_iter: int | None = None,
    relaxation: float = 1.0
) -> tuple[float, int]:
    """
    Solve for fixed point x where func(x) = x using iteration.
    
    Args:
        func: Function to find fixed point for
        x0: Initial guess
        tol: Tolerance for convergence (defaults to config epsilon)
        max_iter: Maximum number of iterations (defaults to config value)
        relaxation: Relaxation factor (1.0 = no relaxation)
        
    Returns:
        Tuple of (fixed_point_value, iterations_used)
    """
    if tol is None:
        tol = epsilon()
    if max_iter is None:
        max_iter = config.get("numerics.max_iterations", 1000)
    
    x = x0
    for i in range(max_iter):
        x_new = (1 - relaxation) * x + relaxation * func(x)
        if abs(x_new - x) < tol:
            return x_new, i + 1
        x = x_new
    
    # If we get here, we didn't converge
    return x, max_iter


def derivative(
    func: Callable[[float], float],
    x: float,
    h: float | None = None,
    method: str = "central"
) -> float:
    """
    Compute numerical derivative of a function.
    
    Args:
        func: Function to differentiate
        x: Point at which to evaluate derivative
        h: Step size (defaults to sqrt(epsilon))
        method: Differentiation method ('forward', 'backward', or 'central')
        
    Returns:
        Numerical derivative value
    """
    if h is None:
        h = np.sqrt(epsilon())
    
    if method == "central":
        return (func(x + h) - func(x - h)) / (2 * h)
    if method == "forward":
        return (func(x + h) - func(x)) / h
    if method == "backward":
        return (func(x) - func(x - h)) / h
    raise ValueError(f"Unknown differentiation method: {method}")


def integrate_trapezoid(
    func: Callable[[float], float],
    a: float,
    b: float,
    n: int = 1000
) -> float:
    """
    Numerical integration using the trapezoidal rule.
    
    Args:
        func: Function to integrate
        a: Lower bound
        b: Upper bound
        n: Number of intervals
        
    Returns:
        Definite integral approximation
    """
    if a == b:
        return 0.0
    
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = np.array([func(xi) for xi in x])
    
    return h * (0.5 * (y[0] + y[-1]) + np.sum(y[1:-1]))