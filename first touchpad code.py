from machine import Pin, TouchPad
import time
threshold=100
capval=0
led=Pin(21, Pin.OUT)
tpin=TouchPad(Pin(4))
while True:
    capval=tpin.read()
    led.value(0)
    #print(float(capval))
    if capval<threshold:
        led.value(1)
        #print("Touch Detected")
