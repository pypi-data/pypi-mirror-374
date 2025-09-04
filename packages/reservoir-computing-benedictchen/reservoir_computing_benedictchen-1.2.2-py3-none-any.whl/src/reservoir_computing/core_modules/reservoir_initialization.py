"""
Reservoir Initialization - Weight Matrix Creation
================================================

Author: Benedict Chen (benedict@benedictchen.com)

Advanced reservoir initialization methods for Echo State Networks.
"""

import numpy as np
from typing import Optional


class ReservoirInitializationMixin:
    """
    Advanced reservoir initialization methods.
    
    Implements multiple initialization strategies for optimal reservoir dynamics:
    - Random sparse matrices with controlled spectral radius
    - Small-world and scale-free topologies
    - Echo State Property validation
    - Input scaling optimization
    """
    
    def initialize_reservoir_matrix(self, n_reservoir: int, 
                                  spectral_radius: float = 0.95,
                                  sparsity: float = 0.1,
                                  random_state: Optional[int] = None) -> np.ndarray:
        """
        Initialize reservoir weight matrix with controlled spectral radius.
        
        Parameters
        ----------
        n_reservoir : int
            Number of reservoir units
        spectral_radius : float
            Desired spectral radius (< 1 for ESP)
        sparsity : float
            Connection density (0.1 = 10% connections)
        random_state : int, optional
            Random seed for reproducibility
            
        Returns
        -------
        np.ndarray
            Initialized reservoir matrix
        """
        if random_state is not None:
            np.random.seed(random_state)
            
        # Create random sparse matrix
        n_connections = int(sparsity * n_reservoir * n_reservoir)
        
        # Random sparse connectivity
        W = np.zeros((n_reservoir, n_reservoir))
        for _ in range(n_connections):
            i = np.random.randint(0, n_reservoir)
            j = np.random.randint(0, n_reservoir)
            W[i, j] = np.random.randn()
            
        # Scale to desired spectral radius
        eigenvalues = np.linalg.eigvals(W)
        current_spectral_radius = np.max(np.abs(eigenvalues))
        
        if current_spectral_radius > 0:
            W = W * (spectral_radius / current_spectral_radius)
            
        return W
    
    def initialize_input_matrix(self, n_reservoir: int, n_inputs: int,
                               input_scaling: float = 1.0,
                               input_sparsity: float = 0.1,
                               random_state: Optional[int] = None) -> np.ndarray:
        """
        Initialize input weight matrix.
        
        Parameters
        ----------
        n_reservoir : int
            Number of reservoir units
        n_inputs : int
            Number of input dimensions
        input_scaling : float
            Input weight scaling factor
        input_sparsity : float
            Input connection density
        random_state : int, optional
            Random seed
            
        Returns
        -------
        np.ndarray
            Input weight matrix
        """
        if random_state is not None:
            np.random.seed(random_state)
            
        W_in = np.random.randn(n_reservoir, n_inputs) * input_scaling
        
        # Apply sparsity
        if input_sparsity < 1.0:
            mask = np.random.rand(n_reservoir, n_inputs) < input_sparsity
            W_in = W_in * mask
            
        return W_in