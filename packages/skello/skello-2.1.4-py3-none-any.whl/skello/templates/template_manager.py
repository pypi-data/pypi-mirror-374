import string
from importlib import resources
from pathlib import Path
from typing import Dict, Optional

class TemplateManager:
    """Manages template loading from organized subdirectories."""
    
    def __init__(self):
        self.templates_root = resources.files('skello.templates')
        
        # Map template categories to subdirectories
        self.template_locations = {
            'project': self.templates_root / 'project',
            'licenses': self.templates_root / 'licenses',
        }
    
    def get_template_content(self, filename: str, **kwargs) -> str:
        """Load and process template with variable substitution."""
        template_path = self._resolve_template_path(filename)
        
        if not template_path:
            raise FileNotFoundError(f"Template '{filename}' not found")
        
        template_content = template_path.read_text(encoding='utf-8')
        template = string.Template(template_content)
        return template.safe_substitute(**kwargs)
    
    def _resolve_template_path(self, filename: str) -> Optional[Path]:
        """Find template file in appropriate subdirectory."""
        
        # License templates
        if filename.startswith('LICENSE_'):
            candidate = self.template_locations['licenses'] / filename
            if self._template_exists(candidate):
                return candidate
        
        # Project templates  
        candidate = self.template_locations['project'] / filename
        if self._template_exists(candidate):
            return candidate
            
        return None
    
    def _template_exists(self, template_path: Path) -> bool:
        """Check if template file exists."""
        try:
            template_path.read_text(encoding='utf-8')
            return True
        except (FileNotFoundError, IsADirectoryError):
            return False
    
    def list_available_templates(self) -> Dict[str, list]:
        """List all available templates by category."""
        templates = {}
        
        for category, location in self.template_locations.items():
            try:
                templates[category] = [
                    f.name for f in location.iterdir() 
                    if f.is_file() and f.suffix == '.tmpl'
                ]
            except (FileNotFoundError, OSError):
                templates[category] = []
        
        return templates