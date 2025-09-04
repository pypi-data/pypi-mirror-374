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


def run_benchmark_suite(datasets=None, metrics=None, n_trials=10, *args, **kwargs):
    """
    Run ESN benchmark suite on standard reservoir computing tasks.
    
    Args:
        datasets: List of dataset names or None for default set
        metrics: List of metrics to compute or None for default set
        n_trials: Number of trials per configuration
        
    Returns:
        dict: Benchmark results with performance statistics
    """
    if datasets is None:
        datasets = ['mackey_glass', 'lorenz', 'narma10']
    
    if metrics is None:
        metrics = ['mse', 'rmse', 'nrmse', 'memory_capacity']
    
    results = {}
    
    for dataset in datasets:
        dataset_results = {}
        
        for metric in metrics:
            # Run multiple trials for statistical significance
            trial_scores = []
            
            for trial in range(n_trials):
                # Generate or load dataset
                if dataset == 'mackey_glass':
                    from ..data_generation import generate_mackey_glass
                    X_train, y_train, X_test, y_test = generate_mackey_glass()
                elif dataset == 'lorenz':
                    from ..data_generation import generate_lorenz
                    X_train, y_train, X_test, y_test = generate_lorenz()
                elif dataset == 'narma10':
                    from ..data_generation import generate_narma10
                    X_train, y_train, X_test, y_test = generate_narma10()
                else:
                    # Skip unknown datasets
                    continue
                
                # Create and train ESN
                from ..core import EchoStateNetwork
                esn = EchoStateNetwork(n_reservoir=100)
                esn.fit(X_train, y_train)
                y_pred = esn.predict(X_test)
                
                # Compute metric
                if metric == 'mse':
                    score = np.mean((y_test - y_pred)**2)
                elif metric == 'rmse':
                    score = np.sqrt(np.mean((y_test - y_pred)**2))
                elif metric == 'nrmse':
                    score = np.sqrt(np.mean((y_test - y_pred)**2)) / np.std(y_test)
                elif metric == 'memory_capacity':
                    # Approximate memory capacity calculation
                    score = _compute_memory_capacity(esn, X_test)
                
                trial_scores.append(score)
            
            # Compute statistics across trials
            dataset_results[metric] = {
                'mean': np.mean(trial_scores),
                'std': np.std(trial_scores),
                'min': np.min(trial_scores),
                'max': np.max(trial_scores),
                'trials': trial_scores
            }
        
        results[dataset] = dataset_results
    
    return {
        'status': 'completed',
        'n_trials': n_trials,
        'results': results,
        'datasets': datasets,
        'metrics': metrics
    }

def _compute_memory_capacity(esn, X_test):
    """Compute approximation of memory capacity for reservoir."""
    # Simplified memory capacity estimation
    # Full implementation would require delay line inputs
    n_delays = min(10, len(X_test) // 2)
    capacities = []
    
    for k in range(1, n_delays + 1):
        # Create delayed target
        y_delayed = X_test[:-k] if k < len(X_test) else X_test[:1]
        X_input = X_test[k:] if k < len(X_test) else X_test[-1:]
        
        if len(y_delayed) == 0 or len(X_input) == 0:
            continue
            
        # Get reservoir states
        states = esn._update_state(X_input.reshape(-1, 1))
        
        # Linear regression to predict delay-k input
        if len(states) == len(y_delayed):
            correlation = np.corrcoef(states.flatten(), y_delayed.flatten())[0, 1]
            capacities.append(correlation**2 if not np.isnan(correlation) else 0)
    
    return np.sum(capacities)