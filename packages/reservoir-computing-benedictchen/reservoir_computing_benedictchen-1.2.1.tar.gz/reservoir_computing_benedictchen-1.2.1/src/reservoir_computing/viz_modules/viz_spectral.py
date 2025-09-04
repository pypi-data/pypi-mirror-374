"""
🌌 Reservoir Computing - Spectral Analysis & Animation Visualization Module
=========================================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Specialized visualization tools for spectral analysis and animation of reservoir systems.
Provides advanced eigenvalue analysis, stability assessment, and dynamic visualization
through animations and interactive plots.

📊 VISUALIZATION CAPABILITIES:
=============================
• Advanced eigenvalue spectrum analysis with stability regions
• Singular value decomposition and condition number analysis
• Effective dimensionality and rank analysis
• Lyapunov exponent visualization for stability assessment
• Dynamic animation of reservoir state evolution

🔬 RESEARCH FOUNDATION:
======================
Based on advanced spectral analysis techniques:
- Jaeger (2001): Spectral radius and stability analysis
- Lukoševičius & Jaeger (2009): Advanced reservoir analysis methods
- Verstraeten et al. (2007): Spectral properties and memory capacity
- Mathematical foundations from linear algebra and dynamical systems

🎨 PROFESSIONAL STANDARDS:
=========================
• High-resolution spectral plots with mathematical precision
• Interactive animations for dynamic behavior visualization
• Comprehensive mathematical annotations and stability indicators
• Publication-ready formatting for mathematical research
• Research-accurate spectral analysis implementations

This module represents the advanced spectral analysis and animation components,
split from the 1569-line monolith for specialized mathematical visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.animation import FuncAnimation
import seaborn as sns
from scipy import signal, stats
from scipy.linalg import svd
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
import warnings
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA
import pandas as pd
import logging

# Configure professional plotting style for spectral analysis
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# ================================
# ADVANCED SPECTRAL VISUALIZATION
# ================================

def visualize_spectral_analysis(reservoir_weights: np.ndarray,
                                title: str = "Advanced Spectral Analysis",
                                save_path: Optional[str] = None,
                                figsize: Tuple[int, int] = (16, 12),
                                dpi: int = 300) -> plt.Figure:
    """
    🌌 Comprehensive Spectral Analysis Visualization
    
    Creates advanced spectral analysis including eigenvalue analysis, singular value
    decomposition, stability assessment, and mathematical characterization.
    
    Args:
        reservoir_weights: Reservoir weight matrix (N×N)
        title: Figure title
        save_path: Path to save figure (optional)
        figsize: Figure size in inches
        dpi: Resolution for saved figures
        
    Returns:
        matplotlib.Figure: The complete spectral analysis figure
        
    Research Background:
    ===================
    Based on advanced spectral analysis methods from dynamical systems theory
    and reservoir computing literature for comprehensive mathematical insight.
    """
    N = reservoir_weights.shape[0]
    
    fig = plt.figure(figsize=figsize, dpi=dpi)
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.95)
    
    # Create subplot layout
    gs = fig.add_gridspec(3, 4, hspace=0.35, wspace=0.4)
    
    # === 1. EIGENVALUE SPECTRUM ===
    ax1 = fig.add_subplot(gs[0, :2])
    
    # Calculate eigenvalues
    eigenvals = np.linalg.eigvals(reservoir_weights)
    spectral_radius = np.max(np.abs(eigenvals))
    
    # Plot eigenvalues in complex plane
    ax1.scatter(eigenvals.real, eigenvals.imag, alpha=0.7, s=30, c='blue', edgecolors='black', linewidth=0.5)
    
    # Add unit circle for stability reference
    circle = patches.Circle((0, 0), 1, fill=False, color='red', linestyle='--', linewidth=2, label='Unit Circle')
    ax1.add_patch(circle)
    
    # Add spectral radius circle
    spec_circle = patches.Circle((0, 0), spectral_radius, fill=False, color='orange', 
                                linestyle='-', linewidth=2, alpha=0.7, label=f'ρ = {spectral_radius:.3f}')
    ax1.add_patch(spec_circle)
    
    # Highlight largest eigenvalue
    max_idx = np.argmax(np.abs(eigenvals))
    ax1.scatter(eigenvals[max_idx].real, eigenvals[max_idx].imag, 
                s=100, c='red', marker='x', linewidth=3, label='Max |λ|')
    
    ax1.set_title('Eigenvalue Spectrum', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Real Part')
    ax1.set_ylabel('Imaginary Part')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    
    # Add stability assessment
    stability_text = "Stable" if spectral_radius < 1.0 else "Marginally Stable" if spectral_radius < 1.1 else "Unstable"
    stability_color = "green" if spectral_radius < 1.0 else "orange" if spectral_radius < 1.1 else "red"
    ax1.text(0.02, 0.98, f'Stability: {stability_text}', transform=ax1.transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor=stability_color, alpha=0.3),
             fontweight='bold')
    
    # === 2. EIGENVALUE MAGNITUDE DISTRIBUTION ===
    ax2 = fig.add_subplot(gs[0, 2:])
    
    eigenval_magnitudes = np.abs(eigenvals)
    n_bins = min(30, N // 3)
    
    ax2.hist(eigenval_magnitudes, bins=n_bins, alpha=0.7, color='skyblue', 
             edgecolor='black', linewidth=0.5, density=True)
    
    # Add spectral radius line
    ax2.axvline(spectral_radius, color='red', linestyle='--', linewidth=2, 
               label=f'Spectral Radius: {spectral_radius:.3f}')
    
    # Add unit circle reference
    ax2.axvline(1.0, color='orange', linestyle=':', linewidth=2, 
               label='Unit Circle', alpha=0.7)
    
    ax2.set_title('Eigenvalue Magnitude Distribution', fontsize=12, fontweight='bold')
    ax2.set_xlabel('|λ|')
    ax2.set_ylabel('Density')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # === 3. SINGULAR VALUE DECOMPOSITION ===
    ax3 = fig.add_subplot(gs[1, :2])
    
    # Compute SVD
    U, sigma, Vt = svd(reservoir_weights)
    
    # Plot singular values
    ax3.semilogy(sigma, 'bo-', linewidth=2, markersize=4, alpha=0.8)
    ax3.set_title('Singular Value Spectrum', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Index')
    ax3.set_ylabel('Singular Value (σ)')
    ax3.grid(True, alpha=0.3)
    
    # Add condition number
    condition_number = np.max(sigma) / np.min(sigma) if np.min(sigma) > 1e-15 else np.inf
    ax3.text(0.02, 0.98, f'Condition Number: {condition_number:.2e}', 
             transform=ax3.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Highlight effective rank
    threshold = 0.01 * np.max(sigma)
    effective_rank = np.sum(sigma > threshold)
    ax3.axhline(threshold, color='red', linestyle='--', alpha=0.7, 
               label=f'1% threshold (rank: {effective_rank})')
    ax3.legend()
    
    # === 4. CUMULATIVE EXPLAINED VARIANCE ===
    ax4 = fig.add_subplot(gs[1, 2:])
    
    # Calculate cumulative explained variance from singular values
    sigma_squared = sigma ** 2
    total_variance = np.sum(sigma_squared)
    cumulative_variance = np.cumsum(sigma_squared) / total_variance
    
    ax4.plot(np.arange(1, len(cumulative_variance) + 1), cumulative_variance, 
             'g-', linewidth=2, marker='o', markersize=3)
    
    # Add reference lines
    ax4.axhline(0.95, color='red', linestyle='--', alpha=0.7, label='95% variance')
    ax4.axhline(0.99, color='orange', linestyle='--', alpha=0.7, label='99% variance')
    
    # Find 95% and 99% points
    idx_95 = np.argmax(cumulative_variance >= 0.95) + 1
    idx_99 = np.argmax(cumulative_variance >= 0.99) + 1
    
    ax4.set_title('Cumulative Explained Variance', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Number of Components')
    ax4.set_ylabel('Cumulative Variance Explained')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Add annotations
    ax4.text(0.02, 0.5, f'95%: {idx_95} components\n99%: {idx_99} components', 
             transform=ax4.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # === 5. EIGENVECTOR ANALYSIS ===
    ax5 = fig.add_subplot(gs[2, :2])
    
    # Get dominant eigenvector
    eigenvals_full, eigenvectors = np.linalg.eig(reservoir_weights)
    dominant_idx = np.argmax(np.abs(eigenvals_full))
    dominant_eigenvector = np.real(eigenvectors[:, dominant_idx])
    
    # Plot dominant eigenvector components
    ax5.plot(dominant_eigenvector, 'b-', linewidth=2, alpha=0.8)
    ax5.fill_between(range(len(dominant_eigenvector)), 0, dominant_eigenvector, 
                     alpha=0.3, color='blue')
    
    ax5.set_title(f'Dominant Eigenvector (λ = {eigenvals_full[dominant_idx]:.3f})', 
                  fontsize=12, fontweight='bold')
    ax5.set_xlabel('Neuron Index')
    ax5.set_ylabel('Eigenvector Component')
    ax5.grid(True, alpha=0.3)
    
    # Add statistics
    ev_mean = np.mean(dominant_eigenvector)
    ev_std = np.std(dominant_eigenvector)
    ax5.axhline(ev_mean, color='red', linestyle='--', alpha=0.7, label=f'Mean: {ev_mean:.3f}')
    ax5.legend()
    
    # === 6. SPECTRAL PROPERTIES SUMMARY ===
    ax6 = fig.add_subplot(gs[2, 2:])
    
    # Calculate additional spectral properties
    trace = np.trace(reservoir_weights)
    frobenius_norm = np.linalg.norm(reservoir_weights, 'fro')
    nuclear_norm = np.sum(sigma)
    
    # Create summary text
    summary_text = f"""
SPECTRAL PROPERTIES:

• Matrix Size: {N}×{N}
• Spectral Radius: {spectral_radius:.4f}
• Condition Number: {condition_number:.2e}
• Effective Rank: {effective_rank}/{N}
• Trace: {trace:.4f}
• Frobenius Norm: {frobenius_norm:.4f}
• Nuclear Norm: {nuclear_norm:.4f}

STABILITY ASSESSMENT:
• Echo State Property: {"Likely" if spectral_radius < 1.0 else "Uncertain"}
• Numerical Stability: {"Good" if condition_number < 1e12 else "Poor"}
• Effective Dimensionality: {effective_rank/N:.1%}
    """
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, 
            verticalalignment='top', fontsize=10, fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    ax6.set_title('Spectral Summary', fontsize=12, fontweight='bold')
    ax6.axis('off')
    
    # Add timestamp and metadata
    fig.text(0.98, 0.02, f'N={N} | Advanced Spectral Analysis | ρ={spectral_radius:.3f}', 
             fontsize=8, style='italic', alpha=0.7, ha='right')
    
    # Save figure if path provided
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        print(f"🌌 Spectral analysis saved to: {save_path}")
    
    plt.tight_layout()
    return fig

# ================================
# ANIMATION UTILITIES
# ================================

def create_reservoir_animation(states: np.ndarray, 
                              title: str = "Reservoir State Evolution",
                              save_path: Optional[str] = None,
                              figsize: Tuple[int, int] = (10, 8),
                              interval: int = 100,
                              max_frames: int = 200) -> FuncAnimation:
    """
    🎥 Create Animation of Reservoir State Evolution
    
    Creates an animated visualization of reservoir state evolution over time,
    showing dynamic patterns and temporal behavior.
    
    Args:
        states: Reservoir states over time (T×N matrix)
        title: Animation title
        save_path: Path to save animation (optional, .gif or .mp4)
        figsize: Figure size in inches
        interval: Frame interval in milliseconds
        max_frames: Maximum number of frames to animate
        
    Returns:
        matplotlib.animation.FuncAnimation: The animation object
        
    Research Background:
    ===================
    Dynamic visualization of reservoir states helps understand temporal patterns
    and phase space trajectories in reservoir computing systems.
    """
    T, N = states.shape
    
    # Limit frames if necessary
    if T > max_frames:
        frame_indices = np.linspace(0, T-1, max_frames, dtype=int)
        animation_states = states[frame_indices]
        T_anim = max_frames
    else:
        animation_states = states
        frame_indices = np.arange(T)
        T_anim = T
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # Setup first subplot: State heatmap
    im1 = ax1.imshow(animation_states[0].reshape(-1, 1), cmap='RdBu_r', 
                     vmin=np.min(animation_states), vmax=np.max(animation_states),
                     aspect='auto')
    ax1.set_title('Current State Vector')
    ax1.set_xlabel('State Value')
    ax1.set_ylabel('Neuron Index')
    
    # Setup second subplot: Activity time series
    mean_activity = np.mean(np.abs(animation_states), axis=1)
    line2, = ax2.plot([], [], 'b-', linewidth=2)
    ax2.set_xlim(0, T_anim-1)
    ax2.set_ylim(0, np.max(mean_activity) * 1.1)
    ax2.set_title('Mean Activity Over Time')
    ax2.set_xlabel('Time Step')
    ax2.set_ylabel('Mean |Activity|')
    ax2.grid(True, alpha=0.3)
    
    # Current time indicator
    time_line = ax2.axvline(x=0, color='red', linestyle='--', linewidth=2, alpha=0.7)
    
    # Animation function
    def animate(frame):
        # Update state heatmap
        im1.set_array(animation_states[frame].reshape(-1, 1))
        
        # Update time series
        line2.set_data(range(frame+1), mean_activity[:frame+1])
        
        # Update time indicator
        time_line.set_xdata([frame, frame])
        
        # Update title with time info
        original_time = frame_indices[frame] if T > max_frames else frame
        ax1.set_title(f'State Vector (t={original_time})')
        
        return [im1, line2, time_line]
    
    # Create animation
    anim = FuncAnimation(fig, animate, frames=T_anim, interval=interval, 
                        blit=False, repeat=True)
    
    # Save animation if path provided
    if save_path:
        if save_path.endswith('.gif'):
            anim.save(save_path, writer='pillow', fps=1000//interval)
            print(f"🎥 Animation saved as GIF to: {save_path}")
        elif save_path.endswith('.mp4'):
            anim.save(save_path, writer='ffmpeg', fps=1000//interval)
            print(f"🎥 Animation saved as MP4 to: {save_path}")
    
    plt.tight_layout()
    return anim

# Export the main functions
__all__ = ['visualize_spectral_analysis', 'create_reservoir_animation']
