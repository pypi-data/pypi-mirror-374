"""
📊 Sequence Analysis Utilities
=============================

Utility functions for analyzing sequences in universal learning contexts.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import List, Dict, Any, Optional, Union
from collections import Counter


def analyze_sequence(sequence: List[Any]) -> Dict[str, Any]:
    """Analyze a sequence and return comprehensive statistics."""
    if not sequence:
        return {'length': 0, 'unique_elements': 0, 'patterns': []}
    
    analysis = {
        'length': len(sequence),
        'unique_elements': len(set(sequence)),
        'element_counts': dict(Counter(sequence)),
        'patterns': detect_patterns(sequence),
        'statistics': sequence_statistics(sequence)
    }
    
    return analysis


def detect_patterns(sequence: List[Any]) -> List[Dict[str, Any]]:
    """Detect common patterns in a sequence."""
    patterns = []
    
    # Arithmetic progression
    if _is_arithmetic_progression(sequence):
        patterns.append({'type': 'arithmetic', 'confidence': 1.0})
    
    # Geometric progression
    if _is_geometric_progression(sequence):
        patterns.append({'type': 'geometric', 'confidence': 1.0})
    
    # Repetition patterns
    repetitions = _find_repetitions(sequence)
    for rep in repetitions:
        patterns.append({'type': 'repetition', 'pattern': rep, 'confidence': 0.8})
    
    return patterns


def sequence_statistics(sequence: List[Any]) -> Dict[str, Any]:
    """Compute basic statistics for a sequence."""
    if not sequence:
        return {}
    
    try:
        # Try to compute numeric statistics
        numeric_seq = [float(x) for x in sequence]
        return {
            'mean': np.mean(numeric_seq),
            'std': np.std(numeric_seq),
            'min': np.min(numeric_seq),
            'max': np.max(numeric_seq),
            'range': np.max(numeric_seq) - np.min(numeric_seq)
        }
    except (ValueError, TypeError):
        # Non-numeric sequence
        return {
            'type': 'non_numeric',
            'most_common': Counter(sequence).most_common(1)[0] if sequence else None
        }


def validate_sequence(sequence: List[Any]) -> bool:
    """Validate that a sequence is suitable for universal learning."""
    if not isinstance(sequence, list):
        return False
    if len(sequence) == 0:
        return False
    if len(sequence) > 10000:  # Arbitrary large limit
        return False
    return True


def _is_arithmetic_progression(sequence: List[Any]) -> bool:
    """Check if sequence is arithmetic progression."""
    if len(sequence) < 3:
        return False
    
    try:
        numeric_seq = [float(x) for x in sequence]
        diffs = [numeric_seq[i+1] - numeric_seq[i] for i in range(len(numeric_seq)-1)]
        return len(set(diffs)) == 1
    except (ValueError, TypeError):
        return False


def _is_geometric_progression(sequence: List[Any]) -> bool:
    """Check if sequence is geometric progression."""
    if len(sequence) < 3:
        return False
    
    try:
        numeric_seq = [float(x) for x in sequence if x != 0]
        if len(numeric_seq) != len(sequence):
            return False
        ratios = [numeric_seq[i+1] / numeric_seq[i] for i in range(len(numeric_seq)-1)]
        return len(set(ratios)) == 1
    except (ValueError, TypeError, ZeroDivisionError):
        return False


def _find_repetitions(sequence: List[Any]) -> List[List[Any]]:
    """Find repetition patterns in sequence."""
    repetitions = []
    
    # Try different period lengths
    for period in range(1, len(sequence) // 2 + 1):
        pattern = sequence[:period]
        
        # Check if sequence repeats this pattern
        is_repetition = True
        for i in range(period, len(sequence)):
            if sequence[i] != pattern[i % period]:
                is_repetition = False
                break
        
        if is_repetition and len(sequence) >= 2 * period:
            repetitions.append(pattern)
            break  # Take the shortest repetition
    
    return repetitions