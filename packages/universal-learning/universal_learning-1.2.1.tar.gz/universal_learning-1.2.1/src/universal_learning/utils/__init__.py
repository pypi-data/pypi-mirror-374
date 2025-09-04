"""
🛠️ Utility Functions for Universal Learning
==========================================

This module provides utility functions for sequence analysis,
data processing, and performance monitoring in universal learning systems.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .sequence_utils import (
    analyze_sequence,
    detect_patterns,
    sequence_statistics,
    validate_sequence
)

from .compression_utils import (
    compress_sequence,
    estimate_compression_ratio,
    available_compressors,
    best_compressor
)

from .validation import (
    validate_prediction_config,
    validate_sequence_data,
    sanitize_input_sequence
)

from .performance import (
    TimeProfiler,
    MemoryMonitor,
    benchmark_prediction,
    performance_summary
)

__all__ = [
    # Sequence utilities
    'analyze_sequence',
    'detect_patterns',
    'sequence_statistics', 
    'validate_sequence',
    
    # Compression utilities
    'compress_sequence',
    'estimate_compression_ratio',
    'available_compressors',
    'best_compressor',
    
    # Validation utilities
    'validate_prediction_config',
    'validate_sequence_data',
    'sanitize_input_sequence',
    
    # Performance utilities
    'TimeProfiler',
    'MemoryMonitor',
    'benchmark_prediction',
    'performance_summary'
]