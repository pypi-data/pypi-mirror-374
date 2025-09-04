# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import neopixel

num_pixels = {{ neopixel_count }}
print(f"Initializing {num_pixels} neopixels...")

# Test the pixel count by setting all pixels to a test color
pixels = neopixel.NeoPixel({{ neopixel_pin }}, num_pixels, brightness={{ brightness }}, auto_write=False)

# Test all pixels with a simple pattern to verify they work
print("Testing all pixels...")
for i in range(num_pixels):
    if i % 2 == 0:
        pixels[i] = (10, 0, 0)  # Dim red
    else:
        pixels[i] = (0, 0, 10)  # Dim blue
pixels.show()
time.sleep(2)

# Clear all pixels
for i in range(num_pixels):
    pixels[i] = (0, 0, 0)
pixels.show()
time.sleep(1)

print(f"Starting rainbow animation for {num_pixels} pixels...")

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def rainbow_cycle(wait):
    """Improved rainbow cycle that handles large pixel counts better."""
    for j in range(255):
        # Use a more precise calculation for large pixel counts
        for i in range(num_pixels):
            # Calculate position in the rainbow cycle
            # This ensures even distribution across all pixels
            pixel_index = (i * 256 // num_pixels + j) & 255
            pixels[i] = wheel(pixel_index)
        pixels.show()
        time.sleep(wait)

print("Rainbow animation started. Press Ctrl+C to stop.")
while True:
    rainbow_cycle({{ wait }})  # 0.01 = faster cycle; adjust for speed
