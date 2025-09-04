# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import busio
import adafruit_tsl2561

# Initialize I2C with fallback
try:
    i2c = busio.I2C({{ scl }}, {{ sda }})
except:
    i2c = board.I2C()

# Initialize TSL2561
try:
    tsl = adafruit_tsl2561.TSL2561(i2c, address={{ address }})
except Exception as e:
    print(f"Error initializing TSL2561: {e}")
    import sys
    sys.exit(1)

print("TSL2561 Digital Light Sensor")
print("=" * 35)

# Display sensor information
print(f"I2C Address: 0x{{ address }}")
print(f"Chip ID: {tsl.chip_id}")
print(f"Integration Time: {tsl.integration_time}ms")
print(f"Gain: {tsl.gain}")
print()

tsl.enabled = True
time.sleep(1)

# Main reading loop
while True:
    # Read light sensor values
    broadband = tsl.broadband
    infrared = tsl.infrared
    lux = tsl.lux
    
    # Display sensor readings
    print("Light Sensor Readings:")
    print(f"  Broadband: {broadband}")
    print(f"  Infrared:  {infrared}")
    if lux is not None:
        print(f"  Lux:       {lux:.2f} lux")
    else:
        print("Lux - underrun or overrun")
    
   
    # Calculate infrared ratio for additional analysis
    if broadband > 0:
        ir_ratio = infrared / broadband
        print(f"  IR Ratio:  {ir_ratio:.3f}")
        
        # Analyze light source based on IR ratio
        if ir_ratio > 0.8:
            light_source = "Incandescent/Tungsten"
        elif ir_ratio > 0.6:
            light_source = "Fluorescent"
        elif ir_ratio > 0.4:
            light_source = "LED"
        else:
            light_source = "Natural/Sunlight"
        
        print(f"  Light Source: {light_source}")
    else:
        print(f"  IR Ratio:  N/A (no light detected)")
        light_source = "None"
    
    # Determine light level
    if lux is None:
        light_level = "Unknown"
    elif lux < 1:
        light_level = "Very Dark"
    elif lux < 10:
        light_level = "Dark"
    elif lux < 50:
        light_level = "Low Light"
    elif lux < 200:
        light_level = "Indoor"
    elif lux < 1000:
        light_level = "Bright Indoor"
    elif lux < 10000:
        light_level = "Outdoor (Overcast)"
    else:
        light_level = "Outdoor (Sunny)"

    print(f"Light Level: {light_level}")
    print("-" * 50)
    
    time.sleep(2)
