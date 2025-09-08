"""
PyTorch-specific model analyzer for comprehensive model analysis and profiling.
"""

from typing import Dict, List, Optional, Any, Tuple
import time
import warnings
import torch
import torch.nn as nn
import torch.profiler
from collections import defaultdict
import numpy as np

try:
    from torchinfo import summary
    TORCHINFO_AVAILABLE = True
except ImportError:
    TORCHINFO_AVAILABLE = False

try:
    from thop import profile, clever_format
    THOP_AVAILABLE = True
except ImportError:
    THOP_AVAILABLE = False


class ModelAnalyzer:
    """
    Comprehensive analyzer for PyTorch models with profiling and performance analysis.
    """
    
    def __init__(self):
        """Initialize the model analyzer."""
        pass
    
    def analyze(self, model: nn.Module, input_shape: Optional[Tuple[int, ...]] = None,
               detailed: bool = True, device: str = 'auto') -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a PyTorch model.
        
        Args:
            model: PyTorch model to analyze
            input_shape: Input tensor shape
            detailed: Whether to include detailed layer-wise analysis
            device: Device to run analysis on
            
        Returns:
            Dictionary containing comprehensive model analysis
        """
        if device == 'auto':
            device = next(model.parameters()).device if list(model.parameters()) else torch.device('cpu')
        elif isinstance(device, str):
            device = torch.device(device)
        
        analysis = {}
        
        # Basic model information
        analysis['basic_info'] = self._analyze_basic_info(model, device)
        
        # Parameter analysis
        analysis['parameters'] = self._analyze_parameters(model)
        
        # Memory analysis
        if input_shape is not None:
            analysis['memory'] = self._analyze_memory(model, input_shape, device)
        
        # Layer-wise analysis
        if detailed:
            analysis['layers'] = self._analyze_layers(model)
        
        # Model complexity
        if input_shape is not None:
            analysis['complexity'] = self._analyze_complexity(model, input_shape, device)
        
        # Architecture patterns
        analysis['architecture'] = self._analyze_architecture(model)
        
        return analysis
    
    def _analyze_basic_info(self, model: nn.Module, device: torch.device) -> Dict[str, Any]:
        """Analyze basic model information."""
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        # Count different types of layers
        layer_counts = defaultdict(int)
        for name, module in model.named_modules():
            if len(list(module.children())) == 0:  # Leaf modules
                layer_counts[type(module).__name__] += 1
        
        return {
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'non_trainable_parameters': total_params - trainable_params,
            'total_modules': len(list(model.named_modules())),
            'total_layers': len(list(model.named_modules())) - 1,  # Exclude root module
            'layer_types': dict(layer_counts),
            'device': str(device),
            'model_mode': 'training' if model.training else 'evaluation',
        }
    
    def _analyze_parameters(self, model: nn.Module) -> Dict[str, Any]:
        """Analyze model parameters in detail."""
        param_info = {
            'by_layer': {},
            'statistics': {},
            'distribution': {}
        }
        
        all_params = []
        
        # Analyze each layer
        for name, module in model.named_modules():
            if len(list(module.children())) == 0 and list(module.parameters()):  # Leaf modules with params
                layer_params = list(module.parameters())
                total_params = sum(p.numel() for p in layer_params)
                trainable_params = sum(p.numel() for p in layer_params if p.requires_grad)
                
                param_info['by_layer'][name] = {
                    'total_params': total_params,
                    'trainable_params': trainable_params,
                    'shapes': [tuple(p.shape) for p in layer_params],
                    'dtypes': [str(p.dtype) for p in layer_params],
                }
                
                # Collect all parameter values for statistics
                for param in layer_params:
                    all_params.extend(param.detach().cpu().numpy().flatten())
        
        # Overall parameter statistics
        if all_params:
            all_params = np.array(all_params)
            param_info['statistics'] = {
                'mean': float(np.mean(all_params)),
                'std': float(np.std(all_params)),
                'min': float(np.min(all_params)),
                'max': float(np.max(all_params)),
                'median': float(np.median(all_params)),
                'q25': float(np.percentile(all_params, 25)),
                'q75': float(np.percentile(all_params, 75)),
            }
            
            # Parameter distribution
            param_info['distribution'] = {
                'zero_params': int(np.sum(all_params == 0)),
                'positive_params': int(np.sum(all_params > 0)),
                'negative_params': int(np.sum(all_params < 0)),
                'abs_mean': float(np.mean(np.abs(all_params))),
            }
        
        return param_info
    
    def _analyze_memory(self, model: nn.Module, input_shape: Tuple[int, ...], 
                       device: torch.device) -> Dict[str, Any]:
        """Analyze memory usage of the model."""
        model = model.to(device)
        
        # Model parameters memory
        param_memory = sum(p.numel() * p.element_size() for p in model.parameters())
        
        # Estimate activation memory with forward pass
        dummy_input = torch.randn(1, *input_shape).to(device)
        
        # Hook to track activation sizes
        activation_sizes = {}
        
        def size_hook(name):
            def hook(module, input, output):
                if isinstance(output, torch.Tensor):
                    size = output.numel() * output.element_size()
                elif isinstance(output, (tuple, list)):
                    size = sum(o.numel() * o.element_size() for o in output if isinstance(o, torch.Tensor))
                else:
                    size = 0
                activation_sizes[name] = size
            return hook
        
        # Register hooks
        hooks = []
        for name, module in model.named_modules():
            if len(list(module.children())) == 0:  # Leaf modules
                hook = module.register_forward_hook(size_hook(name))
                hooks.append(hook)
        
        # Forward pass to measure activations
        model.eval()
        with torch.no_grad():
            _ = model(dummy_input)
        
        # Clean up hooks
        for hook in hooks:
            hook.remove()
        
        total_activation_memory = sum(activation_sizes.values())
        
        # Input memory
        input_memory = dummy_input.numel() * dummy_input.element_size()
        
        return {
            'parameters_bytes': param_memory,
            'parameters_mb': param_memory / (1024 * 1024),
            'activations_bytes': total_activation_memory,
            'activations_mb': total_activation_memory / (1024 * 1024),
            'input_bytes': input_memory,
            'input_mb': input_memory / (1024 * 1024),
            'total_memory_mb': (param_memory + total_activation_memory + input_memory) / (1024 * 1024),
            'activation_sizes_by_layer': {k: v / (1024 * 1024) for k, v in activation_sizes.items()},
        }
    
    def _analyze_layers(self, model: nn.Module) -> Dict[str, Any]:
        """Perform detailed layer-wise analysis."""
        layer_analysis = {}
        
        for name, module in model.named_modules():
            if len(list(module.children())) == 0:  # Leaf modules
                analysis = {
                    'type': type(module).__name__,
                    'parameters': sum(p.numel() for p in module.parameters()),
                    'trainable': sum(p.numel() for p in module.parameters() if p.requires_grad),
                }
                
                # Layer-specific analysis
                if isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
                    analysis.update({
                        'kernel_size': module.kernel_size,
                        'stride': module.stride,
                        'padding': module.padding,
                        'dilation': module.dilation,
                        'groups': module.groups,
                        'in_channels': module.in_channels,
                        'out_channels': module.out_channels,
                    })
                elif isinstance(module, nn.Linear):
                    analysis.update({
                        'in_features': module.in_features,
                        'out_features': module.out_features,
                    })
                elif isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
                    analysis.update({
                        'num_features': module.num_features,
                        'eps': module.eps,
                        'momentum': module.momentum,
                        'affine': module.affine,
                    })
                elif isinstance(module, (nn.LSTM, nn.GRU, nn.RNN)):
                    analysis.update({
                        'input_size': module.input_size,
                        'hidden_size': module.hidden_size,
                        'num_layers': module.num_layers,
                        'bidirectional': module.bidirectional,
                    })
                
                layer_analysis[name] = analysis
        
        return layer_analysis
    
    def _analyze_complexity(self, model: nn.Module, input_shape: Tuple[int, ...],
                          device: torch.device) -> Dict[str, Any]:
        """Analyze computational complexity."""
        complexity = {}
        
        # Use thop if available for FLOP counting
        if THOP_AVAILABLE:
            try:
                model = model.to(device)
                dummy_input = torch.randn(1, *input_shape).to(device)
                flops, params = profile(model, inputs=(dummy_input,), verbose=False)
                
                complexity['flops'] = flops
                complexity['flops_formatted'] = clever_format([flops], "%.3f")
                complexity['theoretical_params'] = params
            except Exception as e:
                warnings.warn(f"FLOP analysis failed: {e}")
        
        # Manual complexity estimation for common layers
        manual_flops = 0
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                manual_flops += module.in_features * module.out_features
            elif isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
                if hasattr(module, 'weight'):
                    kernel_ops = torch.prod(torch.tensor(module.weight.shape))
                    manual_flops += kernel_ops.item()
        
        complexity['estimated_flops'] = manual_flops
        
        return complexity
    
    def _analyze_architecture(self, model: nn.Module) -> Dict[str, Any]:
        """Analyze architectural patterns."""
        architecture = {
            'depth': 0,
            'width': {},
            'patterns': [],
            'skip_connections': False,
            'residual_blocks': 0,
        }
        
        # Count depth (number of sequential operations)
        sequential_count = 0
        conv_count = 0
        linear_count = 0
        norm_count = 0
        activation_count = 0
        
        for name, module in model.named_modules():
            if len(list(module.children())) == 0:  # Leaf modules
                sequential_count += 1
                
                if isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
                    conv_count += 1
                elif isinstance(module, nn.Linear):
                    linear_count += 1
                elif isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d, nn.LayerNorm)):
                    norm_count += 1
                elif isinstance(module, (nn.ReLU, nn.Sigmoid, nn.Tanh, nn.GELU, nn.LeakyReLU)):
                    activation_count += 1
        
        architecture['depth'] = sequential_count
        architecture['conv_layers'] = conv_count
        architecture['linear_layers'] = linear_count
        architecture['norm_layers'] = norm_count
        architecture['activation_layers'] = activation_count
        
        # Detect common patterns
        if conv_count > 0 and norm_count > 0:
            architecture['patterns'].append('CNN with normalization')
        if conv_count > 0 and activation_count > 0:
            architecture['patterns'].append('CNN with activations')
        if linear_count > 0 and conv_count == 0:
            architecture['patterns'].append('Fully connected network')
        if conv_count > 0 and linear_count > 0:
            architecture['patterns'].append('CNN + FC hybrid')
        
        return architecture
    
    def profile_model(self, model: nn.Module, input_shape: Tuple[int, ...],
                     device: str = 'cpu', num_warmup: int = 10, num_runs: int = 100) -> Dict[str, Any]:
        """
        Profile model performance with detailed timing analysis.
        
        Args:
            model: PyTorch model
            input_shape: Input tensor shape
            device: Device for profiling
            num_warmup: Number of warmup runs
            num_runs: Number of timing runs
            
        Returns:
            Dictionary with profiling results
        """
        if isinstance(device, str):
            device = torch.device(device)
        
        model = model.to(device)
        model.eval()
        
        dummy_input = torch.randn(1, *input_shape).to(device)
        
        # Warmup
        with torch.no_grad():
            for _ in range(num_warmup):
                _ = model(dummy_input)
        
        # Synchronize if using CUDA
        if device.type == 'cuda':
            torch.cuda.synchronize()
        
        # Timing runs
        times = []
        with torch.no_grad():
            for _ in range(num_runs):
                start_time = time.time()
                _ = model(dummy_input)
                if device.type == 'cuda':
                    torch.cuda.synchronize()
                end_time = time.time()
                times.append(end_time - start_time)
        
        times = np.array(times)
        
        profiling_results = {
            'device': str(device),
            'num_runs': num_runs,
            'mean_time_ms': float(np.mean(times) * 1000),
            'std_time_ms': float(np.std(times) * 1000),
            'min_time_ms': float(np.min(times) * 1000),
            'max_time_ms': float(np.max(times) * 1000),
            'median_time_ms': float(np.median(times) * 1000),
            'fps': float(1.0 / np.mean(times)),
            'throughput_imgs_per_sec': float(1.0 / np.mean(times)),
        }
        
        # Memory profiling for CUDA
        if device.type == 'cuda':
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            
            with torch.no_grad():
                _ = model(dummy_input)
            
            profiling_results.update({
                'peak_memory_mb': torch.cuda.max_memory_allocated() / (1024 * 1024),
                'memory_reserved_mb': torch.cuda.max_memory_reserved() / (1024 * 1024),
            })
        
        return profiling_results
    
    def compare_models(self, models: List[nn.Module], names: List[str],
                      input_shape: Tuple[int, ...], device: str = 'cpu') -> Dict[str, Any]:
        """
        Compare multiple models across various metrics.
        
        Args:
            models: List of PyTorch models
            names: List of model names
            input_shape: Input tensor shape
            device: Device for comparison
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            'models': names,
            'comparison_table': {},
            'rankings': {}
        }
        
        metrics = ['total_parameters', 'mean_time_ms', 'peak_memory_mb', 'flops']
        
        # Analyze each model
        for name, model in zip(names, models):
            analysis = self.analyze(model, input_shape, detailed=False, device=device)
            profiling = self.profile_model(model, input_shape, device, num_runs=20)
            
            comparison['comparison_table'][name] = {
                'parameters': analysis['basic_info']['total_parameters'],
                'layers': analysis['basic_info']['total_layers'],
                'memory_mb': analysis.get('memory', {}).get('total_memory_mb', 0),
                'inference_time_ms': profiling['mean_time_ms'],
                'fps': profiling['fps'],
            }
            
            if 'complexity' in analysis:
                comparison['comparison_table'][name]['flops'] = analysis['complexity'].get('flops', 0)
        
        # Create rankings
        for metric in ['parameters', 'inference_time_ms', 'memory_mb']:
            if all(metric in comparison['comparison_table'][name] for name in names):
                sorted_models = sorted(names, key=lambda x: comparison['comparison_table'][x][metric])
                comparison['rankings'][f'{metric}_ranking'] = sorted_models
        
        return comparison
    
    def suggest_optimizations(self, model: nn.Module, input_shape: Tuple[int, ...]) -> List[str]:
        """
        Suggest potential optimizations for the model.
        
        Args:
            model: PyTorch model
            input_shape: Input tensor shape
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        analysis = self.analyze(model, input_shape, detailed=True)
        
        # Parameter-based suggestions
        total_params = analysis['basic_info']['total_parameters']
        if total_params > 10_000_000:
            suggestions.append("Consider model pruning or quantization for large parameter count")
        
        # Layer-based suggestions
        layer_types = analysis['basic_info']['layer_types']
        
        if 'Linear' in layer_types and layer_types['Linear'] > 3:
            suggestions.append("Multiple Linear layers detected - consider using more efficient architectures")
        
        if 'Conv2d' in layer_types and 'BatchNorm2d' not in layer_types:
            suggestions.append("Add BatchNormalization layers after convolutions for better training stability")
        
        if layer_types.get('ReLU', 0) > layer_types.get('Conv2d', 0):
            suggestions.append("Consider using inplace=True for ReLU activations to save memory")
        
        # Memory-based suggestions
        if 'memory' in analysis:
            total_memory = analysis['memory']['total_memory_mb']
            if total_memory > 1000:  # > 1GB
                suggestions.append("High memory usage detected - consider gradient checkpointing")
        
        # Architecture-based suggestions
        arch_info = analysis['architecture']
        if arch_info['depth'] > 50:
            suggestions.append("Very deep network - consider residual connections or skip connections")
        
        if len(suggestions) == 0:
            suggestions.append("Model appears well-optimized - no obvious improvements detected")
        
        return suggestions 