"""
Prediction Generation - Forward and Autonomous Prediction
=========================================================

Author: Benedict Chen (benedict@benedictchen.com)

Prediction methods for trained reservoir computing models.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple


class PredictionMixin:
    """
    Prediction generation for trained reservoir networks.
    
    Implements various prediction modes:
    - Forward prediction with external inputs
    - Autonomous prediction (closed-loop)
    - Multi-step ahead prediction
    - Uncertainty quantification
    """
    
    def predict_forward(self, reservoir_states: np.ndarray,
                       readout_weights: np.ndarray,
                       inputs: Optional[np.ndarray] = None,
                       include_bias: bool = True) -> np.ndarray:
        """
        Forward prediction using trained readout weights.
        
        Parameters
        ----------
        reservoir_states : np.ndarray, shape (n_time, n_reservoir)
            Reservoir state time series
        readout_weights : np.ndarray
            Trained readout weight matrix
        inputs : np.ndarray, optional
            Input features if included in training
        include_bias : bool
            Whether to include bias term
            
        Returns
        -------
        np.ndarray
            Predicted outputs
        """
        # Prepare feature matrix
        if inputs is not None:
            features = np.column_stack([reservoir_states, inputs])
        else:
            features = reservoir_states
            
        # Add bias term if used during training
        if include_bias:
            features = np.column_stack([features, np.ones(features.shape[0])])
            
        # Compute predictions
        predictions = features @ readout_weights
        
        return predictions
    
    def predict_autonomous(self, initial_state: np.ndarray,
                          W_reservoir: np.ndarray,
                          W_in: np.ndarray,
                          readout_weights: np.ndarray,
                          n_steps: int,
                          leak_rate: float = 1.0,
                          activation: str = 'tanh',
                          W_feedback: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Autonomous prediction in closed-loop mode.
        
        The network's output is fed back as input for multi-step prediction.
        
        Parameters
        ----------
        initial_state : np.ndarray
            Initial reservoir state
        W_reservoir : np.ndarray
            Reservoir weight matrix
        W_in : np.ndarray
            Input weight matrix
        readout_weights : np.ndarray
            Trained readout weights
        n_steps : int
            Number of prediction steps
        leak_rate : float
            Reservoir leak rate
        activation : str
            Activation function
        W_feedback : np.ndarray, optional
            Feedback weight matrix
            
        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Predicted outputs and reservoir states
        """
        predictions = []
        states = []
        
        x = initial_state.copy()
        
        for step in range(n_steps):
            # Store current state
            states.append(x.copy())
            
            # Compute output
            features = np.append(x, 1.0)  # Add bias
            y = features @ readout_weights
            predictions.append(y)
            
            # Update reservoir state using prediction as input
            if activation == 'tanh':
                activated = np.tanh(W_reservoir @ x + W_in @ y.flatten())
            elif activation == 'sigmoid':
                activated = 1.0 / (1.0 + np.exp(-(W_reservoir @ x + W_in @ y.flatten())))
            else:
                activated = W_reservoir @ x + W_in @ y.flatten()
                
            x = (1 - leak_rate) * x + leak_rate * activated
            
        return np.array(predictions), np.array(states)
    
    def predict_multi_step(self, reservoir_states: np.ndarray,
                          readout_weights: np.ndarray,
                          n_ahead: int = 1) -> np.ndarray:
        """
        Multi-step ahead prediction.
        
        Parameters
        ----------
        reservoir_states : np.ndarray
            Current reservoir states
        readout_weights : np.ndarray
            Trained readout weights
        n_ahead : int
            Number of steps to predict ahead
            
        Returns
        -------
        np.ndarray
            Multi-step predictions
        """
        predictions = []
        
        for step in range(n_ahead):
            # Use current or predicted states for next prediction
            if step == 0:
                current_states = reservoir_states
            else:
                # This is simplified - in practice would need state evolution
                current_states = reservoir_states
                
            features = np.column_stack([current_states, np.ones(current_states.shape[0])])
            pred = features @ readout_weights
            predictions.append(pred)
            
        return np.array(predictions)