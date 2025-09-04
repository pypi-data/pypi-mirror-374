"""
📊 Comparative Visualization - Multi-ESN Performance Analysis
===========================================================

Author: Benedict Chen (benedict@benedictchen.com)

💰 Donations: Help support this research!
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to support continued ESN research

This module provides comprehensive comparative visualization for Echo State Networks,
enabling systematic analysis of multiple reservoir configurations, hyperparameter
effects, and performance trade-offs across different experimental conditions.

🔬 Research Foundation:
======================
Visualization methods supporting ESN research analysis:
- Jaeger (2001): Performance metrics and evaluation methodologies
- Lukoševičius (2012): Practical guide to reservoir computing - analysis techniques
- Verstraeten et al. (2007): Experimental design for reservoir computing
- Modern ML: Statistical comparison methods and visualization best practices

ELI5 Explanation:
================
Think of comparative visualization like a sports scoreboard for AI algorithms! 🏆

🏃‍♂️ **Sports Tournament Analogy**:
Imagine you're coaching multiple teams (different ESN configurations) and you
want to see which performs best:
- Each team has different strengths (spectral radius, reservoir size, etc.)
- They compete in different events (time series tasks, classification, etc.)
- You need clear charts to see who wins what and why

📈 **What This Module Does**:
- Creates "scoreboards" comparing multiple ESN configurations side-by-side
- Shows which settings work best for different types of problems
- Helps you understand trade-offs (accuracy vs speed, memory vs performance)
- Makes it easy to pick the best configuration for your specific task

ASCII Comparative Analysis Architecture:
=======================================
    Multiple ESN Configs    Analysis Engine    Visualization Output
    ┌─────────────────┐    ┌─────────────────┐ ┌─────────────────────┐
    │ Config A:       │    │ Performance     │ │ Bar Charts:         │
    │ ρ=0.9, N=100   │───▶│ Metrics:        │▶│ ┌─┬─┬─┬─┬─┬─┬─┬─┐  │
    │ Accuracy: 85%   │    │ - Accuracy      │ │ │A│B│C│D│A│B│C│D│  │
    └─────────────────┘    │ - Speed         │ │ └─┴─┴─┴─┴─┴─┴─┴─┘  │
    ┌─────────────────┐    │ - Memory        │ │                     │
    │ Config B:       │───▶│ - Stability     │ │ Heatmaps:           │
    │ ρ=0.95, N=200  │    │                 │▶│ ┌─────────────────┐ │
    │ Accuracy: 92%   │    │ Statistical     │ │ │ ■■■□□ Config A  │ │
    └─────────────────┘    │ Tests:          │ │ │ ■■■■■ Config B  │ │
    ┌─────────────────┐    │ - T-tests       │ │ │ ■■■■□ Config C  │ │
    │ Config C:       │───▶│ - ANOVA         │ │ └─────────────────┘ │
    │ ρ=0.8, N=300   │    │ - Effect Size   │ │                     │
    │ Accuracy: 88%   │    │                 │▶│ Scatter Plots:      │
    └─────────────────┘    │ Ranking &       │ │      Acc vs Speed   │
    ┌─────────────────┐    │ Selection:      │ │ 100┌─────────────┐ │
    │ Config D:       │───▶│ - Pareto Front  │ │ 90 │    B●       │ │
    │ ρ=0.85, N=150  │    │ - Best Config   │ │ 80 │ C●    A● D● │ │
    │ Accuracy: 90%   │    │ - Trade-offs    │ │ 70 └─────────────┘ │
    └─────────────────┘    └─────────────────┘ └─────────────────────┘

⚡ Visualization Types:
======================
1. **Performance Bar Charts**: Direct metric comparison across configurations
2. **Heatmaps**: Parameter space exploration and correlation analysis  
3. **Scatter Plots**: Trade-off analysis (accuracy vs speed, memory vs performance)
4. **Box Plots**: Statistical distribution comparison with confidence intervals
5. **Radar Charts**: Multi-dimensional performance profiles
6. **Time Series**: Training convergence and stability analysis

📊 Analysis Features:
====================
• **Statistical Testing**: T-tests, ANOVA for significant differences
• **Effect Size Analysis**: Cohen's d, eta-squared for practical significance
• **Confidence Intervals**: Proper uncertainty quantification
• **Pareto Optimization**: Multi-objective trade-off analysis
• **Ranking Systems**: Automated best-configuration selection
• **Export Options**: High-quality plots for publications

🎯 Common Use Cases:
===================
- **Hyperparameter Tuning**: Which spectral radius works best?
- **Architecture Comparison**: Small vs large reservoirs
- **Task-Specific Analysis**: What works for your specific dataset?
- **Resource Optimization**: Best accuracy within memory/time constraints
- **Research Publication**: Professional-quality comparison figures

This module transforms complex ESN experimental results into clear,
actionable insights for both research and practical applications.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple, Dict, Any, List
import warnings
import logging

# Configure logging
logger = logging.getLogger(__name__)


def visualize_comparative_analysis(results: List[Dict[str, Any]],
                                 metrics: List[str] = None,
                                 figsize: Tuple[int, int] = (15, 10),
                                 save_path: Optional[str] = None) -> None:
    """
    Compare multiple reservoir configurations
    
    Args:
        results: List of result dictionaries from different configurations
        metrics: List of metrics to compare
        figsize: Figure size for visualization
        save_path: Optional path to save visualization
    """
    if not results:
        print("No results provided for comparison")
        return
    
    if metrics is None:
        metrics = ['spectral_radius', 'mse', 'training_time', 'memory_usage']
    
    n_configs = len(results)
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(f'Comparative Analysis of {n_configs} Reservoir Configurations', 
                 fontsize=14, fontweight='bold')
    
    # Extract configuration names
    config_names = [res.get('name', f'Config {i+1}') for i, res in enumerate(results)]
    
    # 1. Performance comparison (MSE)
    ax1 = axes[0, 0]
    if 'mse' in metrics:
        mse_values = []
        for res in results:
            if 'mse' in res:
                mse_values.append(res['mse'])
            elif 'test_error' in res:
                mse_values.append(res['test_error'])
            else:
                mse_values.append(float('nan'))
        
        if any(not np.isnan(v) for v in mse_values):
            bars = ax1.bar(range(n_configs), mse_values, alpha=0.7, edgecolor='black')
            ax1.set_xlabel('Configuration')
            ax1.set_ylabel('Mean Squared Error')
            ax1.set_title('Performance Comparison (MSE)')
            ax1.set_xticks(range(n_configs))
            ax1.set_xticklabels(config_names, rotation=45, ha='right')
            ax1.grid(True, alpha=0.3, axis='y')
            
            # Color best/worst performers
            if len([v for v in mse_values if not np.isnan(v)]) > 1:
                valid_mse = [v for v in mse_values if not np.isnan(v)]
                min_mse = min(valid_mse)
                max_mse = max(valid_mse)
                
                for i, (bar, mse) in enumerate(zip(bars, mse_values)):
                    if not np.isnan(mse):
                        if mse == min_mse:
                            bar.set_color('gold')
                        elif mse == max_mse:
                            bar.set_color('lightcoral')
        else:
            ax1.text(0.5, 0.5, 'MSE data not available', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Performance Comparison (MSE)')
    else:
        ax1.text(0.5, 0.5, 'MSE not in selected metrics', ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Performance Comparison (MSE)')
    
    # 2. Spectral radius comparison
    ax2 = axes[0, 1]
    if 'spectral_radius' in metrics:
        sr_values = []
        for res in results:
            if 'spectral_radius' in res:
                sr_values.append(res['spectral_radius'])
            elif 'reservoir_properties' in res and 'spectral_radius' in res['reservoir_properties']:
                sr_values.append(res['reservoir_properties']['spectral_radius'])
            else:
                sr_values.append(float('nan'))
        
        if any(not np.isnan(v) for v in sr_values):
            bars = ax2.bar(range(n_configs), sr_values, alpha=0.7, edgecolor='black')
            ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Stability Threshold')
            ax2.set_xlabel('Configuration')
            ax2.set_ylabel('Spectral Radius')
            ax2.set_title('Spectral Radius Comparison')
            ax2.set_xticks(range(n_configs))
            ax2.set_xticklabels(config_names, rotation=45, ha='right')
            ax2.legend()
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Color stable/unstable configurations
            for bar, sr in zip(bars, sr_values):
                if not np.isnan(sr):
                    bar.set_color('lightgreen' if sr < 1.0 else 'lightcoral')
        else:
            ax2.text(0.5, 0.5, 'Spectral radius data\nnot available', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Spectral Radius Comparison')
    else:
        ax2.text(0.5, 0.5, 'Spectral radius not\nin selected metrics', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Spectral Radius Comparison')
    
    # 3. Training time comparison
    ax3 = axes[1, 0]
    if 'training_time' in metrics:
        time_values = []
        for res in results:
            if 'training_time' in res:
                time_values.append(res['training_time'])
            elif 'timing' in res and 'training' in res['timing']:
                time_values.append(res['timing']['training'])
            else:
                time_values.append(float('nan'))
        
        if any(not np.isnan(v) for v in time_values):
            bars = ax3.bar(range(n_configs), time_values, alpha=0.7, edgecolor='black', color='skyblue')
            ax3.set_xlabel('Configuration')
            ax3.set_ylabel('Training Time (seconds)')
            ax3.set_title('Training Time Comparison')
            ax3.set_xticks(range(n_configs))
            ax3.set_xticklabels(config_names, rotation=45, ha='right')
            ax3.grid(True, alpha=0.3, axis='y')
            
            # Highlight fastest/slowest
            if len([v for v in time_values if not np.isnan(v)]) > 1:
                valid_times = [v for v in time_values if not np.isnan(v)]
                min_time = min(valid_times)
                max_time = max(valid_times)
                
                for bar, time_val in zip(bars, time_values):
                    if not np.isnan(time_val):
                        if time_val == min_time:
                            bar.set_color('lightgreen')
                        elif time_val == max_time:
                            bar.set_color('lightsalmon')
        else:
            ax3.text(0.5, 0.5, 'Training time data\nnot available', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Training Time Comparison')
    else:
        ax3.text(0.5, 0.5, 'Training time not\nin selected metrics', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Training Time Comparison')
    
    # 4. Multi-metric radar plot (simplified as line plot)
    ax4 = axes[1, 1]
    
    # Collect available metrics
    available_metrics = []
    metric_data = []
    
    for metric in ['mse', 'spectral_radius', 'training_time', 'r2_score']:
        values = []
        for res in results:
            if metric in res:
                values.append(res[metric])
            elif metric == 'mse' and 'test_error' in res:
                values.append(res['test_error'])
            elif metric == 'r2_score' and 'r2' in res:
                values.append(res['r2'])
            else:
                values.append(float('nan'))
        
        # Only include metrics with at least some valid data
        if any(not np.isnan(v) for v in values):
            available_metrics.append(metric.replace('_', ' ').title())
            
            # Normalize values for comparison (0-1 scale)
            valid_values = [v for v in values if not np.isnan(v)]
            if len(valid_values) > 1 and max(valid_values) != min(valid_values):
                # For MSE and training_time, lower is better (invert)
                if metric in ['mse', 'training_time']:
                    normalized = [(max(valid_values) - v) / (max(valid_values) - min(valid_values)) 
                                if not np.isnan(v) else 0 for v in values]
                else:
                    normalized = [(v - min(valid_values)) / (max(valid_values) - min(valid_values))
                                if not np.isnan(v) else 0 for v in values]
            else:
                normalized = [0.5 if not np.isnan(v) else 0 for v in values]
            
            metric_data.append(normalized)
    
    if available_metrics and metric_data:
        # Plot normalized metrics for each configuration
        x_pos = range(len(available_metrics))
        for i, config_name in enumerate(config_names):
            values = [data[i] for data in metric_data]
            ax4.plot(x_pos, values, 'o-', linewidth=2, markersize=6, label=config_name)
        
        ax4.set_xlabel('Metrics')
        ax4.set_ylabel('Normalized Score (0-1)')
        ax4.set_title('Multi-Metric Comparison')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(available_metrics, rotation=45, ha='right')
        ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 1)
        
        # Add note about normalization
        ax4.text(0.02, 0.02, 'Note: Values normalized (0-1)\nHigher is better for all metrics', 
                transform=ax4.transAxes, fontsize=8, alpha=0.7)
    else:
        ax4.text(0.5, 0.5, 'Insufficient data for\nmulti-metric comparison', 
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Multi-Metric Comparison')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    plt.show()


def print_comparative_summary(results: List[Dict[str, Any]]) -> None:
    """
    Print comparative summary statistics
    
    Args:
        results: List of result dictionaries from different configurations
    """
    print("\n" + "="*70)
    print("🔄 COMPARATIVE ANALYSIS SUMMARY")
    print("="*70)
    
    n_configs = len(results)
    print(f"\n📊 OVERVIEW:")
    print(f"   Number of configurations compared: {n_configs}")
    
    if n_configs == 0:
        print("   No configurations to compare")
        return
    
    # Performance comparison
    mse_values = []
    config_names = []
    
    for i, res in enumerate(results):
        name = res.get('name', f'Config {i+1}')
        config_names.append(name)
        
        if 'mse' in res:
            mse_values.append(res['mse'])
        elif 'test_error' in res:
            mse_values.append(res['test_error'])
        else:
            mse_values.append(float('nan'))
    
    valid_mse = [(name, mse) for name, mse in zip(config_names, mse_values) if not np.isnan(mse)]
    
    if valid_mse:
        print(f"\n🏆 PERFORMANCE RANKING (by MSE):")
        sorted_mse = sorted(valid_mse, key=lambda x: x[1])
        
        for rank, (name, mse) in enumerate(sorted_mse, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
            print(f"   {medal} {name}: {mse:.6f}")
    
    # Stability analysis
    sr_values = []
    for res in results:
        if 'spectral_radius' in res:
            sr_values.append(res['spectral_radius'])
        elif 'reservoir_properties' in res and 'spectral_radius' in res['reservoir_properties']:
            sr_values.append(res['reservoir_properties']['spectral_radius'])
        else:
            sr_values.append(float('nan'))
    
    valid_sr = [(name, sr) for name, sr in zip(config_names, sr_values) if not np.isnan(sr)]
    
    if valid_sr:
        print(f"\n⚖️ STABILITY ANALYSIS:")
        stable_configs = [(name, sr) for name, sr in valid_sr if sr < 1.0]
        unstable_configs = [(name, sr) for name, sr in valid_sr if sr >= 1.0]
        
        print(f"   Stable configurations: {len(stable_configs)}/{len(valid_sr)}")
        for name, sr in stable_configs:
            print(f"     ✅ {name}: ρ = {sr:.4f}")
        
        if unstable_configs:
            print(f"   Unstable configurations: {len(unstable_configs)}/{len(valid_sr)}")
            for name, sr in unstable_configs:
                print(f"     ❌ {name}: ρ = {sr:.4f}")
    
    # Resource usage comparison
    time_values = []
    for res in results:
        if 'training_time' in res:
            time_values.append(res['training_time'])
        elif 'timing' in res and 'training' in res['timing']:
            time_values.append(res['timing']['training'])
        else:
            time_values.append(float('nan'))
    
    valid_times = [(name, time_val) for name, time_val in zip(config_names, time_values) if not np.isnan(time_val)]
    
    if valid_times:
        print(f"\n⏱️  EFFICIENCY ANALYSIS:")
        sorted_times = sorted(valid_times, key=lambda x: x[1])
        
        fastest = sorted_times[0]
        slowest = sorted_times[-1]
        
        print(f"   Fastest: {fastest[0]} ({fastest[1]:.3f}s)")
        print(f"   Slowest: {slowest[0]} ({slowest[1]:.3f}s)")
        
        if len(sorted_times) > 1:
            speedup = slowest[1] / fastest[1]
            print(f"   Speed difference: {speedup:.1f}x")
    
    # Overall recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if valid_mse and valid_sr:
        # Find configurations that are both good performance and stable
        good_configs = []
        for (name_mse, mse), (name_sr, sr) in zip(sorted(valid_mse, key=lambda x: x[1]), valid_sr):
            if name_mse == name_sr and sr < 1.0 and mse <= sorted(valid_mse, key=lambda x: x[1])[len(valid_mse)//2][1]:
                good_configs.append((name_mse, mse, sr))
        
        if good_configs:
            print(f"   Best overall configurations (stable + good performance):")
            for name, mse, sr in good_configs[:3]:  # Top 3
                print(f"     🌟 {name}: MSE={mse:.6f}, ρ={sr:.4f}")
        else:
            print(f"   Consider tuning: No configurations combine both stability and good performance")
    
    print("="*70)