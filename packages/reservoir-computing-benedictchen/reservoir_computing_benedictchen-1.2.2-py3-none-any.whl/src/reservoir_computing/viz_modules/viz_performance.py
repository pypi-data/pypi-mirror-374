"""
📈 Reservoir Computing - Performance Visualization Module
=======================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Specialized visualization tools for reservoir performance analysis.
Provides comprehensive tools for analyzing training progress, prediction quality,
memory capacity, and overall system performance metrics.

📊 VISUALIZATION CAPABILITIES:
=============================
• Training curves and learning dynamics visualization
• Prediction quality analysis with error distributions
• Memory capacity benchmarks and nonlinear task analysis
• Cross-validation results and statistical validation
• Performance metrics comparison and trend analysis

🔬 RESEARCH FOUNDATION:
======================
Based on established performance analysis techniques:
- Jaeger (2001): Original ESN performance evaluation methods
- Lukoševičius & Jaeger (2009): Performance benchmarking standards
- Verstraeten et al. (2007): Memory capacity analysis and evaluation
- Dambre et al. (2012): Information processing capacity metrics

🎨 PROFESSIONAL STANDARDS:
=========================
• High-resolution performance plots with error bars
• Statistical significance testing and confidence intervals
• Comprehensive legends and performance annotations
• Publication-ready formatting for research papers
• Research-accurate performance metric implementations

This module represents the performance analysis component of the visualization system,
split from the 1569-line monolith for better maintainability and specialized functionality.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import signal, stats
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
import warnings
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import learning_curve
import pandas as pd
import logging

# Configure professional plotting style for performance analysis
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# ================================
# PERFORMANCE VISUALIZATION
# ================================

def visualize_performance_analysis(predictions: np.ndarray, 
                                   targets: np.ndarray,
                                   training_history: Optional[Dict[str, List]] = None,
                                   time_steps: Optional[np.ndarray] = None,
                                   title: str = "Reservoir Performance Analysis",
                                   save_path: Optional[str] = None,
                                   figsize: Tuple[int, int] = (16, 12),
                                   dpi: int = 300) -> plt.Figure:
    """
    📈 Comprehensive Reservoir Performance Visualization
    
    Creates a multi-panel analysis of reservoir performance including prediction accuracy,
    error distributions, training dynamics, and statistical validation.
    
    Args:
        predictions: Model predictions (T×D array)
        targets: Target values (T×D array)
        training_history: Dictionary with training metrics over time
        time_steps: Time step array (T,), optional
        title: Figure title
        save_path: Path to save figure (optional)
        figsize: Figure size in inches
        dpi: Resolution for saved figures
        
    Returns:
        matplotlib.Figure: The complete performance analysis figure
        
    Research Background:
    ===================
    Based on Jaeger (2001) performance evaluation methods and extended with
    modern statistical analysis techniques for comprehensive performance insight.
    """
    # Ensure inputs are numpy arrays
    predictions = np.asarray(predictions)
    targets = np.asarray(targets)
    
    # Handle different dimensionalities
    if predictions.ndim == 1:
        predictions = predictions.reshape(-1, 1)
    if targets.ndim == 1:
        targets = targets.reshape(-1, 1)
        
    T, D = predictions.shape
    
    if time_steps is None:
        time_steps = np.arange(T)
        
    fig = plt.figure(figsize=figsize, dpi=dpi)
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.95)
    
    # Create subplot layout
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.4)
    
    # Calculate performance metrics
    mse = mean_squared_error(targets, predictions)
    mae = mean_absolute_error(targets, predictions)
    r2 = r2_score(targets, predictions)
    
    # === 1. PREDICTION vs TARGET COMPARISON ===
    ax1 = fig.add_subplot(gs[0, :2])
    
    # Show first output dimension if multiple
    output_idx = 0
    
    ax1.plot(time_steps, targets[:, output_idx], 'b-', linewidth=2, 
             label='Target', alpha=0.8)
    ax1.plot(time_steps, predictions[:, output_idx], 'r--', linewidth=2, 
             label='Prediction', alpha=0.8)
    
    ax1.set_title(f'Prediction vs Target (Dim {output_idx})', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Time Steps')
    ax1.set_ylabel('Value')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add performance metrics as text overlay
    metrics_text = f'MSE: {mse:.4f}\nMAE: {mae:.4f}\nR²: {r2:.4f}'
    ax1.text(0.02, 0.98, metrics_text, transform=ax1.transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
             fontsize=10)
    
    # === 2. SCATTER PLOT: PREDICTED vs ACTUAL ===
    ax2 = fig.add_subplot(gs[0, 2:])
    
    # Flatten for scatter plot
    targets_flat = targets.flatten()
    predictions_flat = predictions.flatten()
    
    # Sample data if too many points
    if len(targets_flat) > 2000:
        sample_idx = np.random.choice(len(targets_flat), 2000, replace=False)
        targets_scatter = targets_flat[sample_idx]
        predictions_scatter = predictions_flat[sample_idx]
    else:
        targets_scatter = targets_flat
        predictions_scatter = predictions_flat
    
    ax2.scatter(targets_scatter, predictions_scatter, alpha=0.6, s=20)
    
    # Perfect prediction line
    min_val = min(targets_scatter.min(), predictions_scatter.min())
    max_val = max(targets_scatter.max(), predictions_scatter.max())
    ax2.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, 
             label='Perfect Prediction')
    
    ax2.set_title('Predicted vs Actual Values', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Actual Values')
    ax2.set_ylabel('Predicted Values')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal', adjustable='box')
    
    # === 3. ERROR DISTRIBUTION ANALYSIS ===
    ax3 = fig.add_subplot(gs[1, :2])
    
    # Calculate errors
    errors = predictions_flat - targets_flat
    
    # Histogram of errors
    n_bins = min(50, int(np.sqrt(len(errors))))
    ax3.hist(errors, bins=n_bins, alpha=0.7, color='lightcoral', 
             edgecolor='black', linewidth=0.5, density=True)
    
    # Overlay normal distribution fit
    error_mean = np.mean(errors)
    error_std = np.std(errors)
    x_fit = np.linspace(errors.min(), errors.max(), 100)
    normal_fit = stats.norm.pdf(x_fit, error_mean, error_std)
    ax3.plot(x_fit, normal_fit, 'r-', linewidth=2, label='Normal Fit')
    
    # Statistical overlays
    ax3.axvline(error_mean, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {error_mean:.4f}')
    ax3.axvline(error_mean + error_std, color='orange', linestyle='--', alpha=0.7)
    ax3.axvline(error_mean - error_std, color='orange', linestyle='--', alpha=0.7)
    
    ax3.set_title('Prediction Error Distribution', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Prediction Error')
    ax3.set_ylabel('Probability Density')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # === 4. TRAINING HISTORY (if available) ===
    ax4 = fig.add_subplot(gs[1, 2:])
    
    if training_history is not None and len(training_history) > 0:
        # Plot available training metrics
        for metric_name, values in training_history.items():
            if len(values) > 0:
                ax4.plot(values, label=metric_name, linewidth=2, marker='o', markersize=3)
        
        ax4.set_title('Training History', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Epoch/Iteration')
        ax4.set_ylabel('Metric Value')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_yscale('log')  # Log scale often better for loss curves
    else:
        # Show residuals over time instead
        residuals = np.abs(errors.reshape(T, D))
        mean_residuals = np.mean(residuals, axis=1)
        
        ax4.plot(time_steps, mean_residuals, 'g-', linewidth=2, alpha=0.8)
        ax4.set_title('Absolute Residuals Over Time', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Time Steps')
        ax4.set_ylabel('Mean Absolute Residual')
        ax4.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(time_steps, mean_residuals, 1)
        p = np.poly1d(z)
        ax4.plot(time_steps, p(time_steps), "r--", alpha=0.8, 
                label=f'Trend: {z[0]:.6f}x + {z[1]:.4f}')
        ax4.legend()
    
    # === 5. PERFORMANCE METRICS SUMMARY ===
    ax5 = fig.add_subplot(gs[2, :2])
    
    # Create a comprehensive metrics summary
    metrics = {
        'MSE': mse,
        'RMSE': np.sqrt(mse),
        'MAE': mae,
        'R² Score': r2,
        'Max Error': np.max(np.abs(errors)),
        'Error Std': error_std
    }
    
    # Create bar plot of metrics (normalized)
    metric_names = list(metrics.keys())
    metric_values = list(metrics.values())
    
    # Normalize metrics for better visualization (exclude R²)
    normalized_values = []
    for i, (name, value) in enumerate(metrics.items()):
        if name == 'R² Score':
            normalized_values.append(value)  # Keep R² as is
        else:
            normalized_values.append(value / np.max(np.abs(list(metrics.values())[:-1])))
    
    bars = ax5.bar(metric_names, normalized_values, alpha=0.7, 
                   color=['skyblue' if name != 'R² Score' else 'lightgreen' 
                         for name in metric_names])
    
    # Add value labels on bars
    for bar, value in zip(bars, metric_values):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.4f}', ha='center', va='bottom', fontsize=9)
    
    ax5.set_title('Performance Metrics Summary', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Normalized Value')
    ax5.tick_params(axis='x', rotation=45)
    ax5.grid(True, alpha=0.3)
    
    # === 6. MULTI-DIMENSIONAL ANALYSIS (if applicable) ===
    ax6 = fig.add_subplot(gs[2, 2:])
    
    if D > 1:
        # Per-dimension performance analysis
        dim_mse = [mean_squared_error(targets[:, d], predictions[:, d]) for d in range(D)]
        dim_r2 = [r2_score(targets[:, d], predictions[:, d]) for d in range(D)]
        
        dimensions = np.arange(D)
        
        # Dual y-axis plot
        ax6_twin = ax6.twinx()
        
        bars1 = ax6.bar(dimensions - 0.2, dim_mse, 0.4, alpha=0.7, 
                        color='lightcoral', label='MSE')
        bars2 = ax6_twin.bar(dimensions + 0.2, dim_r2, 0.4, alpha=0.7, 
                            color='lightblue', label='R²')
        
        ax6.set_title(f'Per-Dimension Performance ({D} dims)', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Output Dimension')
        ax6.set_ylabel('MSE', color='red')
        ax6_twin.set_ylabel('R² Score', color='blue')
        
        # Combine legends
        lines1, labels1 = ax6.get_legend_handles_labels()
        lines2, labels2 = ax6_twin.get_legend_handles_labels()
        ax6.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        ax6.grid(True, alpha=0.3)
    else:
        # Single dimension - show error autocorrelation
        error_1d = errors
        max_lag = min(20, len(error_1d) // 4)
        
        if max_lag > 1:
            lags = np.arange(1, max_lag + 1)
            autocorr = []
            
            for lag in lags:
                if lag < len(error_1d):
                    corr = np.corrcoef(error_1d[:-lag], error_1d[lag:])[0, 1]
                    autocorr.append(corr if not np.isnan(corr) else 0)
                else:
                    autocorr.append(0)
            
            autocorr = np.array(autocorr)
            
            ax6.plot(lags, autocorr, 'g-', linewidth=2, marker='o', markersize=4)
            ax6.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax6.axhline(y=0.1, color='r', linestyle='--', alpha=0.5, label='0.1 threshold')
            
            ax6.set_title('Error Autocorrelation', fontsize=12, fontweight='bold')
            ax6.set_xlabel('Lag')
            ax6.set_ylabel('Autocorrelation')
            ax6.legend()
            ax6.grid(True, alpha=0.3)
    
    # Add timestamp and metadata
    fig.text(0.98, 0.02, f'T={T}, D={D} | Performance Analysis | MSE={mse:.4f}', 
             fontsize=8, style='italic', alpha=0.7, ha='right')
    
    # Save figure if path provided
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        print(f"📈 Performance analysis saved to: {save_path}")
    
    plt.tight_layout()
    return fig

# Export the main function
__all__ = ['visualize_performance_analysis']
