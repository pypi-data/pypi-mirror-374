from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

# ==============================================================================
# Core Enums
# ==============================================================================
class FileType(Enum):
    """File types that can be created."""
    LICENSE = "license"
    REQUIREMENTS = "requirements"
    PYPROJECT = "pyproject"
    GITIGNORE = "gitignore"
    README = "readme"
    CHANGELOG = "changelog"


class StructureTemplate(Enum):
    """Project structure templates."""
    MAIN = "main"        # Creates src/package/main.py structure
    FULL = "full"        # Creates complete project structure
    ALL = "all"          # Creates all files + full structure

# ==============================================================================
# File Request (simplified from FileSpec)
# ==============================================================================

@dataclass
class FileRequest:
    """A parsed file creation request with options."""
    file_type: FileType
    options: Dict[str, str] = field(default_factory=dict)
    
    def get(self, key: str, default: str = None) -> str:
        """Get option value."""
        return self.options.get(key, default)