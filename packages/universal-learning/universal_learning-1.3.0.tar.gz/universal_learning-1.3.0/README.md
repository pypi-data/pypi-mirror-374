# Universal Learning

This package contains implementations of universal learning algorithms including Solomonoff Induction, AIXI, and related methods from algorithmic information theory.

Implements optimal learning through algorithmic information theory and universal priors, providing the theoretical foundation for optimal prediction and learning in any computable environment.

## Features

- **Solomonoff Induction**: Optimal universal prediction algorithm
- **AIXI Framework**: Universal artificial intelligence architecture
- **Modular Design**: Clean separation of concerns with backward compatibility
- **Research Accurate**: Based on foundational algorithmic information theory

## Core Concepts

The package implements optimal learning using Solomonoff's algorithmic probability:

P(x) = Σ_{p:U(p)=x} 2^(-|p|)

where U is a universal Turing machine and |p| is program length.

## Installation

```bash
pip install universal-learning
```

## Basic Usage

```python
from universal_learning import SolomonoffInduction

# Create Solomonoff predictor
predictor = SolomonoffInduction()

# Learn from data sequence
sequence = [1, 0, 1, 1, 0, 1, 0, 0]
predictor.learn_sequence(sequence)

# Predict next symbol
next_symbol = predictor.predict_next()
```

## Research Foundation

Based on foundational work in universal artificial intelligence:
- Solomonoff (1964) "A Formal Theory of Inductive Inference"
- Hutter (2005) "Universal Artificial Intelligence"

## Technical Implementation

Provides the theoretical foundation for optimal prediction and learning in any computable environment through:
- Universal priors over program space
- Algorithmic probability calculations
- Optimal sequence prediction
- Universal artificial intelligence principles

## Author

**Benedict Chen** (benedict@benedictchen.com)

- Support: [PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)
- Sponsor: [GitHub Sponsors](https://github.com/sponsors/benedictchen)

## License

Custom Non-Commercial License with Donation Requirements