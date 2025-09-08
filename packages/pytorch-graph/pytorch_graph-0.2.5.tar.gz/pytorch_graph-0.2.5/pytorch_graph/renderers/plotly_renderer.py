"""
Plotly-based 3D renderer for neural network visualization.
"""

from typing import List, Dict, Any, Optional, Tuple
import warnings

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    warnings.warn("Plotly not available. 3D visualization will be disabled.")
    # Create dummy classes for graceful fallback
    class go:
        class Figure:
            pass
        class Scatter3d:
            pass
        class Bar:
            pass

from ..utils.layer_info import LayerInfo


class PlotlyRenderer:
    """Renders neural network architectures using Plotly."""
    
    def __init__(self, theme: str = 'plotly_dark', width: int = 1200, height: int = 800):
        """
        Initialize Plotly renderer.
        
        Args:
            theme: Plotly theme to use
            width: Figure width in pixels
            height: Figure height in pixels
        """
        self.theme = theme
        self.width = width
        self.height = height
        
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly is required for 3D visualization. Install with: pip install plotly")
    
    def render(self, layers: List[LayerInfo], connections: Dict[str, List[str]],
               title: str = "Neural Network Architecture",
               show_connections: bool = True,
               show_labels: bool = True,
               **kwargs):
        """
        Render the neural network in 3D.
        
        Args:
            layers: List of layer information
            connections: Layer connections
            title: Plot title
            show_connections: Whether to show connections
            show_labels: Whether to show layer labels
            **kwargs: Additional rendering options
            
        Returns:
            Plotly figure object (or None if Plotly not available)
        """
        if not PLOTLY_AVAILABLE:
            print("Plotly not available - cannot render 3D visualization")
            return None
            
        if not layers:
            # Return empty figure
            fig = go.Figure()
            fig.update_layout(title="No layers to display")
            return fig
        
        # Create figure
        fig = go.Figure()
        
        # Add layer nodes
        self._add_layer_nodes(fig, layers, show_labels)
        
        # Add connections
        if show_connections and connections:
            self._add_connections(fig, layers, connections)
        
        # Update layout
        self._update_layout(fig, title)
        
        return fig
    
    def _add_layer_nodes(self, fig, layers: List[LayerInfo], show_labels: bool):
        """Add layer nodes to the figure."""
        # Group layers by type for legend
        layer_groups = {}
        for layer in layers:
            layer_type = layer.layer_type
            if layer_type not in layer_groups:
                layer_groups[layer_type] = []
            layer_groups[layer_type].append(layer)
        
        # Add each group as a separate trace
        for layer_type, group_layers in layer_groups.items():
            x_coords = [layer.position[0] for layer in group_layers]
            y_coords = [layer.position[1] for layer in group_layers]
            z_coords = [layer.position[2] for layer in group_layers]
            
            # Layer names for hover
            layer_names = [layer.name for layer in group_layers]
            
            # Parameter counts for hover
            param_counts = [f"{layer.parameters:,}" for layer in group_layers]
            
            # Colors and sizes
            colors = [layer.color for layer in group_layers]
            sizes = [max(layer.size * 10, 5) for layer in group_layers]  # Scale for visibility
            
            # Create hover text
            hover_texts = []
            for layer in group_layers:
                hover_text = f"<b>{layer.name}</b><br>"
                hover_text += f"Type: {layer.layer_type}<br>"
                hover_text += f"Parameters: {layer.parameters:,}<br>"
                hover_text += f"Input: {layer.input_shape}<br>"
                hover_text += f"Output: {layer.output_shape}"
                
                # Add metadata if available
                if layer.metadata:
                    hover_text += "<br><br><b>Details:</b><br>"
                    for key, value in layer.metadata.items():
                        if key not in ['dummy']:  # Skip internal flags
                            hover_text += f"{key}: {value}<br>"
                
                hover_texts.append(hover_text)
            
            # Text for labels
            text_labels = layer_names if show_labels else None
            
            # Add scatter plot
            fig.add_trace(go.Scatter3d(
                x=x_coords,
                y=y_coords,
                z=z_coords,
                mode='markers+text' if show_labels else 'markers',
                marker=dict(
                    size=sizes,
                    color=colors[0] if colors else '#3498db',  # Use first color or default
                    opacity=0.8,
                    line=dict(width=2, color='rgba(0,0,0,0.3)')
                ),
                text=text_labels,
                textposition="middle center",
                textfont=dict(size=10, color='white'),
                hovertext=hover_texts,
                hoverinfo='text',
                name=layer_type,
                showlegend=True
            ))
    
    def _add_connections(self, fig, layers: List[LayerInfo], 
                        connections: Dict[str, List[str]]):
        """Add connections between layers."""
        # Create layer position lookup
        layer_positions = {layer.name: layer.position for layer in layers}
        
        # Connection lines
        connection_x = []
        connection_y = []
        connection_z = []
        
        for source_name, target_names in connections.items():
            if source_name not in layer_positions:
                continue
                
            source_pos = layer_positions[source_name]
            
            for target_name in target_names:
                if target_name not in layer_positions:
                    continue
                
                target_pos = layer_positions[target_name]
                
                # Add line from source to target
                connection_x.extend([source_pos[0], target_pos[0], None])
                connection_y.extend([source_pos[1], target_pos[1], None])
                connection_z.extend([source_pos[2], target_pos[2], None])
        
        if connection_x:  # Only add if there are connections
            fig.add_trace(go.Scatter3d(
                x=connection_x,
                y=connection_y,
                z=connection_z,
                mode='lines',
                line=dict(
                    color='rgba(100, 100, 100, 0.6)',
                    width=3
                ),
                name='Connections',
                showlegend=True,
                hoverinfo='skip'
            ))
    
    def _update_layout(self, fig, title: str):
        """Update figure layout and styling."""
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=20),
                x=0.5
            ),
            template=self.theme,
            width=self.width,
            height=self.height,
            scene=dict(
                xaxis=dict(
                    title="X",
                    showgrid=True,
                    gridcolor='rgba(100, 100, 100, 0.3)',
                    showline=True,
                    linecolor='rgba(100, 100, 100, 0.5)'
                ),
                yaxis=dict(
                    title="Y", 
                    showgrid=True,
                    gridcolor='rgba(100, 100, 100, 0.3)',
                    showline=True,
                    linecolor='rgba(100, 100, 100, 0.5)'
                ),
                zaxis=dict(
                    title="Z",
                    showgrid=True, 
                    gridcolor='rgba(100, 100, 100, 0.3)',
                    showline=True,
                    linecolor='rgba(100, 100, 100, 0.5)'
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1)
                ),
                aspectmode='cube'
            ),
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(0,0,0,0.5)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1
            )
        )
    
    def add_parameter_visualization(self, layers: List[LayerInfo]):
        """Create a separate parameter count visualization."""
        if not PLOTLY_AVAILABLE:
            print("Plotly not available - cannot create parameter visualization")
            return None
            
        if not layers:
            return go.Figure()
        
        # Sort layers by parameter count
        sorted_layers = sorted(layers, key=lambda x: x.parameters, reverse=True)
        
        layer_names = [layer.name for layer in sorted_layers]
        param_counts = [layer.parameters for layer in sorted_layers]
        colors = [layer.color for layer in sorted_layers]
        
        fig = go.Figure(data=[
            go.Bar(
                x=layer_names,
                y=param_counts,
                marker_color=colors,
                text=[f"{count:,}" for count in param_counts],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Parameters by Layer",
            xaxis_title="Layer",
            yaxis_title="Parameter Count",
            template=self.theme,
            width=self.width,
            height=400
        )
        
        return fig
    
    def export_html(self, fig, filename: str):
        """Export figure as HTML file."""
        fig.write_html(filename, include_plotlyjs='cdn')
    
    def export_image(self, fig, filename: str, format: str = 'png', 
                    scale: float = 2.0):
        """Export figure as static image."""
        try:
            fig.write_image(filename, format=format, scale=scale)
        except Exception as e:
            warnings.warn(f"Image export failed: {e}. Try installing kaleido: pip install kaleido")
    
    def create_comparison_figure(self, model_figures):
        """Create a subplot figure comparing multiple models."""
        if not PLOTLY_AVAILABLE:
            print("Plotly not available - cannot create comparison figure")
            return None
            
        num_models = len(model_figures)
        if num_models == 0:
            return go.Figure()
        
        # Calculate subplot layout
        if num_models == 1:
            rows, cols = 1, 1
        elif num_models == 2:
            rows, cols = 1, 2
        elif num_models <= 4:
            rows, cols = 2, 2
        else:
            rows = (num_models + 2) // 3
            cols = 3
        
        # Create subplots
        fig = make_subplots(
            rows=rows, cols=cols,
            specs=[[{'type': 'scatter3d'} for _ in range(cols)] for _ in range(rows)],
            subplot_titles=[name for name, _ in model_figures],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        # Add each model to its subplot
        for idx, (name, model_fig) in enumerate(model_figures):
            row = idx // cols + 1
            col = idx % cols + 1
            
            # Copy traces from model figure
            for trace in model_fig.data:
                fig.add_trace(trace, row=row, col=col)
        
        fig.update_layout(
            title="Model Architecture Comparison",
            template=self.theme,
            width=self.width * cols,
            height=self.height * rows
        )
        
        return fig


class MatplotlibRenderer:
    """Fallback matplotlib renderer (basic implementation)."""
    
    def __init__(self, **kwargs):
        """Initialize matplotlib renderer."""
        warnings.warn("Matplotlib renderer is a basic fallback. Use Plotly for full features.")
    
    def render(self, layers: List[LayerInfo], connections: Dict[str, List[str]], **kwargs):
        """Basic render method."""
        print("Matplotlib renderer - Basic text output:")
        print(f"Model has {len(layers)} layers")
        
        for i, layer in enumerate(layers):
            print(f"  {i+1}. {layer.name} ({layer.layer_type}) - {layer.parameters:,} params")
        
        print(f"Connections: {len(connections)} layer connections")
        return None 