# config-loader

A minimal configuration file manager with support for YAML, TOML, and JSON formats.

## Installation

```bash
git clone https://github.com/user/config-loader.git
cd config-loader
pip install -e .
```

## Usage

```python
from config_loader import ConfigLoader

loader = ConfigLoader()
config = loader.load('config.yaml')
print(config)
```

## Features

- Multi-format support (YAML, TOML, JSON)
- Simple API
- Automatic format detection
