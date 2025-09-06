from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .scaffold_context import ScaffoldContext
from .scaffolding_types import FileRequest, FileType, StructureTemplate
from ...utils.directory_snapshot import DirectorySnapshot
from ...utils.directory_validator import DirectoryValidationError, DirectoryValidator

# ==============================================================================
# CLI Handler - Entry Point
# ==============================================================================

@dataclass
class CLIHandler:
    """Main entry point for parsing CLI arguments and building scaffold context."""
    target_dir: Path
    project_name: str
    project_package: str
    
    # Parsed from CLI
    requested_files: Dict[FileType, FileRequest] = field(default_factory=dict)
    requested_structures: Set[StructureTemplate] = field(default_factory=set)
    
    # Config data
    _FILE_CONFIGS = {
        FileType.LICENSE: {
            "aliases": ["l", "lic"],
            "option_keys": ["type", "author", "filename"]
        },
        FileType.REQUIREMENTS: {
            "aliases": ["r", "req"], 
            "option_keys": ["filename"]
        },
        FileType.PYPROJECT: {
            "aliases": ["p", "toml"],
            "option_keys": []
        },
        FileType.GITIGNORE: {
            "aliases": ["g", "git"],
            "option_keys": []
        },
        FileType.README: {
            "aliases": ["md", "read"],
            "option_keys": []
        },
        FileType.CHANGELOG: {
            "aliases": ["ch", "log"],
            "option_keys": []
        },
    }
    
    _STRUCTURE_ALIASES = {
        "m": StructureTemplate.MAIN, "main": StructureTemplate.MAIN,
        "f": StructureTemplate.FULL, "full": StructureTemplate.FULL,
        "*": StructureTemplate.ALL, "all": StructureTemplate.ALL,
    }
    
    @classmethod
    def from_cli(cls, target_path: Path, create_args: List[str] = None) -> 'CLIHandler':
        """Create CLIHandler from command line arguments - main entry point."""
        # Extract project info from path
        name = target_path.name if target_path.name != "." else target_path.resolve().name
        package = name.replace("-", "_").replace(" ", "_").lower()
        
        # Create validator for both directory and package validation
        validator = DirectoryValidator(target_path)
        
        # Validate target directory before proceeding
        if not validator.validate_target_directory():
            error_summary = validator.get_validation_summary()
            raise DirectoryValidationError(f"Cannot proceed invalid directory:\n{error_summary}")
        
        # [Shadowing issues] Validate and fix package name if needed
        safe_package = validator.validate_package_name(package)
        
        if not safe_package:
            # This should rarely happen, but handle it gracefully
            raise ValueError(f"Cannot create safe package name for '{package}'")
        
        # Show warning if package name was changed
        if safe_package != package:
            print(f"⚠️  Package name '{package}' conflicts with Python built-ins.")
            print(f"   Using '{safe_package}' instead to avoid import issues.")
        
        # Create handler instance with the safe package name
        handler = cls(
            target_dir=target_path,
            project_name=name,  # Keep original project name
            project_package=safe_package  # Use safe package name
        )
        
        # Parse CLI arguments
        if create_args:
            handler._parse_arguments(create_args)
        
        return handler
    
    def _parse_arguments(self, args: List[str]) -> None:
        """Parse CLI arguments into files and structures."""
        for arg in args:
            file_req, structure = self._parse_single_arg(arg)
            
            if structure == StructureTemplate.ALL:
                # ALL = full structure + all files
                self.requested_structures.add(StructureTemplate.FULL)
                self._add_all_file_types()
            elif structure:
                self.requested_structures.add(structure)
            elif file_req:
                self.requested_files[file_req.file_type] = file_req
            else:
                print(f"⚠️ Unknown argument: {arg}")
    
    def _parse_single_arg(self, arg_str: str) -> Tuple[Optional[FileRequest], Optional[StructureTemplate]]:
        """Parse a single CLI argument into FileRequest or StructureTemplate."""
        parts = arg_str.split(':', 1)
        alias = parts[0]
        option_string = parts[1] if len(parts) > 1 else None
        
        # Check structure templates first
        if alias in self._STRUCTURE_ALIASES:
            return None, self._STRUCTURE_ALIASES[alias]
        
        # Check file types
        for file_type, config in self._FILE_CONFIGS.items():
            if alias in config["aliases"]:
                options = {}
                if option_string and config["option_keys"]:
                    option_values = option_string.split(':')
                    options = {
                        key: value for key, value in 
                        zip(config["option_keys"], option_values) if value
                    }
                return FileRequest(file_type=file_type, options=options), None
        
        return None, None
    
    def _add_all_file_types(self) -> None:
        """Add all file types to requested files."""
        for file_type in FileType:
            if file_type not in self.requested_files:
                self.requested_files[file_type] = FileRequest(file_type=file_type)
    
    def build_context(self) -> ScaffoldContext:
        """Build the immutable scaffold context with conflict resolution."""
        # 1. Scan directory
        snapshot = DirectorySnapshot.scan(self.target_dir)
        
        # 2. Apply prioritization rules
        final_files = self._apply_prioritization(self.requested_files, snapshot)
        
        # 3. Remove files that already exist (conflict resolution)
        safe_files = {}
        for file_type, req in final_files.items():
            if self._file_would_conflict(file_type, req, snapshot):
                print(f"⏭️  Skipped {file_type} – it already exists in the directory")
            else:
                safe_files[file_type] = req
        
        # 4. Create immutable context
        return ScaffoldContext(
            target_dir=self.target_dir,
            project_name=self.project_name,
            project_package=self.project_package,
            files_to_create=safe_files,
            structures_to_create=self.requested_structures,
            directory_snapshot=snapshot
        )
    
    def _apply_prioritization(self, files: Dict[FileType, FileRequest], 
                             snapshot: DirectorySnapshot) -> Dict[FileType, FileRequest]:
        """Apply prioritization rules (pyproject over requirements, etc)."""
        final_files = files.copy()
        
        # If pyproject.toml exists or is requested, remove requirements.txt
        has_pyproject_spec = FileType.PYPROJECT in final_files
        has_pyproject_file = snapshot.file_exists("pyproject.toml")
        
        if has_pyproject_spec or has_pyproject_file:
            if FileType.REQUIREMENTS in final_files:
                del final_files[FileType.REQUIREMENTS]
                print("📝 Note: Prioritizing pyproject.toml over requirements.txt.")
        
        return final_files
    
    def _file_would_conflict(self, file_type: FileType, req: FileRequest, 
                            snapshot: DirectorySnapshot) -> bool:
        """Check if creating this file would conflict with existing files."""
        filename = self._get_filename_for_type(file_type, req)
        return snapshot.file_exists(filename) if filename else False
    
    def _get_filename_for_type(self, file_type: FileType, req: FileRequest) -> Optional[str]:
        """Get the filename that would be created for a file type."""
        filename_map = {
            FileType.LICENSE: req.get("filename", "LICENSE"),
            FileType.REQUIREMENTS: req.get("filename", "requirements.txt"),
            FileType.GITIGNORE: req.get("filename", ".gitignore"),
            FileType.README: req.get("filename", "README.md"),
            FileType.CHANGELOG: req.get("filename", "CHANGELOG.md"),
            FileType.PYPROJECT: "pyproject.toml",
        }
        return filename_map.get(file_type)
