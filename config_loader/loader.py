import json
import sys
from pathlib import Path
from copy import deepcopy

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

try:
    import yaml
except ImportError:
    yaml = None

try:
    import tomli_w
except ImportError:
    tomli_w = None


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
    
    def _parse_yaml(self, content, filepath):
        """Parse YAML content.
        
        Args:
            content: YAML string content.
            filepath: Original file path for error messages.
            
        Returns:
            dict: Parsed YAML data, or empty dict if content is empty/None.
            
        Raises:
            IOError: If YAML parsing fails.
        """
        if yaml is None:
            raise IOError("PyYAML is not installed. Install with: pip install pyyaml")
        
        try:
            result = yaml.safe_load(content)
            # Handle empty files or non-dict content
            return result if isinstance(result, dict) else {}
        except yaml.YAMLError as e:
            raise IOError(f"Failed to parse YAML file {filepath}: {e}") from e
    
    def _parse_toml(self, content, filepath):
        """Parse TOML content.
        
        Args:
            content: TOML string content.
            filepath: Original file path for error messages.
            
        Returns:
            dict: Parsed TOML data.
            
        Raises:
            IOError: If TOML parsing fails.
        """
        try:
            return tomllib.loads(content)
        except Exception as e:
            raise IOError(f"Failed to parse TOML file {filepath}: {e}") from e
    
    def _parse_json(self, content, filepath):
        """Parse JSON content.
        
        Args:
            content: JSON string content.
            filepath: Original file path for error messages.
            
        Returns:
            dict: Parsed JSON data, or empty dict if not a dict.
            
        Raises:
            IOError: If JSON parsing fails.
        """
        try:
            result = json.loads(content)
            # Handle non-dict JSON (arrays, primitives, etc.)
            return result if isinstance(result, dict) else {}
        except json.JSONDecodeError as e:
            raise IOError(f"Failed to parse JSON file {filepath}: {e}") from e
    
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
            
        Raises:
            TypeError: If config is not a dictionary.
        """
        if not isinstance(config, dict):
            raise TypeError("Configuration must be a dictionary")
        
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
    
    def merge(self, base, override):
        """Merge two configuration dictionaries recursively.
        
        Deep merges override configuration into base configuration.
        Nested dictionaries are merged recursively, while non-dict
        values in override completely replace values in base.
        
        Args:
            base: Base configuration dictionary.
            override: Override configuration dictionary.
            
        Returns:
            dict: Merged configuration (new object, inputs not modified).
            
        Raises:
            TypeError: If base or override is not a dictionary.
        """
        if not isinstance(base, dict):
            raise TypeError("Base configuration must be a dictionary")
        if not isinstance(override, dict):
            raise TypeError("Override configuration must be a dictionary")
        
        # Deep copy base to avoid modifying input
        result = deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self.merge(result[key], value)
            else:
                # Replace or add the value
                result[key] = deepcopy(value)
        
        return result
    
    def save(self, config, filepath):
        """Save configuration to a file.
        
        Automatically determines format from file extension and writes
        the configuration data in the appropriate format.
        
        Args:
            config: Configuration dictionary to save.
            filepath: Path where configuration should be written.
            
        Raises:
            TypeError: If config is not a dictionary.
            ValueError: If file format is not supported.
            IOError: If file cannot be written.
        """
        if not isinstance(config, dict):
            raise TypeError("Configuration must be a dictionary")
        
        path = Path(filepath)
        suffix = path.suffix.lower()
        
        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {suffix}")
        
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if suffix in ('.yaml', '.yml'):
                self._write_yaml(config, path)
            elif suffix == '.toml':
                self._write_toml(config, path)
            elif suffix == '.json':
                self._write_json(config, path)
        except IOError:
            raise
        except Exception as e:
            raise IOError(f"Failed to write config file {filepath}: {e}") from e
    
    def _write_yaml(self, config, path):
        """Write configuration to YAML file.
        
        Args:
            config: Configuration dictionary.
            path: Path object for file to write.
            
        Raises:
            IOError: If write fails or PyYAML not available.
        """
        if yaml is None:
            raise IOError("PyYAML is not installed. Install with: pip install pyyaml")
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
    
    def _write_toml(self, config, path):
        """Write configuration to TOML file.
        
        Args:
            config: Configuration dictionary.
            path: Path object for file to write.
            
        Raises:
            IOError: If write fails or tomli-w not available.
        """
        if tomli_w is None:
            raise IOError("tomli-w is not installed. Install with: pip install tomli-w")
        
        with open(path, 'wb') as f:
            tomli_w.dump(config, f)
    
    def _write_json(self, config, path):
        """Write configuration to JSON file.
        
        Args:
            config: Configuration dictionary.
            path: Path object for file to write.
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
