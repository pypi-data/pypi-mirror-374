"""
🏗️ Structure Visualization - Reservoir Architecture Analysis
=============================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides visualization tools for analyzing the structural properties
of reservoir computing systems, including weight matrices, eigenvalue spectra,
network topology, and connectivity patterns.

Based on: Jaeger, H. (2001) "The 'Echo State' Approach to Analysing and Training RNNs"
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import stats
import networkx as nx
from typing import Optional, Tuple, Dict, Any, List
import warnings
import logging

# Configure logging
logger = logging.getLogger(__name__)


def visualize_reservoir_structure(reservoir_weights: np.ndarray, 
                                 sparsity: float,
                                 figsize: Tuple[int, int] = (15, 10),
                                 save_path: Optional[str] = None) -> None:
    """
    Comprehensive reservoir structure visualization with statistical analysis.
    
    🔬 **Research Background:**
    Visualization of reservoir connectivity patterns based on Jaeger (2001) original
    methods extended with modern graph theory analysis and spectral properties.
    
    **Key Visualizations:**
    1. **Weight Matrix Heatmap**: Full connectivity pattern with statistical overlays
    2. **Eigenvalue Spectrum**: Complex plane analysis with stability regions
    3. **Degree Distribution**: Connection pattern statistics and fits
    4. **Weight Distribution**: Statistical analysis of connection strengths
    5. **Network Topology**: Graph visualization for manageable sizes
    6. **Spectral Properties**: Phase distribution and magnitude analysis
    
    Args:
        reservoir_weights: Reservoir weight matrix (n_reservoir × n_reservoir)
        sparsity: Target sparsity level for reference
        figsize: Figure size for the visualization
        save_path: Optional path to save the visualization
        
    References:
        - Jaeger, H. (2001). "The 'echo state' approach to analysing and training RNNs"
        - Newman, M.E.J. (2003). "The structure and function of complex networks"
    """
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle('Echo State Network Reservoir Analysis', fontsize=16, fontweight='bold')
    
    n_reservoir = reservoir_weights.shape[0]
    
    # 1. Enhanced Reservoir connectivity matrix
    ax1 = axes[0, 0]
    im1 = ax1.imshow(reservoir_weights, cmap='RdBu_r', aspect='auto', 
                    vmin=-np.max(np.abs(reservoir_weights)), 
                    vmax=np.max(np.abs(reservoir_weights)))
    ax1.set_title(f'Reservoir Matrix ({n_reservoir}×{n_reservoir})\n'
                 f'Density: {np.mean(reservoir_weights != 0):.1%}')
    ax1.set_xlabel('From Neuron')
    ax1.set_ylabel('To Neuron')
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Connection Strength', rotation=270, labelpad=15)
    
    # 2. Enhanced eigenvalue analysis with stability regions
    eigenvals = np.linalg.eigvals(reservoir_weights)
    ax2 = axes[0, 1]
    scatter = ax2.scatter(eigenvals.real, eigenvals.imag, alpha=0.7, 
                        c=np.abs(eigenvals), cmap='viridis', s=30)
    
    # Unit circle for stability
    circle = plt.Circle((0, 0), 1, fill=False, color='red', linestyle='--', linewidth=2)
    ax2.add_patch(circle)
    
    # Echo state property region
    max_eigenval = np.max(np.abs(eigenvals))
    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax2.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    
    ax2.set_title(f'Eigenvalue Spectrum\nSpectral Radius: {max_eigenval:.4f}')
    ax2.set_xlabel('Real Part')
    ax2.set_ylabel('Imaginary Part')
    ax2.axis('equal')
    ax2.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax2, shrink=0.8, label='|λ|')
    
    # Add stability annotation
    if max_eigenval < 1:
        ax2.text(0.02, 0.98, '✓ Echo State Property', transform=ax2.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7),
                verticalalignment='top')
    else:
        ax2.text(0.02, 0.98, '⚠ Unstable Regime', transform=ax2.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7),
                verticalalignment='top')
    
    # 3. Advanced connection analysis
    degrees = np.sum(reservoir_weights != 0, axis=1)
    ax3 = axes[0, 2]
    
    # Histogram with statistical overlay
    n, bins, patches = ax3.hist(degrees, bins=20, alpha=0.7, edgecolor='black', density=True)
    
    # Add normal distribution overlay
    if len(degrees) > 1:
        mu, sigma = stats.norm.fit(degrees)
        x = np.linspace(degrees.min(), degrees.max(), 100)
        ax3.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                label=f'Normal fit (μ={mu:.1f}, σ={sigma:.1f})')
    
    ax3.set_title(f'Degree Distribution\nSparsity: {sparsity:.1%}')
    ax3.set_xlabel('Number of Connections')
    ax3.set_ylabel('Probability Density')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Weight distribution with statistical analysis
    weights = reservoir_weights[reservoir_weights != 0]
    ax4 = axes[1, 0]
    
    if len(weights) > 0:
        # Enhanced histogram with statistics
        n, bins, patches = ax4.hist(weights, bins=50, alpha=0.7, edgecolor='black', density=True)
        
        # Add statistical overlays
        ax4.axvline(weights.mean(), color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {weights.mean():.3f}')
        ax4.axvline(np.median(weights), color='orange', linestyle='--', linewidth=2, 
                   label=f'Median: {np.median(weights):.3f}')
        
        ax4.set_title('Weight Distribution Analysis')
        ax4.set_xlabel('Weight Value')
        ax4.set_ylabel('Probability Density')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Add text box with statistics
        stats_text = f'Std: {weights.std():.3f}\nSkew: {stats.skew(weights):.3f}\nKurt: {stats.kurtosis(weights):.3f}'
        ax4.text(0.02, 0.98, stats_text, transform=ax4.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top', fontsize=9)
    else:
        ax4.text(0.5, 0.5, 'No connections found', ha='center', va='center', 
                transform=ax4.transAxes)
        ax4.set_title('Weight Distribution Analysis')
    
    # 5. Network topology visualization
    ax5 = axes[1, 1]
    if n_reservoir <= 100:  # Only for manageable sizes
        try:
            # Create networkx graph
            G = nx.from_numpy_array(reservoir_weights, create_using=nx.DiGraph)
            pos = nx.spring_layout(G, k=1/np.sqrt(n_reservoir), iterations=50)
            
            # Draw network with edge weights
            edges = G.edges()
            weights_nx = [G[u][v]['weight'] for u, v in edges]
            
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                                 node_size=50, alpha=0.8, ax=ax5)
            if len(weights_nx) > 0:
                nx.draw_networkx_edges(G, pos, edge_color=weights_nx, edge_cmap=plt.cm.RdBu_r,
                                     width=[abs(w)*3 for w in weights_nx], alpha=0.6, ax=ax5)
            
            ax5.set_title('Network Topology\n(Spring Layout)')
        except Exception as e:
            logger.warning(f"Network visualization failed: {e}")
            ax5.text(0.5, 0.5, 'Network visualization\nfailed', ha='center', va='center', 
                    transform=ax5.transAxes)
            ax5.set_title('Network Topology')
    else:
        # For large networks, show connection pattern heatmap
        sample_size = min(50, n_reservoir)
        indices = np.random.choice(n_reservoir, sample_size, replace=False)
        sample_matrix = reservoir_weights[np.ix_(indices, indices)]
        
        im5 = ax5.imshow(sample_matrix, cmap='RdBu_r', aspect='auto')
        ax5.set_title(f'Connection Pattern\n(Random {sample_size}×{sample_size} Sample)')
        plt.colorbar(im5, ax=ax5, shrink=0.6)
    
    ax5.axis('off')
    
    # 6. Spectral analysis - eigenvalue phase distribution
    ax6 = axes[1, 2]
    eigenval_phases = np.angle(eigenvals)
    
    # Polar histogram of eigenvalue phases
    ax6_polar = plt.subplot(2, 3, 6, projection='polar')
    ax6_polar.hist(eigenval_phases, bins=20, alpha=0.7)
    ax6_polar.set_title('Eigenvalue Phase Distribution')
    ax6_polar.set_theta_zero_location('E')
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Print comprehensive statistics
    print_reservoir_statistics(reservoir_weights, eigenvals, degrees, weights, sparsity)


def print_reservoir_statistics(reservoir_weights: np.ndarray, 
                              eigenvals: np.ndarray,
                              degrees: np.ndarray, 
                              weights: np.ndarray, 
                              sparsity: float) -> None:
    """
    Print comprehensive reservoir statistics
    
    Args:
        reservoir_weights: Reservoir weight matrix
        eigenvals: Eigenvalues of the reservoir matrix
        degrees: Node degree distribution
        weights: Non-zero weight values
        sparsity: Target sparsity level
    """
    print("\n" + "="*60)
    print("📊 RESERVOIR STRUCTURE ANALYSIS STATISTICS")
    print("="*60)
    
    n_reservoir = reservoir_weights.shape[0]
    actual_sparsity = np.mean(reservoir_weights != 0)
    spectral_radius = np.max(np.abs(eigenvals))
    
    # Basic properties
    print(f"\n🏗️  BASIC PROPERTIES:")
    print(f"   Reservoir size: {n_reservoir} neurons")
    print(f"   Target sparsity: {sparsity:.1%}")
    print(f"   Actual density: {actual_sparsity:.1%}")
    print(f"   Total connections: {len(weights)}")
    print(f"   Spectral radius: {spectral_radius:.6f}")
    
    # Connectivity statistics
    if len(degrees) > 0:
        print(f"\n🔗 CONNECTIVITY STATISTICS:")
        print(f"   Average degree: {degrees.mean():.2f} ± {degrees.std():.2f}")
        print(f"   Degree range: [{degrees.min()}, {degrees.max()}]")
        print(f"   Degree skewness: {stats.skew(degrees):.3f}")
    
    # Weight statistics
    if len(weights) > 0:
        print(f"\n⚖️  WEIGHT STATISTICS:")
        print(f"   Weight mean: {weights.mean():.6f}")
        print(f"   Weight std: {weights.std():.6f}")
        print(f"   Weight range: [{weights.min():.6f}, {weights.max():.6f}]")
        print(f"   Weight skewness: {stats.skew(weights):.3f}")
        print(f"   Weight kurtosis: {stats.kurtosis(weights):.3f}")
    
    # Spectral properties
    print(f"\n🌈 SPECTRAL PROPERTIES:")
    print(f"   Complex eigenvalues: {np.sum(np.abs(eigenvals.imag) > 1e-10)}/{len(eigenvals)}")
    print(f"   Real eigenvalue range: [{eigenvals.real.min():.4f}, {eigenvals.real.max():.4f}]")
    print(f"   Echo State Property: {'✓ Satisfied' if spectral_radius < 1.0 else '⚠ Violated'}")
    
    # Stability assessment
    if spectral_radius < 0.95:
        stability = "🟢 Highly stable"
    elif spectral_radius < 1.0:
        stability = "🟡 Marginally stable"
    else:
        stability = "🔴 Unstable"
    print(f"   Stability assessment: {stability}")
    
    print("="*60)