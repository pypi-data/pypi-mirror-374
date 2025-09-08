# Logging Interceptor

A lightweight Python decorator for logging function calls, arguments, return values, execution time, and exceptions.  
Designed to be simple, reusable, and project-agnostic.

---

## ✨ New Features

- **Automatic log saving**: All logs are saved by default to a `./logs` folder.  
- **Timestamped log files**: Each run creates a new log file named like `interceptor_2025-09-07_17-15-30.log`.  
- **Custom log directory**: Users can change the default log folder at runtime by calling `set_log_directory("/path/to/logs")`.  

---

## 📦 Installation

Install from PyPI:

```bash
pip install simple-logging-interceptor
```

---

## 🚀 Usage

```python
from simple_logging_interceptor.decorators import simple_logging_interceptor, set_log_directory

@simple_logging_interceptor
def add(a, b):
    return a + b

@simple_logging_interceptor
def greet(name, age=None):
    if age:
        return f"Hello {name}, you are {age} years old!"
    return f"Hello {name}!"

print(add(2, 3))
print(greet("Alice"))
print(greet("Bob", age=30))

# Change log directory at runtime
set_log_directory("/tmp/custom_logs")
print(add(10, 20))
```

### Example log output:
```
2025-09-07 17:15:30 - INFO - Calling: add with args=(2, 3), kwargs={}
2025-09-07 17:15:30 - INFO - Returned from add -> 5 (took 0.0021 ms)
2025-09-07 17:15:30 - INFO - Calling: greet with args=('Bob',), kwargs={'age': 30}
2025-09-07 17:15:30 - INFO - Returned from greet -> Hello Bob, you are 30 years old! (took 0.0043 ms)
2025-09-07 17:15:30 - INFO - Logging directory changed to: /tmp/custom_logs, file=interceptor_2025-09-07_17-15-30.log
2025-09-07 17:15:30 - INFO - Calling: add with args=(10, 20), kwargs={}
2025-09-07 17:15:30 - INFO - Returned from add -> 30 (took 0.0015 ms)
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
