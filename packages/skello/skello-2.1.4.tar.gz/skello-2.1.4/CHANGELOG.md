# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.1] - 2025-09-05

### Enhanced

-   **DirectoryValidator**: Enhanced existing validator with package name conflict detection
    -   Added `RESERVED_PACKAGE_NAMES` set to detect problematic package names
    -   Added `validate_package_name()` method that returns safe alternatives instead of just boolean validation
    -   Enhanced validation to automatically suggest `package_app`, `package_pkg`, etc. when conflicts detected
-   **CLIHandler integration**: Integrated DirectoryValidator into the CLI entry point
    -   Added comprehensive validation to `CLIHandler.from_cli()` method
    -   Now validates both directory permissions and package name safety upfront
    -   Automatically fixes problematic package names with user notification
-   **Error handling**: Improved error handling in CLI workflow
    -   Added proper exception handling for validation failures

### Fixed

-   **Package name conflicts**: Resolved import shadowing issues with reserved Python names
    -   Projects named "test", "main", "sys", etc. now automatically use safe alternatives
    -   Prevents `ModuleNotFoundError` and import conflicts during project execution
-   **Template compatibility**: Updated scaffolding templates to work correctly with safe package names
    -   Templates now properly reference the validated package names
    -   Ensures generated `pyproject.toml` uses correct entry point references

### Changed

-   **Package name behavior**: Package names that conflict with Python built-ins are now automatically renamed
    -   Example: `Test` project now creates `test_app` package instead of `test`
    -   Users are notified when package names are changed for safety
    -   Original project name is preserved, only package directory name is modified

### Developer Notes

-   The DirectoryValidator now serves dual purpose: directory validation + package name safety
-   Validation occurs at CLI entry point, ensuring all downstream scaffolding uses validated inputs
-   Template generation automatically receives safe package names, eliminating need for validation elsewhere

### Breaking Changes

-   `CLIHandler.from_cli()` now raises `DirectoryValidationError` for validation failures
-   Projects with reserved package names will have different package directory names than before

## [2.1.0] - Rebrand to Skello 2025-09-04

-   I've officially rebranded the project from **easy-venv** to **Skello**! 🎉

-   This change reflects the evolution of the project: what started as a simple `.venv` helper has now grown into a **full mini Python skeleton generator**. Skello now instantly creates:

    -   A ready-to-code folder structure (`src/`, `tests/`)
    -   Essential project files (`pyproject.toml`, `README.md`, `LICENSE`, `CHANGELOG.md`, `.gitignore`)
    -   Optional activated virtual environment

-   Skello emphasizes a **friendly, approachable, zero-configuration way** to kickstart modern Python projects, making setup faster and easier than ever.

-   All existing functionality remains intact — just a new, memorable name that better reflects the expanded scope and capabilities of the tool.

### Added

-   **DirectoryValidator** (Validates the target directory for project setup)
    -   Check if there's sufficient disk space.
    -   Get a formatted summary of validation results.
-   **TemplateManager** (Manages template loading)
    -   Map template categories to subdirectories
    -   Load and process template with variable substitution

### Changed

-   **command_runner** (file name change from `utils`)

## [2.0.3] - 2025-09-03

### Added

-   **CLIHandler** (new main entry point, replaces `FileSpec`)
    -   Owns project metadata (`target_dir`, `project_name`, `project_package`)
    -   Provides `from_cli()` as main constructor from CLI args
    -   Centralizes all CLI parsing logic
    -   `build_context()` creates the immutable `ScaffoldContext`
-   **scaffolding_types.py**
    -   New module containing enums and the `FileRequest` dataclass
    -   No local imports for clean separation of types

### Changed

-   **FileRequest** (simplified from `FileSpec`)
    -   Now a pure data class holding `file_type` and `options`
    -   All parsing/logic removed (moved to `CLIHandler`)
-   **ScaffoldContext**
    -   Now fully immutable and execution-focused
    -   Project metadata removed (lives in `CLIHandler`)
    -   Contains only execution plan details and current state
-   **ScaffoldManager**
    -   Updated to use `FileRequest` instead of `FileSpec`
    -   Renamed parameters from `spec` → `request`
    -   Updated type hints (`FileSpec` → `FileRequest`, `tuple` → `Tuple`)
    -   No logic changes needed — seamless transition

### Technical Improvements

-   Clearer separation of responsibilities:
    -   **CLIHandler** handles CLI parsing and context creation
    -   **FileRequest** is a simple data container
    -   **ScaffoldContext** defines the immutable execution plan
    -   **ScaffoldManager** executes the plan
-   Codebase is now more maintainable and consistent with the new architecture

### Files Modified

-   `src/easy_venv/scaffold_manager.py` — Updated to use `FileRequest` and improved type hints

### Files Added

-   `src/easy_venv/models/scaffolding_types.py` — Contains enums and the `FileRequest` dataclass
-   `src/easy_venv/models/cli_handler.py` — New main entry point (`CLIHandler`)

### Removed

-   `src/easy_venv/models/config.py` - No longer need with cli_handler.py

## [2.0.2] - 2025-09-02

### Added

-   **License System**: Complete license management system with support for multiple license types
    -   Added `LicenseHelper` class for centralized license operations
    -   Support for 7 license types: MIT, Apache 2.0, BSD 3-Clause, GPL v3, LGPL v3, MPL 2.0, and Unlicense
    -   License templates for all supported types:
        -   `LICENSE_MIT.tmpl`
        -   `LICENSE_APACHE.tmpl`
        -   `LICENSE_BSD.tmpl`
        -   `LICENSE_GPL.tmpl`
        -   `LICENSE_LGPL.tmpl`
        -   `LICENSE_MPL.tmpl`
        -   `LICENSE_UNLICENSE.tmpl`
    -   Automatic license detection from existing LICENSE files
    -   Dynamic license classifier detection for pyproject.toml

### Enhanced

-   **CLI License Options**: Enhanced license creation with flexible syntax
    -   `l:apache:author_name` - Create Apache license with specific author
    -   `l:mit` - Create MIT license with default author placeholder
    -   `l` - Create MIT license (default)
    -   Defaults to MIT license when no type specified
-   **Requirements File Naming**: Added ability to specify custom requirements filename

    -   `r:custom_name` - Create requirements file with custom name
    -   `r` - Create standard requirements.txt

-   **Author Name Integration**: License files now properly integrate author names
    -   Author name from CLI arguments
    -   Fallback to "TODO: Add your name" placeholder
    -   Current year automatically inserted

### Changed

-   **CLI Interface**: Expanded CLI argument parsing (`cli.py`)

    -   More robust parsing for license and requirements options
    -   Better error handling for malformed arguments
    -   Improved help text and usage examples

-   **Template Updates**: Updated existing templates for better consistency
    -   Modified `LICENSE_MIT.tmpl` for improved formatting
    -   Updated `pyproject.toml.tmpl` for dynamic license classifier

### Removed

-   `src/easy_venv/file_manager.py` - split into scaffold_manager.py and directory_snapshot.py

### Technical Improvements

-   Added proper license classifier mapping for all supported license types
-   Implemented fallback chain: specified license → detected license → MIT default
-   Enhanced template rendering system with better variable substitution
-   Improved code organization with dedicated license helper class

### Files Modified

-   `src/easy_venv/cli.py` - Enhanced CLI parsing and license options
-   `src/easy_venv/templates/LICENSE_MIT.tmpl` - Template formatting improvements
-   `src/easy_venv/templates/pyproject.toml.tmpl` - Dynamic classifier support
-   `src/easy_venv/dependency_handler.py` - New files support

### Files Added

-   `src/easy_venv/directory_snapshot.py` - Take a snapshot of the target directory
-   `src/easy_venv/models/scaffold_context.py` - Hold the scaffold context
-   `src/easy_venv/scaffold_manager.py` - New way to handle project scaffolding
-   `src/easy_venv/license_helper.py` - New license management utility class
-   `src/easy_venv/templates/LICENSE_APACHE.tmpl` - Apache 2.0 license template
-   `src/easy_venv/templates/LICENSE_BSD.tmpl` - BSD 3-Clause license template
-   `src/easy_venv/templates/LICENSE_GPL.tmpl` - GPL v3 license template
-   `src/easy_venv/templates/LICENSE_LGPL.tmpl` - LGPL v3 license template
-   `src/easy_venv/templates/LICENSE_MPL.tmpl` - MPL 2.0 license template
-   `src/easy_venv/templates/LICENSE_UNLICENSE.tmpl` - Unlicense template

## [2.0.1] - 2025-09-01

### Added

-   **Template-based file generation system** - Complete rewrite of file creation using external template files
    -   All project files now generated from `.tmpl` files in `src/easy_venv/templates/`
    -   Clean separation of content from logic
    -   Easily maintainable and customizable templates
-   **Smart pyproject.toml generation** - Context-aware pyproject.toml creation
    -   Detects existing project structure (src/, tests/, README, LICENSE)
    -   Only includes sections for files that exist or will be created
    -   Prevents build errors from missing files
    -   Auto-detects license types from existing LICENSE files
-   **Project structure scaffolding** - New commands for modern Python project layout
    -   `create_main_structure()` - Creates `src/project_name/main.py` with proper package structure
    -   `create_project_structure()` - Full project scaffold with src/ layout and tests/
    -   Includes `__init__.py`, `main.py` with CLI entry points, and basic test files
-   **Enhanced license detection** - Smart license type identification
    -   Supports MIT, Apache, BSD, GPL, LGPL, MPL, and Unlicense
    -   Automatic detection from existing LICENSE file content
    -   Proper classifier mapping for pyproject.toml
    -   Defaults to MIT License for new projects
-   **Improved file creation logic** - Context-aware file generation
    -   Files are created based on what will be generated in the same session
    -   Prevents inconsistencies between pyproject.toml and actual project structure
    -   Better error handling and validation

### Changed

-   **File generation architecture** - Moved from inline string templates to external template files
-   **pyproject.toml generation** - Now adapts to actual project structure instead of using static template
-   **Template variable system** - Uses `string.Template` with `$variable` syntax for clean substitution

### Technical

-   Added `importlib.resources` support for template file access
-   Enhanced `FileManager` class with template handling capabilities
-   Improved project name sanitization for Python package names
-   Better separation of concerns between file detection and template generation

## [2.0.0] - 2025-08-31

### Added

-   🏗️ **Complete project scaffolding** with `--create` flag (`pyproject.toml`, `.gitignore`, `README.md`, `CHANGELOG.md`, `LICENSE`)
-   🔧 **Modern Python standards**: Prefer `pyproject.toml` over `requirements.txt`
-   🧠 **Smart file logic**: Never overwrites, conflict prevention, intelligent defaults
-   📝 **Professional templates** with current best practices
-   🎯 **Flexible options** with validation + aliases
-   ⚡ **Zero to production**: Setup in one command
-   🛡️ **Enhanced safety**: Comprehensive validation & error handling

---

## [1.1.0] - 2025-06-15

### Added

-   📦 Multi-format dependency detection (`pyproject.toml`, `requirements.txt`, `Pipfile`, etc.)

### Changed

-   📝 `requirements.txt` template now requires a flag
-   🔍 Smarter dependency handling (no auto-create by default)
-   🚀 Improved workflow: better file detection for existing projects

---

## [1.0.0] - 2025-04-10

### Added

-   ✨ Auto-shell activation
-   📝 Smart `requirements.txt` auto-template
-   🚀 Short flags for all options
-   🖥️ Cross-platform improvements (Windows + Unix shells)
-   📦 Installable package via `pip install -e .`
