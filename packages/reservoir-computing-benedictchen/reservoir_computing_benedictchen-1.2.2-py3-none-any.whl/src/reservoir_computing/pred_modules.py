"""
🔮 Modular Prediction Generation - Complete ESN Prediction Suite
==============================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides a unified interface to all prediction generation capabilities
for Echo State Networks, combining core prediction, autonomous generation,
teacher forcing, and output feedback mechanisms.

💰 Donations: Help support this research!
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to fully support continued research

Based on comprehensive prediction research from:
- Jaeger, H. (2001) "Echo state network" core methodology
- Jaeger, H. (2001) Section 3.1 "Linear Readout Training"  
- Jaeger, H. (2001) Section 3.4 "Autonomous Generation"
- Teacher forcing methodologies for RNN training
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, List, Union
import warnings
import logging

# Import modular prediction components
from .pred_modules import (
    EchoStatePredictionMixin,
    predict_from_states,
    compute_linear_readout,
    generate_autonomous_sequence,
    setup_autonomous_mode,
    prime_and_generate,
    train_with_teacher_forcing,
    setup_teacher_forcing_mode,
    compute_forcing_schedule,
    configure_output_feedback,
    update_state_with_feedback,
    OutputFeedbackMixin
)

# Configure logging
logger = logging.getLogger(__name__)


class CompletePredictionMixin(EchoStatePredictionMixin, OutputFeedbackMixin):
    """
    🔮 Complete Prediction Suite for Echo State Networks
    
    Combines all prediction capabilities including open-loop prediction,
    closed-loop autonomous generation, teacher forcing training, and
    output feedback mechanisms.
    """
    
    def train_complete(self, 
                      X_train: np.ndarray,
                      y_train: np.ndarray,
                      method: str = 'teacher_forcing',
                      **kwargs) -> Dict[str, Any]:
        """
        Complete training with prediction-focused methodology
        
        Args:
            X_train: Training inputs
            y_train: Training targets
            method: Training method ('teacher_forcing', 'standard', 'progressive')
            **kwargs: Additional training parameters
            
        Returns:
            Training results
        """
        print("🔮 Starting complete prediction-focused training...")
        print("="*60)
        
        # Setup for prediction
        if not hasattr(self, 'W_feedback'):
            print("📡 Initializing output feedback...")
            self.configure_output_feedback()
        
        # Train based on method
        if method == 'teacher_forcing':
            results = train_with_teacher_forcing(self, X_train, y_train, **kwargs)
        elif method == 'progressive':
            from .pred_modules.teacher_forcing import progressive_teacher_forcing
            results = progressive_teacher_forcing(self, X_train, y_train, **kwargs)
        elif method == 'standard':
            results = self._train_standard_prediction(X_train, y_train, **kwargs)
        else:
            raise ValueError(f"Unknown training method: {method}")
        
        # Setup autonomous mode after training
        setup_autonomous_mode(self)
        
        print(f"✅ Training completed using {method} method")
        print(f"📊 Final MSE: {results.get('train_mse', 'N/A'):.6f}")
        print("="*60)
        
        return results
    
    def predict_complete(self, 
                        X_input: np.ndarray,
                        mode: str = 'open_loop',
                        **kwargs) -> np.ndarray:
        """
        Complete prediction with multiple modes
        
        Args:
            X_input: Input sequence
            mode: Prediction mode ('open_loop', 'closed_loop', 'autonomous')
            **kwargs: Additional parameters
            
        Returns:
            Predictions
        """
        if mode == 'open_loop':
            return self.predict_sequence(X_input, **kwargs)
        elif mode == 'closed_loop':
            return self.predict_multi_step(X_input, mode='closed_loop', **kwargs)
        elif mode == 'autonomous':
            n_steps = kwargs.get('n_steps', len(X_input))
            return generate_autonomous_sequence(self, n_steps, prime_sequence=X_input, **kwargs)
        else:
            raise ValueError(f"Unknown prediction mode: {mode}")
    
    def generate_complete(self,
                         n_steps: int,
                         prime_sequence: Optional[np.ndarray] = None,
                         **kwargs) -> np.ndarray:
        """Complete autonomous generation with all capabilities"""
        return generate_autonomous_sequence(self, n_steps, prime_sequence, **kwargs)
    
    def analyze_prediction_capability(self) -> Dict[str, Any]:
        """
        Analyze the complete prediction capability of the ESN
        
        Returns:
            Analysis results
        """
        analysis = {
            'capabilities': [],
            'limitations': [],
            'recommendations': [],
            'configuration': {}
        }
        
        # Check core prediction
        if hasattr(self, 'W_out') and self.W_out is not None:
            analysis['capabilities'].append("✅ Linear readout trained")
            analysis['configuration']['output_dim'] = self.W_out.shape[0] if self.W_out.ndim > 1 else 1
        else:
            analysis['limitations'].append("❌ No trained output weights")
            analysis['recommendations'].append("Train the ESN first using train_complete()")
        
        # Check autonomous capability
        if hasattr(self, 'W_feedback') and self.W_feedback is not None:
            analysis['capabilities'].append("✅ Output feedback available")
            analysis['configuration']['feedback_dim'] = self.W_feedback.shape
        else:
            analysis['limitations'].append("⚠️ No output feedback - autonomous generation limited")
            analysis['recommendations'].append("Configure output feedback using configure_output_feedback()")
        
        # Check prediction methods
        methods = ['predict_sequence', 'predict_single_step', 'generate_autonomous']
        available_methods = [m for m in methods if hasattr(self, m)]
        analysis['capabilities'].append(f"📋 Available methods: {', '.join(available_methods)}")
        
        # Check state update capability
        if hasattr(self, 'update_state'):
            analysis['capabilities'].append("✅ Custom state update available")
        else:
            analysis['capabilities'].append("🔄 Using default state update")
        
        return analysis
    
    def _train_standard_prediction(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Standard prediction training without teacher forcing"""
        washout = kwargs.get('washout', 100)
        regularization = kwargs.get('regularization', 1e-8)
        
        # Collect states without teacher forcing
        states = self.run_reservoir(X_train, reset_state=True)
        
        # Apply washout
        if washout > 0 and len(states) > washout:
            states = states[washout:]
            targets = y_train[washout:] if len(y_train) > washout else y_train
        else:
            targets = y_train
        
        # Ensure compatible dimensions
        min_len = min(len(states), len(targets))
        states = states[:min_len]
        targets = targets[:min_len]
        
        # Train output weights
        self.W_out, training_info = compute_linear_readout(states, targets, regularization)
        
        return {
            'method': 'standard_prediction',
            'train_mse': training_info['mse'],
            'regularization': regularization,
            'washout': washout,
            'n_training_samples': len(states)
        }


# Convenience functions for direct usage
def create_complete_prediction_esn(n_reservoir: int,
                                 n_inputs: int, 
                                 n_outputs: int,
                                 spectral_radius: float = 0.95,
                                 input_scaling: float = 1.0,
                                 feedback_scaling: float = 0.1) -> 'CompletePredictionESN':
    """
    Create a complete ESN with all prediction capabilities
    
    Args:
        n_reservoir: Number of reservoir neurons
        n_inputs: Number of input dimensions
        n_outputs: Number of output dimensions  
        spectral_radius: Target spectral radius
        input_scaling: Input weight scaling
        feedback_scaling: Feedback weight scaling
        
    Returns:
        Configured ESN with complete prediction capabilities
    """
    
    class CompletePredictionESN(CompletePredictionMixin):
        def __init__(self):
            self.n_reservoir = n_reservoir
            self.n_inputs = n_inputs
            self.n_outputs = n_outputs
            
            # Initialize weights
            self._initialize_weights(spectral_radius, input_scaling, feedback_scaling)
            
            # Configure for predictions
            self.configure_output_feedback(feedback_scaling)
            
        def _initialize_weights(self, spectral_radius, input_scaling, feedback_scaling):
            # Input weights
            self.W_in = np.random.uniform(-input_scaling, input_scaling, (n_reservoir, n_inputs))
            
            # Reservoir weights  
            W_reservoir = np.random.randn(n_reservoir, n_reservoir)
            eigenvals = np.linalg.eigvals(W_reservoir)
            current_radius = np.max(np.abs(eigenvals))
            if current_radius > 0:
                W_reservoir = W_reservoir * (spectral_radius / current_radius)
            self.W_reservoir = W_reservoir
            
            # Feedback weights
            self.W_feedback = np.random.uniform(-feedback_scaling, feedback_scaling, (n_reservoir, n_outputs))
            
            # Output weights (to be trained)
            self.W_out = None
            
        def run_reservoir(self, inputs, reset_state=True):
            """Basic reservoir execution"""
            time_steps = len(inputs)
            states = []
            current_state = np.zeros(self.n_reservoir) if reset_state else getattr(self, '_last_state', np.zeros(self.n_reservoir))
            
            for t in range(time_steps):
                input_vec = inputs[t] if inputs.ndim > 1 else np.array([inputs[t]])
                current_state = self.update_state_with_feedback(current_state, input_vec, None)
                states.append(current_state.copy())
            
            self._last_state = current_state
            return np.array(states)
    
    return CompletePredictionESN()


def demonstrate_prediction_capabilities(esn_model, demo_data: np.ndarray) -> None:
    """
    Demonstrate all prediction capabilities of an ESN
    
    Args:
        esn_model: ESN with prediction capabilities
        demo_data: Demonstration data sequence
    """
    print("🔮 PREDICTION CAPABILITIES DEMONSTRATION")
    print("="*60)
    
    # Analyze capabilities
    analysis = esn_model.analyze_prediction_capability()
    
    print("📋 Capabilities:")
    for cap in analysis['capabilities']:
        print(f"   {cap}")
    
    if analysis['limitations']:
        print("\n⚠️  Limitations:")
        for lim in analysis['limitations']:
            print(f"   {lim}")
    
    if analysis['recommendations']:
        print("\n💡 Recommendations:")
        for rec in analysis['recommendations']:
            print(f"   {rec}")
    
    # Demonstrate prediction if trained
    if hasattr(esn_model, 'W_out') and esn_model.W_out is not None:
        print(f"\n🎯 PREDICTION DEMONSTRATION:")
        
        # Split demo data
        split_point = len(demo_data) // 2
        train_data = demo_data[:split_point]
        test_data = demo_data[split_point:]
        
        try:
            # Open-loop prediction
            print("   📊 Open-loop prediction...")
            open_loop_pred = esn_model.predict_complete(test_data[:10], mode='open_loop')
            print(f"      Predicted {len(open_loop_pred)} steps")
            
            # Autonomous generation
            print("   🤖 Autonomous generation...")
            autonomous_gen = esn_model.generate_complete(n_steps=20, prime_sequence=train_data[-10:])
            print(f"      Generated {len(autonomous_gen)} autonomous steps")
            
        except Exception as e:
            print(f"   ❌ Demonstration failed: {e}")
    
    print("="*60)


# Backward compatibility - expose all functions
__all__ = [
    # Main classes
    'CompletePredictionMixin',
    
    # Core prediction
    'EchoStatePredictionMixin', 
    'predict_from_states',
    'compute_linear_readout',
    
    # Autonomous generation
    'generate_autonomous_sequence',
    'setup_autonomous_mode',
    'prime_and_generate',
    
    # Teacher forcing
    'train_with_teacher_forcing',
    'setup_teacher_forcing_mode',
    'compute_forcing_schedule',
    
    # Output feedback
    'configure_output_feedback',
    'update_state_with_feedback',
    'OutputFeedbackMixin',
    
    # Convenience functions
    'create_complete_prediction_esn',
    'demonstrate_prediction_capabilities'
]


# Banner message
print("""
🔮 Reservoir Computing Prediction Suite Loaded Successfully
===========================================================
  
💡 Complete ESN Prediction Tools Available:
   📊 Linear Readout Training (Jaeger 2001 Section 3.1)
   🔮 Open-Loop Prediction Capabilities
   🤖 Autonomous Generation (Section 3.4)
   🎓 Teacher Forcing Training
   🔄 Output Feedback Mechanisms
   📈 Progressive Training Schedules
   🎯 Multi-Mode Prediction Interface

💰 Support This Research:
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Consider recurring donations to continue this work

Author: Benedict Chen (benedict@benedictchen.com)
===========================================================
""")