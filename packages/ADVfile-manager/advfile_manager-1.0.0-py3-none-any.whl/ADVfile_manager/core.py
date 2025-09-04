"""
Unified File Abstractions with Backups, Context Manager, and Exit Cleanup
========================================================================

Overview
--------
This module provides a small set of classes for common file formats with a unified
API: `TextFile`, `JsonFile`, `CsvFile`, and `YamlFile` (requires PyYAML).
Each class inherits from the base `File` and supports:

- `read()` / `write()` / `append()`
- In-memory caching (`clear_cache()`)
- Size lookup (`get_size()`, `get_size_human()`)
- On-disk backups (`backup()`, `restore()`, `clear_backups()`, `list_backups()`)
- A safe editing *context manager* (`with ... as f:`) that:
  - Optionally creates a backup on enter (default: `keep_backup=True`)
  - Automatically restores from backup if an exception occurs
  - Clears the in-memory cache on exit

Backups & Keep/Discard Behavior
-------------------------------
- `File.__call__(keep_backup: bool)` configures how backups behave for the instance:

      with TextFile("file.txt", "dir")(keep_backup=False) as f:
          ...

  - `keep_backup=True` (default): a backup is created on `__enter__`. On error, `restore()`
    is called during `__exit__`. Backups are **kept** after the context ends.
  - `keep_backup=False`: backups for this file are considered *ephemeral*. They are
    **registered** for removal at interpreter exit (via the atexit hook). You can also
    trigger cleanup manually via `cleanup_backups_for_all()`.

  You can set an optional backup retention per instance with `max_backups` (keep only the
  most recent N backups). If `None`, retention is unlimited.

Module-Level Exit Cleanup
-------------------------
- The module registers a **silent** `atexit` handler that will remove backups for any file
  marked with `keep_backup=False` via `__call__`.
- You can control this behavior:

      set_exit_cleanup(True)   # enable automatic cleanup at interpreter exit (default)
      set_exit_cleanup(False)  # disable it

- You can also trigger cleanup manually at any time:

      removed = cleanup_backups_for_all()
      # 'removed' is the total number of backup files deleted

Notes
-----
- `clear_cache()` only affects the in-memory representation; it does NOT touch the on-disk file.
  The next `read()` reloads content from disk.
- `YamlFile` requires `pyyaml` (`pip install pyyaml`).
- `CsvFile` uses `csv.DictReader`/`DictWriter`; all rows are dicts.
- `JsonFile` supports both dict and list roots. `append()` updates dict keys or appends to/extends a list.
  `get_item()` accepts int (1-based index for list) or key (for dict); `items()` iterates `(index, value)` or `(key, value)`.

Quick Examples
--------------
Text:
    t = TextFile("notes.txt", "work")
    t.write("first line")
    t.append("second line")
    print(t.read_line(2))      # "second line"
    for n, line in t.lines():
        print(n, line)

JSON:
    j = JsonFile("data.json", "work")
    j.write({"users": [{"id": 1}]})
    j.append({"active": True})
    print(j.get_item("active"))  # True
    for k, v in j.items():
        print(k, v)

Context manager with safety:
    with TextFile("draft.txt", "work") as f:
        f.append("safe edit")
        # if an exception occurs here, restore() runs automatically

Ephemeral backups:
    with TextFile("temp.txt", "work")(keep_backup=False) as f:
        f.write("temporary content")
    # backups for this file can be removed automatically at interpreter exit

Exit cleanup controls:
    set_exit_cleanup(True)    # default
    removed = cleanup_backups_for_all()
"""

from __future__ import annotations

import itertools
import os
import csv
import json
import shutil
import glob
import datetime
import atexit
import weakref
from pathlib import Path
from typing import Any, Dict, List, Iterable, Optional, Generator, Tuple, Union

try:
    import yaml  # Requires: pip install pyyaml
except Exception:
    yaml = None

# -----------------------------------------------------------------------------
# Module-level control for atexit cleanup of ephemeral backups
# -----------------------------------------------------------------------------

_exit_cleanup_enabled: bool = True
# Track files that requested keep_backup=False (weak refs to avoid leaks)
_files_to_clear_on_exit: "weakref.WeakSet" = weakref.WeakSet()


def set_exit_cleanup(enabled: bool) -> None:
    """
    Enable or disable automatic backup cleanup at interpreter exit.

    Parameters
    ----------
    enabled : bool
        True to enable (default), False to disable.
    """
    global _exit_cleanup_enabled
    _exit_cleanup_enabled = enabled


def cleanup_backups_for_all() -> int:
    """
    Manually clear backups for all registered files (those with keep_backup=False).

    Returns
    -------
    int
        Total number of backup files removed across all registered files.
    """
    total = 0
    # Copy items to a list to avoid iteration invalidation as WeakSet mutates
    for f in list(_files_to_clear_on_exit):
        try:
            total += f.clear_backups()
        except Exception:
            # Intentionally silent: let caller handle errors if needed
            pass
    return total


def _clear_backups_on_exit() -> None:
    if not _exit_cleanup_enabled:
        return
    cleanup_backups_for_all()


# Register the exit handler once, at import time (no output, silent)
atexit.register(_clear_backups_on_exit)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _as_str_path(p: Optional[Union[str, Path]]) -> str:
    return os.fspath(p) if p is not None else os.getcwd()


def _atomic_write_text(path: str, data: str, *, encoding: str = "utf-8") -> None:
    """
    Atomically write text to 'path' using a temporary file and os.replace().
    """
    tmp = f"{path}.tmp"
    with open(tmp, "wt", encoding=encoding, newline="") as f:
        f.write(data)
    os.replace(tmp, path)


# -----------------------------------------------------------------------------
# Base class
# -----------------------------------------------------------------------------

class File:
    """
    Abstract base class for file handling.

    Provides a unified interface for different file formats
    and common operations like reading, writing, and appending.
    """

    def __init__(
        self,
        file_name: str,
        file_path: Optional[Union[str, Path]] = None,
        keep_backup: bool = True,
        max_backups: Optional[int] = None,
    ):
        """
        Initialize a File object.

        Parameters
        ----------
        file_name : str
            The name of the file.
        file_path : Optional[str | pathlib.Path], default=None
            The directory path where the file resides. If None, uses the current
            working directory.
        keep_backup : bool, default=True
            If False, backups for this instance are considered ephemeral and will be
            registered for automatic cleanup at interpreter exit.
        max_backups : Optional[int], default=None
            If set, keep at most this many backups per file (oldest are deleted
            after creating a new backup). If None, retention is unlimited.
        """
        self.name = file_name
        self.path = _as_str_path(file_path)
        self.full_path = os.path.join(self.path, file_name)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.status = os.path.exists(self.full_path)
        self.content: Any = None
        self.__keep_backup = keep_backup
        self.max_backups: Optional[int] = max_backups

        if not keep_backup:
            _files_to_clear_on_exit.add(self)  # weak reference

    def __call__(self, keep_backup: bool = True):
        """
        Configure keep_backup for context-manager and exit cleanup.

        If keep_backup=False, this file instance will be registered for automatic
        backup cleanup at interpreter exit.

        Returns
        -------
        File
            Self (enables usage like: with File(...)(keep_backup=False) as f:)
        """
        self.__keep_backup = keep_backup
        if not keep_backup:
            _files_to_clear_on_exit.add(self)  # weak reference
        return self

    # --- Context Manager ---
    def __enter__(self):
        """
        Enter context manager.

        Returns
        -------
        File
            The file instance itself.

        Notes
        -----
        If keep_backup=True (default), a backup will be created automatically.
        """
        if self.__keep_backup:
            try:
                self.backup()
            except FileNotFoundError:
                # No file yet — nothing to back up
                pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager.

        Notes
        -----
        - Always clears the in-memory cache.
        - If an exception occurred and keep_backup=True, the file is restored
          from the last backup.
        - If keep_backup=False, backups are left for the atexit handler (or
          can be cleaned by calling cleanup_backups_for_all()).
        """
        if exc_type is not None and self.__keep_backup:
            try:
                self.restore()
            except FileNotFoundError:
                # No backup to restore from
                pass
        self.clear_cache()

    # --- Abstract interface ---
    def read(self) -> Any:
        """Read file content."""
        raise NotImplementedError

    def write(self, data: Any):
        """Write data to file, overwriting existing content."""
        raise NotImplementedError

    def append(self, data: Any):
        """Append data to the file."""
        raise NotImplementedError

    # --- Utilities ---
    def clear_cache(self):
        """
        Clear the in-memory cache of the file content.

        Notes
        -----
        This does not affect the file on disk.
        The next call to `read()` will reload the content from the file.
        """
        self.content = None

    def list_backups(self) -> List[str]:
        """
        List all backup file paths for this file, sorted by creation time ascending.

        Returns
        -------
        List[str]
            List of backup file paths.
        """
        backup_dir = os.path.join(self.path, "backups")
        pattern = os.path.join(backup_dir, f"{self.name}.*.bak")
        backups = glob.glob(pattern)
        backups.sort(key=lambda p: os.path.getmtime(p))
        return backups

    def clear_backups(self) -> int:
        """
        Remove all backups related to this file.

        Returns
        -------
        int
            Number of backup files deleted.
        """
        count = 0
        for b in self.list_backups():
            try:
                os.remove(b)
                count += 1
            except FileNotFoundError:
                pass
        return count

    def get_size(self) -> int:
        """
        Get the size of the file in bytes.

        Returns
        -------
        int
            The file size in bytes. Returns 0 if the file does not exist.
        """
        if os.path.exists(self.full_path):
            return os.path.getsize(self.full_path)
        return 0

    def get_size_human(self) -> str:
        """
        Get the file size in a human-readable format (e.g., '12.3 KB').

        Returns
        -------
        str
            Human-readable size string.
        """
        size = self.get_size()
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024 or unit == "TB":
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return "0 B"

    def backup(self) -> str:
        """
        Create a backup of the file inside a 'backups' folder under the same base path.

        Returns
        -------
        str
            The full path of the created backup file.

        Raises
        ------
        FileNotFoundError
            If the file does not exist yet.
        """
        if not os.path.exists(self.full_path):
            raise FileNotFoundError(f"File does not exist: {self.full_path}")

        backup_dir = os.path.join(self.path, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # Use microseconds to avoid collisions
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_name = f"{self.name}.{timestamp}.bak"
        backup_path = os.path.join(backup_dir, backup_name)

        shutil.copy2(self.full_path, backup_path)

        # Enforce retention if configured
        if isinstance(self.max_backups, int) and self.max_backups >= 0:
            backups = self.list_backups()
            # delete oldest if exceeding limit
            excess = max(0, len(backups) - self.max_backups)
            for old in backups[:excess]:
                try:
                    os.remove(old)
                except FileNotFoundError:
                    pass

        return backup_path

    def restore(self, backup_path: Optional[Union[str, Path]] = None) -> str:
        """
        Restore a backup into the original file path.

        Parameters
        ----------
        backup_path : Optional[str | pathlib.Path], default=None
            If provided, restore from this specific backup path; otherwise restore
            from the most recent backup.

        Returns
        -------
        str
            The full path of the restored file.

        Raises
        ------
        FileNotFoundError
            If no backups are found (or the specific backup_path is invalid).
        """
        if backup_path is None:
            backups = self.list_backups()
            if not backups:
                raise FileNotFoundError(f"No backups found for {self.name} in {os.path.join(self.path, 'backups')}")
            src = backups[-1]  # latest
        else:
            src = os.fspath(backup_path)
            if not os.path.exists(src):
                raise FileNotFoundError(f"Backup not found: {src}")

        shutil.copy2(src, self.full_path)
        self.status = True
        self.content = None  # force reload on next read
        return self.full_path


# -----------------------------------------------------------------------------
# Text files
# -----------------------------------------------------------------------------

class TextFile(File):
    """
    Handler for plain text files (.txt).
    Supports reading, writing, appending, and line-based operations.
    """

    def __init__(self, file_name: str, file_path: Optional[Union[str, Path]] = None, **kwargs):
        super().__init__(file_name, file_path, **kwargs)
        if self.status:
            self.read()

    def write(self, data: str):
        """
        Write text to the file, overwriting existing content (atomic).

        Parameters
        ----------
        data : str
            The string to write.
        """
        _atomic_write_text(self.full_path, data, encoding="utf-8")
        self.content = data
        self.status = True

    def read(self) -> str:
        """
        Read the full file content.

        Returns
        -------
        str
            The file content.
        """
        if self.content is None:
            with open(self.full_path, "rt", encoding="utf-8") as f:
                self.content = f.read()
        return self.content

    def append(self, data: str):
        """
        Append text to the file.

        Parameters
        ----------
        data : str
            Text to append.
        """
        # Efficient append (non-atomic); for atomic append, read+rewrite via _atomic_write_text
        with open(self.full_path, "at", encoding="utf-8") as f:
            if self.status and os.path.getsize(self.full_path) > 0:
                f.write("\n" + data)
            else:
                f.write(data)
        self.content = (self.content + "\n" + data) if self.content else data
        self.status = True

    def lines(self) -> Generator[Tuple[int, str], None, None]:
        """
        Yield lines from the file as (line_number, line_text).

        Yields
        ------
        tuple
            A tuple (line_number, line_text).
        """
        with open(self.full_path, "rt", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                yield i, line.rstrip("\n")

    def read_line(self, line_number: int) -> str:
        """
        Read a specific line by its number.

        Parameters
        ----------
        line_number : int
            The 1-based index of the line to read.

        Returns
        -------
        str
            The line content.

        Raises
        ------
        IndexError
            If the line number does not exist.
        """
        with open(self.full_path, "rt", encoding="utf-8") as f:
            line = next(itertools.islice(f, line_number - 1, line_number), None)
            if line is None:
                raise IndexError(f"Line {line_number} does not exist in {self.full_path}")
            return line.rstrip("\n")


# -----------------------------------------------------------------------------
# JSON files
# -----------------------------------------------------------------------------

class JsonFile(File):
    """
    Handler for JSON files (.json).
    Supports dict and list root objects, with read, write, append,
    and indexed/key-based item access.
    """

    def __init__(self, file_name: str, file_path: Optional[Union[str, Path]] = None, *, indent: int = 2, **kwargs):
        super().__init__(file_name, file_path, **kwargs)
        self.indent = indent
        if self.status:
            self.read()

    def write(self, data: Any):
        """Write dict or list as formatted JSON (atomic)."""
        tmp = f"{self.full_path}.tmp"
        with open(tmp, "wt", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=self.indent)
        os.replace(tmp, self.full_path)
        self.content = data
        self.status = True

    def read(self) -> Any:
        """Read JSON content into a Python dict or list."""
        if self.content is None:
            with open(self.full_path, "rt", encoding="utf-8") as f:
                self.content = json.load(f)
        return self.content

    def append(self, data: Any):
        """
        Append data to JSON.

        Behavior:
        - If root is a list: appends an element or extends with iterable.
        - If root is a dict: updates keys.
        """
        if not self.status:
            self.write(data)
            return

        current = self.read()
        if isinstance(current, list):
            if isinstance(data, Iterable) and not isinstance(data, (str, bytes, dict)):
                current.extend(list(data))
            else:
                current.append(data)
        elif isinstance(current, dict):
            if not isinstance(data, dict):
                raise TypeError("append on dict-backed JSON expects dict")
            current.update(data)
        else:
            raise TypeError("JSON root must be list or dict to support append")

        self.write(current)

    def get_item(self, index_or_key: Any) -> Any:
        """
        Retrieve an element from the JSON content.

        Parameters
        ----------
        index_or_key : int | str
            If list-backed: 1-based index.
            If dict-backed: a key.

        Returns
        -------
        Any
            The requested element.

        Raises
        ------
        IndexError
            For out-of-range list index.
        KeyError
            If dict key is not found.
        """
        data = self.read()
        if isinstance(data, list):
            if not isinstance(index_or_key, int):
                raise TypeError("For list-backed JSON, provide a 1-based integer index")
            if index_or_key < 1:
                raise ValueError("Index must be >= 1")
            idx = index_or_key - 1
            if idx >= len(data):
                raise IndexError(f"Index {index_or_key} out of range")
            return data[idx]
        elif isinstance(data, dict):
            if index_or_key not in data:
                raise KeyError(f"Key {index_or_key!r} not found")
            return data[index_or_key]
        else:
            raise TypeError("JSON root must be list or dict")

    def items(self) -> Iterable:
        """
        Iterate through JSON items.

        Yields
        ------
        tuple
            - list-backed: (index (1-based), item)
            - dict-backed: (key, value)
        """
        data = self.read()
        if isinstance(data, list):
            for i, item in enumerate(data, start=1):
                yield i, item
        elif isinstance(data, dict):
            for k, v in data.items():
                yield k, v
        else:
            raise TypeError("JSON root must be list or dict")


# -----------------------------------------------------------------------------
# CSV files
# -----------------------------------------------------------------------------

class CsvFile(File):
    """
    Handler for CSV files (.csv).
    Uses DictReader/DictWriter for reading and writing.
    """

    def __init__(self, file_name: str, file_path: Optional[Union[str, Path]] = None, **kwargs):
        super().__init__(file_name, file_path, **kwargs)
        self._fieldnames: Optional[List[str]] = None
        if self.status:
            self.read()

    def _infer_fieldnames(self, rows: Iterable[Dict[str, Any]]) -> List[str]:
        """Infer CSV fieldnames from a list of dicts."""
        fields: List[str] = []
        seen = set()
        for row in rows:
            for k in row.keys():
                if k not in seen:
                    seen.add(k)
                    fields.append(k)
        if not fields:
            raise ValueError("Cannot infer CSV header from empty data")
        return fields

    def write(self, data: Iterable[Dict[str, Any]], fieldnames: Optional[List[str]] = None):
        """
        Write rows to CSV, overwriting existing file (atomic).

        Parameters
        ----------
        data : Iterable[Dict[str, Any]]
            Rows to write.
        fieldnames : Optional[List[str]]
            Explicit field order; if None, inferred from data.
        """
        rows = list(data)
        fns = fieldnames or self._infer_fieldnames(rows)
        tmp = f"{self.full_path}.tmp"
        with open(tmp, "wt", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fns)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k, "") for k in fns})
        os.replace(tmp, self.full_path)
        self._fieldnames = fns
        self.content = rows
        self.status = True

    def read(self) -> List[Dict[str, str]]:
        """Read CSV into a list of dicts."""
        if self.content is None:
            with open(self.full_path, "rt", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                self._fieldnames = reader.fieldnames or []
                self.content = list(reader)
        return self.content

    def append(self, data: Any):
        """
        Append row(s) to CSV.

        Parameters
        ----------
        data : dict | iterable of dict
            Row(s) to append.

        Raises
        ------
        TypeError
            If data is not dict or iterable of dicts.
        """
        if isinstance(data, dict):
            rows = [data]
        elif isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
            rows = list(data)
            if rows and not isinstance(rows[0], dict):
                raise TypeError("append expects dict or iterable of dicts")
        else:
            raise TypeError("append expects dict or iterable of dicts")

        file_exists = self.status and os.path.exists(self.full_path) and os.path.getsize(self.full_path) > 0

        if file_exists and self._fieldnames:
            fns = self._fieldnames
        else:
            fns = self._infer_fieldnames(rows)

        with open(self.full_path, "at", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fns)
            if not file_exists:
                writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k, "") for k in fns})

        if self.content is None:
            self.content = []
        self.content.extend([{k: str(r.get(k, "")) for k in fns} for r in rows])
        self._fieldnames = fns
        self.status = True

    def read_row(self, row_number: int) -> Dict[str, str]:
        """
        Read a specific row by index.

        Parameters
        ----------
        row_number : int
            1-based row index.

        Returns
        -------
        dict
            The row data.

        Raises
        ------
        IndexError
            If row_number does not exist.
        """
        with open(self.full_path, "rt", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                if i == row_number:
                    return row
        raise IndexError(f"Row {row_number} does not exist in {self.full_path}")

    def rows(self) -> Generator[Tuple[int, Dict[str, str]], None, None]:
        """
        Generator yielding rows.

        Yields
        ------
        tuple
            (row_number, row_dict)
        """
        with open(self.full_path, "rt", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                yield i, row


# -----------------------------------------------------------------------------
# YAML files
# -----------------------------------------------------------------------------

class YamlFile(File):
    """
    Handler for YAML files (.yaml/.yml).
    Requires PyYAML to be installed.
    """

    def __init__(self, file_name: str, file_path: Optional[Union[str, Path]] = None, *, sort_keys: bool = False, **kwargs):
        super().__init__(file_name, file_path, **kwargs)
        if yaml is None:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")
        self.sort_keys = sort_keys
        if self.status:
            self.read()

    def write(self, data: Any):
        """Write Python object as YAML (atomic)."""
        tmp = f"{self.full_path}.tmp"
        with open(tmp, "wt", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=self.sort_keys, allow_unicode=True)
        os.replace(tmp, self.full_path)
        self.content = data
        self.status = True

    def read(self) -> Any:
        """Read YAML into Python object."""
        if self.content is None:
            with open(self.full_path, "rt", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
            self.content = loaded if loaded is not None else {}
        return self.content

    def append(self, data: Any):
        """
        Append data to YAML.

        Behavior:
        - If root is list: append or extend.
        - If root is dict: update keys.

        Raises
        ------
        TypeError
            If root is not list or dict.
        """
        if not self.status:
            self.write(data)
            return
        current = self.read()
        if isinstance(current, list):
            if isinstance(data, Iterable) and not isinstance(data, (str, bytes, dict)):
                current.extend(list(data))
            else:
                current.append(data)
        elif isinstance(current, dict):
            if not isinstance(data, dict):
                raise TypeError("append on dict-backed YAML expects dict")
            current.update(data)
        else:
            raise TypeError("YAML root must be list or dict to support append")
        self.write(current)

    def get_item(self, index_or_key: Any) -> Any:
        """
        Retrieve an element from the YAML content.

        Parameters
        ----------
        index_or_key : int | str
            If list-backed: 1-based index.
            If dict-backed: a key.

        Returns
        -------
        Any
            The requested element.
        """
        data = self.read()
        if isinstance(data, list):
            if not isinstance(index_or_key, int):
                raise TypeError("For list-backed YAML, provide a 1-based integer index")
            if index_or_key < 1:
                raise ValueError("Index must be >= 1")
            idx = index_or_key - 1
            if idx >= len(data):
                raise IndexError(f"Index {index_or_key} out of range")
            return data[idx]
        elif isinstance(data, dict):
            if index_or_key not in data:
                raise KeyError(f"Key {index_or_key!r} not found")
            return data[index_or_key]
        else:
            raise TypeError("YAML root must be list or dict")

    def items(self) -> Iterable:
        """
        Iterate through YAML items.

        Yields
        ------
        tuple
            - list-backed: (index (1-based), item)
            - dict-backed: (key, value)
        """
        data = self.read()
        if isinstance(data, list):
            for i, item in enumerate(data, start=1):
                yield i, item
        elif isinstance(data, dict):
            for k, v in data.items():
                yield k, v
        else:
            raise TypeError("YAML root must be list or dict to iterate")


# -----------------------------------------------------------------------------
# Demo
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    base_path = "example_data"

    # --- TextFile ---
    print("\n\033[94m--- TextFile Example ---\033[0m")
    txt = TextFile("example.txt", base_path)
    txt.write("Hello world")
    print(txt.read())
    print("Size (bytes):", txt.get_size(), "| human:", txt.get_size_human())

    txt.append("Second line")
    print(txt.read())
    print("Line 2:", txt.read_line(2))
    for num, line in txt.lines():
        print(f"Line {num}: {line}")

    # Show cache behavior
    txt.content = "IN-MEMORY OVERRIDE"
    print("From cache:", txt.read())
    txt.clear_cache()
    print("After clear_cache():", txt.read())

    # Manual backup & restore
    print("\n\033[96mCreating manual backup...\033[0m")
    bpath = txt.backup()
    print("Backup path:", bpath)
    txt.write("Changed content after backup")
    print("Changed file:", txt.read())
    print("Restoring latest backup...")
    txt.restore()
    print("After restore:", txt.read())

    # --- JsonFile (dict root) ---
    print("\n\033[94m--- JsonFile Example (\033[92mdict root\033[94m) ---\033[0m")
    j = JsonFile("data.json", base_path)
    j.write({"users": [{"id": 1}, {"id": 2}]})
    j.append({"active": True})
    print(j.read())
    print("Users:", j.get_item("users"))
    for k, v in j.items():
        print(f"{k}: {v}")

    # --- JsonFile (list root) ---
    print("\n\033[94m--- JsonFile Example (\033[92mlist root\033[94m) ---\033[0m")
    jl = JsonFile("list.json", base_path)
    jl.write([{"id": 1}])
    jl.append({"id": 2})
    jl.append([{"id": 3}, {"id": 4}])
    print(jl.read())
    print("Index 2:", jl.get_item(2))
    for i, item in jl.items():
        print(f"Index {i}: {item}")

    # --- CsvFile ---
    print("\n\033[94m--- CsvFile Example ---\033[0m")
    c = CsvFile("table.csv", base_path)
    c.write([{"name": "Avi", "age": 30}, {"name": "Dana", "age": 25}], fieldnames=["name", "age"])
    c.append({"name": "Noa", "age": 21})
    c.append([{"name": "Lior", "age": 28}, {"name": "Omri", "age": 33}])
    print(c.read())
    print("Row 2:", c.read_row(2))
    for i, row in c.rows():
        print(f"Row {i}: {row}")

    # --- YamlFile (dict root) ---
    print("\n\033[94m--- YamlFile Example (\033[92mdict root\033[94m) ---\033[0m")
    y = YamlFile("config.yaml", base_path)
    y.write({"app": {"name": "demo"}, "features": ["a"]})
    y.append({"features": ["b"]})
    print(y.read())
    print("App:", y.get_item("app"))
    for k, v in y.items():
        print(f"{k}: {v}")

    # --- YamlFile (list root) ---
    print("\n\033[94m--- YamlFile Example (\033[92mlist root\033[94m) ---\033[0m")
    yl = YamlFile("list.yaml", base_path)
    yl.write([{"task": "one"}, {"task": "two"}])
    yl.append({"task": "three"})
    print(yl.read())
    print("Index 2:", yl.get_item(2))
    for i, item in yl.items():
        print(f"Index {i}: {item}")

    # --- Backups management demo ---
    print("\n\033[94m--- Backups Management Demo ---\033[0m")
    # Create a few backups quickly (microsecond-res timestamps)
    txt.write("v1"); bp1 = txt.backup()
    txt.write("v2"); bp2 = txt.backup()
    txt.write("v3"); bp3 = txt.backup()
    print("Backups list:", txt.list_backups())
    print("Restoring specific backup:", bp2)
    txt.restore(bp2)
    print("After restore specific:", txt.read())

    # Demonstrate retention: keep only 2 backups
    txt.max_backups = 2
    txt.write("v4"); txt.backup()
    txt.write("v5"); txt.backup()
    print("After retention (max_backups=2), backups:", txt.list_backups())

    # --- Context manager (keep_backup=True, default) ---
    print("\n\033[94m--- Context Manager (keep_backup=True) ---\033[0m")
    with TextFile("cm_true.txt", base_path) as f:
        # Backup will be created on enter. If an exception occurs, restore() will run.
        f.write("Safe transactional edit")
        print("Inside context:", f.read())
    print("After context:", TextFile("cm_true.txt", base_path).read())

    # --- Context manager (keep_backup=False) + atexit registration ---
    print("\n\033[94m--- Context Manager (keep_backup=False) + exit cleanup ---\033[0m")
    with TextFile("cm_false.txt", base_path)(keep_backup=False) as f:
        f.write("Temporary content")
        print("Inside context:", f.read())
        # Backups for this file are ephemeral and will be cleaned at interpreter exit.

    # Explicitly register another file for exit cleanup without using context
    temp_file = TextFile("temp_noctx.txt", base_path, keep_backup=False)
    temp_file.write("Ephemeral content")
    temp_file.backup()  # ensure there's something to clean

    # --- Global exit cleanup controls ---
    print("\n\033[94m--- Exit Cleanup Controls ---\033[0m")
    print("Manually cleaning backups via cleanup_backups_for_all()...")
    removed_total = cleanup_backups_for_all()
    print(f"Backups removed across all registered files: {removed_total}")

    # --- Cleanup prompt for example_data ---
    print("\n\033[93mDo you want to delete the 'example_data' folder and all generated files? (y/n)\033[0m")
    choice = input("> ").strip().lower()
    if choice == "y":
        if os.path.exists(base_path):
            shutil.rmtree(base_path)
            print(f"\033[92mDeleted folder: {base_path}\033[0m")
        else:
            print(f"\033[91mFolder not found: {base_path}\033[0m")
    else:
        print("\033[93mFiles kept.\033[0m")
