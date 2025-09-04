"""
🔮 Prediction Generation Modules - Echo State Networks
=====================================================

Author: Benedict Chen (benedict@benedictchen.com)

Modular prediction generation components for Echo State Networks based on
Jaeger's seminal work. Provides both open-loop prediction and closed-loop
autonomous generation capabilities.

🏗️ **Module Architecture:**
- core_prediction.py - Basic prediction and readout functionality
- autonomous_generation.py - Closed-loop sequence generation  
- teacher_forcing.py - Training with teacher forcing
- output_feedback.py - Feedback mechanisms and state updates
- prediction_utilities.py - Utility functions and helpers

📊 **Research Foundation:**
Based on Jaeger, H. (2001) "The 'Echo State' Approach to Analysing and Training RNNs"
- Section 3.1: Linear readout training (Equations 11-12)
- Section 3.4: Autonomous generation capabilities
- Section 3.5: Teacher forcing vs. free-running modes

🎯 **Usage Examples:**
```python
from pred_modules import EchoStatePredictionMixin, autonomous_generate
from pred_modules import setup_teacher_forcing, configure_output_feedback

# Basic prediction
predictions = esn.predict_sequence(test_inputs)

# Autonomous generation  
generated = esn.generate_autonomous(n_steps=100, prime_sequence=primer)

# Teacher forcing training
esn.train_with_teacher_forcing(X_train, y_train, forcing_ratio=0.8)
```

💰 Donations: Help support this research!
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
"""

from .core_prediction import (
    EchoStatePredictionMixin,
    predict_from_states,
    compute_linear_readout
)

from .autonomous_generation import (
    generate_autonomous_sequence,
    setup_autonomous_mode,
    prime_and_generate
)

from .teacher_forcing import (
    train_with_teacher_forcing,
    setup_teacher_forcing_mode,
    compute_forcing_schedule
)

from .output_feedback import (
    configure_output_feedback,
    update_state_with_feedback,
    OutputFeedbackMixin
)

__all__ = [
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
    'OutputFeedbackMixin'
]