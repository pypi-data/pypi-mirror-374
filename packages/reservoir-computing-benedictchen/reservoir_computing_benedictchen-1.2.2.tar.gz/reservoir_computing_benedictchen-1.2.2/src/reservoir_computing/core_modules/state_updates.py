"""
State Updates - Reservoir Dynamics
==================================

Author: Benedict Chen (benedict@benedictchen.com)

Reservoir state update mechanisms for Echo State Networks.
"""

import numpy as np
from scipy.special import expit
from typing import Optional


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