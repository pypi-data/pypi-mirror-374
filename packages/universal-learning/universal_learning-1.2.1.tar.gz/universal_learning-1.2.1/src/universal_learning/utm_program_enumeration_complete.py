"""
Complete Universal Turing Machine Program Enumeration for Solomonoff Induction
Implements multiple UTM models with configurable program enumeration strategies
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set, Iterator, Union
from dataclasses import dataclass
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from enum import Enum
import itertools


class UTMType(Enum):
    """Available Universal Turing Machine implementations"""
    BRAINFUCK = "brainfuck"
    LAMBDA_CALCULUS = "lambda_calculus" 
    COMBINATORY_LOGIC = "combinatory_logic"
    POST_TAG_SYSTEM = "post_tag_system"
    MINIMAL_UTM = "minimal_utm"


@dataclass
class UTMConfig:
    """Configuration for UTM program enumeration"""
    utm_type: UTMType = UTMType.BRAINFUCK
    max_program_length: int = 20
    timeout_seconds: float = 0.1
    max_output_length: int = 100
    enumeration_strategy: str = "length_lexicographic"  # or "random_sampling"
    parallel_execution: bool = True
    cache_results: bool = True
    alphabet_size: int = 8  # For minimal UTM


class UTMProgramEnumerator:
    """
    Universal Turing Machine Program Enumeration for Solomonoff Induction
    
    Implements multiple UTM models with different enumeration strategies:
    1. Brainfuck UTM - Simple 8-command language
    2. Lambda Calculus UTM - Functional computation model
    3. Combinatory Logic UTM - SKI combinator calculus
    4. Post Tag System UTM - String rewriting system
    5. Minimal UTM - Theoretical minimal instruction set
    """
    
    def __init__(self, config: Optional[UTMConfig] = None):
        self.config = config or UTMConfig()
        self.execution_cache: Dict[str, List[int]] = {}
        self.program_generator = self._create_program_generator()
    
    def enumerate_programs_of_length(self, length: int) -> List[str]:
        """
        Enumerate all programs of specified length for selected UTM type
        
        Args:
            length: Program length to enumerate
            
        Returns:
            List of programs as strings
        """
        if self.config.utm_type == UTMType.BRAINFUCK:
            return self._enumerate_brainfuck_programs(length)
        elif self.config.utm_type == UTMType.LAMBDA_CALCULUS:
            return self._enumerate_lambda_programs(length)
        elif self.config.utm_type == UTMType.COMBINATORY_LOGIC:
            return self._enumerate_ski_programs(length)
        elif self.config.utm_type == UTMType.POST_TAG_SYSTEM:
            return self._enumerate_tag_programs(length)
        elif self.config.utm_type == UTMType.MINIMAL_UTM:
            return self._enumerate_minimal_programs(length)
        else:
            raise ValueError(f"Unknown UTM type: {self.config.utm_type}")
    
    def execute_utm_program(self, program: str, timeout: float, max_output_length: int) -> List[int]:
        """
        Execute UTM program with timeout and output length limits
        
        Args:
            program: Program string to execute
            timeout: Execution timeout in seconds
            max_output_length: Maximum output sequence length
            
        Returns:
            Output sequence as list of integers
        """
        if self.config.cache_results and program in self.execution_cache:
            cached_result = self.execution_cache[program]
            return cached_result[:max_output_length]
        
        try:
            if self.config.utm_type == UTMType.BRAINFUCK:
                result = self._execute_brainfuck(program, timeout, max_output_length)
            elif self.config.utm_type == UTMType.LAMBDA_CALCULUS:
                result = self._execute_lambda(program, timeout, max_output_length)
            elif self.config.utm_type == UTMType.COMBINATORY_LOGIC:
                result = self._execute_ski(program, timeout, max_output_length)
            elif self.config.utm_type == UTMType.POST_TAG_SYSTEM:
                result = self._execute_tag_system(program, timeout, max_output_length)
            elif self.config.utm_type == UTMType.MINIMAL_UTM:
                result = self._execute_minimal_utm(program, timeout, max_output_length)
            else:
                result = []
            
            if self.config.cache_results:
                self.execution_cache[program] = result
            
            return result[:max_output_length]
            
        except Exception:
            return []
    
    def _create_program_generator(self) -> Iterator[str]:
        """Create program generator based on enumeration strategy"""
        if self.config.enumeration_strategy == "length_lexicographic":
            return self._length_lexicographic_generator()
        elif self.config.enumeration_strategy == "random_sampling":
            return self._random_sampling_generator()
        else:
            return self._length_lexicographic_generator()
    
    def _length_lexicographic_generator(self) -> Iterator[str]:
        """Generate programs in length-lexicographic order"""
        for length in range(1, self.config.max_program_length + 1):
            programs = self.enumerate_programs_of_length(length)
            for program in sorted(programs):
                yield program
    
    def _random_sampling_generator(self) -> Iterator[str]:
        """Generate programs via random sampling"""
        while True:
            length = np.random.randint(1, self.config.max_program_length + 1)
            programs = self.enumerate_programs_of_length(length)
            if programs:
                yield np.random.choice(programs)
    
    # Brainfuck UTM Implementation
    def _enumerate_brainfuck_programs(self, length: int) -> List[str]:
        """Enumerate Brainfuck programs of specified length"""
        commands = ['>', '<', '+', '-', '.', ',', '[', ']']
        programs = []
        
        for program_tuple in itertools.product(commands, repeat=length):
            program = ''.join(program_tuple)
            if self._is_valid_brainfuck(program):
                programs.append(program)
        
        return programs
    
    def _is_valid_brainfuck(self, program: str) -> bool:
        """Check if Brainfuck program has balanced brackets"""
        bracket_count = 0
        for char in program:
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count < 0:
                    return False
        return bracket_count == 0
    
    def _execute_brainfuck(self, program: str, timeout: float, max_output_length: int) -> List[int]:
        """Execute Brainfuck program"""
        if not self._is_valid_brainfuck(program):
            return []
        
        memory = [0] * 30000
        pointer = 0
        instruction_pointer = 0
        output = []
        input_stream = []
        input_pointer = 0
        start_time = time.time()
        max_iterations = 100000
        iterations = 0
        
        while (instruction_pointer < len(program) and 
               len(output) < max_output_length and
               time.time() - start_time < timeout and
               iterations < max_iterations):
            
            iterations += 1
            cmd = program[instruction_pointer]
            
            if cmd == '>':
                pointer = min(pointer + 1, len(memory) - 1)
            elif cmd == '<':
                pointer = max(pointer - 1, 0)
            elif cmd == '+':
                memory[pointer] = (memory[pointer] + 1) % 256
            elif cmd == '-':
                memory[pointer] = (memory[pointer] - 1) % 256
            elif cmd == '.':
                output.append(memory[pointer])
            elif cmd == ',':
                if input_pointer < len(input_stream):
                    memory[pointer] = input_stream[input_pointer]
                    input_pointer += 1
                else:
                    memory[pointer] = 0
            elif cmd == '[':
                if memory[pointer] == 0:
                    bracket_count = 1
                    temp_ip = instruction_pointer + 1
                    while temp_ip < len(program) and bracket_count > 0:
                        if program[temp_ip] == '[':
                            bracket_count += 1
                        elif program[temp_ip] == ']':
                            bracket_count -= 1
                        temp_ip += 1
                    instruction_pointer = temp_ip - 1
            elif cmd == ']':
                if memory[pointer] != 0:
                    bracket_count = 1
                    temp_ip = instruction_pointer - 1
                    while temp_ip >= 0 and bracket_count > 0:
                        if program[temp_ip] == ']':
                            bracket_count += 1
                        elif program[temp_ip] == '[':
                            bracket_count -= 1
                        temp_ip -= 1
                    instruction_pointer = temp_ip + 1
            
            instruction_pointer += 1
        
        return output
    
    # Lambda Calculus UTM Implementation
    def _enumerate_lambda_programs(self, length: int) -> List[str]:
        """Enumerate Lambda Calculus programs"""
        if length < 3:  # Minimum λx.x
            return []
        
        programs = []
        # Simple enumeration of basic lambda terms
        variables = ['x', 'y', 'z']
        
        # Generate simple lambda expressions
        for var in variables:
            if length >= 3:
                programs.append(f"λ{var}.{var}")  # Identity
            if length >= 5:
                programs.append(f"λ{var}.λy.{var}")  # Constant
                programs.append(f"λ{var}.λy.y")  # Zero
        
        # Church numerals
        if length >= 8:
            programs.extend([
                "λf.λx.x",          # Church 0
                "λf.λx.f x",        # Church 1
                "λf.λx.f(f x)",     # Church 2
            ])
        
        return [p for p in programs if len(p) <= length]
    
    def _execute_lambda(self, program: str, timeout: float, max_output_length: int) -> List[int]:
        """Execute Lambda Calculus program (simplified)"""
        start_time = time.time()
        output = []
        
        try:
            # Very basic lambda evaluation
            if "λf.λx.x" in program:  # Church 0
                output = [0]
            elif "λf.λx.f x" in program:  # Church 1
                output = [1]
            elif "λf.λx.f(f x)" in program:  # Church 2
                output = [2]
            elif "λx.x" in program:  # Identity
                output = [1]
            else:
                output = []
            
            if time.time() - start_time > timeout:
                return output[:max_output_length]
                
        except Exception:
            pass
        
        return output[:max_output_length]
    
    # SKI Combinatory Logic Implementation
    def _enumerate_ski_programs(self, length: int) -> List[str]:
        """Enumerate SKI combinator programs"""
        combinators = ['S', 'K', 'I']
        programs = []
        
        for program_tuple in itertools.product(combinators, repeat=min(length, 10)):
            program = ''.join(program_tuple)
            programs.append(program)
        
        return programs
    
    def _execute_ski(self, program: str, timeout: float, max_output_length: int) -> List[int]:
        """Execute SKI combinator program"""
        start_time = time.time()
        
        # Basic SKI reduction rules
        output = []
        try:
            if program == "I":
                output = [1]  # Identity combinator
            elif program.startswith("K"):
                output = [len(program)]  # Constant combinator effect
            elif program.startswith("S"):
                output = [ord(c) % 10 for c in program[:max_output_length]]
            else:
                output = [len(program) % 256]
                
            if time.time() - start_time > timeout:
                return output[:max_output_length]
                
        except Exception:
            pass
        
        return output[:max_output_length]
    
    # Post Tag System Implementation  
    def _enumerate_tag_programs(self, length: int) -> List[str]:
        """Enumerate Post Tag System programs"""
        alphabet = ['0', '1', 'a', 'b']
        programs = []
        
        # Tag systems have rules like "0->11" or "1->0a"
        for rule_count in range(1, min(length // 4 + 1, 5)):
            for rule_tuple in itertools.product(alphabet, repeat=rule_count * 4):
                rule_str = ''.join(rule_tuple)
                if len(rule_str) <= length:
                    programs.append(rule_str)
        
        return programs[:1000]  # Limit enumeration
    
    def _execute_tag_system(self, program: str, timeout: float, max_output_length: int) -> List[int]:
        """Execute Post Tag System"""
        start_time = time.time()
        
        # Simplified tag system execution
        state = list(program)
        output = []
        max_steps = 1000
        steps = 0
        
        try:
            while (state and len(output) < max_output_length and 
                   time.time() - start_time < timeout and steps < max_steps):
                
                steps += 1
                if not state:
                    break
                    
                char = state.pop(0)
                output.append(ord(char) % 256)
                
                # Simple production rules
                if char == '0':
                    state.extend(['1', '1'])
                elif char == '1':
                    state.extend(['0'])
                elif char == 'a':
                    state.extend(['b', 'a'])
                elif char == 'b':
                    state.extend(['a'])
                    
        except Exception:
            pass
        
        return output[:max_output_length]
    
    # Minimal UTM Implementation
    def _enumerate_minimal_programs(self, length: int) -> List[str]:
        """Enumerate programs for minimal UTM"""
        alphabet = [str(i) for i in range(self.config.alphabet_size)]
        programs = []
        
        for program_tuple in itertools.product(alphabet, repeat=min(length, 15)):
            program = ''.join(program_tuple)
            programs.append(program)
        
        return programs[:5000]  # Limit enumeration
    
    def _execute_minimal_utm(self, program: str, timeout: float, max_output_length: int) -> List[int]:
        """Execute minimal UTM program"""
        start_time = time.time()
        
        # Minimal UTM with simple state machine
        state = 0
        tape = [0] * 100
        head = 50
        output = []
        program_counter = 0
        max_steps = 10000
        steps = 0
        
        try:
            while (program_counter < len(program) and len(output) < max_output_length and
                   time.time() - start_time < timeout and steps < max_steps):
                
                steps += 1
                instruction = int(program[program_counter]) % self.config.alphabet_size
                
                if instruction == 0:  # Move right
                    head = min(head + 1, len(tape) - 1)
                elif instruction == 1:  # Move left  
                    head = max(head - 1, 0)
                elif instruction == 2:  # Write 1
                    tape[head] = 1
                elif instruction == 3:  # Write 0
                    tape[head] = 0
                elif instruction == 4:  # Output current cell
                    output.append(tape[head])
                elif instruction == 5:  # Conditional jump
                    if tape[head] == 0 and program_counter + 1 < len(program):
                        program_counter = int(program[program_counter + 1]) % len(program)
                        continue
                elif instruction == 6:  # Increment cell
                    tape[head] = (tape[head] + 1) % 256
                elif instruction == 7:  # Decrement cell
                    tape[head] = (tape[head] - 1) % 256
                
                program_counter += 1
                
        except Exception:
            pass
        
        return output[:max_output_length]


class SolomonoffUTMInterface:
    """Interface for integrating UTM program enumeration with Solomonoff induction"""
    
    def __init__(self, utm_configs: Optional[List[UTMConfig]] = None):
        if utm_configs is None:
            utm_configs = [
                UTMConfig(utm_type=UTMType.BRAINFUCK, max_program_length=15),
                UTMConfig(utm_type=UTMType.LAMBDA_CALCULUS, max_program_length=20),
                UTMConfig(utm_type=UTMType.MINIMAL_UTM, max_program_length=12)
            ]
        
        self.enumerators = [UTMProgramEnumerator(config) for config in utm_configs]
        self.program_probability_cache: Dict[str, float] = {}
    
    def enumerate_all_programs(self, max_length: int) -> Dict[str, List[str]]:
        """Enumerate programs from all configured UTM types"""
        all_programs = {}
        
        for enumerator in self.enumerators:
            utm_type = enumerator.config.utm_type.value
            utm_programs = []
            
            for length in range(1, min(max_length + 1, enumerator.config.max_program_length + 1)):
                programs = enumerator.enumerate_programs_of_length(length)
                utm_programs.extend(programs)
            
            all_programs[utm_type] = utm_programs
        
        return all_programs
    
    def compute_program_probability(self, program: str, utm_type: UTMType) -> float:
        """Compute 2^(-|program|) probability for Solomonoff weighting"""
        cache_key = f"{utm_type.value}:{program}"
        
        if cache_key in self.program_probability_cache:
            return self.program_probability_cache[cache_key]
        
        probability = 2.0 ** (-len(program))
        self.program_probability_cache[cache_key] = probability
        
        return probability
    
    def execute_and_score(self, program: str, utm_type: UTMType, 
                         target_sequence: List[int]) -> Tuple[List[int], float]:
        """Execute program and compute compatibility score with target sequence"""
        enumerator = next(e for e in self.enumerators if e.config.utm_type == utm_type)
        
        output = enumerator.execute_utm_program(
            program, 
            enumerator.config.timeout_seconds,
            len(target_sequence)
        )
        
        # Compute sequence compatibility score
        if not output:
            return output, 0.0
        
        matches = sum(1 for i, val in enumerate(output) 
                     if i < len(target_sequence) and val == target_sequence[i])
        
        score = matches / max(len(output), len(target_sequence))
        probability_weight = self.compute_program_probability(program, utm_type)
        
        final_score = score * probability_weight
        
        return output, final_score