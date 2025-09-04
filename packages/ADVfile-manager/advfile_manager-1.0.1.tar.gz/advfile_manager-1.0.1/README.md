
# ADVfile\_manager

**Author:** Avi Twil
**Repo:** [https://github.com/avitwil/ADVfile\_manager](https://github.com/avitwil/ADVfile_manager)

Unified file abstractions for Python with **safe writes, caching, backups, context managers, and exit-time cleanup** — all under a consistent API for **Text**, **JSON**, **CSV**, and **YAML** files.

* `TextFile` – read/write/append lines with `lines()` and `read_line()`.
* `JsonFile` – works with dict or list roots, `append()`, `get_item()`, `items()`.
* `CsvFile` – `DictReader`/`DictWriter` based, `read_row()`, `rows()`, column-order control.
* `YamlFile` – like `JsonFile`, requires `PyYAML`.

The base class `File` adds **backups**, **restore**, **retention**, **human-readable sizes**, **cache control**, and a **context manager** that automatically backs up and can restore on error. “Ephemeral” backups are cleaned up via a **silent atexit hook**.

---

## Table of Contents

* [Why ADVfile\_manager?](#why-advfile_manager)
* [Installation](#installation)
* [Quick Start](#quick-start)
* [Detailed Usage](#detailed-usage)

  * [Common Base: `File`](#common-base-file)
  * [`TextFile`](#textfile)
  * [`JsonFile`](#jsonfile)
  * [`CsvFile`](#csvfile)
  * [`YamlFile`](#yamlfile)
* [Backups, Retention & Exit Cleanup](#backups-retention--exit-cleanup)
* [Context Manager Safety](#context-manager-safety)
* [Advanced Notes](#advanced-notes)
* [Full Examples](#full-examples)
* [License](#license)

---

## Why ADVfile\_manager?

Typical file code ends up as a mix of ad-hoc helpers and repeated patterns.
ADVfile\_manager provides one consistent interface across common formats:

* **Safer writes**: atomic replace to avoid corrupted files.
* **Backups**: create timestamped `.bak` files, list, restore, retain N most recent.
* **Context safety**: `with` block makes a backup on enter (optional) and restores on exceptions.
* **Exit cleanup**: ephemeral backups (for temp edits) are auto-removed via atexit.
* **Streaming helpers**: iterate lines/rows/items without loading everything.
* **Cache control**: in-memory cache when convenient, `clear_cache()` when not.

---

## Installation

### From PyPI (recommended)

```bash
pip install ADVfile_manager
```

> `YamlFile` requires [PyYAML](https://pypi.org/project/PyYAML/). If your environment doesn’t bring it automatically:

```bash
pip install pyyaml
```

### From source

```bash
git clone https://github.com/avitwil/ADVfile_manager
cd ADVfile_manager
pip install -e .
```

---

# 🔎 Comparison: ADVfile\_manager vs Similar Tools

| Feature / Tool             | **ADVfile\_manager**                                           | [pathlib (stdlib)](https://docs.python.org/3/library/pathlib.html) | [os / shutil (stdlib)](https://docs.python.org/3/library/shutil.html) | [pandas](https://pandas.pydata.org/) | [ruamel.yaml](https://pypi.org/project/ruamel.yaml/) / [PyYAML](https://pyyaml.org/) |
| -------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------ |
| **Supported formats**      | TXT, JSON, CSV, YAML                                           | Works with paths only                                              | Copy/move/delete files                                                | CSV, Excel, JSON, parquet, etc.      | YAML only                                                                            |
| **Unified API**            | ✅ One interface across all formats                             | ❌                                                                  | ❌                                                                     | ❌                                    | ❌                                                                                    |
| **Read/Write/Append**      | ✅ Consistent methods (`read`, `write`, `append`)               | Manual file ops                                                    | Manual file ops                                                       | ✅ (DataFrames)                       | ✅ (YAML load/dump)                                                                   |
| **Cache system**           | ✅ In-memory cache + `clear_cache`                              | ❌                                                                  | ❌                                                                     | Internal DF cache                    | ❌                                                                                    |
| **Line/Row helpers**       | ✅ `lines()`, `read_line()`, `read_row()`, `rows()`             | ❌                                                                  | ❌                                                                     | ✅ but via DataFrame ops              | ❌                                                                                    |
| **Backup & restore**       | ✅ `backup()`, `restore()`, `list_backups()`, `clear_backups()` | ❌                                                                  | ❌                                                                     | ❌                                    | ❌                                                                                    |
| **Backup retention**       | ✅ `max_backups`                                                | ❌                                                                  | ❌                                                                     | ❌                                    | ❌                                                                                    |
| **Atomic writes**          | ✅ via `.tmp` + `os.replace()`                                  | ❌                                                                  | ❌                                                                     | ❌ (relies on storage FS)             | ❌                                                                                    |
| **Human-readable size**    | ✅ `get_size_human()`                                           | ❌                                                                  | ❌                                                                     | ❌                                    | ❌                                                                                    |
| **Context manager safety** | ✅ auto-backup + auto-restore on exception                      | ❌                                                                  | ❌                                                                     | ❌                                    | ❌                                                                                    |
| **Ephemeral backups**      | ✅ Auto-cleaned with `atexit` (if `keep_backup=False`)          | ❌                                                                  | ❌                                                                     | ❌                                    | ❌                                                                                    |
| **Exit cleanup controls**  | ✅ `set_exit_cleanup`, `cleanup_backups_for_all`                | ❌                                                                  | ❌                                                                     | ❌                                    | ❌                                                                                    |
| **Dependencies**           | Optional: `pyyaml`                                             | None                                                               | None                                                                  | Heavy (numpy, etc.)                  | Yes                                                                                  |
| **Target use case**        | General-purpose file management with safety                    | File system path manipulation                                      | File system operations                                                | Data analysis                        | YAML-specific parsing                                                                |

---

## 📌 Key Takeaways

### What ADVfile\_manager does *better*:

* 🔒 **Safety-first**: atomic writes, automatic backups, and restore-on-error context manager.
* 🧩 **Unified API**: instead of juggling `open()`, `json`, `csv`, and `yaml`, you get one interface.
* 🗂 **Backups with retention**: none of the compared tools provide this out-of-the-box.
* 🧹 **Exit cleanup**: ephemeral backups auto-clean themselves.
* ⚡ **Lightweight**: works without pandas overhead (which is overkill if you only want CSV/JSON/YAML).

### When to prefer others:

* **pathlib / shutil** → if you only need filesystem manipulation, not file contents.
* **pandas** → if you need heavy data analysis, joins, filtering, and numeric operations on tabular data.
* **ruamel.yaml / PyYAML** → if you need advanced YAML features (comments preservation, round-trip editing).

---

## 🎯 Example Use Cases for ADVfile\_manager

* **Config management**: load/modify JSON or YAML configs safely, with rollback if something breaks.
* **Logs & reports**: append text or CSV logs with automatic backup retention.
* **Transactional edits**: use `with File(...) as f:` to ensure no data corruption even on crash.
* **Cross-format tools**: build utilities that handle multiple formats with the same code patterns.


---

## Quick Start

```python
from ADVfile_manager import TextFile, JsonFile, CsvFile, YamlFile

# Text
txt = TextFile("notes.txt", "data")
txt.write("first line")
txt.append("second line")
print(txt.read_line(2))     # "second line"
for i, line in txt.lines():
    print(i, line)

# JSON (dict root)
j = JsonFile("config.json", "data")
j.write({"users": [{"id": 1}]})
j.append({"active": True})  # shallow dict update
print(j.get_item("active")) # True

# CSV
c = CsvFile("table.csv", "data")
c.write([{"name":"Avi","age":30},{"name":"Dana","age":25}], fieldnames=["name","age"])
c.append({"name":"Noa","age":21})
print(c.read_row(2))        # {"name":"Dana","age":"25"}
for idx, row in c.rows():
    print(idx, row)

# YAML
y = YamlFile("config.yaml", "data")
y.write({"app":{"name":"demo"}, "features":["a"]})
y.append({"features":["b"]})  # shallow dict update
print(y.get_item("app"))
```

---

## Detailed Usage

### Common Base: `File`

All file types inherit from `File` and share:

* `read()`, `write(data)`, `append(data)`
* `clear_cache()` — clear in-memory cache so next `read()` hits disk
* `get_size()` / `get_size_human()`
* Backups: `backup()`, `list_backups()`, `restore(backup_path=None)`, `clear_backups()`
* Context manager: `with File(...)(keep_backup=True) as f: ...`
* Exit cleanup controls (module-level):
  `set_exit_cleanup(enabled: bool)` and `cleanup_backups_for_all()`

#### Constructor

```python
File(
  file_name: str,
  file_path: str | pathlib.Path | None = None,  # defaults to CWD if None
  keep_backup: bool = True,                     # default keep backups
  max_backups: int | None = None                # retain only N latest backups
)
```

* `keep_backup=False` marks the instance as **ephemeral**: its backups are registered to be removed automatically at interpreter exit (and you can also call `cleanup_backups_for_all()` manually).
* `max_backups` enforces retention whenever `backup()` runs.

#### Backups

* `backup()` creates `backups/<file>.<YYYYMMDD_HHMMSS_micro>.bak`
* `list_backups()` returns sorted list (oldest → newest)
* `restore(path=None)` restores a specific backup, or the latest if `None`
* `clear_backups()` deletes all backups for that file and returns the deleted count

#### Human size

* `get_size_human()` returns `"12.3 KB"` style strings.

---

### `TextFile`

**Extras**:

* `lines()` → generator of `(line_no, text)`
* `read_line(n)` → 1-based line access

```python
txt = TextFile("example.txt", "data")
txt.write("Hello")
txt.append("World")
print(txt.read())           # "Hello\nWorld"
print(txt.read_line(2))     # "World"
for i, line in txt.lines(): # (1, "Hello"), (2, "World")
    print(i, line)
```

---

### `JsonFile`

Works with dict **or** list roots.

**Extras**:

* `get_item(index_or_key)`

  * list-backed: 1-based index (`int`)
  * dict-backed: key (`str`)
* `items()`

  * list-backed: yields `(index, value)` (1-based)
  * dict-backed: yields `(key, value)`
* `append(data)`

  * list-backed: append/extend
  * dict-backed: shallow `dict.update()`

```python
# dict root
j = JsonFile("conf.json", "data")
j.write({"users":[{"id":1}]})
j.append({"active": True})     # shallow merge
print(j.get_item("active"))    # True
for k, v in j.items():
    print(k, v)

# list root
jl = JsonFile("list.json", "data")
jl.write([{"id":1}])
jl.append({"id":2})
jl.append([{"id":3},{"id":4}])
print(jl.get_item(2))          # {"id":2}
for i, item in jl.items():
    print(i, item)
```

---

### `CsvFile`

**Design**: uses `csv.DictReader/DictWriter` (rows are dicts).

**Extras**:

* `write(data, fieldnames=None)` — define columns order; else inferred from data
* `read_row(n)` — 1-based row access
* `rows()` — generator of `(row_no, row_dict)`
* `append(dict | iterable[dict])`

```python
c = CsvFile("table.csv", "data")
c.write(
    [{"name":"Avi","age":30},{"name":"Dana","age":25}],
    fieldnames=["name","age"]           # control column order
)
c.append({"name":"Noa","age":21})
print(c.read_row(2))                    # {"name":"Dana","age":"25"}
for i, row in c.rows():
    print(i, row)
```

---

### `YamlFile`

Like `JsonFile`, but using YAML.
**Requires**: `pip install pyyaml`.

**Extras**:

* `get_item(index_or_key)` — 1-based indexes for lists, keys for dicts
* `items()` — same iteration semantics as `JsonFile`
* `append()` — list append/extend, dict shallow update

```python
from ADVfile_manager import YamlFile

y = YamlFile("config.yaml", "data")
y.write({"app":{"name":"demo"}, "features":["a"]})
y.append({"features":["b"]})            # shallow dict update
print(y.get_item("app"))
for k, v in y.items():
    print(k, v)
```

---

## Backups, Retention & Exit Cleanup

* **Create**: `path = f.backup()`
  Backups are timestamped down to microseconds to avoid collisions.
* **Retention**: set `max_backups=N` on the instance; when `backup()` runs, old backups beyond N are deleted.
* **List**: `f.list_backups()` → sorted list (oldest → newest)
* **Restore**:

  * latest: `f.restore()`
  * specific: `f.restore(path)`
* **Clear**: `f.clear_backups()` returns the deleted count

**Ephemeral backups** (`keep_backup=False`):

* Mark the instance transient with `File(..., keep_backup=False)` or via `obj(keep_backup=False)`.
* These are **registered** for deletion at **interpreter exit** by a silent atexit hook.
* You can control this globally:

```python
from ADVfile_manager import set_exit_cleanup, cleanup_backups_for_all

set_exit_cleanup(True)          # enable (default)
set_exit_cleanup(False)         # disable

removed = cleanup_backups_for_all()  # manual cleanup (returns deleted count)
```

---

## Context Manager Safety

* `with` creates a **backup on enter** (unless you set `keep_backup=False`).
* If an **exception** is raised inside the block and `keep_backup=True`, the file is **restored** from the latest backup.
* **Cache is always cleared** on exit to ensure the next `read()` hits disk.

```python
# default: keep_backup=True
with TextFile("draft.txt", "data") as f:
    f.write("safe transactional edit")
    # if an exception occurs here, latest backup will be restored

# ephemeral: backups are registered for exit cleanup
with TextFile("temp.txt", "data")(keep_backup=False) as f:
    f.write("temporary content")
```

---

## Advanced Notes

* **Atomic writes**: `write()` methods use a `*.tmp` + `os.replace()` strategy so files aren’t left half-written.
* **Pathlib**: all classes accept `str` or `pathlib.Path` for `file_path`.
* **Caching**: `read()` caches content. Use `clear_cache()` if the file was modified externally or you want a fresh read.
* **Append semantics**:

  * Text: appends `"\n"+data"` when file is non-empty.
  * JSON/YAML:

    * list root → append/extend
    * dict root → **shallow** `dict.update()`
* **CSV types**: values read by `DictReader` are `str`. After `append()`, cached rows keep stringified values for consistency.
* **Python**: 3.8+ recommended.

---

## Full Examples

### 1) Text + Backups + Restore Specific

```python
from ADVfile_manager import TextFile

txt = TextFile("example.txt", "example_data")
txt.write("v1"); b1 = txt.backup()
txt.write("v2"); b2 = txt.backup()
txt.write("v3"); b3 = txt.backup()

print("Backups:", txt.list_backups())
txt.restore(b2)
print("Restored content:", txt.read())  # "v2"
```

### 2) Retention (keep only last 2)

```python
txt.max_backups = 2
txt.write("v4"); txt.backup()
txt.write("v5"); txt.backup()
print("After retention:", txt.list_backups())  # only 2 latest remain
```

### 3) Ephemeral Backups + Exit Cleanup

```python
from ADVfile_manager import TextFile, cleanup_backups_for_all, set_exit_cleanup

with TextFile("temp.txt", "example_data")(keep_backup=False) as f:
    f.write("temporary content")

# You can manually clean now (or rely on atexit):
deleted = cleanup_backups_for_all()
print("Deleted backup files:", deleted)

# Disable/Enable the global atexit cleanup:
set_exit_cleanup(False)   # no automatic cleanup on interpreter exit
set_exit_cleanup(True)    # re-enable
```

### 4) CSV with Column Order Control

```python
from ADVfile_manager import CsvFile

rows = [{"name":"Avi","age":30},{"name":"Dana","age":25}]
c = CsvFile("table.csv", "example_data")
c.write(rows, fieldnames=["name","age"])  # explicit order
c.append({"name":"Noa","age":21})

print(c.read_row(2))      # {"name":"Dana","age":"25"}
for i, row in c.rows():
    print(i, row)
```

### 5) JSON/YAML Dict & List Behaviors

```python
from ADVfile_manager import JsonFile, YamlFile

# JSON dict
j = JsonFile("data.json", "example_data")
j.write({"users":[{"id":1}]})
j.append({"active": True})
print(j.get_item("active"))  # True

# JSON list
jl = JsonFile("list.json", "example_data")
jl.write([{"id":1}])
jl.append([{"id":2},{"id":3}])
print(jl.get_item(2))        # {"id":2}

# YAML dict
y = YamlFile("config.yaml", "example_data")
y.write({"app":{"name":"demo"},"features":["a"]})
y.append({"features":["b"]})
print(y.get_item("app"))
```

---

## License

**MIT License** — © 2025 Avi Twil.
See [`LICENSE`](./LICENSE) for details.

---

Questions or suggestions? Open an issue or PR:
**[https://github.com/avitwil/ADVfile\_manager](https://github.com/avitwil/ADVfile_manager)**
