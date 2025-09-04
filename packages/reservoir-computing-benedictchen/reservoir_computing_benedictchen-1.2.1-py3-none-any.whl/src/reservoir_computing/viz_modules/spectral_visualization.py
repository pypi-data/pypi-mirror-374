"""
📊 Spectral Visualization - Eigenvalue and Stability Analysis
==========================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides spectral analysis visualization for Echo State Networks,
focusing on eigenvalue distribution, stability analysis, and spectral properties.

Based on: Jaeger, H. (2001) "Echo state network" spectral analysis methods
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats, signal
from typing import Optional, Tuple, Dict, Any, List
import warnings
import logging

# Configure logging
logger = logging.getLogger(__name__)


def visualize_spectral_analysis(W_reservoir: np.ndarray,
                               figsize: Tuple[int, int] = (12, 8),
                               save_path: Optional[str] = None) -> None:
    """
    Comprehensive spectral analysis of reservoir matrix
    
    Args:
        W_reservoir: Reservoir weight matrix
        figsize: Figure size for visualization
        save_path: Optional path to save visualization
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Spectral Analysis of Reservoir Matrix', fontsize=14, fontweight='bold')
    
    # Compute eigenvalues
    eigenvals = np.linalg.eigvals(W_reservoir)
    spectral_radius = np.max(np.abs(eigenvals))
    
    # 1. Eigenvalue distribution in complex plane
    ax1 = axes[0, 0]
    ax1.scatter(eigenvals.real, eigenvals.imag, alpha=0.7, s=30, c='blue', edgecolors='darkblue')
    
    # Add unit circle
    theta = np.linspace(0, 2*np.pi, 100)
    ax1.plot(np.cos(theta), np.sin(theta), 'r--', linewidth=2, label='Unit Circle')
    
    # Highlight spectral radius
    max_eigenval = eigenvals[np.argmax(np.abs(eigenvals))]
    ax1.scatter(max_eigenval.real, max_eigenval.imag, s=100, c='red', marker='x', linewidth=3)
    
    ax1.set_xlabel('Real Part')
    ax1.set_ylabel('Imaginary Part')
    ax1.set_title(f'Eigenvalue Distribution\nSpectral Radius: {spectral_radius:.4f}')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # 2. Eigenvalue magnitude distribution
    ax2 = axes[0, 1]
    eigenval_mags = np.abs(eigenvals)
    
    ax2.hist(eigenval_mags, bins=30, alpha=0.7, density=True, edgecolor='black')
    ax2.axvline(x=spectral_radius, color='red', linestyle='--', linewidth=2, 
               label=f'Spectral Radius: {spectral_radius:.4f}')
    ax2.axvline(x=1.0, color='green', linestyle='--', linewidth=2, label='Unit Circle')
    
    ax2.set_xlabel('|λ|')
    ax2.set_ylabel('Density')
    ax2.set_title('Eigenvalue Magnitude Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Singular value spectrum
    ax3 = axes[1, 0]
    try:
        singular_vals = np.linalg.svd(W_reservoir, compute_uv=False)
        
        ax3.semilogy(range(1, len(singular_vals) + 1), singular_vals, 'bo-', markersize=4)
        ax3.set_xlabel('Index')
        ax3.set_ylabel('Singular Value (log scale)')
        ax3.set_title('Singular Value Spectrum')
        ax3.grid(True, alpha=0.3)
        
        # Add condition number
        condition_num = singular_vals[0] / singular_vals[-1] if singular_vals[-1] > 1e-15 else float('inf')
        ax3.text(0.02, 0.98, f'Condition Number: {condition_num:.2e}', 
                transform=ax3.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top')
        
    except Exception as e:
        logger.warning(f"SVD computation failed: {e}")
        ax3.text(0.5, 0.5, 'SVD computation\nfailed', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Singular Value Spectrum')
    
    # 4. Stability analysis
    ax4 = axes[1, 1]
    
    # Count eigenvalues inside/outside unit circle
    inside_unit = np.sum(np.abs(eigenvals) < 1.0)
    on_unit = np.sum(np.abs(np.abs(eigenvals) - 1.0) < 1e-10)
    outside_unit = len(eigenvals) - inside_unit - on_unit
    
    categories = ['Inside\nUnit Circle', 'On Unit\nCircle', 'Outside\nUnit Circle']
    counts = [inside_unit, on_unit, outside_unit]
    colors = ['green', 'yellow', 'red']
    
    bars = ax4.bar(categories, counts, color=colors, alpha=0.7, edgecolor='black')
    ax4.set_ylabel('Number of Eigenvalues')
    ax4.set_title('Stability Analysis')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add percentages
    total = len(eigenvals)
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}\n({count/total*100:.1f}%)', 
                ha='center', va='bottom')
    
    # Add stability assessment
    if spectral_radius < 1.0:
        stability_text = "✅ Stable (ρ < 1)"
        color = 'lightgreen'
    elif spectral_radius == 1.0:
        stability_text = "⚠️ Critical (ρ = 1)"
        color = 'lightyellow'
    else:
        stability_text = "❌ Unstable (ρ > 1)"
        color = 'lightcoral'
        
    ax4.text(0.02, 0.98, stability_text, transform=ax4.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.8),
            verticalalignment='top')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    plt.show()


def print_spectral_statistics(W_reservoir: np.ndarray) -> None:
    """
    Print comprehensive spectral statistics
    
    Args:
        W_reservoir: Reservoir weight matrix
    """
    print("\n" + "="*60)
    print("📊 SPECTRAL ANALYSIS STATISTICS")
    print("="*60)
    
    # Basic matrix properties
    n_reservoir = W_reservoir.shape[0]
    print(f"\n🏗️  MATRIX PROPERTIES:")
    print(f"   Matrix size: {n_reservoir}×{n_reservoir}")
    print(f"   Matrix norm (Frobenius): {np.linalg.norm(W_reservoir):.4f}")
    
    # Eigenvalue analysis
    eigenvals = np.linalg.eigvals(W_reservoir)
    spectral_radius = np.max(np.abs(eigenvals))
    
    print(f"\n👁️  EIGENVALUE ANALYSIS:")
    print(f"   Number of eigenvalues: {len(eigenvals)}")
    print(f"   Spectral radius: {spectral_radius:.6f}")
    print(f"   Largest eigenvalue: {eigenvals[np.argmax(np.abs(eigenvals))]:.6f}")
    
    # Stability analysis
    inside_unit = np.sum(np.abs(eigenvals) < 1.0)
    on_unit = np.sum(np.abs(np.abs(eigenvals) - 1.0) < 1e-10)
    outside_unit = len(eigenvals) - inside_unit - on_unit
    
    print(f"\n⚖️  STABILITY ANALYSIS:")
    print(f"   Eigenvalues inside unit circle: {inside_unit} ({inside_unit/len(eigenvals)*100:.1f}%)")
    print(f"   Eigenvalues on unit circle: {on_unit} ({on_unit/len(eigenvals)*100:.1f}%)")  
    print(f"   Eigenvalues outside unit circle: {outside_unit} ({outside_unit/len(eigenvals)*100:.1f}%)")
    
    if spectral_radius < 1.0:
        stability_status = "✅ STABLE (Echo State Property satisfied)"
    elif abs(spectral_radius - 1.0) < 1e-10:
        stability_status = "⚠️ CRITICAL (On stability boundary)"
    else:
        stability_status = "❌ UNSTABLE (Echo State Property violated)"
    
    print(f"   Stability status: {stability_status}")
    
    # Singular value analysis
    try:
        singular_vals = np.linalg.svd(W_reservoir, compute_uv=False)
        condition_num = singular_vals[0] / singular_vals[-1] if singular_vals[-1] > 1e-15 else float('inf')
        
        print(f"\n📈 SINGULAR VALUE ANALYSIS:")
        print(f"   Largest singular value: {singular_vals[0]:.6f}")
        print(f"   Smallest singular value: {singular_vals[-1]:.6e}")
        print(f"   Condition number: {condition_num:.2e}")
        print(f"   Effective rank: {np.sum(singular_vals > 1e-12)}")
        
        if condition_num < 1e12:
            conditioning = "✅ Well-conditioned"
        elif condition_num < 1e15:
            conditioning = "⚠️ Moderately ill-conditioned"  
        else:
            conditioning = "❌ Severely ill-conditioned"
        
        print(f"   Conditioning: {conditioning}")
        
    except Exception as e:
        logger.warning(f"Singular value analysis failed: {e}")
        print(f"\n📈 SINGULAR VALUE ANALYSIS: Failed")
    
    # Additional spectral properties
    real_eigenvals = eigenvals[np.isreal(eigenvals)].real
    complex_eigenvals = eigenvals[~np.isreal(eigenvals)]
    
    print(f"\n🔢 EIGENVALUE COMPOSITION:")
    print(f"   Real eigenvalues: {len(real_eigenvals)} ({len(real_eigenvals)/len(eigenvals)*100:.1f}%)")
    print(f"   Complex eigenvalues: {len(complex_eigenvals)} ({len(complex_eigenvals)/len(eigenvals)*100:.1f}%)")
    
    if len(real_eigenvals) > 0:
        print(f"   Real eigenvalue range: [{real_eigenvals.min():.4f}, {real_eigenvals.max():.4f}]")
    
    # Spectral gap (distance to unit circle)
    spectral_gap = 1.0 - spectral_radius
    print(f"\n🔍 SPECTRAL PROPERTIES:")
    print(f"   Spectral gap: {spectral_gap:.6f}")
    print(f"   Distance to instability: {abs(spectral_gap):.6f}")
    
    if spectral_gap > 0.1:
        gap_assessment = "✅ Large spectral gap (robust stability)"
    elif spectral_gap > 0.01:
        gap_assessment = "🟡 Moderate spectral gap"
    elif spectral_gap > 0:
        gap_assessment = "🟠 Small spectral gap (near critical)"
    else:
        gap_assessment = "🔴 Negative spectral gap (unstable)"
        
    print(f"   Gap assessment: {gap_assessment}")
    
    print("="*60)