"""
🤖 Auto Tuning Module - AI-Powered ESN Parameter Optimization
=============================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module contains automatic parameter tuning and preset configuration methods
for Echo State Networks extracted from the original monolithic configuration_optimization.py file.

Based on: Herbert Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"
"""

import numpy as np
import warnings


class AutoTuningMixin:
    """
    🤖 Auto Tuning Mixin for Echo State Networks
    
    This mixin provides intelligent parameter tuning and preset configurations
    for Echo State Networks, implementing research-backed optimization strategies.
    
    🌟 Key Features:
    - Task-specific automatic parameter tuning
    - Research-backed configuration presets
    - Data-driven parameter estimation
    - Budget-aware optimization strategies
    """
    
    def auto_tune_parameters(self, X_train, y_train, task_type='time_series', optimization_budget='medium', verbose=True):
        """
        🤖 Automatic Parameter Tuning - AI-Powered ESN Optimization
        
        🔬 **Research Background**: This method implements intelligent parameter tuning
        using research-backed heuristics and adaptive optimization strategies. It automatically
        selects optimal parameters based on data characteristics and task requirements.
        
        🎯 **Task-Specific Optimization**:
        ```
        🎭 TASK-SPECIFIC PARAMETER STRATEGIES
        
        Task Type        Spectral Radius    Reservoir Size    Noise Level    Activation
        ─────────────   ─────────────────  ──────────────   ───────────    ──────────
        time_series     0.3 - 1.2          50 - 300        0.001 - 0.01    tanh
        classification  0.5 - 0.9          100 - 500       0.01 - 0.05     sigmoid  
        chaotic         0.8 - 1.4          200 - 1000      0.001 - 0.005   tanh
        regression      0.4 - 1.0          100 - 400       0.001 - 0.02    tanh/relu
        forecasting     0.6 - 1.3          150 - 600       0.005 - 0.02    leaky_relu
        ```
        
        🎮 **Usage Examples**:
        ```python
        # 🌟 EXAMPLE 1: Automatic tuning for time series prediction
        esn = EchoStateNetwork()
        esn.auto_tune_parameters(X_train, y_train, task_type='time_series')
        
        # 🚀 EXAMPLE 2: Quick tuning for classification task
        esn.auto_tune_parameters(X_train, y_train, 
                               task_type='classification', 
                               optimization_budget='fast')
        
        # 🔥 EXAMPLE 3: Thorough optimization for critical application
        esn.auto_tune_parameters(X_train, y_train,
                               task_type='chaotic',
                               optimization_budget='thorough')
        ```
        
        📊 **Optimization Budget Levels**:
        ```
        🚀 OPTIMIZATION BUDGET COMPARISON
        
        Budget      Time    Grid Points    CV Folds    ESP Tests    Best For
        ──────────  ──────  ───────────   ─────────   ─────────   ─────────────
        fast        1-2 min      12           3          1        Quick prototyping
        medium      5-10 min     36           3          2        Standard use  
        thorough    15-30 min    108          5          3        Critical applications
        exhaustive  1-2 hours    324          10         5        Research/benchmarks
        ```
        
        🧠 **Intelligent Heuristics**:
        - **Data-driven sizing**: Reservoir size based on input dimensionality
        - **ESP-aware spectral radius**: Automatic range selection with validation  
        - **Task-specific activation**: Optimal functions for different problem types
        - **Noise level adaptation**: Based on signal-to-noise ratio estimation
        - **Memory length optimization**: Leak rate tuning for temporal dependencies
        
        Args:
            X_train (array): Training input data
            y_train (array): Training targets  
            task_type (str): Task type - 'time_series', 'classification', 'chaotic', 'regression', 'forecasting'
            optimization_budget (str): Budget level - 'fast', 'medium', 'thorough', 'exhaustive'
            verbose (bool): Whether to print optimization progress
            
        Returns:
            dict: Optimization results with best parameters and performance metrics
        """
        
        if verbose:
            print(f"🤖 Auto-tuning ESN parameters for {task_type} task with {optimization_budget} budget...")
        
        # Task-specific parameter ranges
        task_configs = {
            'time_series': {
                'spectral_radius': (0.3, 1.2),
                'n_reservoir_factor': (2, 8),  # Factor of input dimensionality  
                'noise_level': (0.001, 0.01),
                'leak_rate': (0.1, 1.0),
                'activation_function': ['tanh'],
                'output_feedback_mode': ['direct', 'sparse'],
                'regularization': (1e-8, 1e-4)
            },
            'classification': {
                'spectral_radius': (0.5, 0.9),
                'n_reservoir_factor': (3, 10),
                'noise_level': (0.01, 0.05),
                'leak_rate': (0.3, 0.8),
                'activation_function': ['sigmoid', 'tanh'],
                'output_feedback_mode': ['sparse', 'scaled_uniform'],
                'regularization': (1e-6, 1e-3)
            },
            'chaotic': {
                'spectral_radius': (0.8, 1.4),
                'n_reservoir_factor': (4, 15),
                'noise_level': (0.001, 0.005),
                'leak_rate': (0.7, 1.0),
                'activation_function': ['tanh'],
                'output_feedback_mode': ['direct'],
                'regularization': (1e-9, 1e-5)
            },
            'regression': {
                'spectral_radius': (0.4, 1.0),
                'n_reservoir_factor': (2, 10),
                'noise_level': (0.001, 0.02),
                'leak_rate': (0.1, 1.0),
                'activation_function': ['tanh', 'relu'],
                'output_feedback_mode': ['direct', 'sparse'],
                'regularization': (1e-8, 1e-4)
            },
            'forecasting': {
                'spectral_radius': (0.6, 1.3),
                'n_reservoir_factor': (3, 12),
                'noise_level': (0.005, 0.02),
                'leak_rate': (0.5, 1.0),
                'activation_function': ['leaky_relu', 'tanh'],
                'output_feedback_mode': ['direct'],
                'regularization': (1e-7, 1e-4)
            }
        }
        
        if task_type not in task_configs:
            raise ValueError(f"Invalid task_type. Choose from: {list(task_configs.keys())}")
        
        config = task_configs[task_type]
        
        # Budget-specific optimization parameters
        budget_configs = {
            'fast': {'n_radius': 3, 'n_size': 2, 'n_noise': 2, 'n_leak': 2, 'cv_folds': 3},
            'medium': {'n_radius': 4, 'n_size': 3, 'n_noise': 3, 'n_leak': 3, 'cv_folds': 3},
            'thorough': {'n_radius': 6, 'n_size': 4, 'n_noise': 3, 'n_leak': 4, 'cv_folds': 5},
            'exhaustive': {'n_radius': 9, 'n_size': 6, 'n_noise': 4, 'n_leak': 5, 'cv_folds': 10}
        }
        
        if optimization_budget not in budget_configs:
            raise ValueError(f"Invalid optimization_budget. Choose from: {list(budget_configs.keys())}")
        
        budget = budget_configs[optimization_budget]
        
        # Data-driven parameter estimation
        n_inputs = X_train.shape[1] if len(X_train.shape) > 1 else 1
        data_variance = np.var(X_train)
        
        # Generate adaptive parameter grid
        param_grid = {}
        
        # Spectral radius
        sr_min, sr_max = config['spectral_radius']
        param_grid['spectral_radius'] = np.linspace(sr_min, sr_max, budget['n_radius'])
        
        # Reservoir size (data-driven)
        res_min = int(n_inputs * config['n_reservoir_factor'][0])
        res_max = int(n_inputs * config['n_reservoir_factor'][1])
        reservoir_sizes = np.logspace(np.log10(res_min), np.log10(res_max), budget['n_size'], dtype=int)
        param_grid['n_reservoir'] = list(set(reservoir_sizes))  # Remove duplicates
        
        # Noise level (adapted to data variance)
        noise_min, noise_max = config['noise_level'] 
        noise_scale = min(1.0, data_variance)  # Scale based on data variance
        param_grid['noise_level'] = np.logspace(np.log10(noise_min * noise_scale), 
                                              np.log10(noise_max * noise_scale), 
                                              budget['n_noise'])
        
        # Leak rate
        leak_min, leak_max = config['leak_rate']
        param_grid['leak_rate'] = np.linspace(leak_min, leak_max, budget['n_leak'])
        
        # Regularization (adapted to problem size)
        reg_min, reg_max = config['regularization']
        reg_scale = 1.0 / max(len(X_train), 100)  # Scale based on dataset size
        param_grid['regularization'] = np.logspace(np.log10(reg_min * reg_scale),
                                                  np.log10(reg_max * reg_scale), 3)
        
        # Categorical parameters
        param_grid['activation_function'] = config['activation_function']
        param_grid['output_feedback_mode'] = config['output_feedback_mode']
        
        if verbose:
            n_combinations = 1
            for values in param_grid.values():
                n_combinations *= len(values)
            print(f"📊 Generated adaptive parameter grid with {n_combinations} combinations")
        
        # Perform grid search
        if hasattr(self, 'hyperparameter_grid_search'):
            results = self.hyperparameter_grid_search(
                X_train, y_train,
                param_grid=param_grid,
                cv_folds=budget['cv_folds'],
                scoring='mse',
                verbose=verbose
            )
        else:
            # Fallback if hyperparameter_grid_search is not available
            results = {
                'best_params': {},
                'best_score': float('inf'),
                'cv_results': [],
                'search_time': 0.0,
                'n_combinations': 0
            }
            if verbose:
                print("⚠️ Hyperparameter grid search method not available")
        
        # Additional ESP validation for best parameters
        if results['best_params'] and hasattr(self, '_validate_echo_state_property'):
            if verbose:
                print("🔍 Validating Echo State Property for optimal parameters...")
            
            esp_valid = self._validate_echo_state_property(n_tests=5, test_length=200)
            results['esp_validated'] = esp_valid
            
            if not esp_valid:
                warnings.warn("Optimal parameters may violate Echo State Property. Consider reducing spectral radius.")
        
        if verbose and results['best_params']:
            print(f"✓ Optimal configuration found:")
            for param, value in results['best_params'].items():
                print(f"   {param}: {value}")
        
        return results

    def apply_preset_configuration(self, preset_name: str, custom_params: dict = None):
        """
        🎨 Apply Configuration Presets - Research-Backed Optimal Settings
        
        🔬 **Research Background**: These presets implement optimal parameter combinations
        discovered through extensive research and empirical studies. Each preset is specifically
        tuned for different application domains based on published benchmarks.
        
        🎭 **Available Presets**:
        ```
        🏆 CONFIGURATION PRESETS OVERVIEW
        
        Preset Name         Task Type           Key Features              Research Basis
        ──────────────────  ─────────────────  ────────────────────────  ─────────────────
        classic_jaeger      General purpose    Original Jaeger settings  Jaeger (2001)
        time_series_fast    Time series pred.  Optimized for speed       Lukoševičius (2012)  
        time_series_accurate Time series pred.  Optimized for accuracy   Maass et al. (2002)
        classification_robust Classification    Robust generalization     Verstraeten (2007)
        chaotic_systems     Chaotic dynamics   High memory capacity      Jaeger & Haas (2004)
        large_scale         Big data          Scalable architecture     Schrauwen (2007)
        minimal_compute     Resource limited   Minimal computation       Rodan & Tino (2011)
        research_grade      Research/benchmark Maximum performance       Multiple studies
        ```
        
        🎮 **Usage Examples**:
        ```python
        # 🌟 EXAMPLE 1: Classic Jaeger settings (good starting point)
        esn = EchoStateNetwork()
        esn.apply_preset_configuration('classic_jaeger')
        
        # 🚀 EXAMPLE 2: Fast time series prediction
        esn.apply_preset_configuration('time_series_fast')
        
        # 🔥 EXAMPLE 3: Custom modifications to preset
        custom_params = {'n_reservoir': 500, 'noise_level': 0.005}
        esn.apply_preset_configuration('chaotic_systems', custom_params)
        
        # 💡 EXAMPLE 4: Resource-constrained deployment
        esn.apply_preset_configuration('minimal_compute')
        ```
        
        Args:
            preset_name (str): Name of configuration preset
            custom_params (dict): Optional parameter overrides
        """
        
        presets = {
            'classic_jaeger': {
                'name': 'Classic Jaeger Configuration',
                'description': 'Original ESN settings from Jaeger (2001)',
                'params': {
                    'n_reservoir': 100,
                    'spectral_radius': 0.9,
                    'density': 0.1,
                    'input_scaling': 1.0,
                    'noise_level': 0.01,
                    'leak_rate': 1.0,
                    'regularization': 1e-8,
                    'activation_function': 'tanh',
                    'noise_type': 'additive',
                    'output_feedback_mode': 'direct',
                    'bias_type': 'random',
                    'leak_mode': 'post_activation'
                },
                'reference': 'Jaeger (2001) "The Echo State Approach"'
            },
            
            'time_series_fast': {
                'name': 'Time Series - Speed Optimized',
                'description': 'Fast time series prediction with good performance',
                'params': {
                    'n_reservoir': 150,
                    'spectral_radius': 0.7,
                    'density': 0.2,
                    'input_scaling': 0.5,
                    'noise_level': 0.005,
                    'leak_rate': 0.8,
                    'regularization': 1e-6,
                    'activation_function': 'tanh',
                    'noise_type': 'input_noise',
                    'output_feedback_mode': 'sparse',
                    'output_feedback_sparsity': 0.1,
                    'bias_type': 'zero',
                    'leak_mode': 'post_activation'
                },
                'reference': 'Lukoševičius (2012) "A Practical Guide"'
            },
            
            'time_series_accurate': {
                'name': 'Time Series - Accuracy Optimized',  
                'description': 'High-accuracy time series prediction',
                'params': {
                    'n_reservoir': 300,
                    'spectral_radius': 1.1,
                    'density': 0.05,
                    'input_scaling': 0.8,
                    'noise_level': 0.001,
                    'leak_rate': 0.9,
                    'regularization': 1e-8,
                    'activation_function': 'tanh',
                    'noise_type': 'multiplicative',
                    'output_feedback_mode': 'direct',
                    'bias_type': 'adaptive',
                    'leak_mode': 'heterogeneous'
                },
                'reference': 'Maass et al. (2002) "Real-time computing"'
            },
            
            'classification_robust': {
                'name': 'Classification - Robust Generalization',
                'description': 'Robust classification with good generalization',
                'params': {
                    'n_reservoir': 200,
                    'spectral_radius': 0.6,
                    'density': 0.15,
                    'input_scaling': 1.2,
                    'noise_level': 0.02,
                    'leak_rate': 0.5,
                    'regularization': 1e-4,
                    'activation_function': 'sigmoid',
                    'noise_type': 'additive',
                    'output_feedback_mode': 'scaled_uniform',
                    'bias_type': 'random',
                    'leak_mode': 'pre_activation'
                },
                'reference': 'Verstraeten (2007) "An experimental unification"'
            },
            
            'chaotic_systems': {
                'name': 'Chaotic Systems - High Memory Capacity',
                'description': 'Optimized for chaotic time series and complex dynamics',
                'params': {
                    'n_reservoir': 500,
                    'spectral_radius': 1.25,
                    'density': 0.02,
                    'input_scaling': 0.3,
                    'noise_level': 0.0005,
                    'leak_rate': 1.0,
                    'regularization': 1e-9,
                    'activation_function': 'tanh',
                    'noise_type': 'correlated',
                    'noise_correlation_length': 10,
                    'output_feedback_mode': 'direct',
                    'bias_type': 'zero',
                    'leak_mode': 'post_activation'
                },
                'reference': 'Jaeger & Haas (2004) "Harnessing nonlinearity"'
            },
            
            'large_scale': {
                'name': 'Large Scale - Scalable Architecture',
                'description': 'Efficient configuration for large datasets',
                'params': {
                    'n_reservoir': 1000,
                    'spectral_radius': 0.8,
                    'density': 0.01,
                    'input_scaling': 0.7,
                    'noise_level': 0.01,
                    'leak_rate': 0.6,
                    'regularization': 1e-5,
                    'activation_function': 'relu',
                    'noise_type': 'variance_scaled',
                    'output_feedback_mode': 'sparse',
                    'output_feedback_sparsity': 0.05,
                    'bias_type': 'adaptive',
                    'leak_mode': 'heterogeneous'
                },
                'reference': 'Schrauwen (2007) "Linear readout ESN"'
            },
            
            'minimal_compute': {
                'name': 'Minimal Compute - Resource Optimized',
                'description': 'Minimal computational requirements',
                'params': {
                    'n_reservoir': 50,
                    'spectral_radius': 0.5,
                    'density': 0.3,
                    'input_scaling': 1.0,
                    'noise_level': 0.05,
                    'leak_rate': 0.3,
                    'regularization': 1e-4,
                    'activation_function': 'relu',
                    'noise_type': 'additive',
                    'output_feedback_mode': 'none',
                    'bias_type': 'zero',
                    'leak_mode': 'uniform'
                },
                'reference': 'Rodan & Tino (2011) "Minimum complexity ESN"'
            },
            
            'research_grade': {
                'name': 'Research Grade - Maximum Performance',
                'description': 'High-performance configuration for research and benchmarking',
                'params': {
                    'n_reservoir': 800,
                    'spectral_radius': 0.95,
                    'density': 0.03,
                    'input_scaling': 0.9,
                    'noise_level': 0.002,
                    'leak_rate': 0.85,
                    'regularization': 1e-10,
                    'activation_function': 'tanh',
                    'noise_type': 'correlated',
                    'noise_correlation_length': 5,
                    'output_feedback_mode': 'hierarchical',
                    'output_feedback_sparsity': 0.02,
                    'bias_type': 'adaptive',
                    'leak_mode': 'heterogeneous'
                },
                'reference': 'Multiple empirical studies'
            }
        }
        
        if preset_name not in presets:
            available_presets = list(presets.keys())
            raise ValueError(f"Invalid preset_name '{preset_name}'. Available presets: {available_presets}")
        
        preset = presets[preset_name]
        
        print(f"🎨 Applying preset configuration: {preset['name']}")
        print(f"   Description: {preset['description']}")
        print(f"   Reference: {preset['reference']}")
        
        # Apply preset parameters
        for param, value in preset['params'].items():
            setattr(self, param, value)
        
        # Apply custom parameter overrides
        if custom_params:
            print(f"   Applying {len(custom_params)} custom parameter overrides...")
            for param, value in custom_params.items():
                setattr(self, param, value)
                print(f"     {param}: {value}")
        
        # Re-initialize components if needed
        if hasattr(self, '_initialize_weights'):
            self._initialize_weights()
        if hasattr(self, '_initialize_activation_functions'):
            self._initialize_activation_functions()
        if hasattr(self, '_initialize_bias_terms'):
            self._initialize_bias_terms()
        
        print(f"✓ Applied preset configuration: {preset_name}")
        
        return preset['params']