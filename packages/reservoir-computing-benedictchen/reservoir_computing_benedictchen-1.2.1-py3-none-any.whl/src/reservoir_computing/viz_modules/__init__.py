"""
🎨 Visualization Modules - Modular Reservoir Computing Visualization
====================================================================

Author: Benedict Chen (benedict@benedictchen.com)

Modular visualization components extracted from the original monolithic viz.py file.
Each module focuses on specific visualization domains for better organization and maintainability.

🏗️ **Modular Architecture:**
- structure_visualization.py - Reservoir architecture and connectivity analysis
- dynamics_visualization.py - Temporal behavior and state evolution analysis  
- performance_visualization.py - Model quality and error analysis
- comparative_visualization.py - Multi-configuration comparisons
- spectral_visualization.py - Advanced spectral analysis and stability
- animation_utilities.py - Animations and utility functions

📊 **Benefits of Modularization:**
- Visualization functions for reservoir analysis
- Logical separation by visualization domain
- Improved maintainability and testing
- Specialized imports for better performance
- Clean separation of concerns

🎯 **Usage Examples:**
```python
from viz_modules import visualize_reservoir_structure, visualize_dynamics
from viz_modules import visualize_performance_analysis, create_reservoir_animation

# Use specific visualization functions
visualize_reservoir_structure(W_reservoir, sparsity=0.1)
visualize_dynamics(states, inputs=X_test)
visualize_performance_analysis(predictions, targets)
```
"""

from .structure_visualization import (
    visualize_reservoir_structure,
    print_reservoir_statistics
)

from .dynamics_visualization import (
    visualize_reservoir_dynamics, 
    print_dynamics_statistics
)

from .performance_visualization import (
    visualize_performance_analysis,
    print_performance_statistics
)

from .spectral_visualization import (
    visualize_spectral_analysis,
    print_spectral_statistics
)

from .comparative_visualization import (
    visualize_comparative_analysis,
    print_comparative_summary
)

__all__ = [
    # Structure visualization
    'visualize_reservoir_structure',
    'print_reservoir_statistics',
    
    # Dynamics visualization
    'visualize_reservoir_dynamics',
    'print_dynamics_statistics', 
    
    # Performance visualization
    'visualize_performance_analysis',
    'print_performance_statistics',
    
    # Spectral visualization
    'visualize_spectral_analysis',
    'print_spectral_statistics',
    
    # Comparative visualization
    'visualize_comparative_analysis',
    'print_comparative_summary'
]