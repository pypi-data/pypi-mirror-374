"""
🌌 Core Module for Universal Learning
====================================

This module contains the core components of universal learning algorithms,
including Solomonoff Induction, Universal Turing Machine simulation,
and algorithmic information theory implementations.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .solomonoff_induction import SolomonoffInduction, UniversalDistribution
from .program_enumeration import ProgramEnumerator, ProgramGenerator, UTMSimulator
from .kolmogorov_complexity import KolmogorovComplexity, ComplexityMeasure
from .universal_prediction import UniversalPredictor, PredictionResult
from .algorithmic_probability import AlgorithmicProbability, ProbabilityMeasure

__all__ = [
    # Core Solomonoff Induction
    'SolomonoffInduction',
    'UniversalDistribution',
    
    # Program Enumeration
    'ProgramEnumerator', 
    'ProgramGenerator',
    'UTMSimulator',
    
    # Complexity Measures
    'KolmogorovComplexity',
    'ComplexityMeasure',
    
    # Universal Prediction
    'UniversalPredictor',
    'PredictionResult',
    
    # Algorithmic Probability
    'AlgorithmicProbability',
    'ProbabilityMeasure'
]