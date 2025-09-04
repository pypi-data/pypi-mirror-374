"""
🤖 Autonomous Generation - Self-Sustaining ESN Sequence Creation
==============================================================

Author: Benedict Chen (benedict@benedictchen.com)

💰 Donations: Help support this research!
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to support continued ESN research

Autonomous sequence generation for Echo State Networks - the crown jewel capability
that transforms ESNs from pattern recognizers into creative sequence generators.
After training, the network becomes a self-sustaining dynamical system.

🔬 Research Foundation:
======================
Based on Jaeger, H. (2001) "The Echo State Approach" Section 3.4, Figure 5:
- Closed-loop dynamics: x(n+1) = f(W_res·x(n) + W_fb·y(n))
- No external input during generation: u(n) = 0 
- Network sustains dynamics through its own output feedback
- Critical requirement: stable attractor dynamics learned during training

Mathematical Framework:
- Training: x(n+1) = f(W_res·x(n) + W_in·u(n) + W_fb·y_true(n))
- Generation: x(n+1) = f(W_res·x(n) + W_fb·ŷ(n))
- Output: ŷ(n) = W_out·[u(n); x(n)] where u(n) = 0

ELI5 Explanation:
================
Think of autonomous generation like a musician improvising jazz! 🎵

🎹 **Learning Phase (Training)**:
A jazz student learns by playing along with a teacher. The teacher plays
the "correct" notes (ground truth feedback), and the student practices
matching those patterns. The student's brain (reservoir) learns the 
musical relationships and rhythmic patterns.

🎺 **Improvisation Phase (Autonomous Generation)**:
Now the student performs solo! There's no teacher anymore - the musician
must use what they learned to create new music. Each note they play 
influences what note comes next, just like how the ESN's own output
becomes the input for generating the next step.

🎶 **The Magic**:
- The musician doesn't just repeat what they learned exactly
- They create NEW sequences that follow the same musical "style" 
- Sometimes they play variations, sometimes surprising new melodies
- But it all sounds like it belongs to the same musical genre

ASCII Autonomous Generation Architecture:
========================================
    TRAINING PHASE (Learning the Patterns):
    
    External Input    Ground Truth      Network State
    u(n)             y_true(n)         x(n+1)
    ┌─────────────┐  ┌─────────────┐   ┌─────────────────┐
    │ Music Teacher│  │ Correct     │   │ Student Brain   │
    │ Plays Melody │  │ Next Note   │   │ Learns Patterns │
    └─────┬───────┘  └─────┬───────┘   └─────────────────┘
          │                │                     │
          └────────────────┼─────────────────────┘
                           ▼
                  ┌─────────────────┐
                  │ Training Update │
                  │ "Learn to mimic │ 
                  │  the teacher"   │
                  └─────────────────┘

    AUTONOMOUS GENERATION (Creating New Music):
    
    No Input         Own Previous      Network State  
    u(n) = 0        Output ŷ(n-1)     x(n+1)
    ┌─────────────┐ ┌─────────────┐   ┌─────────────────┐
    │ No Teacher  │ │ Previous    │   │ Student Now     │
    │ (Silence)   │ │ Note Played │   │ Improvises Solo │
    └─────────────┘ └─────┬───────┘   └─────────────────┘
                          │                     │
                          └─────────────────────┘
                                    ▼
                          ┌─────────────────┐
                          │ Generate Next   │
                          │ Note: ŷ(n) =    │ ──┐
                          │ f(memory+prev)  │   │
                          └─────────────────┘   │
                                    │           │
                                    └───────────┘
                                   Feeds back for
                                   next generation

⚡ Generation Process:
=====================
1. **Initialization**: Prime network with seed sequence or random state
2. **Autonomous Loop**: x(n+1) = f(W_res·x(n) + W_fb·ŷ(n))
3. **Output Generation**: ŷ(n) = W_out·[0; x(n)] (no external input)
4. **Feedback**: Generated output feeds back as input for next step
5. **Continuation**: Process repeats for desired sequence length

📊 Generation Quality Factors:
=============================
• **Training Quality**: Better trained networks → more coherent generation
• **Feedback Scaling**: W_fb magnitude affects generation dynamics
• **Network Stability**: Spectral radius determines long-term behavior
• **Temperature**: Controls randomness vs deterministic generation
• **Priming**: Initial sequence quality influences subsequent generation

This module enables ESNs to become autonomous creative systems,
generating novel sequences that maintain learned statistical properties.
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
import warnings
import logging

# Configure logging
logger = logging.getLogger(__name__)


def generate_autonomous_sequence(esn_model,
                               n_steps: int,
                               prime_sequence: Optional[np.ndarray] = None,
                               initial_state: Optional[np.ndarray] = None,
                               temperature: float = 0.0,
                               return_states: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """
    Generate sequence autonomously using trained ESN
    
    Based on Jaeger (2001) Section 3.4: "the trained network can autonomously 
    generate the teacher signal"
    
    Args:
        esn_model: Trained ESN with output feedback capability
        n_steps: Number of steps to generate
        prime_sequence: Optional sequence to prime the network
        initial_state: Optional initial reservoir state
        temperature: Noise level for stochastic generation
        return_states: Whether to return reservoir states
        
    Returns:
        Generated sequence, optionally with states
    """
    if not hasattr(esn_model, 'W_out') or esn_model.W_out is None:
        raise ValueError("ESN must be trained first")
    
    # Setup autonomous mode
    setup_autonomous_mode(esn_model)
    
    # Initialize state
    if prime_sequence is not None:
        # Prime with initial sequence
        current_state = prime_and_generate(esn_model, prime_sequence)
        last_output = esn_model.predict_single_step(current_state)
    elif initial_state is not None:
        current_state = initial_state.copy()
        last_output = esn_model.predict_single_step(current_state)
    else:
        # Start from zero state
        current_state = np.zeros(esn_model.n_reservoir)
        last_output = np.zeros(getattr(esn_model, 'n_outputs', 1))
    
    # Generate sequence
    generated_outputs = []
    states_sequence = []
    
    for step in range(n_steps):
        # Update reservoir state with output feedback
        current_state = update_state_with_feedback(
            esn_model, current_state, np.zeros(esn_model.n_inputs), last_output
        )
        
        # Generate next output
        next_output = esn_model.predict_single_step(current_state)
        
        # Add noise if temperature > 0
        if temperature > 0:
            noise = np.random.normal(0, temperature, next_output.shape)
            next_output = next_output + noise
        
        generated_outputs.append(next_output.copy())
        states_sequence.append(current_state.copy())
        
        last_output = next_output
    
    generated_sequence = np.array(generated_outputs)
    
    if return_states:
        return generated_sequence, np.array(states_sequence)
    return generated_sequence


def setup_autonomous_mode(esn_model) -> None:
    """
    Setup ESN for autonomous generation mode
    
    Ensures the ESN has proper output feedback configuration
    for closed-loop generation.
    
    Args:
        esn_model: ESN to configure for autonomous mode
    """
    # Check for output feedback weights
    if not hasattr(esn_model, 'W_feedback'):
        logger.info("No W_feedback found - autonomous generation without output feedback")
        esn_model.W_feedback = None
    
    # Check for reservoir dynamics
    if not hasattr(esn_model, 'update_state'):
        logger.warning("No update_state method - using default state update")
        esn_model.update_state = _default_state_update
    
    # Store generation mode
    esn_model._generation_mode = 'autonomous'
    
    # Validate configuration
    validation = validate_autonomous_setup(esn_model)
    if not validation['valid']:
        logger.warning(f"Autonomous setup issues: {validation['warnings']}")


def prime_and_generate(esn_model, prime_sequence: np.ndarray) -> np.ndarray:
    """
    Prime the ESN with an initial sequence and return final state
    
    Args:
        esn_model: ESN model
        prime_sequence: Sequence to prime the network
        
    Returns:
        Final reservoir state after priming
    """
    if len(prime_sequence) == 0:
        return np.zeros(esn_model.n_reservoir)
    
    # Run prime sequence through reservoir
    if hasattr(esn_model, 'run_reservoir'):
        states = esn_model.run_reservoir(prime_sequence, reset_state=True)
        return states[-1]
    else:
        # Fallback: manual state evolution
        current_state = np.zeros(esn_model.n_reservoir)
        
        for t in range(len(prime_sequence)):
            input_vec = prime_sequence[t]
            if input_vec.ndim == 0:
                input_vec = np.array([input_vec])
                
            current_state = update_state_with_feedback(
                esn_model, current_state, input_vec, None
            )
        
        return current_state


def update_state_with_feedback(esn_model, 
                             current_state: np.ndarray,
                             input_vec: np.ndarray, 
                             feedback_output: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Update reservoir state including output feedback
    
    Implements: x(n+1) = f(W_in*u(n+1) + W*x(n) + W_feedback*y(n))
    
    Args:
        esn_model: ESN model with reservoir parameters
        current_state: Current reservoir state x(n)
        input_vec: Input vector u(n+1)
        feedback_output: Previous output y(n) for feedback
        
    Returns:
        Next reservoir state x(n+1)
    """
    # Input contribution
    if hasattr(esn_model, 'W_in') and esn_model.W_in is not None:
        input_contrib = esn_model.W_in @ input_vec.flatten()
    else:
        input_contrib = np.zeros(len(current_state))
    
    # Reservoir recurrence
    if hasattr(esn_model, 'W_reservoir') and esn_model.W_reservoir is not None:
        reservoir_contrib = esn_model.W_reservoir @ current_state
    else:
        reservoir_contrib = current_state * 0.9  # Simple decay
    
    # Output feedback contribution
    feedback_contrib = np.zeros(len(current_state))
    if feedback_output is not None and hasattr(esn_model, 'W_feedback') and esn_model.W_feedback is not None:
        feedback_contrib = esn_model.W_feedback @ feedback_output.flatten()
    
    # Combined update
    combined_input = input_contrib + reservoir_contrib + feedback_contrib
    
    # Apply activation function
    activation = getattr(esn_model, 'reservoir_activation', np.tanh)
    next_state = activation(combined_input)
    
    return next_state


def generate_with_constraints(esn_model,
                            n_steps: int,
                            constraints: Dict[str, Any],
                            prime_sequence: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Generate sequence with constraints (amplitude, smoothness, etc.)
    
    Args:
        esn_model: Trained ESN
        n_steps: Number of steps to generate  
        constraints: Dictionary of constraints to apply
        prime_sequence: Optional priming sequence
        
    Returns:
        Constrained generated sequence
    """
    # Generate base sequence
    base_sequence = generate_autonomous_sequence(esn_model, n_steps, prime_sequence)
    
    # Apply constraints
    constrained_sequence = base_sequence.copy()
    
    # Amplitude constraints
    if 'amplitude_range' in constraints:
        min_amp, max_amp = constraints['amplitude_range']
        constrained_sequence = np.clip(constrained_sequence, min_amp, max_amp)
    
    # Smoothness constraints
    if 'smoothing_factor' in constraints:
        factor = constraints['smoothing_factor']
        if factor > 0:
            constrained_sequence = apply_smoothing(constrained_sequence, factor)
    
    # Periodic constraints
    if 'enforce_periodicity' in constraints:
        period = constraints['enforce_periodicity']
        if period > 0:
            constrained_sequence = enforce_periodicity(constrained_sequence, period)
    
    return constrained_sequence


def apply_smoothing(sequence: np.ndarray, smoothing_factor: float) -> np.ndarray:
    """Apply smoothing to generated sequence"""
    if smoothing_factor <= 0:
        return sequence
    
    smoothed = sequence.copy()
    for i in range(1, len(sequence)):
        smoothed[i] = (1 - smoothing_factor) * smoothed[i] + smoothing_factor * smoothed[i-1]
    
    return smoothed


def enforce_periodicity(sequence: np.ndarray, period: int) -> np.ndarray:
    """Enforce periodicity in generated sequence"""
    if period <= 0 or period >= len(sequence):
        return sequence
    
    periodic_sequence = sequence.copy()
    for i in range(period, len(sequence)):
        periodic_sequence[i] = sequence[i % period]
    
    return periodic_sequence


def _default_state_update(esn_model, current_state: np.ndarray, 
                        input_vec: np.ndarray, feedback: Optional[np.ndarray] = None) -> np.ndarray:
    """Default state update for ESNs without custom update method"""
    return update_state_with_feedback(esn_model, current_state, input_vec, feedback)


def validate_autonomous_setup(esn_model) -> Dict[str, Any]:
    """
    Validate ESN setup for autonomous generation
    
    Args:
        esn_model: ESN to validate
        
    Returns:
        Validation results
    """
    results = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'capabilities': []
    }
    
    # Check required components
    if not hasattr(esn_model, 'W_out') or esn_model.W_out is None:
        results['errors'].append("No output weights (W_out) - model must be trained")
        results['valid'] = False
    
    if not hasattr(esn_model, 'W_reservoir') or esn_model.W_reservoir is None:
        results['warnings'].append("No reservoir weights - using simple dynamics")
    else:
        results['capabilities'].append("Reservoir dynamics available")
    
    # Check feedback capability
    if hasattr(esn_model, 'W_feedback') and esn_model.W_feedback is not None:
        results['capabilities'].append("Output feedback available")
    else:
        results['warnings'].append("No output feedback weights - limited autonomous capability")
    
    # Check prediction capability
    if hasattr(esn_model, 'predict_single_step'):
        results['capabilities'].append("Single-step prediction available")
    else:
        results['warnings'].append("No predict_single_step method")
    
    # Check state update capability
    if hasattr(esn_model, 'update_state'):
        results['capabilities'].append("Custom state update available")
    elif hasattr(esn_model, 'run_reservoir'):
        results['capabilities'].append("Reservoir execution available")
    else:
        results['warnings'].append("Limited state update capability")
    
    return results


class AutonomousGenerationMixin:
    """
    Mixin class to add autonomous generation capabilities to ESN
    """
    
    def generate_autonomous(self, n_steps: int, **kwargs) -> np.ndarray:
        """Generate autonomous sequence"""
        return generate_autonomous_sequence(self, n_steps, **kwargs)
    
    def setup_autonomous_mode(self) -> None:
        """Setup for autonomous generation"""
        setup_autonomous_mode(self)
    
    def prime_and_generate(self, prime_sequence: np.ndarray, n_generate: int) -> np.ndarray:
        """Prime with sequence then generate"""
        final_state = prime_and_generate(self, prime_sequence)
        return generate_autonomous_sequence(self, n_generate, initial_state=final_state)