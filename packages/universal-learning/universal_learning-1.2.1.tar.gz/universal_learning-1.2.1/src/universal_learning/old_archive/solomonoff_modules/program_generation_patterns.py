#!/usr/bin/env python3
"""
🎨 Universal Learning - Pattern-Based Program Generation Module
===============================================================

Mathematical sequence pattern detection for Solomonoff induction.
Extracted from program_generation.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Solomonoff (1964) - Universal induction via program enumeration

This module implements pattern-specific program generators:
- Constant sequences
- Periodic patterns  
- Arithmetic progressions
- Fibonacci-like sequences
- Polynomial patterns

Each method follows the universal distribution weighting: 2^(-complexity)
"""

import numpy as np
from typing import List, Dict, Optional, Union
from abc import ABC, abstractmethod

class PatternGenerationMixin:
    """
    Pattern-based program generation mixin for mathematical sequences.
    
    Implements fast detection of common mathematical patterns that appear
    frequently in real-world data and have simple algorithmic descriptions.
    """
    
    def _generate_constant_programs(self, sequence: List[int]) -> List[Dict]:
        """
        🔄 Constant Sequence Program Generation
        
        ELI5: This detects sequences where every number is the same, like [5,5,5,5,5].
        These are super simple, so they get very high probability!
        
        Technical Implementation:
        ========================
        Detects constant sequences of the form:
        
        a_n = c for all n
        
        where c is a constant value ∈ {0, 1, ..., alphabet_size-1}
        
        Complexity Estimation:
        =====================
        Constant programs require only:
        - The constant value c: log₂(alphabet_size) bits
        - Pattern type identifier: minimal overhead
        
        We use complexity = 2 as approximation, giving constant sequences
        high weight 2^(-2) = 1/4 in the universal distribution.
        """
        programs = []
        
        if not sequence:
            return programs
            
        # Check if all elements are the same
        first_value = sequence[0]
        if all(x == first_value for x in sequence):
            programs.append({
                'type': 'constant',
                'value': first_value,
                'complexity': 2,  # Very simple program
                'fits_sequence': True,
                'next_prediction': first_value,
                'weight': 2**(-2),
                'method': 'pattern_detection',
                'description': f'Constant sequence outputting {first_value}',
                'accuracy': 1.0
            })
            
        return programs
    
    def _generate_periodic_programs(self, sequence: List[int]) -> List[Dict]:
        """
        🔁 Periodic Pattern Program Generation
        
        ELI5: This finds repeating patterns like [1,2,3,1,2,3,1,2,3] where
        the same chunk repeats over and over.
        
        Technical Implementation:
        ========================
        Detects periodic sequences with period p:
        
        a_n = a_{n mod p}
        
        For period p, the sequence repeats every p elements.
        
        Complexity Estimation:
        =====================
        Periodic programs require:
        - Period length p: log₂(sequence_length) bits
        - Pattern values: p × log₂(alphabet_size) bits
        
        We approximate complexity = 3 + log₂(period) for practical weighting.
        """
        programs = []
        
        if len(sequence) < 2:
            return programs
            
        # Try different periods up to half the sequence length
        max_period = min(len(sequence) // 2, 10)  # Limit for efficiency
        
        for period in range(1, max_period + 1):
            # Check if sequence repeats with this period
            is_periodic = True
            for i in range(len(sequence)):
                if sequence[i] != sequence[i % period]:
                    is_periodic = False
                    break
                    
            if is_periodic:
                pattern = sequence[:period]
                next_pred = sequence[len(sequence) % period] if len(sequence) % period < len(pattern) else pattern[0]
                
                complexity = 3 + np.log2(period + 1)  # Encoding period + pattern
                programs.append({
                    'type': 'periodic',
                    'period': period,
                    'pattern': pattern,
                    'complexity': complexity,
                    'fits_sequence': True,
                    'next_prediction': next_pred,
                    'weight': 2**(-complexity),
                    'method': 'pattern_detection',
                    'description': f'Periodic sequence with period {period}: {pattern}',
                    'accuracy': 1.0
                })
                
        return programs
    
    def _generate_arithmetic_programs(self, sequence: List[int]) -> List[Dict]:
        """
        📈 Arithmetic Progression Program Generation
        
        ELI5: This looks for sequences where you add the same number each time,
        like counting by 2s: [0,2,4,6,8] or counting down by 3s: [10,7,4,1].
        
        Technical Implementation:
        ========================
        Detects arithmetic progressions of the form:
        
        a_n = a_0 + n × d
        
        where:
        - a_0 is the starting value (first term)
        - d is the common difference between consecutive terms
        - n is the position index (0, 1, 2, ...)
        
        Complexity: 4 bits (start value + difference + overhead)
        """
        programs = []
        
        if len(sequence) < 2:
            return programs
            
        # Try arithmetic progressions
        for start in range(self.alphabet_size):
            for diff in range(-2, 3):  # Small differences
                if diff == 0:
                    continue
                    
                # Check if arithmetic progression fits
                fits = True
                for i, value in enumerate(sequence):
                    expected = (start + i * diff) % self.alphabet_size
                    if value != expected:
                        fits = False
                        break
                        
                if fits:
                    next_pred = (start + len(sequence) * diff) % self.alphabet_size
                    programs.append({
                        'type': 'arithmetic',
                        'start': start,
                        'difference': diff,
                        'complexity': 4,  # Start + difference encoding
                        'fits_sequence': True,
                        'next_prediction': next_pred,
                        'weight': 2**(-4),
                        'method': 'pattern_detection',
                        'description': f'Arithmetic sequence: start={start}, diff={diff}',
                        'accuracy': 1.0
                    })
                    
        return programs
    
    def _generate_fibonacci_programs(self, sequence: List[int]) -> List[Dict]:
        """
        🌀 Fibonacci-Like Sequence Program Generation
        
        ELI5: This looks for sequences where each number is the sum of the two 
        before it, like the famous Fibonacci: [0,1,1,2,3,5,8,13,21]. But it can
        start with any two numbers!
        
        Technical Implementation:
        ========================
        Detects generalized Fibonacci sequences:
        
        F_0 = a, F_1 = b
        F_n = (F_{n-1} + F_{n-2}) mod alphabet_size for n ≥ 2
        
        Complexity: 5 bits (two starting values + recurrence rule)
        """
        programs = []
        
        if len(sequence) < 3:
            return programs
            
        # Try different starting pairs
        for a in range(min(self.alphabet_size, 10)):  # Limit search space
            for b in range(min(self.alphabet_size, 10)):
                # Generate Fibonacci-like sequence
                fib_seq = [a, b]
                for i in range(2, len(sequence)):
                    next_val = (fib_seq[i-1] + fib_seq[i-2]) % self.alphabet_size
                    fib_seq.append(next_val)
                
                # Check if it matches
                if fib_seq[:len(sequence)] == sequence:
                    next_pred = (sequence[-1] + sequence[-2]) % self.alphabet_size if len(sequence) >= 2 else a
                    
                    programs.append({
                        'type': 'fibonacci',
                        'start_a': a,
                        'start_b': b,
                        'complexity': 5,  # Two starting values + recurrence
                        'fits_sequence': True,
                        'next_prediction': next_pred,
                        'weight': 2**(-5),
                        'method': 'pattern_detection',
                        'description': f'Fibonacci-like sequence: F_0={a}, F_1={b}',
                        'accuracy': 1.0
                    })
                    
        return programs
    
    def _generate_polynomial_programs(self, sequence: List[int]) -> List[Dict]:
        """
        📊 Polynomial Sequence Program Generation
        
        ELI5: This looks for sequences that follow polynomial patterns like
        squares [1,4,9,16,25] or cubes [1,8,27,64,125].
        
        Technical Implementation:
        ========================
        Detects polynomial sequences up to degree 3:
        
        P(n) = a₃n³ + a₂n² + a₁n + a₀
        
        Uses finite differences to detect polynomial patterns:
        - Degree 1: Constant first differences (arithmetic)
        - Degree 2: Constant second differences (quadratic)
        - Degree 3: Constant third differences (cubic)
        
        Complexity: 6 + degree (coefficients + polynomial order)
        """
        programs = []
        
        if len(sequence) < 4:  # Need at least 4 points for cubic detection
            return programs
        
        # Convert to numpy for easier computation
        seq_array = np.array(sequence, dtype=float)
        
        # Compute finite differences
        diffs = [seq_array]
        for degree in range(1, min(4, len(sequence))):
            next_diff = np.diff(diffs[-1])
            if len(next_diff) == 0:
                break
            diffs.append(next_diff)
            
            # Check if this difference is constant (within tolerance)
            if len(next_diff) > 1 and np.allclose(next_diff, next_diff[0], rtol=1e-6):
                # Found polynomial of degree 'degree'
                complexity = 6 + degree
                
                # Predict next value by continuing the difference pattern
                next_pred = int(sequence[-1] + next_diff[0]) % self.alphabet_size
                
                programs.append({
                    'type': 'polynomial',
                    'degree': degree,
                    'differences': [float(d[0]) if len(d) > 0 else 0.0 for d in diffs],
                    'complexity': complexity,
                    'fits_sequence': True,
                    'next_prediction': next_pred,
                    'weight': 2**(-complexity),
                    'method': 'pattern_detection',
                    'description': f'Polynomial sequence of degree {degree}',
                    'accuracy': 0.9  # Slightly lower due to numerical approximation
                })
                
        return programs
    
    def _generate_power_sequence_programs(self, sequence: List[int]) -> List[Dict]:
        """
        ⚡ Power Sequence Program Generation
        
        ELI5: This finds sequences like powers of 2 [1,2,4,8,16] or 
        powers of 3 [1,3,9,27,81].
        
        Technical Implementation:
        ========================
        Detects geometric sequences:
        
        a_n = a_0 × r^n
        
        where r is the common ratio.
        
        Complexity: 5 bits (base + ratio + overhead)
        """
        programs = []
        
        if len(sequence) < 3:
            return programs
        
        # Try small bases and ratios
        for base in range(1, min(self.alphabet_size, 5)):
            for ratio in range(2, 5):  # Common ratios: 2, 3, 4
                # Generate power sequence
                power_seq = []
                for i in range(len(sequence)):
                    val = (base * (ratio ** i)) % self.alphabet_size
                    power_seq.append(val)
                
                if power_seq == sequence:
                    next_pred = (base * (ratio ** len(sequence))) % self.alphabet_size
                    
                    programs.append({
                        'type': 'power',
                        'base': base,
                        'ratio': ratio,
                        'complexity': 5,
                        'fits_sequence': True,
                        'next_prediction': next_pred,
                        'weight': 2**(-5),
                        'method': 'pattern_detection',
                        'description': f'Power sequence: {base} × {ratio}^n',
                        'accuracy': 1.0
                    })
                    
        return programs
    
    def _generate_prime_programs(self, sequence: List[int]) -> List[Dict]:
        """
        🔢 Prime Sequence Program Generation
        
        ELI5: This checks if the sequence is prime numbers [2,3,5,7,11,13,17,19,23].
        
        Uses a simple prime sieve for detection.
        Complexity: 8 bits (prime generation algorithm)
        """
        programs = []
        
        if len(sequence) < 3:
            return programs
        
        # Generate primes up to maximum possible value
        max_val = max(max(sequence), 100)  # At least check up to 100
        
        # Simple sieve of Eratosthenes
        sieve = [True] * (max_val + 1)
        sieve[0] = sieve[1] = False
        
        for i in range(2, int(max_val**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, max_val + 1, i):
                    sieve[j] = False
        
        primes = [i for i in range(2, max_val + 1) if sieve[i]]
        
        # Check if sequence matches first N primes
        if len(sequence) <= len(primes) and sequence == primes[:len(sequence)]:
            next_pred = primes[len(sequence)] if len(sequence) < len(primes) else sequence[-1] + 1
            
            programs.append({
                'type': 'prime',
                'complexity': 8,  # Prime generation algorithm
                'fits_sequence': True,
                'next_prediction': next_pred % self.alphabet_size,
                'weight': 2**(-8),
                'method': 'pattern_detection',
                'description': 'Sequence of prime numbers',
                'accuracy': 1.0
            })
            
        return programs