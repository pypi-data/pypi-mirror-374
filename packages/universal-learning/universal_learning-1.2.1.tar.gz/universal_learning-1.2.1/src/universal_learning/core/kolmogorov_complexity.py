"""
🎯 Kolmogorov Complexity Estimation
==================================

This module provides methods for estimating Kolmogorov complexity
of sequences and data structures using various approximation techniques.

Based on:
- Kolmogorov (1965) "Three approaches to the quantitative definition of information"
- Li & Vitányi (2019) "An Introduction to Kolmogorov Complexity"

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Any, List, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum
import warnings


class ComplexityMethod(Enum):
    """Methods for approximating Kolmogorov complexity."""
    COMPRESSION = "compression"
    ENUMERATION = "enumeration" 
    STATISTICAL = "statistical"
    PATTERN_BASED = "pattern_based"
    HYBRID = "hybrid"


@dataclass 
class ComplexityMeasure:
    """
    📊 Represents a complexity measurement result.
    
    Attributes
    ----------
    value : float
        Estimated complexity value
    method : ComplexityMethod
        Method used for estimation
    confidence : float
        Confidence in the estimate (0-1)
    metadata : Dict[str, Any]
        Additional information about the measurement
    """
    
    value: float
    method: ComplexityMethod
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class KolmogorovComplexity:
    """
    🎯 Kolmogorov Complexity Estimator
    
    Provides multiple methods for estimating the Kolmogorov complexity
    of sequences, which is fundamentally uncomputable but can be
    approximated through various techniques.
    
    Parameters
    ----------
    default_method : ComplexityMethod, default=HYBRID
        Default method for complexity estimation
    compression_libraries : List[str], default=['zlib', 'bz2', 'lzma']
        Compression libraries to use for compression-based estimation
    enable_caching : bool, default=True
        Enable caching of complexity estimates
    """
    
    def __init__(self,
                 default_method: ComplexityMethod = ComplexityMethod.HYBRID,
                 compression_libraries: List[str] = None,
                 enable_caching: bool = True):
        
        self.default_method = default_method
        self.compression_libraries = compression_libraries or ['zlib', 'bz2', 'lzma']
        self.enable_caching = enable_caching
        
        # Cache for complexity estimates
        self.complexity_cache: Dict[str, ComplexityMeasure] = {}
        
        # Statistics
        self.stats = {
            'total_estimates': 0,
            'cache_hits': 0,
            'method_usage': {method.value: 0 for method in ComplexityMethod}
        }
        
        # Available compression modules
        self.available_compressors = self._check_available_compressors()
    
    def estimate_complexity(self, 
                          sequence: Union[str, List[Any], np.ndarray],
                          method: Optional[ComplexityMethod] = None) -> ComplexityMeasure:
        """
        Estimate Kolmogorov complexity of a sequence.
        
        Parameters
        ----------
        sequence : str, List[Any], or np.ndarray
            Input sequence to analyze
        method : ComplexityMethod, optional
            Specific method to use (default: use default_method)
            
        Returns
        -------
        ComplexityMeasure
            Complexity measurement result
        """
        if method is None:
            method = self.default_method
        
        # Convert sequence to standardized format
        seq_str = self._serialize_sequence(sequence)
        cache_key = f"{method.value}:{seq_str}"
        
        # Check cache first
        if self.enable_caching and cache_key in self.complexity_cache:
            self.stats['cache_hits'] += 1
            return self.complexity_cache[cache_key]
        
        # Compute complexity estimate
        self.stats['total_estimates'] += 1
        self.stats['method_usage'][method.value] += 1
        
        if method == ComplexityMethod.COMPRESSION:
            result = self._compression_based_complexity(sequence)
        elif method == ComplexityMethod.STATISTICAL:
            result = self._statistical_complexity(sequence)
        elif method == ComplexityMethod.PATTERN_BASED:
            result = self._pattern_based_complexity(sequence)
        elif method == ComplexityMethod.HYBRID:
            result = self._hybrid_complexity(sequence)
        else:
            # Default to compression method
            result = self._compression_based_complexity(sequence)
        
        result.method = method
        
        # Cache result
        if self.enable_caching:
            self.complexity_cache[cache_key] = result
        
        return result
    
    def _compression_based_complexity(self, sequence: Union[str, List[Any], np.ndarray]) -> ComplexityMeasure:
        """Estimate complexity using compression algorithms."""
        # Convert sequence to bytes
        if isinstance(sequence, str):
            data_bytes = sequence.encode('utf-8')
        else:
            data_bytes = str(sequence).encode('utf-8')
        
        original_length = len(data_bytes)
        
        # Try multiple compressors and use the best result
        best_compression = original_length
        best_compressor = None
        compressor_results = {}
        
        for compressor_name in self.available_compressors:
            try:
                if compressor_name == 'zlib':
                    import zlib
                    compressed = zlib.compress(data_bytes)
                elif compressor_name == 'bz2':
                    import bz2
                    compressed = bz2.compress(data_bytes)
                elif compressor_name == 'lzma':
                    import lzma
                    compressed = lzma.compress(data_bytes)
                else:
                    continue
                
                compressed_length = len(compressed)
                compressor_results[compressor_name] = compressed_length
                
                if compressed_length < best_compression:
                    best_compression = compressed_length
                    best_compressor = compressor_name
                    
            except ImportError:
                continue
            except Exception:
                continue
        
        # Convert compressed length to bits and add decompressor overhead
        complexity_bits = best_compression * 8 + 100  # 100 bits for decompressor program
        
        # Confidence based on compression ratio
        compression_ratio = best_compression / original_length if original_length > 0 else 1.0
        confidence = min(1.0, 2.0 * (1.0 - compression_ratio))  # Higher confidence for better compression
        
        return ComplexityMeasure(
            value=complexity_bits,
            method=ComplexityMethod.COMPRESSION,
            confidence=confidence,
            metadata={
                'original_length': original_length,
                'compressed_length': best_compression,
                'compression_ratio': compression_ratio,
                'best_compressor': best_compressor,
                'all_results': compressor_results
            }
        )
    
    def _statistical_complexity(self, sequence: Union[str, List[Any], np.ndarray]) -> ComplexityMeasure:
        """Estimate complexity using statistical measures."""
        if isinstance(sequence, str):
            data = [ord(c) for c in sequence]
        elif isinstance(sequence, np.ndarray):
            data = sequence.flatten().tolist()
        else:
            data = list(sequence)
        
        if not data:
            return ComplexityMeasure(value=0.0, method=ComplexityMethod.STATISTICAL)
        
        # Entropy-based complexity
        from collections import Counter
        counts = Counter(data)
        n = len(data)
        
        # Shannon entropy
        entropy = 0.0
        for count in counts.values():
            prob = count / n
            if prob > 0:
                entropy -= prob * np.log2(prob)
        
        # Complexity based on entropy and sequence length
        complexity = entropy * n + np.log2(len(counts)) * 8  # 8 bits per unique symbol encoding
        
        # Confidence based on data distribution uniformity
        expected_entropy = np.log2(len(counts))
        confidence = min(1.0, entropy / expected_entropy if expected_entropy > 0 else 0.0)
        
        return ComplexityMeasure(
            value=complexity,
            method=ComplexityMethod.STATISTICAL,
            confidence=confidence,
            metadata={
                'entropy': entropy,
                'unique_symbols': len(counts),
                'sequence_length': n,
                'symbol_distribution': dict(counts)
            }
        )
    
    def _pattern_based_complexity(self, sequence: Union[str, List[Any], np.ndarray]) -> ComplexityMeasure:
        """Estimate complexity by detecting patterns."""
        if isinstance(sequence, str):
            data = list(sequence)
        elif isinstance(sequence, np.ndarray):
            data = sequence.flatten().tolist()
        else:
            data = list(sequence)
        
        if not data:
            return ComplexityMeasure(value=0.0, method=ComplexityMethod.PATTERN_BASED)
        
        patterns_detected = []
        complexity_reduction = 0
        
        # Check for repetitions
        repetition_savings = self._detect_repetitions(data)
        if repetition_savings > 0:
            patterns_detected.append('repetition')
            complexity_reduction += repetition_savings
        
        # Check for arithmetic progressions
        arithmetic_savings = self._detect_arithmetic_patterns(data)
        if arithmetic_savings > 0:
            patterns_detected.append('arithmetic')
            complexity_reduction += arithmetic_savings
        
        # Check for geometric progressions  
        geometric_savings = self._detect_geometric_patterns(data)
        if geometric_savings > 0:
            patterns_detected.append('geometric')
            complexity_reduction += geometric_savings
        
        # Base complexity (literal encoding)
        base_complexity = len(str(data)) * 8  # 8 bits per character estimate
        
        # Final complexity after pattern reduction
        final_complexity = max(base_complexity - complexity_reduction, 
                              base_complexity * 0.1)  # Minimum 10% of base complexity
        
        # Confidence based on pattern detection success
        confidence = min(1.0, complexity_reduction / base_complexity) if base_complexity > 0 else 0.0
        
        return ComplexityMeasure(
            value=final_complexity,
            method=ComplexityMethod.PATTERN_BASED,
            confidence=confidence,
            metadata={
                'patterns_detected': patterns_detected,
                'base_complexity': base_complexity,
                'complexity_reduction': complexity_reduction,
                'pattern_coverage': complexity_reduction / base_complexity if base_complexity > 0 else 0
            }
        )
    
    def _hybrid_complexity(self, sequence: Union[str, List[Any], np.ndarray]) -> ComplexityMeasure:
        """Estimate complexity using multiple methods and combine results."""
        methods = [ComplexityMethod.COMPRESSION, ComplexityMethod.STATISTICAL, ComplexityMethod.PATTERN_BASED]
        results = []
        
        for method in methods:
            try:
                result = self.estimate_complexity(sequence, method)
                results.append(result)
            except Exception:
                continue
        
        if not results:
            # Fallback to simple length-based estimate
            fallback_complexity = len(str(sequence)) * 8
            return ComplexityMeasure(
                value=fallback_complexity,
                method=ComplexityMethod.HYBRID,
                confidence=0.1,
                metadata={'fallback': True}
            )
        
        # Weighted average of results, with higher weights for higher confidence
        total_weight = sum(r.confidence for r in results)
        if total_weight == 0:
            total_weight = len(results)
            weights = [1.0 / len(results)] * len(results)
        else:
            weights = [r.confidence / total_weight for r in results]
        
        # Weighted complexity estimate
        hybrid_complexity = sum(w * r.value for w, r in zip(weights, results))
        
        # Average confidence
        hybrid_confidence = sum(r.confidence for r in results) / len(results)
        
        return ComplexityMeasure(
            value=hybrid_complexity,
            method=ComplexityMethod.HYBRID,
            confidence=hybrid_confidence,
            metadata={
                'component_results': [
                    {
                        'method': r.method.value,
                        'value': r.value,
                        'confidence': r.confidence,
                        'weight': w
                    } for r, w in zip(results, weights)
                ]
            }
        )
    
    def _detect_repetitions(self, data: List[Any]) -> float:
        """Detect repetition patterns and estimate compression savings."""
        if len(data) < 2:
            return 0.0
        
        max_savings = 0.0
        
        # Try different period lengths
        for period in range(1, len(data) // 2 + 1):
            # Check if sequence repeats with this period
            repetitions = 0
            for i in range(period, len(data)):
                if data[i] == data[i % period]:
                    repetitions += 1
            
            # Calculate savings if we encode as repetition
            if repetitions > period:  # Need at least one full repetition to be worthwhile
                pattern_encoding = period * 8  # Bits to encode the pattern
                repetition_encoding = np.log2(len(data) // period) * 8  # Bits to encode repetition count
                literal_encoding = len(data) * 8  # Bits for literal encoding
                
                savings = literal_encoding - (pattern_encoding + repetition_encoding)
                max_savings = max(max_savings, savings)
        
        return max_savings
    
    def _detect_arithmetic_patterns(self, data: List[Any]) -> float:
        """Detect arithmetic progressions and estimate compression savings."""
        try:
            # Convert to numbers if possible
            numeric_data = [float(x) for x in data]
        except (ValueError, TypeError):
            return 0.0
        
        if len(numeric_data) < 3:
            return 0.0
        
        # Check for arithmetic progression
        diffs = [numeric_data[i+1] - numeric_data[i] for i in range(len(numeric_data)-1)]
        
        if len(set(diffs)) == 1:
            # Perfect arithmetic progression
            start_encoding = 64  # 64 bits for start value
            diff_encoding = 64   # 64 bits for difference
            count_encoding = 32  # 32 bits for count
            
            literal_encoding = len(data) * 64  # Assume 64 bits per number
            
            return max(0, literal_encoding - (start_encoding + diff_encoding + count_encoding))
        
        return 0.0
    
    def _detect_geometric_patterns(self, data: List[Any]) -> float:
        """Detect geometric progressions and estimate compression savings."""
        try:
            numeric_data = [float(x) for x in data if x != 0]
        except (ValueError, TypeError):
            return 0.0
        
        if len(numeric_data) < 3:
            return 0.0
        
        # Check for geometric progression
        ratios = [numeric_data[i+1] / numeric_data[i] for i in range(len(numeric_data)-1)]
        
        if len(set(ratios)) == 1 and all(abs(r - ratios[0]) < 1e-10 for r in ratios):
            # Perfect geometric progression
            start_encoding = 64  # 64 bits for start value
            ratio_encoding = 64  # 64 bits for ratio
            count_encoding = 32  # 32 bits for count
            
            literal_encoding = len(data) * 64
            
            return max(0, literal_encoding - (start_encoding + ratio_encoding + count_encoding))
        
        return 0.0
    
    def _serialize_sequence(self, sequence: Union[str, List[Any], np.ndarray]) -> str:
        """Convert sequence to standardized string representation."""
        if isinstance(sequence, str):
            return sequence
        elif isinstance(sequence, np.ndarray):
            return str(sequence.tolist())
        else:
            return str(list(sequence))
    
    def _check_available_compressors(self) -> List[str]:
        """Check which compression libraries are available."""
        available = []
        
        for lib in self.compression_libraries:
            try:
                if lib == 'zlib':
                    import zlib
                elif lib == 'bz2':
                    import bz2  
                elif lib == 'lzma':
                    import lzma
                available.append(lib)
            except ImportError:
                continue
        
        return available
    
    def batch_estimate(self, sequences: List[Union[str, List[Any], np.ndarray]],
                      method: Optional[ComplexityMethod] = None) -> List[ComplexityMeasure]:
        """
        Estimate complexity for multiple sequences.
        
        Parameters
        ----------
        sequences : List[Union[str, List[Any], np.ndarray]]
            List of sequences to analyze
        method : ComplexityMethod, optional
            Method to use for all sequences
            
        Returns
        -------
        List[ComplexityMeasure]
            Complexity measurements for each sequence
        """
        return [self.estimate_complexity(seq, method) for seq in sequences]
    
    def compare_complexity(self, seq1: Union[str, List[Any], np.ndarray],
                          seq2: Union[str, List[Any], np.ndarray],
                          method: Optional[ComplexityMethod] = None) -> Dict[str, Any]:
        """
        Compare complexity of two sequences.
        
        Parameters
        ----------
        seq1, seq2 : Union[str, List[Any], np.ndarray]
            Sequences to compare
        method : ComplexityMethod, optional
            Method to use for comparison
            
        Returns
        -------
        Dict[str, Any]
            Comparison results
        """
        c1 = self.estimate_complexity(seq1, method)
        c2 = self.estimate_complexity(seq2, method)
        
        return {
            'sequence1_complexity': c1.value,
            'sequence2_complexity': c2.value,
            'complexity_ratio': c1.value / c2.value if c2.value > 0 else float('inf'),
            'complexity_difference': c1.value - c2.value,
            'more_complex': 'sequence1' if c1.value > c2.value else 'sequence2',
            'confidence1': c1.confidence,
            'confidence2': c2.confidence,
            'method_used': c1.method.value
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get complexity estimation statistics."""
        stats = self.stats.copy()
        
        stats.update({
            'cache_size': len(self.complexity_cache),
            'available_compressors': self.available_compressors,
            'cache_hit_rate': self.stats['cache_hits'] / max(1, self.stats['total_estimates']),
            'default_method': self.default_method.value
        })
        
        return stats
    
    def clear_cache(self):
        """Clear the complexity estimation cache."""
        self.complexity_cache.clear()
    
    def __repr__(self) -> str:
        return (f"KolmogorovComplexity(method={self.default_method.value}, "
                f"cache_size={len(self.complexity_cache)}, "
                f"estimates={self.stats['total_estimates']})")