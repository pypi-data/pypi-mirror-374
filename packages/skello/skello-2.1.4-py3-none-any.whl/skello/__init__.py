"""Skello: A complete Python project initialization tool - create virtual environments, install dependencies, and scaffold modern project structure in seconds!"""

from .services.venv_manager import VirtualEnvironmentManager
from .services.dependency_handler import DependencyHandler
from .services.shell_launcher import ShellLauncher
from .core.scaffold_manager import ScaffoldManager
from .templates.template_manager import TemplateManager
from .utils.directory_snapshot import DirectorySnapshot
from .utils.directory_validator import DirectoryValidator
from .utils.command_runner import CommandRunner
from .utils.license_helper import LicenseHelper

__version__ = "1.0.0"
__all__ = [
    "VirtualEnvironmentManager",
    "DependencyHandler",
    "ShellLauncher",
    "ScaffoldManager",
    "TemplateManager",
    "DirectorySnapshot",
    "DirectoryValidator",
    "LicenseHelper",
    "CommandRunner"

]