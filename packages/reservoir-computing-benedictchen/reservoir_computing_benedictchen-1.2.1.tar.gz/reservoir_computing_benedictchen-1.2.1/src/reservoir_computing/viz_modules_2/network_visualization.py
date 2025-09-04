"""
🎨 Network Visualization - Reservoir Structure and Connectivity Analysis
====================================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides network structure visualization capabilities for Echo State Networks,
including reservoir connectivity matrices, eigenvalue analysis, and network topology.

Based on: Jaeger, H. (2001) "Echo state network" visualization methods
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import stats
import networkx as nx
from typing import Optional, Tuple, Dict, Any, List, Union
import warnings
import logging

# Configure logging
logger = logging.getLogger(__name__)


class VisualizationMixin:
    """
    🎨 Comprehensive Visualization Mixin for Echo State Networks
    
    This mixin provides extensive visualization capabilities for analyzing
    reservoir computing systems from network structure perspective.
    """
    
    def visualize_reservoir(self, figsize: Tuple[int, int] = (15, 10), save_path: Optional[str] = None):
        """
        Enhanced reservoir visualization with comprehensive analysis
        
        Based on Jaeger (2001) original visualization extended with modern analysis
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
        
        # Plot eigenvalues in complex plane
        ax2.scatter(eigenvals.real, eigenvals.imag, alpha=0.7, s=30, c='blue', edgecolors='darkblue')
        
        # Add unit circle for stability analysis
        theta = np.linspace(0, 2*np.pi, 100)
        ax2.plot(np.cos(theta), np.sin(theta), 'r--', linewidth=2, label='Unit Circle')
        
        # Highlight spectral radius
        spectral_radius = np.max(np.abs(eigenvals))
        max_eigenval = eigenvals[np.argmax(np.abs(eigenvals))]
        ax2.scatter(max_eigenval.real, max_eigenval.imag, s=100, c='red', marker='x', linewidth=3)
        
        ax2.set_xlabel('Real Part')
        ax2.set_ylabel('Imaginary Part')
        ax2.set_title(f'Eigenvalue Distribution\nSpectral Radius: {spectral_radius:.4f}')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.axis('equal')
        
        # Add stability assessment
        stability_status = "Stable" if spectral_radius < 1.0 else "Unstable"
        stability_color = "green" if spectral_radius < 1.0 else "red"
        ax2.text(0.02, 0.98, f'Status: {stability_status}', transform=ax2.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=stability_color, alpha=0.3),
                verticalalignment='top')
        
        # 3. Input-to-reservoir connectivity analysis
        ax3 = axes[0, 2]
        if hasattr(self, 'W_in') and self.W_in is not None:
            im3 = ax3.imshow(self.W_in.T, cmap='viridis', aspect='auto')
            ax3.set_title(f'Input Weights\n({self.n_inputs}→{self.n_reservoir})')
            ax3.set_xlabel('Input Dimension')
            ax3.set_ylabel('Reservoir Neuron')
            cbar3 = plt.colorbar(im3, ax=ax3, shrink=0.8)
            cbar3.set_label('Weight Value', rotation=270, labelpad=15)
            
            # Add statistics
            input_stats = f'Mean: {self.W_in.mean():.3f}\nStd: {self.W_in.std():.3f}'
            ax3.text(0.02, 0.98, input_stats, transform=ax3.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                    verticalalignment='top', fontsize=8)
        else:
            ax3.text(0.5, 0.5, 'Input weights\nnot available', 
                    ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Input Weights')
        
        # 4. Reservoir-to-output connectivity
        ax4 = axes[1, 0]
        if hasattr(self, 'W_out') and self.W_out is not None:
            im4 = ax4.imshow(self.W_out, cmap='plasma', aspect='auto')
            ax4.set_title(f'Output Weights\n({self.n_reservoir}→{self.n_outputs})')
            ax4.set_xlabel('Reservoir Neuron')
            ax4.set_ylabel('Output Dimension')
            cbar4 = plt.colorbar(im4, ax=ax4, shrink=0.8)
            cbar4.set_label('Weight Value', rotation=270, labelpad=15)
            
            # Add statistics
            output_stats = f'Mean: {self.W_out.mean():.3f}\nStd: {self.W_out.std():.3f}'
            ax4.text(0.02, 0.98, output_stats, transform=ax4.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                    verticalalignment='top', fontsize=8)
        else:
            ax4.text(0.5, 0.5, 'Output weights\nnot available', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Output Weights')
        
        # 5. Connection strength distribution
        ax5 = axes[1, 1]
        reservoir_weights = self.W_reservoir[self.W_reservoir != 0]
        if len(reservoir_weights) > 0:
            ax5.hist(reservoir_weights, bins=50, alpha=0.7, density=True, edgecolor='black')
            
            # Fit normal distribution
            mu, sigma = stats.norm.fit(reservoir_weights)
            x = np.linspace(reservoir_weights.min(), reservoir_weights.max(), 100)
            ax5.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                    label=f'Normal fit\n(μ={mu:.3f}, σ={sigma:.3f})')
            
            ax5.set_xlabel('Connection Strength')
            ax5.set_ylabel('Density')
            ax5.set_title('Weight Distribution')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
        else:
            ax5.text(0.5, 0.5, 'No connections\nfound', 
                    ha='center', va='center', transform=ax5.transAxes)
            ax5.set_title('Weight Distribution')
        
        # 6. Network topology analysis
        ax6 = axes[1, 2]
        try:
            # Create networkx graph for topology analysis
            G = nx.from_numpy_array(np.abs(self.W_reservoir))
            
            if G.number_of_nodes() > 0:
                # Calculate network metrics
                degree_centrality = nx.degree_centrality(G)
                clustering_coef = nx.average_clustering(G)
                
                # Plot degree distribution
                degrees = [G.degree(n) for n in G.nodes()]
                if degrees:
                    ax6.hist(degrees, bins=20, alpha=0.7, edgecolor='black')
                    ax6.set_xlabel('Node Degree')
                    ax6.set_ylabel('Frequency')
                    ax6.set_title(f'Degree Distribution\nClustering: {clustering_coef:.3f}')
                    ax6.grid(True, alpha=0.3)
                    
                    # Add statistics
                    degree_stats = f'Mean: {np.mean(degrees):.1f}\nMax: {max(degrees)}'
                    ax6.text(0.98, 0.98, degree_stats, transform=ax6.transAxes,
                            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                            verticalalignment='top', horizontalalignment='right', fontsize=8)
                else:
                    ax6.text(0.5, 0.5, 'No degree data', ha='center', va='center', transform=ax6.transAxes)
            else:
                ax6.text(0.5, 0.5, 'Empty network', ha='center', va='center', transform=ax6.transAxes)
                ax6.set_title('Degree Distribution')
        except Exception as e:
            logger.warning(f"Network analysis failed: {e}")
            ax6.text(0.5, 0.5, 'Network analysis\nfailed', ha='center', va='center', transform=ax6.transAxes)
            ax6.set_title('Degree Distribution')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.show()

    def visualize_connectivity_patterns(self, figsize: Tuple[int, int] = (12, 8), save_path: Optional[str] = None):
        """
        Analyze and visualize connectivity patterns in the reservoir
        """
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('Reservoir Connectivity Pattern Analysis', fontsize=14, fontweight='bold')
        
        # 1. Connection density heatmap
        ax1 = axes[0, 0]
        block_size = max(1, self.n_reservoir // 20)  # Divide into blocks
        n_blocks = self.n_reservoir // block_size
        
        if n_blocks > 1:
            density_map = np.zeros((n_blocks, n_blocks))
            for i in range(n_blocks):
                for j in range(n_blocks):
                    block = self.W_reservoir[i*block_size:(i+1)*block_size, 
                                           j*block_size:(j+1)*block_size]
                    density_map[i, j] = np.mean(block != 0)
            
            im1 = ax1.imshow(density_map, cmap='YlOrRd', vmin=0, vmax=1)
            ax1.set_title(f'Connection Density Map\n({n_blocks}×{n_blocks} blocks)')
            ax1.set_xlabel('Block Column')
            ax1.set_ylabel('Block Row')
            plt.colorbar(im1, ax=ax1, shrink=0.8, label='Density')
        else:
            ax1.text(0.5, 0.5, 'Reservoir too small\nfor block analysis', 
                    ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Connection Density Map')
        
        # 2. Distance-based connectivity analysis
        ax2 = axes[0, 1]
        try:
            # Create distance matrix based on indices
            positions = np.arange(self.n_reservoir).reshape(-1, 1)
            distances = np.abs(positions - positions.T)
            
            # Flatten for analysis
            dist_flat = distances.flatten()
            conn_flat = (self.W_reservoir != 0).flatten()
            
            # Bin distances and calculate connection probability
            max_dist = distances.max()
            dist_bins = np.linspace(0, max_dist, 20)
            conn_probs = []
            
            for i in range(len(dist_bins) - 1):
                mask = (dist_flat >= dist_bins[i]) & (dist_flat < dist_bins[i+1])
                if np.sum(mask) > 0:
                    conn_probs.append(np.mean(conn_flat[mask]))
                else:
                    conn_probs.append(0)
            
            bin_centers = (dist_bins[:-1] + dist_bins[1:]) / 2
            ax2.plot(bin_centers, conn_probs, 'bo-', linewidth=2, markersize=4)
            ax2.set_xlabel('Index Distance')
            ax2.set_ylabel('Connection Probability')
            ax2.set_title('Distance-based Connectivity')
            ax2.grid(True, alpha=0.3)
            
        except Exception as e:
            logger.warning(f"Distance analysis failed: {e}")
            ax2.text(0.5, 0.5, 'Distance analysis\nfailed', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Distance-based Connectivity')
        
        # 3. In-degree and out-degree distribution
        ax3 = axes[1, 0]
        
        # Calculate degrees
        in_degrees = np.sum(self.W_reservoir != 0, axis=0)  # Incoming connections
        out_degrees = np.sum(self.W_reservoir != 0, axis=1)  # Outgoing connections
        
        ax3.scatter(in_degrees, out_degrees, alpha=0.6, s=30)
        ax3.set_xlabel('In-degree')
        ax3.set_ylabel('Out-degree')
        ax3.set_title('Degree Correlation')
        ax3.grid(True, alpha=0.3)
        
        # Add correlation
        if len(in_degrees) > 1:
            corr_coef = np.corrcoef(in_degrees, out_degrees)[0, 1]
            ax3.text(0.02, 0.98, f'Correlation: {corr_coef:.3f}', 
                    transform=ax3.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                    verticalalignment='top')
        
        # 4. Weight magnitude analysis
        ax4 = axes[1, 1]
        
        # Separate positive and negative weights
        pos_weights = self.W_reservoir[self.W_reservoir > 0]
        neg_weights = self.W_reservoir[self.W_reservoir < 0]
        
        bins = np.linspace(-np.max(np.abs(self.W_reservoir)), 
                          np.max(np.abs(self.W_reservoir)), 50)
        
        ax4.hist(pos_weights, bins=bins[bins >= 0], alpha=0.7, color='red', 
                label=f'Positive ({len(pos_weights)})', density=True)
        ax4.hist(neg_weights, bins=bins[bins <= 0], alpha=0.7, color='blue',
                label=f'Negative ({len(neg_weights)})', density=True)
        
        ax4.set_xlabel('Weight Value')
        ax4.set_ylabel('Density')
        ax4.set_title('Weight Polarity Distribution')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.show()


def print_network_statistics(reservoir_matrix: np.ndarray, 
                           input_weights: Optional[np.ndarray] = None,
                           output_weights: Optional[np.ndarray] = None) -> None:
    """
    Print comprehensive network statistics
    
    Args:
        reservoir_matrix: Reservoir weight matrix
        input_weights: Input weight matrix [optional]
        output_weights: Output weight matrix [optional]
    """
    print("\n" + "="*60)
    print("🎨 NETWORK STRUCTURE STATISTICS")
    print("="*60)
    
    n_reservoir = reservoir_matrix.shape[0]
    
    # Basic network properties
    print(f"\n🏗️  NETWORK ARCHITECTURE:")
    print(f"   Reservoir size: {n_reservoir}")
    print(f"   Total possible connections: {n_reservoir * n_reservoir}")
    
    # Connection statistics
    non_zero = reservoir_matrix != 0
    n_connections = np.sum(non_zero)
    density = n_connections / (n_reservoir * n_reservoir)
    
    print(f"\n🔗 CONNECTION ANALYSIS:")
    print(f"   Active connections: {n_connections}")
    print(f"   Connection density: {density:.4f} ({density*100:.2f}%)")
    print(f"   Sparsity: {1-density:.4f}")
    
    # Weight statistics
    active_weights = reservoir_matrix[non_zero]
    if len(active_weights) > 0:
        print(f"\n⚖️  WEIGHT STATISTICS:")
        print(f"   Weight range: [{active_weights.min():.4f}, {active_weights.max():.4f}]")
        print(f"   Mean weight: {active_weights.mean():.4f}")
        print(f"   Weight std: {active_weights.std():.4f}")
        
        pos_weights = active_weights[active_weights > 0]
        neg_weights = active_weights[active_weights < 0]
        print(f"   Positive weights: {len(pos_weights)} ({len(pos_weights)/len(active_weights)*100:.1f}%)")
        print(f"   Negative weights: {len(neg_weights)} ({len(neg_weights)/len(active_weights)*100:.1f}%)")
    
    # Spectral analysis
    try:
        eigenvals = np.linalg.eigvals(reservoir_matrix)
        spectral_radius = np.max(np.abs(eigenvals))
        
        print(f"\n📊 SPECTRAL PROPERTIES:")
        print(f"   Spectral radius: {spectral_radius:.4f}")
        print(f"   Stability: {'Stable' if spectral_radius < 1.0 else 'Unstable'}")
        print(f"   Largest eigenvalue: {eigenvals[np.argmax(np.abs(eigenvals))]:.4f}")
        
        # Count eigenvalues inside/outside unit circle
        inside_unit = np.sum(np.abs(eigenvals) < 1.0)
        print(f"   Eigenvalues inside unit circle: {inside_unit}/{len(eigenvals)} ({inside_unit/len(eigenvals)*100:.1f}%)")
        
    except Exception as e:
        logger.warning(f"Spectral analysis failed: {e}")
        print(f"\n📊 SPECTRAL PROPERTIES: Analysis failed")
    
    # Input/Output statistics
    if input_weights is not None:
        print(f"\n📥 INPUT CONNECTIVITY:")
        print(f"   Input dimensions: {input_weights.shape[1]}")
        print(f"   Input weight range: [{input_weights.min():.4f}, {input_weights.max():.4f}]")
        print(f"   Input connections per neuron: {np.mean(np.sum(input_weights != 0, axis=1)):.2f}")
    
    if output_weights is not None:
        print(f"\n📤 OUTPUT CONNECTIVITY:")
        print(f"   Output dimensions: {output_weights.shape[0]}")
        print(f"   Output weight range: [{output_weights.min():.4f}, {output_weights.max():.4f}]")
        print(f"   Output connections per dimension: {np.mean(np.sum(output_weights != 0, axis=1)):.2f}")
    
    print("="*60)