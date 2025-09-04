import os
import sys
import board
import microcontroller
import storage

# Interpolated variables
wifi_ssid = "{{ wifi_ssid }}"
wifi_password = "{{ wifi_password }}"
port = "{{ webworkflow_port }}"
web_workflow_password = "{{ webworkflow_password }}"

def is_esp32_variant():
    """Check if the board is an ESP32 variant."""
    try:
        # Check for ESP32-specific attributes
        if hasattr(microcontroller, 'chip'):
            chip = microcontroller.chip
            return chip in ['ESP32', 'ESP32-S2', 'ESP32-S3', 'ESP32-C3', 'ESP32-C6', 'ESP32-H2']
        
        # Fallback: check board module for ESP32 indicators
        board_name = board.board_id.lower()
        esp32_indicators = ['esp32', 'esp32-s2', 'esp32-s3', 'esp32-c3', 'esp32-c6', 'esp32-h2', 'feather', 'qtpy', 'magtag', 'funhouse', 'bling']
        return any(indicator in board_name for indicator in esp32_indicators)
        
    except Exception as e:
        print(f"ERROR: Could not determine board type: {e}")
        return False

def check_filesystem_mounted():
    """Check if the CIRCUITPY filesystem is mounted over USB."""
    try:
        # Try to remount the filesystem - this will fail if it's mounted over USB
        storage.remount("/", False)
        # If we get here, it wasn't mounted over USB
        return False
    except OSError:
        # If remount fails, it's likely mounted over USB
        return True
    except Exception:
        # For any other error, assume it's mounted to be safe
        return True

def read_settings_toml():
    """Read the current settings.toml file."""
    try:
        with open('/settings.toml', 'r') as f:
            return f.read()
    except OSError:
        # settings.toml doesn't exist
        return ""
    except Exception as e:
        print(f"ERROR: Could not read settings.toml: {e}")
        return None

def write_settings_toml(content):
    """Write content to settings.toml file."""
    try:
        with open('/settings.toml', 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"ERROR: Could not write settings.toml: {e}")
        return False

def check_webworkflow_config(settings_content):
    """Check if Web Workflow is already configured."""
    if not settings_content:
        return False
    
    # Check for existing Web Workflow configuration
    webworkflow_vars = [
        'CIRCUITPY_WEB_API_PASSWORD',
        'CIRCUITPY_WEB_API_PORT',
        'CIRCUITPY_WEB_API_HOST'
    ]
    
    # Check for existing WiFi configuration
    wifi_vars = [
        'CIRCUITPY_WIFI_SSID',
        'CIRCUITPY_WIFI_PASSWORD'
    ]
    
    # Check if any Web Workflow or WiFi variables are already configured
    for var in webworkflow_vars + wifi_vars:
        if var in settings_content:
            return True
    
    return False

def add_webworkflow_config(settings_content):
    """Add Web Workflow configuration to settings.toml."""
    # Prepare the new configuration
    webworkflow_config = f"""
# CircuitPython Web Workflow Configuration
CIRCUITPY_WEB_API_PASSWORD = "{web_workflow_password}"
CIRCUITPY_WEB_API_PORT = {port}

# WiFi Configuration
CIRCUITPY_WIFI_SSID = "{wifi_ssid}"
CIRCUITPY_WIFI_PASSWORD = "{wifi_password}"
"""
    
    # Add to existing content or create new file
    if settings_content.strip():
        # Add to existing content
        new_content = settings_content.rstrip() + webworkflow_config
    else:
        # Create new file
        new_content = webworkflow_config.lstrip()
    
    return new_content

def main():
    """Main function to enable Web Workflow."""
    print("CircuitPython Web Workflow Configuration")
    print("=" * 50)
    
    # Validate arguments
    if not wifi_ssid or not wifi_password or not port or not web_workflow_password:
        print("ERROR: Missing required arguments")
        print("Usage: enable-webworkflow <wifi_ssid> <wifi_password> <port> <web_workflow_password>")
        sys.exit(1)
    
    # Validate port number
    try:
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            print(f"ERROR: Invalid port number: {port}")
            print("Port must be between 1 and 65535")
            sys.exit(1)
    except ValueError:
        print(f"ERROR: Invalid port number: {port}")
        print("Port must be a valid integer")
        sys.exit(1)
    
    # Check if filesystem is mounted over USB
    print("Checking filesystem mount status...")
    if check_filesystem_mounted():
        print("ERROR: CIRCUITPY filesystem is mounted over USB")
        print()
        print("To configure Web Workflow, you must unmount the CIRCUITPY drive first:")
        print()
        print("macOS/Linux:")
        print("  sudo umount /Volumes/CIRCUITPY  # macOS")
        print("  sudo umount /media/username/CIRCUITPY  # Linux")
        print()
        print("Windows:")
        print("  Right-click on CIRCUITPY drive → Eject")
        print("  Or use: net use X: /delete  # if mapped as drive X:")
        print()
        print("After unmounting, run this command again.")
        sys.exit(1)
    
    print("✓ Filesystem is not mounted over USB")
    
    # Check if this is an ESP32 variant
    print("Checking board compatibility...")
    if not is_esp32_variant():
        print("ERROR: This command is only supported on ESP32 variants")
        print("Current board may not support CircuitPython Web Workflow")
        print("Supported boards: ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6, ESP32-H2")
        sys.exit(1)
    
    print("✓ Board is ESP32 variant")
    
    # Read current settings.toml
    print("Reading current settings.toml...")
    current_settings = read_settings_toml()
    if current_settings is None:
        sys.exit(1)
    
    # Check if Web Workflow is already configured
    if check_webworkflow_config(current_settings):
        print("ERROR: Web Workflow or WiFi is already configured in settings.toml")
        print("To avoid overwriting existing configuration, please:")
        print("1. Edit settings.toml manually to update values")
        print("2. Or remove the existing Web Workflow/WiFi configuration first")
        print()
        print("Current variables found:")
        print("Web Workflow:")
        print("- CIRCUITPY_WEB_API_PASSWORD")
        print("- CIRCUITPY_WEB_API_PORT") 
        print("WiFi:")
        print("- CIRCUITPY_WIFI_SSID")
        print("- CIRCUITPY_WIFI_PASSWORD")
        sys.exit(1)
    
    print("✓ No existing Web Workflow configuration found")
    
    # Add Web Workflow configuration
    print("Adding Web Workflow configuration...")
    new_settings = add_webworkflow_config(current_settings)
    
    # Write the updated settings.toml
    if write_settings_toml(new_settings):
        print("✓ Web Workflow and WiFi configuration added successfully")
        print()
        print("Configuration details:")
        print(f"  WiFi SSID: {wifi_ssid}")
        print(f"  WiFi Password: {'*' * len(wifi_password)}")
        print(f"  Web Workflow Port: {port}")
        print(f"  Web Workflow Password: {'*' * len(web_workflow_password)}")
        print()
        print("Next steps:")
        print("1. Restart your CircuitPython device")
        print("2. The device will connect to WiFi automatically")
        print("3. Find your device's IP address (check serial output)")
        print("4. Connect to the device at: http://<device_ip>:{port}")
        print("5. Use the Web Workflow password to access the interface")
        print()
        print("You can now use circremote with Web Workflow:")
        print(f"  circremote <device_ip>:{port} -p {web_workflow_password} <command>")
        print()
        print("To learn more about Web Workflow see https://learn.adafruit.com/circuitpython-with-esp32-quick-start/setting-up-web-workflow")
        print("            and                      https://docs.circuitpython.org/en/latest/docs/workflows.html#web")
    else:
        print("ERROR: Failed to write settings.toml")
        sys.exit(1)

if __name__ == "__main__":
    main()
