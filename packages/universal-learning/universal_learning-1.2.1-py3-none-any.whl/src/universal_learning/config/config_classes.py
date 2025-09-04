"""
⚙️ Configuration Classes for Universal Learning
==============================================

This module defines dataclass-based configuration objects for the
universal learning system, providing structured parameter management.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import numpy as np

from .enums import (
    ProgramLanguage,
    ComplexityMethod,
    PredictionMethod,
    EnumerationStrategy,
    OptimizationMethod,
    DataType,
    ValidationMethod
)


@dataclass
class SolomonoffConfig:
    """Configuration for Solomonoff Induction algorithm."""
    
    # Program enumeration settings
    max_program_length: int = 20
    time_budget: int = 1000000
    
    # Universal machine settings
    universal_machine: ProgramLanguage = ProgramLanguage.PYTHON_SUBSET
    enumeration_strategy: EnumerationStrategy = EnumerationStrategy.LENGTH_FIRST
    
    # Approximation methods
    approximation_methods: List[str] = field(default_factory=lambda: ['compression', 'context', 'patterns'])
    
    # Caching and performance
    enable_caching: bool = True
    max_cache_size: int = 10000
    
    # Numerical settings
    min_probability: float = 1e-100
    complexity_penalty: float = 1.0
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.max_program_length <= 0:
            raise ValueError("Max program length must be positive")
        if self.time_budget <= 0:
            raise ValueError("Time budget must be positive")
        if not 0 < self.min_probability <= 1:
            raise ValueError("Min probability must be in (0, 1]")
        return True


@dataclass
class ProgramEnumerationConfig:
    """Configuration for program enumeration."""
    
    # Language settings
    language: ProgramLanguage = ProgramLanguage.PYTHON_SUBSET
    custom_alphabet: Optional[str] = None
    
    # Enumeration bounds
    max_program_length: int = 20
    max_programs_per_length: int = 10000
    
    # Execution limits
    max_execution_steps: int = 10000
    max_memory_usage: int = 1000000
    timeout_seconds: float = 1.0
    
    # Strategy settings
    enumeration_strategy: EnumerationStrategy = EnumerationStrategy.LENGTH_FIRST
    parallel_execution: bool = False
    num_workers: Optional[int] = None
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.max_program_length <= 0:
            raise ValueError("Max program length must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")
        if self.max_execution_steps <= 0:
            raise ValueError("Max execution steps must be positive")
        return True


@dataclass
class ComplexityConfig:
    """Configuration for Kolmogorov complexity estimation."""
    
    # Primary method
    default_method: ComplexityMethod = ComplexityMethod.HYBRID
    
    # Compression settings
    compression_libraries: List[str] = field(default_factory=lambda: ['zlib', 'bz2', 'lzma'])
    
    # Statistical settings
    entropy_estimation_method: str = 'empirical'
    pattern_detection_enabled: bool = True
    
    # Performance settings
    enable_caching: bool = True
    max_cache_entries: int = 5000
    
    # Approximation tolerances
    approximation_tolerance: float = 0.1
    confidence_threshold: float = 0.8
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if not 0 < self.approximation_tolerance <= 1:
            raise ValueError("Approximation tolerance must be in (0, 1]")
        if not 0 < self.confidence_threshold <= 1:
            raise ValueError("Confidence threshold must be in (0, 1]")
        return True


@dataclass
class PredictionConfig:
    """Configuration for universal prediction."""
    
    # Prediction method
    method: PredictionMethod = PredictionMethod.SOLOMONOFF_INDUCTION
    
    # Prediction parameters
    num_predictions: int = 1
    prediction_horizon: int = 10
    
    # Confidence settings
    min_confidence: float = 0.1
    confidence_method: str = 'ensemble'
    
    # Ensemble settings (for ensemble method)
    ensemble_methods: List[PredictionMethod] = field(default_factory=lambda: [
        PredictionMethod.SOLOMONOFF_INDUCTION,
        PredictionMethod.PATTERN_MATCHING,
        PredictionMethod.COMPRESSION_BASED
    ])
    ensemble_weights: Optional[List[float]] = None
    
    # Validation settings
    validation_method: ValidationMethod = ValidationMethod.HOLDOUT
    validation_split: float = 0.2
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.num_predictions <= 0:
            raise ValueError("Number of predictions must be positive")
        if not 0 < self.min_confidence <= 1:
            raise ValueError("Min confidence must be in (0, 1]")
        if not 0 < self.validation_split < 1:
            raise ValueError("Validation split must be in (0, 1)")
        
        if self.ensemble_weights:
            if len(self.ensemble_weights) != len(self.ensemble_methods):
                raise ValueError("Ensemble weights must match number of methods")
            if not np.isclose(sum(self.ensemble_weights), 1.0):
                raise ValueError("Ensemble weights must sum to 1.0")
        
        return True


@dataclass
class UniversalLearningConfig:
    """Main configuration class combining all subsystem configurations."""
    
    # Component configurations
    solomonoff_config: SolomonoffConfig = field(default_factory=SolomonoffConfig)
    enumeration_config: ProgramEnumerationConfig = field(default_factory=ProgramEnumerationConfig)
    complexity_config: ComplexityConfig = field(default_factory=ComplexityConfig)
    prediction_config: PredictionConfig = field(default_factory=PredictionConfig)
    
    # Data settings
    data_type: DataType = DataType.NUMERIC_SEQUENCES
    sequence_length_limit: int = 1000
    
    # Learning settings
    optimization_method: OptimizationMethod = OptimizationMethod.NONE
    learning_rate: float = 0.001
    adaptation_enabled: bool = True
    
    # Performance settings
    parallel_processing: bool = False
    max_memory_gb: Optional[float] = None
    
    # Logging and debugging
    debug_mode: bool = False
    verbose: bool = False
    log_level: str = "INFO"
    
    # Experiment tracking
    experiment_name: Optional[str] = None
    save_intermediate_results: bool = True
    results_directory: str = "./results"
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate all configuration components."""
        self.solomonoff_config.validate()
        self.enumeration_config.validate()
        self.complexity_config.validate()
        self.prediction_config.validate()
        
        # Cross-component validation
        if self.sequence_length_limit <= 0:
            raise ValueError("Sequence length limit must be positive")
        
        if self.learning_rate <= 0:
            raise ValueError("Learning rate must be positive")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'solomonoff_config': self.solomonoff_config.__dict__,
            'enumeration_config': self.enumeration_config.__dict__,
            'complexity_config': self.complexity_config.__dict__,
            'prediction_config': self.prediction_config.__dict__,
            'data_type': self.data_type.value,
            'sequence_length_limit': self.sequence_length_limit,
            'optimization_method': self.optimization_method.value,
            'learning_rate': self.learning_rate,
            'adaptation_enabled': self.adaptation_enabled,
            'parallel_processing': self.parallel_processing,
            'max_memory_gb': self.max_memory_gb,
            'debug_mode': self.debug_mode,
            'verbose': self.verbose,
            'log_level': self.log_level,
            'experiment_name': self.experiment_name,
            'save_intermediate_results': self.save_intermediate_results,
            'results_directory': self.results_directory,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'UniversalLearningConfig':
        """Create configuration from dictionary."""
        # Create component configs
        solomonoff_config = SolomonoffConfig(**config_dict.get('solomonoff_config', {}))
        enumeration_config = ProgramEnumerationConfig(**config_dict.get('enumeration_config', {}))
        complexity_config = ComplexityConfig(**config_dict.get('complexity_config', {}))
        prediction_config = PredictionConfig(**config_dict.get('prediction_config', {}))
        
        # Create main config
        return cls(
            solomonoff_config=solomonoff_config,
            enumeration_config=enumeration_config,
            complexity_config=complexity_config,
            prediction_config=prediction_config,
            data_type=DataType(config_dict.get('data_type', 'numeric_sequences')),
            sequence_length_limit=config_dict.get('sequence_length_limit', 1000),
            optimization_method=OptimizationMethod(config_dict.get('optimization_method', 'none')),
            learning_rate=config_dict.get('learning_rate', 0.001),
            adaptation_enabled=config_dict.get('adaptation_enabled', True),
            parallel_processing=config_dict.get('parallel_processing', False),
            max_memory_gb=config_dict.get('max_memory_gb'),
            debug_mode=config_dict.get('debug_mode', False),
            verbose=config_dict.get('verbose', False),
            log_level=config_dict.get('log_level', 'INFO'),
            experiment_name=config_dict.get('experiment_name'),
            save_intermediate_results=config_dict.get('save_intermediate_results', True),
            results_directory=config_dict.get('results_directory', './results'),
            metadata=config_dict.get('metadata', {})
        )