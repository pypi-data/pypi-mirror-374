"""
Training Methods - Linear Readout Training
==========================================

Author: Benedict Chen (benedict@benedictchen.com)

Advanced training methods for reservoir computing readout layers.
"""

import numpy as np
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
from typing import Optional, Dict, Any


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
            Target outputs
        regularization : float
            Ridge regularization parameter (λ)
        include_inputs : bool
            Whether to include input features in readout
        inputs : np.ndarray, optional
            Input time series if include_inputs=True
            
        Returns
        -------
        Dict[str, Any]
            Training results with weights and metrics
        """
        # Prepare feature matrix
        if include_inputs and inputs is not None:
            features = np.column_stack([reservoir_states, inputs])
        else:
            features = reservoir_states
            
        # Add bias term
        features = np.column_stack([features, np.ones(features.shape[0])])
        
        # Ridge regression
        ridge = Ridge(alpha=regularization, fit_intercept=False)
        ridge.fit(features, targets)
        
        # Compute predictions and metrics
        predictions = ridge.predict(features)
        mse = mean_squared_error(targets, predictions)
        r2 = r2_score(targets, predictions)
        
        return {
            'weights': ridge.coef_.T,
            'predictions': predictions,
            'mse': mse,
            'r2_score': r2,
            'n_features': features.shape[1],
            'regularization': regularization
        }
    
    def train_readout_elastic_net(self, reservoir_states: np.ndarray,
                                 targets: np.ndarray,
                                 l1_ratio: float = 0.5,
                                 regularization: float = 1e-6) -> Dict[str, Any]:
        """
        Train readout using Elastic Net regularization.
        
        Combines L1 and L2 regularization for feature selection and stability.
        """
        # Add bias term
        features = np.column_stack([reservoir_states, np.ones(reservoir_states.shape[0])])
        
        # Elastic Net regression
        elastic_net = ElasticNet(alpha=regularization, l1_ratio=l1_ratio, fit_intercept=False)
        elastic_net.fit(features, targets)
        
        # Compute predictions and metrics
        predictions = elastic_net.predict(features)
        mse = mean_squared_error(targets, predictions)
        r2 = r2_score(targets, predictions)
        
        return {
            'weights': elastic_net.coef_.reshape(-1, 1),
            'predictions': predictions,
            'mse': mse,
            'r2_score': r2,
            'l1_ratio': l1_ratio,
            'regularization': regularization,
            'n_active_features': np.sum(elastic_net.coef_ != 0)
        }