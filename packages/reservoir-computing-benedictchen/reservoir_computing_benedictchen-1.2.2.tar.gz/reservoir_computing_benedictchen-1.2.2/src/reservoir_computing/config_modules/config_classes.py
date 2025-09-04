"""
🏗️ Reservoir Computing - Configuration Classes Module
====================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
Configuration dataclasses for reservoir computing systems, providing structured
configuration objects with validation and default values.

📋 CONFIGURATION CLASSES:
========================
• ESNConfig - Standard Echo State Network configuration
• DeepESNConfig - Multi-layer reservoir configuration  
• OnlineESNConfig - Online learning ESN configuration
• OptimizationConfig - Hyperparameter optimization settings
• TaskConfig - Task-specific configuration parameters

🎓 RESEARCH FOUNDATION:
======================
Configuration design based on:
- Jaeger (2001): Core ESN parameters and their typical ranges
- Lukoševičius & Jaeger (2009): Practical parameter guidelines
- Modern best practices: Regularization, optimization, validation

Each configuration class encapsulates research-validated parameter
ranges and provides sensible defaults for different use cases.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any, Callable, Tuple
import numpy as np
from .config_enums import (
    ReservoirType, ActivationFunction, TopologyType, ReadoutType, 
    NoiseType, FeedbackMode, InitializationMethod, TrainingMethod,
    OptimizationObjective
)


@dataclass
class ESNConfig:
    """
    🏗️ Echo State Network Configuration Class
    
    Comprehensive configuration for standard ESN with research-validated
    parameter ranges and sensible defaults.
    
    Based on Jaeger (2001) and Lukoševičius & Jaeger (2009) guidelines.
    
    Key Parameters:
    - n_reservoir: Reservoir size (typical: 50-1000, larger for complex tasks)
    - spectral_radius: Critical for ESP (typical: 0.8-0.99, <1.0 for stability)
    - input_scaling: Input signal scaling (typical: 0.1-1.0)
    - leak_rate: Leaking rate for temporal dynamics (typical: 0.1-1.0)
    
    Example:
        ```python
        # Minimal configuration
        config = ESNConfig(n_reservoir=100, spectral_radius=0.95)
        
        # Task-specific configuration
        config = ESNConfig(
            n_reservoir=200,
            spectral_radius=0.9, 
            input_scaling=0.5,
            leak_rate=0.2,  # Slow dynamics for long-term dependencies
            activation=ActivationFunction.TANH,
            topology_type=TopologyType.SMALL_WORLD
        )
        ```
    """
    
    # === CORE RESERVOIR PARAMETERS ===
    n_reservoir: int = 100
    spectral_radius: float = 0.95
    input_scaling: float = 0.1  
    leak_rate: float = 1.0
    
    # === RESERVOIR ARCHITECTURE ===
    reservoir_type: ReservoirType = ReservoirType.ECHO_STATE_NETWORK
    activation: ActivationFunction = ActivationFunction.TANH
    topology_type: TopologyType = TopologyType.RANDOM_SPARSE
    sparsity: float = 0.1  # Connection probability
    
    # === INPUT/OUTPUT CONFIGURATION ===
    input_shift: float = 0.0
    output_shift: float = 0.0
    n_inputs: Optional[int] = None  # Auto-detected from data
    n_outputs: Optional[int] = None  # Auto-detected from data
    
    # === FEEDBACK CONFIGURATION ===
    feedback_mode: FeedbackMode = FeedbackMode.NONE
    feedback_scaling: float = 0.1
    output_feedback_scaling: float = 0.1
    
    # === TRAINING PARAMETERS ===
    readout_type: ReadoutType = ReadoutType.RIDGE
    regularization: float = 1e-6
    washout: int = 100  # Transient removal
    training_method: TrainingMethod = TrainingMethod.BATCH
    
    # === INITIALIZATION ===
    initialization_method: InitializationMethod = InitializationMethod.SPECTRAL_RADIUS
    weight_distribution: str = "uniform"  # "uniform" or "normal"
    input_connectivity: float = 1.0  # Fraction of inputs connected
    
    # === NOISE CONFIGURATION ===
    noise_type: NoiseType = NoiseType.NONE
    noise_level: float = 0.0
    input_noise: float = 0.0
    reservoir_noise: float = 0.0
    
    # === ADVANCED PARAMETERS ===
    bias_scaling: float = 0.0
    teacher_forcing_mode: bool = False
    ridge_alpha: Optional[float] = None  # Uses regularization if None
    random_seed: Optional[int] = None
    
    # === VALIDATION FLAGS ===
    validate_esp: bool = True  # Check Echo State Property
    esp_tolerance: float = 1e-3
    verbose: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.ridge_alpha is None:
            self.ridge_alpha = self.regularization
            
        # Basic validation
        if self.n_reservoir <= 0:
            raise ValueError("n_reservoir must be positive")
        if self.spectral_radius <= 0:
            raise ValueError("spectral_radius must be positive")
        if not (0 < self.sparsity <= 1):
            raise ValueError("sparsity must be in (0, 1]")
        if not (0 < self.leak_rate <= 1):
            raise ValueError("leak_rate must be in (0, 1]")


@dataclass  
class DeepESNConfig(ESNConfig):
    """
    🏗️ Deep Echo State Network Configuration
    
    Configuration for multi-layer reservoir networks with hierarchical
    temporal processing capabilities.
    
    Research Context:
    Deep ESNs stack multiple reservoir layers to process information
    at different temporal scales, similar to deep neural networks
    but maintaining the reservoir computing paradigm.
    
    Example:
        ```python
        config = DeepESNConfig(
            layer_sizes=[100, 50, 25],  # 3-layer hierarchy
            inter_layer_scaling=0.5,   # Reduced coupling
            layer_spectral_radii=[0.95, 0.9, 0.85]  # Decreasing dynamics
        )
        ```
    """
    
    # === DEEP ARCHITECTURE ===
    layer_sizes: List[int] = field(default_factory=lambda: [100, 50])
    layer_spectral_radii: Optional[List[float]] = None
    layer_sparsity: Optional[List[float]] = None
    layer_leak_rates: Optional[List[float]] = None
    
    # === INTER-LAYER CONNECTIONS ===
    inter_layer_scaling: float = 0.3
    skip_connections: bool = False
    bidirectional: bool = False
    
    def __post_init__(self):
        """Initialize layer-specific parameters"""
        super().__post_init__()
        
        n_layers = len(self.layer_sizes)
        
        # Set default layer spectral radii (decreasing)
        if self.layer_spectral_radii is None:
            self.layer_spectral_radii = [
                self.spectral_radius * (0.95 ** i) for i in range(n_layers)
            ]
            
        # Set default layer sparsity (same for all)
        if self.layer_sparsity is None:
            self.layer_sparsity = [self.sparsity] * n_layers
            
        # Set default layer leak rates (increasing for hierarchy)
        if self.layer_leak_rates is None:
            self.layer_leak_rates = [
                min(1.0, self.leak_rate * (1.1 ** i)) for i in range(n_layers)
            ]
        
        # Update n_reservoir to total size
        self.n_reservoir = sum(self.layer_sizes)


@dataclass
class OnlineESNConfig(ESNConfig):
    """
    🏗️ Online Echo State Network Configuration
    
    Configuration for online/incremental learning ESN with adaptive
    parameters and real-time processing capabilities.
    
    Research Context:
    Online ESNs adapt to non-stationary environments by updating
    readout weights incrementally as new data arrives, suitable
    for real-time applications and streaming data.
    
    Example:
        ```python
        config = OnlineESNConfig(
            adaptation_rate=0.01,      # Learning rate
            forgetting_factor=0.999,   # Exponential forgetting
            adaptation_threshold=0.1   # Change detection
        )
        ```
    """
    
    # === ONLINE LEARNING ===
    adaptation_rate: float = 0.01
    forgetting_factor: float = 0.999
    adaptation_threshold: float = 0.1
    online_batch_size: int = 1
    
    # === CHANGE DETECTION ===
    change_detection: bool = True
    detection_window: int = 100
    adaptation_window: int = 50
    
    # === REGULARIZATION ===
    online_regularization: float = 1e-4
    stability_check: bool = True
    max_singular_value: float = 100.0
    
    def __post_init__(self):
        """Configure for online learning"""
        super().__post_init__()
        
        # Force online training method
        self.training_method = TrainingMethod.ONLINE
        
        # Reduce washout for online learning
        if self.washout > 50:
            self.washout = 50


@dataclass
class OptimizationConfig:
    """
    🏗️ Hyperparameter Optimization Configuration
    
    Settings for automated hyperparameter optimization using various
    search strategies and evaluation metrics.
    
    Research Foundation:
    Systematic hyperparameter optimization crucial for reservoir computing
    due to sensitivity of ESP and dynamics to parameter choices.
    
    Example:
        ```python
        config = OptimizationConfig(
            param_ranges={
                'spectral_radius': (0.8, 0.99),
                'input_scaling': (0.1, 2.0),
                'leak_rate': (0.1, 1.0)
            },
            n_trials=100,
            cv_folds=5
        )
        ```
    """
    
    # === SEARCH SPACE ===
    param_ranges: Dict[str, Union[Tuple[float, float], List[Any]]] = field(
        default_factory=lambda: {
            'spectral_radius': (0.8, 0.99),
            'input_scaling': (0.1, 2.0),
            'leak_rate': (0.1, 1.0),
            'regularization': (1e-8, 1e-2),
            'sparsity': (0.05, 0.5)
        }
    )
    
    # === OPTIMIZATION STRATEGY ===
    n_trials: int = 50
    optimization_method: str = "random"  # "grid", "random", "bayesian"
    objective: OptimizationObjective = OptimizationObjective.MSE
    
    # === VALIDATION ===
    cv_folds: int = 3
    test_size: float = 0.2
    validation_metric: str = "mse"
    scoring_direction: str = "minimize"  # "minimize" or "maximize"
    
    # === SEARCH CONTROL ===
    timeout: Optional[float] = None  # Search timeout in seconds
    early_stopping: bool = True
    patience: int = 10
    min_improvement: float = 1e-6
    
    # === PARALLEL PROCESSING ===
    n_jobs: int = 1
    random_seed: Optional[int] = None
    verbose: bool = True
    
    # === PRUNING (for advanced methods) ===
    enable_pruning: bool = False
    pruning_percentile: float = 25.0


@dataclass
class TaskConfig:
    """
    🏗️ Task-Specific Configuration
    
    Configuration parameters specific to different types of reservoir
    computing tasks with pre-configured settings.
    
    Research Context:
    Different tasks (time series prediction, classification, generation)
    benefit from different reservoir configurations and parameter ranges.
    
    Example:
        ```python
        # Time series prediction task
        config = TaskConfig(
            task_type="time_series_prediction",
            sequence_length=100,
            prediction_horizon=10
        )
        
        # Classification task  
        config = TaskConfig(
            task_type="classification",
            n_classes=5,
            balanced_dataset=False
        )
        ```
    """
    
    # === TASK SPECIFICATION ===
    task_type: str = "regression"  # "regression", "classification", "generation"
    task_complexity: str = "medium"  # "simple", "medium", "complex"
    
    # === DATA CHARACTERISTICS ===
    sequence_length: Optional[int] = None
    n_features: Optional[int] = None
    n_classes: Optional[int] = None
    prediction_horizon: int = 1
    
    # === TASK-SPECIFIC PARAMETERS ===
    balanced_dataset: bool = True
    temporal_dependencies: str = "medium"  # "short", "medium", "long"
    noise_level: str = "low"  # "low", "medium", "high"
    
    # === PERFORMANCE REQUIREMENTS ===
    target_accuracy: Optional[float] = None
    max_training_time: Optional[float] = None
    memory_capacity_requirement: Optional[float] = None
    
    # === EVALUATION SETTINGS ===
    cross_validation: bool = True
    test_fraction: float = 0.2
    validation_fraction: float = 0.1
    
    def get_recommended_esn_config(self) -> ESNConfig:
        """
        Get recommended ESN configuration for this task.
        
        Returns:
            ESNConfig: Recommended configuration based on task characteristics
        """
        if self.task_type == "time_series_prediction":
            return ESNConfig(
                n_reservoir=min(200, max(50, (self.sequence_length or 100) * 2)),
                spectral_radius=0.95 if self.temporal_dependencies == "long" else 0.9,
                leak_rate=0.3 if self.temporal_dependencies == "long" else 0.7,
                input_scaling=0.1 if self.noise_level == "high" else 0.5
            )
        elif self.task_type == "classification":
            return ESNConfig(
                n_reservoir=max(100, (self.n_classes or 2) * 50),
                spectral_radius=0.9,
                leak_rate=0.5,
                readout_type=ReadoutType.RIDGE if self.n_classes and self.n_classes > 2 else ReadoutType.LINEAR
            )
        elif self.task_type == "generation":
            return ESNConfig(
                n_reservoir=200,
                spectral_radius=0.99,  # Higher for generation tasks
                feedback_mode=FeedbackMode.DIRECT,
                feedback_scaling=0.1,
                teacher_forcing_mode=True
            )
        else:  # Default regression
            return ESNConfig(
                n_reservoir=100,
                spectral_radius=0.95,
                leak_rate=0.5
            )


# Export all configuration classes
__all__ = [
    'ESNConfig',
    'DeepESNConfig', 
    'OnlineESNConfig',
    'OptimizationConfig',
    'TaskConfig'
]


if __name__ == "__main__":
    print("🏗️ Reservoir Computing - Configuration Classes")
    print("=" * 50)
    print("📋 CONFIGURATION CLASSES:")
    print("  • ESNConfig - Standard ESN configuration")
    print("  • DeepESNConfig - Multi-layer reservoir configuration")
    print("  • OnlineESNConfig - Online learning configuration")
    print("  • OptimizationConfig - Hyperparameter optimization settings")
    print("  • TaskConfig - Task-specific configuration parameters")
    print("")
    print("✅ All configuration classes loaded successfully!")
    print("🔬 Research-validated parameter ranges and defaults!")