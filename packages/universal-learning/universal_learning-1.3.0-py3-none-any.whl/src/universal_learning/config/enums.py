"""
📋 Enums
=========

🔬 Research Foundation:
======================
Based on algorithmic information theory and universal induction:
- Solomonoff, R.J. (1964). "A Formal Theory of Inductive Inference"
- Li, M. & Vitányi, P. (1997). "An Introduction to Kolmogorov Complexity and Its Applications"
- Hutter, M. (2005). "Universal Artificial Intelligence"
🎯 ELI5 Summary:
This file is an important component in our AI research system! Like different organs 
in your body that work together to keep you healthy, this file has a specific job that 
helps the overall algorithm work correctly and efficiently.

🧪 Technical Details:
===================
Implementation details and technical specifications for this component.
Designed to work seamlessly within the research framework while
maintaining high performance and accuracy standards.

📋 Component Integration:
========================
    ┌──────────┐
    │   This   │
    │Component │ ←→ Other Components
    └──────────┘
         ↑↓
    System Integration

"""
"""
📋 Enumerations for Universal Learning Configuration
==================================================

This module defines enumeration types used throughout the universal
learning system for consistent parameter specification.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from enum import Enum, auto


class ProgramLanguage(Enum):
    """Programming languages for program enumeration."""
    PYTHON_SUBSET = "python_subset"
    BRAINFUCK = "brainfuck"
    LAMBDA_CALCULUS = "lambda_calculus"
    BINARY_STRINGS = "binary_strings"
    TURING_MACHINE = "turing_machine"
    CUSTOM = "custom"


class ComplexityMethod(Enum):
    """Methods for estimating Kolmogorov complexity."""
    COMPRESSION = "compression"
    ENUMERATION = "enumeration"
    STATISTICAL = "statistical"
    PATTERN_BASED = "pattern_based"
    HYBRID = "hybrid"
    LZ_COMPLEXITY = "lz_complexity"


class PredictionMethod(Enum):
    """Methods for sequence prediction."""
    SOLOMONOFF_INDUCTION = "solomonoff_induction"
    BAYESIAN_MIXTURE = "bayesian_mixture"
    PATTERN_MATCHING = "pattern_matching"
    COMPRESSION_BASED = "compression_based"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"


class EnumerationStrategy(Enum):
    """Strategies for program enumeration."""
    LENGTH_FIRST = "length_first"
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    LEVIN_SEARCH = "levin_search"
    SPEED_PRIOR = "speed_prior"
    RANDOM_SAMPLING = "random_sampling"


class OptimizationMethod(Enum):
    """Optimization methods for learning."""
    NONE = "none"
    GRADIENT_DESCENT = "gradient_descent"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    EVOLUTIONARY = "evolutionary"
    SIMULATED_ANNEALING = "simulated_annealing"


class DataType(Enum):
    """Types of data for universal learning."""
    NUMERIC_SEQUENCES = "numeric_sequences"
    TEXT_SEQUENCES = "text_sequences"
    BINARY_STRINGS = "binary_strings"
    SYMBOLIC_SEQUENCES = "symbolic_sequences"
    MIXED_DATA = "mixed_data"


class ValidationMethod(Enum):
    """Methods for validating predictions."""
    CROSS_VALIDATION = "cross_validation"
    HOLDOUT = "holdout"
    TIME_SERIES_SPLIT = "time_series_split"
    BOOTSTRAP = "bootstrap"
    NONE = "none"