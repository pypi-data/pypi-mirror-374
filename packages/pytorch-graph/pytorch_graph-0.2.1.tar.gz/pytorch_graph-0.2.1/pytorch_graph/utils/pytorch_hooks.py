"""
PyTorch-specific utilities for hooks and activation extraction.
"""

from typing import Dict, List, Optional, Any, Callable
import torch
import torch.nn as nn
from collections import defaultdict


class HookManager:
    """
    Manages PyTorch hooks for model analysis and visualization.
    """
    
    def __init__(self):
        """Initialize the hook manager."""
        self.hooks = []
        self.activations = {}
        self.gradients = {}
        
    def register_forward_hook(self, module: nn.Module, name: str, 
                            hook_fn: Optional[Callable] = None):
        """
        Register a forward hook on a module.
        
        Args:
            module: PyTorch module
            name: Name identifier for the hook
            hook_fn: Custom hook function, if None uses default
        """
        if hook_fn is None:
            hook_fn = self._default_forward_hook(name)
        
        hook = module.register_forward_hook(hook_fn)
        self.hooks.append(hook)
        return hook
    
    def register_backward_hook(self, module: nn.Module, name: str,
                             hook_fn: Optional[Callable] = None):
        """
        Register a backward hook on a module.
        
        Args:
            module: PyTorch module
            name: Name identifier for the hook
            hook_fn: Custom hook function, if None uses default
        """
        if hook_fn is None:
            hook_fn = self._default_backward_hook(name)
        
        hook = module.register_backward_hook(hook_fn)
        self.hooks.append(hook)
        return hook
    
    def _default_forward_hook(self, name: str):
        """Default forward hook that stores activations."""
        def hook(module, input, output):
            self.activations[name] = {
                'input': input,
                'output': output,
                'module': module
            }
        return hook
    
    def _default_backward_hook(self, name: str):
        """Default backward hook that stores gradients."""
        def hook(module, grad_input, grad_output):
            self.gradients[name] = {
                'grad_input': grad_input,
                'grad_output': grad_output,
                'module': module
            }
        return hook
    
    def remove_all_hooks(self):
        """Remove all registered hooks."""
        for hook in self.hooks:
            hook.remove()
        self.hooks.clear()
    
    def get_activations(self) -> Dict[str, Any]:
        """Get all stored activations."""
        return self.activations.copy()
    
    def get_gradients(self) -> Dict[str, Any]:
        """Get all stored gradients."""
        return self.gradients.copy()
    
    def clear_data(self):
        """Clear stored activations and gradients."""
        self.activations.clear()
        self.gradients.clear()


class ActivationExtractor:
    """
    Extracts intermediate activations from PyTorch models.
    """
    
    def __init__(self, model: nn.Module):
        """
        Initialize the activation extractor.
        
        Args:
            model: PyTorch model
        """
        self.model = model
        self.hook_manager = HookManager()
        self.layer_names = []
        
        # Get all layer names
        for name, module in model.named_modules():
            if len(list(module.children())) == 0:  # Leaf modules
                self.layer_names.append(name)
    
    def extract(self, input_tensor: torch.Tensor, 
               layer_names: Optional[List[str]] = None) -> Dict[str, torch.Tensor]:
        """
        Extract activations from specified layers.
        
        Args:
            input_tensor: Input tensor for forward pass
            layer_names: Specific layers to extract (if None, extracts all)
            
        Returns:
            Dictionary mapping layer names to activation tensors
        """
        if layer_names is None:
            layer_names = self.layer_names
        
        # Register hooks for specified layers
        modules_dict = dict(self.model.named_modules())
        
        for name in layer_names:
            if name in modules_dict:
                self.hook_manager.register_forward_hook(modules_dict[name], name)
        
        # Forward pass
        self.model.eval()
        with torch.no_grad():
            _ = self.model(input_tensor)
        
        # Extract activations
        activations = {}
        stored_activations = self.hook_manager.get_activations()
        
        for name in layer_names:
            if name in stored_activations:
                output = stored_activations[name]['output']
                if isinstance(output, torch.Tensor):
                    activations[name] = output.clone()
                elif isinstance(output, (list, tuple)):
                    activations[name] = [t.clone() if isinstance(t, torch.Tensor) else t for t in output]
        
        # Clean up
        self.hook_manager.remove_all_hooks()
        self.hook_manager.clear_data()
        
        return activations
    
    def extract_with_gradients(self, input_tensor: torch.Tensor,
                              layer_names: Optional[List[str]] = None) -> Dict[str, Dict[str, torch.Tensor]]:
        """
        Extract both activations and gradients from specified layers.
        
        Args:
            input_tensor: Input tensor for forward pass
            layer_names: Specific layers to extract (if None, extracts all)
            
        Returns:
            Dictionary with 'activations' and 'gradients' keys
        """
        if layer_names is None:
            layer_names = self.layer_names
        
        # Ensure input requires grad
        input_tensor = input_tensor.requires_grad_(True)
        
        # Register hooks for specified layers
        modules_dict = dict(self.model.named_modules())
        
        for name in layer_names:
            if name in modules_dict:
                self.hook_manager.register_forward_hook(modules_dict[name], name)
                self.hook_manager.register_backward_hook(modules_dict[name], name)
        
        # Forward pass
        self.model.train()  # Need training mode for gradients
        output = self.model(input_tensor)
        
        # Backward pass (assuming scalar loss for simplicity)
        if output.numel() > 1:
            loss = output.sum()
        else:
            loss = output
        loss.backward()
        
        # Extract data
        activations = {}
        gradients = {}
        
        stored_activations = self.hook_manager.get_activations()
        stored_gradients = self.hook_manager.get_gradients()
        
        for name in layer_names:
            if name in stored_activations:
                output = stored_activations[name]['output']
                if isinstance(output, torch.Tensor):
                    activations[name] = output.clone()
            
            if name in stored_gradients:
                grad_output = stored_gradients[name]['grad_output']
                if grad_output and len(grad_output) > 0:
                    if isinstance(grad_output[0], torch.Tensor):
                        gradients[name] = grad_output[0].clone()
        
        # Clean up
        self.hook_manager.remove_all_hooks()
        self.hook_manager.clear_data()
        
        return {
            'activations': activations,
            'gradients': gradients
        }


class FeatureMapExtractor:
    """
    Specialized extractor for convolutional feature maps.
    """
    
    def __init__(self, model: nn.Module):
        """
        Initialize the feature map extractor.
        
        Args:
            model: PyTorch model
        """
        self.model = model
        self.conv_layers = []
        
        # Find all convolutional layers
        for name, module in model.named_modules():
            if isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
                self.conv_layers.append(name)
    
    def extract_feature_maps(self, input_tensor: torch.Tensor,
                           layer_names: Optional[List[str]] = None) -> Dict[str, torch.Tensor]:
        """
        Extract feature maps from convolutional layers.
        
        Args:
            input_tensor: Input tensor
            layer_names: Specific conv layers (if None, uses all conv layers)
            
        Returns:
            Dictionary of layer names to feature map tensors
        """
        if layer_names is None:
            layer_names = self.conv_layers
        
        extractor = ActivationExtractor(self.model)
        activations = extractor.extract(input_tensor, layer_names)
        
        return activations
    
    def visualize_feature_maps(self, feature_maps: Dict[str, torch.Tensor],
                             max_channels: int = 16) -> Dict[str, torch.Tensor]:
        """
        Prepare feature maps for visualization.
        
        Args:
            feature_maps: Dictionary of feature maps
            max_channels: Maximum number of channels to visualize per layer
            
        Returns:
            Processed feature maps ready for visualization
        """
        processed_maps = {}
        
        for layer_name, feature_map in feature_maps.items():
            if len(feature_map.shape) >= 3:  # Has channel dimension
                # Take only first batch item
                if len(feature_map.shape) == 4:  # Conv2D: (B, C, H, W)
                    fm = feature_map[0]  # (C, H, W)
                elif len(feature_map.shape) == 3:  # Conv1D: (B, C, L)
                    fm = feature_map[0]  # (C, L)
                else:
                    fm = feature_map
                
                # Limit number of channels
                if fm.shape[0] > max_channels:
                    fm = fm[:max_channels]
                
                # Normalize to [0, 1]
                fm_min = fm.min()
                fm_max = fm.max()
                if fm_max > fm_min:
                    fm = (fm - fm_min) / (fm_max - fm_min)
                
                processed_maps[layer_name] = fm
        
        return processed_maps


class GradCAMExtractor:
    """
    Extracts Grad-CAM visualizations for CNN models.
    """
    
    def __init__(self, model: nn.Module, target_layer: str):
        """
        Initialize Grad-CAM extractor.
        
        Args:
            model: PyTorch CNN model
            target_layer: Name of the target layer for Grad-CAM
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self._register_hooks()
    
    def _register_hooks(self):
        """Register hooks for Grad-CAM."""
        modules_dict = dict(self.model.named_modules())
        
        if self.target_layer not in modules_dict:
            raise ValueError(f"Layer '{self.target_layer}' not found in model")
        
        target_module = modules_dict[self.target_layer]
        
        def forward_hook(module, input, output):
            self.activations = output
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]
        
        target_module.register_forward_hook(forward_hook)
        target_module.register_backward_hook(backward_hook)
    
    def generate_cam(self, input_tensor: torch.Tensor, class_idx: Optional[int] = None) -> torch.Tensor:
        """
        Generate Grad-CAM heatmap.
        
        Args:
            input_tensor: Input tensor
            class_idx: Target class index (if None, uses predicted class)
            
        Returns:
            Grad-CAM heatmap tensor
        """
        # Forward pass
        self.model.eval()
        output = self.model(input_tensor.requires_grad_(True))
        
        # Get target class
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()
        
        # Backward pass
        self.model.zero_grad()
        class_score = output[0, class_idx]
        class_score.backward()
        
        # Generate Grad-CAM
        gradients = self.gradients[0]  # Remove batch dimension
        activations = self.activations[0]  # Remove batch dimension
        
        # Global average pooling on gradients
        weights = torch.mean(gradients, dim=(1, 2), keepdim=True)
        
        # Weighted combination of activation maps
        cam = torch.sum(weights * activations, dim=0)
        
        # ReLU to keep only positive influences
        cam = torch.relu(cam)
        
        # Normalize
        if cam.max() > 0:
            cam = cam / cam.max()
        
        return cam


class LayerWiseAnalyzer:
    """
    Analyzes PyTorch models layer by layer.
    """
    
    def __init__(self, model: nn.Module):
        """
        Initialize the layer-wise analyzer.
        
        Args:
            model: PyTorch model
        """
        self.model = model
    
    def analyze_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze parameters for each layer.
        
        Returns:
            Dictionary with parameter analysis for each layer
        """
        analysis = {}
        
        for name, module in self.model.named_modules():
            if len(list(module.children())) == 0:  # Leaf modules
                layer_analysis = {
                    'total_params': sum(p.numel() for p in module.parameters()),
                    'trainable_params': sum(p.numel() for p in module.parameters() if p.requires_grad),
                    'module_type': type(module).__name__,
                }
                
                # Parameter statistics
                if hasattr(module, 'weight') and module.weight is not None:
                    weight = module.weight.data
                    layer_analysis.update({
                        'weight_mean': weight.mean().item(),
                        'weight_std': weight.std().item(),
                        'weight_min': weight.min().item(),
                        'weight_max': weight.max().item(),
                        'weight_shape': tuple(weight.shape),
                    })
                
                if hasattr(module, 'bias') and module.bias is not None:
                    bias = module.bias.data
                    layer_analysis.update({
                        'bias_mean': bias.mean().item(),
                        'bias_std': bias.std().item(),
                        'bias_min': bias.min().item(),
                        'bias_max': bias.max().item(),
                        'bias_shape': tuple(bias.shape),
                    })
                
                analysis[name] = layer_analysis
        
        return analysis
    
    def analyze_computational_cost(self, input_shape: tuple) -> Dict[str, Dict[str, Any]]:
        """
        Analyze computational cost for each layer.
        
        Args:
            input_shape: Input tensor shape
            
        Returns:
            Dictionary with computational analysis for each layer
        """
        # This is a simplified analysis - for production use, 
        # consider using tools like ptflops or thop
        analysis = {}
        
        for name, module in self.model.named_modules():
            if len(list(module.children())) == 0:  # Leaf modules
                layer_analysis = {'module_type': type(module).__name__}
                
                if isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
                    # Rough FLOP estimation for convolution
                    if hasattr(module, 'weight'):
                        kernel_flops = torch.prod(torch.tensor(module.weight.shape))
                        layer_analysis['estimated_flops'] = kernel_flops.item()
                
                elif isinstance(module, nn.Linear):
                    # FLOP estimation for linear layer
                    layer_analysis['estimated_flops'] = module.in_features * module.out_features
                
                analysis[name] = layer_analysis
        
        return analysis 