"""
Echo State Network - Main Implementation
========================================

Author: Benedict Chen (benedict@benedictchen.com)

Core Echo State Network implementation combining all mixins.
Based on Herbert Jaeger (2001) and Wolfgang Maass (2002).
"""

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from typing import Optional, Dict, Any, Tuple
import warnings

from .reservoir_theory import ReservoirTheoryMixin
from .reservoir_initialization import ReservoirInitializationMixin
from .state_updates import StateUpdateMixin  
from .training_methods import TrainingMixin
from .prediction_generation import PredictionMixin


class EchoStateNetwork(BaseEstimator, RegressorMixin, 
                      ReservoirTheoryMixin, 
                      ReservoirInitializationMixin,
                      StateUpdateMixin,
                      TrainingMixin, 
                      PredictionMixin):
    """
    Complete Echo State Network implementation.
    
    A reservoir computing model that uses a fixed random recurrent network
    (the reservoir) and only trains the output connections.
    
    Parameters
    ----------
    n_reservoir : int, default=100
        Number of reservoir units
    spectral_radius : float, default=0.95  
        Spectral radius of reservoir matrix
    input_scaling : float, default=1.0
        Scaling of input connections
    regularization : float, default=1e-6
        Ridge regularization parameter
    leak_rate : float, default=1.0
        Leaky integration rate
    random_state : int, optional
        Random seed for reproducibility
    """
    
    def __init__(self, n_reservoir: int = 100,
                 spectral_radius: float = 0.95,
                 input_scaling: float = 1.0,
                 regularization: float = 1e-6,
                 leak_rate: float = 1.0,
                 sparsity: float = 0.1,
                 activation: str = 'tanh',
                 random_state: Optional[int] = None):
        
        self.n_reservoir = n_reservoir
        self.spectral_radius = spectral_radius
        self.input_scaling = input_scaling
        self.regularization = regularization
        self.leak_rate = leak_rate
        self.sparsity = sparsity
        self.activation = activation
        self.random_state = random_state
        
        # Model components (initialized during fit)
        self.W_reservoir_ = None
        self.W_in_ = None
        self.W_out_ = None
        self.reservoir_states_ = None
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'EchoStateNetwork':
        """
        Train the Echo State Network.
        
        Parameters
        ----------
        X : np.ndarray, shape (n_time, n_features)
            Input time series
        y : np.ndarray, shape (n_time, n_outputs)
            Target time series
            
        Returns
        -------
        self : EchoStateNetwork
            Fitted estimator
        """
        X = np.atleast_2d(X)
        y = np.atleast_2d(y)
        
        n_time, n_inputs = X.shape
        n_outputs = y.shape[1]
        
        # Initialize reservoir matrices
        self.W_reservoir_ = self.initialize_reservoir_matrix(
            self.n_reservoir, self.spectral_radius, self.sparsity, self.random_state)
        
        self.W_in_ = self.initialize_input_matrix(
            self.n_reservoir, n_inputs, self.input_scaling, 
            self.sparsity, self.random_state)
        
        # Verify Echo State Property
        esp_results = self.verify_echo_state_property(self.W_reservoir_, verbose=False)
        if not esp_results['esp_satisfied']:
            warnings.warn(f"Echo State Property not satisfied (spectral radius: {esp_results['spectral_radius']:.3f})")
        
        # Run reservoir to collect states
        reservoir_states = np.zeros((n_time, self.n_reservoir))
        x = np.zeros(self.n_reservoir)
        
        for t in range(n_time):
            x = self.update_reservoir_states(
                X[t], x, self.W_reservoir_, self.W_in_,
                leak_rate=self.leak_rate, activation=self.activation)
            reservoir_states[t] = x
            
        self.reservoir_states_ = reservoir_states
        
        # Train readout
        training_results = self.train_readout_ridge(
            reservoir_states, y, self.regularization)
        
        self.W_out_ = training_results['weights']
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Generate predictions for input time series.
        
        Parameters
        ----------
        X : np.ndarray, shape (n_time, n_features)
            Input time series
            
        Returns
        -------
        np.ndarray, shape (n_time, n_outputs)
            Predicted outputs
        """
        if self.W_out_ is None:
            raise ValueError("Model must be fitted before prediction")
            
        X = np.atleast_2d(X)
        n_time, n_inputs = X.shape
        
        # Run reservoir on test data
        reservoir_states = np.zeros((n_time, self.n_reservoir))
        x = np.zeros(self.n_reservoir)
        
        for t in range(n_time):
            x = self.update_reservoir_states(
                X[t], x, self.W_reservoir_, self.W_in_,
                leak_rate=self.leak_rate, activation=self.activation)
            reservoir_states[t] = x
            
        # Generate predictions
        predictions = self.predict_forward(reservoir_states, self.W_out_)
        
        return predictions.squeeze()
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Return coefficient of determination R².
        
        Parameters
        ----------
        X : np.ndarray
            Test input
        y : np.ndarray
            True test output
            
        Returns
        -------
        float
            R² score
        """
        from sklearn.metrics import r2_score
        y_pred = self.predict(X)
        return r2_score(y, y_pred)