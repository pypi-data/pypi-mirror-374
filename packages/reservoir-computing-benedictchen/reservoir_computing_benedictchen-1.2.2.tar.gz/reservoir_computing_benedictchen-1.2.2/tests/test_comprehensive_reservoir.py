#!/usr/bin/env python3
"""
🧪 Comprehensive Reservoir Computing Test Suite
===============================================

Complete test coverage for reservoir computing algorithms including:
- Echo State Networks (ESN) - Jaeger (2001)
- Liquid State Machines (LSM) - Maass et al. (2002)
- Reservoir theory and dynamics
- Performance optimization

This addresses the critical 6.6% test coverage (6/97 files).

Author: Benedict Chen (benedict@benedictchen.com)
Research Foundation: Jaeger (2001), Maass et al. (2002), Lukoševičius & Jaeger (2009)
"""

import pytest
import numpy as np
import torch
import sys
from pathlib import Path

# Add package to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from reservoir_computing.echo_state_network import EchoStateNetwork, ESNConfig
    from reservoir_computing.liquid_state_machine import LiquidStateMachine, LSMConfig
    from reservoir_computing.reservoir_theory import ReservoirTheory
    from reservoir_computing.dynamics import ReservoirDynamics
    from reservoir_computing.optimization import ReservoirOptimizer
except ImportError as e:
    pytest.skip(f"Reservoir computing modules not available: {e}", allow_module_level=True)


class TestEchoStateNetwork:
    """Test Echo State Network implementation."""
    
    def test_esn_initialization(self):
        """Test ESN initialization with default parameters."""
        esn = EchoStateNetwork(n_reservoir=100, spectral_radius=0.9)
        
        assert esn.n_reservoir == 100
        assert esn.spectral_radius == 0.9
        assert hasattr(esn, 'W_reservoir')
        assert hasattr(esn, 'W_input')
        assert hasattr(esn, 'W_output')
        
        # Check spectral radius constraint
        eigenvalues = np.linalg.eigvals(esn.W_reservoir)
        max_eigenvalue = np.max(np.abs(eigenvalues))
        assert max_eigenvalue <= esn.spectral_radius + 1e-6
    
    def test_esn_config(self):
        """Test ESN configuration object."""
        config = ESNConfig(
            n_reservoir=50,
            spectral_radius=0.8,
            input_scaling=0.5,
            leak_rate=0.3
        )
        
        esn = EchoStateNetwork(config=config)
        
        assert esn.n_reservoir == 50
        assert esn.spectral_radius == 0.8
        assert esn.input_scaling == 0.5
        assert esn.leak_rate == 0.3
    
    def test_reservoir_state_update(self):
        """Test reservoir state update dynamics."""
        esn = EchoStateNetwork(n_reservoir=20, n_inputs=2)
        
        # Initialize state
        state = np.zeros(esn.n_reservoir)
        input_data = np.array([0.5, -0.3])
        
        # Update state
        new_state = esn.update_state(state, input_data)
        
        assert len(new_state) == esn.n_reservoir
        assert not np.allclose(new_state, state)  # State should change
        assert np.all(np.abs(new_state) < 10)  # Reasonable bounds
    
    def test_memory_capacity(self):
        """Test ESN memory capacity measurement."""
        esn = EchoStateNetwork(n_reservoir=50)
        
        # Generate random input sequence
        np.random.seed(42)
        input_sequence = np.random.randn(200, 1)
        
        # Measure memory capacity
        memory_capacity = esn.measure_memory_capacity(input_sequence, max_delay=10)
        
        assert isinstance(memory_capacity, float)
        assert 0 <= memory_capacity <= 10  # Should be within bounds
        assert memory_capacity > 0  # Should have some memory
    
    def test_esn_training(self):
        """Test ESN training on simple task."""
        esn = EchoStateNetwork(n_reservoir=30, n_inputs=1, n_outputs=1)
        
        # Generate sine wave prediction task
        t = np.linspace(0, 4*np.pi, 200)
        x = np.sin(t).reshape(-1, 1)
        y = np.sin(t + 0.1).reshape(-1, 1)  # Slightly ahead prediction
        
        # Train ESN
        esn.fit(x, y)
        
        # Test prediction
        predictions = esn.predict(x[:50])
        
        assert predictions.shape == (50, 1)
        # Should predict reasonably well
        mse = np.mean((predictions - y[:50])**2)
        assert mse < 0.5  # Reasonable performance
    
    def test_echo_state_property(self):
        """Test echo state property verification."""
        esn = EchoStateNetwork(n_reservoir=20, spectral_radius=0.7)
        
        # Test with different initial states
        input_seq = np.random.randn(50, 2)
        
        state1 = np.random.randn(esn.n_reservoir)
        state2 = np.random.randn(esn.n_reservoir)
        
        # Run sequences
        states1 = esn.run_sequence(input_seq, initial_state=state1)
        states2 = esn.run_sequence(input_seq, initial_state=state2)
        
        # States should converge (echo state property)
        final_diff = np.linalg.norm(states1[-1] - states2[-1])
        initial_diff = np.linalg.norm(state1 - state2)
        
        assert final_diff < initial_diff  # Should converge


class TestLiquidStateMachine:
    """Test Liquid State Machine implementation."""
    
    def test_lsm_initialization(self):
        """Test LSM initialization."""
        lsm = LiquidStateMachine(n_liquid=100, connection_probability=0.2)
        
        assert lsm.n_liquid == 100
        assert lsm.connection_probability == 0.2
        assert hasattr(lsm, 'liquid_weights')
        assert hasattr(lsm, 'input_weights')
    
    def test_spike_generation(self):
        """Test spike generation mechanism."""
        lsm = LiquidStateMachine(n_liquid=20)
        
        # Apply strong input
        input_current = np.ones(lsm.n_inputs) * 5.0
        spikes = lsm.generate_spikes(input_current, duration_ms=50)
        
        assert spikes.shape[1] == lsm.n_liquid
        assert np.any(spikes)  # Should generate some spikes
    
    def test_liquid_dynamics(self):
        """Test liquid dynamics simulation."""
        lsm = LiquidStateMachine(n_liquid=30)
        
        # Simulate step
        membrane_potentials = np.random.randn(lsm.n_liquid) * 0.1
        input_spikes = np.random.randint(0, 2, lsm.n_inputs)
        
        new_potentials = lsm.simulate_step(membrane_potentials, input_spikes)
        
        assert len(new_potentials) == lsm.n_liquid
        assert np.all(np.isfinite(new_potentials))  # Should be finite
    
    def test_temporal_integration(self):
        """Test temporal integration capability."""
        lsm = LiquidStateMachine(n_liquid=50)
        
        # Create temporal pattern
        pattern = np.array([1, 0, 1, 1, 0])
        
        response = lsm.process_temporal_pattern(pattern, dt=1.0)
        
        assert len(response) == len(pattern)
        assert np.all(np.isfinite(response))
    
    def test_separation_property(self):
        """Test separation property of liquid."""
        lsm = LiquidStateMachine(n_liquid=40)
        
        # Two different input patterns
        pattern1 = np.array([1, 0, 1, 0, 1])
        pattern2 = np.array([0, 1, 0, 1, 0])
        
        response1 = lsm.process_temporal_pattern(pattern1)
        response2 = lsm.process_temporal_pattern(pattern2)
        
        # Responses should be different (separation property)
        separation = np.linalg.norm(response1 - response2)
        assert separation > 0.1  # Should be separable


class TestReservoirTheory:
    """Test reservoir computing theoretical foundations."""
    
    def test_spectral_radius_analysis(self):
        """Test spectral radius effects on dynamics."""
        theory = ReservoirTheory()
        
        # Test different spectral radii
        radii = [0.5, 0.9, 1.1, 1.5]
        stability_measures = []
        
        for radius in radii:
            W = theory.generate_reservoir_matrix(size=20, spectral_radius=radius)
            stability = theory.analyze_stability(W)
            stability_measures.append(stability)
        
        # Lower spectral radii should be more stable
        assert stability_measures[0] > stability_measures[-1]
    
    def test_memory_capacity_bounds(self):
        """Test theoretical memory capacity bounds."""
        theory = ReservoirTheory()
        
        reservoir_sizes = [10, 50, 100, 200]
        capacities = []
        
        for size in reservoir_sizes:
            # Theoretical upper bound
            upper_bound = theory.memory_capacity_upper_bound(size)
            capacities.append(upper_bound)
        
        # Capacity should increase with reservoir size
        assert all(capacities[i] <= capacities[i+1] for i in range(len(capacities)-1))
        assert capacities[0] <= reservoir_sizes[0]  # Can't exceed reservoir size
    
    def test_linear_separation_property(self):
        """Test linear separation property analysis."""
        theory = ReservoirTheory()
        
        # Generate test patterns
        patterns = [
            np.array([1, 0, 1, 0]),
            np.array([0, 1, 0, 1]),
            np.array([1, 1, 0, 0]),
            np.array([0, 0, 1, 1])
        ]
        
        separation_score = theory.measure_linear_separation(patterns)
        
        assert isinstance(separation_score, float)
        assert separation_score >= 0
    
    def test_fading_memory_property(self):
        """Test fading memory property verification."""
        theory = ReservoirTheory()
        
        # Create reservoir with good fading memory
        W = theory.generate_reservoir_matrix(size=30, spectral_radius=0.8)
        
        fading_rate = theory.measure_fading_memory(W)
        
        assert isinstance(fading_rate, float)
        assert fading_rate > 0  # Should have exponential fading


class TestReservoirDynamics:
    """Test reservoir dynamics and state evolution."""
    
    def test_nonlinear_dynamics(self):
        """Test nonlinear activation functions."""
        dynamics = ReservoirDynamics(activation='tanh')
        
        # Test state update
        state = np.array([0.5, -1.2, 2.0, -0.8])
        new_state = dynamics.apply_activation(state)
        
        assert len(new_state) == len(state)
        assert np.all(np.abs(new_state) <= 1)  # Tanh bounds
    
    def test_leaky_integration(self):
        """Test leaky integrator dynamics."""
        dynamics = ReservoirDynamics(leak_rate=0.3)
        
        prev_state = np.array([1.0, -0.5, 0.8])
        new_activation = np.array([0.2, 0.7, -0.3])
        
        integrated_state = dynamics.leaky_integration(prev_state, new_activation)
        
        assert len(integrated_state) == len(prev_state)
        # Should be weighted combination
        assert not np.allclose(integrated_state, prev_state)
        assert not np.allclose(integrated_state, new_activation)
    
    def test_noise_injection(self):
        """Test noise injection effects."""
        dynamics = ReservoirDynamics(noise_level=0.1)
        
        # Clean state
        clean_state = np.zeros(10)
        noisy_state = dynamics.add_noise(clean_state)
        
        assert len(noisy_state) == len(clean_state)
        noise = noisy_state - clean_state
        assert np.std(noise) > 0  # Should add noise
        assert np.std(noise) < 0.2  # Reasonable noise level
    
    def test_washout_period(self):
        """Test washout period handling."""
        dynamics = ReservoirDynamics()
        esn = EchoStateNetwork(n_reservoir=20)
        
        # Random input sequence
        inputs = np.random.randn(100, 2)
        
        states, washout_states = dynamics.run_with_washout(esn, inputs, washout=20)
        
        assert len(states) == 80  # After washout
        assert len(washout_states) == 20  # Washout states
        assert states.shape[1] == esn.n_reservoir


class TestReservoirOptimization:
    """Test reservoir optimization techniques."""
    
    def test_spectral_radius_optimization(self):
        """Test spectral radius optimization."""
        optimizer = ReservoirOptimizer()
        
        # Simple target task
        def performance_fn(radius):
            esn = EchoStateNetwork(n_reservoir=20, spectral_radius=radius)
            # Dummy performance measure
            return -abs(radius - 0.9)  # Best at 0.9
        
        optimal_radius = optimizer.optimize_spectral_radius(performance_fn, bounds=(0.1, 1.5))
        
        assert 0.8 < optimal_radius < 1.0  # Should find optimum near 0.9
    
    def test_input_scaling_optimization(self):
        """Test input scaling optimization."""
        optimizer = ReservoirOptimizer()
        
        # Generate training data
        t = np.linspace(0, 2*np.pi, 100)
        X = np.sin(t).reshape(-1, 1)
        y = np.cos(t).reshape(-1, 1)
        
        best_scaling = optimizer.optimize_input_scaling(X, y, n_reservoir=30)
        
        assert isinstance(best_scaling, float)
        assert best_scaling > 0
    
    def test_hyperparameter_grid_search(self):
        """Test grid search over multiple hyperparameters."""
        optimizer = ReservoirOptimizer()
        
        # Define parameter grid
        param_grid = {
            'spectral_radius': [0.7, 0.9, 1.1],
            'input_scaling': [0.1, 0.5, 1.0],
            'leak_rate': [0.1, 0.3, 0.7]
        }
        
        # Simple sine wave task
        t = np.linspace(0, 2*np.pi, 50)
        X = np.sin(t).reshape(-1, 1)
        y = np.sin(t + 0.1).reshape(-1, 1)
        
        best_params, best_score = optimizer.grid_search(X, y, param_grid, n_reservoir=20)
        
        assert isinstance(best_params, dict)
        assert 'spectral_radius' in best_params
        assert 'input_scaling' in best_params
        assert 'leak_rate' in best_params
        assert isinstance(best_score, float)
    
    def test_bayesian_optimization(self):
        """Test Bayesian optimization of hyperparameters."""
        optimizer = ReservoirOptimizer()
        
        # Define bounds
        bounds = {
            'spectral_radius': (0.1, 1.5),
            'input_scaling': (0.01, 2.0)
        }
        
        # Simple task
        t = np.linspace(0, np.pi, 30)
        X = np.sin(t).reshape(-1, 1)
        y = np.cos(t).reshape(-1, 1)
        
        best_params, history = optimizer.bayesian_optimization(
            X, y, bounds, n_calls=5, n_reservoir=15
        )
        
        assert isinstance(best_params, dict)
        assert len(history) == 5
        assert all(score is not None for score in history)


class TestReservoirApplications:
    """Test reservoir computing applications."""
    
    def test_time_series_prediction(self):
        """Test time series prediction task."""
        esn = EchoStateNetwork(n_reservoir=50, n_inputs=1, n_outputs=1)
        
        # Generate Mackey-Glass time series (standard benchmark)
        def mackey_glass(length, tau=17):
            x = np.zeros(length)
            x[0] = 1.2
            for i in range(1, length):
                if i < tau:
                    x[i] = x[i-1] + 0.2 * x[i-1] / (1 + x[i-1]**10) - 0.1 * x[i-1]
                else:
                    x[i] = x[i-1] + 0.2 * x[i-tau] / (1 + x[i-tau]**10) - 0.1 * x[i-1]
            return x
        
        # Generate data
        data = mackey_glass(300)
        X = data[:-1].reshape(-1, 1)
        y = data[1:].reshape(-1, 1)
        
        # Train and test
        split = 200
        esn.fit(X[:split], y[:split])
        predictions = esn.predict(X[split:split+20])
        
        # Calculate performance
        mse = np.mean((predictions - y[split:split+20])**2)
        assert mse < 0.1  # Should achieve good performance
    
    def test_chaotic_system_modeling(self):
        """Test modeling chaotic dynamical systems."""
        esn = EchoStateNetwork(n_reservoir=100, spectral_radius=0.95)
        
        # Lorenz system
        def lorenz_system(length, dt=0.01):
            sigma, rho, beta = 10, 28, 8/3
            x, y, z = 1, 1, 1
            trajectory = []
            
            for _ in range(length):
                dx = sigma * (y - x)
                dy = x * (rho - z) - y
                dz = x * y - beta * z
                
                x += dt * dx
                y += dt * dy
                z += dt * dz
                
                trajectory.append([x, y, z])
            
            return np.array(trajectory)
        
        # Generate trajectory
        trajectory = lorenz_system(1000)
        
        # Use XYZ as input to predict next XYZ
        X = trajectory[:-1]
        y = trajectory[1:]
        
        # Train
        split = 600
        esn.fit(X[:split], y[:split])
        
        # Multi-step prediction
        predictions = esn.predict(X[split:split+50])
        
        # Should maintain reasonable dynamics
        pred_variance = np.var(predictions, axis=0)
        true_variance = np.var(y[split:split+50], axis=0)
        
        # Variances should be similar (maintaining dynamics)
        for i in range(3):
            assert 0.5 * true_variance[i] < pred_variance[i] < 2.0 * true_variance[i]
    
    def test_speech_recognition_preprocessing(self):
        """Test speech/audio preprocessing with reservoirs."""
        esn = EchoStateNetwork(n_reservoir=200, n_inputs=13)  # MFCC features
        
        # Simulate MFCC features for speech
        np.random.seed(42)
        n_frames = 100
        mfcc_features = np.random.randn(n_frames, 13)  # 13 MFCC coefficients
        
        # Process through reservoir (unsupervised feature extraction)
        reservoir_states = esn.collect_states(mfcc_features)
        
        assert reservoir_states.shape == (n_frames, esn.n_reservoir)
        
        # Features should be different from input
        correlation = np.corrcoef(mfcc_features.flatten(), 
                                 reservoir_states.flatten())[0, 1]
        assert abs(correlation) < 0.9  # Transformed features
    
    def test_pattern_classification(self):
        """Test pattern classification with reservoir features."""
        esn = EchoStateNetwork(n_reservoir=50, n_inputs=2)
        
        # Generate spiral patterns
        def generate_spiral(n_points, noise=0.1):
            t = np.linspace(0, 4*np.pi, n_points)
            r = t
            x = r * np.cos(t) + np.random.randn(n_points) * noise
            y = r * np.sin(t) + np.random.randn(n_points) * noise
            return np.column_stack([x, y])
        
        # Two spirals (different classes)
        spiral1 = generate_spiral(50, noise=0.5)
        spiral2 = -generate_spiral(50, noise=0.5)  # Opposite direction
        
        X = np.vstack([spiral1, spiral2])
        y = np.array([0]*50 + [1]*50)  # Class labels
        
        # Extract reservoir features
        features = esn.collect_states(X)
        
        # Simple classification test (linear separability in reservoir space)
        from sklearn.linear_model import LogisticRegression
        classifier = LogisticRegression()
        
        # Cross-validation split
        train_idx = list(range(0, 40)) + list(range(50, 90))
        test_idx = list(range(40, 50)) + list(range(90, 100))
        
        classifier.fit(features[train_idx], y[train_idx])
        accuracy = classifier.score(features[test_idx], y[test_idx])
        
        assert accuracy > 0.7  # Should achieve reasonable classification


# Integration and benchmark tests
class TestReservoirIntegration:
    """Integration tests combining multiple reservoir components."""
    
    def test_esn_lsm_comparison(self):
        """Compare ESN and LSM on same task."""
        # Same network size
        n_reservoir = 50
        esn = EchoStateNetwork(n_reservoir=n_reservoir, n_inputs=1, n_outputs=1)
        lsm = LiquidStateMachine(n_liquid=n_reservoir, n_inputs=1)
        
        # Same task: sine wave prediction
        t = np.linspace(0, 2*np.pi, 100)
        X = np.sin(t).reshape(-1, 1)
        y = np.sin(t + 0.2).reshape(-1, 1)
        
        # Train both
        esn.fit(X[:70], y[:70])
        # LSM requires different training approach
        lsm_features = lsm.extract_features(X[:70])
        lsm.train_readout(lsm_features, y[:70])
        
        # Test both
        esn_pred = esn.predict(X[70:])
        lsm_pred = lsm.predict(X[70:])
        
        # Both should perform reasonably
        esn_mse = np.mean((esn_pred - y[70:])**2)
        lsm_mse = np.mean((lsm_pred - y[70:])**2)
        
        assert esn_mse < 1.0
        assert lsm_mse < 1.0
    
    def test_reservoir_ensemble(self):
        """Test ensemble of multiple reservoirs."""
        # Create ensemble
        ensemble_size = 3
        esns = []
        
        for i in range(ensemble_size):
            esn = EchoStateNetwork(
                n_reservoir=30, 
                spectral_radius=0.8 + 0.1*i,  # Different parameters
                input_scaling=0.5 + 0.2*i
            )
            esns.append(esn)
        
        # Task
        t = np.linspace(0, 3*np.pi, 150)
        X = np.sin(t).reshape(-1, 1)
        y = np.sin(t + 0.15).reshape(-1, 1)
        
        # Train ensemble
        predictions = []
        for esn in esns:
            esn.fit(X[:100], y[:100])
            pred = esn.predict(X[100:])
            predictions.append(pred)
        
        # Ensemble prediction (average)
        ensemble_pred = np.mean(predictions, axis=0)
        
        # Should perform at least as well as individual members
        ensemble_mse = np.mean((ensemble_pred - y[100:])**2)
        individual_mses = [np.mean((pred - y[100:])**2) for pred in predictions]
        
        assert ensemble_mse <= max(individual_mses)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])