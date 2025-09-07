"""
Version information for sdpmflut.

This module defines the version details for the package.

Notes
-----
Version is defined as a tuple and converted to string format.

Examples
--------
>>> from sdpmflut.__version__ import __version__
>>> print(__version__)
'0.6.2'
"""

from typing import Tuple

__version_info__: Tuple[int, int, int] = (0, 6, 3)
__version__: str = ".".join(map(str, __version_info__))

__major__, __minor__, __patch__ = __version_info__
