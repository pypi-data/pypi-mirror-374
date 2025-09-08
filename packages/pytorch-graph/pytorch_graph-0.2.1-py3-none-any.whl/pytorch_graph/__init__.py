"""
PyTorch Graph - Enhanced PyTorch neural network architecture visualization with flowchart diagrams.

This package provides tools to visualize PyTorch neural networks in professional flowchart
diagrams with comprehensive layer analysis and data flow visualization.
"""

__version__ = "0.2.1"
__author__ = "PyTorch Graph Team"
__email__ = "contact@maxnicholson011@gmail.com"

import warnings

# Check if PyTorch is available
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Some functionality will be limited.")

# Always available imports (don't require PyTorch)
from .utils.layer_info import LayerInfo
from .utils.position_calculator import PositionCalculator

# Computational graph tracking (always available)
from .utils.computational_graph import (
    ComputationalGraphTracker, 
    track_computational_graph, 
    analyze_computational_graph,
    OperationType,
    GraphNode,
    GraphEdge
)

# Conditional imports that require PyTorch
if TORCH_AVAILABLE:
    try:
        from .core.visualizer import PyTorchVisualizer
        from .core.parser import PyTorchModelParser
        from .utils.pytorch_hooks import HookManager, ActivationExtractor
        from .utils.model_analyzer import ModelAnalyzer
    except ImportError as e:
        warnings.warn(f"Failed to import PyTorch-dependent modules: {e}")

# Try to import renderers (may fail if dependencies missing)
try:
    from .renderers.plotly_renderer import PlotlyRenderer
except ImportError:
    warnings.warn("Plotly renderer not available. Install plotly for 3D visualization.")
except (NameError, AttributeError):
    warnings.warn("Plotly renderer not available due to missing dependencies.")

try:
    from .renderers.plotly_renderer import MatplotlibRenderer
except ImportError:
    warnings.warn("Matplotlib renderer not available.")
except AttributeError:
    warnings.warn("Matplotlib renderer not available due to missing dependencies.")

# Try to import diagram renderer for PNG generation
try:
    from .renderers.diagram_renderer import DiagramRenderer, SimpleDiagramRenderer
except ImportError:
    warnings.warn("Diagram renderer not available. Install matplotlib for PNG diagrams.")
except (NameError, AttributeError):
    warnings.warn("Diagram renderer not available due to missing dependencies.")

# Main API functions (require PyTorch)
def visualize(model, input_shape=None, renderer='plotly', **kwargs):
    """
    Visualize a PyTorch model in 3D.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_shape: Input tensor shape (tuple), if None will try to infer
        renderer: Rendering backend ('plotly' or 'matplotlib')
        **kwargs: Additional visualization parameters
    
    Returns:
        Visualization object
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for model visualization. Install with: pip install torch")
    visualizer = PyTorchVisualizer(renderer=renderer)
    return visualizer.visualize(model, input_shape, **kwargs)

def visualize_model(model, input_shape=None, renderer='plotly', **kwargs):
    """
    Alias for visualize() function for backward compatibility.
    """
    return visualize(model, input_shape, renderer, **kwargs)

def analyze_model(model, input_shape=None, detailed=True):
    """
    Analyze a PyTorch model and return detailed statistics.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_shape: Input tensor shape (tuple)
        detailed: Whether to include detailed layer analysis
    
    Returns:
        Dictionary containing model analysis
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for model analysis. Install with: pip install torch")
    analyzer = ModelAnalyzer()
    return analyzer.analyze(model, input_shape, detailed)

def compare_models(models, names=None, input_shapes=None, renderer='plotly', **kwargs):
    """
    Compare multiple PyTorch models in a single visualization.
    
    Args:
        models: List of PyTorch models
        names: Optional list of model names
        input_shapes: Optional list of input shapes for each model
        renderer: Rendering backend ('plotly' or 'matplotlib')
        **kwargs: Additional visualization parameters
    
    Returns:
        Comparison visualization object
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for model comparison. Install with: pip install torch")
    visualizer = PyTorchVisualizer(renderer=renderer)
    return visualizer.compare_models(models, names, input_shapes, **kwargs)

def create_architecture_report(model, input_shape=None, output_path="pytorch_graph_report.html"):
    """
    Create a comprehensive HTML report of the PyTorch model architecture.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_shape: Input tensor shape (tuple)
        output_path: Path for the output HTML file
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for architecture reports. Install with: pip install torch")
    visualizer = PyTorchVisualizer()
    visualizer.export_architecture_report(model, input_shape, output_path)

# PyTorch-specific utilities
def profile_model(model, input_shape, device='cpu'):
    """
    Profile a PyTorch model for performance analysis.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_shape: Input tensor shape (tuple)
        device: Device to run profiling on ('cpu' or 'cuda')
    
    Returns:
        Profiling results dictionary
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for model profiling. Install with: pip install torch")
    analyzer = ModelAnalyzer()
    return analyzer.profile_model(model, input_shape, device)

def extract_activations(model, input_tensor, layer_names=None):
    """
    Extract intermediate activations from a PyTorch model.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_tensor: Input tensor for forward pass
        layer_names: Specific layer names to extract (if None, extracts all)
    
    Returns:
        Dictionary of layer names to activation tensors
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for activation extraction. Install with: pip install torch")
    extractor = ActivationExtractor(model)
    return extractor.extract(input_tensor, layer_names)

def generate_architecture_diagram(model, input_shape, output_path="architecture.png", 
                                title=None, format="png", style="flowchart"):
    """
    Generate an enhanced flowchart architecture diagram from a PyTorch model and save as PNG.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_shape: Input tensor shape (tuple)
        output_path: Output file path 
        title: Diagram title (auto-generated if None)
        format: Output format ('png' or 'txt')
        style: Diagram style ('flowchart', 'standard', or 'research_paper')
    
    Returns:
        Path to the generated diagram file
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for diagram generation. Install with: pip install torch")
    
    if format.lower() == "png":
        try:
            renderer = DiagramRenderer(style=style)
            return renderer.render_model_diagram(model, input_shape, title, output_path)
        except NameError:
            warnings.warn("Matplotlib not available. Falling back to text diagram.")
            format = "txt"
            if output_path.endswith(".png"):
                output_path = output_path.replace(".png", ".txt")
    
    if format.lower() == "txt":
        renderer = SimpleDiagramRenderer()
        return renderer.render_model_diagram(model, input_shape, title, output_path)
    
    raise ValueError(f"Unsupported format: {format}. Use 'png' or 'txt'.")

# Convenience alias
def save_architecture_diagram(model, input_shape, output_path="architecture.png", **kwargs):
    """
    Generate and save an enhanced flowchart architecture diagram (alias for generate_architecture_diagram).
    """
    return generate_architecture_diagram(model, input_shape, output_path, **kwargs)

def generate_research_paper_diagram(model, input_shape, output_path="model_architecture_paper.png", 
                                   title=None):
    """
    Generate a research paper quality architecture diagram.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_shape: Input tensor shape (tuple)
        output_path: Output file path
        title: Diagram title (auto-generated if None)
    
    Returns:
        Path to the generated diagram file
    """
    return generate_architecture_diagram(
        model, input_shape, output_path, title, 
        format="png", style="research_paper"
    )

def generate_flowchart_diagram(model, input_shape, output_path="model_flowchart.png", 
                              title=None):
    """
    Generate a clean flowchart-style architecture diagram with vertical flow.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_shape: Input tensor shape (tuple)
        output_path: Output file path
        title: Diagram title (auto-generated if None)
    
    Returns:
        Path to the generated diagram file
    """
    return generate_architecture_diagram(
        model, input_shape, output_path, title, 
        format="png", style="flowchart"
    )

def track_computational_graph_execution(model, input_tensor, track_memory=True, 
                                      track_timing=True, track_tensor_ops=True):
    """
    Track the computational graph of a PyTorch model execution.
    
    This function provides detailed tracking of:
    - Forward and backward passes through all layers
    - Tensor operations (add, multiply, matmul, etc.)
    - Memory usage and timing information
    - Data flow between operations
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_tensor: Input tensor for the forward pass
        track_memory: Whether to track memory usage
        track_timing: Whether to track execution timing
        track_tensor_ops: Whether to track tensor operations
        
    Returns:
        ComputationalGraphTracker with the execution data
        
    Example:
        >>> import torch
        >>> import torch.nn as nn
        >>> from torch_vis import track_computational_graph_execution
        >>> 
        >>> model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 1))
        >>> input_tensor = torch.randn(1, 10)
        >>> tracker = track_computational_graph_execution(model, input_tensor)
        >>> 
        >>> # Get summary
        >>> summary = tracker.get_graph_summary()
        >>> print(f"Total operations: {summary['total_nodes']}")
        >>> 
        >>> # Visualize the graph
        >>> fig = tracker.visualize_graph('plotly')
        >>> fig.show()
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for computational graph tracking. Install with: pip install torch")
    return track_computational_graph(model, input_tensor, track_memory, track_timing, track_tensor_ops)

def analyze_computational_graph_execution(model, input_tensor, detailed=True):
    """
    Analyze the computational graph of a PyTorch model execution.
    
    This function provides comprehensive analysis of:
    - Operation types and frequencies
    - Layer-wise execution patterns
    - Performance metrics (timing, memory)
    - Data flow analysis
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_tensor: Input tensor for the forward pass
        detailed: Whether to include detailed analysis
        
    Returns:
        Dictionary containing computational graph analysis
        
    Example:
        >>> import torch
        >>> import torch.nn as nn
        >>> from torch_vis import analyze_computational_graph_execution
        >>> 
        >>> model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 1))
        >>> input_tensor = torch.randn(1, 10)
        >>> analysis = analyze_computational_graph_execution(model, input_tensor)
        >>> 
        >>> print(f"Total operations: {analysis['summary']['total_nodes']}")
        >>> print(f"Execution time: {analysis['summary']['execution_time']:.4f}s")
        >>> print(f"Memory usage: {analysis['summary']['memory_usage']}")
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for computational graph analysis. Install with: pip install torch")
    return analyze_computational_graph(model, input_tensor, detailed)

def visualize_computational_graph(model, input_tensor, renderer='plotly'):
    """
    Visualize the computational graph of a PyTorch model execution.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_tensor: Input tensor for the forward pass
        renderer: Rendering backend ('plotly' or 'matplotlib')
        
    Returns:
        Visualization object (Plotly figure or Matplotlib figure)
        
    Example:
        >>> import torch
        >>> import torch.nn as nn
        >>> from torch_vis import visualize_computational_graph
        >>> 
        >>> model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 1))
        >>> input_tensor = torch.randn(1, 10)
        >>> fig = visualize_computational_graph(model, input_tensor, 'plotly')
        >>> fig.show()
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for computational graph visualization. Install with: pip install torch")
    
    tracker = track_computational_graph(model, input_tensor)
    return tracker.visualize_graph(renderer)

def export_computational_graph(model, input_tensor, filepath, format='json'):
    """
    Export the computational graph of a PyTorch model execution to a file.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_tensor: Input tensor for the forward pass
        filepath: Output file path
        format: Export format ('json')
        
    Returns:
        Path to the exported file
        
    Example:
        >>> import torch
        >>> import torch.nn as nn
        >>> from torch_vis import export_computational_graph
        >>> 
        >>> model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 1))
        >>> input_tensor = torch.randn(1, 10)
        >>> filepath = export_computational_graph(model, input_tensor, 'graph.json')
        >>> print(f"Graph exported to: {filepath}")
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for computational graph export. Install with: pip install torch")
    
    tracker = track_computational_graph(model, input_tensor)
    tracker.export_graph(filepath, format)
    return filepath

def save_computational_graph_png(model, input_tensor, filepath="computational_graph.png", 
                                width=1200, height=800, dpi=300, show_legend=True,
                                node_size=20, font_size=10):
    """
    Save the computational graph as a high-quality PNG image.
    
    Args:
        model: PyTorch model (torch.nn.Module)
        input_tensor: Input tensor for the forward pass
        filepath: Output PNG file path
        width: Image width in pixels
        height: Image height in pixels
        dpi: Dots per inch for high resolution
        show_legend: Whether to show legend
        node_size: Size of nodes in the graph
        font_size: Font size for labels
        
    Returns:
        Path to the saved PNG file
        
    Example:
        >>> import torch
        >>> import torch.nn as nn
        >>> from torch_vis import save_computational_graph_png
        >>> 
        >>> model = nn.Sequential(nn.Linear(10, 20), nn.ReLU(), nn.Linear(20, 1))
        >>> input_tensor = torch.randn(1, 10)
        >>> png_path = save_computational_graph_png(model, input_tensor, "graph.png")
        >>> print(f"PNG saved to: {png_path}")
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for computational graph PNG generation. Install with: pip install torch")
    
    tracker = track_computational_graph(model, input_tensor)
    return tracker.save_graph_png(filepath, width, height, dpi, show_legend, node_size, font_size)

# Public API - Build list dynamically based on available dependencies
__all__ = [
    'LayerInfo',
    'PositionCalculator',
    'visualize',
    'visualize_model', 
    'analyze_model',
    'compare_models',
    'create_architecture_report',
    'profile_model',
    'extract_activations',
    'generate_architecture_diagram',
    'save_architecture_diagram',
    'generate_research_paper_diagram',
    'generate_flowchart_diagram',
    # Computational graph functions
    'track_computational_graph_execution',
    'analyze_computational_graph_execution',
    'visualize_computational_graph',
    'export_computational_graph',
    'save_computational_graph_png',
    'ComputationalGraphTracker',
    'OperationType',
    'GraphNode',
    'GraphEdge',
]

# Add PyTorch-specific components if available
if TORCH_AVAILABLE:
    try:
        __all__.extend([
            'PyTorchVisualizer',
            'PyTorchModelParser',
            'HookManager', 
            'ActivationExtractor',
            'ModelAnalyzer',
        ])
    except NameError:
        pass  # Classes not imported due to import errors

# Add renderers if available
try:
    PlotlyRenderer
    __all__.append('PlotlyRenderer')
except NameError:
    pass

try:
    MatplotlibRenderer  
    __all__.append('MatplotlibRenderer')
except NameError:
    pass

# Add diagram renderers if available
try:
    DiagramRenderer
    __all__.extend(['DiagramRenderer', 'SimpleDiagramRenderer'])
except NameError:
    pass 