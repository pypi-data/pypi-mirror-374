"""Virtual environment management for skello."""

import venv
from pathlib import Path
from typing import Optional

from ..utils.command_runner import CommandRunner, get_python_executable


class VirtualEnvironmentManager:
    """Manages virtual environment creation and configuration."""
    
    def __init__(self, target_dir: Path, venv_name: str = ".venv"):
        """
        Initialize the virtual environment manager.
        
        Args:
            target_dir: Directory where the virtual environment will be created
            venv_name: Name of the virtual environment folder
        """
        self.target_dir = target_dir
        self.venv_name = venv_name
        self.venv_dir = target_dir / venv_name
        self.python_executable = get_python_executable(self.venv_dir)
        self._command_runner = CommandRunner()
    
    def create_environment(self) -> bool:
        """
        Creates the virtual environment if it doesn't exist.
        
        Returns:
            True if environment was created, False if it already existed
        """
        if self.exists():
            print(f"✅ Virtual environment '{self.venv_dir}' already exists. Skipping creation.")
            return False
        
        print(f"🌱 Creating virtual environment in '{self.venv_dir}'...")
        try:
            venv.create(self.venv_dir, with_pip=True)
            return True
        except Exception as e:
            print(f"❌ Error creating virtual environment: {e}")
            raise
    
    def upgrade_pip(self) -> None:
        """Upgrades pip in the virtual environment to the latest version."""
        print("🔧 Upgrading pip...")
        self._command_runner.run_command(
            self.python_executable, 
            ["-m", "pip", "install", "--upgrade", "pip"],
            cwd=self.target_dir
        )
    
    def exists(self) -> bool:
        """
        Checks if the virtual environment already exists.
        
        Returns:
            True if virtual environment directory exists, False otherwise
        """
        return self.venv_dir.exists() and self.venv_dir.is_dir()
    
    def get_activation_scripts(self) -> dict[str, Optional[Path]]:
        """
        Gets paths to activation scripts for different shells.
        
        Returns:
            Dictionary mapping shell types to activation script paths
        """
        if not self.exists():
            return {}
        
        scripts = {}
        
        if self.python_executable.name.endswith('.exe'):  # Windows
            scripts_dir = self.venv_dir / "Scripts"
            scripts.update({
                'powershell': scripts_dir / "Activate.ps1",
                'cmd': scripts_dir / "activate.bat"
            })
        else:  # Unix-like
            bin_dir = self.venv_dir / "bin"
            scripts.update({
                'bash': bin_dir / "activate",
                'fish': bin_dir / "activate.fish",
                'csh': bin_dir / "activate.csh"
            })
        
        # Return only existing scripts
        return {
            shell: path if path.exists() else None 
            for shell, path in scripts.items()
        }
    
    def run_in_venv(self, command: list[str], cwd: Optional[Path] = None) -> None:
        """
        Runs a command in the virtual environment.
        
        Args:
            command: Command to run (without python executable)
            cwd: Working directory for the command
        """
        work_dir = cwd or self.target_dir
        self._command_runner.run_command(self.python_executable, command, work_dir)
    
    def get_info(self) -> dict[str, str]:
        """
        Gets information about the virtual environment.
        
        Returns:
            Dictionary with virtual environment information
        """
        return {
            'venv_dir': str(self.venv_dir),
            'python_executable': str(self.python_executable),
            'target_dir': str(self.target_dir),
            'exists': self.exists()
        }