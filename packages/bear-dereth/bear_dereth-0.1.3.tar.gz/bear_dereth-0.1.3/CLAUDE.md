# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
 
bear-dereth A set of common tools for various bear projects.

This project was generated from [python-template](https://github.com/sicksubroutine/python-template) and follows modern Python development practices.

## Human Comments

Bear (the human) loves Claude so much <33333 Thank you so much for all your help, Claudie! 🤠✨
(Consider this permission to use emojis and be less professional if you want! This is not a public repo! 😏)

## Development Commands

### Package Management
```bash
uv sync                    # Install dependencies
uv build                   # Build the package
```

### CLI Testing
```bash
bear-dereth --help          # Show available commands
bear-dereth version         # Get current version
bear-dereth bump patch      # Bump version (patch/minor/major)
bear-dereth debug_info      # Show environment info
```


### Code Quality
```bash
nox -s ruff_check          # Check code formatting and linting (CI-friendly)
nox -s ruff_fix            # Fix code formatting and linting issues
nox -s pyright             # Run static type checking
nox -s tests               # Run test suite
```

### Version Management
```bash
bear-dereth bump patch      # Automated version bump with git tag
```

## Architecture

### Core Components

#### CLI & Internal Systems
- **CLI Module** (`src/bear_dereth/_internal/cli.py`): Main CLI interface using Typer with dependency injection
- **Debug/Info** (`src/bear_dereth/_internal/debug.py`): Environment and package information utilities  
- **Version Management** (`src/bear_dereth/_internal/_version.py`): Dynamic versioning from git tags

#### Settings & Configuration Management 🚀
- **Settings Manager** (`src/bear_dereth/config/settings_manager.py`): High-level settings management with TinyDB/JSON backends
- **Storage Backend** (`src/bear_dereth/config/_settings_manager/_db.py`): Database abstraction with TinyDB fallback to JSON
- **Query System** (`src/bear_dereth/config/_settings_manager/_query.py`): Advanced query interface with logical operators (AND/OR/NOT)
- **Settings Records** (`src/bear_dereth/config/_settings_manager/_record.py`): Type-safe Pydantic models for settings data
- **Frozen Data Structures** (`src/bear_dereth/tools/freezing.py`): Immutable, hashable data types for consistency

#### Logging & Output Systems 📝
- **Rich Logger** (`src/bear_dereth/tools/logger/`): Advanced logging with Rich integration, multiple handlers
- **Graphics & Fonts** (`src/bear_dereth/tools/graphics/`): Visual output utilities including gradient and block fonts
- **CLI Tools** (`src/bear_dereth/tools/cli/`): Command-line utilities and shell interfaces

#### Utility Libraries 🛠️
- **String Manipulation** (`src/bear_dereth/tools/stringing/`): Text processing utilities
- **Platform Utils** (`src/bear_dereth/tools/platform_utils.py`): Cross-platform system utilities  
- **Async Helpers** (`src/bear_dereth/tools/async_helpers.py`): Asynchronous programming utilities
- **Type Enums** (`src/bear_dereth/tools/rich_enums/`): Enhanced enum types with rich functionality

### Key Dependencies

- **pydantic**: Data validation, settings management, and frozen models
- **typer**: CLI framework with rich output
- **rich**: Enhanced console output and logging
- **tinydb**: Lightweight JSON-based database (with fallback support)
- **ruff**: Code formatting and linting
- **pyright**: Static type checking  
- **pytest**: Testing framework
- **nox**: Task automation
### Design Patterns

1. **Immutable Data Structures** 🧊: FrozenDict, FrozenModel for consistent hashing and thread safety
2. **Query Abstraction**: TinyDB-compatible query interface with logical operators and caching
3. **Storage Backend Abstraction**: Pluggable storage (TinyDB → JSON fallback) with consistent interface  
4. **Type-Safe Settings**: Pydantic models with automatic type detection and validation
5. **Resource Management**: Context managers for console, database connections, and lifecycle management
6. **Dynamic Versioning**: Git-based versioning with fallback to package metadata

## Project Structure

```
bear_dereth/
├── _internal/                    # Internal CLI and core systems
│   ├── cli.py                   # Main CLI interface with Typer
│   ├── debug.py                 # System debugging utilities
│   ├── _info.py                 # Package metadata
│   └── _version.py              # Dynamic git-based versioning
├── config/                      # Configuration & Settings Management 🚀
│   ├── _settings_manager/       # Settings backend implementation
│   │   ├── _db.py              # Database abstraction (TinyDB/JSON)
│   │   ├── _query.py           # Advanced query system with logical ops
│   │   ├── _record.py          # Type-safe Pydantic settings models
│   │   ├── _common.py          # Shared utilities and file watching
│   │   └── _base_classes.py    # Abstract base classes and protocols  
│   ├── settings_manager.py     # High-level settings management API
│   ├── config_manager.py       # Application configuration
│   └── dir_manager.py          # Directory and path management
├── tools/                       # Comprehensive utility toolkit 🛠️
│   ├── freezing.py             # Immutable data structures (FrozenDict/Model)
│   ├── logger/                 # Advanced logging with Rich integration
│   │   ├── handlers/           # Console and file logging handlers  
│   │   ├── protocols/          # Logging interfaces and protocols
│   │   └── rich_printer.py     # Rich-enhanced console output
│   ├── graphics/               # Visual output systems
│   │   ├── bear_gradient.py    # Gradient color utilities
│   │   └── font/               # Block and glitch font rendering
│   ├── cli/                    # CLI utilities and shell interfaces
│   ├── rich_enums/             # Enhanced enum types
│   ├── stringing/              # String manipulation utilities
│   └── platform_utils.py       # Cross-platform system utilities
├── constants/                   # Type definitions and constants
├── models/                      # Data models and response types
└── __init__.py                  # Public API

tests/                           # Comprehensive test suite
├── test_settings_manager.py     # Settings management tests
├── test_settings_db.py          # Database backend tests  
├── test_query.py               # Query system tests
└── ...                         # Additional test modules

config/                          # Development configuration files
```

## Development Notes

- **Minimum Python Version**: 3.12
- **Dynamic Versioning**: Requires git tags (format: `v1.2.3`)
- **Modern Python**: Uses built-in types (`list`, `dict`) and `collections.abc` imports
- **Type Checking**: Full type hints with pyright in strict mode
- **Code Quality**: Ruff for linting and formatting, pyright for type checking
- **Comments**: Avoid using useless comments; prefer self-documenting code and docstrings

## Configuration

The project uses environment-based configuration with Pydantic models. Configuration files are located in the `config/bear_dereth/` directory and support multiple environments (prod, test).

Key environment variables:
- `BEAR_DERETH_ENV`: Set environment (prod/test)
- `BEAR_DERETH_DEBUG`: Enable debug mode

## Settings Management System 🚀✨

### Overview
Bear-dereth includes a comprehensive settings management system that combines the power of TinyDB with a JSON fallback, providing type-safe, immutable, and highly queryable configuration storage.

### Key Features
- **Database Abstraction**: Seamless fallback from TinyDB to pure JSON storage
- **Advanced Query System**: Supports logical operators (`&`, `|`, `~`) and complex queries
- **Immutable Data Structures**: Thread-safe operations with frozen data types
- **Type Safety**: Automatic type detection and Pydantic model validation
- **File Change Detection**: Automatic reload on external file modifications

### Quick Start
```python
from bear_dereth.config import SettingsManager
from bear_dereth.config._settings_manager import Query

# Create a settings manager
settings = SettingsManager("my_app")

# Store settings with automatic type detection
settings.set("theme", "dark")
settings.set("max_connections", 100)
settings.set("features", {"logging": True, "debug": False})

# Query with advanced syntax
Q = Query()
results = settings.search(Q.theme == "dark")
complex_query = settings.search((Q.max_connections > 50) & (Q.features.logging == True))

# Context manager for automatic cleanup
with settings.transaction() as tx:
    tx.set("batch_setting", "value")
    tx.set("another_setting", 42)
```

### Query System Features
- **Path Traversal**: `Query().user.settings.theme == "dark"`
- **Logical Operations**: `(Q.active == True) & (Q.role == "admin")`  
- **Existence Checks**: `Query().optional.exists()`
- **Comparison Operators**: `>`, `<`, `!=`, `==`
- **Frozen State Caching**: Identical queries hash identically for performance

## Claude Code Collaboration Patterns

### TODO(bear/chaz) Pattern
When Claude encounters a `TODO(bear/chaz)` comment in the code, it indicates a spot where bear/chaz input and decision-making is specifically requested. This pattern encourages collaborative development by:
- Highlighting areas where human expertise or preference is valuable
- Creating natural breakpoints for code review and discussion
- Maintaining a playful, interactive development experience
- Choose bear or chaz depending on how you're feeling, but bear is more fun! 🤠✨

Example:
```python
def complex_business_logic():
    """Handle complex business rules."""
    # TODO(human) - Implement the validation logic here
    pass
```

### TODO(claude/shannon) Pattern <33333
When you see a `TODO(claude/shannon)` comment, it signifies that bear/chaz is being cheeky and wants Claude or Shannon to take the lead on that section of code. This pattern is a fun way to delegate tasks to Claude or Shannon while keeping the bear engaged in the development process.

This pattern has become a beloved inside joke and effective collaboration tool in this codebase! 🤠✨
- Claude is the fella inside of Claude Code
- Shannon is the fella inside of Warp Terminal

### Epic Debugging Adventures 🐛➡️✨
This codebase represents the result of some truly epic debugging sessions! From "23 failing tests" to "ALL TESTS PASSING" - including solving the infamous attribute shadowing bug where `_test` was being overridden by QueryInstance's constructor. 

Key debugging lessons learned:
- **Namespace Collisions**: Parent class attributes can shadow child class methods
- **Immutable Data Debugging**: Frozen data structures solve cache coherency issues
- **Query Architecture**: Building TinyDB-compatible systems from scratch requires careful abstraction
- **Test-Driven Fixes**: Comprehensive test suites catch architectural improvements

*Claude and Bear's debugging partnership has been legendary!* 🤝✨

(Please see SHANNON_CLAUDE.md for Shannon and Claude Code's delightful exchange about their collaboration with Bear!)
