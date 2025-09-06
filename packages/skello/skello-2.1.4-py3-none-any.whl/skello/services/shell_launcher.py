"""Shell launching utilities for skello."""

import shlex
import subprocess
import sys
import textwrap
from pathlib import Path

from .venv_manager import VirtualEnvironmentManager


class ShellLauncher:
    """Handles launching activated shell sessions across different platforms."""
    
    def __init__(self, venv_manager: VirtualEnvironmentManager):
        """
        Initialize shell launcher.
        
        Args:
            venv_manager: Virtual environment manager instance
        """
        self.venv_manager = venv_manager
        self.target_dir = venv_manager.target_dir
        self.venv_dir = venv_manager.venv_dir
    
    def launch_activated_shell(self) -> None:
        """Launches a new shell with the virtual environment already activated."""
        if not self.venv_manager.exists():
            print("❌ Virtual environment does not exist. Cannot launch shell.")
            return
        
        try:
            if sys.platform == "win32":
                self._launch_windows_shell()
            else:
                self._launch_unix_shell()
            
            print("👋 Returned from activated shell session.")
            
        except Exception as e:
            print(f"❌ Error launching activated shell: {e}")
            self._show_manual_instructions()
    
    def _launch_windows_shell(self) -> None:
        """Launches Windows shell (PowerShell or Command Prompt)."""
        activation_scripts = self.venv_manager.get_activation_scripts()
        
        # Try PowerShell first
        if activation_scripts.get('powershell'):
            self._launch_powershell(activation_scripts['powershell'])
        elif activation_scripts.get('cmd'):
            self._launch_cmd(activation_scripts['cmd'])
        else:
            raise FileNotFoundError("No Windows activation scripts found.")
    
    def _launch_powershell(self, activate_script: Path) -> None:
        """Launches PowerShell with virtual environment activated."""
        powershell_command = textwrap.dedent(f'''
            Set-Location "{self.target_dir}"
            try {{
                & "{activate_script}"
                Write-Host "🎉 Virtual environment activated in new shell!" -ForegroundColor Green
                Write-Host "📁 Current directory: {self.target_dir}" -ForegroundColor Cyan
            }} catch {{
                Write-Host "⚠️ PowerShell activation failed." -ForegroundColor Yellow
            }}
            Write-Host "✨ You can now work in your activated environment. Type 'exit' to return." -ForegroundColor Yellow
        ''')
        
        print("🚀 Launching new PowerShell session...")
        try:
            subprocess.run(
                ["powershell.exe", "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", powershell_command],
                cwd=self.target_dir,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ PowerShell failed or not found, trying Command Prompt...")
            if self.venv_manager.get_activation_scripts().get('cmd'):
                self._launch_cmd(self.venv_manager.get_activation_scripts()['cmd'])
    
    def _launch_cmd(self, activate_script: Path) -> None:
        """Launches Command Prompt with virtual environment activated."""
        cmd_command = f'cd /d "{self.target_dir}" && "{activate_script}" && echo 🎉 Virtual environment activated! && cmd /k'
        
        print("🚀 Launching new Command Prompt session...")
        subprocess.run(["cmd", "/c", cmd_command], cwd=self.target_dir)
    
    def _launch_unix_shell(self) -> None:
        """Launches Unix shell (bash) with virtual environment activated."""
        activation_scripts = self.venv_manager.get_activation_scripts()
        activate_script = activation_scripts.get('bash')
        
        if not activate_script:
            raise FileNotFoundError(f"Activation script not found for Unix shell")
        
        # Use shlex.quote() for security against command injection
        safe_target_dir = shlex.quote(str(self.target_dir))
        safe_activate_script = shlex.quote(str(activate_script))
        
        bash_command = textwrap.dedent(f'''
            cd {safe_target_dir}
            source {safe_activate_script}
            echo "🎉 Virtual environment activated in new shell!"
            echo "📁 Current directory: {self.target_dir}"
            echo "✨ You can now work in your activated environment. Type 'exit' to return."
            exec bash
        ''')
        
        print("🚀 Launching new shell session...")
        subprocess.run(["bash", "-c", bash_command], cwd=self.target_dir)
    
    def get_manual_activation_instructions(self) -> str:
        """
        Gets manual activation instructions for the current platform.
        
        Returns:
            String with platform-specific activation instructions
        """
        if not self.venv_manager.exists():
            return "❌ Virtual environment does not exist."
        
        activation_scripts = self.venv_manager.get_activation_scripts()
        instructions = ["📋 Manual activation instructions:"]
        
        if sys.platform == "win32":
            if activation_scripts.get('powershell'):
                instructions.append(f"   PowerShell: & '{activation_scripts['powershell']}'")
            if activation_scripts.get('cmd'):
                instructions.append(f"   Cmd.exe:    \"{activation_scripts['cmd']}\"")
        else:
            if activation_scripts.get('bash'):
                instructions.append(f"   Terminal: source '{activation_scripts['bash']}'")
        
        instructions.append(f"   Then navigate to: cd \"{self.target_dir}\"")
        
        return "\n".join(instructions)
    
    def _show_manual_instructions(self) -> None:
        """Shows manual activation instructions when auto-launch fails."""
        print(self.get_manual_activation_instructions())
        print(f"\n📁 Paths:")
        print(f"   Virtual environment: {self.venv_dir}")
        print(f"   Project directory: {self.target_dir}")