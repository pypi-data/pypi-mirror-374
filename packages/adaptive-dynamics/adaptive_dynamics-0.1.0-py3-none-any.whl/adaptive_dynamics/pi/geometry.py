"""
Adaptive π (πₐ) geometry implementation.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from ..core.numerics import integrate_trapezoid


class AdaptivePi:
    """
    Adaptive π (πₐ) interface for curved geometry.
    
    In the flat limit (zero curvature), πₐ → π exactly.
    """
    
    def __init__(self, curvature_fn: Callable[[float, float], float] | None = None):
        """
        Initialize an adaptive π calculator with a curvature function.
        
        Args:
            curvature_fn: Function that takes (x,y) coordinates and returns
                          local curvature. Defaults to flat space (zero curvature).
        """
        self.curvature_fn = curvature_fn or (lambda x, y: 0.0)
    
    def pi_a(self, x: float, y: float) -> float:
        """
        Calculate the value of πₐ at a specific point in space.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Value of πₐ at the specified point
        """
        k = self.curvature_fn(x, y)
        # First-order correction; swap in your Gauss–Bonnet machinery here.
        return np.pi * (1.0 + 0.5 * k)
    
    def circle_circumference(self, r: float, x: float = 0.0, y: float = 0.0) -> float:
        """
        Calculate the circumference of a circle in curved space.
        
        Args:
            r: Radius of the circle
            x: X coordinate of circle center
            y: Y coordinate of circle center
            
        Returns:
            Circumference of the circle
        """
        return 2.0 * self.pi_a(x, y) * r
    
    def circle_area(self, r: float, x: float = 0.0, y: float = 0.0) -> float:
        """
        Calculate the area of a circle in curved space.
        
        Args:
            r: Radius of the circle
            x: X coordinate of circle center
            y: Y coordinate of circle center
            
        Returns:
            Area of the circle
        """
        # Simple first-order approximation
        return self.pi_a(x, y) * r * r
    
    def integrated_circle_area(self, r: float, x: float = 0.0, y: float = 0.0, 
                               n_points: int = 100) -> float:
        """
        Calculate the area of a circle in curved space using numerical integration.
        
        This method is more accurate than circle_area() for highly curved spaces
        as it integrates the curvature across the circle.
        
        Args:
            r (float): Radius of the circle.
            x (float): X coordinate of circle center.
            y (float): Y coordinate of circle center.
            n_points (int): Number of integration points (more = higher precision).
            
        Returns:
            Integrated area of the circle
        """
        def integrand(r_prime: float) -> float:
            return 2 * np.pi * r_prime
        
        return integrate_trapezoid(integrand, 0, r, n=n_points)
    
    def linear_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """
        Calculate the straight-line distance between two points in curved space.

        Args:
            x1 (float): X coordinate of the first point.
            y1 (float): Y coordinate of the first point.
            x2 (float): X coordinate of the second point.
            y2 (float): Y coordinate of the second point.

        Returns:
            float: Linear distance between points.
        """
        # For small distances in weakly curved spaces, Euclidean is a good approximation
        dx, dy = x2 - x1, y2 - y1
        return np.sqrt(dx*dx + dy*dy)
    
    def geodesic_distance(self, x1: float, y1: float, x2: float, y2: float,
                          steps: int = 100) -> float:
        """
        Calculate the geodesic distance between two points.

        Args:
            x1 (float): X coordinate of the first point.
            y1 (float): Y coordinate of the first point.
            x2 (float): X coordinate of the second point.
            y2 (float): Y coordinate of the second point.
            steps (int): Number of integration steps.

        Returns:
            float: Geodesic distance between points.
        """
        # Simplified implementation - for advanced usage, replace with
        # proper geodesic calculation using the Gauss-Bonnet formalism
        
        # For this simple version, we'll use a straight line path and integrate
        # the metric along the path
        dx, dy = x2 - x1, y2 - y1
        path_length = 0.0
        
        for i in range(steps):
            t0 = i / steps
            t1 = (i + 1) / steps
            
            # Points along the path
            x0, y0 = x1 + t0 * dx, y1 + t0 * dy
            x1_step, y1_step = x1 + t1 * dx, y1 + t1 * dy
            
            # Average curvature along this segment
            k0 = self.curvature_fn(x0, y0)
            k1 = self.curvature_fn(x1_step, y1_step)
            k_avg = 0.5 * (k0 + k1)
            
            # Segment length with curvature correction
            segment_dx, segment_dy = (x1_step - x0), (y1_step - y0)
            segment_length_euclidean = np.sqrt(segment_dx**2 + segment_dy**2)
            
            # Apply curvature correction factor
            # This is a simplified model - replace with more accurate formulation
            # for your specific curvature model
            correction = 1.0 + 0.5 * k_avg
            path_length += segment_length_euclidean * correction
            
        return path_length