"""
🏗️ Reservoir Computing - Configuration Enumerations Module  
=========================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger, H. (2001) "The Echo State Approach to Analysing and Training Recurrent Neural Networks"

🎯 MODULE PURPOSE:
=================
All enumeration types for reservoir computing configuration options, providing
type-safe configuration choices with clear research-based documentation.

🔤 ENUM CATEGORIES:
==================
• Reservoir architectures and types 
• Activation functions with theoretical backing
• Network topologies for initialization
• Readout layer configurations
• Noise injection strategies
• Feedback mechanisms
• Weight initialization methods
• Training algorithms
• Optimization objectives

🎓 RESEARCH FOUNDATION:
======================
All enums based on established research practices:
- Jaeger (2001): ESN foundations and activation functions
- Maass (2002): LSM architectures and dynamics
- Watts & Strogatz (1998): Small-world network topologies
- Barabási & Albert (1999): Scale-free network structures
- Modern reservoir computing best practices

This module contains all configuration enumerations, split from the
859-line monolith for specialized type definitions.
"""

from enum import Enum


class ReservoirType(Enum):
    """
    Types of reservoir architectures with research foundations.
    
    Based on:
    - Jaeger (2001): Echo State Networks - original ESN formulation
    - Maass et al. (2002): Liquid State Machines - biological inspiration
    - Modern developments: Deep and online variants
    """
    ECHO_STATE_NETWORK = "esn"  # Standard ESN (Jaeger 2001)
    LIQUID_STATE_MACHINE = "lsm"  # LSM (Maass 2002)
    DEEP_RESERVOIR = "deep"  # Multi-layer reservoirs
    ONLINE_ESN = "online"  # Online learning ESN
    MODULAR_ESN = "modular"  # Modular architecture


class ActivationFunction(Enum):
    """
    Reservoir activation functions with theoretical backing.
    
    Research Context:
    - TANH: Standard choice with bounded output [-1, 1], good dynamics
    - SIGMOID: Logistic function [0, 1], alternative to tanh
    - RELU: Modern choice, can cause issues with high spectral radius
    - LEAKY_RELU: Addresses ReLU's dead neuron problem
    - SWISH: Modern smooth activation x * sigmoid(x)
    """
    TANH = "tanh"  # Standard hyperbolic tangent [-1, 1]
    SIGMOID = "sigmoid"  # Logistic sigmoid [0, 1]
    RELU = "relu"  # Rectified linear unit [0, ∞]
    LEAKY_RELU = "leaky_relu"  # Leaky ReLU with small negative slope
    SWISH = "swish"  # Swish activation x * sigmoid(x)
    LINEAR = "linear"  # Linear activation (identity)
    SOFTPLUS = "softplus"  # Smooth approximation to ReLU
    CUSTOM = "custom"  # User-defined function


class TopologyType(Enum):
    """
    Network topology patterns for reservoir initialization.
    
    Research Foundation:
    - RANDOM_SPARSE: Standard approach in most ESN literature
    - SMALL_WORLD: Watts-Strogatz (1998) - balance of local/global connectivity
    - SCALE_FREE: Barabási-Albert (1999) - hub-based connectivity
    - RING: Local connections only, good for temporal tasks
    - GRID: Spatially organized, useful for spatial-temporal processing
    """
    RANDOM_SPARSE = "random_sparse"  # Random sparse connections
    SMALL_WORLD = "small_world"  # Small-world network (Watts-Strogatz)
    SCALE_FREE = "scale_free"  # Scale-free network (Barabási-Albert)
    RING = "ring"  # Ring topology with local connections
    GRID = "grid"  # 2D grid topology
    FULLY_CONNECTED = "fully_connected"  # Dense connections
    CLUSTERED = "clustered"  # Modular cluster structure


class ReadoutType(Enum):
    """
    Types of readout/output layers for different learning scenarios.
    
    Research Context:
    - LINEAR/RIDGE: Standard approach in ESN literature (Jaeger 2001)
    - ELASTIC_NET: Combines L1/L2 regularization for sparse solutions
    - SVM: Support vector learning for classification tasks
    - MLP: Non-linear readout for complex mappings
    - POPULATION: Biological inspiration from neural population coding
    """
    LINEAR = "linear"  # Standard linear readout (ridge regression)
    RIDGE = "ridge"  # Ridge regression with regularization
    ELASTIC_NET = "elastic_net"  # Elastic net regularization
    SVM = "svm"  # Support Vector Machine readout
    MLP = "mlp"  # Multi-layer perceptron readout
    POPULATION = "population"  # Population vector decoding
    LSQR = "lsqr"  # Least squares solver for large systems


class NoiseType(Enum):
    """
    Types of noise injection for reservoir dynamics.
    
    Research Foundation:
    - Noise injection improves robustness and prevents overfitting
    - Different types serve different purposes in reservoir dynamics
    - Based on biological neural noise and regularization theory
    """
    NONE = "none"  # No noise
    GAUSSIAN = "gaussian"  # Additive Gaussian noise
    UNIFORM = "uniform"  # Additive uniform noise
    STATE_DEPENDENT = "state_dependent"  # Multiplicative state-dependent noise
    INPUT_NOISE = "input_noise"  # Noise added to inputs only
    RESERVOIR_NOISE = "reservoir_noise"  # Noise added to reservoir states
    DROPOUT = "dropout"  # Random neuron dropout


class FeedbackMode(Enum):
    """
    Output feedback modes for ESN with different learning dynamics.
    
    Research Context:
    - Feedback connections enable autonomous dynamics and generation
    - Different modes suitable for different task types
    - Teacher forcing prevents error accumulation during training
    """
    NONE = "none"  # No output feedback
    DIRECT = "direct"  # Direct output-to-input feedback
    RESERVOIR = "reservoir"  # Feedback to reservoir states
    MIXED = "mixed"  # Both input and reservoir feedback
    TEACHER_FORCING = "teacher_forcing"  # Use target as feedback during training


class InitializationMethod(Enum):
    """
    Reservoir weight initialization methods with theoretical backing.
    
    Research Foundation:
    - Different initialization schemes affect dynamics and performance
    - Spectral properties crucial for Echo State Property
    - Based on random matrix theory and neural network initialization
    """
    RANDOM_NORMAL = "random_normal"  # Gaussian random weights
    RANDOM_UNIFORM = "random_uniform"  # Uniform random weights
    SPECTRAL_RADIUS = "spectral_radius"  # Initialize then scale spectral radius
    BALANCED = "balanced"  # Balanced positive/negative weights
    SPARSE_RANDOM = "sparse_random"  # Sparse random initialization
    ORTHOGONAL = "orthogonal"  # Orthogonal matrix initialization
    XAVIER = "xavier"  # Xavier/Glorot initialization
    HE = "he"  # He initialization for ReLU networks


class TrainingMethod(Enum):
    """
    Training methods for reservoir computing systems.
    
    Research Context:
    - Batch vs online learning trade-offs
    - Different regularization strategies
    - Adaptive methods for non-stationary environments
    """
    BATCH = "batch"  # Standard batch training
    ONLINE = "online"  # Online/incremental learning
    MINI_BATCH = "mini_batch"  # Mini-batch learning
    FORCE = "force"  # First-Order Reduced and Controlled Error (FORCE)
    RLS = "rls"  # Recursive Least Squares
    ADAPTIVE = "adaptive"  # Adaptive learning rate methods


class OptimizationObjective(Enum):
    """
    Optimization objectives for hyperparameter tuning.
    
    Research Foundation:
    - Different objectives suited for different task types
    - Multi-objective optimization for complex trade-offs
    - Based on machine learning evaluation metrics
    """
    MSE = "mse"  # Mean Squared Error (regression)
    MAE = "mae"  # Mean Absolute Error (robust regression)
    ACCURACY = "accuracy"  # Classification accuracy
    F1_SCORE = "f1_score"  # F1 score for imbalanced classification
    MEMORY_CAPACITY = "memory_capacity"  # Linear memory capacity
    NONLINEAR_CAPACITY = "nonlinear_capacity"  # Nonlinear processing capacity
    STABILITY = "stability"  # Dynamic stability measures
    MULTI_OBJECTIVE = "multi_objective"  # Multiple objectives combined


# Export all enums for easy access
__all__ = [
    'ReservoirType',
    'ActivationFunction', 
    'TopologyType',
    'ReadoutType',
    'NoiseType',
    'FeedbackMode',
    'InitializationMethod',
    'TrainingMethod',
    'OptimizationObjective'
]


if __name__ == "__main__":
    print("🏗️ Reservoir Computing - Configuration Enums")
    print("=" * 50)
    print("📊 ENUM SUMMARY:")
    print(f"  • ReservoirType: {len(ReservoirType)} architectures")
    print(f"  • ActivationFunction: {len(ActivationFunction)} activation types") 
    print(f"  • TopologyType: {len(TopologyType)} network topologies")
    print(f"  • ReadoutType: {len(ReadoutType)} readout configurations")
    print(f"  • NoiseType: {len(NoiseType)} noise strategies")
    print(f"  • FeedbackMode: {len(FeedbackMode)} feedback modes")
    print(f"  • InitializationMethod: {len(InitializationMethod)} init methods")
    print(f"  • TrainingMethod: {len(TrainingMethod)} training approaches")
    print(f"  • OptimizationObjective: {len(OptimizationObjective)} objectives")
    print("")
    print("✅ All configuration enums loaded successfully!")
    print("🔬 Research-based type-safe configuration system!")