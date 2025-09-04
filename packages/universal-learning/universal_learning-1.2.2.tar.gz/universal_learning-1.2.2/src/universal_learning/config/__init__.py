"""
⚙️ Configuration Module for Universal Learning
==============================================

This module provides configuration classes and defaults for
universal learning algorithms and Solomonoff induction.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .config_classes import (
    UniversalLearningConfig,
    SolomonoffConfig,
    ProgramEnumerationConfig,
    ComplexityConfig,
    PredictionConfig
)

from .enums import (
    ProgramLanguage,
    ComplexityMethod,
    PredictionMethod,
    EnumerationStrategy,
    OptimizationMethod,
    DataType,
    ValidationMethod
)

from .defaults import (
    DEFAULT_SOLOMONOFF_CONFIG,
    DEFAULT_ENUMERATION_CONFIG,
    PRESET_CONFIGS,
    get_config,
    list_presets
)

__all__ = [
    # Config Classes
    'UniversalLearningConfig',
    'SolomonoffConfig',
    'ProgramEnumerationConfig', 
    'ComplexityConfig',
    'PredictionConfig',
    
    # Enums
    'ProgramLanguage',
    'ComplexityMethod',
    'PredictionMethod',
    'EnumerationStrategy',
    'OptimizationMethod',
    'DataType',
    'ValidationMethod',
    
    # Defaults
    'DEFAULT_SOLOMONOFF_CONFIG',
    'DEFAULT_ENUMERATION_CONFIG',
    'PRESET_CONFIGS',
    'get_config',
    'list_presets'
]