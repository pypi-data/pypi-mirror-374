# pypi-test-first

This is a simple Python package that provides basic mathematical operations.

## Installation

```bash
pip install pypi-test-first
```

## Usage

```python
import pypi_test_first

result = pypi_test_first.add(2, 3)
print(result)  # Output: 5

result = pypi_test_first.subtract(5, 3)
print(result)  # Output: 2

result = pypi_test_first.multiply(2, 3)
print(result)  # Output: 6

result = pypi_test_first.divide(6, 3)
print(result)  # Output: 2.0
```

## Available Functions

- `add(a, b)`: Returns the sum of `a` and `b`.
- `subtract(a, b)`: Returns the difference between `a` and `b`.
- `multiply(a, b)`: Returns the product of `a` and `b`.
- `divide(a, b)`: Returns the result of dividing `a` by `b`. Raises a `ValueError` if `b` is zero.