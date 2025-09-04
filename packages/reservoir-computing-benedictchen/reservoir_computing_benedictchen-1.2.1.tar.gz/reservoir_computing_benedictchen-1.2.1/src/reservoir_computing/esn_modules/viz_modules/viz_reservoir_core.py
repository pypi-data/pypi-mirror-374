"""
🎨 Reservoir Computing - Core Reservoir Visualization Module
============================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Core reservoir structure visualization including connectivity patterns, 
eigenvalue analysis, weight distributions, and network topology visualization.

📊 VISUALIZATION CAPABILITIES:
=============================
• Enhanced reservoir connectivity matrix with statistical overlay
• Advanced eigenvalue analysis with stability regions  
• Network topology visualization with edge weights
• Connection degree distribution analysis
• Weight distribution with statistical analysis
• Professional publication-ready formatting

🔬 RESEARCH FOUNDATION:
======================
Based on foundational reservoir computing visualization techniques:
- Jaeger (2001): Original ESN visualization of spectral radius and connectivity
- Lukoševičius & Jaeger (2009): Reservoir analysis survey methods
- Schrauwen et al. (2007): Network topology analysis for reservoir computing

This module represents the core reservoir structure analysis components,
split from the 1438-line monolith for specialized network visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import signal, stats
import networkx as nx
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
import warnings
from abc import ABC, abstractmethod

# Configure professional plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class VizReservoirCoreMixin(ABC):
    """
    🎨 Core Reservoir Visualization Mixin
    
    Provides essential reservoir structure visualization capabilities
    for Echo State Networks and other reservoir computing systems.
    """
    
    # Abstract properties that must be provided by the implementing class
    @property
    @abstractmethod
    def W_reservoir(self) -> np.ndarray:
        """Reservoir weight matrix"""
        pass
    
    @property
    @abstractmethod
    def n_reservoir(self) -> int:
        """Number of reservoir neurons"""
        pass
    
    @property
    @abstractmethod
    def sparsity(self) -> float:
        """Reservoir sparsity level"""
        pass

    def visualize_reservoir(self, figsize: Tuple[int, int] = (15, 10), save_path: Optional[str] = None):
        """
        🏗️ Enhanced Reservoir Visualization with Comprehensive Analysis
        
        Creates professional-quality visualization of reservoir structure including
        connectivity patterns, eigenvalue spectrum, degree distributions, and more.
        
        Args:
            figsize: Figure size in inches
            save_path: Path to save figure (optional)
            
        Research Background:
        ===================
        Based on Jaeger (2001) original visualization extended with modern analysis
        techniques for comprehensive reservoir characterization.
        """
        
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle('Echo State Network Reservoir Analysis', fontsize=16, fontweight='bold')
        
        # 1. Enhanced Reservoir connectivity matrix with statistical overlay
        ax1 = axes[0, 0]
        im1 = ax1.imshow(self.W_reservoir, cmap='RdBu_r', aspect='auto', 
                        vmin=-np.max(np.abs(self.W_reservoir)), 
                        vmax=np.max(np.abs(self.W_reservoir)))
        ax1.set_title(f'Reservoir Matrix ({self.n_reservoir}×{self.n_reservoir})\n'
                     f'Density: {np.mean(self.W_reservoir != 0):.1%}')
        ax1.set_xlabel('From Neuron')
        ax1.set_ylabel('To Neuron')
        cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
        cbar1.set_label('Connection Strength', rotation=270, labelpad=15)
        
        # 2. Enhanced eigenvalue analysis with stability regions
        eigenvals = np.linalg.eigvals(self.W_reservoir)
        ax2 = axes[0, 1]
        scatter = ax2.scatter(eigenvals.real, eigenvals.imag, alpha=0.7, 
                            c=np.abs(eigenvals), cmap='viridis', s=30)
        
        # Unit circle for stability
        circle = plt.Circle((0, 0), 1, fill=False, color='red', linestyle='--', linewidth=2)
        ax2.add_patch(circle)
        
        # Echo state property region (|λ| < 1)
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
        degrees = np.sum(self.W_reservoir != 0, axis=1)
        ax3 = axes[0, 2]
        
        # Histogram with statistical overlay
        n, bins, patches = ax3.hist(degrees, bins=20, alpha=0.7, edgecolor='black', density=True)
        
        # Add normal distribution overlay if appropriate
        mu, sigma = stats.norm.fit(degrees)
        x = np.linspace(degrees.min(), degrees.max(), 100)
        ax3.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                label=f'Normal fit (μ={mu:.1f}, σ={sigma:.1f})')
        
        ax3.set_title(f'Degree Distribution\nSparsity: {self.sparsity:.1%}')
        ax3.set_xlabel('Number of Connections')
        ax3.set_ylabel('Probability Density')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Weight distribution with statistical analysis
        weights = self.W_reservoir[self.W_reservoir != 0]
        ax4 = axes[1, 0]
        
        # Enhanced histogram with multiple statistics
        n, bins, patches = ax4.hist(weights, bins=50, alpha=0.7, edgecolor='black', density=True)
        
        # Add statistical overlays
        ax4.axvline(weights.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {weights.mean():.3f}')
        ax4.axvline(np.median(weights), color='orange', linestyle='--', linewidth=2, label=f'Median: {np.median(weights):.3f}')
        
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
        
        # 5. Network topology visualization (sample for large networks)
        ax5 = axes[1, 1]
        if self.n_reservoir <= 100:  # Only for manageable sizes
            # Create networkx graph
            G = nx.from_numpy_array(self.W_reservoir, create_using=nx.DiGraph)
            pos = nx.spring_layout(G, k=1/np.sqrt(self.n_reservoir), iterations=50)
            
            # Draw network with edge weights represented by thickness and color
            edges = G.edges()
            weights_nx = [G[u][v]['weight'] for u, v in edges]
            
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                                 node_size=50, alpha=0.8, ax=ax5)
            nx.draw_networkx_edges(G, pos, edge_color=weights_nx, edge_cmap=plt.cm.RdBu_r,
                                 width=[abs(w)*3 for w in weights_nx], alpha=0.6, ax=ax5)
            
            ax5.set_title('Network Topology\n(Spring Layout)')
        else:
            # For large networks, show connection pattern heatmap
            # Sample a subset for visualization
            sample_size = min(50, self.n_reservoir)
            indices = np.random.choice(self.n_reservoir, sample_size, replace=False)
            sample_matrix = self.W_reservoir[np.ix_(indices, indices)]
            
            im5 = ax5.imshow(sample_matrix, cmap='RdBu_r', aspect='auto')
            ax5.set_title(f'Connection Pattern\n(Random {sample_size}×{sample_size} Sample)')
            plt.colorbar(im5, ax=ax5, shrink=0.6)
        
        ax5.axis('off')
        
        # 6. Spectral analysis - eigenvalue distribution
        ax6 = axes[1, 2]
        eigenval_magnitudes = np.abs(eigenvals)
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
            print(f"🎨 Reservoir visualization saved to: {save_path}")
        
        plt.show()
        
        # Enhanced statistics reporting
        self._print_reservoir_statistics(eigenvals, degrees, weights)
        
    def _print_reservoir_statistics(self, eigenvals: np.ndarray, degrees: np.ndarray, weights: np.ndarray):
        """
        📊 Print Comprehensive Reservoir Statistics
        
        Provides detailed statistical analysis of reservoir properties
        including spectral characteristics and connectivity patterns.
        """
        print("\n" + "="*70)
        print("🏗️  RESERVOIR STRUCTURE ANALYSIS")
        print("="*70)
        
        # Basic structure information
        print(f"📐 Matrix Dimensions: {self.n_reservoir}×{self.n_reservoir}")
        print(f"🕸️  Sparsity Level: {self.sparsity:.1%}")
        print(f"🔗 Total Connections: {np.sum(self.W_reservoir != 0)}")
        print(f"💪 Connection Density: {np.mean(self.W_reservoir != 0):.1%}")
        
        # Spectral properties
        spectral_radius = np.max(np.abs(eigenvals))
        print(f"\n🌌 SPECTRAL ANALYSIS:")
        print(f"   • Spectral Radius: {spectral_radius:.6f}")
        print(f"   • Echo State Property: {'✓ Satisfied' if spectral_radius < 1.0 else '⚠ Violated'}")
        print(f"   • Number of Eigenvalues: {len(eigenvals)}")
        print(f"   • Complex Eigenvalues: {np.sum(np.imag(eigenvals) != 0)}")
        
        # Connection statistics  
        print(f"\n🔗 CONNECTION ANALYSIS:")
        print(f"   • Mean Degree: {degrees.mean():.2f}")
        print(f"   • Degree Std: {degrees.std():.2f}")
        print(f"   • Max Degree: {degrees.max()}")
        print(f"   • Min Degree: {degrees.min()}")
        
        # Weight statistics
        print(f"\n⚖️  WEIGHT ANALYSIS:")
        print(f"   • Mean Weight: {weights.mean():.4f}")
        print(f"   • Weight Std: {weights.std():.4f}")
        print(f"   • Weight Range: [{weights.min():.4f}, {weights.max():.4f}]")
        print(f"   • Weight Skewness: {stats.skew(weights):.4f}")
        print(f"   • Weight Kurtosis: {stats.kurtosis(weights):.4f}")
        
        print("="*70)

# Export the main class
__all__ = ['VizReservoirCoreMixin']