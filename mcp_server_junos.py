import logging
import os
import json
import sys
from pathlib import Path
import yaml
from fastmcp import FastMCP
# junos-eznc imports
from jnpr.junos import Device
from jnpr.junos.exception import CommitError, RpcError
from jnpr.junos.utils.config import Config
# local imports
from utils.config_loader import load_config_file


log_level = os.getenv("LOG_LEVEL", logging.INFO)
logging.basicConfig(stream=sys.stdout, level=log_level)
log = logging.getLogger('mcp-server-junos')


config = load_config_file("config.yml")
mcp = FastMCP(name="mpc-server-junos")


def get_device_access(device_name: str=None, host: str=None, config=config):
    """
    Get device access configuration from the config file.
    Args:
        device_name (str): The name of the device.
        host (str): The IP address of the device.
        config (dict): Configuration data loaded from the config file."""

    # Check if the configuration contains devices inventory
    
    # 1. Take default access configuration from the config file
    dev_cfg = { "host": host }
    if config.get("access", None):
        access = config["access"]
        dev_cfg.update(access.get("default", {}))
            
    
    # 2. Override with environment variables
    if os.getenv("MCP_SERVER_JUNOS_ACCESS_DEFAULT_USER", None):
        dev_cfg['user'] = os.getenv("MCP_SERVER_JUNOS_ACCESS_DEFAULT_USER")
    if os.getenv("MCP_SERVER_JUNOS_ACCESS_DEFAULT_PASSWD", None):
        dev_cfg['passwd'] = os.getenv("MCP_SERVER_JUNOS_ACCESS_DEFAULT_PASSWD")
    if os.getenv("MCP_SERVER_JUNOS_ACCESS_DEFAULT_PORT", None):
        dev_cfg['port'] = int(os.getenv("MCP_SERVER_JUNOS_ACCESS_DEFAULT_PORT"))
    
    devices_dict = config.get("devices", None)
    
    if devices_dict:
        if device_name:
            if devices_dict.get(device_name, None):
                dev_cfg.update(devices_dict[device_name])
        elif host:
            if devices_dict.get(host, None):
                dev_cfg.update(devices_dict[host])
                dev_cfg['host'] = host   
    
    if all(key in dev_cfg for key in ["host", "user", "passwd", "port"]):
        return dev_cfg
    else:
        raise ValueError(f"No access configuration could be determined for device_name '{device_name}' or host {host}")


@mcp.tool()
def list_devices() -> dict:
    """
    Retrieve the list of the devices from the local configuration in CSV format.
    MCP server can access to any device with supplied IP address and using the default access configuration
    """
    try:
        devices_dict = config.get("devices", None)
        output = "name,ip"
        if devices_dict:
            devices_list = list(devices_dict.keys())
            if len(devices_list) > 0:
                for d in devices_list:
                    output += f"{d},{devices_dict[d].get("host"), ""}"
            else:
                return "No devices found in the configuration."
        else:
            return "No devices found in the configuration."

        # Return the output as a CSV string
        return output

    except Exception as e:
        log.error(f"An error occurred while getting the list of devices: {e}")
        return f"An error occurred while getting the list of devices: {e}"    


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
def apply_config(device_name: str=None, host: str=None, config_data: str=None, config_format: str='set') -> str:
    """
    Apply configuration change on a Juniper device and commit it
    Args:
        device_name (str): The name of the device, (supply when IP and access parameters provided locally on server)
        host (str): Supply the IP address of the device if device_name is not provided
        config_data (str): Configuration data to load
        config_format (str): Format of the configuration data ('set' or 'junos')
    """
    try:
        device_config = get_device_access(device_name, host)
        # Connect to the device

        with Device(**device_config) as dev:
            with Config(dev, mode='private') as config:  
                if config_format == 'set':
                    config.load(config_data, format='set')
                elif config_format == 'junos':
                    config.load(config_data, format='junos')
                else:
                    raise ValueError("Invalid configuration format specified. Use 'set' or 'junos'.")

                log.debug(f"Configuration loaded on {device_config['host']}, trying to commit...")

                #try:
                # Commit the configuration
                config.commit()
                log.debug(f"Configuration committed on {device_config['host']}")
                # except CommitError as e:
                #     log.error(f"Error: Unable to commit configuration: {str(e)}")
                #     # try to rollback the configuration candidate before closing the connection
                #     log.error(f"Trying to rollback the configuration candidate")
                #     config.rollback(rb_id=0)
                #     raise f"Error: Unable to commit configuration: {str(e)}"

                log.debug(f"Configuration loaded and committed successfully on {device_config['host']}")
                return f"Configuration loaded and committed successfully. Configuration applied:\n{config_data}"

    except Exception as e:
        log.error(f"Error loading configuration on {device_config['host']}: {e}")
        return f"Error loading configuration on {device_config['host']}: {str(e)}"


def main():
    
    # Default port is 10008
    config_port = 10008 if not config.get("global", None) else config["global"].get("server_port", 10008)
    port = int(os.getenv("MCP_SERVER_JUNOS_PORT", config_port))
    
    # By default, the server will listen only on localhost. Use "0.0.0.0" to listen on all interfaces
    config_host = "127.0.0.1" if not config.get("global", None) else config["global"].get("server_host", "127.0.0.1")
    host = os.getenv("MCP_SERVER_JUNOS_HOST", config_host)
    
    # By default, the server will use SSE transport
    config_transport = "sse" if not config.get("global", None) else config["global"].get("server_transport", "sse")
    transport = os.getenv("MCP_SERVER_JUNOS_TRANSPORT", config_transport)

    log.info(f"Starting MCP server for Junos devices on host {host}, port {port}...")
    mcp.run(transport=transport, port=port, host=host)

if __name__ == "__main__":
    main()
    