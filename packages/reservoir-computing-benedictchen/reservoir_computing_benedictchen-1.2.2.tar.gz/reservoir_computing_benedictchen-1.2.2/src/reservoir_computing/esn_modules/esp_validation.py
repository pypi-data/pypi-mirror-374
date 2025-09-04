"""
Echo State Property Validation for ESN
Implements ESP validation methods from Jaeger 2001 and extensions
"""

import numpy as np
from typing import Tuple, List, Dict, Any, Optional
import warnings


class EspValidationMixin:
    """Validates Echo State Property for reservoir networks"""
    
    def __init__(self, esn_instance):
        self.esn = esn_instance
    
    def validate_comprehensive_esp(self) -> Dict[str, Any]:
        """
        Comprehensive ESP validation using multiple methods
        
        #
        # 1. JAEGER DEFINITION 1 TEST: validate_jaeger_definition_1() - formal ESP validation
        # 2. STATE CONTRACTING PROPERTY: validate_state_contracting_property() - Definition 3.1
        # 3. PROPOSITION 3A SUFFICIENT: validate_proposition_3a_sufficient() - σmax < 1 test
        # 4. PROPOSITION 3B NECESSARY: validate_proposition_3b_necessary() - |λmax| < 1 test  
        # 5. LIPSCHITZ EMPIRICAL: validate_lipschitz_condition_empirical() - contraction mapping
        # 6. STATE FORGETTING: validate_state_forgetting_property() - Definition 3.2
        #
        # CONFIGURATION OPTIONS:
        # - User can choose validation_methods=['jaeger_def1', 'state_contracting', 'proposition_3a', etc.]
        # - Each method returns standardized result format with confidence scores
        # - Backward compatibility maintained with original methods
        """
        # Configuration: User can specify which validation methods to run
        validation_methods = getattr(self, 'validation_methods', 'all')
        results = {}
        
        # SOLUTION 1a: Jaeger (2001) Definition 1 - Formal ESP Test
        if validation_methods == 'all' or 'jaeger_def1' in validation_methods:
            results['jaeger_definition_1'] = self._validate_jaeger_definition_1()
        
        # SOLUTION 1b: Definition 3.1 - State Contracting Property  
        if validation_methods == 'all' or 'state_contracting' in validation_methods:
            results['state_contracting'] = self._validate_state_contracting_property()
        
        # SOLUTION 1c: Definition 3.2 - State Forgetting Property
        if validation_methods == 'all' or 'state_forgetting' in validation_methods:
            results['state_forgetting'] = self._validate_state_forgetting_property()
        
        # SOLUTION 2a: Proposition 3a - Sufficient Condition (σmax < 1)
        if validation_methods == 'all' or 'proposition_3a' in validation_methods:
            results['proposition_3a_sufficient'] = self._validate_proposition_3a_sufficient()
        
        # SOLUTION 2b: Proposition 3b - Necessary Condition (|λmax| < 1) 
        if validation_methods == 'all' or 'proposition_3b' in validation_methods:
            results['proposition_3b_necessary'] = self._validate_proposition_3b_necessary()
        
        # SOLUTION 4a: Empirical Lipschitz Condition Testing
        if validation_methods == 'all' or 'lipschitz_empirical' in validation_methods:
            results['lipschitz_empirical'] = self._validate_lipschitz_condition_empirical()
        
        # SOLUTION 3a: Null Sequence Test for State Contracting
        if validation_methods == 'all' or 'null_sequence' in validation_methods:
            results['null_sequence_test'] = self._validate_null_sequence_contracting()
        
        # SOLUTION 3b: Exponential Decay Test for State Influence
        if validation_methods == 'all' or 'exponential_decay' in validation_methods:
            results['exponential_decay_test'] = self._validate_exponential_decay()
        
        # SOLUTION 3c: Input History Truncation Test
        if validation_methods == 'all' or 'input_truncation' in validation_methods:
            results['input_truncation_test'] = self._validate_input_history_truncation()
        
        # Original methods for backward compatibility
        if validation_methods == 'all' or 'legacy' in validation_methods:
            results['spectral_radius_check'] = self._validate_spectral_radius()
            results['convergence_test'] = self._validate_convergence()
            try:
                results['lyapunov_test'] = self._validate_lyapunov()
            except Exception as e:
                results['lyapunov_test'] = {'valid': False, 'error': str(e)}
            try:
                results['jacobian_test'] = self._validate_jacobian()
            except Exception as e:
                results['jacobian_test'] = {'valid': False, 'error': str(e)}
        
        # Overall ESP status
        valid_tests = [r.get('valid', False) for r in results.values() if isinstance(r, dict)]
        overall_valid = np.mean(valid_tests) > 0.5
        results['overall_esp_valid'] = overall_valid
        results['valid'] = overall_valid  # Compatibility with test expectations
        results['validation_confidence'] = np.mean(valid_tests)
        
        # Compute overall ESP validity with weighted scoring
        method_weights = {
            'jaeger_definition_1': 0.25,  # Highest weight - formal definition
            'state_contracting': 0.20,   # High weight - core property
            'proposition_3a_sufficient': 0.15, # Medium weight - sufficient condition
            'proposition_3b_necessary': 0.15,  # Medium weight - necessary condition
            'lipschitz_empirical': 0.10,  # Medium weight - practical validation
            'state_forgetting': 0.15     # Medium weight - equivalent characterization
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for method, weight in method_weights.items():
            if method in results and results[method].get('valid', False):
                confidence = results[method].get('confidence', 0.5)
                weighted_score += weight * confidence
            total_weight += weight
        
        # Include legacy methods with lower weight if no new methods available
        if len(results) <= 3:  # Only legacy methods
            legacy_methods = ['spectral_radius_check', 'convergence_test', 'lyapunov_test', 'jacobian_test']
            for method in legacy_methods:
                if method in results and results[method].get('valid', False):
                    confidence = results[method].get('confidence', 0.5)
                    weighted_score += 0.05 * confidence  # Low weight for legacy
                    total_weight += 0.05
        
        final_confidence = weighted_score / total_weight if total_weight > 0 else 0.0
        
        results['overall_esp_valid'] = final_confidence > 0.6
        results['valid'] = final_confidence > 0.6  # Compatibility
        results['validation_confidence'] = final_confidence
        results['validation_summary'] = {
            'total_methods_run': len(results) - 3,  # Exclude summary entries
            'research_accurate_methods': sum(1 for k in results.keys() if k.startswith(('jaeger_', 'state_', 'proposition_', 'lipschitz_'))),
            'weighted_confidence_score': final_confidence,
            'esp_conclusion': 'VALID' if final_confidence > 0.7 else 'QUESTIONABLE' if final_confidence > 0.4 else 'INVALID'
        }
        
        return results
    
    def _validate_spectral_radius(self) -> Dict[str, Any]:
        """Basic spectral radius validation"""
        eigenvals = np.linalg.eigvals(self.esn.reservoir_weights)
        spectral_radius = np.max(np.abs(eigenvals))
        
        return {
            'valid': spectral_radius < 1.0,
            'spectral_radius': float(spectral_radius),
            'method': 'spectral_radius',
            'confidence': 0.8 if spectral_radius < 0.95 else 0.6
        }
    
    def _validate_convergence(self, n_tests: int = 10, test_length: int = 1500, 
                            tolerance: float = 1e-6) -> Dict[str, Any]:
        """Test ESP through state convergence from different initial conditions"""
        convergence_results = []
        
        for test in range(n_tests):
            # Create two different initial states
            state1 = np.random.randn(self.esn.reservoir_size) * 0.1
            state2 = np.random.randn(self.esn.reservoir_size) * 0.1
            
            # Generate test input sequence
            input_seq = np.random.randn(test_length, self.esn.n_inputs) * 0.5
            
            # Run both states through same input sequence
            states1 = self._run_test_sequence(state1, input_seq)
            states2 = self._run_test_sequence(state2, input_seq)
            
            # Check final convergence
            final_diff = np.linalg.norm(states1[-1] - states2[-1])
            convergence_results.append(final_diff < tolerance)
        
        convergence_rate = np.mean(convergence_results)
        
        return {
            'valid': convergence_rate > 0.8,
            'convergence_rate': float(convergence_rate),
            'method': 'state_convergence',
            'n_tests': n_tests,
            'confidence': min(convergence_rate, 0.95)
        }
    
    def _validate_lyapunov(self) -> Dict[str, Any]:
        """Validate ESP using Lyapunov exponent analysis"""
        n_steps = 1000
        initial_state = np.random.randn(self.esn.reservoir_size) * 0.1
        input_seq = np.random.randn(n_steps, self.esn.n_inputs) * 0.5
        
        # Compute Lyapunov exponent
        lyapunov_sum = 0.0
        current_state = initial_state.copy()
        
        for t in range(n_steps):
            # Compute Jacobian at current state
            jacobian = self._compute_jacobian_at_state(current_state, input_seq[t])
            
            # Update Lyapunov sum
            eigenvals = np.linalg.eigvals(jacobian)
            max_eigenval = np.max(np.real(eigenvals))
            lyapunov_sum += np.log(abs(max_eigenval)) if max_eigenval != 0 else -10
            
            # Update state
            current_state = self._update_state_for_validation(current_state, input_seq[t])
        
        lyapunov_exponent = lyapunov_sum / n_steps
        
        return {
            'valid': lyapunov_exponent < 0,
            'lyapunov_exponent': float(lyapunov_exponent),
            'method': 'lyapunov_exponent',
            'confidence': 0.9 if lyapunov_exponent < -0.1 else 0.7
        }
    
    def _validate_jacobian(self) -> Dict[str, Any]:
        """Validate ESP through Jacobian spectral radius analysis"""
        # Sample random states and inputs
        n_samples = 20
        jacobian_radii = []
        
        for _ in range(n_samples):
            state = np.random.randn(self.esn.reservoir_size) * 0.5
            input_vec = np.random.randn(self.esn.n_inputs) * 0.5
            
            jacobian = self._compute_jacobian_at_state(state, input_vec)
            eigenvals = np.linalg.eigvals(jacobian)
            spectral_radius = np.max(np.abs(eigenvals))
            jacobian_radii.append(spectral_radius)
        
        mean_radius = np.mean(jacobian_radii)
        std_radius = np.std(jacobian_radii)
        
        return {
            'valid': mean_radius < 1.0,
            'mean_jacobian_radius': float(mean_radius),
            'std_jacobian_radius': float(std_radius),
            'method': 'jacobian_analysis',
            'confidence': 0.85 if mean_radius < 0.9 else 0.6
        }
    
    def _compute_jacobian_at_state(self, state: np.ndarray, input_vec: np.ndarray) -> np.ndarray:
        """Compute Jacobian of state update at given state and input"""
        # For tanh activation: d/dx tanh(x) = 1 - tanh²(x)
        net_input = (self.esn.input_weights @ input_vec + 
                    self.esn.reservoir_weights @ state)
        
        if hasattr(self.esn, 'bias_vector') and self.esn.bias_vector is not None:
            net_input += self.esn.bias_vector
        
        # Derivative of tanh
        tanh_derivative = 1 - np.tanh(net_input)**2
        
        # Jacobian: J = (1-α)I + α * diag(tanh'(net)) * W_res
        alpha = getattr(self.esn, 'leak_rate', 1.0)
        identity = np.eye(self.esn.reservoir_size)
        
        jacobian = ((1 - alpha) * identity + 
                   alpha * np.diag(tanh_derivative) @ self.esn.reservoir_weights)
        
        return jacobian
    
    def _run_test_sequence(self, initial_state: np.ndarray, 
                          input_sequence: np.ndarray) -> List[np.ndarray]:
        """Run ESN through test sequence for validation"""
        states = [initial_state.copy()]
        current_state = initial_state.copy()
        
        for input_vec in input_sequence:
            current_state = self._update_state_for_validation(current_state, input_vec)
            states.append(current_state.copy())
        
        return states
    
    def _update_state_for_validation(self, state: np.ndarray, 
                                   input_vec: np.ndarray) -> np.ndarray:
        """Update state for validation (simplified version)"""
        # Ensure input dimensions
        if len(input_vec) != self.esn.n_inputs:
            input_vec = np.resize(input_vec, self.esn.n_inputs)
        
        # Basic state update
        net_input = (self.esn.input_weights @ input_vec + 
                    self.esn.reservoir_weights @ state)
        
        if hasattr(self.esn, 'bias_vector') and self.esn.bias_vector is not None:
            net_input += self.esn.bias_vector
        
        # Apply activation
        activated = np.tanh(net_input)
        
        # Apply leak rate
        alpha = getattr(self.esn, 'leak_rate', 1.0)
        new_state = (1 - alpha) * state + alpha * activated
        
        return new_state
    
    def validate_echo_state_property_fast(self, n_tests: int = 3, 
                                        test_length: int = 100,
                                        tolerance: float = 1e-4) -> Dict[str, Any]:
        """Fast ESP validation for real-time use"""
        # Quick spectral radius check
        spectral_check = self._validate_spectral_radius()
        if not spectral_check['valid']:
            return {
                'valid': False,
                'method': 'fast_spectral',
                'reason': 'spectral_radius_exceeded',
                **spectral_check
            }
        
        # Quick convergence test
        convergence_results = []
        for _ in range(n_tests):
            state1 = np.random.randn(self.esn.reservoir_size) * 0.1
            state2 = np.random.randn(self.esn.reservoir_size) * 0.1
            input_seq = np.random.randn(test_length, self.esn.n_inputs) * 0.5
            
            # Short test
            for input_vec in input_seq[-20:]:  # Only last 20 steps
                state1 = self._update_state_for_validation(state1, input_vec)
                state2 = self._update_state_for_validation(state2, input_vec)
            
            diff = np.linalg.norm(state1 - state2)
            convergence_results.append(diff < tolerance * 10)  # More lenient
        
        convergence_rate = np.mean(convergence_results)
        
        return {
            'valid': convergence_rate > 0.6,
            'convergence_rate': float(convergence_rate),
            'spectral_radius': spectral_check['spectral_radius'],
            'method': 'fast_validation',
            'confidence': min(convergence_rate * 0.8, 0.8)
        }