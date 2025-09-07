"""Options

This module provides interfaces for managing various options that
affect the way Starch determines how it should format your comments.
"""
# ─── import statements ────────────────────────────────────────────────── ✦ ──
from __future__ import annotations

# standard library imports
import logging
import json

from pathlib import Path

# local imports
from .constants import STARCH_CONFIG_PATH, STARCH_LOG_FILEPATH, STARCH_CONFIG_FILEPATH

# ─── logger setup ─────────────────────────────────────────────────────── ✦ ──

logger = logging.getLogger(__package__)
logging.basicConfig(filename=STARCH_LOG_FILEPATH, level=logging.DEBUG)


# ─── interfaces ───────────────────────────────────────────────────────── ✦ ──

class Configuration:
    """
    A singleton that serves the central configurator for Starch's formatting
    engine.
    """

    # ─── singleton pattern enforcement ────────────────────────────────────────
    def __new__(cls) -> "Configuration":
        """Ensure that only one instance of Configuration exists."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Configuration, cls).__new__(cls)
            return cls.instance
        else:
            return cls.instance


    def __init__(self, filepath: str | Path = STARCH_CONFIG_FILEPATH) -> None:
        """Constructor for the Configuration class."""
        self._config_dir: Path | None = STARCH_CONFIG_PATH

        self._config_filepath: Path = (
            Path(filepath) if isinstance(filepath, str)
            else filepath if isinstance(filepath, Path)
            else STARCH_CONFIG_FILEPATH
        ) 

        self._options: dict[str, dict[str, int | str]] = {
            "cpp": {
                "length": 80,
                "prefix": "// ─── ",
                "suffix": " ✦ ─"
            },
            "haskell": {
                "length": 80,
                "prefix": "-- ─── ",
                "suffix": " ✦ ─"
            },
            "python": {
                "length": 79,
                "prefix": "# ─── ",
                "suffix": " ✦ ─"
            },
            "rust": {
                "length": 80,
                "prefix": "// ─── ",
                "suffix": " ✦ ─"
            },
            "swift": {
                "length": 80,
                "prefix": "// ─── ",
                "suffix": " ✦ ─"
            }
        }

        if not self._config_filepath.exists():
            print("No configuration file found.")
            print("Creating a new configuration file with default settings.")

            try:
                self._config_filepath.touch(exist_ok=True)

                with open(self._config_filepath, "w") as f:
                    data = {
                        "cpp": {
                            "length": 80,
                            "prefix": "// ─── ",
                            "suffix": " ✦ ─"
                        },
                        "haskell": {
                            "length": 80,
                            "prefix": "-- ─── ",
                            "suffix": " ✦ ─"
                        },
                        "python": {
                            "length": 79,
                            "prefix": "# ─── ",
                            "suffix": " ✦ ─"
                        },
                        "rust": {
                            "length": 80,
                            "prefix": "// ─── ",
                            "suffix": " ✦ ─"
                        },
                        "swift": {
                            "length": 80,
                            "prefix": "// ─── ",
                            "suffix": " ✦ ─"
                        }
                    }
                    json.dump(data, f, indent=2)
                print("Configuration file created at: ", self._config_filepath)
            except Exception as e:
                print(f"Error creating configuration file: {e}")
                # self._config_filepath = self._config_dir / "config.json"

        try:
            self.load_config()

        except FileNotFoundError as e:
            logger.warning(f"Failed to load config file: {e}")
            logger.info("Writing default config to config file...")
            self.save_config()
            logger.info("Done.")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")


    # ─── property accessors ───────────────────────────────────────────────────

    @property
    def config_filepath(self) -> Path:
        """Return the path to the configuration file."""
        return self._config_filepath

    @config_filepath.setter
    def config_filepath(self, value: str | Path) -> None:
        """Set the path to the configuration file."""
        self._config_filepath = (
            Path(value) if isinstance(value, str)
            else value if isinstance(value, Path)
            else self._config_dir / "config.json"
        )

    @config_filepath.deleter
    def config_filepath(self) -> Exception:
        return UserWarning(
            "Deleting the configuration file path is not allowed."
        )

    @property
    def options(self) -> dict[str, dict[str, int | str]]:
        return self._options

    @options.setter
    def options(
        self,
        value: dict[str, dict[str, int | str]]
    ) -> None:
        self._options = value

    @options.deleter
    def options(self) -> Exception:
        return UserWarning(
            "Deleting the options dictionary is not allowed."
        )


    # ─── interface methods ────────────────────────────────────────────────────

    def load_config(self) -> None:
        """Load the configuration from the file."""
        try:
            with open(self._config_filepath, "r") as f:
                self._options = json.load(f)

            # logger.info(
            #     f"Configuration loaded from {self._config_filepath}"
            # )
        except FileNotFoundError as e:
            logger.error(
                f"Configuration file {self._config_filepath} not found."
            )
            raise e
        except json.JSONDecodeError as e:
            logger.error(
                f"Error decoding JSON from {self._config_filepath}: {e}"
            )
            raise e        
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise e


    def save_config(self) -> None:
        """Save the options dicionary to the configuration file."""
        try:
            with open(self._config_filepath, "w") as f:
                json.dump(self._options, f, indent=2)
                logger.info(f"Configuration saved to {self._config_filepath}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise e

# ─── API ──────────────────────────────────────────────────────────────── ✦ ──
config: Configuration = Configuration()
