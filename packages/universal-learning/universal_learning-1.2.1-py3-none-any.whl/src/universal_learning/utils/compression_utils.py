"""
🗜️ Compression Utilities for Universal Learning
=============================================

Utilities for data compression analysis, which forms the basis for
Kolmogorov complexity estimation in universal learning systems.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import zlib
import bz2
import lzma
import gzip
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class CompressionResult:
    """Results from compression analysis."""
    original_size: int
    compressed_size: int
    compression_ratio: float
    compressor: str
    time_taken: float


def compress_sequence(
    sequence: Union[List[Any], str, bytes],
    method: str = 'zlib'
) -> CompressionResult:
    """Compress a sequence using specified method."""
    import time
    
    # Convert sequence to bytes
    if isinstance(sequence, list):
        # Convert list to string then to bytes
        data_str = ''.join(str(item) for item in sequence)
        data_bytes = data_str.encode('utf-8')
    elif isinstance(sequence, str):
        data_bytes = sequence.encode('utf-8')
    elif isinstance(sequence, bytes):
        data_bytes = sequence
    else:
        raise ValueError(f"Unsupported sequence type: {type(sequence)}")
    
    original_size = len(data_bytes)
    start_time = time.time()
    
    # Apply compression
    if method == 'zlib':
        compressed = zlib.compress(data_bytes)
    elif method == 'bz2':
        compressed = bz2.compress(data_bytes)
    elif method == 'lzma':
        compressed = lzma.compress(data_bytes)
    elif method == 'gzip':
        compressed = gzip.compress(data_bytes)
    else:
        raise ValueError(f"Unknown compression method: {method}")
    
    end_time = time.time()
    compressed_size = len(compressed)
    compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
    
    return CompressionResult(
        original_size=original_size,
        compressed_size=compressed_size,
        compression_ratio=compression_ratio,
        compressor=method,
        time_taken=end_time - start_time
    )


def estimate_compression_ratio(
    sequence: Union[List[Any], str, bytes],
    methods: Optional[List[str]] = None
) -> Dict[str, float]:
    """Estimate compression ratios using multiple methods."""
    if methods is None:
        methods = ['zlib', 'bz2', 'lzma']
    
    ratios = {}
    for method in methods:
        try:
            result = compress_sequence(sequence, method)
            ratios[method] = result.compression_ratio
        except Exception as e:
            # If compression fails, assume no compression
            ratios[method] = 1.0
    
    return ratios


def available_compressors() -> List[str]:
    """Get list of available compression methods."""
    compressors = []
    
    # Test each compressor
    test_data = b"test data for compression"
    
    for method in ['zlib', 'bz2', 'lzma', 'gzip']:
        try:
            if method == 'zlib':
                zlib.compress(test_data)
            elif method == 'bz2':
                bz2.compress(test_data)
            elif method == 'lzma':
                lzma.compress(test_data)
            elif method == 'gzip':
                gzip.compress(test_data)
            compressors.append(method)
        except:
            pass
    
    return compressors


def best_compressor(
    sequence: Union[List[Any], str, bytes],
    methods: Optional[List[str]] = None
) -> Tuple[str, float]:
    """Find the best compressor for a given sequence."""
    if methods is None:
        methods = available_compressors()
    
    ratios = estimate_compression_ratio(sequence, methods)
    
    if not ratios:
        return 'none', 1.0
    
    best_method = min(ratios.keys(), key=lambda k: ratios[k])
    best_ratio = ratios[best_method]
    
    return best_method, best_ratio


def normalized_compression_distance(
    seq1: Union[List[Any], str, bytes],
    seq2: Union[List[Any], str, bytes],
    method: str = 'zlib'
) -> float:
    """
    Calculate Normalized Compression Distance between two sequences.
    
    NCD(x,y) = [C(xy) - min(C(x),C(y))] / max(C(x),C(y))
    where C(x) is the compressed length of x.
    """
    # Compress individual sequences
    result1 = compress_sequence(seq1, method)
    result2 = compress_sequence(seq2, method)
    
    # Create concatenated sequence
    if isinstance(seq1, list) and isinstance(seq2, list):
        combined = seq1 + seq2
    elif isinstance(seq1, str) and isinstance(seq2, str):
        combined = seq1 + seq2
    elif isinstance(seq1, bytes) and isinstance(seq2, bytes):
        combined = seq1 + seq2
    else:
        # Convert both to strings and concatenate
        str1 = str(seq1) if not isinstance(seq1, str) else seq1
        str2 = str(seq2) if not isinstance(seq2, str) else seq2
        combined = str1 + str2
    
    result_combined = compress_sequence(combined, method)
    
    # Calculate NCD
    c1 = result1.compressed_size
    c2 = result2.compressed_size
    c12 = result_combined.compressed_size
    
    min_c = min(c1, c2)
    max_c = max(c1, c2)
    
    if max_c == 0:
        return 0.0
    
    ncd = (c12 - min_c) / max_c
    return max(0.0, min(1.0, ncd))  # Clamp to [0, 1]


def estimate_entropy_from_compression(
    sequence: Union[List[Any], str, bytes],
    method: str = 'zlib'
) -> float:
    """Estimate Shannon entropy using compression."""
    result = compress_sequence(sequence, method)
    
    if result.original_size == 0:
        return 0.0
    
    # Estimate entropy as compressed size in bits per symbol
    compressed_bits = result.compressed_size * 8
    num_symbols = result.original_size
    
    entropy_estimate = compressed_bits / num_symbols
    return entropy_estimate


def lempel_ziv_complexity(sequence: Union[str, List[Any]]) -> int:
    """
    Calculate Lempel-Ziv complexity of a sequence.
    
    This is a direct measure of algorithmic complexity based on
    the number of distinct substrings.
    """
    if isinstance(sequence, list):
        # Convert list to string
        s = ''.join(str(item) for item in sequence)
    else:
        s = str(sequence)
    
    if not s:
        return 0
    
    n = len(s)
    complexity = 0
    i = 0
    
    while i < n:
        # Find the longest prefix of s[i:] that has appeared before
        longest_match = 0
        for j in range(1, n - i + 1):
            substring = s[i:i+j]
            if substring in s[:i]:
                longest_match = j
            else:
                break
        
        # If no match found, the complexity increases by 1
        if longest_match == 0:
            complexity += 1
            i += 1
        else:
            # Move past the matched substring
            complexity += 1
            i += longest_match
    
    return complexity


def compression_based_similarity(
    seq1: Union[List[Any], str, bytes],
    seq2: Union[List[Any], str, bytes],
    method: str = 'zlib'
) -> float:
    """
    Calculate similarity between sequences based on compression.
    
    Returns value between 0 (completely different) and 1 (identical).
    """
    ncd = normalized_compression_distance(seq1, seq2, method)
    similarity = 1.0 - ncd
    return max(0.0, min(1.0, similarity))


def detect_compression_patterns(
    sequence: Union[List[Any], str, bytes]
) -> Dict[str, Any]:
    """Detect patterns in sequence using compression analysis."""
    patterns = {}
    
    # Try different compression methods
    ratios = estimate_compression_ratio(sequence)
    patterns['compression_ratios'] = ratios
    
    # Find best compressor
    best_method, best_ratio = best_compressor(sequence)
    patterns['best_compressor'] = best_method
    patterns['best_compression_ratio'] = best_ratio
    
    # Estimate complexity
    patterns['lz_complexity'] = lempel_ziv_complexity(sequence)
    patterns['entropy_estimate'] = estimate_entropy_from_compression(sequence)
    
    # Analyze compression efficiency
    if best_ratio < 0.3:
        patterns['compressibility'] = 'highly_compressible'
    elif best_ratio < 0.7:
        patterns['compressibility'] = 'moderately_compressible'
    else:
        patterns['compressibility'] = 'poorly_compressible'
    
    return patterns


def adaptive_compression_test(
    sequence: Union[List[Any], str, bytes],
    window_size: int = 100
) -> List[float]:
    """Test compression ratios over sliding windows of the sequence."""
    if isinstance(sequence, list):
        seq_len = len(sequence)
        ratios = []
        
        for i in range(0, seq_len - window_size + 1, window_size // 2):
            window = sequence[i:i + window_size]
            result = compress_sequence(window)
            ratios.append(result.compression_ratio)
        
        return ratios
    
    elif isinstance(sequence, str):
        seq_len = len(sequence)
        ratios = []
        
        for i in range(0, seq_len - window_size + 1, window_size // 2):
            window = sequence[i:i + window_size]
            result = compress_sequence(window)
            ratios.append(result.compression_ratio)
        
        return ratios
    
    else:
        # For bytes, treat similarly
        seq_len = len(sequence)
        ratios = []
        
        for i in range(0, seq_len - window_size + 1, window_size // 2):
            window = sequence[i:i + window_size]
            result = compress_sequence(window)
            ratios.append(result.compression_ratio)
        
        return ratios