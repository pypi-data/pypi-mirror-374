"""
⚙️ Program Enumeration for Universal Learning
============================================

This module implements systematic program enumeration for Solomonoff Induction,
including Universal Turing Machine simulation and program generation strategies.

Based on:
- Levin (1973) "Universal Sequential Search Problems"
- Schmidhuber (2002) "The Speed Prior: A New Simplicity Measure"

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
import time
from typing import List, Dict, Any, Optional, Iterator, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import itertools
import warnings


class ProgramLanguage(Enum):
    """Enumeration of program languages supported for enumeration."""
    PYTHON_SUBSET = "python_subset"
    BRAINFUCK = "brainfuck"
    LAMBDA_CALCULUS = "lambda_calculus"
    BINARY_STRINGS = "binary_strings"
    CUSTOM = "custom"


@dataclass
class EnumeratedProgram:
    """
    📄 Represents an enumerated program with execution results.
    
    Attributes
    ----------
    code : str
        Program source code
    length : int
        Program length (complexity measure)
    output : List[Any]
        Program output sequence
    execution_time : float
        Time taken to execute program
    success : bool
        Whether program executed successfully
    weight : float
        Universal prior weight (2^-length)
    """
    
    code: str
    length: int
    output: List[Any] = field(default_factory=list)
    execution_time: float = 0.0
    success: bool = False
    weight: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.weight == 0.0:
            self.weight = 2**(-self.length)


class UTMSimulator:
    """
    🖥️ Universal Turing Machine Simulator
    
    Simulates program execution for various computational models,
    with time and space bounds for practical enumeration.
    
    Parameters
    ----------
    language : ProgramLanguage, default=PYTHON_SUBSET
        Programming language to simulate
    max_steps : int, default=10000
        Maximum execution steps per program
    max_memory : int, default=1000000
        Maximum memory usage per program
    timeout_seconds : float, default=1.0
        Maximum execution time per program
    """
    
    def __init__(self,
                 language: ProgramLanguage = ProgramLanguage.PYTHON_SUBSET,
                 max_steps: int = 10000,
                 max_memory: int = 1000000,
                 timeout_seconds: float = 1.0):
        
        self.language = language
        self.max_steps = max_steps
        self.max_memory = max_memory
        self.timeout_seconds = timeout_seconds
        
        # Execution statistics
        self.stats = {
            'programs_executed': 0,
            'successful_executions': 0,
            'timeouts': 0,
            'errors': 0,
            'total_execution_time': 0.0
        }
        
        # Safe execution environment setup
        self._setup_execution_environment()
    
    def execute_program(self, program_code: str, 
                       input_data: Optional[List[Any]] = None) -> EnumeratedProgram:
        """
        Execute a program and return results.
        
        Parameters
        ----------
        program_code : str
            Source code of the program
        input_data : List[Any], optional
            Input data for the program
            
        Returns
        -------
        EnumeratedProgram
            Program with execution results
        """
        self.stats['programs_executed'] += 1
        
        program = EnumeratedProgram(
            code=program_code,
            length=len(program_code)
        )
        
        start_time = time.time()
        
        try:
            if self.language == ProgramLanguage.PYTHON_SUBSET:
                output = self._execute_python_subset(program_code, input_data)
            elif self.language == ProgramLanguage.BRAINFUCK:
                output = self._execute_brainfuck(program_code, input_data)
            elif self.language == ProgramLanguage.BINARY_STRINGS:
                output = self._execute_binary_strings(program_code, input_data)
            else:
                raise ValueError(f"Unsupported language: {self.language}")
            
            program.output = output
            program.success = True
            self.stats['successful_executions'] += 1
            
        except TimeoutError:
            program.success = False
            program.metadata['error'] = 'timeout'
            self.stats['timeouts'] += 1
            
        except Exception as e:
            program.success = False
            program.metadata['error'] = str(e)
            self.stats['errors'] += 1
        
        program.execution_time = time.time() - start_time
        self.stats['total_execution_time'] += program.execution_time
        
        return program
    
    def _execute_python_subset(self, code: str, input_data: Optional[List[Any]] = None) -> List[Any]:
        """Execute Python subset with safety restrictions."""
        # This is a simplified, safe Python subset executor
        # Real implementation would use more sophisticated sandboxing
        
        output = []
        
        # Safe built-in functions only
        safe_builtins = {
            'range': range,
            'len': len,
            'print': lambda x: output.append(x),
            'int': int,
            'float': float,
            'str': str,
            'list': list,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum
        }
        
        # Restricted globals
        safe_globals = {
            '__builtins__': safe_builtins,
            'output': output,
            'input_data': input_data or []
        }
        
        # Execute with timeout
        try:
            # Simple timeout mechanism (not foolproof)
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Execution timeout")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(self.timeout_seconds))
            
            exec(code, safe_globals)
            
            signal.alarm(0)  # Cancel timeout
            
        except Exception as e:
            signal.alarm(0)  # Cancel timeout
            raise e
        
        return output
    
    def _execute_brainfuck(self, code: str, input_data: Optional[List[Any]] = None) -> List[Any]:
        """Execute Brainfuck program."""
        # Simplified Brainfuck interpreter
        memory = [0] * 30000
        pointer = 0
        code_pointer = 0
        output = []
        input_pointer = 0
        
        input_list = input_data or []
        steps = 0
        
        while code_pointer < len(code) and steps < self.max_steps:
            cmd = code[code_pointer]
            
            if cmd == '>':
                pointer = (pointer + 1) % len(memory)
            elif cmd == '<':
                pointer = (pointer - 1) % len(memory)
            elif cmd == '+':
                memory[pointer] = (memory[pointer] + 1) % 256
            elif cmd == '-':
                memory[pointer] = (memory[pointer] - 1) % 256
            elif cmd == '.':
                output.append(memory[pointer])
            elif cmd == ',':
                if input_pointer < len(input_list):
                    memory[pointer] = input_list[input_pointer] % 256
                    input_pointer += 1
                else:
                    memory[pointer] = 0
            elif cmd == '[':
                if memory[pointer] == 0:
                    # Jump forward to matching ]
                    bracket_count = 1
                    while bracket_count > 0 and code_pointer < len(code) - 1:
                        code_pointer += 1
                        if code[code_pointer] == '[':
                            bracket_count += 1
                        elif code[code_pointer] == ']':
                            bracket_count -= 1
            elif cmd == ']':
                if memory[pointer] != 0:
                    # Jump back to matching [
                    bracket_count = 1
                    while bracket_count > 0 and code_pointer > 0:
                        code_pointer -= 1
                        if code[code_pointer] == ']':
                            bracket_count += 1
                        elif code[code_pointer] == '[':
                            bracket_count -= 1
            
            code_pointer += 1
            steps += 1
            
            if steps >= self.max_steps:
                raise TimeoutError("Maximum steps exceeded")
        
        return output
    
    def _execute_binary_strings(self, code: str, input_data: Optional[List[Any]] = None) -> List[Any]:
        """Execute binary string as simple program."""
        # Interpret binary string as sequence of operations
        output = []
        
        try:
            # Split into chunks and interpret as operations
            chunk_size = 8
            for i in range(0, len(code), chunk_size):
                chunk = code[i:i+chunk_size]
                if len(chunk) == chunk_size:
                    # Convert binary to integer
                    value = int(chunk, 2)
                    output.append(value)
        except ValueError:
            # Invalid binary string
            pass
        
        return output
    
    def _setup_execution_environment(self):
        """Setup safe execution environment."""
        # This would set up sandboxing, resource limits, etc.
        # For this implementation, we rely on basic timeout mechanisms
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        stats = self.stats.copy()
        
        if stats['programs_executed'] > 0:
            stats['success_rate'] = stats['successful_executions'] / stats['programs_executed']
            stats['average_execution_time'] = stats['total_execution_time'] / stats['programs_executed']
        else:
            stats['success_rate'] = 0.0
            stats['average_execution_time'] = 0.0
        
        stats.update({
            'language': self.language.value,
            'max_steps': self.max_steps,
            'timeout_seconds': self.timeout_seconds
        })
        
        return stats


class ProgramGenerator:
    """
    🎲 Systematic Program Generator
    
    Generates programs systematically for enumeration, starting from
    shortest programs and increasing in length.
    
    Parameters
    ----------
    language : ProgramLanguage, default=PYTHON_SUBSET
        Programming language to generate
    max_length : int, default=20
        Maximum program length to generate
    alphabet : Optional[str]
        Custom alphabet for program generation
    """
    
    def __init__(self,
                 language: ProgramLanguage = ProgramLanguage.PYTHON_SUBSET,
                 max_length: int = 20,
                 alphabet: Optional[str] = None):
        
        self.language = language
        self.max_length = max_length
        self.alphabet = alphabet or self._get_default_alphabet()
        
        # Generation statistics
        self.stats = {
            'programs_generated': 0,
            'current_length': 1,
            'total_possible_programs': 0
        }
        
        self._compute_total_programs()
    
    def generate_programs(self, max_count: Optional[int] = None) -> Iterator[str]:
        """
        Generate programs systematically by length.
        
        Parameters
        ----------
        max_count : int, optional
            Maximum number of programs to generate
            
        Yields
        ------
        str
            Generated program code
        """
        generated = 0
        
        for length in range(1, self.max_length + 1):
            self.stats['current_length'] = length
            
            for program in self._generate_programs_of_length(length):
                if max_count and generated >= max_count:
                    return
                
                yield program
                generated += 1
                self.stats['programs_generated'] += 1
    
    def _generate_programs_of_length(self, length: int) -> Iterator[str]:
        """Generate all programs of specific length."""
        if self.language == ProgramLanguage.PYTHON_SUBSET:
            yield from self._generate_python_programs(length)
        elif self.language == ProgramLanguage.BRAINFUCK:
            yield from self._generate_brainfuck_programs(length)
        elif self.language == ProgramLanguage.BINARY_STRINGS:
            yield from self._generate_binary_programs(length)
        else:
            # Generic alphabet-based generation
            for program_tuple in itertools.product(self.alphabet, repeat=length):
                yield ''.join(program_tuple)
    
    def _generate_python_programs(self, length: int) -> Iterator[str]:
        """Generate Python subset programs of specific length."""
        # This is a simplified Python program generator
        # Real implementation would use more sophisticated grammar-based generation
        
        templates = [
            "print({})",
            "for i in range({}): print(i)",
            "x={}; print(x)",
            "print({}+{})",
            "print({}*{})",
        ]
        
        # Generate programs from templates
        for template in templates:
            if len(template) <= length:
                # Fill template with simple values
                if '{}' in template:
                    count = template.count('{}')
                    for values in itertools.product(['0', '1', '2', '3', 'i'], repeat=count):
                        program = template.format(*values)
                        if len(program) == length:
                            yield program
    
    def _generate_brainfuck_programs(self, length: int) -> Iterator[str]:
        """Generate Brainfuck programs of specific length."""
        bf_alphabet = '+-<>[].,'
        
        for program_tuple in itertools.product(bf_alphabet, repeat=length):
            program = ''.join(program_tuple)
            # Basic validity check for brackets
            if self._is_valid_brainfuck(program):
                yield program
    
    def _generate_binary_programs(self, length: int) -> Iterator[str]:
        """Generate binary string programs of specific length."""
        for program_tuple in itertools.product('01', repeat=length):
            yield ''.join(program_tuple)
    
    def _is_valid_brainfuck(self, program: str) -> bool:
        """Check if Brainfuck program has balanced brackets."""
        bracket_count = 0
        for char in program:
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count < 0:
                    return False
        return bracket_count == 0
    
    def _get_default_alphabet(self) -> str:
        """Get default alphabet for program generation."""
        if self.language == ProgramLanguage.PYTHON_SUBSET:
            return 'abcdefghijklmnopqrstuvwxyz0123456789()[]{}:=+*-<> .,'
        elif self.language == ProgramLanguage.BRAINFUCK:
            return '+-<>[].,'
        elif self.language == ProgramLanguage.BINARY_STRINGS:
            return '01'
        else:
            return 'abcdefghijklmnopqrstuvwxyz0123456789'
    
    def _compute_total_programs(self):
        """Compute total number of programs possible."""
        total = 0
        alphabet_size = len(self.alphabet)
        
        for length in range(1, self.max_length + 1):
            total += alphabet_size ** length
        
        self.stats['total_possible_programs'] = total
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics."""
        stats = self.stats.copy()
        stats.update({
            'language': self.language.value,
            'alphabet_size': len(self.alphabet),
            'max_length': self.max_length
        })
        return stats


class ProgramEnumerator:
    """
    🔍 Complete Program Enumerator
    
    Combines program generation and execution for systematic enumeration
    of all programs that produce specific outputs.
    
    Parameters
    ----------
    utm_simulator : UTMSimulator
        Universal Turing Machine simulator
    program_generator : ProgramGenerator  
        Program generator
    target_sequence : List[Any], optional
        Target sequence to find programs for
    """
    
    def __init__(self,
                 utm_simulator: UTMSimulator,
                 program_generator: ProgramGenerator,
                 target_sequence: Optional[List[Any]] = None):
        
        self.utm_simulator = utm_simulator
        self.program_generator = program_generator
        self.target_sequence = target_sequence
        
        # Found programs
        self.matching_programs: List[EnumeratedProgram] = []
        
        # Enumeration statistics
        self.stats = {
            'programs_tested': 0,
            'programs_found': 0,
            'enumeration_time': 0.0,
            'current_search_length': 1
        }
    
    def enumerate_programs(self, 
                          target_sequence: Optional[List[Any]] = None,
                          max_programs: int = 1000,
                          max_time_seconds: float = 60.0) -> List[EnumeratedProgram]:
        """
        Enumerate programs that produce target sequence.
        
        Parameters
        ----------
        target_sequence : List[Any], optional
            Target sequence to match
        max_programs : int, default=1000
            Maximum programs to test
        max_time_seconds : float, default=60.0
            Maximum enumeration time
            
        Returns
        -------
        List[EnumeratedProgram]
            Programs that produce target sequence
        """
        if target_sequence is None:
            target_sequence = self.target_sequence
        
        if target_sequence is None:
            warnings.warn("No target sequence specified")
            return []
        
        start_time = time.time()
        matching_programs = []
        
        # Systematic enumeration by program length (Levin Search)
        for program_code in self.program_generator.generate_programs(max_programs):
            if time.time() - start_time > max_time_seconds:
                break
            
            self.stats['programs_tested'] += 1
            
            # Execute program
            program = self.utm_simulator.execute_program(program_code)
            
            # Check if output matches target sequence
            if self._matches_target(program.output, target_sequence):
                matching_programs.append(program)
                self.stats['programs_found'] += 1
                
                # For Solomonoff induction, shorter programs are more important
                # so we can often stop after finding a few good matches
                if len(matching_programs) >= 10:  # Limit matches per search
                    break
        
        self.stats['enumeration_time'] = time.time() - start_time
        self.matching_programs.extend(matching_programs)
        
        # Sort by program length (shorter = higher weight)
        matching_programs.sort(key=lambda p: p.length)
        
        return matching_programs
    
    def find_shortest_program(self, target_sequence: List[Any]) -> Optional[EnumeratedProgram]:
        """
        Find shortest program generating target sequence.
        
        Parameters
        ----------
        target_sequence : List[Any]
            Target sequence to match
            
        Returns
        -------
        EnumeratedProgram or None
            Shortest program found, or None
        """
        programs = self.enumerate_programs(target_sequence, max_programs=10000)
        return programs[0] if programs else None
    
    def _matches_target(self, output: List[Any], target: List[Any]) -> bool:
        """Check if program output matches target sequence."""
        if not output or not target:
            return len(output) == len(target)
        
        # Exact match
        if output == target:
            return True
        
        # Prefix match (program generates target as prefix)
        if len(output) >= len(target):
            return output[:len(target)] == target
        
        # Suffix match (target is continuation of output)
        if len(target) >= len(output):
            return target[:len(output)] == output
        
        return False
    
    def get_universal_distribution(self, sequence: List[Any]) -> float:
        """
        Compute universal distribution approximation for sequence.
        
        Parameters
        ----------
        sequence : List[Any]
            Sequence to compute distribution for
            
        Returns
        -------
        float
            Approximate universal probability
        """
        matching_programs = self.enumerate_programs(sequence)
        
        # Sum of program weights (universal prior)
        total_probability = sum(program.weight for program in matching_programs)
        
        return total_probability
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get enumeration statistics."""
        stats = self.stats.copy()
        
        # Combine with component statistics
        stats.update({
            'utm_stats': self.utm_simulator.get_statistics(),
            'generator_stats': self.program_generator.get_statistics(),
            'total_programs_found': len(self.matching_programs)
        })
        
        return stats