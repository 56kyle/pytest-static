# Getting Started with pytest-static

Welcome to `pytest-static`! This guide will show you how to quickly start parametrizing your pytest tests using type annotations for cleaner, more expressive, and often more comprehensive test suites.

## What is pytest-static?

`pytest-static` lets you tell pytest what **types** of data your test function expects. Instead of manually listing every test input, `pytest-static` generates a set of relevant values for those types.

**Before (Standard pytest):**

```python
import pytest
@pytest.mark.parametrize("username, is_active", [
    ("", True), ("", False),
    ("admin", True), ("admin", False),
    ("guest", True), ("guest", False),
])
def test_user_status_standard(username: str, is_active: bool):
    # ... test logic ...
```

**After (With `pytest-static`):**

```python
import pytest
@pytest.mark.parametrize_types("username, is_active", [str, bool])
def test_user_status_static(username: str, is_active: bool):
    # pytest-static provides combinations of typical strings and booleans
    # ... test logic ...
```

## Installation

Install with pip. Pytest will auto-discover it.

```bash
pip install pytest-static
```

## Core Usage: `@pytest.mark.parametrize_types`

This marker is your main tool.

**1. Parametrizing Single Arguments:**
Provide the argument name and its type.

```python
import pytest

@pytest.mark.parametrize_types("value", [int])
def test_process_number(value: int):
    # 'value' will be tested with 0, 1, -1, max/min int, etc.
    print(f"Testing with: {value}") # Use `pytest -s` to see output
    assert isinstance(value, int)
```

**2. Parametrizing Multiple Arguments:**
List argument names and their corresponding types. `pytest-static` creates test cases from all combinations of generated instances.

```python
import pytest

@pytest.mark.parametrize_types(("item_name", "quantity"), [str, int])
def test_inventory_item(item_name: str, quantity: int):
    # Tests all string instances against all integer instances
    print(f"Item: '{item_name}', Quantity: {quantity}")
    assert isinstance(item_name, str) and isinstance(quantity, int)
```

**3. Combining with Standard `@pytest.mark.parametrize`:**
Use both markers when `pytest-static` handles general types and you explicitly list other values. Standard `parametrize` applies _after_ `parametrize_types` expands its cases.

```python
import pytest

@pytest.mark.parametrize("context_id", ["CTX_A", "CTX_B"]) # Applied to each case from below
@pytest.mark.parametrize_types("flag", [bool])
def test_with_context(flag: bool, context_id: str):
    # For flag=True: runs with CTX_A, then CTX_B
    # For flag=False: runs with CTX_A, then CTX_B
    print(f"Flag: {flag}, Context: {context_id}")
```

## How Instances Are Generated (The Short Version)

- **Built-in Types:** For `int`, `str`, `bool`, `list[T]`, `dict[K,V]`, etc., `pytest-static` has predefined sets of common and edge-case values (e.g., `INT_PARAMS` from `type_sets.py`).
  - For `list[T]` or `set[T]`: By default, it generates containers with _one_ element from `T`'s instances (e.g., `[item_from_T_set_1]`, then `[item_from_T_set_2]`).
  - For `tuple[T1, T2]`: It generates combinations, e.g., `(instance_of_T1, instance_of_T2)`.
- **`typing.Literal` & `Enum`:** Uses the defined members/literals.
- **Your Custom Classes (Dataclasses, etc.):** `pytest-static` **tries to automatically instantiate them** if their `__init__` methods have type hints for all arguments, and it knows how to generate those argument types.

  ```python
  from dataclasses import dataclass
  import pytest

  @dataclass
  class User:
      id: int
      name: str

  # pytest-static will attempt to create User(some_int, some_str) automatically!
  @pytest.mark.parametrize_types("user_obj", [User])
  def test_user_object(user_obj: User):
      assert isinstance(user_obj.id, int)
      assert isinstance(user_obj.name, str)
  ```

  If this automatic "fallback" isn't enough or fails (e.g., complex `__init__`), you'll need a custom handler.

## Customizing Data Generation (When Defaults Aren't Enough)

Sometimes, you need specific instances or more complex data. Use `pytest_static.parametric.type_handlers`.

**Example: Providing Specific Instances for a Custom Class**
Let's say automatic instantiation isn't working for `MyServiceConfig` or you need very specific configurations.

```python
# your_module.py
class MyServiceConfig:
    def __init__(self, api_key: str, retries: int = 3):
        self.api_key = api_key
        self.retries = retries
    def __repr__(self): return f"Config({self.api_key!r}, {self.retries})"

# conftest.py (or at the top of your test file)
from pytest_static.parametric import type_handlers
from your_module import MyServiceConfig # Your custom class

# Define specific instances you want to test with
MY_CONFIGS = [
    MyServiceConfig("key_123", retries=5),
    MyServiceSocketHttpAdapter("prod_key_abc", retries=1), # Typo - this should be MyServiceConfig
    MyServiceConfig("test_key_xyz") # Uses default retries
]

def iter_my_service_configs(base_type, type_args):
    # Yield from your predefined list
    yield from MY_CONFIGS

# Tell pytest-static to use this function for MyServiceConfig
type_handlers.register(MyServiceConfig)(iter_my_service_configs)
```

Now, `@pytest.mark.parametrize_types("cfg", [MyServiceConfig])` will use `MY_CONFIGS`.

**Key Ideas for Custom Handlers:**

- **Target a type:** `type_handlers.register(YourType)`
- **Provide a generator function:** `def my_generator(base_type, type_args): yield ...`
  - `base_type` is the type itself (e.g., `MyServiceConfig`).
  - `type_args` are generic parameters (e.g., `(int,)` for `list[int]`).
- **Clear defaults (optional):** `type_handlers.clear(int)` if you want to _replace_ all `int` generation.
- **Keep it simple:** `yield from a_list_of_your_objects` is often the easiest way.

## Why Use `pytest-static`?

- **Less Boilerplate:** Type-driven parametrization reduces manual listing of test cases.
- **Clearer Intent:** Tests clearly state the _kinds_ of data they expect.
- **Automatic Edge Cases:** Default sets for built-ins often cover common problematic values.
- **Flexible:** Good defaults, powerful auto-instantiation for simple classes, and full control via custom handlers when needed.

## Next Steps

1.  **Try it out:** Convert a simple, manually parametrized test to use `@pytest.mark.parametrize_types`.
2.  **Test your dataclasses:** See if `pytest-static` can instantiate them automatically.
3.  **If needed, write a simple custom handler:** For a key class in your project, define a list of test instances and register a handler that yields from it.

This should give you a solid foundation to start leveraging `pytest-static` effectively! For deeper dives into specific instance sets or advanced handler techniques, refer to the project's source or more detailed documentation.
