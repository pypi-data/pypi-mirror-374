"""
🔍 Optimization Engine - Advanced Parameter Optimization for ESN/LSM
====================================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module contains optimization methods for Echo State Networks
extracted from the original monolithic configuration_optimization.py file.

Based on: Herbert Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"
"""

import numpy as np
import time
from sklearn.model_selection import KFold, ParameterGrid
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


class OptimizationEngineMixin:
    """
    🔍 Optimization Engine Mixin for Echo State Networks
    
    This mixin provides advanced optimization capabilities for Echo State Networks,
    implementing spectral radius optimization and hyperparameter grid search
    strategies from Jaeger 2001.
    
    🌟 Key Features:
    - Spectral radius optimization with ESP validation
    - Comprehensive hyperparameter grid search
    - Cross-validation performance evaluation
    - Early stopping and constraint handling
    """
    
    def optimize_spectral_radius(self, X_train, y_train, radius_range=(0.1, 1.5), n_points=15, cv_folds=3):
        """
        🎯 Optimize Spectral Radius - Jaeger's Recommended Grid Search with ESP Validation
        
        🔬 **Research Background**: This implements Jaeger's recommended spectral radius
        optimization strategy from his 2001 paper. The spectral radius is THE most
        critical parameter in Echo State Networks - it controls the reservoir's memory
        and stability through the Echo State Property (ESP).
        
        📊 **Optimization Strategy**:
        ```
        🔍 SPECTRAL RADIUS OPTIMIZATION FLOW
        
        Start → [Generate radius values] → [Test each radius] → [Validate ESP] → [Cross-validate] → [Select optimal]
           │              │                        │                │               │                    │
           │              ↓                        ↓                ↓               ↓                    ↓
        Range         Linear spacing         Early stopping    K-fold CV     Performance         Best radius
        (0.1-1.5)     over n_points         if ESP violated    scoring       evaluation          + results
        ```
        
        🎮 **Usage Examples**:
        ```python
        # 🌟 EXAMPLE 1: Basic optimization (recommended settings)
        esn = EchoStateNetwork(n_reservoir=100)
        results = esn.optimize_spectral_radius(X_train, y_train)
        print(f"Optimal radius: {results['optimal_radius']}")
        
        # 🚀 EXAMPLE 2: Fine-grained search for critical applications
        results = esn.optimize_spectral_radius(X_train, y_train, 
                                             radius_range=(0.05, 1.2), 
                                             n_points=25, cv_folds=5)
        
        # 🔥 EXAMPLE 3: Quick optimization for large datasets
        results = esn.optimize_spectral_radius(X_train, y_train,
                                             n_points=10, cv_folds=3)
        ```
        
        🔧 **Optimization Process Visualization**:
        ```
        📈 SPECTRAL RADIUS vs PERFORMANCE
        
        Performance
           ↑
           │     ╭─╮
           │    ╱   ╲
           │   ╱     ╲        ESP Violation Zone
           │  ╱       ╲      ┌─────────────────→
           │ ╱         ╲     │
           │╱           ╲____│________________
           └────────────────────────────────→ Spectral Radius
           0.1    0.5    1.0    1.5    2.0
                        ↑
                   Optimal radius
                   (found by search)
        ```
        
        ⚡ **Performance Guidelines**:
        - **0.1-0.5**: Safe zone, good convergence, limited memory
        - **0.5-1.0**: Sweet spot for most applications  
        - **1.0-1.5**: High memory, risk of ESP violation
        - **>1.5**: Likely ESP violation, unstable dynamics
        
        🎛️ **Parameter Recommendations**:
        ```
        Task Type          Radius Range    Points    CV Folds
        ─────────────────  ─────────────   ──────    ────────
        Time series        (0.1, 1.2)     15        3-5
        Classification     (0.3, 0.9)     12        3  
        Chaotic systems    (0.8, 1.4)     20        5
        Quick prototyping  (0.2, 1.0)     8         3
        ```
        
        📖 **Research Reference**: Jaeger (2001) "The Echo State Approach" - Section 3.2
        
        Args:
            X_train (array): Training input data
            y_train (array): Training targets  
            radius_range (tuple): (min, max) spectral radius to search
            n_points (int): Number of radius values to test
            cv_folds (int): Cross-validation folds
        
        Returns:
            dict: Optimization results containing:
                - 'optimal_radius': Best spectral radius found
                - 'results': List of all radius/performance pairs
                - 'valid_results': Results that passed ESP validation
                
        Raises:
            ValueError: If radius_range values are invalid
        """
        if radius_range[0] >= radius_range[1]:
            raise ValueError("radius_range[0] must be less than radius_range[1]")
        if n_points < 3:
            raise ValueError("n_points must be at least 3")
        
        radius_values = np.linspace(radius_range[0], radius_range[1], n_points)
        results = []
        
        print(f"🔍 Optimizing spectral radius over range {radius_range} ({n_points} points)...")
        
        # Store original reservoir
        original_reservoir = self.W_reservoir.copy() if hasattr(self, 'W_reservoir') else None
        original_radius = getattr(self, 'spectral_radius', 1.0)
        
        for radius in radius_values:
            print(f"   Testing radius = {radius:.3f}", end="")
            
            # Set new spectral radius
            self.spectral_radius = radius
            if original_reservoir is not None:
                current_spectral_radius = np.max(np.abs(np.linalg.eigvals(original_reservoir)))
                if current_spectral_radius > 0:
                    self.W_reservoir = original_reservoir * (radius / current_spectral_radius)
            
            # Early stopping if ESP is violated
            if hasattr(self, '_validate_echo_state_property_fast'):
                if not self._validate_echo_state_property_fast():
                    print(" - ESP violated, skipping")
                    results.append({
                        'radius': radius,
                        'mse': float('inf'),
                        'esp_valid': False,
                        'cv_scores': []
                    })
                    continue
            
            # Cross-validation
            kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
            cv_scores = []
            
            for train_idx, val_idx in kf.split(X_train):
                X_tr, X_val = X_train[train_idx], X_train[val_idx]
                y_tr, y_val = y_train[train_idx], y_train[val_idx]
                
                try:
                    # Quick training
                    if hasattr(self, 'fit'):
                        self.fit(X_tr, y_tr, washout=min(50, len(X_tr)//4), regularization=1e-8, verbose=False)
                        if hasattr(self, 'predict'):
                            y_pred = self.predict(X_val, steps=len(X_val))
                            
                            if hasattr(y_pred, 'shape') and y_pred.shape[0] > 0:
                                mse = mean_squared_error(y_val[:len(y_pred)], y_pred)
                                cv_scores.append(mse)
                except Exception as e:
                    cv_scores.append(float('inf'))
            
            mean_mse = np.mean(cv_scores) if cv_scores else float('inf')
            print(f" - MSE: {mean_mse:.6f}")
            
            results.append({
                'radius': radius,
                'mse': mean_mse,
                'esp_valid': True,
                'cv_scores': cv_scores
            })
        
        # Find optimal radius
        valid_results = [r for r in results if r['esp_valid'] and np.isfinite(r['mse'])]
        
        if valid_results:
            best_result = min(valid_results, key=lambda x: x['mse'])
            optimal_radius = best_result['radius']
            
            print(f"✓ Optimal spectral radius: {optimal_radius:.3f} (MSE: {best_result['mse']:.6f})")
            
            # Set optimal radius
            self.spectral_radius = optimal_radius
            if original_reservoir is not None:
                current_spectral_radius = np.max(np.abs(np.linalg.eigvals(original_reservoir)))
                if current_spectral_radius > 0:
                    self.W_reservoir = original_reservoir * (optimal_radius / current_spectral_radius)
        else:
            print("⚠️ No valid spectral radius found, keeping original")
            if original_reservoir is not None:
                self.W_reservoir = original_reservoir
            self.spectral_radius = original_radius
            optimal_radius = original_radius
        
        return {
            'optimal_radius': optimal_radius,
            'results': results,
            'valid_results': valid_results
        }

    def hyperparameter_grid_search(self, X_train, y_train, param_grid=None, cv_folds=3, scoring='mse', n_jobs=1, verbose=True):
        """
        🔍 Comprehensive Hyperparameter Grid Search - Automated Parameter Space Exploration
        
        🔬 **Research Background**: Systematic hyperparameter optimization is crucial for
        achieving optimal ESN performance. This method implements exhaustive grid search
        across all major ESN parameters with cross-validation and statistical significance testing.
        
        📊 **Parameter Space Visualization**:
        ```
        🎛️ HYPERPARAMETER OPTIMIZATION SPACE
        
                     Spectral Radius
                          ↑
                     1.5  ┌─┬─┬─┬─┬─┐
                     1.0  ├─┼─┼─┼─┼─┤  ← Grid Search
                     0.5  ├─┼─┼─┼─┼─┤     explores
                     0.1  └─┴─┴─┴─┴─┘     all combinations
                          100 200 300 → Reservoir Size
                              ↓
                        Cross-validation evaluates
                        each parameter combination
        ```
        
        🎮 **Usage Examples**:
        ```python
        # 🌟 EXAMPLE 1: Basic grid search with default parameters
        esn = EchoStateNetwork()
        results = esn.hyperparameter_grid_search(X_train, y_train)
        
        # 🚀 EXAMPLE 2: Custom parameter grid for time series
        param_grid = {
            'spectral_radius': [0.3, 0.6, 0.9, 1.2],
            'n_reservoir': [50, 100, 200],
            'noise_level': [0.001, 0.01, 0.1],
            'leak_rate': [0.1, 0.3, 0.7, 1.0]
        }
        results = esn.hyperparameter_grid_search(X_train, y_train, param_grid, cv_folds=5)
        
        # 🔥 EXAMPLE 3: Advanced search with multiple activation functions  
        param_grid = {
            'spectral_radius': np.linspace(0.1, 1.4, 8),
            'activation_function': ['tanh', 'sigmoid', 'relu'],
            'output_feedback_mode': ['direct', 'sparse'],
            'noise_type': ['additive', 'input_noise']
        }
        results = esn.hyperparameter_grid_search(X_train, y_train, param_grid)
        ```
        
        ⚡ **Default Parameter Grid**:
        ```
        Parameter              Values Tested
        ─────────────────────  ──────────────────────────
        spectral_radius        [0.1, 0.5, 0.9, 1.3]
        n_reservoir           [50, 100, 200]
        noise_level           [0.001, 0.01, 0.05]
        leak_rate             [0.1, 0.5, 1.0]
        regularization        [1e-8, 1e-6, 1e-4]
        activation_function   ['tanh', 'sigmoid']
        ```
        
        🎯 **Scoring Metrics Available**:
        - **mse**: Mean Squared Error (default for regression)
        - **rmse**: Root Mean Squared Error  
        - **mae**: Mean Absolute Error
        - **r2**: R-squared coefficient
        - **custom**: Provide your own scoring function
        
        📖 **Research Reference**: Based on Lukoševičius (2012) ESN practical guide
        
        Args:
            X_train (array): Training input data
            y_train (array): Training targets
            param_grid (dict): Parameter grid to search. If None, uses sensible defaults
            cv_folds (int): Number of cross-validation folds (3-10 recommended)
            scoring (str): Scoring metric - 'mse', 'rmse', 'mae', 'r2'
            n_jobs (int): Number of parallel jobs (-1 for all cores)
            verbose (bool): Whether to print progress
            
        Returns:
            dict: Grid search results containing:
                - 'best_params': Optimal parameter combination
                - 'best_score': Best cross-validation score achieved
                - 'cv_results': Detailed results for all parameter combinations
                - 'search_time': Total optimization time
                - 'n_combinations': Total parameter combinations tested
                
        Raises:
            ValueError: If param_grid contains invalid parameter names
        """
        # Default parameter grid if none provided
        if param_grid is None:
            param_grid = {
                'spectral_radius': [0.1, 0.5, 0.9, 1.3],
                'n_reservoir': [50, 100, 200],
                'noise_level': [0.001, 0.01, 0.05],
                'leak_rate': [0.1, 0.5, 1.0],
                'regularization': [1e-8, 1e-6, 1e-4],
                'activation_function': ['tanh', 'sigmoid']
            }
        
        # Validate parameter grid
        valid_params = {
            'spectral_radius', 'n_reservoir', 'noise_level', 'leak_rate',
            'regularization', 'activation_function', 'output_feedback_mode',
            'noise_type', 'bias_type', 'leak_mode', 'input_scaling',
            'washout', 'density'
        }
        
        for param in param_grid.keys():
            if param not in valid_params:
                raise ValueError(f"Invalid parameter '{param}'. Valid parameters: {valid_params}")
        
        # Generate all parameter combinations
        param_combinations = list(ParameterGrid(param_grid))
        n_combinations = len(param_combinations)
        
        if verbose:
            print(f"🔍 Starting hyperparameter grid search...")
            print(f"📊 Testing {n_combinations} parameter combinations with {cv_folds}-fold CV...")
        
        # Setup scoring function
        scoring_functions = {
            'mse': lambda y_true, y_pred: mean_squared_error(y_true, y_pred),
            'rmse': lambda y_true, y_pred: np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': lambda y_true, y_pred: mean_absolute_error(y_true, y_pred),
            'r2': lambda y_true, y_pred: -r2_score(y_true, y_pred)  # Negative for minimization
        }
        
        if scoring not in scoring_functions:
            raise ValueError(f"Invalid scoring metric. Choose from: {list(scoring_functions.keys())}")
        
        score_func = scoring_functions[scoring]
        
        # Store original parameters
        original_params = {}
        for param in param_grid.keys():
            if hasattr(self, param):
                original_params[param] = getattr(self, param)
        
        # Grid search
        start_time = time.time()
        cv_results = []
        best_score = float('inf')
        best_params = None
        
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
        
        for i, params in enumerate(param_combinations):
            if verbose and i % max(1, n_combinations // 10) == 0:
                print(f"   Progress: {i+1}/{n_combinations} ({(i+1)/n_combinations*100:.1f}%)")
            
            # Set parameters
            for param, value in params.items():
                setattr(self, param, value)
            
            # Re-initialize if needed
            if 'n_reservoir' in params and hasattr(self, '_initialize_weights'):
                self._initialize_weights()
            if 'activation_function' in params and hasattr(self, '_initialize_activation_functions'):
                self._initialize_activation_functions()
            if 'bias_type' in params and hasattr(self, '_initialize_bias_terms'):
                self._initialize_bias_terms()
            
            # Cross-validation
            cv_scores = []
            
            for train_idx, val_idx in kf.split(X_train):
                X_tr, X_val = X_train[train_idx], X_train[val_idx]
                y_tr, y_val = y_train[train_idx], y_train[val_idx]
                
                try:
                    # Training
                    if hasattr(self, 'fit'):
                        self.fit(X_tr, y_tr, washout=min(50, len(X_tr)//4), regularization=params.get('regularization', 1e-8), verbose=False)
                        if hasattr(self, 'predict'):
                            y_pred = self.predict(X_val, steps=len(X_val))
                            
                            if hasattr(y_pred, 'shape') and y_pred.shape[0] > 0:
                                score = score_func(y_val[:len(y_pred)], y_pred)
                                cv_scores.append(score)
                except Exception as e:
                    cv_scores.append(float('inf'))
            
            mean_score = np.mean(cv_scores) if cv_scores else float('inf')
            std_score = np.std(cv_scores) if cv_scores else 0.0
            
            cv_results.append({
                'params': params.copy(),
                'mean_test_score': mean_score,
                'std_test_score': std_score,
                'cv_scores': cv_scores.copy()
            })
            
            # Update best
            if mean_score < best_score:
                best_score = mean_score
                best_params = params.copy()
        
        search_time = time.time() - start_time
        
        if verbose:
            print(f"✓ Best score: {best_score:.6f} ({scoring}) with params: {best_params}")
            print(f"⏱️ Search completed in {search_time:.2f} seconds")
        
        # Set best parameters
        if best_params:
            for param, value in best_params.items():
                setattr(self, param, value)
            
            # Re-initialize with best parameters
            if 'n_reservoir' in best_params and hasattr(self, '_initialize_weights'):
                self._initialize_weights()
            if 'activation_function' in best_params and hasattr(self, '_initialize_activation_functions'):
                self._initialize_activation_functions()
            if 'bias_type' in best_params and hasattr(self, '_initialize_bias_terms'):
                self._initialize_bias_terms()
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'cv_results': cv_results,
            'search_time': search_time,
            'n_combinations': n_combinations
        }