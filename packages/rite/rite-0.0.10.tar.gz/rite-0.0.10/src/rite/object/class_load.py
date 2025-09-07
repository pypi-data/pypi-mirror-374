# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Load Class Utility Function
===========================

This module provides a function to import a class dynamically using a fully
qualified module path.

Example Usage:
    MyClass = load_class("mypackage.mymodule.MyClass")
    instance = MyClass()
"""

from __future__ import annotations

from importlib import import_module
from typing import List


class ClassImportError(ImportError):
    """Raised when a class cannot be dynamically imported."""


def load_class(path: str) -> type:
    """
    Dynamically import a class from a given module path.

    Args:
        path: The fully qualified module path of the class
              (e.g., "mypackage.mymodule.MyClass").

    Returns:
        The loaded class object.

    Raises:
        ClassImportError: If the module or class cannot be imported.
    """
    try:
        module_path, class_name = path.rsplit(".", 1)
    except ValueError as exc:
        raise ClassImportError(
            f"Invalid path format: '{path}'. Expected format 'module.ClassName'."
        ) from exc

    try:
        module = import_module(module_path)
    except ModuleNotFoundError as exc:
        raise ClassImportError(
            f"Error importing module '{module_path}': {exc}"
        ) from exc

    try:
        cls = getattr(module, class_name)
    except AttributeError as exc:
        raise ClassImportError(
            f"Module '{module_path}' does not define a class named '{class_name}'."
        ) from exc

    return cls


__all__: List[str] = ["load_class", "ClassImportError"]
