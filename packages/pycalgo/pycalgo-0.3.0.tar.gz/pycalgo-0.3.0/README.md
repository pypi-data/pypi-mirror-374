# PyCalGo

A high-performance, cross-platform Python calculator library using Go-based native implementations.

## Features

### Basic Arithmetic
- Addition, subtraction, multiplication, division
- Integer operations with native Go performance

### Scientific Functions
- Square root, power, logarithm
- Trigonometric functions (sin, cos, tan)
- Double precision floating-point operations

### Unique Fast Operations
- Fast bit counting for 64-bit integers
- Modular factorial computation
- XorShift pseudo-random number generation

## Installation

```bash
pip install pycalgo
```

## Quick Start

```python
import pycalgo

# Basic arithmetic
print(pycalgo.add(10, 5))        # 15
print(pycalgo.mul(6, 7))         # 42

# Scientific functions
print(pycalgo.sqrt(16))          # 4.0
print(pycalgo.sin(1.57))         # ~1.0

# Fast operations
print(pycalgo.bitcount(15))      # 4 (binary: 1111)
print(pycalgo.factmod(5, 7))     # 1 (5! mod 7)

# Random number generation
rand, new_seed = pycalgo.xorshift(12345)
print(f"Random: {rand}")
```

## Platform Support

- **Windows**: Uses `calculator.dll`
- **Linux**: Uses `calculator.so`
- **macOS**: Uses `calculator.dylib`

## Requirements

- Python 3.6 or higher
- Native library automatically selected based on OS
