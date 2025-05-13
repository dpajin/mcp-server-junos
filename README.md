# Junos MCP Server (mcp-server-junos)

## Overview
The `mcp-server-junos` project provides MCP tools for viewing operational state and changing configuraton of Juniper Networks devices with **Junos** operating system. 
it uses Juniper's `junos-eznc` Python SDK and `FastMCP`.

## Tools

- **get_fact**: Retrieve basic information about the device, such as OS version and model.
- **show_command**: Execute any specified show command on the device and return the output. It can be used to retrieve device configuration and execute ping command.
- **apply_config**: Load and commit configuration changes to the device in both `set` and `junos` (curly brackets) formats.
- **list_devices**: Retrieve the list of **locally configured** devices on the MCP server. The list include **device name** and **IP address** for remote access.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd mcp-server-junos
   ```

### Running as a standalone application

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Rename example config file `config.example.yml` to `config.yml`

   ```
   mv config.example.yml config.yml
   ```

### Running as a docker container

**NOTE:** If you want to include the configuration file in the docker image, please configure it in advance before building the container image. Otherwise, you can provide global access parameters into the container using Environment Variables (example in *Usage* section)

2. Rename example config file `config.example.yml` to `config.yml` and configure it accordingly, before 

   ```
   mv config.example.yml config.yml
   ```


3. Build docker container image
   ```
   docker build -t mcp-server-junos .
   ```


## Configuration
The expected configuration file is named `config.yml` and it should be located in the root directory.
The supplied example config file `config.example.yml` can be used as a starting point


   ```
   mv config.example.yml config.yml
   ```

If *Environment variables* are used, they will take precedence over configuration file parameters.

### Global server configuration

**Using config file:**

```yaml
global:
  # To listen on all available interfaces use "0.0.0.0"
  server_host: 127.0.0.1
  server_port: 10008
  # Possible values: "sse" or "streamable-http"
  server_transport: "sse"
```

**Using Environment variables:**

```
MCP_SERVER_JUNOS_HOST="127.0.0.1"
MCP_SERVER_JUNOS_PORT=10008
MCP_SERVER_JUNOS_TRANSPORT="sse"
LOG_LEVEL="INFO"
```

### Devices inventory 

**Using config file:**

Configuration file key `devices` contains the dictionary of the device names with their respective access configuration.
- `device_name`: Name of the device
  - `host`: IP address for access
  - `user`: Username for access
  - `passwd`: Password for access
  - `port`: TCP port for NETCONF/SSH access

Example:

```yaml
access: 

  default:
    user: "admin"
    passwd: "admin@123"
    port: 830

  test: &test
    user: "admin"
    passwd: "admin@123"
    port: 830

devices:

  r1:
    host: 172.20.20.2
    user: "admin"
    passwd: "admin@123"
    port: 830

  r2:
    host: 172.20.20.3
    <<: *test

```

**Default access parameters** can be specified for devices which are not explicitly configured in the configuration file.
Those can be used through exposed MCP tools by supplying IP address in the `host` argument.

- First preference are environment variables:

  ```
  MCP_SERVER_JUNOS_ACCESS_DEFAULT_USER="admin"
  MCP_SERVER_JUNOS_ACCESS_DEFAULT_PASSWD="admin"
  MCP_SERVER_JUNOS_ACCESS_DEFAULT_PORT=830
  ```

- Second preference is config file:

  ```
  access:
    default:
      user: "admin"
      passwd: "admin"
      port: 830
  ```


## Usage

### Running as a standalone application

To use the MCP server, run the file:

```
python mcp_server_junos.py
```

- The MCP server exposes HTTP SSE interface on configurable port (default 10008) and IPs
- The URL for connecting to MCP SSE server locally would be: `http://127.0.0.1:10008/sse`

### Running as a docker container

When running as a docker container, user can supply global configuration through Environment variables and no configuration file. Access to any device would use those supplied access credentials. 

Other option is building a docker image with the configuration file `config.yml` or mounting it to the container as a volume to `/mcp-server-junos/config.yml` path.

```bash
docker run -d \
  --net=host \
  --name mcp-server-junos \
  -e MCP_SERVER_JUNOS_ACCESS_DEFAULT_USER="admin" \
  -e MCP_SERVER_JUNOS_ACCESS_DEFAULT_PASSWD="admin@123" \
  -e MCP_SERVER_JUNOS_ACCESS_DEFAULT_PORT=830 \
  -e MCP_SERVER_JUNOS_HOST="127.0.0.1" \
  -e MCP_SERVER_JUNOS_PORT=10008 \
  -e MCP_SERVER_JUNOS_TRANSPORT="sse" \
  mcp-server-junos:latest
```
## Tests

Tested with Github Copilot and VS Code as MCP client using HTTP SSE. 
- various show commands
- basic device configuration
- ping between devices


## License
The project is licensed under the MIT License.