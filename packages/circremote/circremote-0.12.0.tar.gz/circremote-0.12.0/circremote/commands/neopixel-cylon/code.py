# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import neopixel

# Initialize the neopixel display
width = {{ width }}
height = {{ height }}
num_pixels = width * height

print(f"Neopixel Cylon Effect")
print(f"Display: {width}x{height} ({num_pixels} pixels)")
print(f"Pin: {{ neopixel_pin }}")
print(f"Brightness: {{ brightness }}")

pixels = neopixel.NeoPixel({{ neopixel_pin }}, num_pixels, brightness={{ brightness }}, auto_write=False)

def clear_display():
    """Clear all pixels to black."""
    pixels.fill((0, 0, 0))
    pixels.show()

def set_pixel(x, y, color):
    """Set a pixel at position (x, y) with the given color."""
    if 0 <= x < width and 0 <= y < height:
        # Calculate pixel index based on layout
        # For multi-row displays, we'll use a serpentine pattern
        if y % 2 == 0:
            # Even rows: left to right
            pixel_index = y * width + x
        else:
            # Odd rows: right to left
            pixel_index = y * width + (width - 1 - x)
        pixels[pixel_index] = color

def set_column(x, color):
    """Set all pixels in a column to the given color."""
    for y in range(height):
        set_pixel(x, y, color)

def cylon_effect():
    """Run the classic Cylon effect with a red blob bouncing side to side."""
    print("Starting Cylon effect...")
    print("Press Ctrl+C to stop")
    
    # Cylon colors
    RED = (255, 0, 0)
    DIM_RED = (50, 0, 0)
    BLACK = (0, 0, 0)
    
    # Animation parameters
    delay = {{ delay }}
    fade_steps = 5  # Number of fade steps for the trail
    
    try:
        while True:
            # Move from left to right
            for x in range(width):
                # Clear the display
                clear_display()
                
                # Draw the main red blob
                set_column(x, RED)
                
                # Draw fade trail to the left
                for i in range(1, min(fade_steps + 1, x + 1)):
                    fade_x = x - i
                    if fade_x >= 0:
                        # Calculate fade intensity
                        fade_intensity = int(255 * (1 - i / fade_steps))
                        fade_color = (fade_intensity, 0, 0)
                        set_column(fade_x, fade_color)
                
                pixels.show()
                time.sleep(delay)
            
            # Move from right to left
            for x in range(width - 1, -1, -1):
                # Clear the display
                clear_display()
                
                # Draw the main red blob
                set_column(x, RED)
                
                # Draw fade trail to the right
                for i in range(1, min(fade_steps + 1, width - x)):
                    fade_x = x + i
                    if fade_x < width:
                        # Calculate fade intensity
                        fade_intensity = int(255 * (1 - i / fade_steps))
                        fade_color = (fade_intensity, 0, 0)
                        set_column(fade_x, fade_color)
                
                pixels.show()
                time.sleep(delay)
                
    except KeyboardInterrupt:
        print("\nStopping Cylon effect...")
        clear_display()
        print("Cylon effect stopped.")

# Start the Cylon effect
cylon_effect()


