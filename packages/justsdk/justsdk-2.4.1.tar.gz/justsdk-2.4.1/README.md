[![PyPI](https://img.shields.io/pypi/v/justsdk)](https://pypi.org/project/justsdk/)

# justsdk

<img src="https://raw.githubusercontent.com/eesuhn/justsdk/refs/heads/main/docs/cat-pilot.jpeg" alt="cat" width="160" /><br>

This is a collection of my commonly used functions that I figured would be nice to have in a library.

## Installation

```bash
pip install justsdk
```

_or visit [#history](https://pypi.org/project/justsdk/#history) for legacy versions._

## Usage

Get started by importing the package:

```python
import justsdk
```

### 1. Colored Print

*_from [`color_print.py`](https://github.com/eesuhn/justsdk/tree/main/src/justsdk/color_print.py)_

Print colored messages to the console with optional timestamps.<br>
Simple as that, expected output: `[MESSAGE_TYPE] YOUR_MESSAGE_HERE`

<img src="https://raw.githubusercontent.com/eesuhn/justsdk/refs/heads/main/docs/sample_colored_print.png" alt="screenshot" width="200" />

#### 1.1. Convenience Functions

- Most of the time, you’ll use the convenience functions::

  ```python
  justsdk.print_success(
      message="YOUR_MESSAGE_HERE",
      newline_before=False,  # Add a newline before [MESSAGE_TYPE]
      newline_after=False,   # Add a newline after [MESSAGE_TYPE]
      file=None,             # Print to a specific file (default: sys.stdout)
      show_timestamp=False
  )
  ```

- Available functions:
  - `print_success()` — Green
  - `print_warning()` — Yellow
  - `print_error()` — Red
  - `print_info()` — Magenta
  - `print_debug()` — Cyan

#### 1.2. Initiating `ColorPrinter` Object

- Else, you can have more control by creating an instance:

  ```python
  from justsdk import ColorPrinter


  printer = ColorPrinter(
      file=None,
      use_color=True,
      show_timestamp=False,  # Show timestamp in each message (based on your timezone)
      quiet=False
  )
  printer.success("YOUR_MESSAGE_HERE")
  ```

### 2. File Utilities

*_from [`file_utils.py`](https://github.com/eesuhn/justsdk/tree/main/src/justsdk/file_utils.py)_

Handy functions for reading, writing, and pretty-printing files in JSON/YAML formats (and others treated as plain text)

#### 2.1. Reading Files

- Read a single file (auto-detects JSON/YAML/text):

  ```python
  justsdk.read_file(
      file_path="YOUR_FILE_PATH_HERE",
      encoding="utf-8",
      use_orjson=True
  )
  ```

- Returns the parsed data (`dict`/`list` for JSON/YAML, `str` for text).

- Optional arguments:
  - `encoding="utf-8"` — File encoding
  - `use_orjson=True` — Use [`orjson`](https://pypi.org/project/orjson/) for JSON files (just faster & better)

#### 2.2. Writing Files

- Write data to a file (auto-detects JSON/YAML/text):

  ```python
  justsdk.write_file(
      data={"a": 1, "b": 2},
      file_path="YOUR_OUTPUT.json",
      indent=2,            # Indentation level (JSON only)
      sort_keys=True,      # Sort dictionary keys
      use_orjson=True,
      encoding="utf-8",
      ensure_ascii=False,
      atomic=False         # Atomic write (safu for critical data)
  )
  ```

- Creates parent directories if needed.

- Returns `True` on success, else `False`.

- Raises `ValueError` if `data` is `None`.

#### 2.3. Pretty-Print Data

- Print data in JSON or YAML format (optionally colorized):

  ```python
  justsdk.print_data(
      data={"a": 1, "b": 2},
      data_type="json",  # or "yaml", "yml"
      indent=2,
      sort_keys=False,
      use_orjson=True,
      colorize=False
  )
  ```

- If `colorize=True`, uses [`pygments`](https://pypi.org/project/Pygments/) for syntax highlighting.

#### 2.4. Batch Operations

- Read multiple files at once:

  ```python
  justsdk.read_files(["a.json", "b.yaml"])
  # Returns: {Path("a.json"): {...}, Path("b.yaml"): {...}}
  ```

  - `dict` mapping paths to parsed data

- Write multiple files at once:

  ```python
  justsdk.write_files({
      "a.json": {"x": 1},
      "b.yaml": {"y": 2}
  })
  # Returns: {Path("a.json"): True, Path("b.yaml"): True}
  ```

  - `dict` mapping paths to ops status (`True`/`False`)

## License

This project is under the MIT License — see the [LICENSE](https://raw.githubusercontent.com/eesuhn/eesuhn-sdk/refs/heads/main/LICENSE) file for details.
