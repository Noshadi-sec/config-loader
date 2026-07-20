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
