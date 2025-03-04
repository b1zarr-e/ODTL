from machine import Pin
import time
led1=Pin(4, Pin.OUT)
led2=Pin(21, Pin.OUT)
led3=Pin(12, Pin.OUT)
while (True):
    led1.value(1)
    led2.value(0)
    led3.value(0)
    time.sleep(0.2)

    led2.value(1)
    led1.value(0)
    led3.value(0)
    time.sleep(0.2)


    led3.value(1)
    led1.value(0)
    led2.value(0)
    time.sleep(0.2)
