from machine import Pin, TouchPad
import time
import random

# Parameters
threshold = 100
capval1 = 0
capval2 = 0

# Initialize TouchPad and LEDs
tpin1 = TouchPad(Pin(4))
tpin2 = TouchPad(Pin(2))
led = Pin(26, Pin.OUT)
led1 = Pin(19, Pin.OUT)
led2 = Pin(21, Pin.OUT)

# Initial state
led.value(1)
n = random.randint(3, 7)
time.sleep(n)
led.value(0)

# Main loop
while True:
    capval1 = tpin1.read()
    capval2 = tpin2.read()

    print("TouchPad1:", capval1, "TouchPad2:", capval2)  # For debugging

    if capval1 is not None and capval1 < threshold:
        led1.value(1)
        break
    if capval2 is not None and capval2 < threshold:
        led2.value(1)
        break

# Optional: Add more code if required after the loop ends
# Write your code here :-)
