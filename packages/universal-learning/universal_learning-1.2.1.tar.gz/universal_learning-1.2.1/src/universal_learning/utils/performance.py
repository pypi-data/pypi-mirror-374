"""
⚡ Performance Monitoring Utilities for Universal Learning
========================================================

Performance monitoring, profiling, and benchmarking utilities for
tracking the efficiency of universal learning algorithms.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import time
import psutil
import sys
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
import functools
import gc


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    execution_time: float
    memory_usage_mb: float
    peak_memory_mb: float
    cpu_percent: float
    function_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'execution_time': self.execution_time,
            'memory_usage_mb': self.memory_usage_mb,
            'peak_memory_mb': self.peak_memory_mb,
            'cpu_percent': self.cpu_percent,
            'function_calls': self.function_calls,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0.0
        }


@dataclass
class BenchmarkResult:
    """Results from benchmarking operations."""
    test_name: str
    metrics: PerformanceMetrics
    success: bool
    error_message: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


class TimeProfiler:
    """Context manager for timing code execution."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        print(f"{self.name} completed in {self.duration:.4f} seconds")
    
    def get_duration(self) -> Optional[float]:
        """Get the measured duration."""
        return self.duration


class MemoryMonitor:
    """Context manager for monitoring memory usage."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.process = psutil.Process()
        self.start_memory = None
        self.peak_memory = None
        self.end_memory = None
    
    def __enter__(self):
        gc.collect()  # Clean up before measurement
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.start_memory
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        gc.collect()  # Clean up after measurement
        self.end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_diff = self.end_memory - self.start_memory
        print(f"{self.name} memory usage: {memory_diff:.2f} MB (peak: {self.peak_memory:.2f} MB)")
    
    def update_peak_memory(self):
        """Update peak memory usage."""
        current_memory = self.process.memory_info().rss / 1024 / 1024
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics."""
        return {
            'start_memory_mb': self.start_memory,
            'end_memory_mb': self.end_memory,
            'peak_memory_mb': self.peak_memory,
            'memory_diff_mb': self.end_memory - self.start_memory if self.end_memory and self.start_memory else 0
        }


def measure_performance(func: Callable) -> Callable:
    """Decorator to measure function performance."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process()
        
        # Pre-execution measurements
        gc.collect()
        start_time = time.time()
        start_memory = process.memory_info().rss / 1024 / 1024
        start_cpu = process.cpu_percent()
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Post-execution measurements
            end_time = time.time()
            gc.collect()
            end_memory = process.memory_info().rss / 1024 / 1024
            end_cpu = process.cpu_percent()
            
            # Calculate metrics
            metrics = PerformanceMetrics(
                execution_time=end_time - start_time,
                memory_usage_mb=end_memory - start_memory,
                peak_memory_mb=max(start_memory, end_memory),
                cpu_percent=(start_cpu + end_cpu) / 2
            )
            
            # Store metrics as function attribute
            if not hasattr(func, '_performance_metrics'):
                func._performance_metrics = []
            func._performance_metrics.append(metrics)
            
            return result
            
        except Exception as e:
            # Record failed execution
            end_time = time.time()
            metrics = PerformanceMetrics(
                execution_time=end_time - start_time,
                memory_usage_mb=0,
                peak_memory_mb=start_memory,
                cpu_percent=0
            )
            
            if not hasattr(func, '_performance_metrics'):
                func._performance_metrics = []
            func._performance_metrics.append(metrics)
            
            raise e
    
    return wrapper


def benchmark_prediction(
    predictor_func: Callable,
    test_sequences: List[Any],
    test_name: str = "Prediction Benchmark"
) -> BenchmarkResult:
    """Benchmark a prediction function on multiple test sequences."""
    
    process = psutil.Process()
    total_time = 0
    total_memory = 0
    peak_memory = 0
    successful_predictions = 0
    errors = []
    
    start_memory = process.memory_info().rss / 1024 / 1024
    overall_start = time.time()
    
    for i, sequence in enumerate(test_sequences):
        try:
            # Measure individual prediction
            gc.collect()
            pred_start = time.time()
            pred_start_memory = process.memory_info().rss / 1024 / 1024
            
            # Execute prediction
            result = predictor_func(sequence)
            
            pred_end = time.time()
            pred_end_memory = process.memory_info().rss / 1024 / 1024
            
            # Accumulate metrics
            pred_time = pred_end - pred_start
            pred_memory = pred_end_memory - pred_start_memory
            
            total_time += pred_time
            total_memory += pred_memory
            peak_memory = max(peak_memory, pred_end_memory)
            successful_predictions += 1
            
        except Exception as e:
            errors.append(f"Sequence {i}: {str(e)}")
    
    overall_end = time.time()
    overall_time = overall_end - overall_start
    
    # Calculate average metrics
    avg_time = total_time / len(test_sequences) if test_sequences else 0
    avg_memory = total_memory / len(test_sequences) if test_sequences else 0
    success_rate = successful_predictions / len(test_sequences) if test_sequences else 0
    
    metrics = PerformanceMetrics(
        execution_time=overall_time,
        memory_usage_mb=avg_memory,
        peak_memory_mb=peak_memory,
        cpu_percent=process.cpu_percent(),
        function_calls=len(test_sequences)
    )
    
    is_successful = len(errors) == 0
    error_message = "; ".join(errors) if errors else None
    
    additional_data = {
        'total_sequences': len(test_sequences),
        'successful_predictions': successful_predictions,
        'success_rate': success_rate,
        'average_time_per_prediction': avg_time,
        'average_memory_per_prediction': avg_memory,
        'errors': errors
    }
    
    return BenchmarkResult(
        test_name=test_name,
        metrics=metrics,
        success=is_successful,
        error_message=error_message,
        additional_data=additional_data
    )


def performance_summary(benchmark_results: List[BenchmarkResult]) -> Dict[str, Any]:
    """Generate summary statistics from multiple benchmark results."""
    if not benchmark_results:
        return {"error": "No benchmark results provided"}
    
    # Collect metrics
    execution_times = []
    memory_usages = []
    peak_memories = []
    success_rates = []
    
    successful_tests = 0
    total_tests = len(benchmark_results)
    
    for result in benchmark_results:
        execution_times.append(result.metrics.execution_time)
        memory_usages.append(result.metrics.memory_usage_mb)
        peak_memories.append(result.metrics.peak_memory_mb)
        
        if result.success:
            successful_tests += 1
        
        # Extract success rate if available
        if 'success_rate' in result.additional_data:
            success_rates.append(result.additional_data['success_rate'])
    
    # Calculate summary statistics
    summary = {
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'test_success_rate': successful_tests / total_tests,
        
        'execution_time': {
            'min': min(execution_times),
            'max': max(execution_times),
            'mean': sum(execution_times) / len(execution_times),
            'total': sum(execution_times)
        },
        
        'memory_usage_mb': {
            'min': min(memory_usages),
            'max': max(memory_usages),
            'mean': sum(memory_usages) / len(memory_usages),
            'peak_overall': max(peak_memories)
        }
    }
    
    # Add prediction success rate summary if available
    if success_rates:
        summary['prediction_success_rate'] = {
            'min': min(success_rates),
            'max': max(success_rates),
            'mean': sum(success_rates) / len(success_rates)
        }
    
    return summary


@contextmanager
def performance_context(name: str = "Operation"):
    """Context manager that combines time and memory profiling."""
    time_profiler = TimeProfiler(name)
    memory_monitor = MemoryMonitor(name)
    
    with time_profiler:
        with memory_monitor:
            yield {
                'time_profiler': time_profiler,
                'memory_monitor': memory_monitor
            }


def profile_function_calls(func: Callable) -> Callable:
    """Decorator to count and profile function calls."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Initialize call counter
        if not hasattr(func, '_call_count'):
            func._call_count = 0
        if not hasattr(func, '_total_time'):
            func._total_time = 0.0
        
        # Time the execution
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            
            # Update statistics
            func._call_count += 1
            func._total_time += (end_time - start_time)
            
            return result
        except Exception as e:
            end_time = time.time()
            func._call_count += 1
            func._total_time += (end_time - start_time)
            raise e
    
    # Add method to get statistics
    def get_stats():
        return {
            'call_count': getattr(func, '_call_count', 0),
            'total_time': getattr(func, '_total_time', 0.0),
            'average_time': getattr(func, '_total_time', 0.0) / max(1, getattr(func, '_call_count', 1))
        }
    
    wrapper.get_stats = get_stats
    return wrapper


def memory_usage_tracker():
    """Get current memory usage statistics."""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
        'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        'percent': process.memory_percent(),       # Percentage of total system memory
        'available_mb': psutil.virtual_memory().available / 1024 / 1024,
        'total_system_mb': psutil.virtual_memory().total / 1024 / 1024
    }


def cpu_usage_tracker():
    """Get current CPU usage statistics."""
    process = psutil.Process()
    
    return {
        'process_percent': process.cpu_percent(),
        'system_percent': psutil.cpu_percent(),
        'core_count': psutil.cpu_count(),
        'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
    }