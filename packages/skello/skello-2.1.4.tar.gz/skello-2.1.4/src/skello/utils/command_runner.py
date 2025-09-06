"""Utility classes and functions for skello."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

    
class CommandRunner:
    """Handles running subprocess commands safely with error handling."""
    
    @staticmethod
    def run_command(executable: Path, command: List[str], cwd: Optional[Path] = None) -> None:
        """
        Runs a command using the specified executable.
        
        Args:
            executable: Path to the executable (e.g., Python interpreter)
            command: List of command arguments
            cwd: Working directory for the command
            
        Raises:
            SystemExit: If command fails or executable not found
        """
        full_command = [str(executable)] + command
        
        try:
            subprocess.check_call(full_command, cwd=cwd)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running command: {' '.join(command)}")
            print(f"   Executable: {executable}")
            if cwd:
                print(f"   Working directory: {cwd}")
            print(f"   Error: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print(f"❌ Error: Could not find executable at '{executable}'")
            sys.exit(1)
    
    @staticmethod
    def run_command_with_output(command: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """
        Runs a command and returns the result with captured output.
        
        Args:
            command: List of command arguments
            cwd: Working directory for the command
            
        Returns:
            CompletedProcess object with stdout, stderr, and return code
        """
        try:
            return subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                check=False  # Don't raise on non-zero exit
            )
        except FileNotFoundError as e:
            print(f"❌ Error: Command not found: {' '.join(command)}")
            raise e


def get_python_executable(venv_dir: Path) -> Path:
    """
    Gets the path to the Python executable in the virtual environment.
    
    Args:
        venv_dir: Path to the virtual environment directory
        
    Returns:
        Path to the Python executable
    """
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"