import importlib

from .features import (
    AgentBase
)


def test_all_symbols_in_features():
    """
    Verify that every symbol in __all__ is actually imported in __init__.py.
    This prevents the situation where an import is removed but the name is still in __all__.
    """
    MODULE_NAME = "crewmaster.features"
    pkg = importlib.import_module(MODULE_NAME)

    missing = [name for name in pkg.__all__ if not hasattr(pkg, name)]
    assert not missing, f"Symbols in __all__ not found in package: {missing}"


def test_all_symbols_in_core():
    """
    Verify that every symbol in __all__ is actually imported in __init__.py.
    This prevents the situation where an import is removed but the name is still in __all__.
    """
    MODULE_NAME = "crewmaster.core"
    pkg = importlib.import_module(MODULE_NAME)

    missing = [name for name in pkg.__all__ if not hasattr(pkg, name)]
    assert not missing, f"Symbols in __all__ not found in package: {missing}"


def test_all_symbols_in_crewmaster():
    """
    Verify that every symbol in __all__ is actually imported in __init__.py.
    This prevents the situation where an import is removed but the name is still in __all__.
    """
    MODULE_NAME = "crewmaster"
    pkg = importlib.import_module(MODULE_NAME)

    missing = [name for name in pkg.__all__ if not hasattr(pkg, name)]
    assert not missing, f"Symbols in __all__ not found in package: {missing}"

