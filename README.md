# Junos Devices MCP Server (mcp-junos)

## Overview
The `mcp-junos` project provides management and automation tools for Juniper Networks devices running Junos operating system. 
it uses `junos-ez` Python SDK and the Fast MCP.

## Tools
- **get_fact**: Retrieve basic information about the device, such as OS version and model.
- **show_command**: Execute any specified show command on the device and return the output. It can be used to retrieve device configuration and execute ping command.
- **get_config**: Retrieve the entire configuration or specific segments using XPath filters.
- **load_config**: Load and commit configuration changes to the device in both `set` and `junos` (curly brackets) formats.

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd mcp-junos
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
Create a `config.yml` file in the project root directory to specify device connection details. The configuration should include:
- `device_name`: Name of the device
  - `host`: IP address for access
  - `user`: Username for access
  - `passwd`: Password for access
  - `port`: TCP port for NETCONF/SSH access

A special device name called `default` can be used to set default access parameters for devices not explicitly configured, but which can be accessed using IP address supplied using `host` argument in tools call.

## Usage
To use the MCP server, run the main entry point:
```
python mcp_junos.py
```

The MCP server exposes HTTP SSE interface on configurable port (default 10008). 
The URL for connecting to MCP server locally would be `http://127.0.0.1:10008/sse`.
Port is confgurable using ENV variable `MCP_JUNOS_PORT` or configuration file option `mcp_junos_port: 10008`.

## License
This project is licensed under the MIT License.