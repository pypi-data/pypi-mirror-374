"""
🎛️ Default Configurations for Universal Learning
===============================================

This module provides default configuration objects and preset configurations
for common use cases of the universal learning system.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from typing import Dict, List
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
    DataType
)


# Default Solomonoff Configuration
DEFAULT_SOLOMONOFF_CONFIG = SolomonoffConfig(
    max_program_length=15,  # Reasonable for practical use
    time_budget=100000,     # 100K steps per program
    universal_machine=ProgramLanguage.PYTHON_SUBSET,
    enumeration_strategy=EnumerationStrategy.LENGTH_FIRST,
    approximation_methods=['compression', 'statistical', 'patterns'],
    enable_caching=True,
    max_cache_size=5000
)

# Default Program Enumeration Configuration
DEFAULT_ENUMERATION_CONFIG = ProgramEnumerationConfig(
    language=ProgramLanguage.PYTHON_SUBSET,
    max_program_length=15,
    max_programs_per_length=1000,
    max_execution_steps=5000,
    timeout_seconds=0.5,
    enumeration_strategy=EnumerationStrategy.LENGTH_FIRST,
    parallel_execution=False
)

# Default Complexity Configuration
DEFAULT_COMPLEXITY_CONFIG = ComplexityConfig(
    default_method=ComplexityMethod.HYBRID,
    compression_libraries=['zlib', 'bz2'],
    pattern_detection_enabled=True,
    enable_caching=True,
    max_cache_entries=2000
)

# Default Prediction Configuration
DEFAULT_PREDICTION_CONFIG = PredictionConfig(
    method=PredictionMethod.SOLOMONOFF_INDUCTION,
    num_predictions=1,
    prediction_horizon=5,
    min_confidence=0.2,
    ensemble_methods=[
        PredictionMethod.SOLOMONOFF_INDUCTION,
        PredictionMethod.PATTERN_MATCHING,
        PredictionMethod.COMPRESSION_BASED
    ]
)

# Default Universal Learning Configuration
DEFAULT_UNIVERSAL_CONFIG = UniversalLearningConfig(
    solomonoff_config=DEFAULT_SOLOMONOFF_CONFIG,
    enumeration_config=DEFAULT_ENUMERATION_CONFIG,
    complexity_config=DEFAULT_COMPLEXITY_CONFIG,
    prediction_config=DEFAULT_PREDICTION_CONFIG,
    data_type=DataType.NUMERIC_SEQUENCES,
    sequence_length_limit=100,
    debug_mode=False,
    verbose=False
)

# Fast Configuration (for quick experimentation)
FAST_CONFIG = UniversalLearningConfig(
    solomonoff_config=SolomonoffConfig(
        max_program_length=10,
        time_budget=10000,
        approximation_methods=['compression', 'patterns'],
        max_cache_size=1000
    ),
    enumeration_config=ProgramEnumerationConfig(
        max_program_length=10,
        max_programs_per_length=100,
        max_execution_steps=1000,
        timeout_seconds=0.1
    ),
    complexity_config=ComplexityConfig(
        default_method=ComplexityMethod.COMPRESSION,
        compression_libraries=['zlib'],
        max_cache_entries=500
    ),
    prediction_config=PredictionConfig(
        method=PredictionMethod.PATTERN_MATCHING,
        num_predictions=1,
        prediction_horizon=3
    ),
    sequence_length_limit=50,
    debug_mode=True
)

# High Accuracy Configuration (for research)
ACCURACY_CONFIG = UniversalLearningConfig(
    solomonoff_config=SolomonoffConfig(
        max_program_length=25,
        time_budget=1000000,
        approximation_methods=['compression', 'statistical', 'patterns', 'enumeration'],
        max_cache_size=20000
    ),
    enumeration_config=ProgramEnumerationConfig(
        max_program_length=25,
        max_programs_per_length=10000,
        max_execution_steps=50000,
        timeout_seconds=5.0,
        parallel_execution=True
    ),
    complexity_config=ComplexityConfig(
        default_method=ComplexityMethod.HYBRID,
        compression_libraries=['zlib', 'bz2', 'lzma'],
        pattern_detection_enabled=True,
        max_cache_entries=10000
    ),
    prediction_config=PredictionConfig(
        method=PredictionMethod.ENSEMBLE,
        num_predictions=5,
        prediction_horizon=20,
        min_confidence=0.1
    ),
    sequence_length_limit=500,
    parallel_processing=True
)

# Text Processing Configuration
TEXT_CONFIG = UniversalLearningConfig(
    solomonoff_config=SolomonoffConfig(
        max_program_length=20,
        universal_machine=ProgramLanguage.PYTHON_SUBSET,
        approximation_methods=['compression', 'statistical'],
        time_budget=500000
    ),
    enumeration_config=ProgramEnumerationConfig(
        language=ProgramLanguage.PYTHON_SUBSET,
        max_program_length=20,
        timeout_seconds=2.0
    ),
    complexity_config=ComplexityConfig(
        default_method=ComplexityMethod.COMPRESSION,
        compression_libraries=['zlib', 'bz2', 'lzma']
    ),
    prediction_config=PredictionConfig(
        method=PredictionMethod.COMPRESSION_BASED,
        num_predictions=1,
        prediction_horizon=10
    ),
    data_type=DataType.TEXT_SEQUENCES,
    sequence_length_limit=1000
)

# Binary Data Configuration
BINARY_CONFIG = UniversalLearningConfig(
    solomonoff_config=SolomonoffConfig(
        max_program_length=30,
        universal_machine=ProgramLanguage.BINARY_STRINGS,
        approximation_methods=['compression', 'patterns']
    ),
    enumeration_config=ProgramEnumerationConfig(
        language=ProgramLanguage.BINARY_STRINGS,
        max_program_length=30,
        max_programs_per_length=2000
    ),
    complexity_config=ComplexityConfig(
        default_method=ComplexityMethod.COMPRESSION,
        pattern_detection_enabled=True
    ),
    prediction_config=PredictionConfig(
        method=PredictionMethod.PATTERN_MATCHING,
        num_predictions=8,  # Predict next byte
        prediction_horizon=32
    ),
    data_type=DataType.BINARY_STRINGS,
    sequence_length_limit=2000
)

# All preset configurations
PRESET_CONFIGS: Dict[str, UniversalLearningConfig] = {
    'default': DEFAULT_UNIVERSAL_CONFIG,
    'fast': FAST_CONFIG,
    'accuracy': ACCURACY_CONFIG,
    'text': TEXT_CONFIG,
    'binary': BINARY_CONFIG
}


def get_config(preset_name: str = 'default') -> UniversalLearningConfig:
    """
    Get a preset configuration by name.
    
    Parameters
    ----------
    preset_name : str
        Name of the preset configuration
        
    Returns
    -------
    UniversalLearningConfig
        The requested configuration
        
    Raises
    ------
    ValueError
        If preset_name is not found
    """
    if preset_name not in PRESET_CONFIGS:
        available = list(PRESET_CONFIGS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
    
    return PRESET_CONFIGS[preset_name]


def list_presets() -> List[str]:
    """List available preset configuration names."""
    return list(PRESET_CONFIGS.keys())