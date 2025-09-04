"""
🎯 Training Methods for Echo State Networks - Research Implementation
==================================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module implements training methods for Echo State Networks based on
Jaeger's seminal work and subsequent improvements from the research literature.

Based on:
- Jaeger, H. (2001) "The echo state approach to analyzing and training recurrent neural networks"
- Lukoševičius, M., Jaeger, H. (2009) "Reservoir computing approaches to recurrent neural network training"
"""

import numpy as np
import warnings
from typing import Dict, Any, Optional, Tuple, List, Union
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import KFold
import logging

logger = logging.getLogger(__name__)


class TrainingMethodsMixin:
    # Core Training Methods
    
    def train_output_weights(self, X_train: np.ndarray, y_train: np.ndarray,
                           regularization: float = 1e-8, washout: int = 100,
                           method: str = 'ridge') -> Dict[str, Any]:
        """
        Train ESN output weights using various methods
        """
        # Collect reservoir states
        states = self._collect_training_states(X_train, washout)
        
        # Prepare target (accounting for washout)
        y_target = y_train[washout:] if len(y_train) > washout else y_train
        
        # Ensure compatible dimensions
        if len(y_target) != len(states):
            min_len = min(len(y_target), len(states))
            y_target = y_target[:min_len]
            states = states[:min_len]
        
        # Train using specified method
        if method == 'ridge':
            return self._train_ridge(states, y_target, regularization)
        elif method == 'lasso':
            return self._train_lasso(states, y_target, regularization)
        elif method == 'normal':
            return self._train_normal_equation(states, y_target, regularization)
        elif method == 'svd':
            return self._train_svd(states, y_target, regularization)
        else:
            raise ValueError(f"Unknown training method: {method}")
    
    def _collect_training_states(self, X_train: np.ndarray, washout: int = 100) -> np.ndarray:
        """Collect reservoir states for training"""
        if not hasattr(self, 'run_reservoir'):
            raise AttributeError("ESN must have run_reservoir method")
        
        states = self.run_reservoir(X_train, reset_state=True)
        
        # Apply washout
        if washout > 0 and len(states) > washout:
            return states[washout:]
        return states
    
    def _train_ridge(self, states: np.ndarray, targets: np.ndarray, 
                    regularization: float) -> Dict[str, Any]:
        """Train using Ridge regression"""
        ridge = Ridge(alpha=regularization, fit_intercept=False)
        ridge.fit(states, targets)
        
        self.W_out = ridge.coef_.T if targets.ndim == 1 else ridge.coef_
        
        return {
            'method': 'ridge',
            'regularization': regularization,
            'weights_shape': self.W_out.shape
        }
    
    def _train_lasso(self, states: np.ndarray, targets: np.ndarray,
                    regularization: float) -> Dict[str, Any]:
        """Train using Lasso regression"""
        lasso = Lasso(alpha=regularization, fit_intercept=False, max_iter=1000)
        lasso.fit(states, targets)
        
        self.W_out = lasso.coef_.T if targets.ndim == 1 else lasso.coef_
        
        return {
            'method': 'lasso', 
            'regularization': regularization,
            'weights_shape': self.W_out.shape
        }
    
    def _train_normal_equation(self, states: np.ndarray, targets: np.ndarray,
                              regularization: float) -> Dict[str, Any]:
        """Train using normal equation with Tikhonov regularization"""
        try:
            # Normal equation: W_out = (S^T S + λI)^-1 S^T Y
            S = states
            Y = targets
            
            # Add regularization
            StS = S.T @ S
            identity = np.eye(StS.shape[0]) * regularization
            
            # Solve linear system
            self.W_out = np.linalg.solve(StS + identity, S.T @ Y)
            
            if Y.ndim == 1:
                self.W_out = self.W_out.reshape(-1, 1)
            
            return {
                'method': 'normal_equation',
                'regularization': regularization,
                'condition_number': np.linalg.cond(StS + identity)
            }
        except np.linalg.LinAlgError as e:
            logger.warning(f"Normal equation failed: {e}, falling back to SVD")
            return self._train_svd(states, targets, regularization)
    
    def _train_svd(self, states: np.ndarray, targets: np.ndarray,
                  regularization: float) -> Dict[str, Any]:
        """Train using SVD-based pseudoinverse"""
        try:
            # SVD-based solution with regularization
            U, s, Vh = np.linalg.svd(states, full_matrices=False)
            
            # Regularized pseudoinverse
            s_reg = s / (s**2 + regularization)
            S_pinv = Vh.T @ np.diag(s_reg) @ U.T
            
            self.W_out = S_pinv @ targets
            
            if targets.ndim == 1:
                self.W_out = self.W_out.reshape(-1, 1)
            
            return {
                'method': 'svd',
                'regularization': regularization,
                'singular_values': s,
                'effective_rank': np.sum(s > regularization)
            }
        except Exception as e:
            logger.error(f"SVD training failed: {e}")
            raise
    
    def optimize_spectral_radius(self, X_train: np.ndarray, y_train: np.ndarray,
                               radius_range: Tuple[float, float] = (0.1, 1.5),
                               n_points: int = 20, cv_folds: int = 3) -> Dict[str, Any]:
        """
        Optimize spectral radius using cross-validation
        Based on Jaeger 2001 Section 7
        """
        radii = np.linspace(radius_range[0], radius_range[1], n_points)
        cv_scores = []
        
        # Store original weights
        original_weights = self.W_reservoir.copy()
        
        for radius in radii:
            try:
                # Scale reservoir to this radius
                self.W_reservoir = self._scale_to_radius(original_weights, radius)
                
                # Cross-validate
                states = self._collect_training_states(X_train, washout=100)
                y_target = y_train[100:] if len(y_train) > 100 else y_train
                
                # Ensure compatible dimensions
                min_len = min(len(y_target), len(states))
                y_target = y_target[:min_len]
                states = states[:min_len]
                
                # Cross-validation
                kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
                scores = []
                
                for train_idx, val_idx in kf.split(states):
                    S_train, S_val = states[train_idx], states[val_idx]
                    y_train_fold, y_val_fold = y_target[train_idx], y_target[val_idx]
                    
                    # Train and evaluate
                    W_out = self._solve_output_weights(S_train, y_train_fold)
                    predictions = S_val @ W_out
                    
                    # Calculate MSE
                    mse = np.mean((predictions - y_val_fold)**2)
                    scores.append(mse)
                
                cv_scores.append(np.mean(scores))
                
            except Exception as e:
                logger.warning(f"Optimization failed at radius {radius}: {e}")
                cv_scores.append(float('inf'))
        
        # Find best radius
        best_idx = np.argmin(cv_scores)
        best_radius = radii[best_idx]
        
        # Set optimal radius
        self.W_reservoir = self._scale_to_radius(original_weights, best_radius)
        
        return {
            'best_radius': best_radius,
            'best_score': cv_scores[best_idx],
            'all_radii': radii.tolist(),
            'all_scores': cv_scores
        }
    
    def _scale_to_radius(self, weights: np.ndarray, target_radius: float) -> np.ndarray:
        """Scale matrix to target spectral radius"""
        eigenvals = np.linalg.eigvals(weights)
        current_radius = np.max(np.abs(eigenvals))
        
        if current_radius > 0:
            scaling = target_radius / current_radius
            return weights * scaling
        return weights
    
    def train_with_cv_regularization(self, X_train: np.ndarray, y_train: np.ndarray,
                                   reg_range: Tuple[float, float] = (1e-8, 1e-2),
                                   n_points: int = 20, cv_folds: int = 3) -> Dict[str, Any]:
        """Train with cross-validated regularization parameter"""
        reg_values = np.logspace(np.log10(reg_range[0]), np.log10(reg_range[1]), n_points)
        cv_scores = []
        
        # Collect states once
        states = self._collect_training_states(X_train, washout=100)
        y_target = y_train[100:] if len(y_train) > 100 else y_train
        
        # Ensure compatible dimensions
        min_len = min(len(y_target), len(states))
        y_target = y_target[:min_len]
        states = states[:min_len]
        
        # Cross-validate each regularization value
        for reg in reg_values:
            kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
            scores = []
            
            for train_idx, val_idx in kf.split(states):
                S_train, S_val = states[train_idx], states[val_idx]
                y_train_fold, y_val_fold = y_target[train_idx], y_target[val_idx]
                
                # Train with this regularization
                W_out = self._solve_output_weights(S_train, y_train_fold, reg)
                predictions = S_val @ W_out
                
                # Calculate validation error
                mse = np.mean((predictions - y_val_fold)**2)
                scores.append(mse)
            
            cv_scores.append(np.mean(scores))
        
        # Find best regularization
        best_idx = np.argmin(cv_scores)
        best_reg = reg_values[best_idx]
        
        # Train with best regularization
        self.W_out = self._solve_output_weights(states, y_target, best_reg)
        
        return {
            'best_regularization': best_reg,
            'best_score': cv_scores[best_idx],
            'regularization_values': reg_values.tolist(),
            'cv_scores': cv_scores
        }
    
    def _solve_output_weights(self, states: np.ndarray, targets: np.ndarray,
                            regularization: float = 1e-8) -> np.ndarray:
        """Solve for output weights using regularized least squares"""
        try:
            S = states
            Y = targets
            
            # Normal equation with regularization
            StS = S.T @ S
            identity = np.eye(StS.shape[0]) * regularization
            W_out = np.linalg.solve(StS + identity, S.T @ Y)
            
            if Y.ndim == 1:
                W_out = W_out.reshape(-1, 1)
            
            return W_out
            
        except np.linalg.LinAlgError:
            # Fallback to SVD
            U, s, Vh = np.linalg.svd(states, full_matrices=False)
            s_reg = s / (s**2 + regularization)
            S_pinv = Vh.T @ np.diag(s_reg) @ U.T
            W_out = S_pinv @ targets
            
            if targets.ndim == 1:
                W_out = W_out.reshape(-1, 1)
                
            return W_out