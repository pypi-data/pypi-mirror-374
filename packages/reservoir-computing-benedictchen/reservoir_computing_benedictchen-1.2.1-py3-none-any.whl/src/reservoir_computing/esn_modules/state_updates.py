"""
🔄 State Updates Mixin - ESN Reservoir Dynamics and State Management
===================================================================

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Optional, Callable


class StateUpdatesMixin:
    """Handles ESN state updates and reservoir dynamics"""
    
    def update_states(self, input_data: np.ndarray, 
                     current_states: Optional[np.ndarray] = None,
                     activation: Callable = np.tanh) -> np.ndarray:
        """
        Update reservoir states given input
        Implements Equation (1) from Jaeger 2001
        
        x(n+1) = f(W_in * u(n+1) + W * x(n) + W_bias)
        """
        
        if current_states is None:
            current_states = np.zeros(self.n_reservoir if hasattr(self, 'n_reservoir') else 100)
        
        # Standard ESN update equation
        if hasattr(self, 'W_in') and hasattr(self, 'W_reservoir'):
            pre_activation = (np.dot(self.W_in, input_data) + 
                            np.dot(self.W_reservoir, current_states))
            
            if hasattr(self, 'bias'):
                pre_activation += self.bias
                
            new_states = activation(pre_activation)
        else:
            # Fallback if weights not initialized
            new_states = current_states * 0.9 + np.random.randn(len(current_states)) * 0.1
        
        return new_states
    
    def run_reservoir(self, input_sequence: np.ndarray, 
                     initial_state: Optional[np.ndarray] = None,
                     washout: int = 0) -> np.ndarray:
        """Run reservoir for entire input sequence"""
        seq_length = input_sequence.shape[0]
        n_reservoir = self.n_reservoir if hasattr(self, 'n_reservoir') else 100
        
        if initial_state is None:
            initial_state = np.zeros(n_reservoir)
        
        # Collect all states
        states = np.zeros((seq_length, n_reservoir))
        current_state = initial_state.copy()
        
        for i in range(seq_length):
            current_state = self.update_states(input_sequence[i], current_state)
            states[i] = current_state
        
        # Return states after washout period
        return states[washout:]