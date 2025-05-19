from pathlib import Path
import yaml
import logging
import os
import sys

log_level = os.getenv("LOG_LEVEL", logging.INFO)
logging.basicConfig(stream=sys.stdout, level=log_level)
log = logging.getLogger('mcp-server-junos')

def load_config_file(config_path='config.yml'):
    if not Path(config_path).is_file():
        log.warning(f"Configuration file '{config_path}' not found.")
        return {}
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config
