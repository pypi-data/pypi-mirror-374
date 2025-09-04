"""
🔬 Advanced Analysis - Reservoir Dynamics and Comparative Studies
===============================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides advanced analysis tools for Echo State Networks including
reservoir dynamics analysis, memory capacity visualization, and comparative studies.

Based on research from:
- Jaeger, H. (2001) "Short term memory in echo state networks"
- Verstraeten, D. et al. (2007) "Memory capacity analysis"
- Appeltant, L. et al. (2011) "Information processing capacity"
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
from scipy import signal, stats
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import networkx as nx
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import pandas as pd
import warnings
import logging

# Configure logging
logger = logging.getLogger(__name__)


def visualize_reservoir_dynamics_advanced(states: np.ndarray, 
                                         inputs: Optional[np.ndarray] = None, 
                                         outputs: Optional[np.ndarray] = None, 
                                         figsize: Tuple[int, int] = (18, 12),
                                         save_path: Optional[str] = None) -> None:
    """
    Advanced visualization of reservoir dynamics and temporal behavior
    
    Args:
        states: Reservoir state matrix (time_steps × n_reservoir)
        inputs: Input sequence (time_steps × n_inputs) [optional]
        outputs: Output sequence (time_steps × n_outputs) [optional]
        figsize: Figure size for the visualization
        save_path: Optional path to save the visualization
    """
    fig = plt.figure(figsize=figsize)
    fig.suptitle('Advanced Echo State Network Dynamics Analysis', fontsize=16, fontweight='bold')
    
    time_steps, n_reservoir = states.shape
    
    # 1. State evolution heatmap with enhanced features
    ax1 = plt.subplot(3, 3, 1)
    
    # Sample neurons if too many for visualization
    max_neurons_display = 50
    if n_reservoir > max_neurons_display:
        neuron_indices = np.random.choice(n_reservoir, max_neurons_display, replace=False)
        display_states = states[:, neuron_indices]
        title_suffix = f" (Random {max_neurons_display} neurons)"
    else:
        display_states = states
        neuron_indices = np.arange(n_reservoir)
        title_suffix = ""
        
    im1 = ax1.imshow(display_states.T, cmap='viridis', aspect='auto', interpolation='nearest')
    ax1.set_title(f'State Evolution{title_suffix}')
    ax1.set_xlabel('Time Step')
    ax1.set_ylabel('Neuron Index')
    plt.colorbar(im1, ax=ax1, shrink=0.8, label='Activation')
    
    # 2. State trajectory in reduced space (PCA/t-SNE)
    ax2 = plt.subplot(3, 3, 2, projection='3d')
    if n_reservoir >= 3:
        try:
            # Use PCA for dimensionality reduction
            pca = PCA(n_components=3)
            states_reduced = pca.fit_transform(states)
            
            # Color by time
            colors = plt.cm.plasma(np.linspace(0, 1, len(states_reduced)))
            scatter = ax2.scatter(states_reduced[:, 0], states_reduced[:, 1], states_reduced[:, 2],
                                c=np.arange(len(states_reduced)), cmap='plasma', s=20, alpha=0.7)
            
            ax2.set_title(f'State Trajectory (PCA)\\nVar Explained: {pca.explained_variance_ratio_.sum():.1%}')
            ax2.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
            ax2.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
            ax2.set_zlabel(f'PC3 ({pca.explained_variance_ratio_[2]:.1%})')
            
            # Add trajectory lines
            ax2.plot(states_reduced[:, 0], states_reduced[:, 1], states_reduced[:, 2], 
                    'k-', alpha=0.3, linewidth=0.5)
            
        except Exception as e:
            logger.warning(f"PCA visualization failed: {e}")
            ax2.text(0.5, 0.5, 0.5, 'PCA visualization\\nfailed', ha='center', va='center')
            ax2.set_title('State Trajectory (PCA)')
    else:
        ax2.text(0.5, 0.5, 0.5, 'Insufficient dimensions\\nfor 3D visualization', 
                ha='center', va='center')
        ax2.set_title('State Trajectory (PCA)')
    
    # 3. Activity distribution and statistics
    ax3 = plt.subplot(3, 3, 3)
    
    mean_activity = np.mean(states, axis=0)
    std_activity = np.std(states, axis=0)
    
    scatter = ax3.scatter(mean_activity, std_activity, alpha=0.6, s=30, c=np.arange(len(mean_activity)), cmap='viridis')
    ax3.set_xlabel('Mean Activity')
    ax3.set_ylabel('Activity Std')
    ax3.set_title('Neuron Activity Statistics')
    ax3.grid(True, alpha=0.3)
    
    # Add correlation line
    if len(mean_activity) > 1:
        z = np.polyfit(mean_activity, std_activity, 1)
        p = np.poly1d(z)
        ax3.plot(mean_activity, p(mean_activity), "r--", alpha=0.8, linewidth=2)
        
        corr_coef = np.corrcoef(mean_activity, std_activity)[0, 1]
        ax3.text(0.02, 0.98, f'Correlation: {corr_coef:.3f}', 
                transform=ax3.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top')
    
    # 4. Temporal correlation matrix
    ax4 = plt.subplot(3, 3, 4)
    
    # Compute pairwise correlations between time steps
    if time_steps > 10:
        sample_steps = min(50, time_steps)
        step_indices = np.linspace(0, time_steps-1, sample_steps).astype(int)
        sample_states = states[step_indices]
        
        try:
            corr_matrix = np.corrcoef(sample_states)
            im4 = ax4.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
            ax4.set_title('Temporal Correlation Matrix')
            ax4.set_xlabel('Time Step')
            ax4.set_ylabel('Time Step')
            plt.colorbar(im4, ax=ax4, shrink=0.8, label='Correlation')
        except Exception as e:
            logger.warning(f"Temporal correlation failed: {e}")
            ax4.text(0.5, 0.5, 'Temporal correlation\\nanalysis failed', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Temporal Correlation Matrix')
    else:
        ax4.text(0.5, 0.5, 'Insufficient time steps\\nfor correlation analysis', 
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Temporal Correlation Matrix')
    
    # 5. Phase space analysis
    ax5 = plt.subplot(3, 3, 5)
    
    if n_reservoir >= 2:
        # Choose two representative neurons
        neuron1_idx = np.argmax(np.std(states, axis=0))  # Most variable neuron
        remaining_neurons = np.setdiff1d(np.arange(n_reservoir), [neuron1_idx])
        neuron2_idx = remaining_neurons[np.argmax(np.std(states[:, remaining_neurons], axis=0))]
        
        ax5.plot(states[:, neuron1_idx], states[:, neuron2_idx], 'b-', alpha=0.7, linewidth=0.5)
        ax5.scatter(states[0, neuron1_idx], states[0, neuron2_idx], color='green', s=50, label='Start', zorder=5)
        ax5.scatter(states[-1, neuron1_idx], states[-1, neuron2_idx], color='red', s=50, label='End', zorder=5)
        
        ax5.set_xlabel(f'Neuron {neuron1_idx} Activity')
        ax5.set_ylabel(f'Neuron {neuron2_idx} Activity')
        ax5.set_title('Phase Space Trajectory')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
    else:
        ax5.text(0.5, 0.5, 'Insufficient neurons\\nfor phase space analysis', 
                ha='center', va='center', transform=ax5.transAxes)
        ax5.set_title('Phase Space Trajectory')
    
    # 6. Spectral analysis of dynamics
    ax6 = plt.subplot(3, 3, 6)
    
    # Power spectral density of representative neurons
    sample_neurons = min(5, n_reservoir)
    frequencies = []
    power_spectra = []
    
    for i in range(sample_neurons):
        if time_steps > 10:
            try:
                f, Pxx = signal.periodogram(states[:, i], nperseg=min(256, time_steps//4))
                frequencies.append(f)
                power_spectra.append(Pxx)
            except Exception as e:
                logger.warning(f"Periodogram failed for neuron {i}: {e}")
    
    if power_spectra:
        mean_spectrum = np.mean(power_spectra, axis=0)
        std_spectrum = np.std(power_spectra, axis=0)
        
        ax6.loglog(frequencies[0], mean_spectrum, 'b-', linewidth=2, label='Mean PSD')
        ax6.fill_between(frequencies[0], 
                       np.maximum(mean_spectrum - std_spectrum, 1e-10),
                       mean_spectrum + std_spectrum, 
                       alpha=0.3, label='±1 Std')
        
        ax6.set_title('Power Spectral Density')
        ax6.set_xlabel('Frequency (normalized)')
        ax6.set_ylabel('Power')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
    else:
        ax6.text(0.5, 0.5, 'Spectral analysis\\nfailed', 
                ha='center', va='center', transform=ax6.transAxes)
        ax6.set_title('Power Spectral Density')
    
    # 7. Input-state cross-correlation (if inputs provided)
    ax7 = plt.subplot(3, 3, 7)
    if inputs is not None:
        try:
            # Compute cross-correlation between inputs and states
            max_neurons_corr = min(10, n_reservoir)
            input_dim = inputs.shape[1] if inputs.ndim > 1 else 1
            
            if input_dim == 1 and inputs.ndim == 1:
                inputs_use = inputs.reshape(-1, 1)
            else:
                inputs_use = inputs
                
            # Sample subset for computational efficiency
            sample_size = min(500, time_steps)
            sample_indices = np.random.choice(time_steps, sample_size, replace=False)
            
            cross_corrs = []
            for i in range(max_neurons_corr):
                if i < n_reservoir:
                    corr = np.corrcoef(inputs_use[sample_indices, 0], states[sample_indices, i])[0, 1]
                    if not np.isnan(corr):
                        cross_corrs.append(corr)
            
            if cross_corrs:
                neuron_indices = np.arange(len(cross_corrs))
                ax7.bar(neuron_indices, cross_corrs, alpha=0.7, edgecolor='black')
                ax7.set_xlabel('Neuron Index')
                ax7.set_ylabel('Input-State Correlation')
                ax7.set_title('Input-State Cross-correlation')
                ax7.grid(True, alpha=0.3)
                
                # Add statistics
                mean_corr = np.mean(np.abs(cross_corrs))
                ax7.text(0.98, 0.98, f'Mean |Corr|: {mean_corr:.3f}', 
                        transform=ax7.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                        verticalalignment='top', horizontalalignment='right')
            else:
                ax7.text(0.5, 0.5, 'No valid correlations', ha='center', va='center', transform=ax7.transAxes)
                ax7.set_title('Input-State Cross-correlation')
        except Exception as e:
            logger.warning(f"Input-state correlation failed: {e}")
            ax7.text(0.5, 0.5, 'Cross-correlation\\nanalysis failed', 
                    ha='center', va='center', transform=ax7.transAxes)
            ax7.set_title('Input-State Cross-correlation')
    else:
        ax7.text(0.5, 0.5, 'No input data\\nprovided', 
                ha='center', va='center', transform=ax7.transAxes)
        ax7.set_title('Input-State Cross-correlation')
    
    # 8. Hierarchical clustering of neurons
    ax8 = plt.subplot(3, 3, 8)
    
    # Cluster neurons based on activity patterns
    if n_reservoir > 2 and time_steps > 10:
        try:
            # Sample neurons and time steps for clustering
            max_neurons_cluster = min(20, n_reservoir)
            sample_neurons = np.random.choice(n_reservoir, max_neurons_cluster, replace=False)
            
            # Compute distance matrix
            neuron_activities = states[:, sample_neurons].T
            distances = pdist(neuron_activities, metric='correlation')
            
            # Perform hierarchical clustering
            linkage_matrix = linkage(distances, method='ward')
            
            # Plot dendrogram
            dendrogram(linkage_matrix, ax=ax8, orientation='top', truncate_mode='lastp', p=10)
            ax8.set_title(f'Neuron Clustering\\n({max_neurons_cluster} neurons)')
            ax8.set_xlabel('Neuron Cluster')
            ax8.set_ylabel('Distance')
            
        except Exception as e:
            logger.warning(f"Clustering analysis failed: {e}")
            ax8.text(0.5, 0.5, 'Clustering analysis\\nfailed', 
                    ha='center', va='center', transform=ax8.transAxes)
            ax8.set_title('Neuron Clustering')
    else:
        ax8.text(0.5, 0.5, 'Insufficient data\\nfor clustering', 
                ha='center', va='center', transform=ax8.transAxes)
        ax8.set_title('Neuron Clustering')
    
    # 9. Nonlinear dynamics analysis
    ax9 = plt.subplot(3, 3, 9)
    
    # Analyze Lyapunov exponent approximation
    if time_steps > 50 and n_reservoir > 0:
        try:
            # Use most variable neuron for analysis
            most_variable_neuron = np.argmax(np.std(states, axis=0))
            signal_data = states[:, most_variable_neuron]
            
            # Simple approximation of largest Lyapunov exponent
            # This is a simplified version for visualization
            def estimate_lyapunov(data, max_lag=20):
                """Simplified Lyapunov exponent estimation"""
                lags = np.arange(1, min(max_lag, len(data)//4))
                divergences = []
                
                for lag in lags:
                    if len(data) > lag:
                        diff = np.abs(data[lag:] - data[:-lag])
                        avg_div = np.mean(diff)
                        divergences.append(avg_div)
                
                if len(divergences) > 3:
                    # Fit exponential growth
                    log_divs = np.log(np.maximum(divergences, 1e-10))
                    coeffs = np.polyfit(lags[:len(divergences)], log_divs, 1)
                    return coeffs[0], lags[:len(divergences)], divergences
                
                return 0, lags[:len(divergences)], divergences
            
            lyap_est, lags, divs = estimate_lyapunov(signal_data)
            
            ax9.semilogy(lags, divs, 'bo-', markersize=4, linewidth=2)
            ax9.set_xlabel('Time Lag')
            ax9.set_ylabel('Average Divergence (log)')
            ax9.set_title(f'Dynamics Analysis\\nλ ≈ {lyap_est:.3f}')
            ax9.grid(True, alpha=0.3)
            
            # Add interpretation
            stability_text = "Stable" if lyap_est < 0 else "Chaotic" if lyap_est > 0.01 else "Near Critical"
            ax9.text(0.02, 0.98, f'Regime: {stability_text}', 
                    transform=ax9.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7),
                    verticalalignment='top')
            
        except Exception as e:
            logger.warning(f"Nonlinear dynamics analysis failed: {e}")
            ax9.text(0.5, 0.5, 'Dynamics analysis\\nfailed', 
                    ha='center', va='center', transform=ax9.transAxes)
            ax9.set_title('Dynamics Analysis')
    else:
        ax9.text(0.5, 0.5, 'Insufficient data\\nfor dynamics analysis', 
                ha='center', va='center', transform=ax9.transAxes)
        ax9.set_title('Dynamics Analysis')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    plt.show()


def visualize_comparative_analysis(reservoirs: List[Dict[str, Any]], 
                                 metrics: List[str] = None,
                                 figsize: Tuple[int, int] = (15, 10),
                                 save_path: Optional[str] = None) -> None:
    """
    Compare multiple reservoir configurations
    
    Args:
        reservoirs: List of dictionaries containing reservoir data and metadata
        metrics: List of metrics to compare
        figsize: Figure size for the visualization
        save_path: Optional path to save the visualization
    """
    if not reservoirs:
        print("No reservoirs provided for comparison")
        return
    
    if metrics is None:
        metrics = ['spectral_radius', 'performance', 'sparsity', 'memory_capacity']
    
    n_reservoirs = len(reservoirs)
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(f'Comparative Analysis of {n_reservoirs} Reservoir Configurations', 
                 fontsize=14, fontweight='bold')
    
    # Extract labels
    labels = [res.get('name', f'Reservoir {i+1}') for i, res in enumerate(reservoirs)]
    
    # 1. Performance comparison
    ax1 = axes[0, 0]
    if 'performance' in metrics:
        performances = []
        for res in reservoirs:
            if 'performance' in res:
                performances.append(res['performance'])
            elif 'mse' in res:
                performances.append(-np.log10(res['mse']))  # Convert MSE to positive score
            else:
                performances.append(0)
        
        bars = ax1.bar(range(n_reservoirs), performances, alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Reservoir Configuration')
        ax1.set_ylabel('Performance Score')
        ax1.set_title('Performance Comparison')
        ax1.set_xticks(range(n_reservoirs))
        ax1.set_xticklabels(labels, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Color bars based on performance
        for i, (bar, perf) in enumerate(zip(bars, performances)):
            if perf == max(performances):
                bar.set_color('gold')
            elif perf == min(performances):
                bar.set_color('lightcoral')
    else:
        ax1.text(0.5, 0.5, 'Performance data\\nnot available', 
                ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Performance Comparison')
    
    # 2. Spectral radius comparison
    ax2 = axes[0, 1]
    if 'spectral_radius' in metrics:
        spectral_radii = []
        for res in reservoirs:
            if 'spectral_radius' in res:
                spectral_radii.append(res['spectral_radius'])
            elif 'W_reservoir' in res:
                eigenvals = np.linalg.eigvals(res['W_reservoir'])
                spectral_radii.append(np.max(np.abs(eigenvals)))
            else:
                spectral_radii.append(0)
        
        bars = ax2.bar(range(n_reservoirs), spectral_radii, alpha=0.7, edgecolor='black')
        ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Stability Threshold')
        ax2.set_xlabel('Reservoir Configuration')
        ax2.set_ylabel('Spectral Radius')
        ax2.set_title('Spectral Radius Comparison')
        ax2.set_xticks(range(n_reservoirs))
        ax2.set_xticklabels(labels, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Color bars based on stability
        for i, (bar, sr) in enumerate(zip(bars, spectral_radii)):
            bar.set_color('lightgreen' if sr < 1.0 else 'lightcoral')
    else:
        ax2.text(0.5, 0.5, 'Spectral radius data\\nnot available', 
                ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Spectral Radius Comparison')
    
    # 3. Network properties comparison
    ax3 = axes[1, 0]
    properties = ['sparsity', 'clustering', 'path_length']
    prop_data = {prop: [] for prop in properties}
    
    for res in reservoirs:
        for prop in properties:
            if prop in res:
                prop_data[prop].append(res[prop])
            elif prop == 'sparsity' and 'W_reservoir' in res:
                W = res['W_reservoir']
                sparsity = 1 - np.mean(W != 0)
                prop_data[prop].append(sparsity)
            else:
                prop_data[prop].append(0)
    
    # Create grouped bar chart
    x = np.arange(n_reservoirs)
    width = 0.25
    
    for i, prop in enumerate(properties):
        if any(prop_data[prop]):  # Only plot if we have data
            ax3.bar(x + i*width, prop_data[prop], width, label=prop.capitalize(), alpha=0.7)
    
    ax3.set_xlabel('Reservoir Configuration')
    ax3.set_ylabel('Property Value')
    ax3.set_title('Network Properties Comparison')
    ax3.set_xticks(x + width)
    ax3.set_xticklabels(labels, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Multi-dimensional comparison (radar chart)
    ax4 = axes[1, 1]
    
    # Create radar chart for multi-dimensional comparison
    available_metrics = []
    metric_data = []
    
    for metric in ['performance', 'spectral_radius', 'sparsity', 'memory_capacity']:
        metric_values = []
        for res in reservoirs:
            if metric in res:
                metric_values.append(res[metric])
            elif metric == 'spectral_radius' and 'W_reservoir' in res:
                eigenvals = np.linalg.eigvals(res['W_reservoir'])
                metric_values.append(np.max(np.abs(eigenvals)))
            elif metric == 'sparsity' and 'W_reservoir' in res:
                W = res['W_reservoir']
                metric_values.append(1 - np.mean(W != 0))
            else:
                metric_values.append(0)
        
        if any(metric_values):
            available_metrics.append(metric.replace('_', ' ').title())
            # Normalize values to 0-1 range for comparison
            if max(metric_values) != min(metric_values):
                normalized = [(v - min(metric_values)) / (max(metric_values) - min(metric_values)) 
                            for v in metric_values]
            else:
                normalized = [0.5] * len(metric_values)
            metric_data.append(normalized)
    
    if available_metrics and metric_data:
        # Simple scatter plot instead of radar for simplicity
        for i, label in enumerate(labels):
            values = [data[i] for data in metric_data]
            ax4.plot(range(len(available_metrics)), values, 'o-', label=label, linewidth=2, markersize=6)
        
        ax4.set_xlabel('Metrics')
        ax4.set_ylabel('Normalized Value')
        ax4.set_title('Multi-metric Comparison')
        ax4.set_xticks(range(len(available_metrics)))
        ax4.set_xticklabels(available_metrics, rotation=45, ha='right')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 1)
    else:
        ax4.text(0.5, 0.5, 'Insufficient data\\nfor multi-metric comparison', 
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Multi-metric Comparison')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    plt.show()


def visualize_memory_capacity(memory_tasks: List[Tuple[int, float]], 
                            figsize: Tuple[int, int] = (12, 8),
                            save_path: Optional[str] = None) -> None:
    """
    Visualize memory capacity analysis results
    
    Args:
        memory_tasks: List of (delay, capacity) tuples from memory capacity tests
        figsize: Figure size for the visualization
        save_path: Optional path to save the visualization
    """
    if not memory_tasks:
        print("No memory capacity data provided")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle('Memory Capacity Analysis', fontsize=14, fontweight='bold')
    
    delays, capacities = zip(*memory_tasks)
    
    # 1. Memory capacity vs delay
    ax1 = axes[0]
    ax1.plot(delays, capacities, 'bo-', linewidth=2, markersize=6)
    ax1.set_xlabel('Memory Delay (steps)')
    ax1.set_ylabel('Memory Capacity')
    ax1.set_title('Memory Capacity vs Delay')
    ax1.grid(True, alpha=0.3)
    
    # Add exponential fit if enough data points
    if len(delays) > 3:
        try:
            # Fit exponential decay
            popt = np.polyfit(delays, np.log(np.maximum(capacities, 1e-10)), 1)
            decay_rate = -popt[0]
            
            x_fit = np.linspace(min(delays), max(delays), 100)
            y_fit = np.exp(popt[1]) * np.exp(-decay_rate * x_fit)
            
            ax1.plot(x_fit, y_fit, 'r--', linewidth=2, alpha=0.8, 
                    label=f'Exponential fit (λ={decay_rate:.3f})')
            ax1.legend()
        except Exception as e:
            logger.warning(f"Memory capacity fit failed: {e}")
    
    # Add total memory capacity
    total_mc = sum(capacities)
    ax1.text(0.02, 0.98, f'Total MC: {total_mc:.2f}', 
            transform=ax1.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.8),
            verticalalignment='top')
    
    # 2. Memory capacity distribution
    ax2 = axes[1]
    
    # Histogram of capacity values
    ax2.hist(capacities, bins=min(20, len(capacities)), alpha=0.7, edgecolor='black', density=True)
    ax2.set_xlabel('Memory Capacity')
    ax2.set_ylabel('Density')
    ax2.set_title('Memory Capacity Distribution')
    ax2.grid(True, alpha=0.3)
    
    # Add statistics
    mean_capacity = np.mean(capacities)
    std_capacity = np.std(capacities)
    
    ax2.axvline(x=mean_capacity, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_capacity:.3f}')
    ax2.axvline(x=mean_capacity + std_capacity, color='orange', linestyle=':', linewidth=2, alpha=0.7)
    ax2.axvline(x=mean_capacity - std_capacity, color='orange', linestyle=':', linewidth=2, alpha=0.7, 
               label=f'±1 Std: {std_capacity:.3f}')
    
    ax2.legend()
    
    # Add capacity assessment
    if total_mc > 10:
        assessment = "Excellent"
        color = "green"
    elif total_mc > 5:
        assessment = "Good"
        color = "orange"
    else:
        assessment = "Limited"
        color = "red"
    
    ax2.text(0.98, 0.98, f'Assessment: {assessment}', 
            transform=ax2.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.3),
            verticalalignment='top', horizontalalignment='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    plt.show()
    
    # Print summary statistics
    print("\\n" + "="*50)
    print("🧠 MEMORY CAPACITY ANALYSIS SUMMARY")
    print("="*50)
    print(f"Total Memory Capacity: {total_mc:.4f}")
    print(f"Mean Individual Capacity: {mean_capacity:.4f}")
    print(f"Capacity Standard Deviation: {std_capacity:.4f}")
    print(f"Maximum Delay Tested: {max(delays)} steps")
    print(f"Capacity at Delay 1: {capacities[0]:.4f}" if delays[0] == 1 else "N/A")
    print(f"Assessment: {assessment}")
    print("="*50)