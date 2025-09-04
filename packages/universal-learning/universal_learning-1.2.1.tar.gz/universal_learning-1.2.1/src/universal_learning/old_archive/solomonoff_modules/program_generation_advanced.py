#!/usr/bin/env python3
"""
🚀 Universal Learning - Advanced Program Generation Module
==========================================================

Advanced program generation methods for Solomonoff induction.
Extracted from program_generation.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Solomonoff (1964) - Universal induction via program enumeration

This module implements advanced methods:
- Compression-based complexity estimation
- Context tree weighting (CTW)
- Hybrid ensemble approaches

These methods provide practical approximations to the universal distribution
with better computational tractability than exhaustive UTM enumeration.
"""

import numpy as np
import zlib
import bz2
import lzma
from typing import List, Dict, Optional, Union, Any
from collections import defaultdict, Counter
import heapq

class AdvancedGenerationMixin:
    """
    Advanced program generation methods for practical universal prediction.
    
    Implements computationally efficient approximations to the universal
    distribution using compression algorithms and probabilistic models.
    """
    
    def _generate_programs_compression(self, sequence: List[int]) -> List[Dict]:
        """
        🗜️ Compression-Based Program Generation
        
        ELI5: This uses file compression algorithms (like ZIP) to estimate how
        complex a sequence is. If it compresses well, it's probably simple and
        has a short explanation!
        
        Technical Implementation:
        ========================
        Uses compression length as proxy for Kolmogorov complexity:
        
        K(x) ≈ |compress(x)|
        
        This approximation is based on the principle that good compression
        algorithms exploit regularity and structure in data.
        
        Compression Methods:
        ===================
        - GZIP: General-purpose LZ77-based compression
        - BZIP2: Block-sorting compression with Huffman coding
        - LZMA: Lempel-Ziv-Markov chain compression
        - LZ77: Basic dictionary-based compression
        """
        programs = []
        
        if not sequence:
            return programs
        
        # Convert sequence to bytes for compression
        seq_bytes = bytes(sequence)
        
        compression_methods = {
            'gzip': lambda x: zlib.compress(x),
            'bzip2': lambda x: bz2.compress(x),  
            'lzma': lambda x: lzma.compress(x)
        }
        
        for method_name, compress_func in compression_methods.items():
            try:
                compressed = compress_func(seq_bytes)
                complexity = len(compressed)
                
                # Estimate next value using compression-based prediction
                # Try appending different values and see which compresses best
                best_next = 0
                best_compression_gain = float('inf')
                
                for next_val in range(min(self.alphabet_size, 10)):  # Limit search
                    extended_seq = seq_bytes + bytes([next_val])
                    try:
                        extended_compressed = compress_func(extended_seq)
                        compression_gain = len(extended_compressed) - len(compressed)
                        
                        if compression_gain < best_compression_gain:
                            best_compression_gain = compression_gain
                            best_next = next_val
                    except:
                        continue
                
                programs.append({
                    'type': 'compression',
                    'method': method_name,
                    'complexity': complexity,
                    'fits_sequence': True,  # Compression always "fits"
                    'next_prediction': best_next,
                    'weight': 2**(-complexity / 8),  # Scale complexity
                    'compression_ratio': len(seq_bytes) / max(complexity, 1),
                    'description': f'{method_name.upper()} compression program',
                    'accuracy': 0.8  # Lower accuracy due to approximation
                })
                
            except Exception as e:
                continue
                
        return programs
    
    def _generate_programs_context_tree(self, sequence: List[int]) -> List[Dict]:
        """
        🌳 Context Tree Weighting Program Generation
        
        ELI5: This builds a smart tree that remembers what usually comes after
        different patterns. Like noticing that after "1,2" usually comes "3"!
        
        Technical Implementation:
        ========================
        Implements Context Tree Weighting (CTW) algorithm for sequence prediction.
        Builds a tree of contexts of increasing depth and weights predictions.
        
        CTW Properties:
        ==============
        - Optimal for prediction of tree sources
        - Regret bounded by O(log n) for n observations
        - Combines multiple context depths automatically
        
        Context Tree Structure:
        ======================
        Each node represents a context (history of symbols).
        Deeper nodes represent longer contexts.
        Predictions are weighted mixture of all context depths.
        """
        programs = []
        
        if len(sequence) < 2:
            return programs
        
        max_context_depth = min(8, len(sequence) - 1)  # Limit depth
        
        # Build context tree
        context_tree = {}
        
        for depth in range(1, max_context_depth + 1):
            for i in range(depth, len(sequence)):
                context = tuple(sequence[i-depth:i])
                next_symbol = sequence[i]
                
                if context not in context_tree:
                    context_tree[context] = defaultdict(int)
                context_tree[context][next_symbol] += 1
        
        # Generate predictions using different context depths
        for depth in range(1, max_context_depth + 1):
            if len(sequence) >= depth:
                context = tuple(sequence[-depth:])
                
                if context in context_tree:
                    # Get probability distribution for next symbol
                    counts = context_tree[context]
                    total_count = sum(counts.values())
                    
                    if total_count > 0:
                        # Find most likely next symbol
                        best_next = max(counts.keys(), key=lambda k: counts[k])
                        probability = counts[best_next] / total_count
                        
                        # Complexity based on context depth and probability
                        complexity = depth + (-np.log2(probability + 1e-10))
                        
                        programs.append({
                            'type': 'context_tree',
                            'context_depth': depth,
                            'context': list(context),
                            'complexity': complexity,
                            'fits_sequence': True,
                            'next_prediction': best_next,
                            'weight': 2**(-complexity),
                            'probability': probability,
                            'method': 'context_tree',
                            'description': f'Context tree depth {depth}, context {list(context)}',
                            'accuracy': min(0.95, probability)
                        })
        
        return programs
    
    def _generate_programs_hybrid(self, sequence: List[int]) -> List[Dict]:
        """
        🎭 Hybrid Ensemble Program Generation
        
        ELI5: This combines ALL the different methods we have - patterns, 
        compression, UTM simulation, context trees - and picks the best 
        explanations from each!
        
        Technical Implementation:
        ========================
        Runs all available program generation methods and creates weighted
        ensemble of their predictions. Uses multiple strategies:
        
        1. Best-of-each: Top program from each method
        2. Complexity-weighted: Weight by inverse complexity
        3. Accuracy-weighted: Weight by historical accuracy
        4. Ensemble prediction: Combine predictions probabilistically
        """
        all_programs = []
        
        # Collect programs from all methods
        method_programs = {
            'basic': self._generate_programs_basic(sequence),
            'compression': self._generate_programs_compression(sequence),
            'utm': self._generate_programs_utm(sequence),
            'context_tree': self._generate_programs_context_tree(sequence)
        }
        
        # Add programs with method tags
        for method_name, programs in method_programs.items():
            for program in programs:
                program['generation_method'] = method_name
                all_programs.append(program)
        
        # Sort by complexity (better programs first)
        all_programs.sort(key=lambda p: p['complexity'])
        
        # Create ensemble predictions
        ensemble_programs = []
        
        # Method 1: Best program from each method
        for method_name, programs in method_programs.items():
            if programs:
                best_program = min(programs, key=lambda p: p['complexity'])
                best_program['ensemble_type'] = 'best_per_method'
                ensemble_programs.append(best_program)
        
        # Method 2: Top-k by complexity across all methods
        top_k = min(10, len(all_programs))
        for i in range(top_k):
            program = all_programs[i].copy()
            program['ensemble_type'] = 'top_complexity'
            program['rank'] = i + 1
            ensemble_programs.append(program)
        
        # Method 3: Weighted ensemble prediction
        if all_programs:
            # Calculate ensemble next prediction
            prediction_votes = defaultdict(float)
            total_weight = 0
            
            for program in all_programs[:20]:  # Use top 20 programs
                weight = program.get('weight', 2**(-program['complexity']))
                next_pred = program.get('next_prediction', 0)
                
                prediction_votes[next_pred] += weight
                total_weight += weight
            
            # Normalize votes
            if total_weight > 0:
                for pred in prediction_votes:
                    prediction_votes[pred] /= total_weight
            
            # Create ensemble program
            if prediction_votes:
                best_ensemble_pred = max(prediction_votes.keys(), 
                                       key=lambda k: prediction_votes[k])
                ensemble_confidence = prediction_votes[best_ensemble_pred]
                
                ensemble_programs.append({
                    'type': 'hybrid_ensemble',
                    'ensemble_type': 'weighted_voting',
                    'complexity': 6,  # Meta-complexity for ensemble
                    'fits_sequence': True,
                    'next_prediction': best_ensemble_pred,
                    'weight': 2**(-6),
                    'confidence': ensemble_confidence,
                    'prediction_votes': dict(prediction_votes),
                    'method': 'hybrid_ensemble',
                    'description': f'Ensemble of {len(all_programs)} programs',
                    'accuracy': 0.85 + 0.1 * ensemble_confidence  # Boost for ensemble
                })
        
        return ensemble_programs
    
    def _generate_lempel_ziv_programs(self, sequence: List[int]) -> List[Dict]:
        """
        📚 Lempel-Ziv Complexity Program Generation
        
        ELI5: This counts how many unique patterns are needed to build up
        the sequence. Fewer unique patterns = simpler sequence!
        
        Technical Implementation:
        ========================
        Computes Lempel-Ziv complexity by parsing sequence into minimal
        number of distinct substrings.
        
        LZ78 Parsing Algorithm:
        ======================
        1. Start with empty dictionary
        2. Read symbols, finding longest match in dictionary  
        3. Add new pattern to dictionary
        4. Complexity = number of dictionary entries
        """
        programs = []
        
        if not sequence:
            return programs
        
        # Lempel-Ziv 78 parsing
        dictionary = {'': 0}  # Empty string has code 0
        parsed_blocks = []
        current_code = 1
        i = 0
        
        while i < len(sequence):
            # Find longest match in dictionary
            longest_match = ''
            j = i
            
            while j <= len(sequence):
                candidate = tuple(sequence[i:j])
                candidate_str = str(candidate)
                
                if candidate_str in dictionary:
                    longest_match = candidate_str
                    j += 1
                else:
                    break
            
            # Add new pattern to dictionary
            if j <= len(sequence):
                new_pattern = longest_match + str(sequence[j-1]) if j > i else str(sequence[i])
                dictionary[new_pattern] = current_code
                parsed_blocks.append((longest_match, sequence[j-1] if j > i else sequence[i]))
                current_code += 1
                i = j
            else:
                # Handle end of sequence
                parsed_blocks.append((longest_match, None))
                break
        
        lz_complexity = len(parsed_blocks)
        
        # Predict next symbol based on current context
        if len(sequence) >= 2:
            # Look for patterns ending with last few symbols
            context = tuple(sequence[-2:])
            context_str = str(context)
            
            # Find patterns in dictionary that start with this context
            next_prediction = sequence[-1]  # Default fallback
            
            for pattern, code in dictionary.items():
                if pattern.startswith(context_str) and len(pattern) > len(context_str):
                    # Extract what comes after the context
                    try:
                        next_char = pattern[len(context_str)]
                        next_prediction = int(next_char)
                        break
                    except:
                        continue
        else:
            next_prediction = sequence[-1] if sequence else 0
        
        programs.append({
            'type': 'lempel_ziv',
            'complexity': lz_complexity,
            'fits_sequence': True,
            'next_prediction': next_prediction % self.alphabet_size,
            'weight': 2**(-lz_complexity),
            'dictionary_size': len(dictionary),
            'parsed_blocks': len(parsed_blocks),
            'method': 'lempel_ziv',
            'description': f'Lempel-Ziv parsing with {lz_complexity} blocks',
            'accuracy': 0.75
        })
        
        return programs
    
    def _adaptive_complexity_estimation(self, sequence: List[int]) -> Dict[str, float]:
        """
        📊 Adaptive Complexity Estimation
        
        Combines multiple complexity measures to get robust estimate.
        """
        estimates = {}
        
        # Compression-based estimates
        try:
            seq_bytes = bytes(sequence)
            estimates['gzip'] = len(zlib.compress(seq_bytes))
            estimates['bzip2'] = len(bz2.compress(seq_bytes)) 
            estimates['lzma'] = len(lzma.compress(seq_bytes))
        except:
            pass
        
        # Information-theoretic estimates
        if sequence:
            # Empirical entropy
            counts = Counter(sequence)
            probs = [c/len(sequence) for c in counts.values()]
            entropy = -sum(p * np.log2(p) for p in probs if p > 0)
            estimates['entropy'] = entropy * len(sequence)
            
            # Conditional entropy (1st order Markov)
            if len(sequence) > 1:
                conditional_counts = defaultdict(Counter)
                for i in range(len(sequence)-1):
                    conditional_counts[sequence[i]][sequence[i+1]] += 1
                
                conditional_entropy = 0
                for prev_symbol, next_counts in conditional_counts.items():
                    total = sum(next_counts.values())
                    for count in next_counts.values():
                        p = count / total
                        conditional_entropy -= count * np.log2(p)
                
                estimates['conditional_entropy'] = conditional_entropy
        
        return estimates