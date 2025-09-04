"""
📊 Reservoir Computing - Statistics & Utilities Visualization Module
===================================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Specialized utilities for statistical analysis and textual reporting of reservoir systems.
Provides comprehensive statistical summaries, assessment functions, and formatted output
for research documentation and analysis reporting.

📊 STATISTICAL CAPABILITIES:
=============================
• Comprehensive reservoir structure statistics
• Dynamic behavior statistical analysis
• Performance metrics statistical summaries
• Comparative analysis statistical reporting
• Spectral properties assessment and evaluation

🔬 RESEARCH FOUNDATION:
======================
Based on statistical analysis standards from reservoir computing literature:
- Jaeger (2001): Statistical characterization methods
- Lukoševičius & Jaeger (2009): Benchmarking and evaluation standards
- Statistical best practices for scientific reporting
- Mathematical assessment criteria for reservoir systems

🎨 PROFESSIONAL STANDARDS:
=========================
• Comprehensive statistical summaries with confidence intervals
• Research-grade assessment criteria and thresholds
• Professional formatting for scientific documentation
• Clear interpretations and recommendations
• Standardized evaluation metrics and scales

This module represents the statistical analysis and reporting components,
split from the 1569-line monolith for specialized analysis functionality.
"""

import numpy as np
import warnings
from typing import Optional, Tuple, Dict, Any, List, Union
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging

# Configure logging for statistics reporting
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# STATISTICS PRINTING UTILITIES
# ================================

def print_reservoir_statistics(reservoir_weights: np.ndarray, 
                              input_weights: Optional[np.ndarray] = None,
                              spectral_radius: Optional[float] = None,
                              detailed: bool = True) -> None:
    """
    🏗️ Print Comprehensive Reservoir Structure Statistics
    
    Provides detailed statistical analysis of reservoir structure including
    weight distributions, connectivity patterns, and topological properties.
    
    Args:
        reservoir_weights: Reservoir weight matrix (N×N)
        input_weights: Input weight matrix (N×M), optional
        spectral_radius: Known spectral radius for verification
        detailed: Whether to print detailed analysis
        
    Research Background:
    ===================
    Statistical characterization based on Jaeger (2001) reservoir analysis
    methods and extended with modern network analysis techniques.
    """
    N = reservoir_weights.shape[0]
    
    print("\n" + "="*70)
    print("🏗️  RESERVOIR STRUCTURE STATISTICAL ANALYSIS")
    print("="*70)
    
    # === BASIC PROPERTIES ===
    print(f"\n📏 Basic Properties:")
    print(f"   • Matrix Size: {N}×{N} ({N**2:,} total weights)")
    print(f"   • Memory Usage: ~{(N**2 * 8 / 1024**2):.2f} MB (float64)")
    
    # === WEIGHT STATISTICS ===
    weights_flat = reservoir_weights.flatten()
    non_zero_weights = weights_flat[np.abs(weights_flat) > 1e-10]
    
    print(f"\n🎯 Weight Distribution:")
    print(f"   • Mean: {np.mean(weights_flat):.6f}")
    print(f"   • Std Dev: {np.std(weights_flat):.6f}")
    print(f"   • Min/Max: {np.min(weights_flat):.6f} / {np.max(weights_flat):.6f}")
    print(f"   • Range: {np.ptp(weights_flat):.6f}")
    
    # Statistical tests
    try:
        shapiro_stat, shapiro_p = stats.shapiro(weights_flat[:min(5000, len(weights_flat))])
        print(f"   • Normality (Shapiro-Wilk): p={shapiro_p:.4f} {'(Normal)' if shapiro_p > 0.05 else '(Non-normal)'}")
    except:
        print(f"   • Normality test: Failed")
    
    # === CONNECTIVITY ANALYSIS ===
    binary_matrix = (np.abs(reservoir_weights) > 1e-10).astype(int)
    n_connections = np.sum(binary_matrix)
    density = n_connections / (N * N)
    
    print(f"\n🔗 Connectivity Analysis:")
    print(f"   • Total Connections: {n_connections:,} / {N*N:,}")
    print(f"   • Density: {density:.4f} ({density*100:.2f}%)")
    print(f"   • Sparsity: {1-density:.4f} ({(1-density)*100:.2f}%)")
    
    # Degree statistics
    in_degrees = np.sum(binary_matrix, axis=0)
    out_degrees = np.sum(binary_matrix, axis=1)
    
    print(f"   • In-degree:  mean={np.mean(in_degrees):.1f}, std={np.std(in_degrees):.1f}")
    print(f"   • Out-degree: mean={np.mean(out_degrees):.1f}, std={np.std(out_degrees):.1f}")
    
    # === SPECTRAL PROPERTIES ===
    eigenvals = np.linalg.eigvals(reservoir_weights)
    computed_spectral_radius = np.max(np.abs(eigenvals))
    
    print(f"\n🌌 Spectral Properties:")
    print(f"   • Spectral Radius: {computed_spectral_radius:.6f}")
    if spectral_radius is not None:
        error = abs(computed_spectral_radius - spectral_radius)
        print(f"   • Expected: {spectral_radius:.6f} (error: {error:.6f})")
    
    print(f"   • Trace: {np.trace(reservoir_weights):.6f}")
    print(f"   • Determinant: {np.linalg.det(reservoir_weights):.6e}")
    print(f"   • Condition Number: {np.linalg.cond(reservoir_weights):.2e}")
    
    # Stability assessment
    stability_status = assess_spectral_stability(eigenvals)
    print(f"   • Stability Assessment: {stability_status}")
    
    if detailed:
        # === DETAILED EIGENVALUE ANALYSIS ===
        real_eigenvals = eigenvals[np.isreal(eigenvals)].real
        complex_eigenvals = eigenvals[~np.isreal(eigenvals)]
        
        print(f"\n🕵️ Detailed Eigenvalue Analysis:")
        print(f"   • Total Eigenvalues: {len(eigenvals)}")
        print(f"   • Real Eigenvalues: {len(real_eigenvals)} ({len(real_eigenvals)/len(eigenvals)*100:.1f}%)")
        print(f"   • Complex Eigenvalues: {len(complex_eigenvals)} ({len(complex_eigenvals)/len(eigenvals)*100:.1f}%)")
        
        if len(real_eigenvals) > 0:
            print(f"   • Real eigenvalues range: [{np.min(real_eigenvals):.4f}, {np.max(real_eigenvals):.4f}]")
        
        # Count eigenvalues by magnitude regions
        small_eigs = np.sum(np.abs(eigenvals) < 0.1)
        medium_eigs = np.sum((np.abs(eigenvals) >= 0.1) & (np.abs(eigenvals) < 0.9))
        large_eigs = np.sum(np.abs(eigenvals) >= 0.9)
        
        print(f"   • |λ| < 0.1: {small_eigs} ({small_eigs/len(eigenvals)*100:.1f}%)")
        print(f"   • 0.1 ≤ |λ| < 0.9: {medium_eigs} ({medium_eigs/len(eigenvals)*100:.1f}%)")
        print(f"   • |λ| ≥ 0.9: {large_eigs} ({large_eigs/len(eigenvals)*100:.1f}%)")
    
    # === INPUT WEIGHTS ANALYSIS (if provided) ===
    if input_weights is not None:
        print(f"\n📎 Input Weights Analysis:")
        M = input_weights.shape[1]
        print(f"   • Input Dimensions: {M}")
        print(f"   • Weight Statistics:")
        print(f"     - Mean: {np.mean(input_weights):.6f}")
        print(f"     - Std Dev: {np.std(input_weights):.6f}")
        print(f"     - Range: [{np.min(input_weights):.4f}, {np.max(input_weights):.4f}]")
        
        # Per-dimension analysis
        if detailed and M <= 10:
            print(f"   • Per-dimension statistics:")
            for i in range(M):
                dim_weights = input_weights[:, i]
                print(f"     - Dim {i}: mean={np.mean(dim_weights):.4f}, std={np.std(dim_weights):.4f}")
    
    print("\n" + "="*70)

def print_dynamics_statistics(states: np.ndarray, 
                             input_sequence: Optional[np.ndarray] = None,
                             detailed: bool = True) -> None:
    """
    🌊 Print Comprehensive Dynamics Statistics
    
    Provides detailed statistical analysis of reservoir dynamics including
    temporal patterns, activity distributions, and correlation analysis.
    
    Args:
        states: Reservoir states over time (T×N matrix)
        input_sequence: Input sequence over time (T×M), optional
        detailed: Whether to print detailed analysis
        
    Research Background:
    ===================
    Temporal analysis methods based on dynamical systems theory and
    reservoir computing evaluation standards.
    """
    T, N = states.shape
    
    print("\n" + "="*70)
    print("🌊  RESERVOIR DYNAMICS STATISTICAL ANALYSIS")
    print("="*70)
    
    # === BASIC PROPERTIES ===
    print(f"\n📏 Basic Properties:")
    print(f"   • Time Steps: {T:,}")
    print(f"   • Reservoir Size: {N}")
    print(f"   • Total State Values: {T*N:,}")
    
    # === ACTIVITY STATISTICS ===
    states_flat = states.flatten()
    mean_activity = np.mean(states, axis=1)
    
    print(f"\n📈 Activity Statistics:")
    print(f"   • Overall Mean: {np.mean(states_flat):.6f}")
    print(f"   • Overall Std: {np.std(states_flat):.6f}")
    print(f"   • Activity Range: [{np.min(states_flat):.4f}, {np.max(states_flat):.4f}]")
    print(f"   • Mean Absolute Activity: {np.mean(np.abs(states_flat)):.6f}")
    
    # Activity distribution analysis
    print(f"\n📊 Activity Distribution:")
    
    # Count neurons by activity level
    neuron_means = np.mean(states, axis=0)
    neuron_stds = np.std(states, axis=0)
    
    low_activity = np.sum(np.abs(neuron_means) < 0.1)
    medium_activity = np.sum((np.abs(neuron_means) >= 0.1) & (np.abs(neuron_means) < 0.5))
    high_activity = np.sum(np.abs(neuron_means) >= 0.5)
    
    print(f"   • Low activity neurons (|μ| < 0.1): {low_activity} ({low_activity/N*100:.1f}%)")
    print(f"   • Medium activity neurons (0.1 ≤ |μ| < 0.5): {medium_activity} ({medium_activity/N*100:.1f}%)")
    print(f"   • High activity neurons (|μ| ≥ 0.5): {high_activity} ({high_activity/N*100:.1f}%)")
    
    # Temporal statistics
    print(f"\n🕰️ Temporal Analysis:")
    print(f"   • Mean Activity Range: [{np.min(mean_activity):.4f}, {np.max(mean_activity):.4f}]")
    print(f"   • Temporal Std: {np.std(mean_activity):.6f}")
    
    # Autocorrelation analysis
    if T > 10:
        max_lag = min(50, T // 4)
        autocorr_values = []
        
        for lag in range(1, max_lag + 1):
            if lag < len(mean_activity):
                corr = np.corrcoef(mean_activity[:-lag], mean_activity[lag:])[0, 1]
                if not np.isnan(corr):
                    autocorr_values.append(corr)
        
        if autocorr_values:
            first_autocorr = autocorr_values[0]
            min_autocorr = np.min(autocorr_values)
            print(f"   • Autocorrelation (lag=1): {first_autocorr:.4f}")
            print(f"   • Min Autocorrelation: {min_autocorr:.4f}")
            
            # Find memory decay timescale
            decay_threshold = 0.1
            decay_lag = None
            for i, corr in enumerate(autocorr_values):
                if abs(corr) < decay_threshold:
                    decay_lag = i + 1
                    break
            
            if decay_lag:
                print(f"   • Memory Timescale (~{decay_threshold} threshold): {decay_lag} steps")
    
    if detailed:
        # === DETAILED NEURON ANALYSIS ===
        print(f"\n🕵️ Detailed Neuron Analysis:")
        
        # Find most/least active neurons
        neuron_activity = np.mean(np.abs(states), axis=0)
        most_active_idx = np.argmax(neuron_activity)
        least_active_idx = np.argmin(neuron_activity)
        
        print(f"   • Most active neuron: #{most_active_idx} (activity: {neuron_activity[most_active_idx]:.4f})")
        print(f"   • Least active neuron: #{least_active_idx} (activity: {neuron_activity[least_active_idx]:.4f})")
        
        # Synchronization analysis
        if N > 1:
            pairwise_corrs = []
            for i in range(min(10, N)):  # Sample pairs to avoid O(N^2) computation
                for j in range(i+1, min(10, N)):
                    corr = np.corrcoef(states[:, i], states[:, j])[0, 1]
                    if not np.isnan(corr):
                        pairwise_corrs.append(corr)
            
            if pairwise_corrs:
                mean_sync = np.mean(pairwise_corrs)
                max_sync = np.max(pairwise_corrs)
                print(f"   • Mean pairwise correlation: {mean_sync:.4f}")
                print(f"   • Max pairwise correlation: {max_sync:.4f}")
                
                sync_level = "High" if mean_sync > 0.5 else "Medium" if mean_sync > 0.1 else "Low"
                print(f"   • Synchronization Level: {sync_level}")
    
    # === INPUT CORRELATION (if provided) ===
    if input_sequence is not None:
        print(f"\n📎 Input-State Correlation:")
        
        if input_sequence.ndim == 1:
            input_seq = input_sequence.reshape(-1, 1)
        else:
            input_seq = input_sequence
            
        M = input_seq.shape[1]
        
        for dim in range(min(M, 3)):  # Analyze first 3 input dimensions
            input_dim = input_seq[:, dim]
            
            # Correlation with mean activity
            if len(input_dim) == len(mean_activity):
                corr = np.corrcoef(input_dim, mean_activity)[0, 1]
                if not np.isnan(corr):
                    print(f"   • Input dim {dim} vs mean activity: {corr:.4f}")
    
    print("\n" + "="*70)

def print_performance_statistics(predictions: np.ndarray, 
                                targets: np.ndarray,
                                training_time: Optional[float] = None,
                                detailed: bool = True) -> None:
    """
    📈 Print Comprehensive Performance Statistics
    
    Provides detailed statistical analysis of model performance including
    accuracy metrics, error distributions, and comparative assessments.
    
    Args:
        predictions: Model predictions (T×D array)
        targets: Target values (T×D array)
        training_time: Training time in seconds, optional
        detailed: Whether to print detailed analysis
        
    Research Background:
    ===================
    Performance evaluation standards based on machine learning and
    reservoir computing benchmarking literature.
    """
    # Ensure proper shapes
    predictions = np.asarray(predictions)
    targets = np.asarray(targets)
    
    if predictions.ndim == 1:
        predictions = predictions.reshape(-1, 1)
    if targets.ndim == 1:
        targets = targets.reshape(-1, 1)
        
    T, D = predictions.shape
    
    print("\n" + "="*70)
    print("📈  PERFORMANCE STATISTICAL ANALYSIS")
    print("="*70)
    
    # === BASIC PROPERTIES ===
    print(f"\n📏 Basic Properties:")
    print(f"   • Prediction Length: {T:,} time steps")
    print(f"   • Output Dimensions: {D}")
    if training_time is not None:
        print(f"   • Training Time: {training_time:.2f} seconds")
        print(f"   • Prediction Rate: {T/training_time:.1f} samples/second")
    
    # === PERFORMANCE METRICS ===
    mse = mean_squared_error(targets, predictions)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(targets, predictions)
    r2 = r2_score(targets, predictions)
    
    print(f"\n🎯 Performance Metrics:")
    print(f"   • Mean Squared Error (MSE): {mse:.6f}")
    print(f"   • Root Mean Squared Error (RMSE): {rmse:.6f}")
    print(f"   • Mean Absolute Error (MAE): {mae:.6f}")
    print(f"   • R² Score: {r2:.6f}")
    
    # Performance assessment
    performance_level = assess_performance_level(r2)
    print(f"   • Performance Level: {performance_level}")
    
    # === ERROR ANALYSIS ===
    errors = predictions - targets
    errors_flat = errors.flatten()
    
    print(f"\n⚠️ Error Analysis:")
    print(f"   • Error Mean: {np.mean(errors_flat):.6f}")
    print(f"   • Error Std: {np.std(errors_flat):.6f}")
    print(f"   • Error Range: [{np.min(errors_flat):.4f}, {np.max(errors_flat):.4f}]")
    print(f"   • Max Absolute Error: {np.max(np.abs(errors_flat)):.6f}")
    
    # Error distribution analysis
    try:
        error_sample = errors_flat[:min(5000, len(errors_flat))]
        shapiro_stat, shapiro_p = stats.shapiro(error_sample)
        print(f"   • Error Normality (Shapiro-Wilk): p={shapiro_p:.4f} {'(Normal)' if shapiro_p > 0.05 else '(Non-normal)'}")
        
        # Bias test (one-sample t-test against zero mean)
        t_stat, t_p = stats.ttest_1samp(error_sample, 0)
        print(f"   • Bias Test (t-test): p={t_p:.4f} {'(Unbiased)' if t_p > 0.05 else '(Biased)'}")
    except:
        print(f"   • Statistical tests: Failed")
    
    if detailed and D > 1:
        # === PER-DIMENSION ANALYSIS ===
        print(f"\n🕵️ Per-Dimension Analysis:")
        
        for d in range(min(D, 5)):  # Analyze first 5 dimensions
            dim_mse = mean_squared_error(targets[:, d], predictions[:, d])
            dim_r2 = r2_score(targets[:, d], predictions[:, d])
            dim_mae = mean_absolute_error(targets[:, d], predictions[:, d])
            
            print(f"   • Dimension {d}:")
            print(f"     - MSE: {dim_mse:.6f}")
            print(f"     - R²: {dim_r2:.6f}")
            print(f"     - MAE: {dim_mae:.6f}")
    
    # === PREDICTION QUALITY ASSESSMENT ===
    if detailed:
        print(f"\n🎯 Prediction Quality Assessment:")
        
        # Calculate prediction intervals
        percentiles = [5, 25, 50, 75, 95]
        error_percentiles = np.percentile(np.abs(errors_flat), percentiles)
        
        print(f"   • Absolute Error Percentiles:")
        for p, val in zip(percentiles, error_percentiles):
            print(f"     - {p}th: {val:.6f}")
        
        # Outlier analysis
        q75, q25 = np.percentile(np.abs(errors_flat), [75, 25])
        iqr = q75 - q25
        outlier_threshold = q75 + 1.5 * iqr
        n_outliers = np.sum(np.abs(errors_flat) > outlier_threshold)
        
        print(f"   • Outliers (IQR method): {n_outliers} ({n_outliers/len(errors_flat)*100:.2f}%)")
    
    print("\n" + "="*70)

def assess_performance_level(r2_score: float) -> str:
    """
    🏆 Assess Performance Level Based on R² Score
    
    Args:
        r2_score: R-squared score
        
    Returns:
        str: Performance level description
    """
    if r2_score >= 0.9:
        return "Excellent (R² ≥ 0.9)"
    elif r2_score >= 0.8:
        return "Very Good (0.8 ≤ R² < 0.9)"
    elif r2_score >= 0.7:
        return "Good (0.7 ≤ R² < 0.8)"
    elif r2_score >= 0.5:
        return "Fair (0.5 ≤ R² < 0.7)"
    elif r2_score >= 0.0:
        return "Poor (0.0 ≤ R² < 0.5)"
    else:
        return "Very Poor (R² < 0.0)"

def assess_condition_number(condition_number: float) -> str:
    """
    🔢 Assess Matrix Condition Number
    
    Args:
        condition_number: Matrix condition number
        
    Returns:
        str: Condition assessment
    """
    if condition_number < 1e6:
        return "Well-conditioned (< 10⁶)"
    elif condition_number < 1e12:
        return "Moderately ill-conditioned (10⁶-10¹²)"
    elif condition_number < 1e16:
        return "Ill-conditioned (10¹²-10¹⁶)"
    else:
        return "Very ill-conditioned (> 10¹⁶)"

def assess_spectral_stability(eigenvals: np.ndarray) -> str:
    """
    🌌 Assess Spectral Stability of Reservoir
    
    Args:
        eigenvals: Array of eigenvalues
        
    Returns:
        str: Stability assessment
    """
    spectral_radius = np.max(np.abs(eigenvals))
    
    # Count eigenvalues outside unit circle
    outside_unit = np.sum(np.abs(eigenvals) > 1.0)
    
    if spectral_radius < 0.95:
        return f"Highly Stable (ρ={spectral_radius:.3f})"
    elif spectral_radius < 1.0:
        return f"Stable (ρ={spectral_radius:.3f})"
    elif spectral_radius < 1.05:
        return f"Marginally Stable (ρ={spectral_radius:.3f}, {outside_unit} eigs > 1)"
    elif spectral_radius < 1.2:
        return f"Unstable (ρ={spectral_radius:.3f}, {outside_unit} eigs > 1)"
    else:
        return f"Highly Unstable (ρ={spectral_radius:.3f}, {outside_unit} eigs > 1)"

# Export the main functions
__all__ = [
    'print_reservoir_statistics',
    'print_dynamics_statistics', 
    'print_performance_statistics',
    'assess_performance_level',
    'assess_condition_number',
    'assess_spectral_stability'
]
