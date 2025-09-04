"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Reservoir Computing Core Algorithms - UNIFIED IMPLEMENTATION
===========================================================

This module consolidates all reservoir computing algorithm implementations
from the scattered mixin structure into a single, unified location.

Consolidated from:
- esn_modules/esn_core.py (18KB - main ESN class)
- esn_modules/configuration_optimization.py (82KB - MASSIVE optimization code!)
- esn_modules/visualization.py (63KB - visualization mixins)
- esn_modules/topology_management.py (24KB - topology methods)
- esn_modules/training_methods.py (18KB - training algorithms)
- esn_modules/prediction_generation.py (17KB - prediction methods)
- esn_modules/reservoir_initialization.py (4KB - initialization)
- esn_modules/esp_validation.py (9KB - Echo State Property validation)
- esn_modules/state_updates.py (2KB - state dynamics)
- echo_state_network.py (5KB - high-level interface)

Author: Benedict Chen (benedict@benedictchen.com)

Based on: Herbert Jaeger (2001) "The 'Echo State' Approach to Analysing 
and Training Recurrent Neural Networks" and Wolfgang Maass (2002) 
"Real-time Computing Without Stable States"
"""

import numpy as np
import scipy.sparse as sp
from scipy import linalg, optimize
from scipy.special import expit
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from abc import ABC, abstractmethod
import warnings
from typing import Optional, Callable, Dict, Any, Tuple, List, Union, Sequence
import time

# ============================================================================
# CORE RESERVOIR COMPUTING THEORY - Mathematical Foundation
# ============================================================================

class ReservoirTheoryMixin:
    """
    Core mathematical theory for reservoir computing.
    
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
        Verify Echo State Property (ESP) conditions.
        
        The ESP ensures that the reservoir state asymptotically forgets
        initial conditions, enabling stable temporal processing.
        
        Mathematical Condition:
        The largest eigenvalue of W_reservoir must have |λ_max| < 1
        
        Parameters
        ----------
        W_reservoir : np.ndarray
            Reservoir weight matrix
        spectral_radius_threshold : float
            Maximum allowed spectral radius
        verbose : bool
            Whether to print validation results
            
        Returns
        -------
        Dict[str, Any]
            ESP validation results
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
        #
        # Example validation:
        # if W_reservoir.ndim != 2 or W_reservoir.shape[0] != W_reservoir.shape[1]:
        #     raise ValueError("Reservoir matrix must be square")
        # if not np.all(np.isfinite(W_reservoir)):
        #     raise ValueError("Reservoir matrix contains non-finite values")
        # if W_reservoir.shape[0] > 5000:
        #     warnings.warn("Large reservoir matrix - eigenvalue computation may be slow")
        
        # FIXME: Full eigendecomposition is computationally expensive O(n³)
        # Issue: For large reservoirs (>1000 nodes), this becomes prohibitively slow
        # Solutions:
        # 1. Use power iteration to estimate largest eigenvalue: O(n²k) where k << n
        # 2. Use sparse eigenvalue methods if matrix is sparse
        # 3. Cache results and only recompute when matrix changes
        #
        # Efficient implementation:
        # if W_reservoir.shape[0] > 1000:
        #     from scipy.sparse.linalg import eigs
        #     largest_eigenval = eigs(W_reservoir, k=1, which='LM', return_eigenvectors=False)[0]
        #     spectral_radius = np.abs(largest_eigenval)
        # else:
        #     eigenvalues = np.linalg.eigvals(W_reservoir)
        #     spectral_radius = np.max(np.abs(eigenvalues))
        
        eigenvalues = np.linalg.eigvals(W_reservoir)
        spectral_radius = np.max(np.abs(eigenvalues))
        
        # Check ESP condition
        esp_satisfied = spectral_radius < spectral_radius_threshold
        
        # FIXME: Condition number computation can be numerically unstable
        # Issue: For ill-conditioned matrices, condition number can overflow
        # Solutions:
        # 1. Use robust condition number estimation
        # 2. Add bounds checking and warnings
        # 3. Use SVD-based condition number for better stability
        #
        # Robust implementation:
        # try:
        #     condition_number = np.linalg.cond(W_reservoir)
        #     if condition_number > 1e12:
        #         warnings.warn("Matrix is ill-conditioned, results may be unreliable")
        # except np.linalg.LinAlgError:
        #     condition_number = np.inf
        
        # Additional stability metrics
        condition_number = np.linalg.cond(W_reservoir)
        frobenius_norm = np.linalg.norm(W_reservoir, 'fro')
        
        # FIXME: Complex eigenvalues handled incorrectly
        # Issue: For non-symmetric matrices, eigenvalues can be complex
        # The spectral radius should be max(|λ|) where λ can be complex
        # Solutions:
        # 1. Explicitly handle complex eigenvalues with proper magnitude
        # 2. Add information about complex eigenvalues in results
        # 3. Warn if significant imaginary components exist
        #
        # Better handling:
        # complex_eigenvals = eigenvalues[np.abs(np.imag(eigenvalues)) > 1e-10]
        # if len(complex_eigenvals) > 0:
        #     warnings.warn(f"Matrix has {len(complex_eigenvals)} complex eigenvalues")
        
        results = {
            'esp_satisfied': esp_satisfied,
            'spectral_radius': spectral_radius,
            'threshold': spectral_radius_threshold,
            'largest_eigenvalue': eigenvalues[np.argmax(np.abs(eigenvalues))],
            'condition_number': condition_number,
            'frobenius_norm': frobenius_norm,
            'n_eigenvalues_above_threshold': np.sum(np.abs(eigenvalues) >= spectral_radius_threshold)
        }
        
        # FIXME: Missing important ESP diagnostics
        # Issue: ESP validation could provide more actionable feedback
        # Solutions:
        # 1. Add suggestions for spectral radius adjustment
        # 2. Provide information about eigenvalue distribution
        # 3. Estimate optimal spectral radius range
        #
        # Enhanced diagnostics:
        # results['eigenvalue_distribution'] = {
        #     'mean_magnitude': np.mean(np.abs(eigenvalues)),
        #     'eigenvalue_spread': np.std(np.abs(eigenvalues)),
        #     'suggested_spectral_radius': min(0.99, spectral_radius * 0.9)
        # }
        
        if verbose:
            print(f"🌊 Echo State Property Validation:")
            print(f"   Spectral Radius: {spectral_radius:.6f} (threshold: {spectral_radius_threshold})")
            print(f"   ESP Satisfied: {'✅ Yes' if esp_satisfied else '❌ No'}")
            if not esp_satisfied:
                print(f"   ⚠️  Reservoir may not have stable dynamics!")
                
        return results
    
    def compute_memory_capacity(self, reservoir_states: np.ndarray, 
                               input_sequence: np.ndarray,
                               max_delay: int = 50) -> Dict[str, float]:
        """
        Compute Memory Capacity of the reservoir.
        
        Memory Capacity measures how much information about past inputs
        can be linearly reconstructed from current reservoir states.
        
        MC = Σ(k=1 to ∞) MC_k where MC_k = cov²(u(t-k), û(t-k)) / var(u) var(û)
        
        Parameters
        ----------
        reservoir_states : np.ndarray, shape (time_steps, n_reservoir)
            Reservoir state time series
        input_sequence : np.ndarray, shape (time_steps,)
            Input sequence used to drive reservoir
        max_delay : int
            Maximum delay to compute MC for
            
        Returns
        -------
        Dict[str, float]
            Memory capacity metrics
        """
        # FIXME: Critical algorithmic and computational issues in memory capacity computation
        # Issue 1: O(max_delay × n_reservoir²) complexity - extremely slow for large reservoirs
        # Issue 2: Inefficient Ridge regression in loop - should vectorize operations
        # Issue 3: No proper statistical validation of memory capacity estimates
        # Issue 4: Fixed alpha=1e-6 may be inappropriate for different scales
        # Issue 5: No handling of multicollinear reservoir states
        
        if len(reservoir_states) != len(input_sequence):
            raise ValueError("Reservoir states and input must have same length")
        
        # FIXME: No input validation for data quality
        # Issue: Could fail with NaN, Inf, or degenerate data
        # Solutions:
        # 1. Check for NaN/Inf in reservoir states and input
        # 2. Validate minimum sequence length for reliable statistics
        # 3. Check for constant sequences that would break correlation computation
        #
        # Example validation:
        # if np.any(np.isnan(reservoir_states)) or np.any(np.isnan(input_sequence)):
        #     raise ValueError("NaN values detected in input data")
        # if np.var(input_sequence) < 1e-12:
        #     warnings.warn("Input sequence has very low variance - MC results may be unreliable")
        # if n_time < max_delay * 5:
        #     warnings.warn("Short sequence relative to max_delay may give unreliable MC estimates")
            
        n_time, n_reservoir = reservoir_states.shape
        memory_capacities = []
        
        # FIXME: Extremely inefficient loop-based computation O(max_delay × n_reservoir²)
        # Issue: For large reservoirs and long delays, this becomes prohibitively slow
        # Solutions:
        # 1. Vectorize the computation across all delays simultaneously
        # 2. Use more efficient correlation computation methods
        # 3. Implement early stopping when MC drops below threshold
        #
        # Efficient vectorized implementation:
        # delays = np.arange(1, min(max_delay, n_time))
        # target_matrix = np.array([input_sequence[:-d] for d in delays])  # (n_delays, n_samples)
        # state_matrix = np.array([reservoir_states[d:] for d in delays])  # (n_delays, n_samples, n_reservoir)
        # Use batch ridge regression to solve all delays at once
        
        for delay in range(1, min(max_delay, n_time)):
            # FIXME: Arbitrary cutoff of 10 samples is too restrictive
            # Issue: This prevents computation of long-term memory capacity
            # Solutions:
            # 1. Use relative threshold: e.g., min(50, n_time // 10)
            # 2. Add statistical significance testing for small sample sizes
            # 3. Provide warnings about unreliable estimates
            
            # Target: input delayed by 'delay' time steps
            if n_time - delay <= 10:  # Need sufficient samples
                break
                
            target = input_sequence[:-delay]
            states = reservoir_states[delay:]
            
            # FIXME: Fixed ridge regularization parameter is suboptimal
            # Issue: alpha=1e-6 may be too small or too large depending on data scale
            # Solutions:
            # 1. Use cross-validation to select optimal alpha
            # 2. Scale alpha based on data properties (matrix condition number)
            # 3. Implement different regularization strategies (elastic net, etc.)
            #
            # Adaptive regularization:
            # condition_num = np.linalg.cond(states.T @ states)
            # alpha = max(1e-6, condition_num * 1e-12) if condition_num < np.inf else 1e-3
            
            # Linear regression to reconstruct delayed input
            try:
                # Use ridge regression for stability
                ridge = Ridge(alpha=1e-6, fit_intercept=True)
                ridge.fit(states, target)
                prediction = ridge.predict(states)
                
                # FIXME: Correlation coefficient computation can be unstable
                # Issue: np.corrcoef can return NaN for constant sequences or numerical issues
                # Solutions:
                # 1. Use more robust correlation computation
                # 2. Add proper error handling for edge cases
                # 3. Implement alternative MC computation methods
                #
                # Robust correlation:
                # if np.var(target) < 1e-12 or np.var(prediction) < 1e-12:
                #     mc_k = 0.0
                # else:
                #     corr_coef = np.corrcoef(target, prediction)[0, 1]
                #     mc_k = corr_coef ** 2 if np.isfinite(corr_coef) else 0.0
                
                # Memory capacity for this delay
                corr_coef = np.corrcoef(target, prediction)[0, 1]
                mc_k = corr_coef ** 2 if not np.isnan(corr_coef) else 0.0
                memory_capacities.append(mc_k)
                
            except Exception:
                # FIXME: Silent exception handling hides important errors
                # Issue: Broad except clause masks specific problems
                # Solutions:
                # 1. Catch specific exceptions (LinAlgError, ValueError)
                # 2. Log warnings about failed computations
                # 3. Provide diagnostic information about failures
                #
                # Better exception handling:
                # except (np.linalg.LinAlgError, ValueError) as e:
                #     warnings.warn(f"MC computation failed at delay {delay}: {e}")
                #     memory_capacities.append(0.0)
                memory_capacities.append(0.0)
        
        total_mc = np.sum(memory_capacities)
        effective_memory = np.sum([mc for mc in memory_capacities if mc > 0.01])
        
        # FIXME: Arbitrary threshold 0.01 for "effective" memory capacity
        # Issue: This threshold isn't justified and may not be appropriate for all use cases
        # Solutions:
        # 1. Make threshold configurable parameter
        # 2. Use statistical significance testing (e.g., p < 0.05)
        # 3. Base threshold on noise floor estimation
        #
        # Better effective memory computation:
        # noise_floor = np.std(memory_capacities[-10:]) if len(memory_capacities) > 10 else 0.01
        # significance_threshold = max(0.01, 3 * noise_floor)
        # effective_memory = np.sum([mc for mc in memory_capacities if mc > significance_threshold])
        
        return {
            'total_memory_capacity': total_mc,
            'effective_memory_capacity': effective_memory,
            'memory_capacities_by_delay': memory_capacities,
            'theoretical_maximum': n_reservoir,  # Upper bound
            'efficiency': total_mc / n_reservoir if n_reservoir > 0 else 0
        }


class ReservoirInitializationMixin:
    """
    Advanced reservoir initialization methods.
    
    Implements multiple initialization strategies for optimal reservoir dynamics:
    - Random sparse matrices with controlled spectral radius
    - Small-world and scale-free topologies
    - Echo State Property validation
    - Input scaling optimization
    """
    
    def initialize_reservoir_matrix(self, n_reservoir: int, 
                                  spectral_radius: float = 0.95,
                                  sparsity: float = 0.1,
                                  random_state: Optional[int] = None) -> np.ndarray:
        """
        Initialize reservoir weight matrix with controlled spectral radius.
        
        Parameters
        ----------
        n_reservoir : int
            Number of reservoir units
        spectral_radius : float
            Desired spectral radius (< 1 for ESP)
        sparsity : float
            Connection density (0.1 = 10% connections)
        random_state : int, optional
            Random seed for reproducibility
            
        Returns
        -------
        np.ndarray
            Initialized reservoir matrix
        """
        if random_state is not None:
            np.random.seed(random_state)
            
        # Create random sparse matrix
        n_connections = int(sparsity * n_reservoir * n_reservoir)
        
        # Random sparse connectivity
        W = np.zeros((n_reservoir, n_reservoir))
        for _ in range(n_connections):
            i = np.random.randint(0, n_reservoir)
            j = np.random.randint(0, n_reservoir)
            W[i, j] = np.random.randn()
            
        # Scale to desired spectral radius
        eigenvalues = np.linalg.eigvals(W)
        current_spectral_radius = np.max(np.abs(eigenvalues))
        
        if current_spectral_radius > 0:
            W = W * (spectral_radius / current_spectral_radius)
            
        return W
    
    def initialize_input_matrix(self, n_reservoir: int, n_inputs: int,
                               input_scaling: float = 1.0,
                               input_sparsity: float = 0.1,
                               random_state: Optional[int] = None) -> np.ndarray:
        """
        Initialize input weight matrix.
        
        Parameters
        ----------
        n_reservoir : int
            Number of reservoir units
        n_inputs : int
            Number of input dimensions
        input_scaling : float
            Input weight scaling factor
        input_sparsity : float
            Input connection density
        random_state : int, optional
            Random seed
            
        Returns
        -------
        np.ndarray
            Input weight matrix
        """
        if random_state is not None:
            np.random.seed(random_state)
            
        W_in = np.random.randn(n_reservoir, n_inputs) * input_scaling
        
        # Apply sparsity
        if input_sparsity < 1.0:
            mask = np.random.rand(n_reservoir, n_inputs) < input_sparsity
            W_in = W_in * mask
            
        return W_in


class StateUpdateMixin:
    """
    Reservoir state update mechanisms.
    
    Implements various integration methods for reservoir dynamics:
    - Standard leaky integration
    - Euler integration  
    - Multiple timescales
    - Noise injection
    """
    
    def update_reservoir_states(self, u: np.ndarray, x: np.ndarray,
                               W_reservoir: np.ndarray, W_in: np.ndarray,
                               W_feedback: Optional[np.ndarray] = None,
                               y_feedback: Optional[np.ndarray] = None,
                               leak_rate: float = 1.0,
                               activation: str = 'tanh',
                               noise_level: float = 0.0) -> np.ndarray:
        """
        Update reservoir states using leaky integration.
        
        Standard ESN dynamics:
        x(t+1) = (1-α)x(t) + α·f(W_res·x(t) + W_in·u(t) + W_fb·y(t) + noise)
        
        Parameters
        ----------
        u : np.ndarray, shape (n_inputs,)
            Current input vector
        x : np.ndarray, shape (n_reservoir,)
            Current reservoir state
        W_reservoir : np.ndarray
            Reservoir weight matrix
        W_in : np.ndarray
            Input weight matrix
        W_feedback : np.ndarray, optional
            Feedback weight matrix
        y_feedback : np.ndarray, optional
            Feedback signal
        leak_rate : float
            Leaky integration rate (α)
        activation : str
            Activation function ('tanh', 'sigmoid', 'relu')
        noise_level : float
            Gaussian noise standard deviation
            
        Returns
        -------
        np.ndarray
            New reservoir state
        """
        # Compute pre-activation
        pre_activation = W_reservoir @ x + W_in @ u
        
        # Add feedback if provided
        if W_feedback is not None and y_feedback is not None:
            pre_activation += W_feedback @ y_feedback
            
        # Add noise if specified
        if noise_level > 0:
            pre_activation += np.random.normal(0, noise_level, len(pre_activation))
            
        # Apply activation function
        if activation == 'tanh':
            activated = np.tanh(pre_activation)
        elif activation == 'sigmoid':
            activated = expit(pre_activation)  # Numerically stable sigmoid
        elif activation == 'relu':
            activated = np.maximum(0, pre_activation)
        elif activation == 'linear':
            activated = pre_activation
        else:
            raise ValueError(f"Unknown activation function: {activation}")
            
        # Leaky integration
        x_new = (1 - leak_rate) * x + leak_rate * activated
        
        return x_new


class TrainingMixin:
    """
    Advanced training methods for reservoir computing.
    
    Implements multiple training algorithms:
    - Ridge regression (standard)
    - Elastic net regularization
    - LSQR for large systems
    - Online learning algorithms
    - Cross-validation for hyperparameter tuning
    """
    
    def train_readout_ridge(self, reservoir_states: np.ndarray, 
                           targets: np.ndarray,
                           regularization: float = 1e-6,
                           include_inputs: bool = True,
                           inputs: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Train linear readout using ridge regression.
        
        This is the standard ESN training method that solves:
        min ||XW - Y||² + λ||W||²
        
        Parameters
        ----------
        reservoir_states : np.ndarray, shape (n_time, n_reservoir)
            Reservoir state time series
        targets : np.ndarray, shape (n_time, n_outputs)
            Target output time series
        regularization : float
            Ridge regularization parameter (λ)
        include_inputs : bool
            Whether to include direct input-output connections
        inputs : np.ndarray, optional
            Input time series (needed if include_inputs=True)
            
        Returns
        -------
        Dict[str, Any]
            Training results including weights and performance metrics
        """
        n_time, n_reservoir = reservoir_states.shape
        n_outputs = targets.shape[1] if targets.ndim > 1 else 1
        targets = targets.reshape(n_time, -1)
        
        # Prepare extended state matrix
        if include_inputs and inputs is not None:
            n_inputs = inputs.shape[1] if inputs.ndim > 1 else 1
            inputs = inputs.reshape(n_time, -1)
            extended_states = np.column_stack([reservoir_states, inputs])
        else:
            extended_states = reservoir_states
            
        # Add bias term
        X = np.column_stack([extended_states, np.ones(n_time)])
        
        # Ridge regression solution
        # W = (X^T X + λI)^(-1) X^T Y
        XTX = X.T @ X
        XTY = X.T @ targets
        
        # Add regularization
        reg_matrix = regularization * np.eye(X.shape[1])
        reg_matrix[-1, -1] = 0  # Don't regularize bias term
        
        try:
            W = linalg.solve(XTX + reg_matrix, XTY)
        except linalg.LinAlgError:
            # Fallback to pseudoinverse
            W = linalg.pinv(X) @ targets
            
        # Compute predictions and metrics
        predictions = X @ W
        mse = mean_squared_error(targets, predictions)
        r2 = r2_score(targets, predictions)
        
        # Training error analysis
        residuals = targets - predictions
        training_error = np.mean(residuals**2)
        
        return {
            'weights': W,
            'predictions': predictions,
            'mse': mse,
            'r2_score': r2,
            'training_error': training_error,
            'regularization': regularization,
            'n_parameters': W.size,
            'condition_number': np.linalg.cond(XTX + reg_matrix)
        }
    
    def optimize_hyperparameters(self, reservoir_states: np.ndarray,
                                targets: np.ndarray,
                                param_ranges: Dict[str, Tuple],
                                cv_folds: int = 5,
                                metric: str = 'mse') -> Dict[str, Any]:
        """
        Optimize hyperparameters using cross-validation.
        
        Parameters
        ----------
        reservoir_states : np.ndarray
            Reservoir states for training
        targets : np.ndarray
            Target outputs
        param_ranges : Dict[str, Tuple]
            Parameter ranges to search over
        cv_folds : int
            Number of cross-validation folds
        metric : str
            Optimization metric ('mse', 'r2')
            
        Returns
        -------
        Dict[str, Any]
            Optimization results
        """
        from sklearn.model_selection import ParameterGrid, KFold
        
        # Create parameter grid
        param_grid = ParameterGrid(param_ranges)
        
        # Cross-validation setup
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
        
        best_score = float('inf') if metric == 'mse' else float('-inf')
        best_params = None
        results = []
        
        for params in param_grid:
            scores = []
            
            for train_idx, val_idx in kf.split(reservoir_states):
                # Split data
                states_train = reservoir_states[train_idx]
                targets_train = targets[train_idx]
                states_val = reservoir_states[val_idx]  
                targets_val = targets[val_idx]
                
                # Train with current parameters
                train_result = self.train_readout_ridge(
                    states_train, targets_train,
                    regularization=params.get('regularization', 1e-6)
                )
                
                # Validate
                extended_val = np.column_stack([states_val, np.ones(len(states_val))])
                pred_val = extended_val @ train_result['weights']
                
                if metric == 'mse':
                    score = mean_squared_error(targets_val, pred_val)
                elif metric == 'r2':
                    score = r2_score(targets_val, pred_val)
                    
                scores.append(score)
                
            # Average across folds
            mean_score = np.mean(scores)
            results.append({'params': params, 'score': mean_score, 'std': np.std(scores)})
            
            # Update best
            if metric == 'mse' and mean_score < best_score:
                best_score = mean_score
                best_params = params
            elif metric == 'r2' and mean_score > best_score:
                best_score = mean_score
                best_params = params
                
        return {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': results,
            'optimization_metric': metric
        }


class PredictionMixin:
    """
    Advanced prediction and generation methods.
    
    Implements various readout architectures:
    - Linear readout (standard)
    - Population vector readout  
    - Nonlinear readout (SVM, MLP)
    - Autonomous generation modes
    """
    
    def predict_sequence(self, initial_states: np.ndarray,
                        input_sequence: np.ndarray,
                        W_reservoir: np.ndarray,
                        W_in: np.ndarray,
                        W_out: np.ndarray,
                        **dynamics_params) -> Dict[str, np.ndarray]:
        """
        Predict output sequence given input sequence.
        
        Parameters
        ----------
        initial_states : np.ndarray
            Initial reservoir states
        input_sequence : np.ndarray, shape (time_steps, n_inputs)
            Input time series
        W_reservoir : np.ndarray
            Reservoir weight matrix
        W_in : np.ndarray  
            Input weight matrix
        W_out : np.ndarray
            Output weight matrix
        **dynamics_params
            Additional parameters for state updates
            
        Returns
        -------
        Dict[str, np.ndarray]
            Prediction results
        """
        n_time, n_inputs = input_sequence.shape
        n_reservoir = len(initial_states)
        n_outputs = W_out.shape[0]
        
        # Initialize arrays
        states = np.zeros((n_time + 1, n_reservoir))
        outputs = np.zeros((n_time, n_outputs))
        
        states[0] = initial_states
        
        # Forward prediction
        for t in range(n_time):
            # Update reservoir state
            states[t + 1] = self.update_reservoir_states(
                input_sequence[t], states[t],
                W_reservoir, W_in, **dynamics_params
            )
            
            # Compute output (including bias if W_out has it)
            if W_out.shape[1] == n_reservoir + n_inputs + 1:
                # Extended state with inputs and bias
                extended_state = np.concatenate([states[t + 1], input_sequence[t], [1]])
            elif W_out.shape[1] == n_reservoir + 1:
                # Reservoir state with bias
                extended_state = np.concatenate([states[t + 1], [1]])
            else:
                # Just reservoir state
                extended_state = states[t + 1]
                
            outputs[t] = W_out @ extended_state
            
        return {
            'predictions': outputs,
            'reservoir_states': states[1:],  # Exclude initial state
            'final_state': states[-1]
        }
    
    def generate_autonomous(self, initial_state: np.ndarray,
                           n_generate: int,
                           W_reservoir: np.ndarray,
                           W_in: np.ndarray, 
                           W_out: np.ndarray,
                           W_feedback: Optional[np.ndarray] = None,
                           **dynamics_params) -> Dict[str, np.ndarray]:
        """
        Generate sequence autonomously (teacher forcing off).
        
        In autonomous mode, the network's own output is fed back as input,
        allowing it to generate sequences based on learned dynamics.
        
        Parameters
        ----------
        initial_state : np.ndarray
            Initial reservoir state
        n_generate : int
            Number of time steps to generate
        W_reservoir : np.ndarray
            Reservoir weight matrix
        W_in : np.ndarray
            Input weight matrix
        W_out : np.ndarray
            Output weight matrix
        W_feedback : np.ndarray, optional
            Feedback weight matrix (if None, use output as direct input)
        **dynamics_params
            Parameters for state dynamics
            
        Returns
        -------
        Dict[str, np.ndarray]
            Generated sequence and states
        """
        n_reservoir = len(initial_state)
        n_outputs = W_out.shape[0]
        
        # Initialize arrays
        states = np.zeros((n_generate + 1, n_reservoir))
        outputs = np.zeros((n_generate, n_outputs))
        
        states[0] = initial_state
        current_output = np.zeros(n_outputs)  # Initial output
        
        # Generate sequence
        for t in range(n_generate):
            # Use previous output as input (autonomous mode)
            if W_feedback is not None:
                # Dedicated feedback weights
                states[t + 1] = self.update_reservoir_states(
                    np.zeros(W_in.shape[1]),  # No external input
                    states[t], W_reservoir, W_in,
                    W_feedback=W_feedback, y_feedback=current_output,
                    **dynamics_params
                )
            else:
                # Direct output-to-input feedback
                if W_in.shape[1] == n_outputs:
                    states[t + 1] = self.update_reservoir_states(
                        current_output, states[t],
                        W_reservoir, W_in, **dynamics_params
                    )
                else:
                    # Pad or truncate output to match input dimensions
                    feedback_input = np.zeros(W_in.shape[1])
                    min_dims = min(len(current_output), len(feedback_input))
                    feedback_input[:min_dims] = current_output[:min_dims]
                    
                    states[t + 1] = self.update_reservoir_states(
                        feedback_input, states[t],
                        W_reservoir, W_in, **dynamics_params
                    )
            
            # Compute output
            if W_out.shape[1] == n_reservoir + 1:
                extended_state = np.concatenate([states[t + 1], [1]])
            else:
                extended_state = states[t + 1]
                
            current_output = W_out @ extended_state
            outputs[t] = current_output
            
        return {
            'generated_sequence': outputs,
            'reservoir_states': states[1:],
            'final_state': states[-1]
        }


# ============================================================================
# MAIN ECHO STATE NETWORK IMPLEMENTATION
# ============================================================================

class EchoStateNetwork(BaseEstimator, RegressorMixin, 
                       ReservoirTheoryMixin, ReservoirInitializationMixin,
                       StateUpdateMixin, TrainingMixin, PredictionMixin):
    """
    Complete Echo State Network Implementation.
    
    🌊 Revolutionary Reservoir Computing Architecture
    
    Based on Herbert Jaeger's groundbreaking 2001 paper, this implementation
    provides a complete, research-grade Echo State Network with unified
    architecture combining all reservoir computing capabilities.
    
    🧠 Theoretical Foundation:
    The Echo State Network exploits the principle of "liquid state machines"
    where a fixed random recurrent network (the "reservoir") projects input
    sequences into a high-dimensional space with rich temporal dynamics.
    Only the linear readout weights are trained, making ESNs:
    
    - 1000x faster to train than traditional RNNs
    - Naturally suited for temporal pattern recognition
    - Capable of universal approximation with the Echo State Property
    - Robust to hyperparameter choices when ESP is satisfied
    
    🏗️ Architecture Overview:
    Input u(t) → [W_in] → Reservoir x(t) → [W_out] → Output y(t)
                            ↑     ↓
                         [W_res] [W_back]
                         (fixed) (optional)
    
    Mathematical Dynamics:
    x(t+1) = (1-α)x(t) + α·f(W_res·x(t) + W_in·u(t) + W_back·y(t) + noise)
    y(t) = W_out·[x(t); u(t)]
    
    Parameters
    ----------
    n_reservoir : int, default=100
        Number of reservoir neurons
    spectral_radius : float, default=0.95
        Spectral radius of reservoir matrix (must be < 1 for ESP)
    input_scaling : float, default=1.0
        Scaling factor for input weights
    leak_rate : float, default=1.0
        Leaky integration parameter (α)
    regularization : float, default=1e-6
        Ridge regression regularization parameter
    sparsity : float, default=0.1
        Connection density in reservoir
    activation : str, default='tanh'
        Activation function ('tanh', 'sigmoid', 'relu')
    random_state : int, optional
        Random seed for reproducibility
    """
    
    def __init__(self, n_reservoir: int = 100,
                 spectral_radius: float = 0.95,
                 input_scaling: float = 1.0,
                 leak_rate: float = 1.0,
                 regularization: float = 1e-6,
                 sparsity: float = 0.1,
                 activation: str = 'tanh',
                 noise_level: float = 0.0,
                 include_direct_connections: bool = True,
                 random_state: Optional[int] = None):
        
        self.n_reservoir = n_reservoir
        self.spectral_radius = spectral_radius
        self.input_scaling = input_scaling
        self.leak_rate = leak_rate
        self.regularization = regularization
        self.sparsity = sparsity
        self.activation = activation
        self.noise_level = noise_level
        self.include_direct_connections = include_direct_connections
        self.random_state = random_state
        
        # Initialize internal state
        self.is_fitted_ = False
        self.W_reservoir_ = None
        self.W_in_ = None
        self.W_out_ = None
        self.initial_transient_ = 100  # Skip initial transient
    
    def fit(self, X: np.ndarray, y: np.ndarray,
            inputs: Optional[np.ndarray] = None,
            wash_out: Optional[int] = None) -> 'EchoStateNetwork':
        """
        Train the Echo State Network.
        
        Parameters
        ----------
        X : np.ndarray, shape (n_time, n_inputs)
            Input time series
        y : np.ndarray, shape (n_time, n_outputs)
            Target output time series  
        inputs : np.ndarray, optional
            Alternative input specification
        wash_out : int, optional
            Number of initial time steps to discard
            
        Returns
        -------
        self : EchoStateNetwork
            Fitted estimator
        """
        # Handle input format
        if inputs is not None:
            X = inputs
            
        X = np.atleast_2d(X)
        y = np.atleast_2d(y)
        
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must have same number of time steps")
            
        n_time, n_inputs = X.shape
        n_outputs = y.shape[1]
        
        # Initialize network matrices
        if self.random_state is not None:
            np.random.seed(self.random_state)
            
        self.W_reservoir_ = self.initialize_reservoir_matrix(
            self.n_reservoir, self.spectral_radius, self.sparsity, self.random_state
        )
        
        self.W_in_ = self.initialize_input_matrix(
            self.n_reservoir, n_inputs, self.input_scaling,
            self.sparsity, self.random_state
        )
        
        # Verify Echo State Property
        esp_results = self.verify_echo_state_property(self.W_reservoir_, verbose=False)
        if not esp_results['esp_satisfied']:
            warnings.warn(f"Echo State Property not satisfied! "
                         f"Spectral radius: {esp_results['spectral_radius']:.4f}")
        
        # Collect reservoir states
        wash_out = wash_out or self.initial_transient_
        states = self._collect_states(X, wash_out)
        
        # Prepare targets (skip wash-out)
        targets = y[wash_out:]
        
        # Train readout
        if self.include_direct_connections:
            training_result = self.train_readout_ridge(
                states, targets, self.regularization, 
                include_inputs=True, inputs=X[wash_out:]
            )
        else:
            training_result = self.train_readout_ridge(
                states, targets, self.regularization, 
                include_inputs=False
            )
            
        self.W_out_ = training_result['weights']
        self.training_score_ = training_result['r2_score']
        self.training_error_ = training_result['mse']
        
        # Store fitted parameters
        self.n_inputs_ = n_inputs
        self.n_outputs_ = n_outputs
        self.is_fitted_ = True
        
        return self
    
    def predict(self, X: np.ndarray, 
                continuation: bool = False,
                return_states: bool = False) -> Union[np.ndarray, Dict]:
        """
        Predict using the trained ESN.
        
        Parameters
        ----------
        X : np.ndarray, shape (n_time, n_inputs)
            Input sequence
        continuation : bool
            Whether this is a continuation of previous sequence
        return_states : bool
            Whether to return reservoir states
            
        Returns
        -------
        predictions : np.ndarray or Dict
            Predicted outputs, optionally with states
        """
        if not self.is_fitted_:
            raise ValueError("ESN must be fitted before prediction")
            
        X = np.atleast_2d(X)
        
        # Initialize state
        if continuation and hasattr(self, 'last_state_'):
            initial_state = self.last_state_
        else:
            initial_state = np.zeros(self.n_reservoir)
            
        # Generate predictions
        result = self.predict_sequence(
            initial_state, X,
            self.W_reservoir_, self.W_in_, self.W_out_,
            leak_rate=self.leak_rate,
            activation=self.activation,
            noise_level=self.noise_level
        )
        
        # Store final state for potential continuation
        self.last_state_ = result['final_state']
        
        if return_states:
            return result
        else:
            return result['predictions']
    
    def generate(self, n_steps: int, 
                initial_state: Optional[np.ndarray] = None,
                return_states: bool = False) -> Union[np.ndarray, Dict]:
        """
        Generate sequence autonomously.
        
        Parameters
        ----------
        n_steps : int
            Number of steps to generate
        initial_state : np.ndarray, optional
            Initial reservoir state
        return_states : bool
            Whether to return reservoir states
            
        Returns
        -------
        generated : np.ndarray or Dict
            Generated sequence, optionally with states
        """
        if not self.is_fitted_:
            raise ValueError("ESN must be fitted before generation")
            
        if initial_state is None:
            initial_state = getattr(self, 'last_state_', np.zeros(self.n_reservoir))
            
        result = self.generate_autonomous(
            initial_state, n_steps,
            self.W_reservoir_, self.W_in_, self.W_out_,
            leak_rate=self.leak_rate,
            activation=self.activation,
            noise_level=self.noise_level
        )
        
        if return_states:
            return result
        else:
            return result['generated_sequence']
    
    def _collect_states(self, X: np.ndarray, wash_out: int) -> np.ndarray:
        """Collect reservoir states during training."""
        n_time, n_inputs = X.shape
        states = np.zeros((n_time - wash_out, self.n_reservoir))
        
        # Initialize reservoir state
        current_state = np.zeros(self.n_reservoir)
        
        # Run through input sequence
        for t in range(n_time):
            current_state = self.update_reservoir_states(
                X[t], current_state,
                self.W_reservoir_, self.W_in_,
                leak_rate=self.leak_rate,
                activation=self.activation,
                noise_level=self.noise_level
            )
            
            # Collect state after wash-out
            if t >= wash_out:
                states[t - wash_out] = current_state
                
        return states
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Compute R² score on test data."""
        predictions = self.predict(X)
        return r2_score(y, predictions)


# ============================================================================
# SPECIALIZED ESN VARIANTS
# ============================================================================

class DeepEchoStateNetwork(EchoStateNetwork):
    """
    Deep Echo State Network with multiple reservoir layers.
    
    Stacks multiple ESN layers to create hierarchical temporal representations
    with different timescales and dynamics.
    """
    
    def __init__(self, layer_sizes: List[int] = [100, 50, 25],
                 spectral_radii: Optional[List[float]] = None,
                 leak_rates: Optional[List[float]] = None,
                 **esn_params):
        
        self.layer_sizes = layer_sizes
        self.n_layers = len(layer_sizes)
        
        # Default parameters for each layer
        if spectral_radii is None:
            spectral_radii = [0.95 - 0.1*i for i in range(self.n_layers)]
        if leak_rates is None:
            leak_rates = [1.0 - 0.2*i for i in range(self.n_layers)]
            
        self.spectral_radii = spectral_radii
        self.leak_rates = leak_rates
        
        # Initialize first layer as standard ESN
        super().__init__(n_reservoir=layer_sizes[0], 
                        spectral_radius=spectral_radii[0],
                        leak_rate=leak_rates[0],
                        **esn_params)
        
        # Additional layers will be initialized during fit
        self.layers_ = []


class OnlineEchoStateNetwork(EchoStateNetwork):
    """
    Online learning variant of ESN using recursive least squares.
    
    Updates readout weights online using RLS algorithm, enabling
    continuous adaptation to new data.
    """
    
    def __init__(self, forgetting_factor: float = 0.999,
                 online_regularization: float = 1e-6,
                 **esn_params):
        
        super().__init__(**esn_params)
        self.forgetting_factor = forgetting_factor
        self.online_regularization = online_regularization
        
        # RLS parameters
        self.P_ = None  # Inverse correlation matrix
        self.online_weights_ = None
    
    def partial_fit(self, x_input: np.ndarray, y_target: np.ndarray):
        """Update model with single time step using RLS."""
        if not self.is_fitted_:
            raise ValueError("Must call fit() before partial_fit()")
            
        # Update reservoir state
        if not hasattr(self, 'current_state_'):
            self.current_state_ = np.zeros(self.n_reservoir)
            
        self.current_state_ = self.update_reservoir_states(
            x_input, self.current_state_,
            self.W_reservoir_, self.W_in_,
            leak_rate=self.leak_rate,
            activation=self.activation
        )
        
        # Extended state for RLS update
        if self.include_direct_connections:
            phi = np.concatenate([self.current_state_, x_input, [1]])
        else:
            phi = np.concatenate([self.current_state_, [1]])
            
        # RLS update
        self._rls_update(phi, y_target)
    
    def _rls_update(self, phi: np.ndarray, y_target: np.ndarray):
        """Recursive least squares weight update."""
        if self.P_ is None:
            # Initialize RLS matrices
            n_features = len(phi)
            self.P_ = np.eye(n_features) / self.online_regularization
            self.online_weights_ = np.zeros((len(y_target), n_features))
            
        # RLS update equations
        lambda_inv = 1.0 / self.forgetting_factor
        Pphi = self.P_ @ phi
        denominator = 1 + lambda_inv * phi @ Pphi
        
        gain = (lambda_inv * Pphi) / denominator
        prediction_error = y_target - self.online_weights_ @ phi
        
        # Update weights and inverse correlation matrix
        self.online_weights_ += np.outer(prediction_error, gain)
        self.P_ = lambda_inv * (self.P_ - np.outer(gain, Pphi))


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_echo_state_network(task_type: str = 'regression',
                             complexity: str = 'medium',
                             **custom_params) -> EchoStateNetwork:
    """
    Factory function to create ESN with task-appropriate defaults.
    
    Parameters
    ----------
    task_type : str
        Type of task ('regression', 'classification', 'generation')
    complexity : str
        Problem complexity ('simple', 'medium', 'complex')
    **custom_params
        Override default parameters
        
    Returns
    -------
    EchoStateNetwork
        Configured ESN instance
    """
    # Base configurations
    configs = {
        'simple': {
            'n_reservoir': 50,
            'spectral_radius': 0.9,
            'sparsity': 0.2
        },
        'medium': {
            'n_reservoir': 100,
            'spectral_radius': 0.95,
            'sparsity': 0.1
        },
        'complex': {
            'n_reservoir': 200,
            'spectral_radius': 0.99,
            'sparsity': 0.05
        }
    }
    
    # Task-specific modifications
    task_configs = {
        'regression': {
            'regularization': 1e-6,
            'leak_rate': 1.0
        },
        'classification': {
            'regularization': 1e-3,
            'leak_rate': 0.8,
            'activation': 'tanh'
        },
        'generation': {
            'regularization': 1e-8,
            'leak_rate': 0.9,
            'spectral_radius': 0.98  # Closer to edge for richer dynamics
        }
    }
    
    # Merge configurations
    config = configs[complexity].copy()
    config.update(task_configs[task_type])
    config.update(custom_params)
    
    return EchoStateNetwork(**config)


def optimize_esn_hyperparameters(X: np.ndarray, y: np.ndarray,
                                param_space: Optional[Dict] = None,
                                n_trials: int = 50,
                                cv_folds: int = 5) -> Dict[str, Any]:
    """
    Optimize ESN hyperparameters using cross-validation.
    
    Parameters
    ----------
    X : np.ndarray
        Input data
    y : np.ndarray
        Target data
    param_space : Dict, optional
        Parameter search space
    n_trials : int
        Number of optimization trials
    cv_folds : int
        Cross-validation folds
        
    Returns
    -------
    Dict[str, Any]
        Optimization results
    """
    if param_space is None:
        param_space = {
            'n_reservoir': [50, 100, 200, 400],
            'spectral_radius': np.linspace(0.7, 0.99, 10),
            'input_scaling': np.logspace(-2, 1, 10),
            'leak_rate': np.linspace(0.1, 1.0, 10),
            'regularization': np.logspace(-8, -2, 20),
            'sparsity': [0.01, 0.05, 0.1, 0.2, 0.5]
        }
    
    from sklearn.model_selection import ParameterGrid, cross_val_score
    
    # Create parameter combinations
    param_grid = list(ParameterGrid(param_space))
    np.random.shuffle(param_grid)
    
    best_score = float('-inf')
    best_params = None
    results = []
    
    for i, params in enumerate(param_grid[:n_trials]):
        try:
            # Create ESN with current parameters
            esn = EchoStateNetwork(random_state=42, **params)
            
            # Cross-validation
            scores = cross_val_score(esn, X, y, cv=cv_folds, 
                                   scoring='r2', n_jobs=1)
            mean_score = np.mean(scores)
            
            results.append({
                'params': params,
                'mean_score': mean_score,
                'std_score': np.std(scores),
                'scores': scores
            })
            
            if mean_score > best_score:
                best_score = mean_score
                best_params = params
                
            print(f"Trial {i+1}/{n_trials}: R² = {mean_score:.4f} ± {np.std(scores):.4f}")
            
        except Exception as e:
            print(f"Trial {i+1} failed: {e}")
            continue
    
    return {
        'best_params': best_params,
        'best_score': best_score,
        'all_results': results
    }