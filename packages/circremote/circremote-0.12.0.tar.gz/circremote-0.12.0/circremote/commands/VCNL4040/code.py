# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import busio
import adafruit_vcnl4040

# Initialize I2C with fallback
try:
    i2c = busio.I2C({{ scl }}, {{ sda }})
except:
    i2c = board.I2C()

# Initialize VCNL4040
try:
    vcnl = adafruit_vcnl4040.VCNL4040(i2c)
except Exception as e:
    print(f"Error initializing VCNL4040: {e}")
    import sys
    sys.exit(1)

print("VCNL4040 Proximity and Ambient Light Sensor")
print("=" * 50)

# Display sensor information
print(f"Proximity Integration Time: {vcnl.proximity_integration_time}")
print()

# Main reading loop
while True:
    proximity = vcnl.proximity
    white = vcnl.white
    lux = vcnl.lux
    
    print(f"Proximity: {proximity}")
    print(f"White Light: {white}")
    print(f"Lux: {lux:.1f} lux")
    
    # Determine proximity level
    if proximity < 100:
        proximity_level = "Far"
    elif proximity < 500:
        proximity_level = "Medium"
    elif proximity < 1000:
        proximity_level = "Close"
    else:
        proximity_level = "Very Close"
        
    # Determine light level
    if lux < 10:
        light_level = "Dark"
    elif lux < 50:
        light_level = "Low Light"
    elif lux < 200:
        light_level = "Indoor"
    elif lux < 1000:
        light_level = "Bright Indoor"
    else:
        light_level = "Outdoor"
        
    print(f"Proximity Level: {proximity_level}")
    print(f"Light Level: {light_level}")
    print("-" * 50)
    
    time.sleep(1)
