"""
🌐 Reservoir Computing - Topology Management Module
===================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Watts & Strogatz (1998) "Collective dynamics of 'small-world' networks"

🎯 MODULE PURPOSE:
=================
Network topology creation and management utilities for reservoir computing systems.
Provides various connectivity patterns, topology analysis tools, and spectral
radius control methods for optimal reservoir construction.

🌐 TOPOLOGY CAPABILITIES:
========================
• Ring topology creation with customizable connections
• Small-world networks with rewiring probability control
• Scale-free networks using preferential attachment
• Random topology generation with sparsity control
• Custom topology support for specialized architectures
• Spectral radius scaling for stability control
• Comprehensive topology analysis and characterization

🔬 RESEARCH FOUNDATION:
======================
Based on network topology research from:
- Watts & Strogatz (1998): Small-world network properties
- Barabási & Albert (1999): Scale-free network models
- Newman (2003): Network structure and topology analysis
- Reservoir computing topology studies for performance optimization

This module represents the topology management and analysis components,
split from the 1142-line monolith for specialized network construction.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List
import warnings
from scipy import sparse
from scipy.linalg import eigvals
from scipy.sparse import csr_matrix
import logging

# Configure logging for topology functions
logger = logging.getLogger(__name__)

# ================================
# TOPOLOGY CREATION FUNCTIONS
# ================================

def create_topology(topology_type: str, n_reservoir: int, sparsity: float = 0.1,
                   **kwargs) -> np.ndarray:
    """
    🌐 Create Network Topology for Reservoir Computing
    
    Factory function for creating various network topologies optimized
    for reservoir computing applications.
    
    Args:
        topology_type: Type of topology ('ring', 'small_world', 'scale_free', 'random', 'custom')
        n_reservoir: Number of reservoir neurons
        sparsity: Connection density (fraction of possible connections)
        **kwargs: Topology-specific parameters
        
    Returns:
        np.ndarray: Adjacency matrix representing network topology
        
    Supported Topologies:
    ====================
    - 'ring': Ring lattice with nearest neighbor connections
    - 'small_world': Watts-Strogatz small-world network
    - 'scale_free': Barabási-Albert scale-free network  
    - 'random': Erdős-Rényi random network
    - 'custom': User-defined topology from connectivity mask
    
    Research Background:
    ===================
    Different topologies exhibit different information processing characteristics
    in reservoir computing, as demonstrated in network topology studies.
    """
    topology_creators = {
        'ring': create_ring_topology,
        'small_world': create_small_world_topology,
        'scale_free': create_scale_free_topology,
        'random': create_random_topology,
        'custom': create_custom_topology
    }
    
    if topology_type not in topology_creators:
        raise ValueError(f"Unknown topology type: {topology_type}")
    
    creator_func = topology_creators[topology_type]
    
    try:
        if topology_type == 'custom':
            # Custom topology requires connectivity_mask parameter
            if 'connectivity_mask' not in kwargs:
                raise ValueError("Custom topology requires 'connectivity_mask' parameter")
            return creator_func(kwargs['connectivity_mask'])
        else:
            # Standard topologies use n_reservoir and sparsity
            return creator_func(n_reservoir, sparsity, **kwargs)
            
    except Exception as e:
        logger.error(f"Topology creation failed for {topology_type}: {e}")
        # Fallback to random topology
        warnings.warn(f"Falling back to random topology due to error: {e}")
        return create_random_topology(n_reservoir, sparsity)

def create_ring_topology(n_reservoir: int, sparsity: float) -> np.ndarray:
    """
    💍 Create Ring Topology
    
    Creates a ring lattice where each neuron connects to its k nearest neighbors.
    The number of neighbors is determined by the sparsity parameter.
    
    Args:
        n_reservoir: Number of neurons in the ring
        sparsity: Controls connection density (determines k neighbors)
        
    Returns:
        np.ndarray: Ring topology adjacency matrix
        
    Research Background:
    ===================
    Ring topologies provide regular connectivity patterns with predictable
    information flow, useful for temporal processing tasks requiring
    structured signal propagation.
    """
    W = np.zeros((n_reservoir, n_reservoir))
    
    # Calculate number of neighbors based on sparsity
    total_possible = n_reservoir * (n_reservoir - 1)
    target_connections = int(sparsity * total_possible)
    k_neighbors = max(1, target_connections // n_reservoir)  # Connections per neuron
    
    # Create bidirectional ring connections
    for i in range(n_reservoir):
        for offset in range(1, k_neighbors // 2 + 1):
            # Forward connections
            j_forward = (i + offset) % n_reservoir
            W[i, j_forward] = np.random.uniform(-1, 1)
            
            # Backward connections
            j_backward = (i - offset) % n_reservoir
            W[i, j_backward] = np.random.uniform(-1, 1)
    
    # Add some random long-range connections to achieve target sparsity
    current_connections = np.sum(W != 0)
    remaining_connections = target_connections - current_connections
    
    if remaining_connections > 0:
        # Add random connections
        for _ in range(remaining_connections):
            i, j = np.random.choice(n_reservoir, 2, replace=False)
            if W[i, j] == 0:  # Avoid duplicate connections
                W[i, j] = np.random.uniform(-1, 1)
    
    return W

def create_small_world_topology(n_reservoir: int, sparsity: float,
                               rewiring_prob: float = 0.1, k_neighbors: int = None) -> np.ndarray:
    """
    🌍 Create Small-World Topology (Watts-Strogatz Model)
    
    Creates a small-world network by starting with a ring lattice and
    rewiring edges with given probability to create long-range connections.
    
    Args:
        n_reservoir: Number of neurons
        sparsity: Target connection density
        rewiring_prob: Probability of rewiring each edge
        k_neighbors: Initial ring connectivity (auto-calculated if None)
        
    Returns:
        np.ndarray: Small-world topology adjacency matrix
        
    Research Background:
    ===================
    Based on Watts & Strogatz (1998) model. Small-world networks exhibit
    both local clustering and short path lengths, beneficial for reservoir
    computing tasks requiring both local and global information integration.
    """
    # Start with ring topology
    if k_neighbors is None:
        # Calculate k to achieve approximate target sparsity
        k_neighbors = max(4, int(sparsity * n_reservoir * 2))
    
    # Create initial ring lattice
    W = np.zeros((n_reservoir, n_reservoir))
    
    # Add nearest neighbor connections
    for i in range(n_reservoir):
        for offset in range(1, k_neighbors // 2 + 1):
            j = (i + offset) % n_reservoir
            W[i, j] = np.random.uniform(-1, 1)
            W[j, i] = np.random.uniform(-1, 1)  # Make symmetric initially
    
    # Rewiring step
    edges_to_rewire = []
    for i in range(n_reservoir):
        for j in range(i + 1, n_reservoir):
            if W[i, j] != 0 and np.random.random() < rewiring_prob:
                edges_to_rewire.append((i, j))
    
    # Perform rewiring
    for i, j in edges_to_rewire:
        # Remove original edge
        W[i, j] = 0
        W[j, i] = 0
        
        # Add new random edge (avoid self-loops and existing connections)
        attempts = 0
        while attempts < 10:  # Limit attempts to avoid infinite loops
            k = np.random.choice(n_reservoir)
            if k != i and W[i, k] == 0:
                W[i, k] = np.random.uniform(-1, 1)
                break
            attempts += 1
    
    # Adjust to target sparsity
    current_sparsity = np.sum(W != 0) / (n_reservoir * (n_reservoir - 1))
    if current_sparsity < sparsity:
        # Add more random connections
        needed = int((sparsity - current_sparsity) * n_reservoir * (n_reservoir - 1))
        for _ in range(needed):
            i, j = np.random.choice(n_reservoir, 2, replace=False)
            if W[i, j] == 0:
                W[i, j] = np.random.uniform(-1, 1)
    
    return W

def create_scale_free_topology(n_reservoir: int, sparsity: float) -> np.ndarray:
    """
    📈 Create Scale-Free Topology (Barabási-Albert Model)
    
    Creates a scale-free network using preferential attachment where new nodes
    connect to existing nodes with probability proportional to their degree.
    
    Args:
        n_reservoir: Number of neurons
        sparsity: Target connection density
        
    Returns:
        np.ndarray: Scale-free topology adjacency matrix
        
    Research Background:
    ===================
    Based on Barabási & Albert (1999) model. Scale-free networks have
    power-law degree distributions with hub neurons that may enhance
    information integration in reservoir computing systems.
    """
    W = np.zeros((n_reservoir, n_reservoir))
    
    # Calculate target number of connections per new node
    target_connections = int(sparsity * n_reservoir * (n_reservoir - 1))
    m = max(1, target_connections // n_reservoir)  # Edges to add per node
    
    # Start with a small connected core
    core_size = min(m + 1, 5)
    for i in range(core_size):
        for j in range(i + 1, core_size):
            W[i, j] = np.random.uniform(-1, 1)
            W[j, i] = np.random.uniform(-1, 1)
    
    # Add remaining nodes using preferential attachment
    for new_node in range(core_size, n_reservoir):
        # Calculate connection probabilities based on current degrees
        degrees = np.sum(W != 0, axis=1)[:new_node]
        
        if np.sum(degrees) == 0:
            # Fallback: uniform probability
            probabilities = np.ones(new_node) / new_node
        else:
            probabilities = degrees / np.sum(degrees)
        
        # Select m nodes to connect to (without replacement)
        n_connections = min(m, new_node)
        if n_connections > 0:
            try:
                target_nodes = np.random.choice(
                    new_node, size=n_connections, 
                    replace=False, p=probabilities
                )
                
                # Create connections
                for target in target_nodes:
                    W[new_node, target] = np.random.uniform(-1, 1)
                    W[target, new_node] = np.random.uniform(-1, 1)
                    
            except ValueError:
                # Fallback: random connections if sampling fails
                for _ in range(n_connections):
                    target = np.random.choice(new_node)
                    W[new_node, target] = np.random.uniform(-1, 1)
                    W[target, new_node] = np.random.uniform(-1, 1)
    
    return W

def create_random_topology(n_reservoir: int, sparsity: float) -> np.ndarray:
    """
    🎲 Create Random Topology (Erdős-Rényi Model)
    
    Creates a random network where each possible edge exists with
    probability determined by the sparsity parameter.
    
    Args:
        n_reservoir: Number of neurons
        sparsity: Connection probability
        
    Returns:
        np.ndarray: Random topology adjacency matrix
        
    Research Background:
    ===================
    Erdős-Rényi random networks provide baseline connectivity patterns
    for comparison with structured topologies in reservoir computing studies.
    """
    W = np.zeros((n_reservoir, n_reservoir))
    
    # Create random connections
    for i in range(n_reservoir):
        for j in range(n_reservoir):
            if i != j and np.random.random() < sparsity:
                W[i, j] = np.random.uniform(-1, 1)
    
    return W

def create_custom_topology(connectivity_mask: np.ndarray) -> np.ndarray:
    """
    🔧 Create Custom Topology from Connectivity Mask
    
    Creates a topology from a user-provided connectivity mask,
    assigning random weights to specified connections.
    
    Args:
        connectivity_mask: Binary matrix indicating desired connections
        
    Returns:
        np.ndarray: Custom topology with weights assigned to mask connections
        
    Research Background:
    ===================
    Allows implementation of specialized topologies based on domain knowledge
    or specific reservoir computing architectural requirements.
    """
    if connectivity_mask.ndim != 2 or connectivity_mask.shape[0] != connectivity_mask.shape[1]:
        raise ValueError("Connectivity mask must be a square matrix")
    
    W = np.zeros_like(connectivity_mask, dtype=float)
    
    # Assign random weights where mask indicates connections
    mask_positions = connectivity_mask != 0
    n_connections = np.sum(mask_positions)
    
    if n_connections > 0:
        weights = np.random.uniform(-1, 1, n_connections)
        W[mask_positions] = weights
    
    return W

# ================================
# TOPOLOGY ANALYSIS FUNCTIONS
# ================================

def scale_spectral_radius(W: np.ndarray, target_radius: float) -> np.ndarray:
    """
    ⚖️ Scale Matrix to Target Spectral Radius
    
    Rescales a weight matrix to achieve the desired spectral radius
    while preserving the connectivity pattern and relative weight magnitudes.
    
    Args:
        W: Input weight matrix
        target_radius: Desired spectral radius
        
    Returns:
        np.ndarray: Scaled weight matrix
        
    Research Background:
    ===================
    Spectral radius control is crucial for ESP satisfaction in reservoir computing.
    This scaling preserves topology while ensuring desired stability properties.
    """
    try:
        # Compute current spectral radius
        current_radius = np.max(np.abs(eigvals(W)))
        
        if current_radius < 1e-12:
            # Matrix is essentially zero or very close to zero
            warnings.warn("Matrix has very small spectral radius, scaling may be unreliable")
            return W
        
        # Scale to target radius
        scaling_factor = target_radius / current_radius
        W_scaled = W * scaling_factor
        
        return W_scaled
        
    except Exception as e:
        logger.error(f"Spectral radius scaling failed: {e}")
        return W  # Return original matrix if scaling fails

def analyze_topology(W: np.ndarray) -> Dict[str, Any]:
    """
    📊 Comprehensive Topology Analysis
    
    Analyzes various properties of a network topology including
    connectivity metrics, spectral properties, and structural characteristics.
    
    Args:
        W: Weight matrix to analyze
        
    Returns:
        Dict: Comprehensive topology analysis results
        
    Research Background:
    ===================
    Network analysis metrics commonly used in complex networks research
    and reservoir computing topology studies for performance prediction.
    """
    try:
        n = W.shape[0]
        results = {'matrix_size': n}
        
        # Basic connectivity metrics
        binary_W = (W != 0).astype(int)
        total_possible = n * (n - 1)  # Excluding self-loops
        
        results['n_connections'] = np.sum(binary_W)
        results['density'] = results['n_connections'] / total_possible if total_possible > 0 else 0
        results['sparsity'] = 1 - results['density']
        
        # Degree analysis
        in_degrees = np.sum(binary_W, axis=0)
        out_degrees = np.sum(binary_W, axis=1)
        total_degrees = in_degrees + out_degrees
        
        results['degree_stats'] = {
            'mean_in_degree': np.mean(in_degrees),
            'mean_out_degree': np.mean(out_degrees),
            'mean_total_degree': np.mean(total_degrees),
            'degree_std': np.std(total_degrees),
            'max_degree': np.max(total_degrees),
            'min_degree': np.min(total_degrees)
        }
        
        # Spectral analysis
        eigenvals = eigvals(W)
        spectral_radius = np.max(np.abs(eigenvals))
        
        results['spectral_properties'] = {
            'spectral_radius': spectral_radius,
            'largest_eigenvalue': eigenvals[np.argmax(np.abs(eigenvals))],
            'trace': np.trace(W),
            'determinant': np.linalg.det(W) if n <= 100 else 'not_computed',  # Expensive for large matrices
            'condition_number': np.linalg.cond(W) if n <= 100 else 'not_computed'
        }
        
        # Weight statistics
        nonzero_weights = W[W != 0]
        if len(nonzero_weights) > 0:
            results['weight_stats'] = {
                'mean_weight': np.mean(nonzero_weights),
                'weight_std': np.std(nonzero_weights),
                'weight_range': [np.min(nonzero_weights), np.max(nonzero_weights)],
                'positive_weights': np.sum(nonzero_weights > 0),
                'negative_weights': np.sum(nonzero_weights < 0),
                'weight_balance': np.sum(nonzero_weights)
            }
        
        # Structural properties (for smaller networks)
        if n <= 200:
            # Path length analysis (computationally expensive)
            try:
                # Convert to binary adjacency for path analysis
                adj_matrix = (W != 0).astype(int)
                
                # Compute shortest path lengths using Floyd-Warshall
                dist_matrix = _floyd_warshall(adj_matrix)
                finite_distances = dist_matrix[np.isfinite(dist_matrix) & (dist_matrix > 0)]
                
                if len(finite_distances) > 0:
                    results['path_properties'] = {
                        'average_path_length': np.mean(finite_distances),
                        'max_path_length': np.max(finite_distances),
                        'connectivity': len(finite_distances) / (total_possible)
                    }
                
                # Clustering coefficient (simplified)
                clustering_coeffs = []
                for i in range(n):
                    neighbors = np.where(adj_matrix[i, :])[0]
                    if len(neighbors) >= 2:
                        # Count connections among neighbors
                        neighbor_connections = 0
                        for j in neighbors:
                            for k in neighbors:
                                if j != k and adj_matrix[j, k]:
                                    neighbor_connections += 1
                        
                        possible_connections = len(neighbors) * (len(neighbors) - 1)
                        clustering_coeffs.append(neighbor_connections / possible_connections)
                
                if clustering_coeffs:
                    results['clustering_coefficient'] = np.mean(clustering_coeffs)
                    
            except Exception as e:
                logger.warning(f"Structural analysis failed: {e}")
        
        # Topology classification heuristics
        results['topology_classification'] = _classify_topology(results)
        
        return results
        
    except Exception as e:
        logger.error(f"Topology analysis failed: {e}")
        return {'error': str(e), 'matrix_size': W.shape[0] if W.ndim == 2 else 0}

def _floyd_warshall(adj_matrix: np.ndarray) -> np.ndarray:
    """Floyd-Warshall algorithm for all-pairs shortest paths"""
    n = adj_matrix.shape[0]
    dist = adj_matrix.astype(float)
    dist[dist == 0] = np.inf  # No connection
    np.fill_diagonal(dist, 0)  # Distance to self is 0
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
    
    return dist

def _classify_topology(analysis_results: Dict[str, Any]) -> str:
    """Classify topology type based on analysis results"""
    try:
        density = analysis_results.get('density', 0)
        degree_stats = analysis_results.get('degree_stats', {})
        degree_std = degree_stats.get('degree_std', 0)
        mean_degree = degree_stats.get('mean_total_degree', 0)
        
        # Heuristic classification
        if density > 0.8:
            return 'dense'
        elif density < 0.01:
            return 'very_sparse'
        elif degree_std / (mean_degree + 1e-6) > 2.0:  # High degree variability
            return 'scale_free_like'
        elif 'clustering_coefficient' in analysis_results and analysis_results['clustering_coefficient'] > 0.3:
            return 'small_world_like'
        elif 0.05 < density < 0.2:
            return 'random_like'
        else:
            return 'custom'
            
    except Exception:
        return 'unknown'

# Export main topology functions
__all__ = [
    'create_topology',
    'create_ring_topology',
    'create_small_world_topology',
    'create_scale_free_topology',
    'create_random_topology',
    'create_custom_topology',
    'scale_spectral_radius',
    'analyze_topology'
]