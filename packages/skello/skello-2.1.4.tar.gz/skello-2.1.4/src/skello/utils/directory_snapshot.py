from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Set


@dataclass
class DirectorySnapshot:
    """Snapshot of existing directory structure."""
    target_dir: Path
    existing_files: Set[str] = field(default_factory=set)
    has_src_layout: bool = False
    has_tests: bool = False
    
    @classmethod
    def scan(cls, target_dir: Path) -> 'DirectorySnapshot':
        """Scan directory and create snapshot."""
        snapshot = cls(target_dir=target_dir)
        
        # Check for common project files
        common_files = [
            "pyproject.toml", "requirements.txt", "README.md", 
            "LICENSE", ".gitignore", "CHANGELOG.md"
        ]
        
        for filename in common_files:
            if (target_dir / filename).exists():
                snapshot.existing_files.add(filename)
        
        # Check for project structure
        if (target_dir / "src").is_dir():
            snapshot.has_src_layout = True
        if (target_dir / "tests").is_dir():
            snapshot.has_tests = True
            
        return snapshot
    
    def file_exists(self, filename: str) -> bool:
        """Check if file exists in snapshot."""
        return filename in self.existing_files
    
    @classmethod
    def find_dependency_files(self, target_dir: Path) -> Dict[str, Optional[Path]]:
        """
        Searches for common dependency files in the target directory.
        
        Returns:
            Dictionary mapping file types to their paths (or None if not found)
        """
        dependency_files = {
            'pyproject.toml': target_dir / "pyproject.toml",
            'requirements.txt': target_dir / "requirements.txt", 
            'Pipfile': target_dir / "Pipfile",
            'environment.yml': target_dir / "environment.yml"
        }
        
        return {
            name: path if path.exists() else None 
            for name, path in dependency_files.items()
        }
    
    @classmethod
    def get_file_size(self, file_path: Path) -> int:
        """Gets the size of a file in bytes."""
        try:
            return file_path.stat().st_size if file_path.exists() else 0
        except OSError:
            return 0
        
    @classmethod
    def is_file_empty(self, file_path: Path) -> bool:
        """Checks if a file is empty (0 bytes)."""
        return self.get_file_size(file_path) == 0