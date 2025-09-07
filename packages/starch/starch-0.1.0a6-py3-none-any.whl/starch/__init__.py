"""
Starch
======

A configurable line-formatter for visually distinguishing certain comments.

"""
from typing import Final

from . import constants, formatter
from .config import config
from .constants import (
    STARCH_CACHE_PATH,
    STARCH_CONFIG_PATH,
    STARCH_DATA_PATH,
    STARCH_LOG_PATH,
    STARCH_LOG_FILEPATH
)
from .formatter import CommentFormatter

# ─── re-exporting metadata ──────────────────────────────────────────────────────── ✦ ─
__author__ = constants.__author__
__email__ = constants.__email__
__license__ = constants.__license__
__version__ = constants.__version__


__all__ = [
    # ─── metadata ─────────────────────────────────────────────────────────────────────
    #
    "__author__",
    "__email__",
    "__license__",
    "__version__",

    # ─── constants ────────────────────────────────────────────────────────────────────
    #
    "STARCH_CACHE_PATH",
    "STARCH_CONFIG_PATH",
    "STARCH_DATA_PATH",
    "STARCH_LOG_PATH",
    "STARCH_LOG_FILEPATH",

    # ─── modules ──────────────────────────────────────────────────────────────────────
    #
    "config",
    "constants",
    "formatter",
    
    # ─── classes ──────────────────────────────────────────────────────────────────────
    #
    "CommentFormatter",
    "config"
]
