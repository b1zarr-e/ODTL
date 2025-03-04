from machine import Pin, TouchPad
import time
import random

# Define the touchpad sensitivity threshold
threshold = 100

# Initialize touchpads and pins for LEDs
tpin1 = TouchPad(Pin(4))
tpin2 = TouchPad(Pin(2))
led = Pin(26, Pin.OUT)  # Start LED
led1 = Pin(19, Pin.OUT)  # Player 1 LED
led2 = Pin(21, Pin.OUT)  # Player 2 LED

# Turn on the start LED to signal game readiness
led.value(1)

# Random delay before game starts
n = random.randint(3, 7)
time.sleep(n)

# Turn off the start LED to signal "Go!"
led.value(0)

# Main game loop
while True:
    capval1 = tpin1.read()  # Read touchpad 1 value
    capval2 = tpin2.read()  # Read touchpad 2 value

    # Check if player 1 touches their pad first
    if capval1 < threshold:
        led1.value(1)  # Light up Player 1 LED
        print("Player 1 wins!")
        break

    # Check if player 2 touches their pad first
    if capval2 < threshold:
        led2.value(1)  # Light up Player 2 LED
        print("Player 2 wins!")
        break# Write your code here :-)
