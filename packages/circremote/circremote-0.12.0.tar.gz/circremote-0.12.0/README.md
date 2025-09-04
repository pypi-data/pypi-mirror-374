# circremote

A command-line tool for remotely executing CircuitPython code on devices over serial or Web Workflow connections.

It can run the commands included with it, your own commands from anywhere in the filesystem, and commands that it loads over HTTP/HTTPS. It can easily execute example programs from Github.

## Features

- **Cross-platform support**: Works on Windows, macOS, and Linux
- **Multiple connection types**: Serial ports and CircuitPython Web Workflow
- **Built-in commands**: 100+ sensor and utility commands included
- **Remote commands**: Execute commands from URLs and GitHub repositories
- **Dependency management**: Automatic installation of CircuitPython libraries via circup
- **Configuration**: Device aliases and search paths for easy management
- **Quiet mode**: Suppress output for scripting and automation

## Installation

```bash
pip install circremote
```

## Quick Start

### Serial Connection (macOS/Linux)
```bash
# List files on device
circremote /dev/ttyUSB0 ls /

# Run a sensor command
circremote /dev/ttyUSB0 BME280
```

### Serial Connection (Windows)
```bash
# List files on device
circremote COM3 ls /

# Run a sensor command
circremote COM3 BME280
```

### Web Workflow Connection
```bash
# Connect to device over network
circremote 192.168.1.100 BME280

# With password
circremote -p mypassword 192.168.1.100 BME280
```

### Remote Commands
```bash
# Run command from GitHub
circremote /dev/ttyUSB0 https://github.com/user/repo/tree/main/commands/BME280

# Run Python file from web
circremote /dev/ttyUSB0 https://example.com/my_sensor.py
```

## Configuration

Create `~/.circremote/config.json` (cross-platform):

```json
{
  "devices": [
    {
      "name": "my-device",
      "device": "/dev/ttyUSB0",
      "friendly_name": "My CircuitPython Board",
      "defaults": {
        "sda": "board.IO1",
        "scl": "board.IO2",
        "address": "0x76"
      }
    }
  ],
  "command_aliases": [
    {
      "name": "temp",
      "command": "BME280"
    }
  ],
  "search_paths": [
    "/path/to/my/commands"
  ],
  "circup": "/usr/local/bin/circup",
  "variable_defaults": {
    "sda": "board.SDA",
    "scl": "board.SCL",
    "address": "0x76"
  }
}
```

### Device Defaults

You can set default values for command variables on a per-device basis using the `defaults` field in your device configuration. This is especially useful for I2C pin assignments that are specific to your board layout.

**Variable Resolution Priority:**
1. **Command line values** (highest priority)
2. **Device defaults** (from config.json)
3. **Global variable defaults** (from config.json)
4. **Command defaults** (from info.json)

**Example:**
```bash
# With device defaults, you can run:
circremote my-device BME280

# Instead of having to specify pins every time:
circremote my-device BME280 sda=board.IO1 scl=board.IO2 address=0x76
```

### Global Variable Defaults

You can also set global default values for command variables that apply to all devices and commands using the `variable_defaults` field in your configuration. This is useful for setting common defaults like I2C pins that are consistent across your setup.

**Example:**
```bash
# With global defaults, you can run:
circremote /dev/ttyUSB0 BME280  # Uses global sda/scl defaults

# Device-specific defaults still override global defaults:
circremote my-device BME280     # Uses device defaults, then global defaults
```

Then use device aliases:
```bash
circremote my-device temp
```

## Options

- `-v, --verbose`: Verbose output
- `-q, --quiet`: Quiet mode (suppress output except device output)
- `-y, --yes`: Auto-confirm all prompts
- `-c, --skip-circup`: Skip dependency installation
- `-p, --password`: Web Workflow password
- `-C, --config`: Custom config file path
- `-u, --circup`: Custom circup path
- `-t, --timeout`: Connection timeout (seconds)

## Documentation

- [Usage Guide](doc/usage.md)
- [Command Reference](doc/commands.md)
- [FAQ](doc/faq.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.
