"""
⚙️ Reservoir Computing - Core Algorithms Module
===============================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Core algorithmic components including reservoir initialization, state updates,
training algorithms, and prediction methods. Contains the essential computational
building blocks for reservoir computing systems.

⚙️ ALGORITHMIC COMPONENTS:
=========================
• Reservoir matrix initialization with spectral radius control
• Input matrix initialization with scaling and sparsity
• State update dynamics with leaky integration
• Ridge regression training with regularization
• Hyperparameter optimization algorithms
• Sequence prediction and generation methods
• Advanced training methods and regularization

🔬 RESEARCH FOUNDATION:
======================
Based on core algorithmic contributions from:
- Jaeger (2001): State update equations and training methods
- Lukoševičius & Jaeger (2009): Initialization and optimization techniques
- Verstraeten et al. (2007): Advanced training and regularization methods
- Schrauwen et al. (2007): Leaky integration and state dynamics

This module represents the core computational algorithms,
split from the 1405-line monolith for specialized algorithmic processing.
"""

import numpy as np
import scipy.sparse as sp
from scipy import linalg, optimize
from scipy.special import expit
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from typing import Optional, Callable, Dict, Any, Tuple, List, Union, Sequence
import warnings
from abc import ABC

# ============================================================================
# RESERVOIR INITIALIZATION ALGORITHMS
# ============================================================================

class ReservoirInitializationMixin(ABC):
    """
    🏗️ Reservoir Matrix Initialization Algorithms
    
    Provides various methods for initializing reservoir weight matrices
    with proper spectral radius control and connectivity patterns.
    """
    
    def initialize_reservoir_matrix(self, n_reservoir: int, 
                                  spectral_radius: float = 0.95,
                                  sparsity: float = 0.1,
                                  distribution: str = 'uniform',
                                  seed: Optional[int] = None) -> np.ndarray:
        """
        🏗️ Initialize Reservoir Weight Matrix
        
        Creates reservoir matrix with controlled spectral radius and sparsity
        following best practices from reservoir computing literature.
        
        Args:
            n_reservoir: Number of reservoir neurons
            spectral_radius: Desired spectral radius (< 1.0 for stability)
            sparsity: Connection sparsity (fraction of non-zero weights)
            distribution: Weight distribution ('uniform', 'normal', 'binary')
            seed: Random seed for reproducibility
            
        Returns:
            np.ndarray: Initialized reservoir matrix (n_reservoir × n_reservoir)
            
        Research Background:
        ===================
        Based on initialization methods from Jaeger (2001) and optimization
        techniques from Lukoševičius & Jaeger (2009) for optimal performance.
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Create sparse connectivity pattern
        n_connections = int(n_reservoir * n_reservoir * sparsity)
        
        if distribution == 'uniform':
            weights = np.random.uniform(-1, 1, n_connections)
        elif distribution == 'normal':
            weights = np.random.normal(0, 1, n_connections)
        elif distribution == 'binary':
            weights = np.random.choice([-1, 1], n_connections)
        else:
            raise ValueError(f"Unknown distribution: {distribution}")
        
        # Create sparse matrix
        row_indices = np.random.choice(n_reservoir, n_connections)
        col_indices = np.random.choice(n_reservoir, n_connections)
        
        W_reservoir = sp.coo_matrix((weights, (row_indices, col_indices)), 
                                   shape=(n_reservoir, n_reservoir))
        W_reservoir = W_reservoir.todense()
        
        # Scale to desired spectral radius
        current_spectral_radius = np.max(np.abs(linalg.eigvals(W_reservoir)))
        if current_spectral_radius > 1e-10:  # Avoid division by zero
            W_reservoir = W_reservoir * (spectral_radius / current_spectral_radius)
        
        return np.array(W_reservoir)
    
    def initialize_input_matrix(self, n_reservoir: int, n_inputs: int,
                               input_scaling: float = 1.0,
                               distribution: str = 'uniform',
                               sparsity: float = 1.0,
                               seed: Optional[int] = None) -> np.ndarray:
        """
        🔌 Initialize Input Weight Matrix
        
        Creates input weight matrix connecting external inputs to reservoir neurons
        with proper scaling and optional sparsity.
        
        Args:
            n_reservoir: Number of reservoir neurons
            n_inputs: Number of input dimensions
            input_scaling: Scale factor for input weights
            distribution: Weight distribution ('uniform', 'normal', 'binary')
            sparsity: Connection sparsity (1.0 = fully connected)
            seed: Random seed for reproducibility
            
        Returns:
            np.ndarray: Input weight matrix (n_reservoir × n_inputs)
            
        Research Background:
        ===================
        Based on input scaling principles from Jaeger (2001) and optimization
        guidelines from reservoir computing best practices literature.
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Generate base weights
        if distribution == 'uniform':
            W_input = np.random.uniform(-1, 1, (n_reservoir, n_inputs))
        elif distribution == 'normal':
            W_input = np.random.normal(0, 1, (n_reservoir, n_inputs))
        elif distribution == 'binary':
            W_input = np.random.choice([-1, 1], (n_reservoir, n_inputs))
        else:
            raise ValueError(f"Unknown distribution: {distribution}")
        
        # Apply sparsity
        if sparsity < 1.0:
            mask = np.random.random((n_reservoir, n_inputs)) < sparsity
            W_input = W_input * mask
        
        # Apply input scaling
        W_input = W_input * input_scaling
        
        return W_input

# ============================================================================
# STATE UPDATE ALGORITHMS
# ============================================================================

class StateUpdateMixin(ABC):
    """
    🌊 State Update Dynamics
    
    Implements various state update methods for reservoir computing
    including standard ESN updates and leaky integration variants.
    """
    
    def update_reservoir_states(self, u: np.ndarray, x: np.ndarray,
                               W_reservoir: np.ndarray, W_input: np.ndarray,
                               activation: Callable = np.tanh,
                               leak_rate: float = 1.0,
                               noise_level: float = 0.0) -> np.ndarray:
        """
        🌊 Update Reservoir States
        
        Implements the core ESN state update equation with optional
        leaky integration and noise injection.
        
        State Update Equation:
        x(n+1) = (1-α)x(n) + α*f(W_reservoir*x(n) + W_input*u(n+1))
        
        Args:
            u: Input vector at current time step
            x: Current reservoir state vector
            W_reservoir: Reservoir weight matrix
            W_input: Input weight matrix
            activation: Activation function (default: tanh)
            leak_rate: Leaky integration parameter α ∈ (0,1]
            noise_level: Additive noise standard deviation
            
        Returns:
            np.ndarray: Updated reservoir state vector
            
        Research Background:
        ===================
        Based on ESN dynamics from Jaeger (2001) Equation 1 and leaky integration
        extensions from Jaeger et al. (2007) for enhanced temporal processing.
        """
        # Ensure input is properly shaped
        if u.ndim == 0:
            u = np.array([u])
        elif u.ndim == 1:
            u = u.reshape(-1)
        
        # Compute pre-activation
        reservoir_input = W_reservoir @ x
        external_input = W_input @ u
        pre_activation = reservoir_input + external_input
        
        # Apply activation function
        activated = activation(pre_activation)
        
        # Leaky integration
        new_state = (1 - leak_rate) * x + leak_rate * activated
        
        # Add noise if specified
        if noise_level > 0:
            noise = np.random.normal(0, noise_level, new_state.shape)
            new_state = new_state + noise
        
        return new_state

# ============================================================================
# TRAINING ALGORITHMS
# ============================================================================

class TrainingMixin(ABC):
    """
    🎓 Reservoir Training Algorithms
    
    Implements various training methods for reservoir readout layers
    including ridge regression, elastic net, and hyperparameter optimization.
    """
    
    def train_readout_ridge(self, reservoir_states: np.ndarray, 
                           targets: np.ndarray,
                           regularization: float = 1e-6,
                           fit_intercept: bool = True) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        🎓 Train Readout Layer with Ridge Regression
        
        Trains the linear readout layer using ridge regression to map
        reservoir states to target outputs.
        
        Args:
            reservoir_states: Reservoir state matrix (T × N)
            targets: Target output matrix (T × D_out)
            regularization: Ridge regularization parameter
            fit_intercept: Whether to fit intercept term
            
        Returns:
            Tuple[np.ndarray, Dict]: (W_out, training_info)
            
        Research Background:
        ===================
        Based on linear regression methods from Jaeger (2001) and regularization
        techniques from machine learning literature for stable readout training.
        """
        # Input validation
        if reservoir_states.shape[0] != targets.shape[0]:
            raise ValueError("States and targets must have same time dimension")
        
        # Ensure targets are 2D
        if targets.ndim == 1:
            targets = targets.reshape(-1, 1)
        
        T, N = reservoir_states.shape
        D_out = targets.shape[1]
        
        try:
            # Use sklearn Ridge regression for numerical stability
            ridge = Ridge(alpha=regularization, fit_intercept=fit_intercept)
            ridge.fit(reservoir_states, targets)
            
            # Extract weights
            W_out = ridge.coef_.T  # Transpose to match (N × D_out) shape
            bias = ridge.intercept_ if fit_intercept else np.zeros(D_out)
            
            # Training predictions for evaluation
            predictions = ridge.predict(reservoir_states)
            
            # Calculate training metrics
            mse = mean_squared_error(targets, predictions)
            r2 = r2_score(targets, predictions, multioutput='uniform_average')
            
            training_info = {
                'mse': mse,
                'r2_score': r2,
                'regularization': regularization,
                'fit_intercept': fit_intercept,
                'n_samples': T,
                'n_features': N,
                'n_outputs': D_out,
                'bias': bias,
                'training_time': 0.0  # Would need timing in full implementation
            }
            
        except Exception as e:
            # Fallback to direct computation if sklearn fails
            warnings.warn(f"Ridge regression failed, using direct computation: {e}")
            
            # Direct ridge regression computation
            if fit_intercept:
                X_extended = np.hstack([reservoir_states, np.ones((T, 1))])
                reg_matrix = regularization * np.eye(N + 1)
                reg_matrix[-1, -1] = 0  # Don't regularize bias term
            else:
                X_extended = reservoir_states
                reg_matrix = regularization * np.eye(N)
            
            try:
                W_extended = linalg.solve(X_extended.T @ X_extended + reg_matrix,
                                        X_extended.T @ targets)
                
                if fit_intercept:
                    W_out = W_extended[:-1]
                    bias = W_extended[-1]
                else:
                    W_out = W_extended
                    bias = np.zeros(D_out)
                
                # Calculate metrics
                predictions = X_extended @ W_extended
                mse = np.mean((targets - predictions) ** 2)
                ss_res = np.sum((targets - predictions) ** 2)
                ss_tot = np.sum((targets - np.mean(targets, axis=0)) ** 2)
                r2 = 1 - (ss_res / (ss_tot + 1e-10))
                
                training_info = {
                    'mse': mse,
                    'r2_score': r2,
                    'regularization': regularization,
                    'fit_intercept': fit_intercept,
                    'n_samples': T,
                    'n_features': N,
                    'n_outputs': D_out,
                    'bias': bias,
                    'method': 'direct_computation'
                }
                
            except Exception as e2:
                raise RuntimeError(f"Both sklearn and direct methods failed: {e2}")
        
        return W_out, training_info
    
    def optimize_hyperparameters(self, reservoir_states: np.ndarray,
                                targets: np.ndarray,
                                param_ranges: Optional[Dict[str, Tuple[float, float]]] = None,
                                cv_folds: int = 5,
                                scoring: str = 'r2',
                                n_trials: int = 50,
                                verbose: bool = True) -> Dict[str, Any]:
        """
        🔧 Optimize Hyperparameters
        
        Performs hyperparameter optimization for reservoir readout training
        using cross-validation and grid search or random search.
        
        Args:
            reservoir_states: Reservoir state matrix
            targets: Target outputs
            param_ranges: Parameter ranges to search
            cv_folds: Number of cross-validation folds
            scoring: Scoring metric ('r2', 'mse', 'mae')
            n_trials: Number of optimization trials
            verbose: Whether to print progress
            
        Returns:
            Dict[str, Any]: Optimization results and best parameters
            
        Research Background:
        ===================
        Based on hyperparameter optimization best practices from machine learning
        literature and reservoir computing parameter tuning guidelines.
        """
        if param_ranges is None:
            param_ranges = {
                'regularization': (1e-8, 1e-2)
            }
        
        from sklearn.model_selection import cross_val_score
        
        best_score = -np.inf if scoring == 'r2' else np.inf
        best_params = {}
        all_results = []
        
        for trial in range(n_trials):
            # Sample random parameters
            params = {}
            for param_name, (low, high) in param_ranges.items():
                if param_name == 'regularization':
                    # Log-uniform sampling for regularization
                    params[param_name] = np.exp(np.random.uniform(np.log(low), np.log(high)))
                else:
                    params[param_name] = np.random.uniform(low, high)
            
            try:
                # Cross-validation with current parameters
                ridge = Ridge(alpha=params['regularization'], fit_intercept=True)
                
                if scoring == 'r2':
                    scores = cross_val_score(ridge, reservoir_states, targets, 
                                           cv=cv_folds, scoring='r2')
                    score = np.mean(scores)
                    is_better = score > best_score
                elif scoring in ['mse', 'mae']:
                    scores = cross_val_score(ridge, reservoir_states, targets,
                                           cv=cv_folds, scoring=f'neg_mean_squared_error')
                    score = -np.mean(scores)  # Convert back to positive
                    is_better = score < best_score
                else:
                    raise ValueError(f"Unknown scoring metric: {scoring}")
                
                if is_better:
                    best_score = score
                    best_params = params.copy()
                
                all_results.append({
                    'params': params.copy(),
                    'score': score,
                    'scores': scores
                })
                
                if verbose and trial % 10 == 0:
                    print(f"Trial {trial+1}/{n_trials}: Best {scoring} = {best_score:.6f}")
                    
            except Exception as e:
                if verbose:
                    print(f"⚠️ Trial {trial+1} failed: {e}")
                continue
        
        # Train final model with best parameters
        final_ridge = Ridge(alpha=best_params['regularization'], fit_intercept=True)
        final_ridge.fit(reservoir_states, targets)
        
        results = {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': all_results,
            'n_trials': len(all_results),
            'cv_folds': cv_folds,
            'scoring': scoring,
            'final_model': final_ridge
        }
        
        if verbose:
            print(f"\n🎯 Optimization Complete!")
            print(f"Best {scoring}: {best_score:.6f}")
            print(f"Best regularization: {best_params['regularization']:.2e}")
        
        return results

# ============================================================================
# PREDICTION ALGORITHMS
# ============================================================================

class PredictionMixin(ABC):
    """
    🔮 Prediction and Generation Algorithms
    
    Implements various prediction methods including sequence prediction
    and autonomous generation for trained reservoir systems.
    """
    
    def predict_sequence(self, initial_states: np.ndarray,
                        input_sequence: np.ndarray,
                        W_reservoir: np.ndarray,
                        W_input: np.ndarray,
                        W_out: np.ndarray,
                        activation: Callable = np.tanh,
                        leak_rate: float = 1.0,
                        washout: int = 0) -> Tuple[np.ndarray, np.ndarray]:
        """
        🔮 Predict Output Sequence
        
        Predicts output sequence given input sequence using trained reservoir.
        
        Args:
            initial_states: Initial reservoir states
            input_sequence: Input sequence (T × D_in)
            W_reservoir: Reservoir weight matrix
            W_input: Input weight matrix  
            W_out: Output weight matrix
            activation: Activation function
            leak_rate: Leaky integration parameter
            washout: Number of initial steps to discard
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (predictions, all_states)
            
        Research Background:
        ===================
        Based on prediction methods from Jaeger (2001) and sequence processing
        techniques from reservoir computing literature.
        """
        T = len(input_sequence)
        n_reservoir = len(initial_states)
        n_outputs = W_out.shape[1]
        
        # Initialize storage
        states = np.zeros((T, n_reservoir))
        predictions = np.zeros((T, n_outputs))
        
        # Current state
        x = initial_states.copy()
        
        for t in range(T):
            # Update reservoir state
            u = input_sequence[t]
            x = self.update_reservoir_states(u, x, W_reservoir, W_input, 
                                           activation, leak_rate)
            states[t] = x
            
            # Compute output
            y = W_out.T @ x  # W_out is (N × D_out), so transpose for (D_out × N) @ (N,)
            predictions[t] = y
        
        # Remove washout period
        if washout > 0:
            predictions = predictions[washout:]
            states = states[washout:]
        
        return predictions, states
    
    def generate_autonomous(self, initial_state: np.ndarray,
                           n_steps: int,
                           W_reservoir: np.ndarray,
                           W_out: np.ndarray,
                           W_feedback: Optional[np.ndarray] = None,
                           activation: Callable = np.tanh,
                           leak_rate: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        🎵 Generate Autonomous Sequence
        
        Generates autonomous sequence using output feedback without external input.
        
        Args:
            initial_state: Initial reservoir state
            n_steps: Number of steps to generate
            W_reservoir: Reservoir weight matrix
            W_out: Output weight matrix
            W_feedback: Feedback weight matrix (optional)
            activation: Activation function
            leak_rate: Leaky integration parameter
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (generated_sequence, states)
            
        Research Background:
        ===================
        Based on autonomous generation methods from Jaeger (2001) Section 3.4
        for closed-loop sequence generation without external driving input.
        """
        n_reservoir = len(initial_state)
        n_outputs = W_out.shape[1]
        
        # Initialize storage
        generated_sequence = np.zeros((n_steps, n_outputs))
        states = np.zeros((n_steps, n_reservoir))
        
        # Current state and output
        x = initial_state.copy()
        y = W_out.T @ x  # Initial output
        
        for t in range(n_steps):
            # Store current output
            generated_sequence[t] = y
            states[t] = x
            
            # Update reservoir state (no external input)
            if W_feedback is not None:
                # Use output feedback
                u_feedback = W_feedback @ y
                pre_activation = W_reservoir @ x + u_feedback
            else:
                # No feedback, only recurrent connections
                pre_activation = W_reservoir @ x
            
            # Apply activation and leaky integration
            x_new = activation(pre_activation)
            x = (1 - leak_rate) * x + leak_rate * x_new
            
            # Compute new output
            y = W_out.T @ x
        
        return generated_sequence, states

# Export main classes
__all__ = ['ReservoirInitializationMixin', 'StateUpdateMixin', 'TrainingMixin', 'PredictionMixin']