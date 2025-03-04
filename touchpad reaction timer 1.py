from machine import Pin, TouchPad
import time
import random
threshold=100
capval1=0
capval2=0
tpin1=TouchPad(Pin(4))
tpin2=TouchPad(Pin(2))
led=Pin(26, Pin.OUT)
led1=Pin(19, Pin.OUT)
led2=Pin(21, Pin.OUT)
led.value(1)
n=random.randint(3, 7)
time.sleep(n)
led.value(0)
while True:
    capval1=tpin1.read()
    capval2=tpin2.read()
    if capval1<threshold:
        led1.value(1)
        break
    if capval2<threshold:
        led2.value(1)
        break




