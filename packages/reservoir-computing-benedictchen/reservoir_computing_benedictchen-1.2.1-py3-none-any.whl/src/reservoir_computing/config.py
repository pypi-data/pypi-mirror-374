"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Reservoir Computing Configuration Classes - UNIFIED IMPLEMENTATION
================================================================

This module consolidates all configuration classes and enums for 
Reservoir Computing methods from the scattered structure.

Consolidated from:
- esn_modules/configuration_optimization.py (82KB - massive config system!)
- Various configuration enums and classes scattered across modules

Author: Benedict Chen (benedict@benedictchen.com)

Based on: Herbert Jaeger (2001) "The 'Echo State' Approach to Analysing 
and Training Recurrent Neural Networks" and Wolfgang Maass (2002) 
"Real-time Computing Without Stable States"
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any, Callable, Tuple
import numpy as np

# ============================================================================
# ENUMS - All Reservoir Computing Method Options
# ============================================================================

class ReservoirType(Enum):
    """Types of reservoir architectures."""
    ECHO_STATE_NETWORK = "esn"  # Standard ESN (Jaeger 2001)
    LIQUID_STATE_MACHINE = "lsm"  # LSM (Maass 2002)
    DEEP_RESERVOIR = "deep"  # Multi-layer reservoirs
    ONLINE_ESN = "online"  # Online learning ESN
    MODULAR_ESN = "modular"  # Modular architecture


class ActivationFunction(Enum):
    """Reservoir activation functions with theoretical backing."""
    TANH = "tanh"  # Standard hyperbolic tangent [-1, 1]
    SIGMOID = "sigmoid"  # Logistic sigmoid [0, 1]
    RELU = "relu"  # Rectified linear unit [0, ∞]
    LEAKY_RELU = "leaky_relu"  # Leaky ReLU with small negative slope
    SWISH = "swish"  # Swish activation x * sigmoid(x)
    LINEAR = "linear"  # Linear activation (identity)
    SOFTPLUS = "softplus"  # Smooth approximation to ReLU
    CUSTOM = "custom"  # User-defined function


class TopologyType(Enum):
    """Network topology patterns for reservoir initialization."""
    RANDOM_SPARSE = "random_sparse"  # Random sparse connections
    SMALL_WORLD = "small_world"  # Small-world network (Watts-Strogatz)
    SCALE_FREE = "scale_free"  # Scale-free network (Barabási-Albert)
    RING = "ring"  # Ring topology with local connections
    GRID = "grid"  # 2D grid topology
    FULLY_CONNECTED = "fully_connected"  # Dense connections
    CLUSTERED = "clustered"  # Modular cluster structure


class ReadoutType(Enum):
    """Types of readout/output layers."""
    LINEAR = "linear"  # Standard linear readout (ridge regression)
    RIDGE = "ridge"  # Ridge regression with regularization
    ELASTIC_NET = "elastic_net"  # Elastic net regularization
    SVM = "svm"  # Support Vector Machine readout
    MLP = "mlp"  # Multi-layer perceptron readout
    POPULATION = "population"  # Population vector decoding
    LSQR = "lsqr"  # Least squares solver for large systems


class NoiseType(Enum):
    """Types of noise injection for reservoir dynamics."""
    NONE = "none"  # No noise
    GAUSSIAN = "gaussian"  # Additive Gaussian noise
    UNIFORM = "uniform"  # Additive uniform noise
    STATE_DEPENDENT = "state_dependent"  # Multiplicative state-dependent noise
    INPUT_NOISE = "input_noise"  # Noise added to inputs only
    RESERVOIR_NOISE = "reservoir_noise"  # Noise added to reservoir states
    DROPOUT = "dropout"  # Random neuron dropout


class FeedbackMode(Enum):
    """Output feedback modes for ESN."""
    NONE = "none"  # No output feedback
    DIRECT = "direct"  # Direct output-to-input feedback
    RESERVOIR = "reservoir"  # Feedback to reservoir states
    MIXED = "mixed"  # Both input and reservoir feedback
    TEACHER_FORCING = "teacher_forcing"  # Use target as feedback during training


class InitializationMethod(Enum):
    """Reservoir weight initialization methods."""
    RANDOM_NORMAL = "random_normal"  # Gaussian random weights
    RANDOM_UNIFORM = "random_uniform"  # Uniform random weights
    XAVIER = "xavier"  # Xavier/Glorot initialization
    HE = "he"  # He initialization
    ORTHOGONAL = "orthogonal"  # Orthogonal matrix initialization
    SPARSE_RANDOM = "sparse_random"  # Sparse random initialization
    CUSTOM = "custom"  # User-defined initialization


class TrainingMethod(Enum):
    """Training algorithms for reservoir computing."""
    RIDGE_REGRESSION = "ridge"  # Standard ridge regression
    ORDINARY_LEAST_SQUARES = "ols"  # Ordinary least squares
    LASSO = "lasso"  # L1 regularization
    ELASTIC_NET = "elastic_net"  # L1 + L2 regularization  
    SVD_PSEUDOINVERSE = "svd"  # SVD-based pseudoinverse
    RECURSIVE_LEAST_SQUARES = "rls"  # Online RLS
    FORCE_LEARNING = "force"  # FORCE learning algorithm


class OptimizationObjective(Enum):
    """Optimization objectives for hyperparameter tuning."""
    MSE = "mse"  # Mean squared error
    MAE = "mae"  # Mean absolute error
    R2_SCORE = "r2"  # R-squared coefficient
    ACCURACY = "accuracy"  # Classification accuracy
    F1_SCORE = "f1"  # F1 score for classification
    MEMORY_CAPACITY = "memory_capacity"  # Reservoir memory capacity
    SEPARATION_PROPERTY = "separation"  # Class separation measure


# ============================================================================
# CONFIGURATION CLASSES
# ============================================================================

@dataclass
class ESNConfig:
    """
    Comprehensive configuration for Echo State Networks.
    
    Controls all aspects of ESN architecture, dynamics, and training
    based on Jaeger (2001) theoretical foundations.
    
    Parameters
    ----------
    Architecture Parameters:
        n_reservoir : int
            Number of reservoir neurons
        spectral_radius : float  
            Spectral radius of reservoir matrix (< 1 for ESP)
        input_scaling : float
            Input weight scaling factor
        sparsity : float
            Connection density in reservoir (0-1)
            
    Dynamics Parameters:
        activation : ActivationFunction
            Nonlinear activation function
        leak_rate : float
            Leaky integration parameter α ∈ (0,1]
        noise_type : NoiseType
            Type of noise injection
        noise_level : float
            Noise strength parameter
            
    Training Parameters:
        training_method : TrainingMethod
            Readout training algorithm
        regularization : float
            Regularization strength  
        wash_out : int
            Initial transient steps to discard
    """
    
    # ========================================================================
    # Architecture Parameters  
    # ========================================================================
    n_reservoir: int = 100
    """Number of reservoir neurons (typical range: 50-500)"""
    
    spectral_radius: float = 0.95
    """Spectral radius of reservoir matrix (must be < 1.0 for ESP)"""
    
    input_scaling: float = 1.0
    """Input weight scaling factor (typical range: 0.1-10.0)"""
    
    sparsity: float = 0.1
    """Connection density in reservoir (0.05-0.2 typical)"""
    
    topology: TopologyType = TopologyType.RANDOM_SPARSE
    """Network topology structure"""
    
    initialization: InitializationMethod = InitializationMethod.RANDOM_NORMAL
    """Weight initialization method"""
    
    # ========================================================================
    # Dynamics Parameters
    # ========================================================================
    activation: ActivationFunction = ActivationFunction.TANH
    """Reservoir activation function"""
    
    leak_rate: float = 1.0
    """Leaky integration rate α (1.0 = no leakage, 0.1 = strong leakage)"""
    
    noise_type: NoiseType = NoiseType.NONE
    """Type of noise injection"""
    
    noise_level: float = 0.0
    """Noise strength (standard deviation for Gaussian)"""
    
    # ========================================================================
    # Feedback Configuration
    # ========================================================================
    feedback_mode: FeedbackMode = FeedbackMode.NONE
    """Output feedback configuration"""
    
    feedback_scaling: float = 1.0
    """Feedback weight scaling factor"""
    
    # ========================================================================
    # Training Parameters
    # ========================================================================
    training_method: TrainingMethod = TrainingMethod.RIDGE_REGRESSION
    """Readout training algorithm"""
    
    regularization: float = 1e-6
    """Regularization parameter (Ridge: L2, Lasso: L1)"""
    
    readout_type: ReadoutType = ReadoutType.LINEAR
    """Type of readout layer"""
    
    wash_out: int = 100
    """Number of initial transient steps to discard"""
    
    include_bias: bool = True
    """Whether to include bias term in readout"""
    
    include_inputs: bool = True
    """Whether to include direct input-output connections"""
    
    # ========================================================================
    # Advanced Options
    # ========================================================================
    random_state: Optional[int] = None
    """Random seed for reproducibility"""
    
    dtype: str = "float64"
    """Numerical precision ('float32' or 'float64')"""
    
    parallel: bool = False
    """Whether to use parallel processing"""
    
    verbose: bool = True
    """Whether to print training progress"""
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.n_reservoir <= 0:
            raise ValueError(f"n_reservoir must be positive, got {self.n_reservoir}")
        if not 0 < self.spectral_radius <= 2.0:
            raise ValueError(f"spectral_radius should be in (0, 2], got {self.spectral_radius}")
        if self.spectral_radius >= 1.0:
            import warnings
            warnings.warn(f"spectral_radius >= 1.0 ({self.spectral_radius}) may violate Echo State Property")
        if not 0 < self.leak_rate <= 1.0:
            raise ValueError(f"leak_rate must be in (0, 1], got {self.leak_rate}")
        if not 0.0 <= self.sparsity <= 1.0:
            raise ValueError(f"sparsity must be in [0, 1], got {self.sparsity}")
        if self.regularization < 0:
            raise ValueError(f"regularization must be non-negative, got {self.regularization}")


@dataclass  
class DeepESNConfig(ESNConfig):
    """
    Configuration for Deep Echo State Networks.
    
    Extends ESN to multiple hierarchical reservoir layers
    with different timescales and dynamics.
    """
    
    layer_sizes: List[int] = field(default_factory=lambda: [100, 50, 25])
    """Sizes of successive reservoir layers"""
    
    spectral_radii: Optional[List[float]] = None
    """Spectral radius for each layer (None for automatic)"""
    
    leak_rates: Optional[List[float]] = None
    """Leak rate for each layer (None for automatic)"""
    
    layer_connectivity: str = "feedforward"
    """Inter-layer connectivity ('feedforward', 'skip', 'recurrent')"""
    
    def __post_init__(self):
        """Set up multi-layer parameters."""
        super().__post_init__()
        
        n_layers = len(self.layer_sizes)
        if n_layers < 2:
            raise ValueError("Deep ESN requires at least 2 layers")
            
        # Set default spectral radii (decreasing with depth)
        if self.spectral_radii is None:
            self.spectral_radii = [self.spectral_radius - 0.1*i for i in range(n_layers)]
            self.spectral_radii = [max(0.1, sr) for sr in self.spectral_radii]
            
        # Set default leak rates (increasing with depth for longer timescales)
        if self.leak_rates is None:
            self.leak_rates = [self.leak_rate - 0.2*i for i in range(n_layers)]
            self.leak_rates = [max(0.1, lr) for lr in self.leak_rates]
            
        # Override main config with first layer
        self.n_reservoir = self.layer_sizes[0]
        
        if len(self.spectral_radii) != n_layers:
            raise ValueError("spectral_radii length must match layer_sizes")
        if len(self.leak_rates) != n_layers:
            raise ValueError("leak_rates length must match layer_sizes")


@dataclass
class OnlineESNConfig(ESNConfig):
    """
    Configuration for Online Echo State Networks.
    
    Specialized for online/streaming learning scenarios with
    recursive least squares adaptation.
    """
    
    # Override default training method
    training_method: TrainingMethod = TrainingMethod.RECURSIVE_LEAST_SQUARES
    
    # Online learning parameters
    forgetting_factor: float = 0.999
    """RLS forgetting factor (0.9-0.9999 typical)"""
    
    adaptation_rate: float = 0.01
    """Online adaptation learning rate"""
    
    buffer_size: int = 1000
    """Size of replay buffer for online learning"""
    
    update_frequency: int = 1
    """Frequency of weight updates (every N samples)"""
    
    def __post_init__(self):
        """Validate online learning parameters."""
        super().__post_init__()
        
        if not 0.5 < self.forgetting_factor < 1.0:
            raise ValueError(f"forgetting_factor should be in (0.5, 1.0), got {self.forgetting_factor}")
        if not 0.001 <= self.adaptation_rate <= 0.1:
            raise ValueError(f"adaptation_rate should be in [0.001, 0.1], got {self.adaptation_rate}")


@dataclass
class OptimizationConfig:
    """
    Configuration for hyperparameter optimization of reservoirs.
    
    Controls automated search over ESN hyperparameter space
    using cross-validation and advanced optimization algorithms.
    """
    
    # ========================================================================
    # Search Space Definition
    # ========================================================================
    param_ranges: Dict[str, Union[List, Tuple]] = field(default_factory=lambda: {
        'n_reservoir': [50, 100, 200, 400],
        'spectral_radius': (0.1, 1.5),
        'input_scaling': (0.1, 10.0),
        'leak_rate': (0.1, 1.0),
        'regularization': (1e-8, 1e-2),
        'sparsity': [0.01, 0.05, 0.1, 0.2, 0.5]
    })
    """Parameter search ranges (list for discrete, tuple for continuous)"""
    
    # ========================================================================
    # Optimization Strategy
    # ========================================================================
    method: str = "grid_search"
    """Optimization method ('grid_search', 'random_search', 'bayesian')"""
    
    n_trials: int = 100
    """Number of optimization trials"""
    
    cv_folds: int = 5
    """Number of cross-validation folds"""
    
    objective: OptimizationObjective = OptimizationObjective.R2_SCORE
    """Optimization objective to maximize/minimize"""
    
    # ========================================================================
    # Search Control
    # ========================================================================
    early_stopping: bool = True
    """Whether to use early stopping"""
    
    patience: int = 10
    """Early stopping patience"""
    
    min_improvement: float = 1e-4
    """Minimum improvement threshold"""
    
    # ========================================================================
    # Parallel Processing
    # ========================================================================
    n_jobs: int = -1
    """Number of parallel jobs (-1 for all cores)"""
    
    verbose: bool = True
    """Whether to print optimization progress"""
    
    # ========================================================================
    # Advanced Options
    # ========================================================================
    save_intermediate: bool = False
    """Whether to save intermediate results"""
    
    random_state: Optional[int] = None
    """Random seed for optimization"""


@dataclass  
class TaskConfig:
    """
    Task-specific configuration presets for common applications.
    
    Provides optimized ESN configurations for different problem types
    based on empirical research and best practices.
    """
    
    task_type: str = "regression"
    """Type of task ('regression', 'classification', 'time_series', 'generation')"""
    
    complexity: str = "medium"
    """Problem complexity ('simple', 'medium', 'complex')"""
    
    sequence_length: Optional[int] = None
    """Typical sequence length for the task"""
    
    n_features: Optional[int] = None
    """Number of input features"""
    
    n_outputs: Optional[int] = None
    """Number of output dimensions"""
    
    def get_recommended_config(self) -> ESNConfig:
        """Get task-optimized ESN configuration."""
        
        # Base configurations by complexity
        base_configs = {
            'simple': {
                'n_reservoir': 50,
                'spectral_radius': 0.9,
                'sparsity': 0.2,
                'regularization': 1e-4
            },
            'medium': {
                'n_reservoir': 100,
                'spectral_radius': 0.95,
                'sparsity': 0.1,
                'regularization': 1e-6
            },
            'complex': {
                'n_reservoir': 200,
                'spectral_radius': 0.99,
                'sparsity': 0.05,
                'regularization': 1e-8
            }
        }
        
        # Task-specific modifications
        task_configs = {
            'regression': {
                'training_method': TrainingMethod.RIDGE_REGRESSION,
                'activation': ActivationFunction.TANH,
                'leak_rate': 1.0
            },
            'classification': {
                'training_method': TrainingMethod.RIDGE_REGRESSION,
                'activation': ActivationFunction.TANH,
                'leak_rate': 0.8,
                'regularization': 1e-3
            },
            'time_series': {
                'training_method': TrainingMethod.RIDGE_REGRESSION,
                'activation': ActivationFunction.TANH,
                'leak_rate': 0.9,
                'feedback_mode': FeedbackMode.DIRECT
            },
            'generation': {
                'training_method': TrainingMethod.RIDGE_REGRESSION,
                'activation': ActivationFunction.TANH,
                'leak_rate': 0.95,
                'feedback_mode': FeedbackMode.DIRECT,
                'spectral_radius': 0.98  # Close to edge for rich dynamics
            }
        }
        
        # Merge configurations
        config_dict = base_configs[self.complexity].copy()
        config_dict.update(task_configs[self.task_type])
        
        # Sequence length adaptations
        if self.sequence_length is not None:
            if self.sequence_length > 1000:
                config_dict['leak_rate'] = min(0.8, config_dict['leak_rate'])
            elif self.sequence_length < 50:
                config_dict['leak_rate'] = min(1.0, config_dict['leak_rate'] * 1.1)
                
        # Feature dimension adaptations
        if self.n_features is not None:
            if self.n_features > 50:
                config_dict['input_scaling'] = 0.5
            elif self.n_features < 5:
                config_dict['input_scaling'] = 2.0
                
        return ESNConfig(**config_dict)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_esn_config(task_type: str = "regression",
                     complexity: str = "medium", 
                     **kwargs) -> ESNConfig:
    """
    Create ESN configuration with task-optimized defaults.
    
    Parameters
    ----------
    task_type : str
        Type of task ('regression', 'classification', 'time_series', 'generation')
    complexity : str
        Problem complexity ('simple', 'medium', 'complex') 
    **kwargs
        Override default parameters
        
    Returns
    -------
    ESNConfig
        Configured ESN parameters
    """
    task_config = TaskConfig(task_type=task_type, complexity=complexity)
    config = task_config.get_recommended_config()
    
    # Override with user parameters
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown config parameter: {key}")
            
    return config


def create_deep_esn_config(layer_sizes: List[int],
                          task_type: str = "regression",
                          **kwargs) -> DeepESNConfig:
    """
    Create Deep ESN configuration.
    
    Parameters
    ----------
    layer_sizes : List[int]
        Sizes of reservoir layers
    task_type : str
        Type of task
    **kwargs
        Additional configuration parameters
        
    Returns
    -------
    DeepESNConfig
        Deep ESN configuration
    """
    base_config = create_esn_config(task_type=task_type, **kwargs)
    
    # Convert to DeepESNConfig
    deep_config = DeepESNConfig(
        layer_sizes=layer_sizes,
        **{k: v for k, v in base_config.__dict__.items() 
           if k not in ['n_reservoir']}  # Exclude single layer param
    )
    
    return deep_config


def create_online_esn_config(task_type: str = "regression",
                           forgetting_factor: float = 0.999,
                           **kwargs) -> OnlineESNConfig:
    """
    Create Online ESN configuration.
    
    Parameters
    ----------
    task_type : str
        Type of task
    forgetting_factor : float
        RLS forgetting factor
    **kwargs
        Additional configuration parameters
        
    Returns
    -------
    OnlineESNConfig
        Online ESN configuration
    """
    base_config = create_esn_config(task_type=task_type, **kwargs)
    
    online_config = OnlineESNConfig(
        forgetting_factor=forgetting_factor,
        **base_config.__dict__
    )
    
    return online_config


def create_optimization_config(param_ranges: Optional[Dict] = None,
                             method: str = "grid_search",
                             n_trials: int = 100,
                             **kwargs) -> OptimizationConfig:
    """
    Create hyperparameter optimization configuration.
    
    Parameters
    ----------
    param_ranges : Dict, optional
        Parameter search ranges
    method : str
        Optimization method
    n_trials : int
        Number of trials
    **kwargs
        Additional optimization parameters
        
    Returns
    -------
    OptimizationConfig
        Optimization configuration
    """
    config = OptimizationConfig(
        method=method,
        n_trials=n_trials,
        **kwargs
    )
    
    if param_ranges is not None:
        config.param_ranges = param_ranges
        
    return config


# ============================================================================
# PRESET CONFIGURATIONS
# ============================================================================

# Task-specific presets
ESN_PRESETS = {
    "mackey_glass": ESNConfig(
        n_reservoir=100,
        spectral_radius=0.95,
        input_scaling=1.0,
        leak_rate=0.9,
        regularization=1e-6,
        sparsity=0.1
    ),
    
    "narma": ESNConfig(
        n_reservoir=200,
        spectral_radius=0.98,
        input_scaling=0.5,
        leak_rate=0.8,
        regularization=1e-8,
        sparsity=0.05
    ),
    
    "speech_recognition": ESNConfig(
        n_reservoir=400,
        spectral_radius=0.99,
        input_scaling=2.0,
        leak_rate=0.7,
        activation=ActivationFunction.TANH,
        regularization=1e-4,
        sparsity=0.02
    ),
    
    "financial_prediction": ESNConfig(
        n_reservoir=150,
        spectral_radius=0.95,
        input_scaling=1.0,
        leak_rate=0.9,
        noise_type=NoiseType.GAUSSIAN,
        noise_level=0.001,
        regularization=1e-5
    ),
    
    "robot_control": ESNConfig(
        n_reservoir=100,
        spectral_radius=0.9,
        input_scaling=3.0,
        leak_rate=1.0,
        feedback_mode=FeedbackMode.DIRECT,
        regularization=1e-6
    )
}


def get_preset_config(preset_name: str) -> ESNConfig:
    """
    Get a preset ESN configuration.
    
    Parameters
    ----------
    preset_name : str
        Name of the preset configuration
        
    Returns
    -------
    ESNConfig
        Preset configuration
        
    Available presets:
    - 'mackey_glass': Chaotic time series prediction
    - 'narma': NARMA benchmark task  
    - 'speech_recognition': Speech/audio processing
    - 'financial_prediction': Financial time series
    - 'robot_control': Control applications
    """
    if preset_name not in ESN_PRESETS:
        available = list(ESN_PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
        
    return ESN_PRESETS[preset_name]


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_config(config: ESNConfig) -> List[str]:
    """
    Validate ESN configuration and return warnings/recommendations.
    
    Parameters
    ----------
    config : ESNConfig
        Configuration to validate
        
    Returns
    -------
    List[str]
        List of warnings and recommendations
    """
    warnings_list = []
    
    # Echo State Property validation
    if config.spectral_radius >= 1.0:
        warnings_list.append(
            f"Spectral radius {config.spectral_radius} >= 1.0 may violate Echo State Property. "
            f"Consider reducing to < 1.0 for stable dynamics."
        )
    
    # Reservoir size recommendations  
    if config.n_reservoir < 50:
        warnings_list.append(
            f"Small reservoir size ({config.n_reservoir}) may limit memory capacity. "
            f"Consider increasing to 100+ for complex tasks."
        )
    elif config.n_reservoir > 1000:
        warnings_list.append(
            f"Large reservoir size ({config.n_reservoir}) may cause overfitting. "
            f"Consider regularization or reducing size."
        )
    
    # Sparsity recommendations
    if config.sparsity > 0.5:
        warnings_list.append(
            f"High sparsity ({config.sparsity}) may reduce reservoir richness. "
            f"Typical values are 0.01-0.2."
        )
    elif config.sparsity < 0.01:
        warnings_list.append(
            f"Very low sparsity ({config.sparsity}) creates nearly fully connected reservoir. "
            f"This may cause computational issues for large reservoirs."
        )
    
    # Regularization recommendations
    if config.regularization > 1e-2:
        warnings_list.append(
            f"High regularization ({config.regularization}) may cause underfitting. "
            f"Consider reducing or using cross-validation to optimize."
        )
    elif config.regularization < 1e-10:
        warnings_list.append(
            f"Very low regularization ({config.regularization}) may cause overfitting. "
            f"Consider increasing slightly."
        )
    
    # Leak rate recommendations
    if config.leak_rate < 0.1:
        warnings_list.append(
            f"Very low leak rate ({config.leak_rate}) creates slow dynamics. "
            f"Ensure this matches your task's temporal requirements."
        )
    
    # Activation function recommendations
    if config.activation == ActivationFunction.RELU and config.spectral_radius > 0.9:
        warnings_list.append(
            f"ReLU activation with high spectral radius ({config.spectral_radius}) "
            f"may cause exploding dynamics. Consider reducing spectral radius."
        )
    
    return warnings_list


def optimize_config_for_task(X: np.ndarray, y: np.ndarray,
                           base_config: Optional[ESNConfig] = None,
                           optimization_config: Optional[OptimizationConfig] = None) -> ESNConfig:
    """
    Automatically optimize ESN configuration for given task data.
    
    Parameters
    ----------
    X : np.ndarray
        Input data
    y : np.ndarray
        Target data
    base_config : ESNConfig, optional
        Base configuration to optimize from
    optimization_config : OptimizationConfig, optional
        Optimization settings
        
    Returns
    -------
    ESNConfig
        Optimized configuration
    """
    from .core import optimize_esn_hyperparameters
    
    if base_config is None:
        base_config = create_esn_config()
        
    if optimization_config is None:
        optimization_config = create_optimization_config()
        
    # Run hyperparameter optimization
    result = optimize_esn_hyperparameters(
        X, y,
        param_space=optimization_config.param_ranges,
        n_trials=optimization_config.n_trials,
        cv_folds=optimization_config.cv_folds
    )
    
    # Create optimized config
    optimized_params = result['best_params']
    optimized_config = ESNConfig(**{**base_config.__dict__, **optimized_params})
    
    return optimized_config