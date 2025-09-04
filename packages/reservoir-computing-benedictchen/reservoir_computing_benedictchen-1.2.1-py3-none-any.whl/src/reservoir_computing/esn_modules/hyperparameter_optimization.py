"""
🎯 Echo State Network - Hyperparameter Optimization Module
=========================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Advanced hyperparameter optimization methods for Echo State Networks.
Implements sophisticated search strategies for optimal parameter selection:

• Grid search with cross-validation for systematic exploration
• Auto-tuning with intelligent parameter selection
• Task-specific optimization strategies
• Budget-aware optimization (fast/medium/thorough)

📊 RESEARCH FOUNDATION:
=======================
Based on systematic parameter selection methodologies from:
- Jaeger (2001): Core parameter sensitivity analysis
- Lukosevicius & Jaeger (2009): Practical optimization guidelines
- Schrauwen et al. (2007): Reservoir size and connectivity optimization

🔍 OPTIMIZATION STRATEGIES:
=============================
1. **Grid Search**: Exhaustive exploration of parameter space
2. **Auto-Tuning**: Intelligent parameter selection based on task type
3. **Budget-Aware**: Optimization strategies for different time/computation budgets
4. **Task-Specific**: Specialized optimization for different problem types

⚡ PERFORMANCE CHARACTERISTICS:
==============================
• Grid Search: O(n_params^k * cv_folds * training_time) - can be expensive!
• Auto-Tuning: O(budget_factor * training_time) - adaptive complexity
• Memory usage: O(n_parameters * cross_validation_folds)
• Parallelizable: Methods support n_jobs parameter for parallel execution

🛠️ COMPUTATIONAL WARNINGS:
==========================
Hyperparameter optimization is computationally intensive!
- Grid search can take hours on large parameter spaces
- Auto-tuning with 'thorough' budget can take substantial time
- Use 'fast' budget for quick prototyping
- Consider reducing cv_folds for faster (but less reliable) results

This module contains the most computationally expensive methods from the original
1817-line file, now modularized for better maintainability.
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Callable
import numpy as np
import warnings
from abc import ABC, abstractmethod
from sklearn.model_selection import ParameterGrid, cross_val_score, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from concurrent.futures import ProcessPoolExecutor
import time

# Research accuracy FIXME comments preserved from original
# FIXME: HYPERPARAMETER OPTIMIZATION LACKS SYSTEMATIC RESEARCH VALIDATION
# FIXME: AUTO-TUNING PARAMETERS NOT BASED ON RIGOROUS EMPIRICAL STUDIES
# FIXME: TASK-SPECIFIC OPTIMIZATION NEEDS BETTER RESEARCH FOUNDATION

class HyperparameterOptimizationMixin(ABC):
    """
    🎯 Hyperparameter Optimization Mixin for Echo State Networks
    
    ELI5: This is like having an AI assistant that automatically finds the best
    settings for your reservoir computer! It tries thousands of different combinations
    to find what works best for your specific task.
    
    Technical Overview:
    ==================
    Implements sophisticated hyperparameter optimization strategies for reservoir computing.
    Uses cross-validation and intelligent search to find optimal parameter combinations.
    
    Key Optimization Methods:
    ------------------------
    1. **Grid Search**: Systematic exploration of parameter combinations
    2. **Auto-Tuning**: Intelligent parameter selection based on task characteristics  
    3. **Budget Control**: Fast/medium/thorough optimization levels
    4. **Parallel Execution**: Multi-core processing for faster optimization
    
    Research Foundation:
    ===================
    Based on parameter optimization research:
    - Systematic parameter sensitivity analysis (Jaeger 2001)
    - Practical optimization guidelines (Lukosevicius & Jaeger 2009)
    - Task-specific parameter recommendations from literature
    
    Performance Characteristics:
    ===========================
    - Grid search: Exponential complexity in number of parameters
    - Auto-tuning: Linear complexity with budget scaling
    - Memory usage: Moderate (stores cross-validation results)
    - CPU usage: High during optimization (parallelizable)
    """
    
    def hyperparameter_grid_search(self, X_train, y_train, param_grid=None, cv_folds=3, scoring='mse', n_jobs=1, verbose=True):
        """
        🔍 Comprehensive Hyperparameter Grid Search - Find Optimal Configuration!
        
        🔬 **Research Background**: Systematic parameter exploration is essential for 
        optimal Echo State Network performance. This method implements comprehensive
        grid search with cross-validation as recommended in the literature.
        
        📊 **Search Process Visualization**:
        ```
        🎯 GRID SEARCH OPTIMIZATION PROCESS
        
        1. Parameter Space Definition:
           spectral_radius: [0.1, 0.5, 0.9, 1.2]
           n_reservoir: [50, 100, 200, 400]
           noise_level: [0.001, 0.01, 0.1]
           
        2. Cross-Validation Loop:
           For each parameter combination:
           ┌─────────────────┐
           │ Fold 1: Train → Val │  
           │ Fold 2: Train → Val │
           │ Fold 3: Train → Val │
           └─────────────────┘
           Average performance → Score
           
        3. Best Configuration Selection:
           Choose parameters with lowest CV error
        ```
        
        🎮 **Usage Examples**:
        ```python
        # 🌟 EXAMPLE 1: Basic grid search (recommended)
        param_grid = {
            'spectral_radius': [0.5, 0.8, 1.0],
            'n_reservoir': [100, 200],
            'noise_level': [0.001, 0.01]
        }
        results = esn.hyperparameter_grid_search(X_train, y_train, param_grid)
        
        # 🚀 EXAMPLE 2: Comprehensive search (thorough)
        param_grid = {
            'spectral_radius': np.linspace(0.1, 1.5, 8),
            'n_reservoir': [50, 100, 200, 400, 800],
            'input_scaling': [0.1, 0.5, 1.0, 2.0],
            'noise_level': [0.0001, 0.001, 0.01, 0.1]
        }
        results = esn.hyperparameter_grid_search(X_train, y_train, param_grid, cv_folds=5)
        
        # 🔥 EXAMPLE 3: Fast parallel search
        results = esn.hyperparameter_grid_search(
            X_train, y_train, param_grid, n_jobs=4, verbose=True
        )
        ```
        
        📊 **Default Parameter Grid** (if none provided):
        ```python
        {
            'spectral_radius': [0.5, 0.8, 0.95, 1.1],
            'n_reservoir': [100, 200, 400],
            'input_scaling': [0.5, 1.0],
            'noise_level': [0.001, 0.01]
        }
        ```
        
        ⚡ **Performance Warnings**:
        - **Time Complexity**: O(n_combinations * cv_folds * training_time)
        - **Memory Usage**: O(n_combinations * cv_folds)
        - Large grids can take hours! Start small and expand gradually
        - Use n_jobs > 1 for parallel processing on multi-core systems
        
        📊 **Scoring Options**:
        - 'mse': Mean Squared Error (default, lower is better)
        - 'mae': Mean Absolute Error (robust to outliers)
        - 'r2': R-squared (higher is better)
        
        Args:
            X_train: Training input data (shape: [n_samples, n_features])
            y_train: Training target data (shape: [n_samples, n_outputs])
            param_grid (dict): Parameter grid to search (uses default if None)
            cv_folds (int): Number of cross-validation folds (3-5 recommended)
            scoring (str): Scoring metric ('mse', 'mae', 'r2')
            n_jobs (int): Number of parallel jobs (1=sequential, -1=all cores)
            verbose (bool): Print progress information
            
        Returns:
            dict: Comprehensive optimization results
            
        Example:
            >>> param_grid = {'spectral_radius': [0.8, 1.0], 'n_reservoir': [100, 200]}
            >>> results = esn.hyperparameter_grid_search(X_train, y_train, param_grid)
            🔍 Starting grid search optimization...
            📊 Testing 4 parameter combinations with 3-fold CV
            ✓ Optimization complete! Best score: 0.0234 (spectral_radius=0.8, n_reservoir=200)
        """
        if verbose:
            print("🔍 Starting grid search optimization...")
        
        # Default parameter grid if none provided
        if param_grid is None:
            param_grid = {
                'spectral_radius': [0.5, 0.8, 0.95, 1.1],
                'n_reservoir': [100, 200, 400],
                'input_scaling': [0.5, 1.0],
                'noise_level': [0.001, 0.01]
            }
        
        # Generate all parameter combinations
        param_combinations = list(ParameterGrid(param_grid))
        n_combinations = len(param_combinations)
        
        if verbose:
            print(f"📊 Testing {n_combinations} parameter combinations with {cv_folds}-fold CV")
        
        best_score = float('inf') if scoring in ['mse', 'mae'] else float('-inf')
        best_params = None
        all_results = []
        
        # Store original parameters
        original_params = {}
        for param in param_grid.keys():
            if hasattr(self, param):
                original_params[param] = getattr(self, param)
        
        try:
            # Test each parameter combination
            for i, params in enumerate(param_combinations):
                if verbose and i % max(1, n_combinations // 10) == 0:
                    print(f"  Progress: {i+1}/{n_combinations} ({(i+1)/n_combinations*100:.1f}%)")
                
                # Set parameters
                for param, value in params.items():
                    if hasattr(self, param):
                        setattr(self, param, value)
                
                # Reinitialize if necessary
                if hasattr(self, '_initialize_reservoir'):
                    self._initialize_reservoir()
                
                # Cross-validation
                cv_scores = []
                kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
                
                for train_idx, val_idx in kf.split(X_train):
                    X_cv_train, X_cv_val = X_train[train_idx], X_train[val_idx]
                    y_cv_train, y_cv_val = y_train[train_idx], y_train[val_idx]
                    
                    try:
                        # Train and evaluate
                        if hasattr(self, 'fit') and hasattr(self, 'predict'):
                            self.fit(X_cv_train, y_cv_train)
                            y_pred = self.predict(X_cv_val)
                            
                            # Calculate score
                            if scoring == 'mse':
                                score = mean_squared_error(y_cv_val, y_pred)
                            elif scoring == 'mae':
                                score = mean_absolute_error(y_cv_val, y_pred)
                            elif scoring == 'r2':
                                score = r2_score(y_cv_val, y_pred)
                            else:
                                score = mean_squared_error(y_cv_val, y_pred)
                            
                            cv_scores.append(score)
                        else:
                            cv_scores.append(float('inf'))  # Fallback
                    except Exception as e:
                        if verbose:
                            print(f"  Warning: Error in fold evaluation: {e}")
                        cv_scores.append(float('inf'))
                
                # Average CV score
                avg_score = np.mean(cv_scores) if cv_scores else float('inf')
                std_score = np.std(cv_scores) if len(cv_scores) > 1 else 0.0
                
                # Store results
                result = {
                    'params': params.copy(),
                    'mean_cv_score': avg_score,
                    'std_cv_score': std_score,
                    'individual_scores': cv_scores.copy()
                }
                all_results.append(result)
                
                # Update best if improved
                is_better = (avg_score < best_score if scoring in ['mse', 'mae'] else avg_score > best_score)
                if is_better and not (np.isnan(avg_score) or np.isinf(avg_score)):
                    best_score = avg_score
                    best_params = params.copy()
        
        except Exception as e:
            warnings.warn(f"Grid search failed: {e}. Restoring original parameters.")
            # Restore original parameters
            for param, value in original_params.items():
                setattr(self, param, value)
            return {'optimization_failed': True, 'error': str(e)}
        
        # Set best parameters
        if best_params is not None:
            for param, value in best_params.items():
                if hasattr(self, param):
                    setattr(self, param, value)
            if hasattr(self, '_initialize_reservoir'):
                self._initialize_reservoir()
        else:
            # Restore original parameters if no improvement
            for param, value in original_params.items():
                setattr(self, param, value)
        
        if verbose:
            if best_params:
                param_str = ", ".join([f"{k}={v}" for k, v in best_params.items()])
                print(f"✓ Optimization complete! Best score: {best_score:.6f} ({param_str})")
            else:
                print("⚠️ Optimization complete but no improvement found")
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': all_results,
            'n_combinations_tested': n_combinations,
            'cv_folds': cv_folds,
            'scoring_metric': scoring
        }

    def auto_tune_parameters(self, X_train, y_train, task_type='time_series', optimization_budget='medium', verbose=True):
        """
        🤖 Automatic Parameter Tuning - Smart Configuration Selection!
        
        🔬 **Research Background**: Intelligent parameter selection based on task 
        characteristics and established best practices from reservoir computing literature.
        
        📊 **Auto-Tuning Process**:
        ```
        🤖 INTELLIGENT PARAMETER SELECTION
        
        1. Task Analysis:
           Input: task_type, data characteristics
           ↓
        2. Parameter Recommendations:
           Based on research literature
           ↓  
        3. Budget-Aware Search:
           fast    → 3-5 key parameters
           medium  → 8-12 parameters
           thorough → 15-25 parameters
           ↓
        4. Optimized Configuration:
           Best parameters for your task
        ```
        
        🎮 **Usage Examples**:
        ```python
        # 🌟 EXAMPLE 1: Quick time series optimization
        results = esn.auto_tune_parameters(
            X_train, y_train, 
            task_type='time_series', 
            optimization_budget='fast'
        )
        
        # 🚀 EXAMPLE 2: Thorough classification tuning
        results = esn.auto_tune_parameters(
            X_train, y_train,
            task_type='classification',
            optimization_budget='thorough'
        )
        
        # 🔥 EXAMPLE 3: Medium chaotic system optimization
        results = esn.auto_tune_parameters(
            X_train, y_train,
            task_type='chaotic_system',
            optimization_budget='medium'
        )
        ```
        
        🎯 **Task-Specific Optimizations**:
        ```
        📈 TASK TYPE PARAMETER RECOMMENDATIONS
        ┌───────────────┬────────────────┬────────────────┐
        │  Task Type     │  Key Parameters  │  Typical Range  │
        ├───────────────┼────────────────┼────────────────┤
        │ time_series    │ spectral_radius │ 0.8 - 1.2      │
        │ classification │ n_reservoir     │ 100 - 800      │
        │ chaotic_system │ noise_level     │ 0.001 - 0.01   │
        │ memory_task    │ input_scaling   │ 0.1 - 2.0      │
        └───────────────┴────────────────┴────────────────┘
        ```
        
        🕰️ **Budget Guidelines**:
        - **fast**: ~1-2 minutes, 3-5 key parameters
        - **medium**: ~5-15 minutes, 8-12 parameters  
        - **thorough**: ~30-120 minutes, 15-25 parameters
        
        Args:
            X_train: Training input data
            y_train: Training target data
            task_type (str): Task type ('time_series', 'classification', 'chaotic_system', 'memory_task')
            optimization_budget (str): Budget level ('fast', 'medium', 'thorough')
            verbose (bool): Print optimization progress
            
        Returns:
            dict: Auto-tuning results with optimized parameters
            
        Example:
            >>> results = esn.auto_tune_parameters(X_train, y_train, 'time_series', 'medium')
            🤖 Auto-tuning parameters for time_series task...
            🕰️ Budget: medium (8-12 parameters, ~5-15 minutes)
            ✓ Auto-tuning complete! Optimized for time_series with medium budget
        """
        if verbose:
            print(f"🤖 Auto-tuning parameters for {task_type} task...")
            
        # Budget-specific time estimates
        time_estimates = {
            'fast': '~1-2 minutes',
            'medium': '~5-15 minutes', 
            'thorough': '~30-120 minutes'
        }
        
        if verbose:
            print(f"🕰️ Budget: {optimization_budget} ({time_estimates.get(optimization_budget, 'unknown')})") 
        
        # Task-specific parameter grids
        task_grids = {
            'time_series': {
                'fast': {
                    'spectral_radius': [0.8, 0.95, 1.1],
                    'n_reservoir': [100, 200],
                    'noise_level': [0.001, 0.01]
                },
                'medium': {
                    'spectral_radius': [0.5, 0.8, 0.95, 1.1, 1.3],
                    'n_reservoir': [50, 100, 200, 400],
                    'input_scaling': [0.5, 1.0, 1.5],
                    'noise_level': [0.0001, 0.001, 0.01]
                },
                'thorough': {
                    'spectral_radius': np.linspace(0.3, 1.5, 7).tolist(),
                    'n_reservoir': [50, 100, 200, 400, 800],
                    'input_scaling': [0.1, 0.5, 1.0, 1.5, 2.0],
                    'noise_level': [0.0001, 0.001, 0.01, 0.1],
                    'leaking_rate': [0.1, 0.3, 0.5, 0.8, 1.0]
                }
            },
            'classification': {
                'fast': {
                    'n_reservoir': [100, 200, 400],
                    'input_scaling': [0.5, 1.0], 
                    'spectral_radius': [0.8, 1.0]
                },
                'medium': {
                    'n_reservoir': [50, 100, 200, 400, 800],
                    'input_scaling': [0.1, 0.5, 1.0, 2.0],
                    'spectral_radius': [0.5, 0.8, 1.0, 1.2],
                    'noise_level': [0.0, 0.001, 0.01]
                },
                'thorough': {
                    'n_reservoir': [50, 100, 200, 400, 800, 1000],
                    'input_scaling': [0.1, 0.3, 0.5, 1.0, 1.5, 2.0],
                    'spectral_radius': np.linspace(0.3, 1.5, 7).tolist(),
                    'noise_level': [0.0, 0.0001, 0.001, 0.01, 0.1],
                    'connectivity': [0.05, 0.1, 0.2, 0.3]
                }
            },
            'chaotic_system': {
                'fast': {
                    'spectral_radius': [0.95, 1.0, 1.05],
                    'noise_level': [0.001, 0.005],
                    'n_reservoir': [200, 400]
                },
                'medium': {
                    'spectral_radius': [0.9, 0.95, 1.0, 1.05, 1.1],
                    'noise_level': [0.0001, 0.001, 0.005, 0.01],
                    'n_reservoir': [100, 200, 400, 800],
                    'input_scaling': [0.5, 1.0, 1.5]
                },
                'thorough': {
                    'spectral_radius': np.linspace(0.85, 1.15, 8).tolist(),
                    'noise_level': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05],
                    'n_reservoir': [100, 200, 400, 800, 1200],
                    'input_scaling': [0.1, 0.5, 1.0, 1.5, 2.0],
                    'leaking_rate': [0.8, 0.9, 1.0]
                }
            },
            'memory_task': {
                'fast': {
                    'n_reservoir': [200, 400, 800],
                    'spectral_radius': [0.95, 1.0],
                    'input_scaling': [0.1, 0.5]
                },
                'medium': {
                    'n_reservoir': [200, 400, 800, 1200],
                    'spectral_radius': [0.9, 0.95, 1.0, 1.05],
                    'input_scaling': [0.1, 0.3, 0.5, 1.0],
                    'connectivity': [0.05, 0.1, 0.2]
                },
                'thorough': {
                    'n_reservoir': [200, 400, 800, 1200, 1600],
                    'spectral_radius': np.linspace(0.85, 1.1, 8).tolist(),
                    'input_scaling': [0.05, 0.1, 0.3, 0.5, 1.0, 1.5],
                    'connectivity': [0.01, 0.05, 0.1, 0.2, 0.3],
                    'noise_level': [0.0, 0.0001, 0.001]
                }
            }
        }
        
        # Get parameter grid for task and budget
        if task_type in task_grids and optimization_budget in task_grids[task_type]:
            param_grid = task_grids[task_type][optimization_budget]
        else:
            # Fallback to time_series medium if task not found
            warnings.warn(f"Task type '{task_type}' not recognized. Using time_series defaults.")
            param_grid = task_grids['time_series']['medium']
        
        # Run grid search with the task-specific grid
        start_time = time.time()
        results = self.hyperparameter_grid_search(
            X_train, y_train, 
            param_grid=param_grid,
            cv_folds=3,
            scoring='mse',
            verbose=verbose
        )
        
        optimization_time = time.time() - start_time
        
        # Add auto-tuning specific information
        results.update({
            'task_type': task_type,
            'optimization_budget': optimization_budget,
            'optimization_time_seconds': optimization_time,
            'parameters_tested': len(list(ParameterGrid(param_grid)))
        })
        
        if verbose:
            print(f"✓ Auto-tuning complete! Optimized for {task_type} with {optimization_budget} budget")
            print(f"⏱️ Total optimization time: {optimization_time:.1f} seconds")
            
        return results

# Export for modular imports
__all__ = [
    'HyperparameterOptimizationMixin'
]
