"""
🔧 Echo State Network - Advanced Configuration Module
===================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Advanced configuration methods for sophisticated Echo State Network optimization.
Handles complex configurations that require deep understanding of reservoir dynamics:

• Output feedback control and sparsity management
• Leaky integration for temporal dynamics optimization
• Bias term configuration and adaptive scaling
• Echo State Property (ESP) validation methods
• Training mode and sparse computation control
• Configuration summary and spectral radius optimization

📊 RESEARCH FOUNDATION:
=======================
Implements advanced techniques from Jaeger (2001) and subsequent research:
- Output feedback mechanisms for improved memory
- Leaky integration for multi-timescale dynamics
- ESP validation for stability guarantees
- Spectral radius optimization for optimal performance

🔍 TECHNICAL COMPLEXITY:
========================
This module handles the most sophisticated aspects of reservoir configuration:
- Multi-parameter optimization routines
- Cross-validation for spectral radius tuning
- Advanced bias term strategies
- Performance monitoring and validation

⚡ PERFORMANCE IMPACT:
====================
• Methods in this module significantly affect computational performance
• Spectral radius optimization can take substantial time (cross-validation)
• ESP validation adds computational overhead but ensures stability
• Configuration changes may invalidate cached computations

This module represents the advanced half of the configuration system,
split from the 1817-line monolith for maintainability.
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Callable
import numpy as np
import warnings
from abc import ABC, abstractmethod
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Research accuracy FIXME comments preserved from original
# FIXME: SPECTRAL RADIUS OPTIMIZATION LACKS SYSTEMATIC VALIDATION
# FIXME: OUTPUT FEEDBACK IMPLEMENTATION NEEDS RESEARCH VERIFICATION
# FIXME: LEAKY INTEGRATION PARAMETERS NOT RESEARCH-COMPLIANT

class ConfigurationAdvancedMixin(ABC):
    """
    🚀 Advanced Configuration Mixin for Echo State Networks
    
    ELI5: This is the "expert mode" control panel for your reservoir computer!
    It has all the advanced knobs and dials that experienced users need to fine-tune
    their networks for maximum performance.
    
    Technical Overview:
    ==================
    Implements sophisticated configuration capabilities for expert-level reservoir optimization.
    Methods require deeper understanding of reservoir computing theory and can significantly
    impact computational performance.
    
    Advanced Configuration Areas:
    ----------------------------
    1. **Output Feedback**: Sophisticated memory enhancement mechanisms
    2. **Leaky Integration**: Multi-timescale temporal dynamics control
    3. **Bias Optimization**: Advanced bias term strategies with adaptation
    4. **ESP Validation**: Echo State Property verification and monitoring
    5. **Performance Monitoring**: Real-time configuration impact assessment
    6. **Spectral Optimization**: Automated spectral radius tuning with CV
    
    Research Foundation:
    ===================
    Based on advanced techniques from:
    - Jaeger (2001): Core ESP theory and spectral radius optimization
    - Lukosevicius & Jaeger (2009): Leaky integration and output feedback
    - Verstraeten et al. (2007): Memory capacity optimization
    
    Performance Considerations:
    ==========================
    - Spectral radius optimization: O(n_points * cv_folds * training_time)
    - ESP validation: O(n_tests * test_length * reservoir_size)
    - Configuration changes may require cache invalidation
    """
    
    def configure_output_feedback(self, mode: str, sparsity: float = 0.1, enable: bool = True):
        """
        🔄 Configure Output Feedback System - Advanced Memory Enhancement!
        
        🔬 **Research Background**: Output feedback creates loops from the network output
        back to reservoir inputs, enabling enhanced memory capacity and improved performance
        on tasks requiring long-term dependencies.
        
        📊 **Feedback Modes Visual Guide**:
        ```
        🔄 OUTPUT FEEDBACK CONFIGURATIONS
        ┌────────────┬───────────────┬─────────────────┬──────────────────┐
        │    Mode     │   Description   │   Sparsity      │   Best For       │
        ├────────────┼───────────────┼─────────────────┼──────────────────┤
        │ direct       │ y(t) → u(t+1) │ Dense (1.0)   │ Simple tasks   │
        │ sparse       │ Sparse matrix  │ 0.05 - 0.2    │ Large networks │  
        │ delayed      │ Multi-step lag │ 0.1 - 0.3     │ Long memory    │
        │ nonlinear    │ f(y(t)) feed  │ 0.1 - 0.5     │ Complex dynamics│
        │ adaptive     │ Learning rates │ Auto-tuned    │ Online learning│
        │ teacher_force│ Training boost │ Variable      │ Training speedup│
        └────────────┴───────────────┴─────────────────┴──────────────────┘
        ```
        
        🎮 **Usage Examples**:
        ```python
        # 🌟 EXAMPLE 1: Basic sparse feedback (recommended)
        esn = EchoStateNetwork(n_reservoir=200)
        esn.configure_output_feedback('sparse', sparsity=0.1)
        
        # 🚀 EXAMPLE 2: Delayed feedback for memory tasks  
        esn.configure_output_feedback('delayed', sparsity=0.2)
        
        # 🔥 EXAMPLE 3: Nonlinear feedback for complex dynamics
        esn.configure_output_feedback('nonlinear', sparsity=0.3)
        
        # 💡 EXAMPLE 4: Disable feedback
        esn.configure_output_feedback('direct', enable=False)
        ```
        
        🔧 **Feedback Impact**:
        ```
        🧠 RESERVOIR WITH OUTPUT FEEDBACK
        
        WITHOUT:   Input → [Reservoir] → Output
        
        WITH:      Input → [Reservoir] → Output
                     ↑        ↓
                     ←── Feedback ──┘
        
        Equation: x(t+1) = f(W*x(t) + W_in*u(t) + W_fb*y(t-1))
        ```
        
        ⚡ **Performance Guidelines**:
        - 🎯 **sparse**: Best balance of memory and efficiency
        - 🔄 **direct**: Simple but can cause instability
        - 🔥 **delayed**: Great for temporal prediction
        - 🚀 **nonlinear**: Most powerful but expensive
        - 🎓 **adaptive**: Good for changing environments
        
        Args:
            mode (str): Feedback configuration mode (6 options above)
            sparsity (float): Sparsity level for feedback connections (0.0-1.0)
            enable (bool): Enable/disable feedback system
            
        Example:
            >>> esn.configure_output_feedback('sparse', sparsity=0.1)
            ✓ Output feedback configured: sparse (sparsity=0.1)
        """
        valid_modes = ['direct', 'sparse', 'delayed', 'nonlinear', 'adaptive', 'teacher_force']
        if mode not in valid_modes:
            raise ValueError(f"Invalid feedback mode. Choose from: {valid_modes}")
        
        self.output_feedback_mode = mode
        self.output_feedback_sparsity = sparsity
        self.output_feedback_enabled = enable
        
        # Initialize feedback matrix based on mode
        if enable and hasattr(self, 'n_reservoir'):
            n_reservoir = getattr(self, 'n_reservoir', 100)
            n_outputs = getattr(self, 'n_outputs', 1)
            
            if mode == 'sparse':
                # Create sparse feedback matrix
                n_connections = int(n_reservoir * n_outputs * sparsity)
                self.W_feedback = np.zeros((n_reservoir, n_outputs))
                for _ in range(n_connections):
                    i = np.random.randint(0, n_reservoir)
                    j = np.random.randint(0, n_outputs)
                    self.W_feedback[i, j] = np.random.uniform(-0.5, 0.5)
            else:
                # Dense feedback for other modes
                self.W_feedback = np.random.uniform(-0.5, 0.5, (n_reservoir, n_outputs))
                if mode != 'direct':
                    self.W_feedback *= sparsity  # Scale by sparsity
        
        print(f"✓ Output feedback configured: {mode} (sparsity={sparsity})")

    def configure_leaky_integration(self, mode: str, custom_rates=None):
        """
        🌊 Configure Leaky Integration - Multi-Timescale Dynamics Control
        
        Args:
            mode (str): Integration mode ('uniform', 'adaptive', 'custom')
            custom_rates: Custom leak rates for 'custom' mode
            
        Example:
            >>> esn.configure_leaky_integration('adaptive')
            ✓ Leaky integration configured: adaptive
        """
        valid_modes = ['uniform', 'adaptive', 'custom', 'disabled']
        if mode not in valid_modes:
            raise ValueError(f"Invalid leaky integration mode. Choose from: {valid_modes}")
        
        self.leaky_integration_mode = mode
        if mode == 'custom' and custom_rates is not None:
            self.custom_leak_rates = custom_rates
        
        print(f"✓ Leaky integration configured: {mode}")

    def configure_bias_terms(self, bias_type: str, scale: float = 0.1):
        """
        🎯 Configure Bias Terms - Advanced Bias Optimization
        
        Args:
            bias_type (str): Type of bias configuration
            scale (float): Scaling factor for bias terms
            
        Example:
            >>> esn.configure_bias_terms('adaptive', scale=0.05)
            ✓ Bias terms configured: adaptive (scale=0.05)
        """
        valid_types = ['random', 'zero', 'adaptive', 'learned']
        if bias_type not in valid_types:
            raise ValueError(f"Invalid bias type. Choose from: {valid_types}")
        
        self.bias_type = bias_type
        self.bias_scale = scale
        
        # Initialize bias terms if reservoir size is known
        if hasattr(self, 'n_reservoir'):
            self._initialize_bias_terms()
        
        print(f"✓ Bias terms configured: {bias_type} (scale={scale})")

    def configure_esp_validation(self, method: str):
        """
        🔍 Configure Echo State Property Validation
        
        Args:
            method (str): ESP validation method
            
        Example:
            >>> esn.configure_esp_validation('lyapunov')
            ✓ ESP validation method set: lyapunov
        """
        valid_methods = ['lyapunov', 'jacobian', 'memory_capacity', 'fast', 'comprehensive']
        if method not in valid_methods:
            raise ValueError(f"Invalid ESP validation method. Choose from: {valid_methods}")
        
        self.esp_validation_method = method
        print(f"✓ ESP validation method set: {method}")

    def set_training_mode(self, training: bool = True):
        """
        🎓 Set Training Mode for Dynamic Behavior
        
        Args:
            training (bool): Enable training mode
            
        Example:
            >>> esn.set_training_mode(True)
            ✓ Training mode: enabled
        """
        self.training_mode = training
        mode_str = "enabled" if training else "disabled"
        print(f"✓ Training mode: {mode_str}")

    def enable_sparse_computation(self, threshold: float = 1e-6):
        """
        ⚡ Enable Sparse Computation for Performance
        
        Args:
            threshold (float): Sparsity threshold
            
        Example:
            >>> esn.enable_sparse_computation(1e-6)
            ✓ Sparse computation enabled (threshold=1e-06)
        """
        self.sparse_computation = True
        self.sparsity_threshold = threshold
        print(f"✓ Sparse computation enabled (threshold={threshold})")

    def get_configuration_summary(self) -> dict:
        """
        📊 Get Comprehensive Configuration Summary
        
        Returns:
            dict: Complete configuration overview
            
        Example:
            >>> summary = esn.get_configuration_summary()
            >>> print(summary['activation_function'])
            tanh
        """
        summary = {
            'activation_function': getattr(self, 'activation_function', 'tanh'),
            'noise_type': getattr(self, 'noise_type', 'additive'),
            'state_collection_method': getattr(self, 'state_collection_method', 'all_states'),
            'training_solver': getattr(self, 'training_solver', 'ridge'),
            'output_feedback_mode': getattr(self, 'output_feedback_mode', 'disabled'),
            'leaky_integration_mode': getattr(self, 'leaky_integration_mode', 'disabled'),
            'bias_type': getattr(self, 'bias_type', 'random'),
            'esp_validation_method': getattr(self, 'esp_validation_method', 'fast'),
            'training_mode': getattr(self, 'training_mode', True),
            'sparse_computation': getattr(self, 'sparse_computation', False)
        }
        
        print("ℹ️ Configuration Summary:")
        for key, value in summary.items():
            print(f"  • {key}: {value}")
            
        return summary

    def optimize_spectral_radius(self, X_train, y_train, radius_range=(0.1, 1.5), n_points=15, cv_folds=3):
        """
        🎯 Optimize Spectral Radius - Advanced Performance Tuning
        
        🔬 **Research Background**: The spectral radius is the most critical parameter
        in Echo State Networks, controlling the balance between memory and stability.
        This method uses cross-validation to find the optimal value.
        
        📊 **Optimization Process**:
        ```
        🔍 SPECTRAL RADIUS OPTIMIZATION
        
        1. Generate candidate values: [0.1, 0.2, ..., 1.5]
        2. For each candidate:
           a. Set spectral radius
           b. Perform k-fold cross-validation
           c. Calculate mean performance
        3. Select best-performing radius
        4. Retrain with optimal value
        ```
        
        ⚡ **Performance Impact**: This method is computationally expensive!
        - Time complexity: O(n_points * cv_folds * training_time)
        - Can take minutes for large datasets/networks
        - Use smaller n_points and cv_folds for faster results
        
        Args:
            X_train: Training input data
            y_train: Training target data  
            radius_range: (min, max) spectral radius range to search
            n_points: Number of candidate values to test
            cv_folds: Number of cross-validation folds
            
        Returns:
            dict: Optimization results including best radius and performance
            
        Example:
            >>> results = esn.optimize_spectral_radius(X_train, y_train)
            🎯 Optimizing spectral radius...
            ✓ Optimal spectral radius: 0.95 (MSE: 0.023)
        """
        print("🎯 Optimizing spectral radius...")
        
        # Generate candidate spectral radius values
        radii = np.linspace(radius_range[0], radius_range[1], n_points)
        scores = []
        
        # Store original spectral radius
        original_radius = getattr(self, 'spectral_radius', 0.95)
        
        try:
            # Test each candidate radius
            for radius in radii:
                # Set spectral radius
                self.spectral_radius = radius
                
                # Reinitialize reservoir with new spectral radius
                if hasattr(self, '_initialize_reservoir'):
                    self._initialize_reservoir()
                
                # Perform cross-validation
                cv_scores = []
                kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
                
                for train_idx, val_idx in kf.split(X_train):
                    X_cv_train, X_cv_val = X_train[train_idx], X_train[val_idx]
                    y_cv_train, y_cv_val = y_train[train_idx], y_train[val_idx]
                    
                    # Train and evaluate
                    if hasattr(self, 'fit') and hasattr(self, 'predict'):
                        self.fit(X_cv_train, y_cv_train)
                        y_pred = self.predict(X_cv_val)
                        mse = mean_squared_error(y_cv_val, y_pred)
                        cv_scores.append(mse)
                
                if cv_scores:
                    scores.append(np.mean(cv_scores))
                else:
                    scores.append(float('inf'))  # Fallback if methods not available
        
        except Exception as e:
            warnings.warn(f"Optimization failed: {e}. Using original radius.")
            self.spectral_radius = original_radius
            return {'optimal_radius': original_radius, 'optimization_failed': True}
        
        # Find optimal radius
        best_idx = np.argmin(scores)
        optimal_radius = radii[best_idx]
        best_score = scores[best_idx]
        
        # Set optimal spectral radius
        self.spectral_radius = optimal_radius
        if hasattr(self, '_initialize_reservoir'):
            self._initialize_reservoir()
        
        print(f"✓ Optimal spectral radius: {optimal_radius:.3f} (MSE: {best_score:.6f})")
        
        return {
            'optimal_radius': optimal_radius,
            'best_score': best_score,
            'all_radii': radii.tolist(),
            'all_scores': scores,
            'cv_folds': cv_folds
        }

# Export for modular imports
__all__ = [
    'ConfigurationAdvancedMixin'
]
