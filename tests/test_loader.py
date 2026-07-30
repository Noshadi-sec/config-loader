import json
import pytest
from pathlib import Path
from config_loader import ConfigLoader


class TestConfigLoader:
    """Tests for ConfigLoader."""
    
    def test_init(self):
        loader = ConfigLoader()
        assert loader is not None
    
    def test_supported_formats(self):
        loader = ConfigLoader()
        assert '.yaml' in loader.SUPPORTED_FORMATS
        assert '.yml' in loader.SUPPORTED_FORMATS
        assert '.json' in loader.SUPPORTED_FORMATS
        assert '.toml' in loader.SUPPORTED_FORMATS
    
    def test_load_nonexistent_file(self):
        loader = ConfigLoader()
        with pytest.raises(FileNotFoundError):
            loader.load('/nonexistent/path/config.yaml')
    
    def test_load_unsupported_format(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.xml"
        config_file.write_text("<config></config>")
        
        with pytest.raises(ValueError, match="Unsupported format"):
            loader.load(str(config_file))
    
    def test_load_json(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.json"
        data = {"key": "value", "number": 42, "nested": {"inner": "data"}}
        config_file.write_text(json.dumps(data))
        
        result = loader.load(str(config_file))
        assert result == data
    
    def test_load_json_invalid(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.json"
        config_file.write_text("{ invalid json }")
        
        with pytest.raises(IOError, match="Failed to parse JSON"):
            loader.load(str(config_file))
    
    def test_load_yaml(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.yaml"
        yaml_content = """key: value
number: 42
nested:
  inner: data
"""
        config_file.write_text(yaml_content)
        
        result = loader.load(str(config_file))
        assert result["key"] == "value"
        assert result["number"] == 42
        assert result["nested"]["inner"] == "data"
    
    def test_load_yaml_invalid(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.yaml"
        config_file.write_text("key: [invalid yaml: }")
        
        with pytest.raises(IOError, match="Failed to parse YAML"):
            loader.load(str(config_file))
    
    def test_load_toml(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.toml"
        toml_content = """key = "value"
number = 42

[nested]
inner = "data"
"""
        config_file.write_text(toml_content)
        
        result = loader.load(str(config_file))
        assert result["key"] == "value"
        assert result["number"] == 42
        assert result["nested"]["inner"] == "data"
    
    def test_load_toml_invalid(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.toml"
        config_file.write_text("key = [invalid toml}")
        
        with pytest.raises(IOError, match="Failed to parse TOML"):
            loader.load(str(config_file))
    
    def test_load_yml_extension(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.yml"
        yaml_content = "key: value\n"
        config_file.write_text(yaml_content)
        
        result = loader.load(str(config_file))
        assert result["key"] == "value"
    
    def test_load_returns_dict(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.json"
        config_file.write_text("{}")
        
        result = loader.load(str(config_file))
        assert isinstance(result, dict)
    
    def test_load_json_non_dict(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.json"
        config_file.write_text("[1, 2, 3]")
        
        result = loader.load(str(config_file))
        assert result == {}
    
    def test_load_with_defaults_file_exists(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.json"
        data = {"key": "value"}
        config_file.write_text(json.dumps(data))
        
        result = loader.load_with_defaults(str(config_file), {"default": "value"})
        assert result == data
    
    def test_load_with_defaults_file_missing(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "missing.json"
        defaults = {"key": "default"}
        
        result = loader.load_with_defaults(str(config_file), defaults)
        assert result == defaults
    
    def test_load_with_defaults_file_invalid(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.json"
        config_file.write_text("{ invalid }")
        defaults = {"key": "default"}
        
        result = loader.load_with_defaults(str(config_file), defaults)
        assert result == defaults
    
    def test_load_with_defaults_none_defaults(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "missing.json"
        
        result = loader.load_with_defaults(str(config_file))
        assert result == {}
    
    def test_get_simple_key(self):
        loader = ConfigLoader()
        config = {"key": "value", "number": 42}
        
        assert loader.get(config, "key") == "value"
        assert loader.get(config, "number") == 42
    
    def test_get_nested_key(self):
        loader = ConfigLoader()
        config = {"database": {"host": "localhost", "port": 5432}}
        
        assert loader.get(config, "database.host") == "localhost"
        assert loader.get(config, "database.port") == 5432
    
    def test_get_deeply_nested_key(self):
        loader = ConfigLoader()
        config = {"app": {"db": {"connection": {"timeout": 30}}}}
        
        assert loader.get(config, "app.db.connection.timeout") == 30
    
    def test_get_missing_key_returns_default(self):
        loader = ConfigLoader()
        config = {"key": "value"}
        
        assert loader.get(config, "missing") is None
        assert loader.get(config, "missing", "default") == "default"
    
    def test_get_missing_nested_key_returns_default(self):
        loader = ConfigLoader()
        config = {"database": {"host": "localhost"}}
        
        assert loader.get(config, "database.port") is None
        assert loader.get(config, "database.port", 5432) == 5432
    
    def test_get_invalid_path_returns_default(self):
        loader = ConfigLoader()
        config = {"key": "value"}
        
        assert loader.get(config, "key.nested") is None
        assert loader.get(config, "key.nested", "default") == "default"
    
    def test_get_non_dict_config_raises_typeerror(self):
        loader = ConfigLoader()
        
        with pytest.raises(TypeError, match="must be a dictionary"):
            loader.get([1, 2, 3], "key")
        
        with pytest.raises(TypeError, match="must be a dictionary"):
            loader.get("string", "key")
    
    def test_save_json(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.json"
        data = {"key": "value", "number": 42}
        
        loader.save(data, str(config_file))
        
        assert config_file.exists()
        result = loader.load(str(config_file))
        assert result == data
    
    def test_save_yaml(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.yaml"
        data = {"key": "value", "nested": {"inner": "data"}}
        
        loader.save(data, str(config_file))
        
        assert config_file.exists()
        result = loader.load(str(config_file))
        assert result == data
    
    def test_save_toml(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.toml"
        data = {"key": "value", "nested": {"inner": "data"}}
        
        loader.save(data, str(config_file))
        
        assert config_file.exists()
        result = loader.load(str(config_file))
        assert result == data
    
    def test_save_creates_parent_dirs(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "nested" / "dir" / "config.json"
        data = {"key": "value"}
        
        loader.save(data, str(config_file))
        
        assert config_file.exists()
        assert config_file.parent.exists()
    
    def test_save_invalid_type(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.json"
        
        with pytest.raises(TypeError, match="must be a dictionary"):
            loader.save([1, 2, 3], str(config_file))
    
    def test_save_unsupported_format(self, tmp_path):
        loader = ConfigLoader()
        config_file = tmp_path / "config.xml"
        data = {"key": "value"}
        
        with pytest.raises(ValueError, match="Unsupported format"):
            loader.save(data, str(config_file))
