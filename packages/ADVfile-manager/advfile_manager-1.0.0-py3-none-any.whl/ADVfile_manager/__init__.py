"""
ADVfile_manager
===============

Unified file abstractions with backups, context manager, and exit cleanup.

Author: Avi Twil
"""

from .core import (
    File,
    TextFile,
    JsonFile,
    CsvFile,
    YamlFile,
    set_exit_cleanup,
    cleanup_backups_for_all,
)

__all__ = [
    "File",
    "TextFile",
    "JsonFile",
    "CsvFile",
    "YamlFile",
    "set_exit_cleanup",
    "cleanup_backups_for_all",
]

__version__ = "1.0.0"
__author__ = "Avi Twil"