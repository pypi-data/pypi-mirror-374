"""
🔧 Reservoir Computing - Core Utilities Module
==============================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Utility functions, factory methods, and optimization utilities for reservoir computing.
Provides high-level convenience functions, parameter optimization, and system utilities
for easy ESN creation and management.

🔧 UTILITY FUNCTIONS:
====================
• Factory functions for easy ESN creation
• Hyperparameter optimization utilities
• System validation and diagnostic tools
• Data preprocessing and analysis utilities
• Performance evaluation and benchmarking
• Configuration management and presets

🔬 RESEARCH FOUNDATION:
======================
Based on practical implementation guidelines from:
- Lukoševičius & Jaeger (2009): Practical ESN implementation guide
- Jaeger (2001): Original implementation recommendations
- Reservoir computing best practices from literature
- Machine learning utility patterns and conventions

This module represents utility and convenience functions,
split from the 1405-line monolith for specialized system utilities.
"""

import numpy as np
from scipy import optimize
from sklearn.model_selection import ParameterGrid
from sklearn.metrics import mean_squared_error, r2_score
from typing import Optional, Dict, Any, List, Union, Tuple, Callable
import warnings
import time

# Import network classes (these will be available through the parent package)
# from .core_networks import EchoStateNetwork, DeepEchoStateNetwork, OnlineEchoStateNetwork

# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_echo_state_network(task_type: str = 'regression',
                             complexity: str = 'medium',
                             reservoir_size: Optional[int] = None,
                             random_state: Optional[int] = None,
                             **custom_params) -> 'EchoStateNetwork':
    """
    🏭 Factory Function for Echo State Network Creation
    
    Creates pre-configured ESN instances optimized for different task types
    and complexity levels based on reservoir computing best practices.
    
    Args:
        task_type: Type of task ('regression', 'classification', 'generation')
        complexity: Complexity level ('simple', 'medium', 'complex')
        reservoir_size: Number of reservoir neurons (auto-sized if None)
        random_state: Random seed for reproducibility
        **custom_params: Override any default parameters
        
    Returns:
        EchoStateNetwork: Configured ESN instance
        
    Research Background:
    ===================
    Parameter presets based on empirical findings from Lukoševičius & Jaeger (2009)
    and optimization guidelines from reservoir computing literature.
    """
    # Base parameter configurations
    configs = {
        'simple': {
            'n_reservoir': reservoir_size or 50,
            'spectral_radius': 0.8,
            'sparsity': 0.1,
            'input_scaling': 1.0,
            'regularization': 1e-4,
            'leak_rate': 1.0,
            'washout': 10
        },
        'medium': {
            'n_reservoir': reservoir_size or 100,
            'spectral_radius': 0.95,
            'sparsity': 0.1,
            'input_scaling': 1.0,
            'regularization': 1e-6,
            'leak_rate': 0.9,
            'washout': 50
        },
        'complex': {
            'n_reservoir': reservoir_size or 200,
            'spectral_radius': 0.99,
            'sparsity': 0.05,
            'input_scaling': 0.8,
            'regularization': 1e-8,
            'leak_rate': 0.8,
            'washout': 100
        }
    }
    
    # Task-specific adjustments
    task_adjustments = {
        'regression': {},
        'classification': {
            'activation': np.tanh,
            'regularization': 1e-4  # More regularization for classification
        },
        'generation': {
            'spectral_radius': 0.98,  # Higher for generation tasks
            'leak_rate': 0.95,
            'washout': 200
        }
    }
    
    # Get base configuration
    if complexity not in configs:
        raise ValueError(f"Unknown complexity: {complexity}. Use 'simple', 'medium', or 'complex'")
    
    params = configs[complexity].copy()
    
    # Apply task-specific adjustments
    if task_type in task_adjustments:
        params.update(task_adjustments[task_type])
    
    # Apply custom parameter overrides
    params.update(custom_params)
    
    # Add random state
    if random_state is not None:
        params['random_state'] = random_state
    
    # Import here to avoid circular imports
    from .core_networks import EchoStateNetwork
    
    return EchoStateNetwork(**params)

def create_optimized_esn(X_train: np.ndarray, y_train: np.ndarray,
                        X_val: Optional[np.ndarray] = None,
                        y_val: Optional[np.ndarray] = None,
                        optimization_budget: int = 50,
                        random_state: Optional[int] = None,
                        verbose: bool = True) -> Tuple['EchoStateNetwork', Dict[str, Any]]:
    """
    🎯 Create Optimized ESN with Automatic Hyperparameter Tuning
    
    Creates and optimizes an ESN using automated hyperparameter search
    tailored to the specific dataset characteristics.
    
    Args:
        X_train: Training input data
        y_train: Training target data
        X_val: Validation input data (uses train if None)
        y_val: Validation target data (uses train if None)
        optimization_budget: Number of hyperparameter configurations to try
        random_state: Random seed for reproducibility
        verbose: Whether to print optimization progress
        
    Returns:
        Tuple[EchoStateNetwork, Dict]: (optimized_esn, optimization_results)
        
    Research Background:
    ===================
    Optimization strategy based on automated hyperparameter tuning methods
    and reservoir computing parameter sensitivity analysis from literature.
    """
    # Use training data for validation if validation set not provided
    if X_val is None or y_val is None:
        X_val, y_val = X_train, y_train
        
    # Infer dataset characteristics
    data_complexity = _analyze_dataset_complexity(X_train, y_train)
    
    # Define search space based on dataset characteristics
    param_space = _get_adaptive_search_space(data_complexity, optimization_budget)
    
    best_score = -np.inf
    best_params = None
    best_esn = None
    optimization_history = []
    
    if verbose:
        print(f"🎯 Optimizing ESN with {optimization_budget} trials...")
        print(f"📊 Dataset complexity: {data_complexity['category']}")
    
    for trial, params in enumerate(param_space):
        try:
            # Create ESN with current parameters
            esn = create_echo_state_network(random_state=random_state, **params)
            
            # Train
            start_time = time.time()
            esn.fit(X_train, y_train)
            train_time = time.time() - start_time
            
            # Evaluate
            y_pred = esn.predict(X_val)
            score = r2_score(y_val, y_pred, multioutput='uniform_average')
            mse = mean_squared_error(y_val, y_pred)
            
            # Track results
            result = {
                'trial': trial,
                'params': params.copy(),
                'score': score,
                'mse': mse,
                'train_time': train_time
            }
            optimization_history.append(result)
            
            # Update best
            if score > best_score:
                best_score = score
                best_params = params.copy()
                best_esn = esn
            
            if verbose and (trial + 1) % 10 == 0:
                print(f"Trial {trial + 1}/{optimization_budget}: "
                      f"Best R² = {best_score:.4f}")
                
        except Exception as e:
            if verbose:
                print(f"⚠️ Trial {trial} failed: {e}")
            continue
    
    # Prepare results
    optimization_results = {
        'best_score': best_score,
        'best_params': best_params,
        'optimization_history': optimization_history,
        'dataset_complexity': data_complexity,
        'n_trials': len(optimization_history)
    }
    
    if verbose:
        print(f"✅ Optimization complete!")
        print(f"Best R²: {best_score:.4f}")
        print(f"Best parameters: {best_params}")
    
    return best_esn, optimization_results

# ============================================================================
# OPTIMIZATION UTILITIES
# ============================================================================

def optimize_esn_hyperparameters(X: np.ndarray, y: np.ndarray,
                                param_grid: Optional[Dict[str, List]] = None,
                                cv_folds: int = 5,
                                scoring: str = 'r2',
                                n_jobs: int = 1,
                                verbose: bool = True) -> Dict[str, Any]:
    """
    🔧 Comprehensive Hyperparameter Optimization
    
    Performs systematic hyperparameter optimization using cross-validation
    and comprehensive parameter grid search.
    
    Args:
        X: Input data
        y: Target data
        param_grid: Parameter grid (uses default if None)
        cv_folds: Number of cross-validation folds
        scoring: Scoring metric ('r2', 'mse', 'mae')
        n_jobs: Number of parallel jobs (not implemented)
        verbose: Whether to print progress
        
    Returns:
        Dict[str, Any]: Comprehensive optimization results
        
    Research Background:
    ===================
    Grid search methodology adapted for reservoir computing with parameter
    ranges based on empirical studies and theoretical considerations.
    """
    # Default parameter grid based on literature recommendations
    if param_grid is None:
        param_grid = {
            'n_reservoir': [50, 100, 200],
            'spectral_radius': [0.8, 0.9, 0.95, 0.99],
            'sparsity': [0.05, 0.1, 0.2],
            'input_scaling': [0.5, 1.0, 1.5],
            'regularization': [1e-8, 1e-6, 1e-4, 1e-2],
            'leak_rate': [0.8, 0.9, 1.0]
        }
    
    # Generate parameter combinations
    param_combinations = list(ParameterGrid(param_grid))
    n_combinations = len(param_combinations)
    
    if verbose:
        print(f"🔧 Testing {n_combinations} parameter combinations with {cv_folds}-fold CV...")
    
    results = []
    best_score = -np.inf if scoring == 'r2' else np.inf
    best_params = None
    
    for i, params in enumerate(param_combinations):
        try:
            # Cross-validation scores
            cv_scores = []
            
            # Simple K-fold CV (manual implementation for compatibility)
            n_samples = len(X)
            fold_size = n_samples // cv_folds
            
            for fold in range(cv_folds):
                # Create train/val splits
                val_start = fold * fold_size
                val_end = (fold + 1) * fold_size if fold < cv_folds - 1 else n_samples
                
                val_idx = np.arange(val_start, val_end)
                train_idx = np.concatenate([np.arange(0, val_start), np.arange(val_end, n_samples)])
                
                if len(train_idx) == 0 or len(val_idx) == 0:
                    continue
                
                # Train and evaluate
                esn = create_echo_state_network(**params)
                esn.fit(X[train_idx], y[train_idx])
                
                y_pred = esn.predict(X[val_idx])
                
                if scoring == 'r2':
                    score = r2_score(y[val_idx], y_pred, multioutput='uniform_average')
                elif scoring == 'mse':
                    score = -mean_squared_error(y[val_idx], y_pred)  # Negative for maximization
                else:
                    raise ValueError(f"Unknown scoring: {scoring}")
                
                cv_scores.append(score)
            
            # Aggregate CV results
            mean_score = np.mean(cv_scores)
            std_score = np.std(cv_scores)
            
            result = {
                'params': params.copy(),
                'mean_score': mean_score,
                'std_score': std_score,
                'cv_scores': cv_scores
            }
            results.append(result)
            
            # Update best
            is_better = (mean_score > best_score) if scoring == 'r2' else (mean_score > best_score)
            if is_better:
                best_score = mean_score
                best_params = params.copy()
            
            if verbose and (i + 1) % max(1, n_combinations // 10) == 0:
                progress = (i + 1) / n_combinations * 100
                print(f"Progress: {progress:.1f}% | Best {scoring}: {best_score:.4f}")
                
        except Exception as e:
            if verbose:
                print(f"⚠️ Parameter combination {i+1} failed: {e}")
            continue
    
    # Sort results by score
    results.sort(key=lambda x: x['mean_score'], reverse=(scoring == 'r2'))
    
    optimization_results = {
        'best_params': best_params,
        'best_score': best_score,
        'all_results': results,
        'param_grid': param_grid,
        'cv_folds': cv_folds,
        'scoring': scoring,
        'n_combinations_tested': len(results)
    }
    
    if verbose:
        print(f"\n✅ Optimization complete!")
        print(f"Best {scoring}: {best_score:.4f}")
        print(f"Best parameters: {best_params}")
    
    return optimization_results

# ============================================================================
# DIAGNOSTIC AND ANALYSIS UTILITIES
# ============================================================================

def _analyze_dataset_complexity(X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """📊 Analyze dataset complexity to inform parameter selection"""
    T, D_in = X.shape if X.ndim == 2 else (X.shape[1], X.shape[2])
    D_out = y.shape[1] if y.ndim > 1 else 1
    
    # Basic statistics
    input_variance = np.var(X)
    output_variance = np.var(y)
    
    # Temporal characteristics (if time series)
    if T > 10:
        # Autocorrelation as proxy for temporal complexity
        y_flat = y.flatten() if y.ndim > 1 else y
        autocorr = np.corrcoef(y_flat[:-1], y_flat[1:])[0, 1] if len(y_flat) > 1 else 0
    else:
        autocorr = 0
    
    # Determine complexity category
    if T < 100 and D_in <= 5 and input_variance < 1.0:
        category = 'simple'
    elif T < 500 and D_in <= 20 and abs(autocorr) < 0.7:
        category = 'medium'
    else:
        category = 'complex'
    
    return {
        'category': category,
        'sequence_length': T,
        'input_dimensions': D_in,
        'output_dimensions': D_out,
        'input_variance': input_variance,
        'output_variance': output_variance,
        'temporal_autocorr': autocorr
    }

def _get_adaptive_search_space(complexity_info: Dict[str, Any], budget: int) -> List[Dict[str, Any]]:
    """🎯 Generate adaptive search space based on dataset complexity"""
    category = complexity_info['category']
    
    # Base parameter ranges by complexity
    base_ranges = {
        'simple': {
            'n_reservoir': [30, 50, 80],
            'spectral_radius': [0.7, 0.8, 0.9],
            'sparsity': [0.1, 0.2],
            'regularization': [1e-4, 1e-3],
            'leak_rate': [0.9, 1.0]
        },
        'medium': {
            'n_reservoir': [50, 100, 150, 200],
            'spectral_radius': [0.8, 0.9, 0.95, 0.99],
            'sparsity': [0.05, 0.1, 0.15],
            'regularization': [1e-6, 1e-5, 1e-4],
            'leak_rate': [0.8, 0.9, 1.0]
        },
        'complex': {
            'n_reservoir': [100, 200, 300, 500],
            'spectral_radius': [0.9, 0.95, 0.98, 0.99],
            'sparsity': [0.02, 0.05, 0.1],
            'regularization': [1e-8, 1e-6, 1e-4],
            'leak_rate': [0.7, 0.8, 0.9, 1.0]
        }
    }
    
    ranges = base_ranges[category]
    
    # Generate parameter combinations
    all_combinations = list(ParameterGrid(ranges))
    
    # Sample up to budget
    if len(all_combinations) > budget:
        np.random.shuffle(all_combinations)
        return all_combinations[:budget]
    else:
        # If we have fewer combinations than budget, add random sampling
        additional_needed = budget - len(all_combinations)
        
        for _ in range(additional_needed):
            params = {}
            for param, values in ranges.items():
                if param == 'spectral_radius':
                    # Continuous sampling for spectral radius
                    params[param] = np.random.uniform(min(values), max(values))
                elif param == 'regularization':
                    # Log-uniform sampling for regularization
                    log_min, log_max = np.log10(min(values)), np.log10(max(values))
                    params[param] = 10 ** np.random.uniform(log_min, log_max)
                else:
                    # Random choice for discrete parameters
                    params[param] = np.random.choice(values)
            
            all_combinations.append(params)
        
        return all_combinations

# Export main functions
__all__ = [
    'create_echo_state_network',
    'create_optimized_esn', 
    'optimize_esn_hyperparameters'
]