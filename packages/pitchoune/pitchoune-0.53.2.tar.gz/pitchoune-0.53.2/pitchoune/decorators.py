import functools
import inspect
import json
from pathlib import Path
from typing import Any, Iterable
import csv

from pitchoune.utils import (
    enrich_path,
    load_from_conf,
    open_file,
    check_duplicates,
    watch_file
)
from pitchoune import (
    base_io_factory,
    base_chat_factory
)


class StreamFormatNotSupported(Exception):
    """Raised when the file format is not supported for streaming."""
    pass

class RequirementsNotSatisfied(Exception):
    """Raised when one or more required conditions are not met."""
    pass


def input_df(filepath: Path|str, id_cols: Iterable[str] = None, schema = None, **params):
    """Decorator for reading a dataframe from a file"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_filepath = Path(filepath)
            df = base_io_factory.create(suffix=new_filepath.suffix[1:]).deserialize(new_filepath, schema, **params)
            if id_cols:
                check_duplicates(df, *id_cols)  # Check for duplicates in the specified columns
            new_args = args + (df,)
            return func(*new_args, **kwargs)
        return wrapper
    return decorator


def output_df(filepath: Path|str, human_check: bool=False, **params):
    """Decorator for writing a dataframe to a file"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_filepath = Path(filepath)
            df = func(*args, **kwargs)
            base_io_factory.create(suffix=new_filepath.suffix[1:]).serialize(df, new_filepath, **params)
            if human_check:
                open_file(new_filepath)  # Open the file for modification
                watch_file(new_filepath)  # Wait for the file to be modified
            return df
        return wrapper
    return decorator


def output_dfs(*outputs: dict[str, Any]):
    """
        Decorator for writing multiple dataframes to multiple files with individual parameters.
        
        Each argument should be a dict containing:
        - 'filepath': Path or str
        - Optional: 'human_check': bool
        - Optional: any other serialization params
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            dfs = func(*args, **kwargs)
            if not isinstance(dfs, (list, tuple)):
                raise TypeError("Function must return a list or tuple of DataFrames")
            if len(dfs) != len(outputs):
                raise ValueError("Number of outputs must match number of returned DataFrames")
            for df, output_params in zip(dfs, outputs):
                if df is None:
                    continue  # ou raise ValueError("Returned DataFrame is None")
                
                filepath = output_params.get("filepath")
                if not filepath:
                    raise ValueError("Missing 'filepath' in output parameters")

                new_filepath = Path(filepath)

                human_check = output_params.pop("human_check", False)
                suffix = new_filepath.suffix[1:]
                base_io_factory.create(suffix=suffix).serialize(df, new_filepath, **output_params)

                if human_check:
                    open_file(new_filepath)
                    watch_file(new_filepath)
            return dfs
        return wrapper
    return decorator


def read_stream_(filepath: Path | str, recover_progress_filepath: Path | str = None):
    """
    Decorator that streams a .jsonl or .csv file line by line and injects the parsed data into the function.

    Injected kwargs:
        - current_line: line number (starting at 1)
        - total_lines: total number of lines in the file
        - parsed data: dict from JSONL or CSV row
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_filepath = Path(filepath)

            # Count total lines
            with open(new_filepath, "r", encoding="utf-8") as f:
                total_lines = sum(1 for _ in f)

            # Determine how many lines to skip (recover progress)
            already_done = 0
            if recover_progress_filepath:
                try:
                    with open(recover_progress_filepath, "r", encoding="utf-8") as f:
                        already_done = sum(1 for _ in f) - 1  # Ignore header if CSV
                        already_done = max(already_done, 0)
                except FileNotFoundError:
                    already_done = 0

            def process_line(data: dict, current_line: int):
                injected_kwargs = dict(kwargs)
                injected_kwargs.update(data)
                sig = inspect.signature(func).parameters
                if "current_line" in sig:
                    injected_kwargs["current_line"] = current_line
                if "total_lines" in sig:
                    injected_kwargs["total_lines"] = total_lines
                func(*args, **injected_kwargs)

            suffix = new_filepath.suffix.lower()
            with open(new_filepath, "r", encoding="utf-8") as f:
                if suffix == ".jsonl":
                    for current_line, line in enumerate(f, start=1):
                        if current_line <= already_done:
                            continue
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        process_line(data, current_line)

                elif suffix == ".csv":
                    reader = csv.DictReader(f)
                    for current_line, row in enumerate(reader, start=1):
                        if current_line <= already_done:
                            continue
                        process_line(row, current_line)

                else:
                    raise StreamFormatNotSupported(f"Unsupported file format: {suffix}")
        return wrapper
    return decorator


def read_stream(filepath: Path|str, recover_progress_from: Path|str=None):
    """Decorator that reads a JSONL file line by line and injects the data into the function"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_filepath = Path(filepath)
            already_done = 0
            with open(new_filepath, "r", encoding="utf-8") as f:  # Compute the total number of lines
                total_lines = sum(1 for _ in f)
            if recover_progress_from:
                try:
                    with open(recover_progress_from, "r", encoding="utf-8") as f:
                        already_done = sum(1 for _ in f)
                except FileNotFoundError:
                    already_done = 0
            with open(new_filepath, "r", encoding="utf-8") as f:  # Reading and processing the JSONL file
                for current_line, line in enumerate(f, start=1):
                    if already_done > 0:
                        if current_line <= already_done:
                            continue  # Skip lines until we reach the desired start line
                    if new_filepath.suffix == ".jsonl":
                        data = json.loads(line)  # Cast the line to a dictionary
                        kwargs |= data
                        if "total_lines" in inspect.signature(func).parameters:
                            kwargs["total_lines"] = total_lines
                        if "current_line" in inspect.signature(func).parameters:
                            kwargs["current_line"] = current_line
                        func(*args, **kwargs)
                    else:
                        raise Exception("File can't be streamed")
        return wrapper
    return decorator


def write_stream_(filepath: Path | str):
    """
        Decorator that writes the returned dictionary to a .jsonl or .csv file line by line.
        The decorated function must return a dictionary.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_filepath = Path(filepath)

            data = func(*args, **kwargs)
            if data is None:
                return None

            def write_line(entry: dict):
                if not isinstance(entry, dict):
                    raise ValueError("La fonction décorée doit retourner un dictionnaire.")

                if new_filepath.suffix == ".jsonl":
                    with open(new_filepath, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

                elif new_filepath.suffix == ".csv":
                    file_exists = new_filepath.exists()
                    with open(new_filepath, "a", encoding="utf-8", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=entry.keys())
                        if not file_exists:
                            writer.writeheader()
                        writer.writerow(entry)
                else:
                    raise Exception("Unsupported file format for streaming")

            write_line(data)
            return data
        return wrapper
    return decorator


def write_stream(filepath: Path|str):
    """Decorator that writes a dictionary to a JSONL file line by line"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_filepath = Path(filepath)

            data = func(*args, **kwargs)  # Calling the decorated function
            if data is None:
                return data
            if isinstance(data, dict):  # Check if the returned value is a dictionary
                with open(new_filepath, "a", encoding="utf-8") as f:
                    if new_filepath.suffix == ".jsonl":
                        f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    else:
                        raise Exception("File can't receive stream")
            else:
                raise ValueError("La fonction décorée doit retourner un dictionnaire.")
            return data
        return wrapper
    return decorator


def use_chat(
    name: str,
    model: str,
    prompt_filepath: str=None,
    prompt: str=None,
    local: bool=True,
    temperature: float=.5,
    max_tokens: int=4096,
    top_p: float=.9
):
    """Decorator for injecting a chat instance into a function"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_prompt_filepath = Path(prompt_filepath)
            new_prompt = prompt  # Get the prompt from the decorator
            if new_prompt is None:
                with open(new_prompt_filepath, "r") as f:
                    new_prompt = f.read()
            kwargs[name] = base_chat_factory.create(
                name=name,
                model=model,
                prompt=new_prompt,
                local=local,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p
            )  # Get the chat instance
            return func(*args, **kwargs)  # Injection of the chat instance into the function
        return wrapper
    return decorator


def requested(*checks: str):
    """
    Decorator to validate paths or config keys before executing the function.

    Accepted prefixes:
        - "path:"       → must be an existing file or directory
        - "conf_path:"  → config key whose value is a path that must exist
        - "conf:"       → config key must exist and be non-empty
        - "conf_int:"   → config key must be an integer
        - "conf_float:" → config key must be a float
        - "conf_list:"  → config key must be a comma-separated list

    Example:
        @requested("path:/some/file", "conf:API_KEY", "conf_int:MAX_RETRIES")
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for check in checks:
                if ":" not in check:
                    raise RequirementsNotSatisfied(f"Invalid check format: '{check}' (missing prefix)")

                prefix, key = check.split(":", 1)

                # For config keys, retrieve raw value
                value = load_from_conf(key) if prefix.startswith("conf") else key

                # Enrich only if it's a path
                if prefix in ("path", "conf_path"):
                    enriched = enrich_path(value)
                    if not enriched or not Path(enriched).exists():
                        raise RequirementsNotSatisfied(f"Missing file or directory at: {enriched} (check: {check})")

                elif prefix == "conf":
                    if value in [None, "", []]:
                        raise RequirementsNotSatisfied(f"Missing or empty config value for: {key}")

                elif prefix == "conf_int":
                    try:
                        if int(value) != float(value):  # avoid floats like "3.0"
                            raise ValueError
                    except (TypeError, ValueError):
                        raise RequirementsNotSatisfied(f"Config value for '{key}' is not a valid integer: {value}")

                elif prefix == "conf_float":
                    try:
                        float(value)
                    except (TypeError, ValueError):
                        raise RequirementsNotSatisfied(f"Config value for '{key}' is not a valid float: {value}")

                elif prefix == "conf_list":
                    if not isinstance(value, str) or not value.strip():
                        raise RequirementsNotSatisfied(f"Config value for '{key}' is not a valid list string")
                    items = [item.strip() for item in value.split(",") if item.strip()]
                    if not items:
                        raise RequirementsNotSatisfied(f"Config list for '{key}' is empty or malformed")

                else:
                    raise RequirementsNotSatisfied(f"Unknown check prefix: '{prefix}' in '{check}'")

            return func(*args, **kwargs)
        return wrapper
    return decorator


def input_conf_param(
    key: str
):
    """Decorator for injecting a chat instance into a function"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if ":" not in key:
                prefix = "str"
            else:
                prefix, key = key.split(":", 1)

            # For config keys, retrieve raw value
            value = load_from_conf(key)
        
            if prefix == "path":
                value = enrich_path(value)

            elif prefix == "str":
                pass

            elif prefix == "conf_int":
                value = int(value)

            elif prefix == "conf_float":
                value = float(value)

            elif prefix == "conf_list":
                value = [v for v in value.split(",") if v]

            else:
                raise Exception("Invalid prefix")

            new_args = args + (value,)

            return func(*new_args, **kwargs)  # Injection of the chat instance into the function
        return wrapper
    return decorator
