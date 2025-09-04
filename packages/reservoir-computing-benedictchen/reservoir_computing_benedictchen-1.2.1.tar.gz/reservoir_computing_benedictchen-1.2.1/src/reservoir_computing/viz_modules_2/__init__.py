"""
🎨 Advanced Visualization Modules - Complete ESN Analysis Suite
=============================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides comprehensive visualization tools for analyzing Echo State Networks
from the original visualization.py file, focusing on training progress, network analysis,
and comparative studies.

Based on research from:
- Jaeger, H. (2001) "Echo state network" 
- Lukoševičius, M. & Jaeger, H. (2009) "Reservoir computing survey"
- Verstraeten, D. et al. (2007) "Memory capacity analysis"
"""

from .network_visualization import VisualizationMixin
from .training_visualization import visualize_training_progress
from .advanced_analysis import (
    visualize_reservoir_dynamics_advanced,
    visualize_comparative_analysis,
    visualize_memory_capacity
)

__all__ = [
    'VisualizationMixin',
    'visualize_training_progress',
    'visualize_reservoir_dynamics_advanced', 
    'visualize_comparative_analysis',
    'visualize_memory_capacity'
]