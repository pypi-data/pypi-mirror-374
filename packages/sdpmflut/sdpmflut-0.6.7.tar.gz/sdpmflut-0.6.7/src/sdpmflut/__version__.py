"""
Version information for sdpmflut.

This module defines the version details for the package.

Notes
-----
Version is defined both as a simple string and as a tuple for compatibility.

Examples
--------
>>> from sdpmflut.__version__ import __version__
>>> print(__version__)
"""

from typing import Tuple

# Version tuple for compatibility
__version_info__: Tuple[int, int, int] = (0, 6, 7)
__version__: str = "0.6.7"

# Derived version components
__major__, __minor__, __patch__ = __version_info__
