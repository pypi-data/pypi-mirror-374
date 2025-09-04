"""
🌊 Reservoir Computing Library - Unified Architecture
====================================================

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger (2001) Echo State Networks & Maass (2002) Liquid State Machines

This library implements the revolutionary concept of fixed random reservoirs
with trainable readout layers, enabling efficient temporal pattern processing.

🏗️ Unified Architecture:
========================
This package has been consolidated from scattered modules into a clean,
unified structure following the proven 4-File Pattern:

- core.py: All algorithm implementations (EchoStateNetwork, mixins, etc.)
- config.py: All configuration classes and enums
- utils.py: All utility functions (ESP validation, benchmarks, optimization)
- viz.py: All visualization functions (structure, dynamics, performance)

🎯 Key Features:
===============
- Research-accurate Echo State Network implementation
- Comprehensive ESP validation and spectral analysis
- Advanced topology management (small-world, scale-free, custom)
- Memory capacity and nonlinear benchmarking suite
- Professional visualization tools for analysis
- Optimization algorithms for hyperparameter tuning

📚 Research Foundation:
======================
Based on foundational work by:
- Herbert Jaeger (2001): Echo State Networks
- Wolfgang Maass (2002): Liquid State Machines  
- Lukosevicius & Jaeger (2009): Reservoir Computing Survey
- Verstraeten et al. (2007): Memory Capacity Analysis
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🌊 Reservoir Computing Library - Unified Architecture")
        print("   Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("   Support his work: \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\🍺 Buy him a beer\033]8;;\033\\")
        print("   💖 Consider recurring donations to fully support continued research")
    except:
        print("\n🌊 Reservoir Computing Library - Unified Architecture")
        print("   Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("   Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")

# ================================
# UNIFIED IMPORTS - CLEAN API
# ================================

# Core Algorithm Implementation
from .core import (
    # Main ESN Class - PRESERVED
    EchoStateNetwork,
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════════════════
    # ALL ImplementationS - Research implementations
    DeepEchoStateNetwork,      # ✅ REAL: Multiple reservoir layers
    OnlineEchoStateNetwork,    # ✅ REAL: RLS online training
    
    # Factory Functions - ALL ImplementationS  
    create_echo_state_network,      # ✅ REAL: Task-specific ESN creation
    optimize_esn_hyperparameters,   # ✅ REAL: Bayesian optimization
    
    # Configuration System - ALL USER CHOICE OPTIONS
    ESNConfig as CoreESNConfig,
    ESNArchitecture,
    TrainingMethod as CoreTrainingMethod,
    create_deep_esn_config,
    create_online_esn_config,
    create_optimized_esn_config,
    create_task_specific_esn_config,
    
    # Mixin Components (for advanced users) - PRESERVED
    ReservoirTheoryMixin,
    ReservoirInitializationMixin, 
    StateUpdateMixin,
    TrainingMixin,
    PredictionMixin
)

# Configuration Classes and Enums
from .config import (
    # Main Configuration
    ESNConfig,
    
    # Enums for all options (based on what's actually defined)
    ReservoirType,
    ActivationFunction,
    TopologyType,
    ReadoutType,
    NoiseType,
    FeedbackMode,
    InitializationMethod,
    TrainingMethod,
    OptimizationObjective
)

# Utility Functions
from .utils import (
    # ESP Validation
    comprehensive_esp_validation,
    validate_spectral_radius,
    validate_convergence,
    validate_lyapunov,
    validate_jacobian,
    validate_esp_fast,
    
    # Topology Management
    create_topology,
    create_ring_topology,
    create_small_world_topology,
    create_scale_free_topology,
    scale_spectral_radius,
    analyze_topology,
    
    # Benchmark Suite
    memory_capacity_benchmark,
    nonlinear_capacity_benchmark,
    evaluate_narma_task,
    
    # Optimization
    optimize_hyperparameters,
    grid_search_optimization,
    cross_validate_esn,
    analyze_parameter_sensitivity,
    
    # Statistical Validation
    statistical_significance_test,
    confidence_interval,
    performance_summary_statistics
)

# Visualization Functions
from .viz import (
    # Structure Visualization
    visualize_reservoir_structure,
    
    # Dynamics Visualization
    visualize_reservoir_dynamics,
    
    # Performance Visualization
    visualize_performance_analysis,
    
    # Comparative Analysis
    visualize_comparative_analysis,
    
    # Spectral Analysis
    visualize_spectral_analysis,
    
    # Animation
    create_reservoir_animation
)

# Backward Compatibility Aliases
EchoStatePropertyValidator = comprehensive_esp_validation
StructuredReservoirTopologies = create_topology
JaegerBenchmarkTasks = memory_capacity_benchmark
OutputFeedbackESN = EchoStateNetwork  # Same class with output_feedback=True
TeacherForcingTrainer = EchoStateNetwork  # Training is built into main class
OnlineLearningESN = EchoStateNetwork  # Online capabilities built into main class

# Import numpy for convenience functions
import numpy as np

# Convenience Functions
def optimize_spectral_radius(X_train, y_train, esn=None, radius_range=(0.1, 1.5), 
                           n_points=15, cv_folds=3):
    """Optimize spectral radius using grid search - backward compatibility wrapper"""
    if esn is None:
        esn = EchoStateNetwork(random_seed=42)
    
    param_space = {'spectral_radius': np.linspace(radius_range[0], radius_range[1], n_points)}
    return grid_search_optimization(EchoStateNetwork, X_train, y_train, param_space, cv_folds)

def validate_esp(esn, method='comprehensive', **kwargs):
    """Validate Echo State Property - backward compatibility wrapper"""
    return comprehensive_esp_validation(esn, method=method, **kwargs)

def run_benchmark_suite(esn_configs=None, benchmarks=['memory_capacity'], verbose=True):
    """Run benchmark suite - backward compatibility wrapper"""
    if esn_configs is None:
        esn_configs = [{'preset': 'balanced'}]
    
    results = {}
    for i, config in enumerate(esn_configs):
        config_name = config.get('name', f'config_{i+1}')
        if verbose:
            print(f"🧪 Running benchmarks for {config_name}...")
        
        esn = create_echo_state_network(**config)
        
        config_results = {}
        for benchmark in benchmarks:
            if benchmark == 'memory_capacity':
                # Generate standard test data
                np.random.seed(42)
                input_seq = np.random.uniform(-1, 1, (1000, 1))
                config_results[benchmark] = memory_capacity_benchmark(
                    esn, n_samples=1000, max_delay=20
                )
        
        results[config_name] = config_results
    
    return results

ECHO_STATE_AVAILABLE = True

# Show attribution on library import
_print_attribution()

# Package metadata
__version__ = "1.1.1"
__authors__ = ["Based on Jaeger (2001)", "Maass et al. (2002)", "Consolidated by Benedict Chen (2025)"]

# ================================
# CLEAN UNIFIED API EXPORTS
# ================================

__all__ = [
    # Core Classes - PRESERVED
    "EchoStateNetwork",
    "create_echo_state_network",
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════════════════
    "DeepEchoStateNetwork",       # ✅ REAL: Multiple reservoir layers
    "OnlineEchoStateNetwork",     # ✅ REAL: RLS online training
    "optimize_esn_hyperparameters", # ✅ REAL: Bayesian optimization
    
    # Configuration System - ALL USER CHOICE OPTIONS
    "CoreESNConfig",              # Aliased from core module
    "ESNArchitecture",
    "CoreTrainingMethod",         # Aliased from core module
    "create_deep_esn_config",
    "create_online_esn_config", 
    "create_optimized_esn_config",
    "create_task_specific_esn_config",
    
    # Configuration
    "ESNConfig",
    "ReservoirType",
    "ActivationFunction", 
    "TopologyType",
    "ReadoutType",
    "NoiseType",
    "FeedbackMode",
    "InitializationMethod",
    "TrainingMethod",
    "OptimizationObjective",
    
    # ESP Validation Utilities
    "comprehensive_esp_validation",
    "validate_spectral_radius",
    "validate_convergence",
    "validate_lyapunov",
    "validate_jacobian",
    "validate_esp_fast",
    
    # Topology Management
    "create_topology",
    "create_ring_topology",
    "create_small_world_topology",
    "create_scale_free_topology",
    "scale_spectral_radius",
    "analyze_topology",
    
    # Benchmark Suite
    "memory_capacity_benchmark",
    "nonlinear_capacity_benchmark",
    "evaluate_narma_task",
    
    # Optimization Tools
    "optimize_hyperparameters",
    "grid_search_optimization",
    "cross_validate_esn",
    "analyze_parameter_sensitivity",
    
    # Statistical Validation
    "statistical_significance_test",
    "confidence_interval",
    "performance_summary_statistics",
    
    # Visualization Functions
    "visualize_reservoir_structure",
    "visualize_reservoir_dynamics",
    "visualize_performance_analysis",
    "visualize_comparative_analysis",
    "visualize_spectral_analysis",
    "create_reservoir_animation",
    
    # Backward Compatibility
    "EchoStatePropertyValidator",
    "StructuredReservoirTopologies",
    "JaegerBenchmarkTasks",
    "OutputFeedbackESN",
    "TeacherForcingTrainer",
    "OnlineLearningESN",
    "optimize_spectral_radius",
    "validate_esp",
    "run_benchmark_suite",
    
    # Advanced Components (for power users)
    "ReservoirTheoryMixin",
    "ReservoirInitializationMixin",
    "StateUpdateMixin", 
    "TrainingMixin",
    "PredictionMixin"
]