"""
Echo State Network - Modular Components
======================================

🌊 This module contains the modular components for Echo State Network implementation.
Based on: Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"

Components:
- esn_core.py: Core ESN class and functionality
- configuration_optimization.py: Hyperparameter optimization and benchmarks
- topology_management.py: Reservoir topology and structure management
- visualization.py: Plotting and analysis tools

🎯 ELI5: Think of this like a LEGO set for building smart memory networks!
Each module is a different type of LEGO piece that helps build networks that can
remember patterns in sequences (like predicting the next word in a sentence).
"""

# Import REAL ESN implementation directly - no fallbacks!
from .esn_core import (
    EchoStateNetwork,
    ReservoirInitializationMixin
)
from .esp_validation import EspValidationMixin  
from .state_updates import StateUpdatesMixin
from .training_methods import TrainingMethodsMixin
from .prediction_generation import PredictionGenerationMixin
from .topology_management import TopologyManagementMixin
from .configuration_optimization import ConfigurationOptimizationMixin
from .visualization import VisualizationMixin

def create_echo_state_network(*args, **kwargs):
    """Factory function to create EchoStateNetwork with flexible parameters"""
    return EchoStateNetwork(*args, **kwargs)

CORE_AVAILABLE = True

# Import configuration and optimization tools - NO FAKE FALLBACKS!
from .configuration_optimization import (
    ConfigurationOptimizationMixin,
    optimize_spectral_radius,
    run_benchmark_suite
)

# Import topology management - NO FAKE FALLBACKS!
from .topology_management import TopologyManagementMixin

# Import visualization tools - NO FAKE FALLBACKS!
from .visualization import VisualizationMixin

# All components are available since we use direct imports
CONFIG_AVAILABLE = True
TOPOLOGY_AVAILABLE = True
VIZ_AVAILABLE = True

__all__ = [
    # Core classes
    "EchoStateNetwork",
    "create_echo_state_network",
    
    # Mixin classes
    "ReservoirInitializationMixin",
    "EspValidationMixin", 
    "StateUpdatesMixin",
    "TrainingMethodsMixin",
    "PredictionGenerationMixin",
    "TopologyManagementMixin",
    "ConfigurationOptimizationMixin",
    "VisualizationMixin",
    
    # Utility functions
    "optimize_spectral_radius",
    "validate_esp",
    "run_benchmark_suite",
    
    # Status flags
    "CORE_AVAILABLE",
    "CONFIG_AVAILABLE", 
    "TOPOLOGY_AVAILABLE",
    "VIZ_AVAILABLE"
]