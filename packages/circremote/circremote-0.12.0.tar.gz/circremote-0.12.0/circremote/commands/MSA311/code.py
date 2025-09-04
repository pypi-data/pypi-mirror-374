# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import busio
from adafruit_msa3xx import MSA311

# Initialize I2C with fallback
try:
    i2c = busio.I2C({{ scl }}, {{ sda }})
except:
    i2c = board.I2C()

# Initialize MSA311
try:
    msa = MSA311(i2c)
except Exception as e:
    print(f"Error initializing MSA311: {e}")
    import sys
    sys.exit(1)

print("MSA311 3-Axis Accelerometer")
print("=" * 30)

# Main reading loop
while True:
        # Read accelerometer values
        x, y, z = msa.acceleration
        
        # Display readings
        print(f"X: {x:.2f} m/s²")
        print(f"Y: {y:.2f} m/s²")
        print(f"Z: {z:.2f} m/s²")
        print("-" * 30)
        
        time.sleep(1)
