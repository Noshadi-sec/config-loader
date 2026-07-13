import os
from pathlib import Path


class ConfigLoader:
    """Load configuration files in multiple formats.
    
    Supports YAML, TOML, and JSON formats with automatic detection
    based on file extension.
    """
    
    SUPPORTED_FORMATS = ('.yaml', '.yml', '.toml', '.json')
    
    def load(self, filepath):
        """Load a configuration file.
        
        Args:
            filepath: Path to the configuration file.
            
        Returns:
            dict: Parsed configuration data.
            
        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If format is not supported.
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {suffix}")
        
        # TODO: Implement format-specific parsers
        return {}
