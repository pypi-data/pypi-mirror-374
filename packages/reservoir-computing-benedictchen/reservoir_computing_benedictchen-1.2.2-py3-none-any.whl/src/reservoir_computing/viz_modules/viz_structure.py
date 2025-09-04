"""
🎨 Reservoir Computing - Structure Visualization Module
====================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Specialized visualization tools for reservoir structure analysis.
Provides comprehensive tools for analyzing and visualizing reservoir topology,
weight distributions, and connectivity patterns.

📊 VISUALIZATION CAPABILITIES:
=============================
• Weight matrix heatmaps with statistical overlays
• Eigenvalue spectrum analysis with stability regions  
• Network topology and connectivity patterns
• Degree distribution and topological properties
• Statistical summaries and professional formatting

🔬 RESEARCH FOUNDATION:
======================
Based on established reservoir analysis techniques:
- Jaeger (2001): Original ESN visualization methods for spectral analysis
- Lukoševičius & Jaeger (2009): Reservoir computing survey with analysis methods
- Schrauwen et al. (2007): Network topology analysis for reservoir computing
- Verstraeten et al. (2007): Structural analysis techniques

🎨 PROFESSIONAL STANDARDS:
=========================
• High-resolution vector graphics (300 DPI+)
• Perceptually uniform colormaps (viridis, plasma)
• Comprehensive legends and statistical annotations
• Publication-ready formatting and typography
• Research-accurate implementations

This module represents the structural analysis half of the visualization system,
split from the 1569-line monolith for better maintainability.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import signal, stats
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import networkx as nx
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
import warnings
from mpl_toolkits.mplot3d import Axes3D
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import pandas as pd
import logging

# Configure professional plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# ================================
# RESERVOIR STRUCTURE VISUALIZATION
# ================================

def visualize_reservoir_structure(reservoir_weights: np.ndarray, 
                                 input_weights: Optional[np.ndarray] = None,
                                 spectral_radius: Optional[float] = None,
                                 title: str = "Reservoir Structure Analysis",
                                 save_path: Optional[str] = None,
                                 figsize: Tuple[int, int] = (16, 12),
                                 dpi: int = 300) -> plt.Figure:
    """
    🏗️ Comprehensive Reservoir Structure Visualization
    
    Creates a multi-panel analysis of reservoir topology, weight distributions,
    and connectivity patterns with professional formatting and statistical overlays.
    
    Args:
        reservoir_weights: Reservoir weight matrix (N×N)
        input_weights: Input weight matrix (N×M), optional
        spectral_radius: Known spectral radius for annotation
        title: Figure title
        save_path: Path to save figure (optional)
        figsize: Figure size in inches
        dpi: Resolution for saved figures
        
    Returns:
        matplotlib.Figure: The complete structure analysis figure
        
    Research Background:
    ===================
    Based on Jaeger (2001) reservoir analysis methods and extended with
    modern network analysis techniques for comprehensive structural insight.
    """
    fig = plt.figure(figsize=figsize, dpi=dpi)
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.95)
    
    # Create subplot layout
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.4)
    
    # === 1. WEIGHT MATRIX HEATMAP ===
    ax1 = fig.add_subplot(gs[0, :2])
    
    # Create heatmap with statistical overlay
    im1 = ax1.imshow(reservoir_weights, cmap='RdBu_r', aspect='auto',
                     vmin=-np.max(np.abs(reservoir_weights)), 
                     vmax=np.max(np.abs(reservoir_weights)))
    ax1.set_title('Reservoir Weight Matrix', fontsize=12, fontweight='bold')
    ax1.set_xlabel('To Neuron')
    ax1.set_ylabel('From Neuron')
    
    # Add colorbar with statistical annotations
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Weight Value', rotation=270, labelpad=15)
    
    # Statistical overlay
    mean_weight = np.mean(reservoir_weights)
    std_weight = np.std(reservoir_weights)
    ax1.text(0.02, 0.98, f'μ = {mean_weight:.3f}\nσ = {std_weight:.3f}', 
             transform=ax1.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
             fontsize=9)
    
    # === 2. WEIGHT DISTRIBUTION ===
    ax2 = fig.add_subplot(gs[0, 2:])
    
    # Histogram with statistical overlays
    weights_flat = reservoir_weights.flatten()
    n_bins = min(50, int(np.sqrt(len(weights_flat))))
    
    ax2.hist(weights_flat, bins=n_bins, alpha=0.7, color='skyblue', 
             edgecolor='black', linewidth=0.5, density=True)
    
    # Overlay normal distribution fit
    x_fit = np.linspace(weights_flat.min(), weights_flat.max(), 100)
    normal_fit = stats.norm.pdf(x_fit, mean_weight, std_weight)
    ax2.plot(x_fit, normal_fit, 'r-', linewidth=2, label='Normal Fit')
    
    ax2.set_title('Weight Distribution Analysis', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Weight Value')
    ax2.set_ylabel('Probability Density')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Statistical annotations
    ax2.axvline(mean_weight, color='red', linestyle='--', alpha=0.7, label=f'Mean: {mean_weight:.3f}')
    ax2.axvline(mean_weight + std_weight, color='orange', linestyle='--', alpha=0.7)
    ax2.axvline(mean_weight - std_weight, color='orange', linestyle='--', alpha=0.7)
    
    # === 3. EIGENVALUE SPECTRUM ===
    ax3 = fig.add_subplot(gs[1, :2])
    
    # Calculate eigenvalues
    eigenvals = np.linalg.eigvals(reservoir_weights)
    
    # Plot eigenvalues in complex plane
    ax3.scatter(eigenvals.real, eigenvals.imag, alpha=0.6, s=20, c='blue')
    
    # Add unit circle for stability reference
    circle = patches.Circle((0, 0), 1, fill=False, color='red', linestyle='--', linewidth=2)
    ax3.add_patch(circle)
    
    # Calculate and display spectral radius
    computed_spectral_radius = np.max(np.abs(eigenvals))
    
    ax3.set_title(f'Eigenvalue Spectrum (ρ = {computed_spectral_radius:.3f})', 
                  fontsize=12, fontweight='bold')
    ax3.set_xlabel('Real Part')
    ax3.set_ylabel('Imaginary Part')
    ax3.grid(True, alpha=0.3)
    ax3.set_aspect('equal')
    
    # Highlight largest eigenvalue
    max_idx = np.argmax(np.abs(eigenvals))
    ax3.scatter(eigenvals[max_idx].real, eigenvals[max_idx].imag, 
                s=100, c='red', marker='x', linewidth=3, label=f'Max |λ| = {computed_spectral_radius:.3f}')
    ax3.legend()
    
    # === 4. CONNECTIVITY ANALYSIS ===
    ax4 = fig.add_subplot(gs[1, 2:])
    
    # Calculate connectivity statistics
    binary_weights = (np.abs(reservoir_weights) > 1e-10).astype(int)
    connectivity = np.sum(binary_weights) / (reservoir_weights.shape[0] ** 2)
    
    # In-degree and out-degree distributions
    in_degrees = np.sum(binary_weights, axis=0)
    out_degrees = np.sum(binary_weights, axis=1)
    
    ax4.hist(in_degrees, bins=20, alpha=0.5, label='In-degree', density=True)
    ax4.hist(out_degrees, bins=20, alpha=0.5, label='Out-degree', density=True)
    
    ax4.set_title(f'Degree Distribution (Connectivity: {connectivity:.1%})', 
                  fontsize=12, fontweight='bold')
    ax4.set_xlabel('Degree')
    ax4.set_ylabel('Probability Density')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # === 5. INPUT WEIGHTS ANALYSIS (if provided) ===
    if input_weights is not None:
        ax5 = fig.add_subplot(gs[2, :2])
        
        im5 = ax5.imshow(input_weights, cmap='viridis', aspect='auto')
        ax5.set_title('Input Weight Matrix', fontsize=12, fontweight='bold')
        ax5.set_xlabel('Input Dimension')
        ax5.set_ylabel('Reservoir Neuron')
        
        cbar5 = plt.colorbar(im5, ax=ax5, shrink=0.8)
        cbar5.set_label('Weight Value', rotation=270, labelpad=15)
        
        # Input weight statistics
        input_mean = np.mean(input_weights)
        input_std = np.std(input_weights)
        ax5.text(0.02, 0.98, f'μ = {input_mean:.3f}\nσ = {input_std:.3f}', 
                 transform=ax5.transAxes, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                 fontsize=9)
    
    # === 6. NETWORK TOPOLOGY (if small enough) ===
    if reservoir_weights.shape[0] <= 50:  # Only for small networks
        ax6 = fig.add_subplot(gs[2, 2:])
        
        # Create network graph
        G = nx.from_numpy_array(binary_weights, create_using=nx.DiGraph())
        
        # Calculate layout
        pos = nx.spring_layout(G, seed=42)
        
        # Draw network
        nx.draw_networkx_nodes(G, pos, ax=ax6, node_size=50, node_color='lightblue',
                              alpha=0.7)
        nx.draw_networkx_edges(G, pos, ax=ax6, edge_color='gray', alpha=0.5,
                              arrows=True, arrowsize=10, width=0.5)
        
        ax6.set_title(f'Network Topology ({len(G.nodes)} nodes)', 
                      fontsize=12, fontweight='bold')
        ax6.axis('off')
    else:
        # For large networks, show summary statistics
        ax6 = fig.add_subplot(gs[2, 2:])
        
        # Calculate network metrics
        metrics_text = f"""
        Network Statistics:
        • Nodes: {reservoir_weights.shape[0]}
        • Edges: {np.sum(binary_weights)}
        • Connectivity: {connectivity:.1%}
        • Mean In-degree: {np.mean(in_degrees):.1f}
        • Mean Out-degree: {np.mean(out_degrees):.1f}
        • Spectral Radius: {computed_spectral_radius:.3f}
        """
        
        ax6.text(0.1, 0.5, metrics_text, transform=ax6.transAxes,
                fontsize=11, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        ax6.set_title('Network Summary', fontsize=12, fontweight='bold')
        ax6.axis('off')
    
    # Add timestamp and metadata
    fig.text(0.02, 0.02, f'Generated with Reservoir Computing Visualization Suite', 
             fontsize=8, style='italic', alpha=0.7)
    
    # Save figure if path provided
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        print(f"📊 Structure analysis saved to: {save_path}")
    
    plt.tight_layout()
    return fig

# Export the main function
__all__ = ['visualize_reservoir_structure']
