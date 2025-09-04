# unpacking

[![PyPI](https://img.shields.io/pypi/v/unpacking)](https://pypi.org/project/unpacking/)
[![Tests](https://github.com/cctien/unpacking/actions/workflows/python-package.yml/badge.svg)](https://github.com/cctien/unpacking/actions/workflows/python-package.yml)
[![License](https://img.shields.io/github/license/cctien/unpacking)](./LICENSE)

Unpacking, spreading, or splatting positional arguments and keyword arguments in Python.

This library provides functional tools as classes that give you versions of your original functions which use unpacking expressions ([Python reference](https://docs.python.org/3/reference/expressions.html#calls), [PEP 448](https://peps.python.org/pep-0448/)) for the function calls underneath.

## Table of Contents

- [unpacking](#unpacking)
  - [Table of Contents](#table-of-contents)
  - [Why Use Unpacking?](#why-use-unpacking)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Examples](#examples)
    - [Basic Example](#basic-example)
    - [Partial Argument Matching](#partial-argument-matching)
    - [Multiprocessing Examples](#multiprocessing-examples)
      - [Simple Example](#simple-example)
      - [Data Processing Example](#data-processing-example)
  - [Common Patterns](#common-patterns)
    - [Working with Configuration Objects](#working-with-configuration-objects)
    - [Chaining with Other Functional Tools](#chaining-with-other-functional-tools)
  - [API Reference](#api-reference)
    - [`starred(func) -> callable`](#starredfunc---callable)
    - [`doublestarred(func) -> callable`](#doublestarredfunc---callable)
    - [`unpacking(func) -> callable`](#unpackingfunc---callable)
    - [`starredpart(func) -> callable`](#starredpartfunc---callable)
    - [`doublestarredpart(func) -> callable`](#doublestarredpartfunc---callable)
    - [`unpackingpart(func) -> callable`](#unpackingpartfunc---callable)

## Why Use Unpacking?

- **Multiprocessing**: Easily map functions over lists of mixed argument structures
- **Dynamic function calls**: Handle variable argument formats cleanly without manual unpacking
- **Functional programming**: Create reusable argument-unpacking patterns
- **Code simplification**: Reduce boilerplate when working with argument collections

## Installation

```bash
pip install -U unpacking
```

## Quick Start

```python
from unpacking import unpacking

def your_function(x, y, z=None):
    return f"{x} + {y} + {z}"

# Works with both lists and dicts automatically
result1 = unpacking(your_function)([1, 2, 3])          # Uses *args
result2 = unpacking(your_function)({"x": 1, "y": 2})   # Uses **kwargs
```

## Examples

### Basic Example

```python
from unpacking import starred, doublestarred, unpacking

def add(x, y):
    return x + y

args = [1, 2]
kwargs = {"x": 1, "y": 2}

# Traditional unpacking
print(add(*args))                   # 3
print(add(**kwargs))                # 3

# Using unpacking library
print(starred(add)(args))           # 3
print(doublestarred(add)(kwargs))   # 3

# `unpacking` automatically detects the appropriate unpacking method
print(unpacking(add)(args))         # 3
print(unpacking(add)(kwargs))       # 3
```

### Partial Argument Matching

Handle cases where you have more arguments than the function needs:

```python
from unpacking import starredpart, doublestarredpart, unpackingpart

def add(x, y):
    return x + y

args_excess = [1, 2, 3]  # Extra argument ignored
kwargs_excess = {"x": 1, "y": 2, "z": 3}  # Extra keyword ignored

print(starredpart(add)(args_excess))         # 3
print(doublestarredpart(add)(kwargs_excess)) # 3
print(unpackingpart(add)(args_excess))       # 3
print(unpackingpart(add)(kwargs_excess))     # 3
```

### Multiprocessing Examples

#### Simple Example

```python
from concurrent.futures import ProcessPoolExecutor
from unpacking import unpacking

def add(x, y):
    return x + y

args_list = [[1, 2], [3, 4]]
kwargs_list = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]

with ProcessPoolExecutor(2) as executor:
    print(tuple(executor.map(unpacking(add), args_list)))    # (3, 7)
    print(tuple(executor.map(unpacking(add), kwargs_list)))  # (3, 7)
```

#### Data Processing Example

```python
from concurrent.futures import ProcessPoolExecutor
from unpacking import unpacking

def process_data(file_path, format_type, compression=None):
    """Process a data file with specified format and optional compression."""
    # Simulate processing logic
    result = f"Processed {file_path} as {format_type}"
    if compression:
        result += f" with {compression} compression"
    return result

# Mixed argument formats - some positional, some keyword, some partial
tasks = [
    ["data1.csv", "csv", "gzip"],                                    # All positional
    ["data2.json", "json"],                                          # Partial positional
    {"file_path": "data3.xml", "format_type": "xml"},                # Keyword only
    {"file_path": "data4.parquet", "format_type": "parquet", "compression": "snappy"}  # All keyword
]

with ProcessPoolExecutor() as executor:
    results = list(executor.map(unpacking(process_data), tasks))
    for result in results:
        print(result)
```

## Common Patterns

### Working with Configuration Objects

```python
from unpacking import unpacking

def create_connection(host, port, username, password=None, timeout=30):
    return f"Connected to {host}:{port} as {username}"

configs = [
    {"host": "localhost", "port": 5432, "username": "admin"},
    {"host": "remote.db", "port": 3306, "username": "user", "password": "secret"},
]

connections = [unpacking(create_connection)(config) for config in configs]
```

### Chaining with Other Functional Tools

```python
from functools import partial
from unpacking import unpacking

def add_and_multiply(x, y, multiplier=1):
    return (x + y) * multiplier

# Create a specialized function
add_and_double = partial(unpacking(add_and_multiply), multiplier=2)

args_list = [[2, 3], [4, 5], [1, 6]]
results = list(map(add_and_multiply, args_list))  # [10, 18, 14]
```

## API Reference

### `starred(func) -> callable`

Returns a function that calls `func(*args)` when given an iterable.

**Parameters:**

- `func`: The function to wrap

**Returns:** A new function that unpacks positional arguments from an iterable

**Example:**

```python
starred_func = starred(your_function)
result = starred_func([arg1, arg2, arg3])  # Equivalent to your_function(*[arg1, arg2, arg3])
```

### `doublestarred(func) -> callable`

Returns a function that calls `func(**kwargs)` when given a mapping.

**Parameters:**

- `func`: The function to wrap

**Returns:** A new function that unpacks keyword arguments from a mapping

**Example:**

```python
doublestarred_func = doublestarred(your_function)
result = doublestarred_func({"x": 1, "y": 2})  # Equivalent to your_function(**{"x": 1, "y": 2})
```

### `unpacking(func) -> callable`

Automatically detects whether to use `*args` or `**kwargs` unpacking based on the argument type.

**Parameters:**

- `func`: The function to wrap

**Returns:** A new function that unpacks arguments appropriately

**Behavior:**

- For sequences (list, tuple): uses `*args` unpacking
- For mappings (dict): uses `**kwargs` unpacking

**Example:**

```python
unpacking_func = unpacking(your_function)
result1 = unpacking_func([1, 2, 3])          # Uses *args
result2 = unpacking_func({"x": 1, "y": 2})   # Uses **kwargs
```

### `starredpart(func) -> callable`

Like `starred()`, but only passes as many positional arguments as the function accepts.

**Parameters:**

- `func`: The function to wrap

**Returns:** A new function that unpacks only the needed positional arguments

### `doublestarredpart(func) -> callable`

Like `doublestarred()`, but only passes keyword arguments that the function accepts.

**Parameters:**

- `func`: The function to wrap

**Returns:** A new function that unpacks only the needed keyword arguments

### `unpackingpart(func) -> callable`

Like `unpacking()`, but only passes as many arguments as the function needs (works with both positional and keyword arguments).

**Parameters:**

- `func`: The function to wrap

**Returns:** A new function that unpacks only the needed arguments
