"""
Reservoir Computing Core - Modular Implementation
================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides backward-compatible access to reservoir computing functionality
through a modular architecture. The original 1405-line core.py file has been split
into focused modules for better maintainability.

Original file: old_archive/core_original_1405_lines.py

Based on:
- Herbert Jaeger (2001): "The 'Echo State' Approach to Analysing and Training RNNs"
- Wolfgang Maass (2002): "Real-time Computing Without Stable States"
"""

# Import all components from modular structure for backward compatibility
from .core_modules.reservoir_theory import ReservoirTheoryMixin
from .core_modules.reservoir_initialization import ReservoirInitializationMixin
from .core_modules.state_updates import StateUpdateMixin
from .core_modules.training_methods import TrainingMixin
from .core_modules.prediction_generation import PredictionMixin
from .core_modules.echo_state_network import EchoStateNetwork

# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════

# Import real implementations - NO MORE FAKE CODE
from .advanced_esn_implementations import (
    DeepEchoStateNetwork,
    OnlineEchoStateNetwork, 
    create_echo_state_network,
    optimize_esn_hyperparameters
)

# Import configuration system for user choice
from .esn_config import (
    ESNConfig,
    ESNArchitecture, 
    TrainingMethod,
    create_deep_esn_config,
    create_online_esn_config,
    create_optimized_esn_config,
    create_task_specific_esn_config
)

# Export all classes and functions for backward compatibility
__all__ = [
    # Core mixins - PRESERVED
    'ReservoirTheoryMixin',
    'ReservoirInitializationMixin',
    'StateUpdateMixin',
    'TrainingMixin', 
    'PredictionMixin',
    
    # Network classes - ALL REAL IMPLEMENTATIONS (NO MORE FAKE CODE)
    'EchoStateNetwork',
    'DeepEchoStateNetwork',      # ✅ REAL: Multiple reservoir layers
    'OnlineEchoStateNetwork',    # ✅ REAL: RLS online training
    
    # Factory functions - ALL REAL IMPLEMENTATIONS  
    'create_echo_state_network',      # ✅ REAL: Task-specific ESN creation
    'optimize_esn_hyperparameters',   # ✅ REAL: Bayesian optimization
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🔬 NEW: COMPLETE CONFIGURATION SYSTEM - ALL USER CHOICE OPTIONS
    # ═══════════════════════════════════════════════════════════════════════════
    'ESNConfig',
    'ESNArchitecture',
    'TrainingMethod', 
    'create_deep_esn_config',
    'create_online_esn_config',
    'create_optimized_esn_config',
    'create_task_specific_esn_config'
]

# Modularization Summary:
# ======================
# Original core.py (1405 lines) split into:
# 1. reservoir_theory.py (346 lines) - Mathematical foundations
# 2. reservoir_initialization.py (99 lines) - Weight matrix initialization  
# 3. state_updates.py (85 lines) - Reservoir state dynamics
# 4. training_methods.py (147 lines) - Linear readout training
# 5. prediction_generation.py (157 lines) - Forward and autonomous prediction
# 6. echo_state_network.py (152 lines) - Main ESN class
#
# Core reservoir computing implementation
# Based on Echo State Networks (Jaeger 2001)
# Benefits: Better organization, easier testing, focused responsibilities