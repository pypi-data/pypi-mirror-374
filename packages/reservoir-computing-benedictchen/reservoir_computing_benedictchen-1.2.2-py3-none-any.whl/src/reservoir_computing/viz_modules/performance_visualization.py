"""
📊 Performance Visualization - Model Quality and Error Analysis
===============================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides visualization tools for analyzing the performance
of reservoir computing models, including prediction quality, error analysis,
and statistical validation.

Based on: Jaeger, H. (2007) "Echo state network" and
Lukoševičius, M. (2012) "A practical guide to applying echo state networks"
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pandas as pd
from typing import Optional, Tuple, Dict, Any, List
import warnings
import logging

# Configure logging
logger = logging.getLogger(__name__)


def visualize_performance_analysis(predictions: np.ndarray, 
                                  targets: np.ndarray,
                                  inputs: Optional[np.ndarray] = None, 
                                  figsize: Tuple[int, int] = (15, 10),
                                  save_path: Optional[str] = None) -> None:
    """
    Comprehensive performance analysis visualization.
    
    🔬 **Research Background:**
    Performance visualization methods based on regression analysis, time series
    evaluation, and statistical validation techniques for reservoir computing.
    
    **Key Visualizations:**
    1. **Prediction vs Target**: Scatter plot with perfect prediction line and R²
    2. **Time Series Comparison**: Temporal alignment of predictions and targets
    3. **Error Distribution**: Statistical analysis of prediction errors
    4. **Error Evolution**: Temporal analysis of error patterns
    5. **Residual Autocorrelation**: Detection of systematic prediction biases
    6. **Error by Magnitude**: Performance analysis across prediction ranges
    
    Args:
        predictions: Model predictions
        targets: True target values
        inputs: Input sequence [optional]
        figsize: Figure size for the visualization
        save_path: Optional path to save the visualization
        
    References:
        - Jaeger, H. (2007). "Echo state network"
        - Lukoševičius, M. (2012). "A practical guide to applying echo state networks"
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
        pred_plot = predictions[:, 0]
        target_plot = targets[:, 0]
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
    ax1.set_title(f'Prediction Quality\nR² = {r2:.4f}')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add statistics box
    stats_text = f'MSE: {mse:.6f}\nMAE: {mae:.6f}\nR²: {r2:.4f}'
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
    ax2.set_title(f'Time Series Comparison\n(Showing {display_length} points)')
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
                label=f'Normal fit\n(μ={mu:.4f}, σ={sigma:.4f})')
        
        # Add zero line
        ax3.axvline(x=0, color='green', linestyle='--', linewidth=2, label='Zero Error')
        
        ax3.set_xlabel('Prediction Error')
        ax3.set_ylabel('Density')
        ax3.set_title('Error Distribution')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'Insufficient data\nfor error distribution', 
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
            ax5.text(0.5, 0.5, 'Autocorrelation\ncomputation failed', 
                    ha='center', va='center', transform=ax5.transAxes)
            ax5.set_title('Residual Autocorrelation')
    else:
        ax5.text(0.5, 0.5, 'Insufficient data\nfor autocorrelation', 
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
            ax6.text(0.5, 0.5, 'Magnitude analysis\nfailed', 
                    ha='center', va='center', transform=ax6.transAxes)
            ax6.set_title('Error vs Prediction Magnitude')
    else:
        ax6.text(0.5, 0.5, 'Insufficient data\nfor magnitude analysis', 
                ha='center', va='center', transform=ax6.transAxes)
        ax6.set_title('Error vs Prediction Magnitude')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    plt.show()
    
    # Print comprehensive performance statistics
    print_performance_statistics(predictions, targets, errors)


def print_performance_statistics(predictions: np.ndarray, 
                                targets: np.ndarray,
                                errors: np.ndarray) -> None:
    """
    Print comprehensive performance statistics
    
    Args:
        predictions: Model predictions
        targets: True target values
        errors: Prediction errors (predictions - targets)
    """
    print("\n" + "="*60)
    print("📊 PERFORMANCE ANALYSIS STATISTICS")
    print("="*60)
    
    # Basic performance metrics
    mse = np.mean(errors**2)
    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(mse)
    
    # Handle multi-dimensional outputs
    if predictions.ndim > 1 and predictions.shape[1] > 1:
        pred_flat = predictions[:, 0]  # Use first dimension for primary stats
        target_flat = targets[:, 0]
        print(f"\n📏 BASIC METRICS (First dimension):")
    else:
        pred_flat = predictions.flatten()
        target_flat = targets.flatten()
        print(f"\n📏 BASIC METRICS:")
    
    print(f"   Mean Squared Error (MSE): {mse:.6f}")
    print(f"   Root Mean Squared Error (RMSE): {rmse:.6f}")
    print(f"   Mean Absolute Error (MAE): {mae:.6f}")
    
    # R-squared calculation
    if len(target_flat) > 1:
        ss_res = np.sum((target_flat - pred_flat)**2)
        ss_tot = np.sum((target_flat - np.mean(target_flat))**2)
        r2 = 1 - (ss_res / (ss_tot + 1e-8))
        print(f"   R-squared (R²): {r2:.6f}")
    
    # Error statistics
    error_flat = errors.flatten()
    print(f"\n📉 ERROR ANALYSIS:")
    print(f"   Error mean: {error_flat.mean():.6f}")
    print(f"   Error std: {error_flat.std():.6f}")
    print(f"   Error range: [{error_flat.min():.6f}, {error_flat.max():.6f}]")
    print(f"   Error skewness: {stats.skew(error_flat):.4f}")
    print(f"   Error kurtosis: {stats.kurtosis(error_flat):.4f}")
    
    # Bias analysis
    bias = np.mean(error_flat)
    if abs(bias) < 0.01 * mae:
        bias_assessment = "🟢 Low bias (good)"
    elif abs(bias) < 0.05 * mae:
        bias_assessment = "🟡 Moderate bias"
    else:
        bias_assessment = "🔴 High bias (concerning)"
    print(f"   Bias assessment: {bias_assessment}")
    
    # Prediction range analysis
    print(f"\n🎯 PREDICTION ANALYSIS:")
    print(f"   Target range: [{target_flat.min():.6f}, {target_flat.max():.6f}]")
    print(f"   Prediction range: [{pred_flat.min():.6f}, {pred_flat.max():.6f}]")
    print(f"   Target mean: {target_flat.mean():.6f}")
    print(f"   Prediction mean: {pred_flat.mean():.6f}")
    
    # Performance quality assessment
    if len(target_flat) > 1:
        target_std = target_flat.std()
        normalized_rmse = rmse / (target_std + 1e-8)
        
        if normalized_rmse < 0.1:
            quality = "🟢 Excellent"
        elif normalized_rmse < 0.3:
            quality = "🟡 Good"
        elif normalized_rmse < 0.5:
            quality = "🟠 Fair"
        else:
            quality = "🔴 Poor"
        
        print(f"\n🏆 OVERALL ASSESSMENT:")
        print(f"   Normalized RMSE: {normalized_rmse:.4f}")
        print(f"   Performance quality: {quality}")
    
    # Multi-dimensional analysis if applicable
    if predictions.ndim > 1 and predictions.shape[1] > 1:
        print(f"\n📊 MULTI-DIMENSIONAL ANALYSIS:")
        print(f"   Output dimensions: {predictions.shape[1]}")
        
        for i in range(min(3, predictions.shape[1])):  # Show up to 3 dimensions
            dim_mse = np.mean((predictions[:, i] - targets[:, i])**2)
            dim_mae = np.mean(np.abs(predictions[:, i] - targets[:, i]))
            print(f"   Dimension {i+1} - MSE: {dim_mse:.6f}, MAE: {dim_mae:.6f}")
    
    print("="*60)