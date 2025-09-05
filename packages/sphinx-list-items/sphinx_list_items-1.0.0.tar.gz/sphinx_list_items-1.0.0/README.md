
# sphinx-list-items
[![GPL3 License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://spdx.org/licenses/GPL-3.0-only.html)
[![PyPi Status](https://img.shields.io/pypi/status/sphinx-list-items.svg?style=flat)](https://pypi.python.org/pypi/sphinx-list-items)
[![PyPi Version](https://img.shields.io/pypi/v/sphinx-list-items.svg?style=flat)](https://pypi.python.org/pypi/sphinx-list-items)

A Sphinx extension to automatically list figures, tables, and Sphinx version directives (`versionadded`, `versionchanged`, `deprecated`, `versionremoved`) in your documentation. Output as a bulleted list or a customizable table, with filtering and advanced options.

## Features

- List all figures or tables in your documentation
- List Sphinx version directives (with prefix-stripping for cleaner output)
- Output as a bulleted list or a table (with custom columns)
- Filter version items by version number
- Works with cross-references and section links

## Installation

```bash
pip install sphinx-list-items
```

Or for development:

```bash
pip install -e .
```

## Setup

Add to your `conf.py`:

```python
extensions = ['sphinx_list_items']
```

## Usage

### List all figures (as a list)

```rst
.. list-items:: figures
   :list:
```

### List all figures (as a table)

```rst
.. list-items:: figures
   :table:
```

### List all tables (as a list)

```rst
.. list-items:: tables
   :list:
```

### List all tables (as a table)

```rst
.. list-items:: tables
   :table:
```

### List Sphinx version directives (as a list)

```rst
.. list-items:: versionadded
   :list:

.. list-items:: versionchanged
   :list:

.. list-items:: deprecated
   :list:

.. list-items:: versionremoved
   :list:
```

### List Sphinx version directives (as a table)

```rst
.. list-items:: versionadded
   :table:
```

### Filter version items by version

```rst
.. list-items:: versionadded
   :table:
   :version: 0.0.2
```

### Custom columns for tables

```rst
.. list-items:: versionchanged
   :table: docname, version, text, type
```

## Advanced

- All output supports cross-references to the source location.
- Version directive output strips the prefix (e.g., "Added in version 1.0.0:") for clean summaries.
- You can use `:list:` or `:table:` for any supported type.
- For tables, you can specify custom columns (e.g., `:table: id, caption`).

## Example

See the [examples](doc/content/examples.rst) and [specimens](doc/content/specimens.rst) in this repository for real-world usage.
