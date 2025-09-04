"""
🎨 Modular Visualization Interface - Echo State Networks Complete Analysis
========================================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides a unified interface to all visualization capabilities
for Echo State Networks, combining network analysis, training progress,
and advanced dynamics studies.

💰 Donations: Help support this work!
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to fully support continued research

Based on comprehensive visualization research from:
- Jaeger, H. (2001) "Echo state network" 
- Lukoševičius, M. & Jaeger, H. (2009) "Reservoir computing survey"
- Verstraeten, D. et al. (2007) "Memory capacity analysis"
- Appeltant, L. et al. (2011) "Information processing capacity"
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple, Dict, Any, List, Union
import warnings
import logging

# Import modular visualization components
from ..viz_modules_2 import (
    VisualizationMixin,
    visualize_training_progress,
    visualize_reservoir_dynamics_advanced,
    visualize_comparative_analysis,
    visualize_memory_capacity
)

# Import original viz_modules for backward compatibility
from ..viz_modules import (
    visualize_reservoir_structure,
    visualize_reservoir_dynamics,
    visualize_performance_analysis,
    visualize_spectral_analysis,
    visualize_comparative_analysis as viz_comparative,
    print_reservoir_statistics,
    print_dynamics_statistics,
    print_performance_statistics,
    print_spectral_statistics,
    print_comparative_summary
)

# Configure logging
logger = logging.getLogger(__name__)

# Configure seaborn plotting style for consistent visualization
try:
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("husl")
except Exception:
    # Fallback if seaborn style not available
    plt.style.use('default')
    logger.warning("Seaborn style not available, using default matplotlib style")


class ComprehensiveVisualizationMixin(VisualizationMixin):
    """
    🎨 Comprehensive Visualization Suite for Echo State Networks
    
    Combines all visualization capabilities from both original and advanced modules
    for complete reservoir computing analysis.
    """
    
    def visualize_complete_analysis(self, 
                                  states: Optional[np.ndarray] = None,
                                  inputs: Optional[np.ndarray] = None, 
                                  outputs: Optional[np.ndarray] = None,
                                  predictions: Optional[np.ndarray] = None,
                                  targets: Optional[np.ndarray] = None,
                                  figsize: Tuple[int, int] = (20, 15),
                                  save_path: Optional[str] = None) -> None:
        """
        Complete analysis combining network structure, dynamics, and performance
        
        Args:
            states: Reservoir state matrix
            inputs: Input sequences
            outputs: Output sequences  
            predictions: Model predictions
            targets: Target values
            figsize: Figure size for visualization
            save_path: Optional path to save visualization
        """
        
        print("🎨 Generating Complete ESN Analysis Visualization...")
        print("="*60)
        
        # 1. Network structure analysis
        print("📊 Analyzing network structure...")
        if hasattr(self, 'W_reservoir'):
            self.visualize_reservoir(figsize=(15, 10))
            self.visualize_connectivity_patterns(figsize=(12, 8))
        else:
            print("⚠️  Network structure data not available")
        
        # 2. Reservoir dynamics analysis
        print("🌊 Analyzing reservoir dynamics...")
        if states is not None:
            visualize_reservoir_dynamics(states, inputs, outputs, figsize=(15, 10))
            visualize_reservoir_dynamics_advanced(states, inputs, outputs, figsize=(18, 12))
        else:
            print("⚠️  Reservoir state data not available")
        
        # 3. Performance analysis
        print("📈 Analyzing performance...")
        if predictions is not None and targets is not None:
            visualize_performance_analysis(predictions, targets, inputs, figsize=(15, 10))
        else:
            print("⚠️  Prediction/target data not available for performance analysis")
        
        # 4. Spectral analysis
        print("📊 Analyzing spectral properties...")
        if hasattr(self, 'W_reservoir'):
            visualize_spectral_analysis(self.W_reservoir, figsize=(12, 8))
        else:
            print("⚠️  Reservoir matrix not available for spectral analysis")
        
        print("✅ Complete analysis visualization finished!")
        print("="*60)
    
    def generate_analysis_report(self, 
                               states: Optional[np.ndarray] = None,
                               predictions: Optional[np.ndarray] = None,
                               targets: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report
        
        Returns:
            Dictionary containing analysis results
        """
        report = {
            'timestamp': np.datetime64('now'),
            'network_properties': {},
            'dynamics_properties': {},
            'performance_metrics': {}
        }
        
        # Network analysis
        if hasattr(self, 'W_reservoir'):
            eigenvals = np.linalg.eigvals(self.W_reservoir)
            spectral_radius = np.max(np.abs(eigenvals))
            
            report['network_properties'] = {
                'n_reservoir': self.n_reservoir if hasattr(self, 'n_reservoir') else self.W_reservoir.shape[0],
                'spectral_radius': float(spectral_radius),
                'stability': 'stable' if spectral_radius < 1.0 else 'unstable',
                'connectivity_density': float(np.mean(self.W_reservoir != 0)),
                'weight_range': [float(self.W_reservoir.min()), float(self.W_reservoir.max())]
            }
        
        # Dynamics analysis  
        if states is not None:
            report['dynamics_properties'] = {
                'time_steps': int(states.shape[0]),
                'activity_range': [float(states.min()), float(states.max())],
                'mean_activity': float(states.mean()),
                'activity_std': float(states.std()),
                'most_active_neuron': int(np.argmax(np.mean(states, axis=0))),
                'least_active_neuron': int(np.argmin(np.mean(states, axis=0)))
            }
        
        # Performance analysis
        if predictions is not None and targets is not None:
            errors = predictions - targets
            mse = float(np.mean(errors**2))
            mae = float(np.mean(np.abs(errors)))
            
            # Calculate R²
            if len(targets.flatten()) > 1:
                ss_res = np.sum((targets.flatten() - predictions.flatten())**2)
                ss_tot = np.sum((targets.flatten() - np.mean(targets.flatten()))**2)
                r2 = float(1 - (ss_res / (ss_tot + 1e-8)))
            else:
                r2 = 0.0
                
            report['performance_metrics'] = {
                'mse': mse,
                'mae': mae,
                'rmse': float(np.sqrt(mse)),
                'r2': r2,
                'error_std': float(errors.std()),
                'error_range': [float(errors.min()), float(errors.max())]
            }
        
        return report
    
    def print_complete_statistics(self,
                                states: Optional[np.ndarray] = None,
                                predictions: Optional[np.ndarray] = None,
                                targets: Optional[np.ndarray] = None) -> None:
        """
        Print comprehensive statistics from all modules
        """
        print("\\n" + "="*80)
        print("🎨 COMPREHENSIVE ESN ANALYSIS STATISTICS")
        print("="*80)
        
        # Network statistics
        if hasattr(self, 'W_reservoir'):
            input_weights = getattr(self, 'W_in', None)
            output_weights = getattr(self, 'W_out', None)
            print_reservoir_statistics(self.W_reservoir, input_weights, output_weights)
        
        # Dynamics statistics
        if states is not None:
            print_dynamics_statistics(states)
        
        # Performance statistics  
        if predictions is not None and targets is not None:
            errors = predictions - targets
            print_performance_statistics(predictions, targets, errors)
        
        # Spectral statistics
        if hasattr(self, 'W_reservoir'):
            print_spectral_statistics(self.W_reservoir)
        
        print("="*80)


# Convenience functions for direct usage
def create_comprehensive_visualization(esn_model, 
                                     states: Optional[np.ndarray] = None,
                                     inputs: Optional[np.ndarray] = None,
                                     predictions: Optional[np.ndarray] = None,
                                     targets: Optional[np.ndarray] = None,
                                     save_base_path: Optional[str] = None) -> None:
    """
    Create comprehensive visualization for an ESN model
    
    Args:
        esn_model: Echo State Network model with visualization capabilities
        states: Reservoir states
        inputs: Input sequences
        predictions: Model predictions  
        targets: Target values
        save_base_path: Base path for saving visualizations
    """
    
    if not hasattr(esn_model, 'visualize_complete_analysis'):
        # Add visualization capabilities if not present
        esn_model.__class__ = type(esn_model.__class__.__name__, 
                                 (esn_model.__class__, ComprehensiveVisualizationMixin), 
                                 {})
    
    # Generate complete analysis
    save_path = f"{save_base_path}_complete_analysis.png" if save_base_path else None
    esn_model.visualize_complete_analysis(
        states=states,
        inputs=inputs,
        predictions=predictions,
        targets=targets,
        save_path=save_path
    )
    
    # Generate report
    report = esn_model.generate_analysis_report(states, predictions, targets)
    
    # Print statistics
    esn_model.print_complete_statistics(states, predictions, targets)
    
    return report


# Backward compatibility - expose all original functions
__all__ = [
    # Classes
    'ComprehensiveVisualizationMixin',
    'VisualizationMixin',
    
    # Advanced visualization functions  
    'visualize_training_progress',
    'visualize_reservoir_dynamics_advanced',
    'visualize_comparative_analysis',
    'visualize_memory_capacity',
    
    # Original visualization functions
    'visualize_reservoir_structure',
    'visualize_reservoir_dynamics', 
    'visualize_performance_analysis',
    'visualize_spectral_analysis',
    'viz_comparative',
    
    # Statistics functions
    'print_reservoir_statistics',
    'print_dynamics_statistics',
    'print_performance_statistics', 
    'print_spectral_statistics',
    'print_comparative_summary',
    
    # Convenience functions
    'create_comprehensive_visualization'
]


# Banner message
print("""
🌊 Reservoir Computing Visualization Suite Loaded Successfully
==============================================================
  
💡 Complete ESN Analysis Tools Available:
   📊 Network Structure Analysis
   🌊 Reservoir Dynamics Visualization  
   📈 Training Progress Analysis
   🔬 Advanced Dynamics Studies
   📊 Spectral Properties Analysis
   📈 Performance Evaluation
   🔄 Comparative Analysis
   🧠 Memory Capacity Testing

💰 Support This Research:
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Consider recurring donations to continue this work

Author: Benedict Chen (benedict@benedictchen.com)
==============================================================
""")