import json
import os
from pathlib import Path


class ConfigLoader:
    """Load and save configuration files in multiple formats.
    
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
            IOError: If file cannot be read or parsed.
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {suffix}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError as e:
            raise IOError(f"Failed to read config file: {filepath}") from e
        
        if suffix in ('.yaml', '.yml'):
            return self._parse_yaml(content, filepath)
        elif suffix == '.toml':
            return self._parse_toml(content, filepath)
        elif suffix == '.json':
            return self._parse_json(content, filepath)
        
        return {}
    
    def load_with_defaults(self, filepath, defaults=None):
        """Load a configuration file with fallback to defaults.
        
        If the file does not exist or cannot be parsed, returns the
        provided defaults. Useful for optional configuration files.
        
        Args:
            filepath: Path to the configuration file.
            defaults: Default configuration dictionary to use if load fails.
                     Defaults to empty dict if not provided.
            
        Returns:
            dict: Parsed configuration data or defaults.
        """
        if defaults is None:
            defaults = {}
        
        try:
            return self.load(filepath)
        except (FileNotFoundError, ValueError, IOError):
            return defaults
    
    def get(self, config, key, default=None):
        """Get a nested value from configuration using dot notation.
        
        Supports accessing nested dictionary values using dot-separated
        keys. For example, 'database.host' will access config['database']['host'].
        
        Args:
            config: Configuration dictionary to search.
            key: Key path using dot notation (e.g., 'section.subsection.key').
            default: Value to return if key is not found. Defaults to None.
            
        Returns:
            The value at the specified key path, or default if not found.
        """
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
