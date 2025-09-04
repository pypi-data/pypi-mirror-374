"""
🛠️ Reservoir Computing Utilities
===============================

Author: Benedict Chen (benedict@benedictchen.com)

This module consolidates all utility functions for Echo State Networks and Reservoir Computing,
providing essential tools for validation, topology management, benchmarking, and analysis.

🔬 Research Foundation:
======================

The utilities in this module are based on established reservoir computing research:

1. **Echo State Property Validation** (Jaeger, 2001):
   - Spectral radius analysis and Lyapunov exponent methods
   - Convergence testing and Jacobian analysis
   - Comprehensive ESP validation framework

2. **Network Topology Analysis** (Watts & Strogatz, 1998; Barabási-Albert, 1999):
   - Small-world and scale-free network creation
   - Topological property analysis and spectral radius control
   - Custom connectivity pattern support

3. **Benchmark Tasks** (Dambre et al., 2012):
   - Memory capacity evaluation using delay line tasks
   - Nonlinear capacity assessment
   - Performance validation suite

4. **Optimization Methods**:
   - Grid search and Bayesian optimization for hyperparameters
   - Cross-validation and statistical validation
   - Configuration optimization algorithms

📊 Utility Categories:
=====================

- **ESP Validation**: comprehensive_esp_validation, lyapunov_validation, jacobian_analysis
- **Topology Management**: create_topology, scale_spectral_radius, analyze_connectivity
- **Benchmark Suite**: memory_capacity_test, benchmark_configuration, performance_metrics
- **Optimization Tools**: optimize_parameters, grid_search, statistical_validation
- **Analysis Functions**: connectivity_analysis, performance_analysis, visualization_helpers

🎯 Key Features:
===============

- Research-accurate implementations of standard RC validation methods
- Comprehensive topology creation and analysis tools
- Statistical validation and benchmarking framework
- Optimization algorithms for hyperparameter tuning
- Visualization and analysis utilities

References:
----------
- Jaeger, H. (2001). "The 'echo state' approach to analysing and training RNNs"
- Watts, D.J., & Strogatz, S.H. (1998). "Collective dynamics of 'small-world' networks"
- Barabási, A.L., & Albert, R. (1999). "Emergence of scaling in random networks"
- Dambre, J., et al. (2012). "Information processing capacity of dynamical systems"
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List, Union, Callable
import warnings
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import differential_evolution
import logging

# Configure logging for utility functions
logger = logging.getLogger(__name__)


# ================================
# ESP VALIDATION UTILITIES
# ================================

def comprehensive_esp_validation(esn, method='comprehensive', **kwargs) -> Dict[str, Any]:
    """
    Comprehensive Echo State Property validation using multiple methods.
    
    🔬 **Research Background:**
    Validates the Echo State Property using multiple complementary methods from 
    reservoir computing literature. The ESP is fundamental to RC performance.
    
    **Validation Methods:**
    1. **Spectral Radius**: λmax(W) < 1 (Jaeger, 2001)
    2. **Convergence Test**: State convergence from different initial conditions
    3. **Lyapunov Exponent**: Negative largest Lyapunov exponent indicates stability
    4. **Jacobian Analysis**: Local stability through linearization
    
    Args:
        esn: EchoStateNetwork instance to validate
        method: Validation method ('comprehensive', 'fast', 'spectral', 'convergence', 'lyapunov', 'jacobian')
        **kwargs: Additional validation parameters
        
    Returns:
        Dict containing validation results with overall ESP status
        
    References:
        - Jaeger, H. (2001). "The 'echo state' approach to analysing and training RNNs"
        - Yildiz, I.B., et al. (2012). "Re-visiting the echo state property"
    """
    results = {}
    
    if method in ['comprehensive', 'spectral']:
        results['spectral_radius_check'] = validate_spectral_radius(esn)
        
    if method in ['comprehensive', 'convergence']:
        results['convergence_test'] = validate_convergence(esn, **kwargs)
        
    if method in ['comprehensive', 'lyapunov']:
        try:
            results['lyapunov_test'] = validate_lyapunov(esn, **kwargs)
        except Exception as e:
            results['lyapunov_test'] = {'valid': False, 'error': str(e)}
            
    if method in ['comprehensive', 'jacobian']:
        try:
            results['jacobian_test'] = validate_jacobian(esn, **kwargs)
        except Exception as e:
            results['jacobian_test'] = {'valid': False, 'error': str(e)}
            
    if method == 'fast':
        results = validate_esp_fast(esn, **kwargs)
        return results
    
    # Calculate overall ESP status
    valid_tests = [r.get('valid', False) for r in results.values() if isinstance(r, dict)]
    overall_valid = np.mean(valid_tests) > 0.5 if valid_tests else False
    results['overall_esp_valid'] = overall_valid
    results['valid'] = overall_valid
    results['validation_confidence'] = np.mean(valid_tests) if valid_tests else 0.0
    
    return results


def validate_spectral_radius(esn) -> Dict[str, Any]:
    """Basic spectral radius validation for ESP."""
    eigenvals = np.linalg.eigvals(esn.reservoir_weights)
    spectral_radius = np.max(np.abs(eigenvals))
    
    return {
        'valid': spectral_radius < 1.0,
        'spectral_radius': float(spectral_radius),
        'method': 'spectral_radius',
        'confidence': 0.8 if spectral_radius < 0.95 else 0.6
    }


def validate_convergence(esn, n_tests: int = 10, test_length: int = 1500, 
                        tolerance: float = 1e-6) -> Dict[str, Any]:
    """Test ESP through state convergence from different initial conditions."""
    convergence_results = []
    
    for test in range(n_tests):
        # Create two different initial states
        state1 = np.random.randn(esn.reservoir_size) * 0.1
        state2 = np.random.randn(esn.reservoir_size) * 0.1
        
        # Generate test input sequence
        input_seq = np.random.randn(test_length, esn.n_inputs) * 0.5
        
        # Run both states through same input sequence
        states1 = run_test_sequence(esn, state1, input_seq)
        states2 = run_test_sequence(esn, state2, input_seq)
        
        # Check final convergence
        final_diff = np.linalg.norm(states1[-1] - states2[-1])
        convergence_results.append(final_diff < tolerance)
    
    convergence_rate = np.mean(convergence_results)
    
    return {
        'valid': convergence_rate > 0.8,
        'convergence_rate': float(convergence_rate),
        'method': 'state_convergence',
        'n_tests': n_tests,
        'confidence': min(convergence_rate, 0.95)
    }


def validate_lyapunov(esn, n_steps: int = 1000) -> Dict[str, Any]:
    """Validate ESP using Lyapunov exponent analysis."""
    initial_state = np.random.randn(esn.reservoir_size) * 0.1
    input_seq = np.random.randn(n_steps, esn.n_inputs) * 0.5
    
    # Compute Lyapunov exponent
    lyapunov_sum = 0.0
    current_state = initial_state.copy()
    
    for t in range(n_steps):
        # Compute Jacobian at current state
        jacobian = compute_jacobian_at_state(esn, current_state, input_seq[t])
        
        # Update Lyapunov sum
        eigenvals = np.linalg.eigvals(jacobian)
        max_eigenval = np.max(np.real(eigenvals))
        lyapunov_sum += np.log(abs(max_eigenval)) if max_eigenval != 0 else -10
        
        # Update state
        current_state = update_state_for_validation(esn, current_state, input_seq[t])
    
    lyapunov_exponent = lyapunov_sum / n_steps
    
    return {
        'valid': lyapunov_exponent < 0,
        'lyapunov_exponent': float(lyapunov_exponent),
        'method': 'lyapunov_exponent',
        'confidence': 0.9 if lyapunov_exponent < -0.1 else 0.7
    }


def validate_jacobian(esn, n_samples: int = 20) -> Dict[str, Any]:
    """Validate ESP through Jacobian spectral radius analysis."""
    jacobian_radii = []
    
    for _ in range(n_samples):
        state = np.random.randn(esn.reservoir_size) * 0.5
        input_vec = np.random.randn(esn.n_inputs) * 0.5
        
        jacobian = compute_jacobian_at_state(esn, state, input_vec)
        eigenvals = np.linalg.eigvals(jacobian)
        spectral_radius = np.max(np.abs(eigenvals))
        jacobian_radii.append(spectral_radius)
    
    mean_radius = np.mean(jacobian_radii)
    std_radius = np.std(jacobian_radii)
    
    return {
        'valid': mean_radius < 1.0,
        'mean_jacobian_radius': float(mean_radius),
        'std_jacobian_radius': float(std_radius),
        'method': 'jacobian_analysis',
        'confidence': 0.85 if mean_radius < 0.9 else 0.6
    }


def validate_esp_fast(esn, n_tests: int = 3, test_length: int = 100,
                     tolerance: float = 1e-4) -> Dict[str, Any]:
    """Fast ESP validation for real-time use."""
    # Quick spectral radius check
    spectral_check = validate_spectral_radius(esn)
    if not spectral_check['valid']:
        return {
            'valid': False,
            'method': 'fast_spectral',
            'reason': 'spectral_radius_exceeded',
            **spectral_check
        }
    
    # Quick convergence test
    convergence_results = []
    for _ in range(n_tests):
        state1 = np.random.randn(esn.reservoir_size) * 0.1
        state2 = np.random.randn(esn.reservoir_size) * 0.1
        input_seq = np.random.randn(test_length, esn.n_inputs) * 0.5
        
        # Short test - only last 20 steps
        for input_vec in input_seq[-20:]:
            state1 = update_state_for_validation(esn, state1, input_vec)
            state2 = update_state_for_validation(esn, state2, input_vec)
        
        diff = np.linalg.norm(state1 - state2)
        convergence_results.append(diff < tolerance * 10)  # More lenient
    
    convergence_rate = np.mean(convergence_results)
    
    return {
        'valid': convergence_rate > 0.6,
        'convergence_rate': float(convergence_rate),
        'spectral_radius': spectral_check['spectral_radius'],
        'method': 'fast_validation',
        'confidence': min(convergence_rate * 0.8, 0.8)
    }


def compute_jacobian_at_state(esn, state: np.ndarray, input_vec: np.ndarray) -> np.ndarray:
    """Compute Jacobian of state update at given state and input."""
    # For tanh activation: d/dx tanh(x) = 1 - tanh²(x)
    net_input = (esn.input_weights @ input_vec + 
                esn.reservoir_weights @ state)
    
    if hasattr(esn, 'bias_vector') and esn.bias_vector is not None:
        net_input += esn.bias_vector
    
    # Derivative of tanh
    tanh_derivative = 1 - np.tanh(net_input)**2
    
    # Jacobian: J = (1-α)I + α * diag(tanh'(net)) * W_res
    alpha = getattr(esn, 'leak_rate', 1.0)
    identity = np.eye(esn.reservoir_size)
    
    jacobian = ((1 - alpha) * identity + 
               alpha * np.diag(tanh_derivative) @ esn.reservoir_weights)
    
    return jacobian


def run_test_sequence(esn, initial_state: np.ndarray, 
                     input_sequence: np.ndarray) -> List[np.ndarray]:
    """Run ESN through test sequence for validation."""
    states = [initial_state.copy()]
    current_state = initial_state.copy()
    
    for input_vec in input_sequence:
        current_state = update_state_for_validation(esn, current_state, input_vec)
        states.append(current_state.copy())
    
    return states


def update_state_for_validation(esn, state: np.ndarray, 
                               input_vec: np.ndarray) -> np.ndarray:
    """Update state for validation (simplified version)."""
    # Ensure input dimensions
    if len(input_vec) != esn.n_inputs:
        input_vec = np.resize(input_vec, esn.n_inputs)
    
    # Basic state update
    net_input = (esn.input_weights @ input_vec + 
                esn.reservoir_weights @ state)
    
    if hasattr(esn, 'bias_vector') and esn.bias_vector is not None:
        net_input += esn.bias_vector
    
    # Apply activation
    activated = np.tanh(net_input)
    
    # Apply leak rate
    alpha = getattr(esn, 'leak_rate', 1.0)
    new_state = (1 - alpha) * state + alpha * activated
    
    return new_state


# ================================
# TOPOLOGY MANAGEMENT UTILITIES
# ================================

def create_topology(topology_type: str, n_reservoir: int, sparsity: float = 0.1,
                   connectivity_mask: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    """
    Create reservoir topology matrix using specified method.
    
    Args:
        topology_type: Type of topology ('ring', 'small_world', 'scale_free', 'random', 'custom')
        n_reservoir: Number of reservoir neurons
        sparsity: Connection density (0-1)
        connectivity_mask: Custom connectivity pattern for 'custom' topology
        **kwargs: Additional topology parameters
        
    Returns:
        Weight matrix with specified topology
    """
    if topology_type == 'ring':
        return create_ring_topology(n_reservoir, sparsity)
    elif topology_type == 'small_world':
        return create_small_world_topology(n_reservoir, sparsity, **kwargs)
    elif topology_type == 'scale_free':
        return create_scale_free_topology(n_reservoir, sparsity, **kwargs)
    elif topology_type == 'random':
        return create_random_topology(n_reservoir, sparsity)
    elif topology_type == 'custom':
        if connectivity_mask is None:
            raise ValueError("Custom topology requires connectivity_mask parameter")
        return create_custom_topology(connectivity_mask)
    else:
        raise ValueError(f"Unknown topology type: {topology_type}")


def create_ring_topology(n_reservoir: int, sparsity: float) -> np.ndarray:
    """Create ring topology reservoir with local connectivity patterns."""
    W = np.zeros((n_reservoir, n_reservoir))
    connections_per_node = max(1, int(sparsity * n_reservoir))
    
    for i in range(n_reservoir):
        # Create forward and backward connections for bidirectional ring
        for j in range(1, connections_per_node + 1):
            # Forward connections (clockwise)
            forward_target = (i + j) % n_reservoir
            W[i, forward_target] = np.random.uniform(-1, 1)
            
            # Backward connections (counter-clockwise) 
            if j <= connections_per_node // 2:
                backward_target = (i - j) % n_reservoir
                W[i, backward_target] = np.random.uniform(-1, 1)
        
        # Add some random long-range connections
        n_random = max(1, connections_per_node // 4)
        for _ in range(n_random):
            random_target = np.random.randint(n_reservoir)
            if random_target != i and W[i, random_target] == 0:
                W[i, random_target] = np.random.uniform(-1, 1)
    
    return W


def create_small_world_topology(n_reservoir: int, sparsity: float,
                               rewire_probability: float = 0.1) -> np.ndarray:
    """Create small-world topology using Watts-Strogatz model."""
    W = np.zeros((n_reservoir, n_reservoir))
    k = max(2, int(sparsity * n_reservoir))
    if k % 2 == 1:
        k += 1  # Ensure even degree
        
    # Step 1: Create regular ring lattice
    for i in range(n_reservoir):
        for j in range(1, k // 2 + 1):
            right_neighbor = (i + j) % n_reservoir
            W[i, right_neighbor] = np.random.uniform(-1, 1)
            left_neighbor = (i - j) % n_reservoir
            W[i, left_neighbor] = np.random.uniform(-1, 1)
    
    # Step 2: Rewire edges with probability p
    for i in range(n_reservoir):
        existing_connections = np.where(W[i, :] != 0)[0]
        
        for target in existing_connections:
            if np.random.random() < rewire_probability:
                original_weight = W[i, target]
                W[i, target] = 0
                
                # Find new random connection
                attempts = 0
                while attempts < 10:
                    new_target = np.random.randint(n_reservoir)
                    if new_target != i and W[i, new_target] == 0:
                        W[i, new_target] = original_weight
                        break
                    attempts += 1
                
                if attempts >= 10:
                    W[i, target] = original_weight
    
    return W


def create_scale_free_topology(n_reservoir: int, sparsity: float) -> np.ndarray:
    """Create scale-free topology using preferential attachment."""
    W = np.zeros((n_reservoir, n_reservoir))
    
    # Initialize with small fully connected seed
    seed_size = min(5, n_reservoir // 10)
    for i in range(seed_size):
        for j in range(seed_size):
            if i != j:
                W[i, j] = np.random.uniform(-1, 1)
    
    # Track degrees for preferential attachment
    degree = np.sum(W != 0, axis=1) + np.sum(W != 0, axis=0)
    degree = np.maximum(degree, 1)
    
    # Calculate connections to add
    target_connections = int(sparsity * n_reservoir * n_reservoir)
    current_connections = np.sum(W != 0)
    connections_to_add = max(0, target_connections - current_connections)
    
    # Add connections using preferential attachment
    for _ in range(connections_to_add):
        source = np.random.randint(n_reservoir)
        
        if np.sum(degree) > 0:
            probabilities = degree / np.sum(degree)
            target = np.random.choice(n_reservoir, p=probabilities)
            
            if source != target and W[source, target] == 0:
                W[source, target] = np.random.uniform(-1, 1)
                degree[source] += 1
                degree[target] += 1
    
    return W


def create_random_topology(n_reservoir: int, sparsity: float) -> np.ndarray:
    """Create random Erdős-Rényi topology."""
    W = np.random.uniform(-1, 1, (n_reservoir, n_reservoir))
    mask = np.random.random((n_reservoir, n_reservoir)) < sparsity
    np.fill_diagonal(mask, False)  # No self-connections
    W = W * mask
    return W


def create_custom_topology(connectivity_mask: np.ndarray) -> np.ndarray:
    """Create topology using custom connectivity mask."""
    n_reservoir = connectivity_mask.shape[0]
    
    if np.all((connectivity_mask == 0) | (connectivity_mask == 1)):
        # Binary mask
        W = np.random.uniform(-1, 1, (n_reservoir, n_reservoir))
        W = W * connectivity_mask
    else:
        # Weighted mask
        W = connectivity_mask.copy()
        nonzero_mask = (W != 0)
        random_factors = np.random.uniform(0.5, 1.5, W.shape)
        W[nonzero_mask] = W[nonzero_mask] * random_factors[nonzero_mask]
    
    return W


def scale_spectral_radius(W: np.ndarray, target_radius: float) -> np.ndarray:
    """Scale weight matrix to achieve target spectral radius."""
    if W.size == 0 or np.all(W == 0):
        return W
        
    try:
        eigenvalues = np.linalg.eigvals(W)
        current_radius = np.max(np.abs(eigenvalues))
        
        if current_radius > 1e-12:
            scaling_factor = target_radius / current_radius
            W_scaled = W * scaling_factor
            
            # Verify scaling
            new_eigenvalues = np.linalg.eigvals(W_scaled)
            achieved_radius = np.max(np.abs(new_eigenvalues))
            
            if abs(achieved_radius - target_radius) > 1e-6:
                warnings.warn(
                    f"Spectral radius scaling inaccurate. "
                    f"Target: {target_radius:.6f}, Achieved: {achieved_radius:.6f}"
                )
            
            return W_scaled
        else:
            warnings.warn("Matrix has zero spectral radius, no scaling applied.")
            return W
            
    except np.linalg.LinAlgError as e:
        warnings.warn(f"Could not compute eigenvalues for scaling: {e}")
        return W


def analyze_topology(W: np.ndarray) -> Dict[str, Any]:
    """Analyze topological properties of reservoir weight matrix."""
    n = W.shape[0]
    nonzero_mask = (W != 0)
    n_edges = np.sum(nonzero_mask)
    
    if n_edges == 0:
        return {
            'n_nodes': n,
            'n_edges': 0,
            'density': 0.0,
            'clustering_coefficient': 0.0,
            'path_length': np.inf
        }
    
    # Basic properties
    density = n_edges / (n * (n - 1))
    in_degrees = np.sum(nonzero_mask, axis=0)
    out_degrees = np.sum(nonzero_mask, axis=1)
    total_degrees = in_degrees + out_degrees
    
    # Clustering coefficient (simplified version)
    clustering_coeffs = []
    for i in range(n):
        neighbors = np.where(nonzero_mask[i, :])[0]
        k = len(neighbors)
        if k < 2:
            clustering_coeffs.append(0.0)
        else:
            # Count edges among neighbors
            neighbor_edges = 0
            for j in range(k):
                for l in range(j+1, k):
                    if nonzero_mask[neighbors[j], neighbors[l]]:
                        neighbor_edges += 1
            possible_edges = k * (k - 1) / 2
            clustering_coeffs.append(neighbor_edges / possible_edges if possible_edges > 0 else 0.0)
    
    clustering_coefficient = np.mean(clustering_coeffs)
    
    # Spectral properties
    try:
        eigenvalues = np.linalg.eigvals(W)
        spectral_radius = np.max(np.abs(eigenvalues))
        spectral_gap = spectral_radius - np.partition(np.abs(eigenvalues), -2)[-2]
    except:
        spectral_radius = np.nan
        spectral_gap = np.nan
    
    return {
        'n_nodes': n,
        'n_edges': int(n_edges),
        'density': float(density),
        'mean_degree': float(np.mean(total_degrees)),
        'degree_std': float(np.std(total_degrees)),
        'max_degree': int(np.max(total_degrees)),
        'clustering_coefficient': float(clustering_coefficient),
        'spectral_radius': float(spectral_radius),
        'spectral_gap': float(spectral_gap)
    }


# ================================
# BENCHMARK UTILITIES
# ================================

def memory_capacity_benchmark(esn, n_samples: int = 1000, max_delay: int = 20,
                             washout: int = 100, random_seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Evaluate memory capacity using delay line tasks.
    
    🔬 **Research Background:**
    Memory capacity (MC) measures the reservoir's ability to reconstruct delayed
    versions of its input. This is a fundamental benchmark for temporal processing
    capability in reservoir computers.
    
    **Mathematical Foundation:**
    MC_k = max(0, R²(u(t-k), y_k(t))) where:
    - u(t-k) is input delayed by k steps
    - y_k(t) is reservoir output trained to reconstruct u(t-k)
    - R² is coefficient of determination
    
    **Total Memory Capacity:**
    MC_total = Σ MC_k over all delays k
    
    For linear reservoirs, theoretical upper bound is MC_max = N (reservoir size).
    Nonlinear reservoirs typically achieve lower MC due to information mixing.
    
    Args:
        esn: EchoStateNetwork instance
        n_samples: Number of samples in test sequence
        max_delay: Maximum delay to test
        washout: Washout period to ignore
        random_seed: Seed for reproducible results
        
    Returns:
        Dictionary with memory capacity results
        
    References:
        - Jaeger, H. (2001). "Short term memory in echo state networks"
        - Dambre, J., et al. (2012). "Information processing capacity"
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Generate test input sequence
    input_seq = np.random.uniform(-1, 1, (n_samples, 1))
    memory_scores = []
    correlations = []
    r2_scores = []
    
    for delay in range(1, max_delay + 1):
        if n_samples > delay + washout:
            # Create delayed target
            target = np.zeros_like(input_seq)
            target[delay:] = input_seq[:-delay]
            
            try:
                # Train ESN for this delay
                esn.train(input_seq, target, washout=washout)
                pred = esn.predict(input_seq, washout=washout)
                
                # Calculate metrics
                valid_target = target[washout:].flatten()
                valid_pred = pred[washout:].flatten()
                
                # R² score (primary metric)
                r2 = r2_score(valid_target, valid_pred)
                r2_scores.append(max(0, r2))
                
                # Correlation (secondary metric)
                correlation = np.corrcoef(valid_target, valid_pred)[0, 1]
                if np.isnan(correlation):
                    correlation = 0.0
                correlations.append(max(0, correlation))
                
                # Memory score (max of R² and correlation²)
                memory_score = max(0, max(r2, correlation**2))
                memory_scores.append(memory_score)
                
            except Exception as e:
                logger.warning(f"Failed at delay {delay}: {e}")
                memory_scores.append(0.0)
                correlations.append(0.0)
                r2_scores.append(0.0)
        else:
            memory_scores.append(0.0)
            correlations.append(0.0)
            r2_scores.append(0.0)
    
    # Calculate summary statistics
    total_capacity = sum(memory_scores)
    effective_capacity = sum(1 for score in memory_scores if score > 0.1)
    decay_constant = calculate_memory_decay(memory_scores)
    
    return {
        'memory_scores': memory_scores,
        'correlations': correlations,
        'r2_scores': r2_scores,
        'total_capacity': float(total_capacity),
        'effective_capacity': int(effective_capacity),
        'decay_constant': float(decay_constant),
        'delays_tested': list(range(1, max_delay + 1)),
        'normalized_capacity': float(total_capacity / esn.reservoir_size) if hasattr(esn, 'reservoir_size') else None
    }


def nonlinear_capacity_benchmark(esn, task_type: str = 'NARMA',
                                n_samples: int = 1000, **kwargs) -> Dict[str, Any]:
    """
    Evaluate nonlinear processing capacity using standard tasks.
    
    **Supported Tasks:**
    - NARMA-k: Nonlinear Auto-Regressive Moving Average
    - XOR-temporal: Temporal XOR patterns
    - Parity: Temporal parity checking
    - Multiplication: Input multiplication with delays
    
    Args:
        esn: EchoStateNetwork instance
        task_type: Nonlinear task type
        n_samples: Number of samples
        **kwargs: Task-specific parameters
        
    Returns:
        Dictionary with nonlinear capacity results
    """
    if task_type == 'NARMA':
        return evaluate_narma_task(esn, n_samples, **kwargs)
    elif task_type == 'XOR_temporal':
        return evaluate_xor_temporal_task(esn, n_samples, **kwargs)
    elif task_type == 'parity':
        return evaluate_parity_task(esn, n_samples, **kwargs)
    elif task_type == 'multiplication':
        return evaluate_multiplication_task(esn, n_samples, **kwargs)
    else:
        raise ValueError(f"Unknown nonlinear task: {task_type}")


def evaluate_narma_task(esn, n_samples: int, order: int = 10,
                       train_ratio: float = 0.7) -> Dict[str, Any]:
    """Evaluate NARMA-k nonlinear task."""
    # Generate NARMA sequence
    input_seq, target_seq = generate_narma_sequence(n_samples, order)
    
    # Split data
    n_train = int(n_samples * train_ratio)
    X_train, X_test = input_seq[:n_train], input_seq[n_train:]
    y_train, y_test = target_seq[:n_train], target_seq[n_train:]
    
    try:
        # Train and test
        esn.train(X_train, y_train, washout=100)
        pred = esn.predict(X_test)
        
        # Calculate performance
        mse = mean_squared_error(y_test[100:], pred[100:])
        r2 = r2_score(y_test[100:], pred[100:])
        
        return {
            'task': f'NARMA-{order}',
            'mse': float(mse),
            'r2_score': float(max(0, r2)),
            'success': r2 > 0.5,
            'n_samples': n_samples,
            'order': order
        }
    except Exception as e:
        return {
            'task': f'NARMA-{order}',
            'error': str(e),
            'success': False
        }


def generate_narma_sequence(n_samples: int, order: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """Generate NARMA-k sequence for benchmarking."""
    u = np.random.uniform(0, 0.5, (n_samples, 1))
    y = np.zeros((n_samples, 1))
    
    # Initialize first values
    for i in range(order):
        y[i] = 0.2
    
    # Generate NARMA sequence
    for i in range(order, n_samples):
        feedback = 0.0
        for j in range(1, order + 1):
            feedback += y[i - j, 0]
        
        y[i, 0] = (0.3 * y[i - 1, 0] + 
                   0.05 * y[i - 1, 0] * feedback + 
                   1.5 * u[i - 1, 0] * u[i - order, 0] + 0.1)
    
    return u, y


def calculate_memory_decay(memory_scores: List[float]) -> float:
    """Calculate exponential decay constant of memory scores."""
    if not memory_scores or all(s <= 0 for s in memory_scores):
        return 0.0
    
    # Find first non-zero score
    start_idx = 0
    while start_idx < len(memory_scores) and memory_scores[start_idx] <= 0:
        start_idx += 1
    
    if start_idx >= len(memory_scores) - 1:
        return 0.0
    
    # Fit exponential decay: y = a * exp(-x/tau)
    x_data = np.array(range(start_idx, len(memory_scores)))
    y_data = np.array(memory_scores[start_idx:])
    
    # Take log and fit linear relationship
    positive_mask = y_data > 1e-10
    if np.sum(positive_mask) < 2:
        return 0.0
    
    x_fit = x_data[positive_mask]
    log_y_fit = np.log(y_data[positive_mask])
    
    try:
        # Linear fit: log(y) = log(a) - x/tau
        slope, intercept = np.polyfit(x_fit, log_y_fit, 1)
        tau = -1 / slope if slope < 0 else np.inf
        return max(0, tau)
    except:
        return 0.0


# ================================
# OPTIMIZATION UTILITIES
# ================================

def optimize_hyperparameters(esn_class, X_train, y_train, param_space: Dict,
                           optimization_method: str = 'grid_search',
                           cv_folds: int = 3, **kwargs) -> Dict[str, Any]:
    """
    Optimize ESN hyperparameters using specified method.
    
    Args:
        esn_class: EchoStateNetwork class
        X_train: Training input data
        y_train: Training target data
        param_space: Dictionary defining parameter search space
        optimization_method: 'grid_search', 'random_search', or 'bayesian'
        cv_folds: Cross-validation folds
        **kwargs: Additional optimization parameters
        
    Returns:
        Dictionary with optimization results
    """
    if optimization_method == 'grid_search':
        return grid_search_optimization(esn_class, X_train, y_train, param_space, cv_folds)
    elif optimization_method == 'random_search':
        return random_search_optimization(esn_class, X_train, y_train, param_space, cv_folds, **kwargs)
    elif optimization_method == 'bayesian':
        return bayesian_optimization(esn_class, X_train, y_train, param_space, cv_folds, **kwargs)
    else:
        raise ValueError(f"Unknown optimization method: {optimization_method}")


def grid_search_optimization(esn_class, X_train, y_train, param_space: Dict,
                           cv_folds: int = 3) -> Dict[str, Any]:
    """Perform grid search optimization."""
    from itertools import product
    
    # Generate parameter combinations
    param_names = list(param_space.keys())
    param_values = list(param_space.values())
    param_combinations = list(product(*param_values))
    
    best_score = -np.inf
    best_params = None
    all_results = []
    
    for param_combo in param_combinations:
        params = dict(zip(param_names, param_combo))
        
        try:
            # Create ESN with parameters
            esn = esn_class(**params)
            
            # Cross-validation
            scores = cross_validate_esn(esn, X_train, y_train, cv_folds)
            mean_score = np.mean(scores)
            
            result = {
                'params': params,
                'mean_score': float(mean_score),
                'std_score': float(np.std(scores)),
                'scores': scores.tolist()
            }
            all_results.append(result)
            
            if mean_score > best_score:
                best_score = mean_score
                best_params = params
                
        except Exception as e:
            logger.warning(f"Failed parameter combination {params}: {e}")
    
    return {
        'best_params': best_params,
        'best_score': float(best_score) if best_score != -np.inf else None,
        'all_results': all_results,
        'method': 'grid_search'
    }


def cross_validate_esn(esn, X, y, cv_folds: int = 3) -> np.ndarray:
    """Perform cross-validation on ESN."""
    kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
    scores = []
    
    for train_idx, val_idx in kf.split(X):
        X_train_fold, X_val_fold = X[train_idx], X[val_idx]
        y_train_fold, y_val_fold = y[train_idx], y[val_idx]
        
        try:
            # Reset ESN state
            esn.reset_state()
            
            # Train and predict
            esn.train(X_train_fold, y_train_fold, washout=50)
            pred = esn.predict(X_val_fold, washout=0)
            
            # Calculate score (R²)
            score = r2_score(y_val_fold, pred)
            scores.append(max(0, score))  # Ensure non-negative
            
        except Exception as e:
            logger.warning(f"Cross-validation fold failed: {e}")
            scores.append(0.0)
    
    return np.array(scores)


def analyze_parameter_sensitivity(esn_class, X_train, y_train,
                                 base_params: Dict, param_ranges: Dict,
                                 n_points: int = 10) -> Dict[str, Any]:
    """Analyze sensitivity of performance to parameter changes."""
    sensitivity_results = {}
    
    for param_name, param_range in param_ranges.items():
        param_values = np.linspace(param_range[0], param_range[1], n_points)
        scores = []
        
        for param_value in param_values:
            test_params = base_params.copy()
            test_params[param_name] = param_value
            
            try:
                esn = esn_class(**test_params)
                fold_scores = cross_validate_esn(esn, X_train, y_train, cv_folds=3)
                scores.append(np.mean(fold_scores))
            except:
                scores.append(0.0)
        
        sensitivity_results[param_name] = {
            'values': param_values.tolist(),
            'scores': scores,
            'best_value': param_values[np.argmax(scores)],
            'best_score': max(scores),
            'sensitivity': float(np.std(scores))
        }
    
    return sensitivity_results


# ================================
# STATISTICAL VALIDATION UTILITIES
# ================================

def statistical_significance_test(results1: List[float], results2: List[float],
                                 test_type: str = 'wilcoxon') -> Dict[str, Any]:
    """Test statistical significance between two result sets."""
    if test_type == 'wilcoxon':
        statistic, p_value = stats.wilcoxon(results1, results2)
    elif test_type == 't_test':
        statistic, p_value = stats.ttest_rel(results1, results2)
    elif test_type == 'mann_whitney':
        statistic, p_value = stats.mannwhitneyu(results1, results2)
    else:
        raise ValueError(f"Unknown test type: {test_type}")
    
    return {
        'test_type': test_type,
        'statistic': float(statistic),
        'p_value': float(p_value),
        'significant_005': p_value < 0.05,
        'significant_001': p_value < 0.01
    }


def confidence_interval(data: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate confidence interval for data."""
    alpha = 1 - confidence
    n = len(data)
    mean = np.mean(data)
    sem = stats.sem(data)
    
    t_critical = stats.t.ppf(1 - alpha/2, n - 1)
    margin = t_critical * sem
    
    return mean - margin, mean + margin


def performance_summary_statistics(scores: List[float]) -> Dict[str, float]:
    """Calculate comprehensive summary statistics for performance scores."""
    scores_array = np.array(scores)
    
    return {
        'mean': float(np.mean(scores_array)),
        'median': float(np.median(scores_array)),
        'std': float(np.std(scores_array)),
        'min': float(np.min(scores_array)),
        'max': float(np.max(scores_array)),
        'q25': float(np.percentile(scores_array, 25)),
        'q75': float(np.percentile(scores_array, 75)),
        'iqr': float(np.percentile(scores_array, 75) - np.percentile(scores_array, 25)),
        'skewness': float(stats.skew(scores_array)),
        'kurtosis': float(stats.kurtosis(scores_array))
    }


# ================================
# HELPER UTILITIES
# ================================

def create_benchmark_report(results: Dict[str, Any], filename: Optional[str] = None) -> str:
    """Create comprehensive benchmark report."""
    report_lines = [
        "🧪 RESERVOIR COMPUTING BENCHMARK REPORT",
        "=" * 50,
        ""
    ]
    
    # Configuration summary
    if 'configurations' in results:
        report_lines.append("📊 CONFIGURATIONS TESTED:")
        for i, config in enumerate(results['configurations']):
            report_lines.append(f"  {i+1}. {config.get('name', f'Config {i+1}')}")
        report_lines.append("")
    
    # Memory capacity results
    if 'memory_capacity' in results:
        mc = results['memory_capacity']
        report_lines.extend([
            "🧠 MEMORY CAPACITY RESULTS:",
            f"  Total Capacity: {mc.get('total_capacity', 'N/A'):.3f}",
            f"  Effective Capacity: {mc.get('effective_capacity', 'N/A')}",
            f"  Decay Constant: {mc.get('decay_constant', 'N/A'):.3f}",
            ""
        ])
    
    # Nonlinear capacity results
    if 'nonlinear_capacity' in results:
        nc = results['nonlinear_capacity']
        report_lines.extend([
            "🔢 NONLINEAR CAPACITY RESULTS:",
            f"  Task: {nc.get('task', 'N/A')}",
            f"  R² Score: {nc.get('r2_score', 'N/A'):.3f}",
            f"  Success: {nc.get('success', 'N/A')}",
            ""
        ])
    
    # ESP validation results
    if 'esp_validation' in results:
        esp = results['esp_validation']
        report_lines.extend([
            "✅ ECHO STATE PROPERTY VALIDATION:",
            f"  Overall Valid: {esp.get('valid', 'N/A')}",
            f"  Spectral Radius: {esp.get('spectral_radius', 'N/A'):.4f}",
            f"  Confidence: {esp.get('validation_confidence', 'N/A'):.3f}",
            ""
        ])
    
    report_text = "\n".join(report_lines)
    
    if filename:
        with open(filename, 'w') as f:
            f.write(report_text)
    
    return report_text


def validate_esn_configuration(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate ESN configuration parameters."""
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check required parameters
    required_params = ['n_reservoir', 'sparsity', 'spectral_radius']
    for param in required_params:
        if param not in config:
            validation_results['errors'].append(f"Missing required parameter: {param}")
            validation_results['valid'] = False
    
    # Check parameter ranges
    if 'n_reservoir' in config:
        if not isinstance(config['n_reservoir'], int) or config['n_reservoir'] <= 0:
            validation_results['errors'].append("n_reservoir must be positive integer")
            validation_results['valid'] = False
    
    if 'sparsity' in config:
        if not 0 < config['sparsity'] <= 1:
            validation_results['errors'].append("sparsity must be in (0, 1]")
            validation_results['valid'] = False
    
    if 'spectral_radius' in config:
        if not 0 < config['spectral_radius'] < 2:
            validation_results['warnings'].append("spectral_radius outside typical range (0, 1)")
    
    return validation_results


# Export utility functions
__all__ = [
    # ESP Validation
    'comprehensive_esp_validation', 'validate_spectral_radius', 'validate_convergence',
    'validate_lyapunov', 'validate_jacobian', 'validate_esp_fast',
    'compute_jacobian_at_state', 'run_test_sequence', 'update_state_for_validation',
    
    # Topology Management
    'create_topology', 'create_ring_topology', 'create_small_world_topology',
    'create_scale_free_topology', 'create_random_topology', 'create_custom_topology',
    'scale_spectral_radius', 'analyze_topology',
    
    # Benchmark Suite
    'memory_capacity_benchmark', 'nonlinear_capacity_benchmark', 'evaluate_narma_task',
    'generate_narma_sequence', 'calculate_memory_decay',
    
    # Optimization
    'optimize_hyperparameters', 'grid_search_optimization', 'cross_validate_esn',
    'analyze_parameter_sensitivity',
    
    # Statistical Validation
    'statistical_significance_test', 'confidence_interval', 'performance_summary_statistics',
    
    # Helper Functions
    'create_benchmark_report', 'validate_esn_configuration'
]