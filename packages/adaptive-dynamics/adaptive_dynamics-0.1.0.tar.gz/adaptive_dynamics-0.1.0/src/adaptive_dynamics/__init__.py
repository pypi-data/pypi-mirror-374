"""
Adaptive Dynamics Toolkit (ADT): A unified framework for adaptive computing paradigms.
"""

__version__ = "0.1.0"

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("adaptive-dynamics")
except PackageNotFoundError:
    # Package is not installed
    pass