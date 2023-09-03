# pytest-static

[![PyPI](https://img.shields.io/pypi/v/pytest-static.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/pytest-static.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/pytest-static)][python version]
[![License](https://img.shields.io/pypi/l/pytest-static)][license]

[![Read the documentation at https://pytest-static.readthedocs.io/](https://img.shields.io/readthedocs/pytest-static/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/56kyle/pytest-static/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/56kyle/pytest-static/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/pytest-static/
[status]: https://pypi.org/project/pytest-static/
[python version]: https://pypi.org/project/pytest-static
[read the docs]: https://pytest-static.readthedocs.io/
[tests]: https://github.com/56kyle/pytest-static/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/56kyle/pytest-static
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Overview

pytest-static is a pytest plugin that allows you to parametrize your tests using type annotations.

What this looks like in practice is that you can write a test like this:

```python
import pytest
from typing import Tuple


@pytest.mark.parametrize_types("a", [Tuple[bool, bool]])
def test_a(a: bool) -> None:
    assert isinstance(a, bool)
```

Which would be equivalent to the following test

```python
import pytest


@pytest.mark.parametrize("a", [(True, True), (True, False), (False, True), (False, False)])
def test_a(a: int) -> None:
    assert isinstance(a, int)
```

For types such as int, str, etc that have an unlimited amount of values, there are premade sets meant to cover common edge cases that are used by default

However, you can also override these defaults if you wish by passing an instance of Config with some custom handlers set.

## Features

## Requirements

- TODO

## Installation

You can install _pytest-static_ via [pip] from [PyPI]:

```console
$ pip install pytest-static
```

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_pytest-static_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/56kyle/pytest-static/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/56kyle/pytest-static/blob/main/LICENSE
[contributor guide]: https://github.com/56kyle/pytest-static/blob/main/CONTRIBUTING.md
[command-line reference]: https://pytest-static.readthedocs.io/en/latest/usage.html
