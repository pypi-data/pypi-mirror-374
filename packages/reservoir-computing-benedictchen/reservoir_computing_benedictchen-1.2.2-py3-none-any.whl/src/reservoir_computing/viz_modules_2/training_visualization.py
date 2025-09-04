"""
📈 Training Visualization - Progress and Performance Analysis
=========================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides visualization tools for training progress, performance metrics,
and convergence analysis in Echo State Networks.

Based on training visualization methods from:
- Lukoševičius, M. & Jaeger, H. (2009) "Reservoir computing survey"
- Jaeger, H. (2007) "Echo state network training methods"
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pandas as pd
from typing import Optional, Tuple, Dict, Any, List, Union
import warnings
import logging

# Configure logging
logger = logging.getLogger(__name__)


def visualize_training_progress(train_errors: List[float], 
                              val_errors: Optional[List[float]] = None, 
                              metrics: Optional[Dict[str, List[float]]] = None,
                              figsize: Tuple[int, int] = (15, 6),
                              save_path: Optional[str] = None) -> None:
    """
    Visualize training progress and performance metrics
    
    Args:
        train_errors: Training errors over epochs
        val_errors: Validation errors over epochs [optional]  
        metrics: Dictionary of additional metrics to plot [optional]
        figsize: Figure size for the visualization
        save_path: Optional path to save the visualization
    """
    
    n_plots = 2 + (1 if metrics else 0)
    fig, axes = plt.subplots(1, n_plots, figsize=figsize)
    if n_plots == 1:
        axes = [axes]
    elif n_plots == 2:
        axes = list(axes)
        
    fig.suptitle('Training Progress and Performance Analysis', fontsize=14, fontweight='bold')
    
    # 1. Error curves
    ax1 = axes[0]
    epochs = np.arange(1, len(train_errors) + 1)
    
    ax1.semilogy(epochs, train_errors, 'b-', linewidth=2, label='Training Error', marker='o', markersize=4)
    
    if val_errors is not None and len(val_errors) == len(train_errors):
        ax1.semilogy(epochs, val_errors, 'r-', linewidth=2, label='Validation Error', marker='s', markersize=4)
        
        # Find best epoch
        best_epoch = np.argmin(val_errors) + 1
        ax1.axvline(x=best_epoch, color='green', linestyle='--', alpha=0.7, 
                   label=f'Best Epoch: {best_epoch}')
        
        # Add text annotation for best performance
        ax1.text(0.7, 0.95, f'Best Val Error: {min(val_errors):.6f}\\nAt Epoch: {best_epoch}', 
                transform=ax1.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7),
                verticalalignment='top')
    
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Error (log scale)')
    ax1.set_title('Training Error Curves')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Learning rate analysis
    ax2 = axes[1]
    if len(train_errors) > 1:
        # Calculate improvement rate
        improvements = []
        for i in range(1, len(train_errors)):
            improvement = (train_errors[i-1] - train_errors[i]) / train_errors[i-1]
            improvements.append(improvement * 100)  # Convert to percentage
        
        ax2.plot(epochs[1:], improvements, 'g-', linewidth=2, marker='o', markersize=4)
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Improvement (%)')
        ax2.set_title('Learning Rate Analysis')
        ax2.grid(True, alpha=0.3)
        
        # Add statistics
        mean_improvement = np.mean(improvements)
        ax2.text(0.02, 0.98, f'Mean Improvement: {mean_improvement:.2f}%', 
                transform=ax2.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top')
    else:
        ax2.text(0.5, 0.5, 'Insufficient data\\nfor learning rate analysis', 
                ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Learning Rate Analysis')
    
    # 3. Additional metrics (if provided)
    if metrics and len(axes) > 2:
        ax3 = axes[2]
        
        for metric_name, metric_values in metrics.items():
            if len(metric_values) == len(train_errors):
                ax3.plot(epochs, metric_values, linewidth=2, label=metric_name, marker='o', markersize=3)
        
        ax3.set_xlabel('Epoch')
        ax3.set_ylabel('Metric Value')
        ax3.set_title('Additional Performance Metrics')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    plt.show()


def visualize_performance_analysis_detailed(predictions: np.ndarray, 
                                          targets: np.ndarray,
                                          inputs: Optional[np.ndarray] = None, 
                                          figsize: Tuple[int, int] = (15, 10),
                                          save_path: Optional[str] = None) -> None:
    """
    Comprehensive performance analysis visualization
    
    Args:
        predictions: Model predictions
        targets: True target values  
        inputs: Input sequence [optional]
        figsize: Figure size for the visualization
        save_path: Optional path to save the visualization
    """
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle('Performance Analysis and Prediction Quality', fontsize=16, fontweight='bold')
    
    # Calculate errors
    errors = predictions - targets
    mse = np.mean(errors**2)
    mae = np.mean(np.abs(errors))
    
    # 1. Prediction vs Target scatter plot
    ax1 = axes[0, 0]
    
    # Handle multi-dimensional outputs
    if predictions.ndim > 1 and predictions.shape[1] > 1:
        # For multi-output, plot first dimension or flattened
        pred_plot = predictions[:, 0] if predictions.shape[1] > 1 else predictions.flatten()
        target_plot = targets[:, 0] if targets.shape[1] > 1 else targets.flatten()
    else:
        pred_plot = predictions.flatten()
        target_plot = targets.flatten()
    
    ax1.scatter(target_plot, pred_plot, alpha=0.6, s=20)
    
    # Perfect prediction line
    min_val, max_val = min(target_plot.min(), pred_plot.min()), max(target_plot.max(), pred_plot.max())
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
    
    # Calculate R²
    if len(target_plot) > 1:
        ss_res = np.sum((target_plot - pred_plot)**2)
        ss_tot = np.sum((target_plot - np.mean(target_plot))**2)
        r2 = 1 - (ss_res / (ss_tot + 1e-8))
    else:
        r2 = 0.0
    
    ax1.set_xlabel('True Values')
    ax1.set_ylabel('Predictions')
    ax1.set_title(f'Prediction Quality\\nR² = {r2:.4f}')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add statistics box
    stats_text = f'MSE: {mse:.6f}\\nMAE: {mae:.6f}\\nR²: {r2:.4f}'
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
            verticalalignment='top', fontsize=9)
    
    # 2. Time series comparison
    ax2 = axes[0, 1]
    
    # Show a subset for clarity
    display_length = min(200, len(predictions))
    indices = np.linspace(0, len(predictions)-1, display_length).astype(int)
    
    ax2.plot(indices, target_plot[indices], 'b-', linewidth=2, label='True', alpha=0.8)
    ax2.plot(indices, pred_plot[indices], 'r--', linewidth=2, label='Predicted', alpha=0.8)
    ax2.fill_between(indices, target_plot[indices], pred_plot[indices], alpha=0.3, color='gray')
    
    ax2.set_xlabel('Time Step')
    ax2.set_ylabel('Value')
    ax2.set_title(f'Time Series Comparison\\n(Showing {display_length} points)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Error distribution analysis
    ax3 = axes[0, 2]
    
    error_flat = errors.flatten()
    
    if len(error_flat) > 1:
        # Histogram with statistical overlays
        n, bins, patches = ax3.hist(error_flat, bins=50, alpha=0.7, density=True, edgecolor='black')
        
        # Fit normal distribution
        mu, sigma = stats.norm.fit(error_flat)
        x = np.linspace(error_flat.min(), error_flat.max(), 100)
        ax3.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                label=f'Normal fit\\n(μ={mu:.4f}, σ={sigma:.4f})')
        
        # Add zero line
        ax3.axvline(x=0, color='green', linestyle='--', linewidth=2, label='Zero Error')
        
        ax3.set_xlabel('Prediction Error')
        ax3.set_ylabel('Density')
        ax3.set_title('Error Distribution')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'Insufficient data\\nfor error distribution', 
                ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Error Distribution')
    
    # 4. Error evolution over time
    ax4 = axes[1, 0]
    
    # Calculate rolling statistics
    if len(error_flat) > 10:
        window_size = max(1, len(error_flat) // 50)
        rolling_mse = pd.Series(error_flat**2).rolling(window=window_size).mean()
        rolling_mae = pd.Series(np.abs(error_flat)).rolling(window=window_size).mean()
        
        ax4.plot(rolling_mse, label=f'Rolling MSE (window={window_size})', linewidth=2)
        ax4.plot(rolling_mae, label=f'Rolling MAE (window={window_size})', linewidth=2)
    else:
        ax4.plot(error_flat**2, label='Squared Error', linewidth=1, alpha=0.7)
        ax4.plot(np.abs(error_flat), label='Absolute Error', linewidth=1, alpha=0.7)
    
    ax4.set_xlabel('Time Step')
    ax4.set_ylabel('Error')
    ax4.set_title('Error Evolution')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Residuals autocorrelation
    ax5 = axes[1, 1]
    
    # Autocorrelation of residuals
    max_lag = min(50, len(error_flat) // 4)
    if max_lag > 1 and len(error_flat) > max_lag:
        try:
            autocorr = np.correlate(error_flat, error_flat, mode='full')
            autocorr = autocorr[len(autocorr)//2:][:max_lag]
            if autocorr[0] != 0:
                autocorr = autocorr / autocorr[0]  # Normalize
            
            lags = np.arange(len(autocorr))
            ax5.plot(lags, autocorr, 'b-', linewidth=2, marker='o', markersize=4)
            ax5.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            
            # Add confidence bands (approximate)
            n_samples = len(error_flat)
            conf_interval = 1.96 / np.sqrt(n_samples)
            ax5.axhline(y=conf_interval, color='r', linestyle=':', alpha=0.7, label='95% Confidence')
            ax5.axhline(y=-conf_interval, color='r', linestyle=':', alpha=0.7)
            
            ax5.set_xlabel('Lag')
            ax5.set_ylabel('Autocorrelation')
            ax5.set_title('Residual Autocorrelation')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
        except Exception as e:
            logger.warning(f"Autocorrelation computation failed: {e}")
            ax5.text(0.5, 0.5, 'Autocorrelation\\ncomputation failed', 
                    ha='center', va='center', transform=ax5.transAxes)
            ax5.set_title('Residual Autocorrelation')
    else:
        ax5.text(0.5, 0.5, 'Insufficient data\\nfor autocorrelation', 
                ha='center', va='center', transform=ax5.transAxes)
        ax5.set_title('Residual Autocorrelation')
    
    # 6. Performance by prediction magnitude
    ax6 = axes[1, 2]
    
    # Bin predictions by magnitude and show average error
    if len(pred_plot) > 20:  # Ensure sufficient data
        try:
            n_bins = 10
            bin_edges = np.linspace(pred_plot.min(), pred_plot.max(), n_bins + 1)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            bin_errors = []
            bin_counts = []
            
            for i in range(n_bins):
                mask = (pred_plot >= bin_edges[i]) & (pred_plot < bin_edges[i + 1])
                if i == n_bins - 1:  # Include right edge for last bin
                    mask = (pred_plot >= bin_edges[i]) & (pred_plot <= bin_edges[i + 1])
                
                if np.sum(mask) > 0:
                    bin_errors.append(np.mean(np.abs(error_flat[mask])))
                    bin_counts.append(np.sum(mask))
                else:
                    bin_errors.append(0)
                    bin_counts.append(0)
            
            # Bar plot
            ax6.bar(bin_centers, bin_errors, width=np.diff(bin_edges)[0]*0.8, 
                   alpha=0.7, edgecolor='black')
            
            ax6.set_xlabel('Prediction Magnitude')
            ax6.set_ylabel('Mean Absolute Error')
            ax6.set_title('Error vs Prediction Magnitude')
            ax6.grid(True, alpha=0.3)
            
            # Add sample count as text
            for i, (center, count) in enumerate(zip(bin_centers, bin_counts)):
                if count > 0:
                    ax6.text(center, bin_errors[i], str(count), 
                           ha='center', va='bottom', fontsize=8)
        except Exception as e:
            logger.warning(f"Magnitude analysis failed: {e}")
            ax6.text(0.5, 0.5, 'Magnitude analysis\\nfailed', 
                    ha='center', va='center', transform=ax6.transAxes)
            ax6.set_title('Error vs Prediction Magnitude')
    else:
        ax6.text(0.5, 0.5, 'Insufficient data\\nfor magnitude analysis', 
                ha='center', va='center', transform=ax6.transAxes)
        ax6.set_title('Error vs Prediction Magnitude')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    plt.show()


def print_training_statistics(train_errors: List[float],
                            val_errors: Optional[List[float]] = None,
                            metrics: Optional[Dict[str, List[float]]] = None) -> None:
    """
    Print comprehensive training statistics
    
    Args:
        train_errors: Training errors over epochs
        val_errors: Validation errors [optional]
        metrics: Additional metrics [optional]
    """
    print("\\n" + "="*60)
    print("📈 TRAINING PROGRESS STATISTICS")
    print("="*60)
    
    n_epochs = len(train_errors)
    
    # Basic training info
    print(f"\\n📊 TRAINING OVERVIEW:")
    print(f"   Total epochs: {n_epochs}")
    print(f"   Initial training error: {train_errors[0]:.6f}")
    print(f"   Final training error: {train_errors[-1]:.6f}")
    
    if n_epochs > 1:
        improvement = (train_errors[0] - train_errors[-1]) / train_errors[0] * 100
        print(f"   Overall improvement: {improvement:.2f}%")
    
    # Convergence analysis
    if n_epochs > 10:
        print(f"\\n🎯 CONVERGENCE ANALYSIS:")
        
        # Check if converged (last 10% of epochs show <1% change)
        convergence_window = max(2, n_epochs // 10)
        recent_errors = train_errors[-convergence_window:]
        if len(recent_errors) > 1:
            recent_change = abs(recent_errors[-1] - recent_errors[0]) / recent_errors[0] * 100
            converged = recent_change < 1.0
            
            print(f"   Convergence status: {'Converged' if converged else 'Still improving'}")
            print(f"   Recent change (last {convergence_window} epochs): {recent_change:.3f}%")
        
        # Find best improvement epoch
        improvements = []
        for i in range(1, len(train_errors)):
            improvement = (train_errors[i-1] - train_errors[i]) / train_errors[i-1]
            improvements.append(improvement)
        
        if improvements:
            best_improvement_epoch = np.argmax(improvements) + 2  # +2 for 1-indexing and diff
            print(f"   Best improvement at epoch: {best_improvement_epoch}")
            print(f"   Best improvement: {max(improvements)*100:.2f}%")
    
    # Validation analysis
    if val_errors is not None and len(val_errors) == n_epochs:
        print(f"\\n✅ VALIDATION ANALYSIS:")
        print(f"   Initial validation error: {val_errors[0]:.6f}")
        print(f"   Final validation error: {val_errors[-1]:.6f}")
        
        best_val_epoch = np.argmin(val_errors) + 1
        best_val_error = min(val_errors)
        
        print(f"   Best validation error: {best_val_error:.6f} (epoch {best_val_epoch})")
        
        # Check for overfitting
        if best_val_epoch < n_epochs * 0.8:  # Best epoch in first 80%
            print(f"   ⚠️  Potential overfitting detected (best epoch: {best_val_epoch})")
        else:
            print(f"   ✅ No clear overfitting signs")
        
        # Training vs validation gap
        final_gap = abs(train_errors[-1] - val_errors[-1])
        print(f"   Final train-val gap: {final_gap:.6f}")
    
    # Additional metrics analysis
    if metrics:
        print(f"\\n📈 ADDITIONAL METRICS:")
        for metric_name, metric_values in metrics.items():
            if len(metric_values) == n_epochs:
                initial_val = metric_values[0]
                final_val = metric_values[-1]
                
                print(f"   {metric_name}:")
                print(f"     Initial: {initial_val:.6f}")
                print(f"     Final: {final_val:.6f}")
                print(f"     Change: {final_val - initial_val:.6f}")
    
    print("="*60)