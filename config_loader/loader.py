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
    
    def save(self, data, filepath):
        """Save configuration data to a file.
        
        Args:
            data: Dictionary containing configuration data.
            filepath: Path where the configuration file will be saved.
            
        Raises:
            ValueError: If format is not supported.
            IOError: If file cannot be written or serialized.
            TypeError: If data is not a dictionary.
        """
        if not isinstance(data, dict):
            raise TypeError("Configuration data must be a dictionary")
        
        path = Path(filepath)
        suffix = path.suffix.lower()
        
        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {suffix}")
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if suffix in ('.yaml', '.yml'):
                content = self._serialize_yaml(data)
            elif suffix == '.toml':
                content = self._serialize_toml(data, filepath)
            elif suffix == '.json':
                content = self._serialize_json(data)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            raise IOError(f"Failed to write config file: {filepath}") from e
    
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
            data = tomllib.loads(content)
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
    
    def _serialize_yaml(self, data):
        """Serialize data to YAML format.
        
        Args:
            data: Dictionary to serialize.
            
        Returns:
            str: YAML content.
            
        Raises:
            ImportError: If PyYAML is not installed.
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML support. "
                "Install it with: pip install pyyaml"
            )
        
        return yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
    
    def _serialize_toml(self, data, filepath):
        """Serialize data to TOML format.
        
        Args:
            data: Dictionary to serialize.
            filepath: Path to file for error reporting.
            
        Returns:
            str: TOML content.
            
        Raises:
            ImportError: If toml library is not installed.
            IOError: If serialization fails.
        """
        try:
            import tomli_w
        except ImportError:
            raise ImportError(
                "TOML serialization requires tomli-w library. "
                "Install it with: pip install tomli-w"
            )
        
        try:
            return tomli_w.dumps(data)
        except Exception as e:
            raise IOError(f"Failed to serialize data to TOML: {e}") from e
    
    def _serialize_json(self, data):
        """Serialize data to JSON format.
        
        Args:
            data: Dictionary to serialize.
            
        Returns:
            str: JSON content.
        """
        return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
