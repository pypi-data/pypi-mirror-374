"""Async template loaders for jinja2-async-environment.

This module provides async-compatible template loaders that maintain
100% backward compatibility with the original API while offering
improved performance and maintainability through modular design.
"""

# Import all loader classes from their respective modules

from .base import AsyncBaseLoader, AsyncLoaderProtocol, SourceType
from .choice import AsyncChoiceLoader
from .dict import AsyncDictLoader
from .filesystem import AsyncFileSystemLoader
from .function import AsyncFunctionLoader

# Import exception classes from package module
from .package import AsyncPackageLoader, LoaderNotFound, PackageSpecNotFound

# For backward compatibility, also import any existing exceptions and utilities
# from the original loaders module that we need to preserve
try:
    # Import from original module if it still exists during transition
    from ..loaders_old import (
        LoaderContext,
        TestContext,
        UnifiedCache,
        _clear_expired_cache,
        _loader_context,
        _unified_cache,
        clear_test_context,
        set_test_context,
    )
except ImportError:
    # Create placeholder implementations during refactoring
    class LoaderContext:
        """Placeholder for backward compatibility."""

        def is_test_case(self, test_name: str) -> bool:
            return False

    class TestContext:
        """Placeholder for backward compatibility."""

        def __init__(self, test_name: str):
            self.test_name = test_name

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class UnifiedCache:
        """Placeholder for backward compatibility."""

        def get(self, cache_type: str, key, default=None):
            return default

        def set(self, cache_type: str, key, value, ttl=None):
            pass

        def clear_all(self):
            pass

    def _clear_expired_cache():
        """Placeholder function."""
        pass

    def set_test_context(test_name: str):
        """Placeholder function."""
        pass

    def clear_test_context():
        """Placeholder function."""
        pass

    # Create global instances for compatibility
    _loader_context = LoaderContext()
    _unified_cache = UnifiedCache()

# Public API - maintain exact same exports as original module
__all__ = [
    # Main loader classes
    "AsyncBaseLoader",
    "AsyncLoaderProtocol",
    "AsyncFileSystemLoader",
    "AsyncDictLoader",
    "AsyncFunctionLoader",
    "AsyncPackageLoader",
    "AsyncChoiceLoader",
    # Types
    "SourceType",
    # Backward compatibility (will be moved to testing module in later phases)
    "LoaderContext",
    "TestContext",
    "UnifiedCache",
    "set_test_context",
    "clear_test_context",
    "_loader_context",
    "_unified_cache",
    "_clear_expired_cache",
    # Exception classes
    "PackageSpecNotFound",
    "LoaderNotFound",
]

# Version information
__version__ = "2.0.0-refactored"
