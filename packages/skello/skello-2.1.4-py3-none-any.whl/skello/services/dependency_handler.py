"""Dependency detection and installation for easy-venv."""

from pathlib import Path

from ..utils.directory_snapshot import DirectorySnapshot
from ..utils.command_runner import CommandRunner
from .venv_manager import VirtualEnvironmentManager


class DependencyHandler:
    """Handles detection and installation of project dependencies."""
    
    def __init__(self, target_dir: Path, venv_manager: VirtualEnvironmentManager):
        """
        Initialize dependency handler.
        
        Args:
            venv_manager: Virtual environment manager instance
            snapshot: Directory Snapshot instance
        """
        self.target_dir = target_dir
        self.venv_manager = venv_manager
        self._command_runner = CommandRunner()
       
    def detect_and_install(self) -> None:
        """
        Detects dependency files and installs dependencies accordingly.
        
        Args:
            requirements_filename: Name of requirements file to create if none found
        """
        dependency_files = DirectorySnapshot.find_dependency_files(self.target_dir)
        
        # Check if dependency files exist in order of preference
        if dependency_files['pyproject.toml']:
            self._install_from_pyproject(dependency_files['pyproject.toml'])
        elif dependency_files['requirements.txt']:
            self._install_from_requirements(dependency_files['requirements.txt'])
        elif dependency_files['Pipfile']:
            self._install_from_pipfile(dependency_files['Pipfile'])
        elif dependency_files['environment.yml']:
            self._handle_conda_env()
        else:
            self._handle_no_dependencies()
    
    def _install_from_pyproject(self, pyproject_file: Path) -> None:
        """Installs dependencies from pyproject.toml file."""
        print(f"📦 Found pyproject.toml - installing project in editable mode...")
        
        try:
            # Install the project in editable mode
            self.venv_manager.run_in_venv(["-m", "pip", "install", "-e", "."])
        except Exception as e:
            print(f"⚠️  Warning: Failed to install from pyproject.toml. Trying pip install anyway...")
            self.venv_manager.run_in_venv(["-m", "pip", "install", "-e", str(self.target_dir)])
    
    def _install_from_requirements(self, requirements_file: Path) -> None:
        """Attempts to install dependencies from requirements.txt file."""
        if DirectorySnapshot.is_file_empty(requirements_file):
            print(f"🤔 Found empty requirements.txt - nothing to install")
            return
        
        print(f"📦 Installing dependencies from requirements.txt...")
        self.venv_manager.run_in_venv(["-m", "pip", "install", "-r", str(requirements_file)])
    
    def _install_from_pipfile(self, pipfile: Path) -> None:
        """Attempts to install dependencies from Pipfile."""
        print(f"📦 Found Pipfile - attempting to extract requirements...")
        
        try:
            # Try to use pipenv to generate requirements
            result = self._command_runner.run_command_with_output(
                ["pipenv", "requirements"], 
                cwd=self.target_dir
            )
            
            if result.returncode == 0:
                # Create temporary requirements file from pipenv output
                temp_req = self.target_dir / ".temp_requirements.txt"
                with open(temp_req, 'w') as f:
                    f.write(result.stdout)
                
                self.venv_manager.run_in_venv(["-m", "pip", "install", "-r", str(temp_req)])
                temp_req.unlink()  # Clean up
                print(f"✅ Installed dependencies from Pipfile")
            else:
                print(f"⚠️  Found Pipfile but pipenv not available. Consider converting to requirements.txt or pyproject.toml")
                
        except FileNotFoundError:
            print(f"⚠️  Found Pipfile but pipenv not installed. Consider converting to requirements.txt or pyproject.toml")
    
    def _handle_conda_env(self) -> None:
        """Handles conda environment.yml files."""
        print(f"⚠️  Found environment.yml (conda file) - this tool works with pip. Consider creating pyproject.toml or requirements.txt")
    
    def _handle_no_dependencies(self) -> None:
        """Handles case when no dependency files are found."""
        print(f"📭 No dependency files found - skipping package installation")
        print(f"   Looked for: pyproject.toml, requirements.txt, Pipfile, environment.yml")
        print(f"   Use --create p to generate a pyproject file")
    
    def install_package(self, package_name: str, dev: bool = False) -> None:
        """
        Installs a single package in the virtual environment.
        
        Args:
            package_name: Name of the package to install
            dev: Whether this is a development dependency
        """
        print(f"📦 Installing {package_name}...")
        command = ["-m", "pip", "install", package_name]
        self.venv_manager.run_in_venv(command)
    
    def install_from_file(self, requirements_file: Path) -> None:
        """
        Installs dependencies from a specific requirements file.
        
        Args:
            requirements_file: Path to requirements file
        """
        if not requirements_file.exists():
            print(f"❌ Requirements file not found: {requirements_file}")
            return
        
        if DirectorySnapshot.is_file_empty(requirements_file):
            print(f"🤔 Requirements file is empty: {requirements_file}")
            return
        
        print(f"📦 Installing dependencies from {requirements_file.name}...")
        self.venv_manager.run_in_venv(["-m", "pip", "install", "-r", str(requirements_file)])