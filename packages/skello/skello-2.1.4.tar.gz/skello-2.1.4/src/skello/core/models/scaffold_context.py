from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Set

from .scaffolding_types import FileRequest, FileType, StructureTemplate
from ...utils.directory_snapshot import DirectorySnapshot


@dataclass(frozen=True)
class ScaffoldContext:
    """Immutable scaffolding plan after parsing and conflict resolution."""
    target_dir: Path
    project_name: str
    project_package: str
    
    # What to create
    files_to_create: Dict[FileType, FileRequest]
    structures_to_create: Set[StructureTemplate]
    
    # Current state
    directory_snapshot: DirectorySnapshot
    
    # Simple accessors
    def has_file_to_create(self, file_type: FileType) -> bool:
        """Check if file type will be created."""
        return file_type in self.files_to_create
    
    def has_structure_to_create(self, template: StructureTemplate) -> bool:
        """Check if structure template will be created."""
        return template in self.structures_to_create
    
    def get_file_spec(self, file_type: FileType) -> Optional[FileRequest]:
        """Get file request for creation."""
        return self.files_to_create.get(file_type)
    
    def should_create_src(self) -> bool:
        """Check if src structure should be created."""
        return (StructureTemplate.MAIN in self.structures_to_create or 
                StructureTemplate.FULL in self.structures_to_create)
    
    def should_create_tests(self) -> bool:
        """Check if tests structure should be created."""
        return StructureTemplate.FULL in self.structures_to_create
    
    # Convenience getters for file options
    def license_type(self) -> str:
        """Get license type with fallback."""
        spec = self.get_file_spec(FileType.LICENSE)
        return spec.get("type", "mit") if spec else None
    
    def license_author(self) -> str:
        """Get license author with fallback."""
        spec = self.get_file_spec(FileType.LICENSE)
        return spec.get("author", "TODO: Add your name") if spec else "TODO: Add your name"
    
    def requirements_filename(self) -> str:
        """Get requirements filename with fallback."""
        spec = self.get_file_spec(FileType.REQUIREMENTS)
        return spec.get("filename", "requirements.txt") if spec else "requirements.txt"
    
    def project_summary(self) -> str:
        """Get a project summary of the context configuration."""
        lines = [
            f"   Files to create: {[f.value for f in self.files_to_create.keys()]}",
            f"   Structures to create: {[s.value for s in self.structures_to_create]}",
            f"   Existing files: {len(self.directory_snapshot.existing_files)} files found"
        ]
        return "\n".join(lines)