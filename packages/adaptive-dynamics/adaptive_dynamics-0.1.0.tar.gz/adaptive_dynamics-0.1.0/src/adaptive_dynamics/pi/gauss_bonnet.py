"""
Gauss-Bonnet theorem implementation for Adaptive π calculations.
"""

from collections.abc import Callable

import numpy as np


def compute_geodesic_curvature(
    curve_points: np.ndarray,
    metric_tensor: Callable[[float, float], np.ndarray]
) -> np.ndarray:
    """
    Compute the geodesic curvature along a curve.
    
    Args:
        curve_points (np.ndarray): Array of shape (n, 2) containing (x, y) coordinates.
        metric_tensor (Callable[[float, float], np.ndarray]): Function that returns the 2x2 metric tensor at (x, y).

    Returns:
        np.ndarray: Array of geodesic curvatures at each point except endpoints.
    """
    n_points = curve_points.shape[0]
    curvatures = np.zeros(n_points - 2)
    
    for i in range(1, n_points - 1):
        # Get three consecutive points
        p_prev = curve_points[i - 1]
        p_curr = curve_points[i]
        p_next = curve_points[i + 1]
        
        # Compute tangent vector using central difference
        tangent = 0.5 * (p_next - p_prev)
        tangent_norm = np.sqrt(np.sum(tangent**2))
        if tangent_norm > 0:
            tangent = tangent / tangent_norm
        
        # Compute acceleration vector using second derivative approximation
        acceleration = p_next - 2 * p_curr + p_prev
        
        # Get metric at current point
        g = metric_tensor(p_curr[0], p_curr[1])
        
        # Compute geodesic curvature (simplified formula)
        # This is a basic approximation - a full implementation would include
        # Christoffel symbols and the covariant derivative
        normal = np.array([-tangent[1], tangent[0]])  # Rotate 90 degrees
        
        # Project acceleration onto normal direction with metric tensor
        curvatures[i - 1] = np.dot(normal, np.dot(g, acceleration))
    
    return curvatures


def gauss_bonnet_integral(
    curve: np.ndarray,
    gaussian_curvature: Callable[[float, float], float],
    metric_tensor: Callable[[float, float], np.ndarray] | None = None
) -> float:
    """
    Apply the Gauss-Bonnet theorem to compute the integral of curvature.
    
    Args:
        curve (np.ndarray): Closed curve as array of (x, y) points, shape (n, 2).
        gaussian_curvature (Callable[[float, float], float]): Function returning Gaussian curvature at (x, y).
        metric_tensor (Callable[[float, float], np.ndarray] | None): Function returning the 2x2 metric tensor at (x, y) (if None, Euclidean metric is used).

    Returns:
        float: Total angle deficit (related to πₐ).
    """
    # Ensure the curve is closed
    if not np.allclose(curve[0], curve[-1]):
        curve = np.vstack([curve, curve[0]])
    
    n_points = curve.shape[0]
    
    # Default to Euclidean metric if not provided
    if metric_tensor is None:
        metric_tensor = lambda x, y: np.eye(2)
    
    # Compute geodesic curvature along the curve
    kg = compute_geodesic_curvature(curve, metric_tensor)
    
    # Compute the enclosed area (using shoelace formula for simplicity)
    # For more accuracy, use a proper area calculation in curved space
    x, y = curve[:, 0], curve[:, 1]
    area = 0.5 * np.abs(np.sum(x[:-1] * y[1:] - x[1:] * y[:-1]))
    
    # Estimate average Gaussian curvature in the enclosed region
    # For more accuracy, use proper integration of K over the surface
    x_center = np.mean(x)
    y_center = np.mean(y)
    K_avg = gaussian_curvature(x_center, y_center)
    
    # Compute the total geodesic curvature
    kg_total = np.sum(kg) * (2 * np.pi / n_points)
    
    # Apply Gauss-Bonnet: ∮ kg ds + ∫∫ K dA = 2π
    # Therefore, the angle deficit is:
    angle_deficit = 2 * np.pi - (kg_total + K_avg * area)
    
    return angle_deficit


def adaptive_pi_from_curvature(
    x: float,
    y: float,
    gaussian_curvature: Callable[[float, float], float],
    radius: float = 1.0
) -> float:
    """
    Compute adaptive π based on local curvature using Gauss-Bonnet theorem.
    
    Args:
        x (float): X coordinate of center point.
        y (float): Y coordinate of center point.
        gaussian_curvature (Callable[[float, float], float]): Function returning Gaussian curvature at (x, y).
        radius (float): Radius of the circle to consider.

    Returns:
        float: Value of πₐ at the specified point.
    """
    # First-order approximation based on curvature
    K = gaussian_curvature(x, y)
    
    # πₐ = π (1 + K r²/6 + ...)
    # This is a simplified formula - a full implementation would
    # integrate K over the disk with proper measure
    return np.pi * (1.0 + K * radius * radius / 6.0)


def angle_sum_triangle(
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    gaussian_curvature: Callable[[float, float], float]
) -> float:
    """
    Compute the sum of angles in a triangle on a curved surface.
    
    Args:
        p1 (tuple[float, float]): First triangle vertex as (x, y).
        p2 (tuple[float, float]): Second triangle vertex as (x, y).
        p3 (tuple[float, float]): Third triangle vertex as (x, y).
        gaussian_curvature (Callable[[float, float], float]): Function returning Gaussian curvature at (x, y).

    Returns:
        float: Sum of angles in the triangle (in radians).
    """
    # Create a triangular curve
    curve = np.array([p1, p2, p3, p1])
    
    # Compute the area of the triangle (shoelace formula)
    x = np.array([p1[0], p2[0], p3[0]])
    y = np.array([p1[1], p2[1], p3[1]])
    area = 0.5 * np.abs(
        x[0] * (y[1] - y[2]) + x[1] * (y[2] - y[0]) + x[2] * (y[0] - y[1])
    )
    
    # Estimate average Gaussian curvature in the triangle
    x_center = (p1[0] + p2[0] + p3[0]) / 3.0
    y_center = (p1[1] + p2[1] + p3[1]) / 3.0
    K_avg = gaussian_curvature(x_center, y_center)
    
    # By Gauss-Bonnet theorem, angle sum = π + ∫∫ K dA
    return np.pi + K_avg * area