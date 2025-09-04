"""
Echo State Network - Main Module File
Based on: Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"

This module provides the main imports and functions for the Echo State Network implementation.
Uses modular components from esn_modules for the actual implementation.
"""

# Import core classes from modular components
from .esn_modules import (
    EchoStateNetwork,
    create_echo_state_network,
    ReservoirInitializationMixin,
    EspValidationMixin,
    StateUpdatesMixin,
    TrainingMethodsMixin,
    PredictionGenerationMixin,
    TopologyManagementMixin,
    ConfigurationOptimizationMixin,
    VisualizationMixin
)

# Create aliases for backward compatibility
EchoStatePropertyValidator = EspValidationMixin
StructuredReservoirTopologies = TopologyManagementMixin
JaegerBenchmarkTasks = ConfigurationOptimizationMixin
OutputFeedbackESN = EchoStateNetwork  # Same class with output_feedback=True
TeacherForcingTrainer = TrainingMethodsMixin
OnlineLearningESN = EchoStateNetwork  # Same class with online capabilities

def optimize_spectral_radius(X_train, y_train, esn=None, radius_range=(0.1, 1.5), n_points=15, cv_folds=3):
    """
    Optimize spectral radius using grid search
    
    Wrapper function that creates an ESN if not provided and runs optimization.
    
    Args:
        X_train: Training input data
        y_train: Training target data  
        esn: Optional ESN instance (creates new one if None)
        radius_range: Range of spectral radius values to test
        n_points: Number of points to test in range
        cv_folds: Number of cross-validation folds
        
    Returns:
        Dict with optimization results
    """
    if esn is None:
        esn = EchoStateNetwork(random_seed=42)
        
    return esn.optimize_spectral_radius(X_train, y_train, radius_range, n_points, cv_folds)

def validate_esp(esn, method='fast', **kwargs):
    """
    Validate Echo State Property of an ESN
    
    Args:
        esn: EchoStateNetwork instance
        method: ESP validation method ('fast', 'rigorous', 'convergence', 'lyapunov')
        **kwargs: Additional validation parameters
        
    Returns:
        bool: True if ESP is satisfied
    """
    esn.esp_validation_method = method
    return esn._validate_comprehensive_esp()

def run_benchmark_suite(esn_configs=None, benchmarks=['memory_capacity', 'nonlinear_capacity'], verbose=True):
    """
    Run comprehensive benchmark suite on ESN configurations
    
    Args:
        esn_configs: List of ESN configurations to test
        benchmarks: List of benchmark tasks to run
        verbose: Whether to print detailed results
        
    Returns:
        Dict with benchmark results for each configuration
    """
    # FIXME: Critical issues in benchmark suite implementation
    # Issue 1: No error handling for failed configuration creation
    # Issue 2: Inefficient memory capacity computation - retrains ESN for each delay
    # Issue 3: Silent exception handling hides important failures
    # Issue 4: Fixed parameters (n_samples=1000, delays 1-20) aren't configurable
    # Issue 5: Missing nonlinear_capacity benchmark implementation
    # Issue 6: No statistical validation of benchmark results
    
    if esn_configs is None:
        esn_configs = [
            {'preset': 'fast'},
            {'preset': 'balanced'},
            {'preset': 'accurate'}
        ]
    
    # FIXME: No validation of esn_configs parameter
    # Issue: Could crash if configs contain invalid parameters
    # Solutions:
    # 1. Validate each config dictionary before use
    # 2. Provide informative error messages for invalid configs
    # 3. Add schema validation for expected config structure
    #
    # Example validation:
    # for i, config in enumerate(esn_configs):
    #     if not isinstance(config, dict):
    #         raise TypeError(f"Config {i} must be dictionary, got {type(config)}")
    #     if 'preset' in config and config['preset'] not in ['fast', 'balanced', 'accurate']:
    #         raise ValueError(f"Unknown preset: {config['preset']}")
    
    results = {}
    
    for i, config in enumerate(esn_configs):
        config_name = config.get('name', f'config_{i+1}')
        if verbose:
            print(f"🧪 Running benchmarks for {config_name}...")
        
        # FIXME: No error handling for ESN creation
        # Issue: Could crash if config contains invalid parameters
        # Solutions:
        # 1. Wrap ESN creation in try-except
        # 2. Provide informative error messages
        # 3. Skip invalid configurations with warning
        #
        # Robust ESN creation:
        # try:
        #     if 'preset' in config:
        #         esn = create_echo_state_network(config['preset'], **{k:v for k,v in config.items() if k != 'preset'})
        #     else:
        #         esn = EchoStateNetwork(**config)
        # except Exception as e:
        #     warnings.warn(f"Failed to create ESN for config {config_name}: {e}")
        #     continue
        
        # Create ESN with configuration
        if 'preset' in config:
            esn = create_echo_state_network(config['preset'], **{k:v for k,v in config.items() if k != 'preset'})
        else:
            esn = EchoStateNetwork(**config)
        
        config_results = {}
        
        for benchmark in benchmarks:
            if benchmark == 'memory_capacity':
                # FIXME: Extremely inefficient memory capacity benchmark
                # Issue: Retrains entire ESN for each delay - O(n_delays × training_cost)
                # Solutions:
                # 1. Train ESN once, then test reconstruction for all delays
                # 2. Use proper memory capacity computation from reservoir theory
                # 3. Implement incremental delay testing without retraining
                
                # Simple memory capacity test
                import numpy as np
                # Generate delay line task data
                n_samples = 1000
                delays = range(1, 21)  # Test delays 1-20
                
                # FIXME: Fixed random seed would give reproducible results
                # Issue: Results vary between runs due to random input
                # Solutions:
                # 1. Use fixed random seed for reproducible benchmarks
                # 2. Average results over multiple random seeds
                # 3. Use standardized benchmark datasets
                #
                # Better input generation:
                # np.random.seed(42)  # For reproducible results
                # input_seq = np.random.uniform(-1, 1, (n_samples, 1))
                
                input_seq = np.random.uniform(-1, 1, (n_samples, 1))
                
                memory_scores = []
                for delay in delays:
                    if n_samples > delay:
                        # FIXME: Incorrect delay task implementation
                        # Issue: Using np.roll creates artificial circular delay
                        # Should use proper delay line task: target[t] = input[t-delay]
                        # Solutions:
                        # 1. Implement proper delay line task
                        # 2. Handle boundary conditions correctly
                        # 3. Use standard memory capacity task from literature
                        #
                        # Correct implementation:
                        # target = np.zeros_like(input_seq)
                        # target[delay:] = input_seq[:-delay]
                        
                        target = np.roll(input_seq, delay, axis=0)
                        target[:delay] = 0
                        
                        try:
                            esn.train(input_seq, target, washout=100)
                            pred = esn.predict(input_seq, washout=100)
                            
                            # FIXME: Correlation computation can be unstable
                            # Issue: Can return NaN for constant sequences
                            # Solutions:
                            # 1. Add robust correlation computation
                            # 2. Handle edge cases explicitly
                            # 3. Use R² score as alternative metric
                            
                            # Calculate correlation coefficient
                            correlation = np.corrcoef(target[100:].flatten(), pred[100:].flatten())[0,1]
                            if np.isnan(correlation):
                                correlation = 0.0
                            memory_scores.append(max(0, correlation))
                        except:
                            # FIXME: Silent exception handling hides failures
                            # Issue: Masking training/prediction failures without logging
                            # Solutions:
                            # 1. Log specific exceptions for debugging
                            # 2. Collect failure statistics
                            # 3. Distinguish between different failure modes
                            #
                            # Better exception handling:
                            # except Exception as e:
                            #     if verbose:
                            #         print(f"   Warning: Failed at delay {delay}: {e}")
                            #     memory_scores.append(0.0)
                            memory_scores.append(0.0)
                    else:
                        memory_scores.append(0.0)
                
                # FIXME: Arbitrary threshold 0.1 for effective capacity
                # Issue: Threshold not justified by theory or statistics
                # Solutions:
                # 1. Use statistical significance testing
                # 2. Make threshold configurable
                # 3. Base on noise floor estimation
                
                config_results['memory_capacity'] = {
                    'scores': memory_scores,
                    'total_capacity': sum(memory_scores),
                    'effective_capacity': sum(1 for score in memory_scores if score > 0.1)
                }
                
            # FIXME: Missing nonlinear_capacity benchmark implementation
            # Issue: Benchmark is listed but not implemented
            # Solutions:
            # 1. Implement standard nonlinear benchmark tasks
            # 2. Add NARMA tasks, XOR temporal tasks
            # 3. Provide clear error message for unimplemented benchmarks
            elif benchmark == 'nonlinear_capacity':
                if verbose:
                    print(f"   ⚠️  nonlinear_capacity benchmark not yet implemented")
                config_results['nonlinear_capacity'] = {'status': 'not_implemented'}
                
        results[config_name] = config_results
        
        if verbose:
            print(f"   ✅ {config_name} completed")
    
    return results

# Export main classes and functions
__all__ = [
    'EchoStateNetwork',
    'create_echo_state_network', 
    'EchoStatePropertyValidator',
    'StructuredReservoirTopologies',
    'JaegerBenchmarkTasks', 
    'OutputFeedbackESN',
    'TeacherForcingTrainer',
    'OnlineLearningESN',
    'optimize_spectral_radius',
    'validate_esp',
    'run_benchmark_suite'
]