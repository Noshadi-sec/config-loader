import json
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
    
    def _parse_yaml(self, content, filepath):
        """Parse YAML content.
        
        Args:
            content: YAML content as string.
            filepath: Path to file for error reporting.
            
        Returns:
            dict: Parsed YAML data.
            
        Raises:
            ImportError: If PyYAML is not installed.
            IOError: If YAML parsing fails.
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML support. "
                "Install it with: pip install pyyaml"
            )
        
        try:
            data = yaml.safe_load(content)
            return data if isinstance(data, dict) else {}
        except yaml.YAMLError as e:
            raise IOError(f"Failed to parse YAML file {filepath}: {e}") from e
    
    def _parse_toml(self, content, filepath):
        """Parse TOML content.
        
        Args:
            content: TOML content as string.
            filepath: Path to file for error reporting.
            
        Returns:
            dict: Parsed TOML data.
            
        Raises:
            ImportError: If toml is not installed.
            IOError: If TOML parsing fails.
        """
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                raise ImportError(
                    "TOML support requires Python 3.11+ or tomli library. "
                    "Install it with: pip install tomli"
                )
        
        try:
            if hasattr(tomllib, 'loads'):
                data = tomllib.loads(content)
            else:
                data = tomllib.load(open(filepath, 'rb'))
            return data if isinstance(data, dict) else {}
        except Exception as e:
            raise IOError(f"Failed to parse TOML file {filepath}: {e}") from e
    
    def _parse_json(self, content, filepath):
        """Parse JSON content.
        
        Args:
            content: JSON content as string.
            filepath: Path to file for error reporting.
            
        Returns:
            dict: Parsed JSON data.
            
        Raises:
            IOError: If JSON parsing fails.
        """
        try:
            data = json.loads(content)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError as e:
            raise IOError(f"Failed to parse JSON file {filepath}: {e}") from e
