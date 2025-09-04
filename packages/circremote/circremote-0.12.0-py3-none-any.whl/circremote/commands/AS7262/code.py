# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import busio
from adafruit_as726x import AS726x_I2C

# Initialize I2C with fallback
try:
    i2c = busio.I2C({{ scl }}, {{ sda }})
except:
    i2c = board.I2C()

# Initialize AS7262
try:
    spectral = AS726x_I2C(i2c)
except Exception as e:
    print(f"Error initializing AS7262: {e}")
    import sys
    sys.exit(1)

print("AS7262 Spectral Sensor")
print("=" * 30)

# Display sensor information
print(f"Integration Time: {spectral.integration_time}ms")
print(f"Gain: {spectral.gain}")
print(f"Conversion Mode: {spectral.conversion_mode}")
print()

# Main reading loop
while True:
    # Read spectral data
    violet = spectral.violet
    blue = spectral.blue
    green = spectral.green
    yellow = spectral.yellow
    orange = spectral.orange
    red = spectral.red
    
    # Display spectral readings
    print("Spectral Readings:")
    print(f"  Violet (450nm):  {violet:6.2f}")
    print(f"  Blue (500nm):    {blue:6.2f}")
    print(f"  Green (550nm):   {green:6.2f}")
    print(f"  Yellow (570nm):  {yellow:6.2f}")
    print(f"  Orange (590nm):  {orange:6.2f}")
    print(f"  Red (610nm):     {red:6.2f}")
    
    # Calculate total intensity
    total_intensity = violet + blue + green + yellow + orange + red
    
    # Determine dominant color
    colors = [
        ("Violet", violet),
        ("Blue", blue),
        ("Green", green),
        ("Yellow", yellow),
        ("Orange", orange),
        ("Red", red)
    ]
    
    dominant_color = max(colors, key=lambda x: x[1])
    
    print(f"Total Intensity: {total_intensity:.2f}")
    print(f"Dominant Color: {dominant_color[0]} ({dominant_color[1]:.2f})")
    
    # Color classification based on dominant wavelength
    if dominant_color[0] == "Violet" and violet > 100:
        color_class = "Purple/Violet"
    elif dominant_color[0] == "Blue" and blue > 100:
        color_class = "Blue"
    elif dominant_color[0] == "Green" and green > 100:
        color_class = "Green"
    elif dominant_color[0] == "Yellow" and yellow > 100:
        color_class = "Yellow"
    elif dominant_color[0] == "Orange" and orange > 100:
        color_class = "Orange"
    elif dominant_color[0] == "Red" and red > 100:
        color_class = "Red"
    else:
        color_class = "Low Light/Unknown"
    
    print(f"Color Classification: {color_class}")
    print("-" * 40)
    
    time.sleep(2)
