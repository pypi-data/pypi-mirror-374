[![PyPI version](https://badge.fury.io/py/py_llm7_code.svg)](https://badge.fury.io/py/py_llm7_code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/py_llm7_code)](https://pepy.tech/project/py_llm7_code)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# py_llm7_code

`py_llm7_code` generates a **minimal single-function Python package** from a natural-language specification using an LLM7 `ChatLLM7` client.  
It enforces one public function in `__init__.py`, performs safety/syntax/import checks, and runs a minimal demo (`run.py`).

## Installation

```bash
# From PyPI
pip install py_llm7_code

# Or install directly from source
pip install "git+https://github.com/chigwell/py_llm7_code"
````

## Usage

```python
from langchain_llm7 import ChatLLM7
from py_llm7_code.orchestrator import generate_package_with_llm7

llm = ChatLLM7(base_url="https://api.llm7.io/v1")

spec = """
Create a simple package with exactly one function `greet()` that returns 'hello'.
No network calls. Pure stdlib.
"""

result = generate_package_with_llm7(
    llm=llm,
    spec_text=spec,
    package_name="greet_pkg",
    verbose=True,
)

assert result["success"], result.get("error_message")

print("Package dir:", result["package_dir"])
print("Package name:", result["package_name"])
print("Run stdout:", result["stdout"])  # e.g. {"result": "hello"}
```

Generated structure (example):

```
/tmp/llm7_genpkg_xxxxxx/
├─ greet_pkg/
│  └─ __init__.py      # contains exactly one function
└─ run.py              # imports and executes the function
```

## Features

* **One-function enforcement**: rejects multiple functions/classes in `__init__.py`.
* **Safety checks**: blocks dangerous imports (`subprocess`, sockets, HTTP libs, etc.).
* **Syntax & import validation**: `py_compile` + import reflection.
* **Sandboxed execution**: timeouts and best-effort memory limits (POSIX `resource`).
* **Optional venv & deps**: create a temp venv and `pip install` requested packages.
* **Retry loop**: automatically retries generation with feedback.
* **Allow-list for imports**: restrict third-party imports to a provided list.
* **Custom indexes**: supports `--index-url` and `--extra-index-url`.

## API

```python
generate_package_with_llm7(
    llm: ChatLLM7,
    spec_text: str,
    *,
    package_name: str | None = None,
    max_retries: int = 10,
    exec_timeout_sec: int = 8,
    memory_limit_mb: int = 256,
    verbose: bool = False,
    pip_packages: list[str] | None = None,
    allowed_imports: list[str] | None = None,
    pip_index_url: str | None = None,
    pip_extra_index_urls: list[str] | None = None,
    pip_no_deps: bool = False,
) -> dict[str, any]
```

**Key return fields**:

* `success: bool`
* `package_dir: str`
* `package_name: str`
* `init_py_code: str`
* `runner_code: str`
* `run_cmd: str`
* `stdout: str`
* `stderr: str`
* `attempt_count: int`
* `pip_packages_installed: list[str]`
* `venv_python: str`

## Notes

* Memory limits rely on POSIX `resource` and may be ignored on non-POSIX systems.
* By default, third-party imports are **disallowed** unless explicitly allow-listed via `allowed_imports`.
* Network/file-system side effects are restricted; the generator scans for disallowed patterns.

## Contributing

Issues and PRs are welcome. Please use the [issue tracker](https://github.com/chigwell/py_llm7_code/issues).

## License

`py_llm7_code` is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
