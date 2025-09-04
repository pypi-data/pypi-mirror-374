"""
🌊 Reservoir Computing - Dynamics & Temporal Visualization Module
================================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Temporal dynamics visualization including state evolution, trajectory analysis,
activity patterns, and animated visualization of reservoir behavior over time.

📊 VISUALIZATION CAPABILITIES:
=============================
• State evolution heatmaps with neuron sampling
• 3D state trajectory visualization using PCA
• Activity pattern analysis and statistics
• Temporal autocorrelation analysis
• Input-state cross-correlation visualization
• Power spectral density analysis
• Animated state evolution for dynamic behavior

🔬 RESEARCH FOUNDATION:
======================
Based on advanced temporal analysis techniques from:
- Jaeger (2001): Original ESN temporal analysis methods
- Verstraeten et al. (2007): Memory capacity and temporal visualization
- Deng & Zhang (2007): Dynamic analysis visualization methods
- Appeltant et al. (2011): Information processing capacity visualization

This module represents the temporal dynamics and animation components,
split from the 1438-line monolith for specialized dynamic visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
from scipy import signal, stats
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from typing import Optional, Tuple, Dict, Any, List, Union
import warnings
from abc import ABC

# Configure professional plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class VizDynamicsTemporalMixin(ABC):
    """
    🌊 Dynamics & Temporal Visualization Mixin
    
    Provides comprehensive temporal analysis and animation capabilities
    for reservoir computing systems.
    """

    def visualize_dynamics(self, states: np.ndarray, inputs: Optional[np.ndarray] = None, 
                          outputs: Optional[np.ndarray] = None, figsize: Tuple[int, int] = (15, 10),
                          save_path: Optional[str] = None):
        """
        🌊 Comprehensive Visualization of Reservoir Dynamics and Temporal Behavior
        
        Creates multi-panel analysis of reservoir temporal dynamics including
        state evolution, trajectory analysis, and frequency domain characteristics.
        
        Args:
            states: Reservoir state matrix (time_steps × n_reservoir)
            inputs: Input sequence (time_steps × n_inputs) [optional]
            outputs: Output sequence (time_steps × n_outputs) [optional]
            figsize: Figure size in inches
            save_path: Path to save figure (optional)
            
        Research Background:
        ===================
        Based on advanced temporal analysis methods for understanding reservoir
        dynamics, memory capacity, and information processing characteristics.
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
            autocorr = np.correlate(states[:, i], states[:, i], mode='full')
            autocorr = autocorr[len(autocorr)//2:][:max_lag]
            autocorr = autocorr / autocorr[0]  # Normalize
            autocorrs.append(autocorr)
        
        # Plot mean autocorrelation with confidence bands
        mean_autocorr = np.mean(autocorrs, axis=0)
        std_autocorr = np.std(autocorrs, axis=0)
        lags = np.arange(max_lag)
        
        ax4.plot(lags, mean_autocorr, 'b-', linewidth=2, label='Mean')
        ax4.fill_between(lags, mean_autocorr - std_autocorr, mean_autocorr + std_autocorr, 
                        alpha=0.3, label='±1 Std')
        ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax4.set_title('Temporal Autocorrelation')
        ax4.set_xlabel('Lag (time steps)')
        ax4.set_ylabel('Autocorrelation')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Input-State relationship (if inputs provided)
        ax5 = plt.subplot(2, 3, 5)
        if inputs is not None:
            # Cross-correlation between input and reservoir states
            sample_size = min(100, states.shape[0])
            indices = np.random.choice(states.shape[0], sample_size, replace=False)
            
            input_sample = inputs[indices] if inputs.ndim > 1 else inputs[indices].reshape(-1, 1)
            state_sample = states[indices]
            
            # Calculate cross-correlation matrix
            n_inputs = input_sample.shape[1]
            n_display_neurons = min(20, states.shape[1])
            cross_corr = np.corrcoef(input_sample.T, state_sample[:, :n_display_neurons].T)[:n_inputs, n_inputs:]
            
            im5 = ax5.imshow(cross_corr, cmap='RdBu_r', aspect='auto', 
                           vmin=-1, vmax=1)
            ax5.set_title('Input-State Cross-correlation')
            ax5.set_xlabel('Reservoir Neurons')
            ax5.set_ylabel('Input Dimensions')
            plt.colorbar(im5, ax=ax5, shrink=0.8, label='Correlation')
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
                f, Pxx = signal.periodogram(states[:, i], nperseg=min(256, len(states)//4))
                frequencies.append(f)
                power_spectra.append(Pxx)
        
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
            print(f"🌊 Dynamics visualization saved to: {save_path}")
            
        plt.show()
        
        # Print dynamics statistics
        self._print_dynamics_statistics(states, inputs, outputs)

    def create_animation(self, states: np.ndarray, figsize: Tuple[int, int] = (10, 8),
                        interval: int = 100, save_path: Optional[str] = None) -> FuncAnimation:
        """
        🎥 Create Animation of Reservoir State Evolution
        
        Creates animated visualization of reservoir state evolution over time,
        showing dynamic patterns and temporal behavior.
        
        Args:
            states: Reservoir state matrix (time_steps × n_reservoir)
            figsize: Figure size in inches
            interval: Frame interval in milliseconds
            save_path: Path to save animation (optional, .gif or .mp4)
            
        Returns:
            matplotlib.animation.FuncAnimation: The animation object
            
        Research Background:
        ===================
        Dynamic visualization helps understand temporal patterns and phase
        space trajectories in reservoir computing systems.
        """
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle('Reservoir State Evolution Animation', fontsize=14, fontweight='bold')
        
        # Setup first subplot: State heatmap
        max_display = min(50, states.shape[1])
        display_indices = np.random.choice(states.shape[1], max_display, replace=False)
        
        im = ax1.imshow(states[0, display_indices].reshape(-1, 1), cmap='RdBu_r', 
                       vmin=np.min(states[:, display_indices]), vmax=np.max(states[:, display_indices]),
                       aspect='auto')
        ax1.set_title('Current State Vector')
        ax1.set_xlabel('State Value')
        ax1.set_ylabel('Neuron Index')
        
        # Setup second subplot: Activity time series
        mean_activity = np.mean(np.abs(states), axis=1)
        line, = ax2.plot([], [], 'b-', linewidth=2)
        ax2.set_xlim(0, len(states)-1)
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
            im.set_array(states[frame, display_indices].reshape(-1, 1))
            
            # Update time series
            line.set_data(range(frame+1), mean_activity[:frame+1])
            
            # Update time indicator
            time_line.set_xdata([frame, frame])
            
            # Update title with time info
            ax1.set_title(f'State Vector (t={frame})')
            
            return [im, line, time_line]
        
        # Create animation
        anim = FuncAnimation(fig, animate, frames=len(states), interval=interval, 
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
        
    def _print_dynamics_statistics(self, states: np.ndarray, inputs: Optional[np.ndarray], 
                                 outputs: Optional[np.ndarray]):
        """
        📊 Print Comprehensive Dynamics Statistics
        
        Provides detailed statistical analysis of temporal behavior
        including memory capacity and dynamic range analysis.
        """
        print("\n" + "="*70)
        print("🌊 RESERVOIR DYNAMICS ANALYSIS")
        print("="*70)
        
        # Basic dynamics information
        T, N = states.shape
        print(f"⏱️  Time Steps: {T}")
        print(f"🧠 Reservoir Size: {N}")
        print(f"📊 State Matrix Size: {T}×{N}")
        
        # Activity statistics
        mean_activity = np.mean(states, axis=0)
        std_activity = np.std(states, axis=0)
        max_activity = np.max(np.abs(states))
        
        print(f"\n🎯 ACTIVITY ANALYSIS:")
        print(f"   • Mean Activity Range: [{mean_activity.min():.4f}, {mean_activity.max():.4f}]")
        print(f"   • Activity Std Range: [{std_activity.min():.4f}, {std_activity.max():.4f}]")
        print(f"   • Maximum |Activity|: {max_activity:.4f}")
        print(f"   • Active Neurons: {np.sum(std_activity > 0.001)}/{N} ({np.sum(std_activity > 0.001)/N:.1%})")
        
        # Temporal characteristics
        print(f"\n⏰ TEMPORAL CHARACTERISTICS:")
        print(f"   • Mean State Norm: {np.mean(np.linalg.norm(states, axis=1)):.4f}")
        print(f"   • State Norm Std: {np.std(np.linalg.norm(states, axis=1)):.4f}")
        
        # Memory capacity estimation (simplified)
        if T > 10:
            memory_capacity = self._estimate_memory_capacity(states)
            print(f"   • Estimated Memory Capacity: {memory_capacity:.2f}")
        
        # Input-output relationships
        if inputs is not None:
            print(f"\n🔄 INPUT-OUTPUT RELATIONSHIPS:")
            print(f"   • Input Dimensions: {inputs.shape[1] if inputs.ndim > 1 else 1}")
            
            # Cross-correlation analysis
            if inputs.ndim > 1:
                input_state_corr = np.mean([np.corrcoef(inputs[:, i], np.mean(states, axis=1))[0,1] 
                                           for i in range(inputs.shape[1]) if not np.isnan(np.corrcoef(inputs[:, i], np.mean(states, axis=1))[0,1])])
            else:
                input_state_corr = np.corrcoef(inputs, np.mean(states, axis=1))[0,1]
            
            if not np.isnan(input_state_corr):
                print(f"   • Mean Input-State Correlation: {input_state_corr:.4f}")
        
        if outputs is not None:
            print(f"   • Output Dimensions: {outputs.shape[1] if outputs.ndim > 1 else 1}")
        
        print("="*70)
        
    def _estimate_memory_capacity(self, states: np.ndarray) -> float:
        """
        🧠 Estimate Memory Capacity of Reservoir
        
        Simplified estimation based on linear memory capacity measure.
        """
        # Simple approximation based on state autocorrelation decay
        mean_state = np.mean(states, axis=1)
        autocorr = np.correlate(mean_state, mean_state, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]
        
        # Find decay to 1/e
        decay_threshold = 1/np.e
        decay_indices = np.where(autocorr < decay_threshold)[0]
        
        if len(decay_indices) > 0:
            memory_capacity = decay_indices[0]
        else:
            memory_capacity = len(autocorr) - 1
            
        return float(memory_capacity)

# Export the main class
__all__ = ['VizDynamicsTemporalMixin']