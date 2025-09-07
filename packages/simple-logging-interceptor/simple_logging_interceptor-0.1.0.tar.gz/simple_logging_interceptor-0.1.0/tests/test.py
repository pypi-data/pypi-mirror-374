import pytest
import logging
from simple_logging_interceptor.decorators import simple_logging_interceptor

# Match the actual logger name used in decorators.py
LIB_LOGGER_NAME = "logging_interceptor.decorators"


@simple_logging_interceptor
def add(a, b):
    return a + b


@simple_logging_interceptor
def divide(a, b):
    return a / b


@simple_logging_interceptor
def greet(name, title=None, age=None):
    if title and age:
        return f"{title} {name}, {age} years old"
    elif title:
        return f"{title} {name}"
    elif age:
        return f"{name}, {age} years old"
    return f"Hello {name}"


def test_add(caplog):
    caplog.set_level(logging.INFO, logger=LIB_LOGGER_NAME)
    result = add(2, 3)
    assert result == 5
    logs = "\n".join(r.message for r in caplog.records if r.name == LIB_LOGGER_NAME)
    assert "Calling: add" in logs
    assert "Returned from add -> 5" in logs
    print("✅ test_add passed")


def test_divide(caplog):
    caplog.set_level(logging.INFO, logger=LIB_LOGGER_NAME)
    result = divide(10, 2)
    assert result == 5
    logs = "\n".join(r.message for r in caplog.records if r.name == LIB_LOGGER_NAME)
    assert "Calling: divide" in logs
    assert "Returned from divide -> 5.0" in logs
    print("✅ test_divide passed")


def test_divide_by_zero(caplog):
    caplog.set_level(logging.INFO, logger=LIB_LOGGER_NAME)
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
    logs = "\n".join(r.message for r in caplog.records if r.name == LIB_LOGGER_NAME)
    assert "Exception in divide" in logs
    print("✅ test_divide_by_zero passed")


def test_greet_with_kwargs(caplog):
    caplog.set_level(logging.INFO, logger=LIB_LOGGER_NAME)
    result = greet("Alice", title="Dr.", age=30)
    assert result == "Dr. Alice, 30 years old"
    logs = "\n".join(r.message for r in caplog.records if r.name == LIB_LOGGER_NAME)
    assert "Calling: greet" in logs
    assert "kwargs={'title': 'Dr.', 'age': 30}" in logs
    assert "Returned from greet -> Dr. Alice, 30 years old" in logs
    print("✅ test_greet_with_kwargs passed")


def test_greet_without_kwargs(caplog):
    caplog.set_level(logging.INFO, logger=LIB_LOGGER_NAME)
    result = greet("Bob")
    assert result == "Hello Bob"
    logs = "\n".join(r.message for r in caplog.records if r.name == LIB_LOGGER_NAME)
    assert "Calling: greet" in logs
    assert "Returned from greet -> Hello Bob" in logs
    print("✅ test_greet_without_kwargs passed")
