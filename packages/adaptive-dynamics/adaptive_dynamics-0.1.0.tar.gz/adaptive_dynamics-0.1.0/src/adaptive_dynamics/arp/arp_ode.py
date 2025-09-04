"""
Core ODE formulation for ARP (Adaptive Resistance-Potential) optimization.

The fundamental equation is: dG/dt = α|I| - μG

Where:
- G is the conductance-like state variable
- I is the input signal (gradient)
- α is the adaptation rate
- μ is the decay rate
"""

from collections.abc import Callable

import numpy as np


class ARPSystem:
    """
    Core ARP differential equation system solver.
    
    This provides the fundamental ARP dynamics independently from any
    specific machine learning framework.
    """
    
    def __init__(
        self,
        alpha: float = 0.01,
        mu: float = 0.001,
        dt: float = 1.0,
        g_init: float | None = None
    ):
        """
        Initialize an ARP system.
        
        Args:
            alpha: Adaptation rate parameter
            mu: Decay rate parameter
            dt: Time step for integration
            g_init: Initial conductance (default: 0.0)
        """
        self.alpha = alpha
        self.mu = mu
        self.dt = dt
        self.g_init = g_init if g_init is not None else 0.0
    
    def step(self, g: np.ndarray, i: np.ndarray) -> np.ndarray:
        """
        Update the conductance state G based on the ARP ODE.
        
        Args:
            g: Current conductance state
            i: Current input signal
            
        Returns:
            Updated conductance state
        """
        # Core ARP update: dG/dt = α|I| - μG
        dg = self.alpha * np.abs(i) - self.mu * g
        return g + dg * self.dt
    
    def batch_step(self, g_batch: np.ndarray, i_batch: np.ndarray) -> np.ndarray:
        """
        Update conductance for a batch of values.
        
        Args:
            g_batch: Current conductance states, shape (batch_size, ...)
            i_batch: Current input signals, shape (batch_size, ...)
            
        Returns:
            Updated conductance states
        """
        return self.step(g_batch, i_batch)
    
    def integrate(
        self,
        input_func: Callable[[float], np.ndarray],
        t_start: float = 0.0,
        t_end: float = 1.0,
        g_start: np.ndarray | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Integrate the ARP system over time with a time-varying input.
        
        Args:
            input_func: Function that returns input at time t
            t_start: Start time for integration
            t_end: End time for integration
            g_start: Initial conductance state (default: g_init)
            
        Returns:
            Tuple of (time_points, conductance_values)
        """
        if g_start is None:
            g_start = np.full_like(input_func(t_start), self.g_init)
        
        # Number of time steps
        n_steps = int(np.ceil((t_end - t_start) / self.dt))
        dt = (t_end - t_start) / n_steps
        
        # Arrays to store results
        t_points = np.linspace(t_start, t_end, n_steps + 1)
        g_values = np.zeros((n_steps + 1,) + g_start.shape)
        g_values[0] = g_start
        
        # Integration loop
        g = g_start.copy()
        for i in range(n_steps):
            t = t_start + i * dt
            input_val = input_func(t)
            g = self.step(g, input_val)
            g_values[i + 1] = g
        
        return t_points, g_values
    
    def effective_rate(self, g: np.ndarray) -> np.ndarray:
        """
        Calculate effective learning rate modulation based on conductance.
        
        Args:
            g: Conductance state
            
        Returns:
            Effective rate modulation factor
        """
        return 1.0 / (1.0 + g)


# Example usage:
# arp = ARPSystem(alpha=0.01, mu=0.001)
# g = np.zeros(10)  # Initial conductance
# for _ in range(100):
#     i = np.random.randn(10)  # Some input signal
#     g = arp.step(g, i)
#     effective_rate = arp.effective_rate(g)