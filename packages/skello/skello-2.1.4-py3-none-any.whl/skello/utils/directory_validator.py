import os
from pathlib import Path
from typing import List


class DirectoryValidationError(Exception):
    """Raised when directory validation fails."""
    pass


class DirectoryValidator:

    # Only a few names are actually problematic
    RESERVED_PACKAGE_NAMES = {
        'test',      # Python's built-in test module
        'tests',     # Common testing directory name
        'src',       # Source directory name (causes circular issues)
        'lib',       # Library directory name  
        'main',      # Entry point conflicts
        'setup',     # Setup.py conflicts
        'sys',       # System module
        'os',        # Operating system module
        'json',      # JSON module
        'typing',    # Typing module
        'collections', # Collections module
        'itertools', # Itertools module
    }

    def __init__(self, target_dir: Path):
        self.target_dir = target_dir
        self.validation_errors: List[str] = []

    def validate_package_name(self, package_name: str) -> str:
        """
        Validate that package name won't cause import conflicts.
        
        Args:
            package_name: The proposed package name to validate
            
        Returns:
            str: The original package name if safe, or a safe alternative if conflicts.
                 Returns empty string if no safe alternative can be generated.
        """
        # If package name is already safe, return it as-is
        if package_name.lower() not in self.RESERVED_PACKAGE_NAMES:
            return package_name
        
        # Generate safe alternatives
        safe_alternatives = [
            f"{package_name}_app",
            f"{package_name}_pkg",
            f"{package_name}_tool",
            f"my_{package_name}",
        ]
        
        # Find first safe alternative
        for alternative in safe_alternatives:
            if alternative.lower() not in self.RESERVED_PACKAGE_NAMES:
                self.validation_errors.append(
                    f"Package name '{package_name}' conflicts with Python built-in names. "
                    f"Using '{alternative}' instead."
                )
                return alternative
        
        # If we can't find a safe alternative (shouldn't happen), return empty string
        self.validation_errors.append(
            f"Package name '{package_name}' conflicts and no safe alternative found."
        )
        return ""

    def validate_target_directory(self) -> bool:
        """
        Validates the target directory for project setup.
        
        Returns:
            bool: True if directory is valid, False otherwise
            
        Side effects:
            Populates self.validation_errors with any issues found
        """
        self.validation_errors.clear()
        
        try:
            # Check if directory exists
            if self.target_dir.exists():
                return self._validate_existing_directory()
            else:
                # Directory doesn't exist - validate we can create it
                return self._validate_parent_directory()
            
        except (OSError, PermissionError) as e:
            self.validation_errors.append(f"System error accessing directory: {e}")
            return False
    
    def _validate_existing_directory(self) -> bool:
        """Validate an existing directory."""
        is_valid = True
        
        # Check if it's actually a directory
        if not self.target_dir.is_dir():
            self.validation_errors.append(f"Path exists but is not a directory: {self.target_dir}")
            return False
        
        # Check read permissions
        if not os.access(self.target_dir, os.R_OK):
            self.validation_errors.append(f"No read permission for directory: {self.target_dir}")
            is_valid = False
        
        # Check write permissions
        if not os.access(self.target_dir, os.W_OK):
            self.validation_errors.append(f"No write permission for directory: {self.target_dir}")
            is_valid = False
        
        # Check execute permissions (needed to traverse directory)
        if not os.access(self.target_dir, os.X_OK):
            self.validation_errors.append(f"No execute permission for directory: {self.target_dir}")
            is_valid = False
        
        # Check available disk space (at least 100MB recommended)
        if not self._check_disk_space():
            is_valid = False
        
        return is_valid

    def _validate_parent_directory(self) -> bool:
        """Validate parent directory when creating new directory."""
        parent_dir = self.target_dir.parent
        is_valid = True
        
        # Check if parent exists
        if not parent_dir.exists():
            self.validation_errors.append(f"Parent directory does not exist: {parent_dir}")
            return False
        
        # Check if parent is actually a directory
        if not parent_dir.is_dir():
            self.validation_errors.append(f"Parent path exists but is not a directory: {parent_dir}")
            return False
        
        # Check parent permissions
        if not os.access(parent_dir, os.W_OK):
            self.validation_errors.append(f"No write permission in parent directory: {parent_dir}")
            is_valid = False
        
        if not os.access(parent_dir, os.X_OK):
            self.validation_errors.append(f"No execute permission in parent directory: {parent_dir}")
            is_valid = False
        
        # Check if target name would conflict with existing file
        if self.target_dir.exists() and not self.target_dir.is_dir():
            self.validation_errors.append(f"Target exists as file, not directory: {self.target_dir}")
            is_valid = False
        
        # Check available disk space
        if not self._check_disk_space(check_parent=True):
            is_valid = False
        
        return is_valid
    
    def _check_disk_space(self, min_space_mb: int = 100, check_parent: bool = False) -> bool:
        """Check if there's sufficient disk space."""
        try:
            check_path = self.target_dir.parent if check_parent else self.target_dir
            stat_result = os.statvfs(check_path)
            
            # Calculate free space in MB
            free_space_bytes = stat_result.f_bavail * stat_result.f_frsize
            free_space_mb = free_space_bytes / (1024 * 1024)
            
            if free_space_mb < min_space_mb:
                self.validation_errors.append(
                    f"Insufficient disk space: {free_space_mb:.1f}MB available, "
                    f"{min_space_mb}MB required"
                )
                return False
            
            return True
            
        except (OSError, AttributeError):
            # os.statvfs not available on Windows, or other OS error
            # Skip disk space check rather than failing
            return True

    def create_directory_if_valid(self) -> bool:
        """
        Validate and create the target directory if it doesn't exist.
        
        Returns:
            bool: True if directory exists or was created successfully
        """
        if not self.validate_target_directory():
            return False
        
        # If directory already exists and is valid, we're good
        if self.target_dir.exists():
            return True
        
        # Try to create the directory
        try:
            self.target_dir.mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError) as e:
            self.validation_errors.append(f"Failed to create directory: {e}")
            return False

    def get_validation_summary(self) -> str:
        """Get a formatted summary of validation results."""
        if not self.validation_errors:
            return "✅ Directory validation passed"
        
        summary = "❌ Directory validation failed:\n"
        for i, error in enumerate(self.validation_errors, 1):
            summary += f"   {i}. {error}\n"
        
        return summary.rstrip()

    def raise_if_invalid(self) -> None:
        """Raise DirectoryValidationError if validation failed."""
        if not self.validate_target_directory():
            raise DirectoryValidationError(f"Directory validation failed: {self.validation_errors}")
    
    def get_directory_info(self) -> dict:
        """Get detailed information about the directory."""
        info = {
            'path': str(self.target_dir),
            'exists': self.target_dir.exists(),
            'is_directory': self.target_dir.is_dir() if self.target_dir.exists() else None,
            'readable': os.access(self.target_dir, os.R_OK) if self.target_dir.exists() else None,
            'writable': os.access(self.target_dir, os.W_OK) if self.target_dir.exists() else None,
            'executable': os.access(self.target_dir, os.X_OK) if self.target_dir.exists() else None,
        }
        
        # Add parent directory info if target doesn't exist
        if not self.target_dir.exists():
            parent = self.target_dir.parent
            info['parent_exists'] = parent.exists()
            info['parent_writable'] = os.access(parent, os.W_OK) if parent.exists() else None
        
        # Add disk space info
        try:
            check_path = self.target_dir if self.target_dir.exists() else self.target_dir.parent
            if check_path.exists():
                stat_result = os.statvfs(check_path)
                free_space_bytes = stat_result.f_bavail * stat_result.f_frsize
                info['free_space_mb'] = round(free_space_bytes / (1024 * 1024), 1)
        except (OSError, AttributeError):
            info['free_space_mb'] = None
        
        return info