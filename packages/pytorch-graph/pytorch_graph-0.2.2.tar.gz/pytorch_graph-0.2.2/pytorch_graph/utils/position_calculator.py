"""
Position calculation algorithms for 3D visualization of neural network layers.
"""

from typing import List, Dict, Tuple
import math
import warnings

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    warnings.warn("NetworkX not available. Some layout algorithms will be limited.")

from .layer_info import LayerInfo


class PositionCalculator:
    """Calculates 3D positions for neural network layers."""
    
    def __init__(self, layout_style: str = 'hierarchical', spacing: float = 2.0):
        """
        Initialize position calculator.
        
        Args:
            layout_style: Layout algorithm to use
            spacing: Base spacing between layers
        """
        self.layout_style = layout_style
        self.spacing = spacing
        
        self.layout_functions = {
            'hierarchical': self._hierarchical_layout,
            'circular': self._circular_layout,
            'spring': self._spring_layout,
            'custom': self._custom_layout
        }
    
    def calculate_positions(self, layers: List[LayerInfo], 
                          connections: Dict[str, List[str]]) -> List[LayerInfo]:
        """
        Calculate positions for all layers.
        
        Args:
            layers: List of layer information objects
            connections: Dictionary mapping layer names to their connections
            
        Returns:
            List of layers with updated positions
        """
        if self.layout_style not in self.layout_functions:
            warnings.warn(f"Unknown layout style '{self.layout_style}'. Using 'hierarchical'.")
            layout_func = self.layout_functions['hierarchical']
        else:
            layout_func = self.layout_functions[self.layout_style]
        
        return layout_func(layers, connections)
    
    def _hierarchical_layout(self, layers: List[LayerInfo], 
                           connections: Dict[str, List[str]]) -> List[LayerInfo]:
        """Arrange layers in a hierarchical top-down layout."""
        if not layers:
            return layers
        
        # Simple sequential layout for demonstration
        positioned_layers = []
        
        for i, layer in enumerate(layers):
            x = 0.0  # Center horizontally
            y = -i * self.spacing  # Stack vertically
            z = 0.0  # Flat layout
            
            layer.position = (x, y, z)
            positioned_layers.append(layer)
        
        return positioned_layers
    
    def _circular_layout(self, layers: List[LayerInfo], 
                        connections: Dict[str, List[str]]) -> List[LayerInfo]:
        """Arrange layers in a circular pattern."""
        if not layers:
            return layers
        
        positioned_layers = []
        num_layers = len(layers)
        radius = max(num_layers * 0.5, 3.0)  # Adjust radius based on number of layers
        
        for i, layer in enumerate(layers):
            angle = 2 * math.pi * i / num_layers
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = 0.0  # Flat circular layout
            
            layer.position = (x, y, z)
            positioned_layers.append(layer)
        
        return positioned_layers
    
    def _spring_layout(self, layers: List[LayerInfo], 
                      connections: Dict[str, List[str]]) -> List[LayerInfo]:
        """Use spring-based layout algorithm."""
        if not NETWORKX_AVAILABLE:
            warnings.warn("NetworkX not available. Falling back to hierarchical layout.")
            return self._hierarchical_layout(layers, connections)
        
        if not layers:
            return layers
        
        # Create networkx graph
        G = nx.DiGraph()
        
        # Add nodes
        for layer in layers:
            G.add_node(layer.name, layer_info=layer)
        
        # Add edges
        for source, targets in connections.items():
            for target in targets:
                if source in [l.name for l in layers] and target in [l.name for l in layers]:
                    G.add_edge(source, target)
        
        # Calculate spring layout
        try:
            pos_2d = nx.spring_layout(G, k=self.spacing, iterations=50)
            
            # Convert to 3D and apply to layers
            positioned_layers = []
            for layer in layers:
                if layer.name in pos_2d:
                    x, y = pos_2d[layer.name]
                    # Scale positions
                    x *= self.spacing * 5
                    y *= self.spacing * 5
                    z = 0.0  # Flat layout
                else:
                    x, y, z = 0.0, 0.0, 0.0
                
                layer.position = (x, y, z)
                positioned_layers.append(layer)
            
            return positioned_layers
            
        except Exception as e:
            warnings.warn(f"Spring layout failed: {e}. Using hierarchical layout.")
            return self._hierarchical_layout(layers, connections)
    
    def _custom_layout(self, layers: List[LayerInfo], 
                      connections: Dict[str, List[str]]) -> List[LayerInfo]:
        """Custom layout that groups similar layer types."""
        if not layers:
            return layers
        
        # Group layers by type
        layer_groups = {}
        for layer in layers:
            layer_type = layer.layer_type
            if layer_type not in layer_groups:
                layer_groups[layer_type] = []
            layer_groups[layer_type].append(layer)
        
        positioned_layers = []
        group_spacing = self.spacing * 3
        
        # Position each group
        for group_idx, (layer_type, group_layers) in enumerate(layer_groups.items()):
            group_x = group_idx * group_spacing
            
            for i, layer in enumerate(group_layers):
                x = group_x
                y = -i * self.spacing
                z = 0.0
                
                layer.position = (x, y, z)
                positioned_layers.append(layer)
        
        return positioned_layers
    
    def optimize_positions(self, layers: List[LayerInfo], 
                          connections: Dict[str, List[str]],
                          iterations: int = 50) -> List[LayerInfo]:
        """
        Optimize layer positions to minimize overlaps and improve readability.
        
        Args:
            layers: List of positioned layers
            connections: Connection information
            iterations: Number of optimization iterations
            
        Returns:
            List of layers with optimized positions
        """
        if not layers:
            return layers
        
        # Simple optimization: spread out overlapping layers
        positioned_layers = layers.copy()
        
        for iteration in range(iterations):
            improved = False
            
            for i, layer1 in enumerate(positioned_layers):
                for j, layer2 in enumerate(positioned_layers[i+1:], i+1):
                    distance = self._calculate_distance(layer1.position, layer2.position)
                    
                    if distance < self.spacing:
                        # Move layers apart
                        dx = layer2.position[0] - layer1.position[0]
                        dy = layer2.position[1] - layer1.position[1]
                        dz = layer2.position[2] - layer1.position[2]
                        
                        # Normalize direction
                        norm = max(math.sqrt(dx*dx + dy*dy + dz*dz), 0.001)
                        dx, dy, dz = dx/norm, dy/norm, dz/norm
                        
                        # Move apart
                        move_distance = (self.spacing - distance) * 0.1
                        
                        layer1.position = (
                            layer1.position[0] - dx * move_distance,
                            layer1.position[1] - dy * move_distance,
                            layer1.position[2] - dz * move_distance
                        )
                        
                        layer2.position = (
                            layer2.position[0] + dx * move_distance,
                            layer2.position[1] + dy * move_distance,
                            layer2.position[2] + dz * move_distance
                        )
                        
                        improved = True
            
            if not improved:
                break
        
        return positioned_layers
    
    def _calculate_distance(self, pos1: Tuple[float, float, float], 
                          pos2: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance between two positions."""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        dz = pos2[2] - pos1[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def get_layout_bounds(self, layers: List[LayerInfo]) -> Dict[str, Tuple[float, float]]:
        """
        Get the bounds of the layout for centering and scaling.
        
        Args:
            layers: List of positioned layers
            
        Returns:
            Dictionary with min/max bounds for each axis
        """
        if not layers:
            return {'x': (0, 0), 'y': (0, 0), 'z': (0, 0)}
        
        x_coords = [layer.position[0] for layer in layers]
        y_coords = [layer.position[1] for layer in layers]
        z_coords = [layer.position[2] for layer in layers]
        
        return {
            'x': (min(x_coords), max(x_coords)),
            'y': (min(y_coords), max(y_coords)),
            'z': (min(z_coords), max(z_coords))
        }
    
    def center_layout(self, layers: List[LayerInfo]) -> List[LayerInfo]:
        """Center the layout around the origin."""
        if not layers:
            return layers
        
        bounds = self.get_layout_bounds(layers)
        
        # Calculate center offsets
        x_center = (bounds['x'][0] + bounds['x'][1]) / 2
        y_center = (bounds['y'][0] + bounds['y'][1]) / 2
        z_center = (bounds['z'][0] + bounds['z'][1]) / 2
        
        # Apply centering
        centered_layers = []
        for layer in layers:
            new_position = (
                layer.position[0] - x_center,
                layer.position[1] - y_center,
                layer.position[2] - z_center
            )
            layer.position = new_position
            centered_layers.append(layer)
        
        return centered_layers 