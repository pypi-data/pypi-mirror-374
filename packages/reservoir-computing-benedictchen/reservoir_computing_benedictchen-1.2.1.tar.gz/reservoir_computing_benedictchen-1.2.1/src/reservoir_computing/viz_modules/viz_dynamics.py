"""
🌊 Reservoir Computing - Dynamics Visualization Module
===================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Specialized visualization tools for reservoir dynamics analysis.
Provides comprehensive tools for analyzing temporal behavior, state evolution,
and dynamic patterns in reservoir computing systems.

📊 VISUALIZATION CAPABILITIES:
=============================
• State evolution heatmaps and trajectories
• Temporal correlation analysis and autocorrelation
• Activity pattern analysis and phase space plots
• Power spectral density of reservoir dynamics
• Memory capacity visualization and temporal analysis

🔬 RESEARCH FOUNDATION:
======================
Based on established dynamics analysis techniques:
- Jaeger (2001): Echo state dynamics and temporal analysis
- Lukoševičius & Jaeger (2009): Reservoir dynamics visualization methods
- Verstraeten et al. (2007): Memory capacity analysis and visualization
- Dambre et al. (2012): Information processing capacity analysis

🎨 PROFESSIONAL STANDARDS:
=========================
• High-resolution temporal plots with proper time scaling
• Perceptually uniform colormaps for temporal data
• Comprehensive legends and temporal annotations
• Publication-ready formatting for dynamics research
• Research-accurate implementations of analysis methods

This module represents the dynamics analysis component of the visualization system,
split from the 1569-line monolith for better maintainability and focused functionality.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.animation import FuncAnimation
import seaborn as sns
from scipy import signal, stats
from scipy.spatial.distance import pdist, squareform
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
import warnings
from mpl_toolkits.mplot3d import Axes3D
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import pandas as pd
import logging

# Configure professional plotting style for dynamics
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# ================================
# DYNAMIC BEHAVIOR VISUALIZATION
# ================================

def visualize_reservoir_dynamics(states: np.ndarray, 
                                input_sequence: Optional[np.ndarray] = None,
                                time_steps: Optional[np.ndarray] = None,
                                title: str = "Reservoir Dynamics Analysis",
                                save_path: Optional[str] = None,
                                figsize: Tuple[int, int] = (16, 12),
                                dpi: int = 300,
                                max_neurons_display: int = 50) -> plt.Figure:
    """
    🌊 Comprehensive Reservoir Dynamics Visualization
    
    Creates a multi-panel analysis of reservoir temporal behavior, state evolution,
    and dynamic patterns with professional formatting and statistical analysis.
    
    Args:
        states: Reservoir states over time (T×N matrix)
        input_sequence: Input sequence over time (T×M matrix), optional
        time_steps: Time step array (T,), optional
        title: Figure title
        save_path: Path to save figure (optional)
        figsize: Figure size in inches
        dpi: Resolution for saved figures
        max_neurons_display: Maximum number of neurons to display in detailed plots
        
    Returns:
        matplotlib.Figure: The complete dynamics analysis figure
        
    Research Background:
    ===================
    Based on Jaeger (2001) reservoir dynamics analysis and extended with
    modern temporal analysis techniques for comprehensive dynamical insight.
    """
    T, N = states.shape
    
    if time_steps is None:
        time_steps = np.arange(T)
        
    fig = plt.figure(figsize=figsize, dpi=dpi)
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.95)
    
    # Create subplot layout
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.4)
    
    # === 1. STATE EVOLUTION HEATMAP ===
    ax1 = fig.add_subplot(gs[0, :2])
    
    # Sample neurons if too many for display
    if N > max_neurons_display:
        neuron_indices = np.linspace(0, N-1, max_neurons_display, dtype=int)
        display_states = states[:, neuron_indices]
        ylabel = f'Neuron Index (sampled {max_neurons_display}/{N})'
    else:
        display_states = states
        neuron_indices = np.arange(N)
        ylabel = 'Neuron Index'
    
    im1 = ax1.imshow(display_states.T, cmap='RdBu_r', aspect='auto',
                     extent=[time_steps[0], time_steps[-1], 0, len(neuron_indices)])
    
    ax1.set_title('Reservoir State Evolution', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Time Steps')
    ax1.set_ylabel(ylabel)
    
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Activation Level', rotation=270, labelpad=15)
    
    # Add statistics overlay
    mean_activity = np.mean(np.abs(states))
    max_activity = np.max(np.abs(states))
    ax1.text(0.02, 0.98, f'Mean |activity|: {mean_activity:.3f}\nMax |activity|: {max_activity:.3f}', 
             transform=ax1.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
             fontsize=9)
    
    # === 2. TEMPORAL ACTIVITY PATTERNS ===
    ax2 = fig.add_subplot(gs[0, 2:])
    
    # Plot activity of selected neurons over time
    n_plot = min(10, N)
    plot_indices = np.linspace(0, N-1, n_plot, dtype=int)
    
    colors = plt.cm.tab10(np.linspace(0, 1, n_plot))
    for i, idx in enumerate(plot_indices):
        ax2.plot(time_steps, states[:, idx], alpha=0.7, color=colors[i], 
                linewidth=1.5, label=f'Neuron {idx}')
    
    ax2.set_title('Individual Neuron Activities', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Time Steps')
    ax2.set_ylabel('Activation')
    ax2.grid(True, alpha=0.3)
    
    # Add legend for small numbers of neurons
    if n_plot <= 6:
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    # === 3. ACTIVITY DISTRIBUTION ===
    ax3 = fig.add_subplot(gs[1, :2])
    
    # Histogram of all activations
    states_flat = states.flatten()
    n_bins = min(50, int(np.sqrt(len(states_flat))))
    
    ax3.hist(states_flat, bins=n_bins, alpha=0.7, color='lightcoral', 
             edgecolor='black', linewidth=0.5, density=True)
    
    # Statistical overlays
    mean_act = np.mean(states_flat)
    std_act = np.std(states_flat)
    
    ax3.axvline(mean_act, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_act:.3f}')
    ax3.axvline(mean_act + std_act, color='orange', linestyle='--', alpha=0.7)
    ax3.axvline(mean_act - std_act, color='orange', linestyle='--', alpha=0.7)
    
    ax3.set_title('Activation Distribution', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Activation Value')
    ax3.set_ylabel('Probability Density')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # === 4. TEMPORAL CORRELATIONS ===
    ax4 = fig.add_subplot(gs[1, 2:])
    
    # Calculate autocorrelation for mean activity
    mean_states = np.mean(states, axis=1)
    
    # Autocorrelation using scipy
    max_lag = min(50, T // 4)
    lags = np.arange(1, max_lag + 1)
    autocorr = []
    
    for lag in lags:
        if lag < len(mean_states):
            corr = np.corrcoef(mean_states[:-lag], mean_states[lag:])[0, 1]
            autocorr.append(corr if not np.isnan(corr) else 0)
        else:
            autocorr.append(0)
    
    autocorr = np.array(autocorr)
    
    ax4.plot(lags, autocorr, 'b-', linewidth=2, marker='o', markersize=3)
    ax4.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax4.axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label='0.5 threshold')
    
    ax4.set_title('Temporal Autocorrelation', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Time Lag')
    ax4.set_ylabel('Autocorrelation')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # === 5. POWER SPECTRAL DENSITY ===
    ax5 = fig.add_subplot(gs[2, :2])
    
    # Calculate PSD for mean activity
    if len(mean_states) > 10:
        frequencies, psd = signal.periodogram(mean_states, nperseg=min(256, len(mean_states)))
        
        ax5.semilogy(frequencies[1:], psd[1:], 'g-', linewidth=2)  # Skip DC component
        ax5.set_title('Power Spectral Density', fontsize=12, fontweight='bold')
        ax5.set_xlabel('Normalized Frequency')
        ax5.set_ylabel('Power')
        ax5.grid(True, alpha=0.3)
        
        # Find dominant frequency
        dominant_freq_idx = np.argmax(psd[1:]) + 1
        dominant_freq = frequencies[dominant_freq_idx]
        ax5.axvline(dominant_freq, color='red', linestyle='--', 
                   label=f'Dominant: {dominant_freq:.3f}')
        ax5.legend()
    
    # === 6. PHASE SPACE ANALYSIS (if applicable) ===
    ax6 = fig.add_subplot(gs[2, 2:])
    
    if N >= 2:
        # 2D phase space plot using first two principal components
        if N > 2:
            pca = PCA(n_components=2)
            states_2d = pca.fit_transform(states)
            ax6.set_title(f'Phase Space (PC1 vs PC2)', fontsize=12, fontweight='bold')
            ax6.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} var)')
            ax6.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} var)')
        else:
            states_2d = states
            ax6.set_title('Phase Space (2D)', fontsize=12, fontweight='bold')
            ax6.set_xlabel('Neuron 0')
            ax6.set_ylabel('Neuron 1')
        
        # Plot trajectory with color gradient
        colors = np.linspace(0, 1, len(states_2d))
        scatter = ax6.scatter(states_2d[:, 0], states_2d[:, 1], 
                             c=colors, cmap='viridis', alpha=0.6, s=20)
        
        # Mark start and end points
        ax6.plot(states_2d[0, 0], states_2d[0, 1], 'go', markersize=8, label='Start')
        ax6.plot(states_2d[-1, 0], states_2d[-1, 1], 'ro', markersize=8, label='End')
        
        ax6.grid(True, alpha=0.3)
        ax6.legend()
        
        # Add colorbar for time
        cbar6 = plt.colorbar(scatter, ax=ax6, shrink=0.8)
        cbar6.set_label('Time Progress', rotation=270, labelpad=15)
    else:
        # Single neuron case - show phase portrait derivative
        if len(mean_states) > 1:
            derivative = np.diff(mean_states)
            ax6.plot(mean_states[:-1], derivative, 'b-', alpha=0.7, linewidth=1)
            ax6.set_title('Phase Portrait (State vs Derivative)', fontsize=12, fontweight='bold')
            ax6.set_xlabel('State Value')
            ax6.set_ylabel('State Derivative')
            ax6.grid(True, alpha=0.3)
    
    # Add input sequence overlay if provided
    if input_sequence is not None and input_sequence.shape[0] == T:
        # Add small subplot showing input
        ax_input = fig.add_axes([0.02, 0.02, 0.2, 0.1])
        
        if input_sequence.ndim == 1:
            ax_input.plot(time_steps, input_sequence, 'k-', linewidth=1)
        else:
            # Multiple input dimensions - show first one
            ax_input.plot(time_steps, input_sequence[:, 0], 'k-', linewidth=1)
            
        ax_input.set_title('Input Signal', fontsize=8)
        ax_input.set_xlabel('Time', fontsize=8)
        ax_input.tick_params(labelsize=6)
        ax_input.grid(True, alpha=0.3)
    
    # Add timestamp and metadata
    fig.text(0.98, 0.02, f'T={T}, N={N} | Reservoir Computing Dynamics Analysis', 
             fontsize=8, style='italic', alpha=0.7, ha='right')
    
    # Save figure if path provided
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        print(f"🌊 Dynamics analysis saved to: {save_path}")
    
    plt.tight_layout()
    return fig

# Export the main function
__all__ = ['visualize_reservoir_dynamics']
