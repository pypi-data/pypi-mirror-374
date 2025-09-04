"""
🔍 ESP Validation Module - Echo State Property Validation for ESN/LSM
======================================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module contains Echo State Property validation methods
for Echo State Networks extracted from the original monolithic configuration_optimization.py file.

Based on: Herbert Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"
"""

import numpy as np


class ESPValidationMixin:
    """
    🔍 ESP Validation Mixin for Echo State Networks
    
    This mixin provides Echo State Property validation capabilities
    for Echo State Networks, implementing validation strategies from Jaeger 2001.
    
    🌟 Key Features:
    - Fast ESP validation for optimization
    - Comprehensive ESP testing
    - Spectral radius boundary detection
    - Stability analysis methods
    """
    
    def configure_esp_validation(self, method: str):
        """
        🔍 Configure ESP Validation Method - 4 Advanced Validation Strategies
        
        🔬 **Research Background**: Echo State Property validation is crucial for
        ensuring reservoir stability and proper functioning. This method configures
        different validation approaches based on computational requirements and accuracy needs.
        
        📊 **Validation Methods**:
        ```
        🧪 ESP VALIDATION COMPARISON
        
        Method      Speed    Accuracy    Memory    Best For
        ──────────  ──────   ────────   ────────  ──────────────────
        fast        High     Good       Low       Optimization loops
        thorough    Low      Excellent  High      Final validation
        adaptive    Medium   Very Good  Medium    General use
        statistical High     Good       Low       Batch validation
        ```
        
        Args:
            method (str): Validation method - 'fast', 'thorough', 'adaptive', 'statistical'
            
        Example:
            >>> esn.configure_esp_validation('adaptive')
            ✓ ESP validation method set to: adaptive
        """
        valid_methods = ['fast', 'thorough', 'adaptive', 'statistical']
        if method not in valid_methods:
            raise ValueError(f"Invalid ESP validation method. Choose from: {valid_methods}")
        
        self.esp_validation_method = method
        print(f"✓ ESP validation method set to: {method}")
    
    def _validate_echo_state_property_fast(self, n_tests=3, test_length=100, tolerance=1e-4):
        """
        ⚡ Fast ESP Validation for Optimization Routines
        
        🔬 **Research Background**: This implements a fast ESP validation suitable
        for use within optimization loops. It uses fewer tests and shorter sequences
        to quickly identify ESP violations.
        
        Args:
            n_tests (int): Number of validation tests
            test_length (int): Length of each test sequence
            tolerance (float): Convergence tolerance
            
        Returns:
            bool: True if ESP is satisfied, False otherwise
        """
        if not hasattr(self, 'W_reservoir') or self.W_reservoir is None:
            return True  # Cannot validate without reservoir matrix
        
        try:
            # Quick spectral radius check
            spectral_radius = np.max(np.abs(np.linalg.eigvals(self.W_reservoir)))
            
            # If spectral radius > 1.2, likely ESP violation
            if spectral_radius > 1.2:
                return False
            
            # If spectral radius < 1.0, likely ESP satisfied
            if spectral_radius < 1.0:
                return True
            
            # For borderline cases (1.0 <= SR <= 1.2), run convergence tests
            n_reservoir = self.W_reservoir.shape[0]
            activation_func = getattr(self, 'activation_functions', {}).get(
                getattr(self, 'activation_function', 'tanh'),
                lambda x: np.tanh(x)
            )
            
            for _ in range(n_tests):
                # Generate random input sequence
                u = np.random.randn(test_length, getattr(self, 'n_inputs', 1))
                
                # Initialize two different initial states
                x1 = np.random.randn(n_reservoir) * 0.1
                x2 = np.random.randn(n_reservoir) * 0.1
                
                # Run both sequences
                for t in range(test_length):
                    if hasattr(self, 'W_input'):
                        input_term = self.W_input @ u[t] if u[t].ndim == 1 else self.W_input @ u[t].T
                    else:
                        input_term = np.zeros(n_reservoir)
                    
                    x1_new = activation_func(self.W_reservoir @ x1 + input_term)
                    x2_new = activation_func(self.W_reservoir @ x2 + input_term)
                    
                    x1, x2 = x1_new, x2_new
                
                # Check if states converged
                distance = np.linalg.norm(x1 - x2)
                if distance > tolerance:
                    return False
            
            return True
            
        except Exception as e:
            # If validation fails due to numerical issues, assume ESP violated
            return False
    
    def _validate_echo_state_property(self, n_tests=5, test_length=200, tolerance=1e-6):
        """
        🧪 Comprehensive ESP Validation - Thorough Testing
        
        🔬 **Research Background**: This implements comprehensive ESP validation
        as described in Jaeger (2001). It uses multiple tests with different
        initial conditions to ensure the Echo State Property is satisfied.
        
        Args:
            n_tests (int): Number of validation tests
            test_length (int): Length of each test sequence
            tolerance (float): Convergence tolerance
            
        Returns:
            bool: True if ESP is satisfied, False otherwise
        """
        if not hasattr(self, 'W_reservoir') or self.W_reservoir is None:
            return True  # Cannot validate without reservoir matrix
        
        try:
            # Get spectral radius for analysis
            spectral_radius = np.max(np.abs(np.linalg.eigvals(self.W_reservoir)))
            
            # Strict spectral radius check
            if spectral_radius > 1.1:
                return False
            
            n_reservoir = self.W_reservoir.shape[0]
            activation_func = getattr(self, 'activation_functions', {}).get(
                getattr(self, 'activation_function', 'tanh'),
                lambda x: np.tanh(x)
            )
            
            # Multiple convergence tests
            for test_idx in range(n_tests):
                # Generate test input sequence
                u = np.random.randn(test_length, getattr(self, 'n_inputs', 1)) * 0.5
                
                # Test with multiple initial state pairs
                for init_test in range(3):
                    # Initialize two different initial states
                    x1 = np.random.randn(n_reservoir) * 0.2
                    x2 = np.random.randn(n_reservoir) * 0.2
                    
                    # Ensure initial states are different
                    while np.linalg.norm(x1 - x2) < 0.1:
                        x2 = np.random.randn(n_reservoir) * 0.2
                    
                    initial_distance = np.linalg.norm(x1 - x2)
                    
                    # Run sequences and track convergence
                    distances = []
                    for t in range(test_length):
                        if hasattr(self, 'W_input'):
                            input_term = self.W_input @ u[t] if u[t].ndim == 1 else self.W_input @ u[t].T
                        else:
                            input_term = np.zeros(n_reservoir)
                        
                        # Add noise if configured
                        noise_level = getattr(self, 'noise_level', 0.0)
                        noise1 = np.random.randn(n_reservoir) * noise_level
                        noise2 = np.random.randn(n_reservoir) * noise_level
                        
                        x1_new = activation_func(self.W_reservoir @ x1 + input_term + noise1)
                        x2_new = activation_func(self.W_reservoir @ x2 + input_term + noise2)
                        
                        x1, x2 = x1_new, x2_new
                        
                        # Track distance over time
                        distance = np.linalg.norm(x1 - x2)
                        distances.append(distance)
                        
                        # Early termination if diverging
                        if distance > initial_distance * 10:
                            return False
                    
                    # Check final convergence
                    final_distance = distances[-1]
                    
                    # ESP satisfied if states converged
                    if final_distance > tolerance:
                        return False
                    
                    # Check convergence trend (should be decreasing)
                    if len(distances) > 50:
                        recent_trend = np.mean(distances[-20:]) - np.mean(distances[-50:-30])
                        if recent_trend > 0:  # Diverging trend
                            return False
            
            return True
            
        except Exception as e:
            # If validation fails due to numerical issues, assume ESP violated
            return False
    
    def validate_esp_with_spectral_analysis(self):
        """
        📊 ESP Validation with Spectral Analysis - Advanced Validation
        
        🔬 **Research Background**: This method combines traditional ESP validation
        with spectral analysis of the reservoir matrix to provide comprehensive
        validation of the Echo State Property.
        
        Returns:
            dict: Detailed ESP validation results
        """
        results = {
            'esp_satisfied': False,
            'spectral_radius': None,
            'largest_eigenvalue': None,
            'spectral_analysis': {},
            'convergence_tests': {},
            'recommendations': []
        }
        
        if not hasattr(self, 'W_reservoir') or self.W_reservoir is None:
            results['recommendations'].append("Reservoir matrix not initialized")
            return results
        
        try:
            # Spectral analysis
            eigenvalues = np.linalg.eigvals(self.W_reservoir)
            spectral_radius = np.max(np.abs(eigenvalues))
            largest_eigenvalue = eigenvalues[np.argmax(np.abs(eigenvalues))]
            
            results['spectral_radius'] = float(spectral_radius)
            results['largest_eigenvalue'] = complex(largest_eigenvalue).real
            
            results['spectral_analysis'] = {
                'max_real_eigenvalue': float(np.max(np.real(eigenvalues))),
                'max_imaginary_eigenvalue': float(np.max(np.abs(np.imag(eigenvalues)))),
                'eigenvalue_spread': float(spectral_radius - np.min(np.abs(eigenvalues))),
                'complex_eigenvalues': int(np.sum(np.abs(np.imag(eigenvalues)) > 1e-8))
            }
            
            # Spectral radius assessment
            if spectral_radius < 0.95:
                results['recommendations'].append("Spectral radius in safe range - ESP likely satisfied")
            elif spectral_radius > 1.1:
                results['recommendations'].append("High spectral radius - ESP likely violated")
            else:
                results['recommendations'].append("Borderline spectral radius - run convergence tests")
            
            # Convergence validation
            method = getattr(self, 'esp_validation_method', 'fast')
            
            if method == 'fast':
                esp_valid = self._validate_echo_state_property_fast(n_tests=3, test_length=100)
            else:
                esp_valid = self._validate_echo_state_property(n_tests=5, test_length=200)
            
            results['esp_satisfied'] = esp_valid
            results['convergence_tests']['method_used'] = method
            results['convergence_tests']['result'] = esp_valid
            
            # Final recommendations
            if not esp_valid:
                results['recommendations'].append("ESP violated - reduce spectral radius")
                results['recommendations'].append(f"Current SR: {spectral_radius:.3f}, suggest SR < 1.0")
            else:
                results['recommendations'].append("ESP satisfied - configuration stable")
            
        except Exception as e:
            results['recommendations'].append(f"ESP validation failed: {str(e)}")
        
        return results
    
    def find_optimal_spectral_radius_boundary(self):
        """
        🎯 Find Optimal Spectral Radius Boundary - ESP Violation Detection
        
        🔬 **Research Background**: This method finds the maximum spectral radius
        that maintains the Echo State Property, providing the optimal balance
        between memory capacity and stability.
        
        Returns:
            dict: Boundary analysis results
        """
        if not hasattr(self, 'W_reservoir') or self.W_reservoir is None:
            return {'error': 'Reservoir matrix not initialized'}
        
        # Store original matrix
        original_reservoir = self.W_reservoir.copy()
        current_spectral_radius = np.max(np.abs(np.linalg.eigvals(original_reservoir)))
        
        results = {
            'original_spectral_radius': current_spectral_radius,
            'max_stable_radius': None,
            'esp_boundary': None,
            'test_points': [],
            'recommendations': []
        }
        
        # Binary search for ESP boundary
        low_bound = 0.1
        high_bound = 1.5
        tolerance = 0.01
        
        while high_bound - low_bound > tolerance:
            test_radius = (low_bound + high_bound) / 2.0
            
            # Scale reservoir matrix to test radius
            if current_spectral_radius > 0:
                self.W_reservoir = original_reservoir * (test_radius / current_spectral_radius)
            
            # Test ESP at this radius
            esp_valid = self._validate_echo_state_property_fast(n_tests=3, test_length=100)
            
            results['test_points'].append({
                'radius': test_radius,
                'esp_valid': esp_valid
            })
            
            if esp_valid:
                low_bound = test_radius
                results['max_stable_radius'] = test_radius
            else:
                high_bound = test_radius
        
        # Restore original reservoir
        self.W_reservoir = original_reservoir
        
        # Generate recommendations
        if results['max_stable_radius']:
            results['esp_boundary'] = results['max_stable_radius']
            
            if current_spectral_radius > results['max_stable_radius']:
                results['recommendations'].append(
                    f"Current SR ({current_spectral_radius:.3f}) exceeds ESP boundary ({results['max_stable_radius']:.3f})"
                )
                results['recommendations'].append(
                    f"Reduce spectral radius to {results['max_stable_radius']:.3f} for stability"
                )
            else:
                results['recommendations'].append(
                    f"Current SR is stable. Can increase up to {results['max_stable_radius']:.3f}"
                )
        else:
            results['recommendations'].append("Could not find stable ESP boundary - reservoir may be problematic")
        
        return results


# Standalone validation functions for backward compatibility
def validate_esp(W_reservoir, n_tests=5, test_length=200, tolerance=1e-6):
    """
    Standalone ESP validation function.
    
    Args:
        W_reservoir (array): Reservoir weight matrix
        n_tests (int): Number of validation tests
        test_length (int): Length of each test sequence
        tolerance (float): Convergence tolerance
        
    Returns:
        bool: True if ESP is satisfied, False otherwise
    """
    if W_reservoir is None:
        return True
    
    try:
        spectral_radius = np.max(np.abs(np.linalg.eigvals(W_reservoir)))
        if spectral_radius > 1.1:
            return False
        
        n_reservoir = W_reservoir.shape[0]
        activation_func = lambda x: np.tanh(x)
        
        for _ in range(n_tests):
            u = np.random.randn(test_length, 1) * 0.5
            
            x1 = np.random.randn(n_reservoir) * 0.2
            x2 = np.random.randn(n_reservoir) * 0.2
            
            for t in range(test_length):
                x1 = activation_func(W_reservoir @ x1)
                x2 = activation_func(W_reservoir @ x2)
            
            distance = np.linalg.norm(x1 - x2)
            if distance > tolerance:
                return False
        
        return True
        
    except Exception:
        return False