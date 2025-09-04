# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import busio
import adafruit_veml6075

# Initialize I2C with fallback
try:
    i2c = busio.I2C({{ scl }}, {{ sda }})
except:
    i2c = board.I2C()

# Initialize VEML6075
try:
    veml = adafruit_veml6075.VEML6075(i2c)
except Exception as e:
    print(f"Error initializing VEML6075: {e}")
    import sys
    sys.exit(1)

print("VEML6075 UV Sensor")
print("=" * 30)

# Display sensor information
print(f"Integration Time: {veml.integration_time}")
print()

# Main reading loop
while True:
    uva = veml.uva
    uvb = veml.uvb
    uvi = veml.uv_index
    
    print(f"UVA: {uva:.2f}")
    print(f"UVB: {uvb:.2f}")
    print(f"UV Index: {uvi:.2f}")
    
    # Determine UV level
    if uvi < 2:
        uv_level = "Low"
    elif uvi < 5:
        uv_level = "Moderate"
    elif uvi < 7:
        uv_level = "High"
    elif uvi < 10:
        uv_level = "Very High"
    else:
        uv_level = "Extreme"
        
    print(f"UV Level: {uv_level}")
    print("-" * 30)
    
    time.sleep(30)
