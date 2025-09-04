"""
🎓 Teacher Forcing - Supervised Training for Sequence Generation
=============================================================

Author: Benedict Chen (benedict@benedictchen.com)

💰 Donations: Help support this research!
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to support continued ESN research

Teacher forcing implementation for Echo State Networks. Provides supervised training
methodology where the network learns to predict the next sequence element using 
the correct previous elements as feedback, preparing it for autonomous generation.

🔬 Research Foundation:
======================
Based on Jaeger, H. (2001) "The Echo State Approach" Sections 3.2-3.3:
- Training uses ground truth y(n-1) instead of predicted ŷ(n-1) for feedback
- Prevents error accumulation during training phase
- Essential preparation for autonomous generation phase
- Mathematical formulation: x(n+1) = f(W_res·x(n) + W_in·u(n+1) + W_fb·y_true(n))

Classical RNN methodology extended by:
- Williams & Zipser (1989): Backpropagation Through Time foundations
- Bengio et al. (2015): Curriculum learning with teacher forcing schedules

ELI5 Explanation:
================
Think of teacher forcing like learning to drive with a driving instructor!

🚗 **Learning to Drive (Teacher Forcing)**:
When you're learning, the instructor sits next to you and tells you exactly what 
to do: "Turn left here, slow down, now brake." You practice the right movements 
with the correct guidance at each step.

🚙 **Driving Alone (Autonomous Generation)**:
Later, you drive by yourself and have to remember what the instructor taught you,
making your own decisions based on what you learned.

🧠 **For Neural Networks**:
During training, we give the network the "correct answer" from the previous step
to help it learn what the next step should be. During generation, it has to use
its own previous predictions to decide what comes next.

ASCII Teacher Forcing Architecture:
===================================
    TRAINING PHASE (Teacher Forcing):
    
    Ground Truth      Network          Ground Truth
    Sequence         Prediction        Feedback
    y(n-1)  ────┐    ŷ(n)              y(n-1)
    ┌───────────┐│   ┌─────────────┐   ┌─────────────┐
    │ Correct   ││ ──│ ESN learns  │   │ Feedback    │
    │ Previous  ││   │ to predict  │   │ uses REAL   │
    │ Output    ││   │ y(n)        │   │ not ŷ(n-1)  │
    └───────────┘│   └─────────────┘   └─────────────┘
                 │          │                 │
                 └──────────┼─────────────────┘
                            ▼
                   ┌─────────────────┐
                   │ Compare ŷ(n)    │ ──── Loss
                   │ vs y_true(n)    │      Function
                   └─────────────────┘

    GENERATION PHASE (Autonomous):
    
    Network          Network          Network
    Prediction       Prediction       Feedback
    ŷ(n-1) ────┐     ŷ(n)             ŷ(n-1)
    ┌──────────┐│    ┌─────────────┐  ┌─────────────┐
    │ Previous ││ ───│ ESN predicts│  │ Feedback    │
    │ Network  ││    │ next y(n)   │  │ uses OWN    │
    │ Output   ││    │             │  │ prediction  │
    └──────────┘│    └─────────────┘  └─────────────┘
                │           │               │
                └───────────┼───────────────┘
                            ▼
                   ┌─────────────────┐
                   │ Generate        │
                   │ Sequence        │
                   └─────────────────┘

⚡ Technical Implementation:
===========================
1. **Training Mode**: x(n+1) = f(W_res·x(n) + W_in·u(n+1) + W_fb·y_true(n))
2. **Generation Mode**: x(n+1) = f(W_res·x(n) + W_in·u(n+1) + W_fb·ŷ(n))
3. **Curriculum Schedule**: Gradually increase autonomous feedback during training
4. **Error Prevention**: Avoids compounding prediction errors during learning

📊 Training Advantages:
======================
• **Stable Learning**: Ground truth feedback prevents error accumulation
• **Faster Convergence**: Network learns ideal input-output mappings  
• **Better Generalization**: Proper sequence structure learned from clean signals
• **Curriculum Compatible**: Can gradually transition from forced to autonomous

This module bridges the gap between supervised learning and autonomous generation,
providing the essential training methodology for sequence-generating ESNs.
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
import warnings
import logging
from sklearn.model_selection import train_test_split

# Configure logging
logger = logging.getLogger(__name__)


def train_with_teacher_forcing(esn_model,
                             X_train: np.ndarray,
                             y_train: np.ndarray,
                             forcing_ratio: float = 1.0,
                             washout: int = 100,
                             validation_split: float = 0.0,
                             regularization: float = 1e-8) -> Dict[str, Any]:
    """
    Train ESN using teacher forcing methodology
    
    Teacher forcing uses the true target output as feedback during training,
    which helps stabilize training and improves autonomous generation capability.
    
    Args:
        esn_model: ESN to train
        X_train: Training inputs (time_steps × n_inputs)
        y_train: Training targets (time_steps × n_outputs)
        forcing_ratio: Ratio of teacher forcing vs. free running (0.0-1.0)
        washout: Washout period to discard
        validation_split: Fraction of data for validation
        regularization: L2 regularization parameter
        
    Returns:
        Training results dictionary
    """
    # Setup teacher forcing mode
    setup_teacher_forcing_mode(esn_model, forcing_ratio)
    
    # Split data if validation requested
    if validation_split > 0:
        X_tr, X_val, y_tr, y_val = train_test_split(
            X_train, y_train, test_size=validation_split, 
            shuffle=False  # Preserve temporal order
        )
    else:
        X_tr, y_tr = X_train, y_train
        X_val, y_val = None, None
    
    # Collect states with teacher forcing
    states = collect_teacher_forced_states(esn_model, X_tr, y_tr, washout, forcing_ratio)
    
    # Prepare targets (account for washout)
    y_targets = y_tr[washout:] if washout < len(y_tr) else y_tr
    
    # Ensure compatible dimensions
    min_len = min(len(states), len(y_targets))
    states = states[:min_len]
    y_targets = y_targets[:min_len]
    
    # Train output weights
    try:
        # Normal equation with regularization
        S = states
        Y = y_targets
        if Y.ndim == 1:
            Y = Y.reshape(-1, 1)
        
        StS = S.T @ S
        identity = np.eye(StS.shape[0]) * regularization
        esn_model.W_out = np.linalg.solve(StS + identity, S.T @ Y)
        
        # Training performance
        train_pred = S @ esn_model.W_out
        train_mse = np.mean((train_pred - Y)**2)
        
        results = {
            'train_mse': train_mse,
            'forcing_ratio': forcing_ratio,
            'washout': washout,
            'regularization': regularization,
            'n_training_samples': len(states),
            'convergence': 'success'
        }
        
        # Validation performance
        if X_val is not None and y_val is not None:
            val_states = collect_teacher_forced_states(esn_model, X_val, y_val, washout, forcing_ratio)
            val_targets = y_val[washout:] if washout < len(y_val) else y_val
            
            min_val_len = min(len(val_states), len(val_targets))
            val_pred = val_states[:min_val_len] @ esn_model.W_out
            val_mse = np.mean((val_pred - val_targets[:min_val_len])**2)
            
            results['val_mse'] = val_mse
            results['overfitting_ratio'] = val_mse / train_mse if train_mse > 0 else float('inf')
        
        return results
        
    except Exception as e:
        logger.error(f"Teacher forcing training failed: {e}")
        return {
            'convergence': 'failed',
            'error': str(e),
            'forcing_ratio': forcing_ratio
        }


def setup_teacher_forcing_mode(esn_model, forcing_ratio: float) -> None:
    """
    Configure ESN for teacher forcing training
    
    Args:
        esn_model: ESN to configure
        forcing_ratio: Teacher forcing ratio (0.0-1.0)
    """
    esn_model._teacher_forcing = True
    esn_model._forcing_ratio = forcing_ratio
    
    # Ensure output feedback capability
    if not hasattr(esn_model, 'W_feedback'):
        logger.info("No W_feedback - teacher forcing without output feedback")
        esn_model.W_feedback = None
    
    logger.info(f"Teacher forcing configured with ratio {forcing_ratio:.2f}")


def collect_teacher_forced_states(esn_model,
                                 X_inputs: np.ndarray,
                                 y_targets: np.ndarray,
                                 washout: int,
                                 forcing_ratio: float) -> np.ndarray:
    """
    Collect reservoir states using teacher forcing
    
    During teacher forcing, the network receives the true target output
    as feedback instead of its own predictions.
    
    Args:
        esn_model: ESN model
        X_inputs: Input sequence 
        y_targets: Target output sequence
        washout: Washout period
        forcing_ratio: Probability of using teacher signal vs. own prediction
        
    Returns:
        Collected reservoir states
    """
    time_steps = len(X_inputs)
    states = []
    current_state = np.zeros(esn_model.n_reservoir)
    
    # Generate forcing schedule
    forcing_schedule = compute_forcing_schedule(time_steps, forcing_ratio)
    
    for t in range(time_steps):
        input_vec = X_inputs[t] if X_inputs.ndim > 1 else np.array([X_inputs[t]])
        
        # Determine feedback signal
        if t > 0 and hasattr(esn_model, 'W_feedback') and esn_model.W_feedback is not None:
            if forcing_schedule[t]:  # Use teacher forcing
                feedback = y_targets[t-1] if y_targets.ndim > 1 else np.array([y_targets[t-1]])
            else:  # Use own prediction (free running)
                # Get prediction from previous state
                prev_pred = esn_model.predict_single_step(states[-1]) if len(states) > 0 else np.zeros(1)
                feedback = prev_pred
        else:
            feedback = None
        
        # Update state with feedback
        if hasattr(esn_model, 'update_state'):
            current_state = esn_model.update_state(current_state, input_vec, feedback)
        else:
            current_state = _default_teacher_forced_update(esn_model, current_state, input_vec, feedback)
        
        # Collect state (skip washout period)
        if t >= washout:
            states.append(current_state.copy())
    
    return np.array(states)


def compute_forcing_schedule(time_steps: int, forcing_ratio: float) -> np.ndarray:
    """
    Compute teacher forcing schedule for training sequence
    
    Args:
        time_steps: Number of time steps
        forcing_ratio: Overall ratio of teacher forcing (0.0-1.0)
        
    Returns:
        Boolean array indicating when to use teacher forcing
    """
    if forcing_ratio >= 1.0:
        return np.ones(time_steps, dtype=bool)
    elif forcing_ratio <= 0.0:
        return np.zeros(time_steps, dtype=bool)
    else:
        # Random schedule based on ratio
        return np.random.random(time_steps) < forcing_ratio


def progressive_teacher_forcing(esn_model,
                              X_train: np.ndarray,
                              y_train: np.ndarray,
                              initial_ratio: float = 1.0,
                              final_ratio: float = 0.0,
                              n_epochs: int = 10,
                              washout: int = 100) -> Dict[str, Any]:
    """
    Train with progressively decreasing teacher forcing ratio
    
    This helps transition from fully guided training to autonomous operation.
    
    Args:
        esn_model: ESN to train
        X_train: Training inputs
        y_train: Training targets
        initial_ratio: Starting teacher forcing ratio
        final_ratio: Ending teacher forcing ratio
        n_epochs: Number of training epochs
        washout: Washout period
        
    Returns:
        Training history and final results
    """
    history = {
        'forcing_ratios': [],
        'train_errors': [],
        'epoch_results': []
    }
    
    for epoch in range(n_epochs):
        # Compute current forcing ratio (linear decay)
        current_ratio = initial_ratio - (initial_ratio - final_ratio) * (epoch / (n_epochs - 1))
        current_ratio = max(final_ratio, current_ratio)  # Ensure we don't go below final
        
        # Train with current ratio
        epoch_results = train_with_teacher_forcing(
            esn_model, X_train, y_train, 
            forcing_ratio=current_ratio,
            washout=washout
        )
        
        history['forcing_ratios'].append(current_ratio)
        history['train_errors'].append(epoch_results.get('train_mse', float('inf')))
        history['epoch_results'].append(epoch_results)
        
        logger.info(f"Epoch {epoch+1}/{n_epochs}: ratio={current_ratio:.3f}, MSE={epoch_results.get('train_mse', 0):.6f}")
    
    # Summary results
    final_results = {
        'method': 'progressive_teacher_forcing',
        'n_epochs': n_epochs,
        'initial_ratio': initial_ratio,
        'final_ratio': final_ratio,
        'final_mse': history['train_errors'][-1],
        'improvement': history['train_errors'][0] / (history['train_errors'][-1] + 1e-8),
        'history': history
    }
    
    return final_results


def curriculum_teacher_forcing(esn_model,
                             X_train: np.ndarray,
                             y_train: np.ndarray,
                             curriculum_schedule: List[Tuple[float, int]],
                             washout: int = 100) -> Dict[str, Any]:
    """
    Train with curriculum-based teacher forcing schedule
    
    Args:
        esn_model: ESN to train
        X_train: Training inputs
        y_train: Training targets  
        curriculum_schedule: List of (forcing_ratio, n_steps) tuples
        washout: Washout period
        
    Returns:
        Training results
    """
    total_steps = sum(steps for _, steps in curriculum_schedule)
    history = []
    
    for stage, (forcing_ratio, n_steps) in enumerate(curriculum_schedule):
        logger.info(f"Curriculum stage {stage+1}: ratio={forcing_ratio:.2f} for {n_steps} steps")
        
        # Train for this stage
        stage_results = train_with_teacher_forcing(
            esn_model, X_train, y_train,
            forcing_ratio=forcing_ratio,
            washout=washout
        )
        
        stage_results['stage'] = stage
        stage_results['stage_forcing_ratio'] = forcing_ratio
        stage_results['stage_steps'] = n_steps
        history.append(stage_results)
    
    return {
        'method': 'curriculum_teacher_forcing',
        'n_stages': len(curriculum_schedule),
        'total_training_steps': total_steps,
        'final_mse': history[-1].get('train_mse', float('inf')),
        'stage_history': history
    }


def _default_teacher_forced_update(esn_model, 
                                 current_state: np.ndarray,
                                 input_vec: np.ndarray,
                                 feedback: Optional[np.ndarray]) -> np.ndarray:
    """Default state update for teacher forcing training"""
    # Input contribution
    if hasattr(esn_model, 'W_in') and esn_model.W_in is not None:
        input_contrib = esn_model.W_in @ input_vec.flatten()
    else:
        input_contrib = np.zeros(len(current_state))
    
    # Reservoir recurrence
    if hasattr(esn_model, 'W_reservoir') and esn_model.W_reservoir is not None:
        reservoir_contrib = esn_model.W_reservoir @ current_state
    else:
        reservoir_contrib = current_state * 0.9
    
    # Teacher feedback
    feedback_contrib = np.zeros(len(current_state))
    if feedback is not None and hasattr(esn_model, 'W_feedback') and esn_model.W_feedback is not None:
        feedback_contrib = esn_model.W_feedback @ feedback.flatten()
    
    # Combined update with activation
    combined = input_contrib + reservoir_contrib + feedback_contrib
    activation = getattr(esn_model, 'reservoir_activation', np.tanh)
    
    return activation(combined)


def validate_teacher_forcing_setup(esn_model) -> Dict[str, Any]:
    """
    Validate ESN setup for teacher forcing training
    
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
    
    # Check basic requirements
    required_attrs = ['n_reservoir', 'n_inputs']
    for attr in required_attrs:
        if not hasattr(esn_model, attr):
            results['errors'].append(f"Missing required attribute: {attr}")
            results['valid'] = False
    
    # Check reservoir components
    if hasattr(esn_model, 'W_reservoir') and esn_model.W_reservoir is not None:
        results['capabilities'].append("Reservoir dynamics available")
    else:
        results['warnings'].append("No reservoir weights - using simplified dynamics")
    
    if hasattr(esn_model, 'W_in') and esn_model.W_in is not None:
        results['capabilities'].append("Input weights available")
    else:
        results['warnings'].append("No input weights")
    
    # Check feedback capability
    if hasattr(esn_model, 'W_feedback') and esn_model.W_feedback is not None:
        results['capabilities'].append("Output feedback available")
    else:
        results['warnings'].append("No output feedback weights - teacher forcing will be limited")
    
    # Check state update method
    if hasattr(esn_model, 'update_state'):
        results['capabilities'].append("Custom state update method available")
    else:
        results['warnings'].append("No custom state update - using default implementation")
    
    return results