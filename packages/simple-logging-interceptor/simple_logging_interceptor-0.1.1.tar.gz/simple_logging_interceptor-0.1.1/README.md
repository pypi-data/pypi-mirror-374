# Logging Interceptor

A simple Python decorator for logging function calls, arguments, return values, execution time, and exceptions.  
Designed to be **lightweight, reusable, and project-agnostic**.

---

## ✨ Features
- Logs:
  - Function name
  - Arguments (`args`, `kwargs`)
  - Return value
  - Execution time (in ms)
  - Exceptions (with traceback)
- Works across projects with minimal setup
- Compatible with Python 3.8+

---

## 📦 Installation

From **PyPI** (after publishing):

```bash
pip install logging-interceptor
```

Or install locally (development mode):

```bash
git clone https://github.com/yourusername/logging-interceptor.git
cd logging-interceptor
pip install -e .
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


print(add(2, 3))           # Logs inputs, result, and timing
print(greet("Alice"))      # Logs kwargs properly
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
To run tests:

```bash
pip install -r requirements.txt
pytest tests/
```

Example success output:
```
✅ test_add passed
✅ test_divide passed
✅ test_divide_by_zero passed
✅ test_greet_with_kwargs passed
✅ test_greet_without_kwargs passed
```

---

## 📂 Project Structure

```
logging_interceptor/
│── __init__.py
│── decorators.py
tests/
│── test.py
setup.py
README.md
requirements.txt
```

---

## 📜 License
This project is licensed under the **MIT License**.

---

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.