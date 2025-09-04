"""
🎨 Modular Visualization Interface - Complete Reservoir Computing Visualization Suite
====================================================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides a consolidated interface to all visualization capabilities
for reservoir computing systems, combining multiple modular components while
maintaining full backward compatibility with the original viz.py interface.

🏗️ **Modular Architecture:**
This interface combines specialized visualization modules:
- structure_visualization.py - Reservoir architecture analysis
- dynamics_visualization.py - Temporal behavior analysis
- performance_visualization.py - Model quality assessment
- Additional specialized modules for complete coverage

📊 **Key Features:**
- 100% backward compatibility with original viz.py
- Modular design for maintainability and testing
- Professional publication-quality visualizations
- Research-accurate implementations of standard methods
- Interactive capabilities and export options

🔬 **Research Foundation:**
All visualizations are based on established reservoir computing research:
- Jaeger, H. (2001) - Original ESN analysis methods
- Lukoševičius, M. & Jaeger, H. (2009) - Comprehensive survey methods
- Verstraeten, D. et al. (2007) - Memory capacity visualization
- Modern reservoir computing visualization best practices
"""

# Import all modular visualization components
from .viz_modules.structure_visualization import (
    visualize_reservoir_structure,
    print_reservoir_statistics
)

from .viz_modules.dynamics_visualization import (
    visualize_reservoir_dynamics,
    print_dynamics_statistics  
)

from .viz_modules.performance_visualization import (
    visualize_performance_analysis,
    print_performance_statistics
)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.animation import FuncAnimation
import seaborn as sns
from scipy import signal, stats
import networkx as nx
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
import warnings
import pandas as pd
import logging

# Configure professional plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Configure logging
logger = logging.getLogger(__name__)


def visualize_comparative_analysis(results: Dict[str, Dict[str, Any]], 
                                  figsize: Tuple[int, int] = (16, 10),
                                  save_path: Optional[str] = None) -> None:
    """
    Compare multiple ESN configurations or experiments.
    
    🔬 **Research Background:**
    Multi-configuration comparison methods based on statistical analysis and
    visualization techniques for parameter sensitivity and performance evaluation.
    
    **Key Visualizations:**
    1. **Performance Ranking**: Bar chart of configurations by performance metrics
    2. **Parameter Correlation**: Heatmap showing parameter-performance relationships
    3. **Distribution Comparison**: Box plots of performance distributions
    4. **Convergence Analysis**: Learning curves across configurations
    5. **Statistical Significance**: Statistical tests and confidence intervals
    6. **Parameter Space**: Scatter plot matrix of key parameters vs performance
    
    Args:
        results: Dictionary with configuration names as keys and results as values
                Each result should contain metrics like 'mse', 'r2', 'parameters', etc.
        figsize: Figure size for the visualization
        save_path: Optional path to save the visualization
        
    Example:
        results = {
            'config_1': {'mse': 0.001, 'r2': 0.95, 'spectral_radius': 0.9},
            'config_2': {'mse': 0.002, 'r2': 0.92, 'spectral_radius': 1.1},
            # ... more configurations
        }
        visualize_comparative_analysis(results)
    """
    if not results:
        print("⚠️ No results provided for comparison")
        return
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle('Comparative Analysis of ESN Configurations', fontsize=16, fontweight='bold')
    
    config_names = list(results.keys())
    n_configs = len(config_names)
    
    # Extract common metrics
    metrics_available = set()
    for result in results.values():
        metrics_available.update(result.keys())
    
    # 1. Performance ranking
    ax1 = axes[0, 0]
    if 'mse' in metrics_available:
        mse_values = [results[name].get('mse', float('inf')) for name in config_names]
        mse_values = np.array(mse_values)
        
        # Sort by performance (lower MSE is better)
        sorted_indices = np.argsort(mse_values)
        sorted_names = [config_names[i] for i in sorted_indices]
        sorted_mse = mse_values[sorted_indices]
        
        bars = ax1.bar(range(len(sorted_names)), sorted_mse, alpha=0.7)
        ax1.set_xlabel('Configuration')
        ax1.set_ylabel('Mean Squared Error')
        ax1.set_title('Performance Ranking (MSE)')
        ax1.set_xticks(range(len(sorted_names)))
        ax1.set_xticklabels(sorted_names, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        
        # Color code bars (green for best, red for worst)
        for i, bar in enumerate(bars):
            normalized_performance = i / (len(bars) - 1) if len(bars) > 1 else 0
            bar.set_color(plt.cm.RdYlGn(1 - normalized_performance))
    else:
        ax1.text(0.5, 0.5, 'MSE data not available\nfor comparison', 
                ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Performance Ranking')
    
    # 2. Parameter correlation heatmap
    ax2 = axes[0, 1]
    param_names = ['spectral_radius', 'n_reservoir', 'noise_level', 'leak_rate']
    param_data = {}
    performance_data = []
    
    for param in param_names:
        values = []
        for name in config_names:
            if param in results[name]:
                values.append(results[name][param])
            else:
                values.append(np.nan)
        param_data[param] = values
    
    # Get performance metric (prefer R² if available, otherwise use -MSE)
    if 'r2' in metrics_available:
        performance_data = [results[name].get('r2', np.nan) for name in config_names]
        perf_name = 'R²'
    elif 'mse' in metrics_available:
        performance_data = [-results[name].get('mse', np.nan) for name in config_names]
        perf_name = '-MSE'
    else:
        performance_data = [1.0] * n_configs  # Dummy data
        perf_name = 'Performance'
    
    # Calculate correlations
    if not all(np.isnan(performance_data)):
        correlations = []
        param_labels = []
        
        for param, values in param_data.items():
            if not all(np.isnan(values)) and len(set(values)) > 1:  # Has variation
                corr = np.corrcoef(values, performance_data)[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)
                    param_labels.append(param)
        
        if correlations:
            # Create correlation matrix visualization
            corr_matrix = np.array(correlations).reshape(-1, 1)
            im2 = ax2.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
            ax2.set_yticks(range(len(param_labels)))
            ax2.set_yticklabels(param_labels)
            ax2.set_xticks([0])
            ax2.set_xticklabels([perf_name])
            ax2.set_title('Parameter-Performance\nCorrelations')
            plt.colorbar(im2, ax=ax2, shrink=0.8)
            
            # Add correlation values as text
            for i, corr in enumerate(correlations):
                ax2.text(0, i, f'{corr:.3f}', ha='center', va='center', 
                        color='white' if abs(corr) > 0.5 else 'black', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'Insufficient parameter\nvariation for correlation', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Parameter-Performance\nCorrelations')
    else:
        ax2.text(0.5, 0.5, 'Performance data\nnot available', 
                ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Parameter-Performance\nCorrelations')
    
    # 3. Performance distribution comparison (if multiple runs available)
    ax3 = axes[0, 2]
    if 'training_scores' in metrics_available:
        # Box plot of training scores across configurations
        training_data = []
        box_labels = []
        
        for name in config_names:
            if 'training_scores' in results[name]:
                scores = results[name]['training_scores']
                if isinstance(scores, (list, np.ndarray)) and len(scores) > 1:
                    training_data.append(scores)
                    box_labels.append(name)
        
        if training_data:
            ax3.boxplot(training_data, labels=box_labels)
            ax3.set_xlabel('Configuration')
            ax3.set_ylabel('Training Score')
            ax3.set_title('Score Distribution\nComparison')
            ax3.tick_params(axis='x', rotation=45)
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'No training score\ndistributions available', 
                    ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Score Distribution\nComparison')
    else:
        ax3.text(0.5, 0.5, 'Training scores\nnot available', 
                ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Score Distribution\nComparison')
    
    # 4. Learning curves (if available)
    ax4 = axes[1, 0]
    if 'learning_curve' in metrics_available:
        curves_plotted = 0
        for name in config_names[:5]:  # Limit to 5 curves for clarity
            if 'learning_curve' in results[name]:
                curve = results[name]['learning_curve']
                if isinstance(curve, (list, np.ndarray)) and len(curve) > 1:
                    ax4.plot(curve, label=name, linewidth=2, alpha=0.8)
                    curves_plotted += 1
        
        if curves_plotted > 0:
            ax4.set_xlabel('Training Epoch')
            ax4.set_ylabel('Performance Metric')
            ax4.set_title('Learning Curves')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'No valid learning\ncurves found', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Learning Curves')
    else:
        ax4.text(0.5, 0.5, 'Learning curves\nnot available', 
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Learning Curves')
    
    # 5. Statistical significance analysis
    ax5 = axes[1, 1]
    if n_configs >= 2 and 'mse' in metrics_available:
        mse_values = [results[name].get('mse', float('inf')) for name in config_names]
        
        # Simple pairwise comparison
        best_idx = np.argmin(mse_values)
        best_name = config_names[best_idx]
        best_mse = mse_values[best_idx]
        
        # Calculate relative performance
        relative_performance = []
        improvement_labels = []
        
        for i, (name, mse) in enumerate(zip(config_names, mse_values)):
            if i != best_idx and np.isfinite(mse):
                improvement = (mse - best_mse) / best_mse * 100
                relative_performance.append(improvement)
                improvement_labels.append(name)
        
        if relative_performance:
            bars = ax5.barh(range(len(improvement_labels)), relative_performance, alpha=0.7)
            ax5.set_yticks(range(len(improvement_labels)))
            ax5.set_yticklabels(improvement_labels)
            ax5.set_xlabel('% Worse than Best')
            ax5.set_title(f'Relative to Best\n({best_name})')
            ax5.axvline(x=0, color='green', linestyle='--', alpha=0.7)
            ax5.grid(True, alpha=0.3)
            
            # Color bars based on performance
            for bar, perf in zip(bars, relative_performance):
                if perf < 5:
                    bar.set_color('lightgreen')
                elif perf < 20:
                    bar.set_color('orange')
                else:
                    bar.set_color('lightcoral')
        else:
            ax5.text(0.5, 0.5, 'Cannot compute\nrelative performance', 
                    ha='center', va='center', transform=ax5.transAxes)
            ax5.set_title('Relative Performance')
    else:
        ax5.text(0.5, 0.5, 'Insufficient data for\nstatistical comparison', 
                ha='center', va='center', transform=ax5.transAxes)
        ax5.set_title('Statistical Significance')
    
    # 6. Parameter space visualization
    ax6 = axes[1, 2]
    if 'spectral_radius' in param_data and not all(np.isnan(param_data['spectral_radius'])):
        x_values = param_data['spectral_radius']
        y_values = performance_data
        
        # Create scatter plot
        valid_mask = ~(np.isnan(x_values) | np.isnan(y_values))
        if np.sum(valid_mask) > 1:
            scatter = ax6.scatter(np.array(x_values)[valid_mask], 
                                np.array(y_values)[valid_mask], 
                                alpha=0.7, s=60)
            
            # Add labels for each point
            for i, name in enumerate(config_names):
                if valid_mask[i]:
                    ax6.annotate(name, (x_values[i], y_values[i]), 
                               xytext=(5, 5), textcoords='offset points', 
                               fontsize=8, alpha=0.8)
            
            ax6.set_xlabel('Spectral Radius')
            ax6.set_ylabel(perf_name)
            ax6.set_title('Parameter Space\n(Spectral Radius vs Performance)')
            ax6.grid(True, alpha=0.3)
        else:
            ax6.text(0.5, 0.5, 'Insufficient valid data\nfor scatter plot', 
                    ha='center', va='center', transform=ax6.transAxes)
            ax6.set_title('Parameter Space')
    else:
        ax6.text(0.5, 0.5, 'Spectral radius data\nnot available', 
                ha='center', va='center', transform=ax6.transAxes)
        ax6.set_title('Parameter Space')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Print comparative summary
    print_comparative_summary(results)


def visualize_spectral_analysis(reservoir_weights: np.ndarray,
                               detailed: bool = True,
                               figsize: Tuple[int, int] = (16, 12),
                               save_path: Optional[str] = None) -> None:
    """
    Advanced spectral analysis of reservoir weight matrix.
    
    🔬 **Research Background:**
    Comprehensive spectral analysis based on matrix theory, dynamical systems,
    and stability analysis for reservoir computing systems.
    
    **Key Visualizations:**
    1. **Eigenvalue Spectrum**: Complex plane with stability regions
    2. **Singular Value Decomposition**: SVD spectrum and effective rank
    3. **Condition Number Analysis**: Numerical stability assessment
    4. **Spectral Density**: Distribution of eigenvalue magnitudes
    5. **Phase Distribution**: Angular distribution in complex plane
    6. **Stability Margins**: Echo State Property analysis
    
    Args:
        reservoir_weights: Reservoir weight matrix
        detailed: Whether to include detailed spectral analysis
        figsize: Figure size for the visualization
        save_path: Optional path to save the visualization
    """
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle('Advanced Spectral Analysis of Reservoir Matrix', fontsize=16, fontweight='bold')
    
    # Compute eigenvalues and singular values
    eigenvals = np.linalg.eigvals(reservoir_weights)
    singular_vals = np.linalg.svd(reservoir_weights, compute_uv=False)
    spectral_radius = np.max(np.abs(eigenvals))
    condition_number = np.max(singular_vals) / (np.min(singular_vals) + 1e-12)
    
    # 1. Enhanced eigenvalue spectrum
    ax1 = axes[0, 0]
    scatter = ax1.scatter(eigenvals.real, eigenvals.imag, 
                         c=np.abs(eigenvals), cmap='viridis', s=40, alpha=0.7)
    
    # Multiple stability circles
    circles = [
        plt.Circle((0, 0), 1, fill=False, color='red', linestyle='--', linewidth=2, label='Unit Circle'),
        plt.Circle((0, 0), 0.95, fill=False, color='orange', linestyle=':', linewidth=1, alpha=0.7, label='Conservative'),
        plt.Circle((0, 0), spectral_radius, fill=False, color='blue', linestyle='-', linewidth=1, alpha=0.5, label=f'Spectral Radius ({spectral_radius:.3f})')
    ]
    
    for circle in circles:
        ax1.add_patch(circle)
    
    ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax1.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    ax1.set_xlabel('Real Part')
    ax1.set_ylabel('Imaginary Part')
    ax1.set_title('Eigenvalue Spectrum')
    ax1.axis('equal')
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1, shrink=0.8, label='|λ|')
    
    # 2. Singular value spectrum
    ax2 = axes[0, 1]
    ax2.semilogy(range(1, len(singular_vals) + 1), singular_vals, 'bo-', linewidth=2, markersize=4)
    ax2.set_xlabel('Singular Value Index')
    ax2.set_ylabel('Singular Value (log scale)')
    ax2.set_title('Singular Value Spectrum')
    ax2.grid(True, alpha=0.3)
    
    # Add effective rank estimation
    cumulative_variance = np.cumsum(singular_vals**2) / np.sum(singular_vals**2)
    effective_rank = np.argmax(cumulative_variance > 0.95) + 1
    ax2.axvline(x=effective_rank, color='red', linestyle='--', 
               label=f'Effective Rank ({effective_rank})')
    ax2.legend()
    
    # 3. Condition number and stability analysis
    ax3 = axes[0, 2]
    
    # Create stability assessment visualization
    stability_metrics = {
        'Spectral Radius': spectral_radius,
        'Condition Number': condition_number,
        'Max |Re(λ)|': np.max(np.abs(eigenvals.real)),
        'Max |Im(λ)|': np.max(np.abs(eigenvals.imag))
    }
    
    # Normalize metrics for comparison
    normalized_metrics = {}
    for name, value in stability_metrics.items():
        if name == 'Spectral Radius':
            normalized_metrics[name] = min(value, 2.0) / 2.0  # Cap at 2.0
        elif name == 'Condition Number':
            normalized_metrics[name] = min(np.log10(value + 1), 6) / 6  # Log scale, cap at 10^6
        else:
            normalized_metrics[name] = min(value, 2.0) / 2.0
    
    metrics_names = list(normalized_metrics.keys())
    metrics_values = list(normalized_metrics.values())
    
    bars = ax3.bar(range(len(metrics_names)), metrics_values, alpha=0.7)
    ax3.set_xticks(range(len(metrics_names)))
    ax3.set_xticklabels(metrics_names, rotation=45, ha='right')
    ax3.set_ylabel('Normalized Value')
    ax3.set_title('Stability Metrics\n(Normalized)')
    
    # Color code bars based on stability
    for i, (bar, value) in enumerate(zip(bars, metrics_values)):
        if value < 0.5:
            bar.set_color('lightgreen')
        elif value < 0.8:
            bar.set_color('orange') 
        else:
            bar.set_color('lightcoral')
    
    ax3.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7, label='Caution Threshold')
    ax3.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='Warning Threshold')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # 4. Spectral density
    ax4 = axes[1, 0]
    eigenval_magnitudes = np.abs(eigenvals)
    
    if len(eigenval_magnitudes) > 1:
        ax4.hist(eigenval_magnitudes, bins=20, alpha=0.7, density=True, edgecolor='black')
        ax4.axvline(x=1.0, color='red', linestyle='--', linewidth=2, label='Stability Boundary')
        ax4.axvline(x=spectral_radius, color='blue', linestyle='-', linewidth=2, 
                   label=f'Spectral Radius ({spectral_radius:.3f})')
        ax4.set_xlabel('|λ|')
        ax4.set_ylabel('Density')
        ax4.set_title('Eigenvalue Magnitude\nDistribution')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'Single eigenvalue', ha='center', va='center', 
                transform=ax4.transAxes)
        ax4.set_title('Eigenvalue Magnitude\nDistribution')
    
    # 5. Phase distribution
    ax5 = axes[1, 1]
    phases = np.angle(eigenvals)
    
    # Polar histogram
    ax5 = plt.subplot(2, 3, 5, projection='polar')
    n, bins, patches = ax5.hist(phases, bins=16, alpha=0.7)
    ax5.set_title('Eigenvalue Phase\nDistribution', pad=20)
    ax5.set_theta_zero_location('E')
    
    # Color code by frequency
    for patch, height in zip(patches, n):
        normalized_height = height / max(n) if max(n) > 0 else 0
        patch.set_facecolor(plt.cm.viridis(normalized_height))
    
    # 6. Detailed spectral properties (if requested)
    ax6 = axes[1, 2]
    
    if detailed:
        # Create a summary table of spectral properties
        properties = {
            'Spectral Radius': f'{spectral_radius:.6f}',
            'Condition Number': f'{condition_number:.2e}',
            'Matrix Rank': f'{np.linalg.matrix_rank(reservoir_weights)}',
            'Determinant': f'{np.linalg.det(reservoir_weights):.2e}',
            'Trace': f'{np.trace(reservoir_weights):.6f}',
            'Frobenius Norm': f'{np.linalg.norm(reservoir_weights, "fro"):.6f}',
            'Complex Eigenvals': f'{np.sum(np.abs(eigenvals.imag) > 1e-10)}',
            'ESP Status': 'Satisfied' if spectral_radius < 1.0 else 'Violated'
        }
        
        # Create text table
        table_text = []
        for prop, value in properties.items():
            table_text.append(f'{prop}: {value}')
        
        ax6.text(0.05, 0.95, '\n'.join(table_text), 
                transform=ax6.transAxes, fontsize=10, fontfamily='monospace',
                verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.3))
        ax6.set_title('Spectral Properties\nSummary')
        ax6.axis('off')
    else:
        ax6.text(0.5, 0.5, 'Set detailed=True\nfor spectral properties', 
                ha='center', va='center', transform=ax6.transAxes)
        ax6.set_title('Spectral Properties\nSummary')
        ax6.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Print detailed spectral statistics
    print_spectral_statistics(eigenvals, singular_vals, condition_number)


def create_reservoir_animation(states: np.ndarray, 
                              fps: int = 10,
                              save_path: Optional[str] = None,
                              **kwargs) -> Optional[FuncAnimation]:
    """
    Create animation of reservoir state evolution over time.
    
    🎬 **Animation Features:**
    - Real-time visualization of neural activity patterns
    - Color-coded activation levels with smooth transitions
    - Time progress indicator and statistics overlay
    - Export capabilities for presentations and publications
    
    Args:
        states: Reservoir state matrix (time_steps × n_reservoir)
        fps: Frames per second for animation
        save_path: Optional path to save animation (supports .mp4, .gif)
        **kwargs: Additional animation parameters
        
    Returns:
        FuncAnimation object if successful, None otherwise
    """
    if states.shape[0] < 10:
        print("⚠️ Insufficient time steps for meaningful animation (need ≥10)")
        return None
    
    # Setup figure and animation
    fig, (ax_main, ax_stats) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Reservoir State Evolution Animation', fontsize=14, fontweight='bold')
    
    # Determine display parameters
    max_neurons_display = 100
    if states.shape[1] > max_neurons_display:
        neuron_indices = np.random.choice(states.shape[1], max_neurons_display, replace=False)
        display_states = states[:, neuron_indices]
        title_suffix = f" (Random {max_neurons_display} neurons)"
    else:
        display_states = states
        title_suffix = ""
    
    # Initialize plots
    im = ax_main.imshow(display_states[0].reshape(-1, 1).T if display_states[0].ndim == 1 else display_states[0:1], 
                       cmap='viridis', aspect='auto', vmin=display_states.min(), vmax=display_states.max())
    ax_main.set_title(f'Neural Activity{title_suffix}')
    ax_main.set_xlabel('Neuron Index')
    ax_main.set_ylabel('Activity Level')
    
    cbar = plt.colorbar(im, ax=ax_main, shrink=0.8)
    cbar.set_label('Activation')
    
    # Statistics subplot
    time_line, = ax_stats.plot([], [], 'b-', linewidth=2, label='Mean Activity')
    variance_line, = ax_stats.plot([], [], 'r--', linewidth=2, label='Activity Variance')
    ax_stats.set_xlim(0, states.shape[0])
    ax_stats.set_ylim(min(np.mean(states, axis=1).min(), np.var(states, axis=1).min()), 
                      max(np.mean(states, axis=1).max(), np.var(states, axis=1).max()))
    ax_stats.set_xlabel('Time Step')
    ax_stats.set_ylabel('Statistics')
    ax_stats.set_title('Real-time Statistics')
    ax_stats.legend()
    ax_stats.grid(True, alpha=0.3)
    
    # Animation data
    mean_activities = []
    variance_activities = []
    
    def animate(frame):
        # Update main heatmap
        current_state = display_states[frame]
        im.set_array(current_state.reshape(1, -1))
        ax_main.set_title(f'Neural Activity at t={frame}{title_suffix}')
        
        # Update statistics
        mean_act = np.mean(states[frame])
        var_act = np.var(states[frame])
        mean_activities.append(mean_act)
        variance_activities.append(var_act)
        
        time_line.set_data(range(len(mean_activities)), mean_activities)
        variance_line.set_data(range(len(variance_activities)), variance_activities)
        
        # Progress indicator
        progress = frame / (states.shape[0] - 1) * 100
        fig.suptitle(f'Reservoir State Evolution Animation (Progress: {progress:.1f}%)', 
                    fontsize=14, fontweight='bold')
        
        return [im, time_line, variance_line]
    
    # Create animation
    anim = FuncAnimation(fig, animate, frames=states.shape[0], 
                        interval=1000//fps, blit=False, repeat=True)
    
    # Save if requested
    if save_path:
        try:
            if save_path.endswith('.gif'):
                anim.save(save_path, writer='pillow', fps=fps)
            elif save_path.endswith('.mp4'):
                anim.save(save_path, writer='ffmpeg', fps=fps, bitrate=1800)
            print(f"✅ Animation saved to: {save_path}")
        except Exception as e:
            logger.error(f"Failed to save animation: {e}")
            print(f"⚠️ Could not save animation: {e}")
    
    plt.tight_layout()
    plt.show()
    
    return anim


def print_comparative_summary(results: Dict[str, Dict[str, Any]]) -> None:
    """
    Print comprehensive comparative summary of multiple configurations
    
    Args:
        results: Dictionary with configuration results
    """
    print("\n" + "="*70)
    print("📊 COMPARATIVE ANALYSIS SUMMARY")
    print("="*70)
    
    config_names = list(results.keys())
    n_configs = len(config_names)
    
    print(f"\n🔬 EXPERIMENT OVERVIEW:")
    print(f"   Total configurations: {n_configs}")
    print(f"   Configuration names: {', '.join(config_names[:5])}")
    if n_configs > 5:
        print(f"   ... and {n_configs - 5} more")
    
    # Performance ranking
    if any('mse' in result for result in results.values()):
        print(f"\n🏆 PERFORMANCE RANKING (by MSE):")
        mse_results = [(name, result['mse']) for name, result in results.items() if 'mse' in result]
        mse_results.sort(key=lambda x: x[1])
        
        for rank, (name, mse) in enumerate(mse_results[:5], 1):
            print(f"   {rank}. {name}: {mse:.6f}")
        
        if len(mse_results) > 5:
            print(f"   ... and {len(mse_results) - 5} more configurations")
        
        # Performance spread
        best_mse = mse_results[0][1]
        worst_mse = mse_results[-1][1]
        improvement_factor = worst_mse / best_mse if best_mse > 0 else float('inf')
        print(f"\n📈 PERFORMANCE SPREAD:")
        print(f"   Best MSE: {best_mse:.6f} ({mse_results[0][0]})")
        print(f"   Worst MSE: {worst_mse:.6f} ({mse_results[-1][0]})")
        print(f"   Improvement factor: {improvement_factor:.2f}x")
    
    # Parameter analysis
    all_params = set()
    for result in results.values():
        all_params.update(result.keys())
    
    common_params = ['spectral_radius', 'n_reservoir', 'noise_level', 'leak_rate']
    available_params = [p for p in common_params if p in all_params]
    
    if available_params:
        print(f"\n⚙️ PARAMETER RANGES:")
        for param in available_params:
            values = [results[name].get(param) for name in config_names if param in results[name]]
            values = [v for v in values if v is not None and not np.isnan(v)]
            
            if values:
                min_val, max_val = min(values), max(values)
                mean_val = np.mean(values)
                print(f"   {param}: [{min_val:.4f}, {max_val:.4f}] (mean: {mean_val:.4f})")
    
    print("="*70)


def print_spectral_statistics(eigenvals: np.ndarray, 
                             singular_vals: np.ndarray,
                             condition_number: float) -> None:
    """
    Print comprehensive spectral analysis statistics
    
    Args:
        eigenvals: Eigenvalues of the matrix
        singular_vals: Singular values of the matrix  
        condition_number: Condition number of the matrix
    """
    print("\n" + "="*60)
    print("🌈 SPECTRAL ANALYSIS STATISTICS")
    print("="*60)
    
    spectral_radius = np.max(np.abs(eigenvals))
    
    # Basic spectral properties
    print(f"\n🎯 BASIC SPECTRAL PROPERTIES:")
    print(f"   Matrix size: {int(np.sqrt(len(eigenvals)))} × {int(np.sqrt(len(eigenvals)))}")
    print(f"   Number of eigenvalues: {len(eigenvals)}")
    print(f"   Spectral radius: {spectral_radius:.6f}")
    print(f"   Condition number: {condition_number:.2e}")
    
    # Eigenvalue analysis
    complex_eigenvals = np.sum(np.abs(eigenvals.imag) > 1e-10)
    real_eigenvals = len(eigenvals) - complex_eigenvals
    
    print(f"\n🧮 EIGENVALUE COMPOSITION:")
    print(f"   Real eigenvalues: {real_eigenvals} ({real_eigenvals/len(eigenvals):.1%})")
    print(f"   Complex eigenvalues: {complex_eigenvals} ({complex_eigenvals/len(eigenvals):.1%})")
    print(f"   Dominant eigenvalue: {eigenvals[np.argmax(np.abs(eigenvals))]:.6f}")
    
    # Stability analysis
    print(f"\n🎚️ STABILITY ANALYSIS:")
    eigenvals_inside_unit = np.sum(np.abs(eigenvals) < 1.0)
    eigenvals_on_boundary = np.sum(np.abs(np.abs(eigenvals) - 1.0) < 1e-6)
    eigenvals_outside_unit = np.sum(np.abs(eigenvals) > 1.0)
    
    print(f"   Inside unit circle: {eigenvals_inside_unit} ({eigenvals_inside_unit/len(eigenvals):.1%})")
    print(f"   On unit circle: {eigenvals_on_boundary} ({eigenvals_on_boundary/len(eigenvals):.1%})")
    print(f"   Outside unit circle: {eigenvals_outside_unit} ({eigenvals_outside_unit/len(eigenvals):.1%})")
    
    # Echo State Property assessment
    if spectral_radius < 0.95:
        esp_status = "🟢 Strongly satisfied"
    elif spectral_radius < 1.0:
        esp_status = "🟡 Marginally satisfied"
    else:
        esp_status = "🔴 Violated"
    
    print(f"   Echo State Property: {esp_status}")
    
    # Singular value analysis
    effective_rank = np.sum(singular_vals > 1e-10)
    rank_ratio = effective_rank / len(singular_vals)
    
    print(f"\n📐 SINGULAR VALUE ANALYSIS:")
    print(f"   Largest singular value: {singular_vals[0]:.6f}")
    print(f"   Smallest singular value: {singular_vals[-1]:.2e}")
    print(f"   Effective rank: {effective_rank} ({rank_ratio:.1%} of full rank)")
    print(f"   Condition number: {condition_number:.2e}")
    
    # Condition number assessment
    condition_assessment = assess_condition_number(condition_number)
    print(f"   Numerical stability: {condition_assessment}")
    
    print("="*60)


def assess_condition_number(condition_number: float) -> str:
    """Assess numerical stability based on condition number"""
    if condition_number < 1e3:
        return "🟢 Excellent (well-conditioned)"
    elif condition_number < 1e6:
        return "🟡 Good (moderately conditioned)"
    elif condition_number < 1e12:
        return "🟠 Fair (ill-conditioned)"
    else:
        return "🔴 Poor (severely ill-conditioned)"


def assess_spectral_stability(eigenvals: np.ndarray) -> str:
    """Assess overall spectral stability"""
    spectral_radius = np.max(np.abs(eigenvals))
    
    if spectral_radius < 0.8:
        return "🟢 Highly stable"
    elif spectral_radius < 0.95:
        return "🟢 Stable"
    elif spectral_radius < 1.0:
        return "🟡 Marginally stable"
    elif spectral_radius < 1.1:
        return "🟠 Unstable"
    else:
        return "🔴 Highly unstable"


# Export all visualization functions for backward compatibility
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
    
    # Comparative analysis
    'visualize_comparative_analysis',
    'print_comparative_summary',
    
    # Spectral analysis
    'visualize_spectral_analysis',
    'print_spectral_statistics',
    
    # Animation and utilities
    'create_reservoir_animation',
    'assess_condition_number',
    'assess_spectral_stability'
]