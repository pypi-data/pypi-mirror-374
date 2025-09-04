"""
File descriptor profiler for monitoring FD usage and detecting events.
"""

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development installs without git tags
    __version__ = "0.0.0.dev0"

__author__ = "Ian Hunt-Isaak"
__description__ = (
    "File descriptor profiler that monitors FD usage and captures timestamped events"
)

from .core import main


def cli_main():
    """Entry point for the fdprof command-line tool."""
    main()


__all__ = ["main"]
