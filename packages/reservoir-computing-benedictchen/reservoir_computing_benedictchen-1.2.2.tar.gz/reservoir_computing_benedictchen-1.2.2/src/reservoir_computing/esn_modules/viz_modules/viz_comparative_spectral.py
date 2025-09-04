"""
🌌 Reservoir Computing - Comparative & Spectral Analysis Visualization Module
============================================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Advanced comparative analysis and spectral visualization including multi-configuration
comparison, parameter sensitivity analysis, eigenvalue spectrum analysis, and
comprehensive mathematical characterization of reservoir systems.

📊 VISUALIZATION CAPABILITIES:
=============================
• Multi-configuration comparative analysis with statistical significance
• Parameter sensitivity heatmaps and performance landscapes  
• Advanced eigenvalue spectrum analysis with stability assessment
• Singular value decomposition and condition number analysis
• Comparative performance radar charts and ranking systems
• Mathematical spectral properties visualization

🔬 RESEARCH FOUNDATION:
======================
Based on advanced analysis techniques from:
- Jaeger (2001): Spectral analysis and stability assessment methods
- Lukoševičius & Jaeger (2009): Comparative evaluation methodologies
- Verstraeten et al. (2007): Parameter sensitivity and memory capacity analysis
- Mathematical foundations from dynamical systems and linear algebra

This module represents the most advanced analytical components,
split from the 1438-line monolith for specialized mathematical visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import stats
from scipy.linalg import svd
from sklearn.metrics import r2_score, mean_squared_error
from typing import Optional, Tuple, Dict, Any, List, Union
import warnings
from abc import ABC, abstractmethod
import pandas as pd

# Configure professional plotting style for advanced analysis
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class VizComparativeSpectralMixin(ABC):
    """
    🌌 Comparative & Spectral Analysis Visualization Mixin
    
    Provides advanced comparative analysis and spectral visualization
    capabilities for comprehensive reservoir computing system evaluation.
    """
    
    # Abstract properties that must be provided by the implementing class
    @property
    @abstractmethod
    def W_reservoir(self) -> np.ndarray:
        """Reservoir weight matrix"""
        pass

    def visualize_comparative_analysis(self, results: Dict[str, Dict[str, Any]], 
                                     figsize: Tuple[int, int] = (16, 12), save_path: Optional[str] = None):
        """
        🏆 Comprehensive Comparative Analysis Visualization
        
        Creates sophisticated multi-configuration comparison including performance
        rankings, parameter sensitivity, and statistical significance analysis.
        
        Args:
            results: Dictionary with configuration names as keys and metrics as values
                    Expected format: {'config_name': {'metric1': value, 'metric2': [values], ...}}
            figsize: Figure size in inches
            save_path: Path to save figure (optional)
            
        Research Background:
        ===================
        Based on rigorous comparative evaluation methodologies from reservoir computing
        literature for systematic parameter optimization and configuration analysis.
        """
        
        if not results or len(results) < 2:
            print("⚠️  Need at least 2 configurations for meaningful comparison")
            return
            
        fig = plt.figure(figsize=figsize)
        fig.suptitle('Comprehensive Comparative Analysis', fontsize=16, fontweight='bold')
        
        # Create subplot layout
        gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.4)
        
        # Extract common metrics across configurations
        config_names = list(results.keys())
        all_metrics = set()
        for config_results in results.values():
            all_metrics.update(config_results.keys())
        
        # Filter to numeric metrics only
        numeric_metrics = []
        for metric in all_metrics:
            try:
                # Test if all configs have numeric values for this metric
                values = []
                for config_name in config_names:
                    if metric in results[config_name]:
                        val = results[config_name][metric]
                        if isinstance(val, (list, np.ndarray)):
                            if len(val) > 0:
                                values.append(np.mean(val))
                        elif isinstance(val, (int, float)):
                            values.append(val)
                if len(values) == len(config_names):
                    numeric_metrics.append(metric)
            except:
                continue
        
        if len(numeric_metrics) == 0:
            print("⚠️  No compatible numeric metrics found for comparison")
            return
        
        # 1. Performance Ranking Heatmap
        ax1 = fig.add_subplot(gs[0, :2])
        
        # Create performance matrix
        perf_matrix = []
        for metric in numeric_metrics[:8]:  # Limit to top 8 metrics for clarity
            metric_values = []
            for config_name in config_names:
                if metric in results[config_name]:
                    val = results[config_name][metric]
                    if isinstance(val, (list, np.ndarray)):
                        metric_values.append(np.mean(val))
                    else:
                        metric_values.append(val)
                else:
                    metric_values.append(np.nan)
            perf_matrix.append(metric_values)
        
        perf_matrix = np.array(perf_matrix)
        
        # Normalize for heatmap (higher is better convention)
        perf_matrix_norm = np.zeros_like(perf_matrix)
        for i, metric in enumerate(numeric_metrics[:8]):
            values = perf_matrix[i, :]
            valid_values = values[~np.isnan(values)]
            if len(valid_values) > 0:
                # Normalize to [0, 1] where 1 is best
                if 'error' in metric.lower() or 'mse' in metric.lower():
                    # Lower is better
                    perf_matrix_norm[i, :] = 1 - (values - np.nanmin(values)) / (np.nanmax(values) - np.nanmin(values) + 1e-10)
                else:
                    # Higher is better
                    perf_matrix_norm[i, :] = (values - np.nanmin(values)) / (np.nanmax(values) - np.nanmin(values) + 1e-10)
        
        # Create heatmap
        sns.heatmap(perf_matrix_norm, 
                   xticklabels=config_names,
                   yticklabels=numeric_metrics[:8],
                   annot=perf_matrix, 
                   fmt='.4f',
                   cmap='RdYlGn',
                   center=0.5,
                   ax=ax1,
                   cbar_kws={'label': 'Normalized Performance'})
        
        ax1.set_title('Configuration Performance Heatmap')
        ax1.set_xlabel('Configuration')
        ax1.set_ylabel('Metrics')
        
        # 2. Radar Chart for Top Configurations
        ax2 = fig.add_subplot(gs[0, 2], projection='polar')
        
        if len(numeric_metrics) >= 3 and len(config_names) >= 2:
            # Select top 3 configurations based on overall performance
            overall_scores = np.nanmean(perf_matrix_norm, axis=0)
            top_configs = np.argsort(overall_scores)[-3:]
            
            angles = np.linspace(0, 2 * np.pi, len(numeric_metrics[:6]), endpoint=False)
            angles = np.concatenate((angles, [angles[0]]))
            
            colors = ['red', 'blue', 'green']
            for i, config_idx in enumerate(top_configs):
                values = perf_matrix_norm[:6, config_idx]
                values = np.concatenate((values, [values[0]]))
                ax2.plot(angles, values, 'o-', linewidth=2, color=colors[i], 
                        alpha=0.7, label=config_names[config_idx])
                ax2.fill(angles, values, alpha=0.25, color=colors[i])
            
            ax2.set_xticks(angles[:-1])
            ax2.set_xticklabels(numeric_metrics[:6], fontsize=8)
            ax2.set_ylim(0, 1)
            ax2.set_title('Performance Radar Chart\n(Top 3 Configurations)')
            ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        # 3. Statistical Significance Analysis
        ax3 = fig.add_subplot(gs[1, :2])
        
        if len(config_names) >= 2:
            # Perform pairwise t-tests for the first available metric with variance
            test_metric = None
            for metric in numeric_metrics:
                # Find a metric with multiple values or variance
                has_variance = False
                for config_name in config_names[:2]:  # Test first two configs
                    if metric in results[config_name]:
                        val = results[config_name][metric]
                        if isinstance(val, (list, np.ndarray)) and len(val) > 1:
                            has_variance = True
                            break
                if has_variance:
                    test_metric = metric
                    break
            
            if test_metric:
                # Extract values for statistical test
                group1_data = results[config_names[0]][test_metric]
                group2_data = results[config_names[1]][test_metric]
                
                if isinstance(group1_data, (list, np.ndarray)) and isinstance(group2_data, (list, np.ndarray)):
                    # Box plot comparison
                    data_for_plot = [group1_data, group2_data]
                    ax3.boxplot(data_for_plot, labels=config_names[:2])
                    
                    # Perform t-test
                    try:
                        t_stat, p_value = stats.ttest_ind(group1_data, group2_data)
                        significance = "Significant" if p_value < 0.05 else "Not Significant"
                        ax3.text(0.02, 0.98, f't-test: p={p_value:.4f}\n{significance}', 
                                transform=ax3.transAxes,
                                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                                verticalalignment='top')
                    except:
                        pass
                    
                    ax3.set_title(f'Statistical Comparison: {test_metric}')
                    ax3.set_ylabel('Value')
                    ax3.grid(True, alpha=0.3)
                else:
                    ax3.text(0.5, 0.5, 'Insufficient data\nfor statistical analysis', 
                            ha='center', va='center', transform=ax3.transAxes)
            else:
                ax3.text(0.5, 0.5, 'No suitable metrics\nfor statistical analysis', 
                        ha='center', va='center', transform=ax3.transAxes)
            
            ax3.set_title('Statistical Significance Analysis')
        
        # 4. Parameter Sensitivity Matrix
        ax4 = fig.add_subplot(gs[1, 2])
        
        # Extract parameter values if available
        param_names = []
        param_values = []
        
        # Look for common parameter names
        common_params = ['spectral_radius', 'sparsity', 'input_scaling', 'n_reservoir', 'leak_rate']
        for param in common_params:
            param_vals = []
            for config_name in config_names:
                config_data = results[config_name]
                if param in config_data:
                    val = config_data[param]
                    if isinstance(val, (int, float)):
                        param_vals.append(val)
                    elif isinstance(val, (list, np.ndarray)) and len(val) > 0:
                        param_vals.append(np.mean(val))
            
            if len(param_vals) == len(config_names) and len(set(param_vals)) > 1:
                param_names.append(param)
                param_values.append(param_vals)
        
        if len(param_names) > 0 and len(numeric_metrics) > 0:
            # Create correlation matrix between parameters and performance
            perf_metric = numeric_metrics[0]  # Use first metric
            perf_vals = []
            for config_name in config_names:
                val = results[config_name][perf_metric]
                if isinstance(val, (list, np.ndarray)):
                    perf_vals.append(np.mean(val))
                else:
                    perf_vals.append(val)
            
            correlations = []
            for param_vals in param_values:
                try:
                    corr = np.corrcoef(param_vals, perf_vals)[0, 1]
                    correlations.append(corr if not np.isnan(corr) else 0)
                except:
                    correlations.append(0)
            
            # Bar plot of correlations
            bars = ax4.bar(range(len(param_names)), correlations)
            ax4.set_xticks(range(len(param_names)))
            ax4.set_xticklabels(param_names, rotation=45)
            ax4.set_ylabel(f'Correlation with {perf_metric}')
            ax4.set_title('Parameter Sensitivity')
            ax4.axhline(0, color='black', linestyle='-', alpha=0.3)
            ax4.grid(True, alpha=0.3)
            
            # Color bars by correlation strength
            for i, (bar, corr) in enumerate(zip(bars, correlations)):
                bar.set_color('red' if corr > 0 else 'blue')
                bar.set_alpha(min(abs(corr), 1.0))
        else:
            ax4.text(0.5, 0.5, 'No parameter data\navailable', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Parameter Sensitivity')
        
        # 5. Performance Distribution
        ax5 = fig.add_subplot(gs[2, 0])
        
        if len(numeric_metrics) > 0:
            main_metric = numeric_metrics[0]
            metric_values = []
            labels = []
            
            for config_name in config_names:
                if main_metric in results[config_name]:
                    val = results[config_name][main_metric]
                    if isinstance(val, (list, np.ndarray)):
                        metric_values.extend(val)
                        labels.extend([config_name] * len(val))
                    else:
                        metric_values.append(val)
                        labels.append(config_name)
            
            if len(metric_values) > 0:
                # Create violin plot
                df = pd.DataFrame({'value': metric_values, 'config': labels})
                unique_configs = df['config'].unique()
                
                violin_data = [df[df['config'] == config]['value'].values for config in unique_configs]
                parts = ax5.violinplot(violin_data, positions=range(len(unique_configs)), showmeans=True)
                
                ax5.set_xticks(range(len(unique_configs)))
                ax5.set_xticklabels(unique_configs, rotation=45)
                ax5.set_title(f'{main_metric} Distribution')
                ax5.set_ylabel('Value')
                ax5.grid(True, alpha=0.3)
        
        # 6. Configuration Ranking
        ax6 = fig.add_subplot(gs[2, 1:])
        
        # Calculate overall ranking based on normalized performance
        if len(numeric_metrics) > 0:
            overall_scores = np.nanmean(perf_matrix_norm, axis=0)
            ranking_indices = np.argsort(overall_scores)[::-1]  # Descending order
            
            ranked_configs = [config_names[i] for i in ranking_indices]
            ranked_scores = [overall_scores[i] for i in ranking_indices]
            
            bars = ax6.barh(range(len(ranked_configs)), ranked_scores, 
                           color=plt.cm.RdYlGn(ranked_scores))
            
            ax6.set_yticks(range(len(ranked_configs)))
            ax6.set_yticklabels(ranked_configs)
            ax6.set_xlabel('Overall Performance Score')
            ax6.set_title('Configuration Ranking')
            ax6.set_xlim(0, 1)
            
            # Add score annotations
            for i, (bar, score) in enumerate(zip(bars, ranked_scores)):
                ax6.text(score + 0.01, i, f'{score:.3f}', 
                        va='center', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"🏆 Comparative analysis saved to: {save_path}")
            
        plt.show()
        
        # Print comparative summary
        self._print_comparative_summary(results)

    def visualize_spectral_analysis(self, figsize: Tuple[int, int] = (15, 10), 
                                   save_path: Optional[str] = None):
        """
        🌌 Advanced Spectral Analysis Visualization
        
        Creates comprehensive spectral analysis including eigenvalue distribution,
        singular value decomposition, condition number analysis, and stability assessment.
        
        Args:
            figsize: Figure size in inches
            save_path: Path to save figure (optional)
            
        Research Background:
        ===================
        Based on advanced spectral analysis techniques from dynamical systems theory
        and numerical linear algebra for comprehensive mathematical characterization.
        """
        
        fig = plt.figure(figsize=figsize)
        fig.suptitle('Advanced Spectral Analysis', fontsize=16, fontweight='bold')
        
        # Calculate spectral properties
        eigenvals = np.linalg.eigvals(self.W_reservoir)
        U, sigma, Vt = svd(self.W_reservoir)
        spectral_radius = np.max(np.abs(eigenvals))
        condition_number = np.max(sigma) / np.min(sigma) if np.min(sigma) > 1e-15 else np.inf
        
        # Create subplot layout
        gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.4)
        
        # 1. Eigenvalue Spectrum with Stability Analysis
        ax1 = fig.add_subplot(gs[0, 0])
        
        scatter = ax1.scatter(eigenvals.real, eigenvals.imag, alpha=0.7, 
                            c=np.abs(eigenvals), cmap='viridis', s=40, edgecolors='black', linewidth=0.5)
        
        # Unit circle for stability
        circle = patches.Circle((0, 0), 1, fill=False, color='red', linestyle='--', 
                               linewidth=2, label='Unit Circle')
        ax1.add_patch(circle)
        
        # Spectral radius circle
        spec_circle = patches.Circle((0, 0), spectral_radius, fill=False, color='orange', 
                                   linestyle='-', linewidth=2, alpha=0.7, 
                                   label=f'ρ = {spectral_radius:.3f}')
        ax1.add_patch(spec_circle)
        
        ax1.set_title('Eigenvalue Spectrum')
        ax1.set_xlabel('Real Part')
        ax1.set_ylabel('Imaginary Part')
        ax1.axis('equal')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax1, shrink=0.8, label='|λ|')
        
        # Add stability assessment
        stability_status = self._assess_spectral_stability(eigenvals)
        condition_status = self._assess_condition_number(condition_number)
        ax1.text(0.02, 0.98, f'{stability_status}\n{condition_status}', 
                transform=ax1.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7),
                verticalalignment='top')
        
        # 2. Eigenvalue Magnitude Distribution
        ax2 = fig.add_subplot(gs[0, 1])
        
        eigenval_magnitudes = np.abs(eigenvals)
        n, bins, patches = ax2.hist(eigenval_magnitudes, bins=30, alpha=0.7, 
                                   edgecolor='black', density=True, color='skyblue')
        
        # Mark spectral radius
        ax2.axvline(spectral_radius, color='red', linestyle='--', linewidth=2, 
                   label=f'ρ = {spectral_radius:.3f}')
        ax2.axvline(1.0, color='orange', linestyle=':', linewidth=2, 
                   label='Unit Circle', alpha=0.7)
        
        ax2.set_title('Eigenvalue Magnitude Distribution')
        ax2.set_xlabel('|λ|')
        ax2.set_ylabel('Density')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Singular Value Spectrum
        ax3 = fig.add_subplot(gs[0, 2])
        
        ax3.semilogy(sigma, 'bo-', linewidth=2, markersize=4, alpha=0.8)
        ax3.set_title('Singular Value Spectrum')
        ax3.set_xlabel('Index')
        ax3.set_ylabel('Singular Value (σ)')
        ax3.grid(True, alpha=0.3)
        
        # Add condition number annotation
        ax3.text(0.02, 0.98, f'κ = {condition_number:.2e}', transform=ax3.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top', fontweight='bold')
        
        # 4. Spectral Properties Summary
        ax4 = fig.add_subplot(gs[1, 0])
        
        # Calculate additional spectral properties
        trace = np.trace(self.W_reservoir)
        frobenius_norm = np.linalg.norm(self.W_reservoir, 'fro')
        nuclear_norm = np.sum(sigma)
        
        summary_text = f"""
SPECTRAL PROPERTIES:

• Matrix Size: {self.W_reservoir.shape[0]}×{self.W_reservoir.shape[1]}
• Spectral Radius: {spectral_radius:.6f}
• Condition Number: {condition_number:.2e}
• Trace: {trace:.6f}
• Frobenius Norm: {frobenius_norm:.6f}
• Nuclear Norm: {nuclear_norm:.6f}

STABILITY ANALYSIS:
• Echo State Property: {stability_status.split()[0]}
• Numerical Stability: {condition_status.split()[0]}
• Eigenvalue Distribution: {len(eigenvals)} total
• Complex Eigenvalues: {np.sum(np.imag(eigenvals) != 0)}
        """
        
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
                verticalalignment='top', fontsize=10, fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        ax4.set_title('Spectral Summary')
        ax4.axis('off')
        
        # 5. Cumulative Singular Value Energy
        ax5 = fig.add_subplot(gs[1, 1])
        
        sigma_squared = sigma ** 2
        cumulative_energy = np.cumsum(sigma_squared) / np.sum(sigma_squared)
        
        ax5.plot(range(1, len(cumulative_energy) + 1), cumulative_energy, 
                'g-', linewidth=2, marker='o', markersize=3)
        ax5.axhline(0.95, color='red', linestyle='--', alpha=0.7, label='95% Energy')
        ax5.axhline(0.99, color='orange', linestyle='--', alpha=0.7, label='99% Energy')
        
        # Find 95% and 99% points
        idx_95 = np.argmax(cumulative_energy >= 0.95) + 1
        idx_99 = np.argmax(cumulative_energy >= 0.99) + 1
        
        ax5.set_title('Cumulative Spectral Energy')
        ax5.set_xlabel('Number of Components')
        ax5.set_ylabel('Cumulative Energy')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # Add annotations
        ax5.text(0.02, 0.5, f'95%: {idx_95} components\n99%: {idx_99} components', 
                transform=ax5.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        # 6. Eigenvalue Phase Distribution
        ax6 = fig.add_subplot(gs[1, 2], projection='polar')
        
        eigenval_phases = np.angle(eigenvals)
        ax6.hist(eigenval_phases, bins=20, alpha=0.7, edgecolor='black')
        ax6.set_title('Eigenvalue Phase Distribution')
        ax6.set_theta_zero_location('E')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"🌌 Spectral analysis saved to: {save_path}")
            
        plt.show()
        
        # Print spectral statistics
        self._print_spectral_statistics(eigenvals, sigma, condition_number)
        
    def _assess_spectral_stability(self, eigenvals: np.ndarray) -> str:
        """🔍 Assess spectral stability based on eigenvalue distribution"""
        spectral_radius = np.max(np.abs(eigenvals))
        
        if spectral_radius < 1.0:
            return "✓ Stable (Echo State Property)"
        elif spectral_radius < 1.1:
            return "⚠ Marginally Stable"
        else:
            return "❌ Unstable"
    
    def _assess_condition_number(self, condition_number: float) -> str:
        """🔍 Assess numerical condition based on condition number"""
        if condition_number < 1e6:
            return "✓ Well-Conditioned"
        elif condition_number < 1e12:
            return "⚠ Moderately Ill-Conditioned"
        else:
            return "❌ Severely Ill-Conditioned"
            
    def _print_comparative_summary(self, results: Dict[str, Dict[str, Any]]):
        """📊 Print comprehensive comparative analysis summary"""
        print("\n" + "="*70)
        print("🏆 COMPARATIVE ANALYSIS SUMMARY")
        print("="*70)
        
        print(f"📊 Configurations Analyzed: {len(results)}")
        
        for config_name, metrics in results.items():
            print(f"\n🔧 {config_name}:")
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (list, np.ndarray)):
                    if len(metric_value) > 0:
                        print(f"   • {metric_name}: {np.mean(metric_value):.4f} ± {np.std(metric_value):.4f}")
                elif isinstance(metric_value, (int, float)):
                    print(f"   • {metric_name}: {metric_value:.4f}")
        
        print("="*70)
        
    def _print_spectral_statistics(self, eigenvals: np.ndarray, singular_vals: np.ndarray, condition_number: float):
        """📊 Print comprehensive spectral analysis statistics"""
        print("\n" + "="*70)
        print("🌌 SPECTRAL ANALYSIS SUMMARY")
        print("="*70)
        
        spectral_radius = np.max(np.abs(eigenvals))
        
        print(f"🎯 EIGENVALUE ANALYSIS:")
        print(f"   • Spectral Radius: {spectral_radius:.6f}")
        print(f"   • Total Eigenvalues: {len(eigenvals)}")
        print(f"   • Complex Eigenvalues: {np.sum(np.imag(eigenvals) != 0)}")
        print(f"   • Eigenvalues > 1: {np.sum(np.abs(eigenvals) > 1.0)}")
        print(f"   • Stability Status: {self._assess_spectral_stability(eigenvals)}")
        
        print(f"\n📐 SINGULAR VALUE ANALYSIS:")
        print(f"   • Condition Number: {condition_number:.2e}")
        print(f"   • Numerical Status: {self._assess_condition_number(condition_number)}")
        print(f"   • Largest Singular Value: {np.max(singular_vals):.6f}")
        print(f"   • Smallest Singular Value: {np.min(singular_vals):.6f}")
        print(f"   • Effective Rank (1% threshold): {np.sum(singular_vals > 0.01 * np.max(singular_vals))}")
        
        print("="*70)

# Export the main class
__all__ = ['VizComparativeSpectralMixin']