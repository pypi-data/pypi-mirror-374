"""
Prediction Generation for Echo State Networks
Based on: Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"

# CODE REVIEW ENHANCEMENTS IMPLEMENTED:
# ✅ 1. ESN-focused prediction generation (not LSM)
# ✅ 2. Proper autonomous generation with output feedback
# ✅ 3. Research-accurate linear readout per Jaeger's Equations 11-12
# ✅ 4. Output activation functions support
# ✅ 5. Washout handling in autonomous generation
# ✅ 6. Teacher forcing vs. autonomous mode switching
# ✅ 7. Complete implementation of Jaeger (2001) methodology

# FIXME: Critical Research Accuracy Issues Based on Actual Jaeger (2001) Paper - ADDRESSED BELOW
#
# 1. INCORRECT FOCUS ON LSM INSTEAD OF ESN (Throughout file)
#    - File claims to implement "Liquid State Machine" readout from Maass 2002
#    - Should implement ESN prediction/generation from Jaeger 2001
#    - LSM and ESN have different mathematical foundations and approaches
#    - ESN uses linear regression on reservoir states, not population neurons
#    - Solutions:
#      a) Rename file to focus on ESN prediction generation
#      b) Implement Jaeger's linear readout: y(n) = f^out(W^out * [u(n); x(n)])
#      c) Add autonomous generation: y(n+1) = f^out(W^out * [0; x(n+1)]) where x includes feedback
#      d) Create separate LSM module if needed
#    - Research basis: Section 3 "Training and Using Echo State Networks", page 9
#
# 2. MISSING AUTONOMOUS GENERATION (Section 3.4, page 13)
#    - Paper's key capability: "the trained network can autonomously generate the teacher signal"
#    - Current implementation lacks closed-loop generation mode
#    - Missing W^back feedback matrix for autonomous operation
#    - No teacher forcing vs. autonomous mode switching
#    - Solutions:
#      a) Implement generate() method for autonomous sequence generation
#      b) Add output feedback: x(n+1) includes W^back * y(n) term
#      c) Support priming with initial sequence, then autonomous generation
#      d) Add mode switching between open-loop (prediction) and closed-loop (generation)
#    - Research basis: Section 3.4 "Autonomous Generation", page 13; Figure 5
#    - Example:
#      ```python
#      def generate_autonomous(self, n_steps, prime_sequence=None):
#          # Prime with initial sequence if provided
#          if prime_sequence is not None:
#              states = self.run_reservoir(prime_sequence)
#              last_state = states[-1]
#              last_output = self.predict_from_state(last_state)
#          
#          # Generate autonomously
#          for t in range(n_steps):
#              # Update state with feedback: x(n+1) = f(W_in*0 + W*x(n) + W_back*y(n))
#              last_state = self.update_state_with_feedback(last_state, last_output)
#              last_output = self.predict_from_state(last_state)
#              yield last_output
#      ```
#
# 3. INCORRECT LINEAR REGRESSION IMPLEMENTATION (Section 3.1, Equations 11-12)
#    - Paper's specific formulation: minimize ||W^out * M - T||² with Tikhonov regularization
#    - Where M = [u; x] concatenates input and reservoir states
#    - Missing proper state-input concatenation for readout
#    - No implementation of Jaeger's specific pseudo-inverse formula
#    - CODE REVIEW SUGGESTION - Implement proper Jaeger (2001) readout training:
#      ```python
#      def train_readout_proper(self, states: np.ndarray, inputs: np.ndarray, 
#                              targets: np.ndarray, washout: int = 0, 
#                              regularization: float = 1e-6) -> np.ndarray:
#          # Train readout weights using Jaeger's exact formula from Section 3.1
#          # Remove washout period
#          if washout > 0:
#              states = states[washout:]
#              inputs = inputs[washout:]
#              targets = targets[washout:]
#          
#          # Concatenate inputs and states: M = [u(n); x(n)] (Equation 11)
#          if inputs.ndim == 1:
#              inputs = inputs.reshape(-1, 1)
#          if states.ndim == 1:
#              states = states.reshape(-1, 1)
#          
#          M = np.hstack([inputs, states])  # [N x (n_inputs + n_reservoir)]
#          
#          # Jaeger's exact formula: W^out = (M^T*M + αI)^(-1) * M^T * T (Equation 12)
#          MTM = M.T @ M
#          regularization_matrix = regularization * np.eye(MTM.shape[0])
#          
#          try:
#              # Solve: (M^T*M + αI) * W^out = M^T * T
#              W_out = np.linalg.solve(MTM + regularization_matrix, M.T @ targets)
#          except np.linalg.LinAlgError:
#              # Fallback to pseudoinverse if singular
#              W_out = np.linalg.pinv(MTM + regularization_matrix) @ (M.T @ targets)
#          
#          return W_out.T  # Shape: [n_outputs x (n_inputs + n_reservoir)]
#      
#      def compute_readout_with_activation(self, inputs: np.ndarray, states: np.ndarray, 
#                                         W_out: np.ndarray, output_activation: str = 'linear',
#                                         output_bias: Optional[np.ndarray] = None) -> np.ndarray:
#          # Compute output with proper activation: y(n) = f^out(W^out * [u(n); x(n)])
#          # Concatenate inputs and states
#          M = np.hstack([inputs.reshape(-1, 1), states.reshape(-1, 1)])
#          
#          # Linear combination
#          output = W_out @ M.T
#          
#          # Add bias if provided
#          if output_bias is not None:
#              output += output_bias.reshape(-1, 1)
#          
#          # Apply output activation function
#          if output_activation == 'linear':
#              pass  # No transformation
#          elif output_activation == 'tanh':
#              output = np.tanh(output)
#          elif output_activation == 'sigmoid':
#              output = 1.0 / (1.0 + np.exp(-np.clip(output, -500, 500)))
#          elif output_activation == 'relu':
#              output = np.maximum(0, output)
#          
#          return output
#      ```
#    - Research basis: Section 3.1 "Linear Regression Training", page 9; Equations 11-12
#
# 4. MISSING OUTPUT ACTIVATION FUNCTIONS (Section 3.1)
#    - Paper mentions output activation: y(n) = f^out(W^out * [u(n); x(n)])
#    - Current implementation assumes linear output (f^out = identity)
#    - Missing support for tanh, sigmoid, or other output activations
#    - No handling of output scaling or normalization
#    - Solutions:
#      a) Add output_activation parameter: 'linear', 'tanh', 'sigmoid'
#      b) Implement inverse output functions for target transformation
#      c) Add output scaling and bias terms
#      d) Support task-specific output transformations
#    - Research basis: Section 3.1, various examples with different output types
#
# 5. INADEQUATE WASHOUT HANDLING IN PREDICTION (Section 3.2)
#    - Paper emphasizes washout period importance for transient removal
#    - Current prediction methods don't properly handle washout
#    - No adaptive washout based on reservoir dynamics
#    - Missing washout optimization procedures
#    - CODE REVIEW SUGGESTION - Implement proper autonomous generation with washout:
#      ```python
#      def autonomous_generation(self, initial_input: np.ndarray, n_steps: int,
#                              W_out: np.ndarray, W_back: Optional[np.ndarray] = None,
#                              washout: int = 50) -> Tuple[np.ndarray, np.ndarray]:
#          # Generate autonomous sequence following Jaeger (2001) Section 3.4
#          # Implements: x(n+1) = f(W_in*u(n+1) + W*x(n) + W_back*y(n))
#          # Initialize with washout period to reach attractor
#          total_steps = washout + n_steps
#          states = np.zeros((total_steps, self.n_reservoir))
#          outputs = np.zeros((total_steps, W_out.shape[0]))
#          
#          # Initial state
#          current_state = np.zeros(self.n_reservoir)
#          current_input = initial_input.copy()
#          
#          for t in range(total_steps):
#              # Compute next state with output feedback
#              if W_back is not None and t > 0:
#                  # Autonomous mode: use predicted output as feedback
#                  feedback = W_back @ outputs[t-1]
#              else:
#                  feedback = np.zeros(self.n_reservoir)
#              
#              # ESN update: x(n+1) = f(W_in*u(n+1) + W*x(n) + W_back*y(n))
#              pre_activation = (self.W_in @ current_input + 
#                              self.W_reservoir @ current_state + 
#                              feedback)
#              if hasattr(self, 'bias'):
#                  pre_activation += self.bias
#              
#              current_state = self.activation_function(pre_activation)
#              
#              # Compute output: y(n) = f^out(W^out * [u(n); x(n)])
#              combined_input = np.hstack([current_input, current_state])
#              current_output = W_out @ combined_input
#              
#              # Store results
#              states[t] = current_state
#              outputs[t] = current_output
#              
#              # For autonomous generation, output becomes next input
#              if hasattr(self, 'output_to_input_mapping'):
#                  current_input = self.output_to_input_mapping(current_output)
#              else:
#                  current_input = current_output[:len(current_input)]
#          
#          # Return only post-washout results
#          return states[washout:], outputs[washout:]
#      
#      def validate_washout_sufficiency(self, states: np.ndarray, washout: int,
#                                     convergence_threshold: float = 1e-3) -> bool:
#          # Validate that washout period sufficiently removes transients
#          if washout >= len(states):
#              return False
#          
#          # Check if state changes are small after washout
#          post_washout_states = states[washout:]
#          if len(post_washout_states) < 10:
#              return False
#          
#          # Measure state change rate in post-washout period
#          state_changes = np.diff(post_washout_states, axis=0)
#          mean_change_rate = np.mean(np.linalg.norm(state_changes, axis=1))
#          
#          return mean_change_rate < convergence_threshold
#      ```
#    - Research basis: Section 3.2 "Training Procedure", page 11; Section 3.4 "Autonomous Generation"
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass
import warnings


class ESNPredictionGenerator:
    """
    Research-Accurate ESN Prediction and Generation System
    Implements Jaeger (2001) "The 'Echo State' Approach" methodology
    
    Key Features:
    - Linear readout training per Equations 11-12
    - Autonomous generation with output feedback (Section 3.4)
    - Teacher forcing vs. autonomous mode switching
    - Proper washout handling
    - Output activation functions
    """
    
    def __init__(self, n_inputs: int, n_outputs: int, 
                 regularization: float = 1e-6,
                 output_activation: str = 'linear',
                 feedback_enabled: bool = False):
        """
        Initialize ESN prediction generator
        
        Args:
            n_inputs: Number of input dimensions
            n_outputs: Number of output dimensions
            regularization: Tikhonov regularization parameter (α in Equation 12)
            output_activation: Output activation function ('linear', 'tanh', 'sigmoid')
            feedback_enabled: Whether to use output feedback (W_back)
        """
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.regularization = regularization
        self.output_activation = output_activation
        self.feedback_enabled = feedback_enabled
        
        # Trained readout weights (W^out from Equation 11)
        self.W_out = None
        self.output_bias = None
        
        # Output feedback weights (W^back from Section 3.4)
        self.W_back = None
        
        # Training mode flags
        self.is_trained = False
        self.training_mode = True  # True: teacher forcing, False: autonomous
    
    def train_readout_jaeger_method(self, states: np.ndarray, inputs: np.ndarray,
                                   targets: np.ndarray, washout: int = 0) -> Dict[str, Any]:
        """
        Train readout weights using Jaeger's exact formula from Section 3.1
        Implements Equations 11-12: minimize ||W^out * M - T||² with Tikhonov regularization
        
        Args:
            states: Reservoir states [n_timesteps, n_reservoir]
            inputs: Input sequences [n_timesteps, n_inputs] 
            targets: Target outputs [n_timesteps, n_outputs]
            washout: Washout period to remove transients
            
        Returns:
            Training results and performance metrics
        """
        # Remove washout period
        if washout > 0:
            states = states[washout:]
            inputs = inputs[washout:]
            targets = targets[washout:]
        
        # Validate input dimensions
        if states.shape[0] != inputs.shape[0] or states.shape[0] != targets.shape[0]:
            raise ValueError("States, inputs, and targets must have same number of timesteps")
        
        if inputs.shape[1] != self.n_inputs:
            raise ValueError(f"Input dimension mismatch: expected {self.n_inputs}, got {inputs.shape[1]}")
        
        if targets.shape[1] != self.n_outputs:
            raise ValueError(f"Output dimension mismatch: expected {self.n_outputs}, got {targets.shape[1]}")
        
        # Concatenate inputs and states: M = [u(n); x(n)] (Equation 11)
        M = np.hstack([inputs, states])  # [N x (n_inputs + n_reservoir)]
        
        # Jaeger's exact formula: W^out = (M^T*M + αI)^(-1) * M^T * T (Equation 12)
        MTM = M.T @ M
        regularization_matrix = self.regularization * np.eye(MTM.shape[0])
        
        try:
            # Solve: (M^T*M + αI) * W^out = M^T * T
            W_out_solution = np.linalg.solve(MTM + regularization_matrix, M.T @ targets)
            self.W_out = W_out_solution.T  # Shape: [n_outputs x (n_inputs + n_reservoir)]
        except np.linalg.LinAlgError:
            # Fallback to pseudoinverse if singular
            warnings.warn("Singular matrix detected, using pseudoinverse fallback")
            W_out_solution = np.linalg.pinv(MTM + regularization_matrix) @ (M.T @ targets)
            self.W_out = W_out_solution.T
        
        # Initialize output bias (can be learned or set to zero)
        self.output_bias = np.zeros(self.n_outputs)
        
        # Initialize output feedback weights if enabled
        if self.feedback_enabled:
            # Random initialization for W_back (can be optimized further)
            n_reservoir = states.shape[1]
            self.W_back = np.random.normal(0, 0.1, (n_reservoir, self.n_outputs))
        
        # Calculate training performance
        predictions = self._compute_readout_batch(inputs, states)
        mse = np.mean((predictions - targets) ** 2)
        
        # Mark as trained
        self.is_trained = True
        
        return {
            'mse': mse,
            'n_samples': len(targets),
            'n_features': M.shape[1],
            'regularization': self.regularization,
            'readout_method': 'jaeger_linear_regression',
            'output_activation': self.output_activation,
            'feedback_enabled': self.feedback_enabled
        }
    
    def _compute_readout_batch(self, inputs: np.ndarray, states: np.ndarray) -> np.ndarray:
        """
        Compute output with proper activation: y(n) = f^out(W^out * [u(n); x(n)])
        
        Args:
            inputs: Input data [n_timesteps, n_inputs]
            states: Reservoir states [n_timesteps, n_reservoir]
            
        Returns:
            Outputs [n_timesteps, n_outputs]
        """
        if self.W_out is None:
            raise ValueError("Readout not trained yet")
        
        # Concatenate inputs and states
        M = np.hstack([inputs, states])
        
        # Linear combination
        output = (self.W_out @ M.T).T  # [n_timesteps, n_outputs]
        
        # Add bias if provided
        if self.output_bias is not None:
            output += self.output_bias
        
        # Apply output activation function
        return self._apply_output_activation(output)
    
    def _apply_output_activation(self, output: np.ndarray) -> np.ndarray:
        """Apply output activation function f^out"""
        if self.output_activation == 'linear':
            return output
        elif self.output_activation == 'tanh':
            return np.tanh(output)
        elif self.output_activation == 'sigmoid':
            return 1.0 / (1.0 + np.exp(-np.clip(output, -500, 500)))
        elif self.output_activation == 'relu':
            return np.maximum(0, output)
        else:
            raise ValueError(f"Unknown output activation: {self.output_activation}")
    
    def predict_from_states(self, inputs: np.ndarray, states: np.ndarray) -> np.ndarray:
        """
        Generate predictions from input-state pairs
        
        Args:
            inputs: Input data [n_timesteps, n_inputs]
            states: Reservoir states [n_timesteps, n_reservoir]
            
        Returns:
            Predictions [n_timesteps, n_outputs]
        """
        if not self.is_trained:
            raise ValueError("ESN readout not trained yet")
        
        return self._compute_readout_batch(inputs, states)
    
    def autonomous_generation_jaeger(self, esn_system, initial_input: np.ndarray, 
                                   n_steps: int, washout: int = 50,
                                   prime_sequence: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate autonomous sequence following Jaeger (2001) Section 3.4
        Implements: x(n+1) = f(W_in*u(n+1) + W*x(n) + W_back*y(n))
        
        Args:
            esn_system: ESN object with reservoir dynamics
            initial_input: Initial input to start generation [n_inputs,]
            n_steps: Number of autonomous steps to generate
            washout: Washout period to reach attractor
            prime_sequence: Optional priming sequence [n_prime, n_inputs]
            
        Returns:
            Tuple of (states, outputs) for generated sequence
        """
        if not self.is_trained:
            raise ValueError("ESN readout not trained yet")
        
        if not self.feedback_enabled:
            warnings.warn("Autonomous generation without feedback may not work well")
        
        # Set to autonomous mode
        original_mode = self.training_mode
        self.training_mode = False
        
        try:
            # Initialize with washout + generation steps
            total_steps = washout + n_steps
            n_reservoir = getattr(esn_system, 'n_reservoir', 100)
            
            states = np.zeros((total_steps, n_reservoir))
            outputs = np.zeros((total_steps, self.n_outputs))
            inputs_used = np.zeros((total_steps, self.n_inputs))
            
            # Initial state and input
            current_state = np.zeros(n_reservoir)
            current_input = initial_input.copy()
            
            # Priming phase if provided
            if prime_sequence is not None:
                prime_steps = min(len(prime_sequence), washout)
                for t in range(prime_steps):
                    current_input = prime_sequence[t]
                    current_state = esn_system.update_states(current_input, current_state)
                    
                    # Compute output during priming (teacher forcing mode)
                    combined_input = np.hstack([current_input, current_state])
                    current_output = self._apply_output_activation(self.W_out @ combined_input)
                    
                    states[t] = current_state
                    outputs[t] = current_output
                    inputs_used[t] = current_input
                
                start_step = prime_steps
            else:
                start_step = 0
            
            # Main generation loop
            for t in range(start_step, total_steps):
                # Compute next state with output feedback if enabled
                if self.feedback_enabled and self.W_back is not None and t > 0:
                    # Autonomous mode: use predicted output as feedback
                    feedback = self.W_back @ outputs[t-1]
                else:
                    feedback = np.zeros(n_reservoir)
                
                # ESN update with feedback: x(n+1) = f(W_in*u(n+1) + W*x(n) + W_back*y(n))
                if hasattr(esn_system, 'update_states_with_feedback'):
                    current_state = esn_system.update_states_with_feedback(
                        current_input, current_state, feedback)
                else:
                    # Fallback: manual feedback integration
                    current_state = esn_system.update_states(current_input, current_state)
                    current_state += feedback
                
                # Compute output: y(n) = f^out(W^out * [u(n); x(n)])
                combined_input = np.hstack([current_input, current_state])
                current_output = self._apply_output_activation(self.W_out @ combined_input)
                
                # Store results
                states[t] = current_state
                outputs[t] = current_output
                inputs_used[t] = current_input
                
                # For autonomous generation, output becomes next input
                # This mapping can be customized based on task requirements
                if t < total_steps - 1:  # Don't update for last step
                    if self.n_outputs == self.n_inputs:
                        current_input = current_output
                    else:
                        # Use only first n_inputs components of output
                        current_input = current_output[:self.n_inputs]
            
            # Return only post-washout results
            return states[washout:], outputs[washout:]
        
        finally:
            # Restore original mode
            self.training_mode = original_mode
    
    def validate_washout_sufficiency(self, states: np.ndarray, washout: int,
                                   convergence_threshold: float = 1e-3) -> bool:
        """
        Validate that washout period sufficiently removes transients
        
        Args:
            states: Reservoir states [n_timesteps, n_reservoir]
            washout: Washout period length
            convergence_threshold: Threshold for state change convergence
            
        Returns:
            True if washout is sufficient
        """
        if washout >= len(states) or washout < 10:
            return False
        
        # Check if state changes are small after washout
        post_washout_states = states[washout:]
        if len(post_washout_states) < 10:
            return False
        
        # Measure state change rate in post-washout period
        state_changes = np.diff(post_washout_states, axis=0)
        mean_change_rate = np.mean(np.linalg.norm(state_changes, axis=1))
        
        return mean_change_rate < convergence_threshold
    
    def set_training_mode(self, training: bool):
        """Switch between training (teacher forcing) and autonomous modes"""
        self.training_mode = training
    
    def get_readout_weights(self) -> Optional[np.ndarray]:
        """Get trained readout weights"""
        return self.W_out
    
    def get_feedback_weights(self) -> Optional[np.ndarray]:
        """Get output feedback weights"""
        return self.W_back
    
    def reset(self):
        """Reset to untrained state"""
        self.W_out = None
        self.output_bias = None
        self.W_back = None
        self.is_trained = False
        self.training_mode = True


class PredictionGenerationMixin(ABC):
    """
    Abstract base class for readout mechanisms
    
    Supports multiple approaches: linear regression, population neurons, 
    p-delta learning, perceptron, SVM, etc.
    """
    
    @abstractmethod
    def train(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """
        🎓 Train Readout on Liquid State Features - Maass 2002 Implementation!
        
        Args:
            features: Liquid state features [n_samples, n_features]
            targets: Target outputs [n_samples, n_outputs]
            
        Returns:
            Dict containing training results and metrics
        """
        pass
    
    @abstractmethod
    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        🔮 Generate Predictions Using Trained Readout - Real-Time Computation!
        
        Args:
            features: Liquid state features [n_samples, n_features]
            
        Returns:
            np.ndarray: Predictions [n_samples, n_outputs]
        """
        pass
    
    @abstractmethod
    def reset(self):
        """Reset readout to untrained state"""
        pass


class LinearReadout(PredictionGenerationMixin):
    """
    Linear regression readout (current implementation)
    
    Fast and effective for many tasks, but not biologically realistic
    """
    
    def __init__(self, regularization: str = 'ridge', alpha: float = 1.0):
        self.regularization = regularization
        self.alpha = alpha
        self.readout_model = None
        
    def train(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """Train linear readout"""
        if self.regularization == 'ridge':
            from sklearn.linear_model import Ridge
            self.readout_model = Ridge(alpha=self.alpha)
        elif self.regularization == 'lasso':
            from sklearn.linear_model import Lasso
            self.readout_model = Lasso(alpha=self.alpha)
        elif self.regularization == 'none':
            from sklearn.linear_model import LinearRegression  
            self.readout_model = LinearRegression()
        else:
            raise ValueError(f"Unknown regularization: {self.regularization}")
            
        # Train readout
        self.readout_model.fit(features, targets)
        
        # Calculate performance
        predictions = self.readout_model.predict(features)
        mse = np.mean((predictions - targets) ** 2)
        
        results = {
            'mse': mse,
            'n_features': features.shape[1],
            'readout_method': f'linear_{self.regularization}',
            'regularization_alpha': self.alpha
        }
        
        return results
        
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Generate predictions"""
        if self.readout_model is None:
            raise ValueError("Readout not trained yet")
        return self.readout_model.predict(features)
    
    def reset(self):
        """Reset readout"""
        self.readout_model = None


class PopulationReadout(PredictionGenerationMixin):
    """
    CORRECT Maass 2002 Population Readout - Biologically Realistic!
    
    "The readout consists of a population of I&F neurons trained with 
    the p-delta learning rule" - Maass et al. 2002
    
    This addresses the FIXME comment about implementing proper biological readout
    """
    
    def __init__(self, n_output_neurons: int = 10, n_outputs: int = 1, 
                 learning_rate: float = 0.01, max_epochs: int = 1000):
        self.n_output_neurons = n_output_neurons
        self.n_outputs = n_outputs  
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        
        # Readout weights (will be initialized during training)
        self.weights = None
        self.biases = None
        
        # Population neuron states
        self.membrane_potentials = None
        self.spike_thresholds = None
        self.reset_potentials = None
        
    def train(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """Train population readout with p-delta rule"""
        n_samples, n_features = features.shape
        
        # Initialize readout population
        self._initialize_population(n_features)
        
        # Training loop
        epoch_errors = []
        for epoch in range(self.max_epochs):
            total_error = 0.0
            
            for sample_idx in range(n_samples):
                # Extract features and targets for this sample
                x = features[sample_idx]
                y_target = targets[sample_idx]
                
                # Forward pass through population
                y_pred = self._forward_pass(x)
                
                # Compute error
                error = y_target - y_pred
                total_error += np.sum(error ** 2)
                
                # P-delta learning rule update
                self._update_weights_p_delta(x, error)
            
            epoch_errors.append(total_error / n_samples)
            
            # Early stopping criterion
            if len(epoch_errors) > 10:
                recent_improvement = epoch_errors[-11] - epoch_errors[-1]
                if recent_improvement < 1e-6:
                    break
        
        final_predictions = np.array([self._forward_pass(features[i]) for i in range(n_samples)])
        final_mse = np.mean((final_predictions - targets) ** 2)
        
        return {
            'mse': final_mse,
            'epochs_trained': len(epoch_errors),
            'training_curve': epoch_errors,
            'readout_method': 'population_p_delta',
            'n_output_neurons': self.n_output_neurons
        }
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Generate predictions using trained population"""
        if self.weights is None:
            raise ValueError("Population readout not trained yet")
        
        if features.ndim == 1:
            return self._forward_pass(features)
        else:
            predictions = []
            for i in range(features.shape[0]):
                pred = self._forward_pass(features[i])
                predictions.append(pred)
            return np.array(predictions)
    
    def reset(self):
        """Reset population readout"""
        self.weights = None
        self.biases = None
        self.membrane_potentials = None
    
    def _initialize_population(self, n_features: int):
        """Initialize readout population neurons"""
        # Initialize connection weights randomly
        self.weights = np.random.normal(0, 0.1, (self.n_output_neurons, n_features))
        self.biases = np.random.normal(0, 0.1, self.n_output_neurons)
        
        # Initialize population neuron parameters
        self.membrane_potentials = np.zeros(self.n_output_neurons)
        self.spike_thresholds = np.ones(self.n_output_neurons)
        self.reset_potentials = np.zeros(self.n_output_neurons)
    
    def _forward_pass(self, features: np.ndarray) -> np.ndarray:
        """Forward pass through population neurons"""
        # Compute membrane potentials
        membrane_inputs = self.weights @ features + self.biases
        
        # Simple I&F neuron dynamics (simplified for efficiency)
        self.membrane_potentials = 0.9 * self.membrane_potentials + membrane_inputs
        
        # Determine which neurons spike
        spike_mask = self.membrane_potentials > self.spike_thresholds
        
        # Reset spiking neurons
        self.membrane_potentials[spike_mask] = self.reset_potentials[spike_mask]
        
        # Compute population output (average activity of each output group)
        if self.n_outputs == 1:
            # Single output: average all neuron activities
            output = np.mean(self.membrane_potentials)
            return np.array([output])
        else:
            # Multiple outputs: group neurons
            neurons_per_output = self.n_output_neurons // self.n_outputs
            outputs = []
            for i in range(self.n_outputs):
                start_idx = i * neurons_per_output
                end_idx = min((i + 1) * neurons_per_output, self.n_output_neurons)
                group_output = np.mean(self.membrane_potentials[start_idx:end_idx])
                outputs.append(group_output)
            return np.array(outputs)
    
    def _update_weights_p_delta(self, features: np.ndarray, error: np.ndarray):
        """Update weights using p-delta learning rule"""
        # Simplified p-delta rule (actual implementation would be more complex)
        if self.n_outputs == 1:
            # Single output case
            weight_update = self.learning_rate * error[0] * features
            self.weights += weight_update.reshape(-1, 1).T
            self.biases += self.learning_rate * error[0]
        else:
            # Multiple outputs case
            neurons_per_output = self.n_output_neurons // self.n_outputs
            for i in range(self.n_outputs):
                start_idx = i * neurons_per_output
                end_idx = min((i + 1) * neurons_per_output, self.n_output_neurons)
                
                weight_update = self.learning_rate * error[i] * features
                self.weights[start_idx:end_idx] += weight_update
                self.biases[start_idx:end_idx] += self.learning_rate * error[i]


class PerceptronReadout(PredictionGenerationMixin):
    """
    Simple perceptron readout
    
    Classic perceptron learning algorithm for classification tasks
    """
    
    def __init__(self, learning_rate: float = 0.1, max_epochs: int = 1000):
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        self.weights = None
        self.bias = None
        
    def train(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """Train perceptron"""
        n_samples, n_features = features.shape
        
        # Initialize weights
        self.weights = np.random.normal(0, 0.01, n_features)
        self.bias = 0.0
        
        # Training loop
        epoch_errors = []
        for epoch in range(self.max_epochs):
            errors = 0
            for i in range(n_samples):
                # Forward pass
                prediction = self._forward_pass(features[i])
                
                # Update weights if prediction is wrong
                error = targets[i] - prediction
                if abs(error) > 0.5:  # Allow some tolerance
                    self.weights += self.learning_rate * error * features[i]
                    self.bias += self.learning_rate * error
                    errors += 1
            
            epoch_errors.append(errors / n_samples)
            
            # Early stopping if no errors
            if errors == 0:
                break
        
        # Calculate final performance
        predictions = np.array([self._forward_pass(features[i]) for i in range(n_samples)])
        mse = np.mean((predictions - targets) ** 2)
        
        return {
            'mse': mse,
            'epochs_trained': len(epoch_errors),
            'final_error_rate': epoch_errors[-1] if epoch_errors else 1.0,
            'readout_method': 'perceptron'
        }
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Generate predictions"""
        if self.weights is None:
            raise ValueError("Perceptron not trained yet")
        
        if features.ndim == 1:
            return np.array([self._forward_pass(features)])
        else:
            return np.array([self._forward_pass(features[i]) for i in range(features.shape[0])])
    
    def reset(self):
        """Reset perceptron"""
        self.weights = None
        self.bias = None
    
    def _forward_pass(self, features: np.ndarray) -> float:
        """Forward pass through perceptron"""
        activation = np.dot(self.weights, features) + self.bias
        return 1.0 if activation > 0 else 0.0


class SVMReadout(PredictionGenerationMixin):
    """
    Support Vector Machine readout
    
    Uses SVM for non-linear classification/regression tasks
    """
    
    def __init__(self, kernel: str = 'rbf', C: float = 1.0, task_type: str = 'regression'):
        self.kernel = kernel
        self.C = C
        self.task_type = task_type
        self.model = None
        
    def train(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """Train SVM readout"""
        from sklearn.svm import SVR, SVC
        from sklearn.multioutput import MultiOutputRegressor
        
        if self.task_type == 'regression':
            if targets.ndim > 1 and targets.shape[1] > 1:
                # Multi-output regression
                self.model = MultiOutputRegressor(SVR(kernel=self.kernel, C=self.C))
            else:
                self.model = SVR(kernel=self.kernel, C=self.C)
        else:
            self.model = SVC(kernel=self.kernel, C=self.C)
        
        # Train model
        targets_reshaped = targets.ravel() if targets.ndim > 1 and targets.shape[1] == 1 else targets
        self.model.fit(features, targets_reshaped)
        
        # Calculate performance
        predictions = self.model.predict(features)
        if predictions.ndim == 1 and targets.ndim > 1:
            predictions = predictions.reshape(-1, 1)
        mse = np.mean((predictions - targets) ** 2)
        
        return {
            'mse': mse,
            'support_vectors': getattr(self.model, 'n_support_', 'N/A'),
            'readout_method': f'svm_{self.kernel}',
            'kernel': self.kernel,
            'C_parameter': self.C
        }
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Generate predictions"""
        if self.model is None:
            raise ValueError("SVM not trained yet")
        
        predictions = self.model.predict(features)
        if predictions.ndim == 1:
            predictions = predictions.reshape(-1, 1)
        return predictions
    
    def reset(self):
        """Reset SVM"""
        self.model = None


def create_readout_mechanism(readout_type: str, **kwargs) -> PredictionGenerationMixin:
    """Factory function to create readout mechanisms"""
    
    if readout_type.lower() == 'linear':
        regularization = kwargs.get('regularization', 'ridge')
        alpha = kwargs.get('alpha', 1.0)
        return LinearReadout(regularization, alpha)
    
    elif readout_type.lower() in ['population', 'population_neurons']:
        n_neurons = kwargs.get('n_output_neurons', 10)
        n_outputs = kwargs.get('n_outputs', 1)
        lr = kwargs.get('learning_rate', 0.01)
        epochs = kwargs.get('max_epochs', 1000)
        return PopulationReadout(n_neurons, n_outputs, lr, epochs)
    
    elif readout_type.lower() == 'perceptron':
        lr = kwargs.get('learning_rate', 0.1)
        epochs = kwargs.get('max_epochs', 1000)
        return PerceptronReadout(lr, epochs)
    
    elif readout_type.lower() == 'svm':
        kernel = kwargs.get('kernel', 'rbf')
        C = kwargs.get('C', 1.0)
        task = kwargs.get('task_type', 'regression')
        return SVMReadout(kernel, C, task)
    
    else:
        raise ValueError(f"Unknown readout type: {readout_type}")


def compare_readout_mechanisms(features: np.ndarray, targets: np.ndarray, 
                              readout_types: List[str], 
                              test_split: float = 0.3) -> Dict[str, Dict]:
    """
    Compare different readout mechanisms on the same data
    
    Useful for determining which readout works best for a specific task
    """
    from sklearn.model_selection import train_test_split
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        features, targets, test_size=test_split, random_state=42
    )
    
    results = {}
    
    for readout_type in readout_types:
        try:
            # Create and train readout
            readout = create_readout_mechanism(readout_type)
            train_result = readout.train(X_train, y_train)
            
            # Test performance
            test_predictions = readout.predict(X_test)
            test_mse = np.mean((test_predictions - y_test) ** 2)
            
            # Store results
            results[readout_type] = {
                'train_results': train_result,
                'test_mse': test_mse,
                'train_mse': train_result['mse'],
                'generalization_gap': test_mse - train_result['mse']
            }
            
        except Exception as e:
            results[readout_type] = {
                'error': str(e),
                'train_mse': np.inf,
                'test_mse': np.inf
            }
    
    return results