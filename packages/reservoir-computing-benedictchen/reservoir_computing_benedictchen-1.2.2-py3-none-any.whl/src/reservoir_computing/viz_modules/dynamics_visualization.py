"""
🌊 Dynamics Visualization - Reservoir Temporal Behavior Analysis
================================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides visualization tools for analyzing the dynamic behavior
of reservoir computing systems, including state evolution, temporal correlations,
and frequency domain analysis.

Based on: Jaeger, H. (2001) "Short term memory in echo state networks"
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import signal, stats
from sklearn.decomposition import PCA
from typing import Optional, Tuple, Dict, Any, List
import warnings
import logging

# Configure logging
logger = logging.getLogger(__name__)


def visualize_reservoir_dynamics(states: np.ndarray, 
                               inputs: Optional[np.ndarray] = None, 
                               outputs: Optional[np.ndarray] = None, 
                               figsize: Tuple[int, int] = (15, 10),
                               save_path: Optional[str] = None) -> None:
    """
    Comprehensive visualization of reservoir dynamics and temporal behavior.
    
    🔬 **Research Background:**
    Analysis of reservoir state evolution based on dynamical systems theory
    and nonlinear time series analysis methods applied to reservoir computing.
    
    **Key Visualizations:**
    1. **State Evolution Heatmap**: Temporal activity patterns across neurons
    2. **State Trajectory (PCA)**: Reduced-dimensional state space analysis
    3. **Activity Statistics**: Mean vs. variance analysis of neural activity
    4. **Temporal Autocorrelation**: Memory characteristics and decay
    5. **Input-State Correlation**: Cross-correlation analysis
    6. **Power Spectral Density**: Frequency domain analysis of dynamics
    
    Args:
        states: Reservoir state matrix (time_steps × n_reservoir)
        inputs: Input sequence (time_steps × n_inputs) [optional]
        outputs: Output sequence (time_steps × n_outputs) [optional]
        figsize: Figure size for the visualization
        save_path: Optional path to save the visualization
        
    References:
        - Jaeger, H. (2001). "Short term memory in echo state networks"
        - Verstraeten, D., et al. (2007). "An experimental unification of reservoir computing methods"
    """
    fig = plt.figure(figsize=figsize)
    fig.suptitle('Echo State Network Dynamics Analysis', fontsize=16, fontweight='bold')
    
    # 1. State evolution heatmap
    ax1 = plt.subplot(2, 3, 1)
    
    # Sample neurons for visualization if too many
    max_neurons_display = 50
    if states.shape[1] > max_neurons_display:
        neuron_indices = np.random.choice(states.shape[1], max_neurons_display, replace=False)
        display_states = states[:, neuron_indices]
        title_suffix = f" (Random {max_neurons_display} neurons)"
    else:
        display_states = states
        neuron_indices = np.arange(states.shape[1])
        title_suffix = ""
        
    im1 = ax1.imshow(display_states.T, cmap='viridis', aspect='auto', interpolation='nearest')
    ax1.set_title(f'State Evolution{title_suffix}')
    ax1.set_xlabel('Time Step')
    ax1.set_ylabel('Neuron Index')
    plt.colorbar(im1, ax=ax1, shrink=0.8, label='Activation')
    
    # 2. State trajectory in reduced space (PCA)
    ax2 = plt.subplot(2, 3, 2)
    if states.shape[1] >= 3:
        try:
            pca = PCA(n_components=3)
            states_pca = pca.fit_transform(states)
            
            # 3D trajectory
            ax2 = plt.subplot(2, 3, 2, projection='3d')
            scatter = ax2.scatter(states_pca[:, 0], states_pca[:, 1], states_pca[:, 2],
                                c=np.arange(len(states_pca)), cmap='plasma', s=20)
            ax2.set_title(f'State Trajectory (PCA)\nVariance Explained: {pca.explained_variance_ratio_[:3].sum():.1%}')
            ax2.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
            ax2.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
            ax2.set_zlabel(f'PC3 ({pca.explained_variance_ratio_[2]:.1%})')
            plt.colorbar(scatter, ax=ax2, shrink=0.5, label='Time')
        except Exception as e:
            logger.warning(f"PCA visualization failed: {e}")
            ax2.text(0.5, 0.5, 'PCA visualization\nfailed', ha='center', va='center', 
                    transform=ax2.transAxes)
            ax2.set_title('State Trajectory (PCA)')
    else:
        ax2.text(0.5, 0.5, 'Insufficient dimensions\nfor PCA visualization', 
                ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('State Trajectory (PCA)')
    
    # 3. Activity patterns
    ax3 = plt.subplot(2, 3, 3)
    
    # Calculate and plot activity statistics
    mean_activity = np.mean(states, axis=0)
    std_activity = np.std(states, axis=0)
    
    ax3.scatter(mean_activity, std_activity, alpha=0.6, s=30)
    ax3.set_xlabel('Mean Activity')
    ax3.set_ylabel('Activity Std')
    ax3.set_title('Neuron Activity Statistics')
    ax3.grid(True, alpha=0.3)
    
    # Add correlation coefficient
    if len(mean_activity) > 1:
        corr_coef = np.corrcoef(mean_activity, std_activity)[0, 1]
        ax3.text(0.02, 0.98, f'Correlation: {corr_coef:.3f}', 
                transform=ax3.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top')
    
    # 4. Temporal correlation analysis
    ax4 = plt.subplot(2, 3, 4)
    
    # Compute autocorrelation for sample of neurons
    max_lag = min(50, states.shape[0] // 4)
    sample_neurons = min(10, states.shape[1])
    autocorrs = []
    
    for i in range(sample_neurons):
        if states.shape[0] > max_lag:
            autocorr = np.correlate(states[:, i], states[:, i], mode='full')
            autocorr = autocorr[len(autocorr)//2:][:max_lag]
            if autocorr[0] != 0:
                autocorr = autocorr / autocorr[0]  # Normalize
            autocorrs.append(autocorr)
    
    if autocorrs:
        # Plot mean autocorrelation with confidence bands
        mean_autocorr = np.mean(autocorrs, axis=0)
        std_autocorr = np.std(autocorrs, axis=0)
        lags = np.arange(len(mean_autocorr))
        
        ax4.plot(lags, mean_autocorr, 'b-', linewidth=2, label='Mean')
        ax4.fill_between(lags, mean_autocorr - std_autocorr, mean_autocorr + std_autocorr, 
                        alpha=0.3, label='±1 Std')
        ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax4.set_title('Temporal Autocorrelation')
        ax4.set_xlabel('Lag (time steps)')
        ax4.set_ylabel('Autocorrelation')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'Insufficient data for\nautocorrelation analysis', 
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Temporal Autocorrelation')
    
    # 5. Input-State relationship (if inputs provided)
    ax5 = plt.subplot(2, 3, 5)
    if inputs is not None:
        try:
            # Cross-correlation between input and reservoir states
            sample_size = min(100, states.shape[0])
            indices = np.random.choice(states.shape[0], sample_size, replace=False)
            
            input_sample = inputs[indices] if inputs.ndim > 1 else inputs[indices].reshape(-1, 1)
            state_sample = states[indices]
            
            # Calculate cross-correlation matrix
            n_inputs = input_sample.shape[1]
            n_display_neurons = min(20, states.shape[1])
            
            if n_inputs > 0 and n_display_neurons > 0:
                cross_corr = np.corrcoef(input_sample.T, state_sample[:, :n_display_neurons].T)[:n_inputs, n_inputs:]
                
                im5 = ax5.imshow(cross_corr, cmap='RdBu_r', aspect='auto', 
                               vmin=-1, vmax=1)
                ax5.set_title('Input-State Cross-correlation')
                ax5.set_xlabel('Reservoir Neurons')
                ax5.set_ylabel('Input Dimensions')
                plt.colorbar(im5, ax=ax5, shrink=0.8, label='Correlation')
            else:
                ax5.text(0.5, 0.5, 'Invalid input dimensions', ha='center', va='center', 
                        transform=ax5.transAxes)
                ax5.set_title('Input-State Relationship')
        except Exception as e:
            logger.warning(f"Input-state correlation failed: {e}")
            ax5.text(0.5, 0.5, 'Cross-correlation\nanalysis failed', ha='center', va='center', 
                    transform=ax5.transAxes)
            ax5.set_title('Input-State Relationship')
    else:
        ax5.text(0.5, 0.5, 'No input data\nprovided', ha='center', va='center', 
                transform=ax5.transAxes)
        ax5.set_title('Input-State Relationship')
    
    # 6. Spectral analysis of dynamics
    ax6 = plt.subplot(2, 3, 6)
    
    # Power spectral density of sample neurons
    sample_neurons = min(5, states.shape[1])
    frequencies = []
    power_spectra = []
    
    for i in range(sample_neurons):
        if len(states[:, i]) > 10:  # Ensure sufficient data
            try:
                f, Pxx = signal.periodogram(states[:, i], nperseg=min(256, len(states)//4))
                frequencies.append(f)
                power_spectra.append(Pxx)
            except Exception as e:
                logger.warning(f"Periodogram computation failed for neuron {i}: {e}")
    
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
        ax6.text(0.5, 0.5, 'Insufficient data\nfor spectral analysis', 
                ha='center', va='center', transform=ax6.transAxes)
        ax6.set_title('Power Spectral Density')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    plt.show()
    
    # Print dynamics statistics
    print_dynamics_statistics(states, inputs, outputs)


def print_dynamics_statistics(states: np.ndarray, 
                             inputs: Optional[np.ndarray] = None,
                             outputs: Optional[np.ndarray] = None) -> None:
    """
    Print comprehensive dynamics statistics
    
    Args:
        states: Reservoir state matrix (time_steps × n_reservoir)
        inputs: Input sequence [optional]
        outputs: Output sequence [optional]
    """
    print("\n" + "="*60)
    print("🌊 RESERVOIR DYNAMICS ANALYSIS STATISTICS")
    print("="*60)
    
    time_steps, n_reservoir = states.shape
    
    # Basic dynamics properties
    print(f"\n⏱️  TEMPORAL PROPERTIES:")
    print(f"   Time steps: {time_steps}")
    print(f"   Reservoir size: {n_reservoir}")
    print(f"   State range: [{states.min():.4f}, {states.max():.4f}]")
    print(f"   Mean activity: {states.mean():.4f} ± {states.std():.4f}")
    
    # Activity statistics
    mean_activities = np.mean(states, axis=0)
    std_activities = np.std(states, axis=0)
    
    print(f"\n🧠 NEURAL ACTIVITY:")
    print(f"   Most active neuron: {mean_activities.max():.4f} (index {np.argmax(mean_activities)})")
    print(f"   Least active neuron: {mean_activities.min():.4f} (index {np.argmin(mean_activities)})")
    print(f"   Activity variance: {np.var(mean_activities):.6f}")
    print(f"   Silent neurons: {np.sum(np.abs(mean_activities) < 1e-6)} ({np.sum(np.abs(mean_activities) < 1e-6)/n_reservoir:.1%})")
    
    # Temporal correlation
    if time_steps > 10:
        # Sample a few neurons for correlation analysis
        sample_size = min(5, n_reservoir)
        sample_indices = np.random.choice(n_reservoir, sample_size, replace=False)
        
        autocorrs = []
        for i in sample_indices:
            if states.shape[0] > 20:
                autocorr = np.corrcoef(states[:-1, i], states[1:, i])[0, 1]
                if not np.isnan(autocorr):
                    autocorrs.append(autocorr)
        
        if autocorrs:
            mean_autocorr = np.mean(autocorrs)
            print(f"\n🔗 TEMPORAL CORRELATION:")
            print(f"   Mean lag-1 autocorrelation: {mean_autocorr:.4f}")
            print(f"   Memory strength: {'Strong' if abs(mean_autocorr) > 0.7 else 'Moderate' if abs(mean_autocorr) > 0.3 else 'Weak'}")
    
    # Input relationship
    if inputs is not None:
        print(f"\n📥 INPUT-STATE RELATIONSHIP:")
        n_inputs = inputs.shape[1] if inputs.ndim > 1 else 1
        print(f"   Input dimensions: {n_inputs}")
        print(f"   Input range: [{inputs.min():.4f}, {inputs.max():.4f}]")
        
        # Compute input-state correlation for a sample
        if n_inputs <= 10 and n_reservoir <= 50:  # For computational efficiency
            try:
                input_flat = inputs.flatten() if inputs.ndim > 1 else inputs
                sample_neurons = min(10, n_reservoir)
                correlations = []
                
                for i in range(sample_neurons):
                    corr = np.corrcoef(input_flat[:len(states)], states[:, i])[0, 1]
                    if not np.isnan(corr):
                        correlations.append(abs(corr))
                
                if correlations:
                    mean_corr = np.mean(correlations)
                    print(f"   Mean input-state correlation: {mean_corr:.4f}")
            except Exception as e:
                logger.warning(f"Input-state correlation computation failed: {e}")
    
    # Spectral properties
    try:
        # Power spectrum analysis for a sample neuron
        sample_neuron = states[:, 0]
        if len(sample_neuron) > 20:
            f, psd = signal.periodogram(sample_neuron)
            peak_freq = f[np.argmax(psd)]
            total_power = np.sum(psd)
            
            print(f"\n📊 FREQUENCY DOMAIN:")
            print(f"   Peak frequency: {peak_freq:.4f} (normalized)")
            print(f"   Total power: {total_power:.6f}")
            print(f"   Frequency bandwidth: {f.max():.4f}")
    except Exception as e:
        logger.debug(f"Spectral analysis failed: {e}")
    
    print("="*60)