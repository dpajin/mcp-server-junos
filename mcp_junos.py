import logging
import os
import json
import sys
from pathlib import Path
import yaml
from fastmcp import FastMCP
# junos-eznc imports
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import Config
# local imports
from utils.config_loader import load_config_file

log = logging.getLogger('mcp-junos')
log_level = os.getenv("LOGGING", logging.INFO)
logging.basicConfig(stream=sys.stdout, level=log_level)


config = load_config_file("config.yml")
mcp = FastMCP(name="mpc-junos-server")


def get_device_access(device_name: str=None, host: str=None, config=config):
    """
    Get device access configuration from the config file.
    Args:
        device_name (str): The name of the device.
        host (str): The IP address of the device.
        config (dict): Configuration data loaded from the config file."""
    if device_name:
        if device_name in config:
            return config[device_name]
    elif host:
        if config.get(host, None):
            dev_cfg = config[host]
            dev_cfg['host'] = host
            return dev_cfg
        elif 'default' in config:
            dev_cfg = config['default']
            dev_cfg['host'] = host
            return dev_cfg
    else:
        raise ValueError(f"No configuration found for device '{device_name}' and no default configuration set.")


@mcp.tool()
def get_facts(device_name: str=None, host: str=None) -> dict:
    """
    Retrieve device facts from a Juniper device.
    Args:
        device_name (str): The name of the device, (supply when IP and access parameters provided locally on server)
        host (str): Supply the IP address of the device if device_name is not provided
    
    """
    try:
        device_config = get_device_access(device_name, host)

        with Device(**device_config) as dev:
            log.debug(f"Connected to {device_config["host"]}")
            log.debug(str(dev.facts))
            return dev.facts
        
    except Exception as e:
        log.error(f"An error occurred while getting facts: {e}")
        return f"An error occurred while getting facts: {e}"


@mcp.tool()
def show_command(device_name: str=None, host: str=None, command: str=None) -> str:
    """
    Execute a show command on a Juniper device.
    Use this tool to get operational data, 'show configuration' and execute 'ping' command
    Args:
        device_name (str): The name of the device, (supply when IP and access parameters provided locally on server)
        host (str): Supply the IP address of the device if device_name is not provided
        command (str): Command to execute
    """
    try:
        device_config = get_device_access(device_name, host)
        
        with Device(**device_config) as dev:
            log.debug(f"Connected to {device_config["host"]}")
            output = dev.cli(command, format='text')
            return output
        
    except Exception as e:
        log.error(f"An error occurred while executing command {command}: {e}")
        return f"An error occurred while  executing command {command}: {e}"


@mcp.tool()
def load_config(device_name: str=None, host: str=None, config_data: str=None, config_format: str='set') -> str:
    """
    Change configuration on a Juniper device and commit it
    Args:
        device_name (str): The name of the device, (supply when IP and access parameters provided locally on server)
        host (str): Supply the IP address of the device if device_name is not provided
        config_data (str): Configuration data to load
        config_format (str): Format of the configuration data ('set' or 'junos')
    """
    try:
        device_config = get_device_access(device_name, host)
        # Connect to the device
        dev = Device(**device_config)
        dev.open()

        # Load configuration based on the specified format
        config = Config(dev)
        if config_format == 'set':
            config.load(config_data, format='set')
        elif config_format == 'junos':
            config.load(config_data, format='junos')
        else:
            raise ValueError("Invalid configuration format specified. Use 'set' or 'junos'.")

        log.debug(f"Configuration loaded on {device_config['host']}")
        # Commit the configuration
        config.commit()

        log.debug(f"Configuration loaded and committed successfully on {device_config['host']}")
        return "Configuration loaded and committed successfully"

    except Exception as e:
        log.error(f"Error loading configuration on {device_config['host']}: {e}")
        return f"Error loading configurationon {device_config['host']}: {str(e)}"

    finally:
        dev.close()


def main():
    port = int(os.getenv("MCP_JUNOS_PORT", config.get("mcp_junos_port", 10008)))
    
    log.info(f"Starting MCP server for Junos devices on port {port}...")
    mcp.run(transport="sse", port=port, host="0.0.0.0")

if __name__ == "__main__":
    main()
    