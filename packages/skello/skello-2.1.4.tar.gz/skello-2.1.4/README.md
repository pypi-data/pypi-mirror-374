# Skello

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**The friendliest way to bootstrap modern Python projects - from zero to fully-structured, ready-to-code project in seconds! 🚀**

---

## Why Skello?

Starting a new Python project shouldn't take 10+ minutes of setup. You know the drill:

1. Create folders (`src/`, `tests/`)
2. Set up virtual environment
3. Create project files (`pyproject.toml`, `README.md`, `.gitignore`, `LICENSE`)
4. Configure packaging structure
5. Initialize documentation
6. Finally... start coding

**Skello** eliminates ALL these steps with a single command, giving you a complete, modern Python project structure instantly!

---

## What Makes Skello Special?

-   ✨ **Complete Project Skeleton**: Full folder structure with `src/`, `tests/`, and all essential files
-   🚀 **Zero Configuration**: Works perfectly out-of-the-box with sensible defaults
-   🏗️ **Modern Standards**: Creates `pyproject.toml`-based projects following current best practices
-   🎯 **Instant Productivity**: Drop into an activated shell, ready to code immediately
-   🌍 **Cross-Platform**: Reliable on Windows (PowerShell), macOS, and Linux
-   📦 **Smart Dependencies**: Auto-detects and installs from existing dependency files
-   🔧 **Flexible**: Every feature is optional - use what you need
-   🛡️ **Safe**: Never overwrites existing files, validates everything

---

## Installation

### Recommended: Global Installation

Install once, use anywhere:

```bash
git clone https://github.com/snacktimepro/skello.git
cd skello
pip install -e .
```

Now use `skello` command from anywhere on your system!

### Alternative: Direct Usage

```bash
git clone https://github.com/snacktimepro/skello.git
cd skello
python -m skello -p /path/to/project
```

---

## Quick Start

### The Magic Command ✨

Create a complete, modern Python project instantly:

```bash
# Create everything - the full skeleton!
skello -c *
# or use the longer form
skello -c all

# Result: Complete project structure ready to go!
📁 MyProject/
  📁 src/
    📁 myproject/
      📄 __init__.py
      📄 main.py
  📁 tests/
    📄 __init__.py
    📄 test_main.py
  📄 pyproject.toml
  📄 README.md
  📄 LICENSE
  📄 CHANGELOG.md
  📄 .gitignore
  📄 .venv/ (activated and ready!)
```

### Power User Examples

```bash
# Complete new project with custom name
skello -p ~/my-awesome-api -c *

# Quick skeleton with specific files
skello -c full g read lic            # Full structure + gitignore, readme, license

# Just add structure to existing project
skello -c main                       # Add src/package structure only

# Custom license with your name
skello -c l:mit:John Doe            # MIT license with John Doe

# Custom requirements file name
skello -c r:dev-requirements.txt    # Named requirements file
```

---

## Command Reference

```bash
skello [OPTIONS]

Options:
  -p, --path PATH          Target directory (default: current directory)
  -n, --name NAME          Virtual environment name (default: .venv)
  -c, --create FILES       Create project files and structure
  -s, --no-auto-shell      Skip launching activated shell
  -h, --help              Show help and exit
```

### File Creation Options

| Short | Long   | Creates            | Description                    |
| ----- | ------ | ------------------ | ------------------------------ |
| `r`   | `req`  | `requirements.txt` | Pip requirements file          |
| `p`   | `toml` | `pyproject.toml`   | Modern Python packaging config |
| `g`   | `git`  | `.gitignore`       | Python-focused git ignores     |
| `md`  | `read` | `README.md`        | Project documentation          |
| `ch`  | `log`  | `CHANGELOG.md`     | Structured changelog           |
| `l`   | `lic`  | `LICENSE`          | MIT license (current year)     |

### Structure Templates

| Option | Creates | Description                         |
| ------ | ------- | ----------------------------------- |
| `m`    | `main`  | `src/package/main.py` structure     |
| `f`    | `full`  | Complete structure with tests       |
| `*`    | `all`   | Everything - files + full structure |

### Advanced Options

```bash
# Custom license types and names
skello -c l:apache:Your Name        # Apache license
skello -c l:mit:Jane Smith          # MIT with custom name

# Custom file names
skello -c r:dev-requirements.txt    # Named requirements file
```

---

## Real-World Examples

### Brand New Project - Complete Setup

```bash
mkdir my-web-api
skello -p my-web-api -c *

# 🎉 Result: Full project structure with:
# ✅ src/my_web_api/ package structure
# ✅ tests/ directory with test files
# ✅ Modern pyproject.toml configuration
# ✅ Professional README.md
# ✅ MIT LICENSE
# ✅ .gitignore for Python
# ✅ CHANGELOG.md ready for releases
# ✅ Virtual environment activated!
```

### Existing Project - Add Structure

```bash
# Add modern structure to legacy project
cd my-old-project
skello -c main toml git

# Adds src/ structure + pyproject.toml + .gitignore
# Keeps all existing files safe
```

### Selective Enhancement

```bash
# Add just the essentials
skello -c read lic git              # Documentation + license + gitignore

# Add testing structure
skello -c full                      # Complete src/ and tests/ structure
```

### Team Development

```bash
# Standardized team setup
skello -p ~/projects/team-app -c * -n dev

# Custom license for organization
skello -c l:apache:"Acme Corp" -c *
```

---

## What Skello Does

When you run Skello, here's the magic that happens:

1. **🎯 Validates** your target directory and permissions
2. **🏗️ Creates** complete folder structure (`src/`, `tests/` with proper `__init__.py` files)
3. **📝 Generates** all requested project files with professional templates
4. **🌱 Sets up** virtual environment (if needed)
5. **🔧 Upgrades** pip to latest version
6. **📦 Detects** and installs existing dependencies (`pyproject.toml`, `requirements.txt`, etc.)
7. **🚀 Launches** activated shell in your new project directory

**Ready to code in seconds, not minutes!**

---

## Generated Project Structure

### Full Structure (`skello -c *` or `skello -c all`)

```
MyProject/
├── src/
│   └── myproject/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml          # Modern packaging config
├── README.md               # Professional documentation
├── LICENSE                 # MIT license (current year)
├── CHANGELOG.md            # Structured release notes
├── .gitignore              # Python-focused ignores
└── .venv/                  # Activated virtual environment
```

### File Templates

**`pyproject.toml`** - Complete modern Python packaging:

-   Build system with hatchling
-   Development dependencies
-   Tool configurations (black, isort, pytest)
-   Metadata ready for PyPI

**`README.md`** - Professional project documentation:

-   Installation instructions
-   Usage examples
-   Contributing guidelines
-   Badge placeholders

**`src/package/main.py`** - Ready-to-run entry point:

-   Professional docstring
-   Example function with docstring
-   `if __name__ == "__main__"` pattern

**`tests/test_main.py`** - Testing foundation:

-   Pytest-ready test structure
-   Example test cases
-   Proper imports from your package

---

## Smart Behaviors

### Dependency Detection

Skello automatically finds and installs from:

1. **`pyproject.toml`** (modern standard - preferred)
2. **`requirements.txt`** (legacy format)
3. **`Pipfile`** (Pipenv format)
4. Other detected formats

### Safe File Creation

-   **Never overwrites** existing files
-   **Explains** what was created vs. skipped
-   **Validates** all inputs before making changes
-   **Handles** permission issues gracefully

### Modern Defaults

-   Prefers `pyproject.toml` over `requirements.txt`
-   Creates `src/` layout (not flat structure)
-   Includes `tests/` directory with proper structure
-   Uses current year in LICENSE files

---

## Platform Support

### Windows

-   **PowerShell**: Full support with colors and proper activation
-   **Command Prompt**: Fallback batch scripts
-   **Path handling**: Automatic Windows path conversion

### macOS/Linux

-   **Bash/Zsh**: Native shell integration with `exec`
-   **Permissions**: Proper executable permissions
-   **Symbolic links**: Full support for linked directories

---

## Tips & Best Practices

### 🚀 **Getting Started**

-   Use `skello -c *` (or `skello -c all`) for new projects - creates everything you need
-   Keep Skello installed globally for instant access anywhere
-   Let Skello handle the tedious setup so you can focus on coding

### 📁 **Project Organization**

-   The `src/` layout keeps your package code organized
-   `tests/` directory follows Python testing conventions
-   Modern `pyproject.toml` replaces old `setup.py` approach

### 🎯 **Workflow Integration**

-   Use `-s` flag in CI/CD scripts to skip shell activation
-   Combine with your editor: `skello -c * && code .`
-   Create template projects and enhance them with Skello

### 🤝 **Team Development**

-   Standardize team projects with `skello -c *`
-   Use custom license names for organization projects
-   Share the command that created your project structure

---

## Error Handling

Skello handles edge cases gracefully:

-   **Missing directories**: Clear validation with helpful messages
-   **File conflicts**: Never overwrites, shows what was skipped
-   **Permission issues**: Informative error messages with solutions
-   **Invalid options**: Validates inputs and shows available choices
-   **Existing environments**: Skips creation, continues with setup
-   **Empty dependency files**: Informative skip messages

---

## The Skello Advantage

### Traditional Way (10+ commands, 10+ minutes)

```bash
mkdir my-project && cd my-project
mkdir src tests
mkdir src/my_project
touch src/my_project/__init__.py src/my_project/main.py
touch tests/__init__.py tests/test_main.py
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install --upgrade pip
# Manually create pyproject.toml...
# Manually create README.md...
# Manually create .gitignore...
# Manually create LICENSE...
# ...finally ready to code after 5-10 minutes
```

### The Skello Way (1 command, 10 seconds)

```bash
skello -p my-project -c *
# 🎉 Complete project structure, activated environment, ready to code!
```

---

## Requirements

-   **Python 3.7+** (no external dependencies!)
-   **PowerShell** (Windows) or **Bash/Zsh** (macOS/Linux)
-   **Git** (optional, for cloning)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
git clone https://github.com/snacktimepro/skello.git
cd skello
skello -c *  # Use Skello to set up Skello! 🎉
```

---

## Support

Having issues?

1. **Check help**: `skello -h`
2. **Review examples**: See patterns above
3. **Check permissions**: May need admin on Windows
4. **Open issue**: Include OS, Python version, error message

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

---

_Made with ❤️ to make Python project setup effortless_

**From empty directory to fully-structured Python project in seconds! 🚀**
