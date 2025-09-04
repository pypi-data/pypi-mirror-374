# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
from adafruit_display_text import label

# Matrix configuration
width = {{ width }}
height = {{ height }}
bit_depth = {{ bit_depth }}
rgb_pins = {{ rgb_pins }}
addr_pins = {{ addr_pins }}
clock_pin = {{ clock_pin }}
latch_pin = {{ latch_pin }}
output_enable_pin = {{ output_enable_pin }}

print(f"LED Matrix Rainbow Effect")
print(f"Display: {width}x{height}")
print(f"Bit depth: {bit_depth}")

displayio.release_displays()

# Initialize the RGB matrix
matrix = rgbmatrix.RGBMatrix(
    width=width,
    height=height,
    bit_depth=bit_depth,
    rgb_pins=rgb_pins,
    addr_pins=addr_pins,
    clock_pin=clock_pin,
    latch_pin=latch_pin,
    output_enable_pin=output_enable_pin,
    doublebuffer=True,
)

if matrix is None:
    print("failed to create matrix")
    exit()

# Create the display
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color."""
    if s == 0.0:
        return (int(v * 255), int(v * 255), int(v * 255))
    
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    
    return (int(r * 255), int(g * 255), int(b * 255))

def create_rainbow_bitmap(offset=0):
    """Create a bitmap with rainbow colors marching across the display."""
    bitmap = displayio.Bitmap(width, height, 256)
    palette = displayio.Palette(256)
    
    # Create rainbow palette
    for i in range(256):
        hue = (i + offset) / 256.0
        rgb = hsv_to_rgb(hue, 1.0, 1.0)
        palette[i] = rgb
    
    # Fill bitmap with rainbow pattern
    for y in range(height):
        for x in range(width):
            color_index = (x + offset) % 256
            bitmap[x, y] = color_index
    
    return bitmap, palette

def marching_rainbow():
    """Display a marching rainbow effect on the matrix."""
    print("Starting marching rainbow effect...")
    print("Press Ctrl+C to stop")
    
    try:
        offset = 0
        while True:
            # Create rainbow bitmap with current offset
            bitmap, palette = create_rainbow_bitmap(offset)
            
            # Create tile grid
            tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
            
            # Create group and add tile grid
            group = displayio.Group()
            group.append(tile_grid)
            
            # Show the display
            display.root_group = group
            display.refresh()
            
            # Increment offset for marching effect
            offset = (offset + 1) % 256
            
            # Small delay for animation speed
            time.sleep({{ delay }})
            
    except KeyboardInterrupt:
        print("\nStopping rainbow effect...")
        # Clear display
        display.show(displayio.Group())
        display.refresh()
        print("Rainbow effect stopped.")

# Start the marching rainbow effect
marching_rainbow()


