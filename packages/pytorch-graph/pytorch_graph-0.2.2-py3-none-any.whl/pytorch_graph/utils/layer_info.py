"""
Layer information extraction and management for PyTorch models.
"""

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
import warnings

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Layer analysis will be limited.")


@dataclass
class LayerInfo:
    """Information about a neural network layer."""
    name: str
    layer_type: str
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    parameters: int = 0
    trainable_params: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    color: str = "#3498db"
    size: float = 1.0
    
    def get_color_by_type(self) -> str:
        """Get color based on layer type."""
        color_map = {
            # Convolutional layers - Blue variants
            'Conv1d': '#3498db',
            'Conv2d': '#2980b9', 
            'Conv3d': '#1f4e79',
            'ConvTranspose2d': '#5dade2',
            
            # Linear layers - Red variants
            'Linear': '#e74c3c',
            'LazyLinear': '#c0392b',
            'Bilinear': '#f1948a',
            
            # Activation functions - Green variants
            'ReLU': '#27ae60',
            'LeakyReLU': '#2ecc71',
            'Sigmoid': '#58d68d',
            'Tanh': '#82e5aa',
            'GELU': '#a9dfbf',
            'SiLU': '#d5f4e6',
            
            # Normalization layers - Orange variants
            'BatchNorm1d': '#f39c12',
            'BatchNorm2d': '#e67e22',
            'BatchNorm3d': '#d68910',
            'LayerNorm': '#f8c471',
            'GroupNorm': '#f7dc6f',
            
            # Pooling layers - Purple variants
            'MaxPool1d': '#8e44ad',
            'MaxPool2d': '#9b59b6',
            'MaxPool3d': '#a569bd',
            'AvgPool2d': '#bb8fce',
            'AdaptiveAvgPool2d': '#d2b4de',
            
            # Recurrent layers - Teal variants
            'LSTM': '#16a085',
            'GRU': '#48c9b0',
            'RNN': '#76d7c4',
            
            # Dropout - Gray variants
            'Dropout': '#95a5a6',
            'Dropout2d': '#bdc3c7',
            
            # Embedding - Brown variants
            'Embedding': '#a0522d',
            
            # Default
            'default': '#34495e'
        }
        return color_map.get(self.layer_type, color_map['default'])
    
    def calculate_size(self) -> float:
        """Calculate visualization size based on parameters."""
        if self.parameters == 0:
            return 0.5
        
        # Logarithmic scaling for better visualization
        import math
        base_size = 0.5
        param_factor = math.log10(max(self.parameters, 1)) / 6.0  # Normalize to ~1
        return base_size + min(param_factor * 2.0, 3.0)  # Cap at reasonable size


class LayerInfoExtractor:
    """Extracts information from PyTorch layers."""
    
    @staticmethod
    def extract_pytorch_layer_info(module, name: str, 
                                  input_shape: Tuple[int, ...], 
                                  output_shape: Tuple[int, ...]) -> LayerInfo:
        """
        Extract information from a PyTorch module.
        
        Args:
            module: PyTorch module
            name: Layer name
            input_shape: Input tensor shape
            output_shape: Output tensor shape
            
        Returns:
            LayerInfo object with extracted information
        """
        if not TORCH_AVAILABLE:
            return LayerInfo(
                name=name,
                layer_type="Unknown",
                input_shape=input_shape,
                output_shape=output_shape
            )
        
        layer_type = type(module).__name__
        
        # Count parameters
        total_params = sum(p.numel() for p in module.parameters())
        trainable_params = sum(p.numel() for p in module.parameters() if p.requires_grad)
        
        # Extract metadata
        metadata = LayerInfoExtractor._extract_layer_metadata(module)
        
        # Create layer info
        layer_info = LayerInfo(
            name=name,
            layer_type=layer_type,
            input_shape=input_shape,
            output_shape=output_shape,
            parameters=total_params,
            trainable_params=trainable_params,
            metadata=metadata
        )
        
        return layer_info
    
    @staticmethod
    def _extract_layer_metadata(module) -> Dict[str, Any]:
        """Extract metadata specific to layer type."""
        metadata = {}
        
        if not TORCH_AVAILABLE:
            return metadata
        
        # Convolutional layers
        if isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
            metadata.update({
                'in_channels': module.in_channels,
                'out_channels': module.out_channels,
                'kernel_size': module.kernel_size,
                'stride': module.stride,
                'padding': module.padding,
                'dilation': module.dilation,
                'groups': module.groups,
                'bias': module.bias is not None,
            })
        
        # Linear layers
        elif isinstance(module, nn.Linear):
            metadata.update({
                'in_features': module.in_features,
                'out_features': module.out_features,
                'bias': module.bias is not None,
            })
        
        # Recurrent layers
        elif isinstance(module, (nn.LSTM, nn.GRU, nn.RNN)):
            metadata.update({
                'input_size': module.input_size,
                'hidden_size': module.hidden_size,
                'num_layers': module.num_layers,
                'bias': module.bias,
                'batch_first': module.batch_first,
                'dropout': getattr(module, 'dropout', 0),
                'bidirectional': module.bidirectional,
            })
        
        # Normalization layers
        elif isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
            metadata.update({
                'num_features': module.num_features,
                'eps': module.eps,
                'momentum': module.momentum,
                'affine': module.affine,
                'track_running_stats': module.track_running_stats,
            })
        
        elif isinstance(module, nn.LayerNorm):
            metadata.update({
                'normalized_shape': module.normalized_shape,
                'eps': module.eps,
                'elementwise_affine': module.elementwise_affine,
            })
        
        # Pooling layers
        elif isinstance(module, (nn.MaxPool1d, nn.MaxPool2d, nn.MaxPool3d)):
            metadata.update({
                'kernel_size': module.kernel_size,
                'stride': module.stride,
                'padding': module.padding,
                'dilation': module.dilation,
                'ceil_mode': module.ceil_mode,
            })
        
        elif isinstance(module, (nn.AvgPool1d, nn.AvgPool2d, nn.AvgPool3d)):
            metadata.update({
                'kernel_size': module.kernel_size,
                'stride': module.stride,
                'padding': module.padding,
                'ceil_mode': module.ceil_mode,
                'count_include_pad': module.count_include_pad,
            })
        
        # Dropout layers
        elif isinstance(module, (nn.Dropout, nn.Dropout1d, nn.Dropout2d, nn.Dropout3d)):
            metadata.update({
                'p': module.p,
                'inplace': module.inplace,
            })
        
        # Embedding layers
        elif isinstance(module, nn.Embedding):
            metadata.update({
                'num_embeddings': module.num_embeddings,
                'embedding_dim': module.embedding_dim,
                'padding_idx': module.padding_idx,
                'max_norm': module.max_norm,
                'norm_type': module.norm_type,
                'scale_grad_by_freq': module.scale_grad_by_freq,
                'sparse': module.sparse,
            })
        
        # Activation functions (most don't have parameters)
        elif isinstance(module, nn.LeakyReLU):
            metadata.update({
                'negative_slope': module.negative_slope,
                'inplace': module.inplace,
            })
        
        elif isinstance(module, nn.ReLU):
            metadata.update({
                'inplace': module.inplace,
            })
        
        return metadata
    
    @staticmethod
    def create_dummy_layer_info(name: str, layer_type: str) -> LayerInfo:
        """Create a dummy layer info for testing purposes."""
        return LayerInfo(
            name=name,
            layer_type=layer_type,
            input_shape=(32,),
            output_shape=(64,),
            parameters=1000,
            trainable_params=1000,
            metadata={'dummy': True}
        ) 