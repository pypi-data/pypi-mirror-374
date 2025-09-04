# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import neopixel

num_pixels = {{ neopixel_count }}
print(f"Neopixel Diagnostic Test for {num_pixels} pixels")
print(f"Pin: {{ neopixel_pin }}")
print(f"Brightness: {{ brightness }}")

pixels = neopixel.NeoPixel({{ neopixel_pin }}, num_pixels, brightness={{ brightness }}, auto_write=False)

def test_all_pixels():
    """Test each pixel individually to see which ones work."""
    print("\n=== Testing Individual Pixels ===")
    
    # Test each pixel with red
    for i in range(num_pixels):
        print(f"Testing pixel {i}...")
        pixels.fill((0, 0, 0))  # Clear all
        pixels[i] = (50, 0, 0)  # Bright red
        pixels.show()
        time.sleep(0.1)
    
    # Test each pixel with green
    for i in range(num_pixels):
        print(f"Testing pixel {i} with green...")
        pixels.fill((0, 0, 0))  # Clear all
        pixels[i] = (0, 50, 0)  # Bright green
        pixels.show()
        time.sleep(0.1)
    
    # Test each pixel with blue
    for i in range(num_pixels):
        print(f"Testing pixel {i} with blue...")
        pixels.fill((0, 0, 0))  # Clear all
        pixels[i] = (0, 0, 50)  # Bright blue
        pixels.show()
        time.sleep(0.1)

def test_patterns():
    """Test various patterns to see how many pixels respond."""
    print("\n=== Testing Patterns ===")
    
    # Pattern 1: Alternating red/blue
    print("Pattern 1: Alternating red/blue")
    for i in range(num_pixels):
        if i % 2 == 0:
            pixels[i] = (30, 0, 0)
        else:
            pixels[i] = (0, 0, 30)
    pixels.show()
    time.sleep(3)
    
    # Pattern 2: Count up with brightness
    print("Pattern 2: Count up with brightness")
    for i in range(num_pixels):
        brightness = int((i / num_pixels) * 50)
        pixels[i] = (brightness, brightness, brightness)
    pixels.show()
    time.sleep(3)
    
    # Pattern 3: Reverse count
    print("Pattern 3: Reverse count")
    for i in range(num_pixels):
        brightness = int(((num_pixels - i) / num_pixels) * 50)
        pixels[i] = (brightness, 0, brightness)
    pixels.show()
    time.sleep(3)

def test_memory():
    """Test if we can access all pixels in memory."""
    print("\n=== Testing Memory Access ===")
    
    try:
        # Try to set the last pixel
        pixels[num_pixels - 1] = (50, 50, 50)
        print(f"✓ Successfully set pixel {num_pixels - 1}")
    except Exception as e:
        print(f"✗ Error setting pixel {num_pixels - 1}: {e}")
    
    try:
        # Try to set a pixel beyond the count
        pixels[num_pixels] = (50, 50, 50)
        print(f"✗ Should have failed to set pixel {num_pixels}")
    except Exception as e:
        print(f"✓ Correctly failed to set pixel {num_pixels}: {e}")

# Run diagnostics
test_memory()
test_patterns()
test_all_pixels()

print("\n=== Diagnostic Complete ===")
print("If you only see 302 pixels working, possible causes:")
print("1. Power supply insufficient for 320 pixels")
print("2. Hardware connection issue with last 18 pixels")
print("3. CircuitPython memory limitations")
print("4. Neopixel library limitations on this board")

# Keep the last pattern visible
pixels.fill((0, 0, 0))
pixels.show()
