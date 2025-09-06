"""Scaffold management for skello."""

import string
import textwrap
from typing import Dict, List, Tuple
from importlib import resources
from pathlib import Path
from datetime import datetime, date

from .models.scaffolding_types import FileType, FileRequest, StructureTemplate
from .models.scaffold_context import ScaffoldContext
from ..utils.license_helper import LicenseHelper
from ..templates.template_manager import TemplateManager


class ScaffoldManager:
    """Creates project scaffolding from a finalized plan."""

    def __init__(self):
        self.template_manager = TemplateManager()

    def execute_plan(self, context: ScaffoldContext) -> None:
        """Execute the complete scaffolding plan."""
        created_files = []
        skipped_files = []
        
        # 1. Create structure templates first
        for template in context.structures_to_create:
            if template == StructureTemplate.MAIN:
                created, name = self._create_main_structure(context)
            elif template == StructureTemplate.FULL:
                created, name = self._create_full_structure(context)
            else:
                continue
                
            if created:
                created_files.append(name)
            else:
                skipped_files.append(name)

        # 2. Create individual files (except pyproject.toml)
        pyproject_request = None
        for file_type, request in context.files_to_create.items():
            if file_type == FileType.PYPROJECT:
                pyproject_request = request  # Handle last
                continue
                
            created, filename = self._create_file(file_type, request, context)
            if created:
                created_files.append(filename)
            else:
                skipped_files.append(filename)

        # 3. Create pyproject.toml last (so it sees final state)
        if pyproject_request:
            created, filename = self._create_pyproject_toml(pyproject_request, context)
            if created:
                created_files.append(filename)
            else:
                skipped_files.append(filename)

        # 4. Report results
        self._report_summary(created_files, skipped_files)

    def _create_file(self, file_type: FileType, request: FileRequest, context: ScaffoldContext) -> Tuple[bool, str]:
        """Dispatch file creation to appropriate method."""
        if file_type == FileType.REQUIREMENTS:
            return self._create_requirements(request, context)
        elif file_type == FileType.GITIGNORE:
            return self._create_gitignore(request, context)
        elif file_type == FileType.README:
            return self._create_readme(request, context)
        elif file_type == FileType.LICENSE:
            return self._create_license(request, context)
        elif file_type == FileType.CHANGELOG:
            return self._create_changelog(request, context)
        else:
            return False, f"unknown-{file_type.value}"

    # --- File Creation Methods ---
    
    def _create_requirements(self, request: FileRequest, context: ScaffoldContext) -> Tuple[bool, str]:
        """Create requirements.txt file."""
        filename = request.get('filename', 'requirements.txt')
        content = self._get_template_content("requirements.txt.tmpl")
        
        if self._write_file(context.target_dir / filename, content):
            return True, filename
        return False, filename
    
    def _create_gitignore(self, request: FileRequest, context: ScaffoldContext) -> Tuple[bool, str]:
        """Create .gitignore file."""
        filename = request.get('filename', '.gitignore')
        template = request.get('template', 'gitignore.tmpl')
        content = self._get_template_content(template)
        
        if self._write_file(context.target_dir / filename, content):
            return True, filename
        return False, filename
    
    def _create_readme(self, request: FileRequest, context: ScaffoldContext) -> Tuple[bool, str]:
        """Create README.md file."""
        filename = request.get('filename', 'README.md')
        project_title = context.project_name.replace('-', ' ').replace('_', ' ').title()
        
        content = self._get_template_content(
            'README.md.tmpl',
            project_name=context.project_name,
            project_title=project_title,
            project_package=context.project_package
        )
        
        if self._write_file(context.target_dir / filename, content):
            return True, filename
        return False, filename
    
    def _create_license(self, request: FileRequest, context: ScaffoldContext) -> Tuple[bool, str]:
        """Create LICENSE file."""
        filename = request.get('filename', 'LICENSE')
        license_type = request.get('type', 'mit')
        author = request.get('author', 'TODO: Add your name')
        
        license_info = LicenseHelper.get_license_info(license_type)
        template_vars = {
            'current_year': datetime.now().year,
            'author_name': author,
            'project_name': context.project_name,
        }
        content = self._get_template_content(license_info['template'], **template_vars)
        
        if self._write_file(context.target_dir / filename, content):
            return True, filename
        return False, filename
    
    def _create_changelog(self, request: FileRequest, context: ScaffoldContext) -> Tuple[bool, str]:
        """Create CHANGELOG.md file."""
        filename = request.get('filename', 'CHANGELOG.md')
        
        # Build features list based on what will be created
        features = []
        if context.has_file_to_create(FileType.README):
            features.append("-\tAdded README.md documentation")
        if context.has_file_to_create(FileType.LICENSE):
            features.append("-\tAdded LICENSE file")
        if context.should_create_src():
            features.append("-\tAdded src/ package structure")
            features.append("-\tAdded main.py entry point")
        if context.should_create_tests():
            features.append("-\tAdded tests/ directory with basic test structure")
        if context.has_file_to_create(FileType.PYPROJECT):
            features.append("-\tAdded pyproject.toml configuration")
        if context.has_file_to_create(FileType.GITIGNORE):
            features.append("-\tAdded .gitignore file")
        
        changelog_features = "\n" + "\n".join(features) if features else ""
        
        content = self._get_template_content(
            'CHANGELOG.md.tmpl',
            project_name=context.project_name,
            current_date=date.today().strftime("%Y-%m-%d"),
            changelog_features=changelog_features
        )
        
        if self._write_file(context.target_dir / filename, content):
            return True, filename
        return False, filename
    
    def _create_pyproject_toml(self, request: FileRequest, context: ScaffoldContext) -> Tuple[bool, str]:
        """Create pyproject.toml file."""
        filename = "pyproject.toml"
        sections = self._build_pyproject_sections(context)
        content = self._get_template_content('pyproject.toml.tmpl', **sections)
        
        if self._write_file(context.target_dir / filename, content):
            return True, filename
        return False, filename
        
    def _build_pyproject_sections(self, context: ScaffoldContext) -> Dict:
        """Build pyproject.toml sections based on final context state."""
        # Determine license classifier
        license_type = context.license_type() or LicenseHelper.detect_license(context.target_dir)
        spdx_license = LicenseHelper.get_spdx_license(license_type)

        sections = {
            'project_name': context.project_name,
            'project_package': context.project_package
        }

        # README section
        has_readme = (context.directory_snapshot.file_exists("README.md") or 
                    context.has_file_to_create(FileType.README))
        sections['readme_section'] = (
            textwrap.dedent('''
            readme = {file = "README.md", content-type = "text/markdown"}''') if has_readme 
            else textwrap.dedent('''
            # readme = {file = "README.md", content-type = "text/markdown"}  # Uncomment when you add a README''')
        ).strip()

        # LICENSE section  
        has_license = (context.directory_snapshot.file_exists("LICENSE") or 
                    context.has_file_to_create(FileType.LICENSE))
        sections['license_section'] = (
            textwrap.dedent(f'''
            license = "{spdx_license}"
            license-files = ["LICENSE"]''') if has_license 
            else textwrap.dedent('''
            # license = {file = "LICENSE"}
            # license-files = ["LICENSE"]  # Uncomment when you add a LICENSE''')
        ).strip()

        # Helper for commenting sections
        def make_section(text: str, commented: bool = False) -> str:
            if commented:
                lines = text.splitlines()
                return "\n".join(f"# {line}" for line in lines)
            return text
            
        # Pytest section
        pytest_section = textwrap.dedent('''
            [tool.pytest.ini_options]
            testpaths = ["tests"]
            python_files = ["test_*.py", "*_test.py"]
        ''').strip()
        
        has_tests = (context.directory_snapshot.has_tests or 
                    context.should_create_tests())
        sections['pytest_section'] = make_section(pytest_section, not has_tests)
        # Update the dependency section to use pytest
        if has_tests:
            sections['dependency_section'] = textwrap.dedent('''
                dependencies = [
                    "pytest",
                ]
            ''').strip()
        else:
            sections['dependency_section'] = textwrap.dedent('''
                dependencies = [
                    # TODO: Add your project dependencies here
                    # "requests>=2.28.0",
                ]
            ''').strip()
    

        # Build section
        build_section = textwrap.dedent(f'''
            [project.scripts]
            {context.project_name} = "{context.project_package}.main:cli"
                                        
            [tool.hatch.build.targets.wheel]
            sources = ["src"]
            only-include = ["src/{context.project_package}"]
        ''').strip()
        
        has_src = (context.directory_snapshot.has_src_layout or 
                  context.should_create_src())
        sections['build_section'] = make_section(build_section, not has_src)
        
        return sections

    # --- Structure Creation Methods ---
    
    def _create_main_structure(self, context: ScaffoldContext) -> Tuple[bool, str]:
        """Create src/package/main.py structure."""
        package_dir = context.target_dir / "src" / context.project_package
        init_file = package_dir / "__init__.py"
        main_file = package_dir / "main.py"
        
        if main_file.exists():
            return False, "src/main.py structure"
            
        package_dir.mkdir(parents=True, exist_ok=True)
        init_content = self._get_template_content('main__init__.py.tmpl', 
                                                project_name=context.project_package)
        self._write_file(init_file, init_content)
        
        main_content = self._get_template_content('main.py.tmpl', 
                                                project_name=context.project_package)
        self._write_file(main_file, main_content)
       
        
        return True, "src/main.py structure"
        
    def _create_full_structure(self, context: ScaffoldContext) -> Tuple[bool, str]:
        """Create complete project structure with src/ and tests/."""
        # Create main structure first
        created_main = self._create_main_structure(context)[0]
        
        tests_dir = context.target_dir / "tests"
        tests_init = tests_dir / "__init__.py"
        test_main = tests_dir / "test_main.py"
        
        created_tests = False
        if not test_main.exists():
            tests_dir.mkdir(exist_ok=True)
            tests_init.touch()
            
            test_content = self._get_template_content('test_main.py.tmpl', 
                                                    project_name=context.project_package)
            self._write_file(test_main, test_content)
            created_tests = True
        
        if created_main or created_tests:
            return True, "full project structure"
        return False, "full project structure"

    # --- Utility Methods ---

    def _get_template_content(self, filename: str, **kwargs) -> str:
        """Read template file and substitute variables."""
        return self.template_manager.get_template_content(filename, **kwargs)

    def _write_file(self, file_path: Path, content: str) -> bool:
        """Write content to file with error handling."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"❌ Error creating {file_path.name}: {e}")
            return False

    def _report_summary(self, created: List[str], skipped: List[str]) -> None:
        """Print summary of operations."""
        if created:
            print(f"\n✅ Created: {', '.join(sorted(created))}")
        if skipped:
            print(f"⏭️  Skipped existing: {', '.join(sorted(skipped))}")