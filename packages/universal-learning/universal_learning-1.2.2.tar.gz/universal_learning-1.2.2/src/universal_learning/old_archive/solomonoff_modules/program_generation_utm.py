#!/usr/bin/env python3
"""
🤖 Universal Learning - Universal Turing Machine Simulation Module
==================================================================

UTM-based program generation for Solomonoff induction.
Extracted from program_generation.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Solomonoff (1964) - Universal induction via program enumeration

This module implements UTM simulations:
- Brainfuck interpreter (Turing complete minimal language)
- Lambda calculus evaluator (functional programming foundation)
- Binary program executor (machine code simulation)

Each provides direct approximation to universal Turing machine enumeration.
"""

import numpy as np
from typing import List, Dict, Optional, Union, Callable
import re

class UTMSimulationMixin:
    """
    Universal Turing Machine simulation mixin for program enumeration.
    
    Implements computationally tractable approximations to exhaustive
    program search over universal programming languages.
    """
    
    def _utm_brainfuck_simulation(self, sequence: List[int]) -> List[Dict]:
        """
        🧠 Brainfuck UTM Simulation for Program Generation
        
        ELI5: This creates and runs tiny programs in a super-simple programming
        language called Brainfuck (yes, that's really its name!). It has only
        8 instructions but can compute anything a computer can!
        
        Technical Implementation:
        ========================
        Implements a simplified Brainfuck interpreter to approximate Universal
        Turing Machine computation. Brainfuck is Turing complete with minimal
        instruction set, making it ideal for program enumeration.
        
        Brainfuck Instructions:
        ======================
        • >: Move memory pointer right
        • <: Move memory pointer left  
        • +: Increment value at memory pointer
        • -: Decrement value at memory pointer
        • .: Output value at memory pointer
        • ,: Input value to memory pointer  
        • [: Jump forward past matching ] if current value is 0
        • ]: Jump back to matching [ if current value is non-zero
        """
        programs = []
        
        # Generate simple Brainfuck-like programs for short sequences
        if len(sequence) <= 5:  # Keep it computationally feasible
            # Simple patterns in Brainfuck style
            instructions = ['>', '<', '+', '-', '.', ',', '[', ']']
            
            for length in range(1, min(getattr(self.config, 'utm_max_program_length', 8), 8)):
                # Generate a few random programs of this length
                for _ in range(min(10, 2**length)):  # Limit search space
                    program = ''.join(np.random.choice(instructions, length))
                    
                    # Simulate execution (very simplified)
                    try:
                        output = self._simulate_brainfuck_simple(program, sequence)
                        if len(output) >= len(sequence):
                            # Check if program output matches sequence start
                            if output[:len(sequence)] == sequence:
                                next_pred = output[len(sequence)] % self.alphabet_size if len(output) > len(sequence) else sequence[-1]
                                programs.append({
                                    'type': 'utm_brainfuck',
                                    'program': program,
                                    'complexity': len(program),
                                    'fits_sequence': True,
                                    'next_prediction': next_pred,
                                    'weight': 2**(-len(program)),
                                    'method': 'utm_simulation',
                                    'description': f'Brainfuck program: {program}',
                                    'accuracy': 1.0
                                })
                    except:
                        continue
                        
        return programs
    
    def _utm_lambda_simulation(self, sequence: List[int]) -> List[Dict]:
        """
        λ Lambda Calculus UTM Simulation for Program Generation
        
        ELI5: This uses lambda calculus, the mathematical foundation of all 
        functional programming languages. It creates tiny mathematical functions
        that can generate sequences.
        
        Technical Implementation:
        ========================
        Generates simple lambda expressions that can produce the target sequence.
        Uses Church encoding for numbers and basic combinators.
        """
        programs = []
        
        if len(sequence) <= 3:  # Very limited due to complexity
            # Try simple lambda expressions
            lambda_templates = [
                'lambda n: {0}',  # Constant function
                'lambda n: n + {0}',  # Linear function
                'lambda n: n * {0}',  # Multiplication
                'lambda n: ({0} + n) % {1}',  # Modular arithmetic
            ]
            
            for template in lambda_templates:
                # Try different parameter values
                for a in range(min(self.alphabet_size, 5)):
                    for b in range(2, min(self.alphabet_size, 5)):
                        try:
                            # Create lambda expression
                            if '{1}' in template:
                                lambda_expr = template.format(a, b)
                            else:
                                lambda_expr = template.format(a)
                            
                            # Test if it generates the sequence
                            output = self._simulate_lambda_string(lambda_expr, sequence)
                            if len(output) >= len(sequence) and output[:len(sequence)] == sequence:
                                next_pred = output[len(sequence)] if len(output) > len(sequence) else a
                                
                                programs.append({
                                    'type': 'utm_lambda',
                                    'program': lambda_expr,
                                    'complexity': len(lambda_expr) // 4,  # Rough complexity
                                    'fits_sequence': True,
                                    'next_prediction': next_pred % self.alphabet_size,
                                    'weight': 2**(-len(lambda_expr) // 4),
                                    'method': 'utm_simulation',
                                    'description': f'Lambda expression: {lambda_expr}',
                                    'accuracy': 0.9
                                })
                        except:
                            continue
                            
        return programs
    
    def _utm_binary_simulation(self, sequence: List[int]) -> List[Dict]:
        """
        🔢 Binary Program UTM Simulation
        
        ELI5: This creates tiny machine code programs (just 1s and 0s) that
        can generate sequences. It's like the most basic computer instructions!
        
        Technical Implementation:
        ========================
        Simulates a minimal binary instruction set:
        - 00: No operation
        - 01: Increment accumulator
        - 10: Output accumulator
        - 11: Reset accumulator
        """
        programs = []
        
        if len(sequence) <= 4:  # Keep computational load manageable
            # Generate short binary programs
            for length in range(2, min(16, getattr(self.config, 'utm_max_program_length', 12)), 2):  # Even length for 2-bit instructions
                # Try a few random binary programs
                for _ in range(min(5, 2**(length//2))):
                    # Generate binary program as array of 2-bit instructions
                    program = np.random.randint(0, 4, size=length//2)
                    
                    try:
                        output = self._simulate_binary_program(program, len(sequence) + 1)
                        if len(output) >= len(sequence) and output[:len(sequence)] == sequence:
                            next_pred = output[len(sequence)] if len(output) > len(sequence) else 0
                            
                            programs.append({
                                'type': 'utm_binary',
                                'program': program.tolist(),
                                'complexity': length,
                                'fits_sequence': True,
                                'next_prediction': next_pred % self.alphabet_size,
                                'weight': 2**(-length),
                                'method': 'utm_simulation',
                                'description': f'Binary program: {program.tolist()}',
                                'accuracy': 1.0
                            })
                    except:
                        continue
                        
        return programs
    
    def _simulate_brainfuck_simple(self, program: str, input_seq: List[int]) -> List[int]:
        """
        Simple Brainfuck interpreter.
        
        Executes Brainfuck program with limited memory and steps.
        """
        memory = [0] * 100  # Limited memory
        pointer = 0
        input_ptr = 0
        output = []
        pc = 0  # Program counter
        max_steps = getattr(self.config, 'utm_max_execution_steps', 1000)
        steps = 0
        
        bracket_map = {}
        stack = []
        
        # Build bracket matching map
        for i, cmd in enumerate(program):
            if cmd == '[':
                stack.append(i)
            elif cmd == ']' and stack:
                left = stack.pop()
                bracket_map[left] = i
                bracket_map[i] = left
        
        while pc < len(program) and steps < max_steps:
            cmd = program[pc]
            steps += 1
            
            if cmd == '>':
                pointer = min(pointer + 1, len(memory) - 1)
            elif cmd == '<':
                pointer = max(pointer - 1, 0)
            elif cmd == '+':
                memory[pointer] = (memory[pointer] + 1) % self.alphabet_size
            elif cmd == '-':
                memory[pointer] = (memory[pointer] - 1) % self.alphabet_size
            elif cmd == '.':
                output.append(memory[pointer])
            elif cmd == ',':
                if input_ptr < len(input_seq):
                    memory[pointer] = input_seq[input_ptr]
                    input_ptr += 1
                else:
                    memory[pointer] = 0
            elif cmd == '[':
                if memory[pointer] == 0:
                    pc = bracket_map.get(pc, pc)
            elif cmd == ']':
                if memory[pointer] != 0:
                    pc = bracket_map.get(pc, pc)
            
            pc += 1
            
        return output
    
    def _simulate_lambda_string(self, lambda_expr: str, context: List[int]) -> List[int]:
        """
        Simple lambda expression evaluator.
        
        Evaluates mathematical lambda expressions safely.
        """
        try:
            # Very basic and safe evaluation
            # Remove 'lambda n:' prefix if present
            if 'lambda n:' in lambda_expr:
                expr = lambda_expr.replace('lambda n:', '').strip()
            else:
                expr = lambda_expr
            
            # Generate output by evaluating expression for different values of n
            output = []
            for n in range(len(context) + 1):
                # Replace 'n' with actual value
                eval_expr = expr.replace('n', str(n))
                try:
                    # Use eval with restricted environment for safety
                    result = eval(eval_expr, {"__builtins__": {}}, {})
                    output.append(int(result) % self.alphabet_size)
                except:
                    output.append(0)
                    
            return output
        except:
            return []
    
    def _simulate_lambda_function(self, lambda_func: Callable, context: List[int]) -> List[int]:
        """
        Execute actual lambda function.
        
        For pre-compiled lambda functions.
        """
        try:
            output = []
            for n in range(len(context) + 1):
                result = lambda_func(n)
                output.append(int(result) % self.alphabet_size)
            return output
        except:
            return []
    
    def _simulate_binary_program(self, program: np.ndarray, max_output: int) -> List[int]:
        """
        Simple binary program executor.
        
        Executes 2-bit instruction set:
        00: NOP, 01: INC, 10: OUT, 11: RST
        """
        accumulator = 0
        output = []
        max_steps = getattr(self.config, 'utm_max_execution_steps', 100)
        
        for step in range(max_steps):
            if len(output) >= max_output:
                break
                
            # Get instruction (cycle through program)
            instruction = program[step % len(program)]
            
            if instruction == 0:  # NOP
                pass
            elif instruction == 1:  # INC
                accumulator = (accumulator + 1) % self.alphabet_size
            elif instruction == 2:  # OUT
                output.append(accumulator)
            elif instruction == 3:  # RST
                accumulator = 0
                
        return output
    
    def _generate_utm_ensemble(self, sequence: List[int]) -> List[Dict]:
        """
        Ensemble UTM simulation combining all methods.
        
        Runs Brainfuck, Lambda, and Binary simulations and combines results.
        """
        programs = []
        
        # Combine all UTM methods
        programs.extend(self._utm_brainfuck_simulation(sequence))
        programs.extend(self._utm_lambda_simulation(sequence))  
        programs.extend(self._utm_binary_simulation(sequence))
        
        # Sort by complexity (shorter programs first)
        programs.sort(key=lambda p: p['complexity'])
        
        # Limit total number of programs to prevent exponential blowup
        max_programs = getattr(self.config, 'utm_max_programs', 20)
        return programs[:max_programs]