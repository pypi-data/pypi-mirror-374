"""
🏗️ Reservoir Computing - Configuration Utilities Module
======================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Utility functions for configuration validation, optimization, and task-specific
configuration tuning for reservoir computing systems.

🔧 UTILITY FUNCTIONS:
====================
• validate_config() - Configuration validation and warnings
• optimize_config_for_task() - Automated configuration optimization
• config_recommendations() - Expert system for parameter suggestions
• compare_configs() - Configuration comparison and analysis

🎓 RESEARCH FOUNDATION:
======================
Utilities based on:
- Jaeger (2001): ESP conditions and stability requirements
- Lukoševičius & Jaeger (2009): Practical parameter guidelines
- Reservoir computing best practices: Common pitfalls and solutions
- Expert knowledge: Parameter interactions and optimization strategies

Configuration utilities help users avoid common mistakes and optimize
parameters for specific tasks and datasets.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import warnings
from .config_enums import ActivationFunction, TopologyType, ReadoutType
from .config_classes import ESNConfig, DeepESNConfig, OnlineESNConfig


def validate_config(config: ESNConfig) -> List[str]:
    """
    🔍 Validate ESN Configuration and Provide Warnings
    
    Comprehensive validation of ESN configuration parameters with
    research-based recommendations and common pitfall detection.
    
    Args:
        config: ESN configuration to validate
        
    Returns:
        List[str]: List of warning messages (empty if no issues)
        
    Example:
        ```python
        config = ESNConfig(spectral_radius=1.5)  # Invalid
        warnings = validate_config(config)
        for warning in warnings:
            print(f"⚠️  {warning}")
        ```
        
    Research Context:
        Validation based on theoretical requirements (ESP conditions)
        and empirical guidelines from reservoir computing literature.
        Helps prevent common configuration errors.
    """
    warnings_list = []
    
    # === CRITICAL PARAMETER VALIDATION ===
    
    # Echo State Property requirements
    if config.spectral_radius >= 1.0:
        warnings_list.append(
            f"Spectral radius ({config.spectral_radius}) >= 1.0 may violate ESP. "
            f"Consider reducing to 0.8-0.99 for stability."
        )
    elif config.spectral_radius > 0.99:
        warnings_list.append(
            f"Very high spectral radius ({config.spectral_radius}) near ESP boundary. "
            f"Monitor for instability and consider slight reduction."
        )
    elif config.spectral_radius < 0.5:
        warnings_list.append(
            f"Low spectral radius ({config.spectral_radius}) may reduce reservoir dynamics. "
            f"Consider increasing if task requires complex temporal processing."
        )
    
    # Input scaling validation
    if config.input_scaling > 2.0:
        warnings_list.append(
            f"High input scaling ({config.input_scaling}) may saturate activation. "
            f"Consider reducing or using linear activation function."
        )
    elif config.input_scaling < 0.01:
        warnings_list.append(
            f"Very low input scaling ({config.input_scaling}) may limit input influence. "
            f"Ensure inputs can drive reservoir dynamics effectively."
        )
    
    # Regularization validation  
    if config.regularization > 1e-2:
        warnings_list.append(
            f"High regularization ({config.regularization}) may over-constrain learning. "
            f"Consider reducing if underfitting occurs."
        )
    elif config.regularization < 1e-10:
        warnings_list.append(
            f"Very low regularization ({config.regularization}) may cause overfitting. "
            f"Consider increasing for better generalization."
        )
    
    # Reservoir size validation
    if config.n_reservoir < 20:
        warnings_list.append(
            f"Small reservoir size ({config.n_reservoir}) may limit capacity. "
            f"Consider increasing for complex tasks."
        )
    elif config.n_reservoir > 2000:
        warnings_list.append(
            f"Large reservoir size ({config.n_reservoir}) increases computation. "
            f"Ensure this is necessary for your task complexity."
        )
    
    # Sparsity validation
    if config.sparsity > 0.5:
        warnings_list.append(
            f"High sparsity ({config.sparsity}) creates dense connectivity. "
            f"Consider reducing for computational efficiency."
        )
    elif config.sparsity < 0.01:
        warnings_list.append(
            f"Very low sparsity ({config.sparsity}) may isolate neurons. "
            f"Ensure sufficient connectivity for information flow."
        )
    
    # Leak rate validation
    if config.leak_rate < 0.1:
        warnings_list.append(
            f"Very low leak rate ({config.leak_rate}) creates slow dynamics. "
            f"Ensure this matches your task's temporal requirements."
        )
    
    # === ACTIVATION-SPECIFIC WARNINGS ===
    
    if config.activation == ActivationFunction.RELU and config.spectral_radius > 0.9:
        warnings_list.append(
            f"ReLU activation with high spectral radius ({config.spectral_radius}) "
            f"may cause exploding dynamics. Consider reducing spectral radius."
        )
    
    if config.activation == ActivationFunction.LINEAR:
        warnings_list.append(
            "Linear activation reduces nonlinear processing capacity. "
            "Consider tanh or sigmoid for complex tasks."
        )
    
    # === COMBINATION WARNINGS ===
    
    # High input scaling + saturating activation
    if (config.input_scaling > 1.0 and 
        config.activation in [ActivationFunction.TANH, ActivationFunction.SIGMOID]):
        warnings_list.append(
            f"High input scaling ({config.input_scaling}) with saturating activation "
            f"may reduce effective input range. Consider reducing input scaling."
        )
    
    # Low leak rate + high spectral radius
    if config.leak_rate < 0.3 and config.spectral_radius > 0.95:
        warnings_list.append(
            "Combination of low leak rate and high spectral radius creates "
            "very long memory timescales. Ensure this matches task requirements."
        )
    
    # Feedback warnings
    if config.feedback_mode.value != "none" and config.feedback_scaling > 0.5:
        warnings_list.append(
            f"High feedback scaling ({config.feedback_scaling}) may destabilize dynamics. "
            f"Consider reducing or monitoring stability."
        )
    
    return warnings_list


def optimize_config_for_task(X: np.ndarray, y: np.ndarray,
                           base_config: Optional[ESNConfig] = None,
                           optimization_config: Optional[Dict] = None) -> ESNConfig:
    """
    🎯 Automatically Optimize ESN Configuration for Given Task Data
    
    Analyzes task characteristics and automatically optimizes ESN parameters
    using data-driven heuristics and hyperparameter search.
    
    Args:
        X: Input data array
        y: Target data array  
        base_config: Starting configuration (uses defaults if None)
        optimization_config: Optimization settings
        
    Returns:
        ESNConfig: Optimized configuration for the task
        
    Example:
        ```python
        # Automatic optimization
        optimized_config = optimize_config_for_task(X_train, y_train)
        
        # With custom base configuration
        base = ESNConfig(n_reservoir=200)
        optimized_config = optimize_config_for_task(X_train, y_train, base)
        ```
        
    Research Context:
        Uses data characteristics (dimensionality, temporal structure,
        nonlinearity) to guide parameter selection and optimization.
        Combines expert heuristics with automated search.
    """
    
    # Import here to avoid circular imports
    try:
        from ..utils_modules.utils_optimization import optimize_hyperparameters
    except ImportError:
        # Fallback to simplified optimization
        return _simple_config_optimization(X, y, base_config)
    
    # Analyze data characteristics
    data_analysis = _analyze_task_data(X, y)
    
    # Create base configuration if not provided
    if base_config is None:
        base_config = _create_data_driven_config(data_analysis)
    
    # Default optimization settings
    if optimization_config is None:
        optimization_config = {
            'param_ranges': {
                'spectral_radius': (0.8, 0.99),
                'input_scaling': (0.1, 2.0),
                'leak_rate': (0.1, 1.0),
                'regularization': (1e-8, 1e-2)
            },
            'n_trials': 50,
            'cv_folds': 3
        }
    
    # Placeholder for actual optimization (would need ESN class)
    # This is a simplified version for the configuration module
    return _heuristic_config_optimization(data_analysis, base_config)


def config_recommendations(config: ESNConfig, task_type: str = "general") -> Dict[str, str]:
    """
    🔬 Get Expert Recommendations for Configuration Improvements
    
    Provides expert system recommendations for improving ESN configuration
    based on task type and parameter analysis.
    
    Args:
        config: Current ESN configuration
        task_type: Type of task ("regression", "classification", "time_series", 
                  "generation", "memory", "general")
                  
    Returns:
        Dict[str, str]: Recommendations keyed by parameter name
        
    Example:
        ```python
        config = ESNConfig(spectral_radius=0.7, leak_rate=1.0)
        recommendations = config_recommendations(config, "time_series")
        
        for param, advice in recommendations.items():
            print(f"{param}: {advice}")
        ```
    """
    recommendations = {}
    
    # === TASK-SPECIFIC RECOMMENDATIONS ===
    
    if task_type == "time_series":
        if config.leak_rate > 0.7:
            recommendations['leak_rate'] = (
                "Consider reducing leak rate to 0.2-0.5 for better temporal integration "
                "in time series tasks."
            )
        if config.topology_type not in [TopologyType.RING, TopologyType.SMALL_WORLD]:
            recommendations['topology_type'] = (
                "Ring or small-world topologies often work better for time series "
                "due to their temporal processing characteristics."
            )
        if config.washout < 100:
            recommendations['washout'] = (
                "Increase washout to 100-200 for time series to ensure proper "
                "transient removal and stable initial conditions."
            )
    
    elif task_type == "classification":
        if config.regularization < 1e-5:
            recommendations['regularization'] = (
                "Increase regularization to 1e-5 to 1e-3 for better generalization "
                "in classification tasks."
            )
        if config.readout_type == ReadoutType.LINEAR:
            recommendations['readout_type'] = (
                "Consider Ridge regression for better regularization in "
                "classification tasks."
            )
    
    elif task_type == "generation":
        if config.feedback_mode.value == "none":
            recommendations['feedback_mode'] = (
                "Enable output feedback (direct or reservoir) for generation tasks "
                "to enable autonomous dynamics."
            )
        if config.spectral_radius < 0.95:
            recommendations['spectral_radius'] = (
                "Increase spectral radius to 0.95-0.99 for generation tasks "
                "to maintain rich dynamics during autonomous operation."
            )
        if not config.teacher_forcing_mode:
            recommendations['teacher_forcing_mode'] = (
                "Enable teacher forcing during training for stable generation "
                "task learning."
            )
    
    elif task_type == "memory":
        if config.leak_rate < 1.0:
            recommendations['leak_rate'] = (
                "Set leak rate to 1.0 (no leaking) for maximum memory capacity "
                "in memory-based tasks."
            )
        if config.spectral_radius < 0.98:
            recommendations['spectral_radius'] = (
                "Increase spectral radius close to 1.0 (0.98-0.99) for maximum "
                "memory capacity while maintaining stability."
            )
        if config.regularization > 1e-6:
            recommendations['regularization'] = (
                "Use minimal regularization (1e-8 to 1e-6) for memory tasks "
                "to avoid constraining memory capacity."
            )
    
    # === GENERAL PARAMETER RECOMMENDATIONS ===
    
    # Spectral radius
    if config.spectral_radius > 0.99:
        recommendations['spectral_radius'] = (
            "Very high spectral radius risks violating Echo State Property. "
            "Consider reducing to 0.95-0.98 for safety."
        )
    elif config.spectral_radius < 0.8:
        recommendations['spectral_radius'] = (
            "Low spectral radius may reduce reservoir expressivity. "
            "Consider increasing to 0.9-0.95 for richer dynamics."
        )
    
    # Input scaling vs activation function
    if (config.input_scaling > 1.5 and 
        config.activation in [ActivationFunction.TANH, ActivationFunction.SIGMOID]):
        recommendations['input_scaling'] = (
            f"High input scaling ({config.input_scaling}) with {config.activation.value} "
            f"may saturate activation. Consider reducing to 0.1-1.0."
        )
    
    # Reservoir size vs task complexity
    if config.n_reservoir < 50:
        recommendations['n_reservoir'] = (
            "Small reservoir may limit computational capacity. "
            "Consider increasing to 100+ for complex tasks."
        )
    
    # Sparsity recommendations
    if config.sparsity > 0.3:
        recommendations['sparsity'] = (
            "High connectivity may be computationally expensive. "
            "Consider reducing sparsity to 0.1-0.2 for efficiency."
        )
    
    return recommendations


def compare_configs(*configs: ESNConfig, 
                   metrics: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    ⚖️  Compare Multiple ESN Configurations
    
    Provides detailed comparison analysis of multiple ESN configurations,
    highlighting differences and potential trade-offs.
    
    Args:
        *configs: Variable number of ESN configurations to compare
        metrics: Specific metrics to compare (uses defaults if None)
        
    Returns:
        Dict[str, Any]: Comparison analysis with differences and recommendations
        
    Example:
        ```python
        config1 = ESNConfig(n_reservoir=100, spectral_radius=0.9)
        config2 = ESNConfig(n_reservoir=200, spectral_radius=0.95) 
        config3 = get_preset_config("memory_capacity")
        
        comparison = compare_configs(config1, config2, config3)
        print(comparison['summary'])
        ```
    """
    if len(configs) < 2:
        raise ValueError("Need at least 2 configurations to compare")
    
    if metrics is None:
        metrics = ['n_reservoir', 'spectral_radius', 'input_scaling', 'leak_rate',
                  'regularization', 'sparsity', 'activation', 'topology_type']
    
    comparison = {
        'n_configs': len(configs),
        'parameter_comparison': {},
        'differences': [],
        'recommendations': []
    }
    
    # Compare each metric across configurations
    for metric in metrics:
        values = []
        for i, config in enumerate(configs):
            value = getattr(config, metric, "N/A")
            # Handle enum values
            if hasattr(value, 'value'):
                value = value.value
            values.append(f"Config {i+1}: {value}")
        
        comparison['parameter_comparison'][metric] = values
        
        # Identify significant differences
        numeric_values = []
        for config in configs:
            value = getattr(config, metric, None)
            if isinstance(value, (int, float)):
                numeric_values.append(value)
        
        if len(numeric_values) >= 2:
            min_val, max_val = min(numeric_values), max(numeric_values)
            if max_val > min_val * 2:  # Significant difference threshold
                comparison['differences'].append(
                    f"{metric}: Large variation ({min_val:.3f} to {max_val:.3f})"
                )
    
    # Generate recommendations based on differences
    if comparison['differences']:
        comparison['recommendations'].append(
            "Significant parameter variations detected. Consider:"
        )
        comparison['recommendations'].append(
            "- Testing multiple configurations with cross-validation"
        )
        comparison['recommendations'].append(
            "- Using hyperparameter optimization to find optimal values"
        )
        comparison['recommendations'].append(
            "- Analyzing task requirements to guide parameter selection"
        )
    else:
        comparison['recommendations'].append(
            "Configurations are similar. Performance differences may be subtle."
        )
    
    # Summary
    comparison['summary'] = (
        f"Compared {len(configs)} configurations across {len(metrics)} parameters. "
        f"Found {len(comparison['differences'])} significant differences."
    )
    
    return comparison


# Helper functions for internal use
def _analyze_task_data(X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Analyze data characteristics to guide configuration"""
    analysis = {}
    
    # Basic statistics
    analysis['n_samples'], analysis['n_features'] = X.shape
    analysis['n_targets'] = y.shape[1] if y.ndim > 1 else 1
    analysis['sequence_length'] = X.shape[0]
    
    # Data characteristics
    analysis['input_range'] = (np.min(X), np.max(X))
    analysis['input_std'] = np.std(X)
    analysis['target_range'] = (np.min(y), np.max(y)) 
    analysis['target_std'] = np.std(y)
    
    # Temporal characteristics (simple estimates)
    if len(X) > 10:
        # Autocorrelation estimate
        input_autocorr = np.corrcoef(X[:-1].flatten(), X[1:].flatten())[0, 1]
        analysis['temporal_correlation'] = input_autocorr if not np.isnan(input_autocorr) else 0.0
    else:
        analysis['temporal_correlation'] = 0.0
    
    return analysis


def _create_data_driven_config(analysis: Dict[str, Any]) -> ESNConfig:
    """Create configuration based on data analysis"""
    
    # Base configuration
    config_params = {}
    
    # Reservoir size based on data complexity
    n_features = analysis['n_features']
    sequence_length = analysis['sequence_length']
    config_params['n_reservoir'] = min(500, max(50, n_features * 20, sequence_length // 5))
    
    # Input scaling based on data range
    input_std = analysis['input_std']
    if input_std > 2.0:
        config_params['input_scaling'] = 0.1  # Scale down large inputs
    elif input_std < 0.5:
        config_params['input_scaling'] = 1.0  # Scale up small inputs
    else:
        config_params['input_scaling'] = 0.5
    
    # Temporal parameters based on correlation
    temporal_corr = analysis['temporal_correlation']
    if temporal_corr > 0.7:  # High temporal correlation
        config_params['leak_rate'] = 0.3  # Slow dynamics
        config_params['spectral_radius'] = 0.98
    elif temporal_corr < 0.3:  # Low temporal correlation
        config_params['leak_rate'] = 0.8  # Fast dynamics
        config_params['spectral_radius'] = 0.9
    else:  # Medium correlation
        config_params['leak_rate'] = 0.5
        config_params['spectral_radius'] = 0.95
    
    return ESNConfig(**config_params)


def _heuristic_config_optimization(analysis: Dict[str, Any], 
                                 base_config: ESNConfig) -> ESNConfig:
    """Simple heuristic optimization without full hyperparameter search"""
    
    # Start with base configuration
    optimized_params = base_config.__dict__.copy()
    
    # Adjust based on data characteristics
    if analysis['temporal_correlation'] > 0.8:
        # High temporal dependency - slow dynamics
        optimized_params['leak_rate'] = min(0.3, optimized_params['leak_rate'])
        optimized_params['spectral_radius'] = max(0.95, optimized_params['spectral_radius'])
    
    if analysis['input_std'] > 5.0:
        # High input variation - reduce input scaling
        optimized_params['input_scaling'] = min(0.1, optimized_params['input_scaling'])
    
    if analysis['n_features'] > 10:
        # High-dimensional input - larger reservoir
        optimized_params['n_reservoir'] = max(200, optimized_params['n_reservoir'])
    
    return ESNConfig(**optimized_params)


def _simple_config_optimization(X: np.ndarray, y: np.ndarray, 
                              base_config: Optional[ESNConfig]) -> ESNConfig:
    """Fallback optimization when full utils not available"""
    
    analysis = _analyze_task_data(X, y)
    
    if base_config is None:
        return _create_data_driven_config(analysis)
    else:
        return _heuristic_config_optimization(analysis, base_config)


# Export all utility functions
__all__ = [
    'validate_config',
    'optimize_config_for_task',
    'config_recommendations',
    'compare_configs'
]


if __name__ == "__main__":
    print("🏗️ Reservoir Computing - Configuration Utilities")
    print("=" * 50)
    print("🔧 UTILITY FUNCTIONS:")
    print("  • validate_config() - Configuration validation and warnings")
    print("  • optimize_config_for_task() - Data-driven optimization")
    print("  • config_recommendations() - Expert system recommendations")
    print("  • compare_configs() - Multi-configuration comparison")
    print("")
    print("✅ All configuration utilities loaded successfully!")
    print("🔬 Expert knowledge and data-driven optimization tools!")