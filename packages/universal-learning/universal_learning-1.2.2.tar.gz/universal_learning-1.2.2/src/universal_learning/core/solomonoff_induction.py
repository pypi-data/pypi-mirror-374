"""
🔮 Solomonoff Induction - Universal Learning Algorithm
====================================================

This module implements Ray Solomonoff's universal induction algorithm,
the mathematically optimal method for sequence prediction and pattern learning.

Based on:
- Solomonoff (1964) "A Formal Theory of Inductive Inference"
- Li & Vitányi (2019) "An Introduction to Kolmogorov Complexity"
- Hutter (2005) "Universal Artificial Intelligence"

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict
import warnings


@dataclass
class UniversalDistribution:
    """
    🌊 Universal Distribution Implementation
    
    Represents Solomonoff's universal distribution M(x) over sequences,
    approximated through program enumeration and compression methods.
    
    Attributes
    ----------
    sequence : List[Any]
        The observed sequence
    probability : float
        Universal probability M(sequence)
    complexity : float
        Approximate Kolmogorov complexity
    programs : List[Dict]
        Enumerated programs generating the sequence
    """
    
    sequence: List[Any]
    probability: float = 0.0
    complexity: float = float('inf')
    programs: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.metadata.setdefault('method', 'enumeration')
        self.metadata.setdefault('approximation', True)


class SolomonoffInduction:
    """
    🔮 Solomonoff Universal Induction System
    
    Implements Ray Solomonoff's mathematically optimal inductive inference
    algorithm using program enumeration and universal priors.
    
    This is the theoretical foundation for optimal learning and prediction
    in any computable environment.
    
    Parameters
    ----------
    max_program_length : int, default=20
        Maximum program length for enumeration
    time_budget : int, default=1000000
        Maximum computation steps per program
    approximation_methods : List[str], default=['compression', 'context', 'patterns']
        Approximation methods to use when exact enumeration is intractable
    universal_machine : str, default='python'
        Universal Turing machine implementation to use
    """
    
    def __init__(self,
                 max_program_length: int = 20,
                 time_budget: int = 1000000,
                 approximation_methods: List[str] = None,
                 universal_machine: str = 'python'):
        
        self.max_program_length = max_program_length
        self.time_budget = time_budget
        self.approximation_methods = approximation_methods or ['compression', 'context', 'patterns']
        self.universal_machine = universal_machine
        
        # Storage for learned patterns and programs
        self.program_cache: Dict[str, List[Dict]] = defaultdict(list)
        self.complexity_cache: Dict[str, float] = {}
        self.prediction_history: List[Dict[str, Any]] = []
        
        # Statistics
        self.stats = {
            'total_predictions': 0,
            'successful_predictions': 0,
            'programs_enumerated': 0,
            'complexity_computations': 0,
            'cache_hits': 0
        }
        
        # Initialize approximation engines
        self._init_approximation_methods()
    
    def predict_next(self, sequence: List[Any], 
                    num_predictions: int = 1,
                    return_probabilities: bool = False) -> Union[List[Any], List[Tuple[Any, float]]]:
        """
        Predict the next element(s) in a sequence using universal induction.
        
        This implements the core Solomonoff prediction:
        P(x_{n+1} | x_1, ..., x_n) = M(x_1, ..., x_n, x_{n+1}) / M(x_1, ..., x_n)
        
        Parameters
        ----------
        sequence : List[Any]
            Observed sequence to extend
        num_predictions : int, default=1
            Number of future elements to predict
        return_probabilities : bool, default=False
            Whether to return prediction probabilities
            
        Returns
        -------
        List[Any] or List[Tuple[Any, float]]
            Predicted elements, optionally with probabilities
        """
        if not sequence:
            warnings.warn("Empty sequence provided")
            return [] if not return_probabilities else []
        
        self.stats['total_predictions'] += 1
        
        # Compute universal distribution for observed sequence
        sequence_distribution = self.universal_distribution(sequence)
        
        # Generate candidate continuations
        candidates = self._generate_continuations(sequence, num_predictions)
        
        # Compute probabilities for each candidate continuation
        continuations_with_probs = []
        
        for continuation in candidates:
            # Make sure we're concatenating strings
            if isinstance(continuation, list):
                continuation_str = ''.join(str(c) for c in continuation)
            else:
                continuation_str = str(continuation)
            
            extended_sequence = sequence + continuation_str
            extended_distribution = self.universal_distribution(extended_sequence)
            
            # Conditional probability P(continuation | sequence)
            if sequence_distribution.probability > 0:
                conditional_prob = extended_distribution.probability / sequence_distribution.probability
            else:
                conditional_prob = 0.0
            
            continuations_with_probs.append((continuation_str, conditional_prob))
        
        # Sort by probability and return best predictions
        continuations_with_probs.sort(key=lambda x: x[1], reverse=True)
        
        if return_probabilities:
            result = [(cont, prob) for cont, prob in continuations_with_probs[:num_predictions]]
        else:
            result = [cont for cont, prob in continuations_with_probs[:num_predictions]]
        
        # Update statistics and history
        self._update_prediction_history(sequence, result)
        
        return result
    
    def universal_distribution(self, sequence: List[Any]) -> UniversalDistribution:
        """
        Compute the universal distribution M(sequence) over a given sequence.
        
        This approximates Solomonoff's universal distribution:
        M(x) = Σ_{p: U(p) starts with x} 2^(-|p|)
        
        Parameters
        ----------
        sequence : List[Any]
            Sequence to compute distribution for
            
        Returns
        -------
        UniversalDistribution
            Universal distribution with probability and complexity estimates
        """
        sequence_key = str(sequence)
        
        # Check cache first
        if sequence_key in self.complexity_cache:
            self.stats['cache_hits'] += 1
            cached_complexity = self.complexity_cache[sequence_key]
            cached_programs = self.program_cache.get(sequence_key, [])
            
            return UniversalDistribution(
                sequence=sequence,
                probability=2**(-cached_complexity),
                complexity=cached_complexity,
                programs=cached_programs,
                metadata={'cached': True}
            )
        
        # Compute distribution using multiple methods
        programs = []
        total_probability = 0.0
        min_complexity = float('inf')
        
        # Method 1: Program enumeration (exact for short sequences)
        if len(sequence) <= 10 and self.max_program_length <= 15:
            enum_programs = self._enumerate_programs(sequence)
            programs.extend(enum_programs)
            
            for prog in enum_programs:
                total_probability += prog['weight']
                min_complexity = min(min_complexity, prog['complexity'])
        
        # Method 2: Approximation methods
        for method in self.approximation_methods:
            approx_result = self._approximate_complexity(sequence, method)
            if approx_result is not None:
                programs.append(approx_result)
                total_probability += approx_result['weight']
                min_complexity = min(min_complexity, approx_result['complexity'])
        
        # Normalize and create distribution
        if programs:
            # Use minimum complexity as best estimate
            complexity = min_complexity
            probability = max(total_probability, 2**(-min_complexity))
        else:
            # Fallback: uniform distribution assumption
            complexity = len(str(sequence))
            probability = 2**(-complexity)
            programs.append({
                'program': f"uniform_fallback",
                'complexity': complexity,
                'weight': probability,
                'method': 'fallback'
            })
        
        # Cache result
        self.complexity_cache[sequence_key] = complexity
        self.program_cache[sequence_key] = programs
        self.stats['complexity_computations'] += 1
        
        return UniversalDistribution(
            sequence=sequence,
            probability=probability,
            complexity=complexity,
            programs=programs
        )
    
    def kolmogorov_complexity(self, sequence: List[Any]) -> float:
        """
        Estimate Kolmogorov complexity K(sequence) of a sequence.
        
        Parameters
        ----------
        sequence : List[Any]
            Sequence to compute complexity for
            
        Returns
        -------
        float
            Estimated Kolmogorov complexity
        """
        distribution = self.universal_distribution(sequence)
        return distribution.complexity
    
    def algorithmic_probability(self, sequence: List[Any]) -> float:
        """
        Compute algorithmic probability of a sequence.
        
        Parameters
        ----------
        sequence : List[Any]
            Sequence to compute probability for
            
        Returns
        -------
        float
            Algorithmic probability
        """
        distribution = self.universal_distribution(sequence)
        return distribution.probability
    
    def learn_from_sequence(self, sequence: List[Any], 
                          update_cache: bool = True) -> Dict[str, Any]:
        """
        Learn patterns from a sequence and update internal models.
        
        Parameters
        ----------
        sequence : List[Any]
            Sequence to learn from
        update_cache : bool, default=True
            Whether to update internal caches
            
        Returns
        -------
        Dict[str, Any]
            Learning results and statistics
        """
        if not sequence:
            return {'error': 'Empty sequence provided'}
        
        results = {
            'sequence_length': len(sequence),
            'complexity': 0.0,
            'probability': 0.0,
            'patterns_found': [],
            'programs_generated': 0
        }
        
        # Analyze subsequences for pattern learning
        for start in range(len(sequence)):
            for end in range(start + 1, min(start + 20, len(sequence) + 1)):
                subseq = sequence[start:end]
                
                # Compute distribution for subsequence
                distribution = self.universal_distribution(subseq)
                
                # Update results
                results['programs_generated'] += len(distribution.programs)
                
                # Extract patterns
                for program in distribution.programs:
                    if program.get('method') == 'patterns':
                        results['patterns_found'].append({
                            'subsequence': subseq,
                            'pattern': program.get('pattern_type', 'unknown'),
                            'complexity': program['complexity']
                        })
        
        # Overall sequence analysis
        full_distribution = self.universal_distribution(sequence)
        results['complexity'] = full_distribution.complexity
        results['probability'] = full_distribution.probability
        
        return results
    
    def _enumerate_programs(self, sequence: List[Any]) -> List[Dict[str, Any]]:
        """Enumerate programs that generate the given sequence."""
        programs = []
        
        # This is a simplified enumeration - full implementation would
        # systematically generate all programs up to max_program_length
        
        # Simple program generators
        generators = [
            self._try_constant_program,
            self._try_arithmetic_sequence,
            self._try_geometric_sequence,
            self._try_fibonacci_sequence,
            self._try_repetition_pattern
        ]
        
        for generator in generators:
            try:
                result = generator(sequence)
                if result:
                    programs.append(result)
            except Exception:
                continue
        
        self.stats['programs_enumerated'] += len(programs)
        return programs
    
    def _try_constant_program(self, sequence: List[Any]) -> Optional[Dict[str, Any]]:
        """Try to generate sequence with constant program."""
        if len(set(sequence)) == 1:
            value = sequence[0]
            complexity = len(str(value)) + 5  # "print" + value
            return {
                'program': f"print({value})",
                'complexity': complexity,
                'weight': 2**(-complexity),
                'method': 'constant',
                'pattern_type': 'constant'
            }
        return None
    
    def _try_arithmetic_sequence(self, sequence: List[Any]) -> Optional[Dict[str, Any]]:
        """Try to generate sequence with arithmetic progression."""
        if len(sequence) < 3:
            return None
        
        try:
            # Check if it's arithmetic sequence
            diffs = [sequence[i+1] - sequence[i] for i in range(len(sequence)-1)]
            if len(set(diffs)) == 1:
                # Arithmetic sequence found
                start = sequence[0]
                diff = diffs[0]
                
                # Program: "for i in range(n): print(start + i*diff)"
                complexity = len(str(start)) + len(str(diff)) + 15
                return {
                    'program': f"for i in range({len(sequence)}): print({start} + i*{diff})",
                    'complexity': complexity,
                    'weight': 2**(-complexity),
                    'method': 'arithmetic',
                    'pattern_type': 'arithmetic',
                    'parameters': {'start': start, 'diff': diff}
                }
        except (TypeError, ValueError):
            pass
        
        return None
    
    def _try_geometric_sequence(self, sequence: List[Any]) -> Optional[Dict[str, Any]]:
        """Try to generate sequence with geometric progression."""
        if len(sequence) < 3:
            return None
        
        try:
            # Check if it's geometric sequence
            if all(x != 0 for x in sequence[:-1]):
                ratios = [sequence[i+1] / sequence[i] for i in range(len(sequence)-1)]
                if len(set(ratios)) == 1:
                    # Geometric sequence found
                    start = sequence[0]
                    ratio = ratios[0]
                    
                    complexity = len(str(start)) + len(str(ratio)) + 20
                    return {
                        'program': f"x={start}; for i in range({len(sequence)}): print(x); x*={ratio}",
                        'complexity': complexity,
                        'weight': 2**(-complexity),
                        'method': 'geometric',
                        'pattern_type': 'geometric',
                        'parameters': {'start': start, 'ratio': ratio}
                    }
        except (TypeError, ValueError, ZeroDivisionError):
            pass
        
        return None
    
    def _try_fibonacci_sequence(self, sequence: List[Any]) -> Optional[Dict[str, Any]]:
        """Try to generate sequence with Fibonacci pattern."""
        if len(sequence) < 3:
            return None
        
        try:
            # Check if it follows Fibonacci pattern
            is_fibonacci = True
            for i in range(2, len(sequence)):
                if sequence[i] != sequence[i-1] + sequence[i-2]:
                    is_fibonacci = False
                    break
            
            if is_fibonacci:
                a, b = sequence[0], sequence[1]
                complexity = len(str(a)) + len(str(b)) + 25
                return {
                    'program': f"a,b={a},{b}; for i in range({len(sequence)}): print(a); a,b=b,a+b",
                    'complexity': complexity,
                    'weight': 2**(-complexity),
                    'method': 'fibonacci',
                    'pattern_type': 'fibonacci',
                    'parameters': {'start1': a, 'start2': b}
                }
        except (TypeError, ValueError):
            pass
        
        return None
    
    def _try_repetition_pattern(self, sequence: List[Any]) -> Optional[Dict[str, Any]]:
        """Try to find repetition patterns."""
        seq_str = str(sequence)
        
        # Try different period lengths
        for period in range(1, len(sequence) // 2 + 1):
            pattern = sequence[:period]
            
            # Check if sequence is repetition of this pattern
            is_repetition = True
            for i in range(period, len(sequence)):
                if sequence[i] != pattern[i % period]:
                    is_repetition = False
                    break
            
            if is_repetition:
                repetitions = len(sequence) // period
                complexity = len(str(pattern)) + len(str(repetitions)) + 10
                return {
                    'program': f"pattern={pattern}; print(pattern * {repetitions})",
                    'complexity': complexity,
                    'weight': 2**(-complexity),
                    'method': 'repetition',
                    'pattern_type': 'repetition',
                    'parameters': {'pattern': pattern, 'repetitions': repetitions}
                }
        
        return None
    
    def _approximate_complexity(self, sequence: List[Any], method: str) -> Optional[Dict[str, Any]]:
        """Approximate complexity using various methods."""
        if method == 'compression':
            return self._compression_approximation(sequence)
        elif method == 'context':
            return self._context_approximation(sequence)
        elif method == 'patterns':
            return self._pattern_approximation(sequence)
        else:
            return None
    
    def _compression_approximation(self, sequence: List[Any]) -> Dict[str, Any]:
        """Approximate complexity using compression length."""
        try:
            import zlib
            seq_bytes = str(sequence).encode('utf-8')
            compressed = zlib.compress(seq_bytes)
            complexity = len(compressed) * 8  # Convert to bits
            
            return {
                'program': f"decompress({compressed})",
                'complexity': complexity,
                'weight': 2**(-complexity),
                'method': 'compression',
                'compression_ratio': len(compressed) / len(seq_bytes)
            }
        except ImportError:
            # Fallback: simple length-based approximation
            complexity = len(str(sequence))
            return {
                'program': f"literal({sequence})",
                'complexity': complexity,
                'weight': 2**(-complexity),
                'method': 'compression_fallback'
            }
    
    def _context_approximation(self, sequence: List[Any]) -> Dict[str, Any]:
        """Approximate complexity using context modeling."""
        # Simple context modeling - count unique subsequences
        unique_subseqs = set()
        
        for length in range(1, min(6, len(sequence) + 1)):
            for i in range(len(sequence) - length + 1):
                subseq = tuple(sequence[i:i+length])
                unique_subseqs.add(subseq)
        
        # Complexity is log of number of unique contexts needed
        complexity = np.log2(len(unique_subseqs)) + len(str(sequence)) * 0.1
        
        return {
            'program': f"context_model({len(unique_subseqs)}_contexts)",
            'complexity': complexity,
            'weight': 2**(-complexity),
            'method': 'context',
            'unique_contexts': len(unique_subseqs)
        }
    
    def _pattern_approximation(self, sequence: List[Any]) -> Dict[str, Any]:
        """Approximate complexity by detecting common patterns."""
        # Try various pattern detection methods
        patterns_found = []
        
        # Arithmetic patterns
        if self._try_arithmetic_sequence(sequence):
            patterns_found.append('arithmetic')
        
        # Repetition patterns
        if self._try_repetition_pattern(sequence):
            patterns_found.append('repetition')
        
        # Base complexity on number of patterns found
        if patterns_found:
            complexity = 10 + len(str(sequence)) * 0.2  # Lower complexity for patterned data
        else:
            complexity = len(str(sequence)) * 0.8  # Higher complexity for random-looking data
        
        return {
            'program': f"pattern_generator({patterns_found})",
            'complexity': complexity,
            'weight': 2**(-complexity),
            'method': 'patterns',
            'patterns_detected': patterns_found
        }
    
    def _generate_continuations(self, sequence: List[Any], num_predictions: int) -> List[List[Any]]:
        """Generate candidate continuations for a sequence."""
        continuations = []
        
        # Based on detected patterns, generate likely continuations
        distribution = self.universal_distribution(sequence)
        
        for program in distribution.programs:
            continuation = self._extend_with_program(sequence, program, num_predictions)
            if continuation and continuation not in continuations:
                continuations.append(continuation)
        
        # Add some default continuations if none found
        if not continuations:
            # Try continuing with last element
            if sequence:
                continuations.append([sequence[-1]] * num_predictions)
            
            # Try continuing with most common element
            if len(set(sequence)) > 1:
                from collections import Counter
                most_common = Counter(sequence).most_common(1)[0][0]
                continuations.append([most_common] * num_predictions)
        
        return continuations[:10]  # Limit to top 10 candidates
    
    def _extend_with_program(self, sequence: List[Any], program: Dict[str, Any], length: int) -> Optional[List[Any]]:
        """Extend sequence using a specific program pattern."""
        method = program.get('method', 'unknown')
        
        if method == 'arithmetic' and 'parameters' in program:
            params = program['parameters']
            next_val = sequence[-1] + params['diff']
            return [next_val + i * params['diff'] for i in range(length)]
        
        elif method == 'geometric' and 'parameters' in program:
            params = program['parameters']
            next_val = sequence[-1] * params['ratio']
            return [next_val * (params['ratio'] ** i) for i in range(length)]
        
        elif method == 'fibonacci':
            if len(sequence) >= 2:
                continuation = []
                a, b = sequence[-2], sequence[-1]
                for _ in range(length):
                    next_val = a + b
                    continuation.append(next_val)
                    a, b = b, next_val
                return continuation
        
        elif method == 'repetition' and 'parameters' in program:
            pattern = program['parameters']['pattern']
            pattern_len = len(pattern)
            start_idx = len(sequence) % pattern_len
            continuation = []
            for i in range(length):
                continuation.append(pattern[(start_idx + i) % pattern_len])
            return continuation
        
        elif method == 'constant':
            if sequence:
                return [sequence[0]] * length
        
        return None
    
    def _init_approximation_methods(self):
        """Initialize approximation method engines."""
        # This would initialize more sophisticated approximation methods
        # For now, we rely on the built-in methods
        pass
    
    def _update_prediction_history(self, sequence: Union[str, List[Any]], predictions: List[Any]):
        """Update prediction history for learning and analysis."""
        self.prediction_history.append({
            'sequence': list(sequence) if isinstance(sequence, str) else sequence.copy(),
            'predictions': predictions.copy() if hasattr(predictions, 'copy') else list(predictions),
            'timestamp': len(self.prediction_history),
            'sequence_length': len(sequence)
        })
        
        # Keep only recent history
        if len(self.prediction_history) > 1000:
            self.prediction_history = self.prediction_history[-1000:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics and performance metrics."""
        stats = self.stats.copy()
        
        stats.update({
            'cache_size': len(self.complexity_cache),
            'programs_cached': sum(len(progs) for progs in self.program_cache.values()),
            'prediction_history_size': len(self.prediction_history),
            'approximation_methods': self.approximation_methods,
            'max_program_length': self.max_program_length,
            'time_budget': self.time_budget
        })
        
        # Success rate
        if stats['total_predictions'] > 0:
            stats['success_rate'] = stats['successful_predictions'] / stats['total_predictions']
        else:
            stats['success_rate'] = 0.0
        
        return stats
    
    def clear_cache(self):
        """Clear internal caches to free memory."""
        self.program_cache.clear()
        self.complexity_cache.clear()
        self.prediction_history.clear()
    
    def __repr__(self) -> str:
        return (f"SolomonoffInduction(max_length={self.max_program_length}, "
                f"methods={self.approximation_methods}, "
                f"cached_sequences={len(self.complexity_cache)})")