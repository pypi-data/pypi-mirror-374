# Logging Interceptor

A lightweight Python decorator for logging function calls, arguments, return values, execution time, and exceptions.  
Designed to be simple, reusable, and project-agnostic.

---

## 📦 Installation

Install from PyPI:

```bash
pip install logging-interceptor
```

---

## 🚀 Usage

```python
from logging_interceptor.decorators import logging_interceptor


@logging_interceptor
def add(a, b):
    return a + b


@logging_interceptor
def greet(name, age=None):
    if age:
        return f"Hello {name}, you are {age} years old!"
    return f"Hello {name}!"


print(add(2, 3))
print(greet("Alice"))
print(greet("Bob", age=30))
```

### Example log output:
```
2025-09-07 12:01:00,123 - INFO - Calling: add with args=(2, 3), kwargs={}
2025-09-07 12:01:00,124 - INFO - Returned from add -> 5 (took 0.01 ms)
2025-09-07 12:01:00,125 - INFO - Calling: greet with args=('Bob',), kwargs={'age': 30}
2025-09-07 12:01:00,125 - INFO - Returned from greet -> Hello Bob, you are 30 years old! (took 0.02 ms)
```

---

## 🧪 Running Tests

This project uses **pytest**.  
To run tests locally:

```bash
pip install pytest
pytest
```

---

## 📜 License

This project is licensed under the **MIT License**.
