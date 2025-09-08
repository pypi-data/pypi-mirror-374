"""
Main PyTorch-specific visualizer that orchestrates parsing, positioning, and rendering.
"""

from typing import List, Dict, Optional, Any, Union, Tuple
import warnings
import torch
import torch.nn as nn
from .parser import PyTorchModelParser
from ..utils.layer_info import LayerInfo
from ..utils.position_calculator import PositionCalculator
from ..renderers.plotly_renderer import PlotlyRenderer
from ..utils.model_analyzer import ModelAnalyzer
from ..utils.pytorch_hooks import ActivationExtractor, FeatureMapExtractor


class PyTorchVisualizer:
    """
    Main class for visualizing PyTorch neural network architectures in 3D.
    
    This class orchestrates the entire visualization pipeline specifically for PyTorch:
    1. Parse PyTorch models with advanced hook-based analysis
    2. Calculate 3D positions for layers
    3. Render interactive visualizations
    4. Provide PyTorch-specific features like activation visualization
    """
    
    def __init__(self, renderer: str = 'plotly', layout_style: str = 'hierarchical',
                 spacing: float = 2.0, theme: str = 'plotly_dark', 
                 width: int = 1200, height: int = 800):
        """
        Initialize the PyTorch neural network visualizer.
        
        Args:
            renderer: Rendering backend ('plotly' or 'matplotlib')
            layout_style: Layout algorithm ('hierarchical', 'circular', 'spring', 'custom')
            spacing: Spacing between layers
            theme: Color theme for visualization
            width: Figure width in pixels
            height: Figure height in pixels
        """
        self.renderer_type = renderer
        self.layout_style = layout_style
        self.spacing = spacing
        self.theme = theme
        self.width = width
        self.height = height
        
        # Initialize PyTorch-specific components
        self.parser = PyTorchModelParser()
        self.position_calculator = PositionCalculator(layout_style, spacing)
        self.analyzer = ModelAnalyzer()
        
        # Initialize renderer
        if renderer == 'plotly':
            self.renderer = PlotlyRenderer(theme, width, height)
        else:
            raise ValueError(f"Unsupported renderer: {renderer}")
    
    def visualize(self, model: nn.Module, input_shape: Optional[Tuple[int, ...]] = None,
                 title: Optional[str] = None,
                 show_connections: bool = True,
                 show_labels: bool = True,
                 show_parameters: bool = False,
                 show_activations: bool = False,
                 optimize_layout: bool = True,
                 device: str = 'auto',
                 export_path: Optional[str] = None,
                 **kwargs) -> Any:
        """
        Visualize a PyTorch model.
        
        Args:
            model: PyTorch model (torch.nn.Module)
            input_shape: Input tensor shape (required for detailed analysis)
            title: Plot title
            show_connections: Whether to show connections between layers
            show_labels: Whether to show layer labels
            show_parameters: Whether to show parameter count visualization
            show_activations: Whether to include activation statistics
            optimize_layout: Whether to optimize layer positions
            device: Device for model analysis ('auto', 'cpu', 'cuda')
            export_path: Path to export the visualization (optional)
            **kwargs: Additional rendering options
            
        Returns:
            Rendered visualization object
        """
        # Validate model
        validation_warnings = self.parser.validate_model(model)
        if validation_warnings:
            for warning in validation_warnings:
                warnings.warn(warning)
        
        # Parse model with PyTorch-specific features
        layers, connections = self.parser.parse_model(model, input_shape, device)
        
        if not layers:
            raise ValueError("No layers found in the model")
        
        # Add activation information if requested
        if show_activations and input_shape is not None:
            self._add_activation_info(model, layers, input_shape, device)
        
        # Calculate positions
        positioned_layers = self.position_calculator.calculate_positions(layers, connections)
        
        # Optimize layout if requested
        if optimize_layout:
            positioned_layers = self.position_calculator.optimize_positions(
                positioned_layers, connections
            )
        
        # Generate title if not provided
        if title is None:
            total_params = sum(layer.parameters for layer in positioned_layers)
            title = f"PyTorch Model - {len(positioned_layers)} Layers, {total_params:,} Parameters"
        
        # Render visualization
        fig = self.renderer.render(
            positioned_layers,
            connections,
            title=title,
            show_connections=show_connections,
            show_labels=show_labels,
            **kwargs
        )
        
        # Add parameter visualization if requested
        if show_parameters:
            self.renderer.add_parameter_visualization(positioned_layers)
        
        # Export if path provided
        if export_path:
            if export_path.endswith('.html'):
                self.renderer.export_html(export_path)
            elif export_path.endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf')):
                format_type = export_path.split('.')[-1]
                self.renderer.export_image(export_path, format=format_type)
            else:
                warnings.warn(f"Unknown export format for {export_path}")
        
        return fig
    
    def _add_activation_info(self, model: nn.Module, layers: List[LayerInfo],
                           input_shape: Tuple[int, ...], device: str):
        """Add activation statistics to layer information."""
        try:
            if device == 'auto':
                device = next(model.parameters()).device if list(model.parameters()) else torch.device('cpu')
            elif isinstance(device, str):
                device = torch.device(device)
            
            # Extract activations
            dummy_input = torch.randn(1, *input_shape).to(device)
            extractor = ActivationExtractor(model.to(device))
            activations = extractor.extract(dummy_input)
            
            # Add activation stats to layer metadata
            for layer in layers:
                if layer.name in activations:
                    activation = activations[layer.name]
                    if isinstance(activation, torch.Tensor):
                        layer.metadata.update({
                            'activation_mean': float(activation.mean()),
                            'activation_std': float(activation.std()),
                            'activation_min': float(activation.min()),
                            'activation_max': float(activation.max()),
                            'activation_zeros': int((activation == 0).sum()),
                            'activation_sparsity': float((activation == 0).float().mean()),
                        })
        except Exception as e:
            warnings.warn(f"Failed to extract activation information: {e}")
    
    def get_model_summary(self, model: nn.Module, input_shape: Optional[Tuple[int, ...]] = None,
                         device: str = 'auto') -> Dict[str, Any]:
        """
        Get a comprehensive summary of the PyTorch model.
        
        Args:
            model: PyTorch model
            input_shape: Input tensor shape
            device: Device for analysis
            
        Returns:
            Dictionary containing model summary
        """
        return self.parser.get_model_summary(model, input_shape, device)
    
    def analyze_model(self, model: nn.Module, input_shape: Optional[Tuple[int, ...]] = None,
                     device: str = 'auto', detailed: bool = True) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of the PyTorch model.
        
        Args:
            model: PyTorch model
            input_shape: Input tensor shape
            device: Device for analysis
            detailed: Whether to include detailed analysis
            
        Returns:
            Dictionary containing comprehensive analysis
        """
        return self.analyzer.analyze(model, input_shape, detailed, device)
    
    def profile_model(self, model: nn.Module, input_shape: Tuple[int, ...],
                     device: str = 'cpu', num_runs: int = 100) -> Dict[str, Any]:
        """
        Profile PyTorch model performance.
        
        Args:
            model: PyTorch model
            input_shape: Input tensor shape
            device: Device for profiling
            num_runs: Number of timing runs
            
        Returns:
            Dictionary with profiling results
        """
        return self.analyzer.profile_model(model, input_shape, device, num_runs=num_runs)
    
    def compare_models(self, models: List[nn.Module], names: Optional[List[str]] = None,
                      input_shapes: Optional[List[Tuple[int, ...]]] = None,
                      device: str = 'auto', **kwargs) -> Any:
        """
        Compare multiple PyTorch models in a single visualization.
        
        Args:
            models: List of PyTorch models
            names: Optional list of model names
            input_shapes: Optional list of input shapes for each model
            device: Device for analysis
            **kwargs: Additional visualization options
            
        Returns:
            Rendered comparison visualization
        """
        if not models:
            raise ValueError("No models provided for comparison")
        
        if names is None:
            names = [f"Model_{i+1}" for i in range(len(models))]
        
        if input_shapes is None:
            input_shapes = [None] * len(models)
        
        # Parse all models
        all_layers = []
        all_connections = {}
        x_offset = 0
        
        for i, (model, name, input_shape) in enumerate(zip(models, names, input_shapes)):
            # Parse model
            layers, connections = self.parser.parse_model(model, input_shape, device)
            
            # Offset layers horizontally
            for layer in layers:
                layer.name = f"{name}_{layer.name}"
                layer.position = (layer.position[0] + x_offset, layer.position[1], layer.position[2])
            
            # Update connections with new names
            model_connections = {}
            for source, targets in connections.items():
                new_source = f"{name}_{source}"
                new_targets = [f"{name}_{target}" for target in targets]
                model_connections[new_source] = new_targets
            
            all_layers.extend(layers)
            all_connections.update(model_connections)
            
            # Calculate offset for next model
            max_x = max(layer.position[0] for layer in layers) if layers else 0
            x_offset = max_x + self.spacing * 3
        
        # Position all layers
        positioned_layers = self.position_calculator.calculate_positions(all_layers, all_connections)
        
        # Render comparison
        title = f"PyTorch Model Comparison: {', '.join(names)}"
        fig = self.renderer.render(
            positioned_layers,
            all_connections,
            title=title,
            **kwargs
        )
        
        return fig
    
    def visualize_feature_maps(self, model: nn.Module, input_tensor: torch.Tensor,
                              layer_names: Optional[List[str]] = None,
                              max_channels: int = 16) -> Any:
        """
        Visualize feature maps from convolutional layers.
        
        Args:
            model: PyTorch CNN model
            input_tensor: Input tensor for feature extraction
            layer_names: Specific conv layers to visualize
            max_channels: Maximum channels per layer to visualize
            
        Returns:
            Feature map visualization
        """
        extractor = FeatureMapExtractor(model)
        
        if layer_names is None:
            layer_names = extractor.conv_layers
        
        # Extract feature maps
        feature_maps = extractor.extract_feature_maps(input_tensor, layer_names)
        processed_maps = extractor.visualize_feature_maps(feature_maps, max_channels)
        
        # Create visualization (this would need additional renderer support)
        # For now, return the processed feature maps
        return processed_maps
    
    def create_training_visualization(self, model: nn.Module, input_shape: Tuple[int, ...],
                                    num_epochs: int = 1) -> List[Any]:
        """
        Create visualizations showing model changes during training.
        
        Args:
            model: PyTorch model
            input_shape: Input tensor shape
            num_epochs: Number of training epochs to simulate
            
        Returns:
            List of visualizations for each epoch
        """
        visualizations = []
        
        for epoch in range(num_epochs):
            # Create visualization for current epoch
            fig = self.visualize(
                model,
                input_shape,
                title=f"Model Architecture - Epoch {epoch + 1}",
                show_parameters=True,
                show_activations=True
            )
            visualizations.append(fig)
        
        return visualizations
    
    def export_architecture_report(self, model: nn.Module, 
                                 input_shape: Optional[Tuple[int, ...]] = None,
                                 output_path: str = "pytorch_report.html",
                                 include_profiling: bool = True):
        """
        Export a comprehensive HTML report of the PyTorch model architecture.
        
        Args:
            model: PyTorch model
            input_shape: Input tensor shape
            output_path: Path for the output HTML file
            include_profiling: Whether to include performance profiling
        """
        # Get comprehensive analysis
        analysis = self.analyze_model(model, input_shape, detailed=True)
        
        # Get profiling data if requested
        profiling_data = None
        if include_profiling and input_shape is not None:
            try:
                profiling_data = self.profile_model(model, input_shape)
            except Exception as e:
                warnings.warn(f"Profiling failed: {e}")
        
        # Create visualization
        fig = self.visualize(
            model, input_shape,
            show_parameters=True,
            show_activations=True,
            title="PyTorch Model Architecture Report"
        )
        
        # Generate comprehensive HTML report
        html_content = self._generate_html_report(analysis, profiling_data, fig)
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"PyTorch model report exported to {output_path}")
    
    def _generate_html_report(self, analysis: Dict[str, Any], 
                            profiling_data: Optional[Dict[str, Any]], fig) -> str:
        """Generate comprehensive HTML report."""
        basic_info = analysis.get('basic_info', {})
        memory_info = analysis.get('memory', {})
        architecture_info = analysis.get('architecture', {})
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PyTorch Model Architecture Report</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
                .section {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #007bff; }}
                .metric {{ margin: 10px 0; display: flex; justify-content: space-between; }}
                .metric-label {{ font-weight: 600; }}
                .metric-value {{ color: #495057; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .visualization {{ width: 100%; height: 800px; margin: 20px 0; }}
                .performance {{ background: #e8f5e8; border-left-color: #28a745; }}
                .memory {{ background: #fff3cd; border-left-color: #ffc107; }}
                .architecture {{ background: #d1ecf1; border-left-color: #17a2b8; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔥 PyTorch Model Architecture Report</h1>
                <p>Comprehensive analysis and visualization</p>
            </div>
            
            <div class="grid">
                <div class="section">
                    <h2>Model Overview</h2>
                    <div class="metric">
                        <span class="metric-label">Total Parameters:</span>
                        <span class="metric-value">{basic_info.get('total_parameters', 0):,}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Trainable Parameters:</span>
                        <span class="metric-value">{basic_info.get('trainable_parameters', 0):,}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Layers:</span>
                        <span class="metric-value">{basic_info.get('total_layers', 0)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Device:</span>
                        <span class="metric-value">{basic_info.get('device', 'Unknown')}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Mode:</span>
                        <span class="metric-value">{basic_info.get('model_mode', 'Unknown')}</span>
                    </div>
                </div>
                
                <div class="section memory">
                    <h2>Memory Usage</h2>
                    <div class="metric">
                        <span class="metric-label">Parameters Memory:</span>
                        <span class="metric-value">{memory_info.get('parameters_mb', 0):.2f} MB</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Activations Memory:</span>
                        <span class="metric-value">{memory_info.get('activations_mb', 0):.2f} MB</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Input Memory:</span>
                        <span class="metric-value">{memory_info.get('input_mb', 0):.2f} MB</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Memory:</span>
                        <span class="metric-value">{memory_info.get('total_memory_mb', 0):.2f} MB</span>
                    </div>
                </div>
            </div>
        """
        
        # Add performance section if available
        if profiling_data:
            html_content += f"""
            <div class="section performance">
                <h2>Performance Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Inference Time:</span>
                    <span class="metric-value">{profiling_data.get('mean_time_ms', 0):.2f} ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Throughput:</span>
                    <span class="metric-value">{profiling_data.get('fps', 0):.1f} FPS</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Min Time:</span>
                    <span class="metric-value">{profiling_data.get('min_time_ms', 0):.2f} ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Max Time:</span>
                    <span class="metric-value">{profiling_data.get('max_time_ms', 0):.2f} ms</span>
                </div>
            </div>
            """
        
        # Add architecture section
        html_content += f"""
            <div class="section architecture">
                <h2>Architecture Analysis</h2>
                <div class="metric">
                    <span class="metric-label">Network Depth:</span>
                    <span class="metric-value">{architecture_info.get('depth', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Conv Layers:</span>
                    <span class="metric-value">{architecture_info.get('conv_layers', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Linear Layers:</span>
                    <span class="metric-value">{architecture_info.get('linear_layers', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Norm Layers:</span>
                    <span class="metric-value">{architecture_info.get('norm_layers', 0)}</span>
                </div>
                
                <h3>Detected Patterns:</h3>
                <ul>
        """
        
        for pattern in architecture_info.get('patterns', []):
            html_content += f"<li>{pattern}</li>"
        
        html_content += """
                </ul>
            </div>
            
            <div class="section">
                <h2>3D Architecture Visualization</h2>
                <div class="visualization">
        """
        
        # Add the plotly figure
        html_content += fig.to_html(include_plotlyjs='cdn', div_id="visualization")
        
        html_content += """
                </div>
            </div>
            
            <div class="section">
                <h2>📝 Summary</h2>
                <p>This report provides a comprehensive analysis of your PyTorch model including architecture visualization, 
                memory usage, performance metrics, and structural analysis. Use this information to optimize your model 
                for better performance and efficiency.</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def set_theme(self, theme: str):
        """Set the visualization theme."""
        self.theme = theme
        if hasattr(self.renderer, 'theme'):
            self.renderer.theme = theme
    
    def set_layout_style(self, layout_style: str):
        """Set the layout style for positioning layers."""
        self.layout_style = layout_style
        self.position_calculator = PositionCalculator(layout_style, self.spacing)
    
    def set_spacing(self, spacing: float):
        """Set the spacing between layers."""
        self.spacing = spacing
        self.position_calculator.spacing = spacing 