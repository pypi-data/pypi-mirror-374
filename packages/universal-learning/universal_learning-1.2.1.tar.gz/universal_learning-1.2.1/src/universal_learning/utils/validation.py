"""
✅ Validation Utilities for Universal Learning
=============================================

Input validation and sanitization functions for universal learning systems,
ensuring data quality and preventing common errors.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import re
import math
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validation check."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_data: Optional[Any] = None


def validate_prediction_config(config: Dict[str, Any]) -> ValidationResult:
    """Validate prediction configuration parameters."""
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ['method', 'num_predictions', 'prediction_horizon']
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate numeric fields
    if 'num_predictions' in config:
        if not isinstance(config['num_predictions'], int) or config['num_predictions'] <= 0:
            errors.append("num_predictions must be a positive integer")
    
    if 'prediction_horizon' in config:
        if not isinstance(config['prediction_horizon'], int) or config['prediction_horizon'] <= 0:
            errors.append("prediction_horizon must be a positive integer")
        elif config['prediction_horizon'] > 1000:
            warnings.append("Large prediction horizon may impact performance")
    
    # Validate confidence thresholds
    if 'min_confidence' in config:
        min_conf = config['min_confidence']
        if not isinstance(min_conf, (int, float)) or not 0 < min_conf <= 1:
            errors.append("min_confidence must be a float between 0 and 1")
    
    # Validate ensemble settings
    if 'ensemble_methods' in config and 'ensemble_weights' in config:
        methods = config['ensemble_methods']
        weights = config['ensemble_weights']
        
        if len(methods) != len(weights):
            errors.append("ensemble_methods and ensemble_weights must have same length")
        
        if abs(sum(weights) - 1.0) > 1e-6:
            errors.append("ensemble_weights must sum to 1.0")
        
        if any(w <= 0 for w in weights):
            errors.append("All ensemble weights must be positive")
    
    # Validate method names
    valid_methods = [
        'solomonoff_induction', 'bayesian_mixture', 'pattern_matching',
        'compression_based', 'neural_network', 'ensemble'
    ]
    
    if 'method' in config and config['method'] not in valid_methods:
        errors.append(f"Invalid method. Must be one of: {valid_methods}")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_sequence_data(sequence: Any) -> ValidationResult:
    """Validate input sequence data for universal learning."""
    errors = []
    warnings = []
    sanitized_data = None
    
    # Check if sequence exists
    if sequence is None:
        errors.append("Sequence cannot be None")
        return ValidationResult(False, errors, warnings)
    
    # Convert to list if needed
    if isinstance(sequence, (tuple, np.ndarray)):
        sequence = list(sequence)
        warnings.append(f"Converted {type(sequence).__name__} to list")
    
    # Check if sequence is list-like
    if not isinstance(sequence, list):
        errors.append("Sequence must be a list or list-like structure")
        return ValidationResult(False, errors, warnings)
    
    # Check minimum length
    if len(sequence) == 0:
        errors.append("Sequence cannot be empty")
        return ValidationResult(False, errors, warnings)
    
    if len(sequence) == 1:
        warnings.append("Single-element sequence may not provide meaningful patterns")
    
    # Check maximum length
    if len(sequence) > 50000:
        errors.append("Sequence too long (>50000 elements), may cause memory issues")
    elif len(sequence) > 10000:
        warnings.append("Large sequence (>10000 elements) may impact performance")
    
    # Analyze data types
    element_types = set(type(x) for x in sequence)
    
    if len(element_types) > 3:
        warnings.append("Sequence contains many different data types, may be difficult to learn")
    
    # Check for missing values
    missing_values = [i for i, x in enumerate(sequence) if x is None or (isinstance(x, float) and math.isnan(x))]
    if missing_values:
        if len(missing_values) > len(sequence) * 0.1:
            errors.append(f"Too many missing values ({len(missing_values)}/{len(sequence)})")
        else:
            warnings.append(f"Found {len(missing_values)} missing values")
    
    # Check for infinite values
    if any(isinstance(x, float) and math.isinf(x) for x in sequence):
        errors.append("Sequence contains infinite values")
    
    # Validate numeric sequences
    numeric_elements = [x for x in sequence if isinstance(x, (int, float)) and not math.isnan(x)]
    if numeric_elements:
        # Check for extreme values
        min_val = min(numeric_elements)
        max_val = max(numeric_elements)
        
        if abs(min_val) > 1e10 or abs(max_val) > 1e10:
            warnings.append("Sequence contains very large numbers, consider normalization")
        
        # Check for constant sequence
        if len(set(numeric_elements)) == 1:
            warnings.append("Sequence appears to be constant")
    
    # Basic sanitization
    sanitized_sequence = []
    for x in sequence:
        if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
            # Skip invalid values
            continue
        sanitized_sequence.append(x)
    
    if len(sanitized_sequence) != len(sequence):
        warnings.append(f"Removed {len(sequence) - len(sanitized_sequence)} invalid values")
    
    sanitized_data = sanitized_sequence
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        sanitized_data=sanitized_data
    )


def sanitize_input_sequence(sequence: Any) -> List[Any]:
    """Sanitize input sequence, removing invalid values."""
    validation_result = validate_sequence_data(sequence)
    
    if validation_result.sanitized_data is not None:
        return validation_result.sanitized_data
    else:
        # Fallback sanitization
        if not isinstance(sequence, list):
            try:
                sequence = list(sequence)
            except:
                return []
        
        sanitized = []
        for x in sequence:
            if x is not None and not (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
                sanitized.append(x)
        
        return sanitized


def validate_program_parameters(
    max_program_length: int,
    time_budget: int,
    max_execution_steps: int,
    timeout_seconds: float
) -> ValidationResult:
    """Validate program enumeration parameters."""
    errors = []
    warnings = []
    
    # Validate max_program_length
    if not isinstance(max_program_length, int) or max_program_length <= 0:
        errors.append("max_program_length must be a positive integer")
    elif max_program_length > 50:
        warnings.append("Very large max_program_length may cause exponential explosion")
    elif max_program_length < 5:
        warnings.append("Small max_program_length may limit expressiveness")
    
    # Validate time_budget
    if not isinstance(time_budget, int) or time_budget <= 0:
        errors.append("time_budget must be a positive integer")
    elif time_budget > 10**8:
        warnings.append("Very large time_budget may cause long execution times")
    
    # Validate max_execution_steps
    if not isinstance(max_execution_steps, int) or max_execution_steps <= 0:
        errors.append("max_execution_steps must be a positive integer")
    elif max_execution_steps > 10**6:
        warnings.append("Large max_execution_steps may cause slow program evaluation")
    
    # Validate timeout_seconds
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        errors.append("timeout_seconds must be a positive number")
    elif timeout_seconds > 60:
        warnings.append("Long timeout may slow down program enumeration")
    elif timeout_seconds < 0.01:
        warnings.append("Very short timeout may prevent programs from executing")
    
    # Cross-validation
    if max_program_length > 30 and time_budget < 100000:
        warnings.append("Large program length with small time budget may not explore enough programs")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_complexity_parameters(
    method: str,
    compression_libraries: List[str],
    approximation_tolerance: float
) -> ValidationResult:
    """Validate Kolmogorov complexity estimation parameters."""
    errors = []
    warnings = []
    
    # Validate method
    valid_methods = ['compression', 'enumeration', 'statistical', 'pattern_based', 'hybrid']
    if method not in valid_methods:
        errors.append(f"Invalid complexity method. Must be one of: {valid_methods}")
    
    # Validate compression libraries
    available_libs = ['zlib', 'bz2', 'lzma', 'gzip']
    for lib in compression_libraries:
        if lib not in available_libs:
            warnings.append(f"Compression library '{lib}' may not be available")
    
    if not compression_libraries:
        errors.append("At least one compression library must be specified")
    
    # Validate approximation tolerance
    if not isinstance(approximation_tolerance, (int, float)):
        errors.append("approximation_tolerance must be a number")
    elif not 0 < approximation_tolerance <= 1:
        errors.append("approximation_tolerance must be between 0 and 1")
    elif approximation_tolerance < 0.01:
        warnings.append("Very strict approximation tolerance may be difficult to achieve")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def detect_data_anomalies(sequence: List[Any]) -> Dict[str, Any]:
    """Detect anomalies in sequence data."""
    anomalies = {
        'outliers': [],
        'missing_values': [],
        'type_inconsistencies': [],
        'patterns': {}
    }
    
    if not sequence:
        return anomalies
    
    # Type analysis
    type_counts = {}
    for i, item in enumerate(sequence):
        item_type = type(item).__name__
        if item_type not in type_counts:
            type_counts[item_type] = []
        type_counts[item_type].append(i)
    
    # Find type inconsistencies
    if len(type_counts) > 1:
        minority_types = {t: indices for t, indices in type_counts.items() 
                         if len(indices) < len(sequence) * 0.1}
        anomalies['type_inconsistencies'] = minority_types
    
    # Find missing values
    anomalies['missing_values'] = [i for i, x in enumerate(sequence) 
                                  if x is None or (isinstance(x, float) and math.isnan(x))]
    
    # Numeric outlier detection
    numeric_values = [(i, x) for i, x in enumerate(sequence) 
                     if isinstance(x, (int, float)) and not math.isnan(x)]
    
    if len(numeric_values) > 10:
        values = [x for i, x in numeric_values]
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        # Z-score based outlier detection
        threshold = 3.0
        for i, x in numeric_values:
            z_score = abs(x - mean_val) / (std_val + 1e-10)
            if z_score > threshold:
                anomalies['outliers'].append({'index': i, 'value': x, 'z_score': z_score})
    
    return anomalies


def validate_solomonoff_parameters(
    max_program_length: int,
    universal_machine: str,
    approximation_methods: List[str],
    min_probability: float
) -> ValidationResult:
    """Validate Solomonoff induction parameters."""
    errors = []
    warnings = []
    
    # Program length validation
    if not isinstance(max_program_length, int) or max_program_length <= 0:
        errors.append("max_program_length must be a positive integer")
    elif max_program_length > 40:
        warnings.append("Large max_program_length may cause computational issues")
    
    # Universal machine validation
    valid_machines = ['python_subset', 'brainfuck', 'lambda_calculus', 'binary_strings', 'turing_machine']
    if universal_machine not in valid_machines:
        errors.append(f"Invalid universal machine. Must be one of: {valid_machines}")
    
    # Approximation methods validation
    valid_approximations = ['compression', 'statistical', 'patterns', 'enumeration', 'context']
    invalid_methods = [m for m in approximation_methods if m not in valid_approximations]
    if invalid_methods:
        errors.append(f"Invalid approximation methods: {invalid_methods}")
    
    if not approximation_methods:
        errors.append("At least one approximation method must be specified")
    
    # Minimum probability validation
    if not isinstance(min_probability, (int, float)):
        errors.append("min_probability must be a number")
    elif not 0 < min_probability <= 1:
        errors.append("min_probability must be between 0 and 1")
    elif min_probability < 1e-100:
        warnings.append("Very small min_probability may cause numerical underflow")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )