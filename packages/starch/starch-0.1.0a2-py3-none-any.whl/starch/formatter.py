"""Formatter

This module provides the main comment-formatting utility class.
"""
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

import click

from .config import Configuration, config
from .constants import (
    STARCH_CONFIG_FILEPATH,
    STARCH_LOG_FILEPATH,
    __package__,
    __version__
)

# | logger setup

logging.basicConfig(level="INFO", format="%(name)s – %(levelname)s: %(message)s")

logger = logging.getLogger(__package__)


# | supported languages

SUPPORTED_EXTENSIONS = {
    # C/cpp
    "cpp": "cpp", "cxx": "cpp", "cc": "cpp", "c": "cpp",
    "h": "cpp", "hpp": "cpp", "hxx": "cpp",
    # Python
    "py": "python",
    # Rust
    "rs": "rust",
    # Swift
    "swift": "swift",
    # Haskell
    "hs": "haskell"
}


# | API

class CommentFormatter:
    _config: Configuration = config
   
    @classmethod
    def _get_config(
            cls, config_file: Path = STARCH_CONFIG_FILEPATH
    ) -> Configuration:
        """Get or initialize the configuration singleton."""
        if cls._config is None:
            try:
                # For singleton, create without parameters first
                cls._config = config
                
                # If a specific config file is requested, update the filepath
                if isinstance(cls._config, Configuration): 
                    cls._config.config_filepath = config_file
                    cls._config.load_config()
                    
                # logger.info("Configuration loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                raise
        elif config_file is not None and cls._config.config_filepath != config_file:
            # Handle case where different config file is requested
            cls._config.config_filepath = config_file
            cls._config.load_config()
            
        return cls._config

    @staticmethod
    def _default_options() -> Dict[str, Dict[str, Union[str, int]]]:
        """Return default configuration options."""
        return {
            "cpp": {
                "length": 100,
                "prefix": "// ─── ",
                "suffix": " ✦ ─"
            },
            "haskell": {
                "length": 100,
                "prefix": "-- ─── ",
                "suffix": " ✦ ─"
            },
            "python": {
                "length": 88,
                "prefix": "# ─── ",
                "suffix": " ✦ ─"
            },
            "rust": {
                "length": 100,
                "prefix": "// ─── ",
                "suffix": " ✦ ─"
            },
            "swift": {
                "length": 100,
                "prefix": "// ─── ",
                "suffix": " ✦ ─"
            }
        }
    
    @staticmethod
    def format_file(file_path: Path, lang: Optional[str] = None) -> bool:
        """Format a single file. Returns True if file was modified."""
        
        # Validate file exists first
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get configuration
        config = CommentFormatter._get_config()
        
        # Determine language from extension if not provided
        if lang is None:
            ext = file_path.suffix.lstrip(".").lower()
            lang = SUPPORTED_EXTENSIONS.get(ext)
            
            if lang is None:
                raise ValueError(f"File extension '.{ext}' is not supported.")

        # Validate language is supported
        if lang not in config.options:
            raise ValueError(f"Unsupported language: {lang}")

        updated_lines = []
        modified = False

        try:
            with file_path.open("r", encoding="utf-8") as f:
                for line in f:
                    processed_line = CommentFormatter._process_line(line, lang, config)
                    updated_lines.append(processed_line)
                    if processed_line != line:
                        modified = True

            if modified:
                with file_path.open("w", encoding="utf-8") as f:
                    f.writelines(updated_lines)
                    
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise

        return modified

    @staticmethod
    def check_file_needs_formatting(file_path: Path, lang: Optional[str] = None) -> bool:
        """Check if a file needs formatting without modifying it."""
        
        # Validate file exists first
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get configuration
        config = CommentFormatter._get_config()
        
        # Determine language from extension if not provided
        if lang is None:
            ext = file_path.suffix.lstrip(".").lower()
            lang = SUPPORTED_EXTENSIONS.get(ext)
            
            if lang is None:
                raise ValueError(f"File extension '.{ext}' is not supported.")

        # Validate language is supported
        if lang not in config.options:
            raise ValueError(f"Unsupported language: {lang}")

        try:
            with file_path.open("r", encoding="utf-8") as f:
                for line in f:
                    processed_line = CommentFormatter._process_line(line, lang, config)
                    if processed_line != line:
                        return True
                        
        except Exception as e:
            logger.error(f"Error checking file {file_path}: {e}")
            raise

        return False

    @staticmethod
    def _process_line(line: str, lang: str, config: Configuration) -> str:
        """Process a single line, formatting starch comments."""

        # Define comment patterns for each language
        comment_patterns = {
            "python": r"^(\s*)# |(.*)$",
            "haskell": r"^(\s*)-- |(.*)$",
            "rust": r"^(\s*)// |(.*)$",
            "cpp": r"^(\s*)// |(.*)$",
            "swift": r"^(\s*)// |(.*)$",
        }

        if lang not in comment_patterns:
            raise NotImplementedError(f"Language '{lang}' is not yet supported.")

        match = re.match(comment_patterns[lang], line)
        if not match:
            return line

        indent, comment = match.groups()
        comment = comment.strip()
        
        # Access configuration using the options property
        lang_config = config.options.get(lang)
        if not lang_config:
            raise ValueError(f"No configuration found for language: {lang}")

        prefix = lang_config["prefix"]
        
        # Only add suffix for top-level comments (no indentation)
        if indent == "":
            suffix = lang_config["suffix"]
        else:
            suffix = ""

        # Calculate the maximum length for the comment text
        max_comment_length = (
            int(lang_config["length"])
            - len(str(prefix))
            - len(str(suffix))
            - len(str(indent))  # Account for indentation in total length
        )
        
        # Ensure we have at least some space for the comment
        if max_comment_length <= 0:
            logger.warning(f"⚠︎ Warning: Comment length too restrictive for language {lang}")
            max_comment_length = 10  # Minimum fallback
        
        # Trim comment to fit and calculate padding
        trimmed_comment = comment[:max_comment_length] if comment else ""
        
        # Calculate padding needed to reach the desired length
        # Format: indent + prefix + comment + padding + suffix
        current_length = len(indent) + len(str(prefix)) + len(str(trimmed_comment)) + len(str(suffix))
        target_length = lang_config["length"]
        padding_length = max(0, int(target_length) - int(current_length))
        
        # Create the padded comment line
        if trimmed_comment:
            # If there's a comment, add a space before padding
            padded_comment = f"{trimmed_comment} {'─' * max(0, padding_length - 1)}"
        else:
            # If no comment, just use padding
            padded_comment = "─" * padding_length

        return f"{indent}{prefix}{padded_comment}{suffix}\n"

    @staticmethod
    def get_source_files(
        path: Path,
        ignore_patterns: List[str],
        extensions: Optional[List[str]] = None
    ) -> List[Path]:
        """Get source files in a directory recursively.

        Get all supported source files in a directory recursively,
        respecting ignore patterns.
        """
        if extensions is None:
            extensions = list(SUPPORTED_EXTENSIONS.keys())
        
        source_files = []
        ignore_set = set(ignore_patterns)

        def should_ignore(file_path: Path) -> bool:
            """Check if a path should be ignored."""
            path_str = str(file_path)
            path_name = file_path.name

            # Always ignore hidden directories and files (starting with .)
            if any(part.startswith('.') and part != '.' and part != '..' for part in file_path.parts):
                return True

            # Check if any part of the path matches ignore patterns
            for pattern in ignore_set:
                if pattern in path_str or pattern == path_name:
                    return True
                # Check if any parent directory matches the pattern
                for parent in file_path.parents:
                    if parent.name == pattern:
                        return True
            return False

        if path.is_file():
            ext = path.suffix.lstrip(".").lower()
            if ext in extensions and not should_ignore(path):
                source_files.append(path)
        elif path.is_dir():
            for ext in extensions:
                for source_file in path.rglob(f"*.{ext}"):
                    if not should_ignore(source_file):
                        source_files.append(source_file)

        return sorted(source_files)


# | command-line interface
#
def common_options(f):
    """Decorator to add common options to commands."""
    f = click.option(
        "--config-file",
        type=click.Path(path_type=Path),
        default=STARCH_CONFIG_FILEPATH,
        help="Path to configuration file. Use this to specify a custom "
             "configuration file instead of the default location. The file "
             "will be created if it doesn't exist.",
    )(f)
    f = click.option(
        "--verbose", 
        "-v", 
        is_flag=True, 
        help="Enable verbose output showing detailed information about "
             "processing, including files that were unchanged, configuration "
             "details, and additional diagnostic information."
    )(f)
    return f

@click.group(invoke_without_command=True)
@click.option(
    "--version",
    is_flag=True,
    help="Show starch's version string and exit."
)
@click.pass_context
def cli(ctx, version):
    """Starch - A comment formatter for source code files.
    
    Starch is a powerful comment formatting tool that automatically formats
    decorated comment lines in your source code files. It supports multiple
    programming languages and provides consistent, beautiful comment formatting.
    
    Starch looks for comment lines that start with a colon (:) after the
    comment delimiter and transforms them into formatted section headers.
    
    \b
    Supported Languages:
        • Python (.py)
        • C/C++ (.c, .cpp, .cxx, .cc, .h, .hpp, .hxx)
        • Rust (.rs)
        • Swift (.swift)
        • Haskell (.hs)
    
    \b
    Common Usage Patterns:
        starch format .                    # Format all files in current directory
        starch format src/ --dry-run       # Preview changes without applying
        starch format . --check            # Check if formatting is needed
        starch config show                 # View current configuration
        starch config set python.length=80 # Customize formatting options
    
    \b
    Example Comment Transformation:
        Before:  # | main functions
        After:   # ─── main functions ──────────────────────────────────── ✦ ─
    
    Use 'starch COMMAND --help' for detailed help on specific commands.
    """
    if version:
        click.echo(f"starch, v{__version__}")
        return
        
    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument(
    "src", 
    nargs=-1, 
    type=click.Path(exists=True, path_type=Path),
    required=True,
    metavar="[FILES_OR_DIRECTORIES]..."
)
@click.option(
    "--lang",
    "-l",
    type=click.Choice(['python', 'cpp', 'rust', 'swift', 'haskell'], case_sensitive=False),
    help="Restrict formatting to files of this language only. When specified, "
         "only files of the given language will be processed, regardless of "
         "other file types found. Auto-detected from file extensions if not specified."
)
@click.option(
    "--ignore",
    "-i",
    multiple=True,
    metavar="PATTERN",
    help="Directory or file patterns to ignore during recursive processing. "
         "Can be used multiple times to specify multiple patterns. Patterns are "
         "matched against directory names, file names, and path components. "
         "Hidden directories (starting with '.') are always ignored."
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Preview mode: show which files would be reformatted without actually "
         "making any changes to the files. Use this to safely preview the "
         "effects of formatting before applying changes."
)
@click.option(
    "--check",
    is_flag=True,
    help="Validation mode: check if any files would be reformatted and exit "
         "with code 1 if they would, code 0 if no changes are needed. "
         "Useful for CI/CD pipelines to enforce consistent formatting. "
         "Does not modify any files."
)
@common_options
def format(src, lang, ignore, dry_run, check, verbose, config_file):
    """Format decorated comment lines in source code files.
    
    This command processes source code files and formats special comment lines
    that begin with a colon (:) after the comment delimiter. These decorated
    comments are transformed into beautiful, consistent section headers.

    \b
    Input Requirements:
        Files must contain comment lines in this format:
        
        Python:     # | section name
        C/C++:     // | section name  
        Rust:      // | section name
        Swift:     // | section name
        Haskell:   -- | section name

    \b
    Output Format:
        Decorated comments are transformed into formatted headers:

        # ─── section name ─────────────────────────────────────── ✦ ─
    
    \b
    File Discovery:
        • Processes individual files or recursively scans directories
        • Automatically detects file types by extension
        • Respects ignore patterns and skips hidden directories
        • Only processes files with supported extensions
    
    \b
    Processing Modes:
        --dry-run    Preview changes without modifying files
        --check      Validate formatting (exit 1 if changes needed)
        (default)    Apply formatting changes to files
    
    \b
    Language Support:
        python    Python files  (.py)
        cpp       C/C++ files   (.c, .cpp, .cxx, .cc, .h, .hpp, .hxx)
        rust      Rust files    (.rs)
        swift     Swift files   (.swift)
        haskell   Haskell files (.hs)
    
    \b
    Examples:
        starch format .
            Format all supported files in the current directory recursively
        
        starch format src/ tests/ docs/
            Format files in multiple directories
        
        starch format main.py utils.rs
            Format specific files
        
        starch format . --lang python
            Format only Python files, ignoring other file types
        
        starch format . --ignore __pycache__ --ignore node_modules
            Format files while ignoring specific directories
        
        starch format . --dry-run
            Preview which files would be changed without modifying them
        
        starch format . --check
            Check if any files need formatting (for CI/CD validation)
        
        starch format . --verbose
            Show detailed output including unchanged files
        
        starch format . --config-file ./custom-starch.toml
            Use a custom configuration file
    
    \b
    Default Ignore Patterns:
        The following patterns are ignored by default:
        • __pycache__ (Python bytecode)
        • node_modules (Node.js dependencies)  
        • build (Generic build directories)
        • dist (Distribution directories)
        • .git (Git repository data)
        • target (Rust build directory)
        • .build (Swift build directory)
        • Any directory starting with '.' (hidden directories)
    
    \b
    Exit Codes:
        0    Success (no errors occurred)
        1    Error occurred or files need formatting (with --check)
    """
    
    # Set up ignore patterns
    ignore_patterns = list(ignore) if ignore else [
        "__pycache__",      # Python
        "node_modules",     # JavaScript/TypeScript
        "build",            # Generic build
        "dist",             # Generic distribution
        ".git",             # Git
        "target",           # Rust
        ".build",           # Swift build
    ]
    
    try:
        # Load the configuration.
        config = CommentFormatter._get_config(config_file)
    except Exception as e:
        click.echo(f"✗ Error loading config: {e}", err=True)
        sys.exit(1)
    
    # Collect all files to process.
    all_files = []
    for path in src:
        if path.is_file():
            ext = path.suffix.lstrip(".").lower()
            if ext in SUPPORTED_EXTENSIONS:
                all_files.append(path)
        else:
            # Get files from directory
            extensions = None
            if lang:
                extensions = [ext for ext, language in SUPPORTED_EXTENSIONS.items() if language == lang]
            
            directory_files = CommentFormatter.get_source_files(
                path, ignore_patterns, extensions
            )
            all_files.extend(directory_files)
    
    if not all_files:
        if lang:
            click.echo(f"⚠︎ Warning: No {lang} files found to process.")
        else:
            click.echo("⚠︎ Warning: No supported files found.")
        return
    
    # Process files
    modified_files = []
    would_modify_files = []
    error_files = []
    
    for file_path in all_files:
        try:
            file_lang = lang or SUPPORTED_EXTENSIONS[file_path.suffix.lstrip(".").lower()]
            
            if dry_run or check:
                # Use the same check method for consistency
                would_modify = CommentFormatter.check_file_needs_formatting(file_path, file_lang)
                if would_modify:
                    would_modify_files.append(file_path)
                    if dry_run:
                        click.echo(f"would reformat {file_path}")
                    elif verbose:
                        click.echo(f"would reformat {file_path}")
                elif verbose and not check:
                    click.echo(f"unchanged {file_path}")
            else:
                # Actually format the file
                was_modified = CommentFormatter.format_file(file_path, file_lang)
                if was_modified:
                    modified_files.append(file_path)
                    if verbose:
                        click.echo(f"reformatted {file_path}")
                elif verbose:
                    click.echo(f"unchanged {file_path}")
                    
        except Exception as e:
            error_files.append((file_path, str(e)))
            click.echo(f"✗ Error: cannot format {file_path}: {e}", err=True)
   
    # Summary output
    if check:
        if would_modify_files:
            click.echo(f"would reformat {len(would_modify_files)} files")
            sys.exit(1)
        else:
            if verbose:
                click.echo(f"✓ Checked {len(all_files)} files")
    elif dry_run:
        if would_modify_files:
            click.echo(f"would reformat {len(would_modify_files)} files")
        else:
            click.echo("✓ No changes needed")
    else:
        # Show appropriate success message based on what actually happened
        if modified_files:
            # Some files were actually modified
            if len(modified_files) == 1:
                click.echo("✓ Formatted 1 file.")
            else:
                click.echo(f"✓ Formatted {len(modified_files)} files.")
            
            if verbose:
                total_checked = len(all_files)
                if total_checked > len(modified_files):
                    unchanged_count = total_checked - len(modified_files)
                    click.echo(f"({unchanged_count} files were unchanged)")
        else:
            # No files were modified
            if len(all_files) == 1:
                click.echo("✓ Checked 1 file. No changes required.")
            else:
                click.echo(f"✓ Checked {len(all_files)} files. No changes required.")


@cli.group()
def config():
    """Configuration management for starch formatting options.
    
    Starch uses a configuration system to customize formatting behavior for
    different programming languages. Each language has configurable settings
    for line length, comment prefixes, and suffixes.
    
    \b
    Configuration File:
        Starch stores its configuration in a TOML file, typically located at:
        ~/.config/starch/config.toml (Unix/Linux/macOS)
        %APPDATA%\\starch\\config.toml (Windows)
    
    \b
    Available Settings:
        length    Maximum line length for formatted comments (integer)
        prefix    Comment prefix with decorative elements (string)  
        suffix    Comment suffix with decorative elements (string)
    
    \b
    Default Configuration:
        python:   length=88, prefix="  # ─── ", suffix=" ✦ ─"
        cpp:      length=100, prefix="// ─── ", suffix=" ✦ ─"
        rust:     length=100, prefix="// ─── ", suffix=" ✦ ─"
        swift:    length=100, prefix="// ─── ", suffix=" ✦ ─"
        haskell:  length=100, prefix="-- ─── ", suffix=" ✦ ─"
    
    \b
    Common Tasks:
        starch config show                  # View all current settings
        starch config get python.length     # Get a specific value
        starch config set python.length=100 # Change a setting
        starch config reset python          # Reset language to defaults
    
    Use 'starch config SUBCOMMAND --help' for detailed help on each operation.
    """
    pass


@config.command(name="show")
@common_options
def show_config(verbose, config_file):
    """Display the current starch configuration settings.
    
    Shows all configuration settings for all supported languages, including
    line lengths, comment prefixes, and suffixes. This command displays the
    active configuration that will be used for formatting operations.
    
    \b
    Output Format:
        The configuration is displayed grouped by language, showing each
        setting name and its current value. String values are quoted for
        clarity.
    
    \b
    Configuration File Location:
        The command also displays the path to the configuration file being
        used, and whether that file currently exists on disk.
    
    \b
    Example Output:
        Configuration file: /home/user/.config/starch/config.toml
        
        python:
          length = 88
          prefix = "# ─── "
          suffix = " ✦ ─"
        
        cpp:
          length = 100
          prefix = "// ─── "
          suffix = " ✦ ─"
    
    \b
    Usage:
        starch config show                      # Show all settings
        starch config show --verbose            # Show with extra details
        starch config show --config-file /path  # Use specific config file
    """
    try:
        config = CommentFormatter._get_config(config_file)
        if not config.options:
            click.echo("⚠︎ Warning: No configuration found.")
            return
            
        click.echo(f"Configuration file: {config.config_filepath}")
        click.echo()
        for lang_name, settings in config.options.items():
            click.echo(f"{lang_name}:")
            for key, value in settings.items():
                if isinstance(value, str):
                    click.echo(f'  {key} = "{value}"')
                else:
                    click.echo(f"  {key} = {value}")
            click.echo()
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@config.command(name="path")
@common_options
def config_path(verbose, config_file):
    """Display the path to the starch configuration file.
    
    Shows the filesystem path where starch looks for its configuration file,
    and indicates whether the file currently exists. This is useful for
    troubleshooting configuration issues or when you need to manually edit
    the configuration file.
    
    \b
    Information Displayed:
        • Full path to the configuration file
        • Whether the file exists on disk
        • File permissions (when --verbose is used)
    
    \b
    Default Locations:
        Unix/Linux/macOS: ~/.config/starch/config.toml
        Windows: %APPDATA%\\starch\\config.toml
    
    \b
    Usage:
        starch config path                      # Show config file path
        starch config path --verbose            # Show additional file info
        starch config path --config-file /path  # Check specific config file
    
    \b
    Example Output:
        Configuration file: /home/user/.config/starch/config.toml
        Exists: Yes
    """
    try:
        config = CommentFormatter._get_config(config_file)
        click.echo(f"Configuration file: {config.config_filepath}")
        click.echo(f"Exists: {'Yes' if config.config_filepath.exists() else 'No'}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@config.command(name="get")
@click.argument("key", metavar="LANGUAGE.SETTING")
@common_options
def get_config(key, verbose, config_file):
    """Retrieve a specific configuration value.
    
    Gets the current value of a specific configuration setting for a given
    language. The key must be in the format LANGUAGE.SETTING where LANGUAGE
    is one of the supported languages and SETTING is one of the available
    configuration options.
    
    \b
    Key Format:
        LANGUAGE.SETTING
        
        Where LANGUAGE is one of: python, cpp, rust, swift, haskell
        Where SETTING is one of: length, prefix, suffix
    
    \b
    Available Settings:
        length    Maximum line length for formatted comments (integer)
        prefix    Text/symbols placed before the comment content (string)
        suffix    Text/symbols placed after the comment content (string)
    
    \b
    Output Format:
        The command outputs the setting in the format "key = value", with
        string values enclosed in quotes for clarity.
    
    \b
    Examples:
        starch config get python.length
            Output: python.length = 88
        
        starch config get cpp.prefix
            Output: cpp.prefix = "// ─── "
        
        starch config get rust.suffix
            Output: rust.suffix = " ✦ ─"
    
    \b
    Error Handling:
        • Invalid language names will show available languages
        • Invalid setting names will show available settings for that language
        • Missing configuration files will be created with defaults
    """
    try:
        if "." not in key:
            click.echo("✗ Error: Config key must be in format LANGUAGE.SETTING", err=True)
            sys.exit(1)
            
        language, setting = key.split(".", 1)
        config = CommentFormatter._get_config(config_file)
        
        if language not in config.options:
            click.echo(f"✗ Error: Language '{language}' not found.", err=True)
            click.echo(f"Available: {', '.join(config.options.keys())}")
            sys.exit(1)
            
        if setting not in config.options[language]:
            click.echo(f"✗ Error: Setting '{setting}' not found for {language}.", err=True)
            click.echo(f"Available: {', '.join(config.options[language].keys())}")
            sys.exit(1)
            
        value = config.options[language][setting]
        if isinstance(value, str):
            click.echo(f'{key} = "{value}"')
        else:
            click.echo(f"{key} = {value}")
            
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@config.command(name="set")
@click.argument("assignment", metavar="LANGUAGE.SETTING=VALUE")
@common_options
def set_config(assignment, verbose, config_file):
    """Set a configuration value to customize formatting behavior.
    
    Modifies a specific configuration setting for a given language. The
    assignment must be in the format LANGUAGE.SETTING=VALUE. The new value
    will be automatically converted to the appropriate type (integer for
    length, string for prefix/suffix).
    
    \b
    Assignment Format:
        LANGUAGE.SETTING=VALUE
        
        Where LANGUAGE is one of: python, cpp, rust, swift, haskell
        Where SETTING is one of: length, prefix, suffix
        Where VALUE is the new value to set
    
    \b
    Setting Descriptions:
        length    Maximum line length (integer, typically 79-120)
                  Controls the total width of formatted comment lines
        
        prefix    Comment prefix with decorative elements (string)
                  Text/symbols placed at the beginning of formatted comments
        
        suffix    Comment suffix with decorative elements (string)  
                  Text/symbols placed at the end of formatted comments
                  (only applied to top-level, non-indented comments)
    
    \b
    Type Conversion:
        • length values are converted to integers
        • prefix and suffix values are treated as strings
        • Boolean values accept: true/false, 1/0, yes/no, on/off
    
    \b
    Examples:
        starch config set python.length=100
            Set Python line length to 100 characters
        
        starch config set cpp.prefix="/* ═══ "
            Change C++ comment prefix to use different symbols
        
        starch config set rust.suffix=" ═══ */"
            Change Rust comment suffix
        
        starch config set haskell.length=90
            Set Haskell line length to 90 characters
    
    \b
    Persistence:
        Changes are immediately saved to the configuration file and will
        affect all future formatting operations until changed again.
    
    \b
    Validation:
        • Language names are validated against supported languages
        • Setting names are validated against available options
        • Values are type-checked and converted appropriately
    """
    try:
        if "=" not in assignment:
            click.echo("✗ Error: Config setting must be in format LANGUAGE.SETTING=VALUE", err=True)
            sys.exit(1)
            
        key_part, value = assignment.split("=", 1)
        if "." not in key_part:
            click.echo("✗ Error: Config key must be in format LANGUAGE.SETTING=VALUE", err=True)
            sys.exit(1)
            
        language, setting = key_part.split(".", 1)
        config = CommentFormatter._get_config(config_file)
        
        if language not in config.options:
            click.echo(f"✗ Error: Language '{language}' not found.", err=True)
            sys.exit(1)
            
        if setting not in config.options[language]:
            click.echo(f"✗ Error: Setting '{setting}' not found for {language}.", err=True)
            sys.exit(1)
            
        # Type conversion
        current_value = config.options[language][setting]
        try:
            if isinstance(current_value, int):
                new_value = int(value)
            elif isinstance(current_value, bool):
                new_value = value.lower() in ("true", "1", "yes", "on")
            else:
                new_value = value
        except ValueError:
            click.echo(f"✗ Error: Cannot convert '{value}' to expected type.", err=True)
            sys.exit(1)
            
        config.options[language][setting] = new_value
        config.save_config()
        
        if isinstance(new_value, str):
            click.echo(f'Set {key_part} = "{new_value}"')
        else:
            click.echo(f"Set {key_part} = {new_value}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@config.command(name="reset")
@click.argument("language", metavar="LANGUAGE")
@common_options
def reset_config(language, verbose, config_file):
    """Reset configuration settings to default values.
    
    Restores the configuration for a specific language (or all languages)
    back to the built-in default values. This is useful when you want to
    undo customizations or fix corrupted configuration settings.
    
    \b
    Language Options:
        python    Reset Python formatting settings
        cpp       Reset C/C++ formatting settings  
        rust      Reset Rust formatting settings
        swift     Reset Swift formatting settings
        haskell   Reset Haskell formatting settings
        all       Reset all language configurations
    
    \b
    Default Values:
        python:
          length = 88
          prefix = "# ─── "
          suffix = " ✦ ─"
        
        cpp:
          length = 100
          prefix = "// ─── "
          suffix = " ✦ ─"
        
        rust:
          length = 100
          prefix = "// ─── "
          suffix = " ✦ ─"
        
        swift:
          length = 100
          prefix = "// ─── "
          suffix = " ✦ ─"
        
        haskell:
          length = 100
          prefix = "-- ─── "
          suffix = " ✦ ─"
    
    \b
    Examples:
        starch config reset python
            Reset only Python settings to defaults
        
        starch config reset all
            Reset all language settings to defaults
        
        starch config reset cpp --verbose
            Reset C++ settings with detailed output
    
    \b
    Safety:
        This operation immediately saves the reset values to your configuration
        file, overwriting any existing customizations for the specified
        language(s). Use 'starch config show' first if you want to backup
        your current settings.
    
    \b
    Confirmation:
        The command will display a confirmation message showing which
        configurations were reset.
    """
    try:
        config = CommentFormatter._get_config(config_file)
        defaults = CommentFormatter._default_options()
        
        if language == "all":
            config.options = {lang: defaults[lang].copy() for lang in defaults}
            config.save_config()
            click.echo("✓ Reset all language configurations to defaults.")
        else:
            if language not in defaults:
                click.echo(f"✗ Error: Language '{language}' not supported.", err=True)
                click.echo(f"Available: {', '.join(defaults.keys())}")
                sys.exit(1)
                
            config.options[language] = defaults[language].copy()
            config.save_config()
            click.echo(f"✓ Reset {language} configuration to defaults.")
            
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
