from machine import Pin, TouchPad
import time
threshold=100
capval=0
led=Pin(21, Pin.OUT)
led2=Pin(19, Pin.OUT)
tpin0=TouchPad(Pin(2))
tpin=TouchPad(Pin(4))
while True:
    capval=tpin0.read()
    capval=tpin.read()
    led.value(0)
    led2.value(0)
    #print(float(capval))
    if capval<threshold:
        led.value(1)
    if capval<threshold:
        led2.value(1)
        #print("Touch Detected")# Write your code here :-)
