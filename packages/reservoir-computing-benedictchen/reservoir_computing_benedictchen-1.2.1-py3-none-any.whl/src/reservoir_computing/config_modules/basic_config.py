"""
🔧 Basic Configuration Mixin - Core ESN Parameter Settings
=========================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module contains basic configuration methods for Echo State Networks
extracted from the original monolithic configuration_optimization.py file.

Based on: Herbert Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"
"""

import numpy as np


class BasicConfigurationMixin:
    """
    🔧 Basic Configuration Mixin for Echo State Networks
    
    This mixin provides core configuration capabilities for Echo State Networks,
    implementing fundamental settings from Jaeger 2001.
    
    🌟 Key Features:
    - Activation function configuration (6 types)
    - Noise strategy configuration (6 types)  
    - State collection method configuration
    - Training solver configuration
    - Output feedback control
    - Leaky integration settings
    - Bias term configuration
    """
    
    def configure_activation_function(self, func_type: str, custom_func=None):
        """
        🎯 Configure Reservoir Activation Function - 6 Powerful Options from Jaeger 2001!
        
        🔬 **Research Background**: Jaeger (2001) showed different activation functions 
        dramatically affect Echo State Network performance. This method lets you experiment 
        with all major options to find the perfect fit for your task!
        
        📊 **Visual Guide**:
        ```
        📈 ACTIVATION FUNCTIONS COMPARISON
        ┌─────────────────┬──────────────┬─────────────────┬──────────────────┐
        │  Function Type  │   Formula    │   Range         │   Best For       │
        ├─────────────────┼──────────────┼─────────────────┼──────────────────┤
        │ 🌊 tanh         │ tanh(x)      │ [-1, 1]        │ General purpose  │
        │ 📈 sigmoid      │ 1/(1+e^-x)   │ [0, 1]         │ Binary signals   │  
        │ ⚡ relu         │ max(0,x)     │ [0, ∞]         │ Sparse patterns  │
        │ 🔧 leaky_relu   │ max(0.01x,x) │ (-∞, ∞)       │ Better gradients │
        │ 📏 linear       │ x            │ (-∞, ∞)       │ Linear systems   │
        │ 🎨 custom       │ your_func(x) │ user-defined   │ Special tasks    │
        └─────────────────┴──────────────┴─────────────────┴──────────────────┘
        ```
        
        🎮 **Usage Examples**:
        ```python
        # 🌟 EXAMPLE 1: Classic nonlinear time series (recommended)
        esn = EchoStateNetwork(n_reservoir=100)
        esn.configure_activation_function('tanh')  # Smooth, bounded
        
        # 🚀 EXAMPLE 2: Sparse pattern recognition 
        esn.configure_activation_function('relu')  # Creates sparse representations
        
        # 🔥 EXAMPLE 3: Custom activation for special tasks
        def custom_swish(x):
            return x * (1 / (1 + np.exp(-x)))  # Swish activation
        esn.configure_activation_function('custom', custom_func=custom_swish)
        
        # 💡 EXAMPLE 4: Binary classification tasks
        esn.configure_activation_function('sigmoid')  # Output range [0,1]
        ```
        
        ⚡ **Performance Tips**:
        - 🌊 **tanh**: Best general choice, well-tested in literature
        - 📈 **sigmoid**: Use for positive-only outputs  
        - ⚡ **relu**: Great for sparse representations, faster computation
        - 🔧 **leaky_relu**: Fixes "dying ReLU" problem
        - 📏 **linear**: Only for linear dynamics, loses nonlinearity
        - 🎨 **custom**: Experiment with modern activations (swish, gelu, etc.)
        
        📖 **Research Reference**: Jaeger (2001) "The Echo State Approach" - Section 2.1
        
        Args:
            func_type (str): Activation function type - choose from 6 options above
            custom_func (callable, optional): Your custom activation function (only for 'custom' type)
            
        Raises:
            ValueError: If func_type is not one of the 6 valid options
            
        Example:
            >>> esn = EchoStateNetwork(n_reservoir=200)
            >>> esn.configure_activation_function('tanh')  # Classic choice
            ✓ Activation function set to: tanh
        """
        valid_funcs = ['tanh', 'sigmoid', 'relu', 'leaky_relu', 'linear', 'custom']
        if func_type not in valid_funcs:
            raise ValueError(f"Invalid activation function. Choose from: {valid_funcs}")
        self.activation_function = func_type
        if func_type == 'custom' and custom_func:
            self.custom_activation = custom_func
            if hasattr(self, '_initialize_activation_functions'):
                self._initialize_activation_functions()
        print(f"✓ Activation function set to: {func_type}")

    def configure_noise_type(self, noise_type: str, correlation_length: int = 5, training_ratio: float = 1.0):
        """
        🔊 Configure Reservoir Noise Implementation - 6 Advanced Options from Jaeger 2001!
        
        🔬 **Research Background**: Jaeger (2001) demonstrated that strategic noise injection 
        can improve Echo State Property (ESP) and generalization. This method implements all 
        major noise strategies from the research literature!
        
        📊 **Noise Types Visual Guide**:
        ```
        🎚️ NOISE IMPLEMENTATION COMPARISON
        ┌─────────────────┬──────────────────┬─────────────────┬──────────────────┐
        │   Noise Type    │   Where Applied  │   Formula       │   Best For       │
        ├─────────────────┼──────────────────┼─────────────────┼──────────────────┤
        │ 🎵 additive     │ Reservoir state  │ x + ξ(0,σ²)    │ General use      │
        │ 🎯 input_noise  │ Input signal     │ u + ξ(0,σ²)    │ Robust learning  │  
        │ ⚡ multiplicative│ State scaling    │ x*(1+ξ(0,σ²))  │ Dynamic systems  │
        │ 🌊 correlated   │ Spatial pattern  │ spatially-corr  │ Realistic noise  │
        │ 🎓 train_vs_test│ Different levels │ σ_train≠σ_test  │ Robustness test  │
        │ 📊 variance_scaled│ Adaptive scaling│ σ² ∝ var(input)│ Signal-adaptive  │
        └─────────────────┴──────────────────┴─────────────────┴──────────────────┘
        ```
        
        🎮 **Usage Examples**:
        ```python
        # 🌟 EXAMPLE 1: Input noise for robust learning (Jaeger recommended)
        esn = EchoStateNetwork(n_reservoir=100, noise_level=0.01)
        esn.configure_noise_type('input_noise')  # Noise on inputs only
        
        # 🚀 EXAMPLE 2: Spatially correlated noise (more realistic)
        esn.configure_noise_type('correlated', correlation_length=10)
        
        # 🔥 EXAMPLE 3: Different noise during training vs testing
        esn.configure_noise_type('training_vs_testing', training_ratio=2.0)
        # Training noise = 2.0 * base_noise, testing noise = base_noise
        
        # 💡 EXAMPLE 4: Adaptive noise scaling
        esn.configure_noise_type('variance_scaled')  # Noise ∝ input variance
        ```
        
        ⚡ **Performance Guidelines**:
        - 🎯 **input_noise**: Recommended by Jaeger, improves robustness
        - 🎵 **additive**: Simple but effective, use small noise_level (0.001-0.01)
        - ⚡ **multiplicative**: Good for dynamic systems, models realistic variations
        - 🌊 **correlated**: Most realistic, but computationally expensive
        - 🎓 **training_vs_testing**: Essential for robustness evaluation
        - 📊 **variance_scaled**: Automatically adapts to signal strength
        
        📖 **Research Reference**: Jaeger (2001) "The Echo State Approach" - Section 2.3
        
        Args:
            noise_type (str): Noise implementation strategy (6 options above)
            correlation_length (int): Spatial correlation length for 'correlated' noise
            training_ratio (float): Training/testing noise ratio for 'training_vs_testing'
            
        Raises:
            ValueError: If noise_type is not one of the 6 valid options
            
        Example:
            >>> esn = EchoStateNetwork(noise_level=0.01)
            >>> esn.configure_noise_type('input_noise')  # Jaeger's recommendation
            ✓ Noise type set to: input_noise
        """
        valid_types = ['additive', 'input_noise', 'multiplicative', 'correlated', 'training_vs_testing', 'variance_scaled']
        if noise_type not in valid_types:
            raise ValueError(f"Invalid noise type. Choose from: {valid_types}")
        self.noise_type = noise_type
        self.noise_correlation_length = correlation_length
        self.training_noise_ratio = training_ratio
        print(f"✓ Noise type set to: {noise_type}")

    def configure_state_collection_method(self, method: str):
        """
        📊 Configure State Collection Strategy - 7 Advanced Methods for Optimal Training
        
        🔬 **Research Background**: Different state collection strategies can dramatically
        affect training efficiency and model performance. This method implements advanced
        techniques for optimal reservoir state utilization.
        
        📈 **State Collection Methods**:
        ```
        🔍 STATE COLLECTION COMPARISON
        ┌──────────────────┬──────────────────┬─────────────────┬─────────────────┐
        │     Method       │   Description    │   Computation   │   Best For      │
        ├──────────────────┼──────────────────┼─────────────────┼─────────────────┤
        │ all_states       │ Use every state  │ O(n*T)         │ Small datasets  │
        │ subsampled       │ Every nth state  │ O(n*T/k)       │ Large datasets  │
        │ exponential      │ Exp. weighting   │ O(n*T)         │ Recent focus    │
        │ multi_horizon    │ Multiple delays  │ O(n*T*k)       │ Long memory     │
        │ adaptive_spacing │ Dynamic sampling │ O(n*T)         │ Non-uniform     │
        │ adaptive_washout │ Smart washout    │ O(n*T)         │ Fast convergence│
        │ ensemble_washout │ Multi-washout    │ O(n*T*k)       │ Robustness      │
        └──────────────────┴──────────────────┴─────────────────┴─────────────────┘
        ```
        
        Args:
            method (str): State collection method from the 7 options above
            
        Example:
            >>> esn.configure_state_collection_method('adaptive_spacing')
            ✓ State collection method set to: adaptive_spacing
        """
        valid_methods = ['all_states', 'subsampled', 'exponential', 'multi_horizon', 'adaptive_spacing', 'adaptive_washout', 'ensemble_washout']
        if method not in valid_methods:
            raise ValueError(f"Invalid state collection method. Choose from: {valid_methods}")
        self.state_collection_method = method
        print(f"✓ State collection method set to: {method}")

    def configure_training_solver(self, solver: str):
        """
        🔧 Configure Training Solver - 4 Advanced Optimization Methods
        
        Args:
            solver (str): Training solver - 'ridge', 'pseudo_inverse', 'lsqr', 'elastic_net'
            
        Example:
            >>> esn.configure_training_solver('ridge')
            ✓ Training solver set to: ridge
        """
        valid_solvers = ['ridge', 'pseudo_inverse', 'lsqr', 'elastic_net']
        if solver not in valid_solvers:
            raise ValueError(f"Invalid training solver. Choose from: {valid_solvers}")
        self.training_solver = solver
        print(f"✓ Training solver set to: {solver}")

    def configure_output_feedback(self, mode: str, sparsity: float = 0.1, enable: bool = True):
        """
        🔄 Configure Output Feedback - 4 Advanced Modes from Jaeger 2001!
        
        🔬 **Research Background**: Jaeger (2001) Figure 1 shows output feedback as crucial 
        for recurrent systems. This method implements all feedback strategies from the paper, 
        enabling the full power of Echo State Networks with teacher forcing!
        
        📊 **Feedback Modes Visual Guide**:
        ```
        🔄 OUTPUT FEEDBACK COMPARISON  
        ┌─────────────────┬──────────────────┬─────────────────┬──────────────────┐
        │ Feedback Mode   │   Connection     │   Computation   │   Best For       │
        ├─────────────────┼──────────────────┼─────────────────┼──────────────────┤
        │ 🎯 direct       │ All → all        │ W_back @ y(t)   │ Full recurrence  │
        │ ⚡ sparse       │ Few → few        │ Sparse W_back   │ Fast computation │  
        │ 📏 scaled_uniform│ Scaled uniform   │ α * y(t)        │ Simple control   │
        │ 🏗️ hierarchical │ Layer-wise       │ Hierarchical    │ Complex dynamics │
        └─────────────────┴──────────────────┴─────────────────┴──────────────────┘
        ```
        
        Args:
            mode (str): Feedback mode ('direct', 'sparse', 'scaled_uniform', 'hierarchical')
            sparsity (float): Connection sparsity for 'sparse' mode
            enable (bool): Whether to enable output feedback
            
        Example:
            >>> esn.configure_output_feedback('sparse', sparsity=0.2)
            ✓ Output feedback configured: sparse (sparsity=0.2)
        """
        valid_modes = ['direct', 'sparse', 'scaled_uniform', 'hierarchical']
        if mode not in valid_modes:
            raise ValueError(f"Invalid feedback mode. Choose from: {valid_modes}")
        
        self.output_feedback_mode = mode
        self.output_feedback_sparsity = sparsity
        self.output_feedback_enabled = enable
        
        if enable:
            print(f"✓ Output feedback configured: {mode} (sparsity={sparsity})")
        else:
            print("✓ Output feedback disabled")

    def configure_leaky_integration(self, mode: str, custom_rates=None):
        """
        ⏰ Configure Leaky Integration - 4 Advanced Temporal Memory Modes
        
        Args:
            mode (str): Leaky integration mode ('none', 'uniform', 'adaptive', 'custom')
            custom_rates: Custom leak rates for 'custom' mode
            
        Example:
            >>> esn.configure_leaky_integration('adaptive')
            ✓ Leaky integration set to: adaptive
        """
        valid_modes = ['none', 'uniform', 'adaptive', 'custom']
        if mode not in valid_modes:
            raise ValueError(f"Invalid leaky integration mode. Choose from: {valid_modes}")
        
        self.leaky_integration_mode = mode
        if mode == 'custom' and custom_rates is not None:
            self.custom_leak_rates = custom_rates
        print(f"✓ Leaky integration set to: {mode}")

    def configure_bias_terms(self, bias_type: str, scale: float = 0.1):
        """
        ⚖️ Configure Bias Terms - 4 Advanced Bias Strategies
        
        Args:
            bias_type (str): Bias type ('none', 'random', 'learned', 'adaptive')
            scale (float): Bias scaling factor
            
        Example:
            >>> esn.configure_bias_terms('adaptive', scale=0.2)
            ✓ Bias terms configured: adaptive (scale=0.2)
        """
        valid_types = ['none', 'random', 'learned', 'adaptive']
        if bias_type not in valid_types:
            raise ValueError(f"Invalid bias type. Choose from: {valid_types}")
        
        self.bias_type = bias_type
        self.bias_scale = scale
        print(f"✓ Bias terms configured: {bias_type} (scale={scale})")

    def set_training_mode(self, training: bool = True):
        """
        🎓 Set Training Mode - Toggle Between Training and Inference
        
        Args:
            training (bool): Whether the network is in training mode
            
        Example:
            >>> esn.set_training_mode(False)  # Switch to inference mode
            ✓ Training mode: False
        """
        self.training_mode = training
        print(f"✓ Training mode: {training}")

    def enable_sparse_computation(self, threshold: float = 1e-6):
        """
        ⚡ Enable Sparse Computation - Optimize Memory and Speed
        
        Args:
            threshold (float): Sparsity threshold for matrix operations
            
        Example:
            >>> esn.enable_sparse_computation(threshold=1e-5)
            ✓ Sparse computation enabled with threshold: 1e-05
        """
        self.sparse_computation = True
        self.sparse_threshold = threshold
        print(f"✓ Sparse computation enabled with threshold: {threshold}")

    def get_configuration_summary(self) -> dict:
        """
        📋 Get Configuration Summary - Complete Overview of All Settings
        
        Returns:
            dict: Complete configuration summary
            
        Example:
            >>> summary = esn.get_configuration_summary()
            >>> print(f"Activation: {summary['activation_function']}")
        """
        summary = {
            'activation_function': getattr(self, 'activation_function', 'tanh'),
            'noise_type': getattr(self, 'noise_type', 'additive'),
            'state_collection_method': getattr(self, 'state_collection_method', 'all_states'),
            'training_solver': getattr(self, 'training_solver', 'ridge'),
            'output_feedback_mode': getattr(self, 'output_feedback_mode', 'none'),
            'output_feedback_enabled': getattr(self, 'output_feedback_enabled', False),
            'leaky_integration_mode': getattr(self, 'leaky_integration_mode', 'none'),
            'bias_type': getattr(self, 'bias_type', 'none'),
            'training_mode': getattr(self, 'training_mode', True),
            'sparse_computation': getattr(self, 'sparse_computation', False)
        }
        return summary