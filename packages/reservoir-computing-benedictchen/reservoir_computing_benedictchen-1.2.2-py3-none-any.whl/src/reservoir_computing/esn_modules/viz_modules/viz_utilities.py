"""
🔧 Reservoir Computing - Visualization Utilities Module
======================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Utility functions and helper methods for visualization including statistical analysis,
performance assessment, memory capacity estimation, and comprehensive reporting
functions shared across all visualization modules.

📊 UTILITY CAPABILITIES:
========================
• Statistical analysis and reporting functions
• Performance assessment and classification
• Memory capacity estimation algorithms
• Spectral stability and condition number analysis
• Comprehensive reporting and summary generation
• Mathematical utility functions for visualization

🔬 RESEARCH FOUNDATION:
======================
Based on established evaluation metrics from:
- Jaeger (2001): Original ESN evaluation methodologies
- Lukoševičius & Jaeger (2009): Comprehensive reservoir analysis metrics
- Verstraeten et al. (2007): Memory capacity and evaluation techniques
- Standard statistical and numerical analysis methods

This module provides the foundational utility functions,
split from the 1438-line monolith for shared visualization support.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from typing import Optional, Tuple, Dict, Any, List, Union
import warnings
from abc import ABC

# Configure professional plotting style
plt.style.use('seaborn-v0_8-whitegrid')

class VizUtilitiesMixin(ABC):
    """
    🔧 Visualization Utilities Mixin
    
    Provides essential utility functions and helper methods
    for comprehensive visualization and analysis support.
    """

    def _print_reservoir_statistics(self, eigenvals: np.ndarray, degrees: np.ndarray, weights: np.ndarray):
        """
        📊 Print Comprehensive Reservoir Statistics
        
        Provides detailed statistical analysis of reservoir properties
        including spectral characteristics and connectivity patterns.
        
        Args:
            eigenvals: Eigenvalues of reservoir matrix
            degrees: Connection degree distribution
            weights: Non-zero weight values
        """
        print("\n" + "="*70)
        print("🏗️  RESERVOIR STRUCTURE ANALYSIS")
        print("="*70)
        
        # Basic structure information
        n_reservoir = len(eigenvals)
        sparsity = 1.0 - (len(weights) / (n_reservoir * n_reservoir))
        
        print(f"📐 Matrix Dimensions: {n_reservoir}×{n_reservoir}")
        print(f"🕸️  Sparsity Level: {sparsity:.1%}")
        print(f"🔗 Total Connections: {len(weights)}")
        print(f"💪 Connection Density: {(1-sparsity):.1%}")
        
        # Spectral properties
        spectral_radius = np.max(np.abs(eigenvals))
        print(f"\n🌌 SPECTRAL ANALYSIS:")
        print(f"   • Spectral Radius: {spectral_radius:.6f}")
        print(f"   • Echo State Property: {'✓ Satisfied' if spectral_radius < 1.0 else '⚠ Violated'}")
        print(f"   • Number of Eigenvalues: {len(eigenvals)}")
        print(f"   • Complex Eigenvalues: {np.sum(np.imag(eigenvals) != 0)}")
        
        # Connection statistics  
        print(f"\n🔗 CONNECTION ANALYSIS:")
        print(f"   • Mean Degree: {degrees.mean():.2f}")
        print(f"   • Degree Std: {degrees.std():.2f}")
        print(f"   • Max Degree: {degrees.max()}")
        print(f"   • Min Degree: {degrees.min()}")
        
        # Weight statistics
        print(f"\n⚖️  WEIGHT ANALYSIS:")
        print(f"   • Mean Weight: {weights.mean():.4f}")
        print(f"   • Weight Std: {weights.std():.4f}")
        print(f"   • Weight Range: [{weights.min():.4f}, {weights.max():.4f}]")
        print(f"   • Weight Skewness: {stats.skew(weights):.4f}")
        print(f"   • Weight Kurtosis: {stats.kurtosis(weights):.4f}")
        
        print("="*70)

    def _print_dynamics_statistics(self, states: np.ndarray, inputs: Optional[np.ndarray], 
                                 outputs: Optional[np.ndarray]):
        """
        📊 Print Comprehensive Dynamics Statistics
        
        Provides detailed statistical analysis of temporal behavior
        including memory capacity and dynamic range analysis.
        
        Args:
            states: Reservoir state matrix (time_steps × n_reservoir)
            inputs: Input sequence (optional)
            outputs: Output sequence (optional)
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

    def _print_performance_statistics(self, predictions: np.ndarray, targets: np.ndarray, errors: np.ndarray):
        """
        📊 Print Comprehensive Performance Statistics
        
        Provides detailed statistical analysis of model performance
        including accuracy metrics and error characteristics.
        
        Args:
            predictions: Model predictions array
            targets: Ground truth target values  
            errors: Prediction errors (predictions - targets)
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

    def _print_comparative_summary(self, results: Dict[str, Dict[str, Any]]):
        """
        📊 Print Comprehensive Comparative Analysis Summary
        
        Provides detailed comparison across multiple configurations
        including performance rankings and statistical analysis.
        
        Args:
            results: Dictionary with configuration names as keys and metrics as values
        """
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
        """
        📊 Print Comprehensive Spectral Analysis Statistics
        
        Provides detailed mathematical analysis of spectral properties
        including stability assessment and condition analysis.
        
        Args:
            eigenvals: Eigenvalues of the reservoir matrix
            singular_vals: Singular values from SVD
            condition_number: Matrix condition number
        """
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

    def _assess_performance_level(self, r2: float, rmse: float) -> str:
        """
        🎯 Assess Performance Level Based on Metrics
        
        Provides qualitative assessment of model performance based on
        standard machine learning evaluation criteria.
        
        Args:
            r2: R-squared coefficient of determination
            rmse: Root mean squared error
            
        Returns:
            str: Performance level description with emoji
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

    def _assess_spectral_stability(self, eigenvals: np.ndarray) -> str:
        """
        🔍 Assess Spectral Stability Based on Eigenvalue Distribution
        
        Evaluates the Echo State Property and stability characteristics
        based on the eigenvalue spectrum of the reservoir matrix.
        
        Args:
            eigenvals: Array of eigenvalues
            
        Returns:
            str: Stability assessment description
        """
        spectral_radius = np.max(np.abs(eigenvals))
        
        if spectral_radius < 1.0:
            return "✓ Stable (Echo State Property)"
        elif spectral_radius < 1.1:
            return "⚠ Marginally Stable"
        else:
            return "❌ Unstable"

    def _assess_condition_number(self, condition_number: float) -> str:
        """
        🔍 Assess Numerical Condition Based on Condition Number
        
        Evaluates the numerical stability and conditioning of the
        reservoir matrix based on its condition number.
        
        Args:
            condition_number: Matrix condition number (σ_max / σ_min)
            
        Returns:
            str: Condition assessment description
        """
        if condition_number < 1e6:
            return "✓ Well-Conditioned"
        elif condition_number < 1e12:
            return "⚠ Moderately Ill-Conditioned"
        else:
            return "❌ Severely Ill-Conditioned"

    def _estimate_memory_capacity(self, states: np.ndarray) -> float:
        """
        🧠 Estimate Memory Capacity of Reservoir
        
        Provides simplified estimation of memory capacity based on
        linear memory capacity measure using autocorrelation decay.
        
        Args:
            states: Reservoir state matrix (time_steps × n_reservoir)
            
        Returns:
            float: Estimated memory capacity in time steps
            
        Research Background:
        ===================
        Based on linear memory capacity measure from Jaeger (2001) and
        extended analysis methods from Verstraeten et al. (2007).
        """
        # Simple approximation based on state autocorrelation decay
        mean_state = np.mean(states, axis=1)
        
        # Handle edge cases
        if len(mean_state) < 10:
            return 1.0
            
        try:
            # Compute autocorrelation
            autocorr = np.correlate(mean_state, mean_state, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Normalize by zero-lag value
            if autocorr[0] != 0:
                autocorr = autocorr / autocorr[0]
            else:
                return 1.0
            
            # Find decay to 1/e
            decay_threshold = 1/np.e
            decay_indices = np.where(autocorr < decay_threshold)[0]
            
            if len(decay_indices) > 0:
                memory_capacity = float(decay_indices[0])
            else:
                memory_capacity = float(len(autocorr) - 1)
                
        except Exception:
            # Fallback to simple estimate
            memory_capacity = min(10.0, len(mean_state) / 4)
            
        return memory_capacity

    def _calculate_statistical_significance(self, group1: np.ndarray, group2: np.ndarray) -> Tuple[float, str]:
        """
        📊 Calculate Statistical Significance Between Two Groups
        
        Performs appropriate statistical test to determine if there's a
        significant difference between two performance groups.
        
        Args:
            group1: First group of values
            group2: Second group of values
            
        Returns:
            Tuple[float, str]: (p_value, significance_description)
        """
        try:
            # Perform t-test for independent samples
            t_stat, p_value = stats.ttest_ind(group1, group2)
            
            if p_value < 0.001:
                significance = "Highly Significant (p < 0.001)"
            elif p_value < 0.01:
                significance = "Very Significant (p < 0.01)"
            elif p_value < 0.05:
                significance = "Significant (p < 0.05)"
            elif p_value < 0.1:
                significance = "Marginally Significant (p < 0.1)"
            else:
                significance = "Not Significant (p ≥ 0.1)"
                
            return p_value, significance
            
        except Exception:
            return np.nan, "Unable to calculate significance"

    def _normalize_metrics_for_comparison(self, metrics_dict: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """
        📏 Normalize Metrics for Fair Comparison
        
        Normalizes different metrics to [0, 1] scale for comparative analysis,
        handling both "higher is better" and "lower is better" metrics.
        
        Args:
            metrics_dict: Dictionary of metric names to value lists
            
        Returns:
            Dict[str, List[float]]: Normalized metrics dictionary
        """
        normalized_metrics = {}
        
        # Define metrics where lower is better
        lower_is_better = ['mse', 'rmse', 'mae', 'error', 'loss']
        
        for metric_name, values in metrics_dict.items():
            values = np.array(values)
            
            if len(values) == 0 or np.all(np.isnan(values)):
                normalized_metrics[metric_name] = values
                continue
                
            # Remove NaN values for normalization
            valid_values = values[~np.isnan(values)]
            
            if len(valid_values) <= 1:
                normalized_metrics[metric_name] = np.ones_like(values) * 0.5
                continue
                
            # Normalize based on metric type
            val_min, val_max = np.min(valid_values), np.max(valid_values)
            
            if val_max == val_min:
                normalized_values = np.ones_like(valid_values) * 0.5
            elif any(term in metric_name.lower() for term in lower_is_better):
                # Lower is better - invert normalization
                normalized_values = 1 - (valid_values - val_min) / (val_max - val_min)
            else:
                # Higher is better - standard normalization
                normalized_values = (valid_values - val_min) / (val_max - val_min)
            
            # Reconstruct with NaN preservation
            result = np.full_like(values, np.nan, dtype=float)
            result[~np.isnan(values)] = normalized_values
            normalized_metrics[metric_name] = result.tolist()
            
        return normalized_metrics

# Export the main class
__all__ = ['VizUtilitiesMixin']