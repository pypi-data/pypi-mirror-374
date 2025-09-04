#!/usr/bin/env python3
"""
🎯 Universal Learning - Program Generation Core Module
======================================================

Core program generation coordination for Solomonoff induction.
Extracted from program_generation.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Solomonoff (1964) - Universal induction via program enumeration

This module provides the main ProgramGenerationMixin class that coordinates
all program generation methods through configurable routing.

Imports and coordinates:
- Pattern-based detection (arithmetic, fibonacci, etc.)
- UTM simulations (brainfuck, lambda calculus, binary)  
- Advanced methods (compression, context tree, hybrid)

Total original size: 2,356 lines → Split into 4 modules ≤ 600 lines each
"""

import numpy as np
from typing import List, Dict, Optional, Union
from enum import Enum

# Import the specialized mixins
from .program_generation_patterns import PatternGenerationMixin
from .program_generation_utm import UTMSimulationMixin
from .program_generation_advanced import AdvancedGenerationMixin

class ComplexityMethod(Enum):
    """Program generation method selection."""
    BASIC_PATTERNS = "basic_patterns"
    COMPRESSION_BASED = "compression_based"
    UNIVERSAL_TURING = "universal_turing"
    CONTEXT_TREE = "context_tree"
    HYBRID = "hybrid"

class CompressionAlgorithm(Enum):
    """Compression algorithm selection."""
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    LZ77 = "lz77"

class ProgramGenerationMixin(PatternGenerationMixin, UTMSimulationMixin, AdvancedGenerationMixin):
    """
    🧮 Universal Program Generation Mixin for Solomonoff Induction
    
    ELI5: This is like having a super-smart program factory! It can create every 
    possible explanation (program) for any sequence you give it, from simple patterns 
    to complex mathematical relationships.
    
    Technical Overview:
    ==================
    Implements universal program enumeration as required by Solomonoff's theory:
    
    M(x) = Σ_{p: U(p) starts with x} 2^(-|p|)
    
    The core challenge is enumerating all programs p such that running program p
    on a Universal Turing Machine produces output that starts with observed sequence x.
    Since this is computationally intractable in full generality, we implement
    multiple approximation strategies through specialized mixins.
    
    Modular Architecture:
    ====================
    This class inherits from specialized mixins:
    
    1. **PatternGenerationMixin**: Fast pattern detection
       - Constant sequences, periodic patterns
       - Arithmetic progressions, Fibonacci sequences
       - Polynomial sequences, prime numbers
    
    2. **UTMSimulationMixin**: Universal Turing Machine approximation
       - Brainfuck interpreter (minimal Turing-complete language)
       - Lambda calculus evaluator (functional programming)
       - Binary program executor (machine code simulation)
    
    3. **AdvancedGenerationMixin**: Sophisticated approximations
       - Compression-based complexity estimation
       - Context tree weighting (optimal for tree sources)
       - Hybrid ensemble methods combining all approaches
    
    Configuration Requirements:
    ==========================
    The implementing class must provide:
    - self.config: SolomonoffConfig object with method settings
    - self.alphabet_size: Size of input alphabet
    - self.max_program_length: Maximum program length for enumeration
    
    Performance Characteristics:
    ===========================
    • Time Complexity: O(n × 2^L) for UTM, O(n × log n) for approximations
    • Space Complexity: O(2^L) for program storage, with efficient caching
    • Accuracy: Approaches theoretical optimum as computational budget increases
    • Scalability: Handles sequences up to 10^6 symbols with method selection
    """

    def _generate_programs_configurable(self, sequence: List[int]) -> List[Dict]:
        """
        🎛️ Generate Programs Using Configured Complexity Method
        
        ELI5: This is your main control center! It looks at your settings and 
        chooses the right way to find patterns in your data - fast and simple, 
        or slow but super thorough.
        
        Method Selection Strategy:
        - BASIC_PATTERNS: Fast heuristics for common mathematical sequences
        - COMPRESSION_BASED: Use compression algorithms as complexity proxy
        - UNIVERSAL_TURING: Enumerate and execute programs on UTM simulation
        - CONTEXT_TREE: Build probabilistic context models for prediction
        - HYBRID: Weighted ensemble combining multiple approaches
        
        Args:
            sequence (List[int]): Observed sequence to generate programs for
                
        Returns:
            List[Dict]: List of program dictionaries with complexity weighting
        """
        
        if self.config.complexity_method == ComplexityMethod.BASIC_PATTERNS:
            return self._generate_programs_basic(sequence)
        elif self.config.complexity_method == ComplexityMethod.COMPRESSION_BASED:
            return self._generate_programs_compression(sequence)
        elif self.config.complexity_method == ComplexityMethod.UNIVERSAL_TURING:
            return self._generate_programs_utm(sequence)
        elif self.config.complexity_method == ComplexityMethod.CONTEXT_TREE:
            return self._generate_programs_context_tree(sequence)
        elif self.config.complexity_method == ComplexityMethod.HYBRID:
            return self._generate_programs_hybrid(sequence)
        else:
            # Fallback to basic patterns
            return self._generate_programs_fallback(sequence)

    def _generate_programs_basic(self, sequence: List[int]) -> List[Dict]:
        """
        🎯 Basic Pattern-Based Program Generation
        
        ELI5: This looks for simple, common patterns that humans often create,
        like counting, repeating numbers, or basic math sequences.
        
        Combines results from all pattern detection methods.
        """
        programs = []
        
        # Collect programs from all pattern methods
        programs.extend(self._generate_constant_programs(sequence))
        programs.extend(self._generate_periodic_programs(sequence))
        programs.extend(self._generate_arithmetic_programs(sequence))
        programs.extend(self._generate_fibonacci_programs(sequence))
        programs.extend(self._generate_polynomial_programs(sequence))
        programs.extend(self._generate_power_sequence_programs(sequence))
        programs.extend(self._generate_prime_programs(sequence))
        
        # Sort by complexity (simpler explanations first)
        programs.sort(key=lambda p: p['complexity'])
        
        # Limit number of programs to prevent explosion
        max_basic_programs = getattr(self.config, 'max_basic_programs', 50)
        return programs[:max_basic_programs]

    def _generate_programs_fallback(self, sequence: List[int]) -> List[Dict]:
        """
        🆘 Fallback Program Generation
        
        ELI5: When everything else fails, this creates a simple program that
        just memorizes the sequence and repeats the last number.
        
        Always succeeds and provides baseline complexity estimate.
        """
        programs = []
        
        if not sequence:
            return programs
        
        # Simple memorization program
        complexity = len(sequence) * np.log2(self.alphabet_size)  # Bits to encode sequence
        
        programs.append({
            'type': 'memorization',
            'complexity': complexity,
            'fits_sequence': True,
            'next_prediction': sequence[-1] if sequence else 0,
            'weight': 2**(-complexity),
            'method': 'fallback',
            'description': f'Memorization of {len(sequence)} symbols',
            'accuracy': 0.5  # Low accuracy, just memorizes
        })
        
        # Random baseline
        programs.append({
            'type': 'random',
            'complexity': float('inf'),  # Worst possible complexity
            'fits_sequence': False,
            'next_prediction': np.random.randint(0, self.alphabet_size),
            'weight': 0.0,  # No weight for random
            'method': 'fallback',
            'description': 'Random prediction baseline',
            'accuracy': 1.0 / self.alphabet_size
        })
        
        return programs

    def _generate_programs_utm(self, sequence: List[int]) -> List[Dict]:
        """
        🤖 Universal Turing Machine Program Generation
        
        Delegates to UTM simulation mixin methods.
        """
        programs = []
        
        # Collect from all UTM simulation methods
        programs.extend(self._utm_brainfuck_simulation(sequence))
        programs.extend(self._utm_lambda_simulation(sequence))
        programs.extend(self._utm_binary_simulation(sequence))
        
        # Can also use ensemble UTM method
        programs.extend(self._generate_utm_ensemble(sequence))
        
        return programs

    def validate_program_consistency(self, programs: List[Dict]) -> List[Dict]:
        """
        🔍 Validate Program Consistency
        
        Checks that all generated programs meet basic consistency requirements.
        """
        validated_programs = []
        
        for program in programs:
            # Basic validation checks
            if not isinstance(program, dict):
                continue
                
            required_fields = ['type', 'complexity', 'fits_sequence', 'next_prediction']
            if not all(field in program for field in required_fields):
                continue
                
            # Complexity should be positive
            if program['complexity'] <= 0:
                continue
                
            # Next prediction should be valid
            if not (0 <= program['next_prediction'] < self.alphabet_size):
                program['next_prediction'] = program['next_prediction'] % self.alphabet_size
                
            # Add weight if missing
            if 'weight' not in program:
                program['weight'] = 2**(-program['complexity'])
                
            # Add default accuracy if missing
            if 'accuracy' not in program:
                program['accuracy'] = 0.8
                
            # Add method if missing
            if 'method' not in program:
                program['method'] = 'unknown'
                
            # Add description if missing
            if 'description' not in program:
                program['description'] = f"{program['type']} program"
                
            validated_programs.append(program)
        
        return validated_programs

    def get_program_statistics(self, programs: List[Dict]) -> Dict[str, any]:
        """
        📊 Get Program Statistics
        
        Computes summary statistics for generated programs.
        """
        if not programs:
            return {
                'total_programs': 0,
                'method_distribution': {},
                'complexity_range': (0, 0),
                'average_complexity': 0,
                'total_weight': 0
            }
        
        # Method distribution
        method_counts = {}
        for program in programs:
            method = program.get('method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
        
        # Complexity statistics
        complexities = [p['complexity'] for p in programs if np.isfinite(p['complexity'])]
        
        # Weight statistics
        total_weight = sum(p.get('weight', 0) for p in programs)
        
        return {
            'total_programs': len(programs),
            'method_distribution': method_counts,
            'complexity_range': (min(complexities), max(complexities)) if complexities else (0, 0),
            'average_complexity': np.mean(complexities) if complexities else 0,
            'median_complexity': np.median(complexities) if complexities else 0,
            'total_weight': total_weight,
            'unique_predictions': len(set(p['next_prediction'] for p in programs)),
            'fitting_programs': sum(1 for p in programs if p.get('fits_sequence', False))
        }

    def optimize_program_selection(self, programs: List[Dict], max_programs: int = 20) -> List[Dict]:
        """
        ⚡ Optimize Program Selection
        
        Selects best subset of programs for efficiency while maintaining coverage.
        """
        if len(programs) <= max_programs:
            return programs
        
        # Sort by complexity (better programs first)
        sorted_programs = sorted(programs, key=lambda p: p['complexity'])
        
        # Take top programs by complexity
        selected = sorted_programs[:max_programs//2]
        
        # Add diverse programs (different methods/types)
        seen_types = set(p['type'] for p in selected)
        remaining = sorted_programs[max_programs//2:]
        
        for program in remaining:
            if len(selected) >= max_programs:
                break
            if program['type'] not in seen_types:
                selected.append(program)
                seen_types.add(program['type'])
        
        # Fill remaining slots with best complexity
        while len(selected) < max_programs and len(selected) < len(programs):
            for program in remaining:
                if program not in selected:
                    selected.append(program)
                    break
        
        return selected[:max_programs]