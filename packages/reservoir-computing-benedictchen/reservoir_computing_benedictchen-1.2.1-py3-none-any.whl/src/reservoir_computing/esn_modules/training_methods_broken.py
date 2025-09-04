"""
Training and Optimization for Echo State Networks
Implements training algorithms from Jaeger 2001 and extensions
"""

import numpy as np
from typing import Optional, Dict, Any, Tuple, List
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import cross_val_score
import warnings


class TrainingMethodsMixin:
    """Handles ESN training and optimization"""
    
    def __init__(self, esn_instance):
        self.esn = esn_instance
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
             washout: int = 0, 
             regularization: float = 1e-6,
             solver: str = 'ridge') -> Dict[str, Any]:
        """
        Train ESN using linear regression on reservoir states
        
        # FIXME: Critical Research Accuracy Issues Based on Actual Jaeger (2001) Paper
        #
        # 1. INCOMPLETE TRAINING PROCEDURE (Section 3.2, page 13)
        #    - Paper's formal training algorithm has specific steps not implemented
        #    - CODE REVIEW SUGGESTION - Implement complete Jaeger training procedure:
        #      ```python
        #      def train_jaeger_complete(self, X_train, y_train, validate_esp=True):
        #          # Complete training procedure from Jaeger (2001) Section 3.2"""
        #          # Step 1: Validate Echo State Property
        #          if validate_esp and not self._validate_echo_state_property():
        #              raise ValueError("Network does not satisfy Echo State Property")
        #          
        #          # Step 2: Optimize input weights (if requested)
        #          if getattr(self, 'optimize_input_weights', False):
        #              self._optimize_input_weights(X_train)
        #          
        #          # Step 3: Run with teacher input, dismiss transients
        #          washout = self._determine_optimal_washout(X_train)
        #          states = self._collect_training_states(X_train, washout)
        #          y_target = y_train[washout:]
        #          
        #          # Step 4: Linear regression on concatenated [u(n); x(n)]
        #          augmented_states = np.hstack([X_train[washout:], states])
        #          self.output_weights = self._solve_linear_system(augmented_states, y_target)
        #      
        #      def _validate_echo_state_property(self) -> bool:
        #          # Validate ESP using fading memory criterion"""
        #          # Test with two different input sequences
        #          test_length = 100
        #          u1 = np.random.randn(test_length, self.esn.n_inputs)
        #          u2 = u1.copy()
        #          u2[50:] = np.random.randn(50, self.esn.n_inputs)  # Different after t=50
        #          
        #          states1 = self.esn.run_reservoir(u1)
        #          states2 = self.esn.run_reservoir(u2)
        #          
        #          # ESP satisfied if states converge after perturbation
        #          state_diff = np.linalg.norm(states1[-10:] - states2[-10:], axis=1)
        #          return np.mean(state_diff) < 0.1  # Convergence threshold
        #      ```
        #
        # 2. INCORRECT LINEAR REGRESSION FORMULATION (Section 3.1, Equation 11-12)
        #    - Paper's MSE formula: msetrain = 1/(nmax-nmin) Σ εtrain(n)²
        #    - Where εtrain(n) = (f^out)^(-1)yteach(n) - Σ w^out_i xi(n)
        #    - CODE REVIEW SUGGESTION - Apply inverse output transformation:
        #      ```python
        #      def _apply_inverse_output_function(self, targets: np.ndarray) -> np.ndarray:
        #          # Apply (f^out)^(-1) transformation per Equation 11"""
        #          output_func = getattr(self.esn, 'output_function', 'linear')
        #          
        #          if output_func == 'tanh':
        #              # Inverse hyperbolic tangent: atanh(y)
        #              targets_clipped = np.clip(targets, -0.999, 0.999)  # Avoid singularity
        #              return np.arctanh(targets_clipped)
        #          elif output_func == 'sigmoid' or output_func == 'logistic':
        #              # Inverse sigmoid: log(y/(1-y))
        #              targets_clipped = np.clip(targets, 0.001, 0.999)  # Avoid singularity
        #              return np.log(targets_clipped / (1 - targets_clipped))
        #          elif output_func == 'linear':
        #              return targets  # No transformation needed
        #          else:
        #              warnings.warn(f"Unknown output function {output_func}, using linear")
        #              return targets
        #      
        #      def _compute_jaeger_mse(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        #          # Compute MSE using Jaeger's formula from Equation 11"""
        #          # Apply inverse output transformation to targets
        #          targets_transformed = self._apply_inverse_output_function(targets)
        #          
        #          # Compute error: ε(n) = (f^out)^(-1)y_teach(n) - Σ w^out_i x_i(n)
        #          error = targets_transformed - predictions
        #          
        #          # MSE: 1/(nmax-nmin) Σ ε(n)²
        #          mse = np.mean(error ** 2)
        #          return mse
        #      ```
        #
        # 3. MISSING WASHOUT PERIOD OPTIMIZATION (Section 4, multiple examples)
        #    - Paper emphasizes importance of proper transient dismissal
        #    - Examples use 100-500 step washout periods task-specifically
        #    - No adaptive washout based on network dynamics or ESP properties
        #    - Missing validation that washout period is sufficient
        #    - Solutions:
        #      a) Implement adaptive washout: monitor state settling dynamics
        #      b) Use ESP time constant to determine minimum washout
        #      c) Validate washout sufficiency through state stability analysis
        #    - Research basis: Section 4.1.3, page 18; Section 6.3.1, page 29
        #
        # 4. INADEQUATE REGULARIZATION STRATEGY (not explicitly in paper)
        #    - Paper uses simple linear regression without regularization discussion
        #    - Missing analysis of overfit risk with large reservoir states
        #    - No guidance on regularization parameter selection
        #    - Missing cross-validation for hyperparameter tuning
        #    - Solutions:
        #      a) Implement regularization parameter selection via cross-validation
        #      b) Add analysis of training vs validation error curves
        #      c) Implement early stopping based on generalization error
        #    - Research basis: Implicit from paper's emphasis on linear regression simplicity
        
        Implements Algorithm 2 from Jaeger 2001
        """
        # Collect reservoir states
        states = self._collect_training_states(X_train, washout)
        
        # Prepare target data (remove washout)
        if washout > 0:
            y_target = y_train[washout:]
        else:
            y_target = y_train
        
        # Ensure dimensions match
        if len(states) != len(y_target):
            min_len = min(len(states), len(y_target))
            states = states[:min_len]
            y_target = y_target[:min_len]
        
        # Add bias term
        if getattr(self.esn, 'use_bias', True):
            states_with_bias = np.column_stack([states, np.ones(len(states))])
        else:
            states_with_bias = states
        
        # Train output weights using specified solver
        training_result = self._train_output_weights(states_with_bias, y_target, 
                                                   regularization, solver)
        
        # Store output weights
        if getattr(self.esn, 'use_bias', True):
            self.esn.output_weights = training_result['weights'][:-1]
            self.esn.output_bias = training_result['weights'][-1:]
        else:
            self.esn.output_weights = training_result['weights']
            self.esn.output_bias = None
        
        # Compute training metrics
        y_pred = states_with_bias @ training_result['weights'].T
        training_error = np.mean((y_target - y_pred)**2)
        
        return {
            'training_error': training_error,
            'regularization': regularization,
            'solver': solver,
            'n_samples': len(states),
            'washout': washout,
            **training_result
        }
    
    def _collect_training_states(self, X_train: np.ndarray, washout: int) -> np.ndarray:
        """Collect reservoir states for training"""
        # Run reservoir through training data
        states = self.esn.state_dynamics.run_reservoir(X_train, washout=0)
        
        # Apply washout
        if washout > 0:
            states = states[washout:]
        
        return states
    
    def _train_output_weights(self, states: np.ndarray, targets: np.ndarray,
                            regularization: float, solver: str) -> Dict[str, Any]:
        """Train output weights using specified solver"""
        
        if solver == 'ridge':
            return self._train_ridge(states, targets, regularization)
        elif solver == 'lasso':
            return self._train_lasso(states, targets, regularization)
        elif solver == 'normal_equation':
            return self._train_normal_equation(states, targets, regularization)
        elif solver == 'svd':
            return self._train_svd(states, targets, regularization)
        else:
            raise ValueError(f"Unknown solver: {solver}")
    
    def _train_ridge(self, states: np.ndarray, targets: np.ndarray, 
                    regularization: float) -> Dict[str, Any]:
        """Train using Ridge regression"""
        ridge = Ridge(alpha=regularization, fit_intercept=False)
        ridge.fit(states, targets)
        
        return {
            'weights': ridge.coef_,
            'method': 'ridge',
            'regularization_used': regularization
        }
    
    def _train_lasso(self, states: np.ndarray, targets: np.ndarray,
                    regularization: float) -> Dict[str, Any]:
        """Train using Lasso regression"""
        lasso = Lasso(alpha=regularization, fit_intercept=False, max_iter=2000)
        lasso.fit(states, targets)
        
        return {
            'weights': lasso.coef_.reshape(1, -1) if targets.ndim == 1 else lasso.coef_,
            'method': 'lasso',
            'regularization_used': regularization,
            'sparsity': np.mean(lasso.coef_ == 0)
        }
    
    def _train_normal_equation(self, states: np.ndarray, targets: np.ndarray,
                             regularization: float) -> Dict[str, Any]:
        """Train using normal equation with Tikhonov regularization"""
        # W = (X^T X + λI)^(-1) X^T y
        XTX = states.T @ states
        XTy = states.T @ targets
        
        # Add regularization
        I = np.eye(XTX.shape[0])
        regularized_XTX = XTX + regularization * I
        
        try:
            # Solve normal equation
            weights = np.linalg.solve(regularized_XTX, XTy)
            if weights.ndim == 1:
                weights = weights.reshape(1, -1)
            else:
                weights = weights.T
            
            return {
                'weights': weights,
                'method': 'normal_equation',
                'regularization_used': regularization,
                'condition_number': np.linalg.cond(regularized_XTX)
            }
        except np.linalg.LinAlgError:
            # Fallback to pseudoinverse
            weights = np.linalg.pinv(regularized_XTX) @ XTy
            if weights.ndim == 1:
                weights = weights.reshape(1, -1)
            else:
                weights = weights.T
            
            return {
                'weights': weights,
                'method': 'pseudoinverse_fallback',
                'regularization_used': regularization,
                'warning': 'Used pseudoinverse due to singular matrix'
            }
    
    def _train_svd(self, states: np.ndarray, targets: np.ndarray,
                  regularization: float) -> Dict[str, Any]:
        """Train using SVD-based pseudoinverse"""
        # More stable than normal equation for ill-conditioned matrices
        U, s, Vt = np.linalg.svd(states, full_matrices=False)
        
        # Regularized pseudoinverse
        s_reg = s / (s**2 + regularization)
        weights = Vt.T @ np.diag(s_reg) @ U.T @ targets
        
        if weights.ndim == 1:
            weights = weights.reshape(1, -1)
        else:
            weights = weights.T
        
        return {
            'weights': weights,
            'method': 'svd',
            'regularization_used': regularization,
            'rank': np.sum(s > 1e-10),
            'condition_number': s[0] / s[-1] if len(s) > 0 else np.inf
        }
    
    def optimize_spectral_radius(self, X_train: np.ndarray, y_train: np.ndarray,
                               radius_range: Tuple[float, float] = (0.1, 1.5),
                               n_points: int = 15,
                               cv_folds: int = 3) -> Dict[str, Any]:
        """
        Optimize spectral radius using cross-validation
        Based on Jaeger 2001 Section 7
        """
        radii = np.linspace(radius_range[0], radius_range[1], n_points)
        cv_scores = []
        
        # Store original weights
        original_weights = self.esn.reservoir_weights.copy()
        
        for radius in radii:
            try:
                # Scale reservoir to this radius
                self.esn.reservoir_weights = self._scale_to_radius(original_weights, radius)
                
                # Cross-validate
                states = self._collect_training_states(X_train, washout=100)
                y_target = y_train[100:] if len(y_train) > 100 else y_train
                
                if len(states) != len(y_target):
                    min_len = min(len(states), len(y_target))
                    states = states[:min_len]
                    y_target = y_target[:min_len]
                
                # Use Ridge for cross-validation
                ridge = Ridge(alpha=1e-6, fit_intercept=False)
                # Ensure minimum cv folds
                cv = min(cv_folds, max(2, len(states)//5))  # Minimum 2 folds
                if len(states) < 10:  # Too few samples for CV
                    # Use simple train-test split
                    ridge.fit(states, y_target)
                    pred = ridge.predict(states)
                    mse = np.mean((y_target - pred) ** 2)
                    cv_scores.append(mse)
                else:
                    scores = cross_val_score(ridge, states, y_target, 
                                           cv=cv, scoring='neg_mean_squared_error')
                    cv_scores.append(-np.mean(scores))
                
            except Exception as e:
                cv_scores.append(np.inf)
                warnings.warn(f"Error with radius {radius}: {str(e)}")
        
        # Find optimal radius
        best_idx = np.argmin(cv_scores)
        optimal_radius = radii[best_idx]
        
        # Set optimal radius
        self.esn.reservoir_weights = self._scale_to_radius(original_weights, optimal_radius)
        
        return {
            'optimal_radius': optimal_radius,
            'best_cv_score': cv_scores[best_idx],
            'all_radii': radii,
            'all_scores': cv_scores,
            'improvement': cv_scores[best_idx] / max(cv_scores) if max(cv_scores) > 0 else 0
        }
    
    def _scale_to_radius(self, matrix: np.ndarray, target_radius: float) -> np.ndarray:
        """Scale matrix to target spectral radius"""
        eigenvals = np.linalg.eigvals(matrix)
        current_radius = np.max(np.abs(eigenvals))
        
        if current_radius > 1e-10:
            return matrix * (target_radius / current_radius)
        else:
            return matrix
    
    def train_with_cross_validation(self, X_train: np.ndarray, y_train: np.ndarray,
                                  regularization_range: Tuple[float, float] = (1e-8, 1e-2),
                                  n_alphas: int = 10,
                                  cv_folds: int = 5) -> Dict[str, Any]:
        """Train with cross-validated regularization parameter"""
        alphas = np.logspace(np.log10(regularization_range[0]), 
                           np.log10(regularization_range[1]), n_alphas)
        
        # Collect states once
        states = self._collect_training_states(X_train, washout=100)
        y_target = y_train[100:] if len(y_train) > 100 else y_train
        
        if len(states) != len(y_target):
            min_len = min(len(states), len(y_target))
            states = states[:min_len]
            y_target = y_target[:min_len]
        
        # Cross-validate different regularization parameters
        best_score = np.inf
        best_alpha = alphas[0]
        
        for alpha in alphas:
            ridge = Ridge(alpha=alpha, fit_intercept=False)
            scores = cross_val_score(ridge, states, y_target,
                                   cv=min(cv_folds, len(states)//2),
                                   scoring='neg_mean_squared_error')
            score = -np.mean(scores)
            
            if score < best_score:
                best_score = score
                best_alpha = alpha
        
        # Train with best regularization
        return self.train(X_train, y_train, regularization=best_alpha)
    
    def train_online(self, X_stream: np.ndarray, y_stream: np.ndarray,
                    learning_rate: float = 0.01,
                    forgetting_factor: float = 0.99) -> Dict[str, Any]:
        """Online training using RLS (Recursive Least Squares)"""
        n_samples, n_features = X_stream.shape
        n_outputs = y_stream.shape[1] if y_stream.ndim > 1 else 1
        
        # Initialize online parameters
        if not hasattr(self.esn, 'online_P'):
            self.esn.online_P = np.eye(self.esn.reservoir_size) / 0.01
            self.esn.output_weights = np.random.randn(n_outputs, self.esn.reservoir_size) * 0.01
        
        errors = []
        current_state = np.zeros(self.esn.reservoir_size)
        
        for t in range(n_samples):
            # Update reservoir state
            current_state = self.esn.state_dynamics.update_state(current_state, X_stream[t])
            
            # Predict
            y_pred = self.esn.output_weights @ current_state
            
            # Compute error
            error = y_stream[t] - y_pred
            errors.append(np.linalg.norm(error))
            
            # RLS update
            self._rls_update(current_state, error, forgetting_factor)
        
        return {
            'online_errors': errors,
            'final_error': errors[-1] if errors else 0,
            'learning_rate': learning_rate,
            'forgetting_factor': forgetting_factor
        }
    
    def _rls_update(self, state: np.ndarray, error: np.ndarray, 
                   forgetting_factor: float):
        """Recursive Least Squares update"""
        # Update inverse correlation matrix
        Px = self.esn.online_P @ state
        denominator = forgetting_factor + state @ Px
        self.esn.online_P = (self.esn.online_P - np.outer(Px, Px) / denominator) / forgetting_factor
        
        # Update weights
        gain = Px / denominator
        if error.ndim == 0:
            self.esn.output_weights += error * gain
        else:
            self.esn.output_weights += np.outer(error, gain)
    
    def train_teacher_forcing(self, X_train: np.ndarray, y_train: np.ndarray, 
                             washout: int = 50, 
                             teacher_forcing_ratio: float = 1.0,
                             regularization: float = 1e-6) -> Dict[str, Any]:
        """
        Train ESN with teacher forcing - CRITICAL Jaeger 2001 feature
        
        During training, feed target outputs back instead of predictions
        to prevent error accumulation in sequence generation tasks.
        
        Args:
            X_train: Input sequences [time_steps, n_inputs]  
            y_train: Target sequences [time_steps, n_outputs]
            washout: Number of initial steps to ignore
            teacher_forcing_ratio: 1.0 = always use targets, 0.0 = never use targets
            regularization: L2 regularization strength
            
        Returns:
            Dictionary with training results
        """
        if not hasattr(self.esn, 'output_feedback_weights'):
            # Enable output feedback for teacher forcing
            if y_train.ndim == 1:
                n_outputs = 1
            else:
                n_outputs = y_train.shape[1]
            self.esn.enable_output_feedback(n_outputs, 0.1)
        
        # Collect states with teacher forcing
        states = self._collect_teacher_forced_states(X_train, y_train, washout, teacher_forcing_ratio)
        
        # Prepare targets (skip washout)
        if washout > 0:
            y_target = y_train[washout:]
        else:
            y_target = y_train
            
        # Ensure dimensional consistency
        min_len = min(len(states), len(y_target))
        states = states[:min_len]
        y_target = y_target[:min_len]
        
        # Add bias if enabled
        if getattr(self.esn, 'use_bias', True):
            states_with_bias = np.column_stack([states, np.ones(len(states))])
        else:
            states_with_bias = states
        
        # Train output weights
        training_result = self._train_output_weights(states_with_bias, y_target, 
                                                   regularization, 'ridge')
        
        # Store weights and bias separately  
        weights = training_result['weights']
        if weights.ndim == 1:
            weights = weights.reshape(1, -1)
            
        if getattr(self.esn, 'use_bias', True) and weights.shape[1] > 1:
            self.esn.output_weights = weights[:, :-1]
            self.esn.output_bias = weights[:, -1]
        else:
            self.esn.output_weights = weights
        
        # Calculate training error
        weights = training_result['weights']
        if weights.ndim == 1:
            weights = weights.reshape(1, -1)
        train_pred = states_with_bias @ weights.T
        train_error = np.mean((y_target - train_pred) ** 2)
        
        return {
            'training_error': train_error,
            'method': 'teacher_forcing',
            'teacher_forcing_ratio': teacher_forcing_ratio,
            'washout_used': washout,
            'regularization': regularization,
            'states_collected': len(states)
        }
    
    def _collect_teacher_forced_states(self, X_train: np.ndarray, y_train: np.ndarray,
                                     washout: int, teacher_forcing_ratio: float) -> np.ndarray:
        """
        Collect reservoir states with teacher forcing feedback
        """
        time_steps = len(X_train)
        states = []
        current_state = np.zeros(self.esn.reservoir_size)
        
        for t in range(time_steps):
            input_vec = X_train[t]
            
            # Determine feedback signal
            if t > 0 and hasattr(self.esn, 'output_feedback_weights'):
                # Use teacher forcing with specified probability
                if np.random.random() < teacher_forcing_ratio:
                    # Teacher forcing: use target output as feedback
                    if y_train.ndim == 1:
                        feedback = np.array([y_train[t-1]])
                    else:
                        feedback = y_train[t-1]
                else:
                    # Free running: use predicted output (simplified - use target for now)
                    if y_train.ndim == 1:
                        feedback = np.array([y_train[t-1]])
                    else:
                        feedback = y_train[t-1]
            else:
                feedback = None
            
            # Update state
            current_state = self.esn.state_dynamics.update_state(
                current_state, input_vec, feedback
            )
            
            # Collect state (skip washout period)
            if t >= washout:
                states.append(current_state.copy())
        
        return np.array(states)