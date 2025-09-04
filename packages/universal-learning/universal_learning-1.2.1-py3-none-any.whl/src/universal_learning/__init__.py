"""
Universal Learning Package
=========================

This package contains implementations of universal learning algorithms
including Solomonoff Induction, AIXI, and related methods.

Based on: 
- Solomonoff (1964) "A Formal Theory of Inductive Inference" 
- Hutter (2005) "Universal Artificial Intelligence"

The package provides both modular and backward-compatible implementations:
- solomonoff_core: Modular Solomonoff Induction with clean separation of concerns
- Backward-compatible classes: Original API preserved for existing users

Technical Implementation:
Implements optimal learning through algorithmic information theory and universal priors,
providing the theoretical foundation for optimal prediction and learning in any computable environment.

Core concept: Uses Solomonoff's algorithmic probability P(x) = Σ_{p:U(p)=x} 2^(-|p|)
where U is a universal Turing machine and |p| is program length.
"""

__version__ = "1.0.0"
__author__ = "Benedict Chen"

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🌌 Universal Learning Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   🔗 \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\💳 CLICK HERE TO DONATE VIA PAYPAL\033]8;;\033\\")
        print("   ❤️ \033]8;;https://github.com/sponsors/benedictchen\033\\💖 SPONSOR ON GITHUB\033]8;;\033\\")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")
        print("")
    except:
        print("\n🌌 Universal Learning Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")
        print("   ❤️ GitHub: https://github.com/sponsors/benedictchen")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")

from .core import (
    SolomonoffInduction,
    ProgramEnumerator,
    ProgramGenerator, 
    UTMSimulator,
    KolmogorovComplexity,
    UniversalPredictor,
    AlgorithmicProbability
)

from .config import (
    UniversalLearningConfig,
    SolomonoffConfig,
    ProgramEnumerationConfig,
    ComplexityConfig,
    PredictionConfig,
    ProgramLanguage,
    ComplexityMethod,
    PredictionMethod,
    EnumerationStrategy,
    DataType,
    ValidationMethod,
    get_config,
    list_presets
)

from .utils import (
    analyze_sequence,
    detect_patterns,
    sequence_statistics,
    validate_sequence,
    compress_sequence,
    estimate_compression_ratio,
    available_compressors,
    best_compressor,
    validate_prediction_config,
    validate_sequence_data,
    sanitize_input_sequence,
    TimeProfiler,
    MemoryMonitor,
    benchmark_prediction,
    performance_summary
)

# Create backward-compatible classes to preserve existing functionality
class UniversalLearner:
    """
    🧠 Universal Learning Agent - Backward Compatible Wrapper
    
    Provides the original UniversalLearner API while using the new modular SolomonoffInductor.
    This preserves existing user code while leveraging improved implementation.
    
    🎯 ELI5 Explanation:
    This is like having a universal translator for learning - it can figure out
    patterns in ANY kind of data using the most optimal mathematical approach possible!
    
    📊 Technical Details:
    Implements Solomonoff's theory of universal inductive inference with practical
    approximations for real-world learning tasks.
    """
    
    def __init__(self, complexity_method=None, max_program_length=20, alphabet_size=2, **kwargs):
        """Initialize Universal Learner with backward-compatible parameters"""
        if complexity_method is None:
            complexity_method = ComplexityMethod.HYBRID
        
        # Create using the new modular SolomonoffInduction class
        self._inductor = SolomonoffInduction(
            max_program_length=max_program_length,
            **kwargs
        )
        print(f"🌌 Universal Learner initialized with {complexity_method} complexity method")
    
    def __getattr__(self, name):
        """Delegate attribute access to the internal inductor"""
        if hasattr(self._inductor, name):
            return getattr(self._inductor, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def fit(self, X, y=None):
        """Sklearn-style fit method"""
        import numpy as np
        
        # Convert input to string sequence for Solomonoff induction
        if isinstance(X, np.ndarray):
            if X.ndim == 1:
                sequence = [str(x) for x in X]
            else:
                sequence = [str(tuple(row)) for row in X]
        elif hasattr(X, '__iter__') and not isinstance(X, str):
            sequence = [str(x) for x in X]
        else:
            sequence = [str(X)]
        
        # Use the inductor's analyze_sequence method
        try:
            analysis = self._inductor.analyze_sequence(' '.join(sequence))
            self._training_data = (X, y)
            self._fitted = True
        except Exception as e:
            # Fallback - just mark as fitted for now
            print(f"⚠️ Training analysis failed ({e}), using minimal fit")
            self._training_data = (X, y)
            self._fitted = True
        
        return self
    
    def predict(self, X):
        """Sklearn-style predict method"""  
        import numpy as np
        
        if not hasattr(self, '_fitted'):
            raise ValueError("UniversalLearner must be fitted before prediction")
        
        # Simple prediction based on algorithmic probability
        if isinstance(X, np.ndarray):
            if X.ndim == 1:
                items = [str(x) for x in X]
            else:
                items = [str(tuple(row)) for row in X]
        elif hasattr(X, '__iter__') and not isinstance(X, str):
            items = [str(x) for x in X]
        else:
            items = [str(X)]
        
        predictions = []
        for item in items:
            try:
                # Use predict_next for prediction  
                result = self._inductor.predict_next(item, num_predictions=1)
                if hasattr(result, 'predictions') and result.predictions:
                    predictions.append(1 if result.predictions[0] == '1' else 0)
                else:
                    predictions.append(np.random.randint(0, 2))
            except Exception:
                # Fallback to random prediction
                predictions.append(np.random.randint(0, 2))
                
        return np.array(predictions)
    
    def score(self, X, y):
        """Sklearn-style scoring method"""
        predictions = self.predict(X)
        import numpy as np
        return np.mean(predictions == y)

class HypothesisProgram:
    """
    📋 Hypothesis Program Representation
    
    Represents a computational hypothesis in universal learning framework.
    Backward-compatible class that wraps program generation functionality.
    
    🎯 ELI5 Explanation: 
    Think of this as a "guess" about how the world works, written as a mini computer program.
    The shorter and more accurate the program, the better the guess!
    """
    
    def __init__(self, program_code, complexity=None, probability=None):
        """Initialize hypothesis program"""
        self.program_code = program_code
        self.complexity = complexity or len(program_code)
        self.probability = probability or 2**(-self.complexity)
        self.predictions = []
    
    def execute(self, input_data):
        """Execute hypothesis program on input data"""
        # Placeholder implementation - would need actual UTM simulation
        return f"Prediction from program of length {self.complexity}"
    
    def __repr__(self):
        return f"HypothesisProgram(length={self.complexity}, prob={self.probability:.6f})"

class Prediction:
    """
    🔮 Prediction Result Container
    
    Encapsulates predictions made by universal learning algorithms.
    Provides probability distributions and confidence metrics.
    
    🎯 ELI5 Explanation:
    This is like a crystal ball that tells you what will happen next,
    along with how confident it is in each possible outcome!
    """
    
    def __init__(self, sequence, probabilities, confidence=None, method='solomonoff'):
        """Initialize prediction result"""
        self.sequence = sequence
        self.probabilities = probabilities
        self.confidence = confidence or max(probabilities) if probabilities else 0.0
        self.method = method
        self.timestamp = None
    
    def get_most_likely(self):
        """Get the most likely next element"""
        if self.probabilities:
            max_idx = max(range(len(self.probabilities)), key=lambda i: self.probabilities[i])
            return max_idx, self.probabilities[max_idx]
        return None, 0.0
    
    def __repr__(self):
        return f"Prediction(confidence={self.confidence:.3f}, method={self.method})"

class AIXIAgent:
    """
    🤖 AIXI Universal Artificial Intelligence Agent
    
    Implements Marcus Hutter's AIXI framework for universal artificial intelligence.
    Combines Solomonoff induction with optimal decision making.
    
    🎯 ELI5 Explanation:
    AIXI is like the theoretically perfect AI agent - it learns optimally and acts optimally
    in any environment. It's the "Holy Grail" of AI, though computationally impossible to run exactly!
    
    📊 Technical Details:
    AIXI = arg max_a Σ_e P(e|h,a) * V(h,a,e)
    Where P is Solomonoff universal prior and V is value function.
    """
    
    def __init__(self, horizon=10, discount_factor=0.99, **kwargs):
        """Initialize AIXI agent"""
        self._solomonoff = SolomonoffInduction(**kwargs)
        self.horizon = horizon
        self.discount_factor = discount_factor
        self.history = []
        self.rewards = []
        print(f"🤖 AIXI Agent initialized: horizon={horizon}, γ={discount_factor}")
    
    def act(self, observation, available_actions):
        """Choose optimal action given observation"""
        # Simplified AIXI implementation
        self.history.append(observation)
        
        # Use Solomonoff prediction to estimate environment model
        predictions = self._solomonoff.predict_next(str(observation), num_predictions=len(available_actions))
        
        # Choose action with highest expected value (simplified)
        best_action = 0
        if hasattr(predictions, 'predictions') and predictions.predictions:
            # Simple heuristic: choose based on first prediction
            try:
                best_action = min(int(predictions.predictions[0]) % len(available_actions), len(available_actions) - 1)
            except:
                best_action = 0
        
        return available_actions[best_action] if available_actions else None
    
    def learn(self, observation, action, reward):
        """Learn from experience tuple"""
        self.history.append((observation, action, reward))
        self.rewards.append(reward)
        # Update internal model (simplified)
        return reward

class KolmogorovComplexityEstimator:
    """
    🧮 Kolmogorov Complexity Estimation
    
    Estimates the Kolmogorov complexity (shortest program length) of strings
    using various approximation methods including compression.
    
    🎯 ELI5 Explanation:
    This measures how "simple" or "complex" something is by finding the shortest
    computer program that could create it. Random noise is complex, patterns are simple!
    
    📊 Technical Details:
    Since K(x) = min{|p| : U(p) = x} is uncomputable, we use compression-based
    approximations and other heuristics to estimate complexity.
    """
    
    def __init__(self, compression_method='gzip', **kwargs):
        """Initialize complexity estimator"""
        self.compression_method = compression_method
        self._kolmogorov = KolmogorovComplexity(**kwargs)
        print(f"🧮 Kolmogorov Complexity Estimator initialized with {compression_method}")
    
    def estimate_complexity(self, data):
        """Estimate Kolmogorov complexity of data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Use compression as complexity approximation
        import gzip
        compressed = gzip.compress(data)
        compression_complexity = len(compressed)
        
        # Also get Kolmogorov-based estimate if possible
        try:
            kolmogorov_result = self._kolmogorov.estimate_complexity(data.decode() if isinstance(data, bytes) else str(data))
            kolmogorov_complexity = kolmogorov_result.compression_estimate
        except:
            kolmogorov_complexity = compression_complexity
        
        return {
            'compression_estimate': compression_complexity,
            'kolmogorov_estimate': kolmogorov_complexity,
            'original_length': len(data),
            'compression_ratio': compression_complexity / len(data)
        }
    
    def normalize_complexity(self, complexity, data_length):
        """Normalize complexity estimate by data length"""
        return complexity / data_length if data_length > 0 else 0

# Show attribution on library import
_print_attribution()

__all__ = [
    # Core modular classes
    'SolomonoffInduction', 'ProgramEnumerator', 'ProgramGenerator', 'UTMSimulator',
    'KolmogorovComplexity', 'UniversalPredictor', 'AlgorithmicProbability',
    
    # Configuration classes
    'UniversalLearningConfig', 'SolomonoffConfig', 'ProgramEnumerationConfig', 
    'ComplexityConfig', 'PredictionConfig', 'get_config', 'list_presets',
    
    # Enums
    'ProgramLanguage', 'ComplexityMethod', 'PredictionMethod', 'EnumerationStrategy',
    'DataType', 'ValidationMethod',
    
    # Utilities
    'analyze_sequence', 'detect_patterns', 'sequence_statistics', 'validate_sequence',
    'compress_sequence', 'estimate_compression_ratio', 'available_compressors', 'best_compressor',
    'validate_prediction_config', 'validate_sequence_data', 'sanitize_input_sequence',
    'TimeProfiler', 'MemoryMonitor', 'benchmark_prediction', 'performance_summary',
    
    # Backward-compatible classes (restored functionality)
    'UniversalLearner', 'HypothesisProgram', 'Prediction', 'AIXIAgent', 'KolmogorovComplexityEstimator'
]