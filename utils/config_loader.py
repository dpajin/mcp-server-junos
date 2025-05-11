from pathlib import Path
import yaml

def load_config_file(config_path='config.yml'):
    if not Path(config_path).is_file():
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config
