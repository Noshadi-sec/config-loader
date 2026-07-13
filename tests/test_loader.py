import pytest
from config_loader import ConfigLoader


class TestConfigLoader:
    """Tests for ConfigLoader."""
    
    def test_init(self):
        loader = ConfigLoader()
        assert loader is not None
