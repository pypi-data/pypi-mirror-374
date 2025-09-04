#!/usr/bin/env python3
"""
🧪 Comprehensive Test Suite for Reservoir Computing
=================================================

Comprehensive test coverage for reservoir computing package addressing
the critical testing gap identified in package analysis.

Current coverage: ~0.2% (77 test lines / 38,489 source lines)
Target coverage: >80% with focus on core functionality

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Jaeger (2001) Echo State Networks, Maass (2002) Liquid State Machines
"""

import pytest
import numpy as np
import reservoir_computing
from reservoir_computing.core import EchoStateNetwork, ReservoirTheoryMixin
from reservoir_computing.core_modules.reservoir_initialization import ReservoirInitializationMixin
from reservoir_computing.core_modules.state_updates import StateUpdateMixin
from reservoir_computing.core_modules.training_methods import TrainingMixin

# Import shared testing utilities
import sys
sys.path.append('../../../shared')
from shared.testing.test_helpers import create_test_data, time_function
from shared.testing.fixtures import sample_time_series
from shared.utils.data_validation import validate_array_shape


class TestEchoStateNetworkCore:
    """Test core Echo State Network functionality"""
    
    def test_esn_initialization(self):
        """Test ESN initialization with various parameters"""
        # Basic initialization
        esn = EchoStateNetwork(n_reservoir=100, spectral_radius=0.9)
        assert esn.n_reservoir == 100
        assert esn.spectral_radius == 0.9
        assert hasattr(esn, 'W_in')
        assert hasattr(esn, 'W_reservoir')
        
        # Test different initialization methods
        esn_uniform = EchoStateNetwork(
            n_reservoir=50, 
            reservoir_init_method='uniform'
        )
        assert esn_uniform.W_reservoir.shape == (50, 50)
        
        esn_sparse = EchoStateNetwork(
            n_reservoir=50, 
            reservoir_init_method='sparse',
            connectivity=0.1
        )
        # Check sparsity
        density = np.count_nonzero(esn_sparse.W_reservoir) / (50 * 50)
        assert density <= 0.15  # Allow some tolerance
    
    def test_esn_spectral_radius_scaling(self):
        """Test spectral radius scaling functionality"""
        esn = EchoStateNetwork(n_reservoir=100, spectral_radius=0.8)
        
        # Check spectral radius is approximately correct
        eigenvals = np.linalg.eigvals(esn.W_reservoir)
        actual_spectral_radius = np.max(np.abs(eigenvals))
        assert abs(actual_spectral_radius - 0.8) < 0.1
    
    def test_esn_reservoir_states(self):
        """Test reservoir state computation"""
        esn = EchoStateNetwork(n_reservoir=100, n_inputs=3)
        
        # Test single state update
        input_data = np.random.randn(10, 3)  # 10 time steps, 3 inputs
        states = esn.compute_reservoir_states(input_data)
        
        assert states.shape == (10, 100)  # 10 time steps, 100 reservoir units
        assert np.all(np.isfinite(states))
    
    def test_esn_training(self):
        """Test ESN training with regression tasks"""
        # Create synthetic time series data
        time_series = sample_time_series(length=200, n_channels=2)
        X_train = time_series[:-1]  # Input: all but last timestep
        y_train = time_series[1:]   # Target: shifted by one timestep
        
        esn = EchoStateNetwork(n_reservoir=100, n_inputs=2, n_outputs=2)
        
        # Train the ESN
        esn.fit(X_train, y_train)
        
        # Check that output weights were learned
        assert hasattr(esn, 'W_out')
        assert esn.W_out.shape[1] == 2  # 2 outputs
        
        # Test prediction
        X_test = time_series[:50]
        y_pred = esn.predict(X_test)
        assert y_pred.shape == (50, 2)
        assert np.all(np.isfinite(y_pred))


class TestReservoirTheoryMixin:
    """Test reservoir theory mathematical foundations"""
    
    def test_echo_state_property(self):
        """Test echo state property validation"""
        class TestESN(ReservoirTheoryMixin):
            def __init__(self):
                self.spectral_radius = 0.9
                self.W_reservoir = np.random.randn(100, 100) * 0.1
        
        esn = TestESN()
        has_esp = esn.check_echo_state_property()
        
        # With spectral radius < 1, should have echo state property
        assert has_esp is True
    
    def test_memory_capacity_estimation(self):
        """Test memory capacity estimation"""
        class TestESN(ReservoirTheoryMixin):
            def __init__(self):
                self.n_reservoir = 100
                self.spectral_radius = 0.9
        
        esn = TestESN()
        memory_capacity = esn.estimate_memory_capacity()
        
        # Memory capacity should be reasonable for reservoir size
        assert 0 < memory_capacity <= esn.n_reservoir
    
    def test_separation_property(self):
        """Test separation property computation"""
        class TestESN(ReservoirTheoryMixin):
            def __init__(self):
                self.n_reservoir = 50
        
        esn = TestESN()
        
        # Create two different input sequences
        u1 = np.random.randn(20, 3)
        u2 = np.random.randn(20, 3) + 1.0  # Different sequence
        
        separation = esn.compute_separation_property(u1, u2)
        assert separation >= 0  # Separation should be non-negative


class TestReservoirInitialization:
    """Test reservoir initialization methods"""
    
    def test_uniform_initialization(self):
        """Test uniform random initialization"""
        class TestInit(ReservoirInitializationMixin):
            pass
        
        init = TestInit()
        W = init.initialize_reservoir_uniform(100, connectivity=1.0, scale=0.5)
        
        assert W.shape == (100, 100)
        assert np.all(W >= -0.5) and np.all(W <= 0.5)
    
    def test_sparse_initialization(self):
        """Test sparse random initialization"""
        class TestInit(ReservoirInitializationMixin):
            pass
        
        init = TestInit()
        W = init.initialize_reservoir_sparse(100, connectivity=0.1, scale=0.8)
        
        assert W.shape == (100, 100)
        density = np.count_nonzero(W) / (100 * 100)
        assert density <= 0.15  # Should be approximately 10% +- tolerance
    
    def test_small_world_initialization(self):
        """Test small-world network initialization"""
        class TestInit(ReservoirInitializationMixin):
            pass
        
        init = TestInit()
        W = init.initialize_reservoir_small_world(100, k=4, p=0.1)
        
        assert W.shape == (100, 100)
        assert np.all(np.isfinite(W))
    
    def test_scale_free_initialization(self):
        """Test scale-free network initialization"""
        class TestInit(ReservoirInitializationMixin):
            pass
        
        init = TestInit()
        W = init.initialize_reservoir_scale_free(100, m=2)
        
        assert W.shape == (100, 100)
        assert np.all(np.isfinite(W))


class TestStateUpdateMethods:
    """Test different state update methods"""
    
    def test_tanh_update(self):
        """Test hyperbolic tangent state update"""
        class TestUpdate(StateUpdateMixin):
            pass
        
        updater = TestUpdate()
        
        # Create test data
        current_state = np.random.randn(100)
        input_signal = np.random.randn(3)
        W_in = np.random.randn(100, 3) * 0.1
        W_reservoir = np.random.randn(100, 100) * 0.1
        
        new_state = updater.update_state_tanh(
            current_state, input_signal, W_in, W_reservoir
        )
        
        assert new_state.shape == (100,)
        assert np.all(new_state >= -1) and np.all(new_state <= 1)  # tanh bounds
    
    def test_leaky_integrator_update(self):
        """Test leaky integrator state update"""
        class TestUpdate(StateUpdateMixin):
            pass
        
        updater = TestUpdate()
        
        current_state = np.random.randn(50)
        input_signal = np.random.randn(2)
        W_in = np.random.randn(50, 2) * 0.1
        W_reservoir = np.random.randn(50, 50) * 0.1
        
        new_state = updater.update_state_leaky_integrator(
            current_state, input_signal, W_in, W_reservoir, leak_rate=0.1
        )
        
        assert new_state.shape == (50,)
        assert np.all(np.isfinite(new_state))


class TestTrainingMethods:
    """Test different training methods for reservoir computing"""
    
    def test_ridge_regression_training(self):
        """Test ridge regression training method"""
        class TestTraining(TrainingMixin):
            pass
        
        trainer = TestTraining()
        
        # Create training data
        X = np.random.randn(100, 80)  # 100 samples, 80 features
        y = np.random.randn(100, 3)   # 100 samples, 3 outputs
        
        W_out = trainer.train_ridge_regression(X, y, reg_param=0.001)
        
        assert W_out.shape == (80, 3)  # 80 inputs to 3 outputs
        assert np.all(np.isfinite(W_out))
    
    def test_pseudoinverse_training(self):
        """Test pseudoinverse training method"""
        class TestTraining(TrainingMixin):
            pass
        
        trainer = TestTraining()
        
        X = np.random.randn(100, 50)
        y = np.random.randn(100, 2)
        
        W_out = trainer.train_pseudoinverse(X, y)
        
        assert W_out.shape == (50, 2)
        assert np.all(np.isfinite(W_out))
    
    def test_lms_training(self):
        """Test least mean squares (LMS) adaptive training"""
        class TestTraining(TrainingMixin):
            pass
        
        trainer = TestTraining()
        
        X = np.random.randn(200, 30)  # More samples for online learning
        y = np.random.randn(200, 1)
        
        W_out, errors = trainer.train_lms_adaptive(
            X, y, learning_rate=0.01, max_epochs=50
        )
        
        assert W_out.shape == (30, 1)
        assert len(errors) <= 50  # Should converge or reach max epochs
        assert errors[-1] < errors[0]  # Error should decrease


class TestLiquidStateMachine:
    """Test Liquid State Machine functionality (if implemented)"""
    
    def test_lsm_basic_functionality(self):
        """Test basic LSM functionality"""
        # Check if LSM is available
        try:
            from reservoir_computing.liquid_state_machine import LiquidStateMachine
            
            lsm = LiquidStateMachine(n_neurons=200)
            assert lsm.n_neurons == 200
            
            # Test with spike train input
            spike_input = np.random.choice([0, 1], size=(100, 10), p=[0.9, 0.1])
            states = lsm.compute_liquid_states(spike_input)
            
            assert states.shape[0] == 100  # Same number of time steps
            assert np.all(np.isfinite(states))
            
        except ImportError:
            # LSM not implemented yet - create placeholder test
            pytest.skip("LiquidStateMachine not yet implemented")


class TestPerformanceBenchmarks:
    """Performance and benchmarking tests"""
    
    def test_esn_training_performance(self):
        """Benchmark ESN training performance"""
        esn = EchoStateNetwork(n_reservoir=500, n_inputs=10, n_outputs=5)
        
        # Create larger dataset
        X_train = np.random.randn(1000, 10)
        y_train = np.random.randn(1000, 5)
        
        # Time the training
        timing_results = time_function(esn.fit, X_train, y_train, n_runs=1)
        
        # Training should complete reasonably quickly
        assert timing_results['mean_time'] < 10.0  # Less than 10 seconds
        
        # Memory usage should be reasonable
        prediction_results = time_function(esn.predict, X_train[:100], n_runs=1)
        assert prediction_results['mean_time'] < 1.0  # Prediction should be fast
    
    def test_esn_scalability(self):
        """Test ESN scalability with different reservoir sizes"""
        reservoir_sizes = [50, 100, 200]
        
        for n_reservoir in reservoir_sizes:
            esn = EchoStateNetwork(n_reservoir=n_reservoir, n_inputs=5)
            
            # Test state computation scales reasonably
            input_data = np.random.randn(50, 5)
            timing_results = time_function(
                esn.compute_reservoir_states, input_data, n_runs=1
            )
            
            # Larger reservoirs should not be exponentially slower
            assert timing_results['mean_time'] < n_reservoir * 0.001  # Rough scaling check


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_parameters(self):
        """Test handling of invalid parameters"""
        # Spectral radius should be positive
        with pytest.raises((ValueError, AssertionError)):
            EchoStateNetwork(n_reservoir=100, spectral_radius=-0.5)
        
        # Reservoir size should be positive
        with pytest.raises((ValueError, AssertionError)):
            EchoStateNetwork(n_reservoir=0)
    
    def test_mismatched_dimensions(self):
        """Test handling of mismatched input dimensions"""
        esn = EchoStateNetwork(n_reservoir=100, n_inputs=3)
        
        # Wrong input dimension
        wrong_input = np.random.randn(10, 5)  # 5 inputs instead of 3
        
        with pytest.raises((ValueError, AssertionError)):
            esn.compute_reservoir_states(wrong_input)
    
    def test_empty_data(self):
        """Test handling of empty or invalid data"""
        esn = EchoStateNetwork(n_reservoir=50, n_inputs=2)
        
        # Empty input
        with pytest.raises((ValueError, AssertionError)):
            esn.compute_reservoir_states(np.array([]).reshape(0, 2))


# Integration test combining multiple components
class TestIntegration:
    """Integration tests combining multiple reservoir computing components"""
    
    def test_full_pipeline(self):
        """Test complete reservoir computing pipeline"""
        # Generate time series prediction task
        time_series = sample_time_series(length=500, n_channels=1, frequency=0.05)
        
        # Prepare data
        lookback = 10
        X = np.array([time_series[i:i+lookback].flatten() 
                     for i in range(len(time_series)-lookback-1)])
        y = time_series[lookback+1:].flatten()
        
        # Split data
        split_idx = int(0.7 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Create and train ESN
        esn = EchoStateNetwork(
            n_reservoir=200, 
            n_inputs=lookback, 
            n_outputs=1,
            spectral_radius=0.9,
            input_scaling=0.1
        )
        
        esn.fit(X_train, y_train.reshape(-1, 1))
        
        # Make predictions
        y_pred = esn.predict(X_test)
        
        # Evaluate performance
        mse = np.mean((y_test.reshape(-1, 1) - y_pred) ** 2)
        
        # Performance should be reasonable for this simple task
        assert mse < 1.0  # Reasonable MSE threshold
        assert np.all(np.isfinite(y_pred))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])