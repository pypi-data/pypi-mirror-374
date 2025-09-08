"""
PyTorch-specific model parsing utilities for extracting layer information.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import warnings
import torch
import torch.nn as nn
from torch.fx import symbolic_trace
from ..utils.layer_info import LayerInfo, LayerInfoExtractor
from ..utils.pytorch_hooks import HookManager

try:
    from torchinfo import summary
    TORCHINFO_AVAILABLE = True
except ImportError:
    TORCHINFO_AVAILABLE = False
    warnings.warn("torchinfo not available. Enhanced model summaries will be disabled.")

try:
    from torchsummary import summary as torch_summary
    TORCHSUMMARY_AVAILABLE = True
except ImportError:
    TORCHSUMMARY_AVAILABLE = False


class PyTorchModelParser:
    """
    PyTorch-specific model parser for extracting detailed layer information.
    """
    
    def __init__(self):
        """Initialize the PyTorch model parser."""
        self.hook_manager = HookManager()
    
    def parse_model(self, model: nn.Module, 
                   input_shape: Optional[Tuple[int, ...]] = None,
                   device: str = 'auto') -> Tuple[List[LayerInfo], Dict[str, List[str]]]:
        """
        Parse a PyTorch model and extract comprehensive layer information.
        
        Args:
            model: PyTorch model (torch.nn.Module)
            input_shape: Input tensor shape (batch_size, ...)
            device: Device to run analysis on ('auto', 'cpu', 'cuda')
            
        Returns:
            Tuple of (layers, connections) where:
            - layers: List of LayerInfo objects
            - connections: Dictionary mapping layer names to their output connections
        """
        if device == 'auto':
            device = next(model.parameters()).device if list(model.parameters()) else torch.device('cpu')
        elif isinstance(device, str):
            device = torch.device(device)
        
        # Move model to specified device
        model = model.to(device)
        
        # Try different parsing methods
        if input_shape is not None:
            return self._parse_with_forward_pass(model, input_shape, device)
        else:
            return self._parse_structure_only(model)
    
    def _parse_with_forward_pass(self, model: nn.Module, input_shape: Tuple[int, ...], 
                                device: torch.device) -> Tuple[List[LayerInfo], Dict[str, List[str]]]:
        """Parse model with a forward pass to get detailed information."""
        layers = []
        connections = {}
        
        # Create dummy input
        dummy_input = torch.randn(1, *input_shape).to(device)
        
        # Set up hooks to capture layer information
        layer_outputs = {}
        layer_inputs = {}
        execution_order = []
        
        def create_hook(name):
            def hook_fn(module, input, output):
                layer_inputs[name] = input
                layer_outputs[name] = output
                execution_order.append(name)
            return hook_fn
        
        # Register hooks for all named modules
        hooks = []
        for name, module in model.named_modules():
            if len(list(module.children())) == 0:  # Only leaf modules
                hook = module.register_forward_hook(create_hook(name))
                hooks.append(hook)
        
        # Forward pass
        model.eval()
        with torch.no_grad():
            try:
                _ = model(dummy_input)
            except Exception as e:
                warnings.warn(f"Forward pass failed: {e}. Using structure-only parsing.")
                return self._parse_structure_only(model)
        
        # Clean up hooks
        for hook in hooks:
            hook.remove()
        
        # Process collected information
        prev_layer_name = None
        
        for name in execution_order:
            if name not in layer_outputs:
                continue
                
            # Get module
            module = dict(model.named_modules())[name]
            
            # Get input/output shapes
            input_tensor = layer_inputs[name][0] if isinstance(layer_inputs[name], tuple) else layer_inputs[name]
            output_tensor = layer_outputs[name]
            
            input_shape_layer = self._get_tensor_shape(input_tensor)
            output_shape_layer = self._get_tensor_shape(output_tensor)
            
            # Create layer info
            layer_info = LayerInfoExtractor.extract_pytorch_layer_info(
                module, name, input_shape_layer, output_shape_layer
            )
            
            # Enhanced PyTorch-specific metadata
            self._add_pytorch_metadata(layer_info, module, input_tensor, output_tensor)
            
            # Set color and size
            layer_info.color = layer_info.get_color_by_type()
            layer_info.size = layer_info.calculate_size()
            
            layers.append(layer_info)
            
            # Create connections (sequential for now, can be enhanced)
            if prev_layer_name is not None:
                if prev_layer_name not in connections:
                    connections[prev_layer_name] = []
                connections[prev_layer_name].append(name)
            
            prev_layer_name = name
        
        return layers, connections
    
    def _parse_structure_only(self, model: nn.Module) -> Tuple[List[LayerInfo], Dict[str, List[str]]]:
        """Parse model structure without forward pass."""
        layers = []
        connections = {}
        
        prev_layer_name = None
        
        for name, module in model.named_modules():
            if len(list(module.children())) == 0:  # Only leaf modules
                # Estimate shapes (this is approximate without forward pass)
                input_shape = self._estimate_input_shape(module)
                output_shape = self._estimate_output_shape(module, input_shape)
                
                # Create layer info
                layer_info = LayerInfoExtractor.extract_pytorch_layer_info(
                    module, name, input_shape, output_shape
                )
                
                # Add structure-only metadata
                self._add_structure_metadata(layer_info, module)
                
                layer_info.color = layer_info.get_color_by_type()
                layer_info.size = layer_info.calculate_size()
                
                layers.append(layer_info)
                
                # Simple sequential connections
                if prev_layer_name is not None:
                    if prev_layer_name not in connections:
                        connections[prev_layer_name] = []
                    connections[prev_layer_name].append(name)
                
                prev_layer_name = name
        
        return layers, connections
    
    def _get_tensor_shape(self, tensor) -> Tuple[int, ...]:
        """Extract shape from tensor, handling various tensor types."""
        if hasattr(tensor, 'shape'):
            return tuple(tensor.shape[1:])  # Remove batch dimension
        elif isinstance(tensor, (list, tuple)) and len(tensor) > 0:
            return self._get_tensor_shape(tensor[0])
        else:
            return ()
    
    def _add_pytorch_metadata(self, layer_info: LayerInfo, module: nn.Module,
                             input_tensor, output_tensor):
        """Add PyTorch-specific metadata to layer info."""
        # Device information
        if hasattr(module, 'weight') and module.weight is not None:
            layer_info.metadata['device'] = str(module.weight.device)
            layer_info.metadata['dtype'] = str(module.weight.dtype)
        
        # Memory usage
        if hasattr(input_tensor, 'element_size') and hasattr(input_tensor, 'numel'):
            layer_info.metadata['input_memory_mb'] = (
                input_tensor.element_size() * input_tensor.numel() / 1024 / 1024
            )
        
        if hasattr(output_tensor, 'element_size') and hasattr(output_tensor, 'numel'):
            layer_info.metadata['output_memory_mb'] = (
                output_tensor.element_size() * output_tensor.numel() / 1024 / 1024
            )
        
        # Module-specific information
        if isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
            layer_info.metadata.update({
                'kernel_size': module.kernel_size,
                'stride': module.stride,
                'padding': module.padding,
                'dilation': module.dilation,
                'groups': module.groups,
                'bias': module.bias is not None,
            })
        elif isinstance(module, nn.Linear):
            layer_info.metadata.update({
                'in_features': module.in_features,
                'out_features': module.out_features,
                'bias': module.bias is not None,
            })
        elif isinstance(module, (nn.LSTM, nn.GRU, nn.RNN)):
            layer_info.metadata.update({
                'input_size': module.input_size,
                'hidden_size': module.hidden_size,
                'num_layers': module.num_layers,
                'bias': module.bias,
                'batch_first': module.batch_first,
                'dropout': module.dropout,
                'bidirectional': module.bidirectional,
            })
        elif isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
            layer_info.metadata.update({
                'num_features': module.num_features,
                'eps': module.eps,
                'momentum': module.momentum,
                'affine': module.affine,
                'track_running_stats': module.track_running_stats,
            })
    
    def _add_structure_metadata(self, layer_info: LayerInfo, module: nn.Module):
        """Add metadata when only structure is available."""
        layer_info.metadata['analysis_type'] = 'structure_only'
        
        # Add basic module information
        if hasattr(module, 'weight') and module.weight is not None:
            layer_info.metadata['weight_shape'] = tuple(module.weight.shape)
            layer_info.metadata['device'] = str(module.weight.device)
            layer_info.metadata['dtype'] = str(module.weight.dtype)
    
    def _estimate_input_shape(self, module: nn.Module) -> Tuple[int, ...]:
        """Estimate input shape for a module (rough approximation)."""
        if isinstance(module, nn.Linear):
            return (module.in_features,)
        elif isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
            # Hard to estimate without knowing the input
            return ()
        else:
            return ()
    
    def _estimate_output_shape(self, module: nn.Module, input_shape: Tuple[int, ...]) -> Tuple[int, ...]:
        """Estimate output shape for a module."""
        if isinstance(module, nn.Linear):
            return (module.out_features,)
        elif isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
            # Simplified estimation
            return ()
        else:
            return input_shape
    
    def get_model_summary(self, model: nn.Module, input_shape: Optional[Tuple[int, ...]] = None,
                         device: str = 'auto') -> Dict[str, Any]:
        """
        Get a comprehensive summary of the PyTorch model.
        
        Args:
            model: PyTorch model
            input_shape: Input tensor shape
            device: Device for analysis
            
        Returns:
            Dictionary containing model summary information
        """
        if device == 'auto':
            device = next(model.parameters()).device if list(model.parameters()) else torch.device('cpu')
        elif isinstance(device, str):
            device = torch.device(device)
        
        summary_info = {}
        
        # Basic model information
        layers, connections = self.parse_model(model, input_shape, device)
        
        total_params = sum(layer.parameters for layer in layers)
        trainable_params = sum(layer.trainable_params for layer in layers)
        
        layer_types = {}
        for layer in layers:
            layer_type = layer.layer_type
            if layer_type not in layer_types:
                layer_types[layer_type] = 0
            layer_types[layer_type] += 1
        
        summary_info.update({
            'total_layers': len(layers),
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'non_trainable_parameters': total_params - trainable_params,
            'layer_types': layer_types,
            'input_shape': layers[0].input_shape if layers else None,
            'output_shape': layers[-1].output_shape if layers else None,
            'connections_count': sum(len(targets) for targets in connections.values()),
            'device': str(device),
        })
        
        # Enhanced PyTorch summary using torchinfo if available
        if TORCHINFO_AVAILABLE and input_shape is not None:
            try:
                torchinfo_summary = summary(
                    model, 
                    input_size=(1,) + input_shape,
                    device=device,
                    verbose=0
                )
                summary_info['torchinfo_summary'] = str(torchinfo_summary)
                summary_info['model_size_mb'] = torchinfo_summary.total_params * 4 / 1024 / 1024  # Rough estimate
            except Exception as e:
                warnings.warn(f"torchinfo summary failed: {e}")
        
        # Memory estimation
        if input_shape is not None:
            input_size_mb = torch.prod(torch.tensor(input_shape)).item() * 4 / 1024 / 1024
            summary_info['estimated_input_memory_mb'] = input_size_mb
        
        return summary_info
    
    def analyze_graph_structure(self, model: nn.Module) -> Dict[str, Any]:
        """
        Analyze the computational graph structure of the model.
        
        Args:
            model: PyTorch model
            
        Returns:
            Dictionary containing graph analysis
        """
        try:
            # Try to use FX tracing for graph analysis
            traced = symbolic_trace(model)
            
            graph_info = {
                'fx_traceable': True,
                'node_count': len(traced.graph.nodes),
                'node_types': {}
            }
            
            for node in traced.graph.nodes:
                node_type = node.op
                if node_type not in graph_info['node_types']:
                    graph_info['node_types'][node_type] = 0
                graph_info['node_types'][node_type] += 1
            
            return graph_info
            
        except Exception as e:
            return {
                'fx_traceable': False,
                'error': str(e),
                'fallback_analysis': True
            }
    
    def validate_model(self, model: nn.Module) -> List[str]:
        """
        Validate if the PyTorch model can be parsed and visualized.
        
        Args:
            model: PyTorch model
            
        Returns:
            List of validation warnings/errors
        """
        warnings_list = []
        
        try:
            if not isinstance(model, nn.Module):
                warnings_list.append("Model is not a PyTorch nn.Module")
                return warnings_list
            
            # Check if model has parameters
            param_count = sum(p.numel() for p in model.parameters())
            if param_count == 0:
                warnings_list.append("Model has no parameters")
            
            # Check for named modules
            module_count = len(list(model.named_modules()))
            if module_count <= 1:  # Only the model itself
                warnings_list.append("Model has no child modules")
            
            # Check device consistency
            devices = {p.device for p in model.parameters()}
            if len(devices) > 1:
                warnings_list.append(f"Model parameters are on multiple devices: {devices}")
            
            # Check for training mode
            if model.training:
                warnings_list.append("Model is in training mode. Consider using model.eval() for visualization.")
            
        except Exception as e:
            warnings_list.append(f"Error during model validation: {str(e)}")
        
        return warnings_list 