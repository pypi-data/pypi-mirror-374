import json
import yaml
import orjson

from pathlib import Path
from typing import Any, Union, Dict


PathLike = Union[str, Path]

JSON_EXTENSIONS = frozenset({".json", ".ipynb"})
YAML_EXTENSIONS = frozenset({".yml", ".yaml"})

ORJSON_OPTIONS_BASE = (
    orjson.OPT_SERIALIZE_NUMPY
    | orjson.OPT_SERIALIZE_UUID
    | orjson.OPT_SERIALIZE_DATACLASS
    | orjson.OPT_NON_STR_KEYS
)
ORJSON_OPTIONS_INDENT = ORJSON_OPTIONS_BASE | orjson.OPT_INDENT_2
ORJSON_OPTIONS_SORTED = ORJSON_OPTIONS_INDENT | orjson.OPT_SORT_KEYS


class FileTypeNotSupportedError(ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _get_orjson_options(indent: bool = True, sort_keys: bool = False) -> int:
    if sort_keys:
        return ORJSON_OPTIONS_SORTED
    elif indent:
        return ORJSON_OPTIONS_INDENT
    else:
        return ORJSON_OPTIONS_BASE


def read_file(
    file_path: PathLike, *, encoding: str = "utf-8", use_orjson: bool = True
) -> Any:
    """
    Read data from a file.

    Args:
        file_path: Path to the file
        encoding: File encoding (default: utf-8)
        use_orjson: Use orjson for JSON files (faster, default: True)

    Returns:
        Parsed data from the file
    """
    with open(file_path, mode="r", encoding=encoding) as f:
        if file_path.suffix in YAML_EXTENSIONS:
            return yaml.safe_load(f)
        elif file_path.suffix in JSON_EXTENSIONS:
            if use_orjson:
                return orjson.loads(f.read())
            return json.load(f)
        else:
            return f.read()


def write_file(
    data: Any,
    file_path: PathLike,
    *,
    indent: int = 2,
    sort_keys: bool = False,
    use_orjson: bool = True,
    encoding: str = "utf-8",
    ensure_ascii: bool = False,
    atomic: bool = False,
) -> Path:
    """
    Write data to a file.

    Args:
        data: Data to write
        file_path: Path to the file
        indent: Indentation level (only 2 supported with orjson)
        sort_keys: Sort dictionary keys
        use_orjson: Use orjson for JSON files (faster, default: True)
        encoding: File encoding (default: utf-8)
        ensure_ascii: ASCII-only output (JSON only)
        atomic: Write atomically using temp file (safer for critical data)

    Returns:
        Path to the written file
    """
    if data is None:
        raise ValueError("Cannot write None to file")

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    def write_data(f):
        if file_path.suffix in YAML_EXTENSIONS:
            yaml.dump(
                data,
                f,
                sort_keys=sort_keys,
                allow_unicode=not ensure_ascii,
                default_flow_style=False,
            )
        elif file_path.suffix in JSON_EXTENSIONS:
            if use_orjson:
                options = _get_orjson_options(indent=(indent > 0), sort_keys=sort_keys)
                f.write(orjson.dumps(data, option=options).decode(encoding))
            else:
                json.dump(
                    data,
                    f,
                    indent=indent if indent > 0 else None,
                    sort_keys=sort_keys,
                    ensure_ascii=ensure_ascii,
                )
        else:
            f.write(str(data))

    if atomic:
        import tempfile

        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent, prefix=f".{file_path.stem}.", suffix=file_path.suffix
        )
        try:
            with open(temp_fd, mode="w", encoding=encoding) as f:
                write_data(f)
            Path(temp_path).replace(file_path)
        except Exception:
            Path(temp_path).unlink(missing_ok=True)
            raise
    else:
        with open(file_path, mode="w", encoding=encoding) as f:
            write_data(f)

    return file_path


def print_data(
    data: Any,
    *,
    data_type: str = "json",
    indent: int = 2,
    sort_keys: bool = False,
    use_orjson: bool = True,
    colorize: bool = False,
) -> None:
    """
    Pretty-print data in JSON or YAML format.

    Args:
        data: Data to print
        data_type: Output format ('json' or 'yaml')
        indent: Indentation level
        sort_keys: Sort dictionary keys
        use_orjson: Use orjson for JSON (faster, default: True)
        colorize: Colorize output
    """
    if data is None:
        print("null")
        return

    data_type_lower = data_type.lower()

    if data_type_lower == "json":
        if use_orjson and (indent == 0 or indent == 2):
            options = _get_orjson_options(indent=(indent > 0), sort_keys=sort_keys)
            output = orjson.dumps(data, option=options).decode()
        else:
            output = json.dumps(
                data, indent=indent if indent > 0 else None, sort_keys=sort_keys
            )
    elif data_type_lower in {"yml", "yaml"}:
        output = yaml.dump(
            data, sort_keys=sort_keys, default_flow_style=False, allow_unicode=True
        )
    else:
        raise ValueError(
            f"Unsupported data type: {data_type}. Supported: json, yaml, yml"
        )

    if colorize:
        try:
            from pygments import highlight
            from pygments.lexers import JsonLexer, YamlLexer
            from pygments.formatters import TerminalFormatter

            lexer = JsonLexer() if data_type_lower == "json" else YamlLexer()
            output = highlight(output, lexer, TerminalFormatter())
        except ImportError:
            pass

    print(output, end="" if output.endswith("\n") else "\n")


def read_files(file_paths: list[PathLike], **kwargs) -> Dict[Path, Any]:
    """
    Read multiple files and return a dict mapping paths to data.
    """
    return {Path(fp): read_file(fp, **kwargs) for fp in file_paths}


def write_files(data_map: Dict[PathLike, Any], **kwargs) -> Dict[Path, bool]:
    """
    Write multiple files and return success status for each.
    """
    results = {}
    for file_path, data in data_map.items():
        try:
            write_file(data, file_path, **kwargs)
            results[Path(file_path)] = True
        except Exception:
            results[Path(file_path)] = False
    return results
