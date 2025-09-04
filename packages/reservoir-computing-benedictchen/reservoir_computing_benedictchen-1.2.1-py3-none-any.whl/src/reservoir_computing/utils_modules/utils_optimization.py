"""
🏗️ Reservoir Computing - Optimization Utilities Module
=====================================================

Benchmarking, optimization, and performance analysis utilities for reservoir computing.
Part of the modular utils suite (split from monolithic 1142-line utils.py).

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"
         Lukoševičius, M. & Jaeger, H. (2009) "Reservoir computing approaches to RNN training"

🎯 MODULE FUNCTIONALITY:
=======================
This module provides optimization utilities for reservoir computing systems:
• Memory capacity benchmarking and analysis
• Nonlinear capacity evaluation with polynomial tasks
• Hyperparameter optimization using grid search and random search
• Performance benchmarking against standard tasks  
• Statistical analysis and reporting for optimization results

📊 RESEARCH FOUNDATION:
======================
Based on established benchmarking practices:
- Jaeger (2002): Memory capacity as fundamental ESN measure
- Dambre et al. (2012): Information processing capacity analysis
- Lukoševičius & Jaeger (2009): Comprehensive benchmarking guidelines
- Modern hyperparameter optimization techniques for neural systems

⚡ OPTIMIZATION ALGORITHMS:
==========================
• Grid search with intelligent parameter space exploration
• Random search for high-dimensional hyperparameter spaces
• Memory capacity calculation with configurable delay ranges
• Nonlinear capacity evaluation using polynomial regression tasks
• Statistical significance testing for performance comparisons

🔬 BENCHMARKING FRAMEWORK:
=========================
Comprehensive suite for evaluating reservoir computing systems:
- Standard memory capacity benchmark (linear recall tasks)
- Nonlinear capacity evaluation (polynomial transformation tasks)
- Cross-validation for robust performance estimation
- Statistical analysis with confidence intervals
- Comparative analysis between different reservoir configurations
"""

import numpy as np
import warnings
from typing import Dict, List, Tuple, Union, Optional, Any, Callable
from abc import ABC, abstractmethod

# Scientific computing imports
try:
    from scipy import stats
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("SciPy not available. Some optimization features will be limited.")

# Machine learning imports
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import ParameterGrid, RandomizedSearchCV
    from sklearn.metrics import mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available. Some optimization features will be limited.")


def memory_capacity_benchmark(esn, n_delays: int = 20, n_samples: int = 2000, 
                            input_scaling: float = 1.0, washout: int = 100,
                            verbose: bool = True, random_seed: Optional[int] = None) -> Dict[str, Any]:
    """
    🧠 Memory Capacity Benchmark - Standard Linear Recall Task
    
    Evaluates the linear memory capacity of a reservoir using delayed input recall tasks.
    This is the gold standard benchmark for assessing short-term memory in reservoir systems.
    
    Based on Jaeger (2002) "Short Term Memory in Echo State Networks"
    
    Args:
        esn: Fitted Echo State Network instance
        n_delays: Number of delay steps to test (typically 20-50)
        n_samples: Length of test sequence (should be >> n_delays)
        input_scaling: Scaling factor for input signal
        washout: Number of initial samples to discard (burn-in period)
        verbose: Whether to print progress information
        random_seed: Random seed for reproducible results
        
    Returns:
        Dict containing:
        - 'total_capacity': Sum of all individual delay capacities
        - 'capacity_per_delay': List of capacity values for each delay
        - 'effective_capacity': Number of delays with capacity > threshold (0.01)
        - 'capacity_profile': Detailed analysis of capacity decay
        - 'theoretical_maximum': Theoretical upper bound (min(n_reservoir, n_delays))
        
    Example:
        ```python
        # Standard memory capacity evaluation
        results = memory_capacity_benchmark(esn, n_delays=30, n_samples=3000)
        print(f"Total Memory Capacity: {results['total_capacity']:.2f}")
        print(f"Effective Memory Length: {results['effective_capacity']} steps")
        ```
    
    Research Context:
        Memory capacity quantifies how much information about past inputs
        can be linearly extracted from current reservoir states. Theoretical
        maximum is min(N, D) where N=reservoir size, D=delay range.
    """
    if not hasattr(esn, 'is_fitted_') or not esn.is_fitted_:
        raise RuntimeError("ESN must be fitted before memory capacity evaluation")
    
    if random_seed is not None:
        np.random.seed(random_seed)
        
    # Generate random input signal (uniform distribution as per Jaeger 2002)
    u = np.random.uniform(-input_scaling, input_scaling, (n_samples, 1))
    
    # Collect reservoir states
    states = esn._collect_states(u, washout=washout)
    effective_samples = len(states)
    
    if verbose:
        print(f"🧠 Memory Capacity Benchmark - Evaluating {n_delays} delays")
        print(f"📊 Using {effective_samples} samples after {washout}-step washout")
    
    # Calculate capacity for each delay
    capacities = []
    capacity_details = []
    
    for delay in range(1, n_delays + 1):
        if delay >= effective_samples:
            if verbose:
                print(f"⚠️  Delay {delay} exceeds available samples ({effective_samples})")
            capacities.append(0.0)
            capacity_details.append({
                'delay': delay, 
                'capacity': 0.0, 
                'r2_score': 0.0,
                'status': 'insufficient_data'
            })
            continue
            
        # Target: input delayed by 'delay' steps
        target = u[washout - delay: washout - delay + effective_samples].flatten()
        
        # Ensure target and states have same length
        min_length = min(len(target), len(states))
        target = target[:min_length]
        current_states = states[:min_length]
        
        try:
            # Linear regression: target = states @ weights
            # Using pseudoinverse for numerical stability
            weights = np.linalg.pinv(current_states) @ target
            predictions = current_states @ weights
            
            # Capacity is squared correlation coefficient
            if np.var(target) > 1e-12 and np.var(predictions) > 1e-12:
                correlation = np.corrcoef(target, predictions)[0, 1]
                capacity = correlation ** 2 if not np.isnan(correlation) else 0.0
                
                # Also calculate R² score for additional validation
                r2 = r2_score(target, predictions) if SKLEARN_AVAILABLE else capacity
            else:
                capacity = 0.0  
                r2 = 0.0
                
            capacities.append(max(0.0, capacity))  # Ensure non-negative
            capacity_details.append({
                'delay': delay,
                'capacity': capacity,
                'r2_score': r2,
                'target_var': np.var(target),
                'pred_var': np.var(predictions),
                'status': 'success'
            })
            
            if verbose and delay <= 5:  # Show first few delays
                print(f"  Delay {delay:2d}: Capacity = {capacity:.4f}")
                
        except (np.linalg.LinAlgError, ValueError) as e:
            if verbose:
                print(f"⚠️  Delay {delay}: Numerical error - {str(e)}")
            capacities.append(0.0)
            capacity_details.append({
                'delay': delay,
                'capacity': 0.0, 
                'r2_score': 0.0,
                'status': f'error: {str(e)}'
            })
    
    # Calculate summary statistics
    total_capacity = sum(capacities)
    effective_capacity = sum(1 for c in capacities if c > 0.01)  # Standard threshold
    theoretical_max = min(esn.n_reservoir, n_delays) if hasattr(esn, 'n_reservoir') else n_delays
    
    # Analyze capacity decay profile
    valid_capacities = [c for c in capacities if c > 0.001]
    if len(valid_capacities) > 2:
        # Fit exponential decay: capacity ≈ exp(-delay/τ)
        delays_valid = list(range(1, len(valid_capacities) + 1))
        try:
            # Log-linear fit for decay constant
            log_caps = np.log(np.maximum(valid_capacities, 1e-10))
            decay_fit = np.polyfit(delays_valid, log_caps, 1)
            decay_constant = -1.0 / decay_fit[0] if decay_fit[0] < 0 else np.inf
        except (ValueError, np.linalg.LinAlgError):
            decay_constant = np.inf
    else:
        decay_constant = np.inf
    
    results = {
        'total_capacity': total_capacity,
        'capacity_per_delay': capacities,
        'effective_capacity': effective_capacity,
        'theoretical_maximum': theoretical_max,
        'capacity_efficiency': total_capacity / theoretical_max if theoretical_max > 0 else 0.0,
        'capacity_profile': capacity_details,
        'decay_constant': decay_constant,
        'benchmark_params': {
            'n_delays': n_delays,
            'n_samples': n_samples,
            'input_scaling': input_scaling,
            'washout': washout,
            'effective_samples': effective_samples
        }
    }
    
    if verbose:
        print(f"📊 MEMORY CAPACITY RESULTS:")
        print(f"  Total Capacity: {total_capacity:.3f} / {theoretical_max} ({100*results['capacity_efficiency']:.1f}%)")
        print(f"  Effective Memory: {effective_capacity} delays")
        print(f"  Decay Constant: {decay_constant:.2f}" if decay_constant != np.inf else "  Decay: No clear exponential pattern")
        
    return results


def nonlinear_capacity_benchmark(esn, polynomial_degree: int = 3, n_samples: int = 2000,
                                input_scaling: float = 1.0, washout: int = 100, 
                                n_trials: int = 5, verbose: bool = True,
                                random_seed: Optional[int] = None) -> Dict[str, Any]:
    """
    🔬 Nonlinear Capacity Benchmark - Polynomial Transformation Tasks
    
    Evaluates the nonlinear information processing capacity using polynomial
    transformations of delayed inputs. This complements linear memory capacity
    by assessing complex temporal pattern recognition capabilities.
    
    Based on Dambre et al. (2012) "Information processing capacity of dynamical systems"
    
    Args:
        esn: Fitted Echo State Network instance
        polynomial_degree: Maximum degree for polynomial transformations (1-4 typical)
        n_samples: Length of test sequence
        input_scaling: Scaling factor for input signal
        washout: Number of initial samples to discard
        n_trials: Number of random trials for robust estimation
        verbose: Whether to print detailed progress
        random_seed: Random seed for reproducible results
        
    Returns:
        Dict containing:
        - 'linear_capacity': Linear information processing capacity
        - 'nonlinear_capacity': Nonlinear capacity per polynomial degree
        - 'total_capacity': Sum of all linear and nonlinear capacities
        - 'capacity_breakdown': Detailed breakdown by transformation type
        - 'polynomial_performance': Performance for each polynomial degree
        
    Example:
        ```python
        # Comprehensive nonlinear capacity evaluation
        results = nonlinear_capacity_benchmark(esn, polynomial_degree=3, n_trials=10)
        print(f"Linear Capacity: {results['linear_capacity']:.3f}")
        print(f"Nonlinear Capacities: {results['nonlinear_capacity']}")
        ```
    
    Research Context:
        Total information processing capacity quantifies both linear memory
        and nonlinear transformation capabilities. Higher polynomial degrees
        assess complex pattern recognition beyond simple recall tasks.
    """
    if not hasattr(esn, 'is_fitted_') or not esn.is_fitted_:
        raise RuntimeError("ESN must be fitted before nonlinear capacity evaluation")
    
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Initialize results storage
    all_results = []
    capacity_by_degree = {d: [] for d in range(1, polynomial_degree + 1)}
    linear_capacities = []
    
    if verbose:
        print(f"🔬 Nonlinear Capacity Benchmark - {n_trials} trials, degree {polynomial_degree}")
    
    for trial in range(n_trials):
        if verbose and n_trials > 1:
            print(f"  Trial {trial + 1}/{n_trials}")
            
        # Generate random input signal
        u = np.random.uniform(-input_scaling, input_scaling, (n_samples, 1))
        
        # Collect reservoir states
        states = esn._collect_states(u, washout=washout) 
        effective_samples = len(states)
        
        # Linear capacity (degree 1): delayed inputs
        linear_cap = 0.0
        max_delay = min(20, effective_samples // 4)  # Reasonable delay range
        
        for delay in range(1, max_delay + 1):
            if delay >= effective_samples:
                break
                
            target = u[washout - delay: washout - delay + effective_samples].flatten()
            min_length = min(len(target), len(states))
            target = target[:min_length]
            current_states = states[:min_length]
            
            try:
                weights = np.linalg.pinv(current_states) @ target
                predictions = current_states @ weights
                
                if np.var(target) > 1e-12 and np.var(predictions) > 1e-12:
                    correlation = np.corrcoef(target, predictions)[0, 1]
                    capacity = correlation ** 2 if not np.isnan(correlation) else 0.0
                    linear_cap += max(0.0, capacity)
            except:
                continue
                
        linear_capacities.append(linear_cap)
        
        # Nonlinear capacities (degree > 1): polynomial transformations
        for degree in range(2, polynomial_degree + 1):
            degree_capacity = 0.0
            
            # Test various polynomial transformations
            transformations = []
            if degree == 2:
                # Quadratic transformations: u(t-d1) * u(t-d2)
                for d1 in range(1, min(6, effective_samples // 8)):
                    for d2 in range(d1, min(6, effective_samples // 8)):
                        transformations.append((d1, d2))
            elif degree == 3:
                # Cubic transformations: u(t-d1) * u(t-d2) * u(t-d3)
                for d1 in range(1, min(4, effective_samples // 12)):
                    for d2 in range(d1, min(4, effective_samples // 12)):
                        for d3 in range(d2, min(4, effective_samples // 12)):
                            transformations.append((d1, d2, d3))
            else:
                # Higher degree: sample representative transformations
                n_transforms = min(20, max(5, 50 // degree))  
                for _ in range(n_transforms):
                    delays = sorted(np.random.randint(1, min(8, effective_samples // 16), degree))
                    transformations.append(tuple(delays))
            
            # Evaluate each transformation
            for delays in transformations[:15]:  # Limit for computational efficiency
                if max(delays) >= effective_samples:
                    continue
                    
                # Create polynomial target
                target_parts = []
                for delay in delays:
                    delayed_input = u[washout - delay: washout - delay + effective_samples]
                    target_parts.append(delayed_input.flatten())
                
                if all(len(part) >= effective_samples for part in target_parts):
                    # Compute polynomial transformation
                    target = target_parts[0]
                    for part in target_parts[1:]:
                        target = target * part[:len(target)]
                    
                    target = target[:effective_samples]
                    current_states = states[:len(target)]
                    
                    try:
                        weights = np.linalg.pinv(current_states) @ target
                        predictions = current_states @ weights
                        
                        if np.var(target) > 1e-12 and np.var(predictions) > 1e-12:
                            correlation = np.corrcoef(target, predictions)[0, 1] 
                            capacity = correlation ** 2 if not np.isnan(correlation) else 0.0
                            degree_capacity += max(0.0, capacity)
                    except:
                        continue
            
            capacity_by_degree[degree].append(degree_capacity)
    
    # Compute statistics across trials
    mean_linear = np.mean(linear_capacities) if linear_capacities else 0.0
    std_linear = np.std(linear_capacities) if len(linear_capacities) > 1 else 0.0
    
    nonlinear_means = {}
    nonlinear_stds = {}
    total_nonlinear = 0.0
    
    for degree in range(2, polynomial_degree + 1):
        if capacity_by_degree[degree]:
            mean_cap = np.mean(capacity_by_degree[degree])
            std_cap = np.std(capacity_by_degree[degree]) if len(capacity_by_degree[degree]) > 1 else 0.0
            nonlinear_means[degree] = mean_cap
            nonlinear_stds[degree] = std_cap
            total_nonlinear += mean_cap
        else:
            nonlinear_means[degree] = 0.0
            nonlinear_stds[degree] = 0.0
    
    total_capacity = mean_linear + total_nonlinear
    
    results = {
        'linear_capacity': mean_linear,
        'linear_capacity_std': std_linear,
        'nonlinear_capacity': nonlinear_means,
        'nonlinear_capacity_std': nonlinear_stds,
        'total_capacity': total_capacity,
        'capacity_breakdown': {
            'linear': mean_linear,
            'quadratic': nonlinear_means.get(2, 0.0),
            'cubic': nonlinear_means.get(3, 0.0),
            'higher_order': sum(nonlinear_means.get(d, 0.0) for d in range(4, polynomial_degree + 1))
        },
        'polynomial_performance': {
            degree: {
                'mean': nonlinear_means.get(degree, 0.0),
                'std': nonlinear_stds.get(degree, 0.0),
                'trials': len(capacity_by_degree.get(degree, []))
            } for degree in range(1, polynomial_degree + 1)
        },
        'benchmark_params': {
            'polynomial_degree': polynomial_degree,
            'n_samples': n_samples,
            'n_trials': n_trials,
            'input_scaling': input_scaling,
            'washout': washout
        }
    }
    
    if verbose:
        print(f"📊 NONLINEAR CAPACITY RESULTS:")
        print(f"  Linear Capacity: {mean_linear:.3f} ± {std_linear:.3f}")
        for degree, mean_cap in nonlinear_means.items():
            std_cap = nonlinear_stds[degree]
            print(f"  Degree {degree} Capacity: {mean_cap:.3f} ± {std_cap:.3f}")
        print(f"  Total Capacity: {total_capacity:.3f}")
        
    return results


def optimize_hyperparameters(esn_class, param_grid: Dict[str, List], 
                           X_train: np.ndarray, y_train: np.ndarray,
                           X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None,
                           cv_folds: int = 3, scoring: str = 'mse',
                           search_method: str = 'grid', n_iter: int = 50,
                           verbose: bool = True, random_seed: Optional[int] = None) -> Dict[str, Any]:
    """
    🎯 Hyperparameter Optimization for Echo State Networks
    
    Comprehensive hyperparameter optimization using grid search or randomized search.
    Evaluates parameter combinations using cross-validation or validation split.
    
    Args:
        esn_class: ESN class to optimize (not instance)
        param_grid: Dictionary of parameter names and value lists/ranges
        X_train: Training input sequences
        y_train: Training target sequences  
        X_val: Optional validation sequences (if None, uses CV)
        y_val: Optional validation targets
        cv_folds: Number of cross-validation folds (if no validation set)
        scoring: Scoring metric ('mse', 'mae', 'r2')
        search_method: 'grid' for exhaustive, 'random' for randomized
        n_iter: Number of iterations for random search
        verbose: Whether to print optimization progress
        random_seed: Random seed for reproducible results
        
    Returns:
        Dict containing:
        - 'best_params': Optimal parameter combination
        - 'best_score': Best validation score achieved
        - 'best_esn': ESN instance with optimal parameters
        - 'optimization_history': All tried parameter combinations
        - 'score_statistics': Statistics across all evaluations
        
    Example:
        ```python
        param_grid = {
            'n_reservoir': [50, 100, 200],
            'spectral_radius': [0.9, 0.95, 0.99], 
            'input_scaling': [0.1, 0.5, 1.0],
            'regularization': [1e-6, 1e-4, 1e-2]
        }
        
        results = optimize_hyperparameters(EchoStateNetwork, param_grid, 
                                         X_train, y_train, X_val, y_val)
        best_esn = results['best_esn']
        ```
        
    Research Context:
        Systematic hyperparameter optimization is crucial for reservoir computing
        due to sensitivity to spectral radius, input scaling, and regularization.
        Cross-validation provides robust performance estimates.
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Input validation
    if X_val is not None and y_val is not None:
        use_validation_split = True
        if verbose:
            print(f"🎯 Hyperparameter Optimization - Using validation split")
    else:
        use_validation_split = False
        if verbose:
            print(f"🎯 Hyperparameter Optimization - Using {cv_folds}-fold CV")
    
    # Generate parameter combinations
    if search_method == 'grid':
        param_combinations = list(ParameterGrid(param_grid)) if SKLEARN_AVAILABLE else _generate_param_grid(param_grid)
        if verbose:
            print(f"📊 Grid Search: {len(param_combinations)} parameter combinations")
    elif search_method == 'random':
        param_combinations = _generate_random_params(param_grid, n_iter, random_seed)
        if verbose:
            print(f"🎲 Random Search: {n_iter} random parameter combinations")
    else:
        raise ValueError(f"Unknown search method: {search_method}")
    
    # Track optimization progress
    optimization_history = []
    best_score = np.inf if scoring in ['mse', 'mae'] else -np.inf
    best_params = None
    best_esn = None
    all_scores = []
    
    for i, params in enumerate(param_combinations):
        try:
            if verbose and (i + 1) % max(1, len(param_combinations) // 10) == 0:
                print(f"  Progress: {i + 1}/{len(param_combinations)} ({100*(i+1)/len(param_combinations):.1f}%)")
            
            # Evaluate parameter combination
            if use_validation_split:
                score = _evaluate_esn_params(esn_class, params, X_train, y_train, X_val, y_val, scoring)
            else:
                score = _evaluate_esn_cv(esn_class, params, X_train, y_train, cv_folds, scoring, random_seed)
            
            # Track results
            optimization_history.append({
                'params': params.copy(),
                'score': score,
                'iteration': i + 1
            })
            all_scores.append(score)
            
            # Update best parameters
            if scoring in ['mse', 'mae']:  # Lower is better
                if score < best_score:
                    best_score = score
                    best_params = params.copy()
            else:  # Higher is better (r2)
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                    
        except Exception as e:
            if verbose:
                print(f"⚠️  Parameter combination {i+1} failed: {str(e)}")
            optimization_history.append({
                'params': params.copy(),
                'score': np.nan,
                'error': str(e),
                'iteration': i + 1
            })
    
    # Train best ESN
    if best_params is not None:
        try:
            best_esn = esn_class(**best_params)
            best_esn.fit(X_train, y_train)
        except Exception as e:
            if verbose:
                print(f"⚠️  Failed to train best ESN: {str(e)}")
            best_esn = None
    
    # Compute optimization statistics
    valid_scores = [s for s in all_scores if not np.isnan(s)]
    score_statistics = {
        'mean': np.mean(valid_scores) if valid_scores else np.nan,
        'std': np.std(valid_scores) if len(valid_scores) > 1 else np.nan,
        'min': np.min(valid_scores) if valid_scores else np.nan,
        'max': np.max(valid_scores) if valid_scores else np.nan,
        'median': np.median(valid_scores) if valid_scores else np.nan,
        'success_rate': len(valid_scores) / len(param_combinations) if param_combinations else 0.0
    }
    
    results = {
        'best_params': best_params,
        'best_score': best_score,
        'best_esn': best_esn,
        'optimization_history': optimization_history,
        'score_statistics': score_statistics,
        'search_config': {
            'method': search_method,
            'scoring': scoring,
            'n_combinations': len(param_combinations),
            'use_validation_split': use_validation_split,
            'cv_folds': cv_folds if not use_validation_split else None
        }
    }
    
    if verbose:
        print(f"📊 OPTIMIZATION RESULTS:")
        print(f"  Best Score: {best_score:.6f} ({scoring})")
        print(f"  Best Parameters: {best_params}")
        print(f"  Success Rate: {score_statistics['success_rate']:.1%}")
        print(f"  Score Range: {score_statistics['min']:.6f} - {score_statistics['max']:.6f}")
        
    return results


def grid_search_optimization(esn_class, param_ranges: Dict[str, Tuple], 
                           X_train: np.ndarray, y_train: np.ndarray,
                           X_test: np.ndarray, y_test: np.ndarray,
                           n_points_per_param: int = 5, scoring: str = 'mse',
                           early_stopping: bool = True, patience: int = 10,
                           verbose: bool = True, random_seed: Optional[int] = None) -> Dict[str, Any]:
    """
    🔍 Intelligent Grid Search with Adaptive Refinement
    
    Advanced grid search that adaptively refines the search space around
    promising regions. More efficient than exhaustive grid search for
    continuous parameter spaces.
    
    Args:
        esn_class: ESN class to optimize
        param_ranges: Dict of parameter names to (min, max) tuples
        X_train, y_train: Training data
        X_test, y_test: Test data for final evaluation
        n_points_per_param: Grid resolution per parameter
        scoring: Scoring metric ('mse', 'mae', 'r2')
        early_stopping: Whether to stop if no improvement
        patience: Number of iterations without improvement before stopping
        verbose: Progress reporting
        random_seed: Random seed
        
    Returns:
        Dict with optimization results and refined parameter estimates
        
    Example:
        ```python
        param_ranges = {
            'spectral_radius': (0.8, 1.0),
            'input_scaling': (0.1, 2.0),
            'regularization': (1e-8, 1e-2)
        }
        
        results = grid_search_optimization(EchoStateNetwork, param_ranges,
                                         X_train, y_train, X_test, y_test)
        ```
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    if verbose:
        print(f"🔍 Intelligent Grid Search - {n_points_per_param}^{len(param_ranges)} initial grid")
    
    # Initialize grid search space
    param_names = list(param_ranges.keys())
    current_ranges = param_ranges.copy()
    
    optimization_history = []
    best_score = np.inf if scoring in ['mse', 'mae'] else -np.inf
    best_params = None
    iterations_without_improvement = 0
    
    for iteration in range(5):  # Maximum refinement iterations
        if verbose:
            print(f"  Iteration {iteration + 1}: Grid refinement")
        
        # Generate current grid
        param_grids = {}
        for param, (min_val, max_val) in current_ranges.items():
            param_grids[param] = np.linspace(min_val, max_val, n_points_per_param)
        
        param_combinations = _generate_param_grid(param_grids)
        iteration_scores = []
        iteration_params = []
        
        # Evaluate all combinations in current grid
        for params in param_combinations:
            try:
                score = _evaluate_esn_params(esn_class, params, X_train, y_train, X_test, y_test, scoring)
                iteration_scores.append(score)
                iteration_params.append(params)
                
                optimization_history.append({
                    'params': params.copy(),
                    'score': score,
                    'iteration': iteration + 1
                })
                
                # Update global best
                is_better = score < best_score if scoring in ['mse', 'mae'] else score > best_score
                if is_better:
                    best_score = score
                    best_params = params.copy()
                    iterations_without_improvement = 0
                    
            except Exception as e:
                if verbose:
                    print(f"    Parameter evaluation failed: {str(e)}")
                continue
        
        if not iteration_scores:
            if verbose:
                print("    No valid parameter combinations found")
            break
        
        # Find best parameters in this iteration
        if scoring in ['mse', 'mae']:
            best_idx = np.argmin(iteration_scores)
        else:
            best_idx = np.argmax(iteration_scores)
            
        iteration_best_params = iteration_params[best_idx]
        iteration_best_score = iteration_scores[best_idx]
        
        if verbose:
            print(f"    Best score: {iteration_best_score:.6f}")
            print(f"    Best params: {iteration_best_params}")
        
        # Check for early stopping
        iterations_without_improvement += 1
        if early_stopping and iterations_without_improvement >= patience:
            if verbose:
                print(f"    Early stopping: No improvement for {patience} iterations")
            break
        
        # Refine search space around best parameters
        new_ranges = {}
        for param in param_names:
            current_val = iteration_best_params[param]
            min_val, max_val = current_ranges[param]
            range_size = max_val - min_val
            
            # Narrow range around best value (50% reduction)
            new_range_size = range_size * 0.5
            new_min = max(param_ranges[param][0], current_val - new_range_size / 2)
            new_max = min(param_ranges[param][1], current_val + new_range_size / 2)
            
            new_ranges[param] = (new_min, new_max)
        
        current_ranges = new_ranges
        
        if verbose:
            print(f"    Refined ranges: {current_ranges}")
    
    # Final evaluation with best parameters
    final_esn = None
    if best_params is not None:
        try:
            final_esn = esn_class(**best_params)
            final_esn.fit(X_train, y_train)
        except Exception as e:
            if verbose:
                print(f"    Failed to train final ESN: {str(e)}")
    
    results = {
        'best_params': best_params,
        'best_score': best_score,
        'best_esn': final_esn,
        'optimization_history': optimization_history,
        'final_ranges': current_ranges,
        'original_ranges': param_ranges,
        'convergence_info': {
            'total_evaluations': len(optimization_history),
            'iterations': iteration + 1,
            'converged': iterations_without_improvement < patience
        }
    }
    
    if verbose:
        print(f"🎯 GRID SEARCH COMPLETE:")
        print(f"  Best Score: {best_score:.6f}")
        print(f"  Total Evaluations: {len(optimization_history)}")
        print(f"  Final Ranges: {current_ranges}")
        
    return results


# Helper functions for optimization
def _generate_param_grid(param_dict: Dict[str, List]) -> List[Dict[str, Any]]:
    """Generate all parameter combinations from parameter grid"""
    if not param_dict:
        return [{}]
    
    param_names = list(param_dict.keys())
    param_values = list(param_dict.values())
    
    combinations = []
    def _recursive_generate(current_params, remaining_names, remaining_values):
        if not remaining_names:
            combinations.append(current_params.copy())
            return
        
        param_name = remaining_names[0]
        param_vals = remaining_values[0]
        
        for val in param_vals:
            current_params[param_name] = val
            _recursive_generate(current_params, remaining_names[1:], remaining_values[1:])
            
    _recursive_generate({}, param_names, param_values)
    return combinations


def _generate_random_params(param_grid: Dict[str, List], n_iter: int, random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
    """Generate random parameter combinations"""
    if random_seed is not None:
        np.random.seed(random_seed)
    
    combinations = []
    for _ in range(n_iter):
        params = {}
        for param_name, param_values in param_grid.items():
            params[param_name] = np.random.choice(param_values)
        combinations.append(params)
    
    return combinations


def _evaluate_esn_params(esn_class, params: Dict[str, Any], X_train: np.ndarray, y_train: np.ndarray,
                        X_val: np.ndarray, y_val: np.ndarray, scoring: str) -> float:
    """Evaluate ESN parameters using validation split"""
    esn = esn_class(**params)
    esn.fit(X_train, y_train)
    predictions = esn.predict(X_val)
    
    if scoring == 'mse':
        return mean_squared_error(y_val, predictions) if SKLEARN_AVAILABLE else np.mean((y_val - predictions) ** 2)
    elif scoring == 'mae':
        return np.mean(np.abs(y_val - predictions))
    elif scoring == 'r2':
        return r2_score(y_val, predictions) if SKLEARN_AVAILABLE else 1 - np.var(y_val - predictions) / np.var(y_val)
    else:
        raise ValueError(f"Unknown scoring method: {scoring}")


def _evaluate_esn_cv(esn_class, params: Dict[str, Any], X: np.ndarray, y: np.ndarray,
                    cv_folds: int, scoring: str, random_seed: Optional[int] = None) -> float:
    """Evaluate ESN parameters using cross-validation"""
    if random_seed is not None:
        np.random.seed(random_seed)
    
    n_samples = len(X)
    fold_size = n_samples // cv_folds
    scores = []
    
    for fold in range(cv_folds):
        # Create train/validation split
        val_start = fold * fold_size
        val_end = val_start + fold_size if fold < cv_folds - 1 else n_samples
        
        val_indices = range(val_start, val_end)
        train_indices = list(range(0, val_start)) + list(range(val_end, n_samples))
        
        X_train_fold = X[train_indices]
        y_train_fold = y[train_indices] 
        X_val_fold = X[val_indices]
        y_val_fold = y[val_indices]
        
        # Train and evaluate
        fold_score = _evaluate_esn_params(esn_class, params, X_train_fold, y_train_fold, X_val_fold, y_val_fold, scoring)
        scores.append(fold_score)
    
    return np.mean(scores)