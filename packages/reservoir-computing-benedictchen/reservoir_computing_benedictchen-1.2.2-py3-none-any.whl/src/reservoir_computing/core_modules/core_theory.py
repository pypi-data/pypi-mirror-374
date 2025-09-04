"""
🧠 Reservoir Computing - Core Theory Module
==========================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Mathematical theory and theoretical foundations for reservoir computing including
Echo State Property validation, memory capacity theory, spectral analysis,
and core theoretical principles from Jaeger (2001) and Maass (2002).

🔬 THEORETICAL FOUNDATIONS:
==========================
• Echo State Property (ESP) conditions and validation
• Memory capacity theory and measurement
• Spectral radius bounds and stability analysis
• Reservoir dynamics mathematical framework
• Theoretical performance bounds and analysis
• Advanced theoretical validation methods

🎓 RESEARCH FOUNDATION:
======================
Based on foundational theoretical work from:
- Jaeger (2001): Echo State Property and theoretical foundations
- Maass (2002): Real-time computing without stable states
- Lukoševičius & Jaeger (2009): Theoretical survey and analysis
- Verstraeten et al. (2007): Memory capacity theory
- Mathematical foundations from dynamical systems theory

This module represents the core mathematical theory components,
split from the 1405-line monolith for specialized theoretical analysis.
"""

import numpy as np
import scipy.sparse as sp
from scipy import linalg, optimize
from typing import Optional, Dict, Any, Tuple, List
import warnings
from abc import ABC

# ============================================================================
# CORE RESERVOIR COMPUTING THEORY - Mathematical Foundation
# ============================================================================

class ReservoirTheoryMixin(ABC):
    """
    🧠 Core Mathematical Theory for Reservoir Computing
    
    Implements the fundamental equations from Jaeger (2001) and Maass (2002):
    - Echo State Property conditions
    - Reservoir dynamics equations  
    - Memory capacity theory
    - Spectral radius bounds
    """
    
    def verify_echo_state_property(self, W_reservoir: np.ndarray, 
                                  spectral_radius_threshold: float = 1.0,
                                  verbose: bool = True) -> Dict[str, Any]:
        """
        🔍 Verify Echo State Property (ESP) Conditions
        
        The ESP ensures that the reservoir state asymptotically forgets
        initial conditions, enabling stable temporal processing.
        
        Mathematical Condition:
        The largest eigenvalue of W_reservoir must have |λ_max| < 1
        
        Args:
            W_reservoir: Reservoir weight matrix
            spectral_radius_threshold: Maximum allowed spectral radius
            verbose: Whether to print validation results
            
        Returns:
            Dict[str, Any]: ESP validation results
            
        Research Background:
        ===================
        Based on Echo State Property theory from Jaeger (2001) Section 3,
        providing mathematical conditions for reservoir stability and memory.
        """
        # FIXME: Critical efficiency and numerical stability issues in ESP validation
        # Issue 1: Full eigendecomposition is O(n³) - extremely slow for large reservoirs
        # Issue 2: No input validation for matrix properties
        # Issue 3: Complex eigenvalues not handled properly for non-symmetric matrices
        # Issue 4: No caching of expensive eigenvalue computation
        # Issue 5: Missing alternative ESP conditions for special matrix structures
        
        # FIXME: No input validation for reservoir matrix
        # Issue: Could crash with invalid inputs (NaN, Inf, wrong dimensions)
        # Solutions:
        # 1. Validate matrix is square and finite
        # 2. Check for degenerate cases (zero matrix, identity matrix)
        # 3. Add warnings for very large matrices that will be slow
        
        results = {}
        
        try:
            # Input validation
            if W_reservoir.shape[0] != W_reservoir.shape[1]:
                raise ValueError("Reservoir matrix must be square")
            
            if not np.all(np.isfinite(W_reservoir)):
                raise ValueError("Reservoir matrix must contain finite values")
            
            # Calculate eigenvalues
            eigenvalues = linalg.eigvals(W_reservoir)
            spectral_radius = np.max(np.abs(eigenvalues))
            
            # ESP condition check
            esp_satisfied = spectral_radius < spectral_radius_threshold
            
            # Additional theoretical metrics
            max_real_eigenval = np.max(np.real(eigenvalues))
            complex_eigenvals = np.sum(np.abs(np.imag(eigenvalues)) > 1e-10)
            
            results = {
                'esp_satisfied': esp_satisfied,
                'spectral_radius': spectral_radius,
                'threshold': spectral_radius_threshold,
                'eigenvalues': eigenvalues,
                'max_real_eigenvalue': max_real_eigenval,
                'complex_eigenvalues': complex_eigenvals,
                'matrix_size': W_reservoir.shape[0],
                'condition_number': np.linalg.cond(W_reservoir),
                'determinant': np.linalg.det(W_reservoir),
                'trace': np.trace(W_reservoir),
                'frobenius_norm': np.linalg.norm(W_reservoir, 'fro')
            }
            
            if verbose:
                self._print_esp_results(results)
                
        except Exception as e:
            results = {
                'esp_satisfied': False,
                'error': str(e),
                'spectral_radius': np.inf
            }
            if verbose:
                print(f"❌ ESP Validation failed: {e}")
        
        return results
    
    def compute_memory_capacity(self, reservoir_states: np.ndarray, 
                              input_sequence: np.ndarray,
                              max_delay: Optional[int] = None,
                              verbose: bool = True) -> Dict[str, Any]:
        """
        📊 Compute Linear Memory Capacity of Reservoir
        
        Memory capacity measures the reservoir's ability to linearly reconstruct
        delayed versions of the input signal from current reservoir states.
        
        Mathematical Definition:
        MC_k = max_w |corr(u(n-k), w^T * x(n))|²
        Total MC = Σ MC_k for k = 0, 1, 2, ...
        
        Args:
            reservoir_states: Reservoir state matrix (T × N)
            input_sequence: Input signal (T × d)
            max_delay: Maximum delay to test (default: min(T//4, 50))
            verbose: Whether to print results
            
        Returns:
            Dict[str, Any]: Memory capacity analysis results
            
        Research Background:
        ===================
        Based on linear memory capacity theory from Jaeger (2001) Section 4.1.2
        and extended analysis methods from Verstraeten et al. (2007).
        """
        # FIXME: Critical implementation gaps in memory capacity computation
        # Issue 1: No handling of multivariate input sequences
        # Issue 2: Ridge regression regularization parameter not optimized
        # Issue 3: Missing statistical significance testing for memory coefficients
        # Issue 4: No validation of input/state alignment and causality
        # Issue 5: Memory capacity bounds not computed or validated
        
        # FIXME: Input validation missing
        # Issue: No checks for compatible dimensions, finite values, sufficient data
        # Solutions:
        # 1. Validate reservoir_states and input_sequence have same time dimension
        # 2. Check for sufficient data points relative to reservoir size
        # 3. Validate finite values and reasonable magnitudes
        
        T, N = reservoir_states.shape
        
        # Input validation
        if input_sequence.shape[0] != T:
            raise ValueError("Input sequence and reservoir states must have same time dimension")
        
        # Handle multivariate input
        if input_sequence.ndim == 1:
            input_sequence = input_sequence.reshape(-1, 1)
        
        input_dim = input_sequence.shape[1]
        
        if max_delay is None:
            max_delay = min(T // 4, 50)
        
        # Ensure we have enough data
        max_delay = min(max_delay, T - 1)
        
        memory_capacities = []
        correlation_coefficients = []
        reconstruction_errors = []
        
        for delay in range(max_delay + 1):
            if delay >= T:
                break
                
            # Extract delayed input and corresponding states
            delayed_input = input_sequence[:-delay] if delay > 0 else input_sequence
            current_states = reservoir_states[delay:]
            
            if len(delayed_input) < N:  # Not enough data for stable regression
                break
            
            # Compute memory capacity for each input dimension
            delay_mc = 0.0
            delay_corrs = []
            delay_errors = []
            
            for d in range(input_dim):
                try:
                    # Use ridge regression to find optimal readout weights
                    from sklearn.linear_model import Ridge
                    ridge = Ridge(alpha=1e-6, fit_intercept=False)
                    ridge.fit(current_states, delayed_input[:, d])
                    
                    # Predict delayed input from reservoir states
                    predicted = ridge.predict(current_states)
                    
                    # Calculate memory capacity (squared correlation)
                    correlation = np.corrcoef(delayed_input[:, d], predicted)[0, 1]
                    if np.isfinite(correlation):
                        mc_k = correlation ** 2
                        delay_mc += mc_k
                        delay_corrs.append(correlation)
                        delay_errors.append(np.mean((delayed_input[:, d] - predicted) ** 2))
                    
                except Exception as e:
                    if verbose:
                        print(f"⚠️ Warning: Memory capacity computation failed for delay {delay}, dim {d}: {e}")
                    continue
            
            memory_capacities.append(delay_mc / input_dim)  # Average across input dimensions
            correlation_coefficients.append(np.mean(delay_corrs) if delay_corrs else 0.0)
            reconstruction_errors.append(np.mean(delay_errors) if delay_errors else np.inf)
        
        # Calculate total memory capacity
        total_memory_capacity = np.sum(memory_capacities)
        
        # Theoretical upper bound (Jaeger 2001): MC ≤ N (reservoir size)
        theoretical_bound = N
        efficiency = total_memory_capacity / theoretical_bound
        
        results = {
            'total_memory_capacity': total_memory_capacity,
            'memory_capacity_per_delay': memory_capacities,
            'correlation_coefficients': correlation_coefficients,
            'reconstruction_errors': reconstruction_errors,
            'max_delay_tested': len(memory_capacities) - 1,
            'theoretical_bound': theoretical_bound,
            'efficiency': efficiency,
            'reservoir_size': N,
            'sequence_length': T,
            'input_dimensions': input_dim
        }
        
        if verbose:
            self._print_memory_capacity_results(results)
        
        return results
    
    def analyze_reservoir_dynamics(self, W_reservoir: np.ndarray,
                                 W_input: Optional[np.ndarray] = None,
                                 input_sequence: Optional[np.ndarray] = None,
                                 verbose: bool = True) -> Dict[str, Any]:
        """
        🔬 Comprehensive Reservoir Dynamics Analysis
        
        Analyzes the theoretical properties of reservoir dynamics including
        stability, controllability, observability, and dynamic range.
        
        Args:
            W_reservoir: Reservoir weight matrix
            W_input: Input weight matrix (optional)
            input_sequence: Sample input sequence for analysis (optional)
            verbose: Whether to print analysis results
            
        Returns:
            Dict[str, Any]: Comprehensive dynamics analysis
            
        Research Background:
        ===================
        Based on dynamical systems analysis methods applied to reservoir computing
        from theoretical foundations in Jaeger (2001) and control theory literature.
        """
        results = {}
        
        # Basic spectral analysis
        eigenvals = linalg.eigvals(W_reservoir)
        spectral_radius = np.max(np.abs(eigenvals))
        
        # Stability analysis
        stable_eigenvals = np.sum(np.abs(eigenvals) < 1.0)
        marginally_stable = np.sum(np.abs(eigenvals - 1.0) < 1e-6)
        unstable_eigenvals = np.sum(np.abs(eigenvals) > 1.0)
        
        # Spectral gap (important for mixing and convergence)
        sorted_eigenvals = np.sort(np.abs(eigenvals))[::-1]
        spectral_gap = sorted_eigenvals[0] - sorted_eigenvals[1] if len(sorted_eigenvals) > 1 else 0.0
        
        # Matrix conditioning
        condition_number = np.linalg.cond(W_reservoir)
        
        results.update({
            'spectral_radius': spectral_radius,
            'eigenvalues': eigenvals,
            'stable_eigenvals': stable_eigenvals,
            'marginally_stable_eigenvals': marginally_stable,
            'unstable_eigenvals': unstable_eigenvals,
            'spectral_gap': spectral_gap,
            'condition_number': condition_number,
            'matrix_rank': np.linalg.matrix_rank(W_reservoir),
            'determinant': np.linalg.det(W_reservoir)
        })
        
        # Advanced analysis if input matrix provided
        if W_input is not None:
            try:
                # Controllability analysis (simplified)
                n = W_reservoir.shape[0]
                m = W_input.shape[1]
                
                # Controllability matrix [W_input, W_reservoir*W_input, W_reservoir²*W_input, ...]
                controllability_matrix = W_input.copy()
                temp_matrix = W_input.copy()
                
                for i in range(min(n-1, 10)):  # Limit iterations for large matrices
                    temp_matrix = W_reservoir @ temp_matrix
                    controllability_matrix = np.hstack([controllability_matrix, temp_matrix])
                
                controllability_rank = np.linalg.matrix_rank(controllability_matrix)
                is_controllable = controllability_rank == n
                
                results.update({
                    'controllability_rank': controllability_rank,
                    'is_controllable': is_controllable,
                    'input_coupling_strength': np.linalg.norm(W_input, 'fro'),
                    'input_dimensions': m
                })
                
            except Exception as e:
                if verbose:
                    print(f"⚠️ Controllability analysis failed: {e}")
        
        # Dynamic range analysis if input sequence provided
        if input_sequence is not None and W_input is not None:
            try:
                # Simulate reservoir response
                n_steps = min(len(input_sequence), 100)  # Limit for efficiency
                states = np.zeros((n_steps, W_reservoir.shape[0]))
                x = np.zeros(W_reservoir.shape[0])
                
                for t in range(n_steps):
                    u = input_sequence[t] if input_sequence.ndim > 1 else [input_sequence[t]]
                    x = np.tanh(W_reservoir @ x + W_input @ u)
                    states[t] = x
                
                # Dynamic range metrics
                state_variance = np.var(states, axis=0)
                state_range = np.ptp(states, axis=0)  # Peak-to-peak
                activation_saturation = np.mean(np.abs(states) > 0.95)  # Fraction near saturation
                
                results.update({
                    'dynamic_range_variance': np.mean(state_variance),
                    'dynamic_range_spread': np.mean(state_range),
                    'activation_saturation': activation_saturation,
                    'effective_dimensionality': np.sum(state_variance > 0.01 * np.max(state_variance))
                })
                
            except Exception as e:
                if verbose:
                    print(f"⚠️ Dynamic range analysis failed: {e}")
        
        if verbose:
            self._print_dynamics_analysis(results)
        
        return results
    
    def _print_esp_results(self, results: Dict[str, Any]):
        """📊 Print Echo State Property validation results"""
        print("\n" + "="*60)
        print("🔍 ECHO STATE PROPERTY VALIDATION")
        print("="*60)
        
        if 'error' in results:
            print(f"❌ Validation Error: {results['error']}")
            return
        
        status = "✅ SATISFIED" if results['esp_satisfied'] else "❌ VIOLATED"
        print(f"ESP Status: {status}")
        print(f"Spectral Radius: {results['spectral_radius']:.6f}")
        print(f"Threshold: {results['threshold']:.6f}")
        print(f"Matrix Size: {results['matrix_size']}×{results['matrix_size']}")
        print(f"Complex Eigenvalues: {results['complex_eigenvals']}")
        print(f"Condition Number: {results['condition_number']:.2e}")
        print(f"Determinant: {results['determinant']:.6f}")
        print(f"Trace: {results['trace']:.6f}")
        print("="*60)
    
    def _print_memory_capacity_results(self, results: Dict[str, Any]):
        """📊 Print memory capacity analysis results"""
        print("\n" + "="*60)
        print("📊 LINEAR MEMORY CAPACITY ANALYSIS")
        print("="*60)
        
        print(f"Total Memory Capacity: {results['total_memory_capacity']:.4f}")
        print(f"Theoretical Upper Bound: {results['theoretical_bound']}")
        print(f"Efficiency: {results['efficiency']:.1%}")
        print(f"Max Delay Tested: {results['max_delay_tested']}")
        print(f"Reservoir Size: {results['reservoir_size']}")
        print(f"Sequence Length: {results['sequence_length']}")
        print(f"Input Dimensions: {results['input_dimensions']}")
        
        # Show memory capacity per delay (first 10)
        mc_per_delay = results['memory_capacity_per_delay'][:10]
        print(f"\nMemory Capacity by Delay (first 10):")
        for i, mc in enumerate(mc_per_delay):
            print(f"  Delay {i}: {mc:.4f}")
        
        print("="*60)
    
    def _print_dynamics_analysis(self, results: Dict[str, Any]):
        """📊 Print reservoir dynamics analysis results"""
        print("\n" + "="*60)
        print("🔬 RESERVOIR DYNAMICS ANALYSIS")
        print("="*60)
        
        print(f"Spectral Radius: {results['spectral_radius']:.6f}")
        print(f"Spectral Gap: {results['spectral_gap']:.6f}")
        print(f"Condition Number: {results['condition_number']:.2e}")
        print(f"Matrix Rank: {results['matrix_rank']}")
        
        print(f"\nEigenvalue Distribution:")
        print(f"  Stable (|λ| < 1): {results['stable_eigenvals']}")
        print(f"  Marginally Stable (|λ| ≈ 1): {results['marginally_stable_eigenvals']}")
        print(f"  Unstable (|λ| > 1): {results['unstable_eigenvals']}")
        
        if 'is_controllable' in results:
            status = "✅ Yes" if results['is_controllable'] else "❌ No"
            print(f"\nControllability: {status}")
            print(f"Controllability Rank: {results['controllability_rank']}")
            print(f"Input Coupling Strength: {results['input_coupling_strength']:.4f}")
        
        if 'dynamic_range_variance' in results:
            print(f"\nDynamic Range Analysis:")
            print(f"  State Variance: {results['dynamic_range_variance']:.6f}")
            print(f"  State Range: {results['dynamic_range_spread']:.6f}")
            print(f"  Activation Saturation: {results['activation_saturation']:.1%}")
            print(f"  Effective Dimensionality: {results['effective_dimensionality']}")
        
        print("="*60)

# Export the main class
__all__ = ['ReservoirTheoryMixin']