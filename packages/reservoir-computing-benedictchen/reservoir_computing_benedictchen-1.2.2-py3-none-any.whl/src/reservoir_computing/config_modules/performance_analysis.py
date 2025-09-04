"""
📊 Performance Analysis Module - AI-Powered ESN Configuration Analysis
======================================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module contains performance analysis and recommendation methods
for Echo State Networks extracted from the original monolithic configuration_optimization.py file.

Based on: Herbert Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"
"""

import numpy as np
from sklearn.metrics import mean_squared_error


class PerformanceAnalysisMixin:
    """
    📊 Performance Analysis Mixin for Echo State Networks
    
    This mixin provides intelligent performance analysis and optimization
    recommendations for Echo State Networks based on research principles.
    
    🌟 Key Features:
    - Configuration health scoring
    - Parameter analysis and recommendations
    - Performance bottleneck detection
    - Preset configuration suggestions
    """
    
    def get_performance_recommendations(self, X_train=None, y_train=None, task_metrics=None):
        """
        📊 Performance Monitoring & Recommendations - AI-Powered Optimization Suggestions
        
        🔬 **Research Background**: This method analyzes current ESN configuration and
        performance to provide intelligent recommendations for parameter improvements
        based on established research principles and empirical best practices.
        
        🎯 **Analysis Framework**:
        ```
        📈 PERFORMANCE ANALYSIS PIPELINE
        
        Current Config → [Analyze Parameters] → [Evaluate Performance] → [Generate Recommendations]
               │                  │                      │                           │
               ↓                  ↓                      ↓                           ↓
        Configuration       Parameter Analysis     Performance Metrics      Optimization
        Summary             vs Best Practices      & Bottleneck Detection   Suggestions
        ```
        
        Args:
            X_train (array, optional): Training data for performance analysis
            y_train (array, optional): Training targets for performance analysis  
            task_metrics (dict, optional): Task-specific performance metrics
            
        Returns:
            dict: Comprehensive recommendations including:
                - 'parameter_analysis': Analysis of current parameters
                - 'performance_issues': Detected performance bottlenecks
                - 'recommendations': Specific optimization suggestions
                - 'preset_suggestions': Recommended preset configurations
                - 'priority_actions': High-impact optimization steps
                
        Example:
            >>> recommendations = esn.get_performance_recommendations(X_train, y_train)
            >>> for rec in recommendations['recommendations']:
            ...     print(f"💡 {rec}")
        """
        
        recommendations = {
            'parameter_analysis': {},
            'performance_issues': [],
            'recommendations': [],
            'preset_suggestions': [],
            'priority_actions': []
        }
        
        # Analyze current configuration
        config = self.get_configuration_summary() if hasattr(self, 'get_configuration_summary') else {}
        
        print("📊 Analyzing current ESN configuration...")
        
        # 1. Spectral Radius Analysis
        sr = getattr(self, 'spectral_radius', 1.0)
        recommendations['parameter_analysis']['spectral_radius'] = {
            'current': sr,
            'status': 'optimal' if 0.5 <= sr <= 1.2 else 'needs_adjustment',
            'guideline': 'Optimal range: 0.5-1.2 for most tasks'
        }
        
        if sr > 1.3:
            recommendations['performance_issues'].append("High spectral radius may cause ESP violation")
            recommendations['recommendations'].append("Reduce spectral radius to 0.8-1.2 range")
            recommendations['priority_actions'].append("CRITICAL: Test Echo State Property validation")
        elif sr < 0.3:
            recommendations['performance_issues'].append("Low spectral radius limits memory capacity")
            recommendations['recommendations'].append("Increase spectral radius to 0.5-0.9 range")
            recommendations['priority_actions'].append("Increase spectral radius for better temporal modeling")
        
        # 2. Reservoir Size Analysis
        n_res = getattr(self, 'n_reservoir', 100)
        recommendations['parameter_analysis']['n_reservoir'] = {
            'current': n_res,
            'status': 'optimal' if 50 <= n_res <= 1000 else 'needs_adjustment'
        }
        
        if X_train is not None:
            n_inputs = X_train.shape[1] if len(X_train.shape) > 1 else 1
            optimal_size_min = n_inputs * 5
            optimal_size_max = n_inputs * 20
            
            if n_res < optimal_size_min:
                recommendations['performance_issues'].append("Reservoir too small for input dimensionality")
                recommendations['recommendations'].append(f"Increase reservoir size to at least {optimal_size_min}")
            elif n_res > optimal_size_max * 2:
                recommendations['performance_issues'].append("Reservoir may be unnecessarily large")
                recommendations['recommendations'].append(f"Consider reducing reservoir size to {optimal_size_max}")
        
        # 3. Noise Level Analysis
        noise = getattr(self, 'noise_level', 0.01)
        recommendations['parameter_analysis']['noise_level'] = {
            'current': noise,
            'status': 'optimal' if 0.001 <= noise <= 0.05 else 'needs_adjustment'
        }
        
        if noise > 0.1:
            recommendations['performance_issues'].append("Excessive noise may degrade performance")
            recommendations['recommendations'].append("Reduce noise level to 0.001-0.05 range")
        elif noise < 0.0001:
            recommendations['recommendations'].append("Consider adding small amount of noise (0.001-0.01) for robustness")
        
        # 4. Activation Function Analysis
        activation = config.get('activation_function', 'tanh')
        recommendations['parameter_analysis']['activation_function'] = {
            'current': activation,
            'alternatives': ['tanh', 'sigmoid', 'relu', 'leaky_relu']
        }
        
        if activation == 'linear':
            recommendations['performance_issues'].append("Linear activation limits nonlinear modeling capability")
            recommendations['recommendations'].append("Switch to 'tanh' or 'sigmoid' for nonlinear tasks")
            recommendations['priority_actions'].append("Change activation function to enable nonlinearity")
        
        # 5. Output Feedback Analysis
        feedback_mode = config.get('output_feedback_mode', 'direct')
        if feedback_mode == 'direct' and n_res > 500:
            recommendations['recommendations'].append("Consider sparse feedback mode for large reservoirs")
        
        # 6. Performance-based analysis (if data provided)
        if X_train is not None and y_train is not None:
            try:
                # Quick performance test
                washout = min(50, len(X_train) // 4)
                if hasattr(self, 'fit') and hasattr(self, 'predict'):
                    self.fit(X_train, y_train, washout=washout, verbose=False)
                    y_pred = self.predict(X_train[washout:], steps=len(X_train)-washout)
                    
                    if hasattr(y_pred, 'shape') and y_pred.shape[0] > 0:
                        mse = mean_squared_error(y_train[washout:len(y_pred)+washout], y_pred)
                        
                        recommendations['parameter_analysis']['performance'] = {
                            'training_mse': mse,
                            'status': 'good' if mse < 0.1 else 'needs_improvement'
                        }
                        
                        if mse > 1.0:
                            recommendations['performance_issues'].append("High training error indicates poor fit")
                            recommendations['priority_actions'].append("Optimize hyperparameters with grid search")
                        
            except Exception as e:
                recommendations['performance_issues'].append(f"Unable to evaluate performance: {str(e)}")
        
        # 7. Preset Suggestions
        if sr < 0.7:
            recommendations['preset_suggestions'].append("time_series_fast - for quick good performance")
        elif sr > 1.1:
            recommendations['preset_suggestions'].append("chaotic_systems - for high memory capacity")
        
        if n_res < 100:
            recommendations['preset_suggestions'].append("minimal_compute - optimized for small reservoirs")
        elif n_res > 500:
            recommendations['preset_suggestions'].append("large_scale - optimized for large reservoirs")
        
        # 8. ESP Validation Recommendation
        if sr > 1.0:
            recommendations['recommendations'].append("Run ESP validation to ensure stability")
            if hasattr(self, '_validate_echo_state_property'):
                try:
                    esp_valid = self._validate_echo_state_property(n_tests=3, test_length=100)
                    recommendations['parameter_analysis']['esp_validated'] = esp_valid
                    if not esp_valid:
                        recommendations['priority_actions'].append("URGENT: ESP violated - reduce spectral radius")
                except:
                    pass
        
        # 9. Overall Health Score
        issues = len(recommendations['performance_issues'])
        health_score = max(0, 100 - issues * 15)
        recommendations['health_score'] = health_score
        
        # Print summary
        print(f"📋 Configuration Health Score: {health_score}/100")
        print(f"🔍 Issues Found: {issues}")
        print(f"💡 Recommendations Generated: {len(recommendations['recommendations'])}")
        
        if recommendations['priority_actions']:
            print("🚨 Priority Actions:")
            for action in recommendations['priority_actions']:
                print(f"   • {action}")
        
        return recommendations
    
    def get_configuration_health_score(self):
        """
        🏥 Get Configuration Health Score - Quick Assessment
        
        Returns:
            int: Health score from 0-100 based on parameter optimality
        """
        recommendations = self.get_performance_recommendations()
        return recommendations.get('health_score', 50)
    
    def diagnose_performance_bottlenecks(self, X_train, y_train):
        """
        🔍 Diagnose Performance Bottlenecks - Identify Key Issues
        
        Args:
            X_train (array): Training input data
            y_train (array): Training targets
            
        Returns:
            dict: Detailed bottleneck analysis
        """
        bottlenecks = {
            'identified_issues': [],
            'severity_scores': {},
            'suggested_fixes': [],
            'estimated_improvement': {}
        }
        
        recommendations = self.get_performance_recommendations(X_train, y_train)
        
        # Analyze issues by severity
        for issue in recommendations['performance_issues']:
            severity = 'medium'
            if 'CRITICAL' in issue or 'URGENT' in issue:
                severity = 'high'
            elif 'may' in issue or 'consider' in issue:
                severity = 'low'
            
            bottlenecks['identified_issues'].append({
                'issue': issue,
                'severity': severity
            })
        
        # Estimate potential improvements
        sr = getattr(self, 'spectral_radius', 1.0)
        if sr > 1.3 or sr < 0.3:
            bottlenecks['estimated_improvement']['spectral_radius_adjustment'] = '20-40% performance gain'
        
        n_res = getattr(self, 'n_reservoir', 100)
        if X_train is not None:
            n_inputs = X_train.shape[1] if len(X_train.shape) > 1 else 1
            if n_res < n_inputs * 5:
                bottlenecks['estimated_improvement']['reservoir_size_increase'] = '15-30% performance gain'
        
        return bottlenecks