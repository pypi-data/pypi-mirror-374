"""
🔧 Configuration & Optimization - Modular ESN Parameter Management
==================================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides a consolidated interface to all configuration and optimization
capabilities for Echo State Networks, combining multiple modular components.

Based on: Herbert Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"
"""

from ..config_modules import (
    BasicConfigurationMixin,
    OptimizationEngineMixin, 
    AutoTuningMixin,
    PerformanceAnalysisMixin,
    ESPValidationMixin
)


class ConfigurationOptimizationMixin(
    BasicConfigurationMixin,
    OptimizationEngineMixin,
    AutoTuningMixin, 
    PerformanceAnalysisMixin,
    ESPValidationMixin
):
    """
    🔧 Complete Configuration & Optimization Mixin for Echo State Networks
    
    This mixin combines all configuration and optimization capabilities from
    multiple modular components, providing the full functionality that was
    previously in the monolithic configuration_optimization.py file.
    
    🌟 Key Features:
    - Basic configuration (activation, noise, feedback, etc.)
    - Advanced optimization (spectral radius, hyperparameter grid search)
    - Automatic parameter tuning with task-specific strategies
    - Performance analysis and recommendations
    - Echo State Property validation
    
    🏗️ Modular Architecture:
    - BasicConfigurationMixin: Core parameter settings
    - OptimizationEngineMixin: Spectral radius & grid search optimization
    - AutoTuningMixin: Intelligent parameter tuning & presets
    - PerformanceAnalysisMixin: Configuration analysis & recommendations
    - ESPValidationMixin: Echo State Property validation methods
    
    📖 **Research Reference**: Jaeger (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize configuration optimization capabilities"""
        super().__init__(*args, **kwargs)
        
        # Initialize default configuration settings
        if not hasattr(self, 'activation_function'):
            self.activation_function = 'tanh'
        if not hasattr(self, 'noise_type'):
            self.noise_type = 'additive'
        if not hasattr(self, 'esp_validation_method'):
            self.esp_validation_method = 'fast'
        
        # Initialize activation functions if not already done
        if not hasattr(self, 'activation_functions'):
            self._initialize_activation_functions()
    
    def _initialize_activation_functions(self):
        """Initialize activation function options (6 configurable choices)"""
        import numpy as np
        self.activation_functions = {
            'tanh': lambda x: np.tanh(x),
            'sigmoid': lambda x: 1 / (1 + np.exp(-np.clip(x, -500, 500))),
            'relu': lambda x: np.maximum(0, x),
            'leaky_relu': lambda x: np.where(x > 0, x, 0.01 * x),
            'linear': lambda x: x,
            'custom': getattr(self, 'custom_activation', lambda x: np.tanh(x))
        }
    
    def _initialize_bias_terms(self):
        """Initialize bias terms (3 configurable types)"""
        import numpy as np
        bias_type = getattr(self, 'bias_type', 'random')
        bias_scale = getattr(self, 'bias_scale', 0.1)
        n_reservoir = getattr(self, 'n_reservoir', 100)
        
        if bias_type == 'random':
            self.bias = np.random.uniform(-bias_scale, bias_scale, n_reservoir)
        elif bias_type == 'zero':
            self.bias = np.zeros(n_reservoir)
        elif bias_type == 'adaptive':
            # Adaptive bias based on neuron position in network
            self.bias = np.random.uniform(-bias_scale, bias_scale, n_reservoir)
            # Scale bias based on neuron degree (more connected neurons get smaller bias)
            if hasattr(self, 'W_reservoir'):
                degrees = np.sum(np.abs(self.W_reservoir) > 0, axis=1)
                self.bias *= (1.0 / (1.0 + degrees / n_reservoir))
                
        print(f"✓ Bias terms initialized: {bias_type} type")


# Standalone wrapper functions for backward compatibility
def optimize_spectral_radius(X_train, y_train, esn=None, **kwargs):
    """Standalone wrapper for optimize_spectral_radius method."""
    if esn is None:
        # Import here to avoid circular imports
        from ..echo_state_network import EchoStateNetwork
        esn = EchoStateNetwork(random_seed=42)
    return esn.optimize_spectral_radius(X_train, y_train, **kwargs)


def run_benchmark_suite(*args, **kwargs):
    """Placeholder for benchmark suite."""
    return {"status": "benchmark_suite_placeholder"}