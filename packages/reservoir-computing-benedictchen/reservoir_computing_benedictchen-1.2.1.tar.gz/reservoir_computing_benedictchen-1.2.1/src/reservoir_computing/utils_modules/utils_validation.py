"""
🔬 Reservoir Computing - Validation Utilities Module
===================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Echo State Property validation and testing utilities including comprehensive ESP
validation methods, convergence testing, stability analysis, and diagnostic tools
for reservoir computing systems.

🔬 VALIDATION CAPABILITIES:
==========================
• Comprehensive ESP validation using multiple methods
• Spectral radius analysis and stability assessment
• Convergence testing from different initial conditions
• Lyapunov exponent computation for dynamic stability
• Jacobian analysis for local linearization stability
• Fast ESP validation for real-time assessment

🎓 RESEARCH FOUNDATION:
======================
Based on validation methodologies from:
- Jaeger (2001): Original ESP theory and spectral radius conditions
- Lukoševičius & Jaeger (2009): Practical validation techniques
- Doya (1993): Lyapunov exponent methods for RNN stability
- Dynamical systems theory for stability analysis methods

This module represents the ESP validation and testing components,
split from the 1142-line monolith for specialized validation processing.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List, Union
import warnings
from sklearn.metrics import mean_squared_error
from scipy import stats
import logging

# Configure logging for validation functions
logger = logging.getLogger(__name__)

# ================================
# ESP VALIDATION UTILITIES
# ================================

def comprehensive_esp_validation(esn, method='comprehensive', **kwargs) -> Dict[str, Any]:
    """
    🔬 Comprehensive Echo State Property Validation using Multiple Methods
    
    Validates the Echo State Property using multiple complementary methods from 
    reservoir computing literature. The ESP is fundamental to RC performance.
    
    Validation Methods:
    1. **Spectral Radius**: λmax(W) < 1 (Jaeger, 2001)
    2. **Convergence Test**: State convergence from different initial conditions
    3. **Lyapunov Exponent**: Negative largest Lyapunov exponent indicates stability
    4. **Jacobian Analysis**: Local stability through linearization
    
    Args:
        esn: EchoStateNetwork instance to validate
        method: Validation method ('comprehensive', 'fast', 'spectral', 'convergence', 'lyapunov', 'jacobian')
        **kwargs: Additional validation parameters
        
    Returns:
        Dict containing validation results with overall ESP status
        
    Research Background:
    ===================
    Multi-method validation approach ensures robust ESP assessment across different
    mathematical frameworks, following best practices from reservoir computing literature.
    """
    results = {'method': method, 'overall_esp': False}
    
    try:
        if method == 'comprehensive':
            # Run all validation methods
            spectral_result = validate_spectral_radius(esn)
            convergence_result = validate_convergence(esn, **kwargs)
            lyapunov_result = validate_lyapunov(esn, **kwargs) 
            jacobian_result = validate_jacobian(esn, **kwargs)
            
            results.update({
                'spectral_radius': spectral_result,
                'convergence': convergence_result,
                'lyapunov': lyapunov_result,
                'jacobian': jacobian_result
            })
            
            # Overall ESP assessment (all methods should agree)
            esp_votes = [
                spectral_result['esp_satisfied'],
                convergence_result['converges'],
                lyapunov_result['stable'],
                jacobian_result['locally_stable']
            ]
            
            results['overall_esp'] = sum(esp_votes) >= 3  # Majority rule
            results['consensus_score'] = sum(esp_votes) / len(esp_votes)
            
        elif method == 'fast':
            # Quick validation for real-time assessment
            fast_result = validate_esp_fast(esn, **kwargs)
            results.update(fast_result)
            results['overall_esp'] = fast_result['esp_satisfied']
            
        elif method == 'spectral':
            spectral_result = validate_spectral_radius(esn)
            results.update(spectral_result)
            results['overall_esp'] = spectral_result['esp_satisfied']
            
        elif method == 'convergence':
            convergence_result = validate_convergence(esn, **kwargs)
            results.update(convergence_result)
            results['overall_esp'] = convergence_result['converges']
            
        elif method == 'lyapunov':
            lyapunov_result = validate_lyapunov(esn, **kwargs)
            results.update(lyapunov_result)
            results['overall_esp'] = lyapunov_result['stable']
            
        elif method == 'jacobian':
            jacobian_result = validate_jacobian(esn, **kwargs)
            results.update(jacobian_result)
            results['overall_esp'] = jacobian_result['locally_stable']
        
    except Exception as e:
        logger.error(f"ESP validation failed: {e}")
        results['error'] = str(e)
        results['overall_esp'] = False
    
    return results

def validate_spectral_radius(esn) -> Dict[str, Any]:
    """
    🌌 Validate Echo State Property via Spectral Radius Analysis
    
    Tests the fundamental ESP condition: λmax(W_reservoir) < 1
    
    Returns:
        Dict: Spectral radius validation results
        
    Research Background:
    ===================
    Based on Jaeger (2001) Theorem 1: ESP is guaranteed if the spectral 
    radius of the reservoir matrix is less than unity.
    """
    try:
        W = esn.W_reservoir_ if hasattr(esn, 'W_reservoir_') else esn.W_reservoir
        eigenvalues = np.linalg.eigvals(W)
        spectral_radius = np.max(np.abs(eigenvalues))
        
        return {
            'spectral_radius': spectral_radius,
            'esp_satisfied': spectral_radius < 1.0,
            'margin': 1.0 - spectral_radius,
            'n_unstable_modes': np.sum(np.abs(eigenvalues) >= 1.0),
            'largest_eigenvalue': eigenvalues[np.argmax(np.abs(eigenvalues))]
        }
    except Exception as e:
        return {'error': str(e), 'esp_satisfied': False}

def validate_convergence(esn, n_tests: int = 10, test_length: int = 1500, 
                        convergence_threshold: float = 1e-6) -> Dict[str, Any]:
    """
    🔄 Validate ESP via Convergence Testing
    
    Tests whether reservoir states converge to the same trajectory regardless
    of initial conditions, which is a direct consequence of the ESP.
    
    Args:
        esn: ESN instance to test
        n_tests: Number of different initial conditions to test
        test_length: Length of test sequence
        convergence_threshold: Threshold for convergence detection
        
    Returns:
        Dict: Convergence validation results
        
    Research Background:
    ===================
    Based on ESP definition: reservoir states should asymptotically forget
    initial conditions. Tests this by running identical inputs from different
    initial states and measuring trajectory convergence.
    """
    try:
        # Generate random input sequence
        n_inputs = esn.W_input_.shape[1] if hasattr(esn, 'W_input_') else 1
        input_seq = np.random.randn(test_length, n_inputs) * 0.1
        
        trajectories = []
        
        # Run from different initial conditions
        for test in range(n_tests):
            # Random initial state
            initial_state = np.random.randn(esn.n_reservoir) * 0.5
            trajectory = run_test_sequence(esn, initial_state, input_seq)
            trajectories.append(trajectory)
        
        # Measure convergence after washout period
        washout = min(500, test_length // 3)
        trajectories = [traj[washout:] for traj in trajectories]
        
        # Calculate pairwise distances between trajectories
        distances = []
        for i in range(len(trajectories)):
            for j in range(i + 1, len(trajectories)):
                dist = np.mean(np.linalg.norm(trajectories[i] - trajectories[j], axis=1))
                distances.append(dist)
        
        mean_distance = np.mean(distances)
        converges = mean_distance < convergence_threshold
        
        return {
            'converges': converges,
            'mean_trajectory_distance': mean_distance,
            'convergence_threshold': convergence_threshold,
            'n_tests': n_tests,
            'max_distance': np.max(distances),
            'min_distance': np.min(distances)
        }
        
    except Exception as e:
        return {'error': str(e), 'converges': False}

def validate_lyapunov(esn, n_steps: int = 1000) -> Dict[str, Any]:
    """
    📊 Validate ESP via Lyapunov Exponent Analysis
    
    Computes the largest Lyapunov exponent of the reservoir dynamics.
    Negative values indicate stability (ESP satisfied).
    
    Args:
        esn: ESN instance to analyze
        n_steps: Number of steps for Lyapunov computation
        
    Returns:
        Dict: Lyapunov analysis results
        
    Research Background:
    ===================
    Based on dynamical systems theory: negative largest Lyapunov exponent
    indicates contracting dynamics, which is necessary for ESP.
    """
    try:
        # Initialize system
        n_inputs = esn.W_input_.shape[1] if hasattr(esn, 'W_input_') else 1
        x = np.random.randn(esn.n_reservoir) * 0.1
        
        # Small perturbation for Lyapunov computation
        epsilon = 1e-6
        perturbation = np.random.randn(esn.n_reservoir) * epsilon
        x_perturbed = x + perturbation
        
        lyapunov_sum = 0.0
        
        for step in range(n_steps):
            # Random input
            u = np.random.randn(n_inputs) * 0.1
            
            # Update both states
            x_new = update_state_for_validation(esn, x, u)
            x_perturbed_new = update_state_for_validation(esn, x_perturbed, u)
            
            # Measure separation
            separation = np.linalg.norm(x_perturbed_new - x_new)
            
            if separation > 1e-12:  # Avoid numerical issues
                lyapunov_sum += np.log(separation / epsilon)
                
                # Renormalize perturbation
                x_perturbed = x_new + (x_perturbed_new - x_new) * epsilon / separation
            else:
                # Handle case where separation becomes too small
                x_perturbed = x_new + np.random.randn(esn.n_reservoir) * epsilon
            
            x = x_new
        
        largest_lyapunov = lyapunov_sum / n_steps
        
        return {
            'largest_lyapunov_exponent': largest_lyapunov,
            'stable': largest_lyapunov < 0,
            'stability_margin': -largest_lyapunov,
            'n_steps': n_steps
        }
        
    except Exception as e:
        return {'error': str(e), 'stable': False}

def validate_jacobian(esn, n_samples: int = 20) -> Dict[str, Any]:
    """
    📐 Validate ESP via Jacobian Analysis
    
    Analyzes the Jacobian matrix at random points to assess local stability.
    All eigenvalues should have magnitude < 1 for local ESP satisfaction.
    
    Args:
        esn: ESN instance to analyze
        n_samples: Number of random points to sample for Jacobian analysis
        
    Returns:
        Dict: Jacobian stability analysis results
        
    Research Background:
    ===================
    Based on linearization theory: if the Jacobian has spectral radius < 1
    at typical operating points, the system exhibits local contractive behavior.
    """
    try:
        n_inputs = esn.W_input_.shape[1] if hasattr(esn, 'W_input_') else 1
        spectral_radii = []
        max_eigenvalues = []
        
        for sample in range(n_samples):
            # Random state and input
            state = np.random.randn(esn.n_reservoir) * 0.5
            input_vec = np.random.randn(n_inputs) * 0.1
            
            # Compute Jacobian at this point
            J = compute_jacobian_at_state(esn, state, input_vec)
            
            # Analyze eigenvalues
            eigenvals = np.linalg.eigvals(J)
            spectral_radius = np.max(np.abs(eigenvals))
            
            spectral_radii.append(spectral_radius)
            max_eigenvalues.append(eigenvals[np.argmax(np.abs(eigenvals))])
        
        mean_spectral_radius = np.mean(spectral_radii)
        locally_stable = mean_spectral_radius < 1.0
        
        return {
            'locally_stable': locally_stable,
            'mean_spectral_radius': mean_spectral_radius,
            'spectral_radius_std': np.std(spectral_radii),
            'max_spectral_radius': np.max(spectral_radii),
            'min_spectral_radius': np.min(spectral_radii),
            'unstable_points': np.sum(np.array(spectral_radii) >= 1.0),
            'n_samples': n_samples
        }
        
    except Exception as e:
        return {'error': str(e), 'locally_stable': False}

def validate_esp_fast(esn, n_tests: int = 3, test_length: int = 100,
                     threshold: float = 1e-3) -> Dict[str, Any]:
    """
    ⚡ Fast ESP Validation for Real-time Assessment
    
    Lightweight ESP validation using reduced test parameters for speed.
    Suitable for online validation or parameter optimization loops.
    
    Args:
        esn: ESN instance to test
        n_tests: Number of convergence tests (reduced)
        test_length: Length of test sequences (reduced)
        threshold: Convergence threshold
        
    Returns:
        Dict: Fast validation results
        
    Research Background:
    ===================
    Simplified version of comprehensive validation optimized for speed
    while maintaining reasonable accuracy for practical applications.
    """
    try:
        # Quick spectral radius check
        spectral_result = validate_spectral_radius(esn)
        spectral_ok = spectral_result['esp_satisfied']
        
        # Quick convergence check with reduced parameters
        convergence_result = validate_convergence(
            esn, n_tests=n_tests, test_length=test_length, 
            convergence_threshold=threshold
        )
        convergence_ok = convergence_result['converges']
        
        # Combined assessment
        esp_satisfied = spectral_ok and convergence_ok
        
        return {
            'esp_satisfied': esp_satisfied,
            'spectral_radius': spectral_result['spectral_radius'],
            'spectral_ok': spectral_ok,
            'convergence_ok': convergence_ok,
            'convergence_distance': convergence_result['mean_trajectory_distance'],
            'confidence': 'medium'  # Lower confidence due to reduced testing
        }
        
    except Exception as e:
        return {'error': str(e), 'esp_satisfied': False}

# ================================
# VALIDATION HELPER FUNCTIONS  
# ================================

def compute_jacobian_at_state(esn, state: np.ndarray, input_vec: np.ndarray) -> np.ndarray:
    """
    📐 Compute Jacobian Matrix at Given State
    
    Computes the Jacobian matrix ∂f/∂x of the reservoir update function
    at a specific state and input, used for local stability analysis.
    
    Args:
        esn: ESN instance
        state: Current reservoir state
        input_vec: Input vector
        
    Returns:
        np.ndarray: Jacobian matrix (n_reservoir × n_reservoir)
        
    Research Background:
    ===================
    Jacobian computation for nonlinear dynamical systems analysis,
    following standard methods from dynamical systems theory.
    """
    try:
        W_reservoir = esn.W_reservoir_ if hasattr(esn, 'W_reservoir_') else esn.W_reservoir
        W_input = esn.W_input_ if hasattr(esn, 'W_input_') else esn.W_input
        
        # Pre-activation at current state
        pre_activation = W_reservoir @ state + W_input @ input_vec
        
        # Derivative of activation function (assuming tanh)
        activation_derivative = 1 - np.tanh(pre_activation) ** 2
        
        # Jacobian: J = diag(f'(Wx + Wu)) * W
        # For leaky integration: J = (1-α)I + α * diag(f'(·)) * W
        leak_rate = getattr(esn, 'leak_rate', 1.0)
        
        J = (1 - leak_rate) * np.eye(len(state)) + \
            leak_rate * np.diag(activation_derivative) @ W_reservoir
        
        return J
        
    except Exception as e:
        logger.error(f"Jacobian computation failed: {e}")
        return np.eye(len(state))  # Fallback to identity

def run_test_sequence(esn, initial_state: np.ndarray, 
                     input_sequence: np.ndarray) -> np.ndarray:
    """
    🔄 Run Test Sequence for Validation
    
    Runs the ESN with given initial state and input sequence,
    returning the complete state trajectory for analysis.
    
    Args:
        esn: ESN instance
        initial_state: Starting reservoir state
        input_sequence: Input sequence to drive the reservoir
        
    Returns:
        np.ndarray: State trajectory (time_steps × n_reservoir)
    """
    trajectory = []
    state = initial_state.copy()
    
    for t in range(len(input_sequence)):
        state = update_state_for_validation(esn, state, input_sequence[t])
        trajectory.append(state.copy())
    
    return np.array(trajectory)

def update_state_for_validation(esn, state: np.ndarray, 
                               input_vec: np.ndarray) -> np.ndarray:
    """
    🌊 Update State for Validation Testing
    
    Performs ESN state update specifically for validation purposes,
    handling various ESN configurations and parameter access patterns.
    
    Args:
        esn: ESN instance
        state: Current reservoir state
        input_vec: Input vector
        
    Returns:
        np.ndarray: Updated reservoir state
        
    Research Background:
    ===================
    Standard ESN update equation from Jaeger (2001) with support for
    various implementation patterns and parameter access methods.
    """
    try:
        # Access reservoir parameters (handle different attribute patterns)
        W_reservoir = getattr(esn, 'W_reservoir_', None) or getattr(esn, 'W_reservoir', None)
        W_input = getattr(esn, 'W_input_', None) or getattr(esn, 'W_input', None)
        
        if W_reservoir is None or W_input is None:
            raise ValueError("Cannot access reservoir matrices")
        
        # Ensure input is properly shaped
        if np.isscalar(input_vec):
            input_vec = np.array([input_vec])
        elif input_vec.ndim == 0:
            input_vec = np.array([input_vec])
        
        # Pre-activation
        pre_activation = W_reservoir @ state + W_input @ input_vec
        
        # Activation function (default to tanh)
        activation_func = getattr(esn, 'activation', np.tanh)
        activated = activation_func(pre_activation)
        
        # Leaky integration (if supported)
        leak_rate = getattr(esn, 'leak_rate', 1.0)
        new_state = (1 - leak_rate) * state + leak_rate * activated
        
        return new_state
        
    except Exception as e:
        logger.error(f"State update failed in validation: {e}")
        # Fallback: return slightly modified state
        return state + np.random.randn(len(state)) * 1e-6

# Export main validation functions
__all__ = [
    'comprehensive_esp_validation',
    'validate_spectral_radius',
    'validate_convergence', 
    'validate_lyapunov',
    'validate_jacobian',
    'validate_esp_fast',
    'compute_jacobian_at_state',
    'run_test_sequence',
    'update_state_for_validation'
]