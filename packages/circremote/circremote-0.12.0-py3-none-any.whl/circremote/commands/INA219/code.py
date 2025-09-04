# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import busio
import adafruit_ina219

# Initialize I2C with fallback
try:
    i2c = busio.I2C({{ scl }}, {{ sda }})
except:
    i2c = board.I2C()

# Initialize INA219
try:
    ina219 = adafruit_ina219.INA219(i2c, {{ address }})
except Exception as e:
    print(f"Error initializing INA219: {e}")
    import sys
    sys.exit(1)

print("INA219 Current/Voltage Sensor")
print("=" * 35)

# Display sensor information
print(f"Bus Voltage Range: 0-26V")
print(f"Current Range: ±3.2A")
print(f"Shunt Voltage Range: ±320mV")
print()

# Main reading loop
while True:
    # Read sensor values
    bus_voltage = ina219.bus_voltage
    shunt_voltage = ina219.shunt_voltage
    current = ina219.current
    power = ina219.power
    
    # Display sensor readings
    print("Power Measurements:")
    print(f"  Bus Voltage:   {bus_voltage:.3f}V")
    print(f"  Shunt Voltage: {shunt_voltage:.3f}mV")
    print(f"  Current:       {current:.3f}mA")
    print(f"  Power:         {power:.3f}mW")
    
    # Calculate load voltage (bus voltage + shunt voltage)
    load_voltage = bus_voltage + (shunt_voltage / 1000.0)
    print(f"  Load Voltage:  {load_voltage:.3f}V")
    
    # Determine power status
    if current > 0:
        power_status = "Power Consuming"
        if current > 1000:
            current_level = "High Current"
        elif current > 100:
            current_level = "Medium Current"
        else:
            current_level = "Low Current"
    elif current < 0:
        power_status = "Power Generating"
        current_level = "Negative Current"
    else:
        power_status = "No Current"
        current_level = "Standby"
    
    # Voltage level classification
    if bus_voltage < 1:
        voltage_level = "Very Low"
    elif bus_voltage < 3:
        voltage_level = "Low"
    elif bus_voltage < 5:
        voltage_level = "Normal (3.3V)"
    elif bus_voltage < 12:
        voltage_level = "Medium"
    elif bus_voltage < 24:
        voltage_level = "High"
    else:
        voltage_level = "Very High"
    
    print(f"Power Status: {power_status}")
    print(f"Current Level: {current_level}")
    print(f"Voltage Level: {voltage_level}")
    print("-" * 50)
    
    time.sleep(2)
