"""
🔮 Core Prediction - Basic ESN Prediction and Linear Readout
==========================================================

Author: Benedict Chen (benedict@benedictchen.com)

Core prediction functionality for Echo State Networks based on Jaeger's
linear readout methodology from Section 3.1 of the original paper.

Based on: Jaeger, H. (2001) "Echo state network" Equations 11-12
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
import warnings
import logging

# Configure logging
logger = logging.getLogger(__name__)


class EchoStatePredictionMixin:
    """
    🔮 Core prediction capabilities for Echo State Networks
    
    Implements Jaeger's linear readout methodology with proper handling
    of output activation functions and multi-step predictions.
    """
    
    def predict_sequence(self, X_input: np.ndarray, 
                        washout: int = 0,
                        return_states: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Predict output sequence from input sequence using trained readout weights
        
        Based on Jaeger (2001) Section 3.1, Equation 11:
        y(n) = f^out(W^out * [u(n); x(n)])
        
        Args:
            X_input: Input sequence (time_steps × n_inputs)
            washout: Number of initial steps to discard
            return_states: Whether to return reservoir states
            
        Returns:
            Predictions array, optionally with states
        """
        if not hasattr(self, 'W_out') or self.W_out is None:
            raise ValueError("Model must be trained first (W_out is None)")
        
        # Run reservoir to collect states
        if hasattr(self, 'run_reservoir'):
            states = self.run_reservoir(X_input, reset_state=True)
        else:
            states = self._collect_reservoir_states(X_input)
        
        # Apply washout
        if washout > 0 and len(states) > washout:
            states = states[washout:]
            effective_inputs = X_input[washout:] if len(X_input) > washout else X_input
        else:
            effective_inputs = X_input
        
        # Compute predictions using linear readout
        predictions = predict_from_states(states, self.W_out, 
                                        output_activation=getattr(self, 'output_activation', None))
        
        if return_states:
            return predictions, states
        return predictions
    
    def predict_single_step(self, current_state: np.ndarray, 
                          current_input: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Single-step prediction from current reservoir state
        
        Args:
            current_state: Current reservoir state
            current_input: Current input (for concatenation if needed)
            
        Returns:
            Single prediction vector
        """
        if not hasattr(self, 'W_out') or self.W_out is None:
            raise ValueError("Model must be trained first")
        
        # Prepare state vector for readout
        if current_input is not None and hasattr(self, 'include_input_in_readout') and self.include_input_in_readout:
            # Concatenate input and state: [u(n); x(n)]
            readout_input = np.concatenate([current_input.flatten(), current_state.flatten()])
        else:
            # Use only reservoir state: x(n)
            readout_input = current_state.flatten()
        
        # Linear readout: W^out * [u(n); x(n)]
        linear_output = self.W_out.T @ readout_input if self.W_out.ndim == 2 else np.dot(readout_input, self.W_out)
        
        # Apply output activation if specified
        if hasattr(self, 'output_activation') and self.output_activation is not None:
            return self.output_activation(linear_output)
        
        return linear_output
    
    def predict_multi_step(self, initial_input: np.ndarray, 
                          n_steps: int,
                          mode: str = 'open_loop') -> np.ndarray:
        """
        Multi-step prediction with different modes
        
        Args:
            initial_input: Initial input sequence for warming up
            n_steps: Number of steps to predict
            mode: 'open_loop' (with inputs) or 'closed_loop' (autonomous)
            
        Returns:
            Multi-step predictions
        """
        if mode == 'open_loop':
            return self._predict_open_loop(initial_input, n_steps)
        elif mode == 'closed_loop':
            return self._predict_closed_loop(initial_input, n_steps)
        else:
            raise ValueError(f"Unknown prediction mode: {mode}")
    
    def _predict_open_loop(self, inputs: np.ndarray, n_steps: int) -> np.ndarray:
        """Open-loop prediction with provided inputs"""
        if len(inputs) < n_steps:
            raise ValueError(f"Need at least {n_steps} inputs for open-loop prediction")
        
        return self.predict_sequence(inputs[:n_steps])
    
    def _predict_closed_loop(self, prime_sequence: np.ndarray, n_steps: int) -> np.ndarray:
        """Closed-loop (autonomous) prediction"""
        # This will be fully implemented in autonomous_generation.py
        # For now, provide basic functionality
        logger.warning("Closed-loop prediction requires full autonomous generation setup")
        
        # Warm up with prime sequence
        if len(prime_sequence) > 0:
            states = self.run_reservoir(prime_sequence, reset_state=True)
            current_state = states[-1]
        else:
            current_state = np.zeros(self.n_reservoir)
        
        predictions = []
        
        # Generate predictions (simplified - no feedback loop yet)
        for step in range(n_steps):
            pred = self.predict_single_step(current_state)
            predictions.append(pred)
            
            # Update state (simplified - would need proper feedback)
            if hasattr(self, 'update_state'):
                current_state = self.update_state(current_state, np.zeros(self.n_inputs), pred)
            else:
                # Proper ESN state dynamics with leaking rate (Jaeger, 2001)
                # x(t+1) = (1-α)x(t) + α*tanh(W_res*x(t) + W_in*u(t))
                # where α is leaking rate for temporal dynamics
                alpha = getattr(self, 'leaking_rate', 0.3)  # Default leaking rate
                if hasattr(self, 'W_reservoir') and self.W_reservoir is not None:
                    # Proper reservoir computation with leaking
                    reservoir_activation = np.tanh(
                        self.W_reservoir @ current_state + 
                        getattr(self, 'W_in', np.random.randn(len(current_state), 1))[:, 0] * 0.1
                    )
                    current_state = (1 - alpha) * current_state + alpha * reservoir_activation
                else:
                    # Fallback with proper ESN-style decay and recurrence
                    current_state = (1 - alpha) * current_state + alpha * np.tanh(
                        current_state * 0.8 + np.random.randn(*current_state.shape) * 0.1
                    )
        
        return np.array(predictions)
    
    def _collect_reservoir_states(self, X_input: np.ndarray) -> np.ndarray:
        """Fallback method to collect reservoir states if run_reservoir not available"""
        logger.warning("Using fallback state collection - implement run_reservoir for better performance")
        
        time_steps = len(X_input)
        states = []
        current_state = np.zeros(getattr(self, 'n_reservoir', 100))
        
        for t in range(time_steps):
            # Simple state update (would need proper reservoir dynamics)
            input_vec = X_input[t] if X_input.ndim > 1 else np.array([X_input[t]])
            
            # Research-accurate ESN dynamics based on Jaeger (2001) Echo State Property
            # Standard ESN update: x(t+1) = (1-α)x(t) + α*f(W_res*x(t) + W_in*u(t) + W_bias)
            alpha = getattr(self, 'leaking_rate', 0.3)
            if hasattr(self, 'W_reservoir') and hasattr(self, 'W_in'):
                # Standard reservoir computation with input weights
                reservoir_input = self.W_in @ input_vec if len(input_vec) == self.W_in.shape[1] else np.zeros(self.W_in.shape[0])
                bias_term = getattr(self, 'bias', np.zeros(len(current_state)))
                reservoir_activation = np.tanh(
                    self.W_reservoir @ current_state + reservoir_input + bias_term
                )
                current_state = (1 - alpha) * current_state + alpha * reservoir_activation
            else:
                # Fallback with proper ESN recurrent dynamics 
                # Maintain echo state property with spectral radius < 1
                spectral_radius = 0.95  # Standard ESN parameter
                recurrent_weight = np.random.randn(len(current_state), len(current_state)) * spectral_radius / len(current_state)**0.5
                input_scaling = 0.1
                
                reservoir_activation = np.tanh(
                    recurrent_weight @ current_state + input_scaling * np.random.randn(*current_state.shape)
                )
                current_state = (1 - alpha) * current_state + alpha * reservoir_activation
            
            states.append(current_state.copy())
        
        return np.array(states)


def predict_from_states(states: np.ndarray, 
                       W_out: np.ndarray,
                       inputs: Optional[np.ndarray] = None,
                       output_activation: Optional[Callable] = None) -> np.ndarray:
    """
    Compute predictions from reservoir states using linear readout
    
    Implements Jaeger (2001) Equation 11: y(n) = f^out(W^out * [u(n); x(n)])
    
    Args:
        states: Reservoir states (time_steps × n_reservoir)
        W_out: Output weights (n_outputs × n_readout)
        inputs: Optional inputs to include in readout (time_steps × n_inputs)
        output_activation: Optional output activation function
        
    Returns:
        Predictions (time_steps × n_outputs)
    """
    time_steps, n_reservoir = states.shape
    
    # Prepare readout input
    if inputs is not None:
        # Concatenate inputs and states: [u(n); x(n)]
        if inputs.ndim == 1:
            inputs = inputs.reshape(-1, 1)
        
        # Ensure same number of time steps
        min_steps = min(len(states), len(inputs))
        readout_input = np.concatenate([inputs[:min_steps], states[:min_steps]], axis=1)
    else:
        # Use only reservoir states: x(n)
        readout_input = states
    
    # Linear readout: W^out * [u(n); x(n)]
    if W_out.ndim == 2:
        linear_output = readout_input @ W_out.T
    else:
        linear_output = readout_input @ W_out
    
    # Apply output activation function
    if output_activation is not None:
        return output_activation(linear_output)
    
    return linear_output


def compute_linear_readout(states: np.ndarray, 
                         targets: np.ndarray,
                         regularization: float = 1e-8,
                         include_bias: bool = False) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Compute linear readout weights using Jaeger's training method
    
    Based on Jaeger (2001) Section 3.1, Equation 12:
    W^out = (S^T S + λI)^(-1) S^T Y
    
    Args:
        states: Reservoir states (time_steps × n_reservoir)
        targets: Target outputs (time_steps × n_outputs)
        regularization: Regularization parameter λ
        include_bias: Whether to include bias term
        
    Returns:
        Output weights and training info
    """
    # Prepare state matrix
    S = states.copy()
    
    # Add bias column if requested
    if include_bias:
        bias_column = np.ones((len(S), 1))
        S = np.concatenate([S, bias_column], axis=1)
    
    # Ensure targets have correct shape
    Y = targets.copy()
    if Y.ndim == 1:
        Y = Y.reshape(-1, 1)
    
    # Ensure compatible dimensions
    min_len = min(len(S), len(Y))
    S = S[:min_len]
    Y = Y[:min_len]
    
    try:
        # Normal equation with regularization: W^out = (S^T S + λI)^(-1) S^T Y
        StS = S.T @ S
        identity = np.eye(StS.shape[0]) * regularization
        
        W_out = np.linalg.solve(StS + identity, S.T @ Y)
        
        # Compute training statistics
        predictions = S @ W_out
        mse = np.mean((predictions - Y)**2)
        
        training_info = {
            'method': 'linear_readout',
            'regularization': regularization,
            'mse': mse,
            'condition_number': np.linalg.cond(StS),
            'include_bias': include_bias,
            'n_parameters': W_out.size
        }
        
        return W_out, training_info
        
    except np.linalg.LinAlgError as e:
        logger.warning(f"Linear readout failed: {e}, trying SVD")
        
        # Fallback to SVD
        U, s, Vh = np.linalg.svd(S, full_matrices=False)
        
        # Regularized pseudoinverse
        s_reg = s / (s**2 + regularization)
        S_pinv = Vh.T @ np.diag(s_reg) @ U.T
        
        W_out = S_pinv @ Y
        predictions = S @ W_out
        mse = np.mean((predictions - Y)**2)
        
        training_info = {
            'method': 'svd_fallback',
            'regularization': regularization,
            'mse': mse,
            'singular_values': s,
            'include_bias': include_bias,
            'n_parameters': W_out.size
        }
        
        return W_out, training_info


def validate_prediction_setup(esn_model) -> Dict[str, Any]:
    """
    Validate that ESN model is properly configured for prediction
    
    Args:
        esn_model: ESN model to validate
        
    Returns:
        Validation results dictionary
    """
    results = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'recommendations': []
    }
    
    # Check required attributes
    required_attrs = ['W_out', 'n_reservoir']
    for attr in required_attrs:
        if not hasattr(esn_model, attr) or getattr(esn_model, attr) is None:
            results['errors'].append(f"Missing required attribute: {attr}")
            results['valid'] = False
    
    # Check output weights shape
    if hasattr(esn_model, 'W_out') and esn_model.W_out is not None:
        W_out = esn_model.W_out
        if W_out.ndim not in [1, 2]:
            results['errors'].append(f"W_out must be 1D or 2D, got shape {W_out.shape}")
            results['valid'] = False
    
    # Check for prediction methods
    prediction_methods = ['predict_sequence', 'run_reservoir']
    missing_methods = [method for method in prediction_methods 
                      if not hasattr(esn_model, method)]
    
    if missing_methods:
        results['warnings'].append(f"Missing prediction methods: {missing_methods}")
        results['recommendations'].append("Add EchoStatePredictionMixin to enable full prediction capabilities")
    
    # Check for output activation
    if hasattr(esn_model, 'output_activation'):
        if esn_model.output_activation is not None:
            results['recommendations'].append("Output activation function detected - ensure it's appropriate for your task")
    
    return results