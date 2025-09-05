"""
ADEV Tools - Advanced Development Tools

A comprehensive toolkit for GitLab, Jira, and CI/CD automation.
"""

__version__ = "0.1.1"
__author__ = "JLTech"
__email__ = "dev@jltech.com"

# Import commonly used functions
try:
    from . import adev_lib
    from . import ci_lib
except ImportError:
    # Handle cases where the modules might not be available during setup
    pass

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "adev_lib", 
    "ci_lib",
]
