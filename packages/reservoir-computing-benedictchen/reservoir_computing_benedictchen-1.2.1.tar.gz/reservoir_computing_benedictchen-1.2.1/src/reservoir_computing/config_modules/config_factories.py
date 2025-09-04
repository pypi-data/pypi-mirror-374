"""
🏗️ Reservoir Computing - Configuration Factory Functions Module
==============================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Factory functions for creating pre-configured reservoir computing setups
with task-specific defaults and research-validated parameter combinations.

🏭 FACTORY FUNCTIONS:
====================
• create_esn_config() - Standard ESN with task-specific defaults
• create_deep_esn_config() - Multi-layer reservoir configurations
• create_online_esn_config() - Online learning setups
• create_optimization_config() - Hyperparameter optimization configs
• get_preset_config() - Named presets for common scenarios

🎓 RESEARCH FOUNDATION:
======================
Factory presets based on:
- Jaeger (2001): Original ESN parameter recommendations
- Lukoševičius & Jaeger (2009): Practical guidelines and best practices
- Benchmark studies: Parameter ranges for different task types
- Community standards: Commonly used configurations

Each factory provides research-validated starting points that can be
customized for specific applications and datasets.
"""

from typing import List, Optional, Dict, Any
import numpy as np
from .config_enums import (
    ReservoirType, ActivationFunction, TopologyType, ReadoutType,
    NoiseType, FeedbackMode, InitializationMethod, TrainingMethod,
    OptimizationObjective
)
from .config_classes import ESNConfig, DeepESNConfig, OnlineESNConfig, OptimizationConfig, TaskConfig


def create_esn_config(task_type: str = "regression",
                     complexity: str = "medium", 
                     n_reservoir: Optional[int] = None,
                     spectral_radius: Optional[float] = None,
                     **kwargs) -> ESNConfig:
    """
    🏭 Create ESN Configuration with Task-Specific Defaults
    
    Factory function that creates optimized ESN configurations based on
    task type and complexity level, using research-validated parameters.
    
    Args:
        task_type: Type of task ("regression", "classification", "generation", 
                  "time_series", "memory", "nonlinear")
        complexity: Task complexity ("simple", "medium", "complex")  
        n_reservoir: Reservoir size (auto-selected if None)
        spectral_radius: Spectral radius (auto-selected if None)
        **kwargs: Additional configuration overrides
        
    Returns:
        ESNConfig: Configured ESN ready for the specified task
        
    Example:
        ```python
        # Simple regression task
        config = create_esn_config("regression", "simple")
        
        # Complex time series prediction  
        config = create_esn_config("time_series", "complex", n_reservoir=500)
        
        # Classification with custom parameters
        config = create_esn_config("classification", leak_rate=0.3)
        ```
        
    Research Context:
        Parameter selection based on empirical studies and theoretical
        guidelines from reservoir computing literature. Different tasks
        benefit from different reservoir dynamics and connectivity patterns.
    """
    
    # === TASK-SPECIFIC DEFAULTS ===
    if task_type == "regression":
        defaults = {
            'activation': ActivationFunction.TANH,
            'topology_type': TopologyType.RANDOM_SPARSE,
            'readout_type': ReadoutType.RIDGE,
            'feedback_mode': FeedbackMode.NONE
        }
        # Complexity-based sizing
        if complexity == "simple":
            defaults.update({'n_reservoir': 50, 'spectral_radius': 0.9, 'leak_rate': 0.8})
        elif complexity == "medium":
            defaults.update({'n_reservoir': 100, 'spectral_radius': 0.95, 'leak_rate': 0.5})
        else:  # complex
            defaults.update({'n_reservoir': 200, 'spectral_radius': 0.98, 'leak_rate': 0.3})
            
    elif task_type == "classification":
        defaults = {
            'activation': ActivationFunction.TANH,
            'topology_type': TopologyType.RANDOM_SPARSE,
            'readout_type': ReadoutType.RIDGE,
            'feedback_mode': FeedbackMode.NONE,
            'regularization': 1e-5  # Higher regularization for classification
        }
        if complexity == "simple":
            defaults.update({'n_reservoir': 100, 'spectral_radius': 0.9, 'leak_rate': 0.6})
        elif complexity == "medium":
            defaults.update({'n_reservoir': 150, 'spectral_radius': 0.95, 'leak_rate': 0.5})
        else:  # complex
            defaults.update({'n_reservoir': 300, 'spectral_radius': 0.95, 'leak_rate': 0.4})
            
    elif task_type == "generation":
        defaults = {
            'activation': ActivationFunction.TANH,
            'topology_type': TopologyType.SMALL_WORLD,
            'readout_type': ReadoutType.RIDGE,
            'feedback_mode': FeedbackMode.DIRECT,
            'feedback_scaling': 0.1,
            'teacher_forcing_mode': True
        }
        if complexity == "simple":
            defaults.update({'n_reservoir': 100, 'spectral_radius': 0.95, 'leak_rate': 0.7})
        elif complexity == "medium": 
            defaults.update({'n_reservoir': 200, 'spectral_radius': 0.98, 'leak_rate': 0.5})
        else:  # complex
            defaults.update({'n_reservoir': 400, 'spectral_radius': 0.99, 'leak_rate': 0.3})
            
    elif task_type == "time_series":
        defaults = {
            'activation': ActivationFunction.TANH,
            'topology_type': TopologyType.RING,  # Good for temporal patterns
            'readout_type': ReadoutType.RIDGE,
            'feedback_mode': FeedbackMode.NONE,
            'washout': 200  # Longer washout for time series
        }
        if complexity == "simple":
            defaults.update({'n_reservoir': 100, 'spectral_radius': 0.9, 'leak_rate': 0.6})
        elif complexity == "medium":
            defaults.update({'n_reservoir': 200, 'spectral_radius': 0.95, 'leak_rate': 0.4})
        else:  # complex
            defaults.update({'n_reservoir': 500, 'spectral_radius': 0.98, 'leak_rate': 0.2})
            
    elif task_type == "memory":
        # Optimized for memory capacity tasks
        defaults = {
            'activation': ActivationFunction.TANH,
            'topology_type': TopologyType.RANDOM_SPARSE,
            'readout_type': ReadoutType.LINEAR,  # Linear for memory tasks
            'feedback_mode': FeedbackMode.NONE,
            'leak_rate': 1.0,  # No leaking for memory
            'spectral_radius': 0.99,  # High for memory
            'regularization': 1e-8  # Minimal regularization
        }
        if complexity == "simple":
            defaults.update({'n_reservoir': 100})
        elif complexity == "medium":
            defaults.update({'n_reservoir': 200})
        else:  # complex
            defaults.update({'n_reservoir': 500})
            
    elif task_type == "nonlinear":
        # Optimized for nonlinear processing capacity
        defaults = {
            'activation': ActivationFunction.TANH,
            'topology_type': TopologyType.SCALE_FREE,  # Complex connectivity
            'readout_type': ReadoutType.RIDGE,
            'feedback_mode': FeedbackMode.NONE,
            'input_scaling': 0.5  # Moderate input scaling
        }
        if complexity == "simple":
            defaults.update({'n_reservoir': 150, 'spectral_radius': 0.9, 'leak_rate': 0.7})
        elif complexity == "medium":
            defaults.update({'n_reservoir': 300, 'spectral_radius': 0.95, 'leak_rate': 0.5})
        else:  # complex
            defaults.update({'n_reservoir': 500, 'spectral_radius': 0.98, 'leak_rate': 0.3})
            
    else:
        # Default regression setup
        defaults = {
            'n_reservoir': 100,
            'spectral_radius': 0.95,
            'leak_rate': 0.5,
            'activation': ActivationFunction.TANH,
            'topology_type': TopologyType.RANDOM_SPARSE,
            'readout_type': ReadoutType.RIDGE
        }
    
    # Override with user parameters
    if n_reservoir is not None:
        defaults['n_reservoir'] = n_reservoir
    if spectral_radius is not None:
        defaults['spectral_radius'] = spectral_radius
        
    # Apply additional kwargs
    defaults.update(kwargs)
    
    return ESNConfig(**defaults)


def create_deep_esn_config(layer_sizes: List[int],
                          task_type: str = "regression",
                          inter_layer_scaling: float = 0.3,
                          **kwargs) -> DeepESNConfig:
    """
    🏭 Create Deep ESN Configuration with Hierarchical Structure
    
    Factory for multi-layer reservoir networks with task-optimized
    layer configurations and inter-layer connectivity.
    
    Args:
        layer_sizes: List of reservoir sizes for each layer
        task_type: Task type for layer-specific optimization
        inter_layer_scaling: Scaling for inter-layer connections
        **kwargs: Additional configuration parameters
        
    Returns:
        DeepESNConfig: Configured deep ESN
        
    Example:
        ```python
        # 3-layer hierarchy for complex time series
        config = create_deep_esn_config([200, 100, 50], "time_series")
        
        # Classification with bidirectional processing
        config = create_deep_esn_config([150, 100], "classification", 
                                      bidirectional=True)
        ```
    """
    
    # Start with base ESN config for the task
    base_config = create_esn_config(task_type, complexity="medium", **kwargs)
    
    # Task-specific deep configurations
    if task_type in ["time_series", "generation"]:
        # Decreasing leak rates for temporal hierarchy
        layer_leak_rates = [max(0.1, base_config.leak_rate * (0.8 ** i)) 
                           for i in range(len(layer_sizes))]
        # Decreasing spectral radii for stability
        layer_spectral_radii = [min(0.99, base_config.spectral_radius * (0.98 ** i))
                               for i in range(len(layer_sizes))]
        skip_connections = True
    else:
        # Standard decreasing pattern
        layer_leak_rates = [min(1.0, base_config.leak_rate * (1.1 ** i))
                           for i in range(len(layer_sizes))]
        layer_spectral_radii = [base_config.spectral_radius * (0.95 ** i)
                               for i in range(len(layer_sizes))]
        skip_connections = False
    
    # Create deep config
    deep_config = DeepESNConfig(
        layer_sizes=layer_sizes,
        layer_spectral_radii=layer_spectral_radii,
        layer_leak_rates=layer_leak_rates,
        inter_layer_scaling=inter_layer_scaling,
        skip_connections=skip_connections,
        **{k: v for k, v in base_config.__dict__.items() 
           if k not in ['n_reservoir']}  # Exclude single reservoir size
    )
    
    return deep_config


def create_online_esn_config(task_type: str = "regression",
                           adaptation_rate: float = 0.01,
                           forgetting_factor: float = 0.999,
                           **kwargs) -> OnlineESNConfig:
    """
    🏭 Create Online ESN Configuration for Streaming Data
    
    Factory for online/incremental learning ESN optimized for
    non-stationary environments and real-time processing.
    
    Args:
        task_type: Task type for base configuration
        adaptation_rate: Learning rate for online adaptation
        forgetting_factor: Exponential forgetting factor
        **kwargs: Additional configuration parameters
        
    Returns:
        OnlineESNConfig: Configured online ESN
        
    Example:
        ```python
        # Fast adaptation for non-stationary data
        config = create_online_esn_config("time_series", 
                                        adaptation_rate=0.05,
                                        forgetting_factor=0.99)
        
        # Conservative online learning
        config = create_online_esn_config("regression",
                                        adaptation_rate=0.001)
        ```
    """
    
    # Start with base ESN config, modified for online learning
    base_config = create_esn_config(task_type, complexity="medium", **kwargs)
    
    # Online-specific modifications
    online_modifications = {
        'washout': min(50, base_config.washout),  # Reduced washout
        'regularization': max(1e-5, base_config.regularization),  # Higher regularization
        'training_method': TrainingMethod.ONLINE
    }
    
    # Update base config
    for key, value in online_modifications.items():
        setattr(base_config, key, value)
    
    # Create online config
    online_config = OnlineESNConfig(
        adaptation_rate=adaptation_rate,
        forgetting_factor=forgetting_factor,
        **base_config.__dict__
    )
    
    return online_config


def create_optimization_config(param_ranges: Optional[Dict] = None,
                             n_trials: int = 50,
                             method: str = "random",
                             objective: OptimizationObjective = OptimizationObjective.MSE,
                             **kwargs) -> OptimizationConfig:
    """
    🏭 Create Optimization Configuration for Hyperparameter Tuning
    
    Factory for hyperparameter optimization with task-specific parameter
    ranges and search strategies.
    
    Args:
        param_ranges: Parameter search ranges (uses defaults if None)
        n_trials: Number of optimization trials
        method: Search method ("random", "grid", "bayesian")
        objective: Optimization objective
        **kwargs: Additional optimization parameters
        
    Returns:
        OptimizationConfig: Configured optimization setup
        
    Example:
        ```python
        # Standard optimization for regression
        config = create_optimization_config(n_trials=100)
        
        # Custom parameter ranges for classification
        ranges = {
            'n_reservoir': [50, 100, 200, 400],
            'spectral_radius': (0.8, 0.99),
            'leak_rate': (0.1, 1.0)
        }
        config = create_optimization_config(ranges, n_trials=200, 
                                          objective=OptimizationObjective.ACCURACY)
        ```
    """
    
    # Default parameter ranges based on literature
    if param_ranges is None:
        param_ranges = {
            'n_reservoir': [50, 100, 150, 200, 300, 500],
            'spectral_radius': (0.8, 0.99),
            'input_scaling': (0.1, 2.0),
            'leak_rate': (0.1, 1.0),
            'regularization': (1e-8, 1e-2),
            'sparsity': (0.05, 0.5)
        }
    
    # Method-specific defaults
    method_defaults = {
        'random': {'n_trials': 50, 'enable_pruning': False},
        'grid': {'n_trials': None, 'enable_pruning': False}, 
        'bayesian': {'n_trials': 100, 'enable_pruning': True}
    }
    
    config_params = {
        'param_ranges': param_ranges,
        'n_trials': n_trials,
        'optimization_method': method,
        'objective': objective,
        **method_defaults.get(method, {}),
        **kwargs
    }
    
    return OptimizationConfig(**config_params)


def get_preset_config(preset_name: str) -> ESNConfig:
    """
    🏭 Get Named Preset Configuration
    
    Provides pre-configured ESN setups for common applications
    and benchmark tasks, based on literature and best practices.
    
    Args:
        preset_name: Name of preset configuration
        
    Available presets:
        - "jaeger_2001": Original Jaeger (2001) parameters
        - "memory_capacity": Optimized for linear memory tasks
        - "nonlinear_capacity": Optimized for nonlinear processing
        - "lorenz_prediction": Chaotic time series prediction  
        - "speech_recognition": Speech/audio processing
        - "financial_forecasting": Financial time series
        - "benchmark_small": Small benchmark (fast testing)
        - "benchmark_large": Large benchmark (comprehensive)
        
    Returns:
        ESNConfig: Preset configuration
        
    Example:
        ```python
        # Classic ESN parameters from original paper
        config = get_preset_config("jaeger_2001")
        
        # Optimized for memory capacity benchmark
        config = get_preset_config("memory_capacity")
        ```
    """
    
    presets = {
        "jaeger_2001": ESNConfig(
            n_reservoir=100,
            spectral_radius=0.95,
            input_scaling=0.1,
            leak_rate=1.0,
            activation=ActivationFunction.TANH,
            regularization=1e-6,
            washout=100
        ),
        
        "memory_capacity": ESNConfig(
            n_reservoir=200,
            spectral_radius=0.99,
            input_scaling=0.1,
            leak_rate=1.0,
            activation=ActivationFunction.TANH,
            topology_type=TopologyType.RANDOM_SPARSE,
            sparsity=0.1,
            regularization=1e-8,
            readout_type=ReadoutType.LINEAR
        ),
        
        "nonlinear_capacity": ESNConfig(
            n_reservoir=300,
            spectral_radius=0.95,
            input_scaling=0.5,
            leak_rate=0.5,
            activation=ActivationFunction.TANH,
            topology_type=TopologyType.SCALE_FREE,
            sparsity=0.15,
            regularization=1e-6,
            readout_type=ReadoutType.RIDGE
        ),
        
        "lorenz_prediction": ESNConfig(
            n_reservoir=200,
            spectral_radius=0.9,
            input_scaling=1.0,
            leak_rate=0.3,
            activation=ActivationFunction.TANH,
            topology_type=TopologyType.SMALL_WORLD,
            washout=200,
            regularization=1e-8
        ),
        
        "speech_recognition": ESNConfig(
            n_reservoir=500,
            spectral_radius=0.95,
            input_scaling=0.1,
            leak_rate=0.2,
            activation=ActivationFunction.TANH,
            topology_type=TopologyType.RING,
            readout_type=ReadoutType.RIDGE,
            regularization=1e-4
        ),
        
        "financial_forecasting": ESNConfig(
            n_reservoir=150,
            spectral_radius=0.98,
            input_scaling=0.5,
            leak_rate=0.1,
            activation=ActivationFunction.TANH,
            noise_type=NoiseType.GAUSSIAN,
            noise_level=0.01,
            regularization=1e-4
        ),
        
        "benchmark_small": ESNConfig(
            n_reservoir=50,
            spectral_radius=0.9,
            input_scaling=0.1,
            leak_rate=0.5,
            washout=50,
            regularization=1e-6
        ),
        
        "benchmark_large": ESNConfig(
            n_reservoir=1000,
            spectral_radius=0.99,
            input_scaling=0.1,
            leak_rate=0.3,
            washout=500,
            regularization=1e-8,
            topology_type=TopologyType.SMALL_WORLD
        )
    }
    
    if preset_name not in presets:
        available = ", ".join(presets.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
        
    return presets[preset_name]


# Export all factory functions
__all__ = [
    'create_esn_config',
    'create_deep_esn_config',
    'create_online_esn_config', 
    'create_optimization_config',
    'get_preset_config'
]


if __name__ == "__main__":
    print("🏗️ Reservoir Computing - Configuration Factories")
    print("=" * 50)
    print("🏭 FACTORY FUNCTIONS:")
    print("  • create_esn_config() - Task-specific ESN configurations")
    print("  • create_deep_esn_config() - Multi-layer reservoir setups")
    print("  • create_online_esn_config() - Online learning configurations")
    print("  • create_optimization_config() - Hyperparameter optimization")
    print("  • get_preset_config() - Named preset configurations")
    print("")
    
    # Demo preset availability
    print("📋 AVAILABLE PRESETS:")
    presets = ["jaeger_2001", "memory_capacity", "nonlinear_capacity", 
              "lorenz_prediction", "speech_recognition", "financial_forecasting",
              "benchmark_small", "benchmark_large"]
    for preset in presets:
        print(f"  • {preset}")
    
    print("")
    print("✅ All configuration factories loaded successfully!")
    print("🔬 Research-validated presets and task-specific optimization!")