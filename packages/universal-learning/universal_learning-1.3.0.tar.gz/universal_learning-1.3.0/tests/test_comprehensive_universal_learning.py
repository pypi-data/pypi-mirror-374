#!/usr/bin/env python3
"""
🧪 Comprehensive Universal Learning Test Suite
==============================================

Complete test coverage for universal learning algorithms including:
- Solomonoff induction implementation
- Algorithmic information theory
- Universal learning bounds
- Compression-based learning

This addresses the critical 5.7% test coverage (2/37 files).

Author: Benedict Chen (benedict@benedictchen.com)
Research Foundation: Solomonoff (1964), Li & Vitányi (1997), Hutter (2005)
"""

import pytest
import numpy as np
import torch
import sys
from pathlib import Path

# Add package to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from universal_learning.solomonoff import SolomonoffInduction
    from universal_learning.universal_learner import UniversalLearner
    from universal_learning.compression_learner import CompressionLearner
    from universal_learning.algorithmic_information import AlgorithmicInformation
except ImportError as e:
    pytest.skip(f"Universal learning modules not available: {e}", allow_module_level=True)


class TestSolomonoffInduction:
    """Test Solomonoff induction implementation."""
    
    def test_initialization(self):
        """Test Solomonoff induction initialization."""
        sol = SolomonoffInduction(max_program_length=10)
        assert sol.max_program_length == 10
        assert hasattr(sol, 'universal_prior')
    
    def test_universal_prior_computation(self):
        """Test universal prior probability computation."""
        sol = SolomonoffInduction(max_program_length=8)
        
        # Simple binary sequence
        sequence = [0, 1, 0, 1]
        prior = sol.compute_universal_prior(sequence)
        
        assert isinstance(prior, float)
        assert 0 <= prior <= 1
        assert prior > 0  # Should have non-zero probability
    
    def test_prediction_accuracy(self):
        """Test prediction accuracy on simple patterns."""
        sol = SolomonoffInduction(max_program_length=12)
        
        # Repeating pattern
        pattern = [0, 1] * 5
        prediction = sol.predict_next(pattern)
        
        assert prediction in [0, 1]
        # For alternating pattern, should predict 0 next
        assert prediction == 0
    
    def test_compression_ratio(self):
        """Test compression-based learning."""
        sol = SolomonoffInduction()
        
        # Highly compressible sequence
        compressible = [1] * 20
        ratio1 = sol.compression_ratio(compressible)
        
        # Random sequence (less compressible)
        np.random.seed(42)
        random_seq = np.random.randint(0, 2, 20).tolist()
        ratio2 = sol.compression_ratio(random_seq)
        
        assert ratio1 > ratio2  # Compressible should have higher ratio


class TestUniversalLearner:
    """Test universal learner implementation."""
    
    def test_initialization(self):
        """Test universal learner initialization."""
        learner = UniversalLearner(complexity_penalty=0.1)
        assert learner.complexity_penalty == 0.1
        assert hasattr(learner, 'hypothesis_space')
    
    def test_learning_simple_function(self):
        """Test learning simple mathematical functions."""
        learner = UniversalLearner()
        
        # Linear function y = 2x + 1
        X = np.array([[1], [2], [3], [4], [5]])
        y = np.array([3, 5, 7, 9, 11])
        
        learner.fit(X, y)
        predictions = learner.predict([[6], [7]])
        
        # Should predict close to 13, 15
        assert len(predictions) == 2
        assert abs(predictions[0] - 13) < 2
        assert abs(predictions[1] - 15) < 2
    
    def test_model_selection(self):
        """Test automatic model selection."""
        learner = UniversalLearner()
        
        # Quadratic data
        X = np.array([[i] for i in range(1, 6)])
        y = np.array([i**2 for i in range(1, 6)])  # 1, 4, 9, 16, 25
        
        learner.fit(X, y)
        best_model = learner.get_best_model()
        
        assert best_model is not None
        assert hasattr(learner, 'model_complexity')
    
    def test_universal_bound(self):
        """Test universal learning bound computation."""
        learner = UniversalLearner()
        
        # Generate sample data
        X = np.random.randn(50, 2)
        y = X[:, 0] + X[:, 1] + np.random.randn(50) * 0.1
        
        learner.fit(X, y)
        bound = learner.compute_universal_bound(X.shape[0])
        
        assert isinstance(bound, float)
        assert bound > 0


class TestCompressionLearner:
    """Test compression-based learning algorithms."""
    
    def test_initialization(self):
        """Test compression learner initialization."""
        comp_learner = CompressionLearner(compression_method='lz77')
        assert comp_learner.compression_method == 'lz77'
    
    def test_compression_distance(self):
        """Test compression-based distance metric."""
        comp_learner = CompressionLearner()
        
        # Similar sequences should have smaller distance
        seq1 = "abcabcabc" * 5
        seq2 = "abcabcabc" * 4
        seq3 = "xyzxyzxyz" * 5
        
        dist12 = comp_learner.compression_distance(seq1, seq2)
        dist13 = comp_learner.compression_distance(seq1, seq3)
        
        assert dist12 < dist13  # More similar sequences closer
    
    def test_clustering_by_compression(self):
        """Test clustering using compression distance."""
        comp_learner = CompressionLearner()
        
        # Create distinct patterns
        patterns = [
            "ababab" * 10,
            "ababab" * 8,
            "cdcdcd" * 10,
            "cdcdcd" * 9,
        ]
        
        clusters = comp_learner.cluster(patterns, n_clusters=2)
        
        assert len(clusters) == 4
        assert len(set(clusters)) == 2  # Should form 2 clusters
        # Similar patterns should be in same cluster
        assert clusters[0] == clusters[1]
        assert clusters[2] == clusters[3]
    
    def test_classification_by_compression(self):
        """Test classification using compression."""
        comp_learner = CompressionLearner()
        
        # Train on pattern classes
        X_train = [
            "aaa" * 20,    # Class 0
            "bbb" * 20,    # Class 1
            "aaa" * 18,    # Class 0
            "bbb" * 19,    # Class 1
        ]
        y_train = [0, 1, 0, 1]
        
        comp_learner.fit(X_train, y_train)
        
        # Test predictions
        X_test = ["aaa" * 15, "bbb" * 17]
        predictions = comp_learner.predict(X_test)
        
        assert predictions[0] == 0  # Should predict class 0
        assert predictions[1] == 1  # Should predict class 1


class TestAlgorithmicInformation:
    """Test algorithmic information theory implementations."""
    
    def test_kolmogorov_complexity_estimation(self):
        """Test Kolmogorov complexity estimation."""
        ai = AlgorithmicInformation()
        
        # Simple repeating pattern (low complexity)
        simple = "01" * 50
        complex_est = ai.estimate_kolmogorov_complexity(simple)
        
        # Random string (high complexity)
        np.random.seed(42)
        random_bits = ''.join(str(np.random.randint(0, 2)) for _ in range(100))
        random_est = ai.estimate_kolmogorov_complexity(random_bits)
        
        assert complex_est < random_est  # Simple should have lower complexity
    
    def test_mutual_information(self):
        """Test algorithmic mutual information."""
        ai = AlgorithmicInformation()
        
        # Related sequences
        seq1 = "abcdefgh" * 10
        seq2 = "abcdefgh" * 8  # Similar to seq1
        seq3 = "12345678" * 10  # Different pattern
        
        mi_12 = ai.mutual_information(seq1, seq2)
        mi_13 = ai.mutual_information(seq1, seq3)
        
        assert mi_12 > mi_13  # Related sequences have higher MI
    
    def test_randomness_deficiency(self):
        """Test randomness deficiency computation."""
        ai = AlgorithmicInformation()
        
        # Non-random sequence
        pattern = "0123" * 25
        deficiency = ai.randomness_deficiency(pattern)
        
        assert deficiency > 0  # Should have positive deficiency
        assert isinstance(deficiency, (int, float))
    
    def test_logical_depth(self):
        """Test logical depth estimation."""
        ai = AlgorithmicInformation()
        
        # Sequence that requires computation
        fibonacci_like = [1, 1]
        for i in range(20):
            fibonacci_like.append(fibonacci_like[-1] + fibonacci_like[-2])
        
        depth = ai.logical_depth(str(fibonacci_like))
        
        assert depth > 0
        assert isinstance(depth, (int, float))


class TestUniversalLearningBounds:
    """Test universal learning theoretical bounds."""
    
    def test_pac_bound(self):
        """Test PAC learning bound computation."""
        from universal_learning.bounds import compute_pac_bound
        
        # Typical parameters
        n_samples = 1000
        complexity = 100
        confidence = 0.95
        
        bound = compute_pac_bound(n_samples, complexity, confidence)
        
        assert isinstance(bound, float)
        assert bound > 0
        assert bound < 1  # Should be a valid probability bound
    
    def test_rademacher_complexity(self):
        """Test Rademacher complexity estimation."""
        from universal_learning.bounds import estimate_rademacher_complexity
        
        # Random function class
        n_samples = 100
        n_functions = 50
        
        complexity = estimate_rademacher_complexity(n_samples, n_functions)
        
        assert isinstance(complexity, float)
        assert complexity >= 0
    
    def test_universal_consistency(self):
        """Test universal consistency conditions."""
        from universal_learning.bounds import check_universal_consistency
        
        # Learning algorithm parameters
        params = {
            'complexity_penalty': 0.1,
            'sample_size': 1000,
            'hypothesis_space_size': 100
        }
        
        is_consistent = check_universal_consistency(params)
        
        assert isinstance(is_consistent, bool)


class TestIntegrationScenarios:
    """Integration tests for complete universal learning pipeline."""
    
    def test_sequence_prediction_pipeline(self):
        """Test complete sequence prediction pipeline."""
        # Initialize components
        sol = SolomonoffInduction(max_program_length=10)
        learner = UniversalLearner()
        
        # Generate pattern
        pattern = [0, 1, 0, 1, 0, 1, 0, 1]
        
        # Solomonoff prediction
        sol_pred = sol.predict_next(pattern)
        
        # Universal learner prediction
        X = np.array([[i] for i in range(len(pattern))])
        y = np.array(pattern)
        learner.fit(X, y)
        ul_pred = learner.predict([[len(pattern)]])
        
        # Both should predict continuation of pattern
        assert sol_pred in [0, 1]
        assert len(ul_pred) == 1
    
    def test_compression_based_classification(self):
        """Test compression-based classification pipeline."""
        comp_learner = CompressionLearner()
        ai = AlgorithmicInformation()
        
        # Create dataset with different complexity classes
        low_complexity = ["ab" * 25, "cd" * 25, "ef" * 25]
        high_complexity = [
            "".join(str(np.random.randint(0, 2)) for _ in range(50)),
            "".join(str(np.random.randint(0, 2)) for _ in range(50)),
            "".join(str(np.random.randint(0, 2)) for _ in range(50))
        ]
        
        X = low_complexity + high_complexity
        y = [0] * 3 + [1] * 3  # 0 = low complexity, 1 = high complexity
        
        # Train classifier
        comp_learner.fit(X, y)
        
        # Test on new examples
        test_simple = "xy" * 20
        test_complex = "".join(str(np.random.randint(0, 2)) for _ in range(40))
        
        pred_simple = comp_learner.predict([test_simple])[0]
        pred_complex = comp_learner.predict([test_complex])[0]
        
        # Should classify correctly based on complexity
        assert pred_simple == 0  # Low complexity
        assert pred_complex == 1  # High complexity
    
    def test_universal_learning_convergence(self):
        """Test universal learning convergence properties."""
        learner = UniversalLearner(complexity_penalty=0.05)
        
        # Generate increasingly complex patterns
        sample_sizes = [50, 100, 200, 400]
        accuracies = []
        
        for n in sample_sizes:
            # Create polynomial data
            X = np.random.randn(n, 1)
            y = X[:, 0]**2 + 0.1 * np.random.randn(n)
            
            # Split train/test
            n_train = int(0.8 * n)
            X_train, X_test = X[:n_train], X[n_train:]
            y_train, y_test = y[:n_train], y[n_train:]
            
            learner.fit(X_train, y_train)
            predictions = learner.predict(X_test)
            
            # Compute accuracy (1 - normalized error)
            error = np.mean((predictions - y_test)**2)
            accuracy = max(0, 1 - error / np.var(y_test))
            accuracies.append(accuracy)
        
        # Should improve with more data
        assert accuracies[-1] >= accuracies[0]


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmarks for universal learning algorithms."""
    
    @pytest.mark.slow
    def test_solomonoff_performance(self):
        """Benchmark Solomonoff induction performance."""
        sol = SolomonoffInduction(max_program_length=8)
        
        import time
        start_time = time.time()
        
        # Process multiple sequences
        sequences = [
            [0, 1] * 25,
            [1, 0, 1, 1] * 12,
            list(range(10)) * 5
        ]
        
        for seq in sequences:
            sol.compute_universal_prior(seq)
        
        elapsed = time.time() - start_time
        
        # Should complete within reasonable time
        assert elapsed < 10.0  # 10 seconds max
    
    @pytest.mark.slow
    def test_compression_performance(self):
        """Benchmark compression-based learning performance."""
        comp_learner = CompressionLearner()
        
        import time
        start_time = time.time()
        
        # Large strings
        large_strings = [
            "pattern" * 1000,
            "different" * 1000,
            "another" * 1000
        ]
        
        # Compute all pairwise distances
        for i in range(len(large_strings)):
            for j in range(i+1, len(large_strings)):
                comp_learner.compression_distance(large_strings[i], large_strings[j])
        
        elapsed = time.time() - start_time
        
        # Should complete within reasonable time
        assert elapsed < 30.0  # 30 seconds max


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])