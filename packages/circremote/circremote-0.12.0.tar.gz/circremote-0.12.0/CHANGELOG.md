# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.12.0] - 2025-08-14

Windows support! Mostly worked on Windows already but this update
makes timeouts work properly, runs `circup` under Windows,  properly
locates the `config.json` file and updates the documentation.

New `enable-webworkflow` and `erase_fs` commands

Tested more commands (mostly light sensors), added VEML6075 UV sensor,
VCNL4040 proximity sensor, and combined BMP3XX sensors into one command.

### Added
- Global variable defaults support via `variable_defaults` in config.json
- Enhanced variable resolution priority: command line > device defaults > global defaults > command defaults

## [0.11.0] - 2025-08-11

Added "quiet mode" -q to eliminate noise, for use in testing environments.

Also new `ls` and `rm` commands to list and remove files.

## [0.10.2] - 2025-08-07

Fixed package building to properly omit files and use pypackage.toml
and MANFEST.in and not setuptools.py

No functional changes, only packaging.

## [0.10.0] - 2025-08-07 

### Added
- Initial release with core functionality
- Support for serial and WebSocket connections
- Built-in command library for sensors and utilities
- Configuration system with device aliases
- Dependency management with circup integration
- Support for local and remote command execution

### Features
- Upload and run Python code on CircuitPython devices
- I2C bus scanning and sensor communication
- File system operations (clean, cat, etc.)
- Network utilities (ping, WiFi scanning)
- Hardware abstraction for various sensors and displays

## [0.10.1] - 2025-08-08

- PyPI support
