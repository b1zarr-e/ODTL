import time
import neopixel
from machine import Pin

NUM_LEDS = 16  # Number of LEDs
PIN = 4  # GPIO pin

np = neopixel.NeoPixel(Pin(PIN), NUM_LEDS)

# Rainbow color function
def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

# Rainbow cycle function
def rainbow_cycle(wait):
    for j in range(256):
        for i in range(NUM_LEDS):
            pixel_index = (i * 256 // NUM_LEDS) + j
            np[i] = wheel(pixel_index & 255)
        np.write()
        time.sleep(wait)

# Run rainbow effect
while True:
    rainbow_cycle(0.05)
# Write your code here :-)
