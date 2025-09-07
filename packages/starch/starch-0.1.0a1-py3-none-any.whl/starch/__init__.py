"""
Starch
======

A configurable line-formatter for visually distinguishing certain comments.

"""
from typing import Final

from . import config, constants, formatter
from .config import Configuration
from .constants import (
    STARCH_CACHE_PATH,
    STARCH_CONFIG_PATH,
    STARCH_DATA_PATH,
    STARCH_LOG_PATH,
    STARCH_LOG_FILEPATH
)
from .formatter import CommentFormatter


# | package metadata
#
__author__: Final[str] = "Caleb Rice"
__description__: Final[str] = (
    "A configurable line-formatter for visually distinguishing "
    "certain comments."
)
__email__: Final[str] = "hyletic@proton.me"
__license__: Final[str] = "MIT"

# VERSION_CONFIG: {"base":"0.1.0","phase":"a","build":1}
__version__ = "0.1.0a1"



__all__ = [
    # | metadata
    #
    "__author__",
    "__email__",
    "__license__",
    "__version__",
    "__package__",

    # | constants
    #
    "STARCH_CACHE_PATH",
    "STARCH_CONFIG_PATH",
    "STARCH_DATA_PATH",
    "STARCH_LOG_PATH",
    "STARCH_LOG_FILEPATH",

    # | modules
    #
    "config",
    "constants",
    "formatter",
    
    # | classes
    #
    "CommentFormatter",
    "Configuration"
]
