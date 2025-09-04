"""
📈 Reservoir Computing - Performance Metrics Visualization Module
================================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Performance analysis visualization including training progress monitoring,
prediction accuracy analysis, error distribution analysis, and comprehensive
performance metrics visualization for reservoir computing systems.

📊 VISUALIZATION CAPABILITIES:
=============================
• Training progress curves with validation tracking
• Prediction accuracy scatter plots and error analysis
• Error distribution histograms with statistical analysis
• Performance metrics dashboard with multiple metrics
• Learning curve analysis with convergence detection
• Model diagnostic plots for comprehensive evaluation

🔬 RESEARCH FOUNDATION:
======================
Based on performance evaluation techniques from:
- Jaeger (2001): Original ESN performance evaluation methods
- Lukoševičius & Jaeger (2009): Comprehensive performance metrics
- Verstraeten et al. (2007): Evaluation methodologies for reservoir computing
- Performance analysis standards from machine learning literature

This module represents the performance analysis and training monitoring components,
split from the 1438-line monolith for specialized performance visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from typing import Optional, Tuple, Dict, Any, List, Union
import warnings
from abc import ABC

# Configure professional plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class VizPerformanceMetricsMixin(ABC):
    """
    📈 Performance Metrics Visualization Mixin
    
    Provides comprehensive performance analysis and training monitoring
    capabilities for reservoir computing systems.
    """

    def visualize_training_progress(self, train_errors: List[float], val_errors: Optional[List[float]] = None,
                                  metrics: Optional[Dict[str, List[float]]] = None,
                                  figsize: Tuple[int, int] = (12, 8), save_path: Optional[str] = None):
        """
        📈 Comprehensive Training Progress Visualization
        
        Creates detailed visualization of training progress including error curves,
        convergence analysis, and additional performance metrics.
        
        Args:
            train_errors: Training error values over epochs/iterations
            val_errors: Validation error values (optional)
            metrics: Dictionary of additional metrics to plot (optional)
            figsize: Figure size in inches
            save_path: Path to save figure (optional)
            
        Research Background:
        ===================
        Based on machine learning best practices for training monitoring
        and convergence analysis in reservoir computing systems.
        """
        
        fig = plt.figure(figsize=figsize)
        fig.suptitle('Training Progress Analysis', fontsize=16, fontweight='bold')
        
        # Determine subplot layout based on available data
        n_plots = 2 if metrics is None else 4
        if n_plots == 2:
            gs = fig.add_gridspec(1, 2, hspace=0.3, wspace=0.3)
        else:
            gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)
        
        # 1. Training/Validation Error Curves
        ax1 = fig.add_subplot(gs[0, 0])
        epochs = range(1, len(train_errors) + 1)
        
        ax1.semilogy(epochs, train_errors, 'b-', linewidth=2, label='Training Error', alpha=0.8)
        
        if val_errors is not None:
            ax1.semilogy(epochs[:len(val_errors)], val_errors, 'r-', linewidth=2, 
                        label='Validation Error', alpha=0.8)
            
            # Find best validation epoch
            best_epoch = np.argmin(val_errors) + 1
            best_val_error = min(val_errors)
            ax1.axvline(best_epoch, color='green', linestyle='--', alpha=0.7, 
                       label=f'Best Val (Epoch {best_epoch})')
            ax1.plot(best_epoch, best_val_error, 'go', markersize=8, markerfacecolor='lightgreen')
        
        ax1.set_title('Error Convergence')
        ax1.set_xlabel('Epoch/Iteration')
        ax1.set_ylabel('Error (log scale)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add convergence status
        final_train_error = train_errors[-1]
        if len(train_errors) > 10:
            recent_trend = np.mean(np.diff(train_errors[-10:]))
            convergence_status = "Converged" if abs(recent_trend) < final_train_error * 0.01 else "Still Learning"
            color = 'green' if convergence_status == "Converged" else 'orange'
            ax1.text(0.02, 0.98, f'Status: {convergence_status}', transform=ax1.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.3),
                    verticalalignment='top')
        
        # 2. Error Distribution Analysis
        ax2 = fig.add_subplot(gs[0, 1])
        
        # Histogram of training errors
        ax2.hist(train_errors, bins=20, alpha=0.7, color='blue', edgecolor='black', 
                density=True, label='Training Errors')
        
        if val_errors is not None:
            ax2.hist(val_errors, bins=20, alpha=0.7, color='red', edgecolor='black',
                    density=True, label='Validation Errors')
        
        # Add statistical information
        train_mean = np.mean(train_errors)
        train_std = np.std(train_errors)
        ax2.axvline(train_mean, color='darkblue', linestyle='--', linewidth=2,
                   label=f'Train Mean: {train_mean:.4f}')
        
        ax2.set_title('Error Distribution')
        ax2.set_xlabel('Error Value')
        ax2.set_ylabel('Density')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Add statistics box
        stats_text = f'Train μ: {train_mean:.4f}\nTrain σ: {train_std:.4f}'
        if val_errors is not None:
            val_mean = np.mean(val_errors)
            val_std = np.std(val_errors)
            stats_text += f'\nVal μ: {val_mean:.4f}\nVal σ: {val_std:.4f}'
        
        ax2.text(0.98, 0.98, stats_text, transform=ax2.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top', horizontalalignment='right', fontsize=9)
        
        # 3. Additional Metrics (if provided)
        if metrics is not None and n_plots == 4:
            ax3 = fig.add_subplot(gs[1, 0])
            
            colors = ['green', 'orange', 'purple', 'brown', 'pink']
            for i, (metric_name, metric_values) in enumerate(metrics.items()):
                color = colors[i % len(colors)]
                epochs_metric = range(1, len(metric_values) + 1)
                ax3.plot(epochs_metric, metric_values, color=color, linewidth=2, 
                        label=metric_name, alpha=0.8, marker='o', markersize=3)
            
            ax3.set_title('Additional Metrics')
            ax3.set_xlabel('Epoch/Iteration')
            ax3.set_ylabel('Metric Value')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # 4. Learning Rate Analysis
            ax4 = fig.add_subplot(gs[1, 1])
            
            # Compute learning rate as negative gradient of error
            if len(train_errors) > 1:
                learning_rates = -np.diff(train_errors)
                ax4.plot(range(2, len(train_errors) + 1), learning_rates, 'b-', 
                        linewidth=2, alpha=0.7, label='Learning Rate')
                ax4.axhline(0, color='red', linestyle='--', alpha=0.5)
                
                # Smooth learning rate
                if len(learning_rates) > 5:
                    window_size = min(5, len(learning_rates) // 3)
                    smooth_lr = np.convolve(learning_rates, np.ones(window_size)/window_size, mode='valid')
                    ax4.plot(range(2 + window_size//2, len(train_errors) + 1 - window_size//2), 
                            smooth_lr, 'r-', linewidth=2, alpha=0.8, label='Smoothed')
                
                ax4.set_title('Learning Rate (Error Reduction)')
                ax4.set_xlabel('Epoch/Iteration')
                ax4.set_ylabel('Error Reduction')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'Insufficient data\nfor learning rate analysis', 
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Learning Rate Analysis')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📈 Training progress visualization saved to: {save_path}")
            
        plt.show()

    def visualize_performance_analysis(self, predictions: np.ndarray, targets: np.ndarray,
                                     training_history: Optional[Dict[str, List[float]]] = None,
                                     figsize: Tuple[int, int] = (15, 10), save_path: Optional[str] = None):
        """
        📊 Comprehensive Performance Analysis Visualization
        
        Creates detailed analysis of model performance including prediction accuracy,
        error analysis, residual plots, and statistical evaluation.
        
        Args:
            predictions: Model predictions array
            targets: Ground truth target values
            training_history: Optional training history dictionary
            figsize: Figure size in inches
            save_path: Path to save figure (optional)
            
        Research Background:
        ===================
        Based on comprehensive model evaluation practices from machine learning
        and reservoir computing literature for thorough performance assessment.
        """
        
        fig = plt.figure(figsize=figsize)
        fig.suptitle('Comprehensive Performance Analysis', fontsize=16, fontweight='bold')
        
        # Calculate performance metrics
        mse = mean_squared_error(targets, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(targets, predictions)
        r2 = r2_score(targets, predictions)
        
        # Create subplot layout
        gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.4)
        
        # 1. Prediction vs Target Scatter Plot
        ax1 = fig.add_subplot(gs[0, 0])
        
        # Create scatter plot with density coloring if many points
        if len(predictions) > 1000:
            # Use hexbin for large datasets
            hb = ax1.hexbin(targets.flatten(), predictions.flatten(), gridsize=30, cmap='Blues', alpha=0.7)
            plt.colorbar(hb, ax=ax1, shrink=0.8, label='Density')
        else:
            ax1.scatter(targets, predictions, alpha=0.6, s=20, edgecolors='black', linewidth=0.5)
        
        # Perfect prediction line
        min_val = min(np.min(targets), np.min(predictions))
        max_val = max(np.max(targets), np.max(predictions))
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, 
                label='Perfect Prediction', alpha=0.8)
        
        ax1.set_title('Predictions vs Targets')
        ax1.set_xlabel('Target Values')
        ax1.set_ylabel('Predicted Values')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add R² annotation
        ax1.text(0.05, 0.95, f'R² = {r2:.4f}', transform=ax1.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top', fontweight='bold')
        
        # 2. Error Distribution
        ax2 = fig.add_subplot(gs[0, 1])
        
        errors = predictions - targets
        
        # Histogram with statistical overlay
        n, bins, patches = ax2.hist(errors.flatten(), bins=50, alpha=0.7, 
                                   edgecolor='black', density=True, color='skyblue')
        
        # Add normal distribution overlay
        mu, sigma = stats.norm.fit(errors.flatten())
        x = np.linspace(errors.min(), errors.max(), 100)
        ax2.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                label=f'Normal fit (μ={mu:.4f}, σ={sigma:.4f})')
        
        # Add zero error line
        ax2.axvline(0, color='green', linestyle='--', linewidth=2, label='Zero Error')
        ax2.axvline(mu, color='red', linestyle=':', linewidth=2, label=f'Mean Error: {mu:.4f}')
        
        ax2.set_title('Error Distribution')
        ax2.set_xlabel('Error (Prediction - Target)')
        ax2.set_ylabel('Density')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Residual Plot
        ax3 = fig.add_subplot(gs[0, 2])
        
        ax3.scatter(predictions.flatten(), errors.flatten(), alpha=0.6, s=20)
        ax3.axhline(0, color='red', linestyle='--', linewidth=2, alpha=0.8)
        
        # Add trend line
        z = np.polyfit(predictions.flatten(), errors.flatten(), 1)
        p = np.poly1d(z)
        x_trend = np.linspace(predictions.min(), predictions.max(), 100)
        ax3.plot(x_trend, p(x_trend), 'g-', linewidth=2, alpha=0.7, 
                label=f'Trend (slope: {z[0]:.4f})')
        
        ax3.set_title('Residual Analysis')
        ax3.set_xlabel('Predicted Values')
        ax3.set_ylabel('Residuals')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Time Series Comparison (if data is sequential)
        ax4 = fig.add_subplot(gs[1, 0])
        
        # Show sample of time series for comparison
        sample_size = min(200, len(targets))
        indices = np.random.choice(len(targets), sample_size, replace=False)
        indices.sort()
        
        ax4.plot(indices, targets[indices], 'b-', linewidth=2, label='Targets', alpha=0.8)
        ax4.plot(indices, predictions[indices], 'r-', linewidth=2, label='Predictions', alpha=0.8)
        
        ax4.set_title('Time Series Comparison (Sample)')
        ax4.set_xlabel('Sample Index')
        ax4.set_ylabel('Value')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Performance Metrics Summary
        ax5 = fig.add_subplot(gs[1, 1])
        
        # Create performance metrics text
        metrics_text = f"""
PERFORMANCE METRICS:

• Mean Squared Error: {mse:.6f}
• Root Mean Squared Error: {rmse:.6f}  
• Mean Absolute Error: {mae:.6f}
• R² Score: {r2:.6f}

ERROR STATISTICS:
• Mean Error: {np.mean(errors):.6f}
• Error Std: {np.std(errors):.6f}
• Max |Error|: {np.max(np.abs(errors)):.6f}
• Error Skewness: {stats.skew(errors.flatten()):.4f}
• Error Kurtosis: {stats.kurtosis(errors.flatten()):.4f}

PERFORMANCE LEVEL:
{self._assess_performance_level(r2, rmse)}
        """
        
        ax5.text(0.05, 0.95, metrics_text, transform=ax5.transAxes,
                verticalalignment='top', fontsize=10, fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        ax5.set_title('Performance Summary')
        ax5.axis('off')
        
        # 6. Error Evolution (if training history available)
        ax6 = fig.add_subplot(gs[1, 2])
        
        if training_history is not None and 'train_errors' in training_history:
            train_errors = training_history['train_errors']
            epochs = range(1, len(train_errors) + 1)
            ax6.semilogy(epochs, train_errors, 'b-', linewidth=2, label='Training Error')
            
            if 'val_errors' in training_history:
                val_errors = training_history['val_errors']
                ax6.semilogy(epochs[:len(val_errors)], val_errors, 'r-', 
                           linewidth=2, label='Validation Error')
            
            ax6.set_title('Training History')
            ax6.set_xlabel('Epoch')
            ax6.set_ylabel('Error (log scale)')
            ax6.legend()
            ax6.grid(True, alpha=0.3)
        else:
            ax6.text(0.5, 0.5, 'No training history\navailable', 
                    ha='center', va='center', transform=ax6.transAxes)
            ax6.set_title('Training History')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Performance analysis saved to: {save_path}")
            
        plt.show()
        
        # Print performance statistics
        self._print_performance_statistics(predictions, targets, errors)
        
    def _assess_performance_level(self, r2: float, rmse: float) -> str:
        """
        🎯 Assess Performance Level Based on Metrics
        
        Provides qualitative assessment of model performance based on
        standard machine learning evaluation criteria.
        """
        if r2 >= 0.95:
            return "🌟 EXCELLENT (R² ≥ 0.95)"
        elif r2 >= 0.90:
            return "🎯 VERY GOOD (R² ≥ 0.90)"
        elif r2 >= 0.80:
            return "👍 GOOD (R² ≥ 0.80)"
        elif r2 >= 0.60:
            return "⚠️  FAIR (R² ≥ 0.60)"
        else:
            return "❌ POOR (R² < 0.60)"
    
    def _print_performance_statistics(self, predictions: np.ndarray, targets: np.ndarray, errors: np.ndarray):
        """
        📊 Print Comprehensive Performance Statistics
        
        Provides detailed statistical analysis of model performance
        including accuracy metrics and error characteristics.
        """
        print("\n" + "="*70)
        print("📊 PERFORMANCE ANALYSIS SUMMARY")
        print("="*70)
        
        # Basic metrics
        mse = mean_squared_error(targets, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(targets, predictions)
        r2 = r2_score(targets, predictions)
        
        print(f"🎯 ACCURACY METRICS:")
        print(f"   • R² Score: {r2:.6f}")
        print(f"   • Mean Squared Error: {mse:.6f}")
        print(f"   • Root Mean Squared Error: {rmse:.6f}")
        print(f"   • Mean Absolute Error: {mae:.6f}")
        
        # Error statistics
        print(f"\n📈 ERROR ANALYSIS:")
        print(f"   • Mean Error: {np.mean(errors):.6f}")
        print(f"   • Error Standard Deviation: {np.std(errors):.6f}")
        print(f"   • Maximum Absolute Error: {np.max(np.abs(errors)):.6f}")
        print(f"   • Error Skewness: {stats.skew(errors.flatten()):.4f}")
        print(f"   • Error Kurtosis: {stats.kurtosis(errors.flatten()):.4f}")
        
        # Performance assessment
        performance_level = self._assess_performance_level(r2, rmse)
        print(f"\n🏆 PERFORMANCE LEVEL: {performance_level}")
        
        # Data characteristics
        print(f"\n📊 DATA CHARACTERISTICS:")
        print(f"   • Sample Size: {len(predictions)}")
        print(f"   • Target Range: [{np.min(targets):.4f}, {np.max(targets):.4f}]")
        print(f"   • Prediction Range: [{np.min(predictions):.4f}, {np.max(predictions):.4f}]")
        
        print("="*70)

# Export the main class
__all__ = ['VizPerformanceMetricsMixin']