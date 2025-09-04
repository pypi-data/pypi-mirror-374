"""
Slicer implementation for 3D printing toolpath optimization.
"""

from dataclasses import dataclass
from enum import Enum

import numpy as np


class OptimizationMethod(Enum):
    """Optimization methods for TSP path finding."""
    NEAREST_NEIGHBOR = "nearest_neighbor"
    TWO_OPT = "two_opt"
    GENETIC = "genetic"
    ADAPTIVE = "adaptive"  # Automatically selects best method based on problem size


@dataclass
class SliceConfig:
    """Configuration for 3D model slicing."""
    layer_height: float = 0.2  # mm
    wall_thickness: float = 0.8  # mm
    infill_density: float = 0.2  # 0.0-1.0
    optimization_method: OptimizationMethod = OptimizationMethod.ADAPTIVE
    max_optimization_time: float = 10.0  # seconds
    include_bridges: bool = True
    adaptive_layer_height: bool = False
    min_layer_height: float = 0.1  # mm
    max_layer_height: float = 0.3  # mm


class Slicer:
    """
    Slicer for 3D models with TSP path optimization.
    
    This class takes a 3D model and produces optimized toolpaths for 3D printing.
    """
    
    def __init__(self, config: SliceConfig | None = None):
        """
        Initialize a slicer with configuration.
        
        Args:
            config: Slicer configuration, or None for defaults
        """
        self.config = config or SliceConfig()
        self.mesh = None
        self.layers = []
    
    def load_mesh(self, filepath: str) -> bool:
        """
        Load a 3D mesh from file.
        
        Args:
            filepath: Path to mesh file (STL, OBJ, 3MF, etc.)
            
        Returns:
            Success status
        """
        # Simplified implementation - in a real implementation, 
        # this would use a proper 3D mesh library
        print(f"Loading mesh from {filepath}")
        
        # Placeholder for mesh data
        self.mesh = {
            "filepath": filepath,
            "vertices": [],
            "faces": [],
            "bounds": (
                (0.0, 0.0, 0.0),  # min x,y,z
                (100.0, 100.0, 50.0)  # max x,y,z
            )
        }
        
        return True
    
    def generate_slices(self) -> int:
        """
        Generate horizontal slices of the loaded mesh.
        
        Returns:
            Number of slices generated
        """
        if self.mesh is None:
            raise ValueError("No mesh loaded. Call load_mesh() first.")
        
        # Clear existing layers
        self.layers = []
        
        # Get mesh bounds
        (min_x, min_y, min_z), (max_x, max_y, max_z) = self.mesh["bounds"]
        height = max_z - min_z
        
        # Calculate number of layers
        layer_height = self.config.layer_height
        num_layers = int(height / layer_height) + 1
        
        # Generate slices (simplified for this example)
        for i in range(num_layers):
            z = min_z + i * layer_height
            
            # Placeholder for a slice - in a real implementation,
            # this would calculate the intersection of a plane with the mesh
            layer = {
                "z": z,
                "contours": self._generate_demo_contours(z),
                "paths": []
            }
            
            self.layers.append(layer)
        
        return len(self.layers)
    
    def _generate_demo_contours(self, z: float) -> list[np.ndarray]:
        """Generate demo contours for visualization purposes."""
        # This is just a simplified example - in a real implementation,
        # contours would be calculated from mesh-plane intersection
        
        # Simple shape that changes with height
        radius = 20.0 + 10.0 * np.sin(z / 5.0)
        center_x, center_y = 50.0, 50.0
        
        # Generate a circle
        theta = np.linspace(0, 2 * np.pi, 100)
        x = center_x + radius * np.cos(theta)
        y = center_y + radius * np.sin(theta)
        
        # Create a contour as an array of (x, y) points
        contour = np.column_stack((x, y))
        
        # Add a second smaller circle inside the first one
        inner_radius = radius * 0.7
        x_inner = center_x + inner_radius * np.cos(theta)
        y_inner = center_y + inner_radius * np.sin(theta)
        inner_contour = np.column_stack((x_inner, y_inner))
        
        return [contour, inner_contour]
    
    def optimize_paths(self) -> int:
        """
        Optimize toolpaths for all layers.
        
        Returns:
            Total number of path segments after optimization
        """
        if not self.layers:
            raise ValueError("No slices generated. Call generate_slices() first.")
        
        total_segments = 0
        
        # Choose optimization method
        method = self.config.optimization_method
        if method == OptimizationMethod.ADAPTIVE:
            # For demo purposes, choose based on simple heuristic
            num_contours = sum(len(layer["contours"]) for layer in self.layers)
            if num_contours > 100:
                method = OptimizationMethod.NEAREST_NEIGHBOR
            else:
                method = OptimizationMethod.TWO_OPT
        
        print(f"Using optimization method: {method.value}")
        
        # Process each layer
        for layer in self.layers:
            contours = layer["contours"]
            
            # Extract all points that need to be visited
            all_points = []
            for contour in contours:
                # Take a subset of points from each contour for path planning
                # (in a real implementation, we'd use more sophisticated sampling)
                step = max(1, len(contour) // 10)  # Take ~10 points per contour
                sampled_points = contour[::step]
                all_points.extend(sampled_points)
            
            all_points = np.array(all_points)
            
            # Optimize the path through these points
            if method == OptimizationMethod.NEAREST_NEIGHBOR:
                path = self._nearest_neighbor_tsp(all_points)
            elif method == OptimizationMethod.TWO_OPT:
                path = self._two_opt_tsp(all_points)
            else:  # Fallback to nearest neighbor
                path = self._nearest_neighbor_tsp(all_points)
            
            # Store the optimized path
            layer["paths"] = path
            total_segments += len(path) - 1
        
        return total_segments
    
    def _nearest_neighbor_tsp(self, points: np.ndarray) -> np.ndarray:
        """
        Solve TSP using nearest neighbor heuristic.
        
        Args:
            points: Array of points, shape (n, 2)
            
        Returns:
            Ordered array of points for the path
        """
        n = len(points)
        if n <= 1:
            return points
        
        # Start from the first point
        path = [0]
        unvisited = set(range(1, n))
        
        # Construct path by always visiting the nearest unvisited point
        current = 0
        while unvisited:
            current_point = points[current]
            nearest_idx = None
            nearest_dist = float('inf')
            
            for idx in unvisited:
                dist = np.sum((current_point - points[idx]) ** 2)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_idx = idx
            
            path.append(nearest_idx)
            unvisited.remove(nearest_idx)
            current = nearest_idx
        
        # Return the actual points in the path order
        return points[path]
    
    def _two_opt_tsp(self, points: np.ndarray) -> np.ndarray:
        """
        Solve TSP using 2-opt local search heuristic.
        
        Args:
            points: Array of points, shape (n, 2)
            
        Returns:
            Ordered array of points for the path
        """
        # First get a greedy solution using nearest neighbor
        path_indices = list(range(len(points)))
        
        # Simple 2-opt implementation
        improved = True
        iteration = 0
        max_iterations = 100  # Limit iterations for demo
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for i in range(1, len(path_indices) - 1):
                for j in range(i + 1, len(path_indices)):
                    # Skip adjacent edges
                    if j - i == 1:
                        continue
                    
                    # Calculate current distance
                    current_distance = (
                        np.sum((points[path_indices[i-1]] - points[path_indices[i]]) ** 2) +
                        np.sum((points[path_indices[j-1]] - points[path_indices[j]]) ** 2)
                    )
                    
                    # Calculate new distance if we swap
                    new_distance = (
                        np.sum((points[path_indices[i-1]] - points[path_indices[j-1]]) ** 2) +
                        np.sum((points[path_indices[i]] - points[path_indices[j]]) ** 2)
                    )
                    
                    # If new distance is shorter, swap
                    if new_distance < current_distance:
                        path_indices[i:j] = reversed(path_indices[i:j])
                        improved = True
                        break
                
                if improved:
                    break
        
        # Return the actual points in the path order
        return points[path_indices]
    
    def export_gcode(self, filepath: str) -> bool:
        """
        Export optimized toolpaths as G-code.
        
        Args:
            filepath: Output filepath for G-code
            
        Returns:
            Success status
        """
        if not self.layers:
            raise ValueError("No paths optimized. Call optimize_paths() first.")
        
        try:
            with open(filepath, 'w') as f:
                # Write G-code header
                f.write("; Generated by Adaptive Dynamics Toolkit TSP Slicer\n")
                f.write(f"; Layer height: {self.config.layer_height}mm\n")
                f.write(f"; Wall thickness: {self.config.wall_thickness}mm\n")
                f.write(f"; Infill density: {int(self.config.infill_density * 100)}%\n")
                f.write("\n")
                f.write("M104 S210 ; set extruder temp\n")
                f.write("M140 S60 ; set bed temp\n")
                f.write("G28 ; home all axes\n")
                f.write("G1 Z5 F5000 ; lift nozzle\n")
                f.write("\n")
                
                # Iterate through layers and write G-code
                for i, layer in enumerate(self.layers):
                    z = layer["z"]
                    paths = layer["paths"]
                    
                    f.write(f"; Layer {i}, Z = {z:.3f}\n")
                    f.write(f"G1 Z{z:.3f} F600\n")
                    
                    # Write paths
                    if len(paths) > 0:
                        # Move to first point without extrusion
                        f.write(f"G0 X{paths[0][0]:.3f} Y{paths[0][1]:.3f} F3000\n")
                        
                        # Set extrusion parameters (simplified)
                        e_multiplier = 0.033  # Placeholder extrusion multiplier
                        e_pos = 0.0
                        
                        # Write path points with extrusion
                        for j in range(1, len(paths)):
                            x, y = paths[j]
                            prev_x, prev_y = paths[j-1]
                            
                            # Calculate extrusion amount based on distance
                            dist = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                            e_pos += dist * e_multiplier
                            
                            # Write G-code line
                            f.write(f"G1 X{x:.3f} Y{y:.3f} E{e_pos:.5f} F1800\n")
                    
                    # Small retraction at end of layer
                    f.write("G1 E-0.5 F1800\n\n")
                
                # Write G-code footer
                f.write("; End G-code\n")
                f.write("M104 S0 ; turn off extruder\n")
                f.write("M140 S0 ; turn off bed\n")
                f.write("G1 X0 Y220 F3000 ; move to front\n")
                f.write("M84 ; disable motors\n")
            
            print(f"G-code exported to {filepath}")
            return True
            
        except Exception as e:
            print(f"Error exporting G-code: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """
        Get statistics about the sliced model.
        
        Returns:
            Dictionary with statistics
        """
        if not self.layers:
            raise ValueError("No slices generated. Call generate_slices() first.")
        
        # Calculate some basic statistics
        num_layers = len(self.layers)
        total_path_length = 0.0
        total_path_segments = 0
        
        for layer in self.layers:
            paths = layer.get("paths", [])
            if len(paths) > 1:
                # Calculate path length
                for i in range(1, len(paths)):
                    dx = paths[i][0] - paths[i-1][0]
                    dy = paths[i][1] - paths[i-1][1]
                    total_path_length += np.sqrt(dx**2 + dy**2)
                
                total_path_segments += len(paths) - 1
        
        # Estimate print time (very simplified)
        # Assuming an average print speed of 60 mm/s
        print_speed_mm_s = 60.0
        estimated_print_time_s = total_path_length / print_speed_mm_s
        
        # Estimate material usage (very simplified)
        # Assuming 1.75mm filament and extrusion multiplier from above
        filament_diameter_mm = 1.75
        extrusion_multiplier = 0.033
        filament_volume_mm3 = total_path_length * extrusion_multiplier * (np.pi * (filament_diameter_mm/2)**2)
        
        # Package statistics
        stats = {
            "num_layers": num_layers,
            "total_path_length_mm": total_path_length,
            "total_path_segments": total_path_segments,
            "estimated_print_time_s": estimated_print_time_s,
            "estimated_filament_volume_mm3": filament_volume_mm3,
        }
        
        return stats